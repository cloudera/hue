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

describe("autocomplete.js", function() {

  var subject;

  var ajaxHelper = {
    responseForUrls: {}
  };

  beforeAll(function() {
    var totalStorage = {};
    $.totalStorage = function(key, value) {
      if (typeof value === "undefined") {
        return totalStorage[key];
      }
      totalStorage[key] = value;
      return value;
    };

    jasmine.addMatchers({
      toEqualAutocompleteValues : function() {
        return {
          compare: function(actualItems, expectedValues) {
            var itemIndex = {};

            if (actualItems.length !== expectedValues.length) {
              return { pass: false };
            }
            $.each(actualItems, function(i, item) {
              itemIndex[item.value] = true;
            });

            for (var i = 0; i < expectedValues.length; i++) {
              if (! itemIndex[expectedValues[i]]) {
                return { pass: false };
              }
            }
            return { pass: true };
          }
        }
      }
    });
    spyOn($, "ajax").and.callFake(function(options) {
      var firstUrlPart = options.url.split("?")[0];
      expect(ajaxHelper.responseForUrls[firstUrlPart]).toBeDefined("fake response for url " + firstUrlPart + " not found");
      options.success(ajaxHelper.responseForUrls[firstUrlPart]);
    });
  });

  beforeEach(function() {
    var options = {
      autocompleteBaseURL: "http://baseUrl/",
      autocompleteApp: "testApp",
      autocompleteUser: "testUser"
    };
    subject = new Autocomplete(options);
    subject.setDatabase("testDb");
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

  describe("table completion", function() {
    it("should suggest table names with no columns", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb" : {
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
          "http://baseUrl/testDb" : {
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
          "http://baseUrl/testDb" : {
            tables: ["testTable1", "testTable2"]
          }
        },
        beforeCursor: "SELECT *",
        afterCursor: "",
        expectedSuggestions: [" FROM testTable1", " FROM testTable2"]
      });
    });

    // TODO: Fix me
    xit("should suggest table names with started FROM", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb" : {
            tables: ["testTable1", "testTable2"]
          }
        },
        beforeCursor: "SELECT * fr",
        afterCursor: "",
        expectedSuggestions: [" FROM testTable1", " FROM testTable2"]
      });
    });

    it("should suggest table names after FROM", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb" : {
            tables: ["testTable1", "testTable2"]
          }
        },
        beforeCursor: "SELECT * FROM ",
        afterCursor: "",
        expectedSuggestions: ["testTable1", "testTable2"]
      });
    });

  });

  describe("field completion", function() {

    it("should suggest columns for table", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb/testTable" : {
            columns: ["testTableColumn1", "testTableColumn2"]
          }
        },
        beforeCursor: "SELECT ",
        afterCursor: " FROM testTable",
        expectedSuggestions: ["*", "testTableColumn1", "testTableColumn2"]
      });
    });

    // TODO: Fix me
    it("should suggest columns for table after WHERE", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb/testTable" : {
            columns: ["testTableColumn1", "testTableColumn2"]
          }
        },
        beforeCursor: "SELECT * FROM testTable WHERE ",
        afterCursor: "",
        expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
      });
    });

    // TODO: Fix me
    it("should suggest columns for table after ORDER BY ", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb/testTable" : {
            columns: ["testTableColumn1", "testTableColumn2"]
          }
        },
        beforeCursor: "SELECT * FROM testTable ORDER BY ",
        afterCursor: "",
        expectedSuggestions: ["testTableColumn1", "testTableColumn2"]
      });
    });

    // TODO: Fix me
    it("should suggest columns for table after ON ", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb/testTable1" : {
            columns: ["testTableColumn1", "testTableColumn2"]
          },
          "http://baseUrl/testDb/testTable2" : {
            columns: ["testTableColumn3", "testTableColumn4"]
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
          "http://baseUrl/testDb/testTable" : {
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
          "http://baseUrl/testDb/testTable" : {
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
        "http://baseUrl/testDb/testTableA": {
          columns: ["testTableColumn1", "testTableColumn2"]
        },
        "http://baseUrl/testDb/testTableB": {
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

    // TODO: Fix me
    xit("should suggest aliases", function() {
      assertAutoComplete({
        serverResponses: {
          "http://baseUrl/testDb/testTableA" : {
            columns: ["testTableColumn1", "testTableColumn2"]
          },
          "http://baseUrl/testDb/testTableB" : {
            columns: ["testTableColumn3", "testTableColumn4"]
          }
        },
        beforeCursor: "SELECT ",
        afterCursor: " FROM testTableA tta, testTableB ttb",
        expectedSuggestions: ["tta", "ttb"]
      });
    });


  });
});