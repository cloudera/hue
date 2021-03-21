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
describe('prestoAutocompleteParser.js INSERT statements', () => {
  beforeAll(() => {
    prestoAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
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

    it('should handle "INSERT OVERWRITE TABLE bla.boo PARTITION (bla=1, bo) IF NOT EXISTS SELECT ba.boo, ba, ble FROM db.tbl; |"', () => {
      assertAutoComplete({
        beforeCursor:
          'INSERT OVERWRITE TABLE bla.boo PARTITION (bla=1, bo) IF NOT EXISTS SELECT ba.boo, ba, ble FROM db.tbl;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "INSERT INTO TABLE bla.boo PARTITION (bla=1, bo) (a, b, c) SELECT ba.boo, ba, ble FROM db.tbl; |"', () => {
      assertAutoComplete({
        beforeCursor:
          'INSERT INTO TABLE bla.boo PARTITION (bla=1, bo) (a, b, c) SELECT ba.boo, ba, ble FROM db.tbl;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "INSERT OVERWRITE DIRECTORY \'blabla\' SELECT * FROM boo;|"', () => {
      assertAutoComplete({
        beforeCursor: "INSERT OVERWRITE DIRECTORY 'blabla' SELECT * FROM boo;",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "INSERT INTO bla.boo SELECT ba.boo, ba, ble FROM db.tbl; |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO bla.boo SELECT ba.boo, ba, ble FROM db.tbl;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "FROM boo.baa\\nINSERT INTO TABLE baa2 PARTITION (a, b) SELECT * ORDER BY ba\\nINSERT INTO TABLE baa3 SELECT * GROUP BY boo;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'FROM boo.baa\n' +
          'INSERT INTO TABLE baa2 PARTITION (a, b) SELECT * ORDER BY ba\n' +
          'INSERT INTO TABLE baa3 SELECT * GROUP BY boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "FROM boo.baa SELECT * ORDER BY ba;|"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM boo.baa SELECT * ORDER BY ba;',
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
        containsKeywords: ['FROM', 'INSERT'],
        noErrors: true,
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

    it('should suggest tables for "FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "from baa.boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'from baa.boo ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['INSERT INTO', 'INSERT OVERWRITE', 'SELECT']
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO', 'OVERWRITE']
        }
      });
    });

    it('should suggest tables for "FROM baa.boo INSERT INTO |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO ',
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

    it('should suggest tables for "FROM baa.boo INSERT INTO baa.|"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO baa.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'baa' }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT INTO TABLE baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'SELECT']
        }
      });
    });

    it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
        }
      });
    });

    it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (|"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }]
          },
          suggestAnalyticFunctions: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
        }
      });
    });

    it('should suggest columns for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT a, |"', () => {
      assertAutoComplete({
        beforeCursor:
          'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT a, ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }]
          },
          suggestAnalyticFunctions: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d ',
        afterCursor: '',
        noErrors: true,
        containsColRefKeywords: true,
        containsKeywords: ['WHERE', 'ORDER BY'],
        doesNotContainKeywords: ['FROM'],
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'SELECT']
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'SELECT']
        }
      });
    });

    it('should suggest columns for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bla' }, { name: 'ble' }] }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS', 'SELECT']
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest columns for "FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT |"', () => {
      assertAutoComplete({
        beforeCursor:
          'FROM baa.boo INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }]
          },
          suggestAnalyticFunctions: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d ',
        afterCursor: '',
        noErrors: true,
        containsColRefKeywords: true,
        containsKeywords: ['WHERE', 'ORDER BY'],
        doesNotContainKeywords: ['FROM'],
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d INSERT OVERWRITE bla.ble SELECT a |"', () => {
      assertAutoComplete({
        beforeCursor:
          'FROM baa.boo INSERT OVERWRITE bla.ble SELECT c, d INSERT OVERWRITE bla.ble SELECT a ',
        afterCursor: '',
        noErrors: true,
        containsColRefKeywords: true,
        containsKeywords: ['WHERE', 'ORDER BY'],
        doesNotContainKeywords: ['FROM'],
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest columns for "FROM baa.boo SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo SELECT ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }]
          },
          suggestAnalyticFunctions: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }, { name: 'boo' }] }] }
        }
      });
    });

    it('should suggest keywords for "FROM baa.boo SELECT c, d |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM baa.boo SELECT c, d ',
        afterCursor: '',
        noErrors: true,
        containsColRefKeywords: true,
        containsKeywords: ['WHERE', 'ORDER BY'],
        doesNotContainKeywords: ['FROM'],
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'baa' }, { name: 'boo' }, { name: 'd' }] }
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

    it('should suggest keywords for "INSERT INTO TABLE baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'VALUES', 'SELECT']
        }
      });
    });

    it('should suggest columns for "INSERT INTO TABLE baa PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
        }
      });
    });

    it('should suggest columns for "INSERT INTO TABLE baa PARTITION (a,b) (x, |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'baa' }] }] }
        }
      });
    });

    it('should suggest keywords for "insert into table baa partition (a,b) (x, z) |"', () => {
      assertAutoComplete({
        beforeCursor: 'insert into table baa partition (a,b) (x, z) ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest columns for "INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestTables: { prependFrom: true, prependQuestionMark: true },
          suggestDatabases: { prependFrom: true, prependQuestionMark: true, appendDot: true }
        }
      });
    });

    it('should suggest columns for "INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestTables: { prependFrom: true, prependQuestionMark: true },
          suggestDatabases: { prependFrom: true, prependQuestionMark: true, appendDot: true }
        }
      });
    });

    it('should suggest keywords for "INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT INTO TABLE baa PARTITION (a,b) (x, z) SELECT c, d ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['AS', 'IN'],
        expectedResult: {
          lowerCase: false,
          suggestTables: { prependFrom: true },
          suggestDatabases: { prependFrom: true, appendDot: true }
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
          suggestKeywords: ['DIRECTORY', 'LOCAL DIRECTORY', 'TABLE']
        }
      });
    });

    it('should suggest tables for "INSERT OVERWRITE LOCAL |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE LOCAL ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DIRECTORY']
        }
      });
    });

    it('should suggest hdfs for "INSERT OVERWRITE DIRECTORY \'|"', () => {
      assertAutoComplete({
        beforeCursor: "INSERT OVERWRITE DIRECTORY '",
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE DIRECTORY \'blabla\' |"', () => {
      assertAutoComplete({
        beforeCursor: "INSERT OVERWRITE DIRECTORY 'blabla' ",
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE bla.ble |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'SELECT']
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE bla.ble |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'SELECT']
        }
      });
    });

    it('should suggest columns for "INSERT OVERWRITE bla.ble PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bla' }, { name: 'ble' }] }] }
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS', 'SELECT']
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest columns for "INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble PARTITION (a, b) IF NOT EXISTS SELECT ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestTables: { prependFrom: true, prependQuestionMark: true },
          suggestDatabases: { prependFrom: true, prependQuestionMark: true, appendDot: true }
        }
      });
    });

    it('should suggest keywords for "INSERT OVERWRITE bla.ble SELECT c, d |"', () => {
      assertAutoComplete({
        beforeCursor: 'INSERT OVERWRITE bla.ble SELECT c, d ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['AS', 'IN'],
        expectedResult: {
          lowerCase: false,
          suggestTables: { prependFrom: true },
          suggestDatabases: { prependFrom: true, appendDot: true }
        }
      });
    });

    it('should suggest identifier for "WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT INTO tab SELECT * FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 AS (SELECT 1), t2 AS (SELECT 2) INSERT INTO tab SELECT * FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
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
  });

  describe('MERGE', () => {
    it(
      'should handle "MERGE INTO target AS T USING source AS S ON T.col = S.col ' +
        ' WHEN MATCHED AND (S.col2 IS NOT NULL) THEN UPDATE SET col2 = S.col' +
        ' WHEN MATCHED AND S.col2 IS NULL THEN DELETE' +
        ' WHEN NOT MATCHED THEN INSERT VALUES (S.col, S.col2);"',
      () => {
        assertAutoComplete({
          beforeCursor:
            'MERGE INTO target AS T USING source AS S ON T.col = S.col\n' +
            ' WHEN MATCHED AND (S.col2 IS NOT NULL) THEN UPDATE SET col2 = S.col\n' +
            ' WHEN MATCHED AND S.col2 IS NULL THEN DELETE\n' +
            ' WHEN NOT MATCHED THEN INSERT VALUES (S.col, S.col2);',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['MERGE'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "MERGE |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO']
        }
      });
    });

    it('should suggest tables for "MERGE INTO |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: true },
          suggestTables: {}
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS T USING']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['T USING']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['USING']
        }
      });
    });

    it('should suggest tables for "MERGE INTO tbl AS T USING |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: true },
          suggestTables: {}
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING (|"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS S ON']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['S ON']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS S ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON']
        }
      });
    });

    it('should suggest columns for "MERGE INTO tbl AS T USING db.tbl2 AS S ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS S ON ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['CASE', 'EXISTS', 'NOT', 'NULL'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'db' }, { name: 'tbl2' }], alias: 'S' },
              { identifierChain: [{ name: 'tbl' }], alias: 'T' }
            ]
          },
          suggestFunctions: {},
          suggestIdentifiers: [
            { name: 'S.', type: 'alias' },
            { name: 'T.', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar  ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['WHEN', 'OR'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['MATCHED', 'NOT MATCHED']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN NOT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['MATCHED']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AND', 'THEN']
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED AND (S.col2 IS NOT NULL) |"', () => {
      assertAutoComplete({
        beforeCursor:
          'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED AND (S.col2 IS NOT NULL) ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['AND', 'THEN'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN |"', () => {
      assertAutoComplete({
        beforeCursor: 'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DELETE', 'INSERT VALUES', 'UPDATE SET']
        }
      });
    });

    it('should suggest columns for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET |"', () => {
      assertAutoComplete({
        beforeCursor:
          'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'db' }, { name: 'tbl2' }], alias: 'S' },
              { identifierChain: [{ name: 'tbl' }], alias: 'T' }
            ]
          },
          suggestIdentifiers: [
            { name: 'S.', type: 'alias' },
            { name: 'T.', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b |"', () => {
      assertAutoComplete({
        beforeCursor:
          'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WHEN']
        }
      });
    });

    it('should not suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN NOT MATCHED THEN UPDATE SET a = b |"', () => {
      assertAutoComplete({
        beforeCursor:
          'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN NOT MATCHED THEN UPDATE SET a = b ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN MATCHED AND a = b THEN |"', () => {
      assertAutoComplete({
        beforeCursor:
          'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN MATCHED AND a = b THEN ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DELETE', 'INSERT VALUES']
        }
      });
    });

    it(
      'should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN MATCHED AND a = b THEN DELETE ' +
        'WHEN MATCHED THEN |"',
      () => {
        assertAutoComplete({
          beforeCursor:
            'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN MATCHED AND a = b THEN DELETE ' +
            'WHEN MATCHED THEN ',
          afterCursor: '',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INSERT VALUES']
          }
        });
      }
    );

    it(
      'should suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN MATCHED AND a = b THEN DELETE ' +
        'WHEN MATCHED THEN |"',
      () => {
        assertAutoComplete({
          beforeCursor:
            'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN MATCHED AND a = b THEN DELETE ' +
            'WHEN MATCHED THEN INSERT ',
          afterCursor: '',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['VALUES']
          }
        });
      }
    );

    it('should not suggest keywords for "MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN NOT MATCHED AND a = b THEN DELETE |"', () => {
      assertAutoComplete({
        beforeCursor:
          'MERGE INTO tbl AS T USING db.tbl2 AS S ON T.foo = S.bar WHEN MATCHED THEN UPDATE SET a = b WHEN NOT MATCHED AND a = b THEN DELETE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });
});
