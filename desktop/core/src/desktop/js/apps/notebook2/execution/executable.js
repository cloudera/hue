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

export default class Executable {
  /**
   * @param options
   * @param {string} options.sourceType
   * @param {ContextCompute} options.compute
   * @param {ContextNamespace} options.namespace
   * @param {string} [options.statement] - Either supply a statement or a parsedStatement
   * @param {SqlStatementsParserResult} [options.parsedStatement] - Either supply a statement or a parsedStatement
   * @param {string} [options.database]
   * @param {Executor} options.executor
   * @param {Session[]} [options.sessions]
   */
  constructor(options) {
    this.compute = options.compute;
    this.namespace = options.namespace;
    this.sourceType = options.sourceType;
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

  async execute() {
    if (this.status !== EXECUTION_STATUS.ready) {
      return;
    }
    this.executeStarted = Date.now();

    this.setStatus(EXECUTION_STATUS.running);
    this.setProgress(0);

    try {
      const session = await sessionManager.getSession({ type: this.sourceType });
      hueAnalytics.log('notebook', 'execute/' + this.sourceType);
      this.handle = await this.internalExecute(session);

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
      apiHelper.checkExecutionStatus({ executable: this }).done(queryStatus => {
        switch (this.status) {
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

  async cancel() {
    if (this.cancellables.length && this.status === EXECUTION_STATUS.running) {
      hueAnalytics.log('notebook', 'cancel/' + this.sourceType);
      this.setStatus(EXECUTION_STATUS.canceling);
      while (this.cancellables.length) {
        await this.cancellables.pop().cancel();
      }
      this.setStatus(EXECUTION_STATUS.canceled);
    }
  }

  async close() {
    while (this.cancellables.length) {
      await this.cancellables.pop().cancel();
    }

    return new Promise(resolve => {
      apiHelper.closeStatement({ executable: this }).finally(() => {
        this.setStatus(EXECUTION_STATUS.closed);
        resolve();
      });
    });
  }
}
