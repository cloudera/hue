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
import sqlParserRepository from 'parse/sql/sqlParserRepository';

class SqlAutocompleter {
  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {string} [options.fixedPrefix] - Optional prefix to always use on parse
   * @param {string} [options.fixedPostfix] - Optional postfix to always use on parse
   * @constructor
   */
  constructor(options) {
    this.snippet = options.snippet;
    this.editor = options.editor;
    this.fixedPrefix =
      options.fixedPrefix ||
      function () {
        return '';
      };
    this.fixedPostfix =
      options.fixedPostfix ||
      function () {
        return '';
      };
    this.suggestions = new AutocompleteResults(options);
  }

  async parseActiveStatement() {
    return new Promise((resolve, reject) => {
      if (this.snippet.positionStatement() && this.snippet.positionStatement().location) {
        const activeStatementLocation = this.snippet.positionStatement().location;
        const cursorPosition = this.editor().getCursorPosition();

        if (
          (activeStatementLocation.first_line - 1 < cursorPosition.row ||
            (activeStatementLocation.first_line - 1 === cursorPosition.row &&
              activeStatementLocation.first_column <= cursorPosition.column)) &&
          (activeStatementLocation.last_line - 1 > cursorPosition.row ||
            (activeStatementLocation.last_line - 1 === cursorPosition.row &&
              activeStatementLocation.last_column >= cursorPosition.column))
        ) {
          const beforeCursor =
            this.fixedPrefix() +
            this.editor().session.getTextRange({
              start: {
                row: activeStatementLocation.first_line - 1,
                column: activeStatementLocation.first_column
              },
              end: cursorPosition
            });
          const afterCursor =
            this.editor().session.getTextRange({
              start: cursorPosition,
              end: {
                row: activeStatementLocation.last_line - 1,
                column: activeStatementLocation.last_column
              }
            }) + this.fixedPostfix();
          sqlParserRepository
            .getAutocompleter(this.snippet.dialect())
            .then(autocompleteParser => {
              resolve(autocompleteParser.parseSql(beforeCursor, afterCursor));
            })
            .catch(err => {
              console.warn(err);
              reject(err);
            });
        } else {
          resolve();
        }
      } else {
        resolve();
      }
    });
  }

  async parseAll() {
    return new Promise((resolve, reject) => {
      sqlParserRepository
        .getAutocompleter(this.snippet.dialect())
        .then(autocompleteParser => {
          resolve(
            autocompleteParser.parseSql(
              this.editor().getTextBeforeCursor(),
              this.editor().getTextAfterCursor()
            )
          );
        })
        .catch(reject);
    });
  }

  async autocomplete() {
    let parseResult;
    try {
      huePubSub.publish(
        'get.active.editor.locations',
        locations => {
          // This could happen in case the user is editing at the borders of the statement and the locations haven't
          // been updated yet, in that case we have to force a location update before parsing
          if (
            this.snippet.ace &&
            this.snippet.ace() &&
            locations &&
            this.snippet.ace().lastChangeTime !== locations.editorChangeTime
          ) {
            huePubSub.publish('editor.refresh.statement.locations', this.snippet.id());
          }
        },
        this.snippet
      );

      parseResult = await this.parseActiveStatement();
    } catch (e) {
      if (typeof console.warn !== 'undefined') {
        console.warn(e);
      }
    }

    // In the unlikely case the statement parser fails we fall back to parsing all of it
    if (!parseResult) {
      try {
        parseResult = await this.parseAll();
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
      if (typeof hueDebug !== 'undefined' && hueDebug.showParseResult) {
        // eslint-disable-next-line no-restricted-syntax
        console.log(parseResult);
      }
      try {
        if (this.lastContextRequest) {
          this.lastContextRequest.dispose();
        }
        this.lastContextRequest = this.snippet
          .whenContextSet()
          .done(() => {
            this.suggestions.update(parseResult);
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
