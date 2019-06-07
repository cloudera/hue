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

import $ from 'jquery';

import ApiHelper from 'api/apiHelper';
import { ExecutableStatement, EXECUTION_STATUS } from '../executableStatement';

describe('executableStatement.js', () => {
  /**
   * @param statement
   * @return {ExecutableStatement}
   */
  const createSubject = statement => {
    if (typeof statement === 'string') {
      return new ExecutableStatement({
        compute: { id: 'compute' },
        namespace: { id: 'namespace' },
        database: 'default',
        statement: statement,
        sourceType: 'impala'
      });
    }

    return new ExecutableStatement({
      compute: { id: 'compute' },
      namespace: { id: 'namespace' },
      database: 'default',
      parsedStatement: statement,
      sourceType: 'impala'
    });
  };

  it('should handle strings statements', () => {
    const subject = createSubject('SELECT * FROM customers');

    expect(subject.getStatement()).toEqual('SELECT * FROM customers');
  });

  it('should handle parsed statements', () => {
    const subject = createSubject({ statement: 'SELECT * FROM customers' });

    expect(subject.getStatement()).toEqual('SELECT * FROM customers');
  });

  xit('should set the correct status after successful execute', done => {
    const subject = createSubject('SELECT * FROM customers');

    const simplePostDeferred = $.Deferred();
    spyOn(ApiHelper, 'simplePost').and.callFake(url => {
      expect(url).toEqual('/notebook/api/execute/impala');
      return simplePostDeferred;
    });

    subject
      .execute()
      .then(() => {
        expect(subject.status).toEqual(EXECUTION_STATUS.available);
        done();
      })
      .catch(fail);

    expect(subject.status).toEqual(EXECUTION_STATUS.running);

    simplePostDeferred.resolve({ handle: {} });
  });

  it('should set the correct status after failed execute', done => {
    const subject = createSubject('SELECT * FROM customers');

    const simplePostDeferred = $.Deferred();
    spyOn(ApiHelper, 'simplePost').and.callFake(url => {
      expect(url).toEqual('/notebook/api/execute/impala');
      return simplePostDeferred;
    });

    subject
      .execute()
      .then(fail)
      .catch(() => {
        expect(subject.status).toEqual(EXECUTION_STATUS.running);
        done();
      });

    expect(subject.status).toEqual(EXECUTION_STATUS.running);

    simplePostDeferred.reject();
  });

  xit('should set the correct status when cancelling', done => {
    const subject = createSubject('SELECT * FROM customers');

    const simplePostExeuteDeferred = $.Deferred();
    const simplePostCancelDeferred = $.Deferred();
    spyOn(ApiHelper, 'simplePost').and.callFake(url => {
      if (url === '/notebook/api/execute/impala') {
        return simplePostExeuteDeferred;
      } else if (url === '/notebook/api/cancel_statement') {
        return simplePostCancelDeferred;
      }
      fail();
    });

    subject
      .execute()
      .then(() => {
        expect(subject.status).toEqual(EXECUTION_STATUS.available);
        subject.cancel().then(() => {
          expect(subject.status).toEqual(EXECUTION_STATUS.canceled);
          done();
        });

        expect(subject.status).toEqual(EXECUTION_STATUS.canceling);

        simplePostCancelDeferred.resolve();
      })
      .catch(fail);

    expect(subject.status).toEqual(EXECUTION_STATUS.running);

    simplePostExeuteDeferred.resolve({ handle: {} });
  });
});
