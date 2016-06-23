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

    if (parseResult.suggestHdfs || parseResult.suggestTables || parseResult.suggestColumns || parseResult.suggestValues) {
      var database = parseResult.useDatabase || self.snippet.database();

      var deferrals = [];

      if (parseResult.suggestHdfs) {
        var parts = parseResult.suggestHdfs.path.split('/');
        // Drop the first " or '
        parts.shift();
        // Last one is either partial name or empty
        parts.pop();

        var hdfsDeferred = $.Deferred();
        deferrals.push(hdfsDeferred);

        self.snippet.getApiHelper().fetchHdfsPath({
          pathParts: parts,
          successCallback: function (data) {
            if (!data.error) {
              data.files.forEach(function (file) {
                if (file.name !== '..' && file.name !== '.') {
                  completions.push({ value: parseResult.suggestHdfs.path === '' ? '/' + file.name : file.name, meta: file.type });
                }
              });
            }
            hdfsDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: hdfsDeferred.resolve,
          editor: editor
        });
      }

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
            if (data.extended_columns) {
              data.extended_columns.forEach(function (column) {
                if (column.type.indexOf('map') === 0 && self.snippet.type() === 'hive') {
                  completions.push({value: column.name + '[]', meta: 'map'})
                } else if (column.type.indexOf('map') === 0) {
                  completions.push({value: column.name, meta: 'map'})
                } else if (column.type.indexOf('struct') === 0) {
                  completions.push({ value: column.name, meta: 'struct' })
                } else if (column.type.indexOf('array') === 0 && self.snippet.type() === 'hive') {
                  completions.push({ value: column.name + '[]', meta: 'array' })
                } else if (column.type.indexOf('array') === 0) {
                  completions.push({ value: column.name, meta: 'array' })
                } else {
                  completions.push({ value: column.name, meta: column.type })
                }
              });
            } else if (data.columns) {
              data.columns.forEach(function (column) {
                completions.push({ value: column, meta: 'column' })
              });
            }
            if (data.type === 'map' && self.snippet.type() === 'impala') {
              completions.push({ value: 'key', meta: 'key' });
              completions.push({ value: 'value', meta: 'value' });
            }
            if (data.type === 'struct') {
              data.fields.forEach(function (field) {
                completions.push({ value: field.name, meta: 'struct' })
              });
            } else if (data.type === 'map' && (data.value && data.value.fields)) {
              data.value.fields.forEach(function (field) {
                completions.push({ value: field.name, meta: field.type });
              });
            } else if (data.type === 'array' && (data.item && data.item.fields)) {
              data.item.fields.forEach(function (field) {
                if ((field.type === 'array' || field.type === 'map') && self.snippet.type() === 'hive') {
                  completions.push({ value: field.name + '[]', meta: field.type });
                } else {
                  completions.push({ value: field.name, meta: field.type });
                }
              });
            }
            columnsDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: columnsDeferred.resolve
        });
      }

      if (parseResult.suggestValues) {
        var valuesDeferred = $.Deferred();
        var impalaValuesDeferred = $.Deferred();
        deferrals.push(valuesDeferred);
        deferrals.push(impalaValuesDeferred);

        self.snippet.getApiHelper().fetchTableSample({
          sourceType: self.snippet.type(),
          databaseName: parseResult.suggestValues.database || database,
          tableName: parseResult.suggestValues.table,
          columnName: parseResult.suggestValues.identifierChain[0].name,
          editor: editor,
          successCallback: function (data) {
            if (data.status === 0 && data.headers.length === 1) {
              data.rows.forEach(function (row) {
                completions.push({ value: typeof row[0] === 'string' ? "'" + row[0] + "'" :  '' + row[0], meta: 'value' });
              });
            }
            valuesDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: valuesDeferred.resolve
        });

        if (self.snippet.type() === 'impala') {
          // TODO: Fetch for each identifier in the chain, we need to add key or value for impala
          //       select a.key from customers c, c.addresses a WHERE a.zip_code = |
          // Same goes for Hive
          //       SELECT orders[].items[].| FROM customers
          self.snippet.getApiHelper().fetchFields({
            sourceType: self.snippet.type(),
            databaseName: parseResult.suggestValues.database || database,
            tableName: parseResult.suggestValues.table,
            fields: $.map(parseResult.suggestValues.identifierChain, function (value) { return value.name }),
            editor: editor,
            successCallback: function (data) {
              if (data.sample) {
                var isString = data.type === "string";
                data.sample.forEach(function (sample) {
                  completions.push({ meta: 'value', value: isString ? "'" + sample + "'" : new String(sample) })
                });
              }
              impalaValuesDeferred.resolve();
            },
            silenceErrors: true,
            errorCallback: impalaValuesDeferred.resolve
          });
        } else {
          impalaValuesDeferred.resolve();
        }
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

  var typeOrder = { 'star': 1, 'alias': 2, 'table': 3, 'identifier': 4, 'key' : 5, 'value' : 6, 'keyword': 7 };

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