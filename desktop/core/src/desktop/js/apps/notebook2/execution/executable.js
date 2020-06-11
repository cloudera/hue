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

import apiHelper from 'api/apiHelper';
import ExecutionResult from 'apps/notebook2/execution/executionResult';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import ExecutionLogs from 'apps/notebook2/execution/executionLogs';
import hueUtils, { UUID } from 'utils/hueUtils';

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

const ERROR_REGEX = /line ([0-9]+)(\:([0-9]+))?/i;

export default class Executable {
  /**
   * @param options
   * @param {string} [options.statement] - Either supply a statement or a parsedStatement
   * @param {Executor} options.executor
   * @param {Session[]} [options.sessions]
   */
  constructor(options) {
    this.id = UUID();
    this.executor = options.executor;
    this.handle = {
      statement_id: 0 // TODO: Get rid of need for initial handle in the backend
    };
    this.operationId = undefined;
    this.history = undefined;
    this.status = EXECUTION_STATUS.ready;
    this.progress = 0;
    this.result = undefined;
    this.logs = new ExecutionLogs(this);

    this.cancellables = [];
    this.notifyThrottle = -1;

    this.executeStarted = 0;
    this.executeEnded = 0;

    this.previousExecutable = undefined;
    this.nextExecutable = undefined;

    this.observerState = {};

    this.lost = false;
  }

  setStatus(status) {
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

  setProgress(progress) {
    this.progress = progress;
    this.notify();
  }

  getExecutionTime() {
    return (this.executeEnded || Date.now()) - this.executeStarted;
  }

  notify(sync) {
    window.clearTimeout(this.notifyThrottle);
    if (sync) {
      huePubSub.publish(EXECUTABLE_UPDATED_EVENT, this);
    } else {
      this.notifyThrottle = window.setTimeout(() => {
        huePubSub.publish(EXECUTABLE_UPDATED_EVENT, this);
      }, 1);
    }
  }

  isReady() {
    return (
      this.status === EXECUTION_STATUS.ready ||
      this.status === EXECUTION_STATUS.closed ||
      this.status === EXECUTION_STATUS.canceled
    );
  }

  isRunning() {
    return this.status === EXECUTION_STATUS.running || this.status === EXECUTION_STATUS.streaming;
  }

  isSuccess() {
    return this.status === EXECUTION_STATUS.success || this.status === EXECUTION_STATUS.available;
  }

  isFailed() {
    return this.status === EXECUTION_STATUS.failed;
  }

  isPartOfRunningExecution() {
    if (!this.isReady()) {
      return true;
    }
    return this.previousExecutable && this.previousExecutable.isPartOfRunningExecution();
  }

  async cancelBatchChain(wait) {
    if (this.previousExecutable) {
      this.previousExecutable.nextExecutable = undefined;
      if (wait) {
        await this.previousExecutable.cancelBatchChain(wait);
      } else {
        this.previousExecutable.cancelBatchChain();
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
      if (wait) {
        await this.nextExecutable.cancelBatchChain(wait);
      } else {
        this.nextExecutable.cancelBatchChain();
      }
      this.nextExecutable = undefined;
    }
    this.notify();
  }

  async execute() {
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
        this.operationId = response.history.uuid;
        if (response.handle.session_id) {
          sessionManager.updateSession({
            type: response.handle.session_type,
            id: response.handle.session_id,
            session_id: response.handle.session_guid,
            properties: []
          });
        }
      } catch (err) {
        const match = ERROR_REGEX.exec(err);
        if (match) {
          const errorLine = parseInt(match[1]) + this.parsedStatement.location.first_line - 1;
          let errorCol = match[3] && parseInt(match[3]);
          if (errorCol && errorLine === 1) {
            errorCol += this.parsedStatement.location.first_column;
          }

          const adjustedErr = err.replace(
            match[0],
            'line ' + errorLine + (errorCol !== null ? ':' + errorCol : '')
          );

          this.logs.errors.push(adjustedErr);
          this.logs.notify();

          throw new Error(adjustedErr);
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

      if (this.executor.isOptimizerEnabled) {
        huePubSub.publish('editor.upload.query', this.history.id);
      }

      this.checkStatus();
      this.logs.fetchLogs();
    } catch (err) {
      this.setStatus(EXECUTION_STATUS.failed);
    }
  }

  checkStatus(statusCheckCount) {
    let checkStatusTimeout = -1;

    if (!statusCheckCount) {
      statusCheckCount = 0;
      this.cancellables.push({
        cancel: () => {
          window.clearTimeout(checkStatusTimeout);
        }
      });
    }
    statusCheckCount++;

    this.cancellables.push(
      apiHelper.checkExecutionStatus({ executable: this }).done(async queryStatus => {
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
            if (window.WEB_SOCKETS_ENABLED) {
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
              statusCheckCount > 45 ? 5000 : 1000
            );
            break;
          case EXECUTION_STATUS.failed:
            this.executeEnded = Date.now();
            this.setStatus(queryStatus.status);
            if (queryStatus.message) {
              $.jHueNotify.error(queryStatus.message); // TODO: Inline instead of popup, e.g. ERROR_REGEX in Execute()
            }
            break;
          default:
            this.executeEnded = Date.now();
            this.setStatus(EXECUTION_STATUS.failed);
            console.warn('Got unknown status ' + queryStatus.status);
        }
      })
    );
  }

  addCancellable(cancellable) {
    this.cancellables.push(cancellable);
  }

  async internalExecute() {
    throw new Error('Implement in subclass!');
  }

  canExecuteInBatch() {
    throw new Error('Implement in subclass!');
  }

  getKey() {
    throw new Error('Implement in subclass!');
  }

  async cancel() {
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
        await this.cancellables.pop().cancel();
      }
      this.setStatus(EXECUTION_STATUS.canceled);
    }
  }

  async reset() {
    this.result = undefined;
    this.logs.reset();
    if (!this.isReady()) {
      try {
        await this.close();
      } catch (err) {}
    }
    this.handle = {
      statement_id: 0
    };
    this.setProgress(0);
    this.setStatus(EXECUTION_STATUS.ready);
  }

  toJs() {
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

  async close() {
    while (this.cancellables.length) {
      const nextCancellable = this.cancellables.pop();
      try {
        await nextCancellable.cancel();
      } catch (err) {
        console.warn(err);
      }
    }

    try {
      await apiHelper.closeStatement({ executable: this, silenceErrors: true });
    } catch (err) {
      console.warn('Failed closing statement');
    }
    this.setStatus(EXECUTION_STATUS.closed);
  }

  async toContext(id) {
    if (this.snippet) {
      // V1
      return {
        operationId: this.operationId,
        snippet: this.snippet.toContextJson(),
        notebook: await this.snippet.parentNotebook.toContextJson()
      };
    }

    const session = await sessionManager.getSession({ type: this.executor.connector().id });
    const statement = this.getStatement();
    const snippet = {
      type: this.executor.connector().id,
      result: {
        handle: this.handle
      },
      executor: this.executor.toJs(),
      status: this.status,
      id: id || UUID(),
      statement_raw: statement,
      statement: statement,
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
      id: this.notebookId,
      uuid: hueUtils.UUID(),
      name: '',
      isSaved: false,
      sessions: [session],
      editorWsChannel: window.WS_CHANNEL
    };

    return {
      operationId: this.operationId,
      snippet: JSON.stringify(snippet),
      notebook: JSON.stringify(notebook)
    };
  }
}
