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

import prestoAutocompleteParser from '../prestoAutocompleteParser';
import SqlTestUtils from '../../../spec/sqlTestUtils';

describe('prestoAutocompleteParser.js SHOW statements', () => {
  beforeAll(() => {
    prestoAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      prestoAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  it('should suggest keywords for "SHOW |"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW ',
      afterCursor: '',
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
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['LIKE']
      }
    });
  });
});
