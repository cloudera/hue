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
    define([
      'desktop/js/sqlAutocompleter',
      'desktop/js/hdfsAutocompleter'
    ], factory);
  } else {
    root.Autocompleter = factory(SqlAutocompleter, HdfsAutocompleter);
  }
}(this, function (SqlAutocompleter, HdfsAutocompleter) {

  /**
   * @param options {object}
   * @param options.snippet
   * @param options.user
   *
   * @constructor
   */
  function Autocompleter(options) {
    var self = this;
    self.snippet = options.snippet;

    var initializeAutocompleter = function () {
      var hdfsAutocompleter = new HdfsAutocompleter({
        user: options.user,
        snippet: options.snippet
      });
      if (self.snippet.isSqlDialect()) {
        self.autocompleter = new SqlAutocompleter({
          hdfsAutocompleter: hdfsAutocompleter,
          snippet: options.snippet,
          oldEditor: options.oldEditor
        })
      } else {
        self.autocompleter = hdfsAutocompleter;
      }
    };
    self.snippet.type.subscribe(function () {
      initializeAutocompleter();
    });
    initializeAutocompleter();
  }

  Autocompleter.prototype.initializeAutocompleter = function () {
    var self = this;
  };

  // ACE Format for autocompleter
  Autocompleter.prototype.getCompletions = function (editor, session, pos, prefix, callback) {
    var self = this;
    if (! self.autocompleter) {
      return;
    }

    var before = editor.getTextBeforeCursor();
    var after = editor.getTextAfterCursor(";");

    self.autocomplete(before, after, function(result) {
      callback(null, result);
    }, editor);
  };

  Autocompleter.prototype.autocomplete = function(beforeCursor, afterCursor, callback, editor) {
    var self = this;
    if (self.autocompleter) {
      self.autocompleter.autocomplete(beforeCursor, afterCursor, callback, editor);
    }
  };

  return Autocompleter;
}));