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

import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import {
  AutocompleteParser,
  IdentifierLocation,
  ParsedLocation,
  SqlParserProvider
} from 'parse/types';

const handleStatement = (
  statement: ParsedSqlStatement,
  locations: IdentifierLocation[],
  autocompleteParser: AutocompleteParser,
  active: boolean
) => {
  // Statement locations come in the message to the worker and are generally more accurate
  locations.push(statement as unknown as IdentifierLocation);
  try {
    const sqlParseResult = autocompleteParser.parseSql(statement.statement + ' ', '');
    if (sqlParseResult.locations) {
      sqlParseResult.locations.forEach(location => {
        location.active = active;
        // Skip statement locations from the sql parser
        if (location.type !== 'statement') {
          if (location.location.first_line === 1) {
            location.location.first_column += statement.location.first_column;
            location.location.last_column += statement.location.first_column;
          }
          location.location.first_line += statement.location.first_line - 1;
          location.location.last_line += statement.location.first_line - 1;
          locations.push(location);
        }
      });
    }
  } catch (error) {}
};

/**
 * This function turns the relative nested location into an absolute location given the statement location.
 */
const toAbsoluteLocation = (statementLocation: ParsedLocation, nestedLocation: ParsedLocation) => {
  if (nestedLocation.first_line === 1) {
    nestedLocation.first_column += statementLocation.first_column;
  }
  if (nestedLocation.last_line === 1) {
    nestedLocation.last_column += statementLocation.first_column;
  }
  const lineAdjust = statementLocation.first_line - 1;
  nestedLocation.first_line += lineAdjust;
  nestedLocation.last_line += lineAdjust;
};

export const attachSyntaxListener = (
  ctx: DedicatedWorkerGlobalScope,
  parserProvider: SqlParserProvider,
  beforeMessage?: (message: MessageEvent) => void
): void => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let throttle: any = -1;

  ctx.addEventListener('message', msg => {
    if (beforeMessage) {
      beforeMessage(msg);
    }
    if (msg.data.ping) {
      ctx.postMessage({ ping: true });
      return;
    }
    clearTimeout(throttle);
    throttle = setTimeout(() => {
      parserProvider.getSyntaxParser(msg.data.connector.dialect).then(parser => {
        const syntaxError = parser.parseSyntax(
          msg.data.beforeCursor,
          msg.data.afterCursor
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ) as any;

        if (syntaxError) {
          toAbsoluteLocation(msg.data.statementLocation, syntaxError.loc);
        }
        ctx.postMessage({
          id: msg.data.id,
          connector: msg.data.connector,
          editorChangeTime: msg.data.editorChangeTime,
          syntaxError: syntaxError,
          statementLocation: msg.data.statementLocation
        });
      });
    }, 400);
  });
};

export const attachLocationListeners = (
  ctx: DedicatedWorkerGlobalScope,
  parserProvider: SqlParserProvider,
  beforeMessage?: (message: MessageEvent) => void
): void => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let throttle: any = -1;

  ctx.addEventListener('message', msg => {
    if (beforeMessage) {
      beforeMessage(msg);
    }
    if (msg.data.ping) {
      ctx.postMessage({ ping: true });
      return;
    }
    clearTimeout(throttle);
    throttle = setTimeout(() => {
      if (msg.data.statementDetails) {
        parserProvider.getAutocompleteParser(msg.data.connector.dialect).then(parser => {
          let locations: IdentifierLocation[] = [];
          const activeStatementLocations: IdentifierLocation[] = [];
          msg.data.statementDetails.precedingStatements.forEach((statement: ParsedSqlStatement) => {
            handleStatement(statement, locations, parser, false);
          });
          if (msg.data.statementDetails.activeStatement) {
            handleStatement(
              msg.data.statementDetails.activeStatement,
              activeStatementLocations,
              parser,
              true
            );
            locations = locations.concat(activeStatementLocations);
          }
          msg.data.statementDetails.followingStatements.forEach((statement: ParsedSqlStatement) => {
            handleStatement(statement, locations, parser, false);
          });

          // Add databases where missing in the table identifier chains
          if (msg.data.defaultDatabase) {
            locations.forEach(location => {
              if (
                location.identifierChain &&
                location.identifierChain.length &&
                location.identifierChain[0].name
              ) {
                if (location.tables) {
                  location.tables.forEach(table => {
                    if (
                      table.identifierChain &&
                      table.identifierChain.length === 1 &&
                      table.identifierChain[0].name
                    ) {
                      table.identifierChain.unshift({ name: msg.data.defaultDatabase });
                    }
                  });
                } else if (location.type === 'table' && location.identifierChain.length === 1) {
                  location.identifierChain.unshift({ name: msg.data.defaultDatabase });
                }
              }
            });
          }

          ctx.postMessage({
            id: msg.data.id,
            connector: msg.data.connector,
            namespace: msg.data.namespace,
            compute: msg.data.compute,
            editorChangeTime: msg.data.statementDetails.editorChangeTime,
            locations: locations,
            activeStatementLocations: activeStatementLocations,
            totalStatementCount: msg.data.statementDetails.totalStatementCount,
            activeStatementIndex: msg.data.statementDetails.activeStatementIndex
          });
        });
      }
    }, 400);
  });
};
