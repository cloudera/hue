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

import { Ace } from 'ext/ace';

import AceAnchoredRange from './AceAnchoredRange';
import { ACTIVE_STATEMENT_CHANGED_EVENT } from './AceLocationHandler';
import { EXECUTABLE_UPDATED_EVENT } from 'apps/editor/execution/executable';
import Executor from 'apps/editor/execution/executor';
import SqlExecutable from 'apps/editor/execution/sqlExecutable';
import SubscriptionTracker, { Disposable } from 'components/utils/SubscriptionTracker';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';

const LINE_BREAK_REGEX = /(\r\n)|(\n)|(\r)/g;
const LEADING_WHITE_SPACE_REGEX = /^\s+/;

const ACTIVE_CSS = 'ace-active-gutter-decoration';
const COMPLETED_CSS = 'ace-completed-gutter-decoration';
const EXECUTING_CSS = 'ace-executing-gutter-decoration';
const FAILED_CSS = 'ace-failed-gutter-decoration';
const FAILED_MARKER_CSS = 'ace-failed-marker';

const getLeadingEmptyLineCount = (parsedStatement: ParsedSqlStatement): number => {
  let leadingEmptyLineCount = 0;
  const leadingWhiteSpace = parsedStatement.statement.match(LEADING_WHITE_SPACE_REGEX);
  if (leadingWhiteSpace) {
    const lineBreakMatch = leadingWhiteSpace[0].match(LINE_BREAK_REGEX);
    if (lineBreakMatch) {
      leadingEmptyLineCount = lineBreakMatch.length;
    }
  }
  return leadingEmptyLineCount;
};

export default class AceGutterHandler implements Disposable {
  editor: Ace.Editor;
  editorId: string;
  executor: Executor;
  trackedAnchors: Map<string, AceAnchoredRange> = new Map();

  subTracker: SubscriptionTracker = new SubscriptionTracker();

  constructor(options: { editor: Ace.Editor; editorId: string; executor: Executor }) {
    this.editor = options.editor;
    this.editorId = options.editorId;
    this.executor = options.executor;

    const activeStatementAnchor = new AceAnchoredRange(this.editor);
    activeStatementAnchor.setGutterCss(ACTIVE_CSS);

    this.subTracker.subscribe(ACTIVE_STATEMENT_CHANGED_EVENT, statementDetails => {
      if (statementDetails.id !== this.editorId || !statementDetails.activeStatement) {
        return;
      }
      const leadingEmptyLineCount = getLeadingEmptyLineCount(statementDetails.activeStatement);
      activeStatementAnchor.move(statementDetails.activeStatement.location, leadingEmptyLineCount);
    });

    this.subTracker.addDisposable(activeStatementAnchor);

    if (this.executor) {
      this.subTracker.subscribe(EXECUTABLE_UPDATED_EVENT, (executable: SqlExecutable) => {
        if (executable.executor === this.executor) {
          let anchor = this.trackedAnchors.get(executable.id);
          if (!anchor) {
            anchor = new AceAnchoredRange(this.editor);
            this.trackedAnchors.set(executable.id, anchor);
          }

          if (executable.lost) {
            anchor.dispose();
            this.trackedAnchors.delete(executable.id);
            return;
          }

          anchor.removeGutterCss();
          anchor.removeMarkerRowCss();

          const statement = executable.parsedStatement;
          const leadingEmptyLineCount = getLeadingEmptyLineCount(statement);
          anchor.move(statement.location, leadingEmptyLineCount);

          if (executable.isRunning()) {
            anchor.setGutterCss(EXECUTING_CSS);
          } else if (!executable.edited && executable.isSuccess()) {
            anchor.setGutterCss(COMPLETED_CSS);
          } else if (!executable.edited && executable.isFailed()) {
            anchor.setGutterCss(FAILED_CSS);
            if (executable.logs && executable.logs.errors.length) {
              const error = executable.logs.errors[0];
              anchor.setMarkerRowCss(FAILED_MARKER_CSS, error.row - leadingEmptyLineCount - 1);
            }
          }
        }
      });
    }
  }

  dispose(): void {
    this.subTracker.dispose();
  }
}
