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
import { ExecutionResult } from 'apps/notebook2/execution/executionResult';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';

/**
 *
 * @type {{running: string, canceling: string, canceled: string, expired: string, waiting: string, success: string, ready: string, available: string, closed: string, starting: string}}
 */
const EXECUTION_STATUS = {
  available: 'available',
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

const notifyUpdates = executable => {
  huePubSub.publish('hue.executable.updated', executable);
};

class ExecutableStatement {
  /**
   * @param options
   * @param {string} options.sourceType
   * @param {ContextCompute} options.compute
   * @param {ContextNamespace} options.namespace
   * @param {string} [options.statement] - Either supply a statement or a parsedStatement
   * @param {SqlStatementsParserResult} [options.parsedStatement] - Either supply a statement or a parsedStatement
   * @param {string} [options.database]
   * @param {Session[]} [options.sessions]
   */
  constructor(options) {
    this.compute = options.compute;
    this.database = options.database;
    this.namespace = options.namespace;
    this.sourceType = options.sourceType;
    this.parsedStatement = options.parsedStatement;
    this.statement = options.statement;
    this.sessions = options.sessions;
    this.handle = {
      statement_id: 0 // TODO: Get rid of need for initial handle in the backend
    };

    this.lastCancellable = undefined;
    this.status = EXECUTION_STATUS.ready;
    this.progress = 0;
  }

  getStatement() {
    return this.statement || this.parsedStatement.statement;
  }

  async execute() {
    return new Promise((resolve, reject) => {
      if (this.status !== EXECUTION_STATUS.ready) {
        reject();
        return;
      }

      let statusCheckCount = 0;
      let checkStatusTimeout = -1;

      const checkStatus = () =>
        new Promise((statusResolve, statusReject) => {
          statusCheckCount++;
          this.lastCancellable = apiHelper
            .checkExecutionStatus({ executable: this })
            .done(queryStatus => {
              this.status = queryStatus;
              switch (this.status) {
                case 'success':
                  this.progress = 99; // TODO: why 99 here (from old code)?
                  statusResolve();
                  break;
                case 'available':
                  this.progress = 100;
                  statusResolve();
                  break;
                case 'expired':
                  statusReject();
                  break;
                case 'running':
                case 'starting':
                case 'waiting':
                  notifyUpdates(this);
                  checkStatusTimeout = window.setTimeout(
                    () => {
                      checkStatus()
                        .then(statusResolve)
                        .catch(statusReject);
                    },
                    statusCheckCount > 45 ? 5000 : 1000
                  );
                  break;
                default:
                  console.warn('Got unknown status ' + queryStatus);
                  statusReject();
              }
            })
            .fail(statusReject);

          this.lastCancellable.onCancel(() => {
            window.clearTimeout(checkStatusTimeout);
          });
        }).finally(() => {
          notifyUpdates(this);
        });

      hueAnalytics.log('notebook', 'execute/' + this.sourceType);
      this.status = EXECUTION_STATUS.running;
      this.progress = 0;

      notifyUpdates(this);
      this.lastCancellable = apiHelper
        .executeStatement({
          executable: this
        })
        .done(handle => {
          this.handle = handle;

          checkStatus()
            .then(() => {
              this.result = new ExecutionResult(this);
              resolve(this.result);
            })
            .catch(error => {
              reject(error);
            });
        })
        .fail(error => {
          reject(error);
        });
    });
  }

  async cancel() {
    return new Promise(resolve => {
      if (this.lastCancellable && this.status === EXECUTION_STATUS.running) {
        hueAnalytics.log('notebook', 'cancel/' + this.sourceType);
        this.status = EXECUTION_STATUS.canceling;
        notifyUpdates(this);
        this.lastCancellable.cancel().always(() => {
          this.status = EXECUTION_STATUS.canceled;
          notifyUpdates(this);
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
      this.status = EXECUTION_STATUS.closed;
      notifyUpdates(this);
    });
  }
}

export { EXECUTION_STATUS, ExecutableStatement };
