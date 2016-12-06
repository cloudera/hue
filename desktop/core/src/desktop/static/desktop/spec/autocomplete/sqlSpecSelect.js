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
  describe('sql.js SELECT statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

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

    it('should suggest tables and databases for "SELECT *\\r\\n |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT *\r\n',
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

    it('should not suggest anything for "SELECT u.|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT u.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false
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
          suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'testTableB' }] }] },
          suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
          suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
          suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
          suggestKeywords: ['AS', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'UNION', 'FULL JOIN', 'FULL OUTER JOIN', 'INNER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN'],
          lowerCase: false
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
          suggestTables: { identifierChain: [{ name: 'database_two' }] }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM `database_two`.|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM `database_two`.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'database_two' }] }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM 33abc.|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM 33abc.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: '33abc' }] }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM `database_two`.`bla |"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM `database_two`.`bla ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'database_two' }] }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM database_two.boo.|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.bla.',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'database_two' }, { name: 'bla' }] }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM database_two.boo.bee.boo.bl|"', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.boo.bee.boo.bl',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'database_two' }, { name: 'boo' }, { name: 'bee' }, { name: 'boo' }] }
        }
      });
    });

    describe('Complete Statements', function () {
      it ('should handle "SELECT bla NOT RLIKE \'ble\', ble NOT REGEXP \'b\' FROM tbl; |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bla NOT RLIKE \'ble\', ble NOT REGEXP \'b\' FROM tbl; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns "SELECT IF(baa, boo, bee) AS b, | FROM testTable;"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT IF(baa, boo, bee) AS b, ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAnalyticFunctions: true,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest columns "SELECT IF(baa > 2, boo, bee) AS b, | FROM testTable;"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT IF(baa > 2, boo, bee) AS b, ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAnalyticFunctions: true,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestKeywords: ['*']
          }
        });
      });

      it('should handle 100k rows before and after "SELECT * FROM foo WHERE (bar = \'bla\') AND (ble = 1);|"', function() {
        var beforeCursor = '';
        var afterCursor = ';\n';
        for (var i = 0; i < 100000; i++) {
          beforeCursor += 'SELECT * FROM foo WHERE (bar = \'bla\') AND (ble = 1);\n';
          afterCursor += 'SELECT * FROM foo WHERE (bar = \'bla\') AND (ble = 1);\n';
        }
        assertAutoComplete({
          beforeCursor: beforeCursor,
          afterCursor: afterCursor,
          dialect: 'hive',
          noErrors: true,
          hasLocations: true,
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
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestTables: {
              prependQuestionMark: true,
              prependFrom: true
            },
            suggestAggregateFunctions: { tables: [] },
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
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: true,
            suggestAggregateFunctions: { tables: [] },
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
          containsKeywords: ['*'],
          doesNotContainKeywords: ['ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [] },
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
          containsKeywords: ['*'],
          doesNotContainKeywords: ['ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
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
          containsKeywords: ['*'],
          doesNotContainKeywords: ['ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'tbl' }] }] },
            locations: [
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 }, identifierChain:[{ name: 'tbl' }, { name: 'a'}] },
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 21, last_column: 22 }, identifierChain:[{ name: 'tbl' }, { name: 'b'}] },
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 24, last_column: 25 }, identifierChain:[{ name: 'tbl' }, { name: 'c'}] },
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 31, last_column: 34 }, identifierChain: [{ name: 'tbl' }]}
            ]
          }
        });
      });

      it('should suggest tables for "SELECT | FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM tableA;',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'tableA' }] }] }
          }
        });
      });

      it('should suggest tables for "SELECT | AS boo FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' AS boo FROM tableA;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'tableA' }] }] }
          }
        });
      });

      it('should suggest tables for "SELECT | boo FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' boo FROM tableA;',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'tableA' }] }] }
          }
        });
      });

      it('should suggest tables for "SELECT bla| AS boo FROM tableA;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bla',
          afterCursor: ' AS boo FROM tableA;',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'tableA' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testWHERE"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testWHERE',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testWHERE' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testWHERE' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT (bl|a AND boo FROM testWHERE"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT (bl',
          afterCursor: ' AND boo FROM testWHERE',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testWHERE' }] }] }
          }
        });
      });

      // TODO: Parser can't handle multiple errors in a row, in this case 2 missing ')')
      xit('should suggest columns for "SELECT ((| FROM testWHERE"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ((',
          afterCursor: ' FROM testWHERE',
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testWHERE' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT (bla| AND boo FROM testWHERE"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT (bla',
          afterCursor: ' AND boo FROM testWHERE',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testWHERE' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM testON"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testON',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testON' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testON' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM transactions"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM transactions',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'transactions' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'transactions' }] }] }
          }
        });
      });

      it('should suggest aliases for "SELECT | FROM testTableA tta, testTableB"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, testTableB',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "SELECT | FROM db.tbl1, db.tbl2"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM db.tbl1, db.tbl2',
          dialect: 'generic',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl1' }] }, { identifierChain: [{ name: 'db' }, { name: 'tbl2' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl1' }] }, { identifierChain: [{ name: 'db' }, { name: 'tbl2' }] }] },
            suggestIdentifiers: [{ name: 'tbl1.', type: 'table' },{ name: 'tbl2.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "SELECT | FROM db.tbl1.col, db.tbl2"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM db.tbl1.col, db.tbl2',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl1' }, { name: 'col' }] }, { identifierChain: [{ name: 'db' }, { name: 'tbl2' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl1' }, { name: 'col' }] }, { identifierChain: [{ name: 'db' }, { name: 'tbl2' }] }] },
            suggestIdentifiers: [{ name: 'col.', type: 'table' },{ name: 'tbl2.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "select | from database_two.testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from database_two.testTable',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: true,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "select | from `database one`.`test table`"', function () {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from `database one`.`test table`',
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: true,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'database one' }, { name: 'test table' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'database one' }, { name: 'test table' }] }] },
            locations: [
              { type: 'database', location: { first_line: 1, last_line: 1, first_column: 14, last_column: 28}, identifierChain: [{ name: 'database one' }]},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 29, last_column: 41}, identifierChain: [{ name: 'database one' }, { name: 'test table' }] }
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
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }], alias: 'ttb' }] },
            suggestAnalyticFunctions: true,
            suggestKeywords: ['*', 'ALL', 'DISTINCT'],
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ subQuery: 'ttaSum'}] }, { identifierChain: [{ name: 'testTableB' }], alias: 'ttb' }] },
            subQueries: [{
              alias: 'ttaSum',
              columns: [{ alias: 'total', type: 'DOUBLE' }]
            }],
            suggestIdentifiers: [{ name:'tta.', type:'alias' }, { name:'ttaSum.', type:'sub-query' }, { name:'ttb.', type:'alias' }],
            lowerCase: false
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
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'tableA' }] }] }
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
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'tableA' }] }] }
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
            colRef: { identifierChain: [{ name: 'tableA' }, { name: 'a' }] }
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
            colRef: { identifierChain: [{ name: 'tableA' }, { name: 'a' }] }
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
            colRef: { identifierChain: [{ name: 'tableA' }, { name: 'b' }] }
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
            colRef: { identifierChain: [{ name: 'tableA' }, { name: 'a' }] }
          }
        });
      });

      it('should suggest columns for "SELECT | a, cast(b as int), c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' a, cast(b as int), c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            locations: [
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9} , identifierChain: [{ name: 'testTable' }, { name: 'a' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 11, last_column: 12 }, identifierChain: [{ name: 'testTable' }, { name: 'b' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 }, identifierChain: [{ name: 'testTable' }, { name: 'c' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 }, identifierChain: [{ name: 'testTable' }, { name: 'd' }]},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 34 }, identifierChain: [{ name: 'testTable' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 42 }, identifierChain: [{ name: 'testTable' }, { name: 'a' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 54, last_column: 55 }, identifierChain: [{ name: 'testTable' }, { name: 'b' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 72, last_column: 73 }, identifierChain: [{ name: 'testTable' }, { name: 'c' }]}
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
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: '${some_variable}' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: '${some_variable}' }] }] }
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
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain:[{ name: 'testTable' }, { name: '${some_variable}' }]}
          }
        });
      });

      it('should suggest tables for "SELECT * FROM testTable WHERE ${some_variable} + 1 = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ${some_variable} + 1 = ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER']},
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }]}] }
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
            suggestAggregateFunctions: { tables: [] },
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT row_number() OVER (ORDER BY |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (ORDER BY ',
          afterCursor: ') FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] } // TODO: source: 'order by'
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT row_number() OVER (PARTITION BY a, | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT row_number() OVER (PARTITION BY a, ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            beforeCursor: 'SELECT count(id) OVER w FROM customers ',
            afterCursor: '',
            hasLocations: true,
            dialect: 'hive',
            containsKeywords: ['WINDOW'],
            expectedResult: {
              lowerCase: false,
              suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'customers' }] }] },
              suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'customers' }] }] },
              suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'customers' }] }] },
              suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'customers' }] }] }
            }
          });
        });

        it('should suggest keywords for "SELECT count(id) OVER w FROM customers WINDOW w |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT count(id) OVER w FROM customers WINDOW w ',
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
            beforeCursor: 'SELECT count(id) OVER w FROM customers WINDOW w AS (',
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT COUNT(foo, bl|, bla) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(foo, bl',
          afterCursor: ',bla) FROM bar;',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
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
          containsKeywords: ['CASE'],
          hasErrors: false,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { source: 'select',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'bar' }] }] },
            suggestValues: {},
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
          }
        });
      });

      it('should suggest columns and values for "SELECT bl = \'| FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bl = \'',
          afterCursor: ' FROM bar;',
          hasErrors: false,
          expectedResult: {
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'bar' }, { name: 'bl' }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 20, last_column: 23 }, identifierChain: [{ name: 'bar' }] }
            ],
            lowerCase: false,
            suggestValues: { partialQuote: '\'', missingEndQuote: true },
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
          }
        });
      });

      it('should suggest columns and values for "SELECT bl = \'|\' FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bl = \'',
          afterCursor: '\' FROM bar;',
          hasErrors: false,
          expectedResult: {
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'bar' }, { name: 'bl' }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 21, last_column: 24 }, identifierChain: [{ name: 'bar' }] }
            ],
            lowerCase: false,
            suggestValues: { partialQuote: '\'', missingEndQuote: false },
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
          }
        });
      });

      it('should suggest columns and values for "SELECT bl = \'bl| bl\' FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bl = \'bl',
          afterCursor: ' bl\' FROM bar;',
          hasErrors: false,
          expectedResult: {
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'bar' }, { name: 'bl' }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 29 }, identifierChain: [{ name: 'bar' }] }
            ],
            lowerCase: false,
            suggestValues: { partialQuote: '\'', missingEndQuote: false },
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
          }
        });
      });

      it('should suggest columns and values for "SELECT bl = "| FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bl = "',
          afterCursor: ' FROM bar;',
          hasLocations: true,
          hasErrors: false,
          expectedResult: {
            lowerCase: false,
            suggestValues: { partialQuote: '"', missingEndQuote: true },
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
          }
        });
      });

      it('should suggest columns and values for "SELECT bl = "|" FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bl = "',
          afterCursor: '" FROM bar;',
          hasErrors: false,
          expectedResult: {
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'bar' }, { name: 'bl' }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 21, last_column: 24 }, identifierChain: [{ name: 'bar' }] }
            ],
            lowerCase: false,
            suggestValues: { partialQuote: '"', missingEndQuote: false },
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
          }
        });
      });

      it('should suggest columns and values for "SELECT bl = "bl| bl" FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bl = "bl',
          afterCursor: ' bl" FROM bar;',
          hasErrors: false,
          expectedResult: {
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'bar' }, { name: 'bl' }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 29 }, identifierChain: [{ name: 'bar' }] }
            ],
            lowerCase: false,
            suggestValues: { partialQuote: '"', missingEndQuote: false },
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
          }
        });
      });

      it('should suggest functions for "SELECT CAST(|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(bla| FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla',
          afterCursor: ' FROM bar;',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS FROM bar;',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS INT FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS INT FROM bar;',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(| AS STRING) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(',
          afterCursor: ' AS STRING) FROM bar;',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CAST(bla| AS STRING) FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(bla',
          afterCursor: ' AS STRING) FROM bar;',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'bar' }] }] }
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
            colRef: { identifierChain: [{ name: 'bar' }, { name: 'bla' }]}
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['TIMESTAMP'] },
            suggestColumns: { source: 'select',  types: ['TIMESTAMP'], tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla ,|  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla ,',
          afterCursor: ' FROM bar;',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { source: 'select',  types: ['STRING'], tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, extract(bla FROM |)  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, extract(bla FROM ',
          afterCursor: ') FROM bar;',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['TIMESTAMP'] },
            suggestColumns: { source: 'select',  types: ['TIMESTAMP'], tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT extract(bla ,|)  FROM bar;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT extract(bla ,',
          afterCursor: ') FROM bar;',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { source: 'select',  types: ['STRING'], tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });


      it('should suggest columns for "SELECT <GeneralSetFunction>(|) FROM testTable"', function () {
        var aggregateFunctions = [
          { name: 'APPX_MEDIAN', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'AVG', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'AVG', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'AVG', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'collect_set', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'COLLECT_LIST', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'COUNT', dialect: 'generic', containsKeywords: ['*', 'DISTINCT'] },
          { name: 'COUNT', dialect: 'hive', containsKeywords: ['*', 'DISTINCT'] },
          { name: 'COUNT', dialect: 'impala', containsKeywords: ['*', 'ALL', 'DISTINCT'] },
          { name: 'GROUP_CONCAT', dialect: 'impala', containsKeywords: ['ALL'], types: ['STRING'] },
          { name: 'stddev', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'STDDEV_POP', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'STDDEV_POP', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'STDDEV_POP', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'STDDEV_SAMP', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'STDDEV_SAMP', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'STDDEV_SAMP', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'SUM', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'sum', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'SUM', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'MAX', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'MAX', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'max', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'MIN', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'MIN', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'MIN', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'VARIANCE', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'variance_pop', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'VARIANCE_SAMP', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'VAR_POP', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'VAR_POP', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'VAR_POP', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] },
          { name: 'var_samp', dialect: 'generic', containsKeywords: ['DISTINCT'] },
          { name: 'VAR_SAMP', dialect: 'hive', containsKeywords: ['DISTINCT'] },
          { name: 'VAR_SAMP', dialect: 'impala', containsKeywords: ['ALL', 'DISTINCT'] }
        ];
        aggregateFunctions.forEach(function (aggregateFunction) {
          if (aggregateFunction.name === 'COUNT') {
            assertAutoComplete({
              beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
              afterCursor: ') FROM testTable',
              dialect: aggregateFunction.dialect,
              hasLocations: true,
              containsKeywords: aggregateFunction.containsKeywords.concat(['*', 'CASE']),
              expectedResult: {
                lowerCase: false,
                suggestFunctions: {},
                suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
              }
            });
          } else {
            var expectedResult = {
              lowerCase: false,
              suggestFunctions: { types: aggregateFunction.types || ['T'] },
              suggestColumns: { source: 'select',  types: aggregateFunction.types || ['T'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
            };
            assertAutoComplete({
              beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
              afterCursor: ') FROM testTable',
              dialect: aggregateFunction.dialect,
              hasLocations: true,
              containsKeywords: aggregateFunction.containsKeywords.concat(['CASE']),
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
            containsKeywords: ['DISTINCT', 'CASE'],
            doesNotContainKeywords: ['ALL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['T'] },
              suggestColumns: { source: 'select',  types: ['T'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['T'] },
              suggestColumns: { source: 'select',  types: ['T'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            containsKeywords: ['CASE', 'DISTINCT'],
            doesNotContainKeywords: ['ALL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['T'] },
              suggestColumns: { source: 'select',  types: ['T'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
            }
          });
        })
      });

      it('should suggest columns for "SELECT id, SUM(a * | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT id, SUM(a * ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'select',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestKeywords: ['WHEN']
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b AND | THEN FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b AND ',
          afterCursor: ' THEN FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = b AND | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = b AND ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = b OR c THEN boo OR | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = b OR c THEN boo OR ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a =| WHEN c THEN d END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a =',
          afterCursor: ' WHEN c THEN d END FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { source: 'select',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestValues: {},
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a =| WHEN c THEN d ELSE e END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a =',
          afterCursor: ' WHEN c THEN d ELSE e END FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { source: 'select',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestValues: {},
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
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
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d=| ELSE FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d=',
          afterCursor: ' ELSE FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { source: 'select',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestValues: {},
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE e AND | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE e AND ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE ELSE | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE ELSE ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
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
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'e' }]}
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN THEN boo OR | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN THEN boo OR ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'c' }] }
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
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'c' }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN | THEN FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' THEN FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest values for "SELECT CASE WHEN | = a FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' = a FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { source: 'select',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestValues: {},
            colRef: { identifierChain :[{ name: 'testTable' }, { name :'a'}] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN ab| THEN bla ELSE foo FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ab',
          afterCursor: ' THEN bla ELSE foo FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE bla WHEN ab| THEN bla ELSE foo END FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE bla WHEN ab',
          afterCursor: ' THEN bla ELSE foo END FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a WHEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a WHEN ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN a = | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN a = ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { source: 'select',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestValues: {},
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
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
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'c' }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE a = c WHEN c THEN | g FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE a = c WHEN c THEN ',
          afterCursor: ' g FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN THEN | g FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN THEN ',
          afterCursor: ' g FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT CASE WHEN THEN | FROM testTable"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT CASE WHEN THEN ',
          afterCursor: ' FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestKeywords: ['TABLESAMPLE', 'AS', 'LATERAL VIEW', 'WHERE', 'GROUP BY', 'HAVING', 'WINDOW', 'ORDER BY', 'CLUSTER BY', 'DISTRIBUTE BY', 'SORT BY', 'LIMIT', 'UNION', 'CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN']
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
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }] },
            suggestKeywords: ['LATERAL VIEW', 'WHERE', 'GROUP BY', 'HAVING', 'WINDOW', 'ORDER BY', 'CLUSTER BY', 'DISTRIBUTE BY', 'SORT BY', 'LIMIT', 'UNION', 'CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN']
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
            lowerCase: false,
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }] },
            suggestJoinConditions: { prependOn: true, tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }] }
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
            lowerCase: false,
            suggestJoinConditions: { prependOn: true, tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }] }
          }
        });
      });

      it('should suggest keywords for "SELECT bar\\nFROM foo\\n|"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar\nFROM foo\n',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['WHERE', 'HAVING'],
          expectedResult: {
            lowerCase: false,
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
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
            suggestKeywords: ['OUTER', 'explode', 'posexplode']
          }
        });
      });

      it('should suggest keywords for "SELECT bar FROM foo LATERAL VIEW explode(bar) b |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo LATERAL VIEW explode(bar) b ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['AS', 'WHERE'],
          expectedResult: {
            lowerCase: false,
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap', keySet: true }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestKeyValues: { identifierChain: [{ name: 'testTable' }, { name: 'testMap' }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap', keySet: true }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap', keySet: true }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap', keySet: true }, { name: 'fieldC' }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testArray', keySet: true }, { name: 'fieldC' }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testFoo', keySet: true }, { name: 'testBar', keySet: true }] }] },
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
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap', keySet: true }] }] }
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
              locations: [
                {type: 'table', location: { first_line: 1, last_line: 1, first_column: 14, last_column: 23 }, identifierChain: [{ name: 'testTable' }] },
                {type: 'function', location: { first_line: 1, last_line: 1, first_column: 37, last_column: 43 }, function: 'explode'},
                {type: 'column', location: { first_line: 1, last_line: 1, first_column: 45, last_column: 54 }, identifierChain: [{ name: 'testTable' }, { name: 'testArray' }] }
              ],
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestAnalyticFunctions: true,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestFunctions: {},
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testItem', type: 'alias' }],
              lowerCase: false
            }
          });
        });

        it('should suggest aliases for "SELECT | FROM testTable LATERAL VIEW EXPLODE(testTable.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW EXPLODE(testTable.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;',
            dialect: 'hive',
            hasLocations: true,
            noErrors: true,
            containsKeywords: ['*', 'ALL', 'DISTINCT'],
            expectedResult: {
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestAnalyticFunctions: true,
              suggestFunctions: {},
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestIdentifiers: [{ name: 'a.', type: 'alias' }, { name: 'arr_exp', type: 'alias' }, { name: 'i.', type: 'alias' }, { name: 'arr_items', type: 'alias' }],
              lowerCase: false
            }
          });
        });

        it('should suggest aliases for "SELECT | FROM testTable t LATERAL VIEW EXPLODE(t.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable t LATERAL VIEW EXPLODE(t.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;',
            dialect: 'hive',
            noErrors: true,
            hasLocations: true,
            containsKeywords: ['*', 'ALL', 'DISTINCT'],
            expectedResult: {
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }] },
              suggestAnalyticFunctions: true,
              suggestFunctions: {},
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }] },
              suggestIdentifiers: [{ name: 't.', type: 'alias' }, { name: 'a.', type: 'alias' }, { name: 'arr_exp', type: 'alias' }, { name: 'i.', type: 'alias' }, { name: 'arr_items', type: 'alias' }],
              lowerCase: false
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
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestAnalyticFunctions: true,
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
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
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['ARRAY', 'MAP' ] },
              suggestColumns: { types: ['ARRAY', 'MAP' ], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
              suggestColumns: { types: ['ARRAY', 'MAP' ], tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'a' }, { name: 'b' }] }] }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW posexplode(|"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW posexplode(',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['ARRAY' ] },
              suggestColumns: { types: ['ARRAY' ], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
            }
          });
        });

        it('should suggest aliases for "SELECT | FROM testTable LATERAL VIEW explode(testMap) explodedTable AS testKey, testValue"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedTable AS testKey, testValue',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
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
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testArray' }, { name: 'item' }] }] }
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
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testArrayA' }, { name: 'item' }] }] }
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
              locations: [
                { type: 'column', location: { first_line: 2, last_line: 2, first_column: 2, last_column: 11 }, identifierChain: [{ name: 'testTable2' }, { name: 'testArrayA'}, {name: 'item'}] },
                { type: 'column', location: { first_line: 3, last_line: 3, first_column: 2, last_column: 11 }, identifierChain: [{ name: 'testTable2' },{ name: 'testArrayB' },{ name: 'item'}]},
                { type: 'table', location: { first_line: 5, last_line: 5, first_column: 3, last_column: 13 }, identifierChain: [{ name: 'testTable2' }]},
                { type: 'function', location: { first_line: 6, last_line: 6, first_column: 16, last_column: 22 }, function: 'explode'},
                { type: 'table', location: { first_line: 6, last_line: 6, first_column: 24, last_column: 27 }, identifierChain: [{ name: 'testTable2' }]},
                { type: 'column', location: { first_line: 6, last_line: 6, first_column: 28, last_column: 38 }, identifierChain: [{ name: 'testTable2' }, { name: 'testArrayA'}] },
                { type: 'function', location: { first_line: 7, last_line: 7, first_column: 16, last_column: 22 }, function: 'explode'},
                { type: 'table', location: { first_line: 7, last_line: 7, first_column: 24, last_column: 27 }, identifierChain: [{ name: 'testTable2' }]},
                { type: 'column', location: { first_line: 7, last_line: 7, first_column: 28, last_column: 38 }, identifierChain: [{ name: 'testTable2' }, { name: 'testArrayB'}] }
              ],
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable2' }, { name: 'testArrayB' }, { name: 'item' }] }] },
              lowerCase: false
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
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testArray1' }, { name: 'item' }, { name: 'testArray2' }, { name: 'item' }] }] }
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
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testArray' }, { name: 'item' }] }] }
            }
          });
        });

        it('should suggest identifiers for "SELECT testValue.| FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS testIndex, testValue"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT testValue.',
            afterCursor: ' FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS testIndex, testValue',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testArray' }, { name: 'item' }] }] }
            }
          });
        });

        it('should suggest columns for "SELECT boo.| FROM customers LATERAL VIEW explode(baa) boo;"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT boo.',
            afterCursor: ' FROM customers LATERAL VIEW explode(baa) boo;',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestIdentifiers: [{ name: 'key', type: 'alias' }, { name: 'value', type: 'alias' }]
            }
          });
        });

        it('should suggest columns for "SELECT boo.| FROM customers LATERAL VIEW posexplode(baa) boo;"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT boo.',
            afterCursor: ' FROM customers LATERAL VIEW posexplode(baa) boo;',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestIdentifiers: [{ name: 'pos', type: 'alias' }, { name: 'val', type: 'alias' }]
            }
          });
        });

        it('should suggest columns for "SELECT testMapValue.| FROM testTable LATERAL VIEW explode(testMap) bla AS testMapKey, testMapValue"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) AS testMapKey, testMapValue',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap' }, { name: 'value' }] }] }
            }
          });
        });

        it('should suggest columns for "SELECT explodedMap.testMapValue.| FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT explodedMap.testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap' }, { name: 'value' }] }] }
            }
          });
        });

        it('should suggest identifier for "SELECT explodedMap.| FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT explodedMap.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestIdentifiers: [{ name: 'testMapKey', type: 'alias' }, { name: 'testMapValue', type: 'alias' }]
            }
          });
        });

        it('should suggest identifiers for "SELECT | FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['*', 'ALL', 'DISTINCT'],
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestAnalyticFunctions: true,
              suggestFunctions: {},
              suggestIdentifiers: [{ name: 'explodedMap.', type: 'alias' }, { name: 'testMapKey', type: 'alias' }, { name: 'testMapValue', type: 'alias' }],
              suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'testTableB' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestKeywords: ['AS', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'OFFSET', 'UNION', 'FULL JOIN', 'FULL OUTER JOIN', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN']
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap',  keySet: true }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'columnA' }, { name: 'fieldC' }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'columnA' }, { name: 'fieldC' }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'columnA' }, { name: 'fieldC' }] }] },
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
            locations: [
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10}, identifierChain: [{ name: 'testTable' },{ name: 'testMap' }]},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 17, last_column :26}, identifierChain: [{ name: 'testTable' }]},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 30, last_column: 31}, identifierChain: [{ name: 'testTable' }]},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 32, last_column :39}, identifierChain: [{ name: 'testTable' }, { name: 'testMap'}] }
            ],
            suggestKeywords: ['*'],
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap' }] }] },
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT tm.a| FROM testTable t, t.testMap tm;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT tm.a',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap' }] }] }
          }
        });
      });

      // Same as above, 'items' or 'value' for scalar
      it('should suggest columns for "SELECT ta.* FROM testTable t, t.testArray ta WHERE ta.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ta.* FROM testTable t, t.testArray ta WHERE ta.',
          afterCursor: '',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testArray' }] }] },
            lowerCase: false
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
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestKeywords: ['*', 'ALL', 'DISTINCT', 'STRAIGHT_JOIN'],
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }] },
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
            suggestColumns: { source: 'where', tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap' }] }] }
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
            suggestColumns: { source: 'where', tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'testMap' }, { name: 'value' }] }] }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable t, t.testMap tm WHERE tm.key =|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable t, t.testMap tm WHERE tm.key =',
          afterCursor: '',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }] },
            suggestIdentifiers : [{ name: 't.', type: 'alias' }, { name: 'tm.', type: 'alias' }],
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'testMap' }, { name: 'key' }] }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable t, t.testMap m WHERE m.field = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable t, t.testMap m WHERE m.field = ',
          afterCursor: '',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }] },
            suggestIdentifiers : [{ name: 't.', type: 'alias' }, { name: 'm.', type: 'alias' }],
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'testMap' }, { name: 'field' }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'columnA' }] }] }
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'columnA' }, { name: 'fieldC' }] }] },
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
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }, { name: 'columnA' }, { name: 'fieldC' }] }] },
            suggestKeywords: ['*'] // TODO: Verify that this is true
          }
        });
      });
    });

    describe('Dates', function () {
      describe('Impala specific', function () {
        it('should suggest keywords for "SELECT now() +|"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT now() +',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] }
            }
          });
        });

        it('should suggest keywords for "SELECT now() -|"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT now() -',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] }
            }
          });
        });

        it('should suggest keywords for "SELECT now() *|"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT now() *',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            doesNotContainKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] }
            }
          });
        });

        it('should suggest keywords for "SELECT \'1980-07-03\' +|"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT  \'1980-07-03\' +',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] }
            }
          });
        });

        it('should suggest keywords for "SELECT now() + INTERVAL 1 |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT now() + INTERVAL 1 ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['DAYS', 'HOURS', 'MICROSECONDS', 'MILLISECONDS', 'MINUTES', 'MONTHS', 'NANOSECONDS', 'SECONDS', 'WEEKS', 'YEARS']
            }
          });
        });

        it('should suggest keywords for "SELECT \'1999-01-01\' + INTERVAL 1 MONTH - |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT \'1999-01-01\' + INTERVAL 1 MONTH - ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] }
            }
          });
        });

        it('should suggest keywords for "SELECT to_utc_timestamp(now() + |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT to_utc_timestamp(now() + ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] } // TODO: Don't suggest functions for arithmetic expressions involving dates
            }
          });
        });

        it('should suggest keywords for "SELECT date_sub(now(), |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT date_sub(now(), ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['INT'] }
            }
          });
        });

        it('should suggest keywords for "SELECT date_add(now(), |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT date_add(now(), ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['INTERVAL'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['INT'] }
            }
          });
        });

        it('should suggest keywords for "SELECT date_add(now(), INTERVAL 100 |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT date_add(now(), INTERVAL 100 ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['DAYS'],
            expectedResult: {
              lowerCase: false
            }
          });
        });
      });
    });

    describe('Value Expression Completion', function() {
      it('should suggest functions for "SELECT \'boo \\\' baa\' = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT \'boo \\\' baa\' = ',
          afterCursor: '',
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] }
          }
        });
      });

      it('should suggest functions for "SELECT "boo \\" baa" = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT "boo \\" baa" = ',
          afterCursor: '',
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] }
          }
        });
      });

      it('should suggest identifiers for "SELECT 1 = | OR false FROM tableOne boo, tableTwo baa;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT 1 = ',
          afterCursor: ' OR false FROM tableOne boo, tableTwo baa;',
          containsKeywords: ['CASE'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'select',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'tableOne' }], alias: 'boo'}, { identifierChain: [{ name: 'tableTwo' }], alias: 'baa'}] },
            suggestIdentifiers:[{ name: 'boo.', type: 'alias'},{ name: 'baa.', type: 'alias'}]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { source: 'where', types: ['T'], tables: [{ identifierChain: [{ name: 'tbl2' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { source: 'where', types: ['T'], tables: [{ identifierChain: [{ name: 'tbl2' }] }] }
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
            suggestColumns: { source: 'where', types: ['DOUBLE'], tables: [{ identifierChain: [{ name: 'tbl2' }, { name: 'bla' }] }] }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE id = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE id =',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
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
            suggestColumns: { source: 'where', types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT 1 < | FROM testTable WHERE id = 1;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT 1 < ',
          afterCursor: ' FROM testTable WHERE id = 1;',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'select',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "select foo from tbl where | % 2 = 0"', function() {
        assertAutoComplete({
          beforeCursor: 'select foo from tbl where ',
          afterCursor: ' % 2 = 0',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: true,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where', types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'tbl' }] }] }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE -id = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE -id = ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
          }
        });
      });

      it('should suggest values for "SELECT * FROM testTable WHERE \'foo\' = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE \'foo\' = ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { source: 'where',  types: ['STRING'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed values for "SELECT * FROM testTable WHERE \'foo\' = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE \'foo\' = ',
          afterCursor: '',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { source: 'where',  types: ['STRING'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { source: 'select',  types: ['DECIMAL', 'DOUBLE'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT cos(| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cos(',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DOUBLE'] },
            suggestColumns: { source: 'select',  types: ['DOUBLE'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT ceiling(| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ceiling(',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DOUBLE'] },
            suggestColumns: { source: 'select',  types: ['DOUBLE'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT ceiling(| FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ceiling(',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { source: 'select',  types: ['DECIMAL', 'DOUBLE'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT a, ceiling(| b, c AS bla, d FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ceiling(',
          afterCursor: ' b, c AS bla, d FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { source: 'select',  types: ['DECIMAL', 'DOUBLE'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['T'] },
            suggestColumns: { source: 'select',  types: ['T'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT greatest(1, |, a, 4) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT greatest(1, ',
          afterCursor: ', a, 4) FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['T'] },
            suggestColumns: { source: 'select',  types: ['T'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT log(a, |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT log(a, ',
          afterCursor: ') FROM testTable',
          hasLocations: true,
          dialect: 'hive',
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL', 'DOUBLE'] },
            suggestColumns: { source: 'select',  types: ['DECIMAL', 'DOUBLE'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT log(a, |) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT log(a, ',
          afterCursor: ') FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DOUBLE'] },
            suggestColumns: { source: 'select',  types: ['DOUBLE'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['INT'] },
            suggestColumns: { source: 'select',  types: ['INT'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT substr(|, 1, 2) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT substr(',
          afterCursor: ', 1, 2) FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { source: 'select',  types: ['STRING'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['INT'] },
            suggestColumns: { source: 'select',  types: ['INT'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT cast(a AS BIGINT) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(a AS BIGINT) = ',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['BIGINT'] },
            suggestColumns: { source: 'select',  types: ['BIGINT'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT cast(a AS BIGINT) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(a AS BIGINT) = ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['BIGINT'] },
            suggestColumns: { source: 'select',  types: ['BIGINT'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT CAST(18446744073709001000BD AS DECIMAL(38,0)) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT CAST(18446744073709001000BD AS DECIMAL(38,0)) = ',
          afterCursor: ' FROM testTable',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['DECIMAL'] },
            suggestColumns: { source: 'select',  types: ['DECIMAL'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT cast(a AS BIGINT) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cast(a AS BIGINT) = ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['BIGINT'] },
            suggestColumns: { source: 'select',  types: ['BIGINT'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT years_add(a , 10) = | FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT years_add(a , 10) = ',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['TIMESTAMP'] },
            suggestColumns: { source: 'select',  types: ['TIMESTAMP'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT | > cast(years_add(a , 10) AS INT) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' > cast(years_add(a , 10) AS INT) FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['INT'] },
            suggestColumns: { source: 'select',  types: ['INT'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest typed columns for "SELECT bloo.partial| > cast(years_add(a , 10) AS INT) FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bloo.partial',
          afterCursor: ' > cast(years_add(a , 10) AS INT) FROM testTable',
          dialect: 'impala',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { source: 'select',  types: [ 'INT' ], tables: [{ identifierChain: [{ name: 'testTable' }, { name: 'bloo' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT | > id FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' > id FROM testTable',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { source: 'select',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestValues: {},
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT * FROM testTable WHERE | = id"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: ' = id',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d = |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d < |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d < ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <= |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <= ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <=> |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <=> ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <> |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <> ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d >= |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d > |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d > ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d != |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d != ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where',  types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + 1 != |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + 1 != ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE bla| + 1 != 3"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE bla',
          afterCursor: ' + 1 != 3',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d - |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d - ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d * |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d * ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d / |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d / ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d % |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d % ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d | |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d | ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d & |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d & ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d ^ |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ^ ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'where',  types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      // TODO: This one causes an unrecoverable error after the cursor, we should suggest group by etc.
      it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d | RLIKE \'bla bla\'"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ',
          afterCursor: ' RLIKE \'bla bla\'',
          hasLocations: true,
          containsKeywords: ['<', 'IN'],
          containsColRefKeywords: true,
          expectedResult: {
            lowerCase: false,
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd'}] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
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
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestKeywords: ['GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'UNION', '<', '<=', '<>', '=', '>', '>=', 'AND', 'BETWEEN', 'IN', 'IS NOT NULL', 'IS NULL', 'NOT BETWEEN', 'NOT IN', 'OR']
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
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestKeywords: ['GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'UNION', '<', '<=', '<>', '=', '>', '>=', 'AND', 'BETWEEN', 'IN', 'IS NOT NULL', 'IS NULL', 'NOT BETWEEN', 'NOT IN', 'OR']
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
            colRef: { identifierChain: [{ name: 'id' }], identifierChain: [{ name: 'foo' }] }
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
            suggestColumns: { source: 'where',  types: ['STRING'], tables: [{ identifierChain: [{ name: 'foo' }] }] }
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
            suggestGroupBys: {prefix: 'BY', tables: [{identifierChain: [{name: 'foo'}]}]},
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
            lowerCase: false,
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
          }
        });
      });

      it('should suggest identifiers for "SELECT * FROM foo bla, bar WHERE id IS NULL AND |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bla, bar WHERE id IS NULL AND ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }, { identifierChain: [{ name: 'bar' }] }] },
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }, { name: 'bar.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL && |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL && ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }] },
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL OR | AND 1 + 1 > 1"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL OR ',
          afterCursor: ' AND 1 + 1 > 1',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }] },
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL || |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL || ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }] },
            suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo bar WHERE NOT |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE NOT ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bar' }] },
            suggestKeywords: ['EXISTS'],
            suggestIdentifiers: [{ name: 'bar.', type: 'alias' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM foo bar WHERE ! |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo bar WHERE ! ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['BOOLEAN'] },
            suggestColumns: { source: 'where',  types: ['BOOLEAN'], tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bar' }] },
            suggestIdentifiers: [{ name: 'bar.', type: 'alias' }]
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest functions for "SELECT 100Y = |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT 100Y = ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] }
            }
          });
        });

        it('should suggest functions for "SELECT 100BD = |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT 100BD = ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['NUMBER'] }
            }
          });
        });

        it('should suggest keywords for "SELECT bar FROM foo WHERE id = 1 |"', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
              suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
              suggestKeywords: ['GROUP BY', 'HAVING', 'WINDOW', 'ORDER BY', 'CLUSTER BY', 'DISTRIBUTE BY', 'SORT BY', 'LIMIT', 'UNION', '<', '<=', '<=>', '<>', '=', '>', '>=', 'AND', 'BETWEEN',  'IN', 'IS NOT NULL', 'IS NULL',  'NOT BETWEEN', 'NOT IN', 'OR']
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
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestKeywords: ['EXISTS', 'NOT EXISTS'],
            suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestKeywords: ['EXISTS', 'NOT EXISTS'],
            suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
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
            lowerCase: false,
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            lowerCase: false,
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'tableOne' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE foo = \'bar\' AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE foo = \'bar\' AND ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'where',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestAnalyticFunctions: true,
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
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
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestAnalyticFunctions: true,
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest columns for "SELECT | a, b, c FROM testTable"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' a, b, c FROM testTable',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestAnalyticFunctions: true,
            suggestColumns: { source: 'select',  tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable WHERE | = \'bar\' AND "', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: ' = \'bar\' AND ',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['STRING'] },
            suggestColumns: { source: 'where', types: ['STRING'], tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a'}] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
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

      it('should suggest columns for "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }] }
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'dbOne' }, { name: 'bar' }] }] }
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
            suggestColumns: { tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable1' }] }] }
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'testTableA' }] }] }
          }
        });
        assertAutoComplete({
          beforeCursor: 'SELECT ttb.',
          afterCursor: ' FROM testTableA tta, testTableB ttb',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['*'],
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'testTableB' }] }] }
          }
        });
      });
    });

    describe('ORDER BY Clause', function () {
      it('should suggest keywords for "SELECT * FROM testTable GROUP BY a | LIMIT 10"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable GROUP BY a ',
          afterCursor: ' LIMIT 10',
          hasLocations: true,
          doesNotContainKeywords: ['LIMIT'],
          containsKeywords: ['ORDER BY'],
          containsColRefKeywords: true,
          expectedResult: {
            lowerCase: false,
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM testTable ORDER |"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable ORDER ',
          afterCursor: '',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['BY'],
            suggestOrderBys: { prefix: 'BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable ORDER BY |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable ORDER BY ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAnalyticFunctions: true,
            suggestColumns: { source: 'order by', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestOrderBys: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            suggestColumns: { source: 'order by', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] },
            suggestFunctions: {},
            suggestAnalyticFunctions: true,
            suggestOrderBys: { tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] },
            lowerCase: false
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
            suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'UNION']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo + |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo + ',
          afterCursor: '',
          dialect: 'generic',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'order by', types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo, |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo, ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAnalyticFunctions: true,
            suggestColumns: { source: 'order by', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo + baa ASC, |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo + baa ASC, ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAnalyticFunctions: true,
            suggestColumns: { source: 'order by', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo ASC, |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ASC, ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestAnalyticFunctions: true,
            suggestColumns: { source: 'order by', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
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
            suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'UNION']
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

      it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo LIMIT 10 |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo LIMIT 10 ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['UNION']
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
              suggestKeywords: ['ASC', 'DESC', 'NULLS FIRST', 'NULLS LAST', 'LIMIT', 'OFFSET', 'UNION']
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
              suggestKeywords: ['ASC', 'DESC', 'NULLS FIRST', 'NULLS LAST', 'LIMIT', 'OFFSET', 'UNION']
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
              suggestKeywords: ['ASC', 'DESC', 'NULLS FIRST', 'NULLS LAST', 'LIMIT', 'OFFSET', 'UNION']
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

    describe('CLUSTER BY, DISTRIBUTE BY and SORT BY', function () {
      describe('Hive specific', function () {
        it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC |', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['CLUSTER BY', 'DISTRIBUTE BY', 'LIMIT'],
            doesNotContainKeywords: ['SORT BY'],
            hasLocations: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC CLUSTER BY a |', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC CLUSTER BY a ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['LIMIT'],
            doesNotContainKeywords: ['DISTRIBUTE BY', 'SORT BY'],
            hasLocations: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC DISTRIBUTE BY a |', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC DISTRIBUTE BY a ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SORT BY', 'LIMIT'],
            doesNotContainKeywords: ['CLUSTER BY', 'DISTRIBUTE BY'],
            hasLocations: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC SORT BY a DESC |', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC SORT BY a DESC ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['LIMIT'],
            doesNotContainKeywords: ['CLUSTER BY', 'DISTRIBUTE BY', 'NULLS FIRST', 'SORT BY'],
            hasLocations: true,
            expectedResult: {
              lowerCase: false
            }
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
            suggestKeywords: ['BY'],
            suggestGroupBys: { prefix: 'BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest identifiers for "SELECT * FROM testTableA tta, testTableB GROUP BY |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY ',
          afterCursor: '',
          dialect: 'generic',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult : {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'group by', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }],
            suggestGroupBys: { tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] }
          }
        });
      });

      it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla, |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla, ',
          afterCursor: '',
          dialect: 'generic',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult : {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'group by', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
          }
        });
      });

      it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla+|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla+',
          afterCursor: '',
          dialect: 'generic',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult : {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'group by', types: ['NUMBER'], tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
          }
        });
      });

      it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla+foo, |, foo"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla, ',
          afterCursor: ', foo',
          dialect: 'generic',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult : {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'group by', tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }, { identifierChain: [{ name: 'testTableB' }] }] },
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM testTable GROUP BY |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable GROUP BY ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'group by', tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            suggestGroupBys: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM database_two.testTable GROUP BY |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { source: 'group by', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] },
            suggestGroupBys: { tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
          }
        });
      });

      describe('GROUPING SETS', function () {
        it('should handle "SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH CUBE;"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH CUBE;',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            noErrors: true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH ROLLUP;"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH ROLLUP;',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            noErrors: true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b GROUPING SETS ( (a, b), a, b, ( ) );"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b GROUPING SETS ( (a, b), a, b, ( ) );',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            noErrors: true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM database_two.testTable GROUP BY a, b |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            containsKeywords: ['GROUPING SETS', 'WITH CUBE', 'WITH ROLLUP', '<'],
            containsColRefKeywords: true,
            expectedResult: {
              lowerCase: false,
              suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] },
              colRef: { identifierChain: [{ name: 'database_two' }, { name: 'testTable' }, { name: 'b'}] }
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM database_two.testTable GROUP BY a, b WITH |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b WITH ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            containsKeywords: ['CUBE', 'ROLLUP'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "SELECT * FROM database_two.testTable GROUP BY a, b GROUPING |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b GROUPING ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            containsKeywords: ['SETS'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest columns for "SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS (|"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS (',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestColumns: { source: 'group by', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
            }
          });
        });

        it('should suggest columns for "SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS ((a, b), |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS ((a, b), ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            expectedResult: {
              lowerCase: false,
              suggestColumns: { source: 'group by', tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }] }
            }
          });
        });
      })
    });

    describe('HAVING clause', function () {
      describe('Hive specific', function () {
        it('should suggest identifiers for "SELECT COUNT(*) AS boo FROM testTable GROUP BY baa HAVING |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable GROUP BY baa HAVING ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestColumnAliases: [{ name: 'boo', types: ['BIGINT'] }]
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should suggest identifiers for "SELECT COUNT(*) AS boo FROM testTable GROUP BY baa HAVING |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable GROUP BY baa HAVING ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
              suggestColumnAliases: [{ name: 'boo', types: ['BIGINT'] }]
            }
          });
        });
      });
    });

    describe('LIMIT clause', function () {
      it('should not suggest anything for "SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT ',
          afterCursor: '',
          dialect: 'generic',
          hasLocations: true,
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      });

      describe('Hive specific', function () {
        it('should not suggest anything for "SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT ',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should not suggest columns for "SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['BIGINT'] }
            }
          });
        });
      });
    });

    describe('OFFSET clause', function () {
      describe('Impala specific', function () {
        it('should handle "SELECT COUNT(*) AS boo FROM testTable ORDER BY baa OFFSET 1;|"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable ORDER BY baa OFFSET 1; ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            noErrors: true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should not suggest columns for "SELECT COUNT(*) AS boo FROM testTable ORDER BY baa OFFSET |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable ORDER BY baa OFFSET ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestFunctions: { types: ['BIGINT'] }
            }
          });
        });

        it('should suggest keywords for "SELECT COUNT(*) AS boo FROM testTable ORDER BY baa LIMIT 10 |"', function() {
          assertAutoComplete({
            beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable ORDER BY baa LIMIT 10 ',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            containsKeywords: ['OFFSET'],
            expectedResult: {
              lowerCase: false
            }
          });
        });
      });
    });

    describe('TABLESAMPLE', function () {
      it('should handle "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 32 ON baa) baa JOIN bla;|', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 32 ON baa) baa JOIN bla;',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM boo |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['TABLESAMPLE', 'AS'],
          expectedResult: {
            lowerCase: false,
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'boo' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'boo' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'boo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'boo' }] }] }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM boo |, baa', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo ',
          afterCursor: ', baa',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['TABLESAMPLE', 'AS'],
          expectedResult: {
            lowerCase: false,
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'boo' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'boo' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'boo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'boo' }] }] }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (|', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo TABLESAMPLE (',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['BUCKET']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['OUT OF']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['OF']
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest columns for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 ON |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 ON ',
          afterCursor: '',
          dialect: 'hive',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }] }] }
          }
        });
      });
    });

    describe('UNION clause', function () {
      // TODO: Fix locations
      xit('should handle "SELECT * FROM (SELECT x FROM few_ints UNION ALL SELECT x FROM few_ints) AS t1 ORDER BY x;|', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT x FROM few_ints UNION ALL SELECT x FROM few_ints) AS t1 ORDER BY x;',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT key FROM (SELECT key FROM src ORDER BY key LIMIT 10)subq1 UNION SELECT key FROM (SELECT key FROM src1 ORDER BY key LIMIT 10)subq2;|', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT key FROM (SELECT key FROM src ORDER BY key LIMIT 10)subq1 UNION SELECT key FROM (SELECT key FROM src1 ORDER BY key LIMIT 10)subq2;',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT * FROM t1 UNION DISTINCT SELECT * FROM t2;|', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM t1 UNION DISTINCT SELECT * FROM t2;',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT * FROM t1 UNION SELECT * FROM t2;|', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM t1 UNION SELECT * FROM t2;',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM t1 UNION |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM t1 UNION ',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ALL', 'DISTINCT', 'SELECT']
          }
        });
      });

      it('should suggest tables for "SELECT * FROM t1 UNION ALL SELECT |', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM t1 UNION ALL SELECT ',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [] },
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
    });

    describe('WITH clause', function () {
      it('should handle "WITH q1 AS ( SELECT key FROM src WHERE something) SELECT * FROM q1;|', function () {
        assertAutoComplete({
          beforeCursor: 'WITH q1 AS ( SELECT key FROM src WHERE something) SELECT * FROM q1;',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "WITH q1 AS (SELECT * FROM src WHERE something), q2 AS (SELECT * FROM src s2 WHERE something) SELECT * FROM q1 UNION ALL SELECT * FROM q2;|', function () {
        assertAutoComplete({
          beforeCursor: 'WITH q1 AS (SELECT * FROM src WHERE something), q2 AS (SELECT * FROM src s2 WHERE something) SELECT * FROM q1 UNION ALL SELECT * FROM q2;',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "WITH t1 AS (SELECT 1) (WITH t2 AS (SELECT 2) SELECT * FROM t2) UNION ALL SELECT * FROM t1;|', function () {
        assertAutoComplete({
          beforeCursor: 'WITH t1 AS (SELECT 1) (WITH t2 AS (SELECT 2) SELECT * FROM t2) UNION ALL SELECT * FROM t1;',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "WITH t1 |', function () {
        assertAutoComplete({
          beforeCursor: 'WITH t1 ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest keywords for "WITH t1 AS (|', function () {
        assertAutoComplete({
          beforeCursor: 'WITH t1 AS (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest keywords for "WITH t1 AS (SELECT * FROM boo) |', function () {
        assertAutoComplete({
          beforeCursor: 'WITH t1 AS (SELECT * FROM boo) ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest identifiers for "WITH t1 AS (SELECT * FROM FOO) SELECT |', function () {
        assertAutoComplete({
          beforeCursor: 'WITH t1 AS (SELECT * FROM FOO) SELECT ',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestTables: { prependQuestionMark: true, prependFrom: true },
            suggestDatabases: { prependQuestionMark: true, prependFrom: true, appendDot:true },
            suggestCommonTableExpressions: [{ name: 't1', prependFrom: true, prependQuestionMark:true }]
          }
        });
      });

      it('should suggest identifiers for "WITH t1 AS (SELECT * FROM FOO) SELECT * FROM |', function () {
        assertAutoComplete({
          beforeCursor: 'WITH t1 AS (SELECT * FROM FOO) SELECT * FROM ',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestTables: { },
            suggestDatabases: { appendDot: true },
            suggestCommonTableExpressions: [{ name: 't1' }]
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
            suggestJoins: { prependJoin: false, joinType: 'JOIN', tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest joins for "SELECT * FROM testTable1 JOIN testTable2 JOIN |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN testTable2 JOIN ',
          afterCursor: '',
          hasLocations: true,
          dialect: 'generic',
          expectedResult: {
            lowerCase: false,
            suggestJoins: { prependJoin: false, joinType: 'JOIN', tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
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
            suggestTables: { identifierChain: [{ name: 'db1' }] }
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
            suggestTables: { identifierChain: [{ name: 'db1' }] }
          }
        });
      });

      it('should suggest join conditions for "SELECT testTable1.* FROM testTable1 JOIN testTable2 |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['ON'],
          expectedResult: {
            lowerCase: false,
            suggestJoinConditions: { prependOn: true, tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] }
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestFunctions: {},
            suggestJoinConditions: { prependOn: false, tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }],
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (|"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (| AND testTable1.testColumn1 = testTable2.testColumn3"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: ' AND testTable1.testColumn1 = testTable2.testColumn3',
          containsKeywords: ['CASE'],
          expectedResult: {
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 18 }, identifierChain: [{ name: 'testTable1' }]},
              { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 19, last_column: 20 }, tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 36}, identifierChain: [{ name: 'testTable1' }]},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 42, last_column: 52}, identifierChain: [{ name: 'testTable2' }]},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 62, last_column: 72 }, identifierChain: [{ name: 'testTable1' }]},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 73, last_column: 84}, identifierChain: [{ name: 'testTable1' }, { name: 'testColumn1'}] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 87, last_column: 97 }, identifierChain: [{ name: 'testTable2' }]},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 98, last_column: 109}, identifierChain: [{ name: 'testTable2' }, { name: 'testColumn3'}] }
            ],
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }],
            suggestFunctions: {},
            lowerCase: false
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
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable2' }]}] }
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
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }]}] }
          }
        });
      });

      it('should suggest identifiers for "select * from testTable1 join db.testTable2 on |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 join db.testTable2 on ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: true,
            suggestFunctions: {},
            suggestJoinConditions: { prependOn: false, tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'db' }, { name: 'testTable2' }] }] },
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'db' }, { name: 'testTable2' }] }] },
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }]
          }
        });
      });

      it('should suggest identifiers for "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            suggestValues: {},
            colRef: { identifierChain: [{ name: 'testTable1' }, { name: 'testColumn1'}] },
            suggestFunctions: { types: ['COLREF'] },
            suggestColumns: { types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'testTable2' }] }] },
            suggestIdentifiers: [{ name: 'testTable1.', type: 'table' }, { name: 'testTable2.', type: 'table' }],
            lowerCase: true
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
            colRef: { identifierChain: [{ name: 'testTable1' }, { name: 'testColumn1'}] },
            suggestColumns: { types: ['COLREF'], tables: [{ identifierChain: [{ name: 'testTable2' }]}] }
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
            suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }]}] }
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
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
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
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
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
            suggestKeywords: ['ON', 'FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER'],
            suggestJoinConditions: { prependOn: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }, { identifierChain: [{ name: 'table2' }], alias: 't2' }] }
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
            colRef: { identifierChain: [{ name: 'table1' }, { name: 'bla' }] }
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

      it('should suggest joins for "SELECT * FROM testTable1 |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['JOIN'],
          expectedResult: {
            lowerCase: false,
            suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
            suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'testTable1' }] }] }
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
              lowerCase: false,
              suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
              suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
              suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
              suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] }
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
              suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
              suggestKeywords: ['LATERAL VIEW', 'CROSS', 'FULL', 'FULL OUTER', 'LEFT', 'LEFT OUTER', 'LEFT SEMI', 'RIGHT', 'RIGHT OUTER']
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
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestColumns: { tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }, { identifierChain: [{ name: 'table2' }] }, { identifierChain: [{ name: 'table3' }] }, { identifierChain: [{ name: 'table4' }], alias: 't4' }] },
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
              suggestJoins: { prependJoin: false, joinType: 'LEFT OUTER JOIN', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
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
              suggestColumns: { source: 'where', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1'}, { identifierChain: [{ name: 'table2' }], alias: 't2' }] },
              suggestFilters: { tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }, { identifierChain: [{ name: 'table2' }], alias: 't2' }] },
              suggestIdentifiers: [{ name: 't1.', type: 'alias' }, { name: 't2.', type: 'alias' }]
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
              lowerCase: false,
              suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
              suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
              suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
              suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] }
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
              suggestJoins: { prependJoin: false, joinType: 'JOIN', tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
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
              lowerCase: false,
              suggestJoinConditions: { prependOn: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }, { identifierChain: [{ name: 'table2' }], alias: 't2' }] }
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
              suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
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
            containsKeywords: ['CASE'],
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestColumns: { tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1'}, { identifierChain: [{ name: 'table2' }]}, { identifierChain: [{ name: 'table3' }]}, { identifierChain: [{ name: 'table4' }], alias: 't4'}] },
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
              suggestJoins: { prependJoin: false, joinType: 'LEFT OUTER JOIN', tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }] },
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
            colRef: { identifierChain: [{ name: 'foo' }, { name: 'bar' }] },
            suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
            suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
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
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['COLREF'], tables: [{ identifierChain: [{ name: 'foo' }] }] },
            colRef: { identifierChain: [{ name: 'foo' }, { name: 'bar'}] }
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
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['COLREF'], tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'bar' }] }] },
            suggestIdentifiers: [{ name: 'foo.', type: 'table' }, { name: 'bar.', type: 'table' }],
            colRef: { identifierChain: [{ name: 'bar' }, {name: 'bla'}] }
          }
        });
      });

      it('should suggest values for "select * from foo, bar where bar.bla in (\'a\', |"', function() {
        assertAutoComplete({
          beforeCursor: 'select * from foo, bar where bar.bla in (\'a\', ',
          afterCursor: '',
          hasLocations: true,
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: true,
            suggestFunctions: { types: ['COLREF'] },
            suggestValues: {},
            suggestColumns: { source: 'where', types: ['COLREF'], tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'bar' }] }] },
            suggestIdentifiers: [{ name: 'foo.', type: 'table' }, { name: 'bar.', type: 'table' }],
            colRef: { identifierChain: [{ name: 'bar' }, {name: 'bla'}] }
          }
        });
      });

      it('should suggest tables for "SELECT * FROM foo WHERE bar IN (SELECT |"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT ',
          afterCursor: '',
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [] },
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


      it('should suggest tables for "SELECT * FROM bar WHERE foo NOT IN (SELECT |)"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM bar WHERE foo NOT IN (SELECT ',
          afterCursor: ')',
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          hasLocations: true,
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [] },
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
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [] },
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
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] },
            suggestColumns: { source: 'where', types: ['NUMBER'], tables: [{ identifierChain: [{ name: 't1' }] }, { identifierChain: [{ name: 't2' }], alias: 'ta2' }, { identifierChain: [{ name: 't3' }]}] },
            suggestIdentifiers: [{ name: 't1.', type: 'table' }, { name: 'ta2.', type: 'alias' }, { name: 't3.', type:'table' }],
            locations: [
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 39, last_column: 41}, identifierChain: [{ name: 't1' }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 43, last_column: 45}, identifierChain: [{ name: 't2' }] },
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 74, last_column: 76}, identifierChain: [{ name: 't3' }]},
              { type: 'column', location: { first_line: 1, last_line: 1, first_column: 77, last_column: 80}, identifierChain: [{ name: 't3' }, { name: 'foo'}]},
              { type: 'table', location: { first_line: 1, last_line: 1, first_column: 86, last_column: 88}, identifierChain: [{ name: 't3' }] }
            ]
          }
        });
      });

      it('should suggest identifiers for "SELECT | FROM testTable tt, (SELECT bla FROM abc WHERE foo > 1) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable tt, (SELECT bla FROM abc WHERE foo > 1) bar',
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            locations: [
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 14, last_column: 23}, identifierChain: [{ name: 'testTable' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 36, last_column: 39}, identifierChain: [{ name: 'abc' }, { name: 'bla'}]},
              {type: 'table', location: { first_line: 1, last_line: 1, first_column: 45, last_column: 48}, identifierChain: [{ name: 'abc' }]},
              {type: 'column', location: { first_line: 1, last_line: 1, first_column: 55, last_column: 58}, identifierChain: [{ name: 'abc' }, { name: 'foo'}]}
            ],
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }], alias: 'tt' }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'testTable' }], alias: 'tt' }, { identifierChain: [{ subQuery: 'bar' }] }] },
            suggestIdentifiers: [{ name: 'tt.', type: 'alias' }, { name: 'bar.', type: 'sub-query' }],
            subQueries: [{
              alias: 'bar',
              columns: [
                { identifierChain: [{ name: 'abc' }, { name: 'bla' }], type: 'COLREF'}
              ]
            }],
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "select | from (select id i, name as n, bla from foo) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from (select id i, name as n, bla from foo) bar',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 'bar' }] }] },
            subQueries: [{
              alias: 'bar',
              columns: [
                { alias: 'i', identifierChain: [{ name: 'foo' }, { name: 'id' }], type: 'COLREF' },
                { alias: 'n', identifierChain: [{ name: 'foo' }, { name: 'name' }], type: 'COLREF' },
                { identifierChain: [{ name: 'foo' }, { name: 'bla' }], type: 'COLREF' }
              ]
            }],
            suggestIdentifiers: [{ name: 'bar.', type: 'sub-query' }],
            lowerCase: true
          }
        });
      });

      it('should suggest sub-query columns for "SELECT bar.| FROM (SELECT col1, col2, (col3 + 1) col3alias FROM foo) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT bar.',
          afterCursor: ' FROM (SELECT col1, col2, (col3 + 1) col3alias FROM foo) bar',
          hasLocations: true,
          expectedResult: {
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 'bar' }] }] },
            suggestKeywords: ['*'],
            lowerCase: false,
            subQueries: [{
              alias: 'bar',
              columns: [
                { identifierChain: [{ name: 'foo' }, { name: 'col1' }], type: 'COLREF' },
                { identifierChain: [{ name: 'foo' }, { name: 'col2' }], type: 'COLREF' },
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 'bar' }] }] },
            suggestKeywords: ['*'],
            subQueries: [{
              alias: 'boo',
              columns: [{ identifierChain: [{ name: 'foo' }, { name: 'b' }], type: 'COLREF' }]
            }, {
              alias: 'bar',
              columns: [{ identifierChain: [{ name: 'bla' }, { name: 'a' }], type: 'COLREF' }]
            }],
            lowerCase: false
          }
        });
      });

      it('should suggest identifiers for "SELECT cos(| FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT cos(',
          afterCursor: ' FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar',
          hasLocations: true,
          dialect: 'generic',
          containsKeywords: ['CASE'],
          expectedResult: {
            suggestColumns: { source: 'select', types: ['T'], tables: [{ identifierChain: [{ subQuery: 'boo'}] }, { identifierChain: [{ subQuery: 'bar' }] }] },
            suggestIdentifiers: [{ name: 'boo.', type: 'sub-query' }, { name: 'bar.', type: 'sub-query' }],
            suggestFunctions: { types: ['T'] },
            subQueries: [{
              alias: 'boo',
              columns: [{ identifierChain: [{ name: 'foo' }, { name: 'b' }], type: 'COLREF' }]
            }, {
              alias: 'bar',
              columns: [{ identifierChain: [{ name: 'bla' }, { name: 'a' }], type: 'COLREF' }]
            }],
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "SELECT * FROM (SELECT |)"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ')',
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [] },
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
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          dialect: 'hive',
          expectedResult: {
            suggestAggregateFunctions: { tables: [
              { identifierChain: [{ name: 'someDb' }, { name: 'tableTwo' }], alias: 'tAlias' },
              { identifierChain: [{ name: 'tableThree' }] }
            ] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [
              { identifierChain: [{ subQuery: 'subQueryOne'}] },
              { identifierChain: [{ name: 'someDb' }, { name: 'tableTwo' }], alias: 'tAlias' },
              { identifierChain: [{ name: 'tableThree' }] },
              { identifierChain: [{ subQuery: 'subQueryTwo'}] }
            ]},
            subQueries: [{
              columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }],
              alias: 'subQueryOne'
            }, {
              columns: [{ tables: [{ identifierChain: [{ name: 't3' }]}, { alias:'t4', identifierChain: [{ name: 'table4' }] }] }],
              alias: 'subQueryTwo'
            }],
            suggestIdentifiers: [{ name: 'subQueryOne.', type: 'sub-query' }, { name: 'tAlias.', type: 'alias' }, { name: 'tableThree.', type: 'table' }, { name: 'subQueryTwo.', type: 'sub-query' }],
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT * FROM (SELECT | FROM tableOne) subQueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subQueryTwo;"', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ' FROM tableOne) subQueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subQueryTwo;',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableOne' }] }] }
          }
        });
      });

      it('should suggest columns for "SELECT | FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 'subQueryTwo'}] }] },
            suggestIdentifiers: [{ name: 'subQueryTwo.', type: 'sub-query' }],
            subQueries: [{
              alias: 'subQueryTwo',
              columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryOne' }] }] }],
              subQueries: [{
                alias: 'subQueryOne',
                columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
              }]
            }],
            lowerCase:false
          }
        });
      });

      it('should suggest columns for "SELECT | FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase:false,
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 'subQueryThree'}] }] },
            suggestIdentifiers: [{ name: 'subQueryThree.', type: 'sub-query' }],
            subQueries: [{
              alias: 'subQueryThree',
              columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryTwo' }] }] }],
              subQueries: [{
                alias: 'subQueryTwo',
                columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryOne' }] }] }],
                subQueries: [{
                  alias: 'subQueryOne',
                  columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
                }]
              }]
            }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM (SELECT | FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT ',
          afterCursor: ' FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase:false,
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 'subQueryTwo'}] }] },
            suggestIdentifiers: [{ name: 'subQueryTwo.', type: 'sub-query' }],
            subQueries: [{
              alias: 'subQueryTwo',
              columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryOne' }] }] }],
              subQueries: [{
                alias: 'subQueryOne',
                columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
              }]
            }]
          }
        });
      });

      it('should suggest columns for "SELECT * FROM (SELECT * FROM (SELECT | FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM (SELECT * FROM (SELECT ',
          afterCursor: ' FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
          hasLocations: true,
          containsKeywords: ['*', 'ALL', 'DISTINCT'],
          expectedResult: {
            lowerCase:false,
            suggestAggregateFunctions: { tables: [] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 'subQueryOne'}] }] },
            suggestIdentifiers: [{ name: 'subQueryOne.', type: 'sub-query' }],
            subQueries: [{
              alias: 'subQueryOne',
              columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
            }]
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 's2'}] }] },
            suggestKeywords: ['*'],
            subQueries: [{
              alias: 's2',
              columns: [
                { identifierChain: [{ subQuery: 's1' }, { name: 'a' }], type: 'COLREF'},
                { identifierChain: [{ subQuery: 's1' }, { name: 'bla' }], type: 'COLREF' }
              ],
              subQueries: [{
                alias: 's1',
                columns: [
                  { identifierChain: [{ name: 'testTable' }, { name: 'a' }], type: 'COLREF' },
                  { identifierChain: [{ name: 'testTable' }, { name: 'b' }], type: 'COLREF' },
                  { alias: 'bla', type: 'T' }
                ]
              }]
            }],
            lowerCase:false
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
            suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 's2'}] }] },
            subQueries: [{
              alias: 's2',
              columns: [
                { identifierChain: [{ subQuery: 's1' }, { name: 'a' }], type: 'COLREF'},
                { identifierChain: [{ subQuery: 's1' }, { name: 'bla' }], type: 'COLREF' }
              ],
              subQueries: [{
                alias: 's1',
                columns: [
                  { identifierChain: [{ name: 'testTable' }, { name: 'a' }], type: 'COLREF' },
                  { identifierChain: [{ name: 'testTable' }, { name: 'b' }], type: 'COLREF' },
                  { alias: 'bla', type: 'DOUBLE' }
                ]
              }]
            }]
          }
        });
      });
    });
  });
})();