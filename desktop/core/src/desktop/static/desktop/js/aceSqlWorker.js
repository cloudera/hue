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

importScripts('/static/desktop/js/autocomplete/sql.js?version=9');
importScripts('/static/desktop/js/sqlFunctions.js?version=9');

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
        var errors = [];
        var locations = [];
        var lineCount = 0;
        msg.data.text.split(';').forEach(function (statement) {
          var parseResult = sql.parseSql(statement + ' ', '', msg.data.type, false);
          if (parseResult.errors) {
            parseResult.errors.forEach(function (error) {
              if (error.token.indexOf('CURSOR') === -1) {
                error.loc.first_line += lineCount;
                error.loc.last_line += lineCount;
                errors.push(error);
              }
            })
          }
          if (parseResult.locations) {
            parseResult.locations.forEach(function (location) {
              location.location.first_line += lineCount;
              location.location.last_line += lineCount;
              locations.push(location);
            })
          }
          lineCount += statement.split(/\r\n|\r|\n/).length - 1;
        });
        postMessage({ errors: errors, locations: locations });
      }
    }, 400);
  }
})();