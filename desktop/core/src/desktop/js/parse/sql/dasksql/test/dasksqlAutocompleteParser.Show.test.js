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

import dasksqlAutocompleteParser from '../dasksqlAutocompleteParser';

describe('dasksqlAutocompleteParser.js SHOW statements', () => {
  beforeAll(() => {
    dasksqlAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      dasksqlAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  it('should suggest keywords for "|"', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: '',
      containsKeywords: ['SHOW'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "SHOW |"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW ',
      afterCursor: '',
      containsKeywords: ['SCHEMAS', 'TABLES', 'COLUMNS'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  describe('dasksqlAutocompleteParser.js SHOW SCHEMAS statements', () => {
    it('should suggest keywords for "SHOW SCHEMAS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW SCHEMAS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LIKE']
        }
      });
    });
  });

  describe('dasksqlAutocompleteParser.js SHOW COLUMNS statements', () => {
    it('should suggest keywords for "SHOW COLUMNS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW COLUMNS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest keywords for "SHOW COLUMNS FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW COLUMNS FROM ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });
  });

  describe('dasksqlAutocompleteParser.js SHOW TABLES statements', () => {
    it('should suggest keywords for "SHOW TABLES |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW TABLES ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest keywords for "SHOW TABLES FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW TABLES FROM ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: false }
        }
      });
    });
  });
});
