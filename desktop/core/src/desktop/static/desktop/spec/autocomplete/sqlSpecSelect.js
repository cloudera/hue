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
define([
  'knockout',
  'desktop/js/autocomplete/sql',
  'desktop/spec/autocompleterTestUtils'
], function(ko, sql, testUtils) {

  describe('sql.js SELECT statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = testUtils.assertAutocomplete;

    it('should suggest keywords for "|"', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables and databases for "SELECT * |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables:{
            prependFrom:true
          },
          suggestDatabases:{
            prependFrom:true,
            appendDot:true
          }
        }
      });
    });

    it('should suggest keywords for "SELECT foo, bar |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT foo, bar ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables:{
            prependFrom:true
          },
          suggestDatabases:{
            prependFrom:true,
            appendDot:true
          },
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "SELECT foo AS a, bar |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT foo AS a, bar ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables:{
            prependFrom:true
          },
          suggestDatabases:{
            prependFrom:true,
            appendDot:true
          },
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTableA tta, testTableB |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']
        }
      });
    });
    it('should suggest databases or tables for "SELECT * fr|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * fr',
        afterCursor: '',
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

    it('should suggest databases or tables for "SELECT * FROM |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest databases or tables for "SELECT * FROM tes|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM tes',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest databases or tables for "SELECT * FROM `tes|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM `tes',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM database_two.|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            database: 'database_two'
          }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM `database_two`.|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM `database_two`.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            database: 'database_two'
          }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM `database_two`.`bla |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM `database_two`.`bla ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            database: 'database_two'
          }
        }
      });
    });

    describe('Complete Statements', function () {
      it('should handle "SELECT tta.* FROM testTableA tta, testTableB; |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tta.* FROM testTableA tta, testTableB; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT COUNT(*) FROM testTable; |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(*) FROM testTable;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      // Fails on YEAR(, and ROUND but recoverable error
      xit('should handle "SELECT tmp.bc, ROUND(tmp.r, 2) AS r FROM ( SELECT tstDb1.b1.cat AS bc, SUM(tstDb1.b1.price * tran.qua) AS r FROM tstDb1.b1 JOIN [SHUFFLE] tran ON ( tran.b_id = tstDb1.b1.id AND YEAR(tran.tran_d) BETWEEN 2008 AND 2010) GROUP BY tstDb1.b1.cat) tmp ORDER BY r DESC LIMIT 60; |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT tmp.bc, ROUND(tmp.r, 2) AS r FROM ( SELECT tstDb1.b1.cat AS bc, SUM(tstDb1.b1.price * tran.qua) AS r FROM tstDb1.b1 JOIN [SHUFFLE] tran ON ( tran.b_id = tstDb1.b1.id AND YEAR(tran.tran_d) BETWEEN 2008 AND 2010) GROUP BY tstDb1.b1.cat) tmp ORDER BY r DESC LIMIT 60;',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT * FROM testTable ORDER BY a ASC, b, c DESC, d; |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable ORDER BY a ASC, b, c DESC, d; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT * FROM testTable1 JOIN db1.table2; |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.table2; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT t1.foo FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2); |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.foo FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2); ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

    describe('Select List Completion', function() {
      it('should suggest tables for "SELECT |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: '',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });

      it('should suggest lowerCase for "select |"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: '',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables for "SELECT ALL |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ALL ',
          afterCursor: '',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables for "SELECT DISTINCT |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT DISTINCT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });

      it('should suggest keywords for "SELECT DISTINCT | a, b, c FROM tbl"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT DISTINCT ',
          afterCursor: ' a, b, c FROM tbl',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'tbl' }
          }
        });
      });

      it('should suggest tables for "SELECT | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM tableA;',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testWHERE"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testWHERE',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestColumns: { table: 'testWHERE' }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testON"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testON',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestColumns: { table: 'testON' }
          }
        });
      });

      it('should suggest aliases for "SELECT | FROM testTableA tta, testTableB"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, testTableB',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "select | from database_two.testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from database_two.testTable',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestColumns: { table: 'testTable', database: 'database_two' }
          }
        });
      });

      it('should suggest columns for "select | from `database one`.`test table`"', function () {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from `database one`.`test table`',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestColumns: { table: 'test table', database: 'database one' }
          }
        });
      });

      it('should suggest aliases for "SELECT | FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb',
          ignoreErrors: true,
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'ttaSum.', type: 'subquery' }, { name: 'ttb.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT a, | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, ',
          afterCursor: ' FROM tableA;',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest columns for "SELECT a,| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a,',
          afterCursor: ' FROM testTable',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT *, | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT *, ',
          afterCursor: ' FROM tableA;',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest keywords for "SELECT a | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a ',
          afterCursor: ' FROM tableA;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest keywords for "SELECT a |, FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a ',
          afterCursor: ', FROM tableA;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest keywords for "SELECT a, b | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b ',
          afterCursor: ' FROM tableA;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest keywords for "SELECT a |, b, c AS foo, d FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a ',
          afterCursor: ', b, c AS foo, d FROM tableA;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest columns for "SELECT | a, b, c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' a, b, c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, |,c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, ',
          afterCursor: ',c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTable' }
          }
        });
      });
    });

    describe('Functions', function () {
      it('should suggest table names with just a function', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(*) ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: {
              prependFrom: true
            },
            suggestDatabases: {
              prependFrom: true,
              appendDot: true
            },
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest columns in aggregate functions', function () {
        var aggregateFunctions = [
          { name: 'COUNT', dialect: 'generic'}];
        aggregateFunctions.forEach(function (aggregateFunction) {
          if (aggregateFunction.name === 'COUNT') {
            assertAutoComplete({
              beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
              afterCursor: ') FROM testTable',
              expectedResult: {
                lowerCase: false,
                suggestColumns: {
                  table: 'testTable'
                },
                suggestKeywords: ['*']
              }
            });
          } else {
            assertAutoComplete({
              beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
              afterCursor: ') FROM testTable',
              expectedResult: {
                lowerCase: false,
                suggestColumns: {
                  table: 'testTable'
                }
              }
            });
          }
        })
      });

      it('should suggest fields in functions', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT id, SUM(',
          afterCursor: ' FROM testTable',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest fields in functions after operators', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT id, SUM(a *  ',
          afterCursor: ' FROM testTable',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      })
    });

    describe('Hive Specific', function() {
      it('should suggest keywords after SELECT SelectList FROM TablePrimary ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM db.foo f ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary JOIN TablePrimary ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo JOIN baz ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['ON'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary JOIN TablePrimary before other JOIN ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo JOIN baz ',
          afterCursor: ' JOIN bla',
          dialect: 'hive',
          containsKeywords: ['ON'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary with linebreaks', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar\nFROM foo\n',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary LATERAL ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo LATERAL ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['VIEW']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary LATERAL ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM db.foo f LATERAL ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['VIEW']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary LATERAL ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM db.foo AS f LATERAL ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['VIEW']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary LATERAL VIEW ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo LATERAL VIEW ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['explode', 'posexplode']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary LATERAL VIEW udtf ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo LATERAL VIEW explode(bar) ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest keywords after SELECT SelectList FROM TablePrimary LATERAL VIEW udtf ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo LATERAL VIEW explode(bar) b ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest struct from map values', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap[\"anyKey\"].',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', key: '\"anyKey\"' }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest struct from map values without a given key', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap[].',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', key: null }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest struct from structs from map values', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap["anyKey"].fieldC.',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', key: '\"anyKey\"' }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest struct from structs from arrays', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testArray[1].fieldC.',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testArray', key: 1 }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest structs from maps from arrays', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testArray[1].testMap[\"key\"].',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testArray', key: 1 }, { name: 'testMap', key: '\"key\"' }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest struct from map values without a given key after where', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE testMap[].',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', key: null }]
            }
          }
        });
      });

      // Lateral view === only hive?
      describe('lateral views', function() {
        it('should suggest lateral view aliases', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            dialect: 'hive',
            containsFunctions: ['count(col)'],
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestColumns: {
                table: 'testTable'
              },
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testItem', type: 'alias' }]
            }
          });
        });

        it('should suggest columns in explode', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        });

        it('should suggest columns in explode for structs', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(a.b.',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns: {
                table: 'testTable',
                identifierChain: [ { name: 'a' }, { name: 'b' }]
              }
            }
          });
        });

        it('should suggest columns in posexplode', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW posexplode(',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        });

        it('should suggest lateral view aliases with multiple column aliases', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedTable AS (testKey, testValue)',
            dialect: 'hive',
            containsFunctions: ['count(col)'],
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestColumns: {
                table: 'testTable'
              },
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testKey', type: 'alias' }, { name: 'testValue', type: 'alias' }]
            }
          });
        });

        it('should suggest structs from exploded item references to arrays', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT testItem.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*'], // TODO: Verify that this is true
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testArray' }, { name: 'item' }]
              }
            }
          });
        });

        it('should suggest structs from multiple exploded item references to arrays', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT testItemA.',
            afterCursor: ' FROM testTable' +
            ' LATERAL VIEW explode(testArrayA) explodedTableA AS testItemA' +
            ' LATERAL VIEW explode(testArrayB) explodedTableB AS testItemB',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*'], // TODO: Verify that this is true
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testArrayA' }, { name: 'item' }]
              }
            }
          });
        });

        it('should support table references as arguments of explode function', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT\n testItemA,\n testItemB.',
            afterCursor: '\n\tFROM\n\t testTable2 tt2\n' +
            '\t LATERAL VIEW EXPLODE(tt2.testArrayA) explodedTableA AS testItemA\n' +
            '\t LATERAL VIEW EXPLODE(tt2.testArrayB) explodedTableB AS testItemB',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*'], // TODO: Verify that this is true
              suggestColumns: {
                table: 'testTable2',
                identifierChain: [{ name: 'testArrayB' }, { name: 'item' }]
              }
            }
          });
        });

        it('should suggest structs from exploded item references to exploded item references to arrays ', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ta2_exp.',
            afterCursor: ' FROM ' +
            '   testTable tt' +
            ' LATERAL VIEW explode(tt.testArray1) ta1 AS ta1_exp\n' +
            '   LATERAL VIEW explode(ta1_exp.testArray2)    ta2   AS  ta2_exp',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*'], // TODO: Verify that this is true
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testArray1' }, { name: 'item' }, { name: 'testArray2' }, { name: 'item' }]
              }
            }
          });
        });

        it('should suggest structs from references to exploded arrays', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT explodedTable.testItem.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testArray' }, { name: 'item' }]
              },
              suggestKeywords: ['*']
            }
          });
        });

        it('should suggest posexploded references to arrays', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT testValue.',
            afterCursor: ' FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS (testIndex, testValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*'], // TODO: Verify that this is true
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testArray' }, { name: 'item' }]
              }
            }
          });
        });

        it('should suggest exploded references to map values', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) AS (testMapKey, testMapValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testMap' }, { name: 'value' }]
              },
              suggestKeywords: ['*'] // TODO: Verify that this is true
            }
          });
        });

        it('should suggest exploded references to map values from view references', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT explodedMap.testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testMap' }, { name: 'value' }]
              },
              suggestKeywords: ['*'] // TODO: Verify that this is true
            }
          });
        });

        it('should suggest references to exploded references from view reference', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT explodedMap.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestIdentifiers: [{ name: 'testMapKey', type: 'alias' }, { name: 'testMapValue', type: 'alias' }],
              suggestKeywords: ['*'] // TODO: Check if really true
            }
          });
        });

        it('should suggest references to exploded references', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            dialect: 'hive',
            containsFunctions: ['count(col)'],
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestIdentifiers: [{ name: 'explodedMap.', type: 'alias' }, { name: 'testMapKey', type: 'alias' }, { name: 'testMapValue', type: 'alias' }],
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        });
      });
    });

    describe('Impala Specific', function() {
      it('should suggest keywords for SELECT * FROM testTableA tta, testTableB | ', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN', 'WHERE']
          }
        });
      });

      it('should not suggest struct from map values with hive style syntax', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap[\"anyKey\"].',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'testMap',  key: '\"anyKey\"' }]
            },
            suggestKeywords: ['*'] // TODO: Verify that this is true
          }
        });
      });

      it('should suggest fields from nested structs', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT columnA.fieldC.',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'columnA' }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*'] // TODO: Verify that this is true
          }
        });
      });

      it('should suggest fields from nested structs with table alias', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tt.columnA.fieldC.',
          afterCursor: ' FROM testTable tt',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'columnA' }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*'] // TODO: Verify that this is true
          }
        });
      });

      it('should suggest fields from nested structs with table alias', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tt.columnA.fieldC.',
          afterCursor: ' FROM testTable tt',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'columnA' }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*'] // TODO: Verify that this is true
          }
        });
      });


      // TODO: Result should have 'key', 'key' is only possible after call to see column type but as it's
      //       after FROM perhaps only maps are allowed there?
      //       If the map has a scalar value type (int etc.) it should also suggest 'value'
      //       For arrays it should suggest 'items' for scalar values
      it('should suggest fields from map values of type structs', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tm.',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap' }]
            }
          }
        });
      });

      it('should suggest fields from map values of type structs with partial identifier', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tm.a',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap' }]
            }
          }
        });
      });

      // Same as above, 'items' or 'value' for scalar
      it('should suggest items from arrays if complex in from clause', function() {
        assertAutoComplete({

          beforeCursor: 'SELECT ta.* FROM testTable t, t.testArray ta WHERE ta.',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testArray' }]
            }
          }
        });
      });

      it('should suggest columns from table refs in from clause', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t.*  FROM testTable t, t.',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest map references in select', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          dialect: 'impala',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestIdentifiers: [{ name: 't.', type: 'alias' }, { name: 'tm.', type: 'alias' }]
          }
        });
      });

      // TODO: Should add Key and Value once we know it's a map
      it('should suggest fields with key and value in where clause from map values of type structs', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'testMap' }]
            }
          }
        });
      });

      it('should suggest fields in where clause from map values of type structs', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.value.',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'testMap' }, { name: 'value' }]
            }
          }
        });
      });

      it('should suggest values for map keys', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable t, t.testMap tm WHERE tm.key =',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'testMap' }, { name: 'key' }]
            },
            suggestIdentifiers : [{ name: 't.', type: 'alias' }, { name: 'tm.', type: 'alias' }]
          }
        });
      });

      it('should suggest values from fields in map values in conditions', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable t, t.testMap m WHERE m.field = ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'testMap' }, { name: 'field' }]
            },
            suggestIdentifiers : [{ name: 't.', type: 'alias' }, { name: 'm.', type: 'alias' }]
          }
        });
      })
    });

    describe('Hive and Impala Struct Completion', function() {
      it('should suggest fields from columns that are structs', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT columnA.',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'], // TODO: Verify that this is true
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'columnA' }]
            }
          }
        });
      });

      it('should suggest fields from nested structs', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT columnA.fieldC.',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'columnA' }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*'] // TODO: Verify that this is true
          }
        });
      });

      it('should suggest fields from nested structs with database reference', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT columnA.fieldC.',
          afterCursor: ' FROM database_two.testTable',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              database: 'database_two',
              identifierChain: [{ name: 'columnA' }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*'] // TODO: Verify that this is true
          }
        });
      });
    });

    describe('Value Expression Completion', function() {
      it('should suggest columns for "SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'tbl2' }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE id = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE id =',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'id' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT * FROM testTable WHERE | = id"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: ' = id',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'id' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d < |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d < ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <= |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <= ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <=> |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <=> ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <> |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <> ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d >= |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d > |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d > ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d != |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d != ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + 1 != |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + 1 != ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE bla| + 1 != 3"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE bla',
          afterCursor: ' + 1 != 3',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d - |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d - ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d * |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d * ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d / |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d / ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d % |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d % ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d | |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d | ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d & |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d & ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d ^ |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ^ ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE ~|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE ~',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE -|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE -',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      xit('should suggest columns for "SELECT a, b, c FROM testTable WHERE | RLIKE \'bla bla\'"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ',
          afterCursor: ' RLIKE \'bla bla\'',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT bar FROM foo WHERE id = 1 |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
          afterCursor: '',
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['<', '<=', '<>', '=', '>', '>=', 'AND', 'BETWEEN', 'GROUP BY', 'IN', 'IS NOT NULL', 'IS NULL', 'LIMIT', 'NOT BETWEEN', 'NOT IN', 'OR', 'ORDER BY']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE id <=> 1 |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id <=> 1 ',
          afterCursor: '',
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['<', '<=', '<>', '=', '>', '>=', 'AND', 'BETWEEN', 'GROUP BY', 'IN', 'IS NOT NULL', 'IS NULL', 'LIMIT', 'NOT BETWEEN', 'NOT IN', 'OR', 'ORDER BY']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE id IS |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id IS ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT NULL', 'NULL']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE id IS NOT |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id IS NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NULL']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE id IS | NULL"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id IS ',
          afterCursor: ' NULL',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT']
          }
        });
      });

      xit('should suggest keywords for "SELECT * FROM foo WHERE id | LIKE \'bla bla\'"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id ',
          afterCursor: ' LIKE \'bla bla\'',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT']
          }
        });
      });

      it('should suggest identifiers for "SELECT * FROM foo bla, bar WHERE id IS NULL AND |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bla, bar WHERE id IS NULL AND ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }, { name: 'bar.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL && |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL && ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL OR | AND 1 + 1 > 1"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL OR ',
          afterCursor: ' AND 1 + 1 > 1',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL || |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL || ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE NOT |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'foo' },
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE ! |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE ! ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE !|', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE !',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords for "SELECT bar FROM foo WHERE id = 1 |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['<', '<=', '<=>', '<>', '=', '>', '>=', 'AND', 'BETWEEN', 'GROUP BY', 'IN', 'IS NOT NULL', 'IS NULL', 'LIMIT', 'NOT BETWEEN', 'NOT IN', 'OR', 'ORDER BY']
            }
          });
        });
      })
    });

    describe('Field Completion', function() {
      it('should suggest columns for table after WHERE', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS', 'NOT EXISTS']
          }
        });
      });

      it('should suggest columns for table after WHERE with partial column', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS', 'NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for table after WHERE NOT', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest keywords after WHERE foo = \'bar\' ', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE foo = \'bar\' ',
          afterCursor: '',
          containsKeywords: ['AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords after WHERE with partial AND', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c, d, e FROM tableOne WHERE c >= 9998 an',
          afterCursor: '',
          containsKeywords: ['AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for table after WHERE foo = \'bar\' AND ', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE foo = \'bar\' AND ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });


      it('should suggest columns for table after WHERE but before = \'bar\' AND ', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: ' = \'bar\' AND ',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for between after value expression', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a ',
          afterCursor: '',
          containsKeywords: ['BETWEEN', 'NOT BETWEEN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for like and regex after value expression', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a ',
          afterCursor: '',
          containsKeywords: ['LIKE', 'RLIKE', 'REGEX', 'NOT LIKE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for between after value expression', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['BETWEEN', 'EXISTS', 'IN', 'LIKE']
          }
        });
      });

      it('should suggest values after between', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a BETWEEN ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: { table: 'testTable', identifierChain: [{ name: 'a' }] },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest suggest select for exists subquery', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a OR NOT EXISTS (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      describe('ORDER BY Clause', function () {
        it('should suggest BY after ORDER', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable ORDER ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest columns for table after ORDER BY ', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable ORDER BY ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { table: 'testTable' }
            }
          });
        });

        it('should suggest columns for table after ORDER BY with db reference', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest keywords for table after ORDER BY table', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ',
            afterCursor: '',
            dialect: 'generic',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ASC', 'DESC', 'LIMIT']
            }
          });
        });

        it('should suggest columns for table after ORDER BY col', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo, ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest columns for table after ORDER BY col ASC', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ASC, ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest keywords for table after ORDER BY table DESC, table', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
            afterCursor: '',
            dialect: 'generic',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ASC', 'DESC', 'LIMIT']
            }
          });
        });

        it('should suggest keywords for table after ORDER BY table DESC, table and before ,table', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
            afterCursor: ', bla',
            containsKeywords: ['ASC', 'DESC'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        describe('Impala specific', function () {
          it('should suggest keywords for table after ORDER BY table', function() {
            assertAutoComplete({
              beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ',
              afterCursor: '',
              dialect: 'impala',
              expectedResult: {
                lowerCase: false,
                suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'NULLS FIRST', 'NULLS LAST']
              }
            });
          });

          it('should suggest keywords for table after ORDER BY integer', function() {
            assertAutoComplete({
              beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY 1 ',
              afterCursor: '',
              dialect: 'impala',
              expectedResult: {
                lowerCase: false,
                suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'NULLS FIRST', 'NULLS LAST']
              }
            });
          });

          it('should suggest keywords for table after ORDER BY table NULLS', function() {
            assertAutoComplete({
              beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo NULLS ',
              afterCursor: '',
              dialect: 'impala',
              expectedResult: {
                lowerCase: false,
                suggestKeywords: ['FIRST', 'LAST']
              }
            });
          });

          it('should suggest keywords for table after ORDER BY table DESC, table', function() {
            assertAutoComplete({
              beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
              afterCursor: '',
              dialect: 'impala',
              expectedResult: {
                lowerCase: false,
                suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'NULLS FIRST', 'NULLS LAST']
              }
            });

            it('should suggest keywords for table after ORDER BY table DESC, table and before ,table', function() {
              assertAutoComplete({
                beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
                afterCursor: ', bla',
                dialect: 'impala',
                containsKeywords: ['ASC', 'DESC', 'NULLS FIRST', 'NULLS LAST'],
                expectedResult: {
                  lowerCase: false
                }
              });
            });

            it('should suggest keywords for table after ORDER BY table DESC, table ASC NULLS and before ,table', function() {
              assertAutoComplete({
                beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ASC NULLS ',
                afterCursor: ', bla',
                dialect: 'impala',
                containsKeywords: ['FIRST', 'LAST'],
                expectedResult: {
                  lowerCase: false
                }
              });
            });
          });
        });
      });


      describe('GROUP BY Clause', function () {
        it('should suggest BY after GROUP', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable GROUP ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest aliases in GROUP BY', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY ',
            afterCursor: '',
            dialect: 'generic',
            expectedResult : {
              lowerCase: false,
              suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
            }
          });
        });

        it('should suggest aliases in GROUP BY table', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla, ',
            afterCursor: '',
            dialect: 'generic',
            expectedResult : {
              lowerCase: false,
              suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
            }
          });
        });

        it('should suggest aliases in GROUP BY tableOne but before another table', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla, ',
            afterCursor: ', foo',
            dialect: 'generic',
            expectedResult : {
              lowerCase: false,
              suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
            }
          });
        });

        it('should suggest columns for table after GROUP BY ', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable GROUP BY ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { table: 'testTable' }
            }
          });
        });

        it('should suggest columns for table after GROUP BY with db reference ', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });
      });

      it('should suggest columns for table after ON ', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable1' }
          }
        });
      });

      it('should suggest columns for table after ON with database reference', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable1', database: 'database_two' }
          }
        });
      });

      it('should suggest columns for table with table ref', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable.',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns with table alias', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tt.',
          afterCursor: ' FROM testTable tt',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns with table alias from database reference', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tt.',
          afterCursor: ' FROM database_two.testTable tt',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTable', database: 'database_two' }
          }
        });
      });

      it('should suggest columns with multiple table aliases', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tta.',
          afterCursor: ' FROM testTableA tta, testTableB ttb',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTableA' }
          }
        });
        assertAutoComplete({
          beforeCursor: 'SELECT ttb.',
          afterCursor: ' FROM testTableA tta, testTableB ttb',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTableB' }
          }
        });
      });
    });

    describe('Joins', function() {
      it('should suggest tables to join with', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest tables to join with from database', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { database: 'db1' }
          }
        });
      });

      it('should suggest tables to join with from database before other join', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.',
          afterCursor: ' JOIN foo',
          expectedResult: {
            lowerCase: false,
            suggestTables: { database: 'db1' }
          }
        });
      });

      it('should suggest table references in join condition if not already there', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest table references in join condition if not already there with parenthesis', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest table references in join condition if not already there for multiple conditions after AND', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest table references in join condition if not already there for multiple conditions', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: ' AND testTable1.testColumn1 = testTable2.testColumn3',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest field references in join condition if table reference is present', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable2'}
          }
        });
      });

      it('should suggest field references in join condition if table reference is present', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 cross join testTable2 on testTable1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestColumns: { table: 'testTable1'}
          }
        });
      });

      it('should suggest correct identifier in join condition if database reference is present', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 join db.testTable2 on ',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'db.testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest identifiers or values in join condition if table reference is present from multiple tables', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = ',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest field references in join condition if table reference is present from multiple tables', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.',
          afterCursor: '',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: true,
            suggestColumns: { table: 'testTable2'}
          }
        });
      });

      it('should suggest field references in join condition if table reference is present from multiple tables for multiple conditions', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.',
          afterCursor: '',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable1'}
          }
        });
      });

      xit('should suggest join types before JOIN', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 ',
          afterCursor: ' JOIN',
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']
          }
        });
      });

      it('should suggest join types before JOIN and after FULL', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 FULL ',
          afterCursor: ' JOIN',
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['OUTER']
          }
        });
      });

      it('should suggest join types before JOIN and after LEFT', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT ',
          afterCursor: ' JOIN',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ANTI', 'OUTER', 'SEMI']
          }
        });
      });

      it('should suggest join types before JOIN and after RIGHT', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 RIGHT ',
          afterCursor: ' JOIN',
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['OUTER']
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest join types', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['LEFT SEMI JOIN', 'CROSS JOIN'], // Tested in full above
            expectedResult: {
              lowerCase: false
            }
          });
        });

        xit('should suggest join types before JOIN', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 ',
            afterCursor: ' JOIN',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CROSS', 'FULL', 'FULL OUTER', 'LEFT', 'LEFT OUTER', 'LEFT SEMI', 'RIGHT', 'RIGHT OUTER']
            }
          });
        });

        it('should suggest join types before JOIN and after FULL', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 FULL ',
            afterCursor: ' JOIN',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['OUTER']
            }
          });
        });

        it('should suggest join types before JOIN and after LEFT', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT ',
            afterCursor: ' JOIN',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['OUTER', 'SEMI']
            }
          });
        });

        it('should suggest join types before JOIN and after RIGHT', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 RIGHT ',
            afterCursor: ' JOIN',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['OUTER']
            }
          });
        });

        it('should suggest table references in join conditions for multiple joins', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (',
            afterCursor: ' AND t1.c1 = t2.c2',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestIdentifiers: [{ name: 't1.', type: 'alias' }, { name: 'table2.', type: 'table' }, { name: 'table3.', type: 'table' }, { name: 't4.', type: 'alias' }]
            }
          });
        });

        it('should suggest tables in partial join conditions for multiple joins', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab',
            afterCursor: ' CROSS JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should suggest join types', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['LEFT ANTI JOIN', 'RIGHT ANTI JOIN'], // Tested in full above
            expectedResult: {
              lowerCase: false
            }
          });
        });

        xit('should suggest join types before JOIN', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 ',
            afterCursor: ' JOIN',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT ANTI', 'LEFT OUTER', 'LEFT SEMI', 'RIGHT', 'RIGHT ANTI', 'RIGHT OUTER', 'RIGHT SEMI']
            }
          });
        });

        it('should suggest join types before JOIN and after FULL', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 FULL ',
            afterCursor: ' JOIN',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['OUTER']
            }
          });
        });

        it('should suggest join types before JOIN and after LEFT', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT ',
            afterCursor: ' JOIN',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ANTI', 'OUTER', 'SEMI']
            }
          });
        });

        it('should suggest join types before JOIN and after RIGHT', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 RIGHT ',
            afterCursor: ' JOIN',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ANTI', 'OUTER', 'SEMI']
            }
          });
        });

        it('should suggest table references in join conditions for multiple joins', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT OUTER JOIN table2 INNER JOIN table3 JOIN table4 t4 ON (',
            afterCursor: ' AND t1.c1 = t2.c2',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestIdentifiers: [{ name: 't1.', type: 'alias' }, { name: 'table2.', type: 'table' }, { name: 'table3.', type: 'table' }, { name: 't4.', type: 'alias' }]
            }
          });
        });

        it('should suggest tables in partial join conditions for multiple joins', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab',
            afterCursor: ' INNER JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });
      });
    });

    describe('Subqueries in WHERE Clause', function () {
      it('should suggest keywords for in predicate with no IN', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar ',
          afterCursor: '',
          dialect: 'generic',
          containsKeywords: ['IN', 'NOT IN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for in predicate after NOT', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar NOT ',
          afterCursor: '',
          containsKeywords: ['IN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords at the start of a subquery', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT'],
            suggestValues: { identifierChain: [{name: 'bar'}], table: 'foo' }
          }
        });
      });

      it('should suggest keywords at the start of a subquery following case', function() {
        assertAutoComplete({
          beforeCursor: 'select * from foo, bar where bar.bla in (',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['SELECT'],
            suggestValues: { identifierChain: [{name: 'bla'}], table: 'bar' }
          }
        });
      });

      it('should suggest values in an in value list', function() {
        assertAutoComplete({
          beforeCursor: 'select * from foo, bar where bar.bla in (\'a\', ',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestValues: { identifierChain: [{name: 'bla'}], table: 'bar' }
          }
        });
      });

      it('should suggest database or table names after SELECT in subquery', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT ',
          afterCursor: '',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });


      it('should suggest database or table names after SELECT in subquery with end parenthesis', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM bar WHERE foo NOT IN (SELECT ',
          afterCursor: ')',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });
    });

    describe('Subqueries in FROM Clause', function () {
      it('should suggest keywords at the start of a subquery', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest keywords at the start of a subquery following case', function() {
        assertAutoComplete({
          beforeCursor: 'select * from (',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest database or table names after SELECT in subquery', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: '',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });

      it('should suggest columns before a numeric expression', function() {
        assertAutoComplete({
          beforeCursor: 'select foo from tbl where ',
          afterCursor: ' % 2 = 0',
          expectedResult: {
            lowerCase: true,
            suggestColumns: { table: 'tbl' }
          }
        });
      });

      it('should suggest columns within a subquery', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT "contains an even number" FROM t1, t2 AS ta2 WHERE EXISTS (SELECT foo FROM t3 WHERE ',
          afterCursor: ' % 2 = 0',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 't1.', type: 'table' }, { name: 'ta2.', type: 'alias' }, { name: 't3.', type: 'table'}]
          }
        });
      });

      it('should suggest identifiers after SELECT with subqueries defined', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT bla FROM abc WHERE foo > 1) bar',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestIdentifiers: [{ name: 'bar.', type: 'subquery'}]
          }
        });
      });

      it('should suggest database or table names after SELECT in subquery with end parenthesis', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ')',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            }
          }
        });
      });

      it('should suggest identifiers with a mix of subqueries and tables', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT * FROM tableOne) AS subqueryOne, someDb.tableTwo tAlias, tableThree, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) subqueryTwo;',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestIdentifiers: [{ name: 'subqueryOne.', type: 'subquery'}, { name: 'tAlias.', type: 'alias'}, { name: 'tableThree.', type: 'table'}, { name: 'subqueryTwo.', type: 'subquery'}]
          }
        });
      });

      it('should suggest columns in a subquery with other subqueries', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ' FROM tableOne) subqueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subqueryTwo;',
          containsFunctions: ['count(col)'],
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestColumns: {
              table: 'tableOne'
            }
          }
        });
      });
    });
  });
});