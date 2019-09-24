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

import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
import { EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import huePubSub from 'utils/huePubSub';
import sessionManager from 'apps/notebook2/execution/sessionManager';

// TODO: Remove, debug var
window.sessionManager = sessionManager;

const EXECUTION_FLOW = {
  step: 'step',
  batch: 'batch'
  // batchNoBreak: 'batchNoBreak'
};

export const EXECUTOR_UPDATED_EVENT = 'hue.executor.updated';

class Executor {
  /**
   * @param options
   * @param {boolean} [options.isSqlEngine] (default false)
   * @param {string} options.sourceType
   * @param {ContextCompute} options.compute
   * @param {ContextNamespace} options.namespace
   * @param {EXECUTION_FLOW} [options.executionFlow] (default EXECUTION_FLOW.batch)
   * @param {string} options.statement
   * @param {string} [options.database]
   */
  constructor(options) {
    this.sourceType = options.sourceType;
    this.compute = options.compute;
    this.namespace = options.namespace;
    this.database = options.database;
    this.isSqlEngine = options.isSqlEngine;
    this.executionFlow = this.isSqlEngine
      ? options.executionFlow || EXECUTION_FLOW.batch
      : EXECUTION_FLOW.step;

    this.toExecute = [];
    this.currentExecutable = undefined;
    this.executed = [];

    if (this.isSqlEngine) {
      this.toExecute = SqlExecutable.fromStatement(options);
    } else {
      throw new Error('Not implemented yet');
    }

    huePubSub.subscribe('hue.executable.updated', executable => {
      if (
        executable === this.currentExecutable ||
        this.executed.some(executed => executed === executable)
      ) {
        huePubSub.publish(EXECUTOR_UPDATED_EVENT, {
          executable: executable,
          executor: this
        });
      }
    });
  }

  isRunning() {
    return this.currentExecutable && this.currentExecutable.status === EXECUTION_STATUS.running;
  }

  async cancel() {
    if (this.isRunning()) {
      return await this.currentExecutable.cancel();
    }
  }

  async executeNext() {
    return new Promise((resolve, reject) => {
      const executeBatch = () => {
        if (this.toExecute.length === 0) {
          reject();
        } else {
          this.currentExecutable = this.toExecute.shift();
          this.currentExecutable
            .execute()
            .then(executionResult => {
              this.executed.push(this.currentExecutable);
              this.currentExecutable = undefined;

              if (this.canExecuteNextInBatch()) {
                this.executeNext()
                  .then(executeBatch)
                  .catch(reject);
              } else {
                resolve(executionResult);
              }
            })
            .catch(reject);
        }
      };

      executeBatch();
    });
  }

  canExecuteNextInBatch() {
    return (
      !this.executed.length ||
      (this.isSqlEngine &&
        this.executionFlow !== EXECUTION_FLOW.step &&
        this.currentExecutable &&
        this.currentExecutable.canExecuteInBatch())
    );
  }
}

export default Executor;
