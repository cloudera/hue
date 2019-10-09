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
import sessionManager from 'apps/notebook2/execution/sessionManager';

// TODO: Remove, debug var
window.sessionManager = sessionManager;

class Executor {
  /**
   * @param options
   * @param {boolean} [options.isSqlEngine] (default false)
   * @param {string} options.sourceType
   * @param {ContextCompute} options.compute
   * @param {ContextNamespace} options.namespace
   * @param {string} options.statement
   * @param {string} [options.database]
   */
  constructor(options) {
    this.sourceType = options.sourceType;
    this.compute = options.compute;
    this.namespace = options.namespace;
    this.database = options.database;
    this.isSqlEngine = options.isSqlEngine;
    this.executables = [];
  }

  update(statementDetails) {
    const newExecutables = statementDetails.precedingStatements
      .concat(statementDetails.activeStatement, statementDetails.followingStatements)
      .map(
        parsedStatement =>
          new SqlExecutable({
            parsedStatement: parsedStatement,
            database: this.database(),
            executor: this
          })
      );

    const existingExecutableIndex = {};
    this.executables.forEach(executable => {
      existingExecutableIndex[executable.getKey()] = executable;
    });

    let activeExecutable = new SqlExecutable({
      parsedStatement: statementDetails.activeStatement,
      database: this.database(),
      executor: this
    });

    if (existingExecutableIndex[activeExecutable.getKey()]) {
      activeExecutable = existingExecutableIndex[activeExecutable.getKey()];
    }

    // Refresh the executables list
    this.executables = newExecutables.map(newExecutable => {
      let actualExecutable = newExecutable;
      const existingExecutable = existingExecutableIndex[newExecutable.getKey()];
      if (existingExecutable) {
        actualExecutable = existingExecutable;
        delete existingExecutableIndex[newExecutable.getKey()];
      }
      return actualExecutable;
    });

    // Cancel lost executables
    Object.keys(existingExecutableIndex).forEach(key => {
      existingExecutableIndex[key].cancel();
    });

    return activeExecutable;
  }
}

export default Executor;
