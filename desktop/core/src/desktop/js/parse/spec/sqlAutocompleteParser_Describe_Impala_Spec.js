// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import SqlTestUtils from './sqlTestUtils';
import sqlAutocompleteParser from '../sqlAutocompleteParser';

describe('sqlAutocompleteParser.js Impala DESCRIBE statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = function(spec) {
    spec.dialect = 'impala';
    return SqlTestUtils.assertAutocomplete(spec);
  };

  it('should handle "DESCRIBE tbl;|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE tbl;',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false,
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 13 }
          },
          {
            type: 'statementType',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 9 },
            identifier: 'DESCRIBE'
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 10, last_column: 13 },
            identifierChain: [{ name: 'tbl' }]
          }
        ]
      }
    });
  });

  it('should handle "DESCRIBE db.tbl;|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE db.tbl;',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false,
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 16 }
          },
          {
            type: 'statementType',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 9 },
            identifier: 'DESCRIBE'
          },
          {
            type: 'database',
            location: { first_line: 1, last_line: 1, first_column: 10, last_column: 12 },
            identifierChain: [{ name: 'db' }]
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 13, last_column: 16 },
            identifierChain: [{ name: 'db' }, { name: 'tbl' }]
          }
        ]
      }
    });
  });

  it('should handle "DESCRIBE DATABASE db;|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE DATABASE db;',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "DESCRIBE EXTENDED db.tbl;|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE EXTENDED db.tbl;',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "DESCRIBE FORMATTED db.tbl;|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE FORMATTED db.tbl;',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest tables for "DESCRIBE |"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['DATABASE', 'EXTENDED', 'FORMATTED'],
        suggestTables: {},
        suggestDatabases: { appendDot: true }
      }
    });
  });

  it('should suggest databases for "DESCRIBE DATABASE |"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE DATABASE ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['EXTENDED', 'FORMATTED'],
        suggestDatabases: {}
      }
    });
  });

  it('should suggest tables for "DESCRIBE db|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE db',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['DATABASE', 'EXTENDED', 'FORMATTED'],
        suggestTables: {},
        suggestDatabases: { appendDot: true }
      }
    });
  });

  it('should suggest tables for "DESCRIBE FORMATTED db|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE FORMATTED db',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: {},
        suggestDatabases: { appendDot: true }
      }
    });
  });

  it('should suggest tables for "DESCRIBE EXTENDED db|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE EXTENDED db',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: {},
        suggestDatabases: { appendDot: true }
      }
    });
  });

  it('should suggest tables for "DESCRIBE db.|"', () => {
    assertAutoComplete({
      beforeCursor: 'DESCRIBE db.',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: 'db' }] }
      }
    });
  });
});
