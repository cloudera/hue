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
import sqlStatementsParser from 'parse/sqlStatementsParser';

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

  async internalExecute(session) {
    return await apiHelper.executeStatement({
      executable: this,
      session: session
    });
  }

  getKey() {
    return this.database + '_' + this.parsedStatement.statement;
  }

  /**
   *
   * @param options
   * @param options.database
   * @param options.statement
   * @param options.executor
   * @param options.sourceType
   * @param options.compute
   * @param options.namespace
   * @return {Array}
   */
  static fromStatement(options) {
    const result = [];
    let database = options.database;
    sqlStatementsParser.parse(options.statement).forEach(parsedStatement => {
      // If there's no first token it's a trailing comment
      if (parsedStatement.firstToken) {
        let skip = false;
        // TODO: Do we want to send USE statements separately or do we want to send database as param instead?
        if (/USE/i.test(parsedStatement.firstToken)) {
          const dbMatch = parsedStatement.statement.match(/use\s+([^;]+)/i);
          if (dbMatch) {
            database = dbMatch[1];
            skip = this.sourceType === 'impala' || this.sourceType === 'hive';
          }
        }
        if (!skip) {
          result.push(
            new SqlExecutable({
              executor: options.executor,
              sourceType: options.sourceType,
              compute: options.compute,
              namespace: options.namespace,
              database: database,
              parsedStatement: parsedStatement
            })
          );
        }
      }
    });
    return result;
  }

  canExecuteInBatch() {
    return this.parsedStatement && BATCHABLE_STATEMENT_TYPES.test(this.parsedStatement.firstToken);
  }
}
