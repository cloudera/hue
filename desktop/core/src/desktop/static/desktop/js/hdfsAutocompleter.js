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

var HdfsAutocompleter = (function () {

  var TIME_TO_LIVE_IN_MILLIS = 60000; // 1 minute
  var BASE_PATH = "/filebrowser/view=";
  var PARAMETERS = "?pagesize=100&format=json";

  /**
   * @param {object} options
   * @param {string} options.user
   * @param {Number} options.timeout
   * @param {Snippet} options.snippet
   *
   * @constructor
   */
  function HdfsAutocompleter(options) {
    var self = this;
    self.user = options.user;
    self.snippet = options.snippet;
    self.timeout = options.timeout
  }

  HdfsAutocompleter.prototype.getTotalStorageUserPrefix = function () {
    var self = this;
    return self.user;
  };

  HdfsAutocompleter.prototype.hasExpired = function (timestamp) {
    return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  };

  HdfsAutocompleter.prototype.extractFields = function (data) {
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

      var successCallback = function (data) {
        if (!data.error) {
          callback(self.extractFields(data));
        } else {
          onFailure();
        }
      };

      self.snippet.getApiHelper().fetchHdfsPath({
        pathParts: parts,
        successCallback: successCallback,
        silenceErrors: true,
        errorCallback: onFailure,
        timeout: self.timeout,
        editor: editor
      });
    } else {
      onFailure();
    }
  };

  HdfsAutocompleter.prototype.getDocTooltip = function (item) {
  };

  return HdfsAutocompleter;
})();