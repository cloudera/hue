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

import impalaAutocompleteParser from '../impalaAutocompleteParser';

describe('impalaAutocompleteParser.js ANALYZE statements', () => {
  beforeAll(() => {
    impalaAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      impalaAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug || testDefinition.debug
      )
    ).toEqualDefinition(testDefinition);
  };

  describe('COMPUTE STATS', () => {
    it('should handle "COMPUTE STATS bla.boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS bla.boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "COMPUTE STATS bla.boo (foo, bar) TABLESAMPLE SYSTEM(10) REPEATABLE(10);|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS bla.boo (foo, bar) TABLESAMPLE SYSTEM(10) REPEATABLE(10);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "COMPUTE INCREMENTAL STATS bla.boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL STATS bla.boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "COMPUTE INCREMENTAL STATS bla.boo PARTITION (a=1, b = 2);|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL STATS bla.boo PARTITION (a=1, b = 2);',
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
        noErrors: true,
        containsKeywords: ['COMPUTE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "COMPUTE |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INCREMENTAL STATS', 'STATS']
        }
      });
    });

    it('should suggest keywords for "COMPUTE | tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE ',
        afterCursor: ' tbl',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INCREMENTAL STATS', 'STATS']
        }
      });
    });

    it('should suggest keywords for "COMPUTE foo| tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE foo',
        afterCursor: ' tbl',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INCREMENTAL STATS', 'STATS']
        }
      });
    });

    it('should suggest keywords for "COMPUTE INCREMENTAL | tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL ',
        afterCursor: ' tbl',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['STATS']
        }
      });
    });

    it('should suggest tables for "COMPUTE STATS |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "COMPUTE STATS tbl |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS tbl ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLESAMPLE']
        }
      });
    });

    it('should suggest columns for "COMPUTE STATS db.tbl (|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS db.tbl (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });

    it('should suggest keywords for "COMPUTE STATS tbl TABLESAMPLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS tbl TABLESAMPLE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SYSTEM()']
        }
      });
    });

    it('should suggest keywords for "COMPUTE STATS tbl TABLESAMPLE SYSTEM(1) |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS tbl TABLESAMPLE SYSTEM(1) ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REPEATABLE()']
        }
      });
    });

    it('should suggest tables for "COMPUTE STATS db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest keywords for "COMPUTE INCREMENTAL |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['STATS']
        }
      });
    });

    it('should suggest tables for "COMPUTE INCREMENTAL STATS |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL STATS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "COMPUTE INCREMENTAL STATS db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest keywords for "COMPUTE INCREMENTAL STATS db.tbl |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL STATS db.tbl ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest columns for "COMPUTE INCREMENTAL STATS db.tbl PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL STATS db.tbl PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });

    it('should suggest columns for "COMPUTE INCREMENTAL STATS db.tbl PARTITION (bla = 1, |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE INCREMENTAL STATS db.tbl PARTITION (bla = 1, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });
  });

  describe('INVALIDATE METADATA', () => {
    it('should handle "INVALIDATE METADATA;|"', () => {
      assertAutoComplete({
        beforeCursor: 'INVALIDATE METADATA;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "INVALIDATE METADATA db.tbl;|"', () => {
      assertAutoComplete({
        beforeCursor: 'INVALIDATE METADATA db.tbl;',
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
        noErrors: true,
        containsKeywords: ['INVALIDATE METADATA'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INVALIDATE |"', () => {
      assertAutoComplete({
        beforeCursor: 'INVALIDATE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['METADATA']
        }
      });
    });

    it('should suggest keywords for "INVALIDATE | tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'INVALIDATE ',
        afterCursor: ' tbl',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['METADATA']
        }
      });
    });

    it('should suggest keywords for "INVALIDATE meta| tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'INVALIDATE meta',
        afterCursor: ' tbl',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['METADATA']
        }
      });
    });

    it('should suggest tables for "INVALIDATE METADATA |"', () => {
      assertAutoComplete({
        beforeCursor: 'INVALIDATE METADATA ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "INVALIDATE METADATA db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'INVALIDATE METADATA db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });
  });

  describe('REFRESH', () => {
    it('should handle "REFRESH db.tbl PARTITION (id = 1);|"', () => {
      assertAutoComplete({
        beforeCursor: 'REFRESH db.tbl PARTITION (id = 1);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REFRESH FUNCTIONS db;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REFRESH FUNCTIONS db;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REFRESH db.tbl;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REFRESH db.tbl;',
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
        noErrors: true,
        containsKeywords: ['REFRESH'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "REFRESH |"', () => {
      assertAutoComplete({
        beforeCursor: 'REFRESH ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['AUTHORIZATION', 'FUNCTIONS']
        }
      });
    });

    it('should suggest databases for "REFRESH FUNCTIONS |"', () => {
      assertAutoComplete({
        beforeCursor: 'REFRESH FUNCTIONS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest tables for "REFRESH db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'REFRESH db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest keywords for "REFRESH db.tbl |"', () => {
      assertAutoComplete({
        beforeCursor: 'REFRESH db.tbl ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });
  });
});
