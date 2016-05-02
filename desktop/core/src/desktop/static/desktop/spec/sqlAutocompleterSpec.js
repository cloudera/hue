// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
define([
  'knockout',
  'desktop/js/sqlAutocompleter',
  'desktop/js/apiHelper',
  'desktop/spec/autocompleterTestUtils'
], function (ko, SqlAutocompleter, ApiHelper, testUtils) {
  describe('sqlAutocompleter.js', function () {
    var apiHelper = ApiHelper.getInstance({
      i18n: {},
      user: 'testUser'
    });

    var langTools = ace.require('ace/ext/language_tools');

    beforeAll(function () {
      jasmine.addMatchers(testUtils.autocompleteMatcher);
      $.totalStorage = function (key, value) {
        return null;
      };
    });

    var getCompleter = function (options) {
      langTools.textCompleter.setSqlMode(true);
      var sqlAutocompleter = new SqlAutocompleter(options);
      return {
        autocomplete: function (before, after, callback) {
          var textCompleterCallback = function (values) {
            langTools.textCompleter.getCompletions(null, {
              getValue: function () {
                return before + after;
              },
              getTextRange: function () {
                return before;
              }
            }, before.length, null, function (ignore, textCompletions) {
              callback(textCompletions.concat(values))
            });
          };
          return sqlAutocompleter.autocomplete(before, after, textCompleterCallback);
        }
      };
    };

    var createCallbackSpyForValues = function (values, includeLocal) {
      return jasmine.createSpy('callback', function (value) {
        if (!includeLocal) {
          expect(value.filter(function (val) {
            return val.meta !== 'local';
          })).toEqualAutocompleteValues(values, includeLocal)
        } else {
          expect(value).toEqualAutocompleteValues(values, includeLocal)
        }
      }).and.callThrough();
    };

    var assertAutoComplete = function (testDefinition) {
      var snippet = {
        type: ko.observable(testDefinition.type ? testDefinition.type : 'genericSqlType'),
        database: ko.observable('database_one'),
        isSqlDialect: function () {
          return true;
        },
        getContext: function () {
          return ko.mapping.fromJS(null)
        },
        getApiHelper: function () {
          return apiHelper
        }
      };

      jasmine.Ajax.withMock(function() {
        jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\//).andReturn({
          status: 200,
          statusText: 'HTTP/1.1 200 OK',
          contentType: 'application/json;charset=UTF-8',
          responseText: ko.mapping.toJSON({
            status: 0,
            databases: ['database_one', 'database_two']
          })
        });
        testDefinition.serverResponses.forEach(function (responseDef) {
          jasmine.Ajax.stubRequest(responseDef.url).andReturn({
            status: 200,
            statusText: 'HTTP/1.1 200 OK',
            contentType: 'application/json;charset=UTF-8',
            responseText: responseDef.response ? ko.mapping.toJSON(responseDef.response) : ''
          });
        });
        var subject = getCompleter({
          hdfsAutocompleter: {
            autocomplete: function (before, after, callback) {
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
          snippet: snippet,
          optEnabled: false
        });
        var callback = createCallbackSpyForValues(testDefinition.expectedSuggestions, testDefinition.includeLocal);
        subject.autocomplete(testDefinition.beforeCursor, testDefinition.afterCursor, callback);
      });
    };

    it('should return empty suggestions for empty statement', function () {
      assertAutoComplete({
        type: 'hive',
        serverResponses: [],
        beforeCursor: '',
        afterCursor: '',
        expectedSuggestions: []
      });
    });

    it('should return empty suggestions for bogus statement', function () {
      assertAutoComplete({
        type: 'hive',
        serverResponses: [],
        beforeCursor: 'foo',
        afterCursor: 'bar',
        expectedSuggestions: []
      });
    });

    describe('database awareness', function () {
      it('should suggest databases after use', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'USE ',
          afterCursor: '',
          expectedSuggestions: ['database_one', 'database_two']
        });
      });

      it('should use a use statement before the cursor if present', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_two/,
            response: {
              status: 0,
              tables_meta: [{name: 'otherTable1'}, {name: 'otherTable2'}]
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/asdf/,
            response: {
              status: 0,
              tables_meta: [{name: 'otherTable1'}, {name: 'otherTable2'}]
            }
          }],
          beforeCursor: 'USE database_two; \n\tSELECT ',
          afterCursor: '',
          expectedSuggestions: ['? FROM otherTable1', '? FROM otherTable2', '? FROM database_one.', '? FROM database_two.']
        });
      });

      it('should use the last use statement before the cursor if multiple are present', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/closest_db/,
            response: {
              status: 0,
              tables_meta: [{name: 'otherTable1'}, {name: 'otherTable2'}]
            }
          }],
          beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
          afterCursor: '',
          expectedSuggestions: ['? FROM otherTable1', '? FROM otherTable2', '? FROM database_one.', '? FROM database_two.']
        });
      });

      it('should use the use statement before the cursor if multiple are present after the cursor', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/closest_db/,
            response: {
              status: 0,
              tables_meta: [{name: 'otherTable1'}, {name: 'otherTable2'}]
            }
          }],
          beforeCursor: 'USE other_db; USE closest_db; \n\tSELECT ',
          afterCursor: 'USE some_other_db;',
          expectedSuggestions: ['? FROM otherTable1', '? FROM otherTable2', '? FROM database_one.', '? FROM database_two.']
        });
      });
    });

    describe('text completer', function () {
      it('should ignore line comments for local suggestions', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          includeLocal: true,
          beforeCursor: '-- line comment\nSELECT * from testTable1;\n',
          afterCursor: '\n-- other line comment',
          expectedSuggestions: ['SELECT', 'from', 'testTable1']
        });
      });

      it('should ignore multi-line comments for local suggestions', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          includeLocal: true,
          beforeCursor: '/* line 1\nline 2\n*/\nSELECT * from testTable1;\n',
          afterCursor: '',
          expectedSuggestions: ['SELECT', 'from', 'testTable1']
        });
      });
    });

    describe('table completion', function () {
      it('should suggest table names with no columns', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'SELECT ',
          afterCursor: '',
          expectedSuggestions: ['? FROM testTable1', '? FROM testTable2', '? FROM database_one.', '? FROM database_two.']
        });
      });

      it('should follow keyword case for table name completion', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'select ',
          afterCursor: '',
          expectedSuggestions: ['? from testTable1', '? from testTable2', '? from database_one.', '? from database_two.']
        });
      });

      it('should suggest table names with *', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'SELECT *',
          afterCursor: '',
          expectedSuggestions: [' FROM testTable1', ' FROM testTable2', ' FROM database_one.', ' FROM database_two.']
        });
      });

      it('should suggest table names with started FROM', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'SELECT * fr',
          afterCursor: '',
          expectedSuggestions: ['FROM testTable1', 'FROM testTable2', 'FROM database_one.', 'FROM database_two.']
        });
      });

      it('should suggest table names after FROM', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'SELECT * FROM ',
          afterCursor: '',
          expectedSuggestions: ['testTable1', 'testTable2', 'database_one.', 'database_two.']
        });
      });

      it('should suggest table names after FROM with started name', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'SELECT * FROM tes',
          afterCursor: '',
          expectedSuggestions: ['testTable1', 'testTable2']
        });
      });

      it('should suggest database names after FROM with started name', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'SELECT * FROM dat',
          afterCursor: '',
          expectedSuggestions: ['database_one.', 'database_two.']
        });
      });

      it('should suggest table names after FROM with database reference', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_two/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable3'}, {name: 'testTable4'}]
            }
          }],
          beforeCursor: 'SELECT * FROM database_two.',
          afterCursor: '',
          expectedSuggestions: ['testTable3', 'testTable4']
        });
      });

      it('should suggest aliases', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA   tta, testTableB',
          expectedSuggestions: ['tta.', 'testTableB.']
        });
      });

      it('should suggest aliases in GROUP BY', function () {
        assertAutoComplete({
          type: 'hive',
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY ',
          afterCursor: '',
          expectedSuggestions: ['tta.', 'testTableB.']
        });
      });

      it('should only suggest table aliases', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb',
          expectedSuggestions: ['tta.', 'ttb.']
        });
      });

      // TODO: Fix me...
      xit('should suggest aliases from nested selects', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTableA tta, testTableB ttb, (SELECT SUM(A*B) total FROM tta.array) ttaSum',
          expectedSuggestions: ['tta.', 'ttb.', 'ttaSum.']
        });
      });
    });

    describe('hive-specific stuff', function () {

      describe('HDFS autocompletion', function () {
        it('should autocomplete hdfs paths in location references without initial /', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [],
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'',
            afterCursor: '\'',
            expectedSuggestions: ['/file_one', '/folder_one/']
          });
        });

        it('should autocomplete hdfs paths in location references from root', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [],
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'/',
            afterCursor: '\'',
            expectedSuggestions: ['file_one', 'folder_one/']
          });
        });

        it('should autocomplete hdfs paths and suggest trailing apostrophe if empty after cursor', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [],
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'/',
            afterCursor: '',
            expectedSuggestions: ['file_one\'', 'folder_one/']
          });
        });

        it('should autocomplete hdfs paths in location references from inside a path', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [],
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) LOCATION \'/',
            afterCursor: '/bar\'',
            expectedSuggestions: ['file_one', 'folder_one']
          });
        });
      });

      it('should suggest struct from map values', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'string', name: 'fieldB'},
                {
                  type: 'struct', name: 'fieldC', 'fields': [
                  {type: 'string', name: 'fieldC_A'},
                  {type: 'boolean', name: 'fieldC_B'}
                ]
                }],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT testMap[\'anyKey\'].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldA', 'fieldB', 'fieldC']
        });
      });

      it('should suggest struct from map values without a given key', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'string', name: 'fieldB'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT testMap[].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldA', 'fieldB']
        });
      });

      it('should suggest struct from structs from map values', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value\/fieldC/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldC_A'},
                {type: 'boolean', name: 'fieldC_B'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT testMap[\'anyKey\'].fieldC.',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldC_A', 'fieldC_B']
        });
      });

      it('should suggest struct from structs from arrays', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray/,
            response: {
              status: 0,
              type: 'array'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item\/fieldC/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldC_A'},
                {type: 'boolean', name: 'fieldC_B'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT testArray[1].fieldC.',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldC_A', 'fieldC_B']
        });
      });

      it('should suggest structs from maps from arrays', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray/,
            response: {
              status: 0,
              type: 'array'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item\/testMap\/value/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'boolean', name: 'fieldB'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT testArray[1].testMap[\'key\'].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldA', 'fieldB']
        });
      });

      describe('lateral views', function () {
        it('should suggest structs from exploded item references to arrays', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT testItem.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should suggest structs from multiple exploded item references to arrays', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArrayA\/item/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT testItemA.',
            afterCursor: ' FROM testTable' +
            ' LATERAL VIEW explode(testArrayA) explodedTableA AS testItemA' +
            ' LATERAL VIEW explode(testArrayB) explodedTableB AS testItemB',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should support table references as arguments of explode function', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable2\/testArrayB\/item/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT\n testItemA,\n testItemB.',
            afterCursor: '\n\tFROM\n\t testTable2 tt2\n' +
            '\t LATERAL VIEW EXPLODE(tt2.testArrayA) explodedTableA AS testItemA\n' +
            '\t LATERAL VIEW EXPLODE(tt2.testArrayB) explodedTableB AS testItemB',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should suggest structs from exploded item references to exploded item references to arrays ', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray1\/item\/testArray2\/item/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT ta2_exp.',
            afterCursor: ' FROM ' +
            '   testTable tt' +
            ' LATERAL VIEW explode(tt.testArray1) ta1 AS ta1_exp\n' +
            '   LATERAL VIEW explode(ta1_exp.testArray2)    ta2   AS  ta2_exp',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should suggest structs from references to exploded arrays', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT explodedTable.testItem.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should suggest posexploded references to arrays', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT testValue.',
            afterCursor: ' FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS (testIndex, testValue)',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should suggest exploded references to map values', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) AS (testMapKey, testMapValue)',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should suggest exploded references to map values from view references', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'string', name: 'fieldB'}
                ],
                type: 'struct'
              }
            }],
            beforeCursor: 'SELECT explodedMap.testMapValue.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            expectedSuggestions: ['fieldA', 'fieldB']
          });
        });

        it('should suggest references to exploded references from view reference', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [],
            beforeCursor: 'SELECT explodedMap.',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            expectedSuggestions: ['testMapKey', 'testMapValue']
          });
        });

        it('should suggest references to exploded references', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
              response: {
                status: 0,
                columns: ['testTableColumn1', 'testTableColumn2']
              }
            }],
            beforeCursor: 'SELECT ',
            afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)',
            expectedSuggestions: ['*', 'explodedMap', 'testMapKey', 'testMapValue', 'testTableColumn1', 'testTableColumn2']
          });
        });
      });
    });

    describe('impala-specific stuff', function () {
      describe('HDFS autocompletion', function () {
        it('should autocomplete hdfs paths in location references without initial /', function () {
          assertAutoComplete({
            type: 'impala',
            serverResponses: [],
            beforeCursor: 'LOAD DATA INPATH \'',
            afterCursor: '\'',
            expectedSuggestions: ['/file_one', '/folder_one/']
          });
        });

        it('should autocomplete hdfs paths in location references from root', function () {
          assertAutoComplete({
            type: 'impala',
            serverResponses: [],
            beforeCursor: 'LOAD DATA INPATH \'/',
            afterCursor: '\'',
            expectedSuggestions: ['file_one', 'folder_one/']
          });
        });

        it('should autocomplete hdfs paths and suggest trailing apostrophe if empty after cursor', function () {
          assertAutoComplete({
            type: 'impala',
            serverResponses: [],
            beforeCursor: 'LOAD DATA INPATH \'/',
            afterCursor: '',
            expectedSuggestions: ['file_one\'', 'folder_one/']
          });
        });

        it('should autocomplete hdfs paths in location references from inside a path', function () {
          assertAutoComplete({
            type: 'impala',
            serverResponses: [],
            beforeCursor: 'LOAD DATA INPATH \'/',
            afterCursor: '/bar\' INTO TABLE foo',
            expectedSuggestions: ['file_one', 'folder_one']
          });
        });
      });

      it('should not suggest struct from map values with hive style syntax', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\['anyKey'\]/,
            response: {
              status: 0,
              someResponse: true
            }
          }],
          beforeCursor: 'SELECT testMap[\'anyKey\'].',
          afterCursor: ' FROM testTable',
          expectedSuggestions: []
        });
      });

      it('should suggest fields from nested structs', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/columnA/,
            response: {
              status: 0
              // Impala has to query every part for it's type, for hive '[' and ']' is used to indicate map or array.
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/columnA\/fieldC/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldC_A'},
                {type: 'boolean', name: 'fieldC_B'}
              ],
              type: 'struct',
              name: 'fieldC'
            }
          }],
          beforeCursor: 'SELECT columnA.fieldC.',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['fieldC_A', 'fieldC_B']
        });
      });

      it('should suggest fields from map values of type structs', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'string', name: 'fieldB'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT tm.',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          expectedSuggestions: ['*', 'key', 'fieldA', 'fieldB']
        });
      });

      it('should suggest map value if type is scalar', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
            response: {
              status: 0,
              type: 'int'
            }
          }],
          beforeCursor: 'SELECT tm.',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          expectedSuggestions: ['*', 'key', 'value']
        });
      });

      it('should not suggest items from arrays if complex in select clause', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray/,
            response: {
              status: 0,
              type: 'array'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'string', name: 'fieldB'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT ta.',
          afterCursor: ' FROM testTable t, t.testArray ta;',
          expectedSuggestions: ['*', 'fieldA', 'fieldB']
        });
      });

      it('should suggest items from arrays if scalar in select clause', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray/,
            response: {
              status: 0,
              type: 'array'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item/,
            response: {
              status: 0,
              type: 'int'
            }
          }],
          beforeCursor: 'SELECT ta.',
          afterCursor: ' FROM testTable t, t.testArray ta;',
          expectedSuggestions: ['*', 'items']
        });
      });

      it('should suggest items from arrays if complex in from clause', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray/,
            response: {
              status: 0,
              type: 'array'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testArray\/item/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'string', name: 'fieldB'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT ta.* FROM testTable t, t.testArray ta WHERE ta.',
          afterCursor: '',
          expectedSuggestions: ['items', 'fieldA', 'fieldB']
        });
      });


      it('should suggest columns from table refs in from clause', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT t.*  FROM testTable t, t.',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest map references in select', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable t, t.testMap tm;',
          expectedSuggestions: ['t.', 'tm.']
        });
      });

      it('should suggest fields with key and value in where clause from map values of type structs', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'string', name: 'fieldB'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.',
          afterCursor: '',
          expectedSuggestions: ['key', 'value', 'fieldA', 'fieldB']
        });
      });

      it('should suggest fields in where clause from map values of type structs', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value/,
            response: {
              status: 0,
              fields: [
                {type: 'string', name: 'fieldA'},
                {type: 'string', name: 'fieldB'}
              ],
              type: 'struct'
            }
          }],
          beforeCursor: 'SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.value.',
          afterCursor: '',
          expectedSuggestions: ['fieldA', 'fieldB']
        });
      });

      it('should suggest values for map keys', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/key/,
            response: {
              status: 0,
              sample: ['value1', 'value2'],
              type: 'string'
            }
          }],
          beforeCursor: 'SELECT * FROM testTable t, t.testMap tm WHERE tm.key =',
          afterCursor: '',
          expectedSuggestions: ['t.', 'tm.', '\'value1\'', '\'value2\'']
        });
      });

      it('should suggest values for columns in conditions', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/id/,
            response: {
              status: 0,
              sample: [1, 2, 3],
              type: 'int'
            }
          }, {
            url: /.*\/notebook\/api\/sample\/database_one\/testTable\/id/,
            response: {
              status: 0,
              headers: [],
              rows: []
            }
          }],
          beforeCursor: 'SELECT * FROM testTable WHERE id =',
          afterCursor: '',
          expectedSuggestions: ['testTable', '1', '2', '3']
        });
      });

      it('should suggest values from fields in map values in conditions', function () {
        assertAutoComplete({
          type: 'impala',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap/,
            response: {
              status: 0,
              type: 'map'
            }
          }, {
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/testMap\/value\/field/,
            response: {
              status: 0,
              sample: [1, 2, 3],
              type: 'int'
            }
          }],
          beforeCursor: 'SELECT * FROM testTable t, t.testMap m WHERE m.field = ',
          afterCursor: '',
          expectedSuggestions: ['t.', 'm.', '1', '2', '3']
        });
      })
    });

    describe('value completion', function () {
      it('should suggest numeric sample values for columns in conditions', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/sample\/database_one\/testTable\/id/,
            response: {
              status: 0,
              headers: ['id'],
              rows: [[1], [2], [3]]
            }
          }],
          beforeCursor: 'SELECT * FROM testTable WHERE id =',
          afterCursor: '',
          expectedSuggestions: ['1', '2', '3']
        });
      });

      it('should suggest string sample values for columns in conditions with started value', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/sample\/database_one\/testTable\/string/,
            response: {
              status: 0,
              headers: ['id'],
              rows: [['abc'], ['def'], ['ghi']]
            }
          }],
          beforeCursor: 'SELECT * FROM testTable WHERE string = \'d',
          afterCursor: '',
          expectedSuggestions: ['\'abc\'', '\'def\'', '\'ghi\'']
        });
      });

      it('should suggest string sample values for columns in conditions with started value after AND', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/sample\/database_one\/testTable\/string/,
            response: {
              status: 0,
              headers: ['id'],
              rows: [['abc'], ['def'], ['ghi']]
            }
          }],
          beforeCursor: 'SELECT * FROM testTable WHERE id = 1 AND string =',
          afterCursor: '',
          expectedSuggestions: ['\'abc\'', '\'def\'', '\'ghi\'']
        });
      });

      it('should suggest string sample values for columns in conditions with started value after OR', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/sample\/database_one\/testTable\/string/,
            response: {
              status: 0,
              headers: ['id'],
              rows: [['ab'], ['cd'], ['ef']]
            }
          }],
          beforeCursor: 'SELECT * FROM testTable WHERE id = 1 OR string =',
          afterCursor: '',
          expectedSuggestions: ['\'ab\'', '\'cd\'', '\'ef\'']
        });
      });
    });

    describe('field completion', function () {
      it('should suggest columns for table', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for tables with where keyword in name', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testwhere/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM testwhere',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for tables with on keyword in name', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/teston/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM teston',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table with database prefix', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_two\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT ',
          afterCursor: ' FROM database_two.testTable',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table after WHERE', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT * FROM testTable WHERE ',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table after ORDER BY ', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT * FROM testTable ORDER BY ',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table after ORDER BY with db reference', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_two\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY ',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table after GROUP BY ', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT * FROM testTable GROUP BY ',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table after ON ', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable1/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table after ON with database reference', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_two\/testTable1/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.',
          afterCursor: '',
          expectedSuggestions: ['testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns for table with table ref', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT testTable.',
          afterCursor: ' FROM testTable',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns with table alias', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT tt.',
          afterCursor: ' FROM testTable tt',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns with table alias from database reference', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_two\/testTable/,
            response: {
              status: 0,
              columns: ['testTableColumn1', 'testTableColumn2']
            }
          }],
          beforeCursor: 'SELECT tt.',
          afterCursor: ' FROM database_two.testTable tt',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
      });

      it('should suggest columns with multiple table aliases', function () {
        var serverResponses = [{
          url: /.*\/notebook\/api\/autocomplete\/database_one\/testTableA/,
          response: {
            status: 0,
            columns: ['testTableColumn1', 'testTableColumn2']
          }
        }, {
          url: /.*\/notebook\/api\/autocomplete\/database_one\/testTableB/,
          response: {
            status: 0,
            columns: ['testTableColumn3', 'testTableColumn4']
          }
        }];
        assertAutoComplete({
          type: 'hive',
          serverResponses: serverResponses,
          beforeCursor: 'SELECT tta.',
          afterCursor: ' FROM testTableA tta, testTableB ttb',
          expectedSuggestions: ['*', 'testTableColumn1', 'testTableColumn2']
        });
        assertAutoComplete({
          type: 'hive',
          serverResponses: serverResponses,
          beforeCursor: 'SELECT ttb.',
          afterCursor: ' FROM testTableA tta, testTableB ttb',
          expectedSuggestions: ['*', 'testTableColumn3', 'testTableColumn4']
        });
      });

      describe('struct completion', function () {
        it('should suggest fields from columns that are structs', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/columnA/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldA'},
                  {type: 'boolean', name: 'fieldB'},
                  {
                    type: 'struct', name: 'fieldC', 'fields': [
                    {type: 'string', name: 'fieldC_A'},
                    {type: 'boolean', name: 'fieldC_B'}
                  ]
                  }
                ],
                type: 'struct',
                name: 'columnB'
              }
            }],
            beforeCursor: 'SELECT columnA.',
            afterCursor: ' FROM testTable',
            expectedSuggestions: ['fieldA', 'fieldB', 'fieldC']
          });
        });

        it('should suggest fields from nested structs', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable\/columnA\/fieldC/,
              response: {
                status: 0,
                fields: [
                  {type: 'string', name: 'fieldC_A'},
                  {type: 'boolean', name: 'fieldC_B'}
                ],
                type: 'struct',
                name: 'fieldC'
              }
            }],
            beforeCursor: 'SELECT columnA.fieldC.',
            afterCursor: ' FROM testTable',
            expectedSuggestions: ['fieldC_A', 'fieldC_B']
          });
        });

        it('should suggest fields from nested structs with database reference', function () {
          assertAutoComplete({
            type: 'hive',
            serverResponses: [{
              url: /.*\/notebook\/api\/autocomplete\/database_two\/testTable\/columnA\/fieldC/,
              response: {
                status: 0,
                fields: [
                  {'type': 'string', 'name': 'fieldC_A'},
                  {'type': 'boolean', 'name': 'fieldC_B'}
                ],
                type: 'struct',
                name: 'fieldC'
              }
            }],
            beforeCursor: 'SELECT columnA.fieldC.',
            afterCursor: ' FROM database_two.testTable',
            expectedSuggestions: ['fieldC_A', 'fieldC_B']
          });
        });
      });
    });

    describe('joins', function () {
      it('should suggest tables to join with', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one/,
            response: {
              status: 0,
              tables_meta: [{name: 'testTable1'}, {name: 'testTable2'}]
            }
          }],
          beforeCursor: 'SELECT * FROM testTable1 JOIN ',
          afterCursor: '',
          expectedSuggestions: ['testTable1', 'testTable2', 'database_one.', 'database_two.']
        });
      });

      it('should suggest table references in join condition if not already there', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: '',
          expectedSuggestions: ['testTable1.', 'testTable2.']
        });
      });

      it('should suggest table references in join condition if not already there for multiple conditions', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ',
          afterCursor: '',
          expectedSuggestions: ['testTable1.', 'testTable2.']
        });
      });

      it('should suggest table references in join condition if not already there for multiple conditions', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [],
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
          afterCursor: ' AND testTable1.testColumn1 = testTable2.testColumn3',
          expectedSuggestions: ['testTable1.', 'testTable2.']
        });
      });

      it('should suggest field references in join condition if table reference is present', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable2/,
            response: {
              status: 0,
              columns: ['testColumn3', 'testColumn4']
            }
          }],
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.',
          afterCursor: '',
          expectedSuggestions: ['testColumn3', 'testColumn4']
        });
      });

      it('should suggest field references in join condition if table reference is present from multiple tables', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable2/,
            response: {
              status: 0,
              columns: ['testColumn3', 'testColumn4']
            }
          }],
          beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.',
          afterCursor: '',
          expectedSuggestions: ['testColumn3', 'testColumn4']
        });
      });

      it('should suggest field references in join condition if table reference is present from multiple tables for multiple conditions', function () {
        assertAutoComplete({
          type: 'hive',
          serverResponses: [{
            url: /.*\/notebook\/api\/autocomplete\/database_one\/testTable1/,
            response: {
              status: 0,
              columns: ['testColumn1', 'testColumn2']
            }
          }],
          beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.',
          afterCursor: '',
          expectedSuggestions: ['testColumn1', 'testColumn2']
        });
      });
    })
  });
});