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
   * @param {boolean} [options.isOptimizerEnabled] - Default false
   * @param {Snippet} [options.snippet] - Optional snippet for history
   */
  constructor(options) {
    this.sourceType = options.sourceType;
    this.compute = options.compute;
    this.namespace = options.namespace;
    this.database = options.database;
    this.isSqlEngine = options.isSqlEngine;
    this.isOptimizerEnabled = options.isOptimizerEnabled;
    this.executables = [];

    this.snippet = options.snippet;
  }

  getExecutables(statementDetails) {
    const allExecutablesIndex = {};
    this.executables.forEach(executable => {
      allExecutablesIndex[executable.getKey()] = executable;
    });

    const selectedExecutables = [];
    let activeDatabase = this.database();
    let currentSelectedIndex = 0;
    const newExecutables = statementDetails.precedingStatements
      .concat(statementDetails.activeStatement, statementDetails.followingStatements)
      .map(parsedStatement => {
        if (/USE/i.test(parsedStatement.firstToken)) {
          const dbMatch = parsedStatement.statement.match(/use\s+([^;]+)/i);
          if (dbMatch) {
            activeDatabase = dbMatch[1];
          }
        }
        let executable = new SqlExecutable({
          parsedStatement: parsedStatement,
          database: activeDatabase,
          executor: this
        });
        if (allExecutablesIndex[executable.getKey()]) {
          executable = allExecutablesIndex[executable.getKey()];
          executable.parsedStatement = parsedStatement;
          delete allExecutablesIndex[executable.getKey()];
        }
        if (
          currentSelectedIndex < statementDetails.selectedStatements.length &&
          parsedStatement === statementDetails.selectedStatements[currentSelectedIndex]
        ) {
          selectedExecutables.push(executable);
          currentSelectedIndex++;
        }
        return executable;
      });

    const lostExecutables = Object.keys(allExecutablesIndex).map(key => allExecutablesIndex[key]);
    return {
      all: newExecutables,
      lost: lostExecutables,
      selected: selectedExecutables
    };
  }

  toJs() {
    return {
      executables: this.executables.map(executable => executable.toJs())
    };
  }

  update(statementDetails, beforeExecute) {
    const executables = this.getExecutables(statementDetails);

    // Cancel any "lost" executables and any batch chain it's part of
    executables.lost.forEach(lostExecutable => {
      lostExecutable.lost = true;
      lostExecutable.cancelBatchChain();
    });

    // Cancel any intersecting batch chains and create a new chain if just before execute
    if (beforeExecute) {
      executables.selected.forEach(executable => executable.cancelBatchChain());

      let previous = undefined;
      executables.selected.forEach(executable => {
        if (previous) {
          executable.previousExecutable = previous;
          previous.nextExecutable = executable;
        }
        previous = executable;
      });
    }

    // Update the executables list
    this.executables = executables.all;

    this.executables.forEach(executable => executable.notify());

    return executables.selected[0];
  }
}

export default Executor;
