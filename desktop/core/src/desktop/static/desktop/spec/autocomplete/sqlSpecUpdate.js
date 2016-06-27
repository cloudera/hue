// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
define([
  'knockout',
  'desktop/js/autocomplete/sql',
  'desktop/spec/autocompleterTestUtils'
], function(ko, sql, testUtils) {

  describe('sql.js UPDATE statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = testUtils.assertAutocomplete;

    it('should suggest keywords for empty statement', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['UPDATE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords after UPDATE TableReference ', function () {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar  ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SET']
        }
      });
    });

    it('should suggest keywords after UPDATE TableReference SET SetClauseList ', function () {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar SET id=1, foo=2 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WHERE']
        }
      });
    });

    it('should suggest keywords after UPDATE TableReference SET identifier ', function () {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar SET id ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest tables after UPDATE', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables after UPDATE with partial table or schema ref', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bla',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables after UPDATE with database', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            database: 'bar'
          }
        }
      });
    });

    it('should suggest tables after UPDATE with database and partial table', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            database: 'bar'
          }
        }
      });
    });

    it('should suggest columns after SET', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            database: 'bar',
            table: 'foo'
          }
        }
      });
    });

    it('should suggest columns after SET id = 1, bar = \'foo\', ', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET id = 1, bar = \'foo\', ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            database: 'bar',
            table: 'foo'
          }
        }
      });
    });

    it('should suggest columns after SET bar = \'foo\' WHERE ', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET bar = \'foo\' WHERE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            database: 'bar',
            table: 'foo'
          }
        }
      });
    });

    it('should suggest values after SET bar = \'foo\' WHERE id = ', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET bar = \'foo\' WHERE id = ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestValues: {
            database: 'bar',
            table: 'foo',
            identifierChain: [{ name: 'id' }]
          }
        }
      });
    });

    it('should suggest columns after SET bar = \'foo\' WHERE id = 1 AND ', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET bar = \'foo\' WHERE id = 1 AND ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            database: 'bar',
            table: 'foo'
          }
        }
      });
    });
  });
});