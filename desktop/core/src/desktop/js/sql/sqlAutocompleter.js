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

import AutocompleteResults from 'sql/autocompleteResults';
import hueDebug from 'utils/hueDebug';
import huePubSub from 'utils/huePubSub';
import sqlAutocompleteParser from 'parse/sqlAutocompleteParser';

class SqlAutocompleter {
  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {string} [options.fixedPrefix] - Optional prefix to always use on parse
   * @param {string} [options.fixedPostfix] - Optional postfix to always use on parse
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.snippet = options.snippet;
    self.editor = options.editor;
    self.fixedPrefix =
      options.fixedPrefix ||
      function() {
        return '';
      };
    self.fixedPostfix =
      options.fixedPostfix ||
      function() {
        return '';
      };
    self.suggestions = new AutocompleteResults(options);
  }

  parseActiveStatement() {
    const self = this;
    if (self.snippet.positionStatement() && self.snippet.positionStatement().location) {
      const activeStatementLocation = self.snippet.positionStatement().location;
      const cursorPosition = self.editor().getCursorPosition();

      if (
        (activeStatementLocation.first_line - 1 < cursorPosition.row ||
          (activeStatementLocation.first_line - 1 === cursorPosition.row &&
            activeStatementLocation.first_column <= cursorPosition.column)) &&
        (activeStatementLocation.last_line - 1 > cursorPosition.row ||
          (activeStatementLocation.last_line - 1 === cursorPosition.row &&
            activeStatementLocation.last_column >= cursorPosition.column))
      ) {
        const beforeCursor =
          self.fixedPrefix() +
          self.editor().session.getTextRange({
            start: {
              row: activeStatementLocation.first_line - 1,
              column: activeStatementLocation.first_column
            },
            end: cursorPosition
          });
        const afterCursor =
          self.editor().session.getTextRange({
            start: cursorPosition,
            end: {
              row: activeStatementLocation.last_line - 1,
              column: activeStatementLocation.last_column
            }
          }) + self.fixedPostfix();
        return sqlAutocompleteParser.parseSql(
          beforeCursor,
          afterCursor,
          self.snippet.type(),
          false
        );
      }
    }
  }

  autocomplete() {
    const self = this;
    let parseResult;
    try {
      huePubSub.publish(
        'get.active.editor.locations',
        locations => {
          // This could happen in case the user is editing at the borders of the statement and the locations haven't
          // been updated yet, in that case we have to force a location update before parsing
          if (
            self.snippet.ace &&
            self.snippet.ace() &&
            locations &&
            self.snippet.ace().lastChangeTime !== locations.editorChangeTime
          ) {
            huePubSub.publish('editor.refresh.statement.locations', self.snippet);
          }
        },
        self.snippet
      );

      parseResult = self.parseActiveStatement();

      if (typeof hueDebug !== 'undefined' && hueDebug.showParseResult) {
        console.log(parseResult);
      }
    } catch (e) {
      if (typeof console.warn !== 'undefined') {
        console.warn(e);
      }
    }

    // In the unlikely case the statement parser fails we fall back to parsing all of it
    if (!parseResult) {
      try {
        parseResult = sqlAutocompleteParser.parseSql(
          self.editor().getTextBeforeCursor(),
          self.editor().getTextAfterCursor(),
          self.snippet.type(),
          false
        );
      } catch (e) {
        if (typeof console.warn !== 'undefined') {
          console.warn(e);
        }
      }
    }

    if (!parseResult) {
      // This prevents Ace from inserting garbled text in case of exception
      huePubSub.publish('hue.ace.autocompleter.done');
    } else {
      try {
        if (self.lastContextRequest) {
          self.lastContextRequest.dispose();
        }
        self.lastContextRequest = self.snippet
          .whenContextSet()
          .done(() => {
            self.suggestions.update(parseResult);
          })
          .fail(() => {
            huePubSub.publish('hue.ace.autocompleter.done');
          });
      } catch (e) {
        if (typeof console.warn !== 'undefined') {
          console.warn(e);
        }
        huePubSub.publish('hue.ace.autocompleter.done');
      }
    }
  }
}

export default SqlAutocompleter;
