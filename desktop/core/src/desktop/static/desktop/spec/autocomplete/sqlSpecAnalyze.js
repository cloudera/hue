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
  describe('sql.js ANALYZE statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    describe('ANALYZE TABLE', function () {
      it('should handle "ANALYZE TABLE boo.baa PARTITION (bla=1, boo=\'baa\') COMPUTE STATISTICS FOR COLUMNS CACHE METADATA NOSCAN;|"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE boo.baa PARTITION (bla=1, boo=\'baa\') COMPUTE STATISTICS FOR COLUMNS CACHE METADATA NOSCAN;',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          containsKeywords: ['ANALYZE TABLE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "analyze |"', function() {
        assertAutoComplete({
          beforeCursor: 'analyze ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest keywords for "analyze | tbl"', function() {
        assertAutoComplete({
          beforeCursor: 'analyze ',
          afterCursor: ' tbl',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest keywords for "analyze tab| tbl"', function() {
        assertAutoComplete({
          beforeCursor: 'analyze tab',
          afterCursor: ' tbl',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables for "ANALYZE TABLE |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { onlyTables: true },
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest tables for "ANALYZE TABLE boo.|"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE boo.',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'boo' }], onlyTables: true }
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE boo |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE boo ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', 'COMPUTE STATISTICS']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE boo PARTITION (baa = 1) |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE boo PARTITION (baa = 1) ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMPUTE STATISTICS']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE boo PARTITION (baa = 1) COMPUTE |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE boo PARTITION (baa = 1) COMPUTE ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['STATISTICS']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FOR COLUMNS', 'CACHE METADATA', 'NOSCAN']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COLUMNS']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CACHE METADATA', 'NOSCAN']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['METADATA']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE METADATA |"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE METADATA ',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOSCAN']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS | NOSCAN"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS ',
          afterCursor: ' NOSCAN',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FOR COLUMNS', 'CACHE METADATA']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS CACHE | NOSCAN"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS CACHE ',
          afterCursor: ' NOSCAN',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['METADATA']
          }
        });
      });

      it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS | NOSCAN"', function() {
        assertAutoComplete({
          beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS ',
          afterCursor: ' NOSCAN',
          dialect: 'hive',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CACHE METADATA']
          }
        });
      });
    });

    describe('COMPUTE STATS', function () {
      it('should handle "COMPUTE STATS bla.boo;|"', function() {
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

      it('should handle "COMPUTE INCREMENTAL STATS bla.boo;|"', function() {
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

      it('should handle "COMPUTE INCREMENTAL STATS bla.boo PARTITION (a=1, b = 2);|"', function() {
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

      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          containsKeywords: ['COMPUTE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "COMPUTE |"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INCREMENTAL STATS', 'STATS']
          }
        });
      });

      it('should suggest keywords for "COMPUTE | tbl"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE ',
          afterCursor: ' tbl',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INCREMENTAL STATS', 'STATS']
          }
        });
      });

      it('should suggest keywords for "COMPUTE foo| tbl"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE foo',
          afterCursor: ' tbl',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INCREMENTAL STATS', 'STATS']
          }
        });
      });

      it('should suggest keywords for "COMPUTE INCREMENTAL | tbl"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE INCREMENTAL ',
          afterCursor: ' tbl',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['STATS']
          }
        });
      });

      it('should suggest tables for "COMPUTE STATS |"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE STATS ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest tables for "COMPUTE STATS db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE STATS db.',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'db' }]}
          }
        });
      });

      it('should suggest keywords for "COMPUTE INCREMENTAL |"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE INCREMENTAL ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['STATS']
          }
        });
      });

      it('should suggest tables for "COMPUTE INCREMENTAL STATS |"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE INCREMENTAL STATS ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest tables for "COMPUTE INCREMENTAL STATS db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE STATS db.',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'db' }]}
          }
        });
      });

      it('should suggest keywords for "COMPUTE INCREMENTAL STATS db.tbl |"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE INCREMENTAL STATS db.tbl ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION']
          }
        });
      });

      it('should suggest columns for "COMPUTE INCREMENTAL STATS db.tbl PARTITION (|"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE INCREMENTAL STATS db.tbl PARTITION (',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }]} ]}
          }
        });
      });

      it('should suggest columns for "COMPUTE INCREMENTAL STATS db.tbl PARTITION (bla = 1, |"', function() {
        assertAutoComplete({
          beforeCursor: 'COMPUTE INCREMENTAL STATS db.tbl PARTITION (bla = 1, ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }]} ]}
          }
        });
      });
    });

    describe('INVALIDATE METADATA', function () {
      it('should handle "INVALIDATE METADATA;|"', function() {
        assertAutoComplete({
          beforeCursor: 'INVALIDATE METADATA;',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "INVALIDATE METADATA db.tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'INVALIDATE METADATA db.tbl;',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          containsKeywords: ['INVALIDATE METADATA'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "INVALIDATE |"', function() {
        assertAutoComplete({
          beforeCursor: 'INVALIDATE ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['METADATA']
          }
        });
      });

      it('should suggest keywords for "INVALIDATE | tbl"', function() {
        assertAutoComplete({
          beforeCursor: 'INVALIDATE ',
          afterCursor: ' tbl',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['METADATA']
          }
        });
      });

      it('should suggest keywords for "INVALIDATE meta| tbl"', function() {
        assertAutoComplete({
          beforeCursor: 'INVALIDATE meta',
          afterCursor: ' tbl',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['METADATA']
          }
        });
      });

      it('should suggest tables for "INVALIDATE METADATA |"', function() {
        assertAutoComplete({
          beforeCursor: 'INVALIDATE METADATA ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest tables for "INVALIDATE METADATA db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'INVALIDATE METADATA db.',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'db' }]}
          }
        });
      });
    });

    describe('REFRESH', function () {
      it('should handle "REFRESH db.tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'REFRESH db.tbl;',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          containsKeywords: ['REFRESH'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "REFRESH |"', function() {
        assertAutoComplete({
          beforeCursor: 'REFRESH ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest tables for "REFRESH db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'REFRESH db.',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'db' }]}
          }
        });
      });
    });
  });
})();