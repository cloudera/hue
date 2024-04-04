/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { LOCATION_TYPES } from 'parse/sql/sqlParseUtils';
import { TableColumnsMetadata } from 'api/apiAIHelper';
import { IdentifierLocation } from 'parse/types';

interface ReplaceItem {
  lineNumber: number;
  toBeReplaced: string;
  replacement: string;
}

const applyReplacements = (sql: string, replacements: Array<ReplaceItem>) => {
  const lines = sql.split('\n');
  replacements.forEach(({ lineNumber, toBeReplaced, replacement }) => {
    lines[lineNumber] = lines[lineNumber].replace(toBeReplaced, replacement);
  });

  return lines.join('\n');
};

const isColumnStringBased = (
  tableName: string,
  columnName: string,
  tableColumnsMetadata: TableColumnsMetadata
): boolean => {
  const table = tableColumnsMetadata.find(table => table.name === tableName);
  const column = table?.columns.find(column => column.name === columnName);
  return (
    column?.name === columnName &&
    (column.type?.includes('char') ||
      column.type?.includes('string') ||
      column.type?.includes('text'))
  );
};

const getQualifiedColumnPrefix = (col: IdentifierLocation) => {
  let prefix = '';
  if (col.qualified && Array.isArray(col.tables)) {
    const parsedTable = col.tables[0];
    const qualifiedPrefix = parsedTable.alias || parsedTable.identifierChain[0].name;
    prefix = `${qualifiedPrefix}.`;
  }
  return prefix;
};

const makeZeroBased = (num: number) => num - 1;

/**
 * This function transforms the SQL query to use case insensitive
 * pattern matching on string based values, i.e.
 *
 * "Select * from table1 where col1 = 'value';"
 *
 * is transformed into:
 *
 * "Select * from table1 where LOWER(col1) LIKE LOWER('%value%');"
 */
export const transformToCaseInsensitivePatternMatching = async ({
  sql,
  dialect,
  tableColumnsMetadata
}: {
  sql: string;
  dialect: string;
  tableColumnsMetadata: TableColumnsMetadata;
}): Promise<{
  modifiedSql: string | undefined;
}> => {
  const replaceInstructions: Array<ReplaceItem> = [];
  const autocompleteParser = await sqlParserRepository.getAutocompleteParser(dialect);
  const result = autocompleteParser.parseSql(sql, '', true);
  const lines = sql.split('\n');
  const columns = result.locations.filter(loc => loc.type === LOCATION_TYPES.COLUMN);

  columns.forEach(col => {
    const columnName = (col.identifierChain && col.identifierChain[0].name) || '';
    const tableName = Array.isArray(col.tables) ? col.tables[0].identifierChain[0].name : '';

    if (isColumnStringBased(tableName, columnName, tableColumnsMetadata)) {
      const lineNumber = col.location.first_line - 1;
      const line = lines[lineNumber];
      const restAfterColName = line.slice(col.location.last_column - 1).trim();

      if (restAfterColName.startsWith('=')) {
        const doubleQuotedValueRegex = /^\"[^"]*\"/;
        const singleQuotedValueRegex = /^\'[^']*\'/;
        const quotedValueStart = restAfterColName.slice(1).trim();
        const matchedValue = quotedValueStart.startsWith('"')
          ? quotedValueStart.match(doubleQuotedValueRegex)
          : quotedValueStart.match(singleQuotedValueRegex);

        const quotedValue = (matchedValue && matchedValue[0]) || '';

        if (quotedValue) {
          const value = quotedValue.slice(1, -1);
          const prefix = getQualifiedColumnPrefix(col);
          const sliceStart = makeZeroBased(col.location.first_column) - prefix.length;
          const start = line.slice(sliceStart).trim();
          const replacement = `LOWER(${prefix}${columnName}) LIKE LOWER('%${value}%')`;
          const replaceUntilPosition = start.indexOf(quotedValue) + quotedValue.length;
          const toBeReplaced = start.slice(0, replaceUntilPosition);
          replaceInstructions.push({ lineNumber, toBeReplaced, replacement });
        }
      }
    }
  });

  return {
    modifiedSql: replaceInstructions.length
      ? applyReplacements(sql, replaceInstructions)
      : undefined
  };
};
