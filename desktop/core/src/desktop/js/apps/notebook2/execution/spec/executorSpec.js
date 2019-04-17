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
import { EXECUTION_STATUS } from '../executableStatement';
import Executor from '../executor';

describe('executor.js', () => {
  /**
   * @param statement
   * @return {Executor}
   */
  const createSubject = statement =>
    new Executor({
      compute: { id: 'compute' },
      namespace: { id: 'namespace' },
      database: 'default',
      sourceType: 'impala',
      statement: statement,
      isSqlEngine: true
    });

  xit('should set the correct status after successful execute', done => {
    const subject = createSubject('SELECT * FROM customers;');

    const simplePostDeferred = $.Deferred();
    spyOn(ApiHelper, 'simplePost').and.callFake(url => {
      expect(url).toEqual('/notebook/api/execute/impala');
      return simplePostDeferred;
    });

    subject
      .executeNext()
      .then(() => {
        expect(subject.status).toEqual(EXECUTION_STATUS.available);
        done();
      })
      .catch(fail);

    expect(subject.status).toEqual(EXECUTION_STATUS.running);

    simplePostDeferred.resolve({ handle: {} });
  });
});
