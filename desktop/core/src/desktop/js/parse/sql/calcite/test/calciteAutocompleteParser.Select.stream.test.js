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

import calciteAutocompleteParser from '../calciteAutocompleteParser';

describe('calciteAutocompleteParser.js SELECT STREAM statements', () => {
  beforeAll(() => {
    calciteAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      calciteAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  it('should suggest STREAM keywords for "SELECT |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['STREAM'],
      expectedResult: {
        lowerCase: false,
        suggestTables: {
          prependQuestionMark: true,
          prependFrom: true
        },
        suggestAggregateFunctions: { tables: [] },
        suggestAnalyticFunctions: true,
        suggestFunctions: {},
        suggestDatabases: {
          prependQuestionMark: true,
          prependFrom: true,
          appendDot: true
        }
      }
    });
  });

  it('should suggest ALL keyword after for "SELECT STREAM |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT STREAM ',
      afterCursor: '',
      noErrors: true,
      doesNotContainKeywords: ['STREAM'],
      expectedResult: {
        lowerCase: false,
        suggestTables: {
          prependFrom: true
        },
        suggestDatabases: {
          prependFrom: true,
          appendDot: true
        }
      }
    });
  });
});
