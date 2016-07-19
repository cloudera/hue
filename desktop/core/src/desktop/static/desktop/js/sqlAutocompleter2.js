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
  if (typeof define === "function" && define.amd) {
    define([
      'desktop/js/autocomplete/sql',
      'desktop/js/sqlFunctions'
    ], factory);
  } else {
    root.SqlAutocompleter2 = factory(sql, sqlFunctions);
  }
}(this, function (sqlParser, sqlFunctions) {

  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {Number} options.timeout
   * @constructor
   */
  function SqlAutocompleter2(options) {
    var self = this;
    self.snippet = options.snippet;
    self.timeout = options.timeout;
  }

  SqlAutocompleter2.prototype.autocomplete = function (beforeCursor, afterCursor, callback, editor) {
    var self = this;
    var parseResult = sqlParser.parseSql(beforeCursor, afterCursor, self.snippet.type(), sqlFunctions);

    var deferrals = [];
    var completions = [];

    if (parseResult.suggestKeywords) {
      parseResult.suggestKeywords.forEach(function (keyword) {
        completions.push({
          value: parseResult.lowerCase ? keyword.toLowerCase() : keyword,
          meta: 'keyword',
          type: 'keyword'
        });
      });
    }

    if (parseResult.suggestIdentifiers) {
      parseResult.suggestIdentifiers.forEach(function (identifier) {
        completions.push({value: identifier.name, meta: identifier.type, type: 'identifier'});
      });
    }

    var database = parseResult.useDatabase || self.snippet.database();

    var colRefDeferral = $.Deferred();
    deferrals.push(colRefDeferral);
    var colRef = null;

    if (parseResult.colRef) {
      var colRefCallback = function (data) {
        colRef = data;
        colRefDeferral.resolve();
      };

      self.fetchFieldsForIdentifiers(editor, parseResult.colRef.table, parseResult.colRef.database || database, parseResult.colRef.identifierChain, colRefCallback, colRefDeferral.resolve);

    } else {
      colRefDeferral.resolve();
    }

    if (parseResult.suggestFunctions) {
      var suggestFunctionsDeferral = $.Deferred();
      if (parseResult.suggestFunctions.types && parseResult.suggestFunctions.types[0] === 'COLREF') {
        $.when.apply($, colRefDeferral).done(function () {
          if (colRef !== null) {
            sqlFunctions.suggestFunctions(self.snippet.type(), [colRef.type.toUpperCase()], parseResult.suggestAggregateFunctions || false, completions);
          } else {
            sqlFunctions.suggestFunctions(self.snippet.type(), ['T'], parseResult.suggestAggregateFunctions || false, completions);
          }
          suggestFunctionsDeferral.resolve();
        });
      } else {
        sqlFunctions.suggestFunctions(self.snippet.type(), parseResult.suggestFunctions.types || ['T'], parseResult.suggestAggregateFunctions || false, completions);
        suggestFunctionsDeferral.resolve();
      }
      deferrals.push(suggestFunctionsDeferral);
    }

    if (parseResult.suggestValues) {
      var suggestValuesDeferral = $.Deferred();
      $.when.apply($, colRefDeferral).done(function () {
        if (colRef !== null) {
          self.addValues(colRef, completions);
        }
        suggestValuesDeferral.resolve();
      });
      deferrals.push(suggestValuesDeferral);
    }

    if (parseResult.suggestColRefKeywords) {
      var suggestColRefKeywordsDeferral = $.Deferred();
      $.when.apply($, colRefDeferral).done(function () {
        if (colRef !== null) {
          self.addColRefKeywords(parseResult, colRef.type, completions);
        }
        suggestColRefKeywordsDeferral.resolve();
      });
      deferrals.push(suggestColRefKeywordsDeferral);
    }

    if (parseResult.suggestColumns) {
      var suggestColumnsDeferral =  $.Deferred();
      if (parseResult.suggestColumns.types && parseResult.suggestColumns.types[0] === 'COLREF') {
        $.when.apply($, colRefDeferral).done(function () {
          if (colRef !== null) {
            deferrals.push(self.addColumns(parseResult, editor, database, [colRef.type.toUpperCase()], completions));
          } else {
            deferrals.push(self.addColumns(parseResult, editor, database, ['T'], completions));
          }
          suggestColumnsDeferral.resolve();
        });
      } else {
        deferrals.push(self.addColumns(parseResult, editor, database, parseResult.suggestColumns.types || ['T'], completions));
        suggestColumnsDeferral.resolve();
      }
      deferrals.push(suggestColumnsDeferral);
    }

    if (parseResult.suggestDatabases) {
      deferrals.push(self.addDatabases(parseResult, completions));
    }

    if (parseResult.suggestHdfs) {
      deferrals.push(self.addHdfs(parseResult, completions));
    }

    if (parseResult.suggestTables) {
      deferrals.push(self.addTables(parseResult, editor, database, completions))
    }

    $.when.apply($, deferrals).done(function () {
      self.finalizeCompletions(completions, callback, editor);
    });
  };

  SqlAutocompleter2.prototype.addValues = function (columnReference, completions) {
    if (columnReference.sample) {
      var isString = columnReference.type === "string";
      columnReference.sample.forEach(function (sample) {
        completions.push({meta: 'value', value: isString ? "'" + sample + "'" : new String(sample), type: 'sample'})
      });
    }
  };

  SqlAutocompleter2.prototype.addColRefKeywords = function (parseResult, type, completions) {
    var self = this;
    Object.keys(parseResult.suggestColRefKeywords).forEach(function (typeForKeywords) {
      if (sqlFunctions.matchesType(self.snippet.type(), [typeForKeywords], [type.toUpperCase()])) {
        parseResult.suggestColRefKeywords[typeForKeywords].forEach(function (keyword) {
          completions.push({
            value: parseResult.lowerCase ? keyword.toLowerCase() : keyword,
            meta: 'keyword',
            type: 'keyword'
          });
        })
      }
    });
  };

  SqlAutocompleter2.prototype.fetchFieldsForIdentifiers = function (editor, tableName, databaseName, identifierChain, callback, errorCallback, fetchedFields) {
    var self = this;
    if (!fetchedFields) {
      fetchedFields = [];
    }
    if (!identifierChain) {
      identifierChain = [];
    }
    if (identifierChain.length > 0) {
      fetchedFields.push(identifierChain[0].name);
      identifierChain = identifierChain.slice(1);
    }

    self.snippet.getApiHelper().fetchFields({
      sourceType: self.snippet.type(),
      databaseName: databaseName,
      tableName: tableName,
      fields: fetchedFields,
      editor: editor,
      timeout: self.timeout,
      successCallback: function (data) {
        if (identifierChain.length > 0) {
          if (data.type === 'array') {
            fetchedFields.push('item')
          }
          if (data.type === 'map') {
            fetchedFields.push('value')
          }
          self.fetchFieldsForIdentifiers(editor, tableName, databaseName, identifierChain, callback, errorCallback, fetchedFields)
        } else {
          callback(data);
        }
      },
      silenceErrors: true,
      errorCallback: errorCallback
    });
  };

  SqlAutocompleter2.prototype.addTables = function (parseResult, editor, database, completions) {
    var self = this;
    var tableDeferred = $.Deferred();
    var prefix = parseResult.suggestTables.prependQuestionMark ? '? ' : '';
    if (parseResult.suggestTables.prependFrom) {
      prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
    }

    self.snippet.getApiHelper().fetchTables({
      sourceType: self.snippet.type(),
      databaseName: parseResult.suggestTables.database || database,
      successCallback: function (data) {
        data.tables_meta.forEach(function (tablesMeta) {
          completions.push({
            value: prefix + tablesMeta.name,
            meta: tablesMeta.type.toLowerCase(),
            type: 'table'
          })
        });
        tableDeferred.resolve();
      },
      silenceErrors: true,
      errorCallback: tableDeferred.resolve,
      editor: editor,
      timeout: self.timeout
    });
    return tableDeferred;
  };

  SqlAutocompleter2.prototype.addColumns = function (parseResult, editor, database, types, completions) {
    var self = this;
    var addColumnsDeferred = $.Deferred();

    var callback = function (data) {
      if (data.extended_columns) {
        data.extended_columns.forEach(function (column) {
          if (column.type.indexOf('map') === 0 && self.snippet.type() === 'hive') {
            completions.push({value: column.name + '[]', meta: 'map', type: 'column'})
          } else if (column.type.indexOf('map') === 0) {
            completions.push({value: column.name, meta: 'map', type: 'column'})
          } else if (column.type.indexOf('struct') === 0) {
            completions.push({value: column.name, meta: 'struct', type: 'column'})
          } else if (column.type.indexOf('array') === 0 && self.snippet.type() === 'hive') {
            completions.push({value: column.name + '[]', meta: 'array', type: 'column'})
          } else if (column.type.indexOf('array') === 0) {
            completions.push({value: column.name, meta: 'array', type: 'column'})
          } else if (sqlFunctions.matchesType(self.snippet.type(), types, [column.type.toUpperCase()]) ||
              sqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
            completions.push({value: column.name, meta: column.type, type: 'column'})
          }
        });
      } else if (data.columns) {
        data.columns.forEach(function (column) {
          completions.push({value: column, meta: 'column', type: 'column'})
        });
      }
      if (data.type === 'map' && self.snippet.type() === 'impala') {
        completions.push({value: 'key', meta: 'key', type: 'column'});
        completions.push({value: 'value', meta: 'value', type: 'column'});
      }
      if (data.type === 'struct') {
        data.fields.forEach(function (field) {
          completions.push({value: field.name, meta: 'struct', type: 'column'})
        });
      } else if (data.type === 'map' && (data.value && data.value.fields)) {
        data.value.fields.forEach(function (field) {
          if (sqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
              sqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
            completions.push({value: field.name, meta: field.type, type: 'column'});
          }
        });
      } else if (data.type === 'array' && (data.item && data.item.fields)) {
        data.item.fields.forEach(function (field) {
          if ((field.type === 'array' || field.type === 'map')) {
            if (self.snippet.type() === 'hive') {
              completions.push({value: field.name + '[]', meta: field.type, type: 'column'});
            } else {
              completions.push({value: field.name, meta: field.type, type: 'column'});
            }
          } else if (sqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
              sqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
            completions.push({value: field.name, meta: field.type, type: 'column'});
          }
        });
      }
      addColumnsDeferred.resolve();
    };

    self.fetchFieldsForIdentifiers(editor, parseResult.suggestColumns.table, parseResult.suggestColumns.database || database, parseResult.suggestColumns.identifierChain, callback, addColumnsDeferred.resolve);

    return addColumnsDeferred;
  };

  SqlAutocompleter2.prototype.addDatabases = function (parseResult, completions) {
    var self = this;
    var databasesDeferred = $.Deferred();
    var prefix = parseResult.suggestDatabases.prependQuestionMark ? '? ' : '';
    if (parseResult.suggestDatabases.prependFrom) {
      prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
    }
    self.snippet.getApiHelper().loadDatabases({
      sourceType: self.snippet.type(),
      successCallback: function (data) {
        data.forEach(function (db) {
          completions.push({
            value: prefix + db + (parseResult.suggestDatabases.appendDot ? '.' : ''),
            meta: 'database',
            type: 'database'
          });
        });
        databasesDeferred.resolve();
      },
      silenceErrors: true,
      errorCallback: databasesDeferred.resolve
    });
    return databasesDeferred;
  };

  SqlAutocompleter2.prototype.addHdfs = function (parseResult, completions) {
    var self = this;
    var hdfsDeferred = $.Deferred();
    var parts = parseResult.suggestHdfs.path.split('/');
    // Drop the first " or '
    parts.shift();
    // Last one is either partial name or empty
    parts.pop();

    self.snippet.getApiHelper().fetchHdfsPath({
      pathParts: parts,
      successCallback: function (data) {
        if (!data.error) {
          data.files.forEach(function (file) {
            if (file.name !== '..' && file.name !== '.') {
              completions.push({
                value: parseResult.suggestHdfs.path === '' ? '/' + file.name : file.name,
                meta: file.type,
                type: 'HDFS'
              });
            }
          });
        }
        hdfsDeferred.resolve();
      },
      silenceErrors: true,
      errorCallback: hdfsDeferred.resolve,
      editor: editor,
      timeout: self.timeout
    });

    return hdfsDeferred;
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

  var typeOrder = {
    'star': 1,
    'column': 2,
    'sample': 3,
    'table': 4,
    'database': 5,
    'identifier': 6,
    'keyword': 7,
    'function': 8
  };

  SqlAutocompleter2.prototype.sortCompletions = function (completions) {
    completions.sort(function (a, b) {
      if (typeOrder[a.value === '*' ? 'star' : a.type] !== typeOrder[b.value === '*' ? 'star' : b.type]) {
        return typeOrder[a.value == '*' ? 'star' : a.type] - typeOrder[b.value == '*' ? 'star' : b.type];
      }
      return a.value.localeCompare(b.value);
    });
  };

  SqlAutocompleter2.prototype.getDocTooltip = function (item) {

  };

  return SqlAutocompleter2;
}));