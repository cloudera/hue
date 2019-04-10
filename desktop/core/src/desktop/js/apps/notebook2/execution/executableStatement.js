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
import { ExecutionResult } from "apps/notebook2/execution/executionResult";
import hueAnalytics from 'utils/hueAnalytics';

/**
 *  ready +----> executing +----> done +----> closed
 *                   +     |
 *                   |     +----> fail
 *                   |
 *                   +----> canceling +----> canceled
 *
 * @type { { canceling: string, canceled: string, fail: string, ready: string, executing: string, done: string } }
 */
const EXECUTION_STATUS = {
  ready: 'ready',
  executing: 'executing',
  canceled: 'canceled',
  canceling: 'canceling',
  closed: 'closed',
  done: 'done',
  fail: 'fail'
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
   */
  constructor(options) {
    this.compute = options.compute;
    this.database = options.database;
    this.namespace = options.namespace;
    this.sourceType = options.sourceType;
    this.parsedStatement = options.parsedStatement;
    this.statement = options.statement;
    this.handle = {
      statement_id: 0 // TODO: Get rid of need for initial handle in the backend
    };

    this.executionResult = undefined;
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

      const checkStatus = () => new Promise( (resolve, reject) => {
        statusCheckCount++;
        this.lastCancellable = apiHelper.checkExecutionStatus({ executable: this }).done(queryStatus => {
          switch (queryStatus) {
            case 'success':
              this.progress = 99; // TODO: why 99 here (from old code)?
              resolve();
              break;
            case 'available':
              this.progress = 100;
              resolve();
              break;
            case 'expired':
              reject();
              break;
            case 'running':
            case 'starting':
            case 'waiting':
              checkStatusTimeout = window.setTimeout(() => {
                checkStatus().then(resolve).catch(reject);
              }, statusCheckCount > 45 ? 5000 : 1000);
              break;
            default:
              console.warn('Got unknown status ' + queryStatus);
              reject();
          }
        }).fail(reject);

        this.lastCancellable.onCancel(() => {
          window.clearTimeout(checkStatusTimeout);
        })
      });

      hueAnalytics.log('notebook', 'execute/' + this.sourceType);
      this.status = EXECUTION_STATUS.executing;

      this.lastCancellable = apiHelper
        .executeStatement({
          executable: this
        })
        .done(handle => {
          this.handle = handle;

          checkStatus().then(() => {
            this.result = new ExecutionResult(this);
            this.status = EXECUTION_STATUS.done;
            resolve(this.result);
          }).catch(error => {
            this.status = EXECUTION_STATUS.fail;
            reject(error);
          });
        })
        .fail(error => {
          this.status = EXECUTION_STATUS.fail;
          reject(error);
        });
    })
  }

  async cancel() {
    return new Promise(resolve => {
      if (this.lastCancellable && this.status === EXECUTION_STATUS.executing) {
        hueAnalytics.log('notebook', 'cancel/' + this.sourceType);
        this.status = EXECUTION_STATUS.canceling;
        this.lastCancellable.cancel().always(() => {
          this.status = EXECUTION_STATUS.canceled;
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
      if (this.status === EXECUTION_STATUS.executing) {
        this.cancel().finally(resolve)
      } else if (this.status === EXECUTION_STATUS.done) {
        apiHelper.closeStatement({ executable: this }).finally(resolve);
      }
    }).finally(() => {
      this.status = EXECUTION_STATUS.closed;
    });
  }
}

export { EXECUTION_STATUS, ExecutableStatement };
