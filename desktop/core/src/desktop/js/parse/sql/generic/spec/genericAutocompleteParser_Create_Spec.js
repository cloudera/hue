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

fdescribe('genericAutocompleteParser.js CREATE statements', () => {
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
        undefined,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  it('should suggest keywords for "|"', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: '',
      containsKeywords: ['CREATE'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE ',
      afterCursor: '',
      containsKeywords: ['DATABASE', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  describe('CREATE DATABASE', () => {
    it('should suggest keywords for "CREATE DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE DATABASE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE DATABASE IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE DATABASE IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE SCHEMA |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE SCHEMA ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE DATABASE | bla;"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE DATABASE ',
        afterCursor: ' bla;',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });
  });

  describe('CREATE ROLE', () => {
    it('should handle "CREATE ROLE boo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE ROLE boo; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('CREATE TABLE', () => {
    it('should suggest keywords for "CREATE TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE IF NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE IF NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should handle for "CREATE TABLE foo (id INT);|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id INT);',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id ',
        afterCursor: '',
        containsKeywords: ['BOOLEAN'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id INT, `some` FLOAT, bar |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id INT, `some` FLOAT, bar ',
        afterCursor: '',
        containsKeywords: ['BOOLEAN'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('CREATE VIEW', () => {
    it('should handle "CREATE VIEW foo AS SELECT a, | FROM tableOne"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW foo AS SELECT a, ',
        afterCursor: ' FROM tableOne',
        hasLocations: true,
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'tableOne' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS'],
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW | boo AS select * from baa;"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW ',
        afterCursor: ' boo AS SELECT * FROM baa;',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW IF NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW IF NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW boo AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW boo AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW IF NOT EXISTS boo AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW IF NOT EXISTS boo AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });
  });
});
