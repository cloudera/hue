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
  from desktop import conf
%>

var scriptPrefix = '';
% if conf.IS_EMBEDDED.get():
  scriptPrefix = location.href.substring(0, location.href.indexOf('/desktop/workers/'));
% endif

% if conf.DEV.get():
importScripts(scriptPrefix + '${ static('desktop/js/autocomplete/sqlParseSupport.js') }' + '?' + Math.random());
importScripts(scriptPrefix + '${ static('desktop/js/autocomplete/sqlSyntaxParser.js') }' + '?' + Math.random());
% else:
importScripts(scriptPrefix + '${ static('desktop/js/autocomplete/sqlParseSupport.js') }');
importScripts(scriptPrefix + '${ static('desktop/js/autocomplete/sqlSyntaxParser.js') }');
% endif

(function () {

  // TODO: Move to utils and re-use elsewhere
  /**
  * This function turns the relative nested location into an absolute location given the statement location.
  *
  * @param statementLocation
  * @param nestedLocation
  */
  var toAbsoluteLocation = function (statementLocation, nestedLocation) {
    if (nestedLocation.first_line === 1) {
      nestedLocation.first_column += statementLocation.first_column;
    }
    if (nestedLocation.last_line === 1) {
      nestedLocation.last_column += statementLocation.first_column;
    }
    var lineAdjust = statementLocation.first_line - 1;
    nestedLocation.first_line += lineAdjust;
    nestedLocation.last_line += lineAdjust;
  };

  this.throttle = -1;

  this.onmessage = function (msg) {
    if (msg.data.ping) {
      postMessage({ ping: true });
      return;
    }
    clearTimeout(this.throttle);
    this.throttle = setTimeout(function () {
      var syntaxError = sqlSyntaxParser.parseSyntax(msg.data.beforeCursor, msg.data.afterCursor, msg.data.type, false);
      if (syntaxError) {
        toAbsoluteLocation(msg.data.statementLocation, syntaxError.loc);
      }
      postMessage({
        id: msg.data.id,
        editorChangeTime: msg.data.editorChangeTime,
        syntaxError: syntaxError,
        statementLocation: msg.data.statementLocation
      });
    }, 400);
  }
})();