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

import $ from 'jquery';
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import dataCatalog from 'catalog/dataCatalog';
import HueColors from 'utils/hueColors';
import hueUtils from 'utils/hueUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import sqlUtils from 'sql/sqlUtils';
import { SqlSetOptions, SqlFunctions } from 'sql/sqlFunctions';

const normalizedColors = HueColors.getNormalizedColors();

const COLORS = {
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

const META_I18n = {
  aggregateFunction: I18n('aggregate'),
  alias: I18n('alias'),
  commonTableExpression: I18n('cte'),
  database: I18n('database'),
  dir: I18n('dir'),
  filter: I18n('filter'),
  groupBy: I18n('group by'),
  join: I18n('join'),
  joinCondition: I18n('condition'),
  keyword: I18n('keyword'),
  orderBy: I18n('order by'),
  sample: I18n('sample'),
  table: I18n('table'),
  variable: I18n('variable'),
  view: I18n('view'),
  virtual: I18n('virtual')
};

const CATEGORIES = {
  ALL: {
    id: 'all',
    color: HueColors.BLUE,
    label: I18n('All')
  },
  POPULAR: {
    id: 'popular',
    color: COLORS.POPULAR,
    label: I18n('Popular')
  },
  POPULAR_AGGREGATE: {
    id: 'popularAggregate',
    weight: 1500,
    color: COLORS.POPULAR,
    label: I18n('Popular'),
    detailsTemplate: 'agg-udf'
  },
  POPULAR_GROUP_BY: {
    id: 'popularGroupBy',
    weight: 1300,
    color: COLORS.POPULAR,
    label: I18n('Popular'),
    detailsTemplate: 'group-by'
  },
  POPULAR_ORDER_BY: {
    id: 'popularOrderBy',
    weight: 1200,
    color: COLORS.POPULAR,
    label: I18n('Popular'),
    detailsTemplate: 'order-by'
  },
  POPULAR_FILTER: {
    id: 'popularFilter',
    weight: 1400,
    color: COLORS.POPULAR,
    label: I18n('Popular'),
    detailsTemplate: 'filter'
  },
  POPULAR_ACTIVE_JOIN: {
    id: 'popularActiveJoin',
    weight: 1500,
    color: COLORS.POPULAR,
    label: I18n('Popular'),
    detailsTemplate: 'join'
  },
  POPULAR_JOIN_CONDITION: {
    id: 'popularJoinCondition',
    weight: 1500,
    color: COLORS.POPULAR,
    label: I18n('Popular'),
    detailsTemplate: 'join-condition'
  },
  COLUMN: {
    id: 'column',
    weight: 1000,
    color: COLORS.COLUMN,
    label: I18n('Columns'),
    detailsTemplate: 'column'
  },
  SAMPLE: {
    id: 'sample',
    weight: 900,
    color: COLORS.SAMPLE,
    label: I18n('Samples'),
    detailsTemplate: 'value'
  },
  IDENTIFIER: {
    id: 'identifier',
    weight: 800,
    color: COLORS.IDENT_CTE_VAR,
    label: I18n('Identifiers'),
    detailsTemplate: 'identifier'
  },
  CTE: {
    id: 'cte',
    weight: 700,
    color: COLORS.IDENT_CTE_VAR,
    label: I18n('CTEs'),
    detailsTemplate: 'cte'
  },
  TABLE: {
    id: 'table',
    weight: 600,
    color: COLORS.TABLE,
    label: I18n('Tables'),
    detailsTemplate: 'table'
  },
  DATABASE: {
    id: 'database',
    weight: 500,
    color: COLORS.DATABASE,
    label: I18n('Databases'),
    detailsTemplate: 'database'
  },
  UDF: {
    id: 'udf',
    weight: 400,
    color: COLORS.UDF,
    label: I18n('UDFs'),
    detailsTemplate: 'udf'
  },
  OPTION: {
    id: 'option',
    weight: 400,
    color: COLORS.UDF,
    label: I18n('Options'),
    detailsTemplate: 'option'
  },
  HDFS: {
    id: 'hdfs',
    weight: 300,
    color: COLORS.HDFS,
    label: I18n('Files'),
    detailsTemplate: 'hdfs'
  },
  VIRTUAL_COLUMN: {
    id: 'virtualColumn',
    weight: 200,
    color: COLORS.COLUMN,
    label: I18n('Columns'),
    detailsTemplate: 'column'
  },
  COLREF_KEYWORD: {
    id: 'colrefKeyword',
    weight: 100,
    color: COLORS.KEYWORD,
    label: I18n('Keywords'),
    detailsTemplate: 'keyword'
  },
  VARIABLE: {
    id: 'variable',
    weight: 50,
    color: COLORS.IDENT_CTE_VAR,
    label: I18n('Variables'),
    detailsTemplate: 'variable'
  },
  KEYWORD: {
    id: 'keyword',
    weight: 0,
    color: COLORS.KEYWORD,
    label: I18n('Keywords'),
    detailsTemplate: 'keyword'
  },
  POPULAR_JOIN: {
    id: 'popularJoin',
    weight: 1500,
    color: COLORS.POPULAR,
    label: I18n('Popular'),
    detailsTemplate: 'join'
  }
};

const POPULAR_CATEGORIES = [
  CATEGORIES.POPULAR_AGGREGATE,
  CATEGORIES.POPULAR_GROUP_BY,
  CATEGORIES.POPULAR_ORDER_BY,
  CATEGORIES.POPULAR_FILTER,
  CATEGORIES.POPULAR_ACTIVE_JOIN,
  CATEGORIES.POPULAR_JOIN_CONDITION,
  CATEGORIES.POPULAR_JOIN
];

const initLoading = function(loadingObservable, deferred) {
  loadingObservable(true);
  deferred.always(() => {
    loadingObservable(false);
  });
};

const locateSubQuery = function(subQueries, subQueryName) {
  if (typeof subQueries === 'undefined') {
    return null;
  }
  const foundSubQueries = subQueries.filter(knownSubQuery => {
    return hueUtils.equalIgnoreCase(knownSubQuery.alias, subQueryName);
  });
  if (foundSubQueries.length > 0) {
    return foundSubQueries[0];
  }
  return null;
};

/**
 * Merges popular group by and order by columns with the column suggestions
 *
 * @param sourceDeferred
 * @param columnsDeferred
 * @param suggestions
 */
const mergeWithColumns = function(sourceDeferred, columnsDeferred, suggestions) {
  columnsDeferred.done(columns => {
    const suggestionIndex = {};
    suggestions.forEach(suggestion => {
      suggestionIndex[suggestion.value] = suggestion;
    });
    columns.forEach(col => {
      if (suggestionIndex[col.details.name]) {
        col.category = suggestionIndex[col.details.name].category;
      }
    });
    sourceDeferred.resolve([]);
  });
};

class AutocompleteResults {
  /**
   *
   * @param options
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.snippet = options.snippet;
    self.editor = options.editor;
    self.temporaryOnly =
      options.snippet.autocompleteSettings && options.snippet.autocompleteSettings.temporaryOnly;

    self.sortOverride = null;

    huePubSub.subscribe('editor.autocomplete.temporary.sort.override', sortOverride => {
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

    self.appendEntries = function(entries) {
      self.entries(self.entries().concat(entries));
    };

    self.loading = ko
      .pureComputed(() => {
        return (
          self.loadingKeywords() ||
          self.loadingFunctions() ||
          self.loadingDatabases() ||
          self.loadingTables() ||
          self.loadingColumns() ||
          self.loadingValues() ||
          self.loadingPaths() ||
          self.loadingJoins() ||
          self.loadingJoinConditions() ||
          self.loadingAggregateFunctions() ||
          self.loadingGroupBys() ||
          self.loadingOrderBys() ||
          self.loadingFilters() ||
          self.loadingPopularTables() ||
          self.loadingPopularColumns()
        );
      })
      .extend({ rateLimit: 200 });

    self.filter = ko.observable();

    self.availableCategories = ko.observableArray([CATEGORIES.ALL]);

    self.availableCategories.subscribe(newCategories => {
      if (newCategories.indexOf(self.activeCategory()) === -1) {
        self.activeCategory(CATEGORIES.ALL);
      }
    });

    self.activeCategory = ko.observable(CATEGORIES.ALL);

    const updateCategories = function(suggestions) {
      const newCategories = {};
      suggestions.forEach(suggestion => {
        if (suggestion.popular() && !newCategories[CATEGORIES.POPULAR.label]) {
          newCategories[CATEGORIES.POPULAR.label] = CATEGORIES.POPULAR;
        } else if (
          suggestion.category === CATEGORIES.TABLE ||
          suggestion.category === CATEGORIES.COLUMN ||
          suggestion.category === CATEGORIES.UDF
        ) {
          if (!newCategories[suggestion.category.label]) {
            newCategories[suggestion.category.label] = suggestion.category;
          }
        }
      });
      const result = [];
      Object.keys(newCategories).forEach(key => {
        result.push(newCategories[key]);
      });
      result.sort((a, b) => {
        return a.label.localeCompare(b.label);
      });
      result.unshift(CATEGORIES.ALL);
      self.availableCategories(result);
    };

    self.filtered = ko
      .pureComputed(() => {
        let result = self.entries();

        if (self.filter()) {
          result = sqlUtils.autocompleteFilter(self.filter(), result);
          huePubSub.publish('hue.ace.autocompleter.match.updated');
        }

        updateCategories(result);

        const activeCategory = self.activeCategory();

        const categoriesCount = {};

        result = result.filter(suggestion => {
          if (typeof categoriesCount[suggestion.category.id] === 'undefined') {
            categoriesCount[suggestion.category.id] = 0;
          } else {
            categoriesCount[suggestion.category.id]++;
          }
          if (
            activeCategory !== CATEGORIES.POPULAR &&
            categoriesCount[suggestion.category.id] >= 10 &&
            POPULAR_CATEGORIES.indexOf(suggestion.category) !== -1
          ) {
            return false;
          }
          return (
            activeCategory === CATEGORIES.ALL ||
            activeCategory === suggestion.category ||
            (activeCategory === CATEGORIES.POPULAR && suggestion.popular())
          );
        });

        sqlUtils.sortSuggestions(result, self.filter(), self.sortOverride);
        self.sortOverride = null;
        return result;
      })
      .extend({ rateLimit: 200 });
  }

  cancelRequests() {
    const self = this;

    while (self.lastKnownRequests.length) {
      apiHelper.cancelActiveRequest(self.lastKnownRequests.pop());
    }

    while (self.cancellablePromises.length) {
      const promise = self.cancellablePromises.pop();
      if (promise.cancel) {
        promise.cancel();
      }
    }
  }

  update(parseResult) {
    const self = this;

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

    const colRefDeferred = self.handleColumnReference();
    self.activeDeferrals.push(colRefDeferred);
    const databasesDeferred = self.loadDatabases();
    self.activeDeferrals.push(databasesDeferred);

    self.handleKeywords(colRefDeferred);
    self.handleIdentifiers();
    self.handleColumnAliases();
    self.handleCommonTableExpressions();
    self.handleOptions();
    self.handleFunctions(colRefDeferred);
    self.handleDatabases(databasesDeferred);
    const tablesDeferred = self.handleTables(databasesDeferred);
    self.activeDeferrals.push(tablesDeferred);
    const columnsDeferred = self.handleColumns(colRefDeferred, tablesDeferred);
    self.activeDeferrals.push(columnsDeferred);
    self.handleValues(colRefDeferred);
    self.activeDeferrals.push(self.handlePaths());

    if (!self.temporaryOnly) {
      self.activeDeferrals.push(self.handleJoins());
      self.activeDeferrals.push(self.handleJoinConditions());
      self.activeDeferrals.push(self.handleAggregateFunctions());
      self.activeDeferrals.push(self.handleGroupBys(columnsDeferred));
      self.activeDeferrals.push(self.handleOrderBys(columnsDeferred));
      self.activeDeferrals.push(self.handleFilters());
      self.activeDeferrals.push(self.handlePopularTables(tablesDeferred));
      self.activeDeferrals.push(self.handlePopularColumns(columnsDeferred));
    }

    $.when.apply($, self.activeDeferrals).always(() => {
      huePubSub.publish('hue.ace.autocompleter.done');
    });
  }

  /**
   * For some suggestions the column type is needed, for instance with functions we should only suggest
   * columns that matches the argument type, cos(|) etc.
   *
   * The deferred will always resolve, and the default values is { type: 'T' }
   *
   * @returns {object} - jQuery Deferred
   */
  handleColumnReference() {
    const self = this;
    const colRefDeferred = $.Deferred();
    if (self.parseResult.colRef) {
      const colRefCallback = function(catalogEntry) {
        self.cancellablePromises.push(
          catalogEntry
            .getSourceMeta({ silenceErrors: true, cancellable: true })
            .done(sourceMeta => {
              if (typeof sourceMeta.type !== 'undefined') {
                colRefDeferred.resolve(sourceMeta);
              } else {
                colRefDeferred.resolve({ type: 'T' });
              }
            })
            .fail(() => {
              colRefDeferred.resolve({ type: 'T' });
            })
        );
      };

      const foundVarRef = self.parseResult.colRef.identifierChain.some(identifier => {
        return typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0;
      });

      if (foundVarRef) {
        colRefDeferred.resolve({ type: 'T' });
      } else {
        self
          .fetchFieldsForIdentifiers(self.parseResult.colRef.identifierChain)
          .done(colRefCallback)
          .fail(() => {
            colRefDeferred.resolve({ type: 'T' });
          });
      }
    } else {
      colRefDeferred.resolve({ type: 'T' });
    }
    return colRefDeferred;
  }

  loadDatabases() {
    const self = this;
    const databasesDeferred = $.Deferred();
    dataCatalog
      .getEntry({
        sourceType: self.snippet.type(),
        namespace: self.snippet.namespace(),
        compute: self.snippet.compute(),
        path: [],
        temporaryOnly: self.temporaryOnly
      })
      .done(entry => {
        self.cancellablePromises.push(
          entry
            .getChildren({ silenceErrors: true, cancellable: true })
            .done(databases => {
              databasesDeferred.resolve(databases);
            })
            .fail(databasesDeferred.reject)
        );
      })
      .fail(databasesDeferred.reject);
    return databasesDeferred;
  }

  handleKeywords(colRefDeferred) {
    const self = this;
    if (self.parseResult.suggestKeywords) {
      const keywordSuggestions = $.map(self.parseResult.suggestKeywords, keyword => {
        return {
          value: self.parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value,
          meta: META_I18n.keyword,
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
      colRefDeferred.done(colRef => {
        const colRefKeywordSuggestions = [];
        Object.keys(self.parseResult.suggestColRefKeywords).forEach(typeForKeywords => {
          if (
            SqlFunctions.matchesType(
              self.snippet.type(),
              [typeForKeywords],
              [colRef.type.toUpperCase()]
            )
          ) {
            self.parseResult.suggestColRefKeywords[typeForKeywords].forEach(keyword => {
              colRefKeywordSuggestions.push({
                value: self.parseResult.lowerCase ? keyword.toLowerCase() : keyword,
                meta: META_I18n.keyword,
                category: CATEGORIES.COLREF_KEYWORD,
                popular: ko.observable(false),
                details: {
                  type: colRef.type
                }
              });
            });
          }
        });
        self.appendEntries(colRefKeywordSuggestions);
      });
    }
  }

  handleIdentifiers() {
    const self = this;
    if (self.parseResult.suggestIdentifiers) {
      const identifierSuggestions = [];
      self.parseResult.suggestIdentifiers.forEach(identifier => {
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
  }

  handleColumnAliases() {
    const self = this;
    if (self.parseResult.suggestColumnAliases) {
      const columnAliasSuggestions = [];
      self.parseResult.suggestColumnAliases.forEach(columnAlias => {
        const type =
          columnAlias.types && columnAlias.types.length === 1 ? columnAlias.types[0] : 'T';
        if (type === 'COLREF') {
          columnAliasSuggestions.push({
            value: columnAlias.name,
            meta: META_I18n.alias,
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
  }

  handleCommonTableExpressions() {
    const self = this;
    if (self.parseResult.suggestCommonTableExpressions) {
      const commonTableExpressionSuggestions = [];
      self.parseResult.suggestCommonTableExpressions.forEach(expression => {
        let prefix = expression.prependQuestionMark ? '? ' : '';
        if (expression.prependFrom) {
          prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
        }
        commonTableExpressionSuggestions.push({
          value: prefix + expression.name,
          filterValue: expression.name,
          meta: META_I18n.commonTableExpression,
          category: CATEGORIES.CTE,
          popular: ko.observable(false),
          details: null
        });
      });
      self.appendEntries(commonTableExpressionSuggestions);
    }
  }

  handleOptions() {
    const self = this;
    if (self.parseResult.suggestSetOptions) {
      const suggestions = [];
      SqlSetOptions.suggestOptions(self.snippet.type(), suggestions, CATEGORIES.OPTION);
      self.appendEntries(suggestions);
    }
  }

  handleFunctions(colRefDeferred) {
    const self = this;
    if (self.parseResult.suggestFunctions) {
      const functionSuggestions = [];
      if (
        self.parseResult.suggestFunctions.types &&
        self.parseResult.suggestFunctions.types[0] === 'COLREF'
      ) {
        initLoading(self.loadingFunctions, colRefDeferred);

        colRefDeferred.done(colRef => {
          const functionsToSuggest = SqlFunctions.getFunctionsWithReturnTypes(
            self.snippet.type(),
            [colRef.type.toUpperCase()],
            self.parseResult.suggestAggregateFunctions || false,
            self.parseResult.suggestAnalyticFunctions || false
          );

          Object.keys(functionsToSuggest).forEach(name => {
            functionSuggestions.push({
              category: CATEGORIES.UDF,
              value: name + '()',
              meta: functionsToSuggest[name].returnTypes.join('|'),
              weightAdjust:
                colRef.type.toUpperCase() !== 'T' &&
                functionsToSuggest[name].returnTypes.some(otherType => {
                  return otherType === colRef.type.toUpperCase();
                })
                  ? 1
                  : 0,
              popular: ko.observable(false),
              details: functionsToSuggest[name]
            });
          });

          self.appendEntries(functionSuggestions);
        });
      } else {
        const types = self.parseResult.suggestFunctions.types || ['T'];
        const functionsToSuggest = SqlFunctions.getFunctionsWithReturnTypes(
          self.snippet.type(),
          types,
          self.parseResult.suggestAggregateFunctions || false,
          self.parseResult.suggestAnalyticFunctions || false
        );

        Object.keys(functionsToSuggest).forEach(name => {
          functionSuggestions.push({
            category: CATEGORIES.UDF,
            value: name + '()',
            meta: functionsToSuggest[name].returnTypes.join('|'),
            weightAdjust:
              types[0].toUpperCase() !== 'T' &&
              functionsToSuggest[name].returnTypes.some(otherType => {
                return otherType === types[0].toUpperCase();
              })
                ? 1
                : 0,
            popular: ko.observable(false),
            details: functionsToSuggest[name]
          });
        });
        self.appendEntries(functionSuggestions);
      }
    }
  }

  handleDatabases(databasesDeferred) {
    const self = this;
    const suggestDatabases = self.parseResult.suggestDatabases;
    if (suggestDatabases) {
      initLoading(self.loadingDatabases, databasesDeferred);

      let prefix = suggestDatabases.prependQuestionMark ? '? ' : '';
      if (suggestDatabases.prependFrom) {
        prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
      }
      const databaseSuggestions = [];

      databasesDeferred.done(catalogEntries => {
        catalogEntries.forEach(dbEntry => {
          databaseSuggestions.push({
            value:
              prefix +
              sqlUtils.backTickIfNeeded(self.snippet.type(), dbEntry.name) +
              (suggestDatabases.appendDot ? '.' : ''),
            filterValue: dbEntry.name,
            meta: META_I18n.database,
            category: CATEGORIES.DATABASE,
            popular: ko.observable(false),
            hasCatalogEntry: true,
            details: dbEntry
          });
        });
        self.appendEntries(databaseSuggestions);
      });
    }
  }

  handleTables(databasesDeferred) {
    const self = this;
    const tablesDeferred = $.Deferred();

    if (self.parseResult.suggestTables) {
      const suggestTables = self.parseResult.suggestTables;
      const fetchTables = function() {
        initLoading(self.loadingTables, tablesDeferred);
        tablesDeferred.done(self.appendEntries);

        let prefix = suggestTables.prependQuestionMark ? '? ' : '';
        if (suggestTables.prependFrom) {
          prefix += self.parseResult.lowerCase ? 'from ' : 'FROM ';
        }

        const database =
          suggestTables.identifierChain && suggestTables.identifierChain.length === 1
            ? suggestTables.identifierChain[0].name
            : self.activeDatabase;

        dataCatalog
          .getEntry({
            sourceType: self.snippet.type(),
            namespace: self.snippet.namespace(),
            compute: self.snippet.compute(),
            path: [database],
            temporaryOnly: self.temporaryOnly
          })
          .done(dbEntry => {
            self.cancellablePromises.push(
              dbEntry
                .getChildren({ silenceErrors: true, cancellable: true })
                .done(tableEntries => {
                  const tableSuggestions = [];

                  tableEntries.forEach(tableEntry => {
                    if (
                      (suggestTables.onlyTables && !tableEntry.isTable()) ||
                      (suggestTables.onlyViews && !tableEntry.isView())
                    ) {
                      return;
                    }
                    tableSuggestions.push({
                      value:
                        prefix + sqlUtils.backTickIfNeeded(self.snippet.type(), tableEntry.name),
                      filterValue: tableEntry.name,
                      tableName: tableEntry.name,
                      meta: META_I18n[tableEntry.getType().toLowerCase()],
                      category: CATEGORIES.TABLE,
                      popular: ko.observable(false),
                      hasCatalogEntry: true,
                      details: tableEntry
                    });
                  });
                  tablesDeferred.resolve(tableSuggestions);
                })
                .fail(tablesDeferred.reject)
            );
          })
          .fail(tablesDeferred.reject);
      };

      if (
        self.snippet.type() === 'impala' &&
        self.parseResult.suggestTables.identifierChain &&
        self.parseResult.suggestTables.identifierChain.length === 1
      ) {
        databasesDeferred.done(databases => {
          const foundDb = databases.some(dbEntry => {
            return hueUtils.equalIgnoreCase(
              dbEntry.name,
              self.parseResult.suggestTables.identifierChain[0].name
            );
          });
          if (foundDb) {
            fetchTables();
          } else {
            self.parseResult.suggestColumns = {
              tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }]
            };
            tablesDeferred.reject();
          }
        });
      } else if (
        self.snippet.type() === 'impala' &&
        self.parseResult.suggestTables.identifierChain &&
        self.parseResult.suggestTables.identifierChain.length > 1
      ) {
        self.parseResult.suggestColumns = {
          tables: [{ identifierChain: self.parseResult.suggestTables.identifierChain }]
        };
        tablesDeferred.reject();
      } else {
        fetchTables();
      }
    } else {
      tablesDeferred.reject();
    }

    return tablesDeferred;
  }

  handleColumns(colRefDeferred, tablesDeferred) {
    const self = this;
    const columnsDeferred = $.Deferred();

    tablesDeferred.always(() => {
      if (self.parseResult.suggestColumns) {
        initLoading(self.loadingColumns, columnsDeferred);
        columnsDeferred.done(self.appendEntries);

        const suggestColumns = self.parseResult.suggestColumns;
        const columnSuggestions = [];
        // For multiple tables we need to merge and make sure identifiers are unique
        const columnDeferrals = [];

        const waitForCols = function() {
          $.when.apply($, columnDeferrals).always(() => {
            AutocompleteResults.mergeColumns(columnSuggestions);
            if (
              self.snippet.type() === 'hive' &&
              /[^.]$/.test(self.editor().getTextBeforeCursor())
            ) {
              columnSuggestions.push({
                value: 'BLOCK__OFFSET__INSIDE__FILE',
                meta: META_I18n.virtual,
                category: CATEGORIES.VIRTUAL_COLUMN,
                popular: ko.observable(false),
                details: { name: 'BLOCK__OFFSET__INSIDE__FILE' }
              });
              columnSuggestions.push({
                value: 'INPUT__FILE__NAME',
                meta: META_I18n.virtual,
                category: CATEGORIES.VIRTUAL_COLUMN,
                popular: ko.observable(false),
                details: { name: 'INPUT__FILE__NAME' }
              });
            }
            columnsDeferred.resolve(columnSuggestions);
          });
        };

        if (suggestColumns.types && suggestColumns.types[0] === 'COLREF') {
          colRefDeferred.done(colRef => {
            suggestColumns.tables.forEach(table => {
              columnDeferrals.push(
                self.addColumns(table, [colRef.type.toUpperCase()], columnSuggestions)
              );
            });
            waitForCols();
          });
        } else {
          suggestColumns.tables.forEach(table => {
            columnDeferrals.push(
              self.addColumns(table, suggestColumns.types || ['T'], columnSuggestions)
            );
          });
          waitForCols();
        }
      } else {
        columnsDeferred.reject();
      }
    });

    return columnsDeferred;
  }

  addColumns(table, types, columnSuggestions) {
    const self = this;
    const addColumnsDeferred = $.Deferred();

    if (
      typeof table.identifierChain !== 'undefined' &&
      table.identifierChain.length === 1 &&
      typeof table.identifierChain[0].cte !== 'undefined'
    ) {
      if (
        typeof self.parseResult.commonTableExpressions !== 'undefined' &&
        self.parseResult.commonTableExpressions.length > 0
      ) {
        self.parseResult.commonTableExpressions.every(cte => {
          if (hueUtils.equalIgnoreCase(cte.alias, table.identifierChain[0].cte)) {
            cte.columns.forEach(column => {
              const type =
                typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
              if (typeof column.alias !== 'undefined') {
                columnSuggestions.push({
                  value: sqlUtils.backTickIfNeeded(self.snippet.type(), column.alias),
                  filterValue: column.alias,
                  meta: type,
                  category: CATEGORIES.COLUMN,
                  table: table,
                  popular: ko.observable(false),
                  details: column
                });
              } else if (
                typeof column.identifierChain !== 'undefined' &&
                column.identifierChain.length > 0 &&
                typeof column.identifierChain[column.identifierChain.length - 1].name !==
                  'undefined'
              ) {
                columnSuggestions.push({
                  value: sqlUtils.backTickIfNeeded(
                    self.snippet.type(),
                    column.identifierChain[column.identifierChain.length - 1].name
                  ),
                  filterValue: column.identifierChain[column.identifierChain.length - 1].name,
                  meta: type,
                  category: CATEGORIES.COLUMN,
                  table: table,
                  popular: ko.observable(false),
                  details: column
                });
              }
            });
            return false;
          }
          return true;
        });
      }
      addColumnsDeferred.resolve();
    } else if (
      typeof table.identifierChain !== 'undefined' &&
      table.identifierChain.length === 1 &&
      typeof table.identifierChain[0].subQuery !== 'undefined'
    ) {
      const foundSubQuery = locateSubQuery(
        self.parseResult.subQueries,
        table.identifierChain[0].subQuery
      );

      const addSubQueryColumns = function(subQueryColumns) {
        subQueryColumns.forEach(column => {
          if (column.alias || column.identifierChain) {
            // TODO: Potentially fetch column types for sub-queries, possible performance hit.
            const type =
              typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
            if (column.alias) {
              columnSuggestions.push({
                value: sqlUtils.backTickIfNeeded(self.snippet.type(), column.alias),
                filterValue: column.alias,
                meta: type,
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              });
            } else if (column.identifierChain && column.identifierChain.length > 0) {
              columnSuggestions.push({
                value: sqlUtils.backTickIfNeeded(
                  self.snippet.type(),
                  column.identifierChain[column.identifierChain.length - 1].name
                ),
                filterValue: column.identifierChain[column.identifierChain.length - 1].name,
                meta: type,
                category: CATEGORIES.COLUMN,
                table: table,
                popular: ko.observable(false),
                details: column
              });
            }
          } else if (column.subQuery && foundSubQuery.subQueries) {
            const foundNestedSubQuery = locateSubQuery(foundSubQuery.subQueries, column.subQuery);
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
      const addColumnsFromEntry = function(dataCatalogEntry) {
        self.cancellablePromises.push(
          dataCatalogEntry
            .getSourceMeta({ silenceErrors: true, cancellable: true })
            .done(sourceMeta => {
              self.cancellablePromises.push(
                dataCatalogEntry
                  .getChildren({ silenceErrors: true, cancellable: true })
                  .done(childEntries => {
                    childEntries.forEach(childEntry => {
                      let name = sqlUtils.backTickIfNeeded(self.snippet.type(), childEntry.name);
                      if (
                        self.snippet.type() === 'hive' &&
                        (childEntry.isArray() || childEntry.isMap())
                      ) {
                        name += '[]';
                      }
                      if (
                        SqlFunctions.matchesType(self.snippet.type(), types, [
                          childEntry.getType().toUpperCase()
                        ]) ||
                        SqlFunctions.matchesType(
                          self.snippet.type(),
                          [childEntry.getType().toUpperCase()],
                          types
                        ) ||
                        childEntry.getType === 'column' ||
                        childEntry.isComplex()
                      ) {
                        columnSuggestions.push({
                          value: name,
                          meta: childEntry.getType(),
                          table: table,
                          category: CATEGORIES.COLUMN,
                          popular: ko.observable(false),
                          weightAdjust:
                            types[0].toUpperCase() !== 'T' &&
                            types.some(type => {
                              return hueUtils.equalIgnoreCase(type, childEntry.getType());
                            })
                              ? 1
                              : 0,
                          hasCatalogEntry: true,
                          details: childEntry
                        });
                      }
                    });
                    if (
                      self.snippet.type() === 'hive' &&
                      (dataCatalogEntry.isArray() || dataCatalogEntry.isMap())
                    ) {
                      // Remove 'item' or 'value' and 'key' for Hive
                      columnSuggestions.pop();
                      if (dataCatalogEntry.isMap()) {
                        columnSuggestions.pop();
                      }
                    }

                    const complexExtras =
                      (sourceMeta.value && sourceMeta.value.fields) ||
                      (sourceMeta.item && sourceMeta.item.fields);
                    if (
                      (self.snippet.type() === 'impala' || self.snippet.type() === 'hive') &&
                      complexExtras
                    ) {
                      complexExtras.forEach(field => {
                        const fieldType =
                          field.type.indexOf('<') !== -1
                            ? field.type.substring(0, field.type.indexOf('<'))
                            : field.type;
                        columnSuggestions.push({
                          value: field.name,
                          meta: fieldType,
                          table: table,
                          category: CATEGORIES.COLUMN,
                          popular: ko.observable(false),
                          weightAdjust:
                            types[0].toUpperCase() !== 'T' &&
                            types.some(type => {
                              return hueUtils.equalIgnoreCase(type, fieldType);
                            })
                              ? 1
                              : 0,
                          hasCatalogEntry: false,
                          details: field
                        });
                      });
                    }
                    addColumnsDeferred.resolve();
                  })
                  .fail(addColumnsDeferred.reject)
              );
            })
            .fail(addColumnsDeferred.reject)
        );
      };

      if (self.parseResult.suggestColumns && self.parseResult.suggestColumns.identifierChain) {
        self
          .fetchFieldsForIdentifiers(
            table.identifierChain.concat(self.parseResult.suggestColumns.identifierChain)
          )
          .done(addColumnsFromEntry)
          .fail(addColumnsDeferred.reject);
      } else {
        self
          .fetchFieldsForIdentifiers(table.identifierChain)
          .done(addColumnsFromEntry)
          .fail(addColumnsDeferred.reject);
      }
    } else {
      addColumnsDeferred.resolve();
    }
    return addColumnsDeferred;
  }

  static mergeColumns(columnSuggestions) {
    columnSuggestions.sort((a, b) => {
      return a.value.localeCompare(b.value);
    });

    for (let i = 0; i < columnSuggestions.length; i++) {
      const suggestion = columnSuggestions[i];
      suggestion.isColumn = true;
      let hasDuplicates = false;
      for (
        i;
        i + 1 < columnSuggestions.length && columnSuggestions[i + 1].value === suggestion.value;
        i++
      ) {
        const nextTable = columnSuggestions[i + 1].table;
        if (typeof nextTable.alias !== 'undefined') {
          columnSuggestions[i + 1].value = nextTable.alias + '.' + columnSuggestions[i + 1].value;
        } else if (
          typeof nextTable.identifierChain !== 'undefined' &&
          nextTable.identifierChain.length > 0
        ) {
          const previousIdentifier =
            nextTable.identifierChain[nextTable.identifierChain.length - 1];
          if (typeof previousIdentifier.name !== 'undefined') {
            columnSuggestions[i + 1].value =
              previousIdentifier.name + '.' + columnSuggestions[i + 1].value;
          } else if (typeof previousIdentifier.subQuery !== 'undefined') {
            columnSuggestions[i + 1].value =
              previousIdentifier.subQuery + '.' + columnSuggestions[i + 1].value;
          }
        }
        hasDuplicates = true;
      }
      if (typeof suggestion.table.alias !== 'undefined') {
        suggestion.value = suggestion.table.alias + '.' + suggestion.value;
      } else if (
        hasDuplicates &&
        typeof suggestion.table.identifierChain !== 'undefined' &&
        suggestion.table.identifierChain.length > 0
      ) {
        const lastIdentifier =
          suggestion.table.identifierChain[suggestion.table.identifierChain.length - 1];
        if (typeof lastIdentifier.name !== 'undefined') {
          suggestion.value = lastIdentifier.name + '.' + suggestion.value;
        } else if (typeof lastIdentifier.subQuery !== 'undefined') {
          suggestion.value = lastIdentifier.subQuery + '.' + suggestion.value;
        }
      }
    }
  }

  handleValues(colRefDeferred) {
    const self = this;
    const suggestValues = self.parseResult.suggestValues;
    if (suggestValues) {
      const valueSuggestions = [];
      if (self.parseResult.colRef && self.parseResult.colRef.identifierChain) {
        valueSuggestions.push({
          value:
            '${' +
            self.parseResult.colRef.identifierChain[
              self.parseResult.colRef.identifierChain.length - 1
            ].name +
            '}',
          meta: META_I18n.variable,
          category: CATEGORIES.VARIABLE,
          popular: ko.observable(false),
          details: null
        });
      }
      colRefDeferred.done(colRef => {
        if (colRef.sample) {
          const isString = colRef.type === 'string';
          const startQuote = suggestValues.partialQuote ? '' : "'";
          const endQuote =
            typeof suggestValues.missingEndQuote !== 'undefined' &&
            suggestValues.missingEndQuote === false
              ? ''
              : suggestValues.partialQuote || "'";
          colRef.sample.forEach(sample => {
            valueSuggestions.push({
              value: isString ? startQuote + sample + endQuote : new String(sample),
              meta: META_I18n.sample,
              category: CATEGORIES.SAMPLE,
              popular: ko.observable(false),
              details: null
            });
          });
        }
        self.appendEntries(valueSuggestions);
      });
    }
  }

  handlePaths() {
    const self = this;
    const suggestHdfs = self.parseResult.suggestHdfs;
    const pathsDeferred = $.Deferred();

    if (suggestHdfs) {
      initLoading(self.loadingPaths, pathsDeferred);
      pathsDeferred.done(self.appendEntries);

      let path = suggestHdfs.path;
      if (path === '') {
        self.appendEntries([
          {
            value: 'adl://',
            meta: META_I18n.keyword,
            category: CATEGORIES.KEYWORD,
            weightAdjust: 0,
            popular: ko.observable(false),
            details: null
          },
          {
            value: 's3a://',
            meta: META_I18n.keyword,
            category: CATEGORIES.KEYWORD,
            weightAdjust: 0,
            popular: ko.observable(false),
            details: null
          },
          {
            value: 'hdfs://',
            meta: META_I18n.keyword,
            category: CATEGORIES.KEYWORD,
            weightAdjust: 0,
            popular: ko.observable(false),
            details: null
          },
          {
            value: '/',
            meta: META_I18n.dir,
            category: CATEGORIES.HDFS,
            popular: ko.observable(false),
            details: null
          }
        ]);
      }

      let fetchFunction = 'fetchHdfsPath';

      if (/^s3a:\/\//i.test(path)) {
        fetchFunction = 'fetchS3Path';
        path = path.substring(5);
      } else if (/^adl:\/\//i.test(path)) {
        fetchFunction = 'fetchAdlsPath';
        path = path.substring(5);
      } else if (/^hdfs:\/\//i.test(path)) {
        path = path.substring(6);
      }

      const parts = path.split('/');
      // Drop the first " or '
      parts.shift();
      // Last one is either partial name or empty
      parts.pop();

      self.lastKnownRequests.push(
        apiHelper[fetchFunction]({
          pathParts: parts,
          successCallback: function(data) {
            if (!data.error) {
              const pathSuggestions = [];
              data.files.forEach(file => {
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
        })
      );
    } else {
      pathsDeferred.reject();
    }
    return pathsDeferred;
  }

  tableIdentifierChainsToPaths(tables) {
    const self = this;
    const paths = [];
    tables.forEach(table => {
      // Could be subquery
      const isTable = table.identifierChain.every(identifier => {
        return typeof identifier.name !== 'undefined';
      });
      if (isTable) {
        const path = $.map(table.identifierChain, identifier => {
          return identifier.name;
        });
        if (path.length === 1) {
          path.unshift(self.activeDatabase);
        }
        paths.push(path);
      }
    });
    return paths;
  }

  handleJoins() {
    const self = this;
    const joinsDeferred = $.Deferred();
    const suggestJoins = self.parseResult.suggestJoins;
    if (window.HAS_OPTIMIZER && suggestJoins) {
      initLoading(self.loadingJoins, joinsDeferred);
      joinsDeferred.done(self.appendEntries);

      const paths = self.tableIdentifierChainsToPaths(suggestJoins.tables);
      if (paths.length) {
        dataCatalog
          .getMultiTableEntry({
            sourceType: self.snippet.type(),
            namespace: self.snippet.namespace(),
            compute: self.snippet.compute(),
            paths: paths
          })
          .done(multiTableEntry => {
            self.cancellablePromises.push(
              multiTableEntry
                .getTopJoins({ silenceErrors: true, cancellable: true })
                .done(topJoins => {
                  const joinSuggestions = [];
                  let totalCount = 0;
                  if (topJoins.values) {
                    topJoins.values.forEach(value => {
                      let joinType = value.joinType || 'join';
                      joinType += ' ';
                      let suggestionString = suggestJoins.prependJoin
                        ? self.parseResult.lowerCase
                          ? joinType.toLowerCase()
                          : joinType.toUpperCase()
                        : '';
                      let first = true;

                      const existingTables = {};
                      suggestJoins.tables.forEach(table => {
                        existingTables[
                          table.identifierChain[table.identifierChain.length - 1].name
                        ] = true;
                      });

                      let joinRequired = false;
                      let tablesAdded = false;
                      value.tables.forEach(table => {
                        const tableParts = table.split('.');
                        if (!existingTables[tableParts[tableParts.length - 1]]) {
                          tablesAdded = true;
                          const identifier = self.convertNavOptQualifiedIdentifier(
                            table,
                            suggestJoins.tables
                          );
                          suggestionString += joinRequired
                            ? (self.parseResult.lowerCase ? ' join ' : ' JOIN ') + identifier
                            : identifier;
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
                        value.joinCols.forEach(joinColPair => {
                          if (!first) {
                            suggestionString += self.parseResult.lowerCase ? ' and ' : ' AND ';
                          }
                          suggestionString +=
                            self.convertNavOptQualifiedIdentifier(
                              joinColPair.columns[0],
                              suggestJoins.tables,
                              self.snippet.type()
                            ) +
                            ' = ' +
                            self.convertNavOptQualifiedIdentifier(
                              joinColPair.columns[1],
                              suggestJoins.tables,
                              self.snippet.type()
                            );
                          first = false;
                        });
                        totalCount += value.totalQueryCount;
                        joinSuggestions.push({
                          value: suggestionString,
                          meta: META_I18n.join,
                          category: suggestJoins.prependJoin
                            ? CATEGORIES.POPULAR_JOIN
                            : CATEGORIES.POPULAR_ACTIVE_JOIN,
                          popular: ko.observable(true),
                          details: value
                        });
                      }
                    });
                    joinSuggestions.forEach(suggestion => {
                      suggestion.details.relativePopularity =
                        totalCount === 0
                          ? suggestion.details.totalQueryCount
                          : Math.round((100 * suggestion.details.totalQueryCount) / totalCount);
                      suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
                    });
                  }
                  joinsDeferred.resolve(joinSuggestions);
                })
                .fail(joinsDeferred.reject)
            );
          })
          .fail(joinsDeferred.reject);
      } else {
        joinsDeferred.reject();
      }
    } else {
      joinsDeferred.reject();
    }
    return joinsDeferred;
  }

  handleJoinConditions() {
    const self = this;
    const joinConditionsDeferred = $.Deferred();
    const suggestJoinConditions = self.parseResult.suggestJoinConditions;
    if (window.HAS_OPTIMIZER && suggestJoinConditions) {
      initLoading(self.loadingJoinConditions, joinConditionsDeferred);
      joinConditionsDeferred.done(self.appendEntries);

      const paths = self.tableIdentifierChainsToPaths(suggestJoinConditions.tables);
      if (paths.length) {
        dataCatalog
          .getMultiTableEntry({
            sourceType: self.snippet.type(),
            namespace: self.snippet.namespace(),
            compute: self.snippet.compute(),
            paths: paths
          })
          .done(multiTableEntry => {
            self.cancellablePromises.push(
              multiTableEntry
                .getTopJoins({ silenceErrors: true, cancellable: true })
                .done(topJoins => {
                  const joinConditionSuggestions = [];
                  let totalCount = 0;
                  if (topJoins.values) {
                    topJoins.values.forEach(value => {
                      if (value.joinCols.length > 0) {
                        let suggestionString = suggestJoinConditions.prependOn
                          ? self.parseResult.lowerCase
                            ? 'on '
                            : 'ON '
                          : '';
                        let first = true;
                        value.joinCols.forEach(joinColPair => {
                          if (!first) {
                            suggestionString += self.parseResult.lowerCase ? ' and ' : ' AND ';
                          }
                          suggestionString +=
                            self.convertNavOptQualifiedIdentifier(
                              joinColPair.columns[0],
                              suggestJoinConditions.tables
                            ) +
                            ' = ' +
                            self.convertNavOptQualifiedIdentifier(
                              joinColPair.columns[1],
                              suggestJoinConditions.tables
                            );
                          first = false;
                        });
                        totalCount += value.totalQueryCount;
                        joinConditionSuggestions.push({
                          value: suggestionString,
                          meta: META_I18n.joinCondition,
                          category: CATEGORIES.POPULAR_JOIN_CONDITION,
                          popular: ko.observable(true),
                          details: value
                        });
                      }
                    });
                    joinConditionSuggestions.forEach(suggestion => {
                      suggestion.details.relativePopularity =
                        totalCount === 0
                          ? suggestion.details.totalQueryCount
                          : Math.round((100 * suggestion.details.totalQueryCount) / totalCount);
                      suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
                    });
                  }

                  joinConditionsDeferred.resolve(joinConditionSuggestions);
                })
                .fail(joinConditionsDeferred.reject)
            );
          })
          .fail(joinConditionsDeferred.reject);
      } else {
        joinConditionsDeferred.reject();
      }
    } else {
      joinConditionsDeferred.reject();
    }

    return joinConditionsDeferred;
  }

  handleAggregateFunctions() {
    const self = this;
    const aggregateFunctionsDeferred = $.Deferred();

    const suggestAggregateFunctions = self.parseResult.suggestAggregateFunctions;
    if (
      window.HAS_OPTIMIZER &&
      suggestAggregateFunctions &&
      suggestAggregateFunctions.tables.length > 0
    ) {
      initLoading(self.loadingAggregateFunctions, aggregateFunctionsDeferred);
      aggregateFunctionsDeferred.done(self.appendEntries);

      const paths = self.tableIdentifierChainsToPaths(suggestAggregateFunctions.tables);
      if (paths.length) {
        dataCatalog
          .getMultiTableEntry({
            sourceType: self.snippet.type(),
            namespace: self.snippet.namespace(),
            compute: self.snippet.compute(),
            paths: paths
          })
          .done(multiTableEntry => {
            self.cancellablePromises.push(
              multiTableEntry
                .getTopAggs({ silenceErrors: true, cancellable: true })
                .done(topAggs => {
                  const aggregateFunctionsSuggestions = [];
                  if (topAggs.values && topAggs.values.length > 0) {
                    // Expand all column names to the fully qualified name including db and table.
                    topAggs.values.forEach(value => {
                      value.aggregateInfo.forEach(info => {
                        value.aggregateClause = value.aggregateClause.replace(
                          new RegExp('([^.])' + info.columnName, 'gi'),
                          '$1' + info.databaseName + '.' + info.tableName + '.' + info.columnName
                        );
                      });
                    });

                    // Substitute qualified table identifiers with either alias or table when multiple tables are present or just empty string
                    const substitutions = [];
                    suggestAggregateFunctions.tables.forEach(table => {
                      const replaceWith = table.alias
                        ? table.alias + '.'
                        : suggestAggregateFunctions.tables.length > 1
                        ? table.identifierChain[table.identifierChain.length - 1].name + '.'
                        : '';
                      if (table.identifierChain.length > 1) {
                        substitutions.push({
                          replace: new RegExp(
                            $.map(table.identifierChain, identifier => {
                              return identifier.name;
                            }).join('.') + '.',
                            'gi'
                          ),
                          with: replaceWith
                        });
                      } else if (table.identifierChain.length === 1) {
                        substitutions.push({
                          replace: new RegExp(
                            self.activeDatabase + '.' + table.identifierChain[0].name + '.',
                            'gi'
                          ),
                          with: replaceWith
                        });
                        substitutions.push({
                          replace: new RegExp(table.identifierChain[0].name + '.', 'gi'),
                          with: replaceWith
                        });
                      }
                    });

                    let totalCount = 0;
                    topAggs.values.forEach(value => {
                      let clean = value.aggregateClause;
                      substitutions.forEach(substitution => {
                        clean = clean.replace(substitution.replace, substitution.with);
                      });
                      totalCount += value.totalQueryCount;
                      value.function = SqlFunctions.findFunction(
                        self.snippet.type(),
                        value.aggregateFunction
                      );
                      aggregateFunctionsSuggestions.push({
                        value: clean,
                        meta: value.function.returnTypes.join('|'),
                        category: CATEGORIES.POPULAR_AGGREGATE,
                        weightAdjust: Math.min(value.totalQueryCount, 99),
                        popular: ko.observable(true),
                        details: value
                      });
                    });

                    aggregateFunctionsSuggestions.forEach(suggestion => {
                      suggestion.details.relativePopularity =
                        totalCount === 0
                          ? suggestion.details.totalQueryCount
                          : Math.round((100 * suggestion.details.totalQueryCount) / totalCount);
                      suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
                    });
                  }
                  aggregateFunctionsDeferred.resolve(aggregateFunctionsSuggestions);
                })
                .fail(aggregateFunctionsDeferred.reject)
            );
          })
          .fail(aggregateFunctionsDeferred.reject);
      } else {
        aggregateFunctionsDeferred.reject();
      }
    } else {
      aggregateFunctionsDeferred.reject();
    }
    return aggregateFunctionsDeferred;
  }

  handlePopularGroupByOrOrderBy(navOptAttribute, suggestSpec, deferred, columnsDeferred) {
    const self = this;
    const paths = [];
    suggestSpec.tables.forEach(table => {
      if (table.identifierChain) {
        if (table.identifierChain.length === 1 && table.identifierChain[0].name) {
          paths.push([self.activeDatabase, table.identifierChain[0].name]);
        } else if (
          table.identifierChain.length === 2 &&
          table.identifierChain[0].name &&
          table.identifierChain[1].name
        ) {
          paths.push([table.identifierChain[0].name, table.identifierChain[1].name]);
        }
      }
    });

    self.cancellablePromises.push(
      dataCatalog
        .getCatalog(self.snippet.type())
        .loadNavOptPopularityForTables({
          namespace: self.snippet.namespace(),
          compute: self.snippet.compute(),
          paths: paths,
          silenceErrors: true,
          cancellable: true
        })
        .done(entries => {
          let totalColumnCount = 0;
          const matchedEntries = [];
          const prefix = suggestSpec.prefix
            ? (self.parseResult.lowerCase ? suggestSpec.prefix.toLowerCase() : suggestSpec.prefix) +
              ' '
            : '';

          entries.forEach(entry => {
            if (entry.navOptPopularity[navOptAttribute]) {
              totalColumnCount += entry.navOptPopularity[navOptAttribute].columnCount;
              matchedEntries.push(entry);
            }
          });
          if (totalColumnCount > 0) {
            const suggestions = [];
            matchedEntries.forEach(entry => {
              const filterValue = self.createNavOptIdentifierForColumn(
                entry.navOptPopularity[navOptAttribute],
                suggestSpec.tables
              );
              suggestions.push({
                value: prefix + filterValue,
                filterValue: filterValue,
                meta: navOptAttribute === 'groupByColumn' ? META_I18n.groupBy : META_I18n.orderBy,
                category:
                  navOptAttribute === 'groupByColumn'
                    ? CATEGORIES.POPULAR_GROUP_BY
                    : CATEGORIES.POPULAR_ORDER_BY,
                weightAdjust: Math.round(
                  (100 * entry.navOptPopularity[navOptAttribute].columnCount) / totalColumnCount
                ),
                popular: ko.observable(true),
                hasCatalogEntry: false,
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
        })
        .fail(deferred.reject)
    );
  }

  handleGroupBys(columnsDeferred) {
    const self = this;
    const groupBysDeferred = $.Deferred();
    const suggestGroupBys = self.parseResult.suggestGroupBys;
    if (window.HAS_OPTIMIZER && suggestGroupBys) {
      initLoading(self.loadingGroupBys, groupBysDeferred);
      groupBysDeferred.done(self.appendEntries);
      self.handlePopularGroupByOrOrderBy(
        'groupByColumn',
        suggestGroupBys,
        groupBysDeferred,
        columnsDeferred
      );
    } else {
      groupBysDeferred.reject();
    }

    return groupBysDeferred;
  }

  handleOrderBys(columnsDeferred) {
    const self = this;
    const orderBysDeferred = $.Deferred();
    const suggestOrderBys = self.parseResult.suggestOrderBys;
    if (window.HAS_OPTIMIZER && suggestOrderBys) {
      initLoading(self.loadingOrderBys, orderBysDeferred);
      orderBysDeferred.done(self.appendEntries);
      self.handlePopularGroupByOrOrderBy(
        'orderByColumn',
        suggestOrderBys,
        orderBysDeferred,
        columnsDeferred
      );
    } else {
      orderBysDeferred.reject();
    }
    return orderBysDeferred;
  }

  handleFilters() {
    const self = this;
    const filtersDeferred = $.Deferred();
    const suggestFilters = self.parseResult.suggestFilters;
    if (window.HAS_OPTIMIZER && suggestFilters) {
      initLoading(self.loadingFilters, filtersDeferred);
      filtersDeferred.done(self.appendEntries);

      const paths = self.tableIdentifierChainsToPaths(suggestFilters.tables);
      if (paths.length) {
        dataCatalog
          .getMultiTableEntry({
            sourceType: self.snippet.type(),
            namespace: self.snippet.namespace(),
            compute: self.snippet.compute(),
            paths: paths
          })
          .done(multiTableEntry => {
            self.cancellablePromises.push(
              multiTableEntry
                .getTopFilters({ silenceErrors: true, cancellable: true })
                .done(topFilters => {
                  const filterSuggestions = [];
                  let totalCount = 0;
                  if (topFilters.values) {
                    topFilters.values.forEach(value => {
                      if (
                        typeof value.popularValues !== 'undefined' &&
                        value.popularValues.length > 0
                      ) {
                        value.popularValues.forEach(popularValue => {
                          if (typeof popularValue.group !== 'undefined') {
                            popularValue.group.forEach(grp => {
                              let compVal = suggestFilters.prefix
                                ? (self.parseResult.lowerCase
                                    ? suggestFilters.prefix.toLowerCase()
                                    : suggestFilters.prefix) + ' '
                                : '';
                              compVal += self.createNavOptIdentifier(
                                value.tableName,
                                grp.columnName,
                                suggestFilters.tables
                              );
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
                                meta: META_I18n.filter,
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
                  filterSuggestions.forEach(suggestion => {
                    suggestion.details.relativePopularity =
                      totalCount === 0
                        ? suggestion.details.count
                        : Math.round((100 * suggestion.details.count) / totalCount);
                    suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
                  });

                  filtersDeferred.resolve(filterSuggestions);
                })
                .fail(filtersDeferred.reject)
            );
          })
          .fail(filtersDeferred.reject);
      } else {
        filtersDeferred.reject();
      }
    } else {
      filtersDeferred.reject();
    }
    return filtersDeferred;
  }

  handlePopularTables(tablesDeferred) {
    const self = this;
    const popularTablesDeferred = $.Deferred();
    if (window.HAS_OPTIMIZER && self.parseResult.suggestTables) {
      initLoading(self.loadingPopularTables, popularTablesDeferred);

      const db =
        self.parseResult.suggestTables.identifierChain &&
        self.parseResult.suggestTables.identifierChain.length === 1 &&
        self.parseResult.suggestTables.identifierChain[0].name
          ? self.parseResult.suggestTables.identifierChain[0].name
          : self.activeDatabase;

      dataCatalog
        .getEntry({
          sourceType: self.snippet.type(),
          namespace: self.snippet.namespace(),
          compute: self.snippet.compute(),
          path: [db],
          temporaryOnly: self.temporaryOnly
        })
        .done(entry => {
          self.cancellablePromises.push(
            entry
              .loadNavOptPopularityForChildren({ silenceErrors: true, cancellable: true })
              .done(childEntries => {
                let totalPopularity = 0;
                const popularityIndex = {};
                childEntries.forEach(childEntry => {
                  if (childEntry.navOptPopularity && childEntry.navOptPopularity.popularity) {
                    popularityIndex[childEntry.name] = true;
                    totalPopularity += childEntry.navOptPopularity.popularity;
                  }
                });
                if (totalPopularity > 0 && Object.keys(popularityIndex).length) {
                  tablesDeferred
                    .done(tableSuggestions => {
                      tableSuggestions.forEach(suggestion => {
                        if (popularityIndex[suggestion.details.name]) {
                          suggestion.relativePopularity = Math.round(
                            (100 * suggestion.details.navOptPopularity.popularity) / totalPopularity
                          );
                          if (suggestion.relativePopularity >= 5) {
                            suggestion.popular(true);
                          }
                          suggestion.weightAdjust = suggestion.relativePopularity;
                        }
                      });
                      popularTablesDeferred.resolve();
                    })
                    .fail(popularTablesDeferred.reject);
                } else {
                  popularTablesDeferred.resolve();
                }
              })
              .fail(popularTablesDeferred.reject)
          );
        })
        .fail(popularTablesDeferred.reject);
    } else {
      popularTablesDeferred.reject();
    }
    return popularTablesDeferred;
  }

  handlePopularColumns(columnsDeferred) {
    const self = this;
    const popularColumnsDeferred = $.Deferred();
    const suggestColumns = self.parseResult.suggestColumns;

    // The columnsDeferred gets resolved synchronously when the data is cached, if not, assume there are some suggestions.
    let hasColumnSuggestions = true;
    columnsDeferred.done(columns => {
      hasColumnSuggestions = columns.length > 0;
    });

    if (
      hasColumnSuggestions &&
      window.HAS_OPTIMIZER &&
      suggestColumns &&
      suggestColumns.source !== 'undefined'
    ) {
      initLoading(self.loadingPopularColumns, popularColumnsDeferred);

      const paths = [];
      suggestColumns.tables.forEach(table => {
        if (table.identifierChain && table.identifierChain.length > 0) {
          if (table.identifierChain.length === 1 && table.identifierChain[0].name) {
            paths.push([self.activeDatabase, table.identifierChain[0].name]);
          } else if (
            table.identifierChain.length === 2 &&
            table.identifierChain[0].name &&
            table.identifierChain[1].name
          ) {
            paths.push([table.identifierChain[0].name, table.identifierChain[1].name]);
          }
        }
      });

      self.cancellablePromises.push(
        dataCatalog
          .getCatalog(self.snippet.type())
          .loadNavOptPopularityForTables({
            namespace: self.snippet.namespace(),
            compute: self.snippet.compute(),
            paths: paths,
            silenceErrors: true,
            cancellable: true
          })
          .done(popularEntries => {
            let valueAttribute = '';
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

            const popularityIndex = {};

            popularEntries.forEach(popularEntry => {
              if (popularEntry.navOptPopularity && popularEntry.navOptPopularity[valueAttribute]) {
                popularityIndex[popularEntry.getQualifiedPath()] = true;
              }
            });

            if (!valueAttribute || Object.keys(popularityIndex).length === 0) {
              popularColumnsDeferred.reject();
              return;
            }

            columnsDeferred
              .done(columns => {
                let totalColumnCount = 0;
                const matchedSuggestions = [];
                columns.forEach(suggestion => {
                  if (
                    suggestion.hasCatalogEntry &&
                    popularityIndex[suggestion.details.getQualifiedPath()]
                  ) {
                    matchedSuggestions.push(suggestion);
                    totalColumnCount +=
                      suggestion.details.navOptPopularity[valueAttribute].columnCount;
                  }
                });
                if (totalColumnCount > 0) {
                  matchedSuggestions.forEach(matchedSuggestion => {
                    matchedSuggestion.relativePopularity = Math.round(
                      (100 *
                        matchedSuggestion.details.navOptPopularity[valueAttribute].columnCount) /
                        totalColumnCount
                    );
                    if (matchedSuggestion.relativePopularity >= 5) {
                      matchedSuggestion.popular(true);
                    }
                    matchedSuggestion.weightAdjust = matchedSuggestion.relativePopularity;
                  });
                }
                popularColumnsDeferred.resolve();
              })
              .fail(popularColumnsDeferred.reject);
          })
      );
    } else {
      popularColumnsDeferred.reject();
    }
    return popularColumnsDeferred;
  }

  createNavOptIdentifier(navOptTableName, navOptColumnName, tables) {
    const self = this;
    let path = navOptTableName + '.' + navOptColumnName.split('.').pop();
    for (let i = 0; i < tables.length; i++) {
      let tablePath = '';
      if (tables[i].identifierChain.length === 2) {
        tablePath = $.map(tables[i].identifierChain, identifier => {
          return identifier.name;
        }).join('.');
      } else if (tables[i].identifierChain.length === 1) {
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
  }

  createNavOptIdentifierForColumn(navOptColumn, tables) {
    const self = this;
    for (let i = 0; i < tables.length; i++) {
      if (
        navOptColumn.dbName &&
        (navOptColumn.dbName !== self.activeDatabase ||
          navOptColumn.dbName !== tables[i].identifierChain[0].name)
      ) {
        continue;
      }
      if (
        navOptColumn.tableName &&
        hueUtils.equalIgnoreCase(
          navOptColumn.tableName,
          tables[i].identifierChain[tables[i].identifierChain.length - 1].name
        ) &&
        tables[i].alias
      ) {
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
  }

  convertNavOptQualifiedIdentifier(qualifiedIdentifier, tables, type) {
    const self = this;
    const aliases = [];
    let tablesHasDefaultDatabase = false;
    tables.forEach(table => {
      tablesHasDefaultDatabase =
        tablesHasDefaultDatabase ||
        hueUtils.equalIgnoreCase(
          table.identifierChain[0].name.toLowerCase(),
          self.activeDatabase.toLowerCase()
        );
      if (table.alias) {
        aliases.push({
          qualifiedName: $.map(table.identifierChain, identifier => {
            return identifier.name;
          })
            .join('.')
            .toLowerCase(),
          alias: table.alias
        });
      }
    });

    for (let i = 0; i < aliases.length; i++) {
      if (qualifiedIdentifier.toLowerCase().indexOf(aliases[i].qualifiedName) === 0) {
        return aliases[i].alias + qualifiedIdentifier.substring(aliases[i].qualifiedName.length);
      } else if (
        qualifiedIdentifier
          .toLowerCase()
          .indexOf(self.activeDatabase.toLowerCase() + '.' + aliases[i].qualifiedName) === 0
      ) {
        return (
          aliases[i].alias +
          qualifiedIdentifier.substring(
            (self.activeDatabase + '.' + aliases[i].qualifiedName).length
          )
        );
      }
    }

    if (
      qualifiedIdentifier.toLowerCase().indexOf(self.activeDatabase.toLowerCase()) === 0 &&
      !tablesHasDefaultDatabase
    ) {
      return qualifiedIdentifier.substring(self.activeDatabase.length + 1);
    }
    if (type === 'hive') {
      // Remove DB reference if given for Hive
      const parts = qualifiedIdentifier.split('.');
      if (parts.length > 2) {
        return parts.slice(1).join('.');
      }
    }
    return qualifiedIdentifier;
  }

  /**
   * Helper function to fetch columns/fields given an identifierChain, this also takes care of expanding arrays
   * and maps to match the required format for the API.
   *
   * @param originalIdentifierChain
   */
  fetchFieldsForIdentifiers(originalIdentifierChain) {
    const self = this;
    const deferred = $.Deferred();
    const path = [];
    for (let i = 0; i < originalIdentifierChain.length; i++) {
      if (originalIdentifierChain[i].name && !originalIdentifierChain[i].subQuery) {
        path.push(originalIdentifierChain[i].name);
      } else {
        return deferred.reject().promise();
      }
    }

    const fetchFieldsInternal = function(remainingPath, fetchedPath) {
      if (!fetchedPath) {
        fetchedPath = [];
      }
      if (remainingPath.length > 0) {
        fetchedPath.push(remainingPath.shift());
        // Parser sometimes knows if it's a map or array.
        if (
          remainingPath.length > 0 &&
          (remainingPath[0] === 'item' || remainingPath[0].name === 'value')
        ) {
          fetchedPath.push(remainingPath.shift());
        }
      }

      dataCatalog
        .getEntry({
          sourceType: self.snippet.type(),
          namespace: self.snippet.namespace(),
          compute: self.snippet.compute(),
          path: fetchedPath,
          temporaryOnly: self.temporaryOnly
        })
        .done(catalogEntry => {
          self.cancellablePromises.push(
            catalogEntry
              .getSourceMeta({ silenceErrors: true, cancellable: true })
              .done(sourceMeta => {
                if (
                  self.snippet.type() === 'hive' &&
                  typeof sourceMeta.extended_columns !== 'undefined' &&
                  sourceMeta.extended_columns.length === 1 &&
                  /^(?:map|array|struct)/i.test(sourceMeta.extended_columns[0].type)
                ) {
                  remainingPath.unshift(sourceMeta.extended_columns[0].name);
                }
                if (remainingPath.length) {
                  if (/value|item|key/i.test(remainingPath[0])) {
                    fetchedPath.push(remainingPath.shift());
                  } else if (sourceMeta.type === 'array') {
                    fetchedPath.push('item');
                  } else if (sourceMeta.type === 'map') {
                    fetchedPath.push('value');
                  }
                  fetchFieldsInternal(remainingPath, fetchedPath);
                } else {
                  deferred.resolve(catalogEntry);
                }
              })
              .fail(deferred.reject)
          );
        })
        .fail(deferred.reject);
    };

    // For Impala the first parts of the identifier chain could be either database or table, either:
    // SELECT | FROM database.table -or- SELECT | FROM table.column

    // For Hive it could be either:
    // SELECT col.struct FROM db.tbl -or- SELECT col.struct FROM tbl
    if (path.length > 1 && (self.snippet.type() === 'impala' || self.snippet.type() === 'hive')) {
      dataCatalog
        .getEntry({
          sourceType: self.snippet.type(),
          namespace: self.snippet.namespace(),
          compute: self.snippet.compute(),
          path: [],
          temporaryOnly: self.temporaryOnly
        })
        .done(catalogEntry => {
          self.cancellablePromises.push(
            catalogEntry
              .getChildren({ silenceErrors: true, cancellable: true })
              .done(databaseEntries => {
                const firstIsDb = databaseEntries.some(dbEntry => {
                  return hueUtils.equalIgnoreCase(dbEntry.name, path[0]);
                });
                if (!firstIsDb) {
                  path.unshift(self.activeDatabase);
                }
                fetchFieldsInternal(path);
              })
              .fail(deferred.reject)
          );
        })
        .fail(deferred.reject);
    } else if (path.length > 1) {
      fetchFieldsInternal(path);
    } else {
      path.unshift(self.activeDatabase);
      fetchFieldsInternal(path);
    }

    return deferred.promise();
  }
}

export default AutocompleteResults;
