/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { AutocompleteParser } from 'parse/types';
import huePubSub from 'utils/huePubSub';
import {
  INSERT_AT_CURSOR_EVENT,
  INSERT_AT_POSITION_EVENT
} from '../../../../ko/bindings/ace/ko.aceEditor';
import { getLeadingEmptyLineCount, LINE_BREAK_REGEX } from '../editorUtils';

import { extractLeadingNqlComments } from './PreviewModal/formattingUtils';

import { AiActionModes } from './sharedTypes';

export interface EditorInsertMsg {
  topic: string;
  details: {
    text: string;
    position?: { row: number; column: number };
    location?: {
      first_line: number;
      first_column: number;
      last_line: number;
      last_column: number;
    };
    newCursorPosition?: { row: number; column: number };
  };
}

export const getRowInterval = (
  parsedStatement: ParsedSqlStatement
): { firstRow: number; lastRow: number } => {
  if (!parsedStatement) {
    return { firstRow: 0, lastRow: 0 };
  }
  const { first_line: firstLineInlcudingEmptyLines, last_line: lastLine } =
    parsedStatement?.location || {};
  const firstRow = firstLineInlcudingEmptyLines + getLeadingEmptyLineCount(parsedStatement);
  return { firstRow, lastRow: lastLine };
};

export const convertToOneBased = ({
  row,
  column
}: {
  row: number;
  column: number;
}): { row: number; column: number } => {
  return { row: row + 1, column: column + 1 };
};

const calculateNewCursorPosition = ({
  row,
  sqlToInsert,
  leadingLineBreaks
}: {
  row: number;
  sqlToInsert: string;
  leadingLineBreaks: number;
}) => {
  const trimmedSql = sqlToInsert.trim();
  const matchingLineBreaks = trimmedSql.match(LINE_BREAK_REGEX);
  const lineBreaksInNewSql = matchingLineBreaks ? matchingLineBreaks.length : 0;
  const newRow = row + leadingLineBreaks + lineBreaksInNewSql;

  const lines = trimmedSql.split(LINE_BREAK_REGEX);
  const lastLine = lines[lines.length - 1] || '';
  const newColumn = lastLine.lastIndexOf(';') + 1;
  return { row: newRow, column: newColumn };
};

const insertBeforeOrAfter = ({ activeStatementInEditor, cursorPosition, sqlToInsert }) => {
  const { firstRow: activeStatementFirstRow, lastRow: activeStatementLastRow } =
    getRowInterval(activeStatementInEditor);
  const lastColumn = activeStatementInEditor.location.last_column;

  const cursorIsAboveStatement = cursorPosition.row < activeStatementFirstRow;
  const cursorIsBelowStatement = cursorPosition.row > activeStatementLastRow;
  const shouldInsertAtCursor = cursorIsAboveStatement || cursorIsBelowStatement;

  // We can not insert the row at activeStatementLastRow + 1 since there might
  // not be an empty line after activeStatementLastRow in which case the Editor
  // will insert on the row activeStatementLastRow instead. Therfore we
  // need to use activeStatementLastRow and append line breaks to the text.
  const row = shouldInsertAtCursor ? cursorPosition.row : activeStatementLastRow;
  const column = shouldInsertAtCursor ? cursorPosition.column : lastColumn + 1;
  const leadingLineBreaks = shouldInsertAtCursor ? (cursorPosition.column > 1 ? 2 : 1) : 2;

  const trailingLineBreaks = 2;
  const LINE_BREAK = '\n';
  const text = `${LINE_BREAK.repeat(leadingLineBreaks)}${sqlToInsert}${LINE_BREAK.repeat(
    trailingLineBreaks
  )}`;

  huePubSub.publish(INSERT_AT_POSITION_EVENT, { text, position: { row, column } });

  // Place the cursor at the end of the inserted SQL but before the ;
  const newCursorPosition = calculateNewCursorPosition({ row, sqlToInsert, leadingLineBreaks });
  huePubSub.publish('ace.cursor.move', newCursorPosition);
};

const replaceNql = ({ activeStatementInEditor, sqlToInsert }) => {
  const { firstRow: activeStatementFirstRow, lastRow: activeStatementLastRow } =
    getRowInterval(activeStatementInEditor);

  huePubSub.publish('ace.replace', {
    text: sqlToInsert,
    location: {
      first_line: activeStatementFirstRow,
      first_column: 1,
      last_line: activeStatementLastRow,
      last_column: activeStatementInEditor.location.last_column + 1
    }
  });
};

const replaceActiveStatement = ({ activeStatementInEditor, sqlToInsert }) => {
  const { firstRow, lastRow } = getRowInterval(activeStatementInEditor);
  huePubSub.publish('ace.replace', {
    text: sqlToInsert,
    location: {
      first_line: firstRow,
      first_column: 1,
      last_line: lastRow,
      last_column: activeStatementInEditor.location.last_column + 1
    }
  });

  // Place the cursor at the end of the inserted SQL but before the ;
  const newCursorPosition = calculateNewCursorPosition({
    row: firstRow,
    sqlToInsert,
    leadingLineBreaks: 0
  });
  huePubSub.publish('ace.cursor.move', newCursorPosition);
};

export const prependCommentToSql = (comment: string, sql: string): string => {
  const leadingEmptyLines = getLeadingEmptyLineCount({ statement: sql });
  const leadingLineBreaks = '\n'.repeat(leadingEmptyLines);
  const prependText = comment ? `${leadingLineBreaks}/* ${comment} */\n` : '';

  return prependText ? `${prependText}${sql.trim()}\n` : sql;
};

/**
 * Publishes a huePubSub event to insert generated SQL at the correct position
 * in the editor, depending on the AI action mode and cursor position.
 * Unlike the Editor it assumes all rows and columns in the params are 1-based in
 * order to match the numbering used in the in the parsedStatement from SqlExecutable.
 *
 * Note!
 * This is only tested for editor v1. Some of the publish events are not
 * supported in editor v2 but can be easily added.
 */
export const modifyEditorContents = ({
  activeStatementInEditor,
  sqlToInsert,
  actionMode,
  cursorPosition,
  autocompleteParser
}: {
  activeStatementInEditor: ParsedSqlStatement;
  sqlToInsert: string;
  actionMode?: AiActionModes;
  cursorPosition: { row: number; column: number };
  autocompleteParser: AutocompleteParser;
}): void => {
  const selectedStatement = activeStatementInEditor.statement;

  const parsedActiveStatement = autocompleteParser.parseSql(selectedStatement, '');
  const syntaxErrors = parsedActiveStatement.errors?.length > 0;
  const hasNoValidSql = parsedActiveStatement.locations?.length === 0;
  const leadingNqlComments = extractLeadingNqlComments(selectedStatement);

  const REPLACE_SINGLE_NQL_COMMENT =
    AiActionModes.GENERATE && leadingNqlComments.length > 0 && !syntaxErrors && hasNoValidSql;
  const INSERT_INTO_EMPTY_EDITOR =
    actionMode === AiActionModes.GENERATE && selectedStatement.trim() === '';
  const INSERT_BEFORE_OR_AFTER =
    actionMode === AiActionModes.GENERATE &&
    !REPLACE_SINGLE_NQL_COMMENT &&
    !INSERT_INTO_EMPTY_EDITOR;
  const REPLACE_ACTIVE_STATEMENT = actionMode !== AiActionModes.GENERATE;

  if (REPLACE_SINGLE_NQL_COMMENT) {
    replaceNql({ activeStatementInEditor, sqlToInsert });
  } else if (INSERT_INTO_EMPTY_EDITOR) {
    huePubSub.publish(INSERT_AT_CURSOR_EVENT, {
      text: sqlToInsert
    });
  } else if (INSERT_BEFORE_OR_AFTER) {
    insertBeforeOrAfter({
      activeStatementInEditor,
      cursorPosition,
      sqlToInsert
    });
  } else if (REPLACE_ACTIVE_STATEMENT) {
    replaceActiveStatement({ activeStatementInEditor, sqlToInsert });
  }
};
