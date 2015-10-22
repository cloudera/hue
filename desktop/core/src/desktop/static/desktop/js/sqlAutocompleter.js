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
    root.SqlAutocompleter = factory();
  }
}(this, function () {

  var SQL_TERMS = /\b(FROM|TABLE|STATS|REFRESH|METADATA|DESCRIBE|ORDER BY|JOIN|ON|WHERE|SELECT|LIMIT|GROUP|SORT)\b/g;

  /**
   * @param options {object}
   * @param options.assistHelper
   *
   * @constructor
   */
  function SqlAutocompleter(options) {
    var self = this;
    self.snippet = options.snippet;

    var initDatabases = function () {
      if (! self.snippet.getAssistHelper().loaded()) {
        self.snippet.getAssistHelper().load(self.snippet);
      }
    };
    self.snippet.type.subscribe(function() {
      if (self.snippet.isSqlDialect()) {
        initDatabases();
      }
    });
    initDatabases();
  }

  SqlAutocompleter.prototype.getFromReferenceIndex = function (statement) {
    var result = {
      tables: {},
      complex: {}
    };
    var fromMatch = statement.match(/\s*from\s*([^;]*).*$/i);
    if (fromMatch) {
      var refsRaw = fromMatch[1];
      var upToMatch = refsRaw.match(/\bLATERAL|VIEW|EXPLODE|POSEXPLODE|ON|LIMIT|WHERE|GROUP|SORT|ORDER BY\b/i);
      if (upToMatch) {
        refsRaw = $.trim(refsRaw.substring(0, upToMatch.index));
      }
      var refs = refsRaw.split(/\s*(?:,|\bJOIN\b)\s*/i);
      refs.sort();
      $.each(refs, function(index, tableRefRaw) {
        if (tableRefRaw.indexOf('(') == -1) {
          var refMatch = tableRefRaw.match(/\s*(\S+)\s*(\S+)?\s*/);

          var refParts = refMatch[1].split('.');
          if (refMatch[2]) {
            if (refParts.length == 1) {
              result.tables[refMatch[2]] = refParts[0];
            } else {
              result.complex[refMatch[2]] = refParts;
            }
          } else {
            result.tables[refMatch[1]] = refMatch[1];
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

  SqlAutocompleter.prototype.getValueReferences = function (conditionMatch, fromReferences, tableAndComplexRefs, callback) {
    var self = this;

    var fields = conditionMatch[1].split(".");
    var tableName = null;
    if (fields[0] in fromReferences.complex) {
      var complexRef = fields.shift();
      fields = fromReferences.complex[complexRef].concat(fields);
    }
    if (fields[0] in fromReferences.tables) {
      tableName = fromReferences.tables[fields.shift()];
    }
    if (! tableName && tableAndComplexRefs.length === 1) {
      tableName = tableAndComplexRefs[0].value;
    }
    if (tableName) {
      self.snippet.getAssistHelper().fetchFields(self.snippet, tableName, fields, function(data) {
        if (data.sample) {
          var isString = data.type === "string";
          var values = $.map(data.sample.sort(), function(value, index) {
            return {
              meta: "value",
              score: 900 - index,
              value: isString ? "'" + value + "'" : new String(value)
            }
          });
          callback(tableAndComplexRefs.concat(values));
        } else {
          callback(tableAndComplexRefs);
        }
      });
      return;
    }
  };

  SqlAutocompleter.prototype.extractFields = function (data, valuePrefix, includeStar, extraSuggestions) {
    var fields = [];
    var result = [];

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
    } else if (typeof data.tables != "undefined") {
      fields = $.map(data.tables, function(table) {
        return {
          name: table,
          type: "table"
        }
      });
    }

    fields.sort(function (a, b) {
      return a.name.localeCompare(b.name);
    });

    if (extraSuggestions) {
      extraSuggestions.sort(function (a, b) {
        return a.name.localeCompare(b.name);
      });
      fields = extraSuggestions.concat(fields);
    }

    fields.forEach(function(field, idx) {
      if (field.name != "") {
        result.push({value: typeof valuePrefix != "undefined" ? valuePrefix + field.name : field.name, score: 1000 - idx, meta: field.type});
      }
    });
    return result;
  };

  SqlAutocompleter.prototype.autocomplete = function(beforeCursor, afterCursor, callback, editor) {
    var onFailure = function() {
      callback([]);
    };

    var self = this;

    var hiveSyntax = self.snippet.type() === "hive";
    var impalaSyntax = self.snippet.type() === "impala";

    if (typeof self.snippet.getAssistHelper().activeDatabase() == "undefined"
      || self.snippet.getAssistHelper().activeDatabase() == null
      || self.snippet.getAssistHelper().activeDatabase() == "") {
      onFailure();
      return;
    }

    var beforeCursorU = beforeCursor.toUpperCase();
    var afterCursorU = afterCursor.toUpperCase();

    var beforeMatcher = beforeCursorU.match(SQL_TERMS);
    var afterMatcher = afterCursorU.match(SQL_TERMS);

    if (beforeMatcher == null || beforeMatcher.length == 0) {
      callback([]);
      return;
    }

    var keywordBeforeCursor = beforeMatcher[beforeMatcher.length - 1];

    var impalaFieldRef = impalaSyntax && beforeCursor.slice(-1) === '.';

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
      keywordBeforeCursor === "ORDER BY";

    var fromAfter = afterMatcher != null && afterMatcher[0] === "FROM";

    if (tableNameAutoComplete || (selectBefore && !fromAfter)) {

      self.snippet.getAssistHelper().fetchTables(self.snippet, function (data) {
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
        callback(self.extractFields(data, fromKeyword));
      }, onFailure, editor);
    } else if ((selectBefore && fromAfter) || fieldTermBefore || impalaFieldRef) {
      var partialTermsMatch = beforeCursor.match(/([^\s\(\-\+\<\>\,]*)$/);
      var parts = partialTermsMatch ? partialTermsMatch[0].split(".") : [];

      // Drop the last part, empty or not. If it's not empty it's the start of a
      // field (or a complete one) for that case we suggest the same.
      // SELECT tablename.colu => suggestion: "column"
      parts.pop();

      var fromReferences = self.getFromReferenceIndex(beforeCursor + afterCursor);
      var viewReferences = self.getViewReferenceIndex(beforeCursor + afterCursor, hiveSyntax);
      var conditionMatch = beforeCursor.match(/(\S+)\s*=\s*$/);

      var tableName = "";

      if (parts.length > 0 && fromReferences.tables[parts[0]]) {
        // SELECT tableref.column.
        tableName = fromReferences.tables[parts.shift()];
      } else if (parts.length > 0 && fromReferences.complex[parts[0]]) {
        var complexRefList = fromReferences.complex[parts.shift()];
        if (fromReferences.tables[complexRefList[0]]) {
          tableName = fromReferences.tables[complexRefList[0]];
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
            value: key + (afterCursor.indexOf(".") == 0 ? "" : "."),
            score: 1000 - count++,
            meta: fromReferences.tables[key] == key ? 'table' : 'alias'
          };
        });

        var complexRefs = $.map(Object.keys(fromReferences.complex), function (key, idx) {
          return {
            value: key + (afterCursor.indexOf(".") == 0 ? "" : "."),
            score: 1000 - count++,
            meta: 'alias'
          };
        });

        if (conditionMatch && impalaSyntax) {
          self.getValueReferences(conditionMatch, fromReferences, tableRefs.concat(complexRefs), callback);
        } else {
          callback(tableRefs.concat(complexRefs));
        }
        return;
      } else if (Object.keys(fromReferences.tables).length == 1) {
        // SELECT column. or just SELECT
        // We use first and only table reference if exist
        // if there are no parts the call to getFields will fetch the columns
        tableName = fromReferences.tables[Object.keys(fromReferences.tables)[0]];
        if (conditionMatch && impalaSyntax) {
          var tableRefs = [{
            value: tableName,
            score: 1000,
            meta: 'table'
          }];
          self.getValueReferences(conditionMatch, fromReferences, tableRefs, callback);
          return;
        }
      } else if (parts.length > 0 && viewReferences.index[parts[0]] && viewReferences.index[parts[0]].leadingPath.length > 0) {
        tableName = fromReferences.tables[viewReferences.index[parts[0]].leadingPath[0]];
      } else {
        // Can't complete without table reference
        onFailure();
        return;
      }

      var getFields = function (remainingParts, fields) {
        if (remainingParts.length == 0) {
          self.snippet.getAssistHelper().fetchFields(self.snippet, tableName, fields, function(data) {
            if (fields.length == 0) {
              callback(self.extractFields(data, "", !fieldTermBefore && !impalaFieldRef, viewReferences.allViewReferences));
            } else {
              callback(self.extractFields(data, "", !fieldTermBefore));
            }
          }, onFailure, editor);
          return; // break recursion
        }
        var part = remainingParts.shift();

        if (part != '' && part !== tableName) {
          if (hiveSyntax) {
            if (viewReferences.index[part]) {
              if (viewReferences.index[part].references && remainingParts.length == 0) {
                callback(self.extractFields([], "", true, viewReferences.index[part].references));
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
              getFields(remainingParts, fields);
              return;
            }
            var mapOrArrayMatch = part.match(/([^\[]*)\[[^\]]*\]$/i);
            if (mapOrArrayMatch !== null) {
              fields.push(mapOrArrayMatch[1]);
              self.snippet.getAssistHelper().fetchFields(self.snippet, tableName, fields, function(data) {
                if (data.type === "map") {
                  fields.push("value");
                  getFields(remainingParts, fields);
                } else if (data.type === "array") {
                  fields.push("item");
                  getFields(remainingParts, fields);
                } else {
                  onFailure();
                }
              }, onFailure, editor);
              return; // break recursion, it'll be async above
            }
          } else if (impalaSyntax) {
            var isValueCompletion = part == "value" && fields.length > 0 && fields[fields.length - 1] == "value";
            if (!isValueCompletion) {
              fields.push(part);
            }
            // For impala we have to fetch info about each field as we don't know
            // whether it's a map or array for hive the [ and ] gives it away...
            self.snippet.getAssistHelper().fetchFields(self.snippet, tableName, fields, function(data) {
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
                callback(self.extractFields(data, "", false, extraFields));
                return;
              }
              getFields(remainingParts, fields);
            }, onFailure, editor);
            return; // break recursion, it'll be async above
          }
          fields.push(part);
        }
        getFields(remainingParts, fields);
      };

      getFields(parts, []);
    } else {
      onFailure();
    }
  };

  return SqlAutocompleter;
}));