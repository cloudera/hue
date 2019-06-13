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

import SqlTestUtils from './sqlTestUtils';
import sqlAutocompleteParser from '../sqlAutocompleteParser';

describe('sqlAutocompleteParser.js USE statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  it('should suggest keywords for "|"', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: '',
      containsKeywords: ['USE'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest databases for "USE |"', () => {
    assertAutoComplete({
      serverResponses: {},
      beforeCursor: 'USE ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestDatabases: {}
      }
    });
  });

  it('should suggest databases for "USE bla|"', () => {
    assertAutoComplete({
      serverResponses: {},
      beforeCursor: 'USE bla',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestDatabases: {}
      }
    });
  });

  it('should use a use statement for "use database_two; \\nselect |"', () => {
    assertAutoComplete({
      beforeCursor: 'use database_two; \nSELECT ',
      afterCursor: '',
      containsKeywords: ['*', 'ALL', 'DISTINCT'],
      expectedResult: {
        useDatabase: 'database_two',
        lowerCase: true,
        suggestAggregateFunctions: { tables: [] },
        suggestAnalyticFunctions: true,
        suggestFunctions: {},
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

  it('should use the last use statement for "USE other_db; USE closest_db; \\n\\tSELECT |"', () => {
    assertAutoComplete({
      beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
      afterCursor: '',
      containsKeywords: ['*', 'ALL', 'DISTINCT'],
      expectedResult: {
        useDatabase: 'closest_db',
        lowerCase: false,
        suggestAggregateFunctions: { tables: [] },
        suggestAnalyticFunctions: true,
        suggestFunctions: {},
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

  it('should use the use statement for "USE other_db; USE closest_db; \\n\\tSELECT |; USE some_other_db;"', () => {
    assertAutoComplete({
      beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
      afterCursor: '; USE some_other_db;',
      containsKeywords: ['*', 'ALL', 'DISTINCT'],
      expectedResult: {
        useDatabase: 'closest_db',
        lowerCase: false,
        suggestAggregateFunctions: { tables: [] },
        suggestAnalyticFunctions: true,
        suggestFunctions: {},
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
