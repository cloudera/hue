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

var SqlAutocompleter3 = (function () {

  // Keyword weights come from the parser
  var DEFAULT_WEIGHTS = {
    POPULAR_AGGREGATE: 1500,
    POPULAR_GROUP_BY: 1400,
    POPULAR_ORDER_BY: 1300,
    POPULAR_FILTER: 1200,
    POPULAR_ACTIVE_JOIN: 1200,
    POPULAR_JOIN_CONDITION: 1100,
    COLUMN: 1000,
    SAMPLE: 900,
    IDENTIFIER: 800,
    CTE: 700,
    TABLE: 600,
    DATABASE: 500,
    UDF: 400,
    HDFS: 300,
    VIRTUAL_COLUMN: 200,
    COLREF_KEYWORD: 100,
    VARIABLE: 50,
    JOIN: -1
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
    ASC: true, CLUSTER: true, DESC: true, DISTRIBUTE: true, FORMATTED: true, FUNCTION: true, INDEX: true, INDEXES: true, LIMIT: true, LOCK: true, SCHEMA: true, SORT: true
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

  var backTickIfNeeded = function (sourceType, text) {
    if (text.indexOf('`') === 0) {
      return text;
    }
    var upperText = text.toUpperCase();
    if (sourceType === 'hive' && (hiveReservedKeywords[upperText] || extraHiveReservedKeywords[upperText])) {
      return '`' + text + '`';
    } else if (sourceType === 'impala' && impalaReservedKeywords[upperText]) {
      return '`' + text + '`';
    } else if (impalaReservedKeywords[upperText] || hiveReservedKeywords[upperText] || extraHiveReservedKeywords[upperText]) {
      return '`' + text + '`';
    } else if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(text)) {
      return '`' + text + '`';
    }
    return text;
  };

  /**
   * Represents a single suggestion
   *
   * @param value
   * @param meta
   * @param weight
   * @constructor
   */
  function Suggestion (value, meta, weight) {
    var self = this;
    self.value = value;
    self.meta = meta;
    self.weight = weight;
  }

  /**
   *
   * @param options
   * @constructor
   */
  function Suggestions (options) {
    var self = this;
    self.apiHelper = ApiHelper.getInstance();
    self.snippet = options.snippet;

    self.keywords = ko.observableArray();
    self.loadingKeywords = ko.observable(false);

    self.tables = ko.observableArray();
    self.loadingTables = ko.observable(false);

    self.columns = ko.observableArray();
    self.loadingColumns = ko.observable(false);

    self.filter = ko.observable();

    self.filtered = ko.pureComputed(function () {
      var result = self.keywords().concat(self.tables(), self.columns());

      if (self.filter()) {
        var lowerCaseFilter = self.filter().toLowerCase();
        result = result.filter(function (suggestion) {
          // TODO: Extend with fuzzy matches
          var foundIndex = suggestion.value.toLowerCase().indexOf(lowerCaseFilter);
          if (foundIndex === -1) {
            return false;
          }
          if (foundIndex === 0) {
            suggestion.sortWeight = 2;
          } else if (foundIndex > 0) {
            suggestion.sortWeight = 1;
          }
          suggestion.matchIndex = foundIndex;
          suggestion.matchLength = self.filter().length;
          return true;
        });
      }
      result.sort(function (a, b) {
        if (self.filter()) {
          if (typeof a.sortWeight !== 'undefined' && typeof b.sortWeight !== 'undefined' && b.sortWeight !== a.sortWeight) {
            return b.sortWeight - a.sortWeight;
          }
          if (typeof a.sortWeight !== 'undefined' && typeof b.sortWeight === 'undefined') {
            return -1;
          }
          if (typeof a.sortWeight === 'undefined' && typeof b.sortWeight !== 'undefined') {
            return 1;
          }
        }
        if (typeof a.weight !== 'undefined' && typeof b.weight !== 'undefined' && b.weight !== a.weight) {
          return b.weight - a.weight;
        }
        if (typeof a.weight !== 'undefined' && typeof b.weight === 'undefined') {
          return -1;
        }
        if (typeof a.weight === 'undefined' && typeof b.weight !== 'undefined') {
          return 1;
        }
        return a.value.localeCompare(b.value);
      });
      return result;
    });
  }

  Suggestions.prototype.update = function (parseResult) {
    var self = this;
    self.defaultDatabase = parseResult.useDatabase || self.snippet.database();
    self.parseResult = parseResult;
    self.keywords([]);
    self.tables([]);
    self.columns([]);
    self.loadingKeywords(false);
    self.loadingTables(false);
    self.loadingColumns(false);
    self.filter('');

    var colRefDeferral = self.handleColumnReference();
    var allDbsDeferral = self.loadDatabases();

    self.handleKeywords(colRefDeferral);
    self.handleTables(allDbsDeferral);
  };

  Suggestions.prototype.loadDatabases = function () {
    var self = this;
    var dbsDeferral = $.Deferred();
    self.apiHelper.loadDatabases({
      sourceType: self.snippet.type(),
      successCallback: dbsDeferral.resolve,
      timeout: AUTOCOMPLETE_TIMEOUT,
      silenceErrors: true,
      errorCallback: function () {
        dbsDeferral.resolve([]);
      }
    });
    return dbsDeferral;
  };

  Suggestions.prototype.handleKeywords = function (colRefDeferral) {
    var self = this;
    if (self.parseResult.suggestKeywords) {
      var keywordSuggestions = $.map(self.parseResult.suggestKeywords, function (keyword) {
        return new Suggestion(self.parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value, AutocompleterGlobals.i18n.meta.keyword, keyword.weight);
      });
      self.keywords(keywordSuggestions);
    }

    if (self.parseResult.suggestColRefKeywords) {
      self.loadingKeywords(true);
      // Wait for the column reference type to be resolved to pick the right keywords
      colRefDeferral.done(function (colRef) {
        if (colRef !== null) {
          var keywordSuggestions = self.keywords();
          Object.keys(self.parseResult.suggestColRefKeywords).forEach(function (typeForKeywords) {
            if (SqlFunctions.matchesType(sourceType, [typeForKeywords], [type.toUpperCase()])) {
              self.parseResult.suggestColRefKeywords[typeForKeywords].forEach(function (keyword) {
                keywordSuggestions.push(new Suggestion(self.parseResult.lowerCase ? keyword.toLowerCase() : keyword, AutocompleterGlobals.i18n.meta.keyword, DEFAULT_WEIGHTS.COLREF_KEYWORD));
              })
            }
          });
          self.keywords(keywordSuggestions);
        }
        self.loadingKeywords(false);
      });
    }
  };

  Suggestions.prototype.handleTables = function (allDbsDeferral, colRefDeferral) {
    var self = this;
    if (self.parseResult.suggestTables) {
      var suggestTables = self.parseResult.suggestTables;
      var fetchTables = function () {
        self.loadingTables(true);
        var prefix = suggestTables.prependQuestionMark ? '? ' : '';
        if (suggestTables.prependFrom) {
          prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
        }

        self.apiHelper.fetchTables({
          sourceType: self.snippet.type(),
          databaseName: suggestTables.identifierChain && suggestTables.identifierChain.length === 1 ? suggestTables.identifierChain[0].name : self.defaultDatabase,
          successCallback: function (data) {
            var tableSuggestions = [];
            data.tables_meta.forEach(function (tablesMeta) {
              if (suggestTables.onlyTables && tablesMeta.type.toLowerCase() !== 'table' ||
                  suggestTables.onlyViews && tablesMeta.type.toLowerCase() !== 'view') {
                return;
              }
              tableSuggestions.push(new Suggestion(prefix + backTickIfNeeded(self.snippet.type(), tablesMeta.name), AutocompleterGlobals.i18n.meta[tablesMeta.type.toLowerCase()], DEFAULT_WEIGHTS.TABLE));
            });
            self.loadingTables(false);
            self.tables(tableSuggestions);
          },
          silenceErrors: true,
          errorCallback: function () {
            self.loadingTables(false);
          },
          timeout: AUTOCOMPLETE_TIMEOUT
        });
      };

      if (self.snippet.type() == 'impala' && self.parseResult.suggestTables.identifierChain && self.parseResult.suggestTables.identifierChain.length === 1) {
        allDbsDeferral.done(function (databases) {
          var foundDb = databases.filter(function (db) {
            return db.toLowerCase() === self.parseResult.suggestTables.identifierChain[0].name.toLowerCase();
          });
          if (foundDb.length > 0) {
            fetchTables();
          } else {
            self.parseResult.suggestColumns = { tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }] };
            self.handleColumns(colRefDeferral);
          }
        });
      } else if (self.snippet.type() == 'impala' && self.parseResult.suggestTables.identifierChain && self.parseResult.suggestTables.identifierChain.length > 1) {
        self.parseResult.suggestColumns = { tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }] };
        self.handleColumns(colRefDeferral);
      } else {
        fetchTables();
      }
    }
  };

  Suggestions.prototype.handleColumns = function (colRefDeferral) {

  };

  /**
   * For some suggestions the column type is needed, for instance with functions we should only suggest
   * columns that matches the argument type, cos(|) etc.
   *
   * The deferred will always resolve, and the default values is { type: 'T' }
   *
   * @returns {object} - jQuery Deferred
   */
  Suggestions.prototype.handleColumnReference = function () {
    var self = this;
    var colRefDeferral = $.Deferred();
    if (self.parseResult.colRef) {
      var colRefCallback = function (data) {
        if (typeof data.type !== 'undefined') {
          colRefDeferral.resolve(data);
        } else if (typeof data.extended_columns !== 'undefined' && data.extended_columns.length === 1) {
          colRefDeferral.resolve(data.extended_columns[0]);
        }
      };

      var foundVarRef = self.parseResult.colRef.identifierChain.filter(function (identifier) {
        return typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0;
      });

      if (foundVarRef.length > 0) {
        colRefDeferral.resolve({ type: 'T' });
      } else {
        self.fetchFieldsForIdentifiers(self.parseResult.colRef.identifierChain, colRefCallback, function () {
          colRefDeferral.resolve({ type: 'T' });
        });
      }
    } else {
      colRefDeferral.resolve({ type: 'T' });
    }
    return colRefDeferral;
  };

  /**
   * Helper function to fetch columns/fields given an identifierChain, this also takes care of expanding arrays
   * and maps to match the required format for the API.
   *
   * @param originalIdentifierChain
   * @param callback
   * @param errorCallback
   */

  Suggestions.prototype.fetchFieldsForIdentifiers = function (originalIdentifierChain, callback, errorCallback) {
    var self = this;
    var identifierChain = originalIdentifierChain.concat();

    var fetchFieldsInternal =  function (table, database, identifierChain, callback, errorCallback, fetchedFields) {
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

      self.apiHelper.fetchFields({
        sourceType: self.snippet.type(),
        databaseName: database,
        tableName: table,
        fields: fetchedFields,
        timeout: AUTOCOMPLETE_TIMEOUT,
        successCallback: function (data) {
          if (self.snippet.type() === 'hive'
              && typeof data.extended_columns !== 'undefined'
              && data.extended_columns.length === 1
              && data.extended_columns.length
              && /^map|array|struct/i.test(data.extended_columns[0].type)) {
            identifierChain.unshift({ name: data.extended_columns[0].name })
          }
          if (identifierChain.length > 0) {
            if (typeof identifierChain[0].name !== 'undefined' && /value|item|key/i.test(identifierChain[0].name)) {
              fetchedFields.push(identifierChain[0].name);
              identifierChain.shift();
            } else {
              if (data.type === 'array') {
                fetchedFields.push('item')
              }
              if (data.type === 'map') {
                fetchedFields.push('value')
              }
            }
            fetchFieldsInternal(table, database, identifierChain, callback, errorCallback, fetchedFields)
          } else {
            callback(data);
          }
        },
        silenceErrors: true,
        errorCallback: errorCallback
      });
    };

    // For Impala the first parts of the identifier chain could be either database or table, either:
    // SELECT | FROM database.table -or- SELECT | FROM table.column

    // For Hive it could be either:
    // SELECT col.struct FROM db.tbl -or- SELECT col.struct FROM tbl
    if (self.snippet.type() === 'impala' || self.snippet.type() === 'hive') {
      if (identifierChain.length > 1) {
        self.apiHelper.loadDatabases({
          sourceType: self.snippet.type(),
          timeout: AUTOCOMPLETE_TIMEOUT,
          successCallback: function (data) {
            var foundDb = data.filter(function (db) {
              return db.toLowerCase() === identifierChain[0].name.toLowerCase();
            });
            var databaseName = foundDb.length > 0 ? identifierChain.shift().name : self.defaultDatabase;
            var tableName = identifierChain.shift().name;
            fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
          },
          silenceErrors: true,
          errorCallback: errorCallback
        });
      } else {
        var databaseName = self.defaultDatabase;
        var tableName = identifierChain.shift().name;
        fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
      }
    } else {
      var databaseName = identifierChain.length > 1 ? identifierChain.shift().name : self.defaultDatabase;
      var tableName = identifierChain.shift().name;
      fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
    }
  };

  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @constructor
   */
  function SqlAutocompleter3(options) {
    var self = this;
    self.snippet = options.snippet;
    self.editor = options.editor;
    self.suggestions = new Suggestions(options);
  }

  SqlAutocompleter3.prototype.autocomplete = function () {
    var self = this;
    var parseResult = sql.parseSql(self.editor().getTextBeforeCursor(), self.editor().getTextAfterCursor(), self.snippet.type(), false);

    if (typeof hueDebug !== 'undefined' && hueDebug.showParseResult) {
      console.log(parseResult);
    }

    self.suggestions.update(parseResult);
  };

  return SqlAutocompleter3;
})();