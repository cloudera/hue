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

  var normalizedColors = HueColors.getNormalizedColors();

  var COLORS = {
    POPULAR: normalizedColors['blue'][7],
    KEYWORD: normalizedColors['blue'][4],
    COLUMN: normalizedColors['green'][2],
    TABLE: normalizedColors['pink'][3],
    DATABASE: normalizedColors['teal'][5],
    SAMPLE: normalizedColors['purple'][5],
    IDENT_CTE_VAR: normalizedColors['orange'][3],
    UDF: normalizedColors['purple-gray'][3],
    HDFS: normalizedColors['red'][2]
  };

  var CATEGORIES = {
    ALL: { color: HueColors.BLUE, label: AutocompleterGlobals.i18n.category.all },
    POPULAR: { color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular },
    POPULAR_AGGREGATE: { weight: 1500, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'agg-udf' },
    POPULAR_GROUP_BY: { weight: 1400, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'group-by' },
    POPULAR_ORDER_BY: { weight: 1300, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'order-by' },
    POPULAR_FILTER: { weight: 1200, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'filter' },
    POPULAR_ACTIVE_JOIN: { weight: 1200, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'join' },
    POPULAR_JOIN_CONDITION: { weight: 1100, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'join-condition' },
    COLUMN: { weight: 1000, color: COLORS.COLUMN, label: AutocompleterGlobals.i18n.category.column, detailsTemplate: 'column' },
    SAMPLE: { weight: 900, color: COLORS.SAMPLE, label: AutocompleterGlobals.i18n.category.sample, detailsTemplate: 'value' },
    IDENTIFIER: { weight: 800, color: COLORS.IDENT_CTE_VAR, label: AutocompleterGlobals.i18n.category.identifier, detailsTemplate: 'identifier' },
    CTE: { weight: 700, color: COLORS.IDENT_CTE_VAR, label: AutocompleterGlobals.i18n.category.cte, detailsTemplate: 'cte' },
    TABLE: { weight: 600, color: COLORS.TABLE, label: AutocompleterGlobals.i18n.category.table, detailsTemplate: 'table' },
    DATABASE: { weight: 500, color: COLORS.DATABASE, label: AutocompleterGlobals.i18n.category.database, detailsTemplate: 'database' },
    UDF: { weight: 400, color: COLORS.UDF, label: AutocompleterGlobals.i18n.category.udf, detailsTemplate: 'udf' },
    HDFS: { weight: 300, color: COLORS.HDFS, label: AutocompleterGlobals.i18n.category.hdfs, detailsTemplate: 'hdfs' },
    VIRTUAL_COLUMN: { weight: 200, color: COLORS.COLUMN, label: AutocompleterGlobals.i18n.category.column, detailsTemplate: 'column' },
    COLREF_KEYWORD: { weight: 100, color: COLORS.KEYWORD, label: AutocompleterGlobals.i18n.category.keyword, detailsTemplate: 'keyword' },
    VARIABLE: { weight: 50, color: COLORS.IDENT_CTE_VAR, label: AutocompleterGlobals.i18n.category.variable, detailsTemplate: 'variable' },
    KEYWORD: { weight: 0, color: COLORS.KEYWORD, label: AutocompleterGlobals.i18n.category.keyword, detailsTemplate: 'keyword' },
    POPULAR_JOIN: { weight: -1, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'join' }
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
    INIT_FN: true, INNER: true, INPATH: true, INSERT: true, INT: true, INTEGER: true, INTERMEDIATE: true, INTERVAL: true, INTO: true, INVALIDATE: true, IS: true, JOIN: true, KEY: true, KUDU: true, LAST: true, LEFT: true, LIKE: true, LIMIT: true, LINES: true, LOAD: true, LOCATION: true, MERGE_FN: true, METADATA: true,
    NOT: true, NULL: true, NULLS: true, OFFSET: true, ON: true, OR: true, ORDER: true, OUTER: true, OVERWRITE: true, PARQUET: true, PARQUETFILE: true, PARTITION: true, PARTITIONED: true, PARTITIONS: true, PREPARE_FN: true, PRIMARY: true, PRODUCED: true, RCFILE: true, REAL: true, REFRESH: true, REGEXP: true, RENAME: true,
    REPLACE: true, RETURNS: true, RIGHT: true, RLIKE: true, ROW: true, SCHEMA: true, SCHEMAS: true, SELECT: true, SEMI: true, SEQUENCEFILE: true, SERDEPROPERTIES: true, SERIALIZE_FN: true, SET: true, SHOW: true, SMALLINT: true, STATS: true, STORED: true, STRAIGHT_JOIN: true, STRING: true, SYMBOL: true, TABLE: true,
    TABLES: true, TBLPROPERTIES: true, TERMINATED: true, TEXTFILE: true, THEN: true, TIMESTAMP: true, TINYINT: true, TO: true, TRUE: true, UNCACHED: true, UNION: true, UPDATE_FN: true, USE: true, USING: true, VALUES: true, VIEW: true, WHEN: true, WHERE: true, WITH: true
  };

  /**
   *
   * @param options
   * @constructor
   */
  function Suggestions (options) {
    var self = this;
    self.apiHelper = ApiHelper.getInstance();
    self.snippet = options.snippet;
    self.editor = options.editor;

    self.entries = ko.observableArray();

    self.loadingKeywords = ko.observable(false);
    self.loadingFunctions = ko.observable(false);
    self.loadingDatabases = ko.observable(false);
    self.loadingTables = ko.observable(false);
    self.loadingColumns = ko.observable(false);
    self.loadingValues = ko.observable(false);
    self.loadingPaths = ko.observable(false);
    self.loadingJoins = ko.observable(false);
    self.loadingJoinConditions = ko.observable(false);
    self.loadingAggregateFunctions = ko.observable(false);
    self.loadingGroupBys = ko.observable(false);
    self.loadingOrderBys = ko.observable(false);
    self.loadingFilters = ko.observable(false);
    self.loadingPopularTables = ko.observable(false);
    self.loadingPopularColumns = ko.observable(false);

    self.loading = ko.pureComputed(function () {
      return self.loadingKeywords() || self.loadingFunctions() || self.loadingDatabases() || self.loadingTables() ||
              self.loadingColumns() || self.loadingValues() || self.loadingPaths() || self.loadingJoins() ||
              self.loadingJoinConditions() || self.loadingAggregateFunctions() || self.loadingGroupBys() ||
              self.loadingOrderBys() || self.loadingFilters() || self.loadingPopularTables() ||
              self.loadingPopularColumns();
    }).extend({ rateLimit: 200 });

    self.filter = ko.observable();

    self.availableCategories = ko.observableArray([CATEGORIES.ALL]);

    self.availableCategories.subscribe(function (newCategories) {
      if (newCategories.indexOf(self.activeCategory()) === -1) {
        self.activeCategory(CATEGORIES.ALL)
      }
    });

    self.activeCategory = ko.observable(CATEGORIES.ALL);

    var updateCategories = function (suggestions) {
      var newCategories =  {};
      suggestions.forEach(function (suggestion) {
        if (suggestion.popular && ! newCategories[CATEGORIES.POPULAR.label]) {
          newCategories[CATEGORIES.POPULAR.label] = CATEGORIES.POPULAR;
        } else if (suggestion.category === CATEGORIES.TABLE || suggestion.category === CATEGORIES.COLUMN || suggestion.category === CATEGORIES.UDF) {
          if (!newCategories[suggestion.category.label]) {
            newCategories[suggestion.category.label] = suggestion.category;
          }
        }
      });
      var result = [];
      Object.keys(newCategories).forEach(function (key) {
        result.push(newCategories[key]);
      });
      result.sort(function (a, b) { return a.label.localeCompare(b.label)});
      result.unshift(CATEGORIES.ALL);
      self.availableCategories(result);
    };

    self.filtered = ko.pureComputed(function () {
      var result = self.entries();

      if (self.filter()) {
        var lowerCaseFilter = self.filter().toLowerCase();
        result = result.filter(function (suggestion) {
          // TODO: Extend with fuzzy matches
          var foundIndex = suggestion.value.toLowerCase().indexOf(lowerCaseFilter);
          if (foundIndex === -1) {
            return false;
          }
          if (foundIndex === 0 || (suggestion.filterValue && suggestion.filterValue.toLowerCase().indexOf(lowerCaseFilter) === 0)) {
            suggestion.filterWeight = 2;
          } else if (foundIndex > 0) {
            suggestion.filterWeight = 1;
          }
          suggestion.matchIndex = foundIndex;
          suggestion.matchLength = self.filter().length;
          return true;
        });
        huePubSub.publish('hue.ace.autocompleter.match.updated');
      }
      updateCategories(result);

      var activeCategory = self.activeCategory();
      if (activeCategory !== CATEGORIES.ALL) {
        result = result.filter(function (suggestion) {
          return activeCategory === suggestion.category || (activeCategory === CATEGORIES.POPULAR && suggestion.popular);
        });
      }

      result.sort(function (a, b) {
        if (self.filter()) {
          if (typeof a.filterWeight !== 'undefined' && typeof b.filterWeight !== 'undefined' && b.filterWeight !== a.filterWeight) {
            return b.filterWeight - a.filterWeight;
          }
          if (typeof a.filterWeight !== 'undefined' && typeof b.filterWeight === 'undefined') {
            return -1;
          }
          if (typeof a.filterWeight === 'undefined' && typeof b.filterWeight !== 'undefined') {
            return 1;
          }
        }
        var aWeight = a.category.weight + (a.weightAdjust || 0);
        var bWeight = b.category.weight + (b.weightAdjust || 0);
        if (typeof aWeight !== 'undefined' && typeof bWeight !== 'undefined' && bWeight !== aWeight) {
          return bWeight - aWeight;
        }
        if (typeof aWeight !== 'undefined' && typeof bWeight === 'undefined') {
          return -1;
        }
        if (typeof aWeight === 'undefined' && typeof bWeight !== 'undefined') {
          return 1;
        }
        return a.value.localeCompare(b.value);
      });
      return result;
    }).extend({ rateLimit: 200 });
  }

  Suggestions.prototype.backTickIfNeeded = function (text) {
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

  Suggestions.prototype.update = function (parseResult) {
    var self = this;
    self.activeDatabase = parseResult.useDatabase || self.snippet.database();
    self.parseResult = parseResult;

    self.entries([]);

    self.loadingKeywords(false);
    self.loadingFunctions(false);
    self.loadingDatabases(false);
    self.loadingTables(false);
    self.loadingColumns(false);
    self.loadingValues(false);
    self.loadingPaths(false);
    self.loadingJoins(false);
    self.loadingJoinConditions(false);
    self.loadingAggregateFunctions(false);
    self.loadingGroupBys(false);
    self.loadingOrderBys(false);
    self.loadingFilters(false);
    self.loadingPopularTables(false);
    self.loadingPopularColumns(false);

    self.filter('');

    var colRefDeferred = self.handleColumnReference();
    var databasesDeferred = self.loadDatabases();

    self.handleKeywords(colRefDeferred);
    self.handleIdentifiers();
    self.handleColumnAliases();
    self.handleCommonTableExpressions();
    self.handleFunctions(colRefDeferred);
    self.handleDatabases(databasesDeferred);
    var tablesDeferred = self.handleTables(databasesDeferred);
    var columnsDeferred = self.handleColumns(colRefDeferred, tablesDeferred);
    self.handleValues(colRefDeferred);
    var pathsDeferred = self.handlePaths();

    var joinsDeferred = self.handleJoins();
    var joinConditionsDeferred = self.handleJoinConditions();
    var aggregateFunctionsDeferred = self.handleAggregateFunctions();
    var groupBysDeferred = self.handleGroupBys();
    var orderBysDeferred = self.handleOrderBys();
    var filtersDeferred = self.handleFilters();
    var popularTablesDeferred = self.handlePopularTables(tablesDeferred);
    var popularColumnsDeferred = self.handlePopularColumns(columnsDeferred);

    $.when(colRefDeferred, databasesDeferred, tablesDeferred, columnsDeferred, pathsDeferred, joinsDeferred,
        joinConditionsDeferred, aggregateFunctionsDeferred, groupBysDeferred, orderBysDeferred, filtersDeferred,
        popularTablesDeferred, popularColumnsDeferred).done(function () {
      huePubSub.publish('hue.ace.autocompleter.done');
    });
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
    var colRefDeferred = $.Deferred();
    if (self.parseResult.colRef) {
      var colRefCallback = function (data) {
        if (typeof data.type !== 'undefined') {
          colRefDeferred.resolve(data);
        } else if (typeof data.extended_columns !== 'undefined' && data.extended_columns.length === 1) {
          colRefDeferred.resolve(data.extended_columns[0]);
        } else {
          colRefDeferred.resolve({ type: 'T' })
        }
      };

      var foundVarRef = self.parseResult.colRef.identifierChain.filter(function (identifier) {
        return typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0;
      });

      if (foundVarRef.length > 0) {
        colRefDeferred.resolve({ type: 'T' });
      } else {
        self.fetchFieldsForIdentifiers(self.parseResult.colRef.identifierChain, colRefCallback, function () {
          colRefDeferred.resolve({ type: 'T' });
        });
      }
    } else {
      colRefDeferred.resolve({ type: 'T' });
    }
    return colRefDeferred;
  };

  Suggestions.prototype.loadDatabases = function () {
    var self = this;
    var databasesDeferred = $.Deferred();
    self.apiHelper.loadDatabases({
      sourceType: self.snippet.type(),
      successCallback: databasesDeferred.resolve,
      timeout: AUTOCOMPLETE_TIMEOUT,
      silenceErrors: true,
      errorCallback: function () {
        databasesDeferred.resolve([]);
      }
    });
    return databasesDeferred;
  };

  Suggestions.prototype.handleKeywords = function (colRefDeferred) {
    var self = this;
    if (self.parseResult.suggestKeywords) {
      var keywordSuggestions = $.map(self.parseResult.suggestKeywords, function (keyword) {
        return {
          value: self.parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value,
          meta: AutocompleterGlobals.i18n.meta.keyword,
          category: CATEGORIES.KEYWORD,
          weightAdjust: keyword.weight,
          details: null
        };
      });
      self.entries(self.entries().concat(keywordSuggestions));
    }

    if (self.parseResult.suggestColRefKeywords) {
      self.loadingKeywords(true);
      // Wait for the column reference type to be resolved to pick the right keywords
      colRefDeferred.done(function (colRef) {
        var colRefKeywordSuggestions = self.keywords();
        Object.keys(self.parseResult.suggestColRefKeywords).forEach(function (typeForKeywords) {
          if (SqlFunctions.matchesType(sourceType, [typeForKeywords], [colRef.type.toUpperCase()])) {
            self.parseResult.suggestColRefKeywords[typeForKeywords].forEach(function (keyword) {
              colRefKeywordSuggestions.push({
                value: self.parseResult.lowerCase ? keyword.toLowerCase() : keyword,
                meta: AutocompleterGlobals.i18n.meta.keyword,
                category: CATEGORIES.COLREF_KEYWORD,
                details: {
                  type: colRef.type
                }
              });
            })
          }
        });
        self.entries(self.entries().concat(colRefKeywordSuggestions));
        self.loadingKeywords(false);
      });
    }
  };

  Suggestions.prototype.handleIdentifiers = function () {
    var self = this;
    if (self.parseResult.suggestIdentifiers) {
      var identifierSuggestions = [];
      self.parseResult.suggestIdentifiers.forEach(function (identifier) {
        identifierSuggestions.push({
          value: identifier.name,
          meta: identifier.type,
          category: CATEGORIES.IDENTIFIER,
          details: null
        });
      });
      self.entries(self.entries().concat(identifierSuggestions));
    }
  };

  Suggestions.prototype.handleColumnAliases = function () {
    var self = this;
    if (self.parseResult.suggestColumnAliases) {
      var columnAliasSuggestions = [];
      self.parseResult.suggestColumnAliases.forEach(function (columnAlias) {
        var type = columnAlias.types && columnAlias.types.length == 1 ? columnAlias.types[0] : 'T';
        if (type === 'COLREF') {
          columnAliasSuggestions.push({
            value: columnAlias.name,
            meta: AutocompleterGlobals.i18n.meta.alias,
            category: CATEGORIES.COLUMN,
            details: columnAlias
          });
        } else {
          columnAliasSuggestions.push({
            value: columnAlias.name,
            meta: type,
            category: CATEGORIES.COLUMN,
            details: columnAlias
          });
        }
      });
      self.entries(self.entries().concat(columnAliasSuggestions));
    }
  };

  Suggestions.prototype.handleCommonTableExpressions = function () {
    var self = this;
    if (self.parseResult.suggestCommonTableExpressions) {
      var commonTableExpressionSuggestions = [];
      self.parseResult.suggestCommonTableExpressions.forEach(function (expression) {
        var prefix = expression.prependQuestionMark ? '? ' : '';
        if (expression.prependFrom) {
          prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
        }
        commonTableExpressionSuggestions.push({
          value: prefix + expression.name,
          filterValue: expression.name,
          meta: AutocompleterGlobals.i18n.meta.commonTableExpression,
          category: CATEGORIES.CTE,
          details: null
        });
      });
      self.entries(self.entries().concat(commonTableExpressionSuggestions));
    }
  };

  Suggestions.prototype.handleFunctions = function (colRefDeferred) {
    var self = this;
    if (self.parseResult.suggestFunctions) {
      var functionSuggestions = [];
      if (self.parseResult.suggestFunctions.types && self.parseResult.suggestFunctions.types[0] === 'COLREF') {
        self.loadingFunctions(true);
        colRefDeferred.done(function (colRef) {
          var functionsToSuggest = SqlFunctions.getFunctionsWithReturnTypes(self.snippet.type(), [colRef.type.toUpperCase()], self.parseResult.suggestAggregateFunctions || false, self.parseResult.suggestAnalyticFunctions || false);

          Object.keys(functionsToSuggest).forEach(function (name) {
            functionSuggestions.push({
              category: CATEGORIES.UDF,
              value: name === 'current_date' || name === 'current_timestamp' ? name : name + '()',
              meta: functionsToSuggest[name].returnTypes.join('|'),
              weightAdjust: functionsToSuggest[name].returnTypes.filter(function (otherType) {
                  return otherType === colRef.type.toUpperCase();
              }).length > 0 ? 1 : 0,
              details: functionsToSuggest[name]
            })
          });

          self.entries(self.entries().concat(functionSuggestions));
          self.loadingFunctions(false);
        });
      } else {
        var types = self.parseResult.suggestFunctions.types || ['T'];
        var functionsToSuggest = SqlFunctions.getFunctionsWithReturnTypes(self.snippet.type(), types, self.parseResult.suggestAggregateFunctions || false, self.parseResult.suggestAnalyticFunctions || false);

        Object.keys(functionsToSuggest).forEach(function (name) {
          functionSuggestions.push({
            category: CATEGORIES.UDF,
            value: name === 'current_date' || name === 'current_timestamp' ? name : name + '()',
            meta: functionsToSuggest[name].returnTypes.join('|'),
            weightAdjust: functionsToSuggest[name].returnTypes.filter(function (otherType) {
              return otherType === types[0].toUpperCase();
            }).length > 0 ? 1 : 0,
            details: functionsToSuggest[name]
          })
        });
        self.entries(self.entries().concat(functionSuggestions));
      }
    }
  };

  Suggestions.prototype.handleDatabases = function (databasesDeferred) {
    var self = this;
    var suggestDatabases = self.parseResult.suggestDatabases;
    if (suggestDatabases) {
      var prefix = suggestDatabases.prependQuestionMark ? '? ' : '';
      if (suggestDatabases.prependFrom) {
        prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
      }
      var databaseSuggestions = [];
      self.loadingDatabases(true);
      databasesDeferred.done(function (dbs) {
        dbs.forEach(function (db) {
          databaseSuggestions.push({
            value: prefix + self.backTickIfNeeded(db) + (suggestDatabases.appendDot ? '.' : ''),
            filterValue: db,
            meta: AutocompleterGlobals.i18n.meta.database,
            category: CATEGORIES.DATABASE,
            details: null
          })
        });
        self.entries(self.entries().concat(databaseSuggestions));
        self.loadingDatabases(false);
      });
    }
  };

  Suggestions.prototype.handleTables = function (databasesDeferred) {
    var self = this;
    var tablesDeferred = $.Deferred();
    if (self.parseResult.suggestTables) {
      var suggestTables = self.parseResult.suggestTables;
      var fetchTables = function () {
        self.loadingTables(true);
        var prefix = suggestTables.prependQuestionMark ? '? ' : '';
        if (suggestTables.prependFrom) {
          prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
        }

        var database = suggestTables.identifierChain && suggestTables.identifierChain.length === 1 ? suggestTables.identifierChain[0].name : self.activeDatabase;
        self.apiHelper.fetchTables({
          sourceType: self.snippet.type(),
          databaseName: database,
          successCallback: function (data) {
            var tableSuggestions = [];
            data.tables_meta.forEach(function (tableMeta) {
              if (suggestTables.onlyTables && tableMeta.type.toLowerCase() !== 'table' ||
                  suggestTables.onlyViews && tableMeta.type.toLowerCase() !== 'view') {
                return;
              }
              var details = tableMeta;
              details.database = database;
              tableSuggestions.push({
                value: prefix + self.backTickIfNeeded(tableMeta.name),
                filterValue: tableMeta.name,
                tableName: tableMeta.name,
                meta: AutocompleterGlobals.i18n.meta[tableMeta.type.toLowerCase()],
                category: CATEGORIES.TABLE,
                details: details
              });
            });
            self.loadingTables(false);
            self.entries(self.entries().concat(tableSuggestions));
            tablesDeferred.resolve(tableSuggestions);
          },
          silenceErrors: true,
          errorCallback: function () {
            self.loadingTables(false);
            tablesDeferred.resolve([]);
          },
          timeout: AUTOCOMPLETE_TIMEOUT
        });
      };

      if (self.snippet.type() == 'impala' && self.parseResult.suggestTables.identifierChain && self.parseResult.suggestTables.identifierChain.length === 1) {
        databasesDeferred.done(function (databases) {
          var foundDb = databases.filter(function (db) {
            return db.toLowerCase() === self.parseResult.suggestTables.identifierChain[0].name.toLowerCase();
          });
          if (foundDb.length > 0) {
            fetchTables();
          } else {
            self.parseResult.suggestColumns = { tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }] };
            tablesDeferred.resolve([]);
          }
        });
      } else if (self.snippet.type() == 'impala' && self.parseResult.suggestTables.identifierChain && self.parseResult.suggestTables.identifierChain.length > 1) {
        self.parseResult.suggestColumns = { tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }] };
        tablesDeferred.resolve([]);
      } else {
        fetchTables();
      }
    } else {
      tablesDeferred.resolve([]);
    }

    return tablesDeferred;
  };

  Suggestions.prototype.handleColumns = function (colRefDeferred, tablesDeferred) {
    var self = this;
    var columnsDeferred = $.Deferred();
    $.when(tablesDeferred).done(function () {
      if (self.parseResult.suggestColumns) {
        var suggestColumns = self.parseResult.suggestColumns;
        var columnSuggestions = [];
        // For multiple tables we need to merge and make sure identifiers are unique
        var columnDeferrals = [];

        if (suggestColumns.types && suggestColumns.types[0] === 'COLREF') {
          self.loadingColumns(true);
          colRefDeferred.done(function (colRef) {
            suggestColumns.tables.forEach(function (table) {
              columnDeferrals.push(self.addColumns(table, [colRef.type.toUpperCase()], columnSuggestions));
            });
          });
        } else {
          self.loadingColumns(true);
          suggestColumns.tables.forEach(function (table) {
            columnDeferrals.push(self.addColumns(table, suggestColumns.types || ['T'], columnSuggestions));
          });
        }

        $.when.apply($, columnDeferrals).done(function () {
          self.mergeColumns(columnSuggestions);
          if (self.snippet.type() === 'hive' && /[^\.]$/.test(self.editor().getTextBeforeCursor())) {
            columnSuggestions.push({
              value: 'BLOCK__OFFSET__INSIDE__FILE',
              meta: AutocompleterGlobals.i18n.meta.virtual,
              category: CATEGORIES.VIRTUAL_COLUMN,
              details: null
            });
            columnSuggestions.push({
              value: 'INPUT__FILE__NAME',
              meta: AutocompleterGlobals.i18n.meta.virtual,
              category: CATEGORIES.VIRTUAL_COLUMN,
              details: null
            });
          }
          self.entries(self.entries().concat(columnSuggestions));
          columnsDeferred.resolve(columnSuggestions);
          self.loadingColumns(false);
        });
      } else {
        columnsDeferred.resolve([]);
      }
    });

    return columnsDeferred;
  };

  Suggestions.prototype.addColumns = function (table, types, columnSuggestions) {
    var self = this;
    var addColumnsDeferred = $.Deferred();

    if (typeof table.identifierChain !== 'undefined' && table.identifierChain.length === 1 && typeof table.identifierChain[0].subQuery !== 'undefined') {
      var foundSubQuery = self.locateSubQuery(self.parseResult.subQueries, table.identifierChain[0].subQuery);

      var addSubQueryColumns = function (subQueryColumns) {
        subQueryColumns.forEach(function (column) {
          if (column.alias || column.identifierChain) {
            // TODO: Potentially fetch column types for sub-queries, possible performance hit.
            var type = typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
            if (column.alias) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.alias),
                filterValue: column.alias,
                meta: type,
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            } else if (column.identifierChain && column.identifierChain.length > 0) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.identifierChain[column.identifierChain.length - 1].name),
                filterValue: column.identifierChain[column.identifierChain.length - 1].name,
                meta: type,
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            }
          } else if (column.subQuery && foundSubQuery.subQueries) {
            var foundNestedSubQuery = self.locateSubQuery(foundSubQuery.subQueries, column.subQuery);
            if (foundNestedSubQuery !== null) {
              addSubQueryColumns(foundNestedSubQuery.columns);
            }
          }
        });
      };
      if (foundSubQuery !== null && foundSubQuery.columns.length > 0) {
        addSubQueryColumns(foundSubQuery.columns);
      }
      addColumnsDeferred.resolve();
    } else {
      var callback = function (data) {
        if (data.extended_columns) {
          data.extended_columns.forEach(function (column) {
            column.database = data.database;
            column.table = data.table;
            column.identifierChain = data.identifierChain;
            if (column.type.indexOf('map') === 0 && self.snippet.type() === 'hive') {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.name) + '[]',
                filterValue: column.name,
                meta: 'map',
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            } else if (column.type.indexOf('map') === 0) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.name),
                filterValue: column.name,
                meta: 'map',
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            } else if (column.type.indexOf('struct') === 0) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.name),
                filterValue: column.name,
                meta: 'struct',
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            } else if (column.type.indexOf('array') === 0 && self.snippet.type() === 'hive') {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.name) + '[]',
                filterValue: column.name,
                filterValue: column.name,
                meta: 'array',
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            } else if (column.type.indexOf('array') === 0) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.name),
                filterValue: column.name,
                meta: 'array',
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            } else if (types[0].toUpperCase() !== 'T' && types.filter(function (type) { return type.toUpperCase() === column.type.toUpperCase() }).length > 0) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.name),
                filterValue: column.name,
                meta: column.type,
                category: CATEGORIES.COLUMN,
                weightAdjust: 1,
                table: table,
                details: column
              })
            } else if (SqlFunctions.matchesType(self.snippet.type(), types, [column.type.toUpperCase()]) ||
                SqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(column.name),
                filterValue: column.name,
                meta: column.type,
                category: CATEGORIES.COLUMN,
                table: table,
                details: column
              })
            }
          });
        } else if (data.columns) {
          data.columns.forEach(function (column) {
            column.database = data.database;
            column.table = data.table;
            column.identifierChain = data.identifierChain;
            columnSuggestions.push({
              value: self.backTickIfNeeded(column),
              filterValue: column,
              meta: 'column',
              category: CATEGORIES.COLUMN,
              table: table,
              details: column
            })
          });
        }
        if (data.type === 'map' && self.snippet.type() === 'impala') {
          columnSuggestions.push({
            value: 'key',
            meta: 'key',
            category: CATEGORIES.COLUMN,
            table: table,
            details: data
          });
          columnSuggestions.push({
            value: 'value',
            meta: 'value',
            category: CATEGORIES.COLUMN,
            table: table,
            details: data
          });
        }
        if (data.type === 'struct') {
          data.fields.forEach(function (field) {
            field.database = data.database;
            field.table = data.table;
            field.identifierChain = data.identifierChain;

            columnSuggestions.push({
              value: self.backTickIfNeeded(field.name),
              filterValue: field.name,
              meta: field.type,
              category: CATEGORIES.COLUMN,
              table: table,
              details: field
            });
          });
        } else if (data.type === 'map' && (data.value && data.value.fields)) {
          data.value.fields.forEach(function (field) {
            field.database = data.database;
            field.table = data.table;
            field.identifierChain = data.identifierChain;

            if (SqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
                SqlFunctions.matchesType(self.snippet.type(), [field.type.toUpperCase()], types)) {
              columnSuggestions.push({
                value: self.backTickIfNeeded(field.name),
                filterValue: field.name,
                meta: field.type,
                category: CATEGORIES.COLUMN,
                table: table,
                details: field
              });
            }
          });
        } else if (data.type === 'array' && data.item) {
          if (data.item.fields) {
            data.item.fields.forEach(function (field) {
              field.database = data.database;
              field.table = data.table;
              field.identifierChain = data.identifierChain;

              if ((field.type === 'array' || field.type === 'map')) {
                if (self.snippet.type() === 'hive') {
                  columnSuggestions.push({
                    value: self.backTickIfNeeded(field.name) + '[]',
                    filterValue: field.name,
                    meta: field.type,
                    category: CATEGORIES.COLUMN,
                    table: table,
                    details: field
                  });
                } else {
                  columnSuggestions.push({
                    value: self.backTickIfNeeded(field.name),
                    filterValue: field.name,
                    meta: field.type,
                    category: CATEGORIES.COLUMN,
                    table: table,
                    details: field
                  });
                }
              } else if (SqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
                  SqlFunctions.matchesType(self.snippet.type(), [field.type.toUpperCase()], types)) {
                columnSuggestions.push({
                  value: self.backTickIfNeeded(field.name),
                  filterValue: field.name,
                  meta: field.type,
                  category: CATEGORIES.COLUMN,
                  table: table,
                  details: field
                });
              }
            });
          } else if (typeof data.item.type !== 'undefined') {
            if (SqlFunctions.matchesType(self.snippet.type(), types, [data.item.type.toUpperCase()])) {
              columnSuggestions.push({
                value: 'item',
                meta: data.item.type,
                category: CATEGORIES.COLUMN,
                table: table,
                details: data.item
              });
            }
          }
        }
        addColumnsDeferred.resolve();
      };

      self.fetchFieldsForIdentifiers(table.identifierChain, callback, addColumnsDeferred.resolve);
    }
    return addColumnsDeferred;
  };

  Suggestions.prototype.mergeColumns = function (columnSuggestions) {
    columnSuggestions.sort(function (a, b) {
      return a.value.localeCompare(b.value);
    });

    for (var i = 0; i < columnSuggestions.length; i++) {
      var suggestion = columnSuggestions[i];
      suggestion.isColumn = true;
      var hasDuplicates = false;
      for (i; i + 1 < columnSuggestions.length && columnSuggestions[i + 1].value === suggestion.value; i++) {
        var nextTable = columnSuggestions[i + 1].table;
        if (typeof nextTable.alias !== 'undefined') {
          columnSuggestions[i + 1].value = nextTable.alias + '.' + columnSuggestions[i + 1].value
        } else if (typeof nextTable.identifierChain !== 'undefined' && nextTable.identifierChain.length > 0) {
          var previousIdentifier = nextTable.identifierChain[nextTable.identifierChain.length - 1];
          if (typeof previousIdentifier.name !== 'undefined') {
            columnSuggestions[i + 1].value = previousIdentifier.name + '.' + columnSuggestions[i + 1].value;
          } else if (typeof previousIdentifier.subQuery !== 'undefined') {
            columnSuggestions[i + 1].value = previousIdentifier.subQuery + '.' + columnSuggestions[i + 1].value;
          }
        }
        hasDuplicates = true;
      }
      if (typeof suggestion.table.alias !== 'undefined') {
        suggestion.value = suggestion.table.alias + '.' + suggestion.value;
      } else if (hasDuplicates && typeof suggestion.table.identifierChain !== 'undefined' && suggestion.table.identifierChain.length > 0) {
        var lastIdentifier = suggestion.table.identifierChain[suggestion.table.identifierChain.length - 1];
        if (typeof lastIdentifier.name !== 'undefined') {
          suggestion.value = lastIdentifier.name + '.' + suggestion.value;
        } else if (typeof lastIdentifier.subQuery !== 'undefined') {
          suggestion.value = lastIdentifier.subQuery + '.' + suggestion.value;
        }
      }
    }
  };

  Suggestions.prototype.handleValues = function (colRefDeferred) {
    var self = this;
    var suggestValues = self.parseResult.suggestValues;
    if (suggestValues) {
      var valueSuggestions = [];
      if (self.parseResult.colRef && self.parseResult.colRef.identifierChain) {
        valueSuggestions.push({
          value: '${' + self.parseResult.colRef.identifierChain[self.parseResult.colRef.identifierChain.length - 1].name + '}',
          meta: AutocompleterGlobals.i18n.meta.variable,
          category: CATEGORIES.VARIABLE,
          details: null
        });
      }
      colRefDeferred.done(function (colRef) {
        if (colRef.sample) {
          var isString = colRef.type === "string";
          var startQuote = suggestValues.partialQuote ? '' : '\'';
          var endQuote = typeof suggestValues.missingEndQuote !== 'undefined' && suggestValues.missingEndQuote === false ? '' : suggestValues.partialQuote || '\'';
          colRef.sample.forEach(function (sample) {
            valueSuggestions.push({
              value: isString ? startQuote + sample + endQuote : new String(sample),
              meta: AutocompleterGlobals.i18n.meta.value,
              category: CATEGORIES.SAMPLE,
              details: null
            })
          });
        }
        self.entries(self.entries().concat(valueSuggestions));
      });
    }
  };

  Suggestions.prototype.handlePaths = function () {
    var self = this;
    var suggestHdfs = self.parseResult.suggestHdfs;
    var pathsDeferred = $.Deferred();
    if (suggestHdfs) {
      var parts = suggestHdfs.path.split('/');
      // Drop the first " or '
      parts.shift();
      // Last one is either partial name or empty
      parts.pop();

      self.loadingPaths(true);
      self.apiHelper.fetchHdfsPath({
        pathParts: parts,
        successCallback: function (data) {
          if (!data.error) {
            var pathSuggestions = [];
            data.files.forEach(function (file) {
              if (file.name !== '..' && file.name !== '.') {
                pathSuggestions.push({
                  value: suggestHdfs.path === '' ? '/' + file.name : file.name,
                  meta: file.type,
                  category: CATEGORIES.HDFS,
                  details: file
                });
              }
            });
            self.entries(self.entries().concat(pathSuggestions));
            pathsDeferred.resolve(pathSuggestions);
          }
          self.loadingPaths(false);
        },
        silenceErrors: true,
        errorCallback: function () {
          pathsDeferred.resolve([]);
          self.loadingPaths(false);
        },
        timeout: AUTOCOMPLETE_TIMEOUT
      });
    } else {
      pathsDeferred.resolve([]);
    }
    return pathsDeferred;
  };

  Suggestions.prototype.handleJoins = function () {
    var self = this;
    var joinsDeferred = $.Deferred();
    var suggestJoins = self.parseResult.suggestJoins;
    if (HAS_OPTIMIZER && suggestJoins) {
      self.loadingJoins(true);
      self.apiHelper.fetchNavOptPopularJoins({
        sourceType: self.snippet.type(),
        timeout: AUTOCOMPLETE_TIMEOUT,
        defaultDatabase: self.activeDatabase,
        silenceErrors: true,
        tables: suggestJoins.tables,
        successCallback: function (data) {
          var joinSuggestions = [];
          var totalCount = 0;
          data.values.forEach(function (value) {
            var suggestionString = suggestJoins.prependJoin ? (self.parseResult.lowerCase ? 'join ' : 'JOIN ') : '';
            var first = true;

            var existingTables = {};
            suggestJoins.tables.forEach(function (table) {
              existingTables[table.identifierChain[table.identifierChain.length - 1].name] = true;
            });

            var joinRequired = false;
            var tablesAdded = false;
            value.tables.forEach(function (table) {
              var tableParts = table.split('.');
              if (!existingTables[tableParts[tableParts.length - 1]]) {
                tablesAdded = true;
                var identifier = self.convertNavOptQualifiedIdentifier(table, suggestJoins.tables);
                suggestionString += joinRequired ? (self.parseResult.lowerCase ? ' join ' : ' JOIN ') + identifier : identifier;
                joinRequired = true;
              }
            });

            if (value.joinCols.length > 0) {
              if (!tablesAdded && suggestJoins.prependJoin) {
                suggestionString = '';
                tablesAdded = true;
              }
              suggestionString += self.parseResult.lowerCase ? ' on ' : ' ON ';
            }
            if (tablesAdded) {
              value.joinCols.forEach(function (joinColPair) {
                if (!first) {
                  suggestionString += self.parseResult.lowerCase ? ' and ' : ' AND ';
                }
                suggestionString += self.convertNavOptQualifiedIdentifier(joinColPair.columns[0], suggestJoins.tables) + ' = ' + self.convertNavOptQualifiedIdentifier(joinColPair.columns[1], suggestJoins.tables);
                first = false;
              });
              totalCount += value.totalQueryCount;
              joinSuggestions.push({
                value: suggestionString,
                meta: AutocompleterGlobals.i18n.meta.join,
                category: suggestJoins.prependJoin ? CATEGORIES.POPULAR_JOIN : CATEGORIES.POPULAR_ACTIVE_JOIN,
                popular: true,
                details: value
              });
            }
          });
          joinSuggestions.forEach(function (suggestion) {
            suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.totalQueryCount : Math.round(100 * suggestion.details.totalQueryCount / totalCount);
            suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
          });
          self.entries(self.entries().concat(joinSuggestions));
          self.loadingJoins(false);
          joinsDeferred.resolve(joinSuggestions);
        },
        errorCallback: function () {
          self.loadingJoins(false);
          joinsDeferred.resolve([]);
        }
      });
    } else {
      joinsDeferred.resolve([]);
    }
    return joinsDeferred;
  };

  Suggestions.prototype.handleJoinConditions = function () {
    var self = this;
    var joinConditionsDeferred = $.Deferred();
    var suggestJoinConditions = self.parseResult.suggestJoinConditions;
    if (HAS_OPTIMIZER && suggestJoinConditions) {
      self.loadingJoinConditions(true);
      self.apiHelper.fetchNavOptPopularJoins({
        sourceType: self.snippet.type(),
        timeout: AUTOCOMPLETE_TIMEOUT,
        defaultDatabase: self.activeDatabase,
        silenceErrors: true,
        tables: suggestJoinConditions.tables,
        successCallback: function (data) {
          var joinConditionSuggestions = [];
          var totalCount = 0;
          data.values.forEach(function (value) {
            if (value.joinCols.length > 0) {
              var suggestionString = suggestJoinConditions.prependOn ? (self.parseResult.lowerCase ? 'on ' : 'ON ') : '';
              var first = true;
              value.joinCols.forEach(function (joinColPair) {
                if (!first) {
                  suggestionString += self.parseResult.lowerCase ? ' and ' : ' AND ';
                }
                suggestionString += self.convertNavOptQualifiedIdentifier(joinColPair.columns[0], suggestJoinConditions.tables) + ' = ' + self.convertNavOptQualifiedIdentifier(joinColPair.columns[1], suggestJoinConditions.tables);
                first = false;
              });
              totalCount += value.totalQueryCount;
              joinConditionSuggestions.push({
                value: suggestionString,
                meta: AutocompleterGlobals.i18n.meta.joinCondition,
                category: CATEGORIES.POPULAR_JOIN_CONDITION,
                popular: true,
                details: value
              });
            }
          });
          joinConditionSuggestions.forEach(function (suggestion) {
            suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.totalQueryCount : Math.round(100 * suggestion.details.totalQueryCount / totalCount);
            suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
          });

          self.entries(self.entries().concat(joinConditionSuggestions));
          joinConditionsDeferred.resolve();
          self.loadingJoinConditions(false);
        },
        errorCallback: function () {
          self.loadingJoinConditions(false);
          joinConditionsDeferred.resolve([]);
        }
      });
    } else {
      joinConditionsDeferred.resolve([]);
    }

    return joinConditionsDeferred;
  };

  Suggestions.prototype.handleAggregateFunctions = function () {
    var self = this;
    var aggregateFunctionsDeferred = $.Deferred();
    var suggestAggregateFunctions = self.parseResult.suggestAggregateFunctions;
    if (HAS_OPTIMIZER && suggestAggregateFunctions && suggestAggregateFunctions.tables.length > 0) {
      self.loadingAggregateFunctions(true);
      self.apiHelper.fetchNavOptTopAggs({
        sourceType: self.snippet.type(),
        timeout: AUTOCOMPLETE_TIMEOUT,
        defaultDatabase: self.activeDatabase,
        silenceErrors: true,
        tables: suggestAggregateFunctions.tables,
        successCallback: function (data) {
          var aggregateFunctionsSuggestions = [];
          if (data.values.length > 0) {
            // TODO: Handle column conflicts with multiple tables

            // Substitute qualified table identifiers with either alias or empty string
            var substitutions = [];
            suggestAggregateFunctions.tables.forEach(function (table) {
              var replaceWith = table.alias ? table.alias + '.' : '';
              if (table.identifierChain.length > 1) {
                substitutions.push({
                  replace: new RegExp($.map(table.identifierChain, function (identifier) {
                        return identifier.name
                      }).join('\.') + '\.', 'gi'),
                  with: replaceWith
                })
              } else if (table.identifierChain.length === 1) {
                substitutions.push({
                  replace: new RegExp(self.activeDatabase + '\.' + table.identifierChain[0].name + '\.', 'gi'),
                  with: replaceWith
                });
                substitutions.push({
                  replace: new RegExp(table.identifierChain[0].name + '\.', 'gi'),
                  with: replaceWith
                })
              }
            });

            var totalCount = 0;
            data.values.forEach(function (value) {
              var clean = value.aggregateClause;
              substitutions.forEach(function (substitution) {
                clean = clean.replace(substitution.replace, substitution.with);
              });
              totalCount += value.totalQueryCount;
              value.function = SqlFunctions.findFunction(self.snippet.type(), value.aggregateFunction);
              aggregateFunctionsSuggestions.push({
                value: clean,
                meta: value.function.returnTypes.join('|'),
                category: CATEGORIES.POPULAR_AGGREGATE,
                popular: true,
                weightAdjust: Math.min(value.totalQueryCount, 99),
                details: value
              });
            });

            aggregateFunctionsSuggestions.forEach(function (suggestion) {
              suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.totalQueryCount : Math.round(100 * suggestion.details.totalQueryCount / totalCount);
              suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
            });

            self.entries(self.entries().concat(aggregateFunctionsSuggestions));
          }
          aggregateFunctionsDeferred.resolve();
          self.loadingAggregateFunctions(false);
        },
        errorCallback: function () {
          self.loadingAggregateFunctions(false);
          aggregateFunctionsDeferred.resolve();
        }
      });
    } else {
      aggregateFunctionsDeferred.resolve();
    }
    return aggregateFunctionsDeferred;
  };

  Suggestions.prototype.handleGroupBys = function () {
    var self = this;
    var groupBysDeferred = $.Deferred();
    var suggestGroupBys = self.parseResult.suggestGroupBys;
    if (HAS_OPTIMIZER && suggestGroupBys) {
      self.loadingGroupBys(true);
      self.apiHelper.fetchNavOptTopColumns({
        sourceType: self.snippet.type(),
        timeout: AUTOCOMPLETE_TIMEOUT,
        defaultDatabase: self.activeDatabase,
        silenceErrors: true,
        tables: suggestGroupBys.tables,
        successCallback: function (data) {
          var groupBySuggestions = [];
          if (typeof data.values.groupbyColumns !== 'undefined') {
            var prefix = suggestGroupBys.prefix ? (self.parseResult.lowerCase ? suggestGroupBys.prefix.toLowerCase() : suggestGroupBys.prefix) + ' ' : '';
            data.values.groupbyColumns.forEach(function (value) {
              var filterValue = self.createNavOptIdentifierForColumn(value, suggestGroupBys.tables);
              groupBySuggestions.push({
                value: prefix + filterValue,
                filterValue: filterValue,
                meta: AutocompleterGlobals.i18n.meta.groupBy,
                category: CATEGORIES.POPULAR_GROUP_BY,
                popular: true,
                weightAdjust: Math.min(value.columnCount, 99),
                details: value
              });
            });
          }
          self.entries(self.entries().concat(groupBySuggestions));
          self.loadingGroupBys(false);
          groupBysDeferred.resolve(groupBySuggestions);
        },
        errorCallback: function () {
          self.loadingGroupBys(false);
          groupBysDeferred.resolve([])
        }
      });
    } else {
      groupBysDeferred.resolve([]);
    }

    return groupBysDeferred;
  };

  Suggestions.prototype.handleOrderBys = function () {
    var self = this;
    var orderBysDeferred = $.Deferred();
    var suggestOrderBys = self.parseResult.suggestOrderBys;
    if (HAS_OPTIMIZER && suggestOrderBys) {
      self.apiHelper.fetchNavOptTopColumns({
        sourceType: self.snippet.type(),
        timeout: AUTOCOMPLETE_TIMEOUT,
        defaultDatabase: self.activeDatabase,
        silenceErrors: true,
        tables: suggestOrderBys.tables,
        successCallback: function (data) {
          var orderBySuggestions = [];
          if (typeof data.values.orderbyColumns !== 'undefined') {
            var prefix = suggestOrderBys.prefix ? (self.parseResult.lowerCase ? suggestOrderBys.prefix.toLowerCase() : suggestOrderBys.prefix) + ' ' : '';
            data.values.orderbyColumns.forEach(function (value) {
              var filterValue = self.createNavOptIdentifierForColumn(value, suggestOrderBys.tables);
              orderBySuggestions.push({
                value: prefix + filterValue,
                filterValue: filterValue,
                meta: AutocompleterGlobals.i18n.meta.orderBy,
                category: CATEGORIES.POPULAR_ORDER_BY,
                popular: true,
                weightAdjust: Math.min(value.columnCount, 99),
                details: value
              });
            });
          }
          self.entries(self.entries().concat(orderBySuggestions));
          self.loadingOrderBys(false);
          orderBysDeferred.resolve(orderBySuggestions);
        },
        errorCallback: function () {
          self.loadingOrderBys(false);
          orderBysDeferred.resolve([]);
        }
      });
    } else {
      orderBysDeferred.resolve([]);
    }
    return orderBysDeferred;
  };

  Suggestions.prototype.handleFilters = function () {
    var self = this;
    var filtersDeferred = $.Deferred();
    var suggestFilters = self.parseResult.suggestFilters;
    if (HAS_OPTIMIZER && suggestFilters) {
      self.loadingFilters(true);
      self.apiHelper.fetchNavOptTopFilters({
        sourceType: self.snippet.type(),
        timeout: AUTOCOMPLETE_TIMEOUT,
        defaultDatabase: self.activeDatabase,
        silenceErrors: true,
        tables: suggestFilters.tables,
        successCallback: function (data) {
          var filterSuggestions = [];
          var totalCount = 0;
          data.values.forEach(function (value) {
            if (typeof value.popularValues !== 'undefined' && value.popularValues.length > 0) {
              value.popularValues.forEach(function (popularValue) {
                if (typeof popularValue.group !== 'undefined') {
                  popularValue.group.forEach(function (grp) {
                    var compVal = suggestFilters.prefix ? (self.parseResult.lowerCase ? suggestFilters.prefix.toLowerCase() : suggestFilters.prefix) + ' ' : '';
                    compVal += self.createNavOptIdentifier(value.tableName, grp.columnName, suggestFilters.tables);
                    if (!/^ /.test(grp.op)) {
                      compVal += ' ';
                    }
                    compVal += self.parseResult.lowerCase ? grp.op.toLowerCase() : grp.op;
                    if (!/ $/.test(grp.op)) {
                      compVal += ' ';
                    }
                    compVal += grp.literal;
                    totalCount += popularValue.count;
                    filterSuggestions.push({
                      value: compVal,
                      meta: AutocompleterGlobals.i18n.meta.filter,
                      category: CATEGORIES.POPULAR_FILTER,
                      popular: true,
                      details: popularValue
                    });
                  });
                }
              });
            }
          });
          filterSuggestions.forEach(function (suggestion) {
            suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.count : Math.round(100 * suggestion.details.count / totalCount);
            suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
          });

          self.entries(self.entries().concat(filterSuggestions));
          self.loadingFilters(false);
          filtersDeferred.resolve(filterSuggestions);
        },
        errorCallback: function () {
          self.loadingFilters(false);
          filtersDeferred.resolve([]);
        }
      });
    } else {
      filtersDeferred.resolve([]);
    }
    return filtersDeferred;
  };

  var adjustWeightsBasedOnPopularity = function(suggestions, totalPopularity) {
    suggestions.forEach(function (suggestion) {
      suggestion.details.popularity.relativePopularity = Math.round(100 * suggestion.details.popularity.popularity / totalPopularity);
      suggestion.weightAdjust = suggestion.details.popularity.relativePopularity;
    });
  };

  Suggestions.prototype.handlePopularTables = function (tablesDeferred) {
    var self = this;
    var popularTablesDeferred = $.Deferred();
    if (HAS_OPTIMIZER && self.parseResult.suggestTables) {
      self.loadingPopularTables(true);
      self.apiHelper.fetchNavOptTopTables({
        database: self.activeDatabase,
        sourceType: self.snippet.type(),
        silenceErrors: true,
        successCallback: function (data) {
          var popularityIndex = {};
          if (data.top_tables.length == 0) {
            self.loadingPopularTables(false);
            popularTablesDeferred.resolve([]);
            return;
          }
          data.top_tables.forEach(function (topTable) {
            popularityIndex[topTable.name] = topTable;
          });

          $.when(tablesDeferred).done(function (tableSuggestions) {
            var totalMatchedPopularity = 0;
            var matchedSuggestions = [];
            tableSuggestions.forEach(function (suggestion) {
              var topTable = popularityIndex[suggestion.tableName];
              if (typeof topTable !== 'undefined') {
                suggestion.popular = true;
                if (!suggestion.details) {
                  suggestion.details = {};
                }
                suggestion.details.popularity = topTable;
                totalMatchedPopularity += topTable.popularity;
                matchedSuggestions.push(suggestion);
              }
            });
            self.loadingPopularTables(false);
            popularTablesDeferred.resolve(data.top_tables);
            if (matchedSuggestions.length > 0) {
              adjustWeightsBasedOnPopularity(matchedSuggestions, totalMatchedPopularity);
              self.entries.notifySubscribers();
            }
          });
        },
        errorCallback: function () {
          self.loadingPopularTables(false);
          popularTablesDeferred.resolve([]);
        }
      });
    } else {
      popularTablesDeferred.resolve([]);
    }
    return popularTablesDeferred
  };

  Suggestions.prototype.handlePopularColumns = function (columnsDeferred) {
    var self = this;
    var popularColumnsDeferred = $.Deferred();
    var suggestColumns = self.parseResult.suggestColumns;
    // TODO: Handle tables from different databases
    if (HAS_OPTIMIZER && suggestColumns && suggestColumns.source !== 'undefined') {
      self.loadingPopularColumns(true);
      self.apiHelper.fetchNavOptTopColumns({
        sourceType: self.snippet.type(),
        timeout: AUTOCOMPLETE_TIMEOUT,
        defaultDatabase: self.activeDatabase,
        silenceErrors: true,
        tables: suggestColumns.tables,
        successCallback: function (data) {
          var popularColumns = [];
          switch (suggestColumns.source) {
            case 'select':
              popularColumns = data.values.selectColumns;
              break;
            case 'group by':
              popularColumns = data.values.groupbyColumns;
              break;
            case 'order by':
              popularColumns = data.values.orderbyColumns;
              break;
            default:
              popularColumns = [];
          }

          if (popularColumns.length === 0) {
            self.loadingPopularColumns(false);
            popularColumnsDeferred.resolve([]);
            return;
          }

          var popularityIndex = {};
          popularColumns.forEach(function (popularColumn) {
            popularityIndex[popularColumn.columnName.toLowerCase()] = popularColumn;
          });

          $.when(columnsDeferred).done(function (columns) {
            var totalMatchedPopularity = 0;
            var matchedSuggestions = [];
            columns.forEach(function (suggestion) {
              if (typeof suggestion.table === 'undefined') {
                return;
              }
              var topColumn = popularityIndex[suggestion.value.toLowerCase()];
              if (typeof topColumn !== 'undefined') {
                suggestion.popular = true;
                if (!suggestion.details) {
                  suggestions.details = {};
                }
                topColumn.popularity = topColumn.columnCount; // No popularity for columns in response
                suggestion.details.popularity = topColumn;
                totalMatchedPopularity += topColumn.columnCount;
                matchedSuggestions.push(suggestion);
              }
            });
            self.loadingPopularColumns(false);
            popularColumnsDeferred.resolve(popularColumns);
            if (matchedSuggestions.length > 0) {
              adjustWeightsBasedOnPopularity(matchedSuggestions, totalMatchedPopularity);
              self.entries.notifySubscribers();
            }
          });
        },
        errorCallback: function () {
          self.loadingPopularColumns(false);
          popularColumnsDeferred.resolve([]);
        }
      });
    } else {
      popularColumnsDeferred.resolve([]);
    }
    return popularColumnsDeferred;
  };

  Suggestions.prototype.createNavOptIdentifier = function (navOptTableName, navOptColumnName, tables) {
    var self = this;
    var path = navOptTableName + '.' + navOptColumnName.split('.').pop();
    for (var i = 0; i < tables.length; i++) {
      var tablePath = '';
      if (tables[i].identifierChain.length == 2) {
        tablePath = $.map(tables[i].identifierChain, function (identifier) { return identifier.name }).join('.');
      } else if (tables[i].identifierChain.length == 1) {
        tablePath = self.activeDatabase + '.' + tables[i].identifierChain[0].name;
      }
      if (path.indexOf(tablePath) === 0) {
        path = path.substring(tablePath.length + 1);
        if (tables[i].alias) {
          path = tables[i].alias + '.' + path;
        }
        break;
      }
    }
    return path;
  };

  Suggestions.prototype.createNavOptIdentifierForColumn = function (navOptColumn, tables) {
    var self = this;
    for (var i = 0; i < tables.length; i++) {
      if (navOptColumn.dbName && (navOptColumn.dbName !== self.activeDatabase || navOptColumn.dbName !== tables[i].identifierChain[0].name)) {
        continue;
      }
      if (navOptColumn.tableName && navOptColumn.tableName === tables[i].identifierChain[tables[i].identifierChain.length - 1].name && tables[i].alias) {
        return tables[i].alias + '.' + navOptColumn.columnName;
      }
    }

    if (navOptColumn.dbName && navOptColumn.dbName !== self.activeDatabase) {
      return navOptColumn.dbName + '.' + navOptColumn.tableName + '.' + navOptColumn.columnName;
    }
    if (tables.length > 1) {
      return navOptColumn.tableName + '.' + navOptColumn.columnName;
    }
    return navOptColumn.columnName;
  };

  Suggestions.prototype.convertNavOptQualifiedIdentifier = function (qualifiedIdentifier, tables) {
    var self = this;
    var aliases = [];
    var tablesHasDefaultDatabase = false;
    tables.forEach(function (table) {
      tablesHasDefaultDatabase = tablesHasDefaultDatabase || table.identifierChain[0].name.toLowerCase() === self.activeDatabase.toLowerCase();
      if (table.alias) {
        aliases.push({ qualifiedName: $.map(table.identifierChain, function (identifier) { return identifier.name }).join('.').toLowerCase(), alias: table.alias });
      }
    });

    for (var i = 0; i < aliases.length; i++) {
      if (qualifiedIdentifier.toLowerCase().indexOf(aliases[i].qualifiedName) === 0) {
        return aliases[i].alias + qualifiedIdentifier.substring(aliases[i].qualifiedName.length);
      } else if (qualifiedIdentifier.toLowerCase().indexOf(self.activeDatabase.toLowerCase() + '.' + aliases[i].qualifiedName) === 0) {
        return aliases[i].alias + qualifiedIdentifier.substring((self.activeDatabase + '.' + aliases[i].qualifiedName).length);
      }
    }

    return qualifiedIdentifier.toLowerCase().indexOf(self.activeDatabase.toLowerCase()) === 0 && !tablesHasDefaultDatabase ? qualifiedIdentifier.substring(self.activeDatabase.length + 1) : qualifiedIdentifier;
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
            data.database = database;
            data.table = table;
            data.identifierChain = originalIdentifierChain;
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
            var databaseName = foundDb.length > 0 ? identifierChain.shift().name : self.activeDatabase;
            var tableName = identifierChain.shift().name;
            fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
          },
          silenceErrors: true,
          errorCallback: errorCallback
        });
      } else {
        var databaseName = self.activeDatabase;
        var tableName = identifierChain.shift().name;
        fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
      }
    } else {
      var databaseName = identifierChain.length > 1 ? identifierChain.shift().name : self.activeDatabase;
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