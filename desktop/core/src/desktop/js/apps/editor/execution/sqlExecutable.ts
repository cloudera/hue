// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { VariableIndex } from '../components/variableSubstitution/types';
import { Cancellable } from 'api/cancellablePromise';
import {
  checkExecutionStatus,
  closeStatement,
  ExecuteApiResponse,
  executeStatement,
  ExecutionHandle,
  ExecutionHistory
} from 'apps/editor/execution/api';
import {
  EXECUTABLE_TRANSITIONED_TOPIC,
  EXECUTABLE_UPDATED_TOPIC,
  ExecutableTransitionedEvent,
  ExecutableUpdatedEvent
} from 'apps/editor/execution/events';
import ExecutionResult from 'apps/editor/execution/executionResult';
import ExecutionLogs, {
  ExecutionError,
  ExecutionLogsRaw
} from 'apps/editor/execution/executionLogs';
import Executor from 'apps/editor/execution/executor';
import sessionManager from 'apps/editor/execution/sessionManager';
import dataCatalog from 'catalog/dataCatalog';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { hueWindow } from 'types/types';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import UUID from 'utils/string/UUID';

export enum ExecutionStatus {
  available = 'available',
  failed = 'failed',
  success = 'success',
  expired = 'expired',
  running = 'running',
  starting = 'starting',
  waiting = 'waiting',
  ready = 'ready',
  streaming = 'streaming',
  canceled = 'canceled',
  canceling = 'canceling',
  closed = 'closed'
}

export interface ExecutableRaw {
  executeEnded: number;
  executeStarted: number;
  handle?: ExecutionHandle;
  history?: ExecutionHistory;
  id: string;
  logs: ExecutionLogsRaw;
  lost: boolean;
  observerState: { [key: string]: unknown };
  progress: number;
  status: ExecutionStatus;
  type: string;
}

export interface SqlExecutableRaw extends ExecutableRaw {
  database: string;
  parsedStatement: ParsedSqlStatement;
}

const BATCHABLE_STATEMENT_TYPES =
  /ALTER|ANALYZE|WITH|REFRESH|CREATE|DELETE|DROP|GRANT|INSERT|INVALIDATE|LOAD|SET|TRUNCATE|UPDATE|FROM|UPSERT|USE/i;
const SELECT_END_REGEX = /([^;]*)([;]?[^;]*)/;
const ERROR_REGEX = /line ([0-9]+)(:([0-9]+))?/i;
const TABLE_DDL_REGEX =
  /(?:CREATE|DROP)\s+(?:TABLE|VIEW)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))\..*/i;
const DB_DDL_REGEX =
  /(?:CREATE|DROP)\s+(?:DATABASE|SCHEMA)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))/i;

const substituteVariables = (statement: string, variables: VariableIndex): string => {
  if (!Object.keys(variables).length) {
    return statement;
  }

  const variablesString = Object.values(variables)
    .map(variable => variable.name)
    .join('|');

  return statement.replace(
    RegExp('([^\\\\])?\\${(' + variablesString + ')(=[^}]*)?}', 'g'),
    (match, p1, p2) => {
      const { value, type, meta } = variables[p2];
      const pad = type === 'datetime-local' && value.length === 16 ? ':00' : ''; // Chrome drops the seconds from the timestamp when it's at 0 second.
      const isValuePresent = //If value is string there is a need to check whether it is empty
        typeof value === 'string' ? value : value !== undefined && value !== null;
      return p1 + (isValuePresent ? value + pad : meta.placeholder);
    }
  );
};

export default class SqlExecutable {
  id: string = UUID();
  database: string;
  executor: Executor;
  handle?: ExecutionHandle;
  operationId?: string;
  history?: ExecutionHistory;
  status = ExecutionStatus.ready;
  progress = 0;
  result?: ExecutionResult;
  logs: ExecutionLogs;
  cancellables: Cancellable[] = [];
  notifyThrottle = -1;
  executeStarted = 0;
  executeEnded = 0;
  previousExecutable?: SqlExecutable;
  nextExecutable?: SqlExecutable;
  observerState: { [key: string]: unknown } = {};
  lost = false;
  edited = false;
  parsedStatement: ParsedSqlStatement;

  constructor(options: {
    executor: Executor;
    database: string;
    parsedStatement: ParsedSqlStatement;
  }) {
    this.logs = new ExecutionLogs(this);
    this.executor = options.executor;
    this.database = options.database;
    this.parsedStatement = options.parsedStatement;
  }

  getLogs(): ExecutionLogs | undefined {
    return this.logs;
  }

  getResult(): ExecutionResult | undefined {
    return this.result;
  }

  setStatus(status: ExecutionStatus): void {
    const oldStatus = this.status;
    this.status = status;
    if (oldStatus !== status) {
      huePubSub.publish<ExecutableTransitionedEvent>(EXECUTABLE_TRANSITIONED_TOPIC, {
        executable: this,
        oldStatus: oldStatus,
        newStatus: status
      });
    }
    this.notify();
  }

  setProgress(progress: number): void {
    this.progress = progress;
    this.notify();
  }

  getExecutionStatus(): ExecutionStatus {
    return this.status;
  }

  getExecutionTime(): number {
    return (this.executeEnded || Date.now()) - this.executeStarted;
  }

  notify(sync?: boolean): void {
    window.clearTimeout(this.notifyThrottle);
    if (sync) {
      huePubSub.publish<ExecutableUpdatedEvent>(EXECUTABLE_UPDATED_TOPIC, this);
    } else {
      this.notifyThrottle = window.setTimeout(() => {
        huePubSub.publish<ExecutableUpdatedEvent>(EXECUTABLE_UPDATED_TOPIC, this);
      }, 1);
    }
  }

  isReady(): boolean {
    return (
      this.status === ExecutionStatus.ready ||
      this.status === ExecutionStatus.closed ||
      this.status === ExecutionStatus.canceled
    );
  }

  isRunning(): boolean {
    return this.status === ExecutionStatus.running || this.status === ExecutionStatus.streaming;
  }

  isSuccess(): boolean {
    return this.status === ExecutionStatus.success || this.status === ExecutionStatus.available;
  }

  isFailed(): boolean {
    return this.status === ExecutionStatus.failed;
  }

  isPartOfRunningExecution(): boolean {
    return (
      !this.isReady() ||
      (!!this.previousExecutable && this.previousExecutable.isPartOfRunningExecution())
    );
  }

  async cancelBatchChain(wait?: boolean): Promise<void> {
    if (this.previousExecutable) {
      this.previousExecutable.nextExecutable = undefined;
      const cancelPromise = this.previousExecutable.cancelBatchChain(wait);
      if (wait) {
        await cancelPromise;
      }
      this.previousExecutable = undefined;
    }

    if (!this.isReady()) {
      if (wait) {
        await this.cancel();
      } else {
        this.cancel();
      }
    }

    if (this.nextExecutable) {
      this.nextExecutable.previousExecutable = undefined;
      const cancelPromise = this.nextExecutable.cancelBatchChain(wait);
      if (wait) {
        await cancelPromise;
      }
      this.nextExecutable = undefined;
    }
    this.notify();
  }

  async execute(): Promise<void> {
    if (!this.isReady()) {
      return;
    }
    this.edited = false;
    this.executeStarted = Date.now();

    this.setStatus(ExecutionStatus.running);
    this.setProgress(0);
    this.notify(true);

    try {
      hueAnalytics.log(
        'notebook',
        'execute/' + (this.executor.connector() ? this.executor.connector().dialect : '')
      );
      try {
        const response = await this.internalExecute();
        this.handle = response.handle;
        this.history = response.history;
        if (response.history) {
          this.operationId = response.history.uuid;
        }
        if (
          response.handle.session_id &&
          response.handle.session_type &&
          response.handle.session_guid
        ) {
          sessionManager.updateSession({
            type: response.handle.session_type,
            id: response.handle.session_id,
            session_id: response.handle.session_guid,
            properties: []
          });
        }
      } catch (err) {
        if (err && (err.message || typeof err === 'string')) {
          const adapted = this.adaptError((err.message && err.message) || err);
          this.logs.errors.push(adapted);
          this.logs.notify();
        }
        throw err;
      }

      if (this.handle && this.handle.has_result_set && this.handle.sync) {
        this.result = new ExecutionResult(this);
        if (this.handle.result) {
          this.result.handleResultResponse(this.handle.result);
        }
        this.result.fetchRows();
      }

      if (this.executor.isSqlAnalyzerEnabled && this.history) {
        huePubSub.publish('editor.upload.query', this.history.id);
      }

      this.checkStatus();
      this.logs.fetchLogs();
    } catch (err) {
      console.warn(err);
      this.setStatus(ExecutionStatus.failed);
    }
  }

  async checkStatus(statusCheckCount?: number): Promise<void> {
    if (!this.handle) {
      return;
    }

    let checkStatusTimeout = -1;

    let actualCheckCount = statusCheckCount || 0;
    if (!statusCheckCount) {
      this.addCancellable({
        cancel: () => {
          window.clearTimeout(checkStatusTimeout);
        }
      });
    }
    actualCheckCount++;

    const queryStatus = await checkExecutionStatus({ executable: this });

    if (this.handle && typeof queryStatus.has_result_set !== 'undefined') {
      this.handle.has_result_set = queryStatus.has_result_set;
    }

    switch (queryStatus.status) {
      case ExecutionStatus.success:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        this.setProgress(99); // TODO: why 99 here (from old code)?
        break;
      case ExecutionStatus.available:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        this.setProgress(100);
        if (!this.result && this.handle && this.handle.has_result_set) {
          this.result = new ExecutionResult(this);
          this.result.fetchRows();
        }
        if (this.nextExecutable) {
          if (!this.nextExecutable.isReady()) {
            await this.nextExecutable.reset();
          }
          this.nextExecutable.execute();
        }
        break;
      case ExecutionStatus.canceled:
      case ExecutionStatus.expired:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        break;
      case ExecutionStatus.streaming:
        if (!queryStatus.result) {
          return;
        }
        if ((<hueWindow>window).WEB_SOCKETS_ENABLED) {
          huePubSub.publish('editor.ws.query.fetch_result', queryStatus.result);
        } else {
          if (!this.result) {
            this.result = new ExecutionResult(this, true);
          }
          this.result.handleResultResponse(queryStatus.result);
        }
      case ExecutionStatus.running:
      case ExecutionStatus.starting:
      case ExecutionStatus.waiting:
        this.setStatus(queryStatus.status);
        checkStatusTimeout = window.setTimeout(
          () => {
            this.checkStatus(statusCheckCount);
          },
          actualCheckCount > 45 ? 5000 : 1000
        );
        break;
      case ExecutionStatus.failed:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        if (queryStatus.message) {
          huePubSub.publish('hue.error', queryStatus.message);
        }
        break;
      default:
        this.executeEnded = Date.now();
        this.setStatus(ExecutionStatus.failed);
        console.warn('Got unknown status ' + queryStatus.status);
    }
  }

  addCancellable(cancellable: Cancellable): void {
    this.cancellables.push(cancellable);
  }

  async internalExecute(): Promise<ExecuteApiResponse> {
    if (this.parsedStatement && /CREATE|DROP/i.test(this.parsedStatement.firstToken)) {
      let match = this.parsedStatement.statement.match(TABLE_DDL_REGEX);
      const path: Array<string> = [];
      if (match) {
        path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
      } else {
        match = this.parsedStatement.statement.match(DB_DDL_REGEX);
        if (match) {
          path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
        } else if (this.database) {
          path.push(this.database);
        }
      }
      if (path.length) {
        window.setTimeout(() => {
          dataCatalog
            .getEntry({
              namespace: this.executor.namespace(),
              compute: this.executor.compute(),
              connector: this.executor.connector(),
              path: path
            })
            .then(entry => {
              entry.clearCache({ cascade: true, silenceErrors: true });
            })
            .catch();
        }, 5000);
      }
    }
    return await executeStatement({
      executable: this,
      silenceErrors: true
    });
  }

  adaptError(message: string): ExecutionError {
    const match = ERROR_REGEX.exec(message);
    if (match) {
      const row = parseInt(match[1]);
      const column = (match[3] && parseInt(match[3])) || 0;

      return { message, column: column || 0, row };
    }
    return { message, column: 0, row: this.parsedStatement.location.first_line };
  }

  canExecuteInBatch(): boolean {
    return this.parsedStatement && BATCHABLE_STATEMENT_TYPES.test(this.parsedStatement.firstToken);
  }

  getKey(): string {
    return this.database + '_' + this.parsedStatement.statement;
  }

  getRawStatement(): string {
    return this.parsedStatement.statement;
  }

  getStatement(): string {
    let statement = this.getRawStatement();

    if (
      this.parsedStatement.firstToken &&
      this.parsedStatement.firstToken.toLowerCase() === 'select' &&
      this.executor.defaultLimit &&
      !isNaN(this.executor.defaultLimit()) &&
      this.executor.defaultLimit() > 0 &&
      /\sfrom\s/i.test(statement) &&
      !/\slimit\s[0-9]/i.test(statement)
    ) {
      const endMatch = statement.match(SELECT_END_REGEX);
      if (endMatch) {
        statement = endMatch[1] + ' LIMIT ' + this.executor.defaultLimit();
        if (endMatch[2]) {
          statement += endMatch[2];
        }
      }
    }

    if (this.executor.variables) {
      statement = substituteVariables(statement, this.executor.variables);
    }

    return statement;
  }

  toJson(): string {
    return JSON.stringify({
      id: this.id,
      parsedStatement: this.parsedStatement,
      statement: this.getStatement(),
      database: this.database
    });
  }

  async cancel(): Promise<void> {
    if (
      this.cancellables.length &&
      (this.status === ExecutionStatus.running || this.status === ExecutionStatus.streaming)
    ) {
      hueAnalytics.log(
        'notebook',
        'cancel/' + (this.executor.connector() ? this.executor.connector().dialect : '')
      );
      this.setStatus(ExecutionStatus.canceling);
      while (this.cancellables.length) {
        const cancellable = this.cancellables.pop();
        if (cancellable) {
          await cancellable.cancel();
        }
      }
      this.setStatus(ExecutionStatus.canceled);
    }
  }

  async reset(): Promise<void> {
    this.result = undefined;
    this.logs.reset();
    if (!this.isReady()) {
      try {
        await this.close();
      } catch (err) {}
    }
    this.handle = undefined;
    this.setProgress(0);
    this.setStatus(ExecutionStatus.ready);
  }

  static fromJs(executor: Executor, executableRaw: SqlExecutableRaw): SqlExecutable {
    const executable = new SqlExecutable({
      database: executableRaw.database,
      executor: executor,
      parsedStatement: executableRaw.parsedStatement
    });
    executable.executeEnded = executableRaw.executeEnded;
    executable.executeStarted = executableRaw.executeStarted;
    executable.handle = executableRaw.handle;
    executable.history = executableRaw.history;
    executable.id = executableRaw.id;
    if (executableRaw.logs.errors) {
      executable.logs.errors = executableRaw.logs.errors.map(error => executable.adaptError(error));
    }
    executable.logs.jobs = executableRaw.logs.jobs;
    executable.lost = executableRaw.lost;
    executable.observerState = executableRaw.observerState || {};
    executable.operationId = executableRaw.history && executableRaw.history.uuid;
    executable.progress = executableRaw.progress;
    executable.status = executableRaw.status;
    return executable;
  }

  toJs(): SqlExecutableRaw {
    const state = Object.assign({}, this.observerState);
    delete state.aceAnchor;
    return {
      executeEnded: this.executeEnded,
      executeStarted: this.executeStarted,
      handle: this.handle,
      history: this.history,
      id: this.id,
      logs: this.logs.toJs(),
      lost: this.lost,
      observerState: state,
      progress: this.progress,
      status: this.status,
      type: 'sqlExecutable',
      database: this.database,
      parsedStatement: this.parsedStatement
    };
  }

  async close(): Promise<void> {
    while (this.cancellables.length) {
      const nextCancellable = this.cancellables.pop();
      if (nextCancellable) {
        try {
          await nextCancellable.cancel();
        } catch (err) {
          console.warn(err);
        }
      }
    }

    try {
      await closeStatement({ executable: this, silenceErrors: true });
    } catch (err) {
      console.warn('Failed closing statement');
    }
    this.setStatus(ExecutionStatus.closed);
  }

  async toContext(id?: string): Promise<ExecutableContext> {
    const session = await sessionManager.getSession({ type: this.executor.connector().id });
    if (this.executor.snippet) {
      return {
        operationId: this.operationId,
        snippet: this.executor.snippet.toContextJson(this.getStatement()),
        notebook: JSON.stringify(await this.executor.snippet.parentNotebook.toJs())
      };
    }

    const snippet = {
      type: this.executor.connector().id,
      result: {
        handle: this.handle
      },
      connector: this.executor.connector(),
      executor: this.executor.toJs(),
      defaultLimit: (this.executor.defaultLimit && this.executor.defaultLimit()) || null,
      status: this.status,
      id: id || UUID(),
      statement_raw: this.getRawStatement(),
      statement: this.getStatement(),
      lastExecuted: this.executeStarted,
      variables: [],
      compute: this.executor.compute(),
      namespace: this.executor.namespace(),
      database: this.database,
      properties: { settings: [] }
    };

    const notebook = {
      type: `query-${this.executor.connector().id}`,
      snippets: [snippet],
      uuid: UUID(),
      name: '',
      isSaved: false,
      sessions: [session],
      editorWsChannel: (<hueWindow>window).WS_CHANNEL
    };

    return {
      operationId: this.operationId,
      snippet: JSON.stringify(snippet),
      notebook: JSON.stringify(notebook)
    };
  }
}

export interface ExecutableContext {
  operationId?: string;
  snippet: string;
  notebook: string;
}
