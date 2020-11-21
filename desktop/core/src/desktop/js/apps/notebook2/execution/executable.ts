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

import $ from 'jquery';

import { Cancellable } from 'api/cancellablePromise';
import {
  checkExecutionStatus,
  closeStatement,
  ExecuteApiResponse,
  ExecutionHandle,
  ExecutionHistory
} from 'apps/notebook2/execution/apiUtils';
import ExecutionResult from 'apps/notebook2/execution/executionResult';
import { hueWindow } from 'types/types';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import ExecutionLogs, { ExecutionLogsRaw } from 'apps/notebook2/execution/executionLogs';
import hueUtils, { UUID } from 'utils/hueUtils';
import Executor from 'apps/notebook2/execution/executor';

/**
 *
 * @type {{running: string, canceling: string, canceled: string, expired: string, waiting: string, success: string, ready: string, available: string, closed: string, starting: string}}
 */
export const EXECUTION_STATUS = {
  available: 'available',
  failed: 'failed',
  success: 'success',
  expired: 'expired',
  running: 'running',
  starting: 'starting',
  waiting: 'waiting',
  ready: 'ready',
  streaming: 'streaming',
  canceled: 'canceled',
  canceling: 'canceling',
  closed: 'closed'
};

export const EXECUTABLE_UPDATED_EVENT = 'hue.executable.updated';
export const EXECUTABLE_STATUS_TRANSITION_EVENT = 'hue.executable.status.transitioned';

export interface ExecutableRaw {
  executeEnded: number;
  executeStarted: number;
  handle: ExecutionHandle;
  history?: ExecutionHistory;
  id: string;
  logs: ExecutionLogsRaw;
  lost: boolean;
  observerState: { [key: string]: unknown };
  progress: number;
  status: string;
  type: string;
}

const INITIAL_HANDLE: ExecutionHandle = {
  statement_id: 0
};

export default abstract class Executable {
  id: string = UUID();
  database?: string;
  executor: Executor;
  handle: ExecutionHandle;
  operationId?: string;
  history?: ExecutionHistory;
  status = EXECUTION_STATUS.ready;
  progress = 0;
  result?: ExecutionResult;
  logs: ExecutionLogs;
  cancellables: Cancellable[] = [];
  notifyThrottle = -1;
  executeStarted = 0;
  executeEnded = 0;
  previousExecutable?: Executable;
  nextExecutable?: Executable;
  observerState: { [key: string]: unknown } = {};
  lost = false;

  protected constructor(options: { executor: Executor }) {
    this.executor = options.executor;

    this.handle = INITIAL_HANDLE;
    this.logs = new ExecutionLogs(this);
  }

  setStatus(status: string): void {
    const oldStatus = this.status;
    this.status = status;
    if (oldStatus !== status) {
      huePubSub.publish(EXECUTABLE_STATUS_TRANSITION_EVENT, {
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

  getExecutionTime(): number {
    return (this.executeEnded || Date.now()) - this.executeStarted;
  }

  notify(sync?: boolean): void {
    window.clearTimeout(this.notifyThrottle);
    if (sync) {
      huePubSub.publish(EXECUTABLE_UPDATED_EVENT, this);
    } else {
      this.notifyThrottle = window.setTimeout(() => {
        huePubSub.publish(EXECUTABLE_UPDATED_EVENT, this);
      }, 1);
    }
  }

  isReady(): boolean {
    return (
      this.status === EXECUTION_STATUS.ready ||
      this.status === EXECUTION_STATUS.closed ||
      this.status === EXECUTION_STATUS.canceled
    );
  }

  isRunning(): boolean {
    return this.status === EXECUTION_STATUS.running || this.status === EXECUTION_STATUS.streaming;
  }

  isSuccess(): boolean {
    return this.status === EXECUTION_STATUS.success || this.status === EXECUTION_STATUS.available;
  }

  isFailed(): boolean {
    return this.status === EXECUTION_STATUS.failed;
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
    this.executeStarted = Date.now();

    this.setStatus(EXECUTION_STATUS.running);
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
        if (typeof err === 'string') {
          err = this.adaptError(err);
        }
        this.logs.errors.push(err);
        throw err;
      }

      if (this.handle.has_result_set && this.handle.sync) {
        this.result = new ExecutionResult(this);
        if (this.handle.sync) {
          if (this.handle.result) {
            this.result.handleResultResponse(this.handle.result);
          }
          this.result.fetchRows();
        }
      }

      if (this.executor.isOptimizerEnabled && this.history) {
        huePubSub.publish('editor.upload.query', this.history.id);
      }

      this.checkStatus();
      this.logs.fetchLogs();
    } catch (err) {
      this.setStatus(EXECUTION_STATUS.failed);
    }
  }

  async checkStatus(statusCheckCount?: number): Promise<void> {
    let checkStatusTimeout = -1;

    let actualCheckCount = statusCheckCount || 0;
    if (!statusCheckCount) {
      this.cancellables.push({
        cancel: () => {
          window.clearTimeout(checkStatusTimeout);
        }
      });
    }
    actualCheckCount++;

    const queryStatus = await checkExecutionStatus({ executable: this });

    switch (queryStatus.status) {
      case EXECUTION_STATUS.success:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        this.setProgress(99); // TODO: why 99 here (from old code)?
        break;
      case EXECUTION_STATUS.available:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        this.setProgress(100);
        if (!this.result && this.handle.has_result_set) {
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
      case EXECUTION_STATUS.canceled:
      case EXECUTION_STATUS.expired:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        break;
      case EXECUTION_STATUS.streaming:
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
      case EXECUTION_STATUS.running:
      case EXECUTION_STATUS.starting:
      case EXECUTION_STATUS.waiting:
        this.setStatus(queryStatus.status);
        checkStatusTimeout = window.setTimeout(
          () => {
            this.checkStatus(statusCheckCount);
          },
          actualCheckCount > 45 ? 5000 : 1000
        );
        break;
      case EXECUTION_STATUS.failed:
        this.executeEnded = Date.now();
        this.setStatus(queryStatus.status);
        if (queryStatus.message) {
          // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          $.jHueNotify.error(queryStatus.message); // TODO: Inline instead of popup, e.g. ERROR_REGEX in Execute()
        }
        break;
      default:
        this.executeEnded = Date.now();
        this.setStatus(EXECUTION_STATUS.failed);
        console.warn('Got unknown status ' + queryStatus.status);
    }
  }

  addCancellable(cancellable: Cancellable): void {
    this.cancellables.push(cancellable);
  }

  abstract async internalExecute(): Promise<ExecuteApiResponse>;

  abstract adaptError(err: string): string;

  abstract canExecuteInBatch(): boolean;

  abstract getKey(): string;

  abstract getRawStatement(): string;

  abstract getStatement(): string;

  abstract toJson(): string;

  async cancel(): Promise<void> {
    if (
      this.cancellables.length &&
      (this.status === EXECUTION_STATUS.running || this.status === EXECUTION_STATUS.streaming)
    ) {
      hueAnalytics.log(
        'notebook',
        'cancel/' + (this.executor.connector() ? this.executor.connector().dialect : '')
      );
      this.setStatus(EXECUTION_STATUS.canceling);
      while (this.cancellables.length) {
        const cancellable = this.cancellables.pop();
        if (cancellable) {
          await cancellable.cancel();
        }
      }
      this.setStatus(EXECUTION_STATUS.canceled);
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
    this.handle = INITIAL_HANDLE;
    this.setProgress(0);
    this.setStatus(EXECUTION_STATUS.ready);
  }

  toJs(): ExecutableRaw {
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
      type: 'executable'
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
    this.setStatus(EXECUTION_STATUS.closed);
  }

  async toContext(id?: string): Promise<ExecutableContext> {
    const session = await sessionManager.getSession({ type: this.executor.connector().id });
    if (this.executor.snippet) {
      return {
        operationId: this.operationId,
        snippet: this.executor.snippet.toContextJson(),
        notebook: JSON.stringify(await this.executor.snippet.parentNotebook.toJs())
      };
    }

    const snippet = {
      type: this.executor.connector().id,
      result: {
        handle: this.handle
      },
      executor: this.executor.toJs(),
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
      type: this.executor.connector().id,
      snippets: [snippet],
      uuid: hueUtils.UUID(),
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
