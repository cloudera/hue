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

describe('sqlAutocompleteParser.js ANALYZE statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  describe('ANALYZE TABLE', () => {
    it('should handle "ANALYZE TABLE boo.baa PARTITION (bla=1, boo=\'baa\') COMPUTE STATISTICS FOR COLUMNS CACHE METADATA NOSCAN;|"', () => {
      assertAutoComplete({
        beforeCursor:
          "ANALYZE TABLE boo.baa PARTITION (bla=1, boo='baa') COMPUTE STATISTICS FOR COLUMNS CACHE METADATA NOSCAN;",
        afterCursor: '',
        dialect: 'hive',
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
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['ANALYZE TABLE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "analyze |"', () => {
      assertAutoComplete({
        beforeCursor: 'analyze ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest keywords for "analyze | tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'analyze ',
        afterCursor: ' tbl',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest keywords for "analyze tab| tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'analyze tab',
        afterCursor: ' tbl',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "ANALYZE TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "ANALYZE TABLE boo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo.',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }], onlyTables: true }
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'COMPUTE STATISTICS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE boo PARTITION (baa = 1) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo PARTITION (baa = 1) ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMPUTE STATISTICS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE boo PARTITION (baa = 1) COMPUTE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo PARTITION (baa = 1) COMPUTE ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['STATISTICS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOR COLUMNS', 'CACHE METADATA', 'NOSCAN']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COLUMNS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CACHE METADATA', 'NOSCAN']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['METADATA']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE METADATA |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE METADATA ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOSCAN']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS | NOSCAN"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS ',
        afterCursor: ' NOSCAN',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOR COLUMNS', 'CACHE METADATA']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS CACHE | NOSCAN"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS CACHE ',
        afterCursor: ' NOSCAN',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['METADATA']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS | NOSCAN"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS ',
        afterCursor: ' NOSCAN',
        dialect: 'hive',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CACHE METADATA']
        }
      });
    });
  });

  describe('COMPUTE STATS', () => {
    it('should handle "COMPUTE STATS bla.boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMPUTE STATS bla.boo;',
        afterCursor: '',
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });
  });
});
