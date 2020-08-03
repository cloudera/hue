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

describe('impalaAutocompleteParser.js INSERT statements', () => {
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

  describe('INSERT', () => {
    it('should handle "INSERT INTO bla.boo VALUES (1, 2, \'a\', 3); |"', () => {
      assertAutoComplete({
        beforeCursor: "INSERT INTO bla.boo VALUES (1, 2, 'a', 3); ",
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
        containsKeywords: ['INSERT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INSERT |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT ',
        afterCursor: '',
        containsKeywords: ['INTO'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "INSERT INTO |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "INSERT INTO baa.|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO baa.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'baa' }] }
        }
      });
    });

    it('should suggest tables for "INSERT INTO TABLE baa.|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'baa' }] }
        }
      });
    });

    it('should suggest keywords for "INSERT INTO baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO baa ',
        afterCursor: '',
        containsKeywords: ['VALUES'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INSERT INTO TABLE baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa ',
        afterCursor: '',
        containsKeywords: ['VALUES'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['UPSERT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "UPSERT INTO TABLE boo.baa (a, b) VALUES (1, 2);|"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO TABLE boo.baa (a, b) VALUES (1, 2);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "UPSERT INTO production_table SELECT * FROM staging_table WHERE c1 IS NOT NULL AND c2 > 0;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'UPSERT INTO production_table SELECT * FROM staging_table WHERE c1 IS NOT NULL AND c2 > 0;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "UPSERT INTO boo.baa [SHUFFLE] SELECT * FROM bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO boo.baa [SHUFFLE] SELECT * FROM bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "INSERT INTO TABLE boo.baa (a, b) PARTITION (a=1) VALUES (1, 2);|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE boo.baa (a, b) PARTITION (a=1) VALUES (1, 2);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "INSERT OVERWRITE boo.baa [SHUFFLE] SELECT * FROM bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE boo.baa [SHUFFLE] SELECT * FROM bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT OVERWRITE tab SELECT * FROM t1, t2;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT OVERWRITE tab SELECT * FROM t1, t2;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "WITH t1 as (select 1), t2 as (select 2) |"', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 as (select 1), t2 as (select 2) ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['INSERT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "UPSERT |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO']
        }
      });
    });

    it('should suggest tables for "UPSERT INTO |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "UPSERT INTO boo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO boo.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }] }
        }
      });
    });

    it('should suggest keywords for "UPSERT INTO baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO baa ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES']
        }
      });
    });

    it('should suggest tables for "UPSERT INTO baa [SHUFFLE] SELECT * FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO baa [SHUFFLE] SELECT * FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest columns for "UPSERT INTO TABLE boo.baa (|"', () => {
      assertAutoComplete({
        beforeCursor: 'UPSERT INTO boo.baa (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
        }
      });
    });

    it('should suggest keywords for "INSERT |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO', 'OVERWRITE']
        }
      });
    });

    it('should suggest tables for "INSERT INTO |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "INSERT INTO boo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO boo.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }] }
        }
      });
    });

    it('should suggest keywords for "INSERT INTO baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO baa ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', '[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES']
        }
      });
    });

    it('should suggest keywords for "INSERT INTO baa [SHUFFLE] |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO baa [SHUFFLE] ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest tables for "INSERT INTO baa [SHUFFLE] SELECT * FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO baa [SHUFFLE] SELECT * FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest columns for "INSERT INTO TABLE boo.baa (|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO boo.baa (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
        }
      });
    });

    it('should suggest columns for "INSERT INTO TABLE boo.baa (a, |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO boo.baa (a, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
        }
      });
    });

    it('should suggest keywords for "WITH t1 as (select 1), t2 as (select 2) INSERT INTO baa (a, b) |"', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 as (select 1), t2 as (select 2) INSERT INTO baa ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', '[NOSHUFFLE]', '[SHUFFLE]', 'SELECT', 'VALUES'],
          commonTableExpressions: [
            { alias: 't1', columns: [{ type: 'NUMBER' }] },
            { alias: 't2', columns: [{ type: 'NUMBER' }] }
          ]
        }
      });
    });

    it('should suggest columns for "INSERT INTO TABLE boo.baa (a, b) PARTITION(a = 1, |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE boo.baa (a, b) PARTITION(a = 1, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
        }
      });
    });

    it('should not suggest keywords for "INSERT INTO TABLE boo.baa (a, b) VALUES (1, 2) |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE boo.baa (a, b) VALUES (1, 2) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "INSERT OVERWRITE |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest identifier for "with t1 as (select 1), t2 as (select 2) insert into tab select * from |"', () => {
      assertAutoComplete({
        beforeCursor: 'with t1 as (select 1), t2 as (select 2) insert into tab select * from ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestCommonTableExpressions: [{ name: 't1' }, { name: 't2' }],
          commonTableExpressions: [
            { alias: 't1', columns: [{ type: 'NUMBER' }] },
            { alias: 't2', columns: [{ type: 'NUMBER' }] }
          ]
        }
      });
    });

    it('should handle "INSERT INTO TABLE boo.t1(a, b) PARTITION (a) VALUES (1, 2);|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE boo.t1 (a, b) PARTITION (a) VALUES (1, 2);',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });
});
