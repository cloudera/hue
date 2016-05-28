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

  describe('sql.js', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = function(testDefinition) {
      expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor, testDefinition.dialect)).toEqualDefinition(testDefinition);
    };

    it('should suggest keywords for empty statement', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [ 'SELECT', 'USE' ]
        }
      });
    });

    it('should suggest keywords after complete statement', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM bar;',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [ 'SELECT', 'USE' ]
        }
      });
    });

    it('should suggest keywords after complete statements', function() {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM bar;SELECT * FROM bar;',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [ 'SELECT', 'USE' ]
        }
      });
    });

    it('should suggest keywords for partial statement', function() {
      assertAutoComplete({
        beforeCursor: 'se',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [ 'SELECT', 'USE' ]
        }
      });
    });
    
    it('should return empty suggestions for bogus statement', function() {
      assertAutoComplete({
        beforeCursor: 'foo',
        afterCursor: 'bar',
        expectedResult: {
          lowerCase: false
        }
      });
    });

    describe('database awareness', function() {
      it('should suggest databases after use', function () {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: 'USE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: { }
          }
        });
      });

      it('should suggest databases after use with started identifier', function () {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: 'USE bla',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: { }
          }
        });
      });

      it('should use a use statement before the cursor if present', function () {
        assertAutoComplete({
          beforeCursor: 'USE database_two; \n\select ',
          afterCursor: '',
          expectedResult: {
            useDatabase: 'database_two',
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

      it('should use the last use statement before the cursor if multiple are present', function () {
        assertAutoComplete({
          beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
          afterCursor: '',
          expectedResult: {
            useDatabase: 'closest_db',
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

      it('should use the use statement before the cursor if multiple are present after the cursor', function () {
        assertAutoComplete({
          beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
          afterCursor: '; USE some_other_db;',
          expectedResult: {
            useDatabase: 'closest_db',
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
    });

    describe('text completer', function () {
      it('should ignore line comments for local suggestions', function () {
        assertAutoComplete({
          beforeCursor: '-- line comment\nSELECT * from testTable1;\n',
          afterCursor: '\n-- other line comment',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'SELECT', 'USE' ]
          }
        });
      });

      it('should ignore multi-line comments for local suggestions', function () {
        assertAutoComplete({
          beforeCursor: '/* line 1\nline 2\n*/\nSELECT * from testTable1;\n',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [ 'SELECT', 'USE' ]
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

      it('should suggest aliases', function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA   tta, testTableB',
          expectedResult: {
            lowerCase: false,
            suggestStar: true,
            suggestIdentifiers: ['tta.', 'testTableB.']
          }
        });
      });
      
      it('should suggest keywords after table references', function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['WHERE', 'GROUP BY', 'LIMIT']
          }
        });
      });

      it('should suggest aliases in GROUP BY', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY ',
          afterCursor: '',
          expectedResult : {
            lowerCase: false,
            suggestIdentifiers: ['tta.', 'testTableB.']
          }
        });
      });

      xit('should only suggest table aliases', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: ['tta.', 'ttb.']
          }
        });
      });

      // TODO: Fix me...
      xit('should suggest aliases from nested selects', function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, testTableB ttb, (SELECT SUM(A*B) total FROM tta.array) ttaSum',
          expectedSuggestions: ['tta.', 'ttb.', 'ttaSum.']
        });
      });
    });

    describe('hive-specific stuff', function() {
      describe('HDFS autocompletion', function () {

        xit("should autocomplete hdfs paths in location references without initial /", function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'',
            afterCursor: '\'',
            dialect: 'hive',
            expectedResult: {
              suggestHdfsFiles : { location: '' }
            }
          });
        });

        xit('should autocomplete hdfs paths in location references from root', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'/',
            afterCursor: '\'',
            expectedSuggestions: ['file_one', 'folder_one/']
          });
        });

        xit('should autocomplete hdfs paths and suggest trailing apostrophe if empty after cursor', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'/',
            afterCursor: '',
            expectedSuggestions: ['file_one\'', 'folder_one/']
          });
        });

        xit('should autocomplete hdfs paths in location references from inside a path', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'/',
            afterCursor: '/bar\'',
            expectedSuggestions: ['file_one', 'folder_one']
          });
        });
      });

      xit('should suggest struct from map values', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'string', 'name': 'fieldB' },
                {'type': 'struct',  'name': 'fieldC', 'fields': [
                  {'type': 'string', 'name': 'fieldC_A' },
                  {'type': 'boolean', 'name': 'fieldC_B'}
                ]}],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT testMap[\"anyKey\"].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldA', 'fieldB', 'fieldC']
        });
      });

      xit('should suggest struct from map values without a given key', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'string', 'name': 'fieldB' }
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT testMap[].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldA', 'fieldB']
        });
      });

      xit('should suggest struct from structs from map values', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value/fieldC' : {
              fields: [
                {'type': 'string', 'name': 'fieldC_A' },
                {'type': 'boolean', 'name': 'fieldC_B'}
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT testMap["anyKey"].fieldC.',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldC_A', 'fieldC_B']
        });
      });

      xit('should suggest struct from structs from arrays', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testArray' : {
              type: 'array'
            },
            '/notebook/api/autocomplete/database_one/testTable/testArray/item/fieldC' : {
              fields: [
                {'type': 'string', 'name': 'fieldC_A' },
                {'type': 'boolean', 'name': 'fieldC_B'}
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT testArray[1].fieldC.',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldC_A', 'fieldC_B']
        });
      });

      xit('should suggest structs from maps from arrays', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testArray' : {
              type: 'array'
            },
            '/notebook/api/autocomplete/database_one/testTable/testArray/item/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testArray/item/testMap/value' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'boolean', 'name': 'fieldB'}
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT testArray[1].testMap[\"key\"].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldA', 'fieldB']
        });
      });

      describe('lateral views', function() {
        xit('should suggest structs from exploded item references to arrays', function () {
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
            beforeCursor: 'SELECT testItem.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should suggest structs from multiple exploded item references to arrays', function () {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable/testArrayA/item': {
                fields: [
                  {'type': 'string', 'name': 'fieldA'},
                  {'type': 'string', 'name': 'fieldB'}
                ],
                type: 'struct'
              }
            },
            beforeCursor: 'SELECT testItemA.',
            afterCursor: ' FROM testTable' +
            ' LATERAL VIEW explode(testArrayA) explodedTableA AS testItemA' +
            ' LATERAL VIEW explode(testArrayB) explodedTableB AS testItemB',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should support table references as arguments of explode function', function() {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable2/testArrayB/item': {
                fields: [
                  {'type': 'string', 'name': 'fieldA'},
                  {'type': 'string', 'name': 'fieldB'}
                ],
                type: 'struct'
              }
            },
            beforeCursor: 'SELECT\n testItemA,\n testItemB.',
            afterCursor: '\n\tFROM\n\t testTable2 tt2\n' +
            '\t LATERAL VIEW EXPLODE(tt2.testArrayA) explodedTableA AS testItemA\n' +
            '\t LATERAL VIEW EXPLODE(tt2.testArrayB) explodedTableB AS testItemB',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should suggest structs from exploded item references to exploded item references to arrays ', function () {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable/testArray1/item/testArray2/item': {
                fields: [
                  {'type': 'string', 'name': 'fieldA'},
                  {'type': 'string', 'name': 'fieldB'}
                ],
                type: 'struct'
              }
            },
            beforeCursor: 'SELECT ta2_exp.',
            afterCursor: ' FROM ' +
            '   testTable tt' +
            ' LATERAL VIEW explode(tt.testArray1) ta1 AS ta1_exp\n' +
            '   LATERAL VIEW explode(ta1_exp.testArray2)    ta2   AS  ta2_exp',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should suggest structs from references to exploded arrays', function () {
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
            beforeCursor: 'SELECT explodedTable.testItem.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should suggest posexploded references to arrays', function () {
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
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should suggest exploded references to map values', function () {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable/testMap/value': {
                fields: [
                  {'type': 'string', 'name': 'fieldA'},
                  {'type': 'string', 'name': 'fieldB'}
                ],
                type: 'struct'
              }
            },
            beforeCursor: 'SELECT testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) AS (testMapKey, testMapValue)',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should suggest exploded references to map values from view references', function () {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable/testMap/value': {
                fields: [
                  {'type': 'string', 'name': 'fieldA'},
                  {'type': 'string', 'name': 'fieldB'}
                ],
                type: 'struct'
              }
            },
            beforeCursor: 'SELECT explodedMap.testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        xit('should suggest references to exploded references from view reference', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'SELECT explodedMap.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            expectedSuggestions: ['testMapKey', 'testMapValue']
          });
        });

        xit('should suggest references to exploded references', function () {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable' : {
                columns: ['testTableColumn1', 'testTableColumn2']
              }
            },
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            expectedSuggestions: ['*', 'explodedMap', 'testMapKey', 'testMapValue', 'testTableColumn1', 'testTableColumn2']
          });
        });
      });
    });

    describe('impala-specific stuff', function() {
      beforeEach(function (done) {
        changeType('impala', done);
        ajaxHelper.responseForUrls = {};
      });

      describe('HDFS autocompletion', function () {
        beforeEach(function() {
          subject = new SqlAutocompleter({
            hdfsAutocompleter: {
              autocomplete: function(before, after, callback) {
                callback([
                  {
                    meta: 'file',
                    score: 1000,
                    value: 'file_one'
                  },
                  {
                    meta: 'dir',
                    score: 999,
                    value: 'folder_one'
                  }
                ])
              }
            },
            snippet: snippet
          });
        });

        xit('should autocomplete hdfs paths in location references without initial /', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'LOAD DATA INPATH \'',
            afterCursor: '\'',
            expectedSuggestions: ['/file_one', '/folder_one/']
          });
        });

        xit('should autocomplete hdfs paths in location references from root', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'LOAD DATA INPATH \'/',
            afterCursor: '\'',
            expectedSuggestions: ['file_one', 'folder_one/']
          });
        });

        xit('should autocomplete hdfs paths and suggest trailing apostrophe if empty after cursor', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'LOAD DATA INPATH \'/',
            afterCursor: '',
            expectedSuggestions: ['file_one\'', 'folder_one/']
          });
        });

        xit('should autocomplete hdfs paths in location references from inside a path', function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: 'LOAD DATA INPATH \'/',
            afterCursor: '/bar\' INTO TABLE foo',
            expectedSuggestions: ['file_one', 'folder_one']
          });
        });
      });

      xit('should not suggest struct from map values with hive style syntax', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap[\"anyKey\"]' : {
              someResponse: true
            }
          },
          beforeCursor: 'SELECT testMap[\"anyKey\"].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: []
        });
      });

      xit('should suggest fields from nested structs', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/columnA' : {
              // Impala has to query every part for it's type, for hive '[' and ']' is used to indicate map or array.
            },
            '/notebook/api/autocomplete/database_one/testTable/columnA/fieldC' : {
              fields: [
                {'type': 'string', 'name': 'fieldC_A' },
                {'type': 'boolean', 'name': 'fieldC_B'}
              ],
              'type': 'struct',
              'name': 'fieldC'
            }
          },
          beforeCursor: 'SELECT columnA.fieldC.',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldC_A', 'fieldC_B']
        });
      });

      xit('should suggest fields from map values of type structs', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'string', 'name': 'fieldB' }
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT tm.',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          expectedSuggestions: ['*', 'key', 'fieldA', 'fieldB']
        });
      });

      xit('should suggest map value if type is scalar', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value' : {
              type: 'int'
            }
          },
          beforeCursor: 'SELECT tm.',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          expectedSuggestions: ['*', 'key', 'value']
        });
      });

      xit('should not suggest items from arrays if complex in select clause', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testArray' : {
              type: 'array'
            },
            '/notebook/api/autocomplete/database_one/testTable/testArray/item' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'string', 'name': 'fieldB' }
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT ta.',
          afterCursor: ' FROM testTable t, t.testArray ta;',
          expectedSuggestions: ['*', 'fieldA', 'fieldB']
        });
      });

      xit('should suggest items from arrays if scalar in select clause', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testArray' : {
              type: 'array'
            },
            '/notebook/api/autocomplete/database_one/testTable/testArray/item' : {
              type: 'int'
            }
          },
          beforeCursor: 'SELECT ta.',
          afterCursor: ' FROM testTable t, t.testArray ta;',
          expectedSuggestions: ['*', 'items']
        });
      });

      xit('should suggest items from arrays if complex in from clause', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testArray' : {
              type: 'array'
            },
            '/notebook/api/autocomplete/database_one/testTable/testArray/item' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'string', 'name': 'fieldB' }
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT ta.* FROM testTable t, t.testArray ta WHERE ta.',
          afterCursor: '',
          expectedSuggestions: ['items', 'fieldA', 'fieldB']
        });
      });

      xit('should suggest columns from table refs in from clause', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable' : {
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          },
          beforeCursor: 'SELECT t.*  FROM testTable t, t.',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      xit('should suggest map references in select', function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          expectedSuggestions: ['t.', 'tm.']
        });
      });

      xit('should suggest fields with key and value in where clause from map values of type structs', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'string', 'name': 'fieldB' }
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.',
          afterCursor: '',
          expectedSuggestions: ['key', 'value', 'fieldA', 'fieldB']
        });
      });

      xit('should suggest fields in where clause from map values of type structs', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value' : {
              fields: [
                {'type': 'string', 'name': 'fieldA' },
                {'type': 'string', 'name': 'fieldB' }
              ],
              type: 'struct'
            }
          },
          beforeCursor: 'SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.value.',
          afterCursor: '',
          expectedSuggestions: ['fieldA', 'fieldB']
        });
      });

      xit('should suggest values for map keys', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap/key' : {
              sample: ['value1', 'value2'],
              type: 'string'
            }
          },
          beforeCursor: 'SELECT * FROM testTable t, t.testMap tm WHERE tm.key =',
          afterCursor: '',
          expectedSuggestions: ['t.', 'tm.', '\'value1\'', '\'value2\'']
        });
      });

      xit('should suggest values for columns in conditions', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/id' : {
              sample: [1, 2, 3],
              type: 'int'
            }
          },
          beforeCursor: 'SELECT * FROM testTable WHERE id =',
          afterCursor: '',
          expectedSuggestions: ['testTable', '1', '2', '3']
        });
      });

      xit('should suggest values from fields in map values in conditions', function() {
        assertAutoComplete({
          serverResponses: {
            '/notebook/api/autocomplete/database_one/testTable/testMap' : {
              type: 'map'
            },
            '/notebook/api/autocomplete/database_one/testTable/testMap/value/field' : {
              sample: [1, 2, 3],
              type: 'int'
            }
          },
          beforeCursor: 'SELECT * FROM testTable t, t.testMap m WHERE m.field = ',
          afterCursor: '',
          expectedSuggestions: ['t.', 'm.', '1', '2', '3']
        });
      })
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

      describe('struct completion', function() {
        xit('should suggest fields from columns that are structs', function() {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable/columnA' : {
                fields: [
                  {'type': 'string', 'name': 'fieldA' },
                  {'type': 'boolean', 'name': 'fieldB' },
                  {'type': 'struct',  'name': 'fieldC', 'fields': [
                    {'type': 'string', 'name': 'fieldC_A' },
                    {'type': 'boolean', 'name': 'fieldC_B'}
                  ]}
                ],
                'type': 'struct',
                'name': 'columnB'
              }
            },
            beforeCursor: 'SELECT columnA.',
            afterCursor: ' FROM testTable',
            expectedSuggestions: ['fieldA', 'fieldB', 'fieldC']
          });
        });

        xit('should suggest fields from nested structs', function() {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_one/testTable/columnA/fieldC' : {
                fields: [
                  {'type': 'string', 'name': 'fieldC_A' },
                  {'type': 'boolean', 'name': 'fieldC_B'}
                ],
                'type': 'struct',
                'name': 'fieldC'
              }
            },
            beforeCursor: 'SELECT columnA.fieldC.',
            afterCursor: ' FROM testTable',
            expectedSuggestions: ['fieldC_A', 'fieldC_B']
          });
        });

        xit('should suggest fields from nested structs with database reference', function() {
          assertAutoComplete({
            serverResponses: {
              '/notebook/api/autocomplete/database_two/testTable/columnA/fieldC' : {
                fields: [
                  {'type': 'string', 'name': 'fieldC_A' },
                  {'type': 'boolean', 'name': 'fieldC_B'}
                ],
                'type': 'struct',
                'name': 'fieldC'
              }
            },
            beforeCursor: 'SELECT columnA.fieldC.',
            afterCursor: ' FROM database_two.testTable',
            expectedSuggestions: ['fieldC_A', 'fieldC_B']
          });
        });
      });
    });

    describe('joins', function() {

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

      it('should suggest table references in join condition if not already there', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: ['testTable1.', 'testTable2.']
          }
        });
      });

      it('should suggest table references in join condition if not already there for multiple conditions', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ',
          afterCursor: '',
          ignoreErrors: true, // Here the right parenthesis is missing and
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: ['testTable1.', 'testTable2.']
          }
        });
      });

      it('should suggest table references in join condition if not already there for multiple conditions', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: ' AND testTable1.testColumn1 = testTable2.testColumn3',
          expectedResult: {
            lowerCase: false,
            suggestIdentifiers: ['testTable1.', 'testTable2.']
          }
        });
      });

      it('should suggest field references in join condition if table reference is present', function() {
        assertAutoComplete({
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.',
          afterCursor: '',
          ignoreErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestColumns: { table: 'testTable2'}
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
    })
  });
});