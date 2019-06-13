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

describe('sqlAutocompleteParser.js SHOW statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  it('should suggest keywords for "|"', () => {
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

  it('should suggest keywords for "SHOW |"', () => {
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

  describe('hive specific', () => {
    it('should suggest keywords for "SHOW |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'COLUMNS',
            'COMPACTIONS',
            'CONF',
            'CREATE TABLE',
            'CURRENT ROLES',
            'DATABASES',
            'FORMATTED',
            'FUNCTIONS',
            'GRANT',
            'INDEX',
            'INDEXES',
            'LOCKS',
            'PARTITIONS',
            'PRINCIPALS',
            'ROLE GRANT',
            'ROLES',
            'SCHEMAS',
            'TABLE EXTENDED',
            'TABLES',
            'TBLPROPERTIES',
            'TRANSACTIONS',
            'VIEWS'
          ]
        }
      });
    });

    it('should handle "SHOW COMPACTIONS;|"', () => {
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

    it('should handle "SHOW CONF a.b.c;|"', () => {
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

    it('should handle "SHOW CURRENT ROLES;|"', () => {
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

    it('should suggest keywords for "SHOW COLUMNS |"', () => {
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

    it('should suggest tables for "SHOW COLUMNS FROM |"', () => {
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

    it('should suggest tables for "SHOW COLUMNS FROM partial|"', () => {
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

    it('should suggest keywords for "SHOW COLUMNS FROM tableName |"', () => {
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

    it('should suggest databases for "SHOW COLUMNS FROM tableName FROM |"', () => {
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

    it('should suggest databases for "SHOW COLUMNS FROM tableName FROM partial|"', () => {
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

    it('should suggest databases for "SHOW COLUMNS FROM tableName IN |"', () => {
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

    it('should suggest databases for "SHOW COLUMNS FROM tableName IN partial|"', () => {
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

    it('should suggest tables for "SHOW COLUMNS IN |"', () => {
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

    it('should suggest tables for "SHOW COLUMNS IN partial|"', () => {
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

    it('should suggest keywords for "SHOW COLUMNS IN tableName |"', () => {
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

    it('should suggest databases for "SHOW COLUMNS IN tableName FROM |"', () => {
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

    it('should suggest databases for "SHOW COLUMNS IN tableName FROM partial|"', () => {
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

    it('should suggest databases for "SHOW COLUMNS IN tableName IN |"', () => {
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

    it('should suggest databases for "SHOW COLUMNS IN tableName IN partial|"', () => {
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

    it('should suggest keywords for "SHOW CREATE |"', () => {
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

    it('should suggest tables for "SHOW CREATE TABLE |"', () => {
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

    it('should suggest tables for "SHOW CREATE TABLE partial|"', () => {
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

    it('should suggest tables for "SHOW CREATE TABLE databaseOne.|"', () => {
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

    it('should suggest tables for "SHOW CREATE TABLE databaseOne.partial|"', () => {
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

    it('should suggest keywords for "SHOW CURRENT |"', () => {
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

    it('should suggest keywords for "SHOW DATABASES |"', () => {
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

    it('should suggest keywords for "SHOW FORMATTED |"', () => {
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

    it('should suggest keywords for "SHOW FORMATTED INDEX |"', () => {
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

    it('should suggest tables for "SHOW FORMATTED INDEX ON |"', () => {
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

    it('should suggest tables for "SHOW FORMATTED INDEX ON partial|"', () => {
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

    it('should suggest keywords for "SHOW FORMATTED INDEX ON tableName |"', () => {
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

    it('should suggest databases for "SHOW FORMATTED INDEX ON table FROM |"', () => {
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

    it('should suggest tables for "SHOW FORMATTED INDEX ON | FROM databaseOne"', () => {
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

    it('should suggest keywords for "SHOW FORMATTED INDEXES |"', () => {
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

    it('should suggest tables for "SHOW FORMATTED INDEXES ON |"', () => {
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

    it('should suggest tables for "SHOW FORMATTED INDEXES ON partial|"', () => {
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

    it('should suggest keywords for "SHOW FORMATTED INDEX ON tableOne |"', () => {
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

    it('should suggest keywords for "SHOW FORMATTED INDEXES |"', () => {
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

    it('should suggest keywords for "SHOW FORMATTED INDEXES ON tableOne |"', () => {
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

    it('should suggest tables and keywords for "SHOW GRANT |"', () => {
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

    it('should suggest tables for "SHOW GRANT ON |"', () => {
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

    it('should suggest tables for "SHOW GRANT ON partial|"', () => {
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

    it('should suggest tables for "SHOW GRANT ON TABLE |"', () => {
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

    it('should suggest tables for SHOW GRANT ON TABLE partial|"', () => {
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

    it('should suggest tables for "SHOW GRANT pcp |"', () => {
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

    it('should suggest tables for "SHOW GRANT pcp ON |"', () => {
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

    it('should suggest tables for "SHOW GRANT pcp ON partial|"', () => {
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

    it('should suggest tables for "SHOW GRANT pcp ON TABLE |"', () => {
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

    it('should suggest tables for "SHOW GRANT pcp ON TABLE partial|"', () => {
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

    it('should suggest keywords for "SHOW INDEX |"', () => {
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

    it('should suggest tables for "SHOW INDEX ON |"', () => {
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

    it('should suggest tables for "SHOW INDEX ON partial|"', () => {
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

    it('should suggest keywords for "SHOW INDEX ON tableOne |"', () => {
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

    it('should suggest keywords for "SHOW INDEXES |"', () => {
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

    it('should suggest tables for "SHOW INDEXES ON |"', () => {
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

    it('should suggest tables for "SHOW INDEXES ON partial|"', () => {
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

    it('should suggest keywords for "SHOW INDEXES ON tableOne |"', () => {
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

    it('should suggest tables for "SHOW LOCKS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW LOCKS ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            // TODO: Is this ok for hive?
            appendDot: true
          },
          suggestKeywords: ['DATABASE', 'SCHEMA']
        }
      });
    });

    it('should suggest tables for "SHOW LOCKS partial|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW LOCKS partial',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            // TODO: Is this ok for hive?
            appendDot: true
          },
          suggestKeywords: ['DATABASE', 'SCHEMA']
        }
      });
    });

    it('should suggest databases for "SHOW LOCKS DATABASE |"', () => {
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

    it('should suggest databases for "SHOW LOCKS DATABASE partial |"', () => {
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

    it('should suggest databases for "SHOW LOCKS SCHEMA |"', () => {
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

    it('should suggest databases for "SHOW LOCKS SCHEMA partial|"', () => {
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

    it('should suggest keywords for "SHOW LOCKS tableName |"', () => {
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

    it("should suggest keywords for \"SHOW LOCKS tableName PARTITION (ds='2010-03-03', hr='12') |\"", () => {
      assertAutoComplete({
        beforeCursor: "SHOW LOCKS tableName PARTITION (ds='2010-03-03', hr='12') ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTENDED']
        }
      });
    });

    it('should suggest tables for "SHOW PARTITIONS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW PARTITIONS ',
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

    it('should suggest tables for "SHOW PARTITIONS partial|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW PARTITIONS partial',
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

    it('should suggest keywords for "SHOW PARTITIONS foo |"', () => {
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

    it('should suggest keywords for "SHOW ROLE |"', () => {
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

    it('should suggest keywords for "SHOW ROLE GRANT |"', () => {
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

    it('should suggest keywords for "SHOW SCHEMAS |"', () => {
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

    it('should suggest keywords for "SHOW TABLE |"', () => {
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

    it('should suggest keywords for "SHOW TABLE EXTENDED |"', () => {
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

    it('should suggest databases for "SHOW TABLE EXTENDED FROM |"', () => {
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

    it('should suggest functions for "SHOW TABLE EXTENDED FROM databaseOne LIKE \'f|oo*\' |"', () => {
      assertAutoComplete({
        beforeCursor: "SHOW TABLE EXTENDED FROM databaseOne LIKE 'f|oo*' ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest databases for "SHOW TABLE EXTENDED IN |"', () => {
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

    it('should suggest functions for "SHOW TABLE EXTENDED IN databaseOne LIKE \'f|oo*\' |"', () => {
      assertAutoComplete({
        beforeCursor: "SHOW TABLE EXTENDED IN databaseOne LIKE 'f|oo*' ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest functions for "SHOW TABLE EXTENDED LIKE \'f|oo*\' |"', () => {
      assertAutoComplete({
        beforeCursor: "SHOW TABLE EXTENDED LIKE 'f|oo*' ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "SHOW TABLES |"', () => {
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

    it('should suggest databases for "SHOW TABLES IN |"', () => {
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

    it('should suggest keywords for "SHOW TABLES IN db |"', () => {
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

    it('should handle "SHOW TBLPROPERTIES boo("foo"); |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW TBLPROPERTIES boo("foo"); ',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "SHOW TBLPROPERTIES |"', () => {
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

    it('should suggest tables for "SHOW TBLPROPERTIES partial|"', () => {
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

    it('should handle "SHOW TRANSACTIONS;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW TRANSACTIONS;',
        afterCursor: '',
        noErrors: true,
        dialect: 'hive',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SHOW VIEWS;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW VIEWS;',
        afterCursor: '',
        noErrors: true,
        dialect: 'hive',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SHOW VIEWS IN boo LIKE \'asdf\';|"', () => {
      assertAutoComplete({
        beforeCursor: "SHOW VIEWS IN boo LIKE 'asdf';",
        afterCursor: '',
        noErrors: true,
        dialect: 'hive',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SHOW VIEWS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW VIEWS ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM', 'IN', 'LIKE']
        }
      });
    });

    it('should suggest databases for "SHOW VIEWS IN |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW VIEWS IN ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest databases for "SHOW VIEWS FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW VIEWS FROM ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest keywords for "SHOW VIEWS IN boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW VIEWS IN boo ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LIKE']
        }
      });
    });
  });

  describe('impala specific', () => {
    it('should suggest keywords for "SHOW |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'AGGREGATE FUNCTIONS',
            'ANALYTIC FUNCTIONS',
            'COLUMN STATS',
            'CREATE TABLE',
            'CREATE VIEW',
            'CURRENT ROLES',
            'DATABASES',
            'FILES IN',
            'FUNCTIONS',
            'GRANT ROLE',
            'GRANT USER',
            'PARTITIONS',
            'RANGE PARTITIONS',
            'ROLE GRANT GROUP',
            'ROLES',
            'SCHEMAS',
            'TABLE STATS',
            'TABLES'
          ]
        }
      });
    });

    it('should suggest keywords for "SHOW AGGREGATE |"', () => {
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

    it('should suggest keywords for "SHOW AGGREGATE FUNCTIONS |"', () => {
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

    it('should suggest databases for "SHOW AGGREGATE FUNCTIONS IN |"', () => {
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

    it('should suggest databases for "SHOW AGGREGATE FUNCTIONS IN partial|"', () => {
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

    it('should suggest keywords for "SHOW ANALYTIC |"', () => {
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

    it('should suggest keywords for "SHOW ANALYTIC FUNCTIONS |"', () => {
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

    it('should suggest databases for "SHOW ANALYTIC FUNCTIONS IN |"', () => {
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

    it('should suggest databases for "SHOW ANALYTIC FUNCTIONS IN partial|"', () => {
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

    it('should suggest keywords for "SHOW COLUMN |"', () => {
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

    it('should suggest tables for "SHOW COLUMN STATS |"', () => {
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

    it('should suggest tables for "SHOW COLUMN STATS partial|"', () => {
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

    it('should suggest keywords for "SHOW CREATE |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW CREATE ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE', 'VIEW']
        }
      });
    });

    it('should suggest tables for "SHOW CREATE TABLE |"', () => {
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

    it('should suggest views for "SHOW CREATE VIEW |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW CREATE VIEW ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyViews: true },
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest views for "SHOW CREATE VIEW db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW CREATE VIEW db.',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyViews: true, identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest tables for "SHOW CREATE TABLE partial|"', () => {
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

    it('should suggest keywords for "SHOW CURRENT |"', () => {
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

    it('should suggest keywords for "SHOW | ROLES"', () => {
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

    it('should handle "SHOW CURRENT ROLES;|"', () => {
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

    it('should suggest keywords for "SHOW DATABASES |"', () => {
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

    it('should handle "SHOW FILES IN bla.boo PARTITION (baa=1, boo=2);|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW FILES IN bla.boo PARTITION (baa=1, boo=2);',
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SHOW FILES |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW FILES ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IN']
        }
      });
    });

    it('should suggest tables for "SHOW FILES IN |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW FILES IN ',
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

    it('should suggest keywords for "SHOW FILES IN boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW FILES IN boo ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should handle "SHOW FUNCTIONS IN _impala_builtins like "*substring*"; |', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW FUNCTIONS IN _impala_builtins like "*substring*"; ',
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"SHOW FUNCTIONS IN _impala_builtins like '*substring*'; |", () => {
      assertAutoComplete({
        beforeCursor: "SHOW FUNCTIONS IN _impala_builtins like '*substring*'; ",
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SHOW FUNCTIONS |"', () => {
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

    it('should suggest databases for "SHOW FUNCTIONS IN |"', () => {
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

    it('should suggest databases for "SHOW FUNCTIONS IN partial|"', () => {
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

    it('should handle "SHOW GRANT ROLE boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT ROLE boo;',
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SHOW GRANT ROLE boo ON DATABASE baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT ROLE boo ON DATABASE baa;',
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SHOW GRANT USER boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT USER boo;',
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SHOW GRANT USER boo ON DATABASE baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT USER boo ON DATABASE baa;',
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SHOW GRANT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "SHOW GRANT ROLE usr |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT ROLE usr ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']
        }
      });
    });

    it('should suggest keywords for "SHOW GRANT USER usr ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT USER usr ON ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'SERVER', 'TABLE', 'URI']
        }
      });
    });

    it('should suggest databases for "SHOW GRANT ROLE usr ON DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT ROLE usr ON DATABASE ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest tables for "SHOW GRANT USER usr ON TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW GRANT USER usr ON TABLE ',
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

    it('should suggest tables for "SHOW PARTITIONS |"', () => {
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

    it('should suggest tables for "SHOW PARTITIONS partial|"', () => {
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

    it('should handle "SHOW RANGE PARTITIONS bla.foo; |', () => {
      assertAutoComplete({
        beforeCursor: 'SHOW RANGE PARTITIONS bla.foo; ',
        afterCursor: '',
        dialect: 'impala',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SHOW ROLE |"', () => {
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

    it('should suggest keywords for "SHOW ROLE GRANT |"', () => {
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

    it('should handle "SHOW ROLES;|"', () => {
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

    it('should suggest keywords for "SHOW SCHEMAS |"', () => {
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

    it('should suggest keywords for "SHOW TABLE |"', () => {
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

    it('should suggest tables for "SHOW TABLE STATS |"', () => {
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

    it('should suggest tables for "SHOW TABLE STATS partial|"', () => {
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

    it('should suggest keywords for "SHOW TABLES |"', () => {
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

    it('should suggest databases for "SHOW TABLES IN |"', () => {
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

    it('should suggest databases for "SHOW TABLES IN partial|"', () => {
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
