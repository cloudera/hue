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

import {
  ColumnDetails,
  CommonTableExpression,
  IdentifierChainEntry,
  ParsedTable
} from 'parse/types';
import { matchesType } from 'sql/reference/typeUtils';
import equalIgnoreCase from 'utils/string/equalIgnoreCase';

export interface AddColumnsContext {
  suggestionTable?: ParsedTable;
  visitedCtes?: Set<string>;
  visibleCtes?: CommonTableExpression[];
}

interface CteSuggestionLike {
  meta?: string;
  details?: unknown;
}

interface CteAutocompleteAdapter<Suggestion extends CteSuggestionLike> {
  dialect: string;
  commonTableExpressions: CommonTableExpression[];
  fetchFieldForIdentifierChain: (
    identifierChain: IdentifierChainEntry[]
  ) => Promise<{ getType: () => string } | undefined>;
  addColumns: (
    table: ParsedTable,
    types: string[],
    columnSuggestions: Suggestion[],
    context: AddColumnsContext
  ) => Promise<void>;
  addColumnSuggestion: (
    column: ColumnDetails,
    table: ParsedTable,
    columnName: string,
    type: string,
    columnSuggestions: Suggestion[]
  ) => Promise<void>;
}

interface AddExpandedCteColumnsOptions {
  resolveColumnRefTypes?: boolean;
  visibleCtes?: CommonTableExpression[];
}

const findCteByAlias = (
  alias: string | undefined,
  commonTableExpressions: CommonTableExpression[] = []
): CommonTableExpression | undefined => {
  if (typeof alias === 'undefined') {
    return;
  }
  for (let index = commonTableExpressions.length - 1; index >= 0; index--) {
    const cte = commonTableExpressions[index];
    if (equalIgnoreCase(cte.alias, alias)) {
      return cte;
    }
  }
};

export const findCteForTable = (
  table: ParsedTable | undefined,
  commonTableExpressions: CommonTableExpression[] = []
): CommonTableExpression | undefined => {
  if (
    typeof table === 'undefined' ||
    typeof table.identifierChain === 'undefined' ||
    table.identifierChain.length !== 1 ||
    (typeof table.identifierChain[0].cte === 'undefined' &&
      typeof table.identifierChain[0].name === 'undefined')
  ) {
    return;
  }
  return findCteByAlias(
    table.identifierChain[0].cte || table.identifierChain[0].name,
    commonTableExpressions
  );
};

export const asCteTable = (table: ParsedTable, cte: CommonTableExpression): ParsedTable => ({
  ...table,
  identifierChain: [{ cte: cte.alias } as IdentifierChainEntry]
});

const getCtesVisibleFromCte = (
  cte: CommonTableExpression,
  commonTableExpressions: CommonTableExpression[]
): CommonTableExpression[] => {
  const cteIndex = commonTableExpressions.indexOf(cte);
  return cteIndex === -1 ? commonTableExpressions : commonTableExpressions.slice(0, cteIndex);
};

const columnTypeMatches = (dialect: string, type: string | undefined, types: string[]): boolean => {
  if (typeof type === 'undefined') {
    return true;
  }
  return (
    equalIgnoreCase(type, 'T') ||
    matchesType(dialect, types, [type.toUpperCase()]) ||
    matchesType(dialect, [type.toUpperCase()], types)
  );
};

const columnTypesRequireSourceExpansion = (types: string[]): boolean =>
  types.length !== 1 || !equalIgnoreCase(types[0], 'T');

const getCteColumnType = async <Suggestion extends CteSuggestionLike>(
  adapter: CteAutocompleteAdapter<Suggestion>,
  column: ColumnDetails,
  resolveColumnRefTypes = false
): Promise<string> => {
  if (typeof column.type !== 'undefined' && column.type !== 'COLREF') {
    return column.type;
  }
  if (
    resolveColumnRefTypes &&
    column.type === 'COLREF' &&
    typeof column.identifierChain !== 'undefined' &&
    column.identifierChain.length > 1
  ) {
    try {
      const entry = await adapter.fetchFieldForIdentifierChain(column.identifierChain);
      if (entry) {
        return entry.getType();
      }
    } catch (err) {}
  }
  return 'T';
};

const addCteColumnSuggestion = async <Suggestion extends CteSuggestionLike>(
  adapter: CteAutocompleteAdapter<Suggestion>,
  column: ColumnDetails,
  table: ParsedTable,
  columnName: string,
  type: string,
  types: string[],
  columnSuggestions: Suggestion[]
): Promise<void> => {
  if (!columnTypeMatches(adapter.dialect, type, types)) {
    return;
  }
  await adapter.addColumnSuggestion(column, table, columnName, type, columnSuggestions);
};

const addCteColumnAliasSuggestions = async <Suggestion extends CteSuggestionLike>(
  adapter: CteAutocompleteAdapter<Suggestion>,
  cte: CommonTableExpression,
  table: ParsedTable,
  types: string[],
  columnSuggestions: Suggestion[],
  sourceSuggestions: Suggestion[]
): Promise<void> => {
  const cteColumns = cte.columns || [];
  const columnAliases = cte.columnAliases || [];
  for (let index = 0; index < columnAliases.length; index++) {
    const sourceSuggestion = sourceSuggestions[index];
    const sourceColumn = (sourceSuggestion?.details || cteColumns[index] || {}) as ColumnDetails;
    const type =
      typeof sourceSuggestion?.meta !== 'undefined'
        ? sourceSuggestion.meta
        : typeof sourceColumn.type !== 'undefined' && sourceColumn.type !== 'COLREF'
          ? sourceColumn.type
          : 'T';
    await addCteColumnSuggestion(
      adapter,
      { ...sourceColumn, alias: columnAliases[index] },
      table,
      columnAliases[index],
      type,
      types,
      columnSuggestions
    );
  }
};

const addExpandedCteColumns = async <Suggestion extends CteSuggestionLike>(
  adapter: CteAutocompleteAdapter<Suggestion>,
  cte: CommonTableExpression,
  suggestionTable: ParsedTable,
  types: string[],
  columnSuggestions: Suggestion[],
  visitedCtes: Set<string>,
  options: AddExpandedCteColumnsOptions = {}
): Promise<void> => {
  for (const column of cte.columns || []) {
    const type = await getCteColumnType(adapter, column, options.resolveColumnRefTypes);
    if (typeof column.alias !== 'undefined') {
      await addCteColumnSuggestion(
        adapter,
        column,
        suggestionTable,
        column.alias,
        type,
        types,
        columnSuggestions
      );
    } else if (typeof column.tables !== 'undefined') {
      for (const cteTable of column.tables) {
        await adapter.addColumns(cteTable, types, columnSuggestions, {
          suggestionTable,
          visitedCtes,
          visibleCtes: options.visibleCtes
        });
      }
    } else if (
      typeof column.identifierChain !== 'undefined' &&
      column.identifierChain.length > 0 &&
      typeof column.identifierChain[column.identifierChain.length - 1].name !== 'undefined'
    ) {
      const columnName = column.identifierChain[column.identifierChain.length - 1].name;
      await addCteColumnSuggestion(
        adapter,
        column,
        suggestionTable,
        columnName,
        type,
        types,
        columnSuggestions
      );
    }
  }
};

export const addCteColumns = async <Suggestion extends CteSuggestionLike>(
  adapter: CteAutocompleteAdapter<Suggestion>,
  table: ParsedTable,
  types: string[],
  columnSuggestions: Suggestion[],
  context: AddColumnsContext = {}
): Promise<void> => {
  const cte = findCteForTable(table, context.visibleCtes || adapter.commonTableExpressions);
  if (!cte || (typeof cte.columns === 'undefined' && typeof cte.columnAliases === 'undefined')) {
    return;
  }
  const cteKey = cte.alias.toLowerCase();
  const visitedCtes = context.visitedCtes || new Set<string>();
  if (visitedCtes.has(cteKey)) {
    return;
  }
  const nestedVisitedCtes = new Set(visitedCtes);
  nestedVisitedCtes.add(cteKey);
  const suggestionTable = context.suggestionTable || asCteTable(table, cte);
  // A CTE body can only reference sibling CTEs declared before it;
  // later siblings remain physical table names here.
  const visibleCtes = getCtesVisibleFromCte(cte, adapter.commonTableExpressions);
  if (typeof cte.columnAliases !== 'undefined') {
    const sourceSuggestions: Suggestion[] = [];
    if (columnTypesRequireSourceExpansion(types)) {
      await addExpandedCteColumns(
        adapter,
        cte,
        suggestionTable,
        ['T'],
        sourceSuggestions,
        nestedVisitedCtes,
        {
          resolveColumnRefTypes: true,
          visibleCtes
        }
      );
    }
    await addCteColumnAliasSuggestions(
      adapter,
      cte,
      suggestionTable,
      types,
      columnSuggestions,
      sourceSuggestions
    );
    return;
  }
  await addExpandedCteColumns(
    adapter,
    cte,
    suggestionTable,
    types,
    columnSuggestions,
    nestedVisitedCtes,
    {
      resolveColumnRefTypes: columnTypesRequireSourceExpansion(types),
      visibleCtes
    }
  );
};
