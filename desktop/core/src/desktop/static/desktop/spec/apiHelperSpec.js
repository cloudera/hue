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
(function() {

  describe('apiHelper.js', function() {
    var subject = ApiHelper.getInstance({
      i18n: {},
      user: 'testUser'
    });

    it('should be singleton', function() {
      var otherHelper = ApiHelper.getInstance();
      expect(subject === otherHelper).toBeTruthy();
    });

    describe('success response that is actually an error', function () {
      it('should not determine that a success response is an error response if status is 0', function () {
        expect(subject.successResponseIsError({ status: 0 })).toBeFalsy();
      });

      it('should determine that a success response is an error response if status is 1', function () {
        expect(subject.successResponseIsError({ status: 1 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if status is -1', function () {
        expect(subject.successResponseIsError({ status: -1 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if status is -3', function () {
        expect(subject.successResponseIsError({ status: -3 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if status is 500', function () {
        expect(subject.successResponseIsError({ status: 500 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if code is 500', function () {
        expect(subject.successResponseIsError({ code: 500 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if code is 503', function () {
        expect(subject.successResponseIsError({ code: 503 })).toBeTruthy();
      });

      it('should determine that a success response is an error response if it contains traceback', function () {
        expect(subject.successResponseIsError({ traceback: {} })).toBeTruthy();
      });
    });
    
    describe('NavOpt', function () {
      describe('Tables JSON generation', function () {
        it('should add the default database when no database is found in the identifier chain', function () {
          spyOn(subject, 'containsDatabase').and.callFake(function () {
            return false;
          });

          var result = subject.createNavOptDbTablesJson({
            defaultDatabase: 'default',
            sourceType: 'hive',
            tables: [{ identifierChain: [{ name: 'some_table' }] }]
          });

          expect(result).toEqual('["default.some_table"]');
        });

        it('should add the database from the identifier chain if found', function () {
          spyOn(subject, 'containsDatabase').and.callFake(function () {
            return true;
          });

          var result = subject.createNavOptDbTablesJson({
            defaultDatabase: 'default',
            sourceType: 'hive',
            tables: [{ identifierChain: [{ name: 'some_db' }, { name: 'some_table' }] }]
          });

          expect(result).toEqual('["some_db.some_table"]');
        });

        it('should support tables with same names as databases', function () {
          spyOn(subject, 'containsDatabase').and.callFake(function () {
            return true;
          });

          var result = subject.createNavOptDbTablesJson({
            defaultDatabase: 'default',
            sourceType: 'hive',
            tables: [{ identifierChain: [{ name: 'table_and_db_name' }] }]
          });

          expect(result).toEqual('["default.table_and_db_name"]');
        });

        it('should support tables with same names as databases', function () {
          spyOn(subject, 'containsDatabase').and.callFake(function () {
            return true;
          });

          var result = subject.createNavOptDbTablesJson({
            defaultDatabase: 'default',
            sourceType: 'hive',
            tables: [{ identifierChain: [{ name: 'table_and_db_name' }, { name: 'table_and_db_name' }] }]
          });

          expect(result).toEqual('["table_and_db_name.table_and_db_name"]');
        });

        it('should support multiple tables some with databases some without', function () {
          spyOn(subject, 'containsDatabase').and.callFake(function () {
            return true;
          });

          var result = subject.createNavOptDbTablesJson({
            defaultDatabase: 'default',
            sourceType: 'hive',
            tables: [{ identifierChain: [{ name: 'a_table_from_default' }] }, { identifierChain: [{ name: 'other_db' }, { name: 'a_table_from_other_db' }] }]
          });

          expect(result).toEqual('["default.a_table_from_default","other_db.a_table_from_other_db"]');
        });

        it('should remove duplicates', function () {
          spyOn(subject, 'containsDatabase').and.callFake(function () {
            return true;
          });

          var result = subject.createNavOptDbTablesJson({
            defaultDatabase: 'default',
            sourceType: 'hive',
            tables: [
              { identifierChain: [{ name: 'someTable' }] },
              { identifierChain: [{ name: 'someDb' }, { name: 'someTable' }] },
              { identifierChain: [{ name: 'default' }, { name: 'someTable' }] },
              { identifierChain: [{ name: 'someDb' }, { name: 'otherTable' }] },
              { identifierChain: [{ name: 'someDb' }, { name: 'someTable' }] },
              { identifierChain: [{ name: 'someTable' }] },
              { identifierChain: [{ name: 'someDb' }, { name: 'otherTable' }] },
              { identifierChain: [{ name: 'someDb' }, { name: 'otherTable' }] }
            ]
          });

          expect(result).toEqual('["default.someTable","someDb.someTable","someDb.otherTable"]');
        })
      });
    })
  });
})();