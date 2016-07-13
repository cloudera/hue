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
define([
  'knockout',
  'desktop/js/autocomplete/sql',
  'desktop/spec/autocompleterTestUtils'
], function(ko, sql, testUtils) {

  describe('sql.js DESCRIBE statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = testUtils.assertAutocomplete;


    describe('hive specific', function () {
      it('should handle "DESCRIBE tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE tbl;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DESCRIBE tbl.col.field;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE tbl col.field;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DESCRIBE EXTENDED tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE EXTENDED tbl;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DESCRIBE EXTENDED tbl col.field;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE EXTENDED tbl col.field;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DESCRIBE FORMATTED tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE FORMATTED tbl;',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: { database: 'db' }
          }
        });
      });

      it('should suggest columns for "DESCRIBE db.tbl |"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE db.tbl ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              table: 'tbl',
              database: 'db'
            }
          }
        });
      });

      it('should suggest keywords for "DESCRIBE FUNCTION |"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE FUNCTION ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: true,
            suggestTables: { database: 'db' }
          }
        });
      });

      it('should suggest columns for "DESCRIBE EXTENDED db.tbl |"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE EXTENDED db.tbl ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              database: 'db',
              table: 'tbl'
            }
          }
        });
      });

      it('should suggest tables for "DESCRIBE FORMATTED |"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE FORMATTED ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {
              database: 'db'
            }
          }
        });
      });

      it('should suggest columns for "DESCRIBE FORMATTED db.tbl |"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE FORMATTED db.tbl ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              database: 'db',
              table: 'tbl'
            }
          }
        });
      });

      it('should suggest fields for "DESCRIBE FORMATTED db.tbl col.|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE FORMATTED db.tbl col.',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              identifierChain: [{ name: 'col' }],
              database: 'db',
              table: 'tbl'
            }
          }
        });
      });
    });

    describe('impala specific', function () {
      it('should handle "DESCRIBE tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE tbl;',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DESCRIBE db.tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE db.tbl;',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "DESCRIBE FORMATTED db.tbl;|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE FORMATTED db.tbl;',
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FORMATTED'],
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables for "DESCRIBE db|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE db',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FORMATTED'],
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables for "DESCRIBE db.|"', function() {
        assertAutoComplete({
          beforeCursor: 'DESCRIBE db.',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {
              database: 'db'
            }
          }
        });
      });
    });
  });
});