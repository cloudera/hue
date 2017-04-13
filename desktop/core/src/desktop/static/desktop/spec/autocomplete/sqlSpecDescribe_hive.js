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

(function () {
  describe('sql.js Hive DESCRIBE statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = function (spec) {
      spec.dialect = 'hive';
      return SqlTestUtils.assertAutocomplete(spec);
    };

    it('should handle "DESCRIBE tbl;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE tbl;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false,
          locations: [
            { type: 'statement', location: { 'first_line': 1, 'last_line': 1, 'first_column': 1, 'last_column': 13 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 10, last_column: 13 }, identifierChain: [{ name: 'tbl' }] }
          ]
        }
      });
    });

    it('should handle "DESCRIBE tbl col.field;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE tbl col.field;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          locations: [
            { type: 'statement', location: { 'first_line': 1, 'last_line': 1, 'first_column': 1, 'last_column': 23 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 10, last_column: 13 }, identifierChain: [{ name: 'tbl' }] },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 14, last_column: 23 }, identifierChain: [{ name: 'col' }, { name: 'field'}], tables: [{ identifierChain: [{ name: 'tbl' }] }] }
          ],
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE EXTENDED tbl;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE EXTENDED tbl;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false,
          locations: [
            { type: 'statement', location: { 'first_line': 1, 'last_line': 1, 'first_column': 1, 'last_column': 22 } },
            {type: 'table', location: { first_line: 1, last_line: 1, first_column: 19, last_column: 22 }, identifierChain: [{ name: 'tbl' }] }
          ]
        }
      });
    });

    it('should handle "DESCRIBE EXTENDED tbl col.field;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE EXTENDED tbl col.field;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle DESCRIBE | tbl;', function () {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE ',
        afterCursor: ' tbl;',
        containsKeywords: ['EXTENDED', 'FORMATTED'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle DESCRIBE ext| db.tbl;', function () {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE ext',
        afterCursor: ' db.tbl;',
        containsKeywords: ['EXTENDED', 'FORMATTED'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE FORMATTED tbl;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FORMATTED tbl;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE FORMATTED tbl col.field;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FORMATTED tbl col.field;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE FUNCTION cos;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FUNCTION cos;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE FUNCTION EXTENDED cos;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FUNCTION EXTENDED cos;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE DATABASE db;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE DATABASE db;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE DATABASE EXTENDED db;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE DATABASE EXTENDED db;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE SCHEMA db;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE SCHEMA db;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DESCRIBE SCHEMA EXTENDED db;|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE SCHEMA EXTENDED db;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "DESCRIBE |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'EXTENDED', 'FORMATTED', 'FUNCTION', 'SCHEMA'],
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "DESCRIBE tbl|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE tbl',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'EXTENDED', 'FORMATTED', 'FUNCTION', 'SCHEMA'],
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "DESCRIBE db.|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE db.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest columns for "DESCRIBE db.tbl |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE db.tbl ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });

    it('should suggest keywords for "DESCRIBE FUNCTION |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FUNCTION ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTENDED']
        }
      });
    });

    it('should suggest keywords for "DESCRIBE FUNCTION | cos"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FUNCTION ',
        afterCursor: ' cos',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTENDED']
        }
      });
    });

    it('should suggest databases for "DESCRIBE DATABASE |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE DATABASE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTENDED'],
          suggestDatabases: {}
        }
      });
    });

    it('should suggest databases for "DESCRIBE DATABASE db|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE DATABASE db',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTENDED'],
          suggestDatabases: {}
        }
      });
    });

    it('should suggest databases for "DESCRIBE DATABASE EXTENDED |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE DATABASE EXTENDED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest databases for "DESCRIBE SCHEMA |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE SCHEMA ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTENDED'],
          suggestDatabases: {}
        }
      });
    });

    it('should suggest databases for "DESCRIBE SCHEMA db|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE SCHEMA db',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTENDED'],
          suggestDatabases: {}
        }
      });
    });

    it('should suggest databases for "DESCRIBE SCHEMA EXTENDED |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE SCHEMA EXTENDED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest tables for "DESCRIBE EXTENDED |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE EXTENDED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "describe extended db.|"', function() {
      assertAutoComplete({
        beforeCursor: 'describe extended db.',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest columns for "DESCRIBE EXTENDED db.tbl |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE EXTENDED db.tbl ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });

    it('should suggest tables for "DESCRIBE FORMATTED |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FORMATTED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "DESCRIBE FORMATTED db.|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FORMATTED db.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            identifierChain: [{ name: 'db' }]
          }
        }
      });
    });

    it('should suggest columns for "DESCRIBE FORMATTED db.tbl |"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FORMATTED db.tbl ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });

    it('should suggest fields for "DESCRIBE FORMATTED db.tbl col.|"', function() {
      assertAutoComplete({
        beforeCursor: 'DESCRIBE FORMATTED db.tbl col.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }, { name: 'col' }] }] }
        }
      });
    });
  });
})();