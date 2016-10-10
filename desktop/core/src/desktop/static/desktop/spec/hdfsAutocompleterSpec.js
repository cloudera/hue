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
(function () {
  describe("hdfsAutocompleter.js", function() {
    var subject;

    var ajaxHelper = {
      responseForUrls: {}
    };

    var apiHelper = ApiHelper.getInstance({
      i18n: {},
      user: 'testUser'
    });

    var snippet = {
      type: ko.observable(),
      database: ko.observable("database_one"),
      isSqlDialect: function () { return true; },
      getContext: function () { return ko.mapping.fromJS(null) },
      getApiHelper: function () { return apiHelper }
    };


    beforeAll(function() {
      jasmine.addMatchers(SqlTestUtils.autocompleteMatcher);
      $.totalStorage = function(key, value) {
        return null;
      };

      spyOn($, "ajax").and.callFake(function(options) {
        var firstUrlPart = options.url.split("?")[0];
        var response;
        expect(ajaxHelper.responseForUrls[firstUrlPart]).toBeDefined("fake response for url " + firstUrlPart + " not found");
        response = ajaxHelper.responseForUrls[firstUrlPart];
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

    beforeEach(function() {
      subject = new HdfsAutocompleter({
        user: "testUser",
        snippet: snippet
      });
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
        serverResponses: {},
        beforeCursor: "",
        afterCursor: "",
        expectedSuggestions: []
      });
    });

    it("should return empty suggestions for bogus statements", function() {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: "qwerqwer'asdf/",
        afterCursor: "",
        expectedSuggestions: []
      });
    });

    it("should return empty suggestions for URIs with schemes ", function() {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: "://blabla",
        afterCursor: "",
        expectedSuggestions: []
      });
    });

    it("should return suggestions for root with '", function() {
      assertAutoComplete({
        serverResponses: {
          "/filebrowser/view=/" : {
            files: [
              { name: ".", type: "dir" },
              { name: "..", type: "dir" },
              { name: "var", type: "dir" },
              { name: "tmp_file", type: "file" }
            ]
          }
        },
        beforeCursor: "'/",
        afterCursor: "",
        expectedSuggestions: ["tmp_file", "var"]
      });
    });

    it("should return suggestions for root with \"", function() {
      assertAutoComplete({
        serverResponses: {
          "/filebrowser/view=/" : {
            files: [
              { name: ".", type: "dir" },
              { name: "..", type: "dir" },
              { name: "var", type: "dir" },
              { name: "tmp_file", type: "file" }
            ]
          }
        },
        beforeCursor: "\"/",
        afterCursor: "",
        expectedSuggestions: ["tmp_file", "var"]
      });
    });

    it("should return suggestions for non-root", function() {
      assertAutoComplete({
        serverResponses: {
          "/filebrowser/view=/foo/bar" : {
            files: [
              { name: ".", type: "dir" },
              { name: "..", type: "dir" },
              { name: "var", type: "dir" },
              { name: "tmp_file", type: "file" }
            ]
          }
        },
        beforeCursor: "'/foo/bar/",
        afterCursor: "",
        expectedSuggestions: ["tmp_file", "var"]
      });
    });
  });
})();