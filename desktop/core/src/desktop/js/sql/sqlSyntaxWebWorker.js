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

/**
 * This function turns the relative nested location into an absolute location given the statement location.
 *
 * @param statementLocation
 * @param nestedLocation
 */
const toAbsoluteLocation = (statementLocation, nestedLocation) => {
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

let throttle = -1;

const onMessage = msg => {
  if (msg.data.ping) {
    postMessage({ ping: true });
    return;
  }
  clearTimeout(throttle);
  throttle = setTimeout(() => {
    sqlParserRepository.getSyntaxParser(msg.data.type).then(parser => {
      const syntaxError = parser.parseSyntax(msg.data.beforeCursor, msg.data.afterCursor);
      console.log(syntaxError);

      if (syntaxError) {
        toAbsoluteLocation(msg.data.statementLocation, syntaxError.loc);
      }
      postMessage({
        id: msg.data.id,
        editorChangeTime: msg.data.editorChangeTime,
        syntaxError: syntaxError,
        statementLocation: msg.data.statementLocation
      });
    });
  }, 400);
};

WorkerGlobalScope.onSyntaxMessage = onMessage;
