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
    var parseResult = sqlParser.parseSql(beforeCursor, afterCursor, self.snippet.type(), sqlFunctions, false);

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

      var foundVarRef = parseResult.colRef.identifierChain.filter(function (identifier) {
        return identifier.name.indexOf('${') === 0;
      });

      if (foundVarRef.length > 0) {
        colRefCallback({ type: 'T' });
      } else {
        self.fetchFieldsForIdentifiers(editor, parseResult.colRef.table, parseResult.colRef.database || database, parseResult.colRef.identifierChain, colRefCallback, colRefDeferral.resolve);
      }

    } else {
      colRefDeferral.resolve();
    }

    if (parseResult.suggestFunctions) {
      var suggestFunctionsDeferral = $.Deferred();
      if (parseResult.suggestFunctions.types && parseResult.suggestFunctions.types[0] === 'COLREF') {
        $.when.apply($, colRefDeferral).done(function () {
          if (colRef !== null) {
            sqlFunctions.suggestFunctions(self.snippet.type(), [colRef.type.toUpperCase()], parseResult.suggestAggregateFunctions || false, parseResult.suggestAnalyticFunctions || false, completions);
          } else {
            sqlFunctions.suggestFunctions(self.snippet.type(), ['T'], parseResult.suggestAggregateFunctions || false, parseResult.suggestAnalyticFunctions || false, completions);
          }
          suggestFunctionsDeferral.resolve();
        });
      } else {
        sqlFunctions.suggestFunctions(self.snippet.type(), parseResult.suggestFunctions.types || ['T'], parseResult.suggestAggregateFunctions || false, parseResult.suggestAnalyticFunctions || false, completions);
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
      deferrals.push(self.addHdfs(parseResult, editor, completions));
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

    // Parser sometimes knows if it's a map or array.
    if (identifierChain.length > 0 && (identifierChain[0].name === 'item' || identifierChain[0].name === 'value')) {
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
            value: prefix + self.backTickIfNeeded(tablesMeta.name),
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

  SqlAutocompleter2.prototype.locateSubQuery = function (subQueries, subQueryName) {
    var foundSubQueries = subQueries.filter(function (knownSubQuery) {
      return knownSubQuery.alias === subQueryName
    });
    if (foundSubQueries.length > 0) {
      return foundSubQueries[0];
    }
    return null;
  };

  SqlAutocompleter2.prototype.addColumns = function (parseResult, editor, database, types, completions) {
    var self = this;
    var addColumnsDeferred = $.Deferred();

    if (parseResult.suggestColumns.subQuery && !parseResult.suggestColumns.identifierChain) {
      var foundSubQuery = self.locateSubQuery(parseResult.subQueries, parseResult.suggestColumns.subQuery);

      var addSubQueryColumns = function (subQueryColumns) {
        subQueryColumns.forEach(function (column) {
          if (column.alias || column.identifierChain) {
            // TODO: Potentially fetch column types for sub-queries, possible performance hit.
            var type = typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
            if (column.alias) {
              completions.push({value: self.backTickIfNeeded(column.alias), meta: type, type: 'column'})
            } else if (column.identifierChain && column.identifierChain.length === 1) {
              completions.push({value: self.backTickIfNeeded(column.identifierChain[0].name), meta: type, type: 'column'})
            }
            addColumnsDeferred.resolve();
            return addColumnsDeferred;
          } else if (column.subQuery && foundSubQuery.subQueries) {
            var foundNestedSubQuery = self.locateSubQuery(foundSubQuery.subQueries, column.subQuery);
            if (foundNestedSubQuery !== null) {
              addSubQueryColumns(foundNestedSubQuery.columns);
            }
          }
        });
      };
      if (foundSubQuery !== null) {
        addSubQueryColumns(foundSubQuery.columns);
      }
    } else {
      var callback = function (data) {
        if (data.extended_columns) {
          data.extended_columns.forEach(function (column) {
            if (column.type.indexOf('map') === 0 && self.snippet.type() === 'hive') {
              completions.push({value: self.backTickIfNeeded(column.name) + '[]', meta: 'map', type: 'column'})
            } else if (column.type.indexOf('map') === 0) {
              completions.push({value: self.backTickIfNeeded(column.name), meta: 'map', type: 'column'})
            } else if (column.type.indexOf('struct') === 0) {
              completions.push({value: self.backTickIfNeeded(column.name), meta: 'struct', type: 'column'})
            } else if (column.type.indexOf('array') === 0 && self.snippet.type() === 'hive') {
              completions.push({value: self.backTickIfNeeded(column.name) + '[]', meta: 'array', type: 'column'})
            } else if (column.type.indexOf('array') === 0) {
              completions.push({value: self.backTickIfNeeded(column.name), meta: 'array', type: 'column'})
            } else if (sqlFunctions.matchesType(self.snippet.type(), types, [column.type.toUpperCase()]) ||
                sqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
              completions.push({value: self.backTickIfNeeded(column.name), meta: column.type, type: 'column'})
            }
          });
        } else if (data.columns) {
          data.columns.forEach(function (column) {
            completions.push({value: self.backTickIfNeeded(column), meta: 'column', type: 'column'})
          });
        }
        if (data.type === 'map' && self.snippet.type() === 'impala') {
          completions.push({value: 'key', meta: 'key', type: 'column'});
          completions.push({value: 'value', meta: 'value', type: 'column'});
        }
        if (data.type === 'struct') {
          data.fields.forEach(function (field) {
            completions.push({value: self.backTickIfNeeded(field.name), meta: 'struct', type: 'column'})
          });
        } else if (data.type === 'map' && (data.value && data.value.fields)) {
          data.value.fields.forEach(function (field) {
            if (sqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
                sqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
              completions.push({value: self.backTickIfNeeded(field.name), meta: field.type, type: 'column'});
            }
          });
        } else if (data.type === 'array' && (data.item && data.item.fields)) {
          data.item.fields.forEach(function (field) {
            if ((field.type === 'array' || field.type === 'map')) {
              if (self.snippet.type() === 'hive') {
                completions.push({value: self.backTickIfNeeded(field.name) + '[]', meta: field.type, type: 'column'});
              } else {
                completions.push({value: self.backTickIfNeeded(field.name), meta: field.type, type: 'column'});
              }
            } else if (sqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
                sqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
              completions.push({value: self.backTickIfNeeded(field.name), meta: field.type, type: 'column'});
            }
          });
        }
        addColumnsDeferred.resolve();
      };

      self.fetchFieldsForIdentifiers(editor, parseResult.suggestColumns.table, parseResult.suggestColumns.database || database, parseResult.suggestColumns.identifierChain, callback, addColumnsDeferred.resolve);
    }
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
            value: prefix + self.backTickIfNeeded(db) + (parseResult.suggestDatabases.appendDot ? '.' : ''),
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

  SqlAutocompleter2.prototype.addHdfs = function (parseResult, editor, completions) {
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

  var hiveReservedKeywords = {
    ALL: true, ALTER: true, AND: true, ARRAY: true, AS: true, AUTHORIZATION: true, BETWEEN: true, BIGINT: true, BINARY: true, BOOLEAN: true, BOTH: true, BY: true, CASE: true, CAST: true, 
    CHAR: true, COLUMN: true, CONF: true, CREATE: true, CROSS: true, CUBE: true, CURRENT: true, CURRENT_DATE: true, CURRENT_TIMESTAMP: true, CURSOR: true, 
    DATABASE: true, DATE: true, DECIMAL: true, DELETE: true, DESCRIBE: true, DISTINCT: true, DOUBLE: true, DROP: true, ELSE: true, END: true, EXCHANGE: true, EXISTS: true, 
    EXTENDED: true, EXTERNAL: true, FALSE: true, FETCH: true, FLOAT: true, FOLLOWING: true, FOR: true, FROM: true, FULL: true, FUNCTION: true, GRANT: true, GROUP: true, 
    GROUPING: true, HAVING: true, IF: true, IMPORT: true, IN: true, INNER: true, INSERT: true, INT: true, INTERSECT: true, INTERVAL: true, INTO: true, IS: true, JOIN: true, LATERAL: true, 
    LEFT: true, LESS: true, LIKE: true, LOCAL: true, MACRO: true, MAP: true, MORE: true, NONE: true, NOT: true, NULL: true, OF: true, ON: true, OR: true, ORDER: true, OUT: true, OUTER: true, OVER: true, 
    PARTIALSCAN: true, PARTITION: true, PERCENT: true, PRECEDING: true, PRESERVE: true, PROCEDURE: true, RANGE: true, READS: true, REDUCE: true, 
    REGEXP: true, REVOKE: true, RIGHT: true, RLIKE: true, ROLLUP: true, ROW: true, ROWS: true, 
    SELECT: true, SET: true, SMALLINT: true, TABLE: true, TABLESAMPLE: true, THEN: true, TIMESTAMP: true, TO: true, TRANSFORM: true, TRIGGER: true, TRUE: true, 
    TRUNCATE: true, UNBOUNDED: true, UNION: true, UNIQUEJOIN: true, UPDATE: true, USER: true, USING: true, VALUES: true, VARCHAR: true, WHEN: true, WHERE: true, 
    WINDOW: true, WITH: true
  };

  var extraHiveReservedKeywords = {
    ASC: true, DESC: true, FORMATTED: true, FUNCTION: true, INDEX: true, INDEXES: true, LIMIT: true, SCHEMA: true
  };

  var impalaReservedKeywords = {
    ADD: true, AGGREGATE: true, ALL: true, ALTER: true, AND: true, API_VERSION: true, AS: true, ASC: true, AVRO: true, BETWEEN: true, BIGINT: true, BINARY: true, BOOLEAN: true, BY: true, CACHED: true, CASE: true, CAST: true, CHANGE: true, CHAR: true, CLASS: true, CLOSE_FN: true,
    COLUMN: true, COLUMNS: true, COMMENT: true, COMPUTE: true, CREATE: true, CROSS: true, DATA: true, DATABASE: true, DATABASES: true, DATE: true, DATETIME: true, DECIMAL: true, DELIMITED: true, DESC: true, DESCRIBE: true, DISTINCT: true, DIV: true, DOUBLE: true, DROP: true, ELSE: true, END: true,
    ESCAPED: true, EXISTS: true, EXPLAIN: true, EXTERNAL: true, FALSE: true, FIELDS: true, FILEFORMAT: true, FINALIZE_FN: true, FIRST: true, FLOAT: true, FORMAT: true, FORMATTED: true, FROM: true, FULL: true, FUNCTION: true, FUNCTIONS: true, GROUP: true, HAVING: true, IF: true, IN: true, INCREMENTAL: true,
    INIT_FN: true, INNER: true, INPATH: true, INSERT: true, INT: true, INTEGER: true, INTERMEDIATE: true, INTERVAL: true, INTO: true, INVALIDATE: true, IS: true, JOIN: true, LAST: true, LEFT: true, LIKE: true, LIMIT: true, LINES: true, LOAD: true, LOCATION: true, MERGE_FN: true, METADATA: true,
    NOT: true, NULL: true, NULLS: true, OFFSET: true, ON: true, OR: true, ORDER: true, OUTER: true, OVERWRITE: true, PARQUET: true, PARQUETFILE: true, PARTITION: true, PARTITIONED: true, PARTITIONS: true, PREPARE_FN: true, PRODUCED: true, RCFILE: true, REAL: true, REFRESH: true, REGEXP: true, RENAME: true,
    REPLACE: true, RETURNS: true, RIGHT: true, RLIKE: true, ROW: true, SCHEMA: true, SCHEMAS: true, SELECT: true, SEMI: true, SEQUENCEFILE: true, SERDEPROPERTIES: true, SERIALIZE_FN: true, SET: true, SHOW: true, SMALLINT: true, STATS: true, STORED: true, STRAIGHT_JOIN: true, STRING: true, SYMBOL: true, TABLE: true,
    TABLES: true, TBLPROPERTIES: true, TERMINATED: true, TEXTFILE: true, THEN: true, TIMESTAMP: true, TINYINT: true, TO: true, TRUE: true, UNCACHED: true, UNION: true, UPDATE_FN: true, USE: true, USING: true, VALUES: true, VIEW: true, WHEN: true, WHERE: true, WITH: true,
  };

  SqlAutocompleter2.prototype.backTickIfNeeded = function (text) {
    var self = this;
    if (text.indexOf('`') === 0) {
      return text;
    }
    var upperText = text.toUpperCase();
    if (self.snippet.type() === 'hive' && (hiveReservedKeywords[upperText] || extraHiveReservedKeywords[upperText])) {
      return '`' + text + '`';
    } else if (self.snippet.type() === 'impala' && impalaReservedKeywords[upperText]) {
      return '`' + text + '`';
    } else if (impalaReservedKeywords[upperText] || hiveReservedKeywords[upperText] || extraHiveReservedKeywords[upperText]) {
      return '`' + text + '`';
    } else if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(text)) {
      return '`' + text + '`';
    }
    return text;
  };

  return SqlAutocompleter2;
}));