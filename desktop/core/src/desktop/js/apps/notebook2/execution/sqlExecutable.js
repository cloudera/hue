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
import Executable from 'apps/notebook2/execution/executable';

const BATCHABLE_STATEMENT_TYPES = /ALTER|CREATE|DELETE|DROP|GRANT|INSERT|INVALIDATE|LOAD|SET|TRUNCATE|UPDATE|UPSERT|USE/i;

export default class SqlExecutable extends Executable {
  /**
   * @param options
   * @param {Executor} options.executor
   *
   * @param {string} options.database
   * @param {SqlStatementsParserResult} options.parsedStatement
   */
  constructor(options) {
    super(options);
    this.database = options.database;
    this.parsedStatement = options.parsedStatement;
  }

  getStatement() {
    return this.statement || this.parsedStatement.statement;
  }

  async internalExecute() {
    return await apiHelper.executeStatement({
      executable: this,
      silenceErrors: true
    });
  }

  getKey() {
    return this.database + '_' + this.parsedStatement.statement;
  }

  canExecuteInBatch() {
    return this.parsedStatement && BATCHABLE_STATEMENT_TYPES.test(this.parsedStatement.firstToken);
  }

  static fromJs(executor, executableRaw) {
    const executable = new SqlExecutable({
      database: executableRaw.database,
      executor: executor,
      parsedStatement: executableRaw.parsedStatement
    });
    executable.executeEnded = executableRaw.executeEnded;
    executable.executeStarted = executableRaw.executeStarted;
    executable.handle = executableRaw.handle;
    executable.history = executableRaw.history;
    executable.id = executableRaw.id;
    executable.logs.errors = executableRaw.logs.errors;
    executable.logs.jobs = executableRaw.logs.jobs;
    executable.lost = executableRaw.lost;
    executable.observerState = executableRaw.observerState || {};
    executable.operationId = executableRaw.history && executableRaw.history.uuid;
    executable.progress = executableRaw.progress;
    executable.status = executableRaw.status;
    return executable;
  }

  toJs() {
    const executableJs = super.toJs();
    executableJs.database = this.database;
    executableJs.parsedStatement = this.parsedStatement;
    executableJs.type = 'sqlExecutable';
    return executableJs;
  }

  // TODO: Use this for execute instead of snippet
  toJson() {
    return JSON.stringify({
      id: this.id,
      statement: this.parsedStatement.statement,
      database: this.database
      // session:
    });
  }
}
