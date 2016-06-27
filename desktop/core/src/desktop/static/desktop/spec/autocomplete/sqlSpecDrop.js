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

  describe('sql.js DROP statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = testUtils.assertAutocomplete;

    it('should suggest keywords for empty statement', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['DROP'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords after DROP', function() {
      assertAutoComplete({
        beforeCursor: 'DROP ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE', 'SCHEMA', 'TABLE', 'VIEW']
        }
      });
    });

    describe('hive specific', function () {
      it('should suggest keywords after DROP', function() {
        assertAutoComplete({
          beforeCursor: 'DROP ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']
          }
        });
      });
    });

    describe('hive specific', function () {
      it('should follow case after drop', function() {
        assertAutoComplete({
          beforeCursor: 'drop ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: true,
            suggestKeywords: ['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']
          }
        });
      });
    });

    describe('impala specific', function () {
      it('should suggest keywords after DROP', function() {
        assertAutoComplete({
          beforeCursor: 'DROP ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']
          }
        });
      });
    });

    describe('drop database statements', function () {
      it('should suggest databases after DROP DATABASE ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP DATABASE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {},
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest databases after DROP SCHEMA ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP SCHEMA ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {},
            suggestKeywords: ['IF EXISTS']
          }
        });
      });

      it('should suggest keywords after DROP DATABASE IF ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP DATABASE IF ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest databases after DROP DATABASE IF EXISTS ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP DATABASE IF EXISTS ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords after DROP DATABASE foo ', function() {
          assertAutoComplete({
            beforeCursor: 'DROP DATABASE foo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CASCADE', 'RESTRICT']
            }
          });
        });
      });
    });

    describe('drop table statements', function () {
      it('should suggest tables after DROP TABLE ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestKeywords: ['IF EXISTS'],
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after DROP TABLE db. ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE db.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { database: 'db' }
          }
        });
      });

      it('should suggest keywords after DROP TABLE IF ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE IF ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest tables after DROP TABLE IF EXISTS ', function() {
        assertAutoComplete({
          beforeCursor: 'DROP TABLE IF EXISTS ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords after DROP TABLE foo ', function() {
          assertAutoComplete({
            beforeCursor: 'DROP TABLE foo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PURGE']
            }
          });
        });
      });
    });
  });
});