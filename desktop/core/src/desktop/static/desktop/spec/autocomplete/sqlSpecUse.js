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

  describe('sql.js USE statements', function() {

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
        containsKeywords: ['USE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest databases after use', function () {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: 'USE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { }
        }
      });
    });

    it('should suggest databases after use with started identifier', function () {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: 'USE bla',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { }
        }
      });
    });

    it('should use a use statement before the cursor if present', function () {
      assertAutoComplete({
        beforeCursor: 'USE database_two; \n\select ',
        afterCursor: '',
        expectedResult: {
          useDatabase: 'database_two',
          lowerCase: true,
          suggestKeywords: ['*', 'ALL', 'DISTINCT'],
          suggestAggregateFunctions: true,
          suggestFunctions: true,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should use the last use statement before the cursor if multiple are present', function () {
      assertAutoComplete({
        beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
        afterCursor: '',
        expectedResult: {
          useDatabase: 'closest_db',
          lowerCase: false,
          suggestKeywords: ['*', 'ALL', 'DISTINCT'],
          suggestAggregateFunctions: true,
          suggestFunctions: true,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should use the use statement before the cursor if multiple are present after the cursor', function () {
      assertAutoComplete({
        beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
        afterCursor: '; USE some_other_db;',
        expectedResult: {
          useDatabase: 'closest_db',
          lowerCase: false,
          suggestKeywords: ['*', 'ALL', 'DISTINCT'],
          suggestAggregateFunctions: true,
          suggestFunctions: true,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });
  });
});