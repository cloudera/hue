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

import { CancellablePromise } from 'api/cancellablePromise';
import DataCatalogEntry from 'catalog/DataCatalogEntry';
import { ParsedSqlStatement } from './sqlStatementsParser';

export interface IdentifierChainEntry {
  name: string;
  cte?: string;
  subQuery?: string;
}

export interface SubQuery {
  alias: string;
  columns: ColumnDetails[];
  subQueries?: SubQuery[];
}

export interface ParsedTable {
  alias?: string;
  identifierChain: IdentifierChainEntry[];
  subQuery?: SubQuery; // TODO: Define
}

export interface ParsedLocation {
  first_line: number;
  first_column: number;
  last_line: number;
  last_column: number;
}

export interface SyntaxError {
  expected: { text: string; distance: number }[];
  expectedStatementEnd?: boolean;
  loc: ParsedLocation;
  text: string;
  ruleId?: string;
}

export interface IdentifierLocation {
  identifier: string;
  type: string;
  alias?: string;
  source?: string;
  location: ParsedLocation;
  function?: string;
  missing?: boolean;
  value?: string;
  active?: boolean;
  tables?: ParsedTable[];
  colRef: boolean | { identifierChain: IdentifierChainEntry[]; tables: ParsedTable[] };
  argumentPosition?: number;
  identifierChain?: IdentifierChainEntry[];
  expression?: { types: string[]; text: string };
  parentLocation?: ParsedLocation;
  path?: string;
  qualified?: boolean;
  resolveCatalogEntry: (options?: {
    cachedOnly?: boolean;
    cancellable?: boolean;
    temporaryOnly?: boolean;
  }) => CancellablePromise<DataCatalogEntry>;
}

export interface StatementDetails {
  selectedStatements: ParsedSqlStatement[];
  precedingStatements: ParsedSqlStatement[];
  activeStatement: ParsedSqlStatement;
  followingStatements: ParsedSqlStatement[];
}

export interface ColumnAliasDetails {
  name: string;
  udfRef?: string;
  types: string[];
}

export interface ColumnDetails {
  type: string;
  alias: string;
  identifierChain: IdentifierChainEntry[];
  subQuery?: string;
}

export interface CommonPopularSuggestion {
  tables: ParsedTable[];
  prefix?: string;
}

export interface AutocompleteParseResult {
  colRef?: {
    identifierChain: IdentifierChainEntry[];
  };
  commonTableExpressions?: {
    alias: string;
    columns: ColumnDetails[];
  }[];
  locations: IdentifierLocation[];
  lowerCase: boolean;
  subQueries: SubQuery[];
  suggestAggregateFunctions?: {
    tables: ParsedTable[];
  };
  suggestAnalyticFunctions?: boolean;
  suggestColRefKeywords?: {
    [type: string]: string[];
  };
  suggestColumnAliases?: ColumnAliasDetails[];
  suggestColumns?: {
    appendBacktick?: boolean;
    identifierChain?: IdentifierChainEntry[];
    source?: string;
    tables: ParsedTable[];
    types?: string[];
    udfRef?: string;
  };
  suggestCommonTableExpressions?: {
    appendBacktick?: boolean;
    name: string;
    prependFrom: boolean;
    prependQuestionMark: boolean;
  }[];
  suggestDatabases?: {
    appendBacktick?: boolean;
    appendDot?: boolean;
    prependFrom?: boolean;
    prependQuestionMark?: boolean;
  };
  suggestFilters?: {
    tables: ParsedTable[];
    prefix?: string;
  };
  suggestFunctions?: {
    types: string[];
    udfRef?: string;
  };
  suggestGroupBys?: CommonPopularSuggestion;
  suggestHdfs?: {
    path: string;
  };
  suggestJoins?: {
    prependJoin?: boolean;
    tables: ParsedTable[];
  };
  suggestJoinConditions?: {
    prependOn?: boolean;
    tables: ParsedTable[];
  };
  suggestIdentifiers?: {
    name: string;
    type: string;
  }[];
  suggestKeyValues?: unknown;
  suggestKeywords?: {
    value: string;
    weight: number;
  }[];
  suggestOrderBys?: CommonPopularSuggestion;
  suggestSetOptions?: boolean;
  suggestTables?: {
    appendBacktick?: boolean;
    identifierChain?: IdentifierChainEntry[];
    onlyTables?: boolean;
    onlyViews?: boolean;
    prependFrom?: boolean;
    prependQuestionMark?: boolean;
  };
  suggestValues?: {
    missingEndQuote?: boolean;
    partialQuote?: boolean;
  };
  udfArgument?: {
    name: string;
    position: number;
  };
  useDatabase?: string;
}

export interface SqlStatementsParser {
  parse(text: string): ParsedSqlStatement[];
}

export interface AutocompleteParser {
  parseSql(beforeCursor: string, afterCursor: string, debug?: boolean): AutocompleteParseResult;
}

export interface SyntaxParser {
  parseSyntax(beforeCursor: string, afterCursor: string): unknown;
}

export interface SqlParserProvider {
  getAutocompleteParser(dialect: string): Promise<AutocompleteParser>;
  getSyntaxParser(dialect: string): Promise<SyntaxParser>;
}
