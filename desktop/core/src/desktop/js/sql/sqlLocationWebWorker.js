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

import 'utils/workerPublicPath';
import '@babel/polyfill';
import sqlParserRepository from 'parse/sql/sqlParserRepository';

const handleStatement = (statement, locations, autocompleteParser, active) => {
  // Statement locations come in the message to the worker and are generally more accurate
  locations.push(statement);
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

let throttle = -1;

const onMessage = msg => {
  if (msg.data.ping) {
    postMessage({ ping: true });
    return;
  }
  clearTimeout(throttle);
  throttle = setTimeout(() => {
    if (msg.data.statementDetails) {
      sqlParserRepository.getAutocompleter(msg.data.type).then(parser => {
        let locations = [];
        const activeStatementLocations = [];
        msg.data.statementDetails.precedingStatements.forEach(statement => {
          handleStatement(statement, locations, msg.data.type, false);
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
        msg.data.statementDetails.followingStatements.forEach(statement => {
          handleStatement(statement, locations, msg.data.type, false);
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

        postMessage({
          id: msg.data.id,
          sourceType: msg.data.type,
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
};

WorkerGlobalScope.onLocationMessage = onMessage;
