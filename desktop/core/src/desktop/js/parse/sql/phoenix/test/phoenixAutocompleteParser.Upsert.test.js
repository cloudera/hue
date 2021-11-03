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

import phoenixAutocompleteParser from '../phoenixAutocompleteParser';

describe('phoenixAutocompleteParser.js UPSERT statements', () => {
  beforeAll(() => {
    phoenixAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      phoenixAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  describe('UPSERT', () => {
    it('should handle "UPSERT INTO bla.boo VALUES(1, 2, 3); |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO bla.boo VALUES(1, 2, 3); ',
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
        containsKeywords: ['UPSERT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "UPSERT |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT ',
        afterCursor: '',
        containsKeywords: ['INTO'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "UPSERT INTO |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "UPSERT INTO baa.|"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO baa.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'baa' }] }
        }
      });
    });

    it('should suggest keywords for "UPSERT INTO baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO baa ',
        afterCursor: '',
        containsKeywords: ['VALUES', 'SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "UPSERT INTO baa SELECT * FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO baa SELECT * FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest columns for "UPSERT INTO boo.baa (|"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO boo.baa (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
        }
      });
    });

    it('should not suggest keywords for "UPSERT INTO boo.baa (a, b) VALUES (1, 2) |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO boo.baa (a, b) VALUES (1, 2) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });
});
