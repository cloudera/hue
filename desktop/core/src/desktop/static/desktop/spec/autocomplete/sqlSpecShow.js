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
  describe('sql.js SHOW statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    it('should suggest keywords for "|"', function() {
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

    it('should suggest keywords for "SHOW |"', function() {
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
      it('should suggest keywords for "SHOW |"', function() {
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

      it('should handle "SHOW COMPACTIONS;|"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW COMPACTIONS;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SHOW CONF a.b.c;|"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CONF a.b.c;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SHOW CURRENT ROLES;|"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CURRENT ROLES;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SHOW COLUMNS |"', function() {
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

      it('should suggest tables for "SHOW COLUMNS FROM |"', function() {
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

      it('should suggest tables for "SHOW COLUMNS FROM partial|"', function() {
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

      it('should suggest keywords for "SHOW COLUMNS FROM tableName |"', function() {
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

      it('should suggest databases for "SHOW COLUMNS FROM tableName FROM |"', function() {
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

      it('should suggest databases for "SHOW COLUMNS FROM tableName FROM partial|"', function() {
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

      it('should suggest databases for "SHOW COLUMNS FROM tableName IN |"', function() {
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

      it('should suggest databases for "SHOW COLUMNS FROM tableName IN partial|"', function() {
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

      it('should suggest tables for "SHOW COLUMNS IN |"', function() {
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

      it('should suggest tables for "SHOW COLUMNS IN partial|"', function() {
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

      it('should suggest keywords for "SHOW COLUMNS IN tableName |"', function() {
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

      it('should suggest databases for "SHOW COLUMNS IN tableName FROM |"', function() {
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

      it('should suggest databases for "SHOW COLUMNS IN tableName FROM partial|"', function() {
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

      it('should suggest databases for "SHOW COLUMNS IN tableName IN |"', function() {
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

      it('should suggest databases for "SHOW COLUMNS IN tableName IN partial|"', function() {
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

      it('should suggest keywords for "SHOW CREATE |"', function() {
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

      it('should suggest tables for "SHOW CREATE TABLE |"', function() {
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

      it('should suggest tables for "SHOW CREATE TABLE partial|"', function() {
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

      it('should suggest tables for "SHOW CREATE TABLE databaseOne.|"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE databaseOne.',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'databaseOne' }] }
          }
        });
      });

      it('should suggest tables for "SHOW CREATE TABLE databaseOne.partial|"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CREATE TABLE databaseOne.partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'databaseOne' }] }
          }
        });
      });

      it('should suggest keywords for "SHOW CURRENT |"', function() {
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

      it('should suggest keywords for "SHOW DATABASES |"', function() {
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

      it('should suggest keywords for "SHOW FORMATTED |"', function() {
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

      it('should suggest keywords for "SHOW FORMATTED INDEX |"', function() {
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

      it('should suggest tables for "SHOW FORMATTED INDEX ON |"', function() {
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

      it('should suggest tables for "SHOW FORMATTED INDEX ON partial|"', function() {
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

      it('should suggest keywords for "SHOW FORMATTED INDEX ON tableName |"', function() {
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

      it('should suggest databases for "SHOW FORMATTED INDEX ON table FROM |"', function() {
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

      it('should suggest tables for "SHOW FORMATTED INDEX ON | FROM databaseOne"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW FORMATTED INDEX ON ',
          afterCursor: ' FROM databaseOne',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'databaseOne' }] }
          }
        });
      });

      it('should suggest keywords for "SHOW FORMATTED INDEXES |"', function() {
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

      it('should suggest tables for "SHOW FORMATTED INDEXES ON |"', function() {
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

      it('should suggest tables for "SHOW FORMATTED INDEXES ON partial|"', function() {
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

      it('should suggest keywords for "SHOW FORMATTED INDEX ON tableOne |"', function() {
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

      it('should suggest keywords for "SHOW FORMATTED INDEXES |"', function() {
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

      it('should suggest keywords for "SHOW FORMATTED INDEXES ON tableOne |"', function() {
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

      it('should suggest tables and keywords for "SHOW GRANT |"', function() {
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

      it('should suggest tables for "SHOW GRANT ON |"', function() {
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

      it('should suggest tables for "SHOW GRANT ON partial|"', function() {
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

      it('should suggest tables for "SHOW GRANT ON TABLE |"', function() {
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

      it('should suggest tables for SHOW GRANT ON TABLE partial|"', function() {
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

      it('should suggest tables for "SHOW GRANT pcp |"', function() {
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

      it('should suggest tables for "SHOW GRANT pcp ON |"', function() {
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

      it('should suggest tables for "SHOW GRANT pcp ON partial|"', function() {
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

      it('should suggest tables for "SHOW GRANT pcp ON TABLE |"', function() {
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

      it('should suggest tables for "SHOW GRANT pcp ON TABLE partial|"', function() {
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

      it('should suggest keywords for "SHOW INDEX |"', function() {
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

      it('should suggest tables for "SHOW INDEX ON |"', function() {
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

      it('should suggest tables for "SHOW INDEX ON partial|"', function() {
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

      it('should suggest keywords for "SHOW INDEX ON tableOne |"', function() {
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

      it('should suggest keywords for "SHOW INDEXES |"', function() {
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

      it('should suggest tables for "SHOW INDEXES ON |"', function() {
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

      it('should suggest tables for "SHOW INDEXES ON partial|"', function() {
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

      it('should suggest keywords for "SHOW INDEXES ON tableOne |"', function() {
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

      it('should suggest tables for "SHOW LOCKS |"', function() {
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

      it('should suggest tables for "SHOW LOCKS partial|"', function() {
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

      it('should suggest databases for "SHOW LOCKS DATABASE |"', function() {
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

      it('should suggest databases for "SHOW LOCKS DATABASE partial |"', function() {
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

      it('should suggest databases for "SHOW LOCKS SCHEMA |"', function() {
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

      it('should suggest databases for "SHOW LOCKS SCHEMA partial|"', function() {
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

      it('should suggest keywords for "SHOW LOCKS tableName |"', function() {
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

      it('should suggest keywords for "SHOW LOCKS tableName PARTITION (ds=\'2010-03-03\', hr=\'12\') |"', function() {
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

      it('should suggest tables for "SHOW PARTITIONS |"', function() {
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

      it('should suggest tables for "SHOW PARTITIONS partial|"', function() {
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

      it('should suggest keywords for "SHOW PARTITIONS foo |"', function() {
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

      it('should suggest keywords for "SHOW ROLE |"', function() {
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

      it('should suggest keywords for "SHOW ROLE GRANT |"', function() {
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

      it('should suggest keywords for "SHOW SCHEMAS |"', function() {
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

      it('should suggest keywords for "SHOW TABLE |"', function() {
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

      it('should suggest keywords for "SHOW TABLE EXTENDED |"', function() {
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

      it('should suggest databases for "SHOW TABLE EXTENDED FROM |"', function() {
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

      it('should suggest functions for "SHOW TABLE EXTENDED FROM databaseOne LIKE \'f|oo*\' |"', function() {
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

      it('should suggest databases for "SHOW TABLE EXTENDED IN |"', function() {
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

      it('should suggest functions for "SHOW TABLE EXTENDED IN databaseOne LIKE \'f|oo*\' |"', function() {
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

      it('should suggest functions for "SHOW TABLE EXTENDED LIKE \'f|oo*\' |"', function() {
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

      it('should suggest keywords for "SHOW TABLES |"', function() {
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

      it('should suggest databases for "SHOW TABLES IN |"', function() {
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

      it('should suggest keywords for "SHOW TABLES IN db |"', function() {
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

      it('should suggest tables for "SHOW TBLPROPERTIES |"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TBLPROPERTIES ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { prependDot: true }
          }
        });
      });

      it('should suggest tables for "SHOW TBLPROPERTIES partial|"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW TBLPROPERTIES partial',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { prependDot: true }
          }
        });
      });

      it('should handle "SHOW TRANSACTIONS;|"', function() {
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
      it('should suggest keywords for "SHOW |"', function() {
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

      it('should suggest keywords for "SHOW AGGREGATE |"', function() {
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

      it('should suggest keywords for "SHOW AGGREGATE FUNCTIONS |"', function() {
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

      it('should suggest databases for "SHOW AGGREGATE FUNCTIONS IN |"', function() {
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

      it('should suggest databases for "SHOW AGGREGATE FUNCTIONS IN partial|"', function() {
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

      it('should suggest keywords for "SHOW ANALYTIC |"', function() {
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

      it('should suggest keywords for "SHOW ANALYTIC FUNCTIONS |"', function() {
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

      it('should suggest databases for "SHOW ANALYTIC FUNCTIONS IN |"', function() {
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

      it('should suggest databases for "SHOW ANALYTIC FUNCTIONS IN partial|"', function() {
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

      it('should suggest keywords for "SHOW COLUMN |"', function() {
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

      it('should suggest tables for "SHOW COLUMN STATS |"', function() {
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

      it('should suggest tables for "SHOW COLUMN STATS partial|"', function() {
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

      it('should suggest keywords for "SHOW CREATE |"', function() {
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

      it('should suggest tables for "SHOW CREATE TABLE |"', function() {
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

      it('should suggest tables for "SHOW CREATE TABLE partial|"', function() {
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

      it('should suggest keywords for "SHOW CURRENT |"', function() {
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

      it('should suggest keywords for "SHOW | ROLES"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW ',
          afterCursor: ' ROLES',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CURRENT']
          }
        });
      });

      it('should handle "SHOW CURRENT ROLES;|"', function() {
        assertAutoComplete({
          beforeCursor: 'SHOW CURRENT ROLES;',
          afterCursor: '',
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SHOW DATABASES |"', function() {
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

      it('should suggest keywords for "SHOW FUNCTIONS |"', function() {
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

      it('should suggest databases for "SHOW FUNCTIONS IN |"', function() {
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

      it('should suggest databases for "SHOW FUNCTIONS IN partial|"', function() {
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

      it('should suggest keywords for "SHOW GRANT |"', function() {
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

      it('should suggest tables for "SHOW PARTITIONS |"', function() {
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

      it('should suggest tables for "SHOW PARTITIONS partial|"', function() {
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

      it('should suggest keywords for "SHOW ROLE |"', function() {
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

      it('should suggest keywords for "SHOW ROLE GRANT |"', function() {
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

      it('should handle "SHOW ROLES;|"', function() {
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

      it('should suggest keywords for "SHOW SCHEMAS |"', function() {
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

      it('should suggest keywords for "SHOW TABLE |"', function() {
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

      it('should suggest tables for "SHOW TABLE STATS |"', function() {
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

      it('should suggest tables for "SHOW TABLE STATS partial|"', function() {
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

      it('should suggest keywords for "SHOW TABLES |"', function() {
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

      it('should suggest databases for "SHOW TABLES IN |"', function() {
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

      it('should suggest databases for "SHOW TABLES IN partial|"', function() {
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
})();