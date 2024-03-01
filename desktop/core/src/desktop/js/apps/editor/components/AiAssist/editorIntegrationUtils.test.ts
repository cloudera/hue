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

jest.mock('utils/huePubSub');
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import sqlParserRepository from 'parse/sql/sqlParserRepository';

import huePubSub from 'utils/huePubSub';
import { AiActionModes } from './sharedTypes';

import {
  getRowInterval,
  convertToOneBased,
  prependCommentToSql,
  modifyEditorContents
} from './editorIntegrationUtils';

const PUBSUB_REPLACE = 'ace.replace';
const PUBSUB_INSERT_AT_CURSOR = 'editor.insert.at.cursor';
const PUBSUB_INSERT_AT_POSITION = 'editor.insert.at.position';
const PUBSUB_MOVE_CURSOR = 'ace.cursor.move';

describe('Editor Utility Functions', () => {
  describe('getRowInterval', () => {
    it('returns firstRow and lastRow as 0 for undefined input', () => {
      const result = getRowInterval(undefined);
      expect(result).toEqual({ firstRow: 0, lastRow: 0 });
    });

    it('returns correct row interval for valid parsedStatement', () => {
      // No leading empty lines
      const parsedStatement = {
        statement: 'SELECT * FROM table;',
        location: {
          first_line: 2,
          last_line: 4
        }
      };
      expect(getRowInterval(parsedStatement)).toEqual({ firstRow: 2, lastRow: 4 });

      // With leading empty lines
      expect(
        getRowInterval({
          statement: '\n\nSELECT * FROM table;',
          location: {
            first_line: 2,
            last_line: 6
          }
        })
      ).toEqual({ firstRow: 4, lastRow: 6 });
    });
  });

  describe('convertToOneBased', () => {
    it('converts row and column to 1-based indexing', () => {
      const input = { row: 0, column: 0 };
      const expected = { row: 1, column: 1 };
      expect(convertToOneBased(input)).toEqual(expected);
    });
  });

  describe('prependCommentToSql', () => {
    it('prepends a comment to SQL that has 0 leading line breaks', () => {
      expect(prependCommentToSql('Test Comment', 'SELECT * FROM table;')).toBe(
        '/* Test Comment */\nSELECT * FROM table;\n'
      );
    });

    it('prepends a comment to SQL that has 2 leading line breaks', () => {
      expect(prependCommentToSql('Test Comment', '\n\n SELECT * FROM table;')).toBe(
        '\n\n/* Test Comment */\nSELECT * FROM table;\n'
      );
    });

    it('prepends a comment that has line breaks to SQL that has 1 leading line break ', () => {
      expect(prependCommentToSql('Test\n Comment\n', '\nSELECT * FROM table;')).toBe(
        '\n/* Test\n Comment\n */\nSELECT * FROM table;\n'
      );
    });
  });

  describe('modifyEditorContents', () => {
    let autocompleteParser;

    beforeEach(async () => {
      autocompleteParser = await sqlParserRepository.getAutocompleteParser('hive');
    });

    describe('using generate', () => {
      it('inserts new SQL before active statement when cursor is on leading empty lines', async () => {
        const activeStatementInEditor: ParsedSqlStatement = {
          type: 'statement',
          statement: '\n\n\nselect * \nfrom call_center \nwhere cc_call_center_id = "testid";',
          location: {
            first_line: 3,
            first_column: 17,
            last_line: 8,
            last_column: 35
          },
          firstToken: 'select'
        };
        const sqlToInsert = 'SELECT * FROM users;';
        const cursorPosition = { row: 1, column: 1 };

        modifyEditorContents({
          activeStatementInEditor,
          sqlToInsert,
          actionMode: AiActionModes.GENERATE,
          cursorPosition,
          autocompleteParser
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_INSERT_AT_POSITION, {
          position: { row: 1, column: 1 },
          text: '\nSELECT * FROM users;\n\n'
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_MOVE_CURSOR, {
          row: 2,
          column: 20
        });
      });

      it('inserts new SQL after active statement when cursor is below active statement', () => {
        const activeStatementInEditor = {
          type: 'statement',
          statement: 'select * from call_center where cc_call_center_id = "testid";',
          location: {
            first_line: 1,
            first_column: 0,
            last_line: 1,
            last_column: 60
          },
          firstToken: 'select'
        };
        const sqlToInsert = 'SELECT * FROM users;';
        const cursorPosition = { row: 3, column: 1 };

        modifyEditorContents({
          activeStatementInEditor,
          sqlToInsert,
          actionMode: AiActionModes.GENERATE,
          cursorPosition,
          autocompleteParser
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_INSERT_AT_POSITION, {
          position: { row: 3, column: 1 },
          text: '\nSELECT * FROM users;\n\n'
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_MOVE_CURSOR, {
          row: 2,
          column: 20
        });
      });

      it('inserts new SQL after single line active statement when cursor inside statement', () => {
        const activeStatementInEditor = {
          type: 'statement',
          statement: 'select * from test;',
          location: {
            first_line: 1,
            first_column: 0,
            last_line: 1,
            last_column: 19
          },
          firstToken: 'select'
        };
        const sqlToInsert = 'SELECT * FROM users;';
        const cursorPosition = { row: 1, column: 6 };

        modifyEditorContents({
          activeStatementInEditor,
          sqlToInsert,
          actionMode: AiActionModes.GENERATE,
          cursorPosition,
          autocompleteParser
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_INSERT_AT_POSITION, {
          position: { row: 1, column: 20 },
          text: '\n\nSELECT * FROM users;\n\n'
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_MOVE_CURSOR, {
          row: 3,
          column: 20
        });
      });

      it('inserts new SQL after multiline active statement when cursor inside statement', () => {
        const activeStatementInEditor = {
          type: 'statement',
          statement: 'select *\n from test;',
          location: {
            first_line: 1,
            first_column: 0,
            last_line: 2,
            last_column: 10
          },
          firstToken: 'select'
        };
        const sqlToInsert = 'SELECT * FROM users;';
        const cursorPosition = { row: 1, column: 6 };

        modifyEditorContents({
          activeStatementInEditor,
          sqlToInsert,
          actionMode: AiActionModes.GENERATE,
          cursorPosition,
          autocompleteParser
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_INSERT_AT_POSITION, {
          position: { row: 2, column: 11 },
          text: '\n\nSELECT * FROM users;\n\n'
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_MOVE_CURSOR, {
          row: 4,
          column: 20
        });
      });

      it('replaces active statement when it contains only NQL comment and no valid SQL', () => {
        const activeStatementInEditor = {
          type: 'statement',
          statement: '/* NQL: test prompt */',
          location: {
            first_line: 1,
            first_column: 0,
            last_line: 1,
            last_column: 22
          }
        };
        const sqlToInsert = 'SELECT * FROM users;';
        const cursorPosition = { row: 1, column: 1 };

        modifyEditorContents({
          activeStatementInEditor,
          sqlToInsert,
          actionMode: AiActionModes.GENERATE,
          cursorPosition,
          autocompleteParser
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_REPLACE, {
          location: {
            first_line: 1,
            first_column: 1,
            last_line: 1,
            last_column: 23
          },
          text: 'SELECT * FROM users;'
        });
      });

      it('inserts new SQL in empty editor', async () => {
        const activeStatementInEditor: ParsedSqlStatement = {
          type: 'statement',
          statement: '\n\n',
          location: {
            first_line: 1,
            first_column: 0,
            last_line: 3,
            last_column: 0
          }
        };
        const sqlToInsert = 'SELECT * FROM users;';
        const cursorPosition = { row: 2, column: 1 };

        modifyEditorContents({
          activeStatementInEditor,
          sqlToInsert,
          actionMode: AiActionModes.GENERATE,
          cursorPosition,
          autocompleteParser
        });

        expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_INSERT_AT_CURSOR, {
          text: 'SELECT * FROM users;'
        });
      });
    });

    [AiActionModes.EDIT, AiActionModes.OPTIMIZE, AiActionModes.EXPLAIN, AiActionModes.FIX].forEach(
      aiActionMode => {
        describe(`using ${aiActionMode}`, () => {
          it('replaces single line active statement', () => {
            const activeStatementInEditor = {
              type: 'statement',
              statement: 'Select * from test;',
              location: {
                first_line: 1,
                first_column: 0,
                last_line: 1,
                last_column: 19
              },
              firstToken: 'SELECT'
            };
            const sqlToInsert = 'SELECT * FROM users;';

            // Cursor position is a required parameter for modifyEditorContents
            // but not used when relacing the active statement
            const ignoredCursorPosition = { row: 0, column: 0 };

            modifyEditorContents({
              activeStatementInEditor,
              sqlToInsert,
              actionMode: aiActionMode,
              cursorPosition: ignoredCursorPosition,
              autocompleteParser
            });

            expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_REPLACE, {
              location: {
                first_line: 1,
                first_column: 1,
                last_line: 1,
                last_column: 20
              },
              text: 'SELECT * FROM users;'
            });

            expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_MOVE_CURSOR, {
              row: 1,
              column: 20
            });
          });

          it('replaces active statement that has leading linebreaks', () => {
            const activeStatementInEditor = {
              type: 'statement',
              statement: '\n\n\nSelect * from test;',
              location: {
                first_line: 1,
                first_column: 0,
                last_line: 4,
                last_column: 19
              },
              firstToken: 'SELECT'
            };
            const sqlToInsert = 'SELECT * FROM users;';

            // Cursor position is a required parameter for modifyEditorContents
            // but not used when replacing the active statement
            const ignoredCursorPosition = { row: 0, column: 0 };

            modifyEditorContents({
              activeStatementInEditor,
              sqlToInsert,
              actionMode: aiActionMode,
              cursorPosition: ignoredCursorPosition,
              autocompleteParser
            });

            expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_REPLACE, {
              location: {
                first_line: 4,
                first_column: 1,
                last_line: 4,
                last_column: 20
              },
              text: 'SELECT * FROM users;'
            });

            expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_MOVE_CURSOR, {
              row: 4,
              column: 20
            });
          });

          it('replaces active statement that spans multiple lines', () => {
            const activeStatementInEditor = {
              type: 'statement',
              statement: ' ',
              location: {
                first_line: 1,
                first_column: 0,
                last_line: 2,
                last_column: 10
              },
              firstToken: 'SELECT'
            };
            const sqlToInsert = 'SELECT * FROM users;';

            // Cursor position is a required parameter for modifyEditorContents
            // but not used when replacing the active statement
            const ignoredCursorPosition = { row: 0, column: 0 };

            modifyEditorContents({
              activeStatementInEditor,
              sqlToInsert,
              actionMode: aiActionMode,
              cursorPosition: ignoredCursorPosition,
              autocompleteParser
            });

            expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_REPLACE, {
              location: {
                first_line: 1,
                first_column: 1,
                last_line: 2,
                last_column: 11
              },
              text: 'SELECT * FROM users;'
            });

            expect(huePubSub.publish).toHaveBeenCalledWith(PUBSUB_MOVE_CURSOR, {
              row: 1,
              column: 20
            });
          });
        });
      }
    );
  });
});
