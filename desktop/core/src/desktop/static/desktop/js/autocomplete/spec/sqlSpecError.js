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

(function () {
  describe('sqlAutocompleteParser.js Error statements', function() {

    beforeAll(function () {
      sqlAutocompleteParser.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    it('should suggest columns for "SELECT BAABO BOOAA BLARGH, | FROM testTable"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT BAABO BOOAA BLARGH, ',
        afterCursor: ' FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT foo, bar, SELECT, | FROM testTable"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT foo, bar, SELECT, ',
        afterCursor: ' FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT foo, baa baa baa baa, SELECT, | FROM testTable"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT foo, baa baa baa baa, SELECT, ',
        afterCursor: ' FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE baa baaa booo |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE baa baaa boo',
        afterCursor: '',
        containsKeywords: ['GROUP BY', 'ORDER BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE baa baaa booo GROUP |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE baa baaa boo GROUP ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY'],
          suggestGroupBys: { prefix: 'BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE baa baaa booo ORDER |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE baa baaa boo ORDER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY'],
          suggestOrderBys: { prefix: 'BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable ORDER BY bla bla bla boo |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable ORDER BY bla bla bla boo ',
        afterCursor: '',
        containsKeywords: ['LIMIT', 'UNION'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable GROUP BY boo hoo hoo ORDER BY bla bla bla boo |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable ORDER BY bla bla bla boo ',
        afterCursor: '',
        containsKeywords: ['LIMIT', 'UNION'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });
})();