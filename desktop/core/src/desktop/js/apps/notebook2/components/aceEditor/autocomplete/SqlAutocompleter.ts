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

import {
  ACTIVE_STATEMENT_CHANGED_EVENT,
  ActiveStatementChangedEvent,
  GET_ACTIVE_LOCATIONS_EVENT,
  REFRESH_STATEMENT_LOCATIONS_EVENT
} from '../AceLocationHandler';
import Executor from 'apps/notebook2/execution/executor';
import SubscriptionTracker, { Disposable } from 'components/utils/SubscriptionTracker';
import { Ace } from 'ext/ace';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { AutocompleteParser, AutocompleteParseResult } from 'parse/types';
import { EditorInterpreter } from 'types/config';
import AutocompleteResults from './AutocompleteResults';
import hueDebug from 'utils/hueDebug';
import huePubSub from 'utils/huePubSub';
import sqlParserRepository from 'parse/sql/sqlParserRepository';

export default class SqlAutocompleter implements Disposable {
  editor: Ace.Editor;
  executor: Executor;
  fixedPrefix: () => string;
  fixedPostfix: () => string;
  autocompleteResults: AutocompleteResults;
  editorId: string;

  subTracker = new SubscriptionTracker();
  activeStatement: ParsedSqlStatement | null = null;

  onPartial?: (partial: string) => void;

  constructor(options: {
    editorId: string;
    executor: Executor;
    temporaryOnly?: boolean;
    editor: Ace.Editor;
    fixedPrefix?: () => string;
    fixedPostfix?: () => string;
  }) {
    this.editorId = options.editorId;
    this.editor = options.editor;
    this.executor = options.executor;
    this.fixedPrefix = options.fixedPrefix || (() => '');
    this.fixedPostfix = options.fixedPrefix || (() => '');

    this.autocompleteResults = new AutocompleteResults({
      executor: options.executor,
      editor: this.editor,
      temporaryOnly: !!options.temporaryOnly
    });

    this.subTracker.subscribe(
      ACTIVE_STATEMENT_CHANGED_EVENT,
      (event: ActiveStatementChangedEvent) => {
        if (event.id === this.editorId) {
          this.activeStatement = event.activeStatement;
        }
      }
    );
  }

  getDialect(): string {
    return (<EditorInterpreter>this.executor.connector()).dialect;
  }

  async parseActiveStatement(): Promise<AutocompleteParseResult> {
    return new Promise((resolve, reject) => {
      if (this.activeStatement) {
        const activeStatementLocation = this.activeStatement.location;
        const cursorPosition = this.editor.getCursorPosition();

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
            this.editor.session.getTextRange({
              start: {
                row: activeStatementLocation.first_line - 1,
                column: activeStatementLocation.first_column
              },
              end: cursorPosition
            });
          const afterCursor =
            this.editor.session.getTextRange({
              start: cursorPosition,
              end: {
                row: activeStatementLocation.last_line - 1,
                column: activeStatementLocation.last_column
              }
            }) + this.fixedPostfix();
          const parserPromise = <Promise<AutocompleteParser>>(
            sqlParserRepository.getAutocompleter(this.getDialect())
          );
          parserPromise
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

  async parseAll(): Promise<AutocompleteParseResult> {
    return new Promise((resolve, reject) => {
      const parserPromise = <Promise<AutocompleteParser>>(
        sqlParserRepository.getAutocompleter(this.getDialect())
      );
      parserPromise
        .then(autocompleteParser => {
          resolve(
            autocompleteParser.parseSql(
              this.editor.getTextBeforeCursor(),
              this.editor.getTextAfterCursor()
            )
          );
        })
        .catch(reject);
    });
  }

  async autocomplete(): Promise<void> {
    let parseResult;
    try {
      huePubSub.publish(GET_ACTIVE_LOCATIONS_EVENT, (locations: ActiveStatementChangedEvent) => {
        // This could happen in case the user is editing at the borders of the statement and the locations haven't
        // been updated yet, in that case we have to force a location update before parsing
        if (locations.editorChangeTime !== this.editor.lastChangeTime) {
          huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this.editorId);
        }
      });

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
        await this.autocompleteResults.update(parseResult);
      } catch (e) {
        if (typeof console.warn !== 'undefined') {
          console.warn(e);
        }
        huePubSub.publish('hue.ace.autocompleter.done');
      }
    }
  }

  dispose(): void {
    this.subTracker.dispose();
  }
}
