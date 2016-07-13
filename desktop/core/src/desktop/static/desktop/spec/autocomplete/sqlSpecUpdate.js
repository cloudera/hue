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

    it('should suggest keywords for "|"', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['UPDATE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "UPDATE bar  |"', function () {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar  ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SET']
        }
      });
    });

    it('should suggest keywords for "UPDATE bar SET id=1, foo=2 |"', function () {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar SET id=1, foo=2 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WHERE']
        }
      });
    });

    it('should suggest keywords for "UPDATE bar SET id |"', function () {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar SET id ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest tables for "UPDATE |"', function() {
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

    it('should suggest tables for "UPDATE bla|"', function() {
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

    it('should suggest tables for "UPDATE bar.|"', function() {
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

    it('should suggest tables for "UPDATE bar.foo|"', function() {
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

    it('should suggest columns for "UPDATE bar.foo SET |"', function() {
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

    it('should suggest columns for "UPDATE bar.foo SET id = 1, bar = \'foo\', |"', function() {
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

    it('should suggest columns for "UPDATE bar.foo SET bar = \'foo\' WHERE |"', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET bar = \'foo\' WHERE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: true,
          suggestColumns: {
            database: 'bar',
            table: 'foo'
          },
          suggestKeywords: ['EXISTS', 'NOT EXISTS']
        }
      });
    });

    it('should suggest values for "UPDATE bar.foo SET bar = \'foo\' WHERE id = |"', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET bar = \'foo\' WHERE id = ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: true,
          suggestValues: {
            database: 'bar',
            table: 'foo',
            identifierChain: [{ name: 'id' }]
          },
          suggestColumns : { database: 'bar', table: 'foo' }
        }
      });
    });

    it('should suggest columns for "UPDATE bar.foo SET bar = \'foo\' WHERE id = 1 AND |"', function() {
      assertAutoComplete({
        beforeCursor: 'UPDATE bar.foo SET bar = \'foo\' WHERE id = 1 AND ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: true,
          suggestColumns: {
            database: 'bar',
            table: 'foo'
          }
        }
      });
    });
  });
});