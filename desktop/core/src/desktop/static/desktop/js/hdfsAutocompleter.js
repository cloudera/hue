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

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define([], factory);
  } else {
    root.HdfsAutocompleter = factory();
  }
}(this, function () {

  var BASE_PATH = "/filebrowser/view=";
  var PARAMETERS = "?pagesize=100&format=json";

  /**
   * @param options {object}
   *
   * @constructor
   */
  function HdfsAutocompleter(options) {
    var self = this;
  }

  HdfsAutocompleter.prototype.fetchAlternatives = function (pathParts, success, error, editor) {
    var self = this;
    if (editor) {
      editor.showSpinner();
    }

    $.ajax({
      dataType: "json",
      url: BASE_PATH + "/" + pathParts.join("/") + PARAMETERS,
      success: function (data) {
        if (editor) {
          editor.hideSpinner();
        }
        if (! data.error) {
          success(self.extractFields(data, pathParts.length > 0));
        } else {
          error();
        }
      }
    }).fail(function () {
      if (editor) {
        editor.hideSpinner();
      }
      error();
    });
  };

  HdfsAutocompleter.prototype.extractFields = function (data, includeParent) {
    var files = $.map(data.files, function (file) {
      return {
        name: file.name,
        type: file.type
      }
    });

    files.sort(function (a, b) {
      return a.name.localeCompare(b.name);
    });

    var result = [];
    files.forEach(function(field, idx) {
      if (field.name !== '..' && field.name !== '.') {
        result.push({
          value: field.name,
          score: 1000 - idx,
          meta: field.type
        });
      }
    });
    return result;
  };

  HdfsAutocompleter.prototype.autocomplete = function (beforeCursor, afterCursor, callback, editor) {
    var self = this;

    var onFailure = function () {
      callback([]);
    };

    if (beforeCursor.match(/["'](?:\/[^\/]*)+/)) {
      var parts = beforeCursor.split('/');
      // Drop the first " or '
      parts.shift();
      // Last one is either partial name or empty
      parts.pop();

      self.fetchAlternatives(parts, callback, onFailure, editor);
    } else {
      onFailure();
    }
  };

  return HdfsAutocompleter;
}));