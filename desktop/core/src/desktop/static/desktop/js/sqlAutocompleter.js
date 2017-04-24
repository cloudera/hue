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

var SqlAutocompleter = (function () {

  var SQL_TERMS = /\b(FROM|TABLE|STATS|REFRESH|METADATA|DESCRIBE|ORDER BY|JOIN|ON|WHERE|SELECT|LIMIT|GROUP BY|SORT|USE|LOCATION|INPATH)\b/g;

  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {Number} options.timeout
   * @param {HdfsAutocompleter} options.hdfsAutocompleter
   * @constructor
   */
  function SqlAutocompleter(options) {
    var self = this;
    self.timeout = options.timeout;
    self.snippet = options.snippet;
    self.hdfsAutocompleter = options.hdfsAutocompleter;
    self.oldEditor = options.oldEditor || false;
    self.optEnabled = options.optEnabled || false;

    self.topTablesPerDb = {};

    // Speed up by caching the databases
    var initDatabases = function () {
      self.snippet.getApiHelper().loadDatabases({
        sourceType: self.snippet.type(),
        silenceErrors: true,
        successCallback: function () {
          if (self.optEnabled) {
            $.each(self.snippet.getApiHelper().lastKnownDatabases[self.snippet.type()], function (idx, db) {
              if (db === 'default') {
                $.post('/metadata/api/optimizer_api/top_tables', {
                  database: db
                }, function(data){
                  if (! self.topTablesPerDb[db]) {
                    self.topTablesPerDb[db] = {};
                  }
                  data.top_tables.forEach(function (table) {
                    self.topTablesPerDb[db][table.name] = table;
                  });
                });
              }
            });
          }
        }
      });
    };
    self.snippet.type.subscribe(function() {
      if (self.snippet.isSqlDialect()) {
        initDatabases();
      }
    });
    initDatabases();
  }

  var fixScore = function (suggestions) {
    $.each(suggestions, function (idx, value) {
      value.score = 1000 - idx;
    });
    return suggestions;
  };

  SqlAutocompleter.prototype.getFromReferenceIndex = function (statement) {
    var self = this;
    var result = {
      tables: {},
      complex: {}
    };
    var fromMatch = statement.match(/\s*from\s*([^;]*).*$/i);
    if (fromMatch) {
      var refsRaw = fromMatch[1];
      var upToMatch = refsRaw.match(/\s+(LATERAL|VIEW|EXPLODE|POSEXPLODE|ON|LIMIT|WHERE|GROUP BY|SORT|ORDER BY)\s+/i);
      if (upToMatch) {
        refsRaw = $.trim(refsRaw.substring(0, upToMatch.index));
      }
      var refs = $.map(refsRaw.split(/\s*(?:,|\bJOIN\b)\s*/i), function (ref) {
        if (ref.indexOf('.') > 0) {
          var refParts = ref.split('.');

          if(self.snippet.getApiHelper().lastKnownDatabases[self.snippet.type()].indexOf(refParts[0]) > -1) {
            return {
              database: refParts.shift(),
              table: refParts.join('.')
            }
          }
        }
        return {
          database: null,
          table: ref
        }
      });

      refs.sort(function (a, b) {
        return a.table.localeCompare(b.table);
      });
      $.each(refs, function(index, tableRefRaw) {
        if (tableRefRaw.table.indexOf('(') == -1) {
          var refMatch = tableRefRaw.table.match(/\s*(\S+)\s*(\S+)?\s*/);

          var refParts = refMatch[1].split('.');
          if (refMatch[2]) {
            if (refParts.length == 1) {
              result.tables[refMatch[2]] = {
                table: refParts[0],
                database: tableRefRaw.database
              };
            } else {
              result.complex[refMatch[2]] = refParts;
            }
          } else {
            result.tables[refMatch[1]] = {
              table: refMatch[1],
              database: tableRefRaw.database
            };
          }
        }
      })
    }
    return result;
  };

  SqlAutocompleter.prototype.getViewReferenceIndex = function (statement, hiveSyntax) {
    var result = {
      allViewReferences: [],
      index: {}
    };

    // For now we only support LATERAL VIEW references for Hive
    if (! hiveSyntax) {
      return result;
    }

    // Matches both arrays and maps "AS ref" or "AS (keyRef, valueRef)" and with
    // or without view reference.
    // group 1 = pos for posexplode or undefined
    // group 2 = argument to table generating function
    // group 3 = view reference or undefined
    // group 4 = array item reference
    //           array index reference (if posexplode)
    //           map key reference (if group 5 is exists)
    // group 5 = array value (if posexplode)
    //           map value reference (if ! posexplode)
    var lateralViewRegex = /LATERAL\s+VIEW\s+(pos)?explode\(([^\)]+)\)\s+(?:(\S+)\s+)?AS\s+\(?([^\s,\)]*)(?:\s*,\s*([^\s,]*)\))?/gi;
    var lateralViewMatch;

    while (lateralViewMatch = lateralViewRegex.exec(statement)) {
      var isMapRef = (!lateralViewMatch[1] && lateralViewMatch[5]) || false ;
      var isPosexplode = lateralViewMatch[1] || false;

      var pathToField = lateralViewMatch[2].split(".");

      var viewRef = {
        leadingPath: pathToField,
        references: []
      };

      if (isMapRef) {
        // TODO : use lateralViewMatch[4] for key ref once API supports map key lookup
        result.index[lateralViewMatch[5]] = {
          leadingPath: pathToField,
          addition: 'value'
        };
        viewRef.references.push({ name: lateralViewMatch[4], type: 'key'});
        viewRef.references.push({ name: lateralViewMatch[5], type: 'value'});
      } else if (isPosexplode) {
        // TODO : use lateralViewMatch[4] for array index ref once API supports array index lookup
        // Currently we don't support array key refs
        result.index[lateralViewMatch[5]] = {
          leadingPath: pathToField,
          addition: 'item'
        };
        viewRef.references.push({ name: lateralViewMatch[4], type: 'index'});
        viewRef.references.push({ name: lateralViewMatch[5], type: 'item'});
      } else {
        // exploded array without position
        result.index[lateralViewMatch[4]] = {
          leadingPath: pathToField,
          addition: 'item'
        };
        viewRef.references.push({ name: lateralViewMatch[4], type: 'item'});
      }

      result.allViewReferences = result.allViewReferences.concat(viewRef.references);

      if (lateralViewMatch[3]) {
        result.allViewReferences.push({ name: lateralViewMatch[3], type: 'view' });
        result.index[lateralViewMatch[3]] = viewRef;
      }
    }

    // Expand any references in paths of references
    var foundRef = false;
    // Limit iterations to 10
    for (var i = 0; i < 10 && (i == 0 || foundRef); i++) {
      $.each(result.index, function(alias, value) {
        var newLeadingPath = [];
        $.each(value.leadingPath, function(index, path) {
          if (result.index[path]) {
            foundRef = true;
            newLeadingPath = newLeadingPath.concat(result.index[path].leadingPath);
            newLeadingPath.push(result.index[path].addition);
          } else {
            newLeadingPath.push(path);
          }
        });
        value.leadingPath = newLeadingPath;
      });
    }

    return result;
  };

  SqlAutocompleter.prototype.getValueReferences = function (conditionMatch, database, fromReferences, tableAndComplexRefs, callback, editor) {
    var self = this;
    var fields = conditionMatch[1].split(".");
    var tableName = null;
    if (fields[0] in fromReferences.complex) {
      var complexRef = fields.shift();
      fields = fromReferences.complex[complexRef].concat(fields);
    }
    if (fields[0] in fromReferences.tables) {
      var tableRef = fromReferences.tables[fields.shift()];
      tableName = tableRef.table;
      if (tableRef.database !== null) {
        database = tableRef.database;
      }
    }
    if (! tableName && tableAndComplexRefs.length === 1) {
      tableName = tableAndComplexRefs[0].value;
    }
    if (tableName) {
      var completeFields = [];
      // For impala we need to check each part with the API, it could be a map or array in which case we need to add
      // either "value" or "item" in between.
      var fetchImpalaFields = function (remainingParts, topValues) {
        completeFields.push(remainingParts.shift());
        if (remainingParts.length > 0 && remainingParts[0] == "value" || remainingParts[0] == "key") {
          fetchImpalaFields(remainingParts, topValues);
        } else {
          self.snippet.getApiHelper().fetchFields({
            sourceType: self.snippet.type(),
            databaseName: database,
            tableName: tableName,
            fields: completeFields,
            editor: editor,
            timeout: self.timeout,
            successCallback: function (data) {
              if (data.type === "map") {
                completeFields.push("value");
                fetchImpalaFields(remainingParts, topValues);
              } else if (data.type === "array") {
                completeFields.push("item");
                fetchImpalaFields(remainingParts, topValues);
              } else if (remainingParts.length == 0 && data.sample) {
                var isString = data.type === "string";
                var values = $.map(data.sample.sort(), function(value, index) {
                  return {
                    meta: "value",
                    score: 900 - index,
                    value: isString ? "'" + value + "'" : new String(value)
                  }
                });
                callback(fixScore(topValues.concat(tableAndComplexRefs).concat(values)));
              } else {
                callback(fixScore(topValues.concat(tableAndComplexRefs)));
              }
            },
            silenceErrors: true,
            errorCallback: function () {
              callback(fixScore(topValues.concat(tableAndComplexRefs)));
            }
          });
        }
      };

      if (fields.length === 1 && !self.optEnabled) {
        self.snippet.getApiHelper().fetchTableSample({
          sourceType: self.snippet.type(),
          databaseName: database,
          tableName: tableName,
          columnName: fields.length === 1 ? fields[0] : null,
          editor: editor,
          timeout: self.timeout,
          silenceErrors: true,
          successCallback: function (data) {
            if (data.status === 0 && data.headers.length === 1) {
              var values = $.map(data.rows, function (row, index) {
                return {
                  meta: 'value',
                  score: 1000 - index,
                  value: typeof row[0] === 'string' ? "'" + row[0] + "'" :  '' + row[0]
                }
              });
              if (self.snippet.type() === 'impala') {
                fetchImpalaFields(fields, values);
              } else {
                callback(values);
              }
            } else {
              if (self.snippet.type() === 'impala') {
                fetchImpalaFields(fields, []);
              }
            }
          },
          errorCallback: function () {
            if (self.snippet.type() === 'impala') {
              fetchImpalaFields(fields, []);
            } else {
              callback([]);
            }
          }
        });
      } else if (fields.length === 1 && self.optEnabled) {
        $.post('/metadata/api/optimizer_api/popular_values', {
          database: database,
          tableName: tableName,
          columnName: fields[0]
        }).done(function(data){
          if (data.status === 0) {
            var foundCol = data.values.filter(function (col) {
              return col.columnName === fields[0];
            });
            var topValues = [];
            if (foundCol.length === 1) {
              topValues = $.map(foundCol[0].values, function (value, index) {
                return {
                  meta: "popular",
                  score: 1000 - index,
                  value: value,
                  caption: value.length > 28 ? value.substring(0, 25) + '...' : null
                };
              })
            }
            if (self.snippet.type() === "impala") {
              fetchImpalaFields(fields, topValues);
            } else {
              callback(fixScore(topValues.concat(tableAndComplexRefs)));
            }
          }
        }).fail(function () {
          if (self.snippet.type() === "impala") {
            fetchImpalaFields(fields, []);
          }
        });
      } else if (self.snippet.type() === "impala") {
        fetchImpalaFields(fields, []);
      }
    }
  };

  SqlAutocompleter.prototype.extractFields = function (data, tableName, database, valuePrefix, includeStar, extraSuggestions, excludeDatabases) {
    var self = this;
    var fields = [];
    var result = [];
    var prependedFields = extraSuggestions || [];

    if (data.type == "struct") {
      fields = $.map(data.fields, function(field) {
        return {
          name: field.name,
          type: field.type
        };
      });
    } else if (typeof data.columns != "undefined") {
      fields = $.map(data.columns, function(column) {
        return {
          name: column,
          type: "column"
        }
      });
      if (includeStar) {
        result.push({value: '*', score: 10000, meta: "column"});
      }
    } else if (typeof data.tables_meta != "undefined") {
      fields = $.map(data.tables_meta, function(tableMeta) {
        return {
          name: tableMeta.name,
          type: "table"
        }
      });
      if (! excludeDatabases && ! self.oldEditor) {
        // No FROM prefix
        prependedFields = prependedFields.concat(fields);
        fields = $.map(self.snippet.getApiHelper().lastKnownDatabases[self.snippet.type()], function(database) {
          return {
            name: database + ".",
            type: "database"
          }
        })
      }
    }

    fields.sort(function (a, b) {
      return a.name.localeCompare(b.name);
    });

    if (prependedFields) {
      prependedFields.sort(function (a, b) {
        return a.name.localeCompare(b.name);
      });
      fields = prependedFields.concat(fields);
    }

    fields.forEach(function(field, idx) {
      if (field.name != "") {
        result.push({
          value: typeof valuePrefix != "undefined" ? valuePrefix + field.name : field.name,
          score: 1000 - idx,
          meta: field.type,
          database: database,
          tableName: tableName
        });
      }
    });
    return result;
  };

  SqlAutocompleter.prototype.autocomplete = function(beforeCursor, upToNextStatement, realCallback, editor) {
    var self = this;
    var callback = function (values) {
      if (! self.optEnabled) {
        realCallback(values);
        return;
      }
      if (values.length > 0) {
        var foundTables = {};
        values.forEach(function (value) {
          if (value.meta === 'column' && value.tableName) {
            if (! foundTables[value.tableName]) {
              foundTables[value.tableName] = [];
            }
            foundTables[value.tableName].push(value)
          }
        });
        if (Object.keys(foundTables).length === 1) {
          $.post('/metadata/api/optimizer_api/popular_values', {
            database: database,
            tableName: tableName
          }).done(function (data) {
            var valueByColumn = {};
            data.values.forEach(function (colValue) {
              valueByColumn[colValue.columnName] = colValue.values;
            });
            foundTables[Object.keys(foundTables)[0]].forEach(function (colSuggestion) {
              if (valueByColumn[colSuggestion.value]) {
                colSuggestion.popularValues = valueByColumn[colSuggestion.value];
              }
            });
            realCallback(values);
          }).fail(function () {
            realCallback(values);
          });
        } else {
          realCallback(values);
        }
      } else {
        realCallback([]);
      }
    };

    var onFailure = function() {
      callback([]);
    };

    var allStatements = beforeCursor.split(';');


    var hiveSyntax = self.snippet.type() === "hive";
    var impalaSyntax = self.snippet.type() === "impala";

    var beforeCursorU = allStatements.pop().toUpperCase();
    var afterCursorU = upToNextStatement.toUpperCase();

    var beforeMatcher = beforeCursorU.match(SQL_TERMS);
    var afterMatcher = afterCursorU.match(SQL_TERMS);

    if (beforeMatcher == null || beforeMatcher.length == 0) {
      callback([]);
      return;
    }

    var database = self.snippet.database();
    for (var i = allStatements.length - 1; i >= 0; i--) {
      var useMatch = allStatements[i].match(/\s*use\s+([^\s;]+)\s*;?/i);
      if (useMatch) {
        database = useMatch[1];
        break;
      }
    }
    if (! database) {
      onFailure();
      return;
    }


    var keywordBeforeCursor = beforeMatcher[beforeMatcher.length - 1];

    var impalaFieldRef = impalaSyntax && beforeCursor.slice(-1) === '.';

    if (keywordBeforeCursor === "USE") {
      var databases = self.snippet.getApiHelper().lastKnownDatabases[self.snippet.type()];
      databases.sort();
      callback($.map(databases, function(db, idx) {
        return {
          value: db,
          score: 1000 - idx,
          meta: 'database'
        };
      }));
      return;
    }

    if (keywordBeforeCursor === "LOCATION" || keywordBeforeCursor === "INPATH") {
      var pathMatch = beforeCursor.match(/.*(?:inpath|location)\s+('[^']*)$/i);
      if (pathMatch) {
        var existingPath = pathMatch[1].length == 1 ? pathMatch[1] + "/" : pathMatch[1];
        self.hdfsAutocompleter.autocomplete(existingPath, "", function (hdfsSuggestions) {
          var addLeadingSlash = pathMatch[1].length == 1;
          var addTrailingSlash = afterCursorU.length == 0 || afterCursorU[0] == "'";
          var addTrailingApostrophe = afterCursorU.length == 0;
          $.each(hdfsSuggestions, function (idx, hdfsSuggestion) {
            if (addLeadingSlash) {
              hdfsSuggestion.value = "/" + hdfsSuggestion.value;
            }
            if (addTrailingSlash && hdfsSuggestion.meta === "dir") {
              hdfsSuggestion.value += "/";
            }
            if (addTrailingApostrophe && hdfsSuggestion.meta === "file") {
              hdfsSuggestion.value += "'";
            }
          });
          callback(hdfsSuggestions);
        });
      } else {
        onFailure();
      }
      return;
    }

    var tableNameAutoComplete = (keywordBeforeCursor === "FROM" ||
      keywordBeforeCursor === "TABLE" ||
      keywordBeforeCursor === "STATS" ||
      keywordBeforeCursor === "JOIN" ||
      keywordBeforeCursor === "REFRESH" ||
      keywordBeforeCursor === "METADATA" ||
      keywordBeforeCursor === "DESCRIBE") && !impalaFieldRef;

    var selectBefore = keywordBeforeCursor === "SELECT";

    var fieldTermBefore = keywordBeforeCursor === "WHERE" ||
      keywordBeforeCursor === "ON" ||
      keywordBeforeCursor === "GROUP BY" ||
      keywordBeforeCursor === "ORDER BY";

    var fromAfter = afterMatcher != null && afterMatcher[0] === "FROM";

    if (tableNameAutoComplete || (selectBefore && !fromAfter)) {
      var dbRefMatch = beforeCursor.match(/.*from\s+([^\.\s]+).$/i);
      var partialMatch = beforeCursor.match(/.*from\s+([\S]+)$/i);
      var partialTableOrDb = null;
      if (dbRefMatch && self.snippet.getApiHelper().lastKnownDatabases[self.snippet.type()].indexOf(dbRefMatch[1]) > -1) {
        database = dbRefMatch[1];
      } else if (dbRefMatch && partialMatch) {
        partialTableOrDb = partialMatch[1].toLowerCase();
        database = self.snippet.database();
      }

      self.snippet.getApiHelper().fetchTables({
        sourceType: self.snippet.type(),
        databaseName: database,
        successCallback: function (data) {
          var fromKeyword = "";
          if (selectBefore) {
            if (beforeCursor.indexOf("SELECT") > -1) {
              fromKeyword = "FROM";
            } else {
              fromKeyword = "from";
            }
            if (beforeCursor.match(/select\s*$/i)) {
              fromKeyword = "? " + fromKeyword;
            }
            if (!beforeCursor.match(/(\s+|f|fr|fro|from)$/)) {
              fromKeyword = " " + fromKeyword;
            }
            fromKeyword += " ";
          }
          var result = self.extractFields(data, null, database, fromKeyword, false, [], dbRefMatch !== null && partialTableOrDb === null);
          if (partialTableOrDb !== null) {
            callback($.grep(result, function (suggestion) {
              return suggestion.value.indexOf(partialTableOrDb) === 0;
            }))
          } else {
            callback(result);
          }
        },
        silenceErrors: true,
        errorCallback: onFailure,
        editor: editor,
        timeout: self.timeout
      });
      return;
    } else if ((selectBefore && fromAfter) || fieldTermBefore || impalaFieldRef) {
      var partialTermsMatch = beforeCursor.match(/([^\s\(\-\+\<\>\,]*)$/);
      var parts = partialTermsMatch ? partialTermsMatch[0].split(".") : [];

      // Drop the last part, empty or not. If it's not empty it's the start of a
      // field (or a complete one) for that case we suggest the same.
      // SELECT tablename.colu => suggestion: "column"
      parts.pop();

      var fromReferences = self.getFromReferenceIndex(beforeCursor + upToNextStatement);
      var viewReferences = self.getViewReferenceIndex(beforeCursor + upToNextStatement, hiveSyntax);
      var conditionMatch = beforeCursor.match(/(\S+)\s*=\s*([^\s;]+)?$/);

      var tableName = "";

      if (parts.length > 0 && fromReferences.tables[parts[0]]) {
        // SELECT tableref.column.
        var tableRef = fromReferences.tables[parts.shift()];
        tableName = tableRef.table;
        if (tableRef.database !== null) {
          database = tableRef.database;
        }
      } else if (parts.length > 0 && fromReferences.complex[parts[0]]) {
        var complexRefList = fromReferences.complex[parts.shift()];
        if (fromReferences.tables[complexRefList[0]]) {
          tableName = fromReferences.tables[complexRefList[0]].table;
          if (fromReferences.tables[complexRefList[0]].database !== null) {
            database = fromReferences.tables[complexRefList[0]].database;
          }
          // The first part is a table ref, the rest are col, struct etc.
          parts = complexRefList.slice(1).concat(parts);
        } else {
          onFailure();
          return;
        }
      } else if (parts.length === 0 && (Object.keys(fromReferences.tables).length + Object.keys(fromReferences.complex).length) > 1) {
        // There are multiple table or complex type references possible so we suggest those
        var count = 0;
        var tableRefs = $.map(Object.keys(fromReferences.tables), function (key, idx) {
          return {
            value: key + (upToNextStatement.indexOf(".") == 0 ? "" : "."),
            score: 1000 - count++,
            meta: fromReferences.tables[key].table == key ? 'table' : 'alias'
          };
        });

        var complexRefs = $.map(Object.keys(fromReferences.complex), function (key, idx) {
          return {
            value: key + (upToNextStatement.indexOf(".") == 0 ? "" : "."),
            score: 1000 - count++,
            meta: 'alias'
          };
        });

        if (conditionMatch) {
          self.getValueReferences(conditionMatch, database, fromReferences, tableRefs.concat(complexRefs), callback, editor);
        } else {
          callback(tableRefs.concat(complexRefs));
        }
        return;
      } else if (Object.keys(fromReferences.tables).length == 1) {
        // SELECT column. or just SELECT
        // We use first and only table reference if exist
        // if there are no parts the call to getFields will fetch the columns
        var tableRef = fromReferences.tables[Object.keys(fromReferences.tables)[0]];
        tableName = tableRef.table;
        if (tableRef.database !== null) {
          database = tableRef.database;
        }
        if (conditionMatch) {
          var tableRefs = [{
            value: tableName,
            score: 1000,
            meta: 'tables'
          }];

          self.getValueReferences(conditionMatch, database, fromReferences, tableRefs, callback);
          return;
        }
      } else if (parts.length > 0 && viewReferences.index[parts[0]] && viewReferences.index[parts[0]].leadingPath.length > 0) {
        var tableRef = fromReferences.tables[viewReferences.index[parts[0]].leadingPath[0]];
        tableName = tableRef.table;
        if (tableRef.database !== null) {
          database = tableRef.database;
        }
      } else {
        // Can't complete without table reference
        onFailure();
        return;
      }

      var getFields = function (database, remainingParts, fields) {
        if (remainingParts.length == 0) {
          self.snippet.getApiHelper().fetchFields({
            sourceType: self.snippet.type(),
            databaseName: database,
            tableName: tableName,
            fields: fields,
            editor: editor,
            timeout: self.timeout,
            successCallback: function (data) {
              var suggestions = [];
              if (fields.length == 0) {
                suggestions = self.extractFields(data, tableName, database, "", !fieldTermBefore && !impalaFieldRef, viewReferences.allViewReferences);
              } else {
                suggestions = self.extractFields(data, tableName, database, "", !fieldTermBefore);
              }

              var startedMatch = beforeCursorU.match(/.* (WHERE|AND|OR)\s+(\S+)$/);
              if (self.optEnabled && keywordBeforeCursor === "WHERE" && startedMatch) {
                $.post('/metadata/api/optimizer_api/popular_values', {
                  database: database,
                  tableName: tableName
                }).done(function (data) {
                  var popular = [];
                  if (data.status === 0) {
                    $.each(data.values, function (idx, colValue) {
                      $.each(colValue.values, function (idx, value) {
                        var suggestion = '';
                        if (colValue.tableName !== tableName) {
                          suggestion += colValue.tableName + ".";
                        }
                        suggestion += colValue.columnName + ' = ' + value;
                        popular.push({
                          meta: "popular",
                          score: 1000,
                          value: suggestion,
                          caption: suggestion.length > 28 ? suggestion.substring(0, 25) + '...' : null
                        });
                      });
                    });
                  }
                  callback(fixScore(popular.concat(suggestions)));
                }).fail(function () {
                  callback(suggestions);
                });
              } else {
                callback(suggestions);
              }
            },
            silenceErrors: true,
            errorCallback: onFailure
          });
          return; // break recursion
        }
        var part = remainingParts.shift();

        if (part != '' && part !== tableName) {
          if (hiveSyntax) {
            if (viewReferences.index[part]) {
              if (viewReferences.index[part].references && remainingParts.length == 0) {
                callback(self.extractFields([], tableName, database, "", true, viewReferences.index[part].references));
                return;
              }
              if (fields.length == 0 && viewReferences.index[part].leadingPath.length > 0) {
                // Drop first if table ref
                if (fromReferences.tables[viewReferences.index[part].leadingPath[0]]) {
                  fields = fields.concat(viewReferences.index[part].leadingPath.slice(1));
                } else {
                  fields = fields.concat(viewReferences.index[part].leadingPath);
                }
              }
              if (viewReferences.index[part].addition) {
                fields.push(viewReferences.index[part].addition);
              }
              getFields(database, remainingParts, fields);
              return;
            }
            var mapOrArrayMatch = part.match(/([^\[]*)\[[^\]]*\]$/i);
            if (mapOrArrayMatch !== null) {
              fields.push(mapOrArrayMatch[1]);
              self.snippet.getApiHelper().fetchFields({
                sourceType: self.snippet.type(),
                databaseName: database,
                tableName: tableName,
                fields: fields,
                editor: editor,
                timeout: self.timeout,
                successCallback: function(data) {
                  if (data.type === "map") {
                    fields.push("value");
                    getFields(database, remainingParts, fields);
                  } else if (data.type === "array") {
                    fields.push("item");
                    getFields(database, remainingParts, fields);
                  } else {
                    onFailure();
                  }
                },
                silenceErrors: true,
                errorCallback: onFailure
              });
              return; // break recursion, it'll be async above
            }
          } else if (impalaSyntax) {
            var isValueCompletion = part == "value" && fields.length > 0 && fields[fields.length - 1] == "value";
            if (!isValueCompletion) {
              fields.push(part);
            }

            var successCallback = function (data) {
              if (data.type === "map") {
                remainingParts.unshift("value");
              } else if (data.type === "array") {
                remainingParts.unshift("item");
              } else if (remainingParts.length == 0 && fields.length > 0) {
                var extraFields = [];
                if (fields[fields.length - 1] == "value") {
                  // impala map completion
                  if (!fieldTermBefore) {
                    extraFields.push({ name: "*", type: "all" });
                  }
                  if (!isValueCompletion) {
                    if (fieldTermBefore || (data.type !== "map" && data.type !== "array" && data.type !== "struct")) {
                      extraFields.push({ name: "value", type: "value" });
                    }
                    extraFields.push({ name: "key", type: "key" });
                  }
                } else if (fields[fields.length - 1] == "item") {
                  if (!fieldTermBefore) {
                    extraFields.push({ name: "*", type: "all" });
                  }
                  if (fieldTermBefore || (data.type !== "map" && data.type !== "array" && data.type !== "struct")) {
                    extraFields.push({ name: "items", type: "items" });
                  }
                }
                callback(self.extractFields(data, tableName, database, "", false, extraFields));
                return;
              }
              getFields(database, remainingParts, fields);
            };
            // For impala we have to fetch info about each field as we don't know
            // whether it's a map or array for hive the [ and ] gives it away...
            self.snippet.getApiHelper().fetchFields({
              sourceType: self.snippet.type(),
              databaseName: database,
              tableName: tableName,
              fields: fields,
              editor: editor,
              timeout: self.timeout,
              successCallback: successCallback,
              silenceErrors: true,
              errorCallback: onFailure
            });
            return; // break recursion, it'll be async above
          }
          fields.push(part);
        }
        getFields(database, remainingParts, fields);
      };

      getFields(database, parts, []);
    } else {
      onFailure();
    }
  };
  
  SqlAutocompleter.prototype.getDocTooltip = function (item) {
    var self = this;
    if (! self.optEnabled) {
      return;
    }
    if (item.meta === 'table' && !item.docHTML) {
      var table = item.value;
      if (table.lastIndexOf(' ') > -1) {
        table = table.substring(table.lastIndexOf(' ') + 1);
      }
      if (self.topTablesPerDb[item.database] && self.topTablesPerDb[item.database][table]) {
        var optData = self.topTablesPerDb[item.database][table];
        item.docHTML = '<table style="margin:10px;">' +
            '<tr style="height: 20px;"><td style="width: 80px;">Table:</td><td style="width: 100px;">' + optData.name + '</td></tr>' +
            '<tr style="height: 20px;"><td style="width: 80px;">Popularity:</td><td style="width: 100px;"><div class="progress" style="height: 10px; width: 100px;"><div class="bar" style="background-color: #0B7FAD; width: ' + optData.popularity + '%" ></div></div></td></tr>' +
            '<tr style="height: 20px;"><td style="width: 80px;">Columns:</td><td style="width: 100px;">' + optData.column_count + '</td></tr>' +
            '<tr style="height: 20px;"><td style="width: 80px;">Fact:</td><td style="width: 100px;">' + optData.is_fact + '</td></tr>' +
            '</table>';

      }
    } else if (item.meta === 'column' && item.popularValues && !item.docHTML) {
      item.docHTML = '<div style="width: 400px; height: 120px; overflow-y: auto;"><div style="margin:10px; font-size: 14px; margin-bottom: 8px;">Popular Values</div><table style="width: 380px; margin: 5px 10px 0 10px;" class="table"><tbody>';
      item.popularValues.forEach(function (value) {
        item.docHTML += '<tr><td><div style=" width: 360px; overflow-x: hidden; font-family: monospace; white-space: nowrap; text-overflow: ellipsis" title="' + value + '">' + value + '</div></td></tr>';
      });
      item.docHTML += '</tbody></table></div>';
    }
    if (item.value.length > 28 && !item.docHTML) {
      item.docHTML = '<div style="margin:10px; width: 220px; overflow-y: auto;"><div style="font-size: 15px; margin-bottom: 6px;">Popular</div><div style="text-wrap: normal; white-space: pre-wrap; font-family: monospace;">' + item.value + '</div></div>';
    }
  };

  return SqlAutocompleter;
})();