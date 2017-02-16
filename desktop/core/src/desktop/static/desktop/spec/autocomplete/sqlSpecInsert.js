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
  describe('sql.js INSERT statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    it('should handle "INSERT INTO bla.boo VALUES (1, 2, \'a\', 3); |"', function() {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO bla.boo VALUES (1, 2, \'a\', 3); ',
        afterCursor: '',
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
        containsKeywords: ['INSERT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INSERT |"', function() {
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

    it('should suggest tables for "INSERT INTO |"', function() {
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

    it('should suggest tables for "INSERT INTO baa.|"', function() {
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

    it('should suggest tables for "INSERT INTO TABLE baa.|"', function() {
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

    it('should suggest keywords for "INSERT INTO baa |"', function() {
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

    it('should suggest keywords for "INSERT INTO TABLE baa |"', function() {
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

    describe('Hive specific', function () {
      it('should handle "INSERT OVERWRITE TABLE bla.boo PARTITION (bla=1, bo) IF NOT EXISTS SELECT ba.boo, ba, ble FROM db.tbl; |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE TABLE bla.boo PARTITION (bla=1, bo) IF NOT EXISTS SELECT ba.boo, ba, ble FROM db.tbl;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "INSERT INTO TABLE bla.boo PARTITION (bla=1, bo) (a, b, c) SELECT ba.boo, ba, ble FROM db.tbl; |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE bla.boo PARTITION (bla=1, bo) (a, b, c) SELECT ba.boo, ba, ble FROM db.tbl;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "INSERT OVERWRITE DIRECTORY \'blabla\' SELECT * FROM boo;|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE DIRECTORY \'blabla\' SELECT * FROM boo;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "INSERT INTO bla.boo SELECT ba.boo, ba, ble FROM db.tbl; |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO bla.boo SELECT ba.boo, ba, ble FROM db.tbl;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "FROM boo.baa\\nINSERT INTO TABLE baa2 PARTITION (a, b) SELECT * ORDER BY ba\\nINSERT INTO TABLE baa3 SELECT * GROUP BY boo;|"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM boo.baa\n' +
          'INSERT INTO TABLE baa2 PARTITION (a, b) SELECT * ORDER BY ba\n' +
          'INSERT INTO TABLE baa3 SELECT * GROUP BY boo;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "FROM boo.baa SELECT * ORDER BY ba;|"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM boo.baa SELECT * ORDER BY ba;',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          containsKeywords: ['FROM', 'INSERT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "WITH t1 as (select 1), t2 as (select 2) |"', function() {
        assertAutoComplete({
          beforeCursor: 'WITH t1 as (select 1), t2 as (select 2) ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['INSERT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "FROM |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest keywords for "from baa.boo |"', function() {
        assertAutoComplete({
          beforeCursor: 'from baa.boo ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['INSERT INTO', 'INSERT OVERWRITE', 'SELECT']
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INTO', 'OVERWRITE']
          }
        });
      });

      it('should suggest tables for "FROM baa.boo INSERT INTO |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true },
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables for "FROM baa.boo INSERT INTO baa.|"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO baa.',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'baa' }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT INTO TABLE baa |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', 'SELECT']
          }
        });
      });

      it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (|"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
          }
        });
      });

      it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (|"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] },
            suggestAnalyticFunctions: true,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
          }
        });
      });

      it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT a, |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT a, ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['*'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] },
            suggestAnalyticFunctions: true,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsColRefKeywords: true,
          containsKeywords: ['WHERE', 'ORDER BY'],
          doesNotContainKeywords: ['FROM'],
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', 'SELECT']
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', 'SELECT']
          }
        });
      });

      it('should suggest columns for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (|"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'bla' }, { name: 'ble' }] }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF NOT EXISTS', 'SELECT']
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest columns for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['*'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] },
            suggestAnalyticFunctions: true,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsColRefKeywords: true,
          containsKeywords: ['WHERE', 'ORDER BY'],
          doesNotContainKeywords: ['FROM'],
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d INSERT OVERWRITE bla.ble SELECT a |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d INSERT OVERWRITE bla.ble SELECT a ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsColRefKeywords: true,
          containsKeywords: ['WHERE', 'ORDER BY'],
          doesNotContainKeywords: ['FROM'],
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'a' }] }
          }
        });
      });

      it('should suggest columns for "FROM baa.boo SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo SELECT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['*'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] },
            suggestAnalyticFunctions: true,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
          }
        });
      });

      it('should suggest keywords for "FROM baa.boo SELECT c, d |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM baa.boo SELECT c, d ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsColRefKeywords: true,
          containsKeywords: ['WHERE', 'ORDER BY'],
          doesNotContainKeywords: ['FROM'],
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest keywords for "INSERT |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INTO', 'OVERWRITE']
          }
        });
      });

      it('should suggest tables for "INSERT INTO |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true },
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables for "INSERT INTO baa.|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO baa.',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'baa' }] }
          }
        });
      });

      it('should suggest keywords for "INSERT INTO TABLE baa |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE baa ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', 'VALUES', 'SELECT']
          }
        });
      });

      it('should suggest columns for "INSERT INTO TABLE baa PARTITION (|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE baa PARTITION (',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
          }
        });
      });

      it('should suggest columns for "INSERT INTO TABLE baa PARTITION (a,b) (x, |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
          }
        });
      });

      it('should suggest keywords for "insert into table baa partition (a,b) (x, z) |"', function() {
        assertAutoComplete({
          beforeCursor: 'insert into table baa partition (a,b) (x, z) ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest columns for "INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['*'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestTables: { prependFrom: true, prependQuestionMark: true },
            suggestDatabases:  { prependFrom: true, prependQuestionMark: true, appendDot: true }
          }
        });
      });

      it('should suggest columns for "INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestTables: { prependFrom: true, prependQuestionMark: true },
            suggestDatabases:  { prependFrom: true, prependQuestionMark: true, appendDot: true }
          }
        });
      });

      it('should suggest keywords for "INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['AS', 'IN'],
          expectedResult: {
            lowerCase: false,
            suggestTables: { prependFrom: true },
            suggestDatabases:  { prependFrom: true, appendDot: true }
          }
        });
      });

      it('should suggest tables for "INSERT OVERWRITE |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true },
            suggestKeywords: ['DIRECTORY', 'LOCAL DIRECTORY', 'TABLE' ]
          }
        });
      });

      it('should suggest tables for "INSERT OVERWRITE LOCAL |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE LOCAL ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DIRECTORY' ]
          }
        });
      });

      it('should suggest hdfs for "INSERT OVERWRITE DIRECTORY \'|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE DIRECTORY \'',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestHdfs: { path: '' }
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE DIRECTORY \'blabla\' |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE DIRECTORY \'blabla\' ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE bla.ble |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', 'SELECT']
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE bla.ble |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', 'SELECT']
          }
        });
      });

      it('should suggest columns for "INSERT OVERWRITE bla.ble PARTITION (|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'bla' }, { name: 'ble' }] }] }
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF NOT EXISTS', 'SELECT']
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest columns for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['*'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestTables: { prependFrom: true, prependQuestionMark: true },
            suggestDatabases:  { prependFrom: true, prependQuestionMark: true, appendDot: true }
          }
        });
      });

      it('should suggest keywords for "INSERT OVERWRITE bla.ble SELECT c, d |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE bla.ble SELECT c, d ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['AS', 'IN'],
          expectedResult: {
            lowerCase: false,
            suggestTables: { prependFrom: true },
            suggestDatabases:  { prependFrom: true, appendDot: true }
          }
        });
      });

      it('should suggest identifier for "WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT INTO tab SELECT * FROM |"', function() {
        assertAutoComplete({
          beforeCursor: 'WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT INTO tab SELECT * FROM ',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true },
            suggestCommonTableExpressions: [{ name: 't1' }, { name: 't2' }],
            commonTableExpressions: [{ alias: 't1', columns: [{ type: 'NUMBER' }] }, { alias: 't2', columns: [{ type: 'NUMBER' }] }],
          }
        });
      });
    });

    describe('Impala specific', function () {
      it('should handle "INSERT INTO TABLE boo.baa (a, b) PARTITION (a=1) VALUES (1, 2);|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE boo.baa (a, b) PARTITION (a=1) VALUES (1, 2);',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "INSERT OVERWRITE boo.baa [SHUFFLE] SELECT * FROM bla;|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE boo.baa [SHUFFLE] SELECT * FROM bla;',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT OVERWRITE tab SELECT * FROM t1, t2;|"', function() {
        assertAutoComplete({
          beforeCursor: 'WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT OVERWRITE tab SELECT * FROM t1, t2;',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "WITH t1 as (select 1), t2 as (select 2) |"', function() {
        assertAutoComplete({
          beforeCursor: 'WITH t1 as (select 1), t2 as (select 2) ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['INSERT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "INSERT |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INTO', 'OVERWRITE' ]
          }
        });
      });

      it('should suggest tables for "INSERT INTO |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true },
            suggestKeywords: ['TABLE' ]
          }
        });
      });

      it('should suggest tables for "INSERT INTO boo.|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO boo.',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'boo' }] }
          }
        });
      });

      it('should suggest keywords for "INSERT INTO baa |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO baa ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', '[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES']
          }
        });
      });

      it('should suggest keywords for "INSERT INTO baa [SHUFFLE] |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO baa [SHUFFLE] ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest tables for "INSERT INTO baa [SHUFFLE] SELECT * FROM |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO baa [SHUFFLE] SELECT * FROM ',
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

      it('should suggest tables for "INSERT INTO TABLE boo.baa (|"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO boo.baa (',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
          }
        });
      });

      it('should suggest tables for "INSERT INTO TABLE boo.baa (a, |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO boo.baa (a, ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
          }
        });
      });

      it('should suggest keywords for "WITH t1 as (select 1), t2 as (select 2) INSERT INTO baa (a, b) |"', function() {
        assertAutoComplete({
          beforeCursor: 'WITH t1 as (select 1), t2 as (select 2) INSERT INTO baa ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION', '[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES'],
            commonTableExpressions: [{ alias: 't1', columns: [{ type: 'NUMBER' }] }, { alias: 't2', columns: [{ type: 'NUMBER' }] }]
          }
        });
      });

      it('should suggest columns for "INSERT INTO TABLE boo.baa (a, b) PARTITION(a = 1, |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE boo.baa (a, b) PARTITION(a = 1, ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
          }
        });
      });

      it('should not suggest keywords for "INSERT INTO TABLE boo.baa (a, b) VALUES (1, 2) |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT INTO TABLE boo.baa (a, b) VALUES (1, 2) |',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "INSERT OVERWRITE |"', function() {
        assertAutoComplete({
          beforeCursor: 'INSERT OVERWRITE ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true },
            suggestKeywords: ['TABLE' ]
          }
        });
      });

      it('should suggest identifier for "with t1 as (select 1), t2 as (select 2) insert into tab select * from |"', function() {
        assertAutoComplete({
          beforeCursor: 'with t1 as (select 1), t2 as (select 2) insert into tab select * from ',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          expectedResult: {
            lowerCase: true,
            suggestTables: {},
            suggestDatabases: { appendDot: true },
            suggestCommonTableExpressions: [{ name: 't1' },{ name: 't2' }],
            commonTableExpressions: [{ alias: 't1', columns: [{ type: 'NUMBER' }] }, { alias: 't2', columns: [{ type: 'NUMBER' }] }]
          }
        });
      });
    });
  });
})();