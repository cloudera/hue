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

import huePubSub from 'utils/huePubSub';
import { ACTIVE_STATEMENT_CHANGED_EVENT } from 'ko/bindings/ace/aceLocationHandler';
import AceAnchoredRange from 'ko/bindings/ace/aceAnchoredRange';
import { EXECUTABLE_UPDATED_TOPIC } from '../../../apps/editor/execution/events';

// TODO: depends on Ace

const LINE_BREAK_REGEX = /(\r\n)|(\n)|(\r)/g;
const LEADING_WHITE_SPACE_REGEX = /^\s+/;

const ACTIVE_CSS = 'ace-active-gutter-decoration';
const COMPLETED_CSS = 'ace-completed-gutter-decoration';
const EXECUTING_CSS = 'ace-executing-gutter-decoration';
const FAILED_CSS = 'ace-failed-gutter-decoration';
const FAILED_MARKER_CSS = 'ace-failed-marker';

const getLeadingEmptyLineCount = parsedStatement => {
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

export default class AceGutterHandler {
  constructor(options) {
    this.editor = options.editor;
    this.editorId = options.editorId;
    this.executor = options.executor;

    this.disposals = [];

    const activeStatementAnchor = new AceAnchoredRange(this.editor);
    activeStatementAnchor.addGutterCss(ACTIVE_CSS);

    const changedSubscription = huePubSub.subscribe(
      ACTIVE_STATEMENT_CHANGED_EVENT,
      statementDetails => {
        if (statementDetails.id !== this.editorId || !statementDetails.activeStatement) {
          return;
        }
        const leadingEmptyLineCount = getLeadingEmptyLineCount(statementDetails.activeStatement);
        activeStatementAnchor.move(
          statementDetails.activeStatement.location,
          leadingEmptyLineCount
        );
      }
    );

    this.disposals.push(() => {
      changedSubscription.remove();
      activeStatementAnchor.dispose();
    });

    if (this.executor) {
      const executableSub = huePubSub.subscribe(EXECUTABLE_UPDATED_TOPIC, executable => {
        if (executable.executor === this.executor) {
          if (executable.lost) {
            if (executable.observerState.aceAnchor) {
              executable.observerState.aceAnchor.dispose();
              delete executable.observerState.aceAnchor;
            }
            return;
          }

          const statement = executable.parsedStatement;
          if (!executable.observerState.aceAnchor) {
            executable.observerState.aceAnchor = new AceAnchoredRange(this.editor);
          }
          const leadingEmptyLineCount = getLeadingEmptyLineCount(statement);
          executable.observerState.aceAnchor.move(statement.location, leadingEmptyLineCount);
          const anchoredRange = executable.observerState.aceAnchor;
          anchoredRange.removeGutterCss(COMPLETED_CSS);
          anchoredRange.removeGutterCss(EXECUTING_CSS);
          anchoredRange.removeGutterCss(FAILED_CSS);
          anchoredRange.removeMarkerCss(FAILED_MARKER_CSS);

          if (executable.isRunning()) {
            anchoredRange.addGutterCss(EXECUTING_CSS);
          } else if (executable.isSuccess()) {
            anchoredRange.addGutterCss(COMPLETED_CSS);
          } else if (executable.isFailed()) {
            anchoredRange.addMarkerCss(FAILED_MARKER_CSS);
            anchoredRange.addGutterCss(FAILED_CSS);
          }
        }
      });

      this.disposals.push(() => {
        executableSub.remove();
      });
    }
  }

  dispose() {
    while (this.disposals.length) {
      this.disposals.pop()();
    }
  }
}
