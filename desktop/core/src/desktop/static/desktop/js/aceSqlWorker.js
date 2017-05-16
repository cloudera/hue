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

var version = 17;
importScripts('/static/desktop/js/autocomplete/sqlParseSupport.js?version=' + version);
importScripts('/static/desktop/js/autocomplete/sqlStatementsParser.js?version=' + version);
importScripts('/static/desktop/js/autocomplete/sql.js?version=' + version);
importScripts('/static/desktop/js/sqlFunctions.js?version=' + version);

(function () {

  this.throttle = -1;

  this.onmessage = function (msg) {
    if (msg.data.ping) {
      postMessage({ ping: true });
      return;
    }
    clearTimeout(this.throttle);
    this.throttle = setTimeout(function () {
      if (msg.data) {
        var statements = sqlStatementsParser.parse(msg.data.text);
        var locations = [];
        // For now we'll only extract the locations
        statements.forEach(function (statement) {
          locations.push(statement);
          try {
            var sqlParseResult =  sql.parseSql(statement.statement + ' ', '', msg.data.type, false);
            if (sqlParseResult.locations) {
              sqlParseResult.locations.forEach(function (location) {
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
        });
        postMessage({ locations: locations });
      }
    }, 400);
  }
})();