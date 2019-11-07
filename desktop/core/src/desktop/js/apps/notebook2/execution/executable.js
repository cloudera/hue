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

import apiHelper from 'api/apiHelper';
import ExecutionResult from 'apps/notebook2/execution/executionResult';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import ExecutionLogs from 'apps/notebook2/execution/executionLogs';

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
  canceled: 'canceled',
  canceling: 'canceling',
  closed: 'closed'
};

export const EXECUTABLE_UPDATED_EVENT = 'hue.executable.updated';

const ERROR_REGEX = /line ([0-9]+)(\:([0-9]+))?/i;

export default class Executable {
  /**
   * @param options
   * @param {string} [options.statement] - Either supply a statement or a parsedStatement
   * @param {Executor} options.executor
   * @param {Session[]} [options.sessions]
   */
  constructor(options) {
    this.executor = options.executor;

    this.handle = {
      statement_id: 0 // TODO: Get rid of need for initial handle in the backend
    };
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
    this.status = status;
    this.notify();
  }

  setProgress(progress) {
    this.progress = progress;
    this.notify();
  }

  getExecutionTime() {
    return (this.executeEnded || Date.now()) - this.executeStarted;
  }

  notify() {
    window.clearTimeout(this.notifyThrottle);
    this.notifyThrottle = window.setTimeout(() => {
      huePubSub.publish(EXECUTABLE_UPDATED_EVENT, this);
    }, 1);
  }

  isReady() {
    return (
      this.status === EXECUTION_STATUS.ready ||
      this.status === EXECUTION_STATUS.closed ||
      this.status === EXECUTION_STATUS.canceled
    );
  }

  isRunning() {
    return this.status === EXECUTION_STATUS.running;
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

    try {
      const session = await sessionManager.getSession({ type: this.executor.sourceType() });
      hueAnalytics.log('notebook', 'execute/' + this.executor.sourceType());
      try {
        this.handle = await this.internalExecute(session);
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
          this.result.fetchRows();
        }
      }

      this.checkStatus();
      this.logs.fetchLogs();
    } catch (err) {
      this.setStatus(EXECUTION_STATUS.failed);
      throw err;
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
        switch (queryStatus) {
          case EXECUTION_STATUS.success:
            this.executeEnded = Date.now();
            this.setStatus(queryStatus);
            this.setProgress(99); // TODO: why 99 here (from old code)?
            break;
          case EXECUTION_STATUS.available:
            this.executeEnded = Date.now();
            this.setStatus(queryStatus);
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
          case EXECUTION_STATUS.expired:
            this.executeEnded = Date.now();
            this.setStatus(queryStatus);
            break;
          case EXECUTION_STATUS.running:
          case EXECUTION_STATUS.starting:
          case EXECUTION_STATUS.waiting:
            this.setStatus(queryStatus);
            checkStatusTimeout = window.setTimeout(
              () => {
                this.checkStatus(statusCheckCount);
              },
              statusCheckCount > 45 ? 5000 : 1000
            );
            break;
          default:
            this.executeEnded = Date.now();
            console.warn('Got unknown status ' + queryStatus);
        }
      })
    );
  }

  addCancellable(cancellable) {
    this.cancellables.push(cancellable);
  }

  async internalExecute(session) {
    throw new Error('Implement in subclass!');
  }

  canExecuteInBatch() {
    throw new Error('Implement in subclass!');
  }

  getKey() {
    throw new Error('Implement in subclass!');
  }

  async cancel() {
    if (this.cancellables.length && this.status === EXECUTION_STATUS.running) {
      hueAnalytics.log('notebook', 'cancel/' + this.executor.sourceType());
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
      type: 'executable',
      handle: this.handle,
      status: this.status,
      progress: this.progress,
      logs: this.logs.toJs(),
      executeStarted: this.executeStarted,
      executeEnded: this.executeEnded,
      observerState: state,
      lost: this.lost
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
}
