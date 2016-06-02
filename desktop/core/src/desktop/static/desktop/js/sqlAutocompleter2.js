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
      'desktop/js/autocomplete/sql'
    ], factory);
  } else {
    root.SqlAutocompleter2 = factory(sql);
  }
}(this, function (sqlParser) {


  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @constructor
   */
  function SqlAutocompleter2(options) {
    var self = this;
    self.snippet = options.snippet;
  };

  SqlAutocompleter2.prototype.autocomplete = function(beforeCursor, afterCursor, callback, editor) {
    var self = this;
    var parseResult = sqlParser.parseSql(beforeCursor, afterCursor, self.snippet.type());
    var completions = [];

    var onFailure = function () {
      editor.hideSpinner();
      self.finalizeCompletions(completions);
    };

    if (parseResult.suggestKeywords) {
      parseResult.suggestKeywords.forEach(function (keyword) {
        completions.push({ value: keyword, meta: 'keyword' });
      });
    }
    if (parseResult.suggestStar) {
      completions.push({ value: '*', meta: 'keyword' });
    }

    if (parseResult.suggestTables || parseResult.suggestColumns || parseResult.suggestValues) {
      var database = parseResult.useDatabase || self.snippet.database();

      if (parseResult.suggestTables) {
        var prefix = parseResult.suggestTables.prependQuestionMark ? '? ' : '';
        if (parseResult.suggestTables.prependFrom) {
          prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
        }
        
        self.snippet.getApiHelper().fetchTables({
          sourceType: self.snippet.type(),
          databaseName: database,
          successCallback: function (data) {
            data.tables_meta.forEach(function (tablesMeta) {
              completions.push({ value: prefix + tablesMeta.name, meta: tablesMeta.type.toLowerCase() })
            });
            self.finalizeCompletions(completions, callback);
          },
          silenceErrors: true,
          errorCallback: onFailure,
          editor: editor
        });
      }
      if (parseResult.suggestColumns) {
        var fields = [];
        if (parseResult.suggestColumns.identifierChain) {
          parseResult.suggestColumns.identifierChain.forEach(function (identifier) {
            var field = identifier.name;
            if (identifier.key) {
              field += '[' + identifier.key + ']';
            }
            fields.push(field);
          });
        }

        self.snippet.getApiHelper().fetchFields({
          sourceType: self.snippet.type(),
          databaseName: parseResult.suggestColumns.database || database,
          tableName: parseResult.suggestColumns.table,
          fields: fields,
          editor: editor,
          successCallback: function (data) {
            console.log(data);
            if (data.columns) {
              data.columns.forEach(function (column) {
                completions.push({ value: column, meta: 'column' })
              });
            }
            if (data.type === 'struct') {
              data.fields.forEach(function (field) {
                completions.push({ value: field.name  , meta: 'struct' })
              });
            }
            self.finalizeCompletions(completions, callback);
          },
          silenceErrors: true,
          errorCallback: onFailure
        });
      }
    } else {
      self.finalizeCompletions(completions, callback);
    }
  };

  SqlAutocompleter2.prototype.finalizeCompletions = function (completions, callback) {
    var self = this;
    self.sortCompletions(completions);

    var currentScore = 1000;
    completions.forEach(function (completion) {
      completion.score = currentScore;
      currentScore--;
    });

    callback(completions);
  };

  var typeOrder = { 'star': 1, 'table': 2, 'keyword': 3,  };

  SqlAutocompleter2.prototype.sortCompletions = function (completions) {
    completions.sort(function (a, b) {
      if (typeOrder[a.value == '*' ? 'star' : a.meta] !== typeOrder[b.value == '*' ? 'star' : b.meta]) {
        return typeOrder[a.value == '*' ? 'star' : a.meta] - typeOrder[b.value == '*' ? 'star' : b.meta];
      }
      return a.value.localeCompare(b.value);
    });
  };
  
  SqlAutocompleter2.prototype.getDocTooltip = function (item) {

  };

  return SqlAutocompleter2;
}));