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

import ksqlAutocompleteParser from '../ksqlAutocompleteParser';

describe('ksqlAutocompleteParser.js INSERT statements', () => {
  beforeAll(() => {
    ksqlAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      ksqlAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  describe('INSERT', () => {
    it('should handle "INSERT INTO bla.boo VALUES (1, 2, \'a\', 3); |"', () => {
      assertAutoComplete({
        beforeCursor: "INSERT INTO bla.boo VALUES (1, 2, 'a', 3); ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['INSERT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INSERT |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT ',
        afterCursor: '',
        containsKeywords: ['INTO'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "INSERT INTO |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "INSERT INTO baa.|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO baa.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'baa' }] }
        }
      });
    });

    it('should suggest tables for "INSERT INTO TABLE baa.|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'baa' }] }
        }
      });
    });

    it('should suggest keywords for "INSERT INTO baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO baa ',
        afterCursor: '',
        containsKeywords: ['VALUES'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INSERT INTO TABLE baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa ',
        afterCursor: '',
        containsKeywords: ['VALUES'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });
});
