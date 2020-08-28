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

import { ExecuteApiResponse, executeStatement } from 'apps/notebook2/execution/apiUtils';
import Executable, { ExecutableRaw } from 'apps/notebook2/execution/executable';
import Executor from 'apps/notebook2/execution/executor';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';

const BATCHABLE_STATEMENT_TYPES = /ALTER|CREATE|DELETE|DROP|GRANT|INSERT|INVALIDATE|LOAD|SET|TRUNCATE|UPDATE|UPSERT|USE/i;

const SELECT_END_REGEX = /([^;]*)([;]?[^;]*)/;
const ERROR_REGEX = /line ([0-9]+)(:([0-9]+))?/i;

export interface SqlExecutableRaw extends ExecutableRaw {
  database: string;
  parsedStatement: ParsedSqlStatement;
}

export default class SqlExecutable extends Executable {
  database: string;
  parsedStatement: ParsedSqlStatement;

  constructor(options: {
    executor: Executor;
    database: string;
    parsedStatement: ParsedSqlStatement;
  }) {
    super(options);
    this.database = options.database;
    this.parsedStatement = options.parsedStatement;
  }

  getStatement(): string {
    let statement = this.parsedStatement.statement;
    if (
      this.parsedStatement.firstToken &&
      this.parsedStatement.firstToken.toLowerCase() === 'select' &&
      this.executor.defaultLimit &&
      !isNaN(this.executor.defaultLimit()) &&
      this.executor.defaultLimit() > 0 &&
      !/\slimit\s[0-9]/i.test(statement)
    ) {
      const endMatch = statement.match(SELECT_END_REGEX);
      if (endMatch) {
        statement = endMatch[1] + ' LIMIT ' + this.executor.defaultLimit();
        if (endMatch[2]) {
          statement += endMatch[2];
        }
      }
    }

    return statement;
  }

  async internalExecute(): Promise<ExecuteApiResponse> {
    return await executeStatement({
      executable: this,
      silenceErrors: true
    });
  }

  getKey(): string {
    return this.database + '_' + this.parsedStatement.statement;
  }

  canExecuteInBatch(): boolean {
    return this.parsedStatement && BATCHABLE_STATEMENT_TYPES.test(this.parsedStatement.firstToken);
  }

  static fromJs(executor: Executor, executableRaw: SqlExecutableRaw): SqlExecutable {
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

  toJs(): SqlExecutableRaw {
    const executableJs = (super.toJs() as unknown) as SqlExecutableRaw;
    executableJs.database = this.database;
    executableJs.parsedStatement = this.parsedStatement;
    executableJs.type = 'sqlExecutable';
    return executableJs;
  }

  toJson(): string {
    return JSON.stringify({
      id: this.id,
      statement: this.getStatement(),
      database: this.database
    });
  }

  adaptError(err: string): string {
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

      return adjustedErr;
    }
    return err;
  }
}
