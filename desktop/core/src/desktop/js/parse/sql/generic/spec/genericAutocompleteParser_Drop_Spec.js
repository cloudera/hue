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
import genericAutocompleteParser from '../genericAutocompleteParser';

describe('genericAutocompleteParser.js DROP statements', () => {
  beforeAll(() => {
    genericAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;
    expect(
      genericAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  it('should suggest keywords for "DROP |"', () => {
    assertAutoComplete({
      beforeCursor: 'DROP ',
      afterCursor: '',
      containsKeywords: ['DATABASE', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  describe('DROP DATABASE', () => {
    it('should suggest databases for "DROP DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP DATABASE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {},
          suggestKeywords: ['IF EXISTS']
        }
      });
    });

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

    it('should suggest databases for "DROP DATABASE IF EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP DATABASE IF EXISTS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest keywords for "DROP DATABASE foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'DROP DATABASE foo ',
        afterCursor: '',
        containsKeywords: ['CASCADE'],
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
    it('should handle "TRUNCATE TABLE baa.boo;"', () => {
      assertAutoComplete({
        beforeCursor: 'TRUNCATE TABLE baa.boo;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "TRUNCATE |"', () => {
      assertAutoComplete({
        beforeCursor: 'truncate ',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['TABLE']
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
  });
});
