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

import SqlTestUtils from 'parse/spec/sqlTestUtils';
import impalaAutocompleteParser from '../impalaAutocompleteParser';

describe('impalaAutocompleteParser.js DROP statements', () => {
  beforeAll(() => {
    impalaAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
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

  it('should suggest keywords for "DROP |"', () => {
    assertAutoComplete({
      beforeCursor: 'DROP ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: [
          'AGGREGATE FUNCTION',
          'DATABASE',
          'FUNCTION',
          'INCREMENTAL STATS',
          'ROLE',
          'SCHEMA',
          'STATS',
          'TABLE',
          'VIEW'
        ]
      }
    });
  });

  describe('DELETE FROM', () => {
    it('should handle "DELETE FROM boo.baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE FROM boo.baa;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x;|"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DELETE t2 FROM non_kudu_table t1 JOIN kudu_table t2 ON t1.x = t2.x;|"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE t2 FROM non_kudu_table t1 JOIN kudu_table t2 ON t1.x = t2.x;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x WHERE t1.y = FALSE and t2.z > 100;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'DELETE t1 FROM t1 JOIN t2 ON t1.x = t2.x WHERE t1.y = FALSE and t2.z > 100;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DELETE FROM boo.baa WHERE id < 1 AND bla IN (SELECT * FROM boo);|"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE FROM boo.baa WHERE id < 1 AND bla IN (SELECT * FROM boo);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DELETE FROM boo.baa b JOIN bla.ble c ON b.foo = c.bar WHERE b.id < 1 AND c.id IN (SELECT * FROM boo);|"', () => {
      assertAutoComplete({
        beforeCursor:
          'DELETE FROM boo.baa b JOIN bla.ble c ON b.foo = c.bar WHERE b.id < 1 AND c.id IN (SELECT * FROM boo);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['DELETE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "DELETE |"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM'],
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "DELETE FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "DELETE FROM db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE FROM db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest tables for "DELETE t1 FROM db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE FROM db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest keywords for "DELETE FROM boo.baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE FROM boo.baa ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['WHERE', 'AS', 'LEFT ANTI JOIN'],
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: true,
            tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }]
          }
        }
      });
    });

    it('should suggst tables for "DELETE t1 FROM tbl t1 JOIN |"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE t1 FROM tbl t1 JOIN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['[BROADCAST]', '[SHUFFLE]'],
          suggestJoins: {
            prependJoin: false,
            joinType: 'JOIN',
            tables: [{ identifierChain: [{ name: 'tbl' }], alias: 't1' }]
          },
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest columns for "DELETE FROM boo.baa WHERE |"', () => {
      assertAutoComplete({
        beforeCursor: 'DELETE FROM boo.baa WHERE ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['EXISTS'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] },
          suggestFilters: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
        }
      });
    });
  });

  describe('DROP DATABASE', () => {
    it('should suggest databases for "DROP SCHEMA |"', () => {
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

    it('should suggest keywords for "DROP DATABASE IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP DATABASE IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "DROP DATABASE foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP DATABASE foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE', 'RESTRICT']
        }
      });
    });
  });

  describe('DROP FUNCTION', () => {
    it('should handle "DROP AGGREGATE FUNCTION IF EXISTS baa.boo(INT, STRING ...);', () => {
      assertAutoComplete({
        beforeCursor: 'DROP AGGREGATE FUNCTION IF EXISTS baa.boo(INT, STRING ...);',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "DROP |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP ',
        afterCursor: '',
        containsKeywords: ['AGGREGATE FUNCTION', 'FUNCTION'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "DROP AGGREGATE |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP AGGREGATE ',
        afterCursor: '',
        containsKeywords: ['FUNCTION'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "DROP FUNCTION |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP FUNCTION ',
        afterCursor: '',
        containsKeywords: ['IF EXISTS'],
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "DROP AGGREGATE FUNCTION |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP AGGREGATE FUNCTION ',
        afterCursor: '',
        containsKeywords: ['IF EXISTS'],
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "DROP FUNCTION IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP FUNCTION IF ',
        afterCursor: '',
        containsKeywords: ['EXISTS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest databases for "DROP FUNCTION IF EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP FUNCTION IF EXISTS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "DROP FUNCTION IF EXISTS baa.boo(|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP FUNCTION IF EXISTS baa.boo(',
        afterCursor: '',
        containsKeywords: ['INT'],
        doesNotContainKeywords: ['...'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "DROP FUNCTION IF EXISTS baa.boo(INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP FUNCTION IF EXISTS baa.boo(INT ',
        afterCursor: '',
        containsKeywords: ['...'],
        doesNotContainKeywords: ['INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "DROP FUNCTION IF EXISTS baa.boo(INT, STRING, |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP FUNCTION IF EXISTS baa.boo(INT, STRING, ',
        afterCursor: '',
        containsKeywords: ['INT'],
        doesNotContainKeywords: ['...'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('DROP ROLE', () => {
    it('should handle "DROP ROLE boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP ROLE boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('DROP STATS', () => {
    it('should handle "DROP STATS bla.boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP STATS bla.boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DROP INCREMENTAL STATS bla.boo PARTITION (a=1, b = 2);|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP INCREMENTAL STATS bla.boo PARTITION (a=1, b = 2);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "DROP |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['INCREMENTAL STATS', 'STATS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "DROP STATS |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP STATS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "DROP STATS db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP STATS db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest keywords for "DROP INCREMENTAL |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP INCREMENTAL ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['STATS']
        }
      });
    });

    it('should suggest tables for "DROP INCREMENTAL STATS |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP INCREMENTAL STATS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "DROP INCREMENTAL STATS db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP STATS db.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }] }
        }
      });
    });

    it('should suggest keywords for "DROP INCREMENTAL STATS db.tbl |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP INCREMENTAL STATS db.tbl ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest columns for "DROP INCREMENTAL STATS db.tbl PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP INCREMENTAL STATS db.tbl PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });

    it('should suggest columns for "DROP INCREMENTAL STATS db.tbl PARTITION (bla = 1, |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP INCREMENTAL STATS db.tbl PARTITION (bla = 1, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }] }] }
        }
      });
    });
  });

  describe('DROP TABLE', () => {
    it('should handle "DROP TABLE db.tbl PURGE;"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP TABLE db.tbl PURGE;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "DROP TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP TABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestKeywords: ['IF EXISTS'],
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "DROP TABLE db.|"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP TABLE db.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db' }], onlyTables: true }
        }
      });
    });

    it('should suggest keywords for "DROP TABLE IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP TABLE IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest tables for "DROP TABLE IF EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP TABLE IF EXISTS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest keywords for "DROP TABLE foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP TABLE foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PURGE'],
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 15 }
            },
            {
              type: 'statementType',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 5 },
              identifier: 'DROP TABLE'
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
              identifierChain: [{ name: 'foo' }]
            }
          ]
        }
      });
    });
  });

  describe('DROP VIEW', () => {
    it('should handle "DROP VIEW boo;|', () => {
      assertAutoComplete({
        beforeCursor: 'DROP VIEW boo;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "DROP VIEW IF EXISTS baa.boo;|', () => {
      assertAutoComplete({
        beforeCursor: 'DROP VIEW IF EXISTS baa.boo;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest views for "DROP VIEW |', () => {
      assertAutoComplete({
        beforeCursor: 'DROP VIEW ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyViews: true },
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['IF EXISTS']
        }
      });
    });

    it('should suggest keywords for "DROP VIEW IF |', () => {
      assertAutoComplete({
        beforeCursor: 'DROP VIEW IF ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest views for "DROP VIEW boo.|', () => {
      assertAutoComplete({
        beforeCursor: 'DROP VIEW boo.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }], onlyViews: true }
        }
      });
    });
  });

  describe('TRUNCATE TABLE', () => {
    it('should handle "TRUNCATE TABLE IF EXISTS baa.boo;"', () => {
      assertAutoComplete({
        beforeCursor: 'TRUNCATE TABLE IF EXISTS baa.boo;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "TRUNCATE TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'TRUNCATE TABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['IF EXISTS']
        }
      });
    });

    it('should suggest keywords for "TRUNCATE TABLE IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'TRUNCATE TABLE IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest tables for "TRUNCATE TABLE IF EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'TRUNCATE TABLE IF EXISTS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "TRUNCATE TABLE | boo"', () => {
      assertAutoComplete({
        beforeCursor: 'TRUNCATE TABLE ',
        afterCursor: ' boo',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF EXISTS']
        }
      });
    });
  });
});
