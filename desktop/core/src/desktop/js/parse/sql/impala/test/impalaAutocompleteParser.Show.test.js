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

import impalaAutocompleteParser from '../impalaAutocompleteParser';

describe('impalaAutocompleteParser.js SHOW statements', () => {
  beforeAll(() => {
    impalaAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      impalaAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug || testDefinition.debug
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
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['GROUP', 'ROLE', 'USER']
      }
    });
  });

  it('should suggest keywords for "SHOW GRANT ROLE usr |"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW GRANT ROLE usr ',
      afterCursor: '',
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
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['COLUMN', 'DATABASE', 'SERVER', 'TABLE', 'URI']
      }
    });
  });

  it('should suggest tables for "SHOW GRANT ROLE usr ON COLUMN |"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW GRANT ROLE usr ON COLUMN ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestDatabases: { appendDot: true },
        suggestTables: {}
      }
    });
  });

  it('should suggest tables for "SHOW GRANT ROLE usr ON COLUMN db.|"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW GRANT ROLE usr ON COLUMN db.',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: 'db' }] }
      }
    });
  });

  it('should suggest databases for "SHOW GRANT ROLE usr ON DATABASE |"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW GRANT ROLE usr ON DATABASE ',
      afterCursor: '',
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

  it('should handle "SHOW RANGE PARTITIONS bla.foo; |', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW RANGE PARTITIONS bla.foo; ',
      afterCursor: '',
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
        suggestKeywords: ['GROUP']
      }
    });
  });

  it('should handle "SHOW ROLES;|"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW ROLES;',
      afterCursor: '',
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
        suggestKeywords: ['STATS']
      }
    });
  });

  it('should suggest tables for "SHOW TABLE STATS |"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW TABLE STATS ',
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

  it('should suggest tables for "SHOW TABLE STATS partial|"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW TABLE STATS partial',
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

  it('should suggest databases for "SHOW TABLES IN partial|"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW TABLES IN partial',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestDatabases: {}
      }
    });
  });
});
