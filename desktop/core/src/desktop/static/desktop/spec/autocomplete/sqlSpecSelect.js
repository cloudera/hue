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

      // Fails on YEAR( in JOIN condition (should be valueExpression)
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

      it('should handle "SELECT CASE a WHEN b THEN c WHEN d THEN e WHEN f THEN g ELSE h END FROM foo WHERE bar IN (SELECT * FROM bla);|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN b THEN c WHEN d THEN e ELSE h END FROM foo WHERE bar IN (SELECT * FROM bla);',
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
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
            suggestColumns: { table: 'tbl' }
          }
        });
      });

      it('should suggest tables for "SELECT | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM tableA;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testWHERE"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testWHERE',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: { table: 'testWHERE' }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testON"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testON',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: { table: 'testON' }
          }
        });
      });

      it('should suggest aliases for "SELECT | FROM testTableA tta, testTableB"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, testTableB',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "select | from database_two.testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from database_two.testTable',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable', database: 'database_two' }
          }
        });
      });

      it('should suggest columns for "select | from `database one`.`test table`"', function () {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from `database one`.`test table`',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: { table: 'test table', database: 'database one' }
          }
        });
      });

      it('should suggest aliases for "SELECT | FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'ttaSum.', type: 'subquery' }, { name: 'ttb.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT a, | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, ',
          afterCursor: ' FROM tableA;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest columns for "SELECT a,| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a,',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT *, | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT *, ',
          afterCursor: ' FROM tableA;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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

      it('should suggest columns for "SELECT | a, cast(b as int), c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' a, cast(b as int), c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, |,c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, ',
          afterCursor: ',c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });
    });

    describe('Functions', function () {
      it('should suggest tables for "SELECT COUNT(*) |"', function() {
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

      it('should suggest keywords for "SELECT COUNT(foo |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo ',
          afterCursor: '',
          containsKeywords: ['AND', '='],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT COUNT(foo, |) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo, ',
          afterCursor: ') FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT COUNT(foo, bl|, bla) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo, bl',
          afterCursor: ',bla) FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest keywords for "SELECT COUNT(foo, bla |, bar)"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo ',
          afterCursor: ', bar)',
          containsKeywords: ['AND', '='],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns and values for "SELECT COUNT(foo, bl + |, bla) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo, bl = ',
          afterCursor: ',bla) FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' },
            suggestValues: { identifierChain: [ {name: 'bl' }], table: 'bar' }
          }
        });
      });

      it('should suggest functions for "SELECT CAST(|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(bla| FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla',
          afterCursor: ' FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS INT FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS INT FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS STRING) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS STRING) FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(bla| AS STRING) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla',
          afterCursor: ' AS STRING) FROM bar;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest keywords for "SELECT CAST(bla |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla ',
          afterCursor: '',
          containsKeywords: ['AS', 'AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT CAST(bla | FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla ',
          afterCursor: ' FROM bar;',
          containsKeywords: ['AS', 'AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "select cast(bla as |"', function() {
        assertAutoComplete({
          beforeCursor: 'select cast(bla as ',
          afterCursor: '',
          containsKeywords: ['INT', 'STRING'],
          expectedResult: {
            lowerCase: true
          }
        });
      });

      it('should suggest keywords for "SELECT CAST(bla AS | FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla AS ',
          afterCursor: ' FROM bar;',
          containsKeywords: ['INT', 'STRING'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT CAST(bla AS ST|) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla AS ST',
          afterCursor: ') FROM bar;',
          containsKeywords: ['INT', 'STRING'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT CAST(AS |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(AS ',
          afterCursor: '',
          containsKeywords: ['INT', 'STRING'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla FROM |  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla FROM ',
          afterCursor: ' FROM bar;',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla ,|  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla ,',
          afterCursor: ' FROM bar;',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT a, extract(bla FROM |)  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, extract(bla FROM ',
          afterCursor: ') FROM bar;',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla ,|)  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla ,',
          afterCursor: ') FROM bar;',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'bar' }
          }
        });
      });


      it('should suggest columns for "SELECT <GeneralSetFunction>(|) FROM testTable"', function () {
        var aggregateFunctions = [
          { name: 'APPX_MEDIAN', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'AVG', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'AVG', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'AVG', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'collect_set', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'COLLECT_LIST', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'COUNT', dialect: 'generic', suggestKeywords: ['*', 'DISTINCT'] },
          { name: 'COUNT', dialect: 'hive', suggestKeywords: ['*', 'DISTINCT'] },
          { name: 'COUNT', dialect: 'impala', suggestKeywords: ['*', 'ALL', 'DISTINCT'] },
          { name: 'GROUP_CONCAT', dialect: 'impala', suggestKeywords: ['ALL'] },
          { name: 'stddev', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'STDDEV_POP', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'STDDEV_POP', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'STDDEV_POP', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'STDDEV_SAMP', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'STDDEV_SAMP', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'STDDEV_SAMP', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'SUM', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'sum', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'SUM', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'MAX', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'MAX', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'max', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'MIN', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'MIN', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'MIN', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'VARIANCE', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'variance_pop', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'VARIANCE_SAMP', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'VAR_POP', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'VAR_POP', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'VAR_POP', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] },
          { name: 'var_samp', dialect: 'generic', suggestKeywords: ['DISTINCT'] },
          { name: 'VAR_SAMP', dialect: 'hive', suggestKeywords: ['DISTINCT'] },
          { name: 'VAR_SAMP', dialect: 'impala', suggestKeywords: ['ALL', 'DISTINCT'] }
        ];
        aggregateFunctions.forEach(function (aggregateFunction) {
          if (aggregateFunction.name === 'COUNT') {
            assertAutoComplete({
              beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
              afterCursor: ') FROM testTable',
              dialect: aggregateFunction.dialect,
              expectedResult: {
                lowerCase: false,
                suggestColumns: {
                  table: 'testTable'
                },
                suggestKeywords: aggregateFunction.suggestKeywords || ['*']
              }
            });
          } else {
            var expectedResult = {
              lowerCase: false,
              suggestFunctions: true,
              suggestColumns: {
                table: 'testTable'
              }
            };
            if (aggregateFunction.suggestKeywords) {
              expectedResult.suggestKeywords = aggregateFunction.suggestKeywords
            }
            assertAutoComplete({
              beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
              afterCursor: ') FROM testTable',
              dialect: aggregateFunction.dialect,
              expectedResult: expectedResult
            });
          }
        })
      });

      it('should suggest columns for "SELECT <BinarySetFunction>(|,col) FROM testTable"', function () {
        var binaryFunctions = [
          { name: 'CORR', dialect: 'hive' },
          { name: 'COVAR_POP', dialect: 'hive' },
          { name: 'COVAR_SAMP', dialect: 'hive' }
        ];
        
        binaryFunctions.forEach(function (binaryFunction) {
          assertAutoComplete({
            beforeCursor: 'SELECT ' + binaryFunction.name + '(',
            afterCursor: ',col) FROM testTable',
            dialect: binaryFunction.dialect,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: true,
              suggestColumns: {
                table: 'testTable'
              },
              suggestKeywords: ['DISTINCT']
            }
          });
        })
      });

      it('should suggest columns for "SELECT <BinarySetFunction>(,|) FROM testTable"', function () {
        var binaryFunctions = [
          { name: 'CORR', dialect: 'hive' },
          { name: 'COVAR_POP', dialect: 'hive' },
          { name: 'COVAR_SAMP', dialect: 'hive' }
        ];

        binaryFunctions.forEach(function (binaryFunction) {
          assertAutoComplete({
            beforeCursor: 'SELECT ' + binaryFunction.name + '(,',
            afterCursor: ') FROM testTable',
            dialect: binaryFunction.dialect,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: true,
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        })
      });

      it('should suggest columns for "SELECT <BinarySetFunction>(| FROM testTable"', function () {
        var binaryFunctions = [
          { name: 'CORR', dialect: 'hive' },
          { name: 'COVAR_POP', dialect: 'hive' },
          { name: 'COVAR_SAMP', dialect: 'hive' }
        ];

        binaryFunctions.forEach(function (binaryFunction) {
          assertAutoComplete({
            beforeCursor: 'SELECT ' + binaryFunction.name + '(',
            afterCursor: ' FROM testTable',
            dialect: binaryFunction.dialect,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: true,
              suggestColumns: {
                table: 'testTable'
              },
              suggestKeywords: ['DISTINCT']
            }
          });
        })
      });

      it('should suggest columns for "SELECT id, SUM(a * | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT id, SUM(a * ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestKeywords: ['WHEN']
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b AND | THEN FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b AND ',
          afterCursor: ' THEN FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = b AND | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = b AND ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a = b | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = b ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['WHEN', 'AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b OR | THEN boo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b OR ',
          afterCursor: ' THEN boo FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b OR c THEN boo OR | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b OR c THEN boo OR ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a =| WHEN c THEN d END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a =',
          afterCursor: ' WHEN c THEN d END FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestValues: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a =| WHEN c THEN d ELSE e END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a =',
          afterCursor: ' WHEN c THEN d ELSE e END FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestValues: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['OR', 'END'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d=| ELSE FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d=',
          afterCursor: ' ELSE FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestValues: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a = c WHEN c THEN d=1 | bla=foo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d=1 ',
          afterCursor: ' bla=foo FROM testTable',
          containsKeywords: ['<', 'WHEN', 'ELSE', 'END'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a = c WHEN c THEN d=1 | bla=foo END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d=1 ',
          afterCursor: ' bla=foo FROM testTable',
          containsKeywords: ['<', 'WHEN', 'ELSE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE e AND | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE e AND ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE ELSE | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ELSE ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE | ELSE a FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ',
          afterCursor: ' ELSE a FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestKeywords: ['WHEN']
          }
        });
      });

      it('should suggest columns for "SELECT CASE | ELSE FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ',
          afterCursor: ' ELSE FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestKeywords: ['WHEN']
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE e | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE e ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['OR', 'END'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN THEN boo OR | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN THEN boo OR ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest keywords for "SELECT CASE | a = b THEN FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ',
          afterCursor: ' a = b THEN FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['WHEN']
          }
        });
      });

      it('should suggest keywords for "SELECT CASE | a = b THEN boo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ',
          afterCursor: ' a = b THEN boo FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['WHEN']
          }
        });
      });

      it('should suggest keywords for "SELECT CASE | THEN boo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ',
          afterCursor: ' THEN boo FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['WHEN'],
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN | boo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' boo FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN bla| boo WHEN b THEN c END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN bla',
          afterCursor: ' boo WHEN b THEN c END FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a WHEN b THEN c WHEN | boo ELSE c FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN b THEN c WHEN ',
          afterCursor: ' boo ELSE c FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a WHEN b THEN c WHEN | boo WHEN d THEN e END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN b THEN c WHEN ',
          afterCursor: ' boo WHEN d THEN e END FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a WHEN b THEN c | WHEN d THEN e END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN b THEN c ',
          afterCursor: ' WHEN d THEN e END FROM testTable',
          containsKeywords: ['WHEN', 'AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a WHEN b THEN c | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN b THEN c ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['WHEN', 'AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN | THEN FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' THEN FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest values for "SELECT CASE WHEN | = a FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' = a FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestValues: { identifierChain :[{ name :'a'}], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN ab| THEN bla ELSE foo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ab',
          afterCursor: ' THEN bla ELSE foo FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE bla WHEN ab| THEN bla ELSE foo END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE bla WHEN ab',
          afterCursor: ' THEN bla ELSE foo END FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a WHEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            },
            suggestValues: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['AND', 'THEN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c | d FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c ',
          afterCursor: ' d FROM testTable',
          containsKeywords: ['THEN', 'OR'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN | g FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN ',
          afterCursor: ' g FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN THEN | g FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN THEN ',
          afterCursor: ' g FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN THEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN THEN ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: {
              table: 'testTable'
            }
          }
        });
      });
    });

    describe('Hive Specific', function() {
      it('should suggest keywords for "SELECT bar FROM foo |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM db.foo f |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM foo JOIN baz |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM foo JOIN baz | JOIN bla"', function () {
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

      it('should suggest keywords for "SELECT bar\\nFROM foo\\n|"', function () {
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

      it('should suggest keywords for "SELECT bar FROM foo LATERAL |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM db.foo f LATERAL |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM db.foo AS f LATERAL |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM foo LATERAL VIEW |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM foo LATERAL VIEW explode(bar) |"', function () {
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

      it('should suggest keywords for "SELECT bar FROM foo LATERAL VIEW explode(bar) b |"', function () {
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

      it('should suggest columns for "SELECT testMap[\"anyKey\"].| FROM testTable"', function() {
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

      it('should suggest columns for "SELECT testMap[].| FROM testTable"', function() {
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

      it('should suggest columns for "SELECT testMap["anyKey"].fieldC.| FROM testTable"', function() {
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

      it('should suggest columns for "SELECT testArray[1].fieldC.| FROM testTable"', function() {
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

      it('should suggest columns for "SELECT testArray[1].testMap[\"key\"].| FROM testTable"', function() {
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

      it('should suggest identifiers for "SELECT * FROM testTable WHERE testMap[].|"', function() {
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
        it('should suggest aliases for "SELECT | FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestColumns: {
                table: 'testTable'
              },
              suggestAggregateFunctions: true,
              suggestFunctions: true,
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testItem', type: 'alias' }]
            }
          });
        });

        it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW explode(|"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestFunctions: true,
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW explode(a.b.|"', function () {
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

        it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW posexplode(|"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW posexplode(',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestFunctions: true,
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        });

        it('should suggest aliases for "SELECT |  FROM testTable LATERAL VIEW explode(testMap) explodedTable AS (testKey, testValue)"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedTable AS (testKey, testValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestColumns: {
                table: 'testTable'
              },
              suggestAggregateFunctions: true,
              suggestFunctions: true,
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testKey', type: 'alias' }, { name: 'testValue', type: 'alias' }]
            }
          });
        });

        it('should suggest columns for "SELECT testItem.| FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem"', function () {
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

        it('should suggest columns for "SELECT testItemA.| FROM testTable LATERAL VIEW explode(testArrayA) explodedTableA AS testItemA LATERAL VIEW explode(testArrayB) explodedTableB AS testItemB"', function () {
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

        it('should suggest columns for "SELECT\\n testItemA,\\n testItemB.|\\n\\tFROM\\n\\t testTable2 tt2\\n\\t LATERAL VIEW EXPLODE(tt2.testArrayA) explodedTableA AS testItemA\\n\\t LATERAL VIEW EXPLODE(tt2.testArrayB) explodedTableB AS testItemB"', function() {
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

        it('should suggest columns for "SELECT ta2_exp.| FROM    testTable tt LATERAL VIEW explode(tt.testArray1) ta1 AS ta1_exp\\n   LATERAL VIEW explode(ta1_exp.testArray2)    ta2   AS  ta2_exp"', function () {
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

        it('should suggest columns for "SELECT explodedTable.testItem.| FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem"', function () {
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

        it('should suggest identifiers for "SELECT testValue.| FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS (testIndex, testValue)"', function () {
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

        it('should suggest columns for "SELECT testMapValue.| FROM testTable LATERAL VIEW explode(testMap) AS (testMapKey, testMapValue)"', function () {
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

        it('should suggest columns for "SELECT explodedMap.testMapValue.| FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)"', function () {
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

        it('should suggest identifier for "SELECT explodedMap.| FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)"', function () {
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

        it('should suggest identifiers for "SELECT | FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestAggregateFunctions: true,
              suggestFunctions: true,
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
      it('should suggest keywords for "SELECT * FROM testTableA tta, testTableB |"', function() {
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

      it('should suggest columns for "SELECT testMap[\"anyKey\"].| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap["anyKey"].',
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

      it('should suggest columns for "SELECT columnA.fieldC.| FROM testTable"', function() {
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

      it('should suggest columns for "SELECT tt.columnA.fieldC.| FROM testTable tt"', function() {
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

      it('should suggest columns for "SELECT tt.columnA.fieldC.| FROM testTable tt"', function() {
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
      it('should suggest columns for "SELECT tm.| FROM testTable t, t.testMap tm;"', function() {
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

      it('should suggest columns for "SELECT tm.a| FROM testTable t, t.testMap tm;"', function() {
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
      it('should suggest columns for "SELECT ta.* FROM testTable t, t.testArray ta WHERE ta.|"', function() {
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

      it('should suggest columns for "SELECT t.*  FROM testTable t, t.|"', function() {
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

      it('should suggest identifier for "SELECT | FROM testTable t, t.testMap tm;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestIdentifiers: [{ name: 't.', type: 'alias' }, { name: 'tm.', type: 'alias' }]
          }
        });
      });

      // TODO: Should add Key and Value once we know it's a map
      it('should suggest columns for "SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.|"', function() {
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

      it('should suggest columns for "SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.value.|"', function() {
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

      it('should suggest values for "SELECT * FROM testTable t, t.testMap tm WHERE tm.key =|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable t, t.testMap tm WHERE tm.key =',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'testMap' }, { name: 'key' }]
            },
            suggestIdentifiers : [{ name: 't.', type: 'alias' }, { name: 'tm.', type: 'alias' }]
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable t, t.testMap m WHERE m.field = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable t, t.testMap m WHERE m.field = ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
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
      it('should suggest columns for SELECT columnA.| FROM testTable"', function() {
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

      it('should suggest columns for "SELECT columnA.fieldC.| FROM testTable"', function() {
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

      it('should suggest columns for "SELECT columnA.fieldC.| FROM database_two.testTable"', function() {
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
            suggestFunctions: true,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'id' }]
            },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE -|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE -',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT -| FROM testTable WHERE id = 1;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT -',
          afterCursor: ' FROM testTable WHERE id = 1;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT 1 < | FROM testTable WHERE id = 1;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT 1 < ',
          afterCursor: ' FROM testTable WHERE id = 1;',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE -id = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE -id = ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
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
            suggestFunctions: true,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL || |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL || ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE NOT |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'foo' },
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE ! |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE ! ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE !|"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE !',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
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
      it('should suggest columns for "SELECT * FROM testTable WHERE |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS', 'NOT EXISTS']
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE a|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS', 'NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE foo = \'bar\' |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE foo = \'bar\' ',
          afterCursor: '',
          containsKeywords: ['AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT a, b, c, d, e FROM tableOne WHERE c >= 9998 an|"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c, d, e FROM tableOne WHERE c >= 9998 an',
          afterCursor: '',
          containsKeywords: ['AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE foo = \'bar\' AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE foo = \'bar\' AND ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });


      it('should suggest columns for "SELECT * FROM testTable WHERE | = \'bar\' AND "', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: ' = \'bar\' AND ',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE a |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a ',
          afterCursor: '',
          containsKeywords: ['BETWEEN', 'NOT BETWEEN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE a |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a ',
          afterCursor: '',
          containsKeywords: ['LIKE', 'RLIKE', 'REGEX', 'NOT LIKE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE a NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['BETWEEN', 'EXISTS', 'IN', 'LIKE']
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE a BETWEEN |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a BETWEEN ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestValues: { table: 'testTable', identifierChain: [{ name: 'a' }] },
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE a OR NOT EXISTS (|"', function() {
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
        it('should suggest keywords for "SELECT * FROM testTable ORDER |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable ORDER ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest columns for "SELECT * FROM testTable ORDER BY |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable ORDER BY ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { table: 'testTable' }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo |"', function() {
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

        it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo, |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo, ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo ASC, |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ASC, ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |"', function() {
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

        it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |, bla"', function() {
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
          it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo |"', function() {
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

          it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY 1 |"', function() {
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

          it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo NULLS |"', function() {
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

          it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |"', function() {
            assertAutoComplete({
              beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
              afterCursor: '',
              dialect: 'impala',
              expectedResult: {
                lowerCase: false,
                suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'NULLS FIRST', 'NULLS LAST']
              }
            });

            it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |, bla"', function() {
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

            it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ASC NULLS |, bla"', function() {
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
        it('should suggest keywords for "SELECT * FROM testTable GROUP |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable GROUP ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest identifiers for "SELECT * FROM testTableA tta, testTableB GROUP BY |"', function() {
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

        it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla, |"', function() {
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

        it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla, |, foo"', function() {
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

        it('should suggest columns for "SELECT * FROM testTable GROUP BY |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable GROUP BY ',
            afterCursor: '',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { table: 'testTable' }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM database_two.testTable GROUP BY |"', function() {
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

      it('should suggest columns for "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable1' }
          }
        });
      });

      it('should suggest columns for "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable1', database: 'database_two' }
          }
        });
      });

      it('should suggest columns for "SELECT testTable.| FROM testTable"', function() {
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

      it('should suggest columns "SELECT tt.| FROM testTable tt"', function() {
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

      it('should suggest columns for "SELECT tt.| FROM database_two.testTable tt"', function() {
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

      it('should suggest columns for "SELECT tta.| FROM testTableA tta, testTableB ttb"', function() {
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
      it('should suggest tables for "SELECT * FROM testTable1 JOIN |"', function() {
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

      it('should suggest tables for "SELECT * FROM testTable1 JOIN db1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { database: 'db1' }
          }
        });
      });

      it('should suggest tables for "SELECT * FROM testTable1 JOIN db1.| JOIN foo"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.',
          afterCursor: ' JOIN foo',
          expectedResult: {
            lowerCase: false,
            suggestTables: { database: 'db1' }
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (| AND testTable1.testColumn1 = testTable2.testColumn3"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: ' AND testTable1.testColumn1 = testTable2.testColumn3',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable2'}
          }
        });
      });

      it('should suggest columns for "select * from testTable1 cross join testTable2 on testTable1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 cross join testTable2 on testTable1.',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestColumns: { table: 'testTable1'}
          }
        });
      });

      it('should suggest identifiers for "select * from testTable1 join db.testTable2 on |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 join db.testTable2 on ',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'db.testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest identifiers for "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = ',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.|"', function() {
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

      it('should suggest columns for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.|"', function() {
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

      xit('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN"', function () {
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

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 FULL | JOIN"', function () {
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

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 LEFT | JOIN"', function () {
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

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 RIGHT | JOIN"', function () {
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
        it('should suggest keywords for "SELECT t1.* FROM table1 t1 |"', function () {
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

        xit('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN"', function () {
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

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 FULL | JOIN"', function () {
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

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 LEFT | JOIN"', function () {
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

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 RIGHT | JOIN"', function () {
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

        it('should suggest identifiers for "SELECT t1.* FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (| AND t1.c1 = t2.c2"', function() {
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

        it('should suggest tables for "SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab| CROSS JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2"', function() {
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
        it('should suggest keywords for "SELECT t1.* FROM table1 t1 |"', function () {
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

        xit('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN"', function () {
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

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 FULL | JOIN"', function () {
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

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 LEFT | JOIN"', function () {
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

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 RIGHT | JOIN"', function () {
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

        it('should suggest tables for "SELECT t1.* FROM table1 t1 LEFT OUTER JOIN table2 INNER JOIN table3 JOIN table4 t4 ON (| AND t1.c1 = t2.c2"', function() {
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

        it('should suggest tables for "SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab| INNER JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2"', function() {
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
      it('should suggest keywords for "SELECT * FROM foo WHERE bar |"', function() {
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

      it('should suggest keywords for "SELECT * FROM foo WHERE bar NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar NOT ',
          afterCursor: '',
          containsKeywords: ['IN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE bar IN (|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT'],
            suggestFunctions: true,
            suggestValues: { identifierChain: [{name: 'bar'}], table: 'foo' },
            suggestColumns: { table: 'foo' }
          }
        });
      });

      it('should suggest keywords for "select * from foo, bar where bar.bla in (|"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from foo, bar where bar.bla in (',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['SELECT'],
            suggestFunctions: true,
            suggestValues: { identifierChain: [{name: 'bla'}], table: 'bar' },
            suggestIdentifiers: [{ name: 'foo.', type: 'table'}, { name: 'bar.', type: 'table'}]
          }
        });
      });

      it('should suggest values for "select * from foo, bar where bar.bla in (\'a\', |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from foo, bar where bar.bla in (\'a\', ',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestFunctions: true,
            suggestValues: { identifierChain: [{name: 'bla'}], table: 'bar' },
            suggestIdentifiers: [{ name: 'foo.', type: 'table'}, { name: 'bar.', type: 'table'}]
          }
        });
      });

      it('should suggest tables for "SELECT * FROM foo WHERE bar IN (SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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


      it('should suggest tables for "SELECT * FROM bar WHERE foo NOT IN (SELECT |)"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM bar WHERE foo NOT IN (SELECT ',
          afterCursor: ')',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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
      it('should suggest keywords for "SELECT * FROM (|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest keywords for "select * from (|"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from (',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest tables for "SELECT * FROM (SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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

      it('should suggest columns for "select foo from tbl where | % 2 = 0"', function() {
        assertAutoComplete({
          beforeCursor: 'select foo from tbl where ',
          afterCursor: ' % 2 = 0',
          expectedResult: {
            lowerCase: true,
            suggestFunctions: true,
            suggestColumns: { table: 'tbl' }
          }
        });
      });

      it('should suggest columns for "SELECT "contains an even number" FROM t1, t2 AS ta2 WHERE EXISTS (SELECT foo FROM t3 WHERE | % 2 = 0"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT "contains an even number" FROM t1, t2 AS ta2 WHERE EXISTS (SELECT foo FROM t3 WHERE ',
          afterCursor: ' % 2 = 0',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: true,
            suggestIdentifiers: [{ name: 't1.', type: 'table' }, { name: 'ta2.', type: 'alias' }, { name: 't3.', type: 'table'}]
          }
        });
      });

      it('should suggest identifiers for "SELECT | FROM (SELECT bla FROM abc WHERE foo > 1) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT bla FROM abc WHERE foo > 1) bar',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestIdentifiers: [{ name: 'bar.', type: 'subquery'}]
          }
        });
      });

      it('should suggest tables for "SELECT * FROM (SELECT |)"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ')',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
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

      it('should suggest identifiers for "SELECT | FROM (SELECT * FROM tableOne) AS subqueryOne, someDb.tableTwo tAlias, tableThree, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) subqueryTwo;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT * FROM tableOne) AS subqueryOne, someDb.tableTwo tAlias, tableThree, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) subqueryTwo;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestIdentifiers: [{ name: 'subqueryOne.', type: 'subquery'}, { name: 'tAlias.', type: 'alias'}, { name: 'tableThree.', type: 'table'}, { name: 'subqueryTwo.', type: 'subquery'}]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM (SELECT | FROM tableOne) subqueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subqueryTwo;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ' FROM tableOne) subqueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subqueryTwo;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestFunctions: true,
            suggestColumns: {
              table: 'tableOne'
            }
          }
        });
      });
    });
  });
});