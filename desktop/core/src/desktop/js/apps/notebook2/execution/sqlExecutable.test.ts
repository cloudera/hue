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

import { CancellablePromise } from 'api/cancellablePromise';
import { CHECK_STATUS_API, CREATE_SESSION_API, EXECUTE_API_PREFIX, GET_LOGS_API } from 'api/urls';

import Executor from 'apps/notebook2/execution/executor';
import SqlExecutable from './sqlExecutable';
import { EXECUTION_STATUS } from './executable';
import sessionManager from './sessionManager';
import * as ApiUtils from 'api/apiUtilsV2';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';

describe('sqlExecutable.js', () => {
  afterEach(() => {
    sessionManager.knownSessionPromises = {};
  });

  const mockExecutor = (mock: unknown): Executor => mock as Executor;

  const createParsedStatement = (statement: string, firstToken: string): ParsedSqlStatement => ({
    location: { first_line: 0, first_column: 0, last_line: 1, last_column: 0 },
    firstToken: firstToken,
    statement: statement,
    type: 'statement'
  });

  const createSubject = (
    statement: string | ParsedSqlStatement,
    limit?: number,
    dialect?: string
  ): SqlExecutable => {
    if (typeof statement === 'string') {
      return new SqlExecutable({
        database: 'default',
        parsedStatement: createParsedStatement(statement, 'seleft'),
        executor: mockExecutor({
          connector: () => ({ id: 'test', dialect: dialect || '' }),
          compute: () => ({ id: 'test' }),
          namespace: () => ({ id: 'test' }),
          defaultLimit: () => limit,
          toJs: () => ({})
        })
      });
    }

    return new SqlExecutable({
      database: 'default',
      parsedStatement: statement,
      executor: mockExecutor({
        defaultLimit: () => limit
      })
    });
  };

  const SELECT_STATEMENT = 'SELECT * FROM customers';

  it('should handle strings statements', () => {
    const subject = createSubject(SELECT_STATEMENT);

    expect(subject.getStatement()).toEqual(SELECT_STATEMENT);
  });

  it('should handle parsed statements', () => {
    const subject = createSubject(createParsedStatement(SELECT_STATEMENT, 'SELECT'));

    expect(subject.getStatement()).toEqual(SELECT_STATEMENT);
  });

  it('should set the correct status after successful execute', async () => {
    const subject = createSubject(SELECT_STATEMENT, undefined, 'impala');

    let createSessionApiHit = -1;
    let executeApiHit = -1;
    let checkStatusApiHit = -1;
    let getLogsApiHit = -1;

    let currentApiHit = 0;

    let logsResolve: (data: unknown) => void;
    const logsPromise = new CancellablePromise<unknown>(resolve => {
      logsResolve = resolve;
    });

    let statusResolve: (data: unknown) => void;
    const statusPromise = new CancellablePromise<unknown>(resolve => {
      statusResolve = resolve;
    });

    jest.spyOn(ApiUtils, 'simplePost').mockImplementation(
      (url: string): CancellablePromise<unknown> => {
        currentApiHit++;
        if (url.indexOf(CREATE_SESSION_API) !== -1) {
          createSessionApiHit = currentApiHit;
          return new CancellablePromise<unknown>(resolve => {
            resolve({ session: { type: 'foo' } });
          });
        } else if (url.indexOf(EXECUTE_API_PREFIX) !== -1) {
          executeApiHit = currentApiHit;
          expect(url).toEqual(EXECUTE_API_PREFIX + 'impala');
          return new CancellablePromise<unknown>(resolve => {
            resolve({
              handle: {},
              history_id: 1,
              history_uuid: 'some-history_uuid',
              history_parent_uuid: 'some_history_parent_uuid'
            });
          });
        } else if (url.indexOf(CHECK_STATUS_API) !== -1) {
          checkStatusApiHit = currentApiHit;
          statusResolve({ query_status: { status: EXECUTION_STATUS.available } });
          return statusPromise;
        } else if (url.indexOf(GET_LOGS_API) !== -1) {
          getLogsApiHit = currentApiHit;
          logsResolve({ status: 0, logs: '' });
          return logsPromise;
        }
        fail('fail for URL: ' + url);
        throw new Error('fail for URL: ' + url);
      }
    );

    expect(subject.status).toEqual(EXECUTION_STATUS.ready);

    await subject.execute();
    await statusPromise;
    await logsPromise;

    expect(createSessionApiHit).toEqual(1);
    expect(executeApiHit).toEqual(2);
    expect(checkStatusApiHit).toEqual(3);
    expect(getLogsApiHit).toEqual(4);

    expect(subject.status).toEqual(EXECUTION_STATUS.available);
  });

  // xit('should set the correct status after failed execute', done => {
  //   const subject = createSubject('SELECT * FROM customers');
  //
  //   const simplePostDeferred = $.Deferred();
  //
  //   jest.spyOn(ApiHelper, 'createSession').mockImplementation(
  //     () =>
  //       new Promise(resolve => {
  //         resolve({ type: 'x' });
  //       })
  //   );
  //
  //   jest.spyOn(ApiUtils, 'simplePost').mockImplementation(url => {
  //     expect(url).toEqual('/notebook/api/execute/impala');
  //     return simplePostDeferred;
  //   });
  //
  //   subject
  //     .execute()
  //     .then(fail)
  //     .catch(() => {
  //       expect(subject.status).toEqual(EXECUTION_STATUS.failed);
  //       done();
  //     });
  //
  //   expect(subject.status).toEqual(EXECUTION_STATUS.running);
  //
  //   simplePostDeferred.reject();
  // });

  // xit('should set the correct status when cancelling', done => {
  //   const subject = createSubject('SELECT * FROM customers');
  //
  //   const simplePostExeuteDeferred = $.Deferred();
  //   const simplePostCancelDeferred = $.Deferred();
  //   jest.spyOn(ApiUtils, 'simplePost').mockImplementation(url => {
  //     if (url === '/notebook/api/execute/impala') {
  //       return simplePostExeuteDeferred;
  //     } else if (url === '/notebook/api/cancel_statement') {
  //       return simplePostCancelDeferred;
  //     }
  //     fail();
  //   });
  //
  //   subject
  //     .execute()
  //     .then(() => {
  //       expect(subject.status).toEqual(EXECUTION_STATUS.available);
  //       subject.cancel().then(() => {
  //         expect(subject.status).toEqual(EXECUTION_STATUS.canceled);
  //         done();
  //       });
  //
  //       expect(subject.status).toEqual(EXECUTION_STATUS.canceling);
  //
  //       simplePostCancelDeferred.resolve();
  //     })
  //     .catch(fail);
  //
  //   expect(subject.status).toEqual(EXECUTION_STATUS.running);
  //
  //   simplePostExeuteDeferred.resolve({ handle: {} });
  // });
});
