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
  'desktop/js/assistHelper',
  'desktop/spec/autocompleterTestUtils'
], function(ko, SqlAutocompleter, AssistHelper, testUtils) {
  describe("sqlAutocompleter.js", function() {
    var subject;

    var ajaxHelper = {
      responseForUrls: {}
    };

    var assistHelper = new AssistHelper({
      notebook: {
        getContext: function() { return ko.mapping.fromJS(null) }
      },
      activeDatabase: "testDb",
      user: "testUser"
    });

    var snippet = {
      type: ko.observable(),
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
      assistHelper.load(snippet, $.noop);
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
            databases: ["testDb"]
          };
        } else {
          expect(ajaxHelper.responseForUrls[firstUrlPart]).toBeDefined("fake response for url " + firstUrlPart + " not found");
          response = ajaxHelper.responseForUrls[firstUrlPart];
        }
        response.called = true;
        response.status = 0;
        options.success(response);
        return({
          fail: function() {
            return {
              always: $.noop
            }
          }
        })
      });
    });

    afterEach(function() {
      $.each(ajaxHelper.responseForUrls, function(key, value) {
        expect(value.called).toEqual(true, key + " was never called");
      })
    });

    beforeEach(function(done) {
      changeType("genericSqlType", done);
      subject = new SqlAutocompleter({ snippet: snippet });
      ajaxHelper.responseForUrls = {};
    });

    var createCallbackSpyForValues = function(values, name) {
      return jasmine.createSpy(name ? name : 'callback', function (value) {
        expect(value).toEqualAutocompleteValues(values)
      }).and.callThrough();
    };

    var assertAutoComplete = function(testDefinition) {
      ajaxHelper.responseForUrls = testDefinition.serverResponses;
      var callback = createCallbackSpyForValues(testDefinition.expectedSuggestions);
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

    describe("table completion", function() {
      it("should suggest table names with no columns", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb" : {
              tables: ["testTable1", "testTable2"]
            }
          },
          beforeCursor: "SELECT ",
          afterCursor: "",
          expectedSuggestions: ["? FROM testTable1", "? FROM testTable2"]
        });
      });

      it("should follow keyword case for table name completion", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb" : {
              tables: ["testTable1", "testTable2"]
            }
          },
          beforeCursor: "select ",
          afterCursor: "",
          expectedSuggestions: ["? from testTable1", "? from testTable2"]
        });
      });

      it("should suggest table names with *", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb" : {
              tables: ["testTable1", "testTable2"]
            }
          },
          beforeCursor: "SELECT *",
          afterCursor: "",
          expectedSuggestions: [" FROM testTable1", " FROM testTable2"]
        });
      });

      it("should suggest table names with started FROM", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb" : {
              tables: ["testTable1", "testTable2"]
            }
          },
          beforeCursor: "SELECT * fr",
          afterCursor: "",
          expectedSuggestions: ["FROM testTable1", "FROM testTable2"]
        });
      });

      it("should suggest table names after FROM", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb" : {
              tables: ["testTable1", "testTable2"]
            }
          },
          beforeCursor: "SELECT * FROM ",
          afterCursor: "",
          expectedSuggestions: ["testTable1", "testTable2"]
        });
      });

      it("should suggest aliases", function() {
        assertAutoComplete({
          serverResponses: {},
          beforeCursor: "SELECT ",
          afterCursor: " FROM testTableA   tta, testTableB",
          expectedSuggestions: ["testTableB.", "tta."]
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

      it("should suggest struct from map values", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testMap/value" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testMap/value" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testMap/value/fieldC" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/testDb/testTable/testArray/item/fieldC" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/testDb/testTable/testArray/item/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testArray/item/testMap/value" : {
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
              "/notebook/api/autocomplete/testDb/testTable/testArray/item": {
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
              "/notebook/api/autocomplete/testDb/testTable/testArrayA/item": {
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
              "/notebook/api/autocomplete/testDb/testTable2/testArrayB/item": {
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
              "/notebook/api/autocomplete/testDb/testTable/testArray1/item/testArray2/item": {
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
              "/notebook/api/autocomplete/testDb/testTable/testArray/item": {
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
              "/notebook/api/autocomplete/testDb/testTable/testArray/item": {
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
              "/notebook/api/autocomplete/testDb/testTable/testMap/value": {
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
              "/notebook/api/autocomplete/testDb/testTable/testMap/value": {
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
              "/notebook/api/autocomplete/testDb/testTable" : {
                columns: ["testTableColumn1", "testTableColumn2"]
              }
            },
            beforeCursor: "SELECT ",
            afterCursor: " FROM testTable LATERAL VIEW explode(testMap) explodedMap AS (testMapKey, testMapValue)",
            expectedSuggestions: ["*", "explodedMap", "testTableColumn1", "testTableColumn2", "testMapKey", "testMapValue"]
          });
        });
      });
    });

    describe("impala-specific stuff", function() {
      beforeEach(function (done) {
        changeType("impala", done);
        ajaxHelper.responseForUrls = {};
      });

      it("should not suggest struct from map values with hive style syntax", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb/testTable/testMap[\"anyKey\"]" : {
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
            "/notebook/api/autocomplete/testDb/testTable/columnA" : {
              // Impala has to query every part for it's type, for hive '[' and ']' is used to indicate map or array.
            },
            "/notebook/api/autocomplete/testDb/testTable/columnA/fieldC" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testMap/value" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testMap/value" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/testDb/testTable/testArray/item" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/testDb/testTable/testArray/item" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testArray" : {
              type: "array"
            },
            "/notebook/api/autocomplete/testDb/testTable/testArray/item" : {
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
            "/notebook/api/autocomplete/testDb/testTable" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testMap/value" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testMap" : {
              type: "map"
            },
            "/notebook/api/autocomplete/testDb/testTable/testMap/value" : {
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
            "/notebook/api/autocomplete/testDb/testTable/testMap/key" : {
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
            "/notebook/api/autocomplete/testDb/testTable/id" : {
              sample: [1, 2, 3],
              type: "int"
            }
          },
          beforeCursor: "SELECT * FROM testTable WHERE id =",
          afterCursor: "",
          expectedSuggestions: ["testTable", "1", "2", "3"]
        });
      });
    });

    describe("field completion", function() {

      it("should suggest columns for table", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT ",
          afterCursor: " FROM testTable",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after WHERE", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb/testTable" : {
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
            "/notebook/api/autocomplete/testDb/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT * FROM testTable ORDER BY ",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table after ON ", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb/testTable1" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.",
          afterCursor: "",
          expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns for table with table ref", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb/testTable" : {
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
            "/notebook/api/autocomplete/testDb/testTable" : {
              columns: ["testTableColumn1", "testTableColumn2"]
            }
          },
          beforeCursor: "SELECT tt.",
          afterCursor: " FROM testTable tt",
          expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
        });
      });

      it("should suggest columns with multiple table aliases", function() {
        var serverResponses = {
          "/notebook/api/autocomplete/testDb/testTableA": {
            columns: ["testTableColumn1", "testTableColumn2"]
          },
          "/notebook/api/autocomplete/testDb/testTableB": {
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
              "/notebook/api/autocomplete/testDb/testTable/columnA" : {
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
              "/notebook/api/autocomplete/testDb/testTable/columnA/fieldC" : {
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
      });
    });

    describe("joins", function() {

      it("should suggest tables to join with", function() {
        assertAutoComplete({
          serverResponses: {
            "/notebook/api/autocomplete/testDb" : {
              tables: ["testTable1", "testTable2"]
            }
          },
          beforeCursor: "SELECT * FROM testTable1 JOIN ",
          afterCursor: "",
          expectedSuggestions: ["testTable1", "testTable2"]
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
            "/notebook/api/autocomplete/testDb/testTable2" : {
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
            "/notebook/api/autocomplete/testDb/testTable2" : {
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
            "/notebook/api/autocomplete/testDb/testTable1" : {
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