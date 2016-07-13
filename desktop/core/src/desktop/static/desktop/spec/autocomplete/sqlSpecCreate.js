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

  describe('sql.js CREATE statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = testUtils.assertAutocomplete;

    it('should suggest keywords for "|"', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['CREATE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE |"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'SCHEMA', 'TABLE']
        }
      });
    });

    it('should suggest keywords for "CREATE DATABASE |"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE DATABASE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE DATABASE IF |"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE DATABASE IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE SCHEMA |"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE SCHEMA ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE DATABASE | bla;"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE DATABASE ',
        afterCursor: ' bla;',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id |"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'STRING', 'TIMESTAMP', 'TINYINT', 'VARCHAR']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id INT, some FLOAT, bar |"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id INT, some FLOAT, bar ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'STRING', 'TIMESTAMP', 'TINYINT', 'VARCHAR']
        }
      });
    });

    describe('Impala specific', function () {
      it('should suggest keywords for "CREATE DATABASE foo |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE DATABASE foo ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT', 'LOCATION']
          }
        });
      });
    });

    describe('Hive specific', function () {
      it ('should suggest keywords for "CREATE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']
          }
        });
      });

      it ('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int) |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['LOCATION']
          }
        });
      });

      it('should suggest keywords for "CREATE TABLE foo (id |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TABLE foo (id ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'STRING', 'TIMESTAMP', 'TINYINT', 'VARCHAR']
          }
        });
      });

      it('should suggest keywords for "CREATE DATABASE foo |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE DATABASE foo ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']
          }
        });
      });

      it('should suggest keywords for "CREATE DATABASE foo COMMENT \'bla\' |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE DATABASE foo COMMENT \'bla\' ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['LOCATION', 'WITH DBPROPERTIES']
          }
        });
      });

      it('should suggest keywords for "CREATE DATABASE foo COMMENT \'bla\' LOCATION \'/bla\' |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE DATABASE foo COMMENT \'bla\' LOCATION \'/bla\' ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['WITH DBPROPERTIES']
          }
        });
      });
    });
  });
});