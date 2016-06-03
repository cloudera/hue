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
  }

  SqlAutocompleter2.prototype.autocomplete = function(beforeCursor, afterCursor, callback, editor) {
    var self = this;
    var parseResult = sqlParser.parseSql(beforeCursor, afterCursor, self.snippet.type());

    var completions = [];

    if (parseResult.suggestKeywords) {
      parseResult.suggestKeywords.forEach(function (keyword) {
        completions.push({ value: keyword, meta: 'keyword' });
      });
    }

    if (parseResult.suggestIdentifiers) {
      parseResult.suggestIdentifiers.forEach(function (identifier) {
        completions.push({ value: identifier.name, meta: identifier.type });
      });
    }

    if (parseResult.suggestStar) {
      completions.push({ value: '*', meta: 'keyword' });
    }

    if (parseResult.suggestTables || parseResult.suggestColumns || parseResult.suggestValues) {
      var database = parseResult.useDatabase || self.snippet.database();

      var deferrals = [];

      if (parseResult.suggestTables) {
        var prefix = parseResult.suggestTables.prependQuestionMark ? '? ' : '';
        if (parseResult.suggestTables.prependFrom) {
          prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
        }

        var tableDeferred = $.Deferred();
        deferrals.push(tableDeferred);
        self.snippet.getApiHelper().fetchTables({
          sourceType: self.snippet.type(),
          databaseName: database,
          successCallback: function (data) {
            data.tables_meta.forEach(function (tablesMeta) {
              completions.push({ value: prefix + tablesMeta.name, meta: tablesMeta.type.toLowerCase() })
            });
            tableDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: tableDeferred.resolve,
          editor: editor
        });
      }

      if (parseResult.suggestColumns) {
        var columnsDeferred = $.Deferred();
        deferrals.push(columnsDeferred);

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
            columnsDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: columnsDeferred.resolve
        });
      }

      $.when.apply($, deferrals).done(function () {
        self.finalizeCompletions(completions, callback, editor);
      });
    } else {
      self.finalizeCompletions(completions, callback, editor);
    }
  };

  SqlAutocompleter2.prototype.finalizeCompletions = function (completions, callback, editor) {
    var self = this;
    self.sortCompletions(completions);

    var currentScore = 1000;
    completions.forEach(function (completion) {
      completion.score = currentScore;
      currentScore--;
    });

    // TODO Figure out why SELECT | FROM customers LATERAL VIEW explode(a) AS (b, c)
    if (typeof editor !== 'undefined') {
      editor.hideSpinner();
    }
    callback(completions);
  };

  var typeOrder = { 'star': 1, 'alias': 2, 'table': 3, 'identifier': 4, 'keyword': 5 };

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