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
import * as ko from 'knockout';

import apiHelper from 'api/apiHelper';
import dataCatalog from 'catalog/dataCatalog';
import HueColors from 'utils/hueColors';
import hueUtils from 'utils/hueUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import sqlUtils from 'sql/sqlUtils';
import { matchesType } from 'sql/reference/typeUtils';
import { DIALECT } from 'apps/notebook2/snippet';
import { cancelActiveRequest } from 'api/apiUtils';
import { findBrowserConnector, getRootFilePath } from 'utils/hueConfig';
import {
  findUdf,
  getArgumentDetailsForUdf,
  getUdfsWithReturnTypes,
  getReturnTypesForUdf,
  getSetOptions
} from './reference/sqlReferenceRepository';

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

const locateSubQuery = function (subQueries, subQueryName) {
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

class AutocompleteResults {
  /**
   *
   * @param options
   * @constructor
   */
  constructor(options) {
    this.snippet = options.snippet;
    this.dialect = () => (window.ENABLE_NOTEBOOK_2 ? this.snippet.dialect() : this.snippet.type());
    this.editor = options.editor;
    this.temporaryOnly =
      options.snippet.autocompleteSettings && options.snippet.autocompleteSettings.temporaryOnly;

    this.sortOverride = null;

    huePubSub.subscribe('editor.autocomplete.temporary.sort.override', sortOverride => {
      this.sortOverride = sortOverride;
    });

    this.entries = ko.observableArray();

    this.lastKnownRequests = [];
    this.cancellablePromises = [];
    this.activeRejectables = [];

    this.loadingKeywords = ko.observable(false);
    this.loadingFunctions = ko.observable(false);
    this.loadingDatabases = ko.observable(false);
    this.loadingTables = ko.observable(false);
    this.loadingColumns = ko.observable(false);
    this.loadingValues = ko.observable(false);
    this.loadingPaths = ko.observable(false);
    this.loadingJoins = ko.observable(false);
    this.loadingJoinConditions = ko.observable(false);
    this.loadingAggregateFunctions = ko.observable(false);
    this.loadingGroupBys = ko.observable(false);
    this.loadingOrderBys = ko.observable(false);
    this.loadingFilters = ko.observable(false);
    this.loadingPopularTables = ko.observable(false);
    this.loadingPopularColumns = ko.observable(false);

    this.loading = ko
      .pureComputed(
        () =>
          this.loadingKeywords() ||
          this.loadingFunctions() ||
          this.loadingDatabases() ||
          this.loadingTables() ||
          this.loadingColumns() ||
          this.loadingValues() ||
          this.loadingPaths() ||
          this.loadingJoins() ||
          this.loadingJoinConditions() ||
          this.loadingAggregateFunctions() ||
          this.loadingGroupBys() ||
          this.loadingOrderBys() ||
          this.loadingFilters() ||
          this.loadingPopularTables() ||
          this.loadingPopularColumns()
      )
      .extend({ rateLimit: 200 });

    this.filter = ko.observable();

    this.availableCategories = ko.observableArray([CATEGORIES.ALL]);

    this.availableCategories.subscribe(newCategories => {
      if (newCategories.indexOf(this.activeCategory()) === -1) {
        this.activeCategory(CATEGORIES.ALL);
      }
    });

    this.activeCategory = ko.observable(CATEGORIES.ALL);

    const updateCategories = suggestions => {
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
      this.availableCategories(result);
    };

    this.filtered = ko
      .pureComputed(() => {
        let result = this.entries();

        if (this.filter()) {
          result = sqlUtils.autocompleteFilter(this.filter(), result);
          huePubSub.publish('hue.ace.autocompleter.match.updated');
        }

        updateCategories(result);

        const activeCategory = this.activeCategory();

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

        sqlUtils.sortSuggestions(result, this.filter(), this.sortOverride);
        this.sortOverride = null;
        return result;
      })
      .extend({ rateLimit: 200 });
  }

  cancelRequests() {
    while (this.lastKnownRequests.length) {
      cancelActiveRequest(this.lastKnownRequests.pop());
    }

    while (this.cancellablePromises.length) {
      const promise = this.cancellablePromises.pop();
      if (promise.cancel) {
        promise.cancel();
      }
    }
  }

  async update(parseResult) {
    while (this.activeRejectables.length > 0) {
      this.activeRejectables.pop()();
    }

    this.activeDatabase = parseResult.useDatabase || this.snippet.database();
    this.parseResult = parseResult;

    this.entries([]);

    this.loadingKeywords(false);
    this.loadingFunctions(false);
    this.loadingDatabases(false);
    this.loadingTables(false);
    this.loadingColumns(false);
    this.loadingValues(false);
    this.loadingPaths(false);
    this.loadingJoins(false);
    this.loadingJoinConditions(false);
    this.loadingAggregateFunctions(false);
    this.loadingGroupBys(false);
    this.loadingOrderBys(false);
    this.loadingFilters(false);
    this.loadingPopularTables(false);
    this.loadingPopularColumns(false);

    this.filter('');

    if (this.parseResult.udfArgument) {
      await this.adjustForUdfArgument();
    }

    const promises = [];

    const trackPromise = promise => {
      const wrapped = new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        promise
          .then(suggestions => {
            if (suggestions && suggestions.length) {
              this.entries(this.entries().concat(suggestions));
            }
            resolve();
          })
          .catch(reject);
      });
      promises.push(wrapped);
      return promise;
    };

    const colRefPromise = this.handleColumnReference();
    const databasesPromise = this.loadDatabases();

    trackPromise(this.handleKeywords());
    trackPromise(this.handleColRefKeywords(colRefPromise));
    trackPromise(this.handleIdentifiers());
    trackPromise(this.handleColumnAliases());
    trackPromise(this.handleCommonTableExpressions());
    trackPromise(this.handleOptions());
    trackPromise(this.handleFunctions(colRefPromise));
    trackPromise(this.handleDatabases(databasesPromise));
    const tablesPromise = trackPromise(this.handleTables(databasesPromise));
    const columnsPromise = trackPromise(this.handleColumns(colRefPromise, tablesPromise));
    trackPromise(this.handleValues(colRefPromise));
    trackPromise(this.handlePaths());

    if (!this.temporaryOnly) {
      trackPromise(this.handleJoins());
      trackPromise(this.handleJoinConditions());
      trackPromise(this.handleAggregateFunctions());
      trackPromise(this.handleGroupBys(columnsPromise));
      trackPromise(this.handleOrderBys(columnsPromise));
      trackPromise(this.handleFilters());
      trackPromise(this.handlePopularTables(tablesPromise));
      trackPromise(this.handlePopularColumns(columnsPromise));
    }

    await Promise.allSettled(promises);
    huePubSub.publish('hue.ace.autocompleter.done');
  }

  async adjustForUdfArgument() {
    const foundArgumentDetails = (await getArgumentDetailsForUdf(
      this.snippet.connector(),
      this.parseResult.udfArgument.name,
      this.parseResult.udfArgument.position
    )) || [{ type: 'T' }];

    if (foundArgumentDetails.length === 0 && this.parseResult.suggestColumns) {
      delete this.parseResult.suggestColumns;
      delete this.parseResult.suggestKeyValues;
      delete this.parseResult.suggestValues;
      delete this.parseResult.suggestFunctions;
      delete this.parseResult.suggestIdentifiers;
      delete this.parseResult.suggestKeywords;
    } else if (foundArgumentDetails[0].type !== 'BOOLEAN') {
      if (this.parseResult.suggestFunctions && !this.parseResult.suggestFunctions.types) {
        this.parseResult.suggestFunctions.types = foundArgumentDetails.map(details => details.type);
      }
      if (this.parseResult.suggestColumns && !this.parseResult.suggestColumns.types) {
        this.parseResult.suggestColumns.types = foundArgumentDetails.map(details => details.type);
      }
    }
    if (foundArgumentDetails.length) {
      const keywords = [];
      foundArgumentDetails.forEach(details => {
        if (details.keywords) {
          keywords.push(...details.keywords);
        }
      });
      if (keywords.length) {
        if (!this.parseResult.suggestKeywords) {
          this.parseResult.suggestKeywords = [];
        }
        this.parseResult.suggestKeywords.push(
          ...keywords.map(keyword => {
            if (typeof keyword === 'object') {
              return keyword;
            }
            return {
              value: keyword,
              weight: 10000 // Bubble up units etc on top
            };
          })
        );
      }
    }
  }

  /**
   * For some suggestions the column type is needed, for instance with functions we should only suggest
   * columns that matches the argument type, cos(|) etc.
   *
   * The promise will always resolve, and the default values is { type: 'T' }
   *
   * @returns {Promise} - promise
   */
  async handleColumnReference() {
    if (!this.parseResult.colRef) {
      return { type: 'T' };
    }

    const foundVarRef = this.parseResult.colRef.identifierChain.some(
      identifier => typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0
    );

    if (!foundVarRef) {
      const catalogEntry = await this.fetchFieldForIdentifierChain(
        this.parseResult.colRef.identifierChain
      );
      try {
        const sourceMeta = await new Promise((resolve, reject) => {
          this.activeRejectables.push(reject);
          const sourceMetaDeferred = catalogEntry.getSourceMeta({
            silenceErrors: true,
            cancellable: true
          });
          this.cancellablePromises.push(sourceMetaDeferred);
          sourceMetaDeferred.done(resolve).fail(reject);
        });
        if (typeof sourceMeta.type !== 'undefined') {
          return sourceMeta; // sourceMeta.samples is used in handleValues.
        }
      } catch (err) {}
    }
    return { type: 'T' };
  }

  async loadDatabases() {
    try {
      const entry = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        dataCatalog
          .getEntry({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            connector: this.snippet.connector(),
            path: [],
            temporaryOnly: this.temporaryOnly
          })
          .done(resolve)
          .fail(reject);
      });

      return await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const childrenDeferred = entry.getChildren({ silenceErrors: true, cancellable: true });
        this.cancellablePromises.push(childrenDeferred);
        childrenDeferred.done(resolve).fail(reject);
      });
    } catch (err) {
      return [];
    }
  }

  async handleKeywords() {
    const suggestKeywords = this.parseResult.suggestKeywords;
    if (!suggestKeywords) {
      return [];
    }
    return suggestKeywords.map(keyword => ({
      value: this.parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value,
      meta: META_I18n.keyword,
      category: CATEGORIES.KEYWORD,
      weightAdjust: keyword.weight,
      popular: ko.observable(false),
      details: null
    }));
  }

  async handleColRefKeywords(colRefPromise) {
    const suggestColRefKeywords = this.parseResult.suggestColRefKeywords;
    if (!suggestColRefKeywords) {
      return [];
    }
    this.loadingKeywords(true);
    // Wait for the column reference type to be resolved to pick the right keywords
    const colRef = await colRefPromise;
    const colRefKeywordSuggestions = [];
    Object.keys(this.parseResult.suggestColRefKeywords).forEach(typeForKeywords => {
      if (matchesType(this.dialect(), [typeForKeywords], [colRef.type.toUpperCase()])) {
        this.parseResult.suggestColRefKeywords[typeForKeywords].forEach(keyword => {
          colRefKeywordSuggestions.push({
            value: this.parseResult.lowerCase ? keyword.toLowerCase() : keyword,
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
    this.loadingKeywords(false);
    return colRefKeywordSuggestions;
  }

  async handleIdentifiers() {
    const suggestIdentifiers = this.parseResult.suggestIdentifiers;
    if (!suggestIdentifiers) {
      return [];
    }
    return suggestIdentifiers.map(identifier => ({
      value: identifier.name,
      meta: identifier.type,
      category: CATEGORIES.IDENTIFIER,
      popular: ko.observable(false),
      details: null
    }));
  }

  async handleColumnAliases() {
    const suggestColumnAliases = this.parseResult.suggestColumnAliases;
    if (!suggestColumnAliases) {
      return [];
    }
    const columnAliasSuggestions = [];

    for (const columnAlias of suggestColumnAliases) {
      const type = columnAlias.types && columnAlias.types.length === 1 ? columnAlias.types[0] : 'T';
      if (type === 'COLREF') {
        columnAliasSuggestions.push({
          value: columnAlias.name,
          meta: META_I18n.alias,
          category: CATEGORIES.COLUMN,
          popular: ko.observable(false),
          details: columnAlias
        });
      } else if (type === 'UDFREF') {
        try {
          const types = await getReturnTypesForUdf(this.snippet.connector(), columnAlias.udfRef);
          const resolvedType = types.length === 1 ? types[0] : 'T';
          columnAliasSuggestions.push({
            value: columnAlias.name,
            meta: resolvedType,
            category: CATEGORIES.COLUMN,
            popular: ko.observable(false),
            details: columnAlias
          });
        } catch (err) {}
      } else {
        columnAliasSuggestions.push({
          value: columnAlias.name,
          meta: type,
          category: CATEGORIES.COLUMN,
          popular: ko.observable(false),
          details: columnAlias
        });
      }
    }

    return columnAliasSuggestions;
  }

  async handleCommonTableExpressions() {
    const suggestCommonTableExpressions = this.parseResult.suggestCommonTableExpressions;
    if (!suggestCommonTableExpressions) {
      return [];
    }
    const commonTableExpressionSuggestions = [];
    suggestCommonTableExpressions.forEach(expression => {
      let prefix = expression.prependQuestionMark ? '? ' : '';
      if (expression.prependFrom) {
        prefix += this.parseResult.lowerCase ? 'from ' : 'FROM ';
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

    return commonTableExpressionSuggestions;
  }

  async handleOptions() {
    if (!this.parseResult.suggestSetOptions) {
      return [];
    }
    try {
      const setOptions = await getSetOptions(this.snippet.connector());
      return Object.keys(setOptions).map(name => ({
        category: CATEGORIES.OPTION,
        value: name,
        meta: '',
        popular: ko.observable(false),
        weightAdjust: 0,
        details: setOptions[name]
      }));
    } catch (err) {
      return [];
    }
  }

  async handleFunctions(colRefPromise) {
    const suggestFunctions = this.parseResult.suggestFunctions;
    if (!suggestFunctions) {
      return [];
    }

    this.loadingFunctions(true);
    let suggestions = [];
    if (
      suggestFunctions.types &&
      (suggestFunctions.types[0] === 'COLREF' || suggestFunctions.types[0] === 'UDFREF')
    ) {
      const getUdfsForTypes = async types => {
        try {
          const functionsToSuggest = await getUdfsWithReturnTypes(
            this.snippet.connector(),
            types,
            this.parseResult.suggestAggregateFunctions || false,
            this.parseResult.suggestAnalyticFunctions || false
          );

          const firstType = types[0].toUpperCase();

          const functionSuggestions = [];
          functionsToSuggest.map(udf => ({
            category: CATEGORIES.UDF,
            value: udf.name + '()',
            meta: udf.returnTypes.join('|'),
            weightAdjust:
              firstType !== 'T' && udf.returnTypes.some(otherType => otherType === firstType)
                ? 1
                : 0,
            popular: ko.observable(false),
            details: udf
          }));

          return functionSuggestions;
        } catch (err) {
          return [];
        }
      };

      let types = ['T'];
      try {
        if (suggestFunctions.types[0] === 'COLREF') {
          const colRef = await colRefPromise;
          types = [colRef.type.toUpperCase()];
        } else {
          types = await getReturnTypesForUdf(this.snippet.connector(), suggestFunctions.udfRef);
        }
      } catch (err) {}
      suggestions = await getUdfsForTypes(types);
    } else {
      const types = suggestFunctions.types || ['T'];

      try {
        const functionsToSuggest = await getUdfsWithReturnTypes(
          this.snippet.connector(),
          types,
          this.parseResult.suggestAggregateFunctions || false,
          this.parseResult.suggestAnalyticFunctions || false
        );
        suggestions = functionsToSuggest.map(udf => ({
          category: CATEGORIES.UDF,
          value: udf.name + '()',
          meta: udf.returnTypes.join('|'),
          weightAdjust:
            types[0].toUpperCase() !== 'T' &&
            udf.returnTypes.some(otherType => otherType === types[0].toUpperCase())
              ? 1
              : 0,
          popular: ko.observable(false),
          details: udf
        }));
      } catch (err) {}
    }

    this.loadingFunctions(false);
    return suggestions;
  }

  async handleDatabases(databasesPromise) {
    const suggestDatabases = this.parseResult.suggestDatabases;
    if (!suggestDatabases) {
      return [];
    }
    this.loadingDatabases(true);
    const databaseSuggestions = [];
    try {
      let prefix = suggestDatabases.prependQuestionMark ? '? ' : '';
      if (suggestDatabases.prependFrom) {
        prefix += this.parseResult.lowerCase ? 'from ' : 'FROM ';
      }

      const catalogEntries = await databasesPromise;

      for (const dbEntry of catalogEntries) {
        if (dbEntry.name !== '') {
          databaseSuggestions.push({
            value:
              prefix +
              (await sqlUtils.backTickIfNeeded(this.snippet.connector(), dbEntry.name)) +
              (suggestDatabases.appendDot ? '.' : ''),
            filterValue: dbEntry.name,
            meta: META_I18n.database,
            category: CATEGORIES.DATABASE,
            popular: ko.observable(false),
            hasCatalogEntry: true,
            details: dbEntry
          });
        }
      }
    } catch (err) {}

    this.loadingDatabases(false);
    return databaseSuggestions;
  }

  async handleTables(databasesPromise) {
    const suggestTables = this.parseResult.suggestTables;
    if (!suggestTables) {
      return [];
    }
    this.loadingTables(true);

    const getTableSuggestions = async () => {
      let prefix = suggestTables.prependQuestionMark ? '? ' : '';
      if (suggestTables.prependFrom) {
        prefix += this.parseResult.lowerCase ? 'from ' : 'FROM ';
      }

      const database =
        suggestTables.identifierChain && suggestTables.identifierChain.length === 1
          ? suggestTables.identifierChain[0].name
          : this.activeDatabase;

      const tableSuggestions = [];

      try {
        const dbEntry = await new Promise((resolve, reject) => {
          this.activeRejectables.push(reject);
          dataCatalog
            .getEntry({
              namespace: this.snippet.namespace(),
              compute: this.snippet.compute(),
              connector: this.snippet.connector(),
              path: [database],
              temporaryOnly: this.temporaryOnly
            })
            .done(resolve)
            .fail(reject);
        });

        const tableEntries = await new Promise((resolve, reject) => {
          this.activeRejectables.push(reject);
          const childrenDeferred = dbEntry.getChildren({ silenceErrors: true, cancellable: true });
          this.cancellablePromises.push(childrenDeferred);
          childrenDeferred.done(resolve).fail(reject);
        });

        for (const tableEntry of tableEntries) {
          if (
            (suggestTables.onlyTables && !tableEntry.isTable()) ||
            (suggestTables.onlyViews && !tableEntry.isView())
          ) {
            continue;
          }
          tableSuggestions.push({
            value:
              prefix + (await sqlUtils.backTickIfNeeded(this.snippet.connector(), tableEntry.name)),
            filterValue: tableEntry.name,
            tableName: tableEntry.name,
            meta: META_I18n[tableEntry.getType().toLowerCase()],
            category: CATEGORIES.TABLE,
            popular: ko.observable(false),
            hasCatalogEntry: true,
            details: tableEntry
          });
        }
      } catch (err) {}

      return tableSuggestions;
    };

    let tableSuggestions = [];
    if (
      this.dialect() === DIALECT.impala &&
      suggestTables.identifierChain &&
      suggestTables.identifierChain.length === 1
    ) {
      try {
        const databases = await databasesPromise;
        const foundDb = databases.find(dbEntry =>
          hueUtils.equalIgnoreCase(dbEntry.name, suggestTables.identifierChain[0].name)
        );
        if (foundDb) {
          tableSuggestions = await getTableSuggestions();
        } else {
          this.parseResult.suggestColumns = {
            tables: [{ identifierChain: suggestTables.identifierChain }]
          };
        }
      } catch (err) {}
    } else if (
      this.dialect() === DIALECT.impala &&
      suggestTables.identifierChain &&
      suggestTables.identifierChain.length > 1
    ) {
      this.parseResult.suggestColumns = {
        tables: [{ identifierChain: suggestTables.identifierChain }]
      };
    } else {
      tableSuggestions = await getTableSuggestions();
    }

    this.loadingTables(false);
    return tableSuggestions;
  }

  async handleColumns(colRefPromise, tablesPromise) {
    try {
      await tablesPromise;
    } catch (err) {}

    const suggestColumns = this.parseResult.suggestColumns;
    if (!suggestColumns) {
      return [];
    }
    this.loadingColumns(true);

    const columnSuggestions = [];
    // For multiple tables we need to merge and make sure identifiers are unique
    const columnPromises = [];

    let types = ['T'];
    try {
      if (suggestColumns.types && suggestColumns.types[0] === 'COLREF') {
        const colRef = await colRefPromise;
        types = [colRef.type.toUpperCase()];
      } else if (suggestColumns.types && suggestColumns.types[0] === 'UDFREF') {
        types = await getReturnTypesForUdf(this.snippet.connector(), suggestColumns.udfRef);
      }
    } catch (err) {}

    suggestColumns.tables.forEach(table => {
      columnPromises.push(this.addColumns(table, types, columnSuggestions));
    });

    try {
      await Promise.allSettled(columnPromises);
    } catch (err) {}

    AutocompleteResults.mergeColumns(columnSuggestions);

    if (this.dialect() === DIALECT.hive && /[^.]$/.test(this.editor().getTextBeforeCursor())) {
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

    this.loadingColumns(false);
    return columnSuggestions;
  }

  async addCteColumns(table, columnSuggestions) {
    const cte = this.parseResult.commonTableExpressions.find(cte =>
      hueUtils.equalIgnoreCase(cte.alias, table.identifierChain[0].cte)
    );
    if (!cte) {
      return;
    }
    for (const column of cte.columns) {
      const type =
        typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
      if (typeof column.alias !== 'undefined') {
        columnSuggestions.push({
          value: await sqlUtils.backTickIfNeeded(this.snippet.connector(), column.alias),
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
        typeof column.identifierChain[column.identifierChain.length - 1].name !== 'undefined'
      ) {
        columnSuggestions.push({
          value: await sqlUtils.backTickIfNeeded(
            this.snippet.connector(),
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
    }
  }

  async addSubQueryColumns(table, columnSuggestions) {
    const foundSubQuery = locateSubQuery(
      this.parseResult.subQueries,
      table.identifierChain[0].subQuery
    );

    const addSubQueryColumnsRecursive = async subQueryColumns => {
      const connector = this.snippet.connector();
      for (const column of subQueryColumns) {
        if (column.alias || column.identifierChain) {
          // TODO: Potentially fetch column types for sub-queries, possible performance hit.
          const type =
            typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
          if (column.alias) {
            columnSuggestions.push({
              value: await sqlUtils.backTickIfNeeded(connector, column.alias),
              filterValue: column.alias,
              meta: type,
              category: CATEGORIES.COLUMN,
              table: table,
              popular: ko.observable(false),
              details: column
            });
          } else if (column.identifierChain && column.identifierChain.length > 0) {
            columnSuggestions.push({
              value: await sqlUtils.backTickIfNeeded(
                connector,
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
            await addSubQueryColumnsRecursive(foundNestedSubQuery.columns);
          }
        }
      }
    };
    if (foundSubQuery !== null && foundSubQuery.columns.length > 0) {
      await addSubQueryColumnsRecursive(foundSubQuery.columns);
    }
  }

  async addColumns(table, types, columnSuggestions) {
    if (
      typeof table.identifierChain !== 'undefined' &&
      table.identifierChain.length === 1 &&
      typeof table.identifierChain[0].cte !== 'undefined'
    ) {
      if (
        typeof this.parseResult.commonTableExpressions !== 'undefined' &&
        this.parseResult.commonTableExpressions.length > 0
      ) {
        await this.addCteColumns(table, columnSuggestions);
      }
    } else if (
      typeof table.identifierChain !== 'undefined' &&
      table.identifierChain.length === 1 &&
      typeof table.identifierChain[0].subQuery !== 'undefined'
    ) {
      await this.addSubQueryColumns(table, columnSuggestions);
    } else if (typeof table.identifierChain !== 'undefined') {
      const addColumnsFromEntry = async dataCatalogEntry => {
        const sourceMeta = await new Promise((resolve, reject) => {
          this.activeRejectables.push(reject);
          const sourceMetaDeferred = dataCatalogEntry.getSourceMeta({
            silenceErrors: true,
            cancellable: true
          });
          this.cancellablePromises.push(sourceMetaDeferred);
          sourceMetaDeferred.done(resolve).fail(reject);
        });

        const childEntries = await new Promise((resolve, reject) => {
          this.activeRejectables.push(reject);
          const childrenDeferred = dataCatalogEntry.getChildren({
            silenceErrors: true,
            cancellable: true
          });
          this.cancellablePromises.push(childrenDeferred);
          childrenDeferred.done(resolve).fail(reject);
        });

        for (const childEntry of childEntries) {
          let name = await sqlUtils.backTickIfNeeded(this.snippet.connector(), childEntry.name);
          if (this.dialect() === DIALECT.hive && (childEntry.isArray() || childEntry.isMap())) {
            name += '[]';
          }
          if (
            matchesType(this.dialect(), types, [childEntry.getType().toUpperCase()]) ||
            matchesType(this.dialect(), [childEntry.getType().toUpperCase()], types) ||
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
                types.some(type => hueUtils.equalIgnoreCase(type, childEntry.getType()))
                  ? 1
                  : 0,
              hasCatalogEntry: true,
              details: childEntry
            });
          }
        }
        if (
          this.dialect() === DIALECT.hive &&
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
          (this.dialect() === DIALECT.impala || this.dialect() === DIALECT.hive) &&
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
                types.some(type => hueUtils.equalIgnoreCase(type, fieldType))
                  ? 1
                  : 0,
              hasCatalogEntry: false,
              details: field
            });
          });
        }
      };

      const suggestcolumns = this.parseResult.suggestColumns;
      const identifierChain =
        (suggestcolumns && suggestcolumns.identifierChain) || table.identifierChain;
      const entry = await this.fetchFieldForIdentifierChain(identifierChain);
      if (entry) {
        await addColumnsFromEntry(entry);
      }
    }
  }

  static mergeColumns(columnSuggestions) {
    columnSuggestions.sort((a, b) => a.value.localeCompare(b.value));

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

  async handleValues(colRefPromise) {
    const suggestValues = this.parseResult.suggestValues;
    if (!suggestValues) {
      return [];
    }
    const valueSuggestions = [];
    const colRefResult = this.parseResult.colRef;
    if (colRefResult && colRefResult.identifierChain) {
      valueSuggestions.push({
        value:
          '${' + colRefResult.identifierChain[colRefResult.identifierChain.length - 1].name + '}',
        meta: META_I18n.variable,
        category: CATEGORIES.VARIABLE,
        popular: ko.observable(false),
        details: null
      });
    }

    this.loadingValues(true);
    const colRef = await colRefPromise;

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
          value: isString ? startQuote + sample + endQuote : String(sample),
          meta: META_I18n.sample,
          category: CATEGORIES.SAMPLE,
          popular: ko.observable(false),
          details: null
        });
      });
    }

    this.loadingValues(false);
    return valueSuggestions;
  }

  async handlePaths() {
    const suggestHdfs = this.parseResult.suggestHdfs;
    if (!suggestHdfs) {
      return [];
    }
    this.loadingPaths(true);

    let suggestions = [];

    let path = suggestHdfs.path;
    if (path === '') {
      suggestions = [
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
          value: 'abfs://',
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
      ];
    }

    let fetchFunction = 'fetchHdfsPath';

    if (/^s3a:\/\//i.test(path)) {
      fetchFunction = 'fetchS3Path';
      path = path.substring(5);
    } else if (/^adl:\/\//i.test(path)) {
      fetchFunction = 'fetchAdlsPath';
      path = path.substring(5);
    } else if (/^abfs:\/\//i.test(path)) {
      fetchFunction = 'fetchAbfsPath';
      path = path.substring(6);
      if (path === '/') {
        // TODO: connector.id for browsers
        const connector = findBrowserConnector(connector => connector.type === 'abfs');
        const rootPath = getRootFilePath(connector);
        if (rootPath) {
          suggestions.push({
            value: rootPath,
            meta: 'abfs',
            category: CATEGORIES.HDFS,
            weightAdjust: 0,
            popular: ko.observable(false),
            details: null
          });
          this.loadingPaths(false);
          return suggestions;
        }
      }
    } else if (/^hdfs:\/\//i.test(path)) {
      path = path.substring(6);
    }

    const parts = path.split('/');
    // Drop the first " or '
    parts.shift();
    // Last one is either partial name or empty
    parts.pop();

    await new Promise(resolve => {
      this.lastKnownRequests.push(
        apiHelper[fetchFunction]({
          pathParts: parts,
          successCallback: data => {
            if (!data.error) {
              data.files.forEach(file => {
                if (file.name !== '..' && file.name !== '.') {
                  suggestions.push({
                    value: path === '' ? '/' + file.name : file.name,
                    meta: file.type,
                    category: CATEGORIES.HDFS,
                    popular: ko.observable(false),
                    details: file
                  });
                }
              });
            }
            resolve();
          },
          silenceErrors: true,
          errorCallback: resolve,
          timeout: AUTOCOMPLETE_TIMEOUT
        })
      );
    });

    this.loadingPaths(false);
    return suggestions;
  }

  tableIdentifierChainsToPaths(tables) {
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
          path.unshift(this.activeDatabase);
        }
        paths.push(path);
      }
    });
    return paths;
  }

  async handleJoins() {
    const suggestJoins = this.parseResult.suggestJoins;
    if (!window.HAS_OPTIMIZER || !suggestJoins) {
      return [];
    }
    this.loadingJoins(true);

    const paths = this.tableIdentifierChainsToPaths(suggestJoins.tables);
    if (!paths.length) {
      return [];
    }

    const joinSuggestions = [];
    try {
      const multiTableEntry = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            connector: this.snippet.connector(),
            paths: paths
          })
          .done(resolve)
          .fail(reject);
      });

      const topJoins = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const topJoinsDeferred = multiTableEntry.getTopJoins({
          silenceErrors: true,
          cancellable: true,
          connector: this.snippet.connector()
        });
        this.cancellablePromises.push(topJoinsDeferred);
        topJoinsDeferred.done(resolve).fail(reject);
      });

      let totalCount = 0;
      if (topJoins.values) {
        topJoins.values.forEach(value => {
          let joinType = value.joinType || 'join';
          joinType += ' ';
          let suggestionString = suggestJoins.prependJoin
            ? this.parseResult.lowerCase
              ? joinType.toLowerCase()
              : joinType.toUpperCase()
            : '';
          let first = true;

          const existingTables = {};
          suggestJoins.tables.forEach(table => {
            existingTables[table.identifierChain[table.identifierChain.length - 1].name] = true;
          });

          let joinRequired = false;
          let tablesAdded = false;
          value.tables.forEach(table => {
            const tableParts = table.split('.');
            if (!existingTables[tableParts[tableParts.length - 1]]) {
              tablesAdded = true;
              const identifier = this.convertOptimizerQualifiedIdentifier(
                table,
                suggestJoins.tables
              );
              suggestionString += joinRequired
                ? (this.parseResult.lowerCase ? ' join ' : ' JOIN ') + identifier
                : identifier;
              joinRequired = true;
            }
          });

          if (value.joinCols.length > 0) {
            if (!tablesAdded && suggestJoins.prependJoin) {
              suggestionString = '';
              tablesAdded = true;
            }
            suggestionString += this.parseResult.lowerCase ? ' on ' : ' ON ';
          }
          if (tablesAdded) {
            value.joinCols.forEach(joinColPair => {
              if (!first) {
                suggestionString += this.parseResult.lowerCase ? ' and ' : ' AND ';
              }
              suggestionString +=
                this.convertOptimizerQualifiedIdentifier(
                  joinColPair.columns[0],
                  suggestJoins.tables,
                  this.dialect()
                ) +
                ' = ' +
                this.convertOptimizerQualifiedIdentifier(
                  joinColPair.columns[1],
                  suggestJoins.tables,
                  this.dialect()
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
    } catch (err) {}

    this.loadingJoins(false);
    return joinSuggestions;
  }

  async handleJoinConditions() {
    const suggestJoinConditions = this.parseResult.suggestJoinConditions;
    if (!window.HAS_OPTIMIZER || !suggestJoinConditions) {
      return [];
    }
    this.loadingJoinConditions(true);

    const paths = this.tableIdentifierChainsToPaths(suggestJoinConditions.tables);
    if (!paths.length) {
      return [];
    }

    const joinConditionSuggestions = [];

    try {
      const multiTableEntry = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            connector: this.snippet.connector(),
            paths: paths
          })
          .done(resolve)
          .fail(reject);
      });

      const topJoins = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const topJoinsDeferred = multiTableEntry.getTopJoins({
          silenceErrors: true,
          cancellable: true,
          connector: this.snippet.connector()
        });
        this.cancellablePromises.push(topJoinsDeferred);
        topJoinsDeferred.done(resolve).fail(reject);
      });

      let totalCount = 0;
      if (topJoins.values) {
        topJoins.values.forEach(value => {
          if (value.joinCols.length > 0) {
            let suggestionString = suggestJoinConditions.prependOn
              ? this.parseResult.lowerCase
                ? 'on '
                : 'ON '
              : '';
            let first = true;
            value.joinCols.forEach(joinColPair => {
              if (!first) {
                suggestionString += this.parseResult.lowerCase ? ' and ' : ' AND ';
              }
              suggestionString +=
                this.convertOptimizerQualifiedIdentifier(
                  joinColPair.columns[0],
                  suggestJoinConditions.tables
                ) +
                ' = ' +
                this.convertOptimizerQualifiedIdentifier(
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
    } catch (err) {}

    this.loadingJoinConditions(true);
    return joinConditionSuggestions;
  }

  async handleAggregateFunctions() {
    const suggestAggregateFunctions = this.parseResult.suggestAggregateFunctions;
    if (
      !window.HAS_OPTIMIZER ||
      !suggestAggregateFunctions ||
      !suggestAggregateFunctions.tables.length
    ) {
      return [];
    }

    this.loadingAggregateFunctions(true);

    const paths = this.tableIdentifierChainsToPaths(suggestAggregateFunctions.tables);
    if (!paths.length) {
      return [];
    }

    const aggregateFunctionsSuggestions = [];

    try {
      const multiTableEntry = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            connector: this.snippet.connector(),
            paths: paths
          })
          .done(resolve)
          .fail(reject);
      });

      const topAggs = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const topAggsDeferred = multiTableEntry.getTopAggs({
          silenceErrors: true,
          cancellable: true,
          connector: this.snippet.connector()
        });
        this.cancellablePromises.push(topAggsDeferred);
        topAggsDeferred.done(resolve).fail(reject);
      });

      if (!topAggs.values || !topAggs.values.length) {
        return;
      }

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
              $.map(table.identifierChain, identifier => identifier.name).join('.') + '.',
              'gi'
            ),
            with: replaceWith
          });
        } else if (table.identifierChain.length === 1) {
          substitutions.push({
            replace: new RegExp(
              this.activeDatabase + '.' + table.identifierChain[0].name + '.',
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
      for (let i = 0; i < topAggs.values.length; i++) {
        const value = topAggs.values[i];
        totalCount += value.totalQueryCount;

        let clean = value.aggregateClause;
        substitutions.forEach(substitution => {
          clean = clean.replace(substitution.replace, substitution.with);
        });

        const foundUdfs = await findUdf(this.snippet.connector(), value.aggregateFunction);

        // TODO: Support showing multiple UDFs with the same name but different category in the autocomplete details.
        // For instance, trunc appears both for dates with one description and for numbers with another description.
        value.function = foundUdfs.length ? foundUdfs[0] : undefined;

        aggregateFunctionsSuggestions.push({
          value: clean,
          meta: value.function.returnTypes.join('|'),
          category: CATEGORIES.POPULAR_AGGREGATE,
          weightAdjust: Math.min(value.totalQueryCount, 99),
          popular: ko.observable(true),
          details: value
        });
      }

      aggregateFunctionsSuggestions.forEach(suggestion => {
        suggestion.details.relativePopularity =
          totalCount === 0
            ? suggestion.details.totalQueryCount
            : Math.round((100 * suggestion.details.totalQueryCount) / totalCount);
        suggestion.weightAdjust = suggestion.details.relativePopularity + 1;
      });
    } catch (err) {}

    this.loadingAggregateFunctions(false);
    return aggregateFunctionsSuggestions;
  }

  async handlePopularGroupByOrOrderBy(optimizerAttribute, suggestSpec, columnsPromise) {
    const paths = [];
    suggestSpec.tables.forEach(table => {
      if (table.identifierChain) {
        if (table.identifierChain.length === 1 && table.identifierChain[0].name) {
          paths.push([this.activeDatabase, table.identifierChain[0].name]);
        } else if (
          table.identifierChain.length === 2 &&
          table.identifierChain[0].name &&
          table.identifierChain[1].name
        ) {
          paths.push([table.identifierChain[0].name, table.identifierChain[1].name]);
        }
      }
    });

    try {
      const entries = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const popularityDeferred = dataCatalog
          .getCatalog(this.snippet.connector())
          .loadOptimizerPopularityForTables({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            paths: paths,
            silenceErrors: true,
            cancellable: true
          });
        this.cancellablePromises.push(popularityDeferred);
        popularityDeferred.done(resolve).fail(reject);
      });

      let totalColumnCount = 0;
      const matchedEntries = [];
      const prefix = suggestSpec.prefix
        ? (this.parseResult.lowerCase ? suggestSpec.prefix.toLowerCase() : suggestSpec.prefix) + ' '
        : '';

      entries.forEach(entry => {
        if (entry.optimizerPopularity[optimizerAttribute]) {
          totalColumnCount += entry.optimizerPopularity[optimizerAttribute].columnCount;
          matchedEntries.push(entry);
        }
      });

      if (totalColumnCount > 0) {
        const suggestions = [];
        matchedEntries.forEach(entry => {
          const filterValue = this.createOptimizerIdentifierForColumn(
            entry.optimizerPopularity[optimizerAttribute],
            suggestSpec.tables
          );
          suggestions.push({
            value: prefix + filterValue,
            filterValue: filterValue,
            meta: optimizerAttribute === 'groupByColumn' ? META_I18n.groupBy : META_I18n.orderBy,
            category:
              optimizerAttribute === 'groupByColumn'
                ? CATEGORIES.POPULAR_GROUP_BY
                : CATEGORIES.POPULAR_ORDER_BY,
            weightAdjust: Math.round(
              (100 * entry.optimizerPopularity[optimizerAttribute].columnCount) / totalColumnCount
            ),
            popular: ko.observable(true),
            hasCatalogEntry: false,
            details: entry
          });
        });

        if (prefix === '' && suggestions.length) {
          const columnSuggestions = await columnsPromise;
          const suggestionIndex = {};
          suggestions.forEach(suggestion => {
            suggestionIndex[suggestion.value] = suggestion;
          });
          columnSuggestions.forEach(col => {
            if (suggestionIndex[col.details.name]) {
              col.category = suggestionIndex[col.details.name].category;
            }
          });
          return [];
        }
        return suggestions;
      }
    } catch (err) {}
    return [];
  }

  async handleGroupBys(columnsPromise) {
    const suggestGroupBys = this.parseResult.suggestGroupBys;
    if (!window.HAS_OPTIMIZER || !suggestGroupBys) {
      return [];
    }
    this.loadingGroupBys(true);
    const suggestions = await this.handlePopularGroupByOrOrderBy(
      'groupByColumn',
      suggestGroupBys,
      columnsPromise
    );
    this.loadingGroupBys(false);
    return suggestions;
  }

  async handleOrderBys(columnsDeferred) {
    const suggestOrderBys = this.parseResult.suggestOrderBys;
    if (!window.HAS_OPTIMIZER || !suggestOrderBys) {
      return [];
    }
    this.loadingOrderBys(true);
    const suggestions = await this.handlePopularGroupByOrOrderBy(
      'orderByColumn',
      suggestOrderBys,
      columnsDeferred
    );
    this.loadingOrderBys(false);
    return suggestions;
  }

  async handleFilters() {
    const suggestFilters = this.parseResult.suggestFilters;
    if (!window.HAS_OPTIMIZER || !suggestFilters) {
      return [];
    }
    this.loadingFilters(true);

    const paths = this.tableIdentifierChainsToPaths(suggestFilters.tables);
    if (!paths.length) {
      return [];
    }

    const filterSuggestions = [];

    try {
      const multiTableEntry = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            connector: this.snippet.connector(),
            paths: paths
          })
          .done(resolve)
          .fail(reject);
      });

      const topFilters = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const topFiltersDeferred = multiTableEntry.getTopFilters({
          silenceErrors: true,
          cancellable: true,
          connector: this.snippet.connector()
        });
        this.cancellablePromises.push(topFiltersDeferred);
        topFiltersDeferred.done(resolve).fail(reject);
      });

      let totalCount = 0;
      if (topFilters.values) {
        topFilters.values.forEach(value => {
          if (typeof value.popularValues !== 'undefined' && value.popularValues.length > 0) {
            value.popularValues.forEach(popularValue => {
              if (typeof popularValue.group !== 'undefined') {
                popularValue.group.forEach(grp => {
                  let compVal = suggestFilters.prefix
                    ? (this.parseResult.lowerCase
                        ? suggestFilters.prefix.toLowerCase()
                        : suggestFilters.prefix) + ' '
                    : '';
                  compVal += this.createOptimizerIdentifier(
                    value.tableName,
                    grp.columnName,
                    suggestFilters.tables
                  );
                  if (!/^ /.test(grp.op)) {
                    compVal += ' ';
                  }
                  compVal += this.parseResult.lowerCase ? grp.op.toLowerCase() : grp.op;
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
    } catch (err) {}

    this.loadingFilters(false);
    return filterSuggestions;
  }

  async handlePopularTables(tablesPromise) {
    const suggestTables = this.parseResult.suggestTables;
    if (!window.HAS_OPTIMIZER || !suggestTables) {
      return [];
    }

    this.loadingPopularTables(true);

    const db =
      suggestTables.identifierChain &&
      suggestTables.identifierChain.length === 1 &&
      suggestTables.identifierChain[0].name
        ? suggestTables.identifierChain[0].name
        : this.activeDatabase;

    const entry = await new Promise((resolve, reject) => {
      this.activeRejectables.push(reject);
      dataCatalog
        .getEntry({
          namespace: this.snippet.namespace(),
          compute: this.snippet.compute(),
          connector: this.snippet.connector(),
          path: [db],
          temporaryOnly: this.temporaryOnly
        })
        .done(resolve)
        .fail(reject);
    });

    const childEntries = await new Promise((resolve, reject) => {
      this.activeRejectables.push(reject);
      const popularityDeferred = entry.loadOptimizerPopularityForChildren({
        silenceErrors: true,
        cancellable: true
      });
      this.cancellablePromises.push(popularityDeferred);
      popularityDeferred.done(resolve).fail(reject);
    });

    let totalPopularity = 0;
    const popularityIndex = {};

    childEntries.forEach(childEntry => {
      if (childEntry.optimizerPopularity && childEntry.optimizerPopularity.popularity) {
        popularityIndex[childEntry.name] = true;
        totalPopularity += childEntry.optimizerPopularity.popularity;
      }
    });

    if (totalPopularity > 0 && Object.keys(popularityIndex).length) {
      const tableSuggestions = await tablesPromise;
      tableSuggestions.forEach(suggestion => {
        if (popularityIndex[suggestion.details.name]) {
          suggestion.relativePopularity = Math.round(
            (100 * suggestion.details.optimizerPopularity.popularity) / totalPopularity
          );
          if (suggestion.relativePopularity >= 5) {
            suggestion.popular(true);
          }
          suggestion.weightAdjust = suggestion.relativePopularity;
        }
      });
    }

    this.loadingPopularTables(false);
    return [];
  }

  async handlePopularColumns(columnsPromise) {
    const suggestColumns = this.parseResult.suggestColumns;

    if (!window.HAS_OPTIMIZER || !suggestColumns || !suggestColumns.source) {
      return [];
    }

    let columnSuggestions = [];
    try {
      // The columnsDeferred gets resolved synchronously when the data is cached, if not, assume there are some suggestions.
      columnSuggestions = await columnsPromise;
    } catch (err) {}
    if (!columnSuggestions.length) {
      return [];
    }

    this.loadingPopularColumns(true);

    try {
      const paths = [];
      suggestColumns.tables.forEach(table => {
        if (table.identifierChain && table.identifierChain.length > 0) {
          if (table.identifierChain.length === 1 && table.identifierChain[0].name) {
            paths.push([this.activeDatabase, table.identifierChain[0].name]);
          } else if (
            table.identifierChain.length === 2 &&
            table.identifierChain[0].name &&
            table.identifierChain[1].name
          ) {
            paths.push([table.identifierChain[0].name, table.identifierChain[1].name]);
          }
        }
      });

      const popularEntries = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const popularityDeferred = dataCatalog
          .getCatalog(this.snippet.connector())
          .loadOptimizerPopularityForTables({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            paths: paths,
            silenceErrors: true,
            cancellable: true
          });
        this.cancellablePromises.push(popularityDeferred);
        popularityDeferred.done(resolve).fail(reject);
      });

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
        if (popularEntry.optimizerPopularity && popularEntry.optimizerPopularity[valueAttribute]) {
          popularityIndex[popularEntry.getQualifiedPath()] = true;
        }
      });

      if (!valueAttribute || Object.keys(popularityIndex).length === 0) {
        return [];
      }

      let totalColumnCount = 0;
      const matchedSuggestions = [];
      columnSuggestions.forEach(suggestion => {
        if (suggestion.hasCatalogEntry && popularityIndex[suggestion.details.getQualifiedPath()]) {
          matchedSuggestions.push(suggestion);
          totalColumnCount += suggestion.details.optimizerPopularity[valueAttribute].columnCount;
        }
      });
      if (totalColumnCount > 0) {
        matchedSuggestions.forEach(matchedSuggestion => {
          matchedSuggestion.relativePopularity = Math.round(
            (100 * matchedSuggestion.details.optimizerPopularity[valueAttribute].columnCount) /
              totalColumnCount
          );
          if (matchedSuggestion.relativePopularity >= 5) {
            matchedSuggestion.popular(true);
          }
          matchedSuggestion.weightAdjust = matchedSuggestion.relativePopularity;
        });
      }
    } catch (err) {}

    this.loadingPopularColumns(false);
    return [];
  }

  createOptimizerIdentifier(optimizerTableName, optimizerColumnName, tables) {
    let path = optimizerTableName + '.' + optimizerColumnName.split('.').pop();
    for (let i = 0; i < tables.length; i++) {
      let tablePath = '';
      if (tables[i].identifierChain.length === 2) {
        tablePath = $.map(tables[i].identifierChain, identifier => {
          return identifier.name;
        }).join('.');
      } else if (tables[i].identifierChain.length === 1) {
        tablePath = this.activeDatabase + '.' + tables[i].identifierChain[0].name;
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

  createOptimizerIdentifierForColumn(optimizerColumn, tables) {
    for (let i = 0; i < tables.length; i++) {
      if (
        optimizerColumn.dbName &&
        (optimizerColumn.dbName !== this.activeDatabase ||
          optimizerColumn.dbName !== tables[i].identifierChain[0].name)
      ) {
        continue;
      }
      if (
        optimizerColumn.tableName &&
        hueUtils.equalIgnoreCase(
          optimizerColumn.tableName,
          tables[i].identifierChain[tables[i].identifierChain.length - 1].name
        ) &&
        tables[i].alias
      ) {
        return tables[i].alias + '.' + optimizerColumn.columnName;
      }
    }

    if (optimizerColumn.dbName && optimizerColumn.dbName !== this.activeDatabase) {
      return (
        optimizerColumn.dbName + '.' + optimizerColumn.tableName + '.' + optimizerColumn.columnName
      );
    }
    if (tables.length > 1) {
      return optimizerColumn.tableName + '.' + optimizerColumn.columnName;
    }
    return optimizerColumn.columnName;
  }

  convertOptimizerQualifiedIdentifier(qualifiedIdentifier, tables, type) {
    const aliases = [];
    let tablesHasDefaultDatabase = false;
    tables.forEach(table => {
      tablesHasDefaultDatabase =
        tablesHasDefaultDatabase ||
        hueUtils.equalIgnoreCase(
          table.identifierChain[0].name.toLowerCase(),
          this.activeDatabase.toLowerCase()
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
          .indexOf(this.activeDatabase.toLowerCase() + '.' + aliases[i].qualifiedName) === 0
      ) {
        return (
          aliases[i].alias +
          qualifiedIdentifier.substring(
            (this.activeDatabase + '.' + aliases[i].qualifiedName).length
          )
        );
      }
    }

    if (
      qualifiedIdentifier.toLowerCase().indexOf(this.activeDatabase.toLowerCase()) === 0 &&
      !tablesHasDefaultDatabase
    ) {
      return qualifiedIdentifier.substring(this.activeDatabase.length + 1);
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
  async fetchFieldForIdentifierChain(originalIdentifierChain) {
    const path = [];

    for (let i = 0; i < originalIdentifierChain.length; i++) {
      if (originalIdentifierChain[i].name && !originalIdentifierChain[i].subQuery) {
        path.push(originalIdentifierChain[i].name);
      } else {
        return;
      }
    }

    const fetchFieldRecursive = async (remainingPath, fetchedPath) => {
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

      const catalogEntry = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        dataCatalog
          .getEntry({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            connector: this.snippet.connector(),
            path: fetchedPath,
            temporaryOnly: this.temporaryOnly
          })
          .done(resolve)
          .fail(reject);
      });

      const sourceMeta = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const sourceMetaDeferred = catalogEntry.getSourceMeta({
          silenceErrors: true,
          cancellable: true
        });
        this.cancellablePromises.push(sourceMetaDeferred);
        sourceMetaDeferred.done(resolve).fail(reject);
      });

      if (
        this.dialect() === DIALECT.hive &&
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
        return await fetchFieldRecursive(remainingPath, fetchedPath);
      } else {
        return catalogEntry;
      }
    };

    // For Impala the first parts of the identifier chain could be either database or table, either:
    // SELECT | FROM database.table -or- SELECT | FROM table.column

    // For Hive it could be either:
    // SELECT col.struct FROM db.tbl -or- SELECT col.struct FROM tbl
    if (path.length > 1 && (this.dialect() === DIALECT.impala || this.dialect() === DIALECT.hive)) {
      const catalogEntry = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        dataCatalog
          .getEntry({
            namespace: this.snippet.namespace(),
            compute: this.snippet.compute(),
            connector: this.snippet.connector(),
            path: [],
            temporaryOnly: this.temporaryOnly
          })
          .done(resolve)
          .fail(reject);
      });

      const databaseEntries = await new Promise((resolve, reject) => {
        this.activeRejectables.push(reject);
        const childrenDeferred = catalogEntry.getChildren({
          silenceErrors: true,
          cancellable: true
        });
        this.cancellablePromises.push(childrenDeferred);
        childrenDeferred.done(resolve).fail(reject);
      });

      const firstIsDb = databaseEntries.some(dbEntry =>
        hueUtils.equalIgnoreCase(dbEntry.name, path[0])
      );
      if (!firstIsDb) {
        path.unshift(this.activeDatabase);
      }
    } else if (path.length <= 1) {
      path.unshift(this.activeDatabase);
    }
    return await fetchFieldRecursive(path);
  }
}

export default AutocompleteResults;
