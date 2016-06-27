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

  describe('sql.js SHOW statements', function() {

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
        dialect: 'generic',
        containsKeywords: ['SHOW'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords after SHOW', function() {
      assertAutoComplete({
        beforeCursor: 'SHOW ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COLUMNS', 'DATABASES', 'TABLES']
        }
      });
    });

    describe('hive specific', function () {
      it('should suggest keywords after SHOW', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']
          }
        });
      });

      it('should handle SHOW COMPACTIONS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COMPACTIONS;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle SHOW CONF confName', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CONF a.b.c;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords after SHOW COLUMNS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest tables after SHOW COLUMNS FROM ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS FROM ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW COLUMNS FROM partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS FROM partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest keywords after SHOW COLUMNS FROM tableName ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS FROM tableName ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS FROM tableName FROM', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS FROM tableName FROM ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS FROM tableName FROM partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS FROM tableName FROM partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS FROM tableName IN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS FROM tableName IN ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS FROM tableName IN partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS FROM tableName IN partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest tables after SHOW COLUMNS IN ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS IN ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW COLUMNS IN partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS IN partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest keywords after SHOW COLUMNS IN tableName ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS IN tableName ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS IN tableName FROM', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS IN tableName FROM ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS IN tableName FROM partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS IN tableName FROM partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS IN tableName IN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS IN tableName IN ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW COLUMNS IN tableName IN partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMNS IN tableName IN partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest keywords after SHOW CREATE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables after SHOW CREATE TABLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after SHOW CREATE TABLE partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after SHOW CREATE TABLE databaseOne.', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE databaseOne.',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {
              database: 'databaseOne'
            }
          }
        });
      });

      it('should suggest tables after SHOW CREATE TABLE databaseOne.partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE databaseOne.partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {
              database: 'databaseOne'
            }
          }
        });
      });

      it('should suggest keywords after SHOW CURRENT', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CURRENT ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROLES']
          }
        });
      });

      it('should suggest keywords after SHOW DATABASES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW DATABASES ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['LIKE']
          }
        });
      });

      it('should suggest keywords after SHOW FORMATTED', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INDEX', 'INDEXES']
          }
        });
      });

      it('should suggest keywords after SHOW FORMATTED INDEX', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest tables after SHOW FORMATTED INDEX ON ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW FORMATTED INDEX ON partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ON partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest keywords after SHOW FORMATTED INDEX ON table', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ON tableName ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest databases after SHOW FORMATTED INDEX ON table FROM ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ON tableName FROM ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest tables after SHOW FORMATTED INDEX ON with db specified ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ON ',
          afterCursor: ' FROM databaseOne',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {
              database: 'databaseOne'
            }
          }
        });
      });

      it('should suggest keywords after SHOW FORMATTED INDEXES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEXES ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest tables after SHOW FORMATTED INDEXES ON ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEXES ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW FORMATTED INDEXES ON partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEXES ON partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest keywords after SHOW FORMATTED INDEX ON tableName ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ON tableOne ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest keywords after SHOW FORMATTED INDEXES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEXES ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest keywords after SHOW FORMATTED INDEXES ON tableName ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEXES ON tableOne ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest tables and keywords after SHOW GRANT', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest tables and keywords after SHOW GRANT ON', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestKeywords: ['ALL', 'TABLE']
          }
        });
      });

      it('should suggest tables and keywords after SHOW GRANT ON partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT ON partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestKeywords: ['ALL', 'TABLE']
          }
        });
      });

      it('should suggest tables after SHOW GRANT ON TABLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT ON TABLE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW GRANT ON TABLE partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT ON TABLE partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables and keywords after SHOW GRANT principal', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT pcp ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest tables and keywords after SHOW GRANT principal ON', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT pcp ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestKeywords: ['ALL', 'TABLE']
          }
        });
      });

      it('should suggest tables and keywords after SHOW GRANT principal ON partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT pcp ON partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestKeywords: ['ALL', 'TABLE']
          }
        });
      });

      it('should suggest tables after SHOW GRANT principal ON TABLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT pcp ON TABLE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW GRANT principal ON TABLE partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT pcp ON TABLE partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest keywords after SHOW INDEX', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEX ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest tables after SHOW INDEX ON ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEX ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW INDEX ON partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEX ON partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest keywords after SHOW INDEX ON tableName ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEX ON tableOne ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest keywords after SHOW INDEXES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEXES ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON']
          }
        });
      });

      it('should suggest tables after SHOW INDEXES ON ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEXES ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW INDEXES ON partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEXES ON partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest keywords after SHOW INDEXES ON tableName ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW INDEXES ON tableOne ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN']
          }
        });
      });

      it('should suggest tables and keywords after SHOW LOCKS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { // TODO: Is this ok for hive?
              appendDot: true
            },
            suggestKeywords: ['DATABASE', 'SCHEMA']
          }
        });
      });

      it('should suggest tables and keywords after SHOW LOCKS partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { // TODO: Is this ok for hive?
              appendDot: true
            },
            suggestKeywords: ['DATABASE', 'SCHEMA']
          }
        });
      });

      it('should suggest databases after SHOW LOCKS DATABASE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS DATABASE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW LOCKS DATABASE partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS DATABASE partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW LOCKS SCHEMA', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS SCHEMA ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW LOCKS SCHEMA partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS SCHEMA partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest keywords after SHOW LOCKS tableName', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS tableName ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXTENDED', 'PARTITION']
          }
        });
      });

      it('should suggest keywords after SHOW LOCKS tableName PARTITION partitionSpec', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW LOCKS tableName PARTITION (ds=\'2010-03-03\', hr=\'12\') ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXTENDED']
          }
        });
      });

      it('should suggest tables after SHOW PARTITIONS ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW PARTITIONS ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases : {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after SHOW PARTITIONS partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW PARTITIONS partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases : {
              appendDot: true
            }
          }
        });
      });

      it('should suggest keywords after SHOW PARTITIONS tableName', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW PARTITIONS foo ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION']
          }
        });
      });

      it('should suggest keywords after SHOW ROLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ROLE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['GRANT']
          }
        });
      });

      it('should suggest keywords after SHOW ROLE GRANT', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ROLE GRANT ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROLE', 'USER']
          }
        });
      });

      it('should suggest keywords after SHOW SCHEMAS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW SCHEMAS ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['LIKE']
          }
        });
      });

      it('should suggest keywords after SHOW TABLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXTENDED']
          }
        });
      });

      it('should suggest keywords after SHOW TABLE EXTENDED', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE EXTENDED ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FROM', 'IN', 'LIKE']
          }
        });
      });

      it('should suggest databases after SHOW TABLE EXTENDED FROM ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE EXTENDED FROM ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest functions after SHOW TABLE EXTENDED FROM database LIKE identifier', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE EXTENDED FROM databaseOne LIKE \'f|oo*\' ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION']
          }
        });
      });

      it('should suggest databases after SHOW TABLE EXTENDED IN ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE EXTENDED IN ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest functions after SHOW TABLE EXTENDED IN database LIKE identifier', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE EXTENDED IN databaseOne LIKE \'f|oo*\' ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION']
          }
        });
      });

      it('should suggest functions after SHOW TABLE EXTENDED LIKE identifier', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE EXTENDED LIKE \'f|oo*\' ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION']
          }
        });
      });

      it('should suggest keywords after SHOW TABLES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLES ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IN', 'LIKE']
          }
        });
      });

      it('should suggest databases after SHOW TABLES IN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLES IN ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest keywords after SHOW TABLES IN db ', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLES IN db ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['LIKE']
          }
        });
      });

      it('should suggest tables after SHOW TBLPROPERTIES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TBLPROPERTIES ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should suggest tables after SHOW TBLPROPERTIES partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TBLPROPERTIES partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {}
          }
        });
      });

      it('should handle SHOW TRANSACTIONS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TRANSACTIONS;',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

    describe('impala specific', function () {
      it('should suggest keywords after SHOW', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']
          }
        });
      });

      it('should suggest keywords after SHOW AGGREGATE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW AGGREGATE ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FUNCTIONS']
          }
        });
      });

      it('should suggest keywords after SHOW AGGREGATE FUNCTIONS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW AGGREGATE FUNCTIONS ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IN', 'LIKE']
          }
        });
      });

      it('should suggest databases after SHOW AGGREGATE FUNCTIONS IN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW AGGREGATE FUNCTIONS IN ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW AGGREGATE FUNCTIONS IN partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW AGGREGATE FUNCTIONS IN partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest keywords after SHOW ANALYTIC', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ANALYTIC ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FUNCTIONS']
          }
        });
      });

      it('should suggest keywords after SHOW ANALYTIC FUNCTIONS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ANALYTIC FUNCTIONS ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IN', 'LIKE']
          }
        });
      });

      it('should suggest databases after SHOW ANALYTIC FUNCTIONS IN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ANALYTIC FUNCTIONS IN ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW ANALYTIC FUNCTIONS IN partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ANALYTIC FUNCTIONS IN partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest keywords after SHOW COLUMN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMN ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['STATS']
          }
        });
      });

      it('should suggest tables after SHOW COLUMN STATS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMN STATS ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after SHOW COLUMN STATS partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COLUMN STATS partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest keywords after SHOW CREATE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables after SHOW CREATE TABLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after SHOW CREATE TABLE partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest keywords after SHOW CURRENT', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CURRENT ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROLES']
          }
        });
      });

      it('should handle SHOW CURRENT ROLES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CURRENT ROLES;',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords after SHOW DATABASES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW DATABASES ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['LIKE']
          }
        });
      });

      it('should suggest keywords after SHOW FUNCTIONS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FUNCTIONS ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IN', 'LIKE']
          }
        });
      });

      it('should suggest databases after SHOW FUNCTIONS IN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FUNCTIONS IN ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW FUNCTIONS IN partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FUNCTIONS IN partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest keywords after SHOW GRANT', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW GRANT ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROLE']
          }
        });
      });

      it('should suggest tables after SHOW PARTITIONS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW PARTITIONS ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after SHOW PARTITIONS partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW PARTITIONS partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest keywords after SHOW ROLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ROLE ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['GRANT']
          }
        });
      });

      it('should suggest keywords after SHOW ROLE GRANT', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ROLE GRANT ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['GROUP']
          }
        });
      });

      it('should handle SHOW ROLES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ROLES;',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords after SHOW SCHEMAS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW SCHEMAS ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['LIKE']
          }
        });
      });

      it('should suggest keywords after SHOW TABLE', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['STATS']
          }
        });
      });

      it('should suggest tables after SHOW TABLE STATS', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE STATS ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest tables after SHOW TABLE STATS partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLE STATS partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: {
              appendDot: true
            }
          }
        });
      });

      it('should suggest keywords after SHOW TABLES', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLES ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IN', 'LIKE']
          }
        });
      });

      it('should suggest databases after SHOW TABLES IN', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLES IN ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });

      it('should suggest databases after SHOW TABLES IN partial', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TABLES IN partial',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestDatabases: {}
          }
        });
      });
    });
  });
});