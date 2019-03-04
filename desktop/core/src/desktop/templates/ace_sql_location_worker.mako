## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
  from webpack_loader import utils
%>

% for js_file in utils.get_files('sqlLocationWebWorker', config='WORKERS'):
  importScripts('${ js_file.get('url') }');
% endfor

(function () {

  this.throttle = -1;

  this.handleStatement = function (statement, locations, type, active) {
    // Statement locations come in the message to the worker and are generally more accurate
    locations.push(statement);
    try {
      var sqlParseResult =  WorkerGlobalScope.sqlAutocompleteParser.parseSql(statement.statement + ' ', '', type, false);
      if (sqlParseResult.locations) {
        sqlParseResult.locations.forEach(function (location) {
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
        })
      }
    } catch (error) {}
  };

  this.onmessage = function (msg) {
    if (msg.data.ping) {
      postMessage({ ping: true });
      return;
    }
    clearTimeout(this.throttle);
    this.throttle = setTimeout(function () {
      if (msg.data.statementDetails) {
        var locations = [];
        var activeStatementLocations = [];
        msg.data.statementDetails.precedingStatements.forEach(function (statement) {
          this.handleStatement(statement, locations, msg.data.type, false);
        });
        if (msg.data.statementDetails.activeStatement) {
          this.handleStatement(msg.data.statementDetails.activeStatement, activeStatementLocations, msg.data.type, true);
          locations = locations.concat(activeStatementLocations);
        }
        msg.data.statementDetails.followingStatements.forEach(function (statement) {
          this.handleStatement(statement, locations, msg.data.type, false);
        });

        // Add databases where missing in the table identifier chains
        if (msg.data.defaultDatabase) {
          locations.forEach(function (location) {
            if (location.identifierChain && location.identifierChain.length && location.identifierChain[0].name) {
              if (location.tables) {
                location.tables.forEach(function (table) {
                  if (table.identifierChain && table.identifierChain.length === 1 && table.identifierChain[0].name) {
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
      }
    }, 400);
  }
})();