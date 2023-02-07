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

import hiveAutocompleteParser from '../hiveAutocompleteParser';

describe('hiveAutocompleteParser.js ALTER statements', () => {
  beforeAll(() => {
    hiveAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      hiveAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  describe('ALTER CONNECTOR', () => {
    it('should handle "ALTER CONNECTOR foo SET URL \'banana\'; |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER CONNECTOR foo SET URL 'banana'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER CONNECTOR foo SET OWNER banana; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER CONNECTOR foo SET OWNER banana; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"ALTER CONNECTOR foo SET DCPROPERTIES ('foo'='bar'); |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER CONNECTOR foo SET  DCPROPERTIES ('foo'='bar'); ",
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
        containsKeywords: ['CONNECTOR'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER CONNECTOR foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER CONNECTOR foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SET DCPROPERTIES', 'SET OWNER', 'SET URL']
        }
      });
    });

    it('should suggest keywords for "ALTER CONNECTOR foo SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER CONNECTOR foo SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DCPROPERTIES', 'OWNER', 'URL']
        }
      });
    });

    it('should suggest keywords for "ALTER CONNECTOR foo SET OWNER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER CONNECTOR foo SET OWNER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE', 'USER']
        }
      });
    });
  });

  describe('ALTER DATABASE', () => {
    it("should handle \"ALTER DATABASE baa SET DBPROPERTIES ('boo'=1, 'baa'=2); |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER DATABASE baa SET DBPROPERTIES ('boo'=1, 'baa'=2); ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER SCHEMA baa SET OWNER ROLE boo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER SCHEMA baa SET OWNER ROLE boo; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER DATABASE baa SET LOCATION \'/baa/boo\'; |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER DATABASE baa SET LOCATION '/baa/boo'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER DATABASE baa SET MANAGEDLOCATION \'/baa/boo\'; |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER DATABASE baa SET MANAGEDLOCATION '/baa/boo'; ",
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
        containsKeywords: ['DATABASE', 'SCHEMA'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest databases for "ALTER DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER DATABASE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest databases for "ALTER SCHEMA |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER SCHEMA ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest keywords for "ALTER SCHEMA boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER SCHEMA boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SET DBPROPERTIES', 'SET LOCATION', 'SET MANAGEDLOCATION', 'SET OWNER']
        }
      });
    });

    it('should suggest keywords for "ALTER DATABASE boo SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER DATABASE boo SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DBPROPERTIES', 'LOCATION', 'MANAGEDLOCATION', 'OWNER']
        }
      });
    });

    it('should suggest keywords for "ALTER DATABASE boo SET OWNER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER DATABASE boo SET OWNER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest hdfs for "ALTER DATABASE boo SET LOCATION \'/|"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER DATABASE boo SET LOCATION '/",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/' }
        }
      });
    });

    it('should suggest hdfs for "ALTER DATABASE boo SET MANAGEDLOCATION \'/|"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER DATABASE boo SET MANAGEDLOCATION '/",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/' }
        }
      });
    });
  });

  describe('ALTER INDEX', () => {
    it('should handle "ALTER INDEX baa ON boo.ba PARTITION (bla=1) REBUILD; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER INDEX baa ON boo.ba PARTITION (bla=1) REBUILD; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER INDEX |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER ',
        afterCursor: '',
        containsKeywords: ['INDEX'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER INDEX boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER INDEX boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON']
        }
      });
    });

    it('should suggest tables for "ALTER INDEX boo ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER INDEX boo ON ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "ALTER INDEX boo ON bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER INDEX boo ON bla ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'REBUILD']
        }
      });
    });

    it('should suggest keywords for "ALTER INDEX boo ON bla PARTITION (baa = 1) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER INDEX boo ON bla PARTITION (baa = 1) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REBUILD']
        }
      });
    });
  });

  describe('ALTER MATERIALIZED VIEW', () => {
    it('should handle "ALTER MATERIALIZED VIEW baa.boo ENABLE REWRITE;|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER MATERIALIZED VIEW baa.boo ENABLE REWRITE;;',
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
        containsKeywords: ['MATERIALIZED VIEW'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER MATERIALIZED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER MATERIALIZED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VIEW']
        }
      });
    });

    it('should suggest views for "ALTER MATERIALIZED VIEW |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER MATERIALIZED VIEW ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyViews: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest views for "ALTER MATERIALIZED VIEW boo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER MATERIALIZED VIEW boo.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }], onlyViews: true }
        }
      });
    });

    it('should suggest keywords for "ALTER MATERIALIZED VIEW boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER MATERIALIZED VIEW boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DISABLE REWRITE', 'ENABLE REWRITE']
        }
      });
    });

    it('should suggest keywords for "ALTER MATERIALIZED VIEW boo.foo DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER MATERIALIZED VIEW boo.foo DISABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REWRITE']
        }
      });
    });
  });

  describe('ALTER TABLE', () => {
    it('should handle "ALTER TABLE foo SET PARTITION SPEC (month(ts)); |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE foo SET PARTITION SPEC (month(ts)); ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE default.part_test SET PARTITION SPEC(year(year_field), month(month_field), day(day_field)); |"', () => {
      assertAutoComplete({
        beforeCursor:
          'ALTER TABLE default.part_test SET PARTITION SPEC(year(year_field), month(month_field), day(day_field)); ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE default.customers ADD COLUMNS (newintcol int, newstringcol string COMMENT \'Column with description\'); |"', () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE default.customers ADD COLUMNS (newintcol int, newstringcol string COMMENT 'Column with description'); ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE default.customers CHANGE COLUMN last_name family_name string COMMENT \'This is family name\'; |"', () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE default.customers CHANGE COLUMN last_name family_name string COMMENT 'This is family name'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE customers CHANGE COLUMN last_name family_name string AFTER customer_id; |"', () => {
      assertAutoComplete({
        beforeCursor:
          'ALTER TABLE customers CHANGE COLUMN last_name family_name string AFTER customer_id; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE customers CHANGE COLUMN family_name family_name string FIRST; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE customers CHANGE COLUMN family_name family_name string FIRST; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE customers UPDATE COLUMNS; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE customers UPDATE COLUMNS; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"ALTER TABLE customers UNSET TBLPROPERTIES('dummy'='dummy'); |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE customers UNSET TBLPROPERTIES('dummy'='dummy'); ",
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
        containsKeywords: ['TABLE'],
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

    it('should handle "ALTER TABLE foo PARTITION (ds=\'2008-04-08\', hr) CHANGE COLUMN dec_column_name dec_column_name DECIMAL; |"', () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE foo PARTITION (ds='2008-04-08', hr) CHANGE COLUMN dec_column_name dec_column_name DECIMAL; ",
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"ALTER TABLE page_view DROP PARTITION (dt='2008-08-08', country='us'); |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE page_view DROP PARTITION (dt='2008-08-08', country='us'); ",
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"ALTER TABLE page_view ADD PARTITION (dt='2008-08-08', country='us') location '/path/to/us/part080808'\nPARTITION (dt='2008-08-09', country='us') location '/path/to/us/part080809'; |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE page_view ADD PARTITION (dt='2008-08-08', country='us') location '/path/to/us/part080808'\nPARTITION (dt='2008-08-09', country='us') location '/path/to/us/part080809'; ",
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "ALTER TABLE bar SET OWNER ROLE boo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET OWNER ROLE boo; ',
        afterCursor: '',
        noErrors: true,
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
            'ADD IF NOT EXISTS',
            'ADD PARTITION',
            'ARCHIVE PARTITION',
            'CHANGE',
            'CLUSTERED BY',
            'COMPACT',
            'CONCATENATE',
            'DISABLE NO_DROP',
            'DISABLE OFFLINE',
            'DROP',
            'ENABLE NO_DROP',
            'ENABLE OFFLINE',
            'EXCHANGE PARTITION',
            'NOT SKEWED',
            'NOT STORED AS DIRECTORIES',
            'PARTITION',
            'RECOVER PARTITIONS',
            'RENAME TO',
            'REPLACE COLUMNS',
            'SET FILEFORMAT',
            'SET LOCATION',
            'SET OWNER',
            'SET PARTITION SPEC',
            'SET SERDE',
            'SET SERDEPROPERTIES',
            'SET SKEWED LOCATION',
            'SET TBLPROPERTIES',
            'SKEWED BY',
            'TOUCH',
            'UNARCHIVE PARTITION',
            'UNSET SERDEPROPERTIES',
            'UNSET TBLPROPERTIES',
            'UPDATE COLUMNS'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS', 'COLUMNS', 'CONSTRAINT', 'PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD COLUMNS (boo ',
        afterCursor: '',
        containsKeywords: ['INT', 'INTEGER', 'STRUCT<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD COLUMNS (boo INT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'DEFAULT', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE', 'COMMENT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo INT) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD COLUMNS (boo INT) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE', 'RESTRICT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'FOREIGN KEY', 'PRIMARY KEY', 'UNIQUE']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo FOREIGN |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo FOREIGN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['KEY']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo FOREIGN KEY (bla) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo FOREIGN KEY (bla) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REFERENCES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOVALIDATE', 'DISABLE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) DISABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOVALIDATE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) DISABLE NOVALIDATE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) DISABLE NOVALIDATE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD IF NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD IF NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ADD IF NOT EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08', country='us') |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08', country='us')  ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LOCATION', 'PARTITION']
        }
      });
    });

    it("should suggest hdfs for \"ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08', country='us') LOCATION '|\"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08', country='us') LOCATION '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar ADD PARTITION (dt=\'2008-08-08\', |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08', ",
        afterCursor: '',
        expectedResult: {
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] },
          lowerCase: false
        }
      });
    });

    it("should suggest columns for \"ALTER TABLE bar ADD PARTITION (dt='2008-08-08') LOCATION '/boo' PARTITION (|\"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08') LOCATION '/boo' PARTITION  (",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar ADD PARTITION (dt='2008-08-08') LOCATION '/boo' PARTITION (baa=1) \"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08') LOCATION '/boo' PARTITION (baa=1) ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LOCATION', 'PARTITION']
        }
      });
    });

    it("should suggest hdfs for \"ALTER TABLE bar ADD PARTITION (dt='2008-08-08') LOCATION '/boo' PARTITION (country='us') LOCATION '\"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt='2008-08-08') LOCATION '/boo' PARTITION (country='us') LOCATION '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar ARCHIVE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar ARCHIVE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar CHANGE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CHANGE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] },
          suggestKeywords: ['COLUMN']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CHANGE boo baa ',
        afterCursor: '',
        containsKeywords: ['ARRAY<>', 'INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CHANGE boo baa INT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'CHECK',
            'DEFAULT',
            'NOT NULL',
            'PRIMARY KEY',
            'UNIQUE',
            'COMMENT',
            'AFTER',
            'FIRST',
            'CASCADE',
            'RESTRICT'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa INT COMMENT \'ble\' |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar CHANGE boo baa INT COMMENT 'ble' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AFTER', 'FIRST', 'CASCADE', 'RESTRICT']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar CHANGE boo baa INT COMMENT \'ble\' AFTER |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar CHANGE boo baa INT COMMENT 'ble' AFTER ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CHANGE COLUMN boo baa INT AFTER ba |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CHANGE COLUMN boo baa INT AFTER ba ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE', 'RESTRICT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CLUSTERED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar CLUSTERED BY (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED BY (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar CLUSTERED BY (a, b, |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED BY (a, b, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CLUSTERED BY (a, b, c) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED BY (a, b, c) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SORTED BY', 'INTO']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CLUSTERED BY (a, b, c) INTO 10 |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED BY (a, b, c) INTO 10 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BUCKETS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar CLUSTERED BY (a, b, c) SORTED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED BY (a, b, c) SORTED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE foo.bar CLUSTERED BY (a, b, c) SORTED BY (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE foo.bar CLUSTERED BY (a, b, c) SORTED BY (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'foo' }, { name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE foo.bar CLUSTERED BY (a, b, c) SORTED BY (a) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED BY (a, b, c) SORTED BY (a) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE foo.bar CLUSTERED BY (a, b, c) SORTED BY (a) INTO 10 |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar CLUSTERED BY (a, b, c) SORTED BY (a) INTO 10 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BUCKETS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar DROP |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF EXISTS', 'CONSTRAINT', 'PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar DROP IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar DROP IF EXISTS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar DROP IF EXISTS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    // TODO: Suggest partitions
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

    it('should suggest keywords for "ALTER TABLE bar DROP IF EXISTS PARTITION (a=\'baa\'), |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar DROP IF EXISTS PARTITION (a='baa'), ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar DROP PARTITION (a=\'baa\') |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar DROP PARTITION (a='baa') ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PURGE']
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar DROP PARTITION (a='baa'), PARTITION (b='boo') |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar DROP PARTITION (a='baa'), PARTITION (b='boo') ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PURGE']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar EXCHANGE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar EXCHANGE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar EXCHANGE PARTITION (boo=\'baa\') |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar EXCHANGE PARTITION (boo='baa') ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH TABLE']
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar EXCHANGE PARTITION ((boo='baa'), (baa='boo')) |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar EXCHANGE PARTITION ((boo='baa'), (baa='boo')) ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH TABLE']
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar EXCHANGE PARTITION ((boo='baa'), (baa='boo')) WITH |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar EXCHANGE PARTITION ((boo='baa'), (baa='boo')) WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it("should suggest tables for \"ALTER TABLE bar EXCHANGE PARTITION ((boo='baa'), (baa='boo')) WITH TABLE |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar EXCHANGE PARTITION ((boo='baa'), (baa='boo')) WITH TABLE ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SKEWED', 'STORED AS DIRECTORIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar NOT STORED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar NOT STORED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS DIRECTORIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar NOT STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar NOT STORED AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DIRECTORIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ADD COLUMNS',
            'CHANGE',
            'COMPACT',
            'CONCATENATE',
            'DISABLE NO_DROP',
            'DISABLE OFFLINE',
            'ENABLE NO_DROP',
            'ENABLE OFFLINE',
            'RENAME TO PARTITION',
            'REPLACE COLUMNS',
            'SET FILEFORMAT',
            'SET LOCATION',
            'SET SERDE',
            'SET SERDEPROPERTIES',
            'UNSET SERDEPROPERTIES'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar COMPACT \'boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar COMPACT 'boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AND WAIT', 'WITH OVERWRITE TBLPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar COMPACT \'boo\' AND |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar COMPACT 'boo' AND ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WAIT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar COMPACT \'boo\' WITH |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar COMPACT 'boo' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OVERWRITE TBLPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar COMPACT \'boo\' WITH OVERWRITE |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar COMPACT 'boo' WITH OVERWRITE ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TBLPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') ADD ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COLUMNS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') ADD COLUMNS (boo ",
        afterCursor: '',
        containsKeywords: ['INT', 'STRUCT<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo INT |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') ADD COLUMNS (boo INT ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'DEFAULT', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE', 'COMMENT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo INT) |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') ADD COLUMNS (boo INT) ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE', 'RESTRICT']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] },
          suggestKeywords: ['COLUMN']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col1, col2) CHANGE boo baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar PARTITION (col1, col2) CHANGE boo baa ',
        afterCursor: '',
        containsKeywords: ['ARRAY<>', 'INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE boo baa ",
        afterCursor: '',
        containsKeywords: ['ARRAY<>', 'INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'CHECK',
            'DEFAULT',
            'NOT NULL',
            'PRIMARY KEY',
            'UNIQUE',
            'COMMENT',
            'AFTER',
            'FIRST',
            'CASCADE',
            'RESTRICT'
          ]
        }
      });
    });

    it("should suggest keywords for \"ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT COMMENT 'ble' |\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT COMMENT 'ble' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AFTER', 'FIRST', 'CASCADE', 'RESTRICT']
        }
      });
    });

    it("should suggest columns for \"ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT COMMENT 'ble' AFTER |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT COMMENT 'ble' AFTER ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE COLUMN boo baa INT AFTER ba |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE COLUMN boo baa INT AFTER ba ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE', 'RESTRICT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') DISABLE ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NO_DROP', 'OFFLINE']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') DISABLE NO_DROP |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') DISABLE NO_DROP ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ENABLE |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') ENABLE ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NO_DROP', 'OFFLINE']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') RENAME |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') RENAME ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') RENAME TO |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') RENAME TO ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') REPLACE ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COLUMNS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') REPLACE COLUMNS (boo ",
        afterCursor: '',
        containsKeywords: ['INT', 'STRUCT<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo INT |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') REPLACE COLUMNS (boo INT ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'DEFAULT', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE', 'COMMENT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo INT) |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') REPLACE COLUMNS (boo INT) ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE', 'RESTRICT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') SET |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') SET ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') SET FILEFORMAT |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') SET FILEFORMAT ",
        afterCursor: '',
        containsKeywords: ['ORC', 'PARQUET'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should suggest hdfs for \"ALTER TABLE bar PARTITION (col='val') SET LOCATION '|\"", () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar PARTITION (col='val') SET LOCATION '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
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

    it('should suggest keywords for "ALTER TABLE bar RENAME |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar RENAME ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar REPLACE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar REPLACE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COLUMNS']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar REPLACE COLUMNS (boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar REPLACE COLUMNS (boo ',
        afterCursor: '',
        containsKeywords: ['INT', 'STRUCT<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar REPLACE COLUMNS (boo INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar REPLACE COLUMNS (boo INT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'DEFAULT', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE', 'COMMENT']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar REPLACE COLUMNS (boo INT) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar REPLACE COLUMNS (boo INT) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CASCADE', 'RESTRICT']
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
            'FILEFORMAT',
            'LOCATION',
            'OWNER',
            'PARTITION SPEC',
            'SERDE',
            'SERDEPROPERTIES',
            'SKEWED LOCATION',
            'TBLPROPERTIES'
          ]
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET PARTITION |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET PARTITION ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SPEC']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET FILEFORMAT |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET FILEFORMAT ',
        afterCursor: '',
        containsKeywords: ['ORC', 'PARQUET'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest hdfs for "ALTER TABLE bar SET LOCATION \'|"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar SET LOCATION '",
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
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET SERDE \'boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar SET SERDE 'boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH SERDEPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET SERDE \'boo\' WITH |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar SET SERDE 'boo' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SERDEPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SET SKEWED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET SKEWED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LOCATION']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar SET SKEWED LOCATION (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SET SKEWED LOCATION (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar SET SKEWED LOCATION (a=\'/boo\', |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE bar SET SKEWED LOCATION (a='/boo', ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SKEWED |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SKEWED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest columns for "ALTER TABLE bar SKEWED BY (|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SKEWED BY (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "ALTER TABLE foo.bar SKEWED BY (a, |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE foo.bar SKEWED BY (a, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'foo' }, { name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SKEWED BY (a, b) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) "', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['STORED AS DIRECTORIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) STORED "', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) STORED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS DIRECTORIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) STORED AS "', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) STORED AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DIRECTORIES']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar TOUCH |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar TOUCH ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar UNARCHIVE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar UNARCHIVE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "ALTER TABLE bar UNSET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE bar UNSET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SERDEPROPERTIES', 'TBLPROPERTIES']
        }
      });
    });
  });

  describe('ALTER VIEW', () => {
    it('should handle "ALTER VIEW baa.boo AS SELECT * FROM bla; |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW baa.boo AS SELECT * FROM bla; ',
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

    it('should handle "ALTER VIEW boo SET TBLPROPERTIES ("baa"=\'boo\'); |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo SET TBLPROPERTIES ("baa"=\'boo\'); ',
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
          suggestKeywords: ['AS', 'SET TBLPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW boo SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo SET ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TBLPROPERTIES']
        }
      });
    });
  });

  describe('MSCK', () => {
    it('should handle "MSCK REPAIR TABLE boo.baa; |"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK REPAIR TABLE boo.baa; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "MSCK REPAIR TABLE boo.baa SYNC PARTITIONS; |"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK REPAIR TABLE boo.baa SYNC PARTITIONS; ',
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
        containsKeywords: ['MSCK'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "MSCK |"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK ',
        afterCursor: '',
        containsKeywords: ['REPAIR TABLE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "MSCK REPAIR |"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK REPAIR ',
        afterCursor: '',
        containsKeywords: ['TABLE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "MSCK REPAIR TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK REPAIR TABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "MSCK REPAIR TABLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK REPAIR TABLE boo ',
        afterCursor: '',
        containsKeywords: ['DROP PARTITIONS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "MSCK REPAIR TABLE boo ADD |"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK REPAIR TABLE boo ADD ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITIONS']
        }
      });
    });
  });

  describe('RELOAD FUNCTION', () => {
    it('should handle "RELOAD FUNCTION; |"', () => {
      assertAutoComplete({
        beforeCursor: 'RELOAD FUNCTION; ',
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
        containsKeywords: ['RELOAD FUNCTION'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "reload |"', () => {
      assertAutoComplete({
        beforeCursor: 'reload ',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['FUNCTION']
        }
      });
    });
  });
});
