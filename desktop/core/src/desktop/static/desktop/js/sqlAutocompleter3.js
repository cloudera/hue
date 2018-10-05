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
    ALL: { id: 'all', color: HueColors.BLUE, label: HUE_I18n.autocomplete.category.all },
    POPULAR: { id: 'popular', color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular },
    POPULAR_AGGREGATE: { id: 'popularAggregate', weight: 1500, color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular, detailsTemplate: 'agg-udf' },
    POPULAR_GROUP_BY: { id: 'popularGroupBy', weight: 1300, color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular, detailsTemplate: 'group-by' },
    POPULAR_ORDER_BY: { id: 'popularOrderBy', weight: 1200, color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular, detailsTemplate: 'order-by' },
    POPULAR_FILTER: { id: 'popularFilter', weight: 1400, color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular, detailsTemplate: 'filter' },
    POPULAR_ACTIVE_JOIN: { id: 'popularActiveJoin', weight: 1500, color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular, detailsTemplate: 'join' },
    POPULAR_JOIN_CONDITION: { id: 'popularJoinCondition', weight: 1500, color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular, detailsTemplate: 'join-condition' },
    COLUMN: { id: 'column', weight: 1000, color: COLORS.COLUMN, label: HUE_I18n.autocomplete.category.column, detailsTemplate: 'column' },
    SAMPLE: { id: 'sample',weight: 900, color: COLORS.SAMPLE, label: HUE_I18n.autocomplete.category.sample, detailsTemplate: 'value' },
    IDENTIFIER: { id: 'identifier', weight: 800, color: COLORS.IDENT_CTE_VAR, label: HUE_I18n.autocomplete.category.identifier, detailsTemplate: 'identifier' },
    CTE: { id: 'cte', weight: 700, color: COLORS.IDENT_CTE_VAR, label: HUE_I18n.autocomplete.category.cte, detailsTemplate: 'cte' },
    TABLE: { id: 'table', weight: 600, color: COLORS.TABLE, label: HUE_I18n.autocomplete.category.table, detailsTemplate: 'table' },
    DATABASE: { id: 'database', weight: 500, color: COLORS.DATABASE, label: HUE_I18n.autocomplete.category.database, detailsTemplate: 'database' },
    UDF: { id: 'udf', weight: 400, color: COLORS.UDF, label: HUE_I18n.autocomplete.category.udf, detailsTemplate: 'udf' },
    OPTION: { id: 'option', weight: 400, color: COLORS.UDF, label: HUE_I18n.autocomplete.category.option, detailsTemplate: 'option' },
    HDFS: { id: 'hdfs', weight: 300, color: COLORS.HDFS, label: HUE_I18n.autocomplete.category.hdfs, detailsTemplate: 'hdfs' },
    VIRTUAL_COLUMN: { id: 'virtualColumn', weight: 200, color: COLORS.COLUMN, label: HUE_I18n.autocomplete.category.column, detailsTemplate: 'column' },
    COLREF_KEYWORD: { id: 'colrefKeyword', weight: 100, color: COLORS.KEYWORD, label: HUE_I18n.autocomplete.category.keyword, detailsTemplate: 'keyword' },
    VARIABLE: { id: 'variable', weight: 50, color: COLORS.IDENT_CTE_VAR, label: HUE_I18n.autocomplete.category.variable, detailsTemplate: 'variable' },
    KEYWORD: { id: 'keyword', weight: 0, color: COLORS.KEYWORD, label: HUE_I18n.autocomplete.category.keyword, detailsTemplate: 'keyword' },
    POPULAR_JOIN: { id: 'popularJoin', weight: 1500, color: COLORS.POPULAR, label: HUE_I18n.autocomplete.category.popular, detailsTemplate: 'join' }
  };

  var POPULAR_CATEGORIES = [CATEGORIES.POPULAR_AGGREGATE, CATEGORIES.POPULAR_GROUP_BY, CATEGORIES.POPULAR_ORDER_BY, CATEGORIES.POPULAR_FILTER, CATEGORIES.POPULAR_ACTIVE_JOIN, CATEGORIES.POPULAR_JOIN_CONDITION, CATEGORIES.POPULAR_JOIN];

  var adjustWeightsBasedOnPopularity = function(suggestions, totalPopularity) {
    suggestions.forEach(function (suggestion) {
      var relativePopularity = Math.round(100 * suggestion.details.popularity.popularity / totalPopularity);
      if (relativePopularity < 5) {
        suggestion.popular(false);
      } else {
        suggestion.details.popularity.relativePopularity = Math.round(100 * suggestion.details.popularity.popularity / totalPopularity);
        suggestion.weightAdjust = suggestion.details.popularity.relativePopularity;
      }
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
      return hueUtils.equalIgnoreCase(knownSubQuery.alias, subQueryName)
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

    self.sortOverride = null;

    huePubSub.subscribe('editor.autocomplete.temporary.sort.override', function (sortOverride) {
      self.sortOverride = sortOverride;
    });

    self.entries = ko.observableArray();

    self.lastKnownRequests = [];
    self.cancellablePromises = [];
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
        result = SqlUtils.autocompleteFilter(self.filter(), result);
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

      SqlUtils.sortSuggestions(result, self.filter(), self.sortOverride);
      self.sortOverride = null;
      return result;
    }).extend({ rateLimit: 200 });
  }

  AutocompleteResults.prototype.cancelRequests = function () {
    var self = this;

    while (self.lastKnownRequests.length) {
      self.apiHelper.cancelActiveRequest(self.lastKnownRequests.pop());
    }

    while (self.cancellablePromises.length) {
      var promise = self.cancellablePromises.pop();
      if (promise.cancel) {
        promise.cancel();
      }
    }
  };

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
    self.handleOptions();
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
    self.activeDeferrals.push(self.handleGroupBys(columnsDeferred));
    self.activeDeferrals.push(self.handleOrderBys(columnsDeferred));
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
      var colRefCallback = function (catalogEntry) {
        self.cancellablePromises.push(catalogEntry.getSourceMeta({ silenceErrors: true, cancellable: true }).done(function (sourceMeta) {
          if (typeof sourceMeta.type !== 'undefined') {
            colRefDeferred.resolve(sourceMeta);
          } else {
            colRefDeferred.resolve({ type: 'T' })
          }
        }).fail(function () {
          colRefDeferred.resolve({ type: 'T' })
        }));
      };

      var foundVarRef = self.parseResult.colRef.identifierChain.some(function (identifier) {
        return typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0;
      });

      if (foundVarRef) {
        colRefDeferred.resolve({ type: 'T' });
      } else {
        self.fetchFieldsForIdentifiers(self.parseResult.colRef.identifierChain).done(colRefCallback).fail(function () {
          colRefDeferred.resolve({ type: 'T' });
        });
      }
    } else {
      colRefDeferred.resolve({ type: 'T' });
    }
    return colRefDeferred;
  };

  AutocompleteResults.prototype.loadDatabases = function () {
    var self = this;
    var databasesDeferred = $.Deferred();
    DataCatalog.getEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), path: [] }).done(function (entry) {
      self.cancellablePromises.push(entry.getChildren({ silenceErrors: true, cancellable: true }).done(function (databases) {
        databasesDeferred.resolve(databases);
      }).fail(databasesDeferred.reject));
    }).fail(databasesDeferred.reject);
    return databasesDeferred;
  };

  AutocompleteResults.prototype.handleKeywords = function (colRefDeferred) {
    var self = this;
    if (self.parseResult.suggestKeywords) {
      var keywordSuggestions = $.map(self.parseResult.suggestKeywords, function (keyword) {
        return {
          value: self.parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value,
          meta: HUE_I18n.autocomplete.meta.keyword,
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
                meta: HUE_I18n.autocomplete.meta.keyword,
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
            meta: HUE_I18n.autocomplete.meta.alias,
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
          meta: HUE_I18n.autocomplete.meta.commonTableExpression,
          category: CATEGORIES.CTE,
          popular: ko.observable(false),
          details: null
        });
      });
      self.appendEntries(commonTableExpressionSuggestions);
    }
  };

  AutocompleteResults.prototype.handleOptions = function () {
    var self = this;
    if (self.parseResult.suggestSetOptions) {
      var suggestions = [];
      SqlSetOptions.suggestOptions(self.snippet.type(), suggestions, CATEGORIES.OPTION);
      self.appendEntries(suggestions);
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
              weightAdjust: colRef.type.toUpperCase() !== 'T' && functionsToSuggest[name].returnTypes.some(function (otherType) {
                  return otherType === colRef.type.toUpperCase();
              }) ? 1 : 0,
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
            weightAdjust: types[0].toUpperCase() !== 'T' && functionsToSuggest[name].returnTypes.some(function (otherType) {
              return otherType === types[0].toUpperCase();
            }) ? 1 : 0,
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

      databasesDeferred.done(function (catalogEntries) {
        catalogEntries.forEach(function (dbEntry) {
          databaseSuggestions.push({
            value: prefix + SqlUtils.backTickIfNeeded(self.snippet.type(), dbEntry.name) + (suggestDatabases.appendDot ? '.' : ''),
            filterValue: dbEntry.name,
            meta: HUE_I18n.autocomplete.meta.database,
            category: CATEGORIES.DATABASE,
            popular: ko.observable(false),
            hasCatalogEntry: true,
            details: dbEntry
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

        DataCatalog.getEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), path: [ database ]}).done(function (dbEntry) {
          self.cancellablePromises.push(dbEntry.getChildren({ silenceErrors: true, cancellable: true }).done(function (tableEntries) {
            var tableSuggestions = [];

            tableEntries.forEach(function (tableEntry) {
              if (suggestTables.onlyTables && !tableEntry.isTable() || suggestTables.onlyViews && !tableEntry.isView()) {
                return;
              }
              tableSuggestions.push({
                value: prefix + SqlUtils.backTickIfNeeded(self.snippet.type(), tableEntry.name),
                filterValue: tableEntry.name,
                tableName: tableEntry.name,
                meta: HUE_I18n.autocomplete.meta[tableEntry.getType().toLowerCase()],
                category: CATEGORIES.TABLE,
                popular: ko.observable(false),
                hasCatalogEntry: true,
                details: tableEntry
              });
            });
            tablesDeferred.resolve(tableSuggestions);
          }).fail(tablesDeferred.reject));
        }).fail(tablesDeferred.reject);
      };

      if (self.snippet.type() === 'impala' && self.parseResult.suggestTables.identifierChain && self.parseResult.suggestTables.identifierChain.length === 1) {
        databasesDeferred.done(function (databases) {
          var foundDb = databases.some(function (dbEntry) {
            return hueUtils.equalIgnoreCase(dbEntry.name, self.parseResult.suggestTables.identifierChain[0].name);
          });
          if (foundDb) {
            fetchTables();
          } else {
            self.parseResult.suggestColumns = { tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }] };
            tablesDeferred.reject();
          }
        });
      } else if (self.snippet.type() === 'impala' && self.parseResult.suggestTables.identifierChain && self.parseResult.suggestTables.identifierChain.length > 1) {
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

        var waitForCols = function () {
          $.when.apply($, columnDeferrals).always(function () {
            self.mergeColumns(columnSuggestions);
            if (self.snippet.type() === 'hive' && /[^\.]$/.test(self.editor().getTextBeforeCursor())) {
              columnSuggestions.push({
                value: 'BLOCK__OFFSET__INSIDE__FILE',
                meta: HUE_I18n.autocomplete.meta.virtual,
                category: CATEGORIES.VIRTUAL_COLUMN,
                popular: ko.observable(false),
                details: { name: 'BLOCK__OFFSET__INSIDE__FILE' }
              });
              columnSuggestions.push({
                value: 'INPUT__FILE__NAME',
                meta: HUE_I18n.autocomplete.meta.virtual,
                category: CATEGORIES.VIRTUAL_COLUMN,
                popular: ko.observable(false),
                details: { name: 'INPUT__FILE__NAME' }
              });
            }
            columnsDeferred.resolve(columnSuggestions);
          });
        };

        if (suggestColumns.types && suggestColumns.types[0] === 'COLREF') {
          colRefDeferred.done(function (colRef) {
            suggestColumns.tables.forEach(function (table) {
              columnDeferrals.push(self.addColumns(table, [colRef.type.toUpperCase()], columnSuggestions));
            });
            waitForCols();
          });
        } else {
          suggestColumns.tables.forEach(function (table) {
            columnDeferrals.push(self.addColumns(table, suggestColumns.types || ['T'], columnSuggestions));
          });
          waitForCols();
        }
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
          if (hueUtils.equalIgnoreCase(cte.alias, table.identifierChain[0].cte)) {
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
    } else if (typeof table.identifierChain !== 'undefined') {
      var addColumnsFromEntry = function (dataCatalogEntry) {
        self.cancellablePromises.push(dataCatalogEntry.getSourceMeta({ silenceErrors: true, cancellable: true }).done(function (sourceMeta) {
          self.cancellablePromises.push(dataCatalogEntry.getChildren({ silenceErrors: true, cancellable: true })
            .done(function (childEntries) {
              childEntries.forEach(function (childEntry) {
                var name = SqlUtils.backTickIfNeeded(self.snippet.type(), childEntry.name);
                if (self.snippet.type() === 'hive' && (childEntry.isArray() || childEntry.isMap())) {
                  name += '[]';
                }
                  if (SqlFunctions.matchesType(self.snippet.type(), types, [childEntry.getType().toUpperCase()])
                      || SqlFunctions.matchesType(self.snippet.type(), [childEntry.getType().toUpperCase()], types)
                      || childEntry.getType === 'column'
                      || childEntry.isComplex()) {
                    columnSuggestions.push({
                      value: name,
                      meta: childEntry.getType(),
                      table: table,
                      category: CATEGORIES.COLUMN,
                      popular: ko.observable(false),
                      weightAdjust: types[0].toUpperCase() !== 'T' && types.some(function (type) { return hueUtils.equalIgnoreCase(type, childEntry.getType()) }) ? 1 : 0,
                      hasCatalogEntry: true,
                      details: childEntry
                    });
                  }
              });
              if (self.snippet.type() === 'hive' && (dataCatalogEntry.isArray() || dataCatalogEntry.isMap()) ) {
                // Remove 'item' or 'value' and 'key' for Hive
                columnSuggestions.pop();
                if (dataCatalogEntry.isMap()) {
                  columnSuggestions.pop();
                }
              }

              var complexExtras = sourceMeta.value && sourceMeta.value.fields || sourceMeta.item && sourceMeta.item.fields;
              if ((self.snippet.type() === 'impala' || self.snippet.type() === 'hive') && complexExtras) {
                complexExtras.forEach(function (field) {
                  var fieldType = field.type.indexOf('<') !== -1 ? field.type.substring(0, field.type.indexOf('<')) : field.type;
                  columnSuggestions.push({
                    value: field.name,
                    meta: fieldType,
                    table: table,
                    category: CATEGORIES.COLUMN,
                    popular: ko.observable(false),
                    weightAdjust: types[0].toUpperCase() !== 'T' && types.some(function (type) { return hueUtils.equalIgnoreCase(type, fieldType) }) ? 1 : 0,
                    hasCatalogEntry: false,
                    details: field
                  });
                });
              }
              addColumnsDeferred.resolve();
            }).fail(addColumnsDeferred.reject));
        }).fail(addColumnsDeferred.reject));
      };

      if (self.parseResult.suggestColumns && self.parseResult.suggestColumns.identifierChain) {
        self.fetchFieldsForIdentifiers(table.identifierChain.concat(self.parseResult.suggestColumns.identifierChain)).done(addColumnsFromEntry).fail(addColumnsDeferred.reject);
      } else {
        self.fetchFieldsForIdentifiers(table.identifierChain).done(addColumnsFromEntry).fail(addColumnsDeferred.reject);
      }
    } else {
      addColumnsDeferred.resolve();
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
          meta: HUE_I18n.autocomplete.meta.variable,
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
              meta: HUE_I18n.autocomplete.meta.sample,
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

      var path = suggestHdfs.path;
      if (path === '') {
        self.appendEntries([{
          value: 'adl://',
          meta: HUE_I18n.autocomplete.meta.keyword,
          category: CATEGORIES.KEYWORD,
          weightAdjust: 0,
          popular: ko.observable(false),
          details: null
        },{
          value: 's3a://',
          meta: HUE_I18n.autocomplete.meta.keyword,
          category: CATEGORIES.KEYWORD,
          weightAdjust: 0,
          popular: ko.observable(false),
          details: null
        },{
          value: 'hdfs://',
          meta: HUE_I18n.autocomplete.meta.keyword,
          category: CATEGORIES.KEYWORD,
          weightAdjust: 0,
          popular: ko.observable(false),
          details: null
        },{
          value: '/',
          meta: 'dir',
          category: CATEGORIES.HDFS,
          popular: ko.observable(false),
          details: null
        }]);
      }

      var fetchFunction = 'fetchHdfsPath';

      if (/^s3a:\/\//i.test(path)) {
        fetchFunction = 'fetchS3Path';
        path = path.substring(5);
      } else if (/^adl:\/\//i.test(path)) {
        fetchFunction = 'fetchAdlsPath';
        path = path.substring(5);
      } else if (/^hdfs:\/\//i.test(path)) {
        path = path.substring(6);
      }

      var parts = path.split('/');
      // Drop the first " or '
      parts.shift();
      // Last one is either partial name or empty
      parts.pop();

      self.lastKnownRequests.push(self.apiHelper[fetchFunction]({
        pathParts: parts,
        successCallback: function (data) {
          if (!data.error) {
            var pathSuggestions = [];
            data.files.forEach(function (file) {
              if (file.name !== '..' && file.name !== '.') {
                pathSuggestions.push({
                  value: path === '' ? '/' + file.name : file.name,
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
      }));
    } else {
      pathsDeferred.reject();
    }
    return pathsDeferred;
  };

  AutocompleteResults.prototype.tableIdentifierChainsToPaths = function (tables) {
    var self = this;
    var paths = [];
    tables.forEach(function (table) {
      // Could be subquery
      var isTable = table.identifierChain.every(function (identifier) { return typeof identifier.name !== 'undefined' });
      if (isTable) {
        var path = $.map(table.identifierChain, function (identifier) {
          return identifier.name;
        });
        if (path.length === 1) {
          path.unshift(self.activeDatabase);
        }
        paths.push(path);
      }
    });
    return paths;
  };

  AutocompleteResults.prototype.handleJoins = function () {
    var self = this;
    var joinsDeferred = $.Deferred();
    var suggestJoins = self.parseResult.suggestJoins;
    if (HAS_OPTIMIZER && suggestJoins) {
      initLoading(self.loadingJoins, joinsDeferred);
      joinsDeferred.done(self.appendEntries);

      var paths = self.tableIdentifierChainsToPaths(suggestJoins.tables);
      if (paths.length) {
        DataCatalog.getMultiTableEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), paths: paths }).done(function (multiTableEntry) {
        self.cancellablePromises.push(multiTableEntry.getTopJoins({ silenceErrors: true, cancellable: true  }).done(function (topJoins) {
          var joinSuggestions = [];
          var totalCount = 0;
          if (topJoins.values) {
            topJoins.values.forEach(function (value) {

              var joinType = value.joinType || 'join';
              joinType += ' ';
              var suggestionString = suggestJoins.prependJoin ? (self.parseResult.lowerCase ? joinType.toLowerCase() : joinType.toUpperCase()) : '';
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
                  suggestionString += self.convertNavOptQualifiedIdentifier(joinColPair.columns[0], suggestJoins.tables, self.snippet.type()) + ' = ' + self.convertNavOptQualifiedIdentifier(joinColPair.columns[1], suggestJoins.tables, self.snippet.type());
                  first = false;
                });
                totalCount += value.totalQueryCount;
                joinSuggestions.push({
                  value: suggestionString,
                  meta: HUE_I18n.autocomplete.meta.join,
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
          }
          joinsDeferred.resolve(joinSuggestions);
        }).fail(joinsDeferred.reject));
      }).fail(joinsDeferred.reject);
      } else {
        joinsDeferred.reject();
      }
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

      var paths = self.tableIdentifierChainsToPaths(suggestJoinConditions.tables);
      if (paths.length) {
        DataCatalog.getMultiTableEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), paths: paths }).done(function (multiTableEntry) {
          self.cancellablePromises.push(multiTableEntry.getTopJoins({ silenceErrors: true, cancellable: true }).done(function (topJoins) {
          var joinConditionSuggestions = [];
          var totalCount = 0;
          if (topJoins.values) {
            topJoins.values.forEach(function (value) {
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
                  meta: HUE_I18n.autocomplete.meta.joinCondition,
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
          }

          joinConditionsDeferred.resolve(joinConditionSuggestions);
        }).fail(joinConditionsDeferred.reject));
        }).fail(joinConditionsDeferred.reject);
      } else {
        joinConditionsDeferred.reject();
      }
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

      var paths = self.tableIdentifierChainsToPaths(suggestAggregateFunctions.tables);
      if (paths.length) {
        DataCatalog.getMultiTableEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), paths: paths }).done(function (multiTableEntry) {
          self.cancellablePromises.push(multiTableEntry.getTopAggs({ silenceErrors: true, cancellable: true }).done(function (topAggs) {
            var aggregateFunctionsSuggestions = [];
            if (topAggs.values && topAggs.values.length > 0) {

              // Expand all column names to the fully qualified name including db and table.
              topAggs.values.forEach(function (value) {
                value.aggregateInfo.forEach(function (info) {
                  value.aggregateClause = value.aggregateClause.replace(new RegExp('([^.])' + info.columnName, 'gi'), '$1' + info.databaseName + '.' + info.tableName + '.' + info.columnName);
                });
              });

              // Substitute qualified table identifiers with either alias or table when multiple tables are present or just empty string
              var substitutions = [];
              suggestAggregateFunctions.tables.forEach(function (table) {
                var replaceWith = table.alias ? table.alias + '.' : (suggestAggregateFunctions.tables.length > 1 ? table.identifierChain[table.identifierChain.length - 1].name + '.' : '');
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
              topAggs.values.forEach(function (value) {
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
          }).fail(aggregateFunctionsDeferred.reject));
        }).fail(aggregateFunctionsDeferred.reject);
      } else {
        aggregateFunctionsDeferred.reject();
      }
    } else {
      aggregateFunctionsDeferred.reject();
    }
    return aggregateFunctionsDeferred;
  };

  /**
   * Merges popular group by and order by columns with the column suggestions
   *
   * @param sourceDeferred
   * @param columnsDeferred
   * @param suggestions
   */
  var mergeWithColumns = function (sourceDeferred, columnsDeferred, suggestions) {
    columnsDeferred.done(function (columns) {
      var suggestionIndex = {};
      suggestions.forEach(function (suggestion) {
        suggestionIndex[suggestion.value] = suggestion;
      });
      columns.forEach(function (col) {
        if (suggestionIndex[col.details.name]) {
          col.category = suggestionIndex[col.details.name].category
        }
      });
      sourceDeferred.resolve([]);
    })
  };

  AutocompleteResults.prototype.handlePopularGroupByOrOrderBy = function (navOptAttribute, suggestSpec, deferred, columnsDeferred) {
    var self = this;
    var paths = [];
    suggestSpec.tables.forEach(function (table) {
      if (table.identifierChain) {
        if (table.identifierChain.length === 1 && table.identifierChain[0].name) {
          paths.push([self.activeDatabase, table.identifierChain[0].name])
        } else if (table.identifierChain.length === 2 && table.identifierChain[0].name && table.identifierChain[1].name) {
          paths.push([table.identifierChain[0].name, table.identifierChain[1].name]);
        }
      }
    });

    self.cancellablePromises.push(DataCatalog.getCatalog(self.snippet.type())
      .loadNavOptPopularityForTables({ namespace: self.snippet.namespace(), compute: self.snippet.compute(), paths: paths, silenceErrors: true, cancellable: true }).done(function (entries) {
        var totalColumnCount = 0;
        var matchedEntries = [];
        var prefix = suggestSpec.prefix ? (self.parseResult.lowerCase ? suggestSpec.prefix.toLowerCase() : suggestSpec.prefix) + ' ' : '';

        entries.forEach(function (entry) {
          if (entry.navOptPopularity[navOptAttribute]) {
            totalColumnCount += entry.navOptPopularity[navOptAttribute].columnCount;
            matchedEntries.push(entry);
          }
        });
        if (totalColumnCount > 0) {
          var suggestions = [];
          matchedEntries.forEach(function (entry) {
            var filterValue = self.createNavOptIdentifierForColumn(entry.navOptPopularity[navOptAttribute], suggestSpec.tables);
            suggestions.push({
              value: prefix + filterValue,
              filterValue: filterValue,
              meta: navOptAttribute === 'groupByColumn' ? HUE_I18n.autocomplete.meta.groupBy : HUE_I18n.autocomplete.meta.orderBy,
              category: navOptAttribute === 'groupByColumn' ? CATEGORIES.POPULAR_GROUP_BY : CATEGORIES.POPULAR_ORDER_BY,
              weightAdjust:  Math.round(100 * entry.navOptPopularity[navOptAttribute].columnCount / totalColumnCount),
              popular: ko.observable(true),
              hasCatalogEntry: true,
              details: entry
            });
          });
          if (prefix === '' && suggestions.length) {
            mergeWithColumns(deferred, columnsDeferred, suggestions);
          } else {
            deferred.resolve(suggestions);
          }
        } else {
          deferred.reject();
        }
      }).fail(deferred.reject));
  };

  AutocompleteResults.prototype.handleGroupBys = function (columnsDeferred) {
    var self = this;
    var groupBysDeferred = $.Deferred();
    var suggestGroupBys = self.parseResult.suggestGroupBys;
    if (HAS_OPTIMIZER && suggestGroupBys) {
      initLoading(self.loadingGroupBys, groupBysDeferred);
      groupBysDeferred.done(self.appendEntries);
      self.handlePopularGroupByOrOrderBy('groupByColumn', suggestGroupBys, groupBysDeferred, columnsDeferred);
    } else {
      groupBysDeferred.reject();
    }

    return groupBysDeferred;
  };

  AutocompleteResults.prototype.handleOrderBys = function (columnsDeferred) {
    var self = this;
    var orderBysDeferred = $.Deferred();
    var suggestOrderBys = self.parseResult.suggestOrderBys;
    if (HAS_OPTIMIZER && suggestOrderBys) {
      initLoading(self.loadingOrderBys, orderBysDeferred);
      orderBysDeferred.done(self.appendEntries);
      self.handlePopularGroupByOrOrderBy('orderByColumn', suggestOrderBys, orderBysDeferred, columnsDeferred);
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

      var paths = self.tableIdentifierChainsToPaths(suggestFilters.tables);
      if (paths.length) {
        DataCatalog.getMultiTableEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), paths: paths }).done(function (multiTableEntry) {
          self.cancellablePromises.push(multiTableEntry.getTopFilters({ silenceErrors: true, cancellable: true }).done(function (topFilters) {
            var filterSuggestions = [];
            var totalCount = 0;
            if (topFilters.values) {
              topFilters.values.forEach(function (value) {
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
                          meta: HUE_I18n.autocomplete.meta.filter,
                          category: CATEGORIES.POPULAR_FILTER,
                          popular: ko.observable(true),
                          details: popularValue
                        });
                      });
                    }
                  });
                }
              });
            }
            filterSuggestions.forEach(function (suggestion) {
              suggestion.details.relativePopularity = totalCount === 0 ? suggestion.details.count : Math.round(100 * suggestion.details.count / totalCount);
              suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
            });

            filtersDeferred.resolve(filterSuggestions);
          }).fail(filtersDeferred.reject));
        }).fail(filtersDeferred.reject);
      } else {
        filtersDeferred.reject();
      }
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

      var db = self.parseResult.suggestTables.identifierChain
        && self.parseResult.suggestTables.identifierChain.length === 1
        && self.parseResult.suggestTables.identifierChain[0].name ? self.parseResult.suggestTables.identifierChain[0].name : self.activeDatabase;

      DataCatalog.getEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), path: [ db ]}).done(function (entry) {
        self.cancellablePromises.push(entry.loadNavOptPopularityForChildren({ silenceErrors: true, cancellable: true }).done(function (childEntries) {
          var totalPopularity = 0;
          var popularityIndex = {};
          childEntries.forEach(function (childEntry) {
            if (childEntry.navOptPopularity && childEntry.navOptPopularity.popularity) {
              popularityIndex[childEntry.name] = true;
              totalPopularity += childEntry.navOptPopularity.popularity;
            }
          });
          if (totalPopularity > 0 && Object.keys(popularityIndex).length) {
            tablesDeferred.done(function (tableSuggestions) {
              tableSuggestions.forEach(function (suggestion) {
                if (popularityIndex[suggestion.details.name]) {
                  suggestion.relativePopularity = Math.round(100 * suggestion.details.navOptPopularity.popularity / totalPopularity);
                  if (suggestion.relativePopularity >= 5) {
                    suggestion.popular(true);
                  }
                  suggestion.weightAdjust = suggestion.relativePopularity;
                }
              });
              popularTablesDeferred.resolve();
            }).fail(popularTablesDeferred.reject);
          } else {
            popularTablesDeferred.resolve();
          }
        }).fail(popularTablesDeferred.reject));
      }).fail(popularTablesDeferred.reject);
    } else {
      popularTablesDeferred.reject();
    }
    return popularTablesDeferred
  };

  AutocompleteResults.prototype.handlePopularColumns = function (columnsDeferred) {
    var self = this;
    var popularColumnsDeferred = $.Deferred();
    var suggestColumns = self.parseResult.suggestColumns;

    // The columnsDeferred gets resolved synchronously when the data is cached, if not, assume there are some suggestions.
    var hasColumnSuggestions = true;
    columnsDeferred.done(function (columns) {
      hasColumnSuggestions = columns.length > 0;
    });

    if (hasColumnSuggestions && HAS_OPTIMIZER && suggestColumns && suggestColumns.source !== 'undefined') {
      initLoading(self.loadingPopularColumns, popularColumnsDeferred);

      var paths = [];
      suggestColumns.tables.forEach(function (table) {
        if (table.identifierChain && table.identifierChain.length > 0) {
          if (table.identifierChain.length === 1 && table.identifierChain[0].name) {
            paths.push([self.activeDatabase, table.identifierChain[0].name])
          } else if (table.identifierChain.length === 2 && table.identifierChain[0].name && table.identifierChain[1].name) {
            paths.push([table.identifierChain[0].name, table.identifierChain[1].name]);
          }
        }
      });

      self.cancellablePromises.push(DataCatalog.getCatalog(self.snippet.type()).loadNavOptPopularityForTables({
        namespace: self.snippet.namespace(),
        compute: self.snippet.compute(),
        paths: paths,
        silenceErrors: true,
        cancellable: true
      }).done(function (popularEntries) {
        var valueAttribute = '';
        switch (suggestColumns.source) {
          case 'select':
            valueAttribute = 'selectColumn';
            break;
          case 'group by':
            valueAttribute = 'groupByColumn';
            break;
          case 'order by':
            valueAttribute = 'orderByColumn';
        }

        var popularityIndex = {};

        popularEntries.forEach(function (popularEntry) {
          if (popularEntry.navOptPopularity && popularEntry.navOptPopularity[valueAttribute]) {
            popularityIndex[popularEntry.getQualifiedPath()] = true;
          }
        });

        if (!valueAttribute || Object.keys(popularityIndex).length === 0) {
          popularColumnsDeferred.reject();
          return;
        }

        columnsDeferred.done(function (columns) {
          var totalColumnCount = 0;
          var matchedSuggestions = [];
          columns.forEach(function (suggestion) {
            if (suggestion.hasCatalogEntry && popularityIndex[suggestion.details.getQualifiedPath()]) {
              matchedSuggestions.push(suggestion);
              totalColumnCount += suggestion.details.navOptPopularity[valueAttribute].columnCount;
            }
          });
          if (totalColumnCount > 0) {
            matchedSuggestions.forEach(function (matchedSuggestion) {
              matchedSuggestion.relativePopularity = Math.round(100 * matchedSuggestion.details.navOptPopularity[valueAttribute].columnCount / totalColumnCount);
              if (matchedSuggestion.relativePopularity  >= 5) {
                matchedSuggestion.popular(true);
              }
              matchedSuggestion.weightAdjust = matchedSuggestion.relativePopularity ;
            });
          }
          popularColumnsDeferred.resolve();
        }).fail(popularColumnsDeferred.reject);
      }));
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
        } else if (tables.length > 0) {
          path = tables[i].identifierChain[tables[i].identifierChain.length - 1].name + '.' + path;
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
      if (navOptColumn.tableName && hueUtils.equalIgnoreCase(navOptColumn.tableName, tables[i].identifierChain[tables[i].identifierChain.length - 1].name) && tables[i].alias) {
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

  AutocompleteResults.prototype.convertNavOptQualifiedIdentifier = function (qualifiedIdentifier, tables, type) {
    var self = this;
    var aliases = [];
    var tablesHasDefaultDatabase = false;
    tables.forEach(function (table) {
      tablesHasDefaultDatabase = tablesHasDefaultDatabase || hueUtils.equalIgnoreCase(table.identifierChain[0].name.toLowerCase(), self.activeDatabase.toLowerCase());
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

    if (qualifiedIdentifier.toLowerCase().indexOf(self.activeDatabase.toLowerCase()) === 0 && !tablesHasDefaultDatabase) {
      return qualifiedIdentifier.substring(self.activeDatabase.length + 1);
    }
    if (type === 'hive') {
      // Remove DB reference if given for Hive
      var parts = qualifiedIdentifier.split('.');
      if (parts.length > 2) {
        return parts.slice(1).join('.')
      }
    }
    return qualifiedIdentifier;
  };

  /**
   * Helper function to fetch columns/fields given an identifierChain, this also takes care of expanding arrays
   * and maps to match the required format for the API.
   *
   * @param originalIdentifierChain
   */
  AutocompleteResults.prototype.fetchFieldsForIdentifiers = function (originalIdentifierChain) {
    var self = this;
    var deferred = $.Deferred();
    var path = [];
    for (var i = 0; i < originalIdentifierChain.length; i++) {
      if (originalIdentifierChain[i].name && !originalIdentifierChain[i].subQuery) {
        path.push(originalIdentifierChain[i].name)
      } else {
        return deferred.reject().promise();
      }
    }

    var fetchFieldsInternal =  function (remainingPath, fetchedPath) {
      if (!fetchedPath) {
        fetchedPath = [];
      }
      if (remainingPath.length > 0) {
        fetchedPath.push(remainingPath.shift());
        // Parser sometimes knows if it's a map or array.
        if (remainingPath.length > 0 && (remainingPath[0] === 'item' || remainingPath[0].name === 'value')) {
          fetchedPath.push(remainingPath.shift());
        }
      }

      DataCatalog.getEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), path: fetchedPath }).done(function (catalogEntry) {
        self.cancellablePromises.push(catalogEntry.getSourceMeta({ silenceErrors: true, cancellable: true }).done(function (sourceMeta) {
          if (self.snippet.type() === 'hive'
              && typeof sourceMeta.extended_columns !== 'undefined'
              && sourceMeta.extended_columns.length === 1
              && /^(?:map|array|struct)/i.test(sourceMeta.extended_columns[0].type)) {
            remainingPath.unshift(data.extended_columns[0].name)
          }
          if (remainingPath.length) {
            if (/value|item|key/i.test(remainingPath[0])) {
              fetchedPath.push(remainingPath.shift());
            } else if (sourceMeta.type === 'array') {
              fetchedPath.push('item');
            } else if (sourceMeta.type === 'map') {
              fetchedPath.push('value');
            }
            fetchFieldsInternal(remainingPath, fetchedPath)
          } else {
            deferred.resolve(catalogEntry);
          }
        }).fail(deferred.reject));
      }).fail(deferred.reject);
    };

    // For Impala the first parts of the identifier chain could be either database or table, either:
    // SELECT | FROM database.table -or- SELECT | FROM table.column

    // For Hive it could be either:
    // SELECT col.struct FROM db.tbl -or- SELECT col.struct FROM tbl
    if (path.length > 1 && (self.snippet.type() === 'impala' || self.snippet.type() === 'hive')) {
      DataCatalog.getEntry({ sourceType: self.snippet.type(), namespace: self.snippet.namespace(), compute: self.snippet.compute(), path: [] }).done(function (catalogEntry) {
        self.cancellablePromises.push(catalogEntry.getChildren({ silenceErrors: true, cancellable: true }).done(function (databaseEntries) {
          var firstIsDb = databaseEntries.some(function (dbEntry) {
            return hueUtils.equalIgnoreCase(dbEntry.name, path[0]);
          });
          if (!firstIsDb) {
            path.unshift(self.activeDatabase);
          }
          fetchFieldsInternal(path);
        }).fail(deferred.reject));
      }).fail(deferred.reject);
    } else if (path.length > 1) {
      fetchFieldsInternal(path);
    } else {
      path.unshift(self.activeDatabase);
      fetchFieldsInternal(path);
    }

    return deferred.promise();
  };

  return AutocompleteResults;
})();

var SqlAutocompleter3 = (function () {
  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {string) [options.fixedPrefix] - Optional prefix to always use on parse
   * @param {string) [options.fixedPostfix] - Optional postfix to always use on parse
   * @constructor
   */
  function SqlAutocompleter3(options) {
    var self = this;
    self.snippet = options.snippet;
    self.editor = options.editor;
    self.fixedPrefix = options.fixedPrefix || function () { return '' };
    self.fixedPostfix = options.fixedPostfix || function () { return '' };
    self.suggestions = new AutocompleteResults(options);
  }

  SqlAutocompleter3.prototype.parseActiveStatement = function () {
    var self = this;
    if (self.snippet.positionStatement() && self.snippet.positionStatement().location) {
      var activeStatementLocation = self.snippet.positionStatement().location;
      var cursorPosition = self.editor().getCursorPosition();

      if ((activeStatementLocation.first_line - 1 < cursorPosition.row || (activeStatementLocation.first_line - 1 === cursorPosition.row && activeStatementLocation.first_column <= cursorPosition.column)) &&
        (activeStatementLocation.last_line - 1 > cursorPosition.row || (activeStatementLocation.last_line - 1 === cursorPosition.row && activeStatementLocation.last_column >= cursorPosition.column))) {
        var beforeCursor = self.fixedPrefix() + self.editor().session.getTextRange({
          start: {
            row: activeStatementLocation.first_line - 1,
            column: activeStatementLocation.first_column
          },
          end: cursorPosition
        });
        var afterCursor = self.editor().session.getTextRange({
          start: cursorPosition,
          end: {
            row: activeStatementLocation.last_line - 1,
            column: activeStatementLocation.last_column
          }
        }) + self.fixedPostfix();
        return sqlAutocompleteParser.parseSql(beforeCursor, afterCursor, self.snippet.type(), false);
      }
    }
  };

  /**
   * Waits for the snippet to have a compute and namespace set, this prevents js exceptions and garbled editor
   * output when autocomplete is triggered while loading the context.
   *
   * @return {Promise}
   */
  SqlAutocompleter3.prototype.whenContextSet = function () {
    var self = this;

    // Fail any queued requests, only the last update should succeed
    if (self.computeDeferred) {
      self.computeDeferred.reject();
    }
    if (self.namespaceDeferred) {
      self.namespaceDeferred.reject();
    }
    if (self.waitForNamespaceSub) {
      self.waitForNamespaceSub.dispose();
    }
    if (self.waitForComputeSub) {
      self.waitForComputeSub.dispose();
    }

    self.computeDeferred = $.Deferred();
    if (self.snippet.compute()) {
      self.computeDeferred.resolve();
    } else {
      self.waitForComputeSub = self.snippet.compute.subscribe(function (newVal) {
        if (newVal) {
          self.computeDeferred.resolve();
          self.waitForComputeSub.dispose();
        }
      })
    }

    self.namespaceDeferred = $.Deferred();
    if (self.snippet.namespace()) {
      self.namespaceDeferred.resolve();
    } else {
      self.waitForNamespaceSub = self.snippet.namespace.subscribe(function (newVal) {
        if (newVal) {
          self.namespaceDeferred.resolve();
          self.waitForNamespaceSub.dispose();
        }
      })
    }
    return $.when(self.computeDeferred, self.namespaceDeferred);
  };

  SqlAutocompleter3.prototype.autocomplete = function () {
    var self = this;
    var parseResult;
    try {
      huePubSub.publish('get.active.editor.locations', function (locations) {
        // This could happen in case the user is editing at the borders of the statement and the locations haven't
        // been updated yet, in that case we have to force a location update before parsing
        if (self.snippet.ace && self.snippet.ace() && locations && self.snippet.ace().lastChangeTime !== locations.editorChangeTime) {
          huePubSub.publish('editor.refresh.statement.locations', self.snippet);
        }
      }, self.snippet);

      parseResult = self.parseActiveStatement();

      if (typeof hueDebug !== 'undefined' && hueDebug.showParseResult) {
        console.log(parseResult);
      }
    } catch (e) {
      if (typeof console.warn !== 'undefined') {
        console.warn(e);
      }
    }

    // In the unlikely case the statement parser fails we fall back to parsing all of it
    if (!parseResult) {
      try {
        parseResult = sqlAutocompleteParser.parseSql(self.editor().getTextBeforeCursor(), self.editor().getTextAfterCursor(), self.snippet.type(), false);
      } catch (e) {
        if (typeof console.warn !== 'undefined') {
          console.warn(e);
        }
      }
    }

    if (!parseResult) {
      // This prevents Ace from inserting garbled text in case of exception
      huePubSub.publish('hue.ace.autocompleter.done');
    } else {
      try {
        self.whenContextSet().done(function () {
          self.suggestions.update(parseResult);
        }).fail(function () {
          huePubSub.publish('hue.ace.autocompleter.done');
        });
      } catch (e) {
        if (typeof console.warn !== 'undefined') {
          console.warn(e);
        }
        huePubSub.publish('hue.ace.autocompleter.done');
      }
    }
  };

  return SqlAutocompleter3;
})();
