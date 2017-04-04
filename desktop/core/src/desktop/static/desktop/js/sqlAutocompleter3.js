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

var AutocompleteResults = (function () {

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
    ALL: { id: 'all', color: HueColors.BLUE, label: AutocompleterGlobals.i18n.category.all },
    POPULAR: { id: 'popular', color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular },
    POPULAR_AGGREGATE: { id: 'popularAggregate', weight: 1500, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'agg-udf' },
    POPULAR_GROUP_BY: { id: 'popularGroupBy', weight: 1400, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'group-by' },
    POPULAR_ORDER_BY: { id: 'popularOrderBy', weight: 1300, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'order-by' },
    POPULAR_FILTER: { id: 'popularFilter', weight: 1200, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'filter' },
    POPULAR_ACTIVE_JOIN: { id: 'popularActiveJoin', weight: 1200, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'join' },
    POPULAR_JOIN_CONDITION: { id: 'popularJoinCondition', weight: 1100, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'join-condition' },
    COLUMN: { id: 'column', weight: 1000, color: COLORS.COLUMN, label: AutocompleterGlobals.i18n.category.column, detailsTemplate: 'column' },
    SAMPLE: { id: 'sample',weight: 900, color: COLORS.SAMPLE, label: AutocompleterGlobals.i18n.category.sample, detailsTemplate: 'value' },
    IDENTIFIER: { id: 'identifier', weight: 800, color: COLORS.IDENT_CTE_VAR, label: AutocompleterGlobals.i18n.category.identifier, detailsTemplate: 'identifier' },
    CTE: { id: 'cte', weight: 700, color: COLORS.IDENT_CTE_VAR, label: AutocompleterGlobals.i18n.category.cte, detailsTemplate: 'cte' },
    TABLE: { id: 'table', weight: 600, color: COLORS.TABLE, label: AutocompleterGlobals.i18n.category.table, detailsTemplate: 'table' },
    DATABASE: { id: 'database', weight: 500, color: COLORS.DATABASE, label: AutocompleterGlobals.i18n.category.database, detailsTemplate: 'database' },
    UDF: { id: 'udf', weight: 400, color: COLORS.UDF, label: AutocompleterGlobals.i18n.category.udf, detailsTemplate: 'udf' },
    HDFS: { id: 'hdfs', weight: 300, color: COLORS.HDFS, label: AutocompleterGlobals.i18n.category.hdfs, detailsTemplate: 'hdfs' },
    VIRTUAL_COLUMN: { id: 'virtualColumn', weight: 200, color: COLORS.COLUMN, label: AutocompleterGlobals.i18n.category.column, detailsTemplate: 'column' },
    COLREF_KEYWORD: { id: 'colrefKeyword', weight: 100, color: COLORS.KEYWORD, label: AutocompleterGlobals.i18n.category.keyword, detailsTemplate: 'keyword' },
    VARIABLE: { id: 'variable', weight: 50, color: COLORS.IDENT_CTE_VAR, label: AutocompleterGlobals.i18n.category.variable, detailsTemplate: 'variable' },
    KEYWORD: { id: 'keyword', weight: 0, color: COLORS.KEYWORD, label: AutocompleterGlobals.i18n.category.keyword, detailsTemplate: 'keyword' },
    POPULAR_JOIN: { id: 'popularJoin', weight: -1, color: COLORS.POPULAR, label: AutocompleterGlobals.i18n.category.popular, detailsTemplate: 'join' }
  };

  var POPULAR_CATEGORIES = [CATEGORIES.POPULAR_AGGREGATE, CATEGORIES.POPULAR_GROUP_BY, CATEGORIES.POPULAR_ORDER_BY, CATEGORIES.POPULAR_FILTER, CATEGORIES.POPULAR_ACTIVE_JOIN, CATEGORIES.POPULAR_JOIN_CONDITION, CATEGORIES.POPULAR_JOIN];

  var adjustWeightsBasedOnPopularity = function(suggestions, totalPopularity) {
    suggestions.forEach(function (suggestion) {
      suggestion.details.popularity.relativePopularity = Math.round(100 * suggestion.details.popularity.popularity / totalPopularity);
      suggestion.weightAdjust = suggestion.details.popularity.relativePopularity;
    });
  };

  var initLoading = function (loadingObservable, deferred) {
    loadingObservable(true);
    deferred.always(function () {
      loadingObservable(false);
    })
  };

  var locateSubQuery = function (subQueries, subQueryName) {
    if (typeof subQueries === 'undefined') {
      return null;
    }
    var foundSubQueries = subQueries.filter(function (knownSubQuery) {
      return knownSubQuery.alias === subQueryName
    });
    if (foundSubQueries.length > 0) {
      return foundSubQueries[0];
    }
    return null;
  };

  /**
   *
   * @param options
   * @constructor
   */
  function AutocompleteResults (options) {
    var self = this;
    self.apiHelper = ApiHelper.getInstance();
    self.snippet = options.snippet;
    self.editor = options.editor;

    self.entries = ko.observableArray();

    self.activeDeferrals = [];

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

    self.appendEntries = function (entries) {
      self.entries(self.entries().concat(entries));
    };

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
        if (suggestion.popular() && ! newCategories[CATEGORIES.POPULAR.label]) {
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
          if (foundIndex !== -1) {
            if (foundIndex === 0 || (suggestion.filterValue && suggestion.filterValue.toLowerCase().indexOf(lowerCaseFilter) === 0)) {
              suggestion.filterWeight = 3;
            } else  {
              suggestion.filterWeight = 2;
            }
          } else {
            if (suggestion.details && suggestion.details.comment) {
              foundIndex = suggestion.details.comment.toLowerCase().indexOf(lowerCaseFilter);
              if (foundIndex !== -1) {
                suggestion.filterWeight = 1;
                suggestion.matchComment = true;
              }
            }
          }
          if (foundIndex !== -1) {
            suggestion.matchIndex = foundIndex;
            suggestion.matchLength = self.filter().length;
            return true;
          }
          return false;
        });
        huePubSub.publish('hue.ace.autocompleter.match.updated');
      }
      updateCategories(result);

      var activeCategory = self.activeCategory();

      var categoriesCount = {};

      result = result.filter(function (suggestion) {
        if (typeof categoriesCount[suggestion.category.id] === 'undefined') {
          categoriesCount[suggestion.category.id] = 0;
        } else {
          categoriesCount[suggestion.category.id]++;
        }
        if (activeCategory !== CATEGORIES.POPULAR && categoriesCount[suggestion.category.id] >= 10 && POPULAR_CATEGORIES.indexOf(suggestion.category) !== -1) {
          return false;
        }
        return activeCategory === CATEGORIES.ALL || activeCategory === suggestion.category || (activeCategory === CATEGORIES.POPULAR && suggestion.popular());
      });

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

  AutocompleteResults.prototype.update = function (parseResult) {
    var self = this;

    while (self.activeDeferrals.length > 0) {
      self.activeDeferrals.pop().reject();
    }

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
    self.activeDeferrals.push(colRefDeferred);
    var databasesDeferred = self.loadDatabases();
    self.activeDeferrals.push(databasesDeferred);

    self.handleKeywords(colRefDeferred);
    self.handleIdentifiers();
    self.handleColumnAliases();
    self.handleCommonTableExpressions();
    self.handleFunctions(colRefDeferred);
    self.handleDatabases(databasesDeferred);
    var tablesDeferred = self.handleTables(databasesDeferred);
    self.activeDeferrals.push(tablesDeferred);
    var columnsDeferred = self.handleColumns(colRefDeferred, tablesDeferred);
    self.activeDeferrals.push(columnsDeferred);
    self.handleValues(colRefDeferred);
    self.activeDeferrals.push(self.handlePaths());

    self.activeDeferrals.push(self.handleJoins());
    self.activeDeferrals.push(self.handleJoinConditions());
    self.activeDeferrals.push(self.handleAggregateFunctions());
    self.activeDeferrals.push(self.handleGroupBys());
    self.activeDeferrals.push(self.handleOrderBys());
    self.activeDeferrals.push(self.handleFilters());
    self.activeDeferrals.push(self.handlePopularTables(tablesDeferred));
    self.activeDeferrals.push(self.handlePopularColumns(columnsDeferred));

    $.when.apply($, self.activeDeferrals).always(function () {
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
  AutocompleteResults.prototype.handleColumnReference = function () {
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
        try {
          self.fetchFieldsForIdentifiers(self.parseResult.colRef.identifierChain, colRefCallback, function () {
            colRefDeferred.resolve({ type: 'T' });
          });
        } catch (e) {
          colRefDeferred.resolve({ type: 'T' });
        }  // TODO: Ignore for subqueries
      }
    } else {
      colRefDeferred.resolve({ type: 'T' });
    }
    return colRefDeferred;
  };

  AutocompleteResults.prototype.loadDatabases = function () {
    var self = this;
    var databasesDeferred = $.Deferred();
    self.apiHelper.loadDatabases({
      sourceType: self.snippet.type(),
      successCallback: databasesDeferred.resolve,
      timeout: AUTOCOMPLETE_TIMEOUT,
      silenceErrors: true,
      errorCallback: databasesDeferred.reject
    });
    return databasesDeferred;
  };

  AutocompleteResults.prototype.handleKeywords = function (colRefDeferred) {
    var self = this;
    if (self.parseResult.suggestKeywords) {
      var keywordSuggestions = $.map(self.parseResult.suggestKeywords, function (keyword) {
        return {
          value: self.parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value,
          meta: AutocompleterGlobals.i18n.meta.keyword,
          category: CATEGORIES.KEYWORD,
          weightAdjust: keyword.weight,
          popular: ko.observable(false),
          details: null
        };
      });
      self.appendEntries(keywordSuggestions);
    }

    if (self.parseResult.suggestColRefKeywords) {
      initLoading(self.loadingKeywords, colRefDeferred);
      // Wait for the column reference type to be resolved to pick the right keywords
      colRefDeferred.done(function (colRef) {
        var colRefKeywordSuggestions = [];
        Object.keys(self.parseResult.suggestColRefKeywords).forEach(function (typeForKeywords) {
          if (SqlFunctions.matchesType(self.snippet.type(), [typeForKeywords], [colRef.type.toUpperCase()])) {
            self.parseResult.suggestColRefKeywords[typeForKeywords].forEach(function (keyword) {
              colRefKeywordSuggestions.push({
                value: self.parseResult.lowerCase ? keyword.toLowerCase() : keyword,
                meta: AutocompleterGlobals.i18n.meta.keyword,
                category: CATEGORIES.COLREF_KEYWORD,
                popular: ko.observable(false),
                details: {
                  type: colRef.type
                }
              });
            })
          }
        });
        self.appendEntries(colRefKeywordSuggestions);
      });
    }
  };

  AutocompleteResults.prototype.handleIdentifiers = function () {
    var self = this;
    if (self.parseResult.suggestIdentifiers) {
      var identifierSuggestions = [];
      self.parseResult.suggestIdentifiers.forEach(function (identifier) {
        identifierSuggestions.push({
          value: identifier.name,
          meta: identifier.type,
          category: CATEGORIES.IDENTIFIER,
          popular: ko.observable(false),
          details: null
        });
      });
      self.appendEntries(identifierSuggestions);
    }
  };

  AutocompleteResults.prototype.handleColumnAliases = function () {
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
            popular: ko.observable(false),
            details: columnAlias
          });
        } else {
          columnAliasSuggestions.push({
            value: columnAlias.name,
            meta: type,
            category: CATEGORIES.COLUMN,
            popular: ko.observable(false),
            details: columnAlias
          });
        }
      });
      self.appendEntries(columnAliasSuggestions);
    }
  };

  AutocompleteResults.prototype.handleCommonTableExpressions = function () {
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
          popular: ko.observable(false),
          details: null
        });
      });
      self.appendEntries(commonTableExpressionSuggestions);
    }
  };

  AutocompleteResults.prototype.handleFunctions = function (colRefDeferred) {
    var self = this;
    if (self.parseResult.suggestFunctions) {
      var functionSuggestions = [];
      if (self.parseResult.suggestFunctions.types && self.parseResult.suggestFunctions.types[0] === 'COLREF') {
        initLoading(self.loadingFunctions, colRefDeferred);

        colRefDeferred.done(function (colRef) {
          var functionsToSuggest = SqlFunctions.getFunctionsWithReturnTypes(self.snippet.type(), [colRef.type.toUpperCase()], self.parseResult.suggestAggregateFunctions || false, self.parseResult.suggestAnalyticFunctions || false);

          Object.keys(functionsToSuggest).forEach(function (name) {
            functionSuggestions.push({
              category: CATEGORIES.UDF,
              value: name + '()',
              meta: functionsToSuggest[name].returnTypes.join('|'),
              weightAdjust: functionsToSuggest[name].returnTypes.filter(function (otherType) {
                  return otherType === colRef.type.toUpperCase();
              }).length > 0 ? 1 : 0,
              popular: ko.observable(false),
              details: functionsToSuggest[name]
            })
          });

          self.appendEntries(functionSuggestions);
        });
      } else {
        var types = self.parseResult.suggestFunctions.types || ['T'];
        var functionsToSuggest = SqlFunctions.getFunctionsWithReturnTypes(self.snippet.type(), types, self.parseResult.suggestAggregateFunctions || false, self.parseResult.suggestAnalyticFunctions || false);

        Object.keys(functionsToSuggest).forEach(function (name) {
          functionSuggestions.push({
            category: CATEGORIES.UDF,
            value: name + '()',
            meta: functionsToSuggest[name].returnTypes.join('|'),
            weightAdjust: functionsToSuggest[name].returnTypes.filter(function (otherType) {
              return otherType === types[0].toUpperCase();
            }).length > 0 ? 1 : 0,
            popular: ko.observable(false),
            details: functionsToSuggest[name]
          })
        });
        self.appendEntries(functionSuggestions);
      }
    }
  };

  AutocompleteResults.prototype.handleDatabases = function (databasesDeferred) {
    var self = this;
    var suggestDatabases = self.parseResult.suggestDatabases;
    if (suggestDatabases) {
      initLoading(self.loadingDatabases, databasesDeferred);

      var prefix = suggestDatabases.prependQuestionMark ? '? ' : '';
      if (suggestDatabases.prependFrom) {
        prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
      }
      var databaseSuggestions = [];

      databasesDeferred.done(function (dbs) {
        dbs.forEach(function (db) {
          databaseSuggestions.push({
            value: prefix + SqlUtils.backTickIfNeeded(self.snippet.type(), db) + (suggestDatabases.appendDot ? '.' : ''),
            filterValue: db,
            meta: AutocompleterGlobals.i18n.meta.database,
            category: CATEGORIES.DATABASE,
            popular: ko.observable(false),
            details: null
          })
        });
        self.appendEntries(databaseSuggestions);
      });
    }
  };

  AutocompleteResults.prototype.handleTables = function (databasesDeferred) {
    var self = this;
    var tablesDeferred = $.Deferred();

    if (self.parseResult.suggestTables) {
      var suggestTables = self.parseResult.suggestTables;
      var fetchTables = function () {
        initLoading(self.loadingTables, tablesDeferred);
        tablesDeferred.done(self.appendEntries);

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
                value: prefix + SqlUtils.backTickIfNeeded(self.snippet.type(), tableMeta.name),
                filterValue: tableMeta.name,
                tableName: tableMeta.name,
                meta: AutocompleterGlobals.i18n.meta[tableMeta.type.toLowerCase()],
                category: CATEGORIES.TABLE,
                popular: ko.observable(false),
                details: details
              });
            });
            tablesDeferred.resolve(tableSuggestions);
          },
          silenceErrors: true,
          errorCallback: tablesDeferred.reject,
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
            tablesDeferred.reject();
          }
        });
      } else if (self.snippet.type() == 'impala' && self.parseResult.suggestTables.identifierChain && self.parseResult.suggestTables.identifierChain.length > 1) {
        self.parseResult.suggestColumns = { tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }] };
        tablesDeferred.reject();
      } else {
        fetchTables();
      }
    } else {
      tablesDeferred.reject();
    }

    return tablesDeferred;
  };

  AutocompleteResults.prototype.handleColumns = function (colRefDeferred, tablesDeferred) {
    var self = this;
    var columnsDeferred = $.Deferred();

    tablesDeferred.always(function () {
      if (self.parseResult.suggestColumns) {
        initLoading(self.loadingColumns, columnsDeferred);
        columnsDeferred.done(self.appendEntries);

        var suggestColumns = self.parseResult.suggestColumns;
        var columnSuggestions = [];
        // For multiple tables we need to merge and make sure identifiers are unique
        var columnDeferrals = [];

        if (suggestColumns.types && suggestColumns.types[0] === 'COLREF') {
          colRefDeferred.done(function (colRef) {
            suggestColumns.tables.forEach(function (table) {
              columnDeferrals.push(self.addColumns(table, [colRef.type.toUpperCase()], columnSuggestions));
            });
          });
        } else {
          suggestColumns.tables.forEach(function (table) {
            columnDeferrals.push(self.addColumns(table, suggestColumns.types || ['T'], columnSuggestions));
          });
        }

        $.when.apply($, columnDeferrals).always(function () {
          self.mergeColumns(columnSuggestions);
          if (self.snippet.type() === 'hive' && /[^\.]$/.test(self.editor().getTextBeforeCursor())) {
            columnSuggestions.push({
              value: 'BLOCK__OFFSET__INSIDE__FILE',
              meta: AutocompleterGlobals.i18n.meta.virtual,
              category: CATEGORIES.VIRTUAL_COLUMN,
              popular: ko.observable(false),
              details: null
            });
            columnSuggestions.push({
              value: 'INPUT__FILE__NAME',
              meta: AutocompleterGlobals.i18n.meta.virtual,
              category: CATEGORIES.VIRTUAL_COLUMN,
              popular: ko.observable(false),
              details: null
            });
          }
          columnsDeferred.resolve(columnSuggestions);
        });
      } else {
        columnsDeferred.reject();
      }
    });

    return columnsDeferred;
  };

  AutocompleteResults.prototype.addColumns = function (table, types, columnSuggestions) {
    var self = this;
    var addColumnsDeferred = $.Deferred();

    if (typeof table.identifierChain !== 'undefined' && table.identifierChain.length === 1 && typeof table.identifierChain[0].cte !== 'undefined') {
      if (typeof self.parseResult.commonTableExpressions !== 'undefined' && self.parseResult.commonTableExpressions.length > 0) {
        self.parseResult.commonTableExpressions.every(function (cte) {
          if (cte.alias === table.identifierChain[0].cte) {
            cte.columns.forEach(function (column) {
              var type = typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
              if (typeof column.alias !== 'undefined') {
                columnSuggestions.push({
                  value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.alias),
                  filterValue: column.alias,
                  meta: type,
                  category: CATEGORIES.COLUMN,
                  table: table,
                  popular: ko.observable(false),
                  details: column
                })
              } else if (typeof column.identifierChain !== 'undefined' && column.identifierChain.length > 0 && typeof column.identifierChain[column.identifierChain.length - 1].name !== 'undefined') {
                columnSuggestions.push({
                  value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.identifierChain[column.identifierChain.length - 1].name),
                  filterValue: column.identifierChain[column.identifierChain.length - 1].name,
                  meta: type,
                  category: CATEGORIES.COLUMN,
                  table: table,
                  popular: ko.observable(false),
                  details: column
                })
              }
            });
            return false;
          }
          return true;
        })
      }
      addColumnsDeferred.resolve();
    } else if (typeof table.identifierChain !== 'undefined' && table.identifierChain.length === 1 && typeof table.identifierChain[0].subQuery !== 'undefined') {
      var foundSubQuery = locateSubQuery(self.parseResult.subQueries, table.identifierChain[0].subQuery);

      var addSubQueryColumns = function (subQueryColumns) {
        subQueryColumns.forEach(function (column) {
          if (column.alias || column.identifierChain) {
            // TODO: Potentially fetch column types for sub-queries, possible performance hit.
            var type = typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
            if (column.alias) {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.alias),
                filterValue: column.alias,
                meta: type,
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            } else if (column.identifierChain && column.identifierChain.length > 0) {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.identifierChain[column.identifierChain.length - 1].name),
                filterValue: column.identifierChain[column.identifierChain.length - 1].name,
                meta: type,
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            }
          } else if (column.subQuery && foundSubQuery.subQueries) {
            var foundNestedSubQuery = locateSubQuery(foundSubQuery.subQueries, column.subQuery);
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
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.name) + '[]',
                filterValue: column.name,
                meta: 'map',
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            } else if (column.type.indexOf('map') === 0) {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.name),
                filterValue: column.name,
                meta: 'map',
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            } else if (column.type.indexOf('struct') === 0) {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.name),
                filterValue: column.name,
                meta: 'struct',
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            } else if (column.type.indexOf('array') === 0 && self.snippet.type() === 'hive') {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.name) + '[]',
                filterValue: column.name,
                meta: 'array',
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            } else if (column.type.indexOf('array') === 0) {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.name),
                filterValue: column.name,
                meta: 'array',
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            } else if (types[0].toUpperCase() !== 'T' && types.filter(function (type) { return type.toUpperCase() === column.type.toUpperCase() }).length > 0) {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.name),
                filterValue: column.name,
                meta: column.type,
                category: CATEGORIES.COLUMN,
                weightAdjust: 1,
                table: table,
                popular: ko.observable(false),
                details: column
              })
            } else if (SqlFunctions.matchesType(self.snippet.type(), types, [column.type.toUpperCase()]) ||
                SqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
              columnSuggestions.push({
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), column.name),
                filterValue: column.name,
                meta: column.type,
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
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
              value: SqlUtils.backTickIfNeeded(self.snippet.type(), column),
              filterValue: column,
              meta: 'column',
              category: CATEGORIES.COLUMN,
              table: table,
              popular: ko.observable(false),
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
            popular: ko.observable(false),
            details: data
          });
          columnSuggestions.push({
            value: 'value',
            meta: 'value',
            category: CATEGORIES.COLUMN,
            table: table,
            popular: ko.observable(false),
            details: data
          });
        }
        if (data.type === 'struct') {
          data.fields.forEach(function (field) {
            field.database = data.database;
            field.table = data.table;
            field.identifierChain = data.identifierChain;

            columnSuggestions.push({
              value: SqlUtils.backTickIfNeeded(self.snippet.type(), field.name),
              filterValue: field.name,
              meta: field.type,
              category: CATEGORIES.COLUMN,
              table: table,
              popular: ko.observable(false),
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
                value: SqlUtils.backTickIfNeeded(self.snippet.type(), field.name),
                filterValue: field.name,
                meta: field.type,
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
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
                    value: SqlUtils.backTickIfNeeded(self.snippet.type(), field.name) + '[]',
                    filterValue: field.name,
                    meta: field.type,
                    category: CATEGORIES.COLUMN,
                    table: table,
                    popular: ko.observable(false),
                    details: field
                  });
                } else {
                  columnSuggestions.push({
                    value: SqlUtils.backTickIfNeeded(self.snippet.type(), field.name),
                    filterValue: field.name,
                    meta: field.type,
                    category: CATEGORIES.COLUMN,
                    table: table,
                    popular: ko.observable(false),
                    details: field
                  });
                }
              } else if (SqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
                  SqlFunctions.matchesType(self.snippet.type(), [field.type.toUpperCase()], types)) {
                columnSuggestions.push({
                  value: SqlUtils.backTickIfNeeded(self.snippet.type(), field.name),
                  filterValue: field.name,
                  meta: field.type,
                  category: CATEGORIES.COLUMN,
                  table: table,
                  popular: ko.observable(false),
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
                popular: ko.observable(false),
                details: data.item
              });
            }
          }
        }
        addColumnsDeferred.resolve();
      };

      try {
        self.fetchFieldsForIdentifiers(table.identifierChain, callback, addColumnsDeferred.resolve);
      } catch (e) {
        addColumnsDeferred.resolve();
      } // TODO: Ignore for subqueries
    }
    return addColumnsDeferred;
  };

  AutocompleteResults.prototype.mergeColumns = function (columnSuggestions) {
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

  AutocompleteResults.prototype.handleValues = function (colRefDeferred) {
    var self = this;
    var suggestValues = self.parseResult.suggestValues;
    if (suggestValues) {
      var valueSuggestions = [];
      if (self.parseResult.colRef && self.parseResult.colRef.identifierChain) {
        valueSuggestions.push({
          value: '${' + self.parseResult.colRef.identifierChain[self.parseResult.colRef.identifierChain.length - 1].name + '}',
          meta: AutocompleterGlobals.i18n.meta.variable,
          category: CATEGORIES.VARIABLE,
          popular: ko.observable(false),
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
              meta: AutocompleterGlobals.i18n.meta.sample,
              category: CATEGORIES.SAMPLE,
              popular: ko.observable(false),
              details: null
            })
          });
        }
        self.appendEntries(valueSuggestions);
      });
    }
  };

  AutocompleteResults.prototype.handlePaths = function () {
    var self = this;
    var suggestHdfs = self.parseResult.suggestHdfs;
    var pathsDeferred = $.Deferred();

    if (suggestHdfs) {
      initLoading(self.loadingPaths, pathsDeferred);
      pathsDeferred.done(self.appendEntries);

      var parts = suggestHdfs.path.split('/');
      // Drop the first " or '
      parts.shift();
      // Last one is either partial name or empty
      parts.pop();

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
                  popular: ko.observable(false),
                  details: file
                });
              }
            });
            pathsDeferred.resolve(pathSuggestions);
          }
          pathsDeferred.reject();
        },
        silenceErrors: true,
        errorCallback: pathsDeferred.reject,
        timeout: AUTOCOMPLETE_TIMEOUT
      });
    } else {
      pathsDeferred.reject();
    }
    return pathsDeferred;
  };

  AutocompleteResults.prototype.handleJoins = function () {
    var self = this;
    var joinsDeferred = $.Deferred();
    var suggestJoins = self.parseResult.suggestJoins;
    if (HAS_OPTIMIZER && suggestJoins) {
      initLoading(self.loadingJoins, joinsDeferred);
      joinsDeferred.done(self.appendEntries);

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
                popular: ko.observable(true),
                details: value
              });
            }
          });
          joinSuggestions.forEach(function (suggestion) {
            suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.totalQueryCount : Math.round(100 * suggestion.details.totalQueryCount / totalCount);
            suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
          });
          joinsDeferred.resolve(joinSuggestions);
        },
        errorCallback: joinsDeferred.reject
      });
    } else {
      joinsDeferred.reject();
    }
    return joinsDeferred;
  };

  AutocompleteResults.prototype.handleJoinConditions = function () {
    var self = this;
    var joinConditionsDeferred = $.Deferred();
    var suggestJoinConditions = self.parseResult.suggestJoinConditions;
    if (HAS_OPTIMIZER && suggestJoinConditions) {
      initLoading(self.loadingJoinConditions, joinConditionsDeferred);
      joinConditionsDeferred.done(self.appendEntries);

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
                popular: ko.observable(true),
                details: value
              });
            }
          });
          joinConditionSuggestions.forEach(function (suggestion) {
            suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.totalQueryCount : Math.round(100 * suggestion.details.totalQueryCount / totalCount);
            suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
          });

          joinConditionsDeferred.resolve(joinConditionSuggestions);
        },
        errorCallback: joinConditionsDeferred.reject
      });
    } else {
      joinConditionsDeferred.reject();
    }

    return joinConditionsDeferred;
  };

  AutocompleteResults.prototype.handleAggregateFunctions = function () {
    var self = this;
    var aggregateFunctionsDeferred = $.Deferred();

    var suggestAggregateFunctions = self.parseResult.suggestAggregateFunctions;
    if (HAS_OPTIMIZER && suggestAggregateFunctions && suggestAggregateFunctions.tables.length > 0) {
      initLoading(self.loadingAggregateFunctions, aggregateFunctionsDeferred);
      aggregateFunctionsDeferred.done(self.appendEntries);

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
                weightAdjust: Math.min(value.totalQueryCount, 99),
                popular: ko.observable(true),
                details: value
              });
            });

            aggregateFunctionsSuggestions.forEach(function (suggestion) {
              suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.totalQueryCount : Math.round(100 * suggestion.details.totalQueryCount / totalCount);
              suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
            });
          }
          aggregateFunctionsDeferred.resolve(aggregateFunctionsSuggestions);
        },
        errorCallback: aggregateFunctionsDeferred.reject
      });
    } else {
      aggregateFunctionsDeferred.reject();
    }
    return aggregateFunctionsDeferred;
  };

  AutocompleteResults.prototype.handleGroupBys = function () {
    var self = this;
    var groupBysDeferred = $.Deferred();
    var suggestGroupBys = self.parseResult.suggestGroupBys;
    if (HAS_OPTIMIZER && suggestGroupBys) {
      initLoading(self.loadingGroupBys, groupBysDeferred);
      groupBysDeferred.done(self.appendEntries);

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
                weightAdjust: Math.min(value.columnCount, 99),
                popular: ko.observable(true),
                details: value
              });
            });
          }
          groupBysDeferred.resolve(groupBySuggestions);
        },
        errorCallback: groupBysDeferred.reject
      });
    } else {
      groupBysDeferred.reject();
    }

    return groupBysDeferred;
  };

  AutocompleteResults.prototype.handleOrderBys = function () {
    var self = this;
    var orderBysDeferred = $.Deferred();
    var suggestOrderBys = self.parseResult.suggestOrderBys;
    if (HAS_OPTIMIZER && suggestOrderBys) {
      initLoading(self.loadingOrderBys, orderBysDeferred);
      orderBysDeferred.done(self.appendEntries);

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
                weightAdjust: Math.min(value.columnCount, 99),
                popular: ko.observable(true),
                details: value
              });
            });
          }
          orderBysDeferred.resolve(orderBySuggestions);
        },
        errorCallback: orderBysDeferred.reject
      });
    } else {
      orderBysDeferred.reject();
    }
    return orderBysDeferred;
  };

  AutocompleteResults.prototype.handleFilters = function () {
    var self = this;
    var filtersDeferred = $.Deferred();
    var suggestFilters = self.parseResult.suggestFilters;
    if (HAS_OPTIMIZER && suggestFilters) {
      initLoading(self.loadingFilters, filtersDeferred);
      filtersDeferred.done(self.appendEntries);

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
                      popular: ko.observable(true),
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

          filtersDeferred.resolve(filterSuggestions);
        },
        errorCallback: filtersDeferred.reject
      });
    } else {
      filtersDeferred.reject();
    }
    return filtersDeferred;
  };

  AutocompleteResults.prototype.handlePopularTables = function (tablesDeferred) {
    var self = this;
    var popularTablesDeferred = $.Deferred();
    if (HAS_OPTIMIZER && self.parseResult.suggestTables) {
      initLoading(self.loadingPopularTables, popularTablesDeferred);

      self.apiHelper.fetchNavOptTopTables({
        database: self.activeDatabase,
        sourceType: self.snippet.type(),
        silenceErrors: true,
        successCallback: function (data) {
          var popularityIndex = {};
          if (data.top_tables.length == 0) {
            popularTablesDeferred.reject();
            return;
          }
          data.top_tables.forEach(function (topTable) {
            popularityIndex[topTable.name] = topTable;
          });

          tablesDeferred.done(function (tableSuggestions) {
            var totalMatchedPopularity = 0;
            var matchedSuggestions = [];
            tableSuggestions.forEach(function (suggestion) {
              var topTable = popularityIndex[suggestion.tableName];
              if (typeof topTable !== 'undefined') {
                suggestion.popular(true);
                if (!suggestion.details) {
                  suggestion.details = {};
                }
                suggestion.details.popularity = topTable;
                totalMatchedPopularity += topTable.popularity;
                matchedSuggestions.push(suggestion);
              }
            });
            popularTablesDeferred.resolve(data.top_tables);
            if (matchedSuggestions.length > 0) {
              adjustWeightsBasedOnPopularity(matchedSuggestions, totalMatchedPopularity);
              self.entries.notifySubscribers();
            }
          });
        },
        errorCallback: popularTablesDeferred.reject
      });
    } else {
      popularTablesDeferred.reject();
    }
    return popularTablesDeferred
  };

  AutocompleteResults.prototype.handlePopularColumns = function (columnsDeferred) {
    var self = this;
    var popularColumnsDeferred = $.Deferred();
    var suggestColumns = self.parseResult.suggestColumns;
    // TODO: Handle tables from different databases
    if (HAS_OPTIMIZER && suggestColumns && suggestColumns.source !== 'undefined') {
      initLoading(self.loadingPopularColumns, popularColumnsDeferred);

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
            popularColumnsDeferred.reject();
            return;
          }

          var popularityIndex = {};
          popularColumns.forEach(function (popularColumn) {
            popularityIndex[popularColumn.columnName.toLowerCase()] = popularColumn;
          });

          columnsDeferred.done(function (columns) {
            var totalMatchedPopularity = 0;
            var matchedSuggestions = [];
            columns.forEach(function (suggestion) {
              if (typeof suggestion.table === 'undefined') {
                return;
              }
              var topColumn = popularityIndex[suggestion.value.toLowerCase()];
              if (typeof topColumn !== 'undefined') {
                suggestion.popular(true);
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
            popularColumnsDeferred.reject();
            if (matchedSuggestions.length > 0) {
              adjustWeightsBasedOnPopularity(matchedSuggestions, totalMatchedPopularity);
              self.entries.notifySubscribers();
            }
          });
        },
        errorCallback: popularColumnsDeferred.reject
      });
    } else {
      popularColumnsDeferred.reject();
    }
    return popularColumnsDeferred;
  };

  AutocompleteResults.prototype.createNavOptIdentifier = function (navOptTableName, navOptColumnName, tables) {
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

  AutocompleteResults.prototype.createNavOptIdentifierForColumn = function (navOptColumn, tables) {
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

  AutocompleteResults.prototype.convertNavOptQualifiedIdentifier = function (qualifiedIdentifier, tables) {
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
  AutocompleteResults.prototype.fetchFieldsForIdentifiers = function (originalIdentifierChain, callback, errorCallback) {
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
      if (identifierChain.length > 1 && $.grep(identifierChain, function (e) { return e.subQuery; }).length == 0) {
        self.apiHelper.loadDatabases({
          sourceType: self.snippet.type(),
          timeout: AUTOCOMPLETE_TIMEOUT,
          successCallback: function (data) {
            try {
              var foundDb = data.filter(function (db) {
                return db.toLowerCase() === identifierChain[0].name.toLowerCase();
              });
              var databaseName = foundDb.length > 0 ? identifierChain.shift().name : self.activeDatabase;
              var tableName = identifierChain.shift().name;
              fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
            } catch (e) {
              callback([]);
            } // TODO: Ignore for subqueries
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

  return AutocompleteResults;
})();

var SqlAutocompleter3 = (function () {
  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @constructor
   */
  function SqlAutocompleter3(options) {
    var self = this;
    self.snippet = options.snippet;
    self.editor = options.editor;
    self.suggestions = new AutocompleteResults(options);
  }

  SqlAutocompleter3.prototype.autocomplete = function () {
    var self = this;
    try {
      var parseResult = sql.parseSql(self.editor().getTextBeforeCursor(), self.editor().getTextAfterCursor(), self.snippet.type(), false);

      if (typeof hueDebug !== 'undefined' && hueDebug.showParseResult) {
        console.log(parseResult);
      }

      self.suggestions.update(parseResult);
    } catch(e) {
      if (typeof console.warn !== 'undefined') {
        console.warn(e);
      }
      // This prevents Ace from inserting garbled text in case of exception
      huePubSub.publish('hue.ace.autocompleter.done');
    }
  };

  return SqlAutocompleter3;
})();
