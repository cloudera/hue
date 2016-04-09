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
  'desktop/js/assist/assistHelper',
  'desktop/spec/autocompleterTestUtils',
], function(ko, SqlAutocompleter, AssistHelper, testUtils) {
  describe("sqlAutocompleter.js", function() {
    var subject;

    var ajaxHelper = {
      responseForUrls: {}
    };

    var assistHelper = AssistHelper.getInstance({
      i18n: {},
      user: 'testUser'
    });

    var snippet = {
      type: ko.observable(),
      database: ko.observable("database_one"),
      isSqlDialect: function () { return true; },
      getContext: function () { return ko.mapping.fromJS(null) },
      getAssistHelper: function () { return assistHelper }
    };

    var changeType = function (newType, callback) {
      if (snippet.type() === newType) {
        callback();
        return;
      }
      snippet.type(newType);
      window.setTimeout(function() {
        callback();
      }, 0);

    };

    beforeAll(function() {
      jasmine.addMatchers(testUtils.autocompleteMatcher);
      $.totalStorage = function(key, value) {
        return null;
      };
      spyOn($, "ajax").and.callFake(function(options) {
        var firstUrlPart = options.url.split("?")[0];
        var response;
        if (firstUrlPart == "/notebook/api/autocomplete/") {
          response = {
            databases: ["database_one", "database_two"]
          };
        } else {
          expect(ajaxHelper.responseForUrls[firstUrlPart]).toBeDefined("fake response for url " + firstUrlPart + " not found");
          response = ajaxHelper.responseForUrls[firstUrlPart];
        }
        response.called = true;
        response.status = 0;
        if (typeof options.success === 'function') {
          options.success(response);
        }

        var functions = {
          fail: function() {
            return functions;
          },
          done: function(success) {
            success(response);
            return functions;
          },
          always: function() {
            return functions;
          }
        };

        return functions;
      });
    });

    afterEach(function() {
      $.each(ajaxHelper.responseForUrls, function(key, value) {
        expect(value.called).toEqual(true, key + " was never called");
      })
    });

    var getCompleter = function (options) {
      var langTools = ace.require("ace/ext/language_tools")
      langTools.textCompleter.setSqlMode(true)
      sqlAutocompleter = new SqlAutocompleter(options);
      return {
        autocomplete: function (before, after, callback) {
          var textCompleterCallback = function (values) {
            langTools.textCompleter.getCompletions(null, {
              getValue: function () {
                return before+after;
              },
              getTextRange: function () {
                return before;
              }
            }, before.length, null, function (ignore, textCompletions) {
              callback(textCompletions.concat(values))
            });
          }
          return sqlAutocompleter.autocomplete(before, after, textCompleterCallback);
        }
      };
    }

    beforeEach(function(done) {
      changeType("genericSqlType", done);
      subject = getCompleter({ snippet: snippet, optEnabled: false });
      ajaxHelper.responseForUrls = {};
    });

    var createCallbackSpyForValues = function(values, includeLocal) {
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

    var assertAutoComplete = function(testDefinition) {
      ajaxHelper.responseForUrls = testDefinition.serverResponses;
      var callback = createCallbackSpyForValues(testDefinition.expectedSuggestions, testDefinition.includeLocal);
      subject.autocomplete(testDefinition.beforeCursor, testDefinition.afterCursor, callback);
      expect(callback).toHaveBeenCalled();
    };

    it("should return empty suggestions for empty statement", function() {
      assertAutoComplete({
        serverResponses: { },
        beforeCursor: "",
        afterCursor: "",
        expectedSuggestions: []
      });
    });

    it("should return empty suggestions for bogus statement", function() {
      assertAutoComplete({
        serverResponses: { },
        beforeCursor: "foo",
        afterCursor: "bar",
        expectedSuggestions: []
      });
    });

    describe("database awareness", function() {
      it("should suggest databases after use", function () {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "USE ",
          afterCursor: "",
          expectedSuggestions: ["database_one", "database_two"]
        });
      });

      it("should use a use statement before the cursor if present", function () {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_two" : {
              tables_meta: [{ name: "otherTable1" }, { name: "otherTable2" }]
            }
          },
          beforeCursor: "USE database_two; \n\tSELECT ",
          afterCursor: "",
          expectedSuggestions: ["? FROM otherTable1", "? FROM otherTable2", "? FROM database_one.", "? FROM database_two."]
        });
      });

      it("should use the last use statement before the cursor if multiple are present", function () {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/closest_db" : {
              tables_meta: [{ name: "otherTable1" }, { name:  "otherTable2" }]
            }
          },
          beforeCursor: "USE other_db; USE closest_db; \n\tSELECT ",
          afterCursor: "",
          expectedSuggestions: ["? FROM otherTable1", "? FROM otherTable2", "? FROM database_one.", "? FROM database_two."]
        });
      });

      it("should use the use statement before the cursor if multiple are present after the cursor", function () {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/closest_db" : {
              tables_meta: [{ name: "otherTable1" }, { name: "otherTable2" }]
            }
          },
          beforeCursor: "USE other_db; USE closest_db; \n\tSELECT ",
          afterCursor: "USE some_other_db;",
          expectedSuggestions: ["? FROM otherTable1", "? FROM otherTable2", "? FROM database_one.", "? FROM database_two."]
        });
      });
    });

    describe("text completer", function() {
      it("should ignore line comments for local suggestions", function () {
        assertAutoComplete({
          serverResponses: { },
          includeLocal: true,
          beforeCursor: "-- line comment'\nSELECT * from testTable1;\n",
          afterCursor: "\n-- other line comment",
          expectedSuggestions: ["SELECT", "from", "testTable1"]
        });
      });

      it("should ignore multi-line comments for local suggestions", function () {
        assertAutoComplete({
          serverResponses: { },
          includeLocal: true,
          beforeCursor: "/* line 1\nline 2\n*/\nSELECT * from testTable1;\n",
          afterCursor: "",
          expectedSuggestions: ["SELECT", "from", "testTable1"]
        });
      });
    })

    describe("table completion", function() {
      it("should suggest table names with no columns", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "SELECT ",
          afterCursor: "",
          expectedSuggestions: ["? FROM testTable1", "? FROM testTable2", "? FROM database_one.", "? FROM database_two."]
        });
      });

      it("should follow keyword case for table name completion", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "select ",
          afterCursor: "",
          expectedSuggestions: ["? from testTable1", "? from testTable2", "? from database_one.", "? from database_two."]
        });
      });

      it("should suggest table names with *", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "SELECT *",
          afterCursor: "",
          expectedSuggestions: [" FROM testTable1", " FROM testTable2", " FROM database_one.", " FROM database_two."]
        });
      });

      it("should suggest table names with started FROM", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "SELECT * fr",
          afterCursor: "",
          expectedSuggestions: ["FROM testTable1", "FROM testTable2", "FROM database_one.", "FROM database_two."]
        });
      });

      it("should suggest table names after FROM", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "SELECT * FROM ",
          afterCursor: "",
          expectedSuggestions: ["testTable1", "testTable2", "database_one.", "database_two."]
        });
      });

      it("should suggest table names after FROM with started name", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "SELECT * FROM tes",
          afterCursor: "",
          expectedSuggestions: ["testTable1", "testTable2"]
        });
      });

      it("should suggest database names after FROM with started name", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "SELECT * FROM dat",
          afterCursor: "",
          expectedSuggestions: ["database_one.", "database_two."]
        });
      });

      it("should suggest table names after FROM with database reference", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_two" : {
              tables_meta: [{ name: "testTable3" }, { name: "testTable4" }]
            }
          },
          beforeCursor: "SELECT * FROM database_two.",
          afterCursor: "",
          expectedSuggestions: ["testTable3", "testTable4"]
        });
      });

      it("should suggest aliases", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT ",
          afterCursor: " FROM testTableA   tta, testTableB",
          expectedSuggestions: ["tta.", "testTableB."]
        });
      });

      it("should suggest aliases in GROUP BY", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT * FROM testTableA tta, testTableB GROUP BY ",
          afterCursor: "",
          expectedSuggestions: ["tta.", "testTableB."]
        });
      });

      it("should only suggest table aliases", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT ",
          afterCursor: " FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.array) ttaSum, testTableB ttb",
          expectedSuggestions: ["tta.", "ttb."]
        });
      });

      // TODO: Fix me...
      xit("should suggest aliases from nested selects", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT ",
          afterCursor: " FROM testTableA tta, testTableB ttb, (SELECT SUM(A*B) total FROM tta.array) ttaSum",
          expectedSuggestions: ["tta.", "ttb.", "ttaSum."]
        });
      });
    });

    describe("hive-specific stuff", function() {
      beforeEach(function(done) {
        changeType("hive", done);
        ajaxHelper.responseForUrls = {};
      });

      describe("HDFS autocompletion", function () {
        beforeEach(function() {
          subject = getCompleter({
            hdfsAutocompleter: {
              autocomplete: function(before, after, callback) {
                callback([
                  {
                    meta: "file",
                    score: 1000,
                    value: "file_one"
                  },
                  {
                    meta: "dir",
                    score: 999,
                    value: "folder_one"
                  }
                ])
              }
            },
            snippet: snippet,
            optEnabled: false
          });
        });

        it("should autocomplete hdfs paths in location references without initial /", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "CREATE EXTERNAL TABLE foo (id int) LOCATION '",
            afterCursor: "'",
            expectedSuggestions: ["/file_one", "/folder_one/"]
          });
        });

        it("should autocomplete hdfs paths in location references from root", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "CREATE EXTERNAL TABLE foo (id int) LOCATION '/",
            afterCursor: "'",
            expectedSuggestions: ["file_one", "folder_one/"]
          });
        });

        it("should autocomplete hdfs paths and suggest trailing apostrophe if empty after cursor", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "CREATE EXTERNAL TABLE foo (id int) LOCATION '/",
            afterCursor: "",
            expectedSuggestions: ["file_one'", "folder_one/"]
          });
        });

        it("should autocomplete hdfs paths in location references from inside a path", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "CREATE EXTERNAL TABLE foo (id int) LOCATION '/",
            afterCursor: "/bar'",
            expectedSuggestions: ["file_one", "folder_one"]
          });
        });
      });

      it("should suggest struct from map values", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "string", "name": "fieldB" },
                {"type": "struct",  "name": "fieldC", "fields": [
                  {"type": "string", "name": "fieldC_A" },
                  {"type": "boolean", "name": "fieldC_B"}
                ]}],
              type: "struct"
            }
          },
          beforeCursor: "SELECT testMap[\"anyKey\"].",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["fieldA", "fieldB", "fieldC"]
        });
      });

      it("should suggest struct from map values without a given key", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "string", "name": "fieldB" }
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT testMap[].",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["fieldA", "fieldB"]
        });
      });

      it("should suggest struct from structs from map values", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value/fieldC" : {
              fields: [
                {"type": "string", "name": "fieldC_A" },
                {"type": "boolean", "name": "fieldC_B"}
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT testMap[\"anyKey\"].fieldC.",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["fieldC_A", "fieldC_B"]
        });
      });

      it("should suggest struct from structs from arrays", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/database_one/testTable/testArray/item/fieldC" : {
              fields: [
                {"type": "string", "name": "fieldC_A" },
                {"type": "boolean", "name": "fieldC_B"}
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT testArray[1].fieldC.",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["fieldC_A", "fieldC_B"]
        });
      });

      it("should suggest structs from maps from arrays", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/database_one/testTable/testArray/item/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testArray/item/testMap/value" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "boolean", "name": "fieldB"}
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT testArray[1].testMap[\"key\"].",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["fieldA", "fieldB"]
        });
      });

      describe("lateral views", function() {
        it("should suggest structs from exploded item references to arrays", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/testArray/item": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT testItem.",
            afterCursor: " FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should suggest structs from multiple exploded item references to arrays", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/testArrayA/item": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT testItemA.",
            afterCursor: " FROM testTable" +
                         " LATERAL VIEW explode(testArrayA) explodedTableA AS testItemA" +
                         " LATERAL VIEW explode(testArrayB) explodedTableB AS testItemB",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should support table references as arguments of explode function", function() {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable2/testArrayB/item": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT\n testItemA,\n testItemB.",
            afterCursor: "\n\tFROM\n\t testTable2 tt2\n" +
            "\t LATERAL VIEW EXPLODE(tt2.testArrayA) explodedTableA AS testItemA\n" +
            "\t LATERAL VIEW EXPLODE(tt2.testArrayB) explodedTableB AS testItemB",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should suggest structs from exploded item references to exploded item references to arrays ", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/testArray1/item/testArray2/item": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT ta2_exp.",
            afterCursor: " FROM " +
            "   testTable tt" +
            " LATERAL VIEW explode(tt.testArray1) ta1 AS ta1_exp\n" +
            "   LATERAL VIEW explode(ta1_exp.testArray2)    ta2   AS  ta2_exp",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should suggest structs from references to exploded arrays", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/testArray/item": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT explodedTable.testItem.",
            afterCursor: " FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should suggest posexploded references to arrays", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/testArray/item": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT testValue.",
            afterCursor: " FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS (testIndex, testValue)",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should suggest exploded references to map values", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/testMap/value": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT testMapValue.",
            afterCursor: " FROM testTable LATERAL VIEW explode(testMap) AS (testMapKey, testMapValue)",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should suggest exploded references to map values from view references", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/testMap/value": {
                fields: [
                  {"type": "string", "name": "fieldA"},
                  {"type": "string", "name": "fieldB"}
                ],
                type: "struct"
              }
            },
            beforeCursor: "SELECT explodedMap.testMapValue.",
            afterCursor: " FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)",
            expectedSuggestions: ["fieldA", "fieldB"]
          });
        });

        it("should suggest references to exploded references from view reference", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "SELECT explodedMap.",
            afterCursor: " FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)",
            expectedSuggestions: ["testMapKey", "testMapValue"]
          });
        });

        it("should suggest references to exploded references", function () {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable" : {
                columns: ["testTableColumn1", "testTableColumn2"]
              }
            },
            beforeCursor: "SELECT ",
            afterCursor: " FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)",
            expectedSuggestions: ["*", "explodedMap", "testMapKey", "testMapValue", "testTableColumn1", "testTableColumn2"]
          });
        });
      });
    });

    describe("impala-specific stuff", function() {
      beforeEach(function (done) {
        changeType("impala", done);
        ajaxHelper.responseForUrls = {};
      });

      describe("HDFS autocompletion", function () {
        beforeEach(function() {
          subject = getCompleter({
            hdfsAutocompleter: {
              autocomplete: function(before, after, callback) {
                callback([
                  {
                    meta: "file",
                    score: 1000,
                    value: "file_one"
                  },
                  {
                    meta: "dir",
                    score: 999,
                    value: "folder_one"
                  }
                ])
              }
            },
            snippet: snippet,
            optEnabled: false
          });
        });

        it("should autocomplete hdfs paths in location references without initial /", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "LOAD DATA INPATH '",
            afterCursor: "'",
            expectedSuggestions: ["/file_one", "/folder_one/"]
          });
        });

        it("should autocomplete hdfs paths in location references from root", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "LOAD DATA INPATH '/",
            afterCursor: "'",
            expectedSuggestions: ["file_one", "folder_one/"]
          });
        });

        it("should autocomplete hdfs paths and suggest trailing apostrophe if empty after cursor", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "LOAD DATA INPATH '/",
            afterCursor: "",
            expectedSuggestions: ["file_one'", "folder_one/"]
          });
        });

        it("should autocomplete hdfs paths in location references from inside a path", function () {
          assertAutoComplete({
            serverResponses: {},
            beforeCursor: "LOAD DATA INPATH '/",
            afterCursor: "/bar' INTO TABLE foo",
            expectedSuggestions: ["file_one", "folder_one"]
          });
        });
      });

      it("should not suggest struct from map values with hive style syntax", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap[\"anyKey\"]" : {
              someResponse: true
            }
          },
          beforeCursor: "SELECT testMap[\"anyKey\"].",
          afterCursor: " FROM testTable",
          expectedSuggestions: []
        });
      });

      it("should suggest fields from nested structs", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/columnA" : {
              // Impala has to query every part for it's type, for hive '[' and ']' is used to indicate map or array.
            },
            "/notebook/api/autocomplete/database_one/testTable/columnA/fieldC" : {
              fields: [
                {"type": "string", "name": "fieldC_A" },
                {"type": "boolean", "name": "fieldC_B"}
              ],
              "type": "struct",
              "name": "fieldC"
            }
          },
          beforeCursor: "SELECT columnA.fieldC.",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["fieldC_A", "fieldC_B"]
        });
      });

      it("should suggest fields from map values of type structs", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "string", "name": "fieldB" }
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT tm.",
          afterCursor: " FROM testTable t, t.testMap tm;",
          expectedSuggestions: ["*", "key", "fieldA", "fieldB"]
        });
      });

      it("should suggest map value if type is scalar", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value" : {
              type: "int"
            }
          },
          beforeCursor: "SELECT tm.",
          afterCursor: " FROM testTable t, t.testMap tm;",
          expectedSuggestions: ["*", "key", "value"]
        });
      });

      it("should not suggest items from arrays if complex in select clause", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/database_one/testTable/testArray/item" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "string", "name": "fieldB" }
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT ta.",
          afterCursor: " FROM testTable t, t.testArray ta;",
          expectedSuggestions: ["*", "fieldA", "fieldB"]
        });
      });

      it("should suggest items from arrays if scalar in select clause", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/database_one/testTable/testArray/item" : {
              type: "int"
            }
          },
          beforeCursor: "SELECT ta.",
          afterCursor: " FROM testTable t, t.testArray ta;",
          expectedSuggestions: ["*", "items"]
        });
      });

      it("should suggest items from arrays if complex in from clause", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/database_one/testTable/testArray/item" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "string", "name": "fieldB" }
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT ta.* FROM testTable t, t.testArray ta WHERE ta.",
          afterCursor: "",
          expectedSuggestions: ["items", "fieldA", "fieldB"]
        });
      });


      it("should suggest columns from table refs in from clause", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT t.*  FROM testTable t, t.",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest map references in select", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT ",
          afterCursor: " FROM testTable t, t.testMap tm;",
          expectedSuggestions: ["t.", "tm."]
        });
      });

      it("should suggest fields with key and value in where clause from map values of type structs", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "string", "name": "fieldB" }
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.",
          afterCursor: "",
          expectedSuggestions: ["key", "value", "fieldA", "fieldB"]
        });
      });

      it("should suggest fields in where clause from map values of type structs", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value" : {
              fields: [
                {"type": "string", "name": "fieldA" },
                {"type": "string", "name": "fieldB" }
              ],
              type: "struct"
            }
          },
          beforeCursor: "SELECT tm.* FROM testTable t, t.testMap tm WHERE tm.value.",
          afterCursor: "",
          expectedSuggestions: ["fieldA", "fieldB"]
        });
      });

      it("should suggest values for map keys", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap/key" : {
              sample: ["value1", "value2"],
              type: "string"
            }
          },
          beforeCursor: "SELECT * FROM testTable t, t.testMap tm WHERE tm.key =",
          afterCursor: "",
          expectedSuggestions: ["t.", "tm.", "'value1'", "'value2'"]
        });
      });

      it("should suggest values for columns in conditions", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/id" : {
              sample: [1, 2, 3],
              type: "int"
            },
            "/notebook/api/sample/database_one/testTable/id": {
              status: 0,
              headers: [],
              rows: []
            }
          },
          beforeCursor: "SELECT * FROM testTable WHERE id =",
          afterCursor: "",
          expectedSuggestions: ["testTable", "1", "2", "3"]
        });
      });

      it("should suggest values from fields in map values in conditions", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/database_one/testTable/testMap/value/field" : {
              sample: [1, 2, 3],
              type: "int"
            }
          },
          beforeCursor: "SELECT * FROM testTable t, t.testMap m WHERE m.field = ",
          afterCursor: "",
          expectedSuggestions: ["t.", "m.", "1", "2", "3"]
        });
      })
    });

    describe("value completion", function () {
      it("should suggest numeric sample values for columns in conditions", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/sample/database_one/testTable/id": {
              status: 0,
              headers: ['id'],
              rows: [[1], [2], [3]]
            }
          },
          beforeCursor: "SELECT * FROM testTable WHERE id =",
          afterCursor: "",
          expectedSuggestions: ['1', '2', '3']
        });
      });

      it("should suggest string sample values for columns in conditions with started value", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/sample/database_one/testTable/string": {
              status: 0,
              headers: ['id'],
              rows: [['abc'], ['def'], ['ghi']]
            }
          },
          beforeCursor: "SELECT * FROM testTable WHERE string = 'd",
          afterCursor: "",
          expectedSuggestions: ["'abc'", "'def'", "'ghi'"]
        });
      });

      it("should suggest string sample values for columns in conditions with started value after AND", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/sample/database_one/testTable/string": {
              status: 0,
              headers: ['id'],
              rows: [['abc'], ['def'], ['ghi']]
            }
          },
          beforeCursor: "SELECT * FROM testTable WHERE id = 1 AND string =",
          afterCursor: "",
          expectedSuggestions: ["'abc'", "'def'", "'ghi'"]
        });
      });

      it("should suggest string sample values for columns in conditions with started value after OR", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/sample/database_one/testTable/string": {
              status: 0,
              headers: ['id'],
              rows: [['ab'], ['cd'], ['ef']]
            }
          },
          beforeCursor: "SELECT * FROM testTable WHERE id = 1 OR string =",
          afterCursor: "",
          expectedSuggestions: ["'ab'", "'cd'", "'ef'"]
        });
      });
    });

    describe("field completion", function() {

      it("should suggest columns for table", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT ",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table with database prefix", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_two/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT ",
          afterCursor: " FROM database_two.testTable",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after WHERE", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT * FROM testTable WHERE ",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after ORDER BY ", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT * FROM testTable ORDER BY ",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after ORDER BY with db reference", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_two/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT * FROM database_two.testTable ORDER BY ",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after GROUP BY ", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT * FROM testTable GROUP BY ",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after ON ", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable1" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after ON with database reference", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_two/testTable1" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table with table ref", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT testTable.",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns with table alias", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT tt.",
          afterCursor: " FROM testTable tt",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns with table alias from database reference", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_two/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT tt.",
          afterCursor: " FROM database_two.testTable tt",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns with multiple table aliases", function() {
        var serverResponses = {
          "/notebook/api/autocomplete/database_one/testTableA": {
            columns: ["testTableColumn1", "testTableColumn2"]
          },
          "/notebook/api/autocomplete/database_one/testTableB": {
            columns: ["testTableColumn3", "testTableColumn4"]
          }
        };
        assertAutoComplete({
          serverResponses: serverResponses,
          beforeCursor: "SELECT tta.",
          afterCursor: " FROM testTableA tta, testTableB ttb",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
        assertAutoComplete({
          serverResponses: serverResponses,
          beforeCursor: "SELECT ttb.",
          afterCursor: " FROM testTableA tta, testTableB ttb",
          expectedSuggestions: ["*", "testTableColumn3", "testTableColumn4"]
        });
      });

      describe("struct completion", function() {
        it("should suggest fields from columns that are structs", function() {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/columnA" : {
                fields: [
                  {"type": "string", "name": "fieldA" },
                  {"type": "boolean", "name": "fieldB" },
                  {"type": "struct",  "name": "fieldC", "fields": [
                    {"type": "string", "name": "fieldC_A" },
                    {"type": "boolean", "name": "fieldC_B"}
                  ]}
                ],
                "type": "struct",
                "name": "columnB"
              }
            },
            beforeCursor: "SELECT columnA.",
            afterCursor: " FROM testTable",
            expectedSuggestions: ["fieldA", "fieldB", "fieldC"]
          });
        });

        it("should suggest fields from nested structs", function() {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_one/testTable/columnA/fieldC" : {
                fields: [
                  {"type": "string", "name": "fieldC_A" },
                  {"type": "boolean", "name": "fieldC_B"}
                ],
                "type": "struct",
                "name": "fieldC"
              }
            },
            beforeCursor: "SELECT columnA.fieldC.",
            afterCursor: " FROM testTable",
            expectedSuggestions: ["fieldC_A", "fieldC_B"]
          });
        });

        it("should suggest fields from nested structs with database reference", function() {
          assertAutoComplete({
            serverResponses: {
              "/notebook/api/autocomplete/database_two/testTable/columnA/fieldC" : {
                fields: [
                  {"type": "string", "name": "fieldC_A" },
                  {"type": "boolean", "name": "fieldC_B"}
                ],
                "type": "struct",
                "name": "fieldC"
              }
            },
            beforeCursor: "SELECT columnA.fieldC.",
            afterCursor: " FROM database_two.testTable",
            expectedSuggestions: ["fieldC_A", "fieldC_B"]
          });
        });
      });
    });

    describe("joins", function() {

      it("should suggest tables to join with", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one" : {
              tables_meta: [{ name: "testTable1" }, { name: "testTable2" }]
            }
          },
          beforeCursor: "SELECT * FROM testTable1 JOIN ",
          afterCursor: "",
          expectedSuggestions: ["testTable1", "testTable2", "database_one.", "database_two."]
        });
      });

      it("should suggest table references in join condition if not already there", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (",
          afterCursor: "",
          expectedSuggestions: ["testTable1.", "testTable2."]
        });
      });

      it("should suggest table references in join condition if not already there for multiple conditions", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ",
          afterCursor: "",
          expectedSuggestions: ["testTable1.", "testTable2."]
        });
      });

      it("should suggest table references in join condition if not already there for multiple conditions", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (",
          afterCursor: " AND testTable1.testColumn1 = testTable2.testColumn3",
          expectedSuggestions: ["testTable1.", "testTable2."]
        });
      });

      it("should suggest field references in join condition if table reference is present", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable2" : {
              columns: ["testColumn3", "testColumn4"]
            }
          },
          beforeCursor: "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.",
          afterCursor: "",
          expectedSuggestions: ["testColumn3", "testColumn4"]
        });
      });

      it("should suggest field references in join condition if table reference is present from multiple tables", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable2" : {
              columns: ["testColumn3", "testColumn4"]
            }
          },
          beforeCursor: "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.",
          afterCursor: "",
          expectedSuggestions: ["testColumn3", "testColumn4"]
        });
      });

      it("should suggest field references in join condition if table reference is present from multiple tables for multiple conditions", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/database_one/testTable1" : {
              columns: ["testColumn1", "testColumn2"]
            }
          },
          beforeCursor: "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.",
          afterCursor: "",
          expectedSuggestions: ["testColumn1", "testColumn2"]
        });
      });
    })
  });
});