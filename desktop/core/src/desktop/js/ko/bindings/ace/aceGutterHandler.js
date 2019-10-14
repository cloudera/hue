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
import { EXECUTABLE_UPDATED_EVENT } from 'apps/notebook2/execution/executable';
import { ACTIVE_STATEMENT_CHANGED_EVENT } from 'ko/bindings/ace/aceLocationHandler';

// TODO: depends on Ace

const LINE_BREAK_REGEX = /(\r\n)|(\n)|(\r)/g;
const LEADING_WHITE_SPACE_REGEX = /^\s+/;

const ACTIVE_CSS = 'ace-active-gutter-decoration';
const EXECUTING_CSS = 'ace-executing-gutter-decoration';
const COMPLETED_CSS = 'ace-completed-gutter-decoration';

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

const forEachLine = (statement, callback) => {
  const leadingEmptyLineCount = getLeadingEmptyLineCount(statement);
  let line = statement.location.first_line - 1 + leadingEmptyLineCount;
  for (line; line < statement.location.last_line; line++) {
    callback(line);
  }
};

export default class AceGutterHandler {
  constructor(options) {
    this.editor = options.editor;
    this.editorId = options.editorId;
    this.executor = options.executor;

    this.disposals = [];

    const previouslyMarkedActiveLines = [];

    const changedSubscription = huePubSub.subscribe(
      ACTIVE_STATEMENT_CHANGED_EVENT,
      statementDetails => {
        if (statementDetails.id !== this.editorId || !statementDetails.activeStatement) {
          return;
        }

        const session = this.editor.getSession();
        while (previouslyMarkedActiveLines.length) {
          session.removeGutterDecoration(previouslyMarkedActiveLines.shift(), ACTIVE_CSS);
        }

        forEachLine(statementDetails.activeStatement, line => {
          previouslyMarkedActiveLines.push(line);
          session.addGutterDecoration(line, ACTIVE_CSS);
        });
      }
    );

    this.disposals.push(() => {
      changedSubscription.remove();
    });

    if (this.executor) {
      const session = this.editor.getSession();

      const executableSub = huePubSub.subscribe(EXECUTABLE_UPDATED_EVENT, executable => {
        if (executable.executor === this.executor) {
          const statement = executable.parsedStatement;
          forEachLine(statement, line => {
            session.removeGutterDecoration(line, COMPLETED_CSS);
            session.removeGutterDecoration(line, EXECUTING_CSS);
            if (executable.isRunning()) {
              session.addGutterDecoration(line, EXECUTING_CSS);
            } else if (executable.isSuccess()) {
              session.addGutterDecoration(line, COMPLETED_CSS);
            }
          });
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
