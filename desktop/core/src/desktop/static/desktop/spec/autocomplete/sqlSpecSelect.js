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

    it('should suggest keywords for empty statement', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords after SELECT * ', function() {
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

    it('should suggest keywords after SELECT SelectList ', function() {
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
          }
        }
      });
    });

    it('should suggest keywords after SELECT SelectList FROM TablePrimary ', function() {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']
        }
      });
    });

    it('should suggest keywords after SELECT SelectList FROM TablePrimary ', function() {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN', 'WHERE']
        }
      });
    });

    it('should suggest keywords after SELECT SelectList FROM TablePrimary WHERE SearchCondition ', function () {
      assertAutoComplete({
        beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP BY', 'LIMIT', 'ORDER BY']
        }
      });
    });

    describe('Hive specific', function () {
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
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
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

      it('should suggest keywords after SELECT SelectList FROM TablePrimary WHERE SearchCondition ', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['GROUP BY', 'LIMIT', 'ORDER BY']
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
    });

    describe('table completion', function() {
      it('should suggest tables after SELECT', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
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

      it('should follow keyword case for table name completion', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: '',
          expectedResult: {
            lowerCase: true,
            suggestStar: true,
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

      it('should suggest table names with *', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * ',
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

      it('should suggest table names with started FROM', function() {
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

      it('should suggest table names after FROM', function() {
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

      it('should suggest database or table names after FROM with started name', function() {
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

      it('should suggest database or table names after FROM with started backticked name', function() {
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

      it('should suggest table names after FROM with database reference', function() {
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

      it('should suggest table names after FROM with backticked database reference', function() {
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

      it('should suggest table names after FROM with partial backticked table reference', function() {
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

      it('should suggest aliases', function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA   tta, testTableB',
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'testTableB.', type: 'table' }]
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

      // TODO: fix me
      xit('should suggest table aliases and select aliases', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
            suggestIdentifiers: [{ name: 'tta.', type: 'alias' }, { name: 'ttaSum', type: 'alias' }, { name: 'ttb.', type: 'alias' }]
          }
        });
      });
    });

    describe('functions', function () {
      xit('should suggest fields in functions', function () {
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

      xit('should suggest fields in functions after operators', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT id, SUM(a * ',
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

    describe('Hive specific', function() {
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
            }
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
            }
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
            }
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
            }
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
            }
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
            expectedResult: {
              lowerCase: false,
              suggestStar: true, // TODO: Verify that this is true
              suggestColumns: {
                table: 'testTable'
              },
              suggestIdentifiers: [{ name: 'explodedTable.', type: 'alias' }, { name: 'testItem', type: 'alias' }]
            }
          });
        });

        xit('should suggest columns in explode', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        });

        xit('should suggest columns in explode for structs', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(a.b.',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              suggestColumns: {
                table: 'testTable',
                identifierChain: [ { name: 'a' }, { name: 'b' }]
              }
            }
          });
        });

        xit('should suggest columns in posexplode', function () {
          assertAutoComplete({
            beforeCursor: 'SELECT * FROM testTable LATERAL VIEW posexplode(',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
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
            expectedResult: {
              lowerCase: false,
              suggestStar: true, // TODO: Verify that this is true
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
              suggestStar: true, // TODO: Verify that this is true
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
              suggestStar: true, // TODO: Verify that this is true
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
              suggestStar: true, // TODO: Verify that this is true
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
              suggestStar: true, // TODO: Verify that this is true
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
              }
            }
          });
        });

        it('should suggest posexploded references to arrays', function () {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable/testArray/item': {
                fields: [
                  {'type': 'string', 'name': 'fieldA'},
                  {'type': 'string', 'name': 'fieldB'}
                ],
                type: 'struct'
              }
            },
            beforeCursor: 'SELECT testValue.',
            afterCursor: ' FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS (testIndex, testValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestStar: true, // TODO: Verify that this is true
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
              suggestStar: true, // TODO: Verify that this is true
              suggestColumns: {
                table: 'testTable',
                identifierChain: [{ name: 'testMap' }, { name: 'value' }]
              }
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
              }
            }
          });
        });

        it('should suggest references to exploded references from view reference', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'SELECT explodedMap.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestStar: true, // TODO: Check if really true
              suggestIdentifiers: [{ name: 'testMapKey', type: 'alias' }, { name: 'testMapValue', type: 'alias' }]
            }
          });
        });

        it('should suggest references to exploded references', function () {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable' : {
                columns: ['testTableColumn1', 'testTableColumn2']
              }
            },
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestStar: true, // TODO: Check if really true
              suggestIdentifiers: [{ name: 'explodedMap.', type: 'alias' }, { name: 'testMapKey', type: 'alias' }, { name: 'testMapValue', type: 'alias' }],
              suggestColumns: {
                table: 'testTable'
              }
            }
          });
        });
      });
    });

    describe('Impala specific', function() {
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
            }
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
            }
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
            }
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
            suggestStar: true,
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
            suggestStar: true,
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
          expectedResult: {
            lowerCase: false,
            suggestStar: true, // TODO: Check if really so
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

    describe('Hive and Impla struct completion', function() {
      it('should suggest fields from columns that are structs', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT columnA.',
          afterCursor: ' FROM testTable',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestStar: true, // TODO: Verify that this is true
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
            }
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
            }
          }
        });
      });
    });

    describe('value completion', function() {
      it('should suggest values for columns in conditions', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE id =',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'id' }]
            }
          }
        });
      });

      it('should suggest values for columns in conditions', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestValues: {
              table: 'testTable',
              identifierChain: [{ name: 'd' }]
            }
          }
        });
      });
    });

    describe('field completion', function() {
      it('should suggest columns for table', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest multiple columns for table', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a, ',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestStar: true, // TODO: Correct?
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest multiple columns for table without space', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT a,',
          afterCursor: ' FROM testTable',
          expectedResult: {
            lowerCase: false,
            suggestStar: true, // TODO: Correct?
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for tables with where keyword in name', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testwhere',
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
            suggestColumns: { table: 'testwhere' }
          }
        });
      });

      it('should suggest columns for tables with on keyword in name', function () {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM teston',
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
            suggestColumns: { table: 'teston' }
          }
        });
      });

      it('should suggest columns for table with database prefix', function() {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from database_two.testTable',
          expectedResult: {
            lowerCase: true,
            suggestStar: true,
            suggestColumns: { table: 'testTable', database: 'database_two' }
          }
        });
      });

      it('should suggest columns for table with grave accents', function () {
        assertAutoComplete({
          beforeCursor: 'select ',
          afterCursor: ' from `database one`.`test table`',
          expectedResult: {
            lowerCase: true,
            suggestStar: true,
            suggestColumns: { table: 'test table', database: 'database one' }
          }
        });
      });

      it('should suggest columns for table after WHERE', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

      it('should suggest columns for table after WHERE with partial column', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable WHERE a',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable' }
          }
        });
      });

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

      it('should suggest columns for table after ORDER BY ', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable' : {
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          },
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
            suggestStar: true,
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
            suggestStar: true,
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
            suggestStar: true,
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
            suggestStar: true,
            suggestColumns: { table: 'testTableA' }
          }
        });
        assertAutoComplete({
          beforeCursor: 'SELECT ttb.',
          afterCursor: ' FROM testTableA tta, testTableB ttb',
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
            suggestColumns: { table: 'testTableB' }
          }
        });
      });
    });

    describe('joins', function() {
      it('should handle complete JOIN statement', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTable1 JOIN db1.table2; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

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
            suggestKeywords: ['ANTI', 'SEMI', 'OUTER']
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
              suggestKeywords: ['SEMI', 'OUTER']
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
              suggestKeywords: ['ANTI', 'SEMI', 'OUTER']
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
              suggestKeywords: ['ANTI', 'SEMI', 'OUTER']
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
      })
    })
  });
});