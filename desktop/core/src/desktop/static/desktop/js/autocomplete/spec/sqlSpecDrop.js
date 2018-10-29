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
  describe('sqlAutocompleteParser.js DROP statements', function() {

    beforeAll(function () {
      sqlAutocompleteParser.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    it('should suggest keywords for "DROP |"', function() {
      assertAutoComplete({
        beforeCursor: 'DROP ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE', 'SCHEMA', 'TABLE', 'VIEW']
        }
      });
    });

    describe('hive specific', function () {

      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['ABORT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "ABORT |"', function () {
        assertAutoComplete({
          beforeCursor: 'ABORT ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TRANSACTIONS']
          }
        });
      });

      it('should suggest keywords for "DROP |"', function () {
        assertAutoComplete({
          beforeCursor: 'DROP ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DATABASE', 'FUNCTION', 'INDEX', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']
          }
        });
      });

      it('should follow case for "drop |"', function () {
        assertAutoComplete({
          beforeCursor: 'drop ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['DATABASE'],
          expectedResult: {
            lowerCase: true
          }
        });
      });
    });

    describe('impala specific', function () {
      it('should suggest keywords for "DROP |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']
          }
        });
      });
    });

    describe('DELETE FROM', function () {
      describe('Hive specific', function () {
        it('should handle "DELETE FROM boo.baa;|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa;',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "DELETE FROM boo.baa WHERE id < 1 AND bla IN (SELECT * FROM boo);|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa WHERE id < 1 AND bla IN (SELECT * FROM boo);',
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
            containsKeywords: ['DELETE'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DELETE |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE ',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FROM']
            }
          });
        });

        it('should suggest tables for "DELETE FROM |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM ',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest tables for "DELETE FROM db.|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM db.',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            expectedResult: {
              lowerCase: false,
              suggestTables: { identifierChain: [{ name: 'db' }]}
            }
          });
        });

        it('should suggest keywords for "DELETE FROM boo.baa |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa ',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['WHERE']
            }
          });
        });

        it('should suggest columns for "DELETE FROM boo.baa WHERE |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa WHERE ',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            containsKeywords: ['EXISTS'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
            }
          });
        });

        it('should suggest columns for "DELETE FROM boo.baa WHERE id > |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa WHERE id > ',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            containsKeywords: ['EXISTS'],
            expectedResult: {
              lowerCase: false,
              suggestValues: {},
              suggestFunctions: { types: ['COLREF'] },
              colRef: { identifierChain: [{ name: 'boo'}, { name: 'baa' }, { name: 'id' }] },
              suggestColumns: { types: ['COLREF'], tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should handle "DELETE FROM boo.baa;|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa;',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x;|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x;',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "DELETE t2 FROM non_kudu_table t1 JOIN kudu_table t2 ON t1.x = t2.x;|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE t2 FROM non_kudu_table t1 JOIN kudu_table t2 ON t1.x = t2.x;',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x WHERE t1.y = FALSE and t2.z > 100;|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x WHERE t1.y = FALSE and t2.z > 100;',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "DELETE FROM boo.baa WHERE id < 1 AND bla IN (SELECT * FROM boo);|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa WHERE id < 1 AND bla IN (SELECT * FROM boo);',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "DELETE FROM boo.baa b JOIN bla.ble c ON b.foo = c.bar WHERE b.id < 1 AND c.id IN (SELECT * FROM boo);|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa b JOIN bla.ble c ON b.foo = c.bar WHERE b.id < 1 AND c.id IN (SELECT * FROM boo);',
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
            containsKeywords: ['DELETE'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DELETE |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE ',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FROM'],
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest tables for "DELETE FROM |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM ',
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

        it('should suggest tables for "DELETE FROM db.|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM db.',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            expectedResult: {
              lowerCase: false,
              suggestTables: { identifierChain: [{ name: 'db' }]}
            }
          });
        });

        it('should suggest tables for "DELETE t1 FROM db.|"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM db.',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            expectedResult: {
              lowerCase: false,
              suggestTables: { identifierChain: [{ name: 'db' }]}
            }
          });
        });

        it('should suggest keywords for "DELETE FROM boo.baa |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa ',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            containsKeywords: ['WHERE', 'AS', 'LEFT ANTI JOIN'],
            expectedResult: {
              lowerCase: false,
              suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
            }
          });
        });

        it('should suggst tables for "DELETE t1 FROM tbl t1 JOIN |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE t1 FROM tbl t1 JOIN ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['[BROADCAST]', '[SHUFFLE]'],
              suggestJoins: { prependJoin: false, joinType: 'JOIN', tables: [{ identifierChain: [{ name: 'tbl' }], alias: 't1' }] },
              suggestTables: {  },
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest columns for "DELETE FROM boo.baa WHERE |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa WHERE ',
            afterCursor: '',
            dialect: 'impala',
            noErrors:true,
            containsKeywords: ['EXISTS'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] },
              suggestFilters: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
            }
          });
        });

        it('should suggest columns for "DELETE FROM boo.baa WHERE id > |"', function() {
          assertAutoComplete({
            beforeCursor: 'DELETE FROM boo.baa WHERE id > ',
            afterCursor: '',
            dialect: 'hive',
            noErrors:true,
            containsKeywords: ['EXISTS'],
            expectedResult: {
              lowerCase: false,
              suggestValues: {},
              suggestFunctions: { types: ['COLREF'] },
              colRef: { identifierChain: [{ name: 'boo'}, { name: 'baa' }, { name: 'id' }] },
              suggestColumns: { types: ['COLREF'], tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
            }
          });
        });
      });
    });

    describe('DROP DATABASE', function () {
      it('should suggest databases for "DROP DATABASE |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP DATABASE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {},
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest databases for "DROP SCHEMA |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP SCHEMA ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {},
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest keywords for "DROP DATABASE IF |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP DATABASE IF ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest databases for "DROP DATABASE IF EXISTS |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP DATABASE IF EXISTS ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords for "DROP DATABASE foo |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP DATABASE foo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CASCADE', 'RESTRICT']
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should suggest keywords for "DROP DATABASE foo |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP DATABASE foo ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CASCADE', 'RESTRICT']
            }
          });
        });
      });
    });

    describe('DROP FUNCTION', function () {
      describe('Hive specific', function () {
        it('should handle "DROP FUNCTION IF EXISTS baa;', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION IF EXISTS baa;',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DROP |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['FUNCTION'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DROP FUNCTION |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['IF EXISTS'],
            expectedResult: {
              lowerCase: false
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should handle "DROP AGGREGATE FUNCTION IF EXISTS baa.boo(INT, STRING ...);', function() {
          assertAutoComplete({
            beforeCursor: 'DROP AGGREGATE FUNCTION IF EXISTS baa.boo(INT, STRING ...);',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DROP |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['AGGREGATE FUNCTION', 'FUNCTION'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DROP AGGREGATE |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP AGGREGATE ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['FUNCTION'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DROP FUNCTION |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['IF EXISTS'],
            expectedResult: {
              lowerCase: false,
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "DROP AGGREGATE FUNCTION |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP AGGREGATE FUNCTION ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['IF EXISTS'],
            expectedResult: {
              lowerCase: false,
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "DROP FUNCTION IF |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION IF ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['EXISTS'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest databases for "DROP FUNCTION IF EXISTS |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION IF EXISTS ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "DROP FUNCTION IF EXISTS baa.boo(|"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION IF EXISTS baa.boo(',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            doesNotContainKeywords: ['...'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DROP FUNCTION IF EXISTS baa.boo(INT |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION IF EXISTS baa.boo(INT ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['...'],
            doesNotContainKeywords: ['INT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "DROP FUNCTION IF EXISTS baa.boo(INT, STRING, |"', function() {
          assertAutoComplete({
            beforeCursor: 'DROP FUNCTION IF EXISTS baa.boo(INT, STRING, ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            doesNotContainKeywords: ['...'],
            expectedResult: {
              lowerCase: false
            }
          });
        });
      })
    });

    describe('DROP INDEX', function () {
      it('should handle "DROP INDEX IF EXISTS baa ON baa.boo;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INDEX IF EXISTS baa ON baa.boo;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "DROP INDEX |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INDEX ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest keywords for "DROP INDEX IF |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INDEX IF ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest keywords for "DROP INDEX baa |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INDEX baa ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest tabls for "DROP INDEX baa ON |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INDEX baa ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });
    });

    describe('DROP ROLE', function () {
      it('should handle "DROP ROLE boo;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP ROLE boo;',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

    describe('DROP STATS', function () {
      it('should handle "DROP STATS bla.boo;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP STATS bla.boo;',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DROP INCREMENTAL STATS bla.boo PARTITION (a=1, b = 2);|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INCREMENTAL STATS bla.boo PARTITION (a=1, b = 2);',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "DROP |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          containsKeywords: ['INCREMENTAL STATS', 'STATS'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "DROP STATS |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP STATS ',
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

      it('should suggest tables for "DROP STATS db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP STATS db.',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'db' }]}
          }
        });
      });

      it('should suggest keywords for "DROP INCREMENTAL |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INCREMENTAL ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['STATS']
          }
        });
      });

      it('should suggest tables for "DROP INCREMENTAL STATS |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INCREMENTAL STATS ',
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

      it('should suggest tables for "DROP INCREMENTAL STATS db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP STATS db.',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'db' }]}
          }
        });
      });

      it('should suggest keywords for "DROP INCREMENTAL STATS db.tbl |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INCREMENTAL STATS db.tbl ',
          afterCursor: '',
          dialect: 'impala',
          noErrors:true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION']
          }
        });
      });

      it('should suggest columns for "DROP INCREMENTAL STATS db.tbl PARTITION (|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INCREMENTAL STATS db.tbl PARTITION (',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }]} ]}
          }
        });
      });

      it('should suggest columns for "DROP INCREMENTAL STATS db.tbl PARTITION (bla = 1, |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP INCREMENTAL STATS db.tbl PARTITION (bla = 1, ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }]} ]}
          }
        });
      });
    });

    describe('DROP TABLE', function () {
      it('should handle "DROP TABLE db.tbl PURGE;"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE db.tbl PURGE;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "DROP TABLE |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { onlyTables: true },
            suggestKeywords: ['IF EXISTS'],
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables for "DROP TABLE db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE db.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'db' }], onlyTables: true }
          }
        });
      });

      it('should suggest keywords for "DROP TABLE IF |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE IF ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest tables for "DROP TABLE IF EXISTS |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE IF EXISTS ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { onlyTables: true },
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest keywords for "DROP TABLE foo |"', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE foo ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PURGE'],
            locations: [
              { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 15 } },
              { type: 'statementType', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 5 }, identifier: 'DROP TABLE' },
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15}, identifierChain: [{ name: 'foo' }]}
            ]
          }
        });
      });
    });

    describe('DROP TEMPORARY MACRO', function () {
      it('should handle "DROP TEMPORARY MACRO IF EXISTS boo;|', function () {
        assertAutoComplete({
          beforeCursor: 'DROP TEMPORARY MACRO IF EXISTS boo;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "DROP |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['TEMPORARY MACRO'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "DROP TEMPORARY |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP TEMPORARY ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FUNCTION', 'MACRO']
          }
        });
      });

      it('should suggest keywords for "DROP TEMPORARY MACRO |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP TEMPORARY MACRO ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest keywords for "DROP TEMPORARY MACRO IF |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP TEMPORARY MACRO IF ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });
    });

    describe('DROP TEMPORARY FUNCTION', function () {
      it('should suggest keywords for "DROP TEMPORARY FUNCTION |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP TEMPORARY FUNCTION ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest keywords for "DROP TEMPORARY FUNCTION IF |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP TEMPORARY FUNCTION IF ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });
    });

    describe('DROP VIEW', function () {
      it('should handle "DROP VIEW boo;|', function () {
        assertAutoComplete({
          beforeCursor: 'DROP VIEW boo;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DROP VIEW IF EXISTS baa.boo;|', function () {
        assertAutoComplete({
          beforeCursor: 'DROP VIEW IF EXISTS baa.boo;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest views for "DROP VIEW |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP VIEW ',
          afterCursor: '',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { onlyViews: true },
            suggestDatabases: { appendDot:true },
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest keywords for "DROP VIEW IF |', function () {
        assertAutoComplete({
          beforeCursor: 'DROP VIEW IF ',
          afterCursor: '',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest views for "DROP VIEW boo.|', function () {
        assertAutoComplete({
          beforeCursor: 'DROP VIEW boo.',
          afterCursor: '',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'boo' }], onlyViews: true }
          }
        });
      });
    });

    describe('TRUNCATE TABLE', function () {
      it('should handle "TRUNCATE TABLE baa.boo;"', function() {
        assertAutoComplete({
          beforeCursor: 'TRUNCATE TABLE baa.boo;',
          afterCursor: '',
          dialect: 'generic',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "TRUNCATE |"', function() {
        assertAutoComplete({
          beforeCursor: 'truncate ',
          afterCursor: '',
          dialect: 'generic',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables for "TRUNCATE TABLE |"', function() {
        assertAutoComplete({
          beforeCursor: 'TRUNCATE TABLE ',
          afterCursor: '',
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      describe('Hive specific', function () {
        it('should handle "TRUNCATE TABLE boo PARTITION (baa=1, boo = \'baa\'); |"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE boo PARTITION (baa=1, boo = \'baa\'); ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "TRUNCATE |"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TABLE']
            }
          });
        });

        it('should suggest tables for "TRUNCATE TABLE |"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "TRUNCATE TABLE boo |"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE boo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PARTITION']
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should handle "TRUNCATE TABLE IF EXISTS baa.boo;"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE IF EXISTS baa.boo;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest tables for "TRUNCATE TABLE |"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true },
              suggestKeywords: ['IF EXISTS']
            }
          });
        });

        it('should suggest keywords for "TRUNCATE TABLE IF |"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE IF ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['EXISTS']
            }
          });
        });

        it('should suggest tables for "TRUNCATE TABLE IF EXISTS |"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE IF EXISTS ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "TRUNCATE TABLE | boo"', function() {
          assertAutoComplete({
            beforeCursor: 'TRUNCATE TABLE ',
            afterCursor: ' boo',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IF EXISTS']
            }
          });
        });
      })
    })
  });
})();