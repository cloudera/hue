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

import Executor from 'apps/notebook2/execution/executor';
import { syncSqlExecutables } from 'apps/notebook2/execution/utils';
import sqlStatementsParser from 'parse/sqlStatementsParser';

const mockExecutor = (mock: unknown): Executor => mock as Executor;

describe('utils.ts', () => {
  it('create new when no executables present', () => {
    const executor = mockExecutor({
      database: () => 'someDb',
      executables: []
    });
    const statements = sqlStatementsParser.parse('SELECT 1;');

    const result = syncSqlExecutables(executor, {
      precedingStatements: [],
      activeStatement: statements[0],
      followingStatements: [],
      selectedStatements: [statements[0]]
    });

    expect(result.edited.length).toEqual(0);
    expect(result.lost.length).toEqual(0);
    expect(result.all.length).toEqual(1);
    expect(result.selected.length).toEqual(1);
    expect(result.all[0].database).toEqual('someDb');
    expect(result.all[0].parsedStatement).toEqual(statements[0]);
  });

  it('should reuse existing executables when nothing has changed', () => {
    const statements = sqlStatementsParser.parse('SELECT 1;');
    const executor = mockExecutor({
      database: () => 'someDb',
      executables: [
        {
          database: 'someDb',
          parsedStatement: JSON.parse(JSON.stringify(statements[0]))
        }
      ]
    });
    const result = syncSqlExecutables(executor, {
      precedingStatements: [],
      activeStatement: statements[0],
      followingStatements: [],
      selectedStatements: [statements[0]]
    });

    expect(result.edited.length).toEqual(0);
    expect(result.lost.length).toEqual(0);
    expect(result.all.length).toEqual(1);
    expect(result.selected.length).toEqual(1);
    expect(result.all[0]).toEqual(executor.executables[0]);
    expect(result.all[0].parsedStatement).toEqual(statements[0]);
  });

  it('should mark existing executables as edited when the database has changed', () => {
    const executor = mockExecutor({
      database: () => 'someOtherDb',
      executables: [
        {
          database: 'someDb',
          parsedStatement: sqlStatementsParser.parse('SELECT 1;')[0]
        }
      ]
    });

    const newStatements = sqlStatementsParser.parse('SELECT 2;');
    const result = syncSqlExecutables(executor, {
      precedingStatements: [],
      activeStatement: newStatements[0],
      followingStatements: [],
      selectedStatements: [newStatements[0]]
    });

    expect(executor.executables[0].database).toEqual('someOtherDb');
    expect(result.edited.length).toEqual(1);
    expect(result.lost.length).toEqual(0);
    expect(result.all.length).toEqual(1);
    expect(result.selected.length).toEqual(1);
    expect(result.edited[0]).toEqual(executor.executables[0]);
    expect(result.edited[0].parsedStatement).toEqual(newStatements[0]);
  });

  it('should mark existing executables as edited when same index and the statement has changed', () => {
    const executor = mockExecutor({
      database: () => 'someDb',
      executables: [
        {
          database: 'someDb',
          parsedStatement: sqlStatementsParser.parse('SELECT 1;')[0]
        }
      ]
    });

    const newStatements = sqlStatementsParser.parse('SELECT 2;');
    const result = syncSqlExecutables(executor, {
      precedingStatements: [],
      activeStatement: newStatements[0],
      followingStatements: [],
      selectedStatements: [newStatements[0]]
    });

    expect(result.edited.length).toEqual(1);
    expect(result.lost.length).toEqual(0);
    expect(result.all.length).toEqual(1);
    expect(result.selected.length).toEqual(1);
    expect(result.edited[0]).toEqual(executor.executables[0]);
    expect(result.edited[0].parsedStatement).toEqual(newStatements[0]);
  });

  it('should not mark existing executables as edited when nothing has changed', () => {
    const executor = mockExecutor({
      database: () => 'someDb',
      executables: [
        {
          database: 'someDb',
          parsedStatement: sqlStatementsParser.parse('SELECT 1;')[0]
        }
      ]
    });

    const newStatements = sqlStatementsParser.parse('SELECT 1;');
    const result = syncSqlExecutables(executor, {
      precedingStatements: [],
      activeStatement: newStatements[0],
      followingStatements: [],
      selectedStatements: [newStatements[0]]
    });

    expect(result.edited.length).toEqual(0);
    expect(result.lost.length).toEqual(0);
    expect(result.all.length).toEqual(1);
    expect(result.selected.length).toEqual(1);
  });

  it('should add executables when a statement is added', () => {
    const executor = mockExecutor({
      database: () => 'someDb',
      executables: [
        {
          database: 'someDb',
          parsedStatement: sqlStatementsParser.parse('SELECT 1;')[0]
        }
      ]
    });

    const newStatements = sqlStatementsParser.parse('SELECT 1;SELECT 2');
    const result = syncSqlExecutables(executor, {
      precedingStatements: [newStatements[0]],
      activeStatement: newStatements[1],
      followingStatements: [],
      selectedStatements: [newStatements[1]]
    });

    expect(result.edited.length).toEqual(0);
    expect(result.lost.length).toEqual(0);
    expect(result.all.length).toEqual(2);
    expect(result.selected.length).toEqual(1);
  });

  it('should mark removed statements as lost', () => {
    const initialStatements = sqlStatementsParser.parse('SELECT 1;SELECT 2;');
    const executor = mockExecutor({
      database: () => 'someDb',
      executables: [
        {
          database: 'someDb',
          parsedStatement: initialStatements[0]
        },
        {
          database: 'someDb',
          parsedStatement: initialStatements[1]
        }
      ]
    });
    const newStatements = sqlStatementsParser.parse('SELECT 1;');
    const result = syncSqlExecutables(executor, {
      precedingStatements: [],
      activeStatement: newStatements[0],
      followingStatements: [],
      selectedStatements: [newStatements[0]]
    });

    expect(result.edited.length).toEqual(0);
    expect(result.lost.length).toEqual(1);
    expect(result.all.length).toEqual(1);
    expect(result.selected.length).toEqual(1);
    expect(result.lost[0].parsedStatement.statement).toEqual('SELECT 2;');
  });
});
