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

describe('dasksqlAutocompleteParser.js CREATE statements', () => {
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
      containsKeywords: ['CREATE'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE ',
      afterCursor: '',
      containsKeywords: ['TABLE', 'VIEW'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  describe('CREATE TABLE', () => {
    it('should suggest keywords for "CREATE TABLE foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS', 'WITH (']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo AS SELECT * |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo AS SELECT * ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM'],
          suggestTables: { prependFrom: true },
          suggestDatabases: { prependFrom: true, appendDot: true }
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo WITH (keyword |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo WITH (keyword ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo WITH (keyword = "value" |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo WITH (keyword = "value" ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [',', ')']
        }
      });
    });

    it('should handle for "CREATE TABLE foo WITH (keyword = "value"); |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo WITH (keyword = "value");',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle for "CREATE TABLE foo AS SELECT 1 + 1; |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo AS SELECT 1 + 1;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('CREATE VIEW', () => {
    it('should suggest keywords for "CREATE VIEW foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW foo AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW foo AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW foo AS SELECT * |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW foo AS SELECT * ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM'],
          suggestTables: { prependFrom: true },
          suggestDatabases: { prependFrom: true, appendDot: true }
        }
      });
    });

    it('should handle for "CREATE VIEW foo AS SELECT 1 + 1; |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW foo AS SELECT 1 + 1;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });
});
