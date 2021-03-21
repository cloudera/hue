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

describe('impalaAutocompleteParser.js ALTER statements', () => {
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

  describe('ALTER DATABASE', () => {
    it('should handle "ALTER DATABASE db SET OWNER USER usr;|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER DATABASE db SET OWNER USER usr;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER DATABASE db SET OWNER ROLE usr;|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER DATABASE db SET OWNER ROLE usr;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER DATABASE boo SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER DATABASE boo SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OWNER']
        }
      });
    });

    it('should suggest keywords for "ALTER DATABASE boo SET OWNER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER DATABASE boo SET OWNER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE', 'USER']
        }
      });
    });
  });

  describe('ALTER TABLE', () => {
    it('should handle "ALTER TABLE foo ALTER COLUMN bar SET COMMENT \'boo\'; |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE foo ALTER COLUMN bar SET COMMENT 'boo'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE foo ALTER bar DROP DEFAULT; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE foo ALTER bar DROP DEFAULT;  ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE bar SET ROW FORMAT ... |"', () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar SET ROW FORMAT DELIMITED FIELDS TERMINATED BY 'a' ESCAPED BY 'c' " +
          "LINES TERMINATED BY 'q'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER ',
        afterCursor: '',
        containsKeywords: ['TABLE', 'DATABASE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "ALTER TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "ALTER TABLE foo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE foo.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'foo' }], onlyTables: true }
        }
      });
    });

    it("should handle \"ALTER TABLE db.tbl SET COLUMN STATS foo ('numDVs'='2','numNulls'='0'); |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE db.tbl SET COLUMN STATS foo ('numDVs'='2','numNulls'='0'); ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE db.tbl SET OWNER USER boo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE db.tbl SET OWNER USER boo; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest databases for "ALTER TABLE db.tbl RENAME TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE db.tbl RENAME TO  ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should handle "alter table d2.mobile rename to d3.mobile;|"', () => {
      assertAutoComplete({
        beforeCursor: 'alter table d2.mobile rename to d3.mobile;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it('should handle "alter table p1 partition (month=1, day=1) set location \'/usr/external_data/new_years_day\';|"', () => {
      assertAutoComplete({
        beforeCursor:
          "alter table p1 partition (month=1, day=1) set location '/usr/external_data/new_years_day';",
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it('should handle "alter table sales_data add partition (zipcode = cast(9021 * 10 as string));|"', () => {
      assertAutoComplete({
        beforeCursor: 'alter table sales_data add partition (zipcode = cast(9021 * 10 as string));',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it("should handle \"ALTER TABLE table_name SET TBLPROPERTIES('EXTERNAL'='FALSE');|\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE table_name SET TBLPROPERTIES('EXTERNAL'='FALSE');",
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ADD COLUMNS',
            'ADD PARTITION',
            'ADD RANGE PARTITION',
            'ALTER',
            'ALTER COLUMN',
            'CHANGE',
            'DROP COLUMN',
            'DROP PARTITION',
            'DROP RANGE PARTITION',
            'PARTITION',
            'RECOVER PARTITIONS',
            'RENAME TO',
            'REPLACE COLUMNS',
            'SET CACHED IN',
            'SET COLUMN STATS',
            'SET FILEFORMAT',
            'SET LOCATION',
            'SET OWNER',
            'SET ROW FORMAT',
            'SET SERDEPROPERTIES',
            'SET TBLPROPERTIES',
            'SET UNCACHED'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'CACHED IN',
            'COLUMN STATS',
            'FILEFORMAT',
            'LOCATION',
            'OWNER ROLE',
            'OWNER USER',
            'ROW FORMAT',
            'SERDEPROPERTIES',
            'TBLPROPERTIES',
            'UNCACHED'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET COLUMN |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET COLUMN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['STATS']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar SET COLUMN STATS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET COLUMN STATS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should handle "ALTER TABLE db.tbl SET COLUMN STATS foo (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE db.tbl SET COLUMN STATS foo (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestIdentifiers: ["'avgSize'", "'maxSize'", "'numDVs'", "'numNulls'"]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ALTER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ALTER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] },
          suggestKeywords: ['COLUMN']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ALTER foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ALTER foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'DROP DEFAULT',
            'SET BLOCK_SIZE',
            'SET COMMENT',
            'SET COMPRESSION',
            'SET DEFAULT',
            'SET ENCODING'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ALTER foo SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ALTER foo SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BLOCK_SIZE', 'COMMENT', 'COMPRESSION', 'DEFAULT', 'ENCODING']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ALTER foo DROP |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ALTER foo DROP ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DEFAULT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS', 'COLUMNS', 'PARTITION', 'RANGE PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD IF NOT EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'RANGE PARTITION']
        }
      });
    });

    it('should handle "ALTER TABLE bar ADD RANGE PARTITION VALUE = \'A\';|"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar ADD RANGE PARTITION VALUE = 'A';",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD RANGE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD RANGE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD RANGE PARTITION |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD RANGE PARTITION ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VALUE']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD RANGE PARTITION VALUE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD RANGE PARTITION VALUE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD RANGE PARTITION 1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD RANGE PARTITION 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['<', '<=', '<>', '=', '>', '>=']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD RANGE PARTITION 1 < |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD RANGE PARTITION 1 < ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VALUES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD RANGE PARTITION 1 < VALUES |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD RANGE PARTITION 1 < VALUES ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['<', '<=', '<>', '=', '>', '>=']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (a INT, b |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD COLUMNS (a INT, b ',
        afterCursor: '',
        containsKeywords: ['INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar ADD PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should handle "ALTER TABLE bar ADD PARTITION (a=1) LOCATION \'/bla\' UNCACHED; |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar ADD PARTITION (a=1) LOCATION '/bla' UNCACHED; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"ALTER TABLE bar ADD IF NOT EXISTS PARTITION (a=1) LOCATION '/bla' CACHED IN 'boo' WITH REPLICATION = 2; |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (a=1) LOCATION '/bla' CACHED IN 'boo' WITH REPLICATION = 2; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD PARTITION (a=1) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD PARTITION (a=1) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CACHED IN', 'LOCATION', 'UNCACHED']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD PARTITION (a=1) CACHED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD PARTITION (a=1) CACHED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IN']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD PARTITION (a=1) CACHED IN \'boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar ADD PARTITION (a=1) CACHED IN 'boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH REPLICATION =']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar CHANGE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CHANGE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CHANGE foo bar |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CHANGE foo bar ',
        afterCursor: '',
        containsKeywords: ['INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] },
          suggestKeywords: ['IF EXISTS', 'COLUMN', 'PARTITION', 'RANGE PARTITION']
        }
      });
    });

    // TODO: Should suggest partitions
    it('should suggest columns for "ALTER TABLE bar DROP PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP IF EXISTS PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF EXISTS PARTITION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP RANGE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP RANGE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP IF EXISTS RANGE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF EXISTS RANGE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP IF EXISTS RANGE PARTITION |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF EXISTS RANGE PARTITION ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VALUE']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP IF EXISTS RANGE PARTITION VALUE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF EXISTS RANGE PARTITION VALUE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP IF EXISTS RANGE PARTITION "a" |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF EXISTS RANGE PARTITION "a" ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['<', '<=', '<>', '=', '>', '>=']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar DROP RANGE PARTITION "a" < |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP RANGE PARTITION "a" < ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VALUES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'SET CACHED IN',
            'SET FILEFORMAT',
            'SET LOCATION',
            'SET ROW FORMAT',
            'SET SERDEPROPERTIES',
            'SET TBLPROPERTIES',
            'SET UNCACHED'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') SET |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') SET ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'CACHED IN',
            'FILEFORMAT',
            'LOCATION',
            'ROW FORMAT',
            'SERDEPROPERTIES',
            'TBLPROPERTIES',
            'UNCACHED'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') SET CACHED |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') SET CACHED ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IN']
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar PARTITION (a='b') SET CACHED IN 'boo' |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') SET CACHED IN 'boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH REPLICATION =']
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar PARTITION (a='b') SET CACHED IN 'boo' WITH |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') SET CACHED IN 'boo' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REPLICATION =']
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar PARTITION (a='b') SET CACHED IN 'boo' WITH REPLICATION |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') SET CACHED IN 'boo' WITH REPLICATION ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') SET FILEFORMAT |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') SET FILEFORMAT ",
        afterCursor: '',
        containsKeywords: ['PARQUET'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should suggest hdfs for \"ALTER TABLE bar PARTITION (a='b') SET LOCATION '|\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (a='b') SET LOCATION '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET OWNER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET OWNER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET ROW |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET ROW ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FORMAT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET ROW FORMAT |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET ROW FORMAT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DELIMITED']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET ROW FORMAT DELIMITED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET ROW FORMAT DELIMITED ',
        afterCursor: '',
        containsKeywords: ['FIELDS TERMINATED BY', 'LINES TERMINATED BY'],
        doestNotContainKeywords: ['ROW FORMAT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET ROW FORMAT DELIMITED FIELDS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET ROW FORMAT DELIMITED FIELDS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TERMINATED BY']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET ROW FORMAT DELIMITED FIELDS TERMINATED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET ROW FORMAT DELIMITED FIELDS TERMINATED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET ROW FORMAT DELIMITED FIELDS TERMINATED BY \'b\' |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar SET ROW FORMAT DELIMITED FIELDS TERMINATED BY 'b' ",
        afterCursor: '',
        containsKeywords: ['LINES TERMINATED BY'],
        doestNotContainKeywords: ['FIELDS TERMINATED BY', 'ROW FORMAT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET ROW FORMAT DELIMITED LINES TERMINATED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET ROW FORMAT DELIMITED LINES TERMINATED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar RECOVER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar RECOVER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITIONS']
        }
      });
    });
  });

  describe('ALTER VIEW', () => {
    it('should handle "ALTER VIEW baa.boo AS SELECT * FROM bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW baa.boo AS SELECT * FROM bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER ',
        afterCursor: '',
        containsKeywords: ['VIEW'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest views for "ALTER VIEW |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyViews: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest views for "ALTER VIEW boo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }], onlyViews: true }
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo ',
        afterCursor: '',
        containsKeywords: ['AS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW baa.boo AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW baa.boo AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest databases for "ALTER VIEW baa.boo AS SELECT * FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW baa.boo AS SELECT * FROM ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest handle "ALTER VIEW bloo.boo RENAME TO baa.bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW bloo.boo RENAME TO baa.bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER VIEW db.foo SET OWNER ROLE boo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW db.tbl SET OWNER ROLE boo; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS', 'RENAME TO', 'SET OWNER']
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW boo RENAME |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo RENAME ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO']
        }
      });
    });

    it('should suggest databases for "ALTER VIEW boo RENAME TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo RENAME TO ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW boo SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OWNER ROLE', 'OWNER USER']
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW db.boo SET OWNER|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW db.boo SET OWNER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE', 'USER']
        }
      });
    });
  });

  describe('COMMENT ON', () => {
    it('should handle "COMMENT ON DATABASE boo IS \'foo\';|"', () => {
      assertAutoComplete({
        beforeCursor: "COMMENT ON DATABASE boo IS 'foo';",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "COMMENT ON DATABASE boo IS NULL;|"', () => {
      assertAutoComplete({
        beforeCursor: 'COMMENT ON DATABASE boo IS NULL;',
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
        containsKeywords: ['COMMENT ON'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "comment |"', () => {
      assertAutoComplete({
        beforeCursor: 'comment ',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['ON DATABASE']
        }
      });
    });

    it('should suggest keywords for "comment on |"', () => {
      assertAutoComplete({
        beforeCursor: 'comment on ',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['DATABASE']
        }
      });
    });

    it('should suggest datagbase for "COMMENT ON DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMMENT ON DATABASE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest keywords for "COMMENT ON DATABASE bar |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMMENT ON DATABASE bar ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IS']
        }
      });
    });

    it('should suggest keywords for "COMMENT ON DATABASE bar IS |"', () => {
      assertAutoComplete({
        beforeCursor: 'COMMENT ON DATABASE bar IS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NULL']
        }
      });
    });
  });
});
