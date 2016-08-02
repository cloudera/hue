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
        containsKeywords: ['AS', '+'],
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

    it('should suggest keywords for "SELECT foo AS a, bar |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT foo AS a, bar ',
        afterCursor: '',
        containsKeywords: ['AS', '+'],
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

    it('should suggest keywords for "SELECT * FROM testTableA tta, testTableB |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB ',
        afterCursor: '',
        dialect: 'generic',
        hasLocations: true,
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

    describe('Locations', function () {
      it('should suggest locations for "SELECT   |    FROM    testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT   ',
          afterCursor: '    FROM    testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTableA' },
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 22, last_column: 32}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT   a.|    FROM    testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT   a.',
          afterCursor: '    FROM    testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { identifierChain: [{ name: 'a' }], table: 'testTableA' },
            suggestKeywords: ['*'],
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 24, last_column: 34}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT aaa| FROM testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT aaa',
          afterCursor: ' FROM testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTableA' },
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 17, last_column: 27}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT aaa| \\nFROM testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT aaa',
          afterCursor: ' \nFROM testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTableA' },
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            locations: [
              { type: 'table', location: { first_line: 2, last_line: 2, first_column: 6, last_column: 16}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT |bbbb FROM testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: 'bbbb FROM testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTableA' },
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 28}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT a.aaaaa|bbbb FROM testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTableA' },
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 23, last_column: 33}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT foo.aaaaa|bbbb FROM testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT foo.aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { identifierChain: [{ name: 'foo' }], table: 'testTableA' },
            suggestKeywords: ['*'],
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 27, last_column: 37}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT b, foo.aaaaa|bbbb FROM testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT b, foo.aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { identifierChain: [{ name: 'foo' }], table: 'testTableA' },
            suggestKeywords: ['*'],
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9}, identifierChain: [{ name: 'b' }], table: 'testTableA'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 30, last_column: 40}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT foo, aaaaa|bbbb FROM testTableA"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT foo, aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTableA' },
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11}, identifierChain: [{ name: 'foo' }], table: 'testTableA'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 28, last_column: 38}, table: 'testTableA'}
            ]
          }
        });
      });

      it('should suggest locations for "SELECT testTableB.a, cos(1), tta.abcdefg|hijk, tta.bla, cos(1) FROM testTableA tta, testTableB;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTableB.a, cos(1), tta.abcdefg',
          afterCursor: 'hijk, tta.bla, cos(1) FROM testTableA tta, testTableB;',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTableA' },
            suggestKeywords: ['*'],
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 20}, identifierChain: [{ name: 'a'}], table: 'testTableB'},
              { type: 'function', location: { first_line: 1, last_line: 1, first_column: 22, last_column: 24}, function: 'cos'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 47, last_column: 54}, identifierChain: [{ name: 'bla'}], table: 'testTableA'},
              { type: 'function', location: { first_line: 1, last_line: 1, first_column: 56, last_column: 58}, function: 'cos'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 68, last_column: 78}, table: 'testTableA'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 84, last_column: 94}, table: 'testTableB'}
            ]
          }
        });
      });
    });

    describe('Complete Statements', function () {
      it('should handle "SELECT tta.* FROM testTableA tta, testTableB; |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tta.* FROM testTableA tta, testTableB; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false,
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 19, last_column: 29}, table: 'testTableA'},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 35, last_column: 45}, table: 'testTableB'}
            ]
          }
        });
      });

      it('should handle "SELECT COUNT(*) FROM testTable; |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(*) FROM testTable;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false,
            locations: [
              {type: 'function', location:{ first_line: 1, last_line: 1, first_column: 8, last_column: 12}, function: 'count'},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 22, last_column: 31}, table: 'testTable'}
            ]
          }
        });
      });

      it('should handle "SELECT tmp.bc, ROUND(tmp.r, 2) AS r FROM ( SELECT tstDb1.b1.cat AS bc, SUM(tstDb1.b1.price * tran.qua) AS r FROM tstDb1.b1 JOIN [SHUFFLE] tran ON ( tran.b_id = tstDb1.b1.id AND YEAR(tran.tran_d) BETWEEN 2008 AND 2010) GROUP BY tstDb1.b1.cat) tmp ORDER BY r DESC LIMIT 60; |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT tmp.bc, ROUND(tmp.r, 2) AS r FROM ( SELECT tstDb1.b1.cat AS bc, SUM(tstDb1.b1.price * tran.qua) AS r FROM tstDb1.b1 JOIN [SHUFFLE] tran ON ( tran.b_id = tstDb1.b1.id AND YEAR(tran.tran_d) BETWEEN 2008 AND 2010) GROUP BY tstDb1.b1.cat) tmp ORDER BY r DESC LIMIT 60;',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false,
            locations: [
              { type: 'function', location: { first_line: 1, last_line: 1, first_column: 16, last_column: 20 }, function: 'round' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 51, last_column: 64 }, identifierChain: [{ name: 'cat'}], database: 'tstDb1', table: 'b1' },
              { type: 'function', location: { first_line: 1, last_line: 1, first_column: 72, last_column: 74 }, function: 'sum' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 76, last_column: 91 }, identifierChain: [{ name: 'price' }],database: 'tstDb1', table: 'b1' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 94, last_column: 102 }, identifierChain: [{ name: 'qua' }], table: 'tran' },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 121, last_column: 123 }, database: 'tstDb1', table: 'b1' },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 139, last_column: 143 }, table: 'tran' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 149, last_column: 158 }, identifierChain: [{ name: 'b_id'}], table: 'tran' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 161, last_column: 173 }, identifierChain: [{ name: 'id'}], database: 'tstDb1', table: 'b1' },
              { type: 'function', location: { first_line: 1, last_line: 1, first_column: 178, last_column: 181 }, function: 'year' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 183, last_column: 194 }, identifierChain: [{ name: 'tran_d' }], table: 'tran' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 234, last_column: 235 }, identifierChain: [{ name: 'cat' }], database: 'tstDb1', table: 'b1' }
            ]
          }
        });
      });

      it('should handle "SELECT * FROM testTable t1 ORDER BY t1.a ASC, t1.b, t1.c DESC, t1.d;\\nSELECT t1.bla FROM testTable2 t1;\nSELECT * FROM testTable3 t3 WHERE |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable t1 ORDER BY t1.a ASC, t1.b, t1.c DESC, t1.d;\nSELECT t1.bla FROM testTable2 t1;\nSELECT * FROM testTable3 t3, testTable4 t4 WHERE ',
          afterCursor: '',
          containsKeywords: ['EXISTS'],
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 't3.', type: 'alias'}, { name: 't4.', type: 'alias'}],
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 24}, table: 'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 39, last_column: 40},identifierChain: [{ name: 'a'}], table:'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 49, last_column: 50},identifierChain: [{ name: 'b'}], table:'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 55, last_column: 56},identifierChain: [{ name: 'c'}], table:'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 66, last_column: 67},identifierChain: [{ name: 'd'}], table:'testTable'},
              { type: 'column', location: { first_line: 2, last_line: 2, first_column: 8, last_column: 14},identifierChain: [{ name: 'bla'}], table:'testTable2'},
              { type: 'table', location: { first_line: 2, last_line: 2, first_column: 20, last_column: 30}, table: 'testTable2'},
              { type: 'table', location: { first_line: 3, last_line: 3, first_column: 15, last_column: 25}, table: 'testTable3'},
              { type: 'table', location: { first_line: 3, last_line: 3, first_column: 30, last_column: 40}, table: 'testTable4'}
            ]
          }
        });
      });

      it('should handle "SELECT * FROM testTable ORDER BY a ASC, b, c DESC, d; |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable ORDER BY a ASC, b, c DESC, d; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 24}, table: 'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 34, last_column: 35},identifierChain: [{ name: 'a'}], table:'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 42},identifierChain: [{ name: 'b'}], table:'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 44, last_column: 45},identifierChain: [{ name: 'c'}], table:'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 52, last_column: 53},identifierChain: [{ name: 'd'}], table:'testTable'}
            ]
          }
        });
      });

      it('should handle "SELECT * FROM testTable1 JOIN db1.table2; |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.table2; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false,
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 25 }, table: 'testTable1' },
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 35, last_column: 41 }, database: 'db1', table: 'table2'}
            ]
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
            lowerCase: false,
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 14 }, identifierChain: [{ name: 'foo' }], table: 'table1' },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 20, last_column: 26 }, table: 'table1'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 47 }, table: 'table2'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 64, last_column: 70 }, table: 'table3'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 76, last_column: 82 }, table: 'table4'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 90, last_column: 95 }, identifierChain: [{ name: 'c1'}], table: 'table1'}
            ]
          }
        });
      });

      it('should handle "SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false,
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 }, table: 'foo'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 }, identifierChain:[{ name: 'bar'}], table: 'foo'},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 47, last_column: 50 }, table: 'bla'}
            ]
          }
        });
      });

    it('should handle "SELECT CASE cos(boo.a) > baa.boo \\n' +
        '\\tWHEN baa.b THEN true \\n' +
        '\\tWHEN boo.c THEN false \\n' +
        '\\tWHEN baa.blue THEN boo.d \\n' +
        '\\tELSE baa.e END \\n' +
        '\\t FROM db1.foo boo, bar baa WHERE baa.bla IN (SELECT ble FROM bla);|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE cos(boo.a) > baa.boo \n\tWHEN baa.b THEN true \n\tWHEN boo.c THEN false \n\tWHEN baa.blue THEN boo.d \n\tELSE baa.e END \n\t FROM db1.foo boo, bar baa WHERE baa.bla IN (SELECT ble FROM bla);',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false,
            locations: [
              {type: 'function', location: { first_line: 1, last_line: 1, first_column: 13, last_column: 15 }, function: 'cos'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 17, last_column: 22 }, identifierChain: [{ name: 'a'}], database: 'db1', table: 'foo'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 33 }, identifierChain: [{ name: 'boo'}], table: 'bar'},
              {type: 'column', location: { first_line: 2, last_line: 2, first_column: 7, last_column: 12 }, identifierChain: [{ name: 'b'}], table: 'bar'},
              {type: 'column', location: { first_line: 3, last_line: 3, first_column: 7, last_column: 12 }, identifierChain: [{ name: 'c'}], database: 'db1', table: 'foo'},
              {type: 'column', location: { first_line: 4, last_line: 4, first_column: 7, last_column: 15 }, identifierChain: [{ name: 'blue'}], table: 'bar'},
              {type: 'column', location: { first_line: 4, last_line: 4, first_column: 21, last_column: 26 }, identifierChain: [{ name: 'd'}], database: 'db1', table: 'foo'},
              {type: 'column', location: { first_line: 5, last_line: 5, first_column: 7, last_column: 12 }, identifierChain: [{ name: 'e'}], table: 'bar'},
              {type: 'table', location: { first_line: 6, last_line: 6, first_column: 12, last_column: 15 }, database: 'db1', table: 'foo'},
              {type: 'table', location: { first_line: 6, last_line: 6, first_column: 21, last_column: 24 }, table: 'bar'},
              {type: 'column', location: { first_line: 6, last_line: 6, first_column: 35, last_column: 42 }, identifierChain: [{ name: 'bla'}], table: 'bar'},
              {type: 'column', location: { first_line: 6, last_line: 6, first_column: 54, last_column: 57 }, identifierChain: [{ name: 'ble'}], table: 'bla'},
              {type: 'table', location: { first_line: 6, last_line: 6, first_column: 63, last_column: 66 }, table: 'bla'}
            ]
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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
            suggestFunctions: {},
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
            suggestFunctions: {},
            suggestColumns: { table: 'tbl' },
            locations: [
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 }, identifierChain:[{ name: 'a'}], table: 'tbl'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 21, last_column: 22 }, identifierChain:[{ name: 'b'}], table: 'tbl'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 24, last_column: 25 }, identifierChain:[{ name: 'c'}], table: 'tbl'},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 31, last_column: 34 }, table: 'tbl'}
            ]
          }
        });
      });



      it('should suggest tables for "SELECT | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM tableA;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testWHERE"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testWHERE',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { table: 'testWHERE' }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testON"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testON',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { table: 'testON' }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM transactions"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM transactions',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { table: 'transactions' }
          }
        });
      });

      it('should suggest aliases for "SELECT | FROM testTableA tta, testTableB"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, testTableB',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "select | from database_two.testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from database_two.testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { table: 'test table', database: 'database one' },
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 29, last_column: 41}, database: 'database one', table: 'test table' }
            ]
          }
        });
      });

      it('should suggest aliases for "SELECT | FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.arr) ttaSum, testTableB ttb"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.arr) ttaSum, testTableB ttb',
          ignoreErrors: true,
          hasLocations: true,
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'ttaSum.', type: 'sub-query' }, { name: 'ttb.', type: 'alias' }],
            subQueries: [{
              alias: 'ttaSum',
              columns: [{ alias: 'total', type: 'DOUBLE' }]
            }]
          }
        });
      });

      it('should suggest columns for "SELECT a, | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, ',
          afterCursor: ' FROM tableA;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest columns for "SELECT a,| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a,',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT *, | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT *, ',
          afterCursor: ' FROM tableA;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: {table: 'tableA'}
          }
        });
      });

      it('should suggest keywords for "SELECT a | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a ',
          afterCursor: ' FROM tableA;',
          containsKeywords: ['AS', '='],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'a' }], table: 'tableA' }
          }
        });
      });

      it('should suggest keywords for "SELECT a |, FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a ',
          afterCursor: ', FROM tableA;',
          containsKeywords: ['AS', '='],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'a' }], table: 'tableA' }
          }
        });
      });

      it('should suggest keywords for "SELECT a, b | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b ',
          afterCursor: ' FROM tableA;',
          containsKeywords: ['AS', '='],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'b' }], table: 'tableA' }
          }
        });
      });

      it('should suggest keywords for "SELECT a |, b, c AS foo, d FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a ',
          afterCursor: ', b, c AS foo, d FROM tableA;',
          containsKeywords: ['AS', '='],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'a' }], table: 'tableA' }
          }
        });
      });

      it('should suggest columns for "SELECT | a, cast(b as int), c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' a, cast(b as int), c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' },
            locations: [
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9} , identifierChain: [{ name: 'a'}], table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 11, last_column: 12 }, identifierChain: [{ name: 'b'}], table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 }, identifierChain: [{ name: 'c'}], table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 }, identifierChain: [{ name: 'd'}], table: 'testTable'},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 34 }, table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 42 }, identifierChain: [{ name: 'a'}], table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 54, last_column: 55 }, identifierChain: [{ name: 'b'}], table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 72, last_column: 73 }, identifierChain: [{ name: 'c'}], table: 'testTable'}
            ]
          }
        });
      });
    });

    describe('Variable References', function () {
      it('should suggest tables for "SELECT | FROM ${some_variable};"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM ${some_variable};',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: {table: '${some_variable}'}
          }
        });
      });

      it('should suggest tables for "SELECT * FROM testTable WHERE ${some_variable} |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ${some_variable} ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['<', 'BETWEEN'],
          containsColRefKeywords: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain:[{ name: '${some_variable}' }], table: 'testTable'}
          }
        });
      });

      it('should suggest tables for "SELECT * FROM testTable WHERE ${some_variable} + 1 = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ${some_variable} + 1 = ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER']},
            suggestColumns: { types: ['NUMBER'], table: 'testTable'}
          }
        });
      });
    });

    describe('Window and analytic functions', function () {
      it('should handle "SELECT row_number() OVER (PARTITION BY a) FROM testTable;|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a) FROM testTable;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT COUNT(DISTINCT a) OVER (PARTITION by c) FROM testTable;|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(DISTINCT a) OVER (PARTITION by c) FROM testTable;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest analytical functions for "SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: '',
          containsKeywords: ['*'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions:true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestTables: { prependQuestionMark: true, prependFrom: true },
            suggestDatabases: { prependQuestionMark: true, prependFrom: true, appendDot: true}
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() ',
          afterCursor: '',
          containsKeywords: ['OVER'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['OVER'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() |, b, c FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() ',
          afterCursor: ', b, c FROM testTable',
          containsKeywords: ['OVER'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT count(DISTINCT a) |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT count(DISTINCT a) ',
          afterCursor: '',
          containsKeywords: ['OVER'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { prependFrom: true} ,
            suggestDatabases: { prependFrom: true, appendDot: true }
          }
        });
      });

      it('should suggest keywords for "SELECT count(DISTINCT a) | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT count(DISTINCT a) ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['OVER'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT count(DISTINCT a) |, b, c FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT count(DISTINCT a) ',
          afterCursor: ', b, c FROM testTable',
          containsKeywords: ['OVER'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER ( ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['PARTITION BY'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['BY'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a, b ORDER | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a, b ORDER ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['BY'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT row_number() OVER (ORDER BY | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (ORDER BY ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT row_number() OVER (ORDER BY |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (ORDER BY ',
          afterCursor: ') FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT row_number() OVER (ORDER BY foo |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (ORDER BY a ',
          afterCursor: ') FROM testTable',
          hasLocations: true,
          containsKeywords: ['ASC', 'DESC'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT row_number() OVER (PARTITION BY | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT row_number() OVER (PARTITION BY a, | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a, ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ',
          afterCursor: '',
          containsKeywords: ['ASC', 'ROWS BETWEEN', 'RANGE BETWEEN'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['BETWEEN']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CURRENT ROW', 'UNBOUNDED PRECEDING']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PRECEDING']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PRECEDING']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROW']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AND']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AND']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AND']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CURRENT ROW', 'UNBOUNDED FOLLOWING']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CURRENT ROW', 'UNBOUNDED FOLLOWING']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CURRENT ROW', 'UNBOUNDED FOLLOWING']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND CURRENT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND CURRENT ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROW']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FOLLOWING']
          }
        });
      });

      it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND 1 |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND 1 ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FOLLOWING']
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords for "SELECT count(id) OVER w FROM customers |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT row_number() OVER w FROM customers ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            containsKeywords: ['WINDOW'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT count(id) OVER w FROM customers WINDOW w |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT row_number() OVER w FROM customers WINDOW w ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            containsKeywords: ['AS'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT count(id) OVER w FROM customers WINDOW w AS (|"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT row_number() OVER w FROM customers WINDOW w AS (',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            containsKeywords: ['ORDER BY', 'PARTITION BY'],
            expectedResult: {
              lowerCase: false
            }
          });
        });
      });
    });

    describe('Functions', function () {
      it('should suggest tables for "SELECT COUNT(*) |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(*) ',
          afterCursor: '',
          containsKeywords: ['AS', '+'],
          hasLocations: true,
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

      it('should suggest keywords for "SELECT COUNT(foo |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo ',
          afterCursor: '',
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT COUNT(foo, bl|, bla) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo, bl',
          afterCursor: ',bla) FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest keywords for "SELECT COUNT(foo, bla |, bar)"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo ',
          afterCursor: ', bar)',
          containsKeywords: ['AND', '='],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns and values for "SELECT COUNT(foo, bl = |,bla) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo, bl = ',
          afterCursor: ',bla) FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { types: ['COLREF'], table: 'bar' },
            suggestValues: true,
            colRef: { identifierChain: [ {name: 'bl' }], table: 'bar' }
          }
        });
      });

      it('should suggest functions for "SELECT CAST(|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {}
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(bla| FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla',
          afterCursor: ' FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS INT FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS INT FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS STRING) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS STRING) FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(bla| AS STRING) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla',
          afterCursor: ' AS STRING) FROM bar;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'bar' }
          }
        });
      });

      it('should suggest keywords for "SELECT CAST(bla |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla ',
          afterCursor: '',
          containsKeywords: ['AS', 'AND'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT CAST(bla | FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla ',
          afterCursor: ' FROM bar;',
          containsKeywords: ['AS', '='],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'bla'}], table: 'bar'}
          }
        });
      });

      it('should suggest keywords for "select cast(bla as |"', function() {
        assertAutoComplete({
          beforeCursor: 'select cast(bla as ',
          afterCursor: '',
          containsKeywords: ['INT', 'STRING'],
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla FROM | FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla FROM ',
          afterCursor: ' FROM bar;',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['TIMESTAMP'] },
            suggestColumns: { types: ['TIMESTAMP'], table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla ,|  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla ,',
          afterCursor: ' FROM bar;',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { types: ['STRING'], table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT a, extract(bla FROM |)  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, extract(bla FROM ',
          afterCursor: ') FROM bar;',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['TIMESTAMP'] },
            suggestColumns: { types: ['TIMESTAMP'], table: 'bar' }
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla ,|)  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla ,',
          afterCursor: ') FROM bar;',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { types: ['STRING'], table: 'bar' }
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
          { name: 'GROUP_CONCAT', dialect: 'impala', suggestKeywords: ['ALL'], types: ['STRING'] },
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
              hasLocations: true,
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
              suggestFunctions: { types: aggregateFunction.types || ['T'] },
              suggestColumns: {
                types: aggregateFunction.types || ['T'],
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
              hasLocations: true,
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['T'] },
              suggestColumns: {
                types: ['T'],
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['T'] },
              suggestColumns: {
                types: ['T'],
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['T'] },
              suggestColumns: {
                types: ['T'],
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: {
              types: ['NUMBER'],
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT CASE | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          containsKeywords: ['WHEN', 'AND', '<>'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b OR | THEN boo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b OR ',
          afterCursor: ' THEN boo FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: {
              types: ['COLREF'],
              table: 'testTable'
            },
            suggestValues: true,
            colRef: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a =| WHEN c THEN d ELSE e END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a =',
          afterCursor: ' WHEN c THEN d ELSE e END FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: {
              types: ['COLREF'],
              table: 'testTable'
            },
            suggestValues: true,
            colRef: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['END', '<>'],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d=| ELSE FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d=',
          afterCursor: ' ELSE FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: {
              types: ['COLREF'],
              table: 'testTable'
            },
            suggestValues: true,
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a = c WHEN c THEN d=1 | bla=foo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d=1 ',
          afterCursor: ' bla=foo FROM testTable',
          containsKeywords: ['AND', 'WHEN', 'ELSE', 'END', '<'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a = c WHEN c THEN d=1 | bla=foo END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d=1 ',
          afterCursor: ' bla=foo FROM testTable',
          containsKeywords: ['AND', 'WHEN', 'ELSE', '>'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          containsKeywords: ['END', '='],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'e' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN THEN boo OR | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN THEN boo OR ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['WHEN'],
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['THEN'],
            suggestFunctions: {},
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
          containsKeywords: ['WHEN', '<'],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'c' }], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT CASE a WHEN b THEN c | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN b THEN c ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['WHEN', '>'],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'c' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN | THEN FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' THEN FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: {
              types: ['COLREF'],
              table: 'testTable'
            },
            suggestValues: true,
            colRef: { identifierChain :[{ name :'a'}], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN ab| THEN bla ELSE foo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ab',
          afterCursor: ' THEN bla ELSE foo FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: {
              types: ['COLREF'],
              table: 'testTable'
            },
            suggestValues: true,
            colRef: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b ',
          afterCursor: ' FROM testTable',
          containsKeywords: ['AND', 'THEN', '<'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c | d FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c ',
          afterCursor: ' d FROM testTable',
          containsKeywords: ['THEN', '>'],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'c' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE', 'WINDOW']
          }
        });
      });

      it('should suggest keywords for "SELECT bar FROM db.foo f |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM db.foo f ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE', 'WINDOW']
          }
        });
      });

      it('should suggest keywords for "SELECT bar FROM foo JOIN baz |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo JOIN baz ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE', 'WINDOW']
          }
        });
      });

      it('should suggest keywords for "SELECT bar FROM foo LATERAL |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo LATERAL ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest columns for "SELECT testMap[].| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap[].',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', keySet: true }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest values for "SELECT testMap[|] FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap[',
          afterCursor: '] FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { }, // TODO: types: ['COLREF_KEY']
            suggestColumns : {
              table: 'testTable'
            },
            suggestKeyValues: {
              identifierChain: [{ name: 'testMap' }],
              table: 'testTable'
            }
          }
        });
      });

      it('should suggest columns for "SELECT testMap[\'anyKey\'].| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap[\'anyKey\'].',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', keySet: true }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest columns for "SELECT testMap[substr(\'bla\', 1)].| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap[substr(\'bla\', 1)].',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', keySet: true }]
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', keySet: true }, { name: 'fieldC' }]
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testArray', keySet: true }, { name: 'fieldC' }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest columns for "SELECT testFoo[1].testBar[\"key\"].| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testFoo[1].testBar[\"key\"].',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testFoo', keySet: true }, { name: 'testBar', keySet: true }]
            },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE testMap[].|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE testMap[].',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns : {
              table: 'testTable',
              identifierChain: [{ name: 'testMap', keySet: true }]
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
              suggestAnalyticFunctions: true,
              suggestFunctions: {},
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testItem', type: 'alias' }],
              locations: [
                {type: 'table', location: { first_line: 1, last_line: 1, first_column: 14, last_column: 23 }, table: 'testTable' },
                {type: 'function', location: { first_line: 1, last_line: 1, first_column: 37, last_column: 43 }, function: 'explode'},
                {type: 'column', location: { first_line: 1, last_line: 1, first_column: 45, last_column: 54 }, identifierChain: [{ name: 'testArray' }], table: 'testTable'}
              ]
            }
          });
        });

        it('should suggest columns for "SELECT | FROM testTable LATERAL VIEW explode("', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestAggregateFunctions: true,
              suggestAnalyticFunctions: true,
              suggestColumns: {
                table: 'testTable'
              },
              suggestKeywords: ['*','ALL','DISTINCT']
            }
          });
        });

        it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW explode(|"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['ARRAY', 'MAP' ] },
              suggestColumns: {
                types: ['ARRAY', 'MAP' ],
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestColumns: {
                types: ['ARRAY', 'MAP' ],
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['ARRAY' ] },
              suggestColumns: {
                types: ['ARRAY' ],
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestColumns: {
                table: 'testTable'
              },
              suggestAggregateFunctions: true,
              suggestAnalyticFunctions: true,
              suggestFunctions: {},
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testKey', type: 'alias' }, { name: 'testValue', type: 'alias' }]
            }
          });
        });

        it('should suggest columns for "SELECT testItem.| FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT testItem.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            dialect: 'hive',
            hasLocations: true,
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
            hasLocations: true,
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
              },
              locations: [
                { type: 'column', location: { first_line: 2, last_line: 2, first_column: 2, last_column: 11 }, identifierChain: [{ name: 'testArrayA'}, {name: 'item'}], table: 'testTable2'},
                { type: 'table', location: { first_line: 5, last_line: 5, first_column: 3, last_column: 13 }, table: 'testTable2'},
                { type: 'function', location: { first_line: 6, last_line: 6, first_column: 16, last_column: 22 }, function: 'explode'},
                { type: 'column', location: { first_line: 6, last_line: 6, first_column: 24, last_column: 38 }, identifierChain: [{ name: 'testArrayA'}], table: 'testTable2'},
                { type: 'function', location: { first_line: 7, last_line: 7, first_column: 16, last_column: 22 }, function: 'explode'},
                { type: 'column', location: { first_line: 7, last_line: 7, first_column: 24, last_column: 38 }, identifierChain: [{ name: 'testArrayB'}] ,table: 'testTable2'}
              ]
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestAggregateFunctions: true,
              suggestAnalyticFunctions: true,
              suggestFunctions: {},
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
            suggestKeywords: ['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN', 'WHERE'],
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 25}, table: 'testTableA'},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 31, last_column: 41}, table: 'testTableB'}
            ]
          }
        });
      });

      it('should suggest columns for "SELECT testMap[\"anyKey\"].| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testMap["anyKey"].',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'testTable',
              identifierChain: [{ name: 'testMap',  keySet: true }]
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
            },
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 17, last_column :26}, table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 32, last_column :39}, identifierChain: [{ name: 'testMap'}], table: 'testTable'}
            ]
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
            },
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 18, last_column :27}, table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 33, last_column :40}, identifierChain: [{ name: 'testMap'}], table: 'testTable'}
            ]

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
            },
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'testArray'}], table: 'testTable'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 27 }, table: 'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 33, last_column: 42 }, identifierChain: [{ name: 'testArray'}], table: 'testTable'}
            ]
          }
        });
      });

      it('should suggest columns for "SELECT t.*  FROM testTable t, t.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t.*  FROM testTable t, t.',
          afterCursor: '',
          dialect: 'impala',
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestIdentifiers : [{ name: 't.', type: 'alias' }, { name: 'tm.', type: 'alias' }],
            colRef: { identifierChain: [{ name: 'testMap' }, { name: 'key' }],  table: 'testTable' }
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
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestIdentifiers : [{ name: 't.', type: 'alias' }, { name: 'm.', type: 'alias' }],
            colRef: { identifierChain: [{ name: 'testMap' }, { name: 'field' }], table: 'testTable' },
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 24}, table: 'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 30, last_column: 37}, identifierChain: [{ name: 'testMap'}], table: 'testTable'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 46, last_column: 53}, identifierChain: [{ name: 'testMap'},{ name: 'field'}], table: 'testTable'}
            ]
          }
        });
      });
    });

    describe('Hive and Impala Struct Completion', function() {
      it('should suggest columns for SELECT columnA.| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT columnA.',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { types: ['T'], table: 'tbl2' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE cos(1) = atbl2.bla.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE cos(1) = atbl2.bla.',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { identifierChain: [{ name: 'bla' }], types: ['DOUBLE'], table: 'tbl2' }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE id = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE id =',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'id' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE -|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE -',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'] , table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT -| FROM testTable WHERE id = 1;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT -',
          afterCursor: ' FROM testTable WHERE id = 1;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT 1 < | FROM testTable WHERE id = 1;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT 1 < ',
          afterCursor: ' FROM testTable WHERE id = 1;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "select foo from tbl where | % 2 = 0"', function() {
        assertAutoComplete({
          beforeCursor: 'select foo from tbl where ',
          afterCursor: ' % 2 = 0',
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'tbl' }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE -id = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE -id = ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestValues: true,
            suggestColumns: { types: ['NUMBER'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'id' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE \'foo\' = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE \'foo\' = ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { types: ['STRING'], table: 'testTable' }
          }
        });
      });

      it('should suggest typed values for "SELECT * FROM testTable WHERE \'foo\' = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE \'foo\' = ',
          afterCursor: '',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { types: ['STRING'], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT cast(\'1\' AS |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(\'1\' AS ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['BIGINT', 'DATE'],
          doesNotContainKeywords: ['REAL'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT cast(\'1\' AS |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(\'1\' AS ',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['BIGINT', 'REAL'],
          doesNotContainKeywords: ['DATE'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT cast(\'1\' AS | b, c bla, d"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(\'1\' AS ',
          afterCursor: ' b, c bla, d',
          dialect: 'impala',
          containsKeywords: ['BIGINT', 'REAL'],
          doesNotContainKeywords: ['DATE'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT cos(| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cos(',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { types: ['DECIMAL', 'DOUBLE'], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT cos(| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cos(',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DOUBLE'] },
            suggestColumns: { types: ['DOUBLE'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT ceiling(| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ceiling(',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DOUBLE'] },
            suggestColumns: { types: ['DOUBLE'], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT ceiling(| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ceiling(',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { types: ['DECIMAL', 'DOUBLE'], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT a, ceiling(| b, c AS bla, d FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ceiling(',
          afterCursor: ' b, c AS bla, d FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { types: ['DECIMAL', 'DOUBLE'], table: 'testTable' }
          }
        });
      });

      it('should not suggest columns for "SELECT cos(1, | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cos(1, ',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should not suggest columns for "SELECT cos(1, | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cos(1, ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT greatest(1, 2, a, 4, | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT greatest(1, 2, a, 4, ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['T'] },
            suggestColumns: { types: ['T'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT greatest(1, |, a, 4) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT greatest(1, ',
          afterCursor: ', a, 4) FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['T'] },
            suggestColumns: { types: ['T'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT log(a, |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT log(a, ',
          afterCursor: ') FROM testTable',
          hasLocations: true,
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { types: ['DECIMAL', 'DOUBLE'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT log(a, |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT log(a, ',
          afterCursor: ') FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DOUBLE'] },
            suggestColumns: { types: ['DOUBLE'], table: 'testTable' }
          }
        });
      });

      it('should not suggest columns for "SELECT log(a, b, | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT log(a, b, ',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should not suggest columns for "SELECT log(a, b, | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT log(a, b, ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest typed columns for "SELECT substr(\'foo\', |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT substr(\'foo\', ',
          afterCursor: ') FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'INT' ] },
            suggestColumns: { types: [ 'INT' ], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT substr(|, 1, 2) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT substr(',
          afterCursor: ', 1, 2) FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'STRING' ] },
            suggestColumns: { types: [ 'STRING' ], table: 'testTable' }
          }
        });
      });

      // Fails because valueExpressionList_EDIT doesn't support empty value expression around ','
      xit('should suggest typed columns for "SELECT substr(,,| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT substr(,,',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'INT' ] },
            suggestColumns: { types: [ 'INT' ], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT cast(a AS BIGINT) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(a AS BIGINT) = ',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'BIGINT' ] },
            suggestColumns: { types: [ 'BIGINT' ], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT cast(a AS BIGINT) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(a AS BIGINT) = ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'BIGINT' ] },
            suggestColumns: { types: [ 'BIGINT' ], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT cast(a AS BIGINT) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(a AS BIGINT) = ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'BIGINT' ] },
            suggestColumns: { types: [ 'BIGINT' ], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT years_add(a , 10) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT years_add(a , 10) = ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'TIMESTAMP' ] },
            suggestColumns: { types: [ 'TIMESTAMP' ], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT | > cast(years_add(a , 10) AS INT) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' > cast(years_add(a , 10) AS INT) FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: [ 'INT' ] },
            suggestColumns: { types: [ 'INT' ], table: 'testTable' }
          }
        });
      });

      it('should suggest typed columns for "SELECT partial.parital| > cast(years_add(a , 10) AS INT) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT partial.partial',
          afterCursor: ' > cast(years_add(a , 10) AS INT) FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { identifierChain: [{ name: 'partial' }], types: [ 'INT' ], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT | > id FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' > id FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            suggestValues: true,
            colRef: { identifierChain: [{ name: 'id' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT * FROM testTable WHERE | = id"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: ' = id',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'id' }], table: 'testTable'}
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d < |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d < ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <= |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <= ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <=> |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <=> ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <> |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <> ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d >= |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d > |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d > ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d != |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d != ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'd' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + 1 != |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + 1 != ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE bla| + 1 != 3"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE bla',
          afterCursor: ' + 1 != 3',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d - |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d - ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d * |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d * ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d / |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d / ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d % |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d % ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d | |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d | ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d & |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d & ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d ^ |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ^ ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE ~|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE ~',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE -|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE -',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { types: ['NUMBER'], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE | RLIKE \'bla bla\'"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ',
          afterCursor: ' RLIKE \'bla bla\'',
          hasLocations: true,
          containsKeywords: ['<', 'IN'],
          containsColRefKeywords: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'd'}], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT bar FROM foo WHERE id = 1 |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
          afterCursor: '',
          dialect: 'generic',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT']
          }
        });
      });

      // Fails because "NOT" is missing
      xit('should suggest keywords for "SELECT * FROM foo WHERE id | LIKE \'bla bla\'"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id ',
          afterCursor: ' LIKE \'bla bla\'',
          hasLocations: true,
          containsKeywords: ['<', 'IN', 'NOT'],
          containsColRefKeywords: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'id' }], table: 'foo' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo WHERE id LIKE |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id LIKE ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { types: ['STRING'], table: 'foo' }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE id LIKE \'\' GROUP |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id LIKE \'\' GROUP ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['BY']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE id LIKE (\'bla bla\') |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE id LIKE (\'bla bla\') ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['AND'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest identifiers for "SELECT * FROM foo bla, bar WHERE id IS NULL AND |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bla, bar WHERE id IS NULL AND ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }, { name: 'bar.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL && |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL && ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'foo' },
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL OR | AND 1 + 1 > 1"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL OR ',
          afterCursor: ' AND 1 + 1 > 1',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'foo' },
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL || |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL || ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'foo' },
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE NOT |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE NOT ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'foo' },
            suggestKeywords: ['EXISTS'],
            suggestIdentifiers: [{ name: 'bar.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE ! |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE ! ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['BOOLEAN'] },
            suggestColumns: { types: ['BOOLEAN'], table: 'foo' },
            suggestIdentifiers: [{ name: 'bar.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE !|"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE !',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['BOOLEAN'] },
            suggestColumns: { types: ['BOOLEAN'], table: 'foo' },
            suggestIdentifiers: [{ name: 'bar.', type: 'alias' }]
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords for "SELECT bar FROM foo WHERE id = 1 |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['<', '<=', '<=>', '<>', '=', '>', '>=', 'AND', 'BETWEEN', 'GROUP BY', 'IN', 'IS NOT NULL', 'IS NULL', 'LIMIT', 'NOT BETWEEN', 'NOT IN', 'OR', 'ORDER BY', 'WINDOW']
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS', 'NOT EXISTS']
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE a|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS', 'NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE NOT ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE foo = \'bar\' |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE foo = \'bar\' ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['AND', '<'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT a, b, c, d, e FROM tableOne WHERE c >= 9998 an|"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c, d, e FROM tableOne WHERE c >= 9998 an',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['AND', '='],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE foo = \'bar\' AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE foo = \'bar\' AND ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, \\nc,\\nd, |\\ng,\\nf\\nFROM testTable WHERE a > 1 AND b = \'b\' ORDER BY c;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, \nc,\nd, ',
          afterCursor: '\ng,\nf\nFROM testTable WHERE a > 1 AND b = \'b\' ORDER BY c;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest columns for "SELECT a, b, | c FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a,b, ',
          afterCursor: ' c FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest columns for "SELECT | a, b, c FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' a, b, c FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestColumns: { table: 'testTable' },
            suggestKeywords: ['*', 'ALL', 'DISTINCT']
          }
        });
      });

      it('should suggest keywords for "SELECT a |, b, c FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a ',
          afterCursor: ', b, c FROM testTable',
          containsKeywords: ['AS', '>'],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE | = \'bar\' AND "', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: ' = \'bar\' AND ',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { types: ['STRING'], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE a |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a ',
          afterCursor: '',
          containsKeywords: ['BETWEEN', 'NOT BETWEEN'],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'a'}], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE a NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a NOT ',
          afterCursor: '',
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'testTable' },
            colRef: { identifierChain: [{ name: 'a' }], table: 'testTable' }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable WHERE a OR NOT EXISTS (|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a OR NOT EXISTS (',
          afterCursor: '',
          hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestAnalyticFunctions: true,
              suggestColumns: { table: 'testTable' }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY ',
            afterCursor: '',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestAnalyticFunctions: true,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ',
            afterCursor: '',
            dialect: 'generic',
            hasLocations: true,
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestAnalyticFunctions: true,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo ASC, |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ASC, ',
            afterCursor: '',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestAnalyticFunctions: true,
              suggestColumns: { database: 'database_two', table: 'testTable' }
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
            afterCursor: '',
            dialect: 'generic',
            hasLocations: true,
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
            hasLocations: true,
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
              hasLocations: true,
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
              hasLocations: true,
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
              hasLocations: true,
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
              hasLocations: true,
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
                hasLocations: true,
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
                hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable1' }
          }
        });
      });

      it('should suggest columns for "SELECT b.| FROM dbOne.foo f JOIN dbOne.bar b"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT b.',
          afterCursor: ' FROM dbOne.foo f JOIN dbOne.bar b',
          hasLocations: true,
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'bar', database: 'dbOne' }
          }
        });
      });

      it('should suggest columns for "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { table: 'testTableA' }
          }
        });
        assertAutoComplete({
          beforeCursor: 'SELECT ttb.',
          afterCursor: ' FROM testTableA tta, testTableB ttb',
          hasLocations: true,
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
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable1 INNER |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 INNER ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'JOIN' ]
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable1 FULL |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 FULL ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'JOIN', 'OUTER JOIN' ]
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable1 FULL OUTER |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 FULL OUTER ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'JOIN' ]
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable1 LEFT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 LEFT ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'JOIN', 'OUTER JOIN' ]
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable1 LEFT OUTER |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 LEFT OUTER ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'JOIN' ]
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable1 RIGHT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 RIGHT ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'JOIN', 'OUTER JOIN' ]
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable1 RIGHT OUTER |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 RIGHT OUTER ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'JOIN' ]
          }
        });
      });

      it('should suggest tables for "SELECT * FROM testTable1 JOIN db1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.',
          afterCursor: '',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
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
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }],
            suggestFunctions: {},
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 36}, table: 'testTable1'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 42, last_column: 52}, table: 'testTable2'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 62, last_column: 84}, identifierChain: [{ name: 'testColumn1'}], table: 'testTable1'},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 87, last_column: 109}, identifierChain: [{ name: 'testColumn3'}], table: 'testTable2'}
            ]
          }
        });
      });

    it('should suggest columns for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'db.testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest identifiers for "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestFunctions: { types: ['COLREF' ]},
            suggestValues: true,
            colRef: { identifierChain: [{ name: 'testColumn1'}], table: 'testTable1' },
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.|"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.',
          afterCursor: '',
          ignoreErrors: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            colRef: { identifierChain: [{ name: 'testColumn1'}], table: 'testTable1' },
            suggestColumns: { types: ['COLREF'], table: 'testTable2'}
          }
        });
      });

      it('should suggest columns for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.',
          afterCursor: '',
          ignoreErrors: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable1'}
          }
        });
      });

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 ',
          afterCursor: ' JOIN',
          dialect: 'generic',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']
          }
        });
      });

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN table2 t2 ON t1.bla = t2.bla"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 ',
          afterCursor: ' JOIN table2 t2 ON t1.bla = t2.bla',
          dialect: 'generic',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']
          }
        });
      });

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 JOIN table2 t2 | JOIN table3"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 ',
          afterCursor: ' JOIN table3',
          dialect: 'generic',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'ON', 'RIGHT', 'RIGHT OUTER']
          }
        });
      });

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla = t2.bla | JOIN table3"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla = t2.bla ',
          afterCursor: ' JOIN table3',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['AND', '=', 'IN', 'FULL', 'FULL OUTER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla | JOIN table3"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla ',
          afterCursor: ' JOIN table3',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['=', 'LEFT OUTER'],
          containsColRefKeywords: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'bla' }], table: 'table1' }
          }
        });
      });

      it('should suggest keywords for "SELECT t1.* FROM table1 t1 FULL | JOIN"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.* FROM table1 t1 FULL ',
          afterCursor: ' JOIN',
          dialect: 'generic',
          hasLocations: true,
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
          hasLocations: true,
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
          hasLocations: true,
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
            hasLocations: true,
            containsKeywords: ['LEFT SEMI JOIN', 'CROSS JOIN'], // Tested in full above
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 INNER |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 INNER ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 FULL |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 FULL ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'JOIN', 'OUTER JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 LEFT |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 LEFT ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'JOIN', 'OUTER JOIN', 'SEMI JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 RIGHT |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 RIGHT ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'JOIN', 'OUTER JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 CROSS |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 CROSS ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 ',
            afterCursor: ' JOIN',
            dialect: 'hive',
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestIdentifiers: [{ name: 't1.', type: 'alias' }, { name: 'table2.', type: 'table' }, { name: 'table3.', type: 'table' }, { name: 't4.', type: 'alias' }]
            }
          });
        });

        it('should suggest tables for "SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab| CROSS JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab',
            afterCursor: ' CROSS JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should suggest identifiers for "SELECT t1.* FROM table1 t1 JOIN table2 t2 USING (foo, bar) WHERE "', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 USING (foo, bar) WHERE ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestKeywords: ['EXISTS', 'NOT EXISTS'],
              suggestIdentifiers: [{ name: 't1.', type: 'alias'}, { name: 't2.', type: 'alias' }]
            }
          });
        });

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['LEFT ANTI JOIN', 'RIGHT ANTI JOIN'], // Tested in full above
            hasLocations: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 INNER |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 INNER ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 FULL |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 FULL ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'JOIN', 'OUTER JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 LEFT |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 LEFT ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'ANTI JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN' ]
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM testTable1 RIGHT |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 LEFT ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: [ 'ANTI JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN' ]
            }
          });
        });

        it('should suggest tables for "SELECT * FROM testTable1 JOIN |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable1 JOIN ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true },
              suggestKeywords: ['[BROADCAST]', '[SHUFFLE]']
            }
          });
        });

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 JOIN table2 t2 | JOIN table3"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 ',
            afterCursor: ' JOIN table3',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'ON', 'RIGHT', 'RIGHT OUTER', 'USING'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 ',
            afterCursor: ' JOIN',
            dialect: 'impala',
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
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
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestIdentifiers: [{ name: 't1.', type: 'alias' }, { name: 'table2.', type: 'table' }, { name: 'table3.', type: 'table' }, { name: 't4.', type: 'alias' }]
            }
          });
        });

        it('should suggest tables for "SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab| INNER JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab',
            afterCursor: ' INNER JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2',
            dialect: 'impala',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true },
              suggestKeywords: ['[BROADCAST]', '[SHUFFLE]']
            }
          });
        });
      });
    });

    describe('SubQueries in WHERE Clause', function () {
      it('should suggest keywords for "SELECT * FROM foo WHERE bar |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar ',
          afterCursor: '',
          dialect: 'generic',
          containsKeywords: ['IN', 'NOT IN'],
          containsColRefKeywords: true,
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'bar' }], table: 'foo' }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE bar NOT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar NOT ',
          afterCursor: '',
          containsKeywords: ['IN'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM foo WHERE bar IN (|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT'],
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestColumns: { types: ['COLREF'], table: 'foo' },
            colRef: { identifierChain: [{ name: 'bar'}], table: 'foo' }
          }
        });
      });

      it('should suggest keywords for "select * from foo, bar where bar.bla in (|"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from foo, bar where bar.bla in (',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['SELECT'],
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestIdentifiers: [{ name: 'foo.', type: 'table'}, { name: 'bar.', type: 'table'}],
            colRef: { identifierChain: [{name: 'bla'}], table: 'bar' }
          }
        });
      });

      it('should suggest values for "select * from foo, bar where bar.bla in (\'a\', |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from foo, bar where bar.bla in (\'a\', ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: true,
            suggestIdentifiers: [{ name: 'foo.', type: 'table'}, { name: 'bar.', type: 'table'}],
            colRef:  { identifierChain: [{name: 'bla'}], table: 'bar' }
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            },
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18}, table: 'foo' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28}, identifierChain: [{ name: 'bar'}], table: 'foo'}
            ]
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestDatabases: {
              prependQuestionMark: true,
              prependFrom: true,
              appendDot: true
            },
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18}, table: 'bar' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28}, identifierChain: [{ name: 'foo'}], table: 'bar'}
            ]
          }
        });
      });
    });

    describe('SubQueries in FROM Clause', function () {
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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

      it('should suggest columns for "SELECT "contains an even number" FROM t1, t2 AS ta2 WHERE EXISTS (SELECT t3.foo FROM t3 WHERE | % 2 = 0"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT "contains an even number" FROM t1, t2 AS ta2 WHERE EXISTS (SELECT t3.foo FROM t3 WHERE ',
          afterCursor: ' % 2 = 0',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestIdentifiers: [{ name: 't1.', type: 'table' }, { name: 'ta2.', type: 'alias' }, { name: 't3.', type: 'table'}],
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 39, last_column: 41}, table: 't1' },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 43, last_column: 45}, table: 't2' },
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 74, last_column: 80}, identifierChain: [{ name: 'foo'}], table: 't3'},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 86, last_column: 88}, table: 't3' }
            ]
          }
        });
      });

      it('should suggest identifiers for "SELECT | FROM testTable tt, (SELECT bla FROM abc WHERE foo > 1) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable tt, (SELECT bla FROM abc WHERE foo > 1) bar',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'tt.', type: 'alias'}, { name: 'bar.', type: 'sub-query'}],
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 14, last_column: 23}, table: 'testTable'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 36, last_column: 39}, identifierChain: [{ name: 'bla'}], table: 'abc'},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 45, last_column: 48}, table: 'abc'},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 55, last_column: 58}, identifierChain: [{ name: 'foo'}], table: 'abc'}
            ],
            subQueries: [{
              alias: 'bar',
              columns: [
                { identifierChain: [{ name: 'bla' }], type: 'COLREF', table: 'abc'}
              ]
            }]
          }
        });
      });

      it('should suggest columns for "select | from (select id i, name as n, bla from foo) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from (select id i, name as n, bla from foo) bar',
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { subQuery: 'bar' },
            subQueries: [{
              alias: 'bar',
              columns: [
                { alias: 'i', identifierChain: [{ name: 'id' }], type: 'COLREF', table: 'foo' },
                { alias: 'n', identifierChain: [{ name: 'name' }], type: 'COLREF', table: 'foo' },
                { identifierChain: [{ name: 'bla' }], type: 'COLREF', table: 'foo' }
              ]
            }],
            suggestIdentifiers: [{ name: 'bar.', type: 'sub-query' }]
          }
        });
      });

      it('should suggest columns for "select | from (select id i, name as n, bla from foo) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from (select id i, name as n, bla from foo) bar',
          hasLocations: true,
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { subQuery: 'bar' },
            subQueries: [{
              alias: 'bar',
              columns: [
                { alias: 'i', identifierChain: [{ name: 'id' }], type: 'COLREF', table: 'foo' },
                { alias: 'n', identifierChain: [{ name: 'name' }], type: 'COLREF', table: 'foo' },
                { identifierChain: [{ name: 'bla' }], type: 'COLREF', table: 'foo' }
              ]
            }],
            suggestIdentifiers: [{ name: 'bar.', type: 'sub-query' }]
          }
        });
      });

      it('should suggest sub-query columns for "SELECT bar.| FROM (SELECT col1, col2, (col3 + 1) col3alias FROM foo) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bar.',
          afterCursor: ' FROM (SELECT col1, col2, (col3 + 1) col3alias FROM foo) bar',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { subQuery: 'bar' },
            subQueries: [{
              alias: 'bar',
              columns: [
                { identifierChain: [{ name: 'col1' }], type: 'COLREF', table: 'foo' },
                { identifierChain: [{ name: 'col2' }], type: 'COLREF', table: 'foo' },
                { alias: 'col3alias', type: 'NUMBER' }
              ]}
            ]
          }
        });
      });

      it('should suggest sub-query columns for "SELECT bar.| FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bar.',
          afterCursor: ' FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { subQuery: 'bar' },
            subQueries: [{
              alias: 'boo',
              columns: [{ identifierChain: [{ name: 'b' }], type: 'COLREF', table: 'foo' }]
            }, {
              alias: 'bar',
              columns: [{ identifierChain: [{ name: 'a' }], type: 'COLREF', table: 'bla' }]
            }]
          }
        });
      });

      it('should suggest identifiers for "SELECT cos(| FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cos(',
          afterCursor: ' FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['T'] },
            subQueries: [{
              alias: 'boo',
              columns: [{ identifierChain: [{ name: 'b' }], type: 'COLREF', table: 'foo' }]
            }, {
              alias: 'bar',
              columns: [{ identifierChain: [{ name: 'a' }], type: 'COLREF', table: 'bla' }]
            }],
            suggestIdentifiers: [{ name: 'boo.', type: 'sub-query' }, { name: 'bar.', type: 'sub-query' }]
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
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
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

      it('should suggest identifiers for "SELECT | FROM (SELECT * FROM tableOne) AS subQueryOne, someDb.tableTwo tAlias, tableThree, (SELECT * FROM t3 JOIN table4 t4 ON t3.id = t4.id) subQueryTwo;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT * FROM tableOne) AS subQueryOne, someDb.tableTwo tAlias, tableThree, (SELECT * FROM t3 JOIN table4 t4 ON t3.id = t4.id) subQueryTwo;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestIdentifiers: [{ name: 'subQueryOne.', type: 'sub-query'}, { name: 'tAlias.', type: 'alias'}, { name: 'tableThree.', type: 'table'}, { name: 'subQueryTwo.', type: 'sub-query'}],
            subQueries: [{
              alias: 'subQueryOne',
              columns: [{ table: 'tableOne' }]
            }, {
              alias: 'subQueryTwo',
              columns: [{ tables: [{ table: 't3' }, { table: 'table4' }] }]
            }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM (SELECT | FROM tableOne) subQueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subQueryTwo;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ' FROM tableOne) subQueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subQueryTwo;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: {
              table: 'tableOne'
            }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo',
          hasLocations: true,
          expectedResult: {
            lowerCase:false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { subQuery: 'subQueryTwo'},
            subQueries: [{
              alias: 'subQueryTwo',
              columns: [{ subQuery: 'subQueryOne' }],
              subQueries: [{
                alias: 'subQueryOne',
                columns: [{ table: 'tableOne'}]
              }]
            }],
            suggestIdentifiers: [{ name: 'subQueryTwo.', type: 'sub-query' }]
          }
        });
      });

      it('should suggest columns for "SELECT | FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
          hasLocations: true,
          expectedResult: {
            lowerCase:false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { subQuery: 'subQueryThree'},
            subQueries: [{
              alias: 'subQueryThree',
              columns: [{ subQuery: 'subQueryTwo' }],
              subQueries: [{
                alias: 'subQueryTwo',
                columns: [{ subQuery: 'subQueryOne' }],
                subQueries: [{
                  alias: 'subQueryOne',
                  columns: [{ table: 'tableOne' }]
                }]
              }]
            }],
            suggestIdentifiers: [{ name: 'subQueryThree.', type: 'sub-query' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM (SELECT | FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ' FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
          hasLocations: true,
          expectedResult: {
            lowerCase:false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { subQuery: 'subQueryTwo'},
            subQueries: [{
              alias: 'subQueryTwo',
              columns: [{ subQuery: 'subQueryOne' }],
              subQueries: [{
                alias: 'subQueryOne',
                columns: [{ table: 'tableOne' }]
              }]
            }],
            suggestIdentifiers: [{ name: 'subQueryTwo.', type: 'sub-query' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM (SELECT * FROM (SELECT | FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT * FROM (SELECT ',
          afterCursor: ' FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
          hasLocations: true,
          expectedResult: {
            lowerCase:false,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestAggregateFunctions: true,
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { subQuery: 'subQueryOne'},
            subQueries: [{
              alias: 'subQueryOne',
              columns: [{ table: 'tableOne' }]
            }],
            suggestIdentifiers: [{ name: 'subQueryOne.', type: 'sub-query' }]
          }
        });
      });

      it('should suggest columns for "SELECT s2.| FROM (SELECT a, bla FROM (SELECT a, b, abs(1) as bla FROM testTable) s1) s2;"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT s2.',
          afterCursor: ' FROM (SELECT a, bla FROM (SELECT a, b, abs(1) as bla FROM testTable) s1) s2;',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase:false,
            suggestKeywords: ['*'],
            suggestColumns: { subQuery: 's2' },
            subQueries: [{
              alias: 's2',
              columns: [
                { identifierChain: [{ name: 'a' }], type: 'COLREF', subQuery: 's1'},
                { identifierChain: [{ name: 'bla' }], type: 'COLREF', subQuery: 's1'}
              ],
              subQueries: [{
                alias: 's1',
                columns: [
                  { identifierChain: [{ name: 'a' }], type: 'COLREF', table: 'testTable'},
                  { identifierChain: [{ name: 'b' }], type: 'COLREF', table: 'testTable'},
                  { alias: 'bla', type: 'T'}
                ]
              }]
            }]
          }
        });
      });

      it('should suggest columns for "SELECT s2.| FROM (SELECT a, bla FROM (SELECT a, b, abs(1) as bla FROM testTable) s1) s2;"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT s2.',
          afterCursor: ' FROM (SELECT a, bla FROM (SELECT a, b, abs(1) as bla FROM testTable) s1) s2;',
          hasLocations: true,
          dialect: 'hive',
          expectedResult: {
            lowerCase:false,
            suggestKeywords: ['*'],
            suggestColumns: { subQuery: 's2' },
            subQueries: [{
              alias: 's2',
              columns: [
                { identifierChain: [{ name: 'a' }], type: 'COLREF', subQuery: 's1'},
                { identifierChain: [{ name: 'bla' }], type: 'COLREF', subQuery: 's1'}
              ],
              subQueries: [{
                alias: 's1',
                columns: [
                  { identifierChain: [{ name: 'a' }], type: 'COLREF', table: 'testTable'},
                  { identifierChain: [{ name: 'b' }], type: 'COLREF', table: 'testTable'},
                  { alias: 'bla', type: 'DOUBLE'}
                ]
              }]
            }]
          }
        });
      });
    });
  });
});