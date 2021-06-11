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
  GET_ACTIVE_LOCATIONS_EVENT,
  REFRESH_STATEMENT_LOCATIONS_EVENT
} from '../AceLocationHandler';
import { ActiveStatementChangedEventDetails } from '../types';
import Executor from 'apps/editor/execution/executor';
import { SqlAnalyzerProvider } from 'catalog/analyzer/types';
import SubscriptionTracker, { Disposable } from 'components/utils/SubscriptionTracker';
import { Ace } from 'ext/ace';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { AutocompleteParser, AutocompleteParseResult } from 'parse/types';
import { EditorInterpreter } from 'config/types';
import AutocompleteResults from './AutocompleteResults';
import { SqlReferenceProvider } from 'sql/reference/types';
import huePubSub from 'utils/huePubSub';

interface SqlAutocompleterOptions {
  editorId: string;
  executor: Executor;
  temporaryOnly?: boolean;
  editor: Ace.Editor;
  fixedPrefix?: () => string;
  fixedPostfix?: () => string;
  autocompleteParser: AutocompleteParser;
  sqlReferenceProvider: SqlReferenceProvider;
  sqlAnalyzerProvider: SqlAnalyzerProvider;
}

export default class SqlAutocompleter implements Disposable {
  editor: Ace.Editor;
  executor: Executor;
  fixedPrefix: () => string;
  fixedPostfix: () => string;
  autocompleteParser: AutocompleteParser;
  autocompleteResults: AutocompleteResults;
  editorId: string;

  subTracker = new SubscriptionTracker();
  activeStatement: ParsedSqlStatement | null = null;

  onPartial?: (partial: string) => void;

  constructor({
    editorId,
    executor,
    temporaryOnly = false,
    editor,
    fixedPrefix,
    fixedPostfix,
    autocompleteParser,
    sqlReferenceProvider,
    sqlAnalyzerProvider
  }: SqlAutocompleterOptions) {
    this.editorId = editorId;
    this.editor = editor;
    this.executor = executor;
    this.fixedPrefix = fixedPrefix || (() => '');
    this.fixedPostfix = fixedPostfix || (() => '');
    this.autocompleteParser = autocompleteParser;

    this.autocompleteResults = new AutocompleteResults({
      sqlReferenceProvider,
      sqlAnalyzerProvider,
      executor,
      editor,
      temporaryOnly
    });

    this.subTracker.subscribe(
      ACTIVE_STATEMENT_CHANGED_EVENT,
      (event: ActiveStatementChangedEventDetails) => {
        if (event.id === this.editorId) {
          this.activeStatement = event.activeStatement;
        }
      }
    );
  }

  getDialect(): string {
    return (<EditorInterpreter>this.executor.connector()).dialect;
  }

  async parseActiveStatement(): Promise<AutocompleteParseResult | undefined> {
    if (!this.activeStatement) {
      return;
    }
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

      try {
        return this.autocompleteParser.parseSql(beforeCursor, afterCursor);
      } catch (err) {
        console.warn(err);
      }
    }
  }

  async parseAll(): Promise<AutocompleteParseResult | undefined> {
    try {
      return this.autocompleteParser.parseSql(
        this.editor.getTextBeforeCursor(),
        this.editor.getTextAfterCursor()
      );
    } catch (err) {
      console.warn(err);
    }
  }

  async autocomplete(): Promise<AutocompleteParseResult | undefined> {
    let parseResult;
    try {
      huePubSub.publish(
        GET_ACTIVE_LOCATIONS_EVENT,
        (locations: ActiveStatementChangedEventDetails) => {
          // This could happen in case the user is editing at the borders of the statement and the locations haven't
          // been updated yet, in that case we have to force a location update before parsing
          if (locations.editorChangeTime !== this.editor.lastChangeTime) {
            huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this.editorId);
          }
        }
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

    return parseResult;
  }

  dispose(): void {
    this.subTracker.dispose();
  }
}
