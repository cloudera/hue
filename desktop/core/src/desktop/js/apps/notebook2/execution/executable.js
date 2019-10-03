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

    this.lastCancellable = undefined;
    this.notifyThrottle = -1;
  }

  setStatus(status) {
    this.status = status;
    this.notify();
  }

  setProgress(progress) {
    this.progress = progress;
    this.notify();
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
    } catch (err) {
      this.setStatus(EXECUTION_STATUS.failed);
      throw err;
    }
  }

  checkStatus(statusCheckCount) {
    if (!statusCheckCount) {
      statusCheckCount = 0;
    }
    statusCheckCount++;
    let checkStatusTimeout = -1;
    this.lastCancellable = apiHelper
      .checkExecutionStatus({ executable: this })
      .done(queryStatus => {
        switch (this.status) {
          case EXECUTION_STATUS.success:
            this.setStatus(queryStatus);
            this.setProgress(99); // TODO: why 99 here (from old code)?
            break;
          case EXECUTION_STATUS.available:
            this.setStatus(queryStatus);
            this.setProgress(100);
            if (!this.result && this.handle.has_result_set) {
              this.result = new ExecutionResult(this);
              this.result.fetchRows();
            }
            break;
          case EXECUTION_STATUS.expired:
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
            console.warn('Got unknown status ' + queryStatus);
        }
      });

    this.lastCancellable.onCancel(() => {
      window.clearTimeout(checkStatusTimeout);
    });
  }

  setLastCancellable(lastCancellable) {
    this.lastCancellable = lastCancellable;
  }

  async internalExecute(session) {
    throw new Error('Implement in subclass!');
  }

  canExecuteInBatch() {
    throw new Error('Implement in subclass!');
  }

  async cancel() {
    return new Promise(resolve => {
      if (this.lastCancellable && this.status === EXECUTION_STATUS.running) {
        hueAnalytics.log('notebook', 'cancel/' + this.sourceType);
        this.setStatus(EXECUTION_STATUS.canceling);
        this.lastCancellable.cancel().always(() => {
          this.setStatus(EXECUTION_STATUS.canceled);
          resolve();
        });
        this.lastCancellable = undefined;
      } else {
        resolve();
      }
    });
  }

  async close() {
    return new Promise(resolve => {
      if (this.status === EXECUTION_STATUS.running) {
        this.cancel().finally(resolve);
      } else if (this.status !== EXECUTION_STATUS.closed) {
        apiHelper.closeStatement({ executable: this }).finally(resolve);
      }
    }).finally(() => {
      this.setStatus(EXECUTION_STATUS.closed);
    });
  }
}
