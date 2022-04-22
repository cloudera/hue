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

import { Category, CategoryInfo } from './Category';
import { CancellablePromise } from 'api/cancellablePromise';
import Executor from 'apps/editor/execution/executor';
import { SqlAnalyzer, SqlAnalyzerProvider } from 'catalog/analyzer/types';
import DataCatalogEntry, {
  FieldSample,
  FieldSourceMeta,
  SourceMeta,
  TableSourceMeta
} from 'catalog/DataCatalogEntry';
import { SqlAnalyzerPopularity, SqlAnalyzerPopularitySubType } from 'catalog/dataCatalog';
import MultiTableEntry, {
  TopAggs,
  TopAggValue,
  TopFilters,
  TopFilterValue,
  TopJoins,
  TopJoinValue
} from 'catalog/MultiTableEntry';
import SubscriptionTracker from 'components/utils/SubscriptionTracker';
import { Ace } from 'ext/ace';
import {
  AutocompleteParseResult,
  ColumnAliasDetails,
  ColumnDetails,
  CommonPopularSuggestion,
  IdentifierChainEntry,
  ParsedTable,
  SubQuery
} from 'parse/types';

import apiHelper from 'api/apiHelper';
import dataCatalog from 'catalog/dataCatalog';
import { SetDetails, SqlReferenceProvider, UdfDetails } from 'sql/reference/types';
import { hueWindow } from 'types/types';
import sqlUtils from 'sql/sqlUtils';
import { matchesType } from 'sql/reference/typeUtils';
import { cancelActiveRequest } from 'api/apiUtils';
import { findBrowserConnector, getRootFilePath } from 'config/hueConfig';
import {
  findUdf,
  getArgumentDetailsForUdf,
  getUdfsWithReturnTypes,
  getReturnTypesForUdf
} from 'sql/reference/sqlUdfRepository';
import I18n from 'utils/i18n';
import equalIgnoreCase from 'utils/string/equalIgnoreCase';

interface ColumnReference {
  type: string;
  sample?: FieldSample[][];
}

export interface ColRefKeywordDetails {
  type: string;
}

export interface FileDetails {
  name: string;
  type: string;
}

export interface CommentDetails {
  comment: string;
}

export interface Suggestion {
  value: string;
  filterValue?: string;
  filterWeight?: number;
  details?:
    | DataCatalogEntry
    | ColRefKeywordDetails
    | ColumnAliasDetails
    | SetDetails
    | UdfDetails
    | FileDetails
    | TopJoinValue
    | TopAggValue
    | TopFilterValue
    | FieldSample
    | CommentDetails
    | { name: string };
  matchComment?: boolean;
  matchIndex?: number;
  matchLength?: number;
  hasCatalogEntry?: boolean;
  meta: string;
  relativePopularity?: number;
  category: CategoryInfo;
  table?: ParsedTable;
  popular?: boolean;
  tableName?: string;
  weightAdjust?: number;
  partitionKey?: boolean;
  isColumn?: boolean;
}

const MetaLabels = {
  AggregateFunction: I18n('aggregate'),
  Alias: I18n('alias'),
  CTE: I18n('cte'),
  Database: I18n('database'),
  Dir: I18n('dir'),
  Filter: I18n('filter'),
  GroupBy: I18n('group by'),
  Join: I18n('join'),
  JoinCondition: I18n('condition'),
  Keyword: I18n('keyword'),
  OrderBy: I18n('order by'),
  Sample: I18n('sample'),
  Table: I18n('table'),
  Variable: I18n('variable'),
  View: I18n('view'),
  Virtual: I18n('virtual')
};

const HIVE_DIALECT = 'hive';
const IMPALA_DIALECT = 'impala';
const PHOENIX_DIALECT = 'phoenix';

const HIVE_VIRTUAL_COLUMNS = [
  'BLOCK__OFFSET__INSIDE__FILE',
  'GROUPING__ID',
  'RAW__DATA__SIZE',
  'ROW__ID',
  'ROW__IS__DELETED',
  'ROW__OFFSET__INSIDE__BLOCK'
];

const locateSubQuery = (subQueries: SubQuery[], subQueryName: string): SubQuery | undefined => {
  if (subQueries) {
    return subQueries.find(knownSubQuery => equalIgnoreCase(knownSubQuery.alias, subQueryName));
  }
};

class AutocompleteResults {
  executor: Executor;
  editor: Ace.Editor;
  temporaryOnly: boolean;
  activeDatabase: string;
  sqlReferenceProvider: SqlReferenceProvider;
  sqlAnalyzer?: SqlAnalyzer;

  parseResult!: AutocompleteParseResult;
  subTracker = new SubscriptionTracker();
  onCancelFunctions: (() => void)[] = [];
  lastKnownRequests: JQueryXHR[] = [];
  cancellablePromises: CancellablePromise<unknown>[] = [];

  constructor(options: {
    sqlReferenceProvider: SqlReferenceProvider;
    sqlAnalyzerProvider?: SqlAnalyzerProvider;
    executor: Executor;
    editor: Ace.Editor;
    temporaryOnly: boolean;
  }) {
    this.sqlReferenceProvider = options.sqlReferenceProvider;
    this.sqlAnalyzer = options.sqlAnalyzerProvider?.getSqlAnalyzer(options.executor.connector());
    this.executor = options.executor;
    this.editor = options.editor;
    this.temporaryOnly = options.temporaryOnly;
    this.activeDatabase = this.executor.database();
  }

  dialect(): string {
    return this.executor.connector().dialect || this.executor.connector().type;
  }

  async update(parseResult: AutocompleteParseResult, suggestions: Suggestion[]): Promise<void[]> {
    let cancelFn;
    while ((cancelFn = this.onCancelFunctions.pop())) {
      cancelFn();
    }
    this.activeDatabase = parseResult.useDatabase || this.executor.database();
    this.parseResult = parseResult;

    if (this.parseResult.udfArgument) {
      await this.adjustForUdfArgument();
    }

    const promises: Promise<void>[] = [];

    const trackPromise = (promise: Promise<Suggestion[]>): Promise<Suggestion[]> => {
      const wrapped = new Promise<void>(resolve => {
        this.onCancelFunctions.push(resolve);
        promise
          .then(newSuggestions => {
            if (newSuggestions && newSuggestions.length) {
              suggestions.push(...newSuggestions);
            }
            resolve();
          })
          .catch(resolve);
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

    return Promise.all(promises);
  }

  async adjustForUdfArgument(): Promise<void> {
    const foundArgumentDetails = (await getArgumentDetailsForUdf(
      this.sqlReferenceProvider,
      this.executor.connector(),
      this.parseResult.udfArgument!.name,
      this.parseResult.udfArgument!.position
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
      const keywords: ({ value: string; weight: number } | string)[] = [];
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
   */
  async handleColumnReference(): Promise<ColumnReference> {
    if (!this.parseResult.colRef) {
      return { type: 'T' };
    }

    const foundVarRef = this.parseResult.colRef.identifierChain.some(
      identifier => typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0
    );

    if (!foundVarRef) {
      try {
        const catalogEntry = await this.fetchFieldForIdentifierChain(
          this.parseResult.colRef.identifierChain
        );
        if (catalogEntry) {
          const sourceMeta = await new Promise<SourceMeta>((resolve, reject) => {
            this.onCancelFunctions.push(reject);
            const sourceMetaPromise = catalogEntry.getSourceMeta({
              silenceErrors: true,
              cancellable: true
            });
            this.cancellablePromises.push(sourceMetaPromise);
            sourceMetaPromise.then(resolve).catch(reject);
          });
          if ((<FieldSourceMeta>sourceMeta).type) {
            return {
              type: (<FieldSourceMeta>sourceMeta).type,
              sample: (<FieldSourceMeta>sourceMeta).sample // sourceMeta.sample is used in handleValues.
            };
          }
        }
      } catch (err) {}
    }
    return { type: 'T' };
  }

  async loadDatabases(): Promise<DataCatalogEntry[]> {
    try {
      const entry = await new Promise<DataCatalogEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            path: [],
            temporaryOnly: this.temporaryOnly
          })
          .then(resolve)
          .catch(reject);
      });

      return await new Promise((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const childrenPromise = entry.getChildren({ silenceErrors: true, cancellable: true });
        this.cancellablePromises.push(childrenPromise);
        childrenPromise.then(resolve).catch(reject);
      });
    } catch (err) {
      return [];
    }
  }

  async handleKeywords(): Promise<Suggestion[]> {
    const suggestKeywords = this.parseResult.suggestKeywords;
    if (!suggestKeywords) {
      return [];
    }
    return suggestKeywords.map(keyword => ({
      value: this.parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value,
      meta: MetaLabels.Keyword,
      category: Category.Keyword,
      weightAdjust: keyword.weight,
      popular: false
    }));
  }

  async handleColRefKeywords(colRefPromise: Promise<ColumnReference>): Promise<Suggestion[]> {
    const suggestColRefKeywords = this.parseResult.suggestColRefKeywords;
    if (!suggestColRefKeywords) {
      return [];
    }
    // Wait for the column reference type to be resolved to pick the right keywords
    const colRef = await colRefPromise;
    const colRefKeywordSuggestions: Suggestion[] = [];
    Object.keys(suggestColRefKeywords).forEach(typeForKeywords => {
      if (matchesType(this.dialect(), [typeForKeywords], [colRef.type.toUpperCase()])) {
        suggestColRefKeywords[typeForKeywords].forEach(keyword => {
          colRefKeywordSuggestions.push({
            value: this.parseResult.lowerCase ? keyword.toLowerCase() : keyword,
            meta: MetaLabels.Keyword,
            category: Category.ColRefKeyword,
            popular: false,
            details: {
              type: colRef.type
            }
          });
        });
      }
    });
    return colRefKeywordSuggestions;
  }

  async handleIdentifiers(): Promise<Suggestion[]> {
    const suggestIdentifiers = this.parseResult.suggestIdentifiers;
    if (!suggestIdentifiers) {
      return [];
    }
    return suggestIdentifiers.map(identifier => ({
      value: identifier.name,
      meta: identifier.type,
      category: Category.Identifier,
      popular: false
    }));
  }

  async handleColumnAliases(): Promise<Suggestion[]> {
    const suggestColumnAliases = this.parseResult.suggestColumnAliases;
    if (!suggestColumnAliases) {
      return [];
    }
    const columnAliasSuggestions: Suggestion[] = [];

    for (const columnAlias of suggestColumnAliases) {
      const type = columnAlias.types && columnAlias.types.length === 1 ? columnAlias.types[0] : 'T';
      if (type === 'COLREF') {
        columnAliasSuggestions.push({
          value: columnAlias.name,
          meta: MetaLabels.Alias,
          category: Category.Column,
          popular: false,
          details: columnAlias
        });
      } else if (type === 'UDFREF' && columnAlias.udfRef) {
        try {
          const types = await getReturnTypesForUdf(
            this.sqlReferenceProvider,
            this.executor.connector(),
            columnAlias.udfRef
          );
          const resolvedType = types.length === 1 ? types[0] : 'T';
          columnAliasSuggestions.push({
            value: columnAlias.name,
            meta: resolvedType,
            category: Category.Column,
            popular: false,
            details: columnAlias
          });
        } catch (err) {}
      } else {
        columnAliasSuggestions.push({
          value: columnAlias.name,
          meta: type,
          category: Category.Column,
          popular: false,
          details: columnAlias
        });
      }
    }

    return columnAliasSuggestions;
  }

  async handleCommonTableExpressions(): Promise<Suggestion[]> {
    const suggestCommonTableExpressions = this.parseResult.suggestCommonTableExpressions;
    if (!suggestCommonTableExpressions) {
      return [];
    }
    const commonTableExpressionSuggestions: Suggestion[] = [];
    suggestCommonTableExpressions.forEach(expression => {
      let prefix = expression.prependQuestionMark ? '? ' : '';
      if (expression.prependFrom) {
        prefix += this.parseResult.lowerCase ? 'from ' : 'FROM ';
      }
      commonTableExpressionSuggestions.push({
        value: prefix + expression.name,
        filterValue: expression.name,
        meta: MetaLabels.CTE,
        category: Category.CTE,
        popular: false
      });
    });

    return commonTableExpressionSuggestions;
  }

  async handleOptions(): Promise<Suggestion[]> {
    if (!this.parseResult.suggestSetOptions) {
      return [];
    }
    try {
      const setOptions = await this.sqlReferenceProvider.getSetOptions(
        this.executor.connector().dialect || 'generic'
      );
      return Object.keys(setOptions).map(name => ({
        category: Category.Option,
        value: name,
        meta: '',
        popular: false,
        weightAdjust: 0,
        details: setOptions[name]
      }));
    } catch (err) {
      return [];
    }
  }

  async handleFunctions(colRefPromise: Promise<ColumnReference>): Promise<Suggestion[]> {
    const suggestFunctions = this.parseResult.suggestFunctions;
    if (!suggestFunctions) {
      return [];
    }

    let suggestions: Suggestion[] = [];
    if (
      suggestFunctions.types &&
      (suggestFunctions.types[0] === 'COLREF' || suggestFunctions.types[0] === 'UDFREF')
    ) {
      const getUdfsForTypes = async (types: string[]): Promise<Suggestion[]> => {
        try {
          const functionsToSuggest = await getUdfsWithReturnTypes(
            this.sqlReferenceProvider,
            this.executor.connector(),
            types,
            !!this.parseResult.suggestAggregateFunctions,
            !!this.parseResult.suggestAnalyticFunctions
          );

          const firstType = types[0].toUpperCase();

          const functionSuggestions: Suggestion[] = [];
          functionsToSuggest.map(udf => ({
            category: Category.UDF,
            value: udf.name + '()',
            meta: udf.returnTypes.join('|'),
            weightAdjust:
              firstType !== 'T' && udf.returnTypes.some(otherType => otherType === firstType)
                ? 1
                : 0,
            popular: false,
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
        } else if (suggestFunctions.udfRef) {
          types = await getReturnTypesForUdf(
            this.sqlReferenceProvider,
            this.executor.connector(),
            suggestFunctions.udfRef
          );
        }
      } catch (err) {}
      suggestions = await getUdfsForTypes(types);
    } else {
      const types = suggestFunctions.types || ['T'];

      try {
        const functionsToSuggest = await getUdfsWithReturnTypes(
          this.sqlReferenceProvider,
          this.executor.connector(),
          types,
          !!this.parseResult.suggestAggregateFunctions,
          !!this.parseResult.suggestAnalyticFunctions
        );
        suggestions = functionsToSuggest.map(udf => ({
          category: Category.UDF,
          value: udf.name + '()',
          meta: udf.returnTypes.join('|'),
          weightAdjust:
            types[0].toUpperCase() !== 'T' &&
            udf.returnTypes.some(otherType => otherType === types[0].toUpperCase())
              ? 1
              : 0,
          popular: false,
          details: udf
        }));
      } catch (err) {}
    }

    return suggestions;
  }

  async handleDatabases(databasesPromise: Promise<DataCatalogEntry[]>): Promise<Suggestion[]> {
    const suggestDatabases = this.parseResult.suggestDatabases;
    if (!suggestDatabases) {
      return [];
    }
    const databaseSuggestions: Suggestion[] = [];
    try {
      let prefix = suggestDatabases.prependQuestionMark ? '? ' : '';
      if (suggestDatabases.prependFrom) {
        prefix += this.parseResult.lowerCase ? 'from ' : 'FROM ';
      }

      const catalogEntries = await databasesPromise;

      for (const dbEntry of catalogEntries) {
        const name = dbEntry.name;
        if (name !== '') {
          databaseSuggestions.push({
            value:
              prefix +
              (await sqlUtils.backTickIfNeeded(
                this.executor.connector(),
                name,
                this.sqlReferenceProvider
              )) +
              (suggestDatabases.appendDot ? '.' : ''),
            filterValue: name,
            meta: MetaLabels.Database,
            category: Category.Database,
            popular: false,
            hasCatalogEntry: true,
            details: dbEntry
          });
        }
      }
    } catch (err) {}

    return databaseSuggestions;
  }

  async handleTables(databasesPromise: Promise<DataCatalogEntry[]>): Promise<Suggestion[]> {
    const suggestTables = this.parseResult.suggestTables;
    if (!suggestTables) {
      return [];
    }

    const getTableSuggestions = async (): Promise<Suggestion[]> => {
      let prefix = suggestTables.prependQuestionMark ? '? ' : '';
      if (suggestTables.prependFrom) {
        prefix += this.parseResult.lowerCase ? 'from ' : 'FROM ';
      }

      const database =
        suggestTables.identifierChain && suggestTables.identifierChain.length === 1
          ? suggestTables.identifierChain[0].name
          : this.activeDatabase;

      const tableSuggestions: Suggestion[] = [];

      try {
        const dbEntry = await new Promise<DataCatalogEntry>((resolve, reject) => {
          this.onCancelFunctions.push(reject);
          dataCatalog
            .getEntry({
              namespace: this.executor.namespace(),
              compute: this.executor.compute(),
              connector: this.executor.connector(),
              path: [database],
              temporaryOnly: this.temporaryOnly
            })
            .then(resolve)
            .catch(reject);
        });

        const tableEntries = await new Promise<DataCatalogEntry[]>((resolve, reject) => {
          this.onCancelFunctions.push(reject);
          const childrenPromise = dbEntry.getChildren({ silenceErrors: true, cancellable: true });
          this.cancellablePromises.push(childrenPromise);
          childrenPromise.then(resolve).catch(reject);
        });

        for (const tableEntry of tableEntries) {
          if (
            (suggestTables.onlyTables && !tableEntry.isTable()) ||
            (suggestTables.onlyViews && !tableEntry.isView())
          ) {
            continue;
          }
          const name = tableEntry.name;
          tableSuggestions.push({
            value:
              prefix +
              (await sqlUtils.backTickIfNeeded(
                this.executor.connector(),
                name,
                this.sqlReferenceProvider
              )),
            filterValue: name,
            tableName: name,
            meta: tableEntry.isView() ? MetaLabels.View : MetaLabels.Table,
            category: Category.Table,
            popular: false,
            hasCatalogEntry: true,
            details: tableEntry
          });
        }
      } catch (err) {}

      return tableSuggestions;
    };

    let tableSuggestions: Suggestion[] = [];
    if (
      this.dialect() === IMPALA_DIALECT &&
      suggestTables.identifierChain &&
      suggestTables.identifierChain.length === 1
    ) {
      try {
        const databases = await databasesPromise;
        const foundDb = databases.find(dbEntry =>
          equalIgnoreCase(dbEntry.name, suggestTables.identifierChain![0].name)
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
      this.dialect() === IMPALA_DIALECT &&
      suggestTables.identifierChain &&
      suggestTables.identifierChain.length > 1
    ) {
      this.parseResult.suggestColumns = {
        tables: [{ identifierChain: suggestTables.identifierChain }]
      };
    } else {
      tableSuggestions = await getTableSuggestions();
    }

    return tableSuggestions;
  }

  async handleColumns(
    colRefPromise: Promise<ColumnReference>,
    tablesPromise: Promise<Suggestion[]>
  ): Promise<Suggestion[]> {
    try {
      await tablesPromise;
    } catch (err) {}

    const suggestColumns = this.parseResult.suggestColumns;
    if (!suggestColumns) {
      return [];
    }

    const columnSuggestions: Suggestion[] = [];
    // For multiple tables we need to merge and make sure identifiers are unique
    const columnPromises: Promise<void>[] = [];

    let types = ['T'];
    try {
      if (suggestColumns.types && suggestColumns.types[0] === 'COLREF') {
        const colRef = await colRefPromise;
        types = [colRef.type.toUpperCase()];
      } else if (
        suggestColumns.types &&
        suggestColumns.types[0] === 'UDFREF' &&
        suggestColumns.udfRef
      ) {
        types = await getReturnTypesForUdf(
          this.sqlReferenceProvider,
          this.executor.connector(),
          suggestColumns.udfRef
        );
      }
    } catch (err) {}

    suggestColumns.tables.forEach(table => {
      columnPromises.push(this.addColumns(table, types, columnSuggestions));
    });

    try {
      await Promise.all(columnPromises);
    } catch (err) {}

    AutocompleteResults.mergeColumns(columnSuggestions);

    if (this.dialect() === HIVE_DIALECT && /[^.]$/.test(this.editor.getTextBeforeCursor())) {
      HIVE_VIRTUAL_COLUMNS.forEach(virtualColumn => {
        columnSuggestions.push({
          value: virtualColumn,
          meta: MetaLabels.Virtual,
          category: Category.VirtualColumn,
          popular: false,
          details: { name: virtualColumn }
        });
      });
    }

    return columnSuggestions;
  }

  async addCteColumns(table: ParsedTable, columnSuggestions: Suggestion[]): Promise<void> {
    const commonTableExpressions = this.parseResult.commonTableExpressions;
    if (!commonTableExpressions) {
      return;
    }
    const cte = commonTableExpressions.find(cte =>
      equalIgnoreCase(cte.alias, table.identifierChain[0].cte)
    );
    if (!cte) {
      return;
    }
    for (const column of cte.columns) {
      const type = column.type && column.type !== 'COLREF' ? column.type : 'T';
      if (column.alias) {
        columnSuggestions.push({
          value: await sqlUtils.backTickIfNeeded(
            this.executor.connector(),
            column.alias,
            this.sqlReferenceProvider
          ),
          filterValue: column.alias,
          meta: type,
          category: Category.Column,
          table: table,
          popular: false,
          details: column
        });
      } else if (
        typeof column.identifierChain !== 'undefined' &&
        column.identifierChain.length > 0 &&
        typeof column.identifierChain[column.identifierChain.length - 1].name !== 'undefined'
      ) {
        columnSuggestions.push({
          value: await sqlUtils.backTickIfNeeded(
            this.executor.connector(),
            column.identifierChain[column.identifierChain.length - 1].name,
            this.sqlReferenceProvider
          ),
          filterValue: column.identifierChain[column.identifierChain.length - 1].name,
          meta: type,
          category: Category.Column,
          table: table,
          popular: false,
          details: column
        });
      }
    }
  }

  async addSubQueryColumns(table: ParsedTable, columnSuggestions: Suggestion[]): Promise<void> {
    if (!table.identifierChain.length || !table.identifierChain[0].subQuery) {
      return;
    }
    const foundSubQuery = locateSubQuery(
      this.parseResult.subQueries,
      table.identifierChain[0].subQuery
    );

    const addSubQueryColumnsRecursive = async (subQueryColumns: ColumnDetails[]): Promise<void> => {
      const connector = this.executor.connector();
      for (const column of subQueryColumns) {
        if (column.alias || column.identifierChain) {
          // TODO: Potentially fetch column types for sub-queries, possible performance hit.
          const type =
            typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
          if (column.alias) {
            columnSuggestions.push({
              value: await sqlUtils.backTickIfNeeded(
                connector,
                column.alias,
                this.sqlReferenceProvider
              ),
              filterValue: column.alias,
              meta: type,
              category: Category.Column,
              table: table,
              popular: false,
              details: column
            });
          } else if (column.identifierChain && column.identifierChain.length > 0) {
            columnSuggestions.push({
              value: await sqlUtils.backTickIfNeeded(
                connector,
                column.identifierChain[column.identifierChain.length - 1].name,
                this.sqlReferenceProvider
              ),
              filterValue: column.identifierChain[column.identifierChain.length - 1].name,
              meta: type,
              category: Category.Column,
              table: table,
              popular: false,
              details: column
            });
          }
        } else if (foundSubQuery && column.subQuery && foundSubQuery.subQueries) {
          const foundNestedSubQuery = locateSubQuery(foundSubQuery.subQueries, column.subQuery);
          if (foundNestedSubQuery) {
            await addSubQueryColumnsRecursive(foundNestedSubQuery.columns);
          }
        }
      }
    };
    if (foundSubQuery && foundSubQuery.columns.length > 0) {
      await addSubQueryColumnsRecursive(foundSubQuery.columns);
    }
  }

  async addColumns(
    table: ParsedTable,
    types: string[],
    columnSuggestions: Suggestion[]
  ): Promise<void> {
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
      const addColumnsFromEntry = async (dataCatalogEntry: DataCatalogEntry): Promise<void> => {
        const sourceMeta = (await new Promise<SourceMeta>((resolve, reject) => {
          this.onCancelFunctions.push(reject);
          const sourceMetaPromise = dataCatalogEntry.getSourceMeta({
            silenceErrors: true,
            cancellable: true
          });
          this.cancellablePromises.push(sourceMetaPromise);
          sourceMetaPromise.then(resolve).catch(reject);
        })) as FieldSourceMeta;

        const childEntries = await new Promise<DataCatalogEntry[]>((resolve, reject) => {
          this.onCancelFunctions.push(reject);
          const childrenPromise = dataCatalogEntry.getChildren({
            silenceErrors: true,
            cancellable: true
          });
          this.cancellablePromises.push(childrenPromise);
          childrenPromise.then(resolve).catch(reject);
        });

        for (const childEntry of childEntries) {
          let name = await sqlUtils.backTickIfNeeded(
            this.executor.connector(),
            childEntry.name,
            this.sqlReferenceProvider
          );
          if (this.dialect() === HIVE_DIALECT && (childEntry.isArray() || childEntry.isMap())) {
            name += '[]';
          }
          if (
            matchesType(this.dialect(), types, [childEntry.getType().toUpperCase()]) ||
            matchesType(this.dialect(), [childEntry.getType().toUpperCase()], types) ||
            childEntry.getType() === 'column' ||
            childEntry.isComplex()
          ) {
            columnSuggestions.push({
              value: name,
              meta: childEntry.getType(),
              table: table,
              category: Category.Column,
              popular: false,
              weightAdjust:
                types[0].toUpperCase() !== 'T' &&
                types.some(type => equalIgnoreCase(type, childEntry.getType()))
                  ? 1
                  : 0,
              hasCatalogEntry: true,
              details: childEntry
            });
          }
        }
        if (
          this.dialect() === HIVE_DIALECT &&
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
          (this.dialect() === IMPALA_DIALECT || this.dialect() === HIVE_DIALECT) &&
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
              category: Category.Column,
              popular: false,
              weightAdjust:
                types[0].toUpperCase() !== 'T' &&
                types.some(type => equalIgnoreCase(type, fieldType))
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
      try {
        const entry = await this.fetchFieldForIdentifierChain(identifierChain);
        if (entry) {
          await addColumnsFromEntry(entry);
        }
      } catch (err) {}
    }
  }

  static mergeColumns(columnSuggestions: Suggestion[]): void {
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
        if (nextTable && nextTable.alias) {
          columnSuggestions[i + 1].value = nextTable.alias + '.' + columnSuggestions[i + 1].value;
        } else if (nextTable && nextTable.identifierChain && nextTable.identifierChain.length) {
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
      if (suggestion.table && suggestion.table.alias) {
        suggestion.value = suggestion.table.alias + '.' + suggestion.value;
      } else if (
        hasDuplicates &&
        suggestion.table &&
        suggestion.table.identifierChain &&
        suggestion.table.identifierChain.length
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

  async handleValues(colRefPromise: Promise<ColumnReference>): Promise<Suggestion[]> {
    const suggestValues = this.parseResult.suggestValues;
    if (!suggestValues) {
      return [];
    }
    const valueSuggestions: Suggestion[] = [];
    const colRefResult = this.parseResult.colRef;
    if (colRefResult && colRefResult.identifierChain) {
      valueSuggestions.push({
        value:
          '${' + colRefResult.identifierChain[colRefResult.identifierChain.length - 1].name + '}',
        meta: MetaLabels.Variable,
        category: Category.Variable,
        popular: false
      });
    }

    const colRef = await colRefPromise;

    if (colRef.sample) {
      const isString = colRef.type === 'string';
      const startQuote = suggestValues.partialQuote ? '' : "'";
      const endQuote =
        typeof suggestValues.missingEndQuote !== 'undefined' && !suggestValues.missingEndQuote
          ? ''
          : suggestValues.partialQuote || "'";
      colRef.sample.forEach(sample => {
        valueSuggestions.push({
          value: isString ? startQuote + sample[0] + endQuote : String(sample[0]),
          meta: MetaLabels.Sample,
          category: Category.Sample,
          popular: false
        });
      });
    }

    return valueSuggestions;
  }

  async handlePaths(): Promise<Suggestion[]> {
    const suggestHdfs = this.parseResult.suggestHdfs;
    if (!suggestHdfs) {
      return [];
    }

    const suggestions: Suggestion[] = [];

    let path = suggestHdfs.path;
    if (path === '') {
      suggestions.push(
        {
          value: 'adl://',
          meta: MetaLabels.Keyword,
          category: Category.Keyword,
          weightAdjust: 0,
          popular: false
        },
        {
          value: 's3a://',
          meta: MetaLabels.Keyword,
          category: Category.Keyword,
          weightAdjust: 0,
          popular: false
        },
        {
          value: 'hdfs://',
          meta: MetaLabels.Keyword,
          category: Category.Keyword,
          weightAdjust: 0,
          popular: false
        },
        {
          value: 'abfs://',
          meta: MetaLabels.Keyword,
          category: Category.Keyword,
          weightAdjust: 0,
          popular: false
        },
        {
          value: '/',
          meta: MetaLabels.Dir,
          category: Category.Files,
          popular: false
        }
      );
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
        const rootPath = connector && getRootFilePath(connector);
        if (rootPath) {
          suggestions.push({
            value: rootPath,
            meta: 'abfs',
            category: Category.Files,
            weightAdjust: 0,
            popular: false
          });
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

    await new Promise<void>(resolve => {
      const apiHelperFn = (<{ [fn: string]: (arg: unknown) => JQueryXHR }>(<unknown>apiHelper))[
        fetchFunction
      ];
      this.lastKnownRequests.push(
        apiHelperFn.bind(apiHelper)({
          pathParts: parts,
          successCallback: (data: { error?: unknown; files: FileDetails[] }) => {
            if (!data.error) {
              data.files.forEach(file => {
                if (file.name !== '..' && file.name !== '.') {
                  let value = path === '' ? '/' + file.name : file.name;
                  if (file.type === 'dir') {
                    value += '/';
                  }
                  suggestions.push({
                    value,
                    meta: file.type,
                    category: Category.Files,
                    popular: false,
                    details: file
                  });
                }
              });
            }
            resolve();
          },
          silenceErrors: true,
          errorCallback: resolve,
          timeout: (<hueWindow>window).AUTOCOMPLETE_TIMEOUT
        })
      );
    });

    return suggestions;
  }

  tableIdentifierChainsToPaths(tables: ParsedTable[]): string[][] {
    const paths: string[][] = [];
    tables.forEach(table => {
      // Could be subquery
      const isTable = table.identifierChain.every(
        identifier => typeof identifier.name !== 'undefined'
      );
      if (isTable) {
        const path = table.identifierChain.map(identifier => identifier.name);
        if (path.length === 1) {
          path.unshift(this.activeDatabase);
        }
        paths.push(path);
      }
    });
    return paths;
  }

  async handleJoins(): Promise<Suggestion[]> {
    const suggestJoins = this.parseResult.suggestJoins;
    if (!(<hueWindow>window).HAS_SQL_ANALYZER || !suggestJoins || !this.sqlAnalyzer) {
      return [];
    }

    const paths = this.tableIdentifierChainsToPaths(suggestJoins.tables);
    if (!paths.length) {
      return [];
    }

    const joinSuggestions: Suggestion[] = [];
    try {
      const multiTableEntry = await new Promise<MultiTableEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            paths: paths
          })
          .then(resolve)
          .catch(reject);
      });

      const topJoins = await new Promise<TopJoins>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const topJoinsPromise = multiTableEntry.getTopJoins({
          cancellable: true,
          silenceErrors: true,
          sqlAnalyzer: this.sqlAnalyzer!
        });
        this.cancellablePromises.push(topJoinsPromise);
        topJoinsPromise.then(resolve).catch(reject);
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

          const existingTables = new Set<string>();
          suggestJoins.tables.forEach(table => {
            existingTables.add(table.identifierChain[table.identifierChain.length - 1].name);
          });

          let joinRequired = false;
          let tablesAdded = false;
          value.tables.forEach(table => {
            const tableParts = table.split('.');
            if (!existingTables.has(tableParts[tableParts.length - 1])) {
              tablesAdded = true;
              const identifier = this.convertSqlAnalyzerQualifiedIdentifier(
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
                this.convertSqlAnalyzerQualifiedIdentifier(
                  joinColPair.columns[0],
                  suggestJoins.tables
                ) +
                ' = ' +
                this.convertSqlAnalyzerQualifiedIdentifier(
                  joinColPair.columns[1],
                  suggestJoins.tables
                );
              first = false;
            });
            totalCount += value.totalQueryCount;
            joinSuggestions.push({
              value: suggestionString,
              meta: MetaLabels.Join,
              category: suggestJoins.prependJoin
                ? Category.PopularJoin
                : Category.PopularActiveJoin,
              popular: true,
              details: value
            });
          }
        });
        joinSuggestions.forEach(suggestion => {
          const details = <TopJoinValue>suggestion.details;
          details.relativePopularity =
            totalCount === 0
              ? details.totalQueryCount
              : Math.round((100 * details.totalQueryCount) / totalCount);
          suggestion.weightAdjust = details.relativePopularity + 1;
        });
      }
    } catch (err) {}

    return joinSuggestions;
  }

  async handleJoinConditions(): Promise<Suggestion[]> {
    const suggestJoinConditions = this.parseResult.suggestJoinConditions;
    if (!(<hueWindow>window).HAS_SQL_ANALYZER || !suggestJoinConditions || !this.sqlAnalyzer) {
      return [];
    }

    const paths = this.tableIdentifierChainsToPaths(suggestJoinConditions.tables);
    if (!paths.length) {
      return [];
    }

    const joinConditionSuggestions: Suggestion[] = [];

    try {
      const multiTableEntry = await new Promise<MultiTableEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            paths: paths
          })
          .then(resolve)
          .catch(reject);
      });

      const topJoins = await new Promise<TopJoins>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const topJoinsPromise = multiTableEntry.getTopJoins({
          cancellable: true,
          silenceErrors: true,
          sqlAnalyzer: this.sqlAnalyzer!
        });
        this.cancellablePromises.push(topJoinsPromise);
        topJoinsPromise.then(resolve).catch(reject);
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
                this.convertSqlAnalyzerQualifiedIdentifier(
                  joinColPair.columns[0],
                  suggestJoinConditions.tables
                ) +
                ' = ' +
                this.convertSqlAnalyzerQualifiedIdentifier(
                  joinColPair.columns[1],
                  suggestJoinConditions.tables
                );
              first = false;
            });
            totalCount += value.totalQueryCount;
            joinConditionSuggestions.push({
              value: suggestionString,
              meta: MetaLabels.JoinCondition,
              category: Category.PopularJoinCondition,
              popular: true,
              details: value
            });
          }
        });
        joinConditionSuggestions.forEach(suggestion => {
          const details = <TopJoinValue>suggestion.details;
          details.relativePopularity =
            totalCount === 0
              ? details.totalQueryCount
              : Math.round((100 * details.totalQueryCount) / totalCount);
          suggestion.weightAdjust = details.relativePopularity + 1;
        });
      }
    } catch (err) {}

    return joinConditionSuggestions;
  }

  async handleAggregateFunctions(): Promise<Suggestion[]> {
    const suggestAggregateFunctions = this.parseResult.suggestAggregateFunctions;
    if (
      !(<hueWindow>window).HAS_SQL_ANALYZER ||
      !suggestAggregateFunctions ||
      !suggestAggregateFunctions.tables.length ||
      !this.sqlAnalyzer
    ) {
      return [];
    }

    const paths = this.tableIdentifierChainsToPaths(suggestAggregateFunctions.tables);
    if (!paths.length) {
      return [];
    }

    const aggregateFunctionsSuggestions: Suggestion[] = [];

    try {
      const multiTableEntry = await new Promise<MultiTableEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            paths: paths
          })
          .then(resolve)
          .catch(reject);
      });

      const topAggs = await new Promise<TopAggs>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const topAggsDeferred = multiTableEntry.getTopAggs({
          cancellable: true,
          silenceErrors: true,
          sqlAnalyzer: this.sqlAnalyzer!
        });
        this.cancellablePromises.push(topAggsDeferred);
        topAggsDeferred.then(resolve).catch(reject);
      });

      if (!topAggs.values || !topAggs.values.length) {
        return [];
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
      const substitutions: { replace: RegExp; with: string }[] = [];
      suggestAggregateFunctions.tables.forEach(table => {
        const replaceWith = table.alias
          ? table.alias + '.'
          : suggestAggregateFunctions.tables.length > 1
          ? table.identifierChain[table.identifierChain.length - 1].name + '.'
          : '';
        if (table.identifierChain.length > 1) {
          substitutions.push({
            replace: new RegExp(
              table.identifierChain.map(identifier => identifier.name).join('.') + '.',
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

        const foundUdfs = await findUdf(
          this.sqlReferenceProvider,
          this.executor.connector(),
          value.aggregateFunction
        );

        // TODO: Support showing multiple UDFs with the same name but different category in the autocomplete details.
        // For instance, trunc appears both for dates with one description and for numbers with another description.
        value.function = foundUdfs.length ? foundUdfs[0] : undefined;

        aggregateFunctionsSuggestions.push({
          value: clean,
          meta: (value.function && value.function.returnTypes.join('|')) || '',
          category: Category.PopularAggregate,
          weightAdjust: Math.min(value.totalQueryCount, 99),
          popular: true,
          details: value
        });
      }

      aggregateFunctionsSuggestions.forEach(suggestion => {
        const details = <TopAggValue>suggestion.details;
        details.relativePopularity =
          totalCount === 0
            ? details.totalQueryCount
            : Math.round((100 * details.totalQueryCount) / totalCount);
        suggestion.weightAdjust = details.relativePopularity + 1;
      });
    } catch (err) {}

    return aggregateFunctionsSuggestions;
  }

  async handlePopularGroupByOrOrderBy(
    sqlAnalyzerAttribute: keyof SqlAnalyzerPopularitySubType,
    suggestSpec: CommonPopularSuggestion,
    columnsPromise: Promise<Suggestion[]>
  ): Promise<Suggestion[]> {
    if (!this.sqlAnalyzer) {
      return [];
    }
    const paths: string[][] = [];
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
      const entries = await new Promise<DataCatalogEntry[]>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const popularityPromise = dataCatalog
          .getCatalog(this.executor.connector())
          .loadSqlAnalyzerPopularityForTables({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            paths,
            sqlAnalyzer: this.sqlAnalyzer!,
            silenceErrors: true,
            cancellable: true
          });
        this.cancellablePromises.push(popularityPromise);
        popularityPromise.then(resolve).catch(reject);
      });

      let totalColumnCount = 0;
      const matchedEntries: DataCatalogEntry[] = [];
      const prefix = suggestSpec.prefix
        ? (this.parseResult.lowerCase ? suggestSpec.prefix.toLowerCase() : suggestSpec.prefix) + ' '
        : '';

      entries.forEach(entry => {
        if (!entry.sqlAnalyzerPopularity) {
          return;
        }
        const popularity = entry.sqlAnalyzerPopularity[sqlAnalyzerAttribute];
        if (popularity) {
          totalColumnCount += popularity.columnCount;
          matchedEntries.push(entry);
        }
      });

      if (totalColumnCount > 0) {
        const suggestions: Suggestion[] = [];
        matchedEntries.forEach(entry => {
          const popularity =
            entry.sqlAnalyzerPopularity && entry.sqlAnalyzerPopularity[sqlAnalyzerAttribute];
          if (!popularity) {
            return;
          }
          const filterValue = this.createSqlAnalyzerIdentifierForColumn(
            popularity,
            suggestSpec.tables
          );
          suggestions.push({
            value: prefix + filterValue,
            filterValue: filterValue,
            meta:
              sqlAnalyzerAttribute === 'groupByColumn' ? MetaLabels.GroupBy : MetaLabels.OrderBy,
            category:
              sqlAnalyzerAttribute === 'groupByColumn'
                ? Category.PopularGroupBy
                : Category.PopularOrderBy,
            weightAdjust: Math.round((100 * popularity.columnCount) / totalColumnCount),
            popular: true,
            hasCatalogEntry: false,
            details: entry
          });
        });

        if (prefix === '' && suggestions.length) {
          const columnSuggestions = await columnsPromise;
          const suggestionIndex: { [value: string]: Suggestion } = {};
          suggestions.forEach(suggestion => {
            suggestionIndex[suggestion.value] = suggestion;
          });
          columnSuggestions.forEach(col => {
            const details = <DataCatalogEntry>col.details;
            if (suggestionIndex[details.name]) {
              col.category = suggestionIndex[details.name].category;
            }
          });
          return [];
        }
        return suggestions;
      }
    } catch (err) {}
    return [];
  }

  async handleGroupBys(columnsPromise: Promise<Suggestion[]>): Promise<Suggestion[]> {
    const suggestGroupBys = this.parseResult.suggestGroupBys;
    if (!(<hueWindow>window).HAS_SQL_ANALYZER || !suggestGroupBys) {
      return [];
    }

    return await this.handlePopularGroupByOrOrderBy(
      'groupByColumn',
      suggestGroupBys,
      columnsPromise
    );
  }

  async handleOrderBys(columnsPromise: Promise<Suggestion[]>): Promise<Suggestion[]> {
    const suggestOrderBys = this.parseResult.suggestOrderBys;
    if (!(<hueWindow>window).HAS_SQL_ANALYZER || !suggestOrderBys) {
      return [];
    }
    return await this.handlePopularGroupByOrOrderBy(
      'orderByColumn',
      suggestOrderBys,
      columnsPromise
    );
  }

  async handleFilters(): Promise<Suggestion[]> {
    const suggestFilters = this.parseResult.suggestFilters;
    if (!(<hueWindow>window).HAS_SQL_ANALYZER || !suggestFilters || !this.sqlAnalyzer) {
      return [];
    }

    const paths = this.tableIdentifierChainsToPaths(suggestFilters.tables);
    if (!paths.length) {
      return [];
    }

    const filterSuggestions: Suggestion[] = [];

    try {
      const multiTableEntry = await new Promise<MultiTableEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getMultiTableEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            paths: paths
          })
          .then(resolve)
          .catch(reject);
      });

      const topFilters = await new Promise<TopFilters>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const topFiltersPromise = multiTableEntry.getTopFilters({
          cancellable: true,
          silenceErrors: true,
          sqlAnalyzer: this.sqlAnalyzer!
        });
        this.cancellablePromises.push(topFiltersPromise);
        topFiltersPromise.then(resolve).catch(reject);
      });

      let totalCount = 0;
      if (topFilters.values) {
        topFilters.values.forEach(value => {
          if (value.popularValues) {
            value.popularValues.forEach(popularValue => {
              if (popularValue.group) {
                popularValue.group.forEach(grp => {
                  let compVal = suggestFilters.prefix
                    ? (this.parseResult.lowerCase
                        ? suggestFilters.prefix.toLowerCase()
                        : suggestFilters.prefix) + ' '
                    : '';
                  compVal += this.createSqlAnalyzerIdentifier(
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
                    meta: MetaLabels.Filter,
                    category: Category.PopularFilter,
                    popular: false,
                    details: popularValue
                  });
                });
              }
            });
          }
        });
      }
      filterSuggestions.forEach(suggestion => {
        const details = <TopFilterValue>suggestion.details;
        details.relativePopularity =
          totalCount === 0 ? details.count : Math.round((100 * details.count) / totalCount);
        suggestion.weightAdjust = details.relativePopularity + 1;
      });
    } catch (err) {}

    return filterSuggestions;
  }

  async handlePopularTables(tablesPromise: Promise<Suggestion[]>): Promise<Suggestion[]> {
    const suggestTables = this.parseResult.suggestTables;
    if (!(<hueWindow>window).HAS_SQL_ANALYZER || !suggestTables || !this.sqlAnalyzer) {
      return [];
    }

    const db =
      suggestTables.identifierChain &&
      suggestTables.identifierChain.length === 1 &&
      suggestTables.identifierChain[0].name
        ? suggestTables.identifierChain[0].name
        : this.activeDatabase;

    try {
      const entry = await new Promise<DataCatalogEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            path: [db],
            temporaryOnly: this.temporaryOnly
          })
          .then(resolve)
          .catch(reject);
      });

      const childEntries = await new Promise<DataCatalogEntry[]>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const popularityPromise = entry.loadSqlAnalyzerPopularityForChildren({
          cancellable: true,
          silenceErrors: true,
          sqlAnalyzer: this.sqlAnalyzer!
        });
        this.cancellablePromises.push(popularityPromise);
        popularityPromise.then(resolve).catch(reject);
      });

      let totalPopularity = 0;
      const popularityIndex = new Set<string>();

      childEntries.forEach(childEntry => {
        if (childEntry.sqlAnalyzerPopularity && childEntry.sqlAnalyzerPopularity.popularity) {
          popularityIndex.add(childEntry.name);
          totalPopularity += <number>childEntry.sqlAnalyzerPopularity.popularity;
        }
      });

      if (totalPopularity > 0 && popularityIndex.size > 0) {
        const tableSuggestions = await tablesPromise;
        tableSuggestions.forEach(suggestion => {
          const details = <DataCatalogEntry>suggestion.details;
          if (popularityIndex.has(details.name)) {
            const popularity =
              (details.sqlAnalyzerPopularity && details.sqlAnalyzerPopularity.popularity) || 0;
            suggestion.relativePopularity = Math.round((100 * popularity) / totalPopularity);
            if (suggestion.relativePopularity >= 5) {
              suggestion.popular = true;
            }
            suggestion.weightAdjust = suggestion.relativePopularity;
          }
        });
      }
    } catch (err) {}

    return [];
  }

  async handlePopularColumns(columnsPromise: Promise<Suggestion[]>): Promise<Suggestion[]> {
    const suggestColumns = this.parseResult.suggestColumns;

    if (
      !(<hueWindow>window).HAS_SQL_ANALYZER ||
      !suggestColumns ||
      !suggestColumns.source ||
      !this.sqlAnalyzer
    ) {
      return [];
    }

    let columnSuggestions: Suggestion[] = [];
    try {
      // The columnsDeferred gets resolved synchronously when the data is cached, if not, assume there are some suggestions.
      columnSuggestions = await columnsPromise;
    } catch (err) {}
    if (!columnSuggestions.length) {
      return [];
    }

    try {
      const paths: string[][] = [];
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

      const popularEntries = await new Promise<DataCatalogEntry[]>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const popularityPromise = dataCatalog
          .getCatalog(this.executor.connector())
          .loadSqlAnalyzerPopularityForTables({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            paths,
            sqlAnalyzer: this.sqlAnalyzer!,
            silenceErrors: true,
            cancellable: true
          });
        this.cancellablePromises.push(popularityPromise);
        popularityPromise.then(resolve).catch(reject);
      });

      let valueAttribute:
        | keyof Pick<
            SqlAnalyzerPopularitySubType,
            'selectColumn' | 'groupByColumn' | 'orderByColumn'
          >
        | undefined;
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

      const popularityIndex = new Set<string>();

      popularEntries.forEach(popularEntry => {
        if (
          valueAttribute &&
          popularEntry.sqlAnalyzerPopularity &&
          popularEntry.sqlAnalyzerPopularity[valueAttribute]
        ) {
          popularityIndex.add(popularEntry.getQualifiedPath());
        }
      });

      if (!valueAttribute || popularityIndex.size === 0) {
        return [];
      }

      let totalColumnCount = 0;
      const matchedSuggestions: Suggestion[] = [];
      columnSuggestions.forEach(suggestion => {
        const details = <DataCatalogEntry>suggestion.details;
        if (!valueAttribute) {
          return;
        }
        const popularity =
          details.sqlAnalyzerPopularity && details.sqlAnalyzerPopularity[valueAttribute];
        if (
          popularity &&
          suggestion.hasCatalogEntry &&
          popularityIndex.has(details.getQualifiedPath())
        ) {
          matchedSuggestions.push(suggestion);
          totalColumnCount += popularity.columnCount;
        }
      });
      if (totalColumnCount > 0) {
        matchedSuggestions.forEach(matchedSuggestion => {
          const details = <DataCatalogEntry>matchedSuggestion.details;
          if (!details.sqlAnalyzerPopularity || !valueAttribute) {
            return;
          }
          const popularity = details.sqlAnalyzerPopularity[valueAttribute];
          if (!popularity) {
            return;
          }
          matchedSuggestion.relativePopularity = Math.round(
            (100 * popularity.columnCount) / totalColumnCount
          );
          if (matchedSuggestion.relativePopularity >= 5) {
            matchedSuggestion.popular = true;
          }
          matchedSuggestion.weightAdjust = matchedSuggestion.relativePopularity;
        });
      }
    } catch (err) {}

    return [];
  }

  createSqlAnalyzerIdentifier(
    sqlAnalyzerTableName: string,
    sqlAnalyzerColumnName: string,
    tables: ParsedTable[]
  ): string {
    let path = sqlAnalyzerTableName + '.' + sqlAnalyzerColumnName.split('.').pop();
    for (let i = 0; i < tables.length; i++) {
      let tablePath = '';
      if (tables[i].identifierChain.length === 2) {
        tablePath = tables[i].identifierChain.map(identifier => identifier.name).join('.');
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

  createSqlAnalyzerIdentifierForColumn(
    sqlAnalyzerColumn: SqlAnalyzerPopularity,
    tables: ParsedTable[]
  ): string {
    for (let i = 0; i < tables.length; i++) {
      if (
        sqlAnalyzerColumn.dbName &&
        (sqlAnalyzerColumn.dbName !== this.activeDatabase ||
          sqlAnalyzerColumn.dbName !== tables[i].identifierChain[0].name)
      ) {
        continue;
      }
      if (
        sqlAnalyzerColumn.tableName &&
        equalIgnoreCase(
          sqlAnalyzerColumn.tableName,
          tables[i].identifierChain[tables[i].identifierChain.length - 1].name
        ) &&
        tables[i].alias
      ) {
        return tables[i].alias + '.' + sqlAnalyzerColumn.columnName;
      }
    }

    if (sqlAnalyzerColumn.dbName && sqlAnalyzerColumn.dbName !== this.activeDatabase) {
      return (
        sqlAnalyzerColumn.dbName +
        '.' +
        sqlAnalyzerColumn.tableName +
        '.' +
        sqlAnalyzerColumn.columnName
      );
    }
    if (tables.length > 1) {
      return sqlAnalyzerColumn.tableName + '.' + sqlAnalyzerColumn.columnName;
    }
    return sqlAnalyzerColumn.columnName || '';
  }

  convertSqlAnalyzerQualifiedIdentifier(
    qualifiedIdentifier: string,
    tables: ParsedTable[]
  ): string {
    const aliases: { qualifiedName: string; alias: string }[] = [];
    let tablesHasDefaultDatabase = false;
    tables.forEach(table => {
      tablesHasDefaultDatabase =
        tablesHasDefaultDatabase ||
        equalIgnoreCase(
          table.identifierChain[0].name.toLowerCase(),
          this.activeDatabase.toLowerCase()
        );
      if (table.alias) {
        aliases.push({
          qualifiedName: table.identifierChain
            .map(identifier => identifier.name)
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
    if (this.dialect() === HIVE_DIALECT) {
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
  async fetchFieldForIdentifierChain(
    originalIdentifierChain: IdentifierChainEntry[]
  ): Promise<DataCatalogEntry | undefined> {
    const path: string[] = [];

    for (let i = 0; i < originalIdentifierChain.length; i++) {
      if (originalIdentifierChain[i].name && !originalIdentifierChain[i].subQuery) {
        path.push(originalIdentifierChain[i].name);
      } else {
        return;
      }
    }

    const fetchFieldRecursive = async (
      remainingPath: string[],
      fetchedPath?: string[]
    ): Promise<DataCatalogEntry> => {
      fetchedPath = fetchedPath || [];

      if (remainingPath.length > 0) {
        let path = remainingPath.shift();
        // path == '' needed for phoenix empty db
        if (path || (this.dialect() === PHOENIX_DIALECT && path === '')) {
          fetchedPath.push(path);
        }
        // Parser sometimes knows if it's a map or array.
        if (
          remainingPath.length > 0 &&
          (remainingPath[0] === 'item' ||
            (<{ name: string }>(<unknown>remainingPath[0])).name === 'value')
        ) {
          path = remainingPath.shift();
          if (path) {
            fetchedPath.push(path);
          }
        }
      }

      const catalogEntry = await new Promise<DataCatalogEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            path: <string[]>fetchedPath,
            temporaryOnly: this.temporaryOnly
          })
          .then(resolve)
          .catch(reject);
      });

      const sourceMeta = await new Promise<SourceMeta>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const sourceMetaPromise = catalogEntry.getSourceMeta({
          silenceErrors: true,
          cancellable: true
        });
        this.cancellablePromises.push(sourceMetaPromise);
        sourceMetaPromise.then(resolve).catch(reject);
      });

      const extendedColumns = (<TableSourceMeta>sourceMeta).extended_columns;
      if (
        this.dialect() === HIVE_DIALECT &&
        extendedColumns &&
        extendedColumns.length === 1 &&
        /^(?:map|array|struct)/i.test(extendedColumns[0].type)
      ) {
        remainingPath.unshift(extendedColumns[0].name);
      }

      if (remainingPath.length) {
        if (/value|item|key/i.test(remainingPath[0])) {
          const path = remainingPath.shift();
          if (path) {
            fetchedPath.push(path);
          }
        } else if ((<FieldSourceMeta>sourceMeta).type === 'array') {
          fetchedPath.push('item');
        } else if ((<FieldSourceMeta>sourceMeta).type === 'map') {
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
    if (path.length > 1 && (this.dialect() === IMPALA_DIALECT || this.dialect() === HIVE_DIALECT)) {
      const catalogEntry = await new Promise<DataCatalogEntry>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        dataCatalog
          .getEntry({
            namespace: this.executor.namespace(),
            compute: this.executor.compute(),
            connector: this.executor.connector(),
            path: [],
            temporaryOnly: this.temporaryOnly
          })
          .then(resolve)
          .catch(reject);
      });

      const databaseEntries = await new Promise<DataCatalogEntry[]>((resolve, reject) => {
        this.onCancelFunctions.push(reject);
        const childrenPromise = catalogEntry.getChildren({
          silenceErrors: true,
          cancellable: true
        });
        this.cancellablePromises.push(childrenPromise);
        childrenPromise.then(resolve).catch(reject);
      });

      const firstIsDb = databaseEntries.some(dbEntry => equalIgnoreCase(dbEntry.name, path[0]));
      if (!firstIsDb) {
        path.unshift(this.activeDatabase);
      }
    } else if (path.length <= 1) {
      path.unshift(this.activeDatabase);
    }
    return await fetchFieldRecursive(path);
  }

  cancelRequests(): void {
    while (this.lastKnownRequests.length) {
      cancelActiveRequest(this.lastKnownRequests.pop());
    }

    while (this.cancellablePromises.length) {
      const promise = this.cancellablePromises.pop();
      if (promise && promise.cancel) {
        promise.cancel();
      }
    }
  }
}

export default AutocompleteResults;
