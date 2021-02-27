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

import { ExecuteApiResponse, executeStatement } from 'apps/editor/execution/api';
import Executable, { ExecutableRaw } from 'apps/editor/execution/executable';
import { ExecutionError } from 'apps/editor/execution/executionLogs';
import Executor from 'apps/editor/execution/executor';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { VariableIndex } from '../components/variableSubstitution/types';

const BATCHABLE_STATEMENT_TYPES = /ALTER|WITH|REFRESH|CREATE|DELETE|DROP|GRANT|INSERT|INVALIDATE|LOAD|SET|TRUNCATE|UPDATE|UPSERT|USE/i;

const SELECT_END_REGEX = /([^;]*)([;]?[^;]*)/;
const ERROR_REGEX = /line ([0-9]+)(:([0-9]+))?/i;

export interface SqlExecutableRaw extends ExecutableRaw {
  database: string;
  parsedStatement: ParsedSqlStatement;
}

const substituteVariables = (statement: string, variables: VariableIndex): string => {
  if (!Object.keys(variables).length) {
    return statement;
  }

  const variablesString = Object.values(variables)
    .map(variable => variable.name)
    .join('|');

  return statement.replace(
    RegExp('([^\\\\])?\\${(' + variablesString + ')(=[^}]*)?}', 'g'),
    (match, p1, p2) => {
      const { value, type, meta } = variables[p2];
      const pad = type === 'datetime-local' && value.length === 16 ? ':00' : ''; // Chrome drops the seconds from the timestamp when it's at 0 second.
      const isValuePresent = //If value is string there is a need to check whether it is empty
        typeof value === 'string' ? value : value !== undefined && value !== null;
      return p1 + (isValuePresent ? value + pad : meta.placeholder);
    }
  );
};

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

  getRawStatement(): string {
    return this.parsedStatement.statement;
  }

  getStatement(): string {
    let statement = this.getRawStatement();

    if (
      this.parsedStatement.firstToken &&
      this.parsedStatement.firstToken.toLowerCase() === 'select' &&
      this.executor.defaultLimit &&
      !isNaN(this.executor.defaultLimit()) &&
      this.executor.defaultLimit() > 0 &&
      /\sfrom\s/i.test(statement) &&
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

    if (this.executor.variables) {
      statement = substituteVariables(statement, this.executor.variables);
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
    if (executableRaw.logs.errors) {
      executable.logs.errors = executableRaw.logs.errors.map(error => executable.adaptError(error));
    }
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
      parsedStatement: this.parsedStatement,
      statement: this.getStatement(),
      database: this.database
    });
  }

  adaptError(message: string): ExecutionError {
    const match = ERROR_REGEX.exec(message);
    if (match) {
      const row = parseInt(match[1]);
      const column = (match[3] && parseInt(match[3])) || 0;

      return { message, column: column || 0, row };
    }
    return { message, column: 0, row: this.parsedStatement.location.first_line };
  }
}
