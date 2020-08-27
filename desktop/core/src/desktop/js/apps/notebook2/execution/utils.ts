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

import Executable from 'apps/notebook2/execution/executable';
import Executor from 'apps/notebook2/execution/executor';
import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
import { StatementDetails } from 'parse/types';

export interface SyncSqlExecutablesResult {
  all: SqlExecutable[];
  edited: SqlExecutable[];
  lost: SqlExecutable[];
  selected: SqlExecutable[];
}

export const syncSqlExecutables = (
  executor: Executor,
  statementDetails: StatementDetails
): SyncSqlExecutablesResult => {
  const allNewStatements = statementDetails.precedingStatements.concat(
    statementDetails.activeStatement,
    statementDetails.followingStatements
  );

  const existingExecutables: (Executable | undefined)[] = executor.executables.concat();

  const result: SyncSqlExecutablesResult = {
    all: [],
    edited: [],
    lost: [],
    selected: []
  };

  let activeDatabase = executor.database();
  let currentSelectedIndex = 0;
  allNewStatements.forEach((parsedStatement, index) => {
    if (/USE/i.test(parsedStatement.firstToken)) {
      const dbMatch = parsedStatement.statement.match(/use\s+([^;]+)/i);
      if (dbMatch) {
        activeDatabase = dbMatch[1];
      }
    }

    let executable = existingExecutables[index] as SqlExecutable;
    if (executable) {
      const edited =
        executable.database !== activeDatabase ||
        parsedStatement.statement !== executable.parsedStatement.statement;
      existingExecutables[index] = undefined; // undefined = not lost below
      executable.database = activeDatabase;
      executable.parsedStatement = parsedStatement;
      if (edited) {
        result.edited.push(executable);
      }
    } else {
      executable = new SqlExecutable({
        parsedStatement: parsedStatement,
        database: activeDatabase,
        executor: executor
      });
    }
    result.all.push(executable);

    if (
      currentSelectedIndex < statementDetails.selectedStatements.length &&
      parsedStatement === statementDetails.selectedStatements[currentSelectedIndex]
    ) {
      result.selected.push(executable);
      currentSelectedIndex++;
    }
  });

  result.lost = existingExecutables.filter(
    executable => typeof executable !== 'undefined'
  ) as SqlExecutable[];

  return result;
};
