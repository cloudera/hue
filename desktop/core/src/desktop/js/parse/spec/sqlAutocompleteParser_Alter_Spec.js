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

describe('sqlAutocompleteParser.js ALTER statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  describe('ALTER DATABASE', () => {
    describe('Hive Specific', () => {
      it("should handle \"ALTER DATABASE baa SET DBPROPERTIES ('boo'=1, 'baa'=2);|\"", () => {
        assertAutoComplete({
          beforeCursor: "ALTER DATABASE baa SET DBPROPERTIES ('boo'=1, 'baa'=2);",
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "ALTER SCHEMA baa SET OWNER ROLE boo;|"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER SCHEMA baa SET OWNER ROLE boo;',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "ALTER DATABASE baa SET LOCATION \'/baa/boo\';|"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER DATABASE baa SET LOCATION '/baa/boo';",
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SET DBPROPERTIES', 'SET LOCATION', 'SET OWNER']
          }
        });
      });

      it('should suggest keywords for "ALTER DATABASE boo SET |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER DATABASE boo SET ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DBPROPERTIES', 'LOCATION', 'OWNER']
          }
        });
      });

      it('should suggest keywords for "ALTER DATABASE boo SET OWNER |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER DATABASE boo SET OWNER ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestHdfs: { path: '/' }
          }
        });
      });
    });

    describe('Impala Specific', () => {
      it('should handle "ALTER DATABASE db SET OWNER USER usr;|"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER DATABASE db SET OWNER USER usr;',
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROLE', 'USER']
          }
        });
      });
    });
  });

  describe('ALTER INDEX', () => {
    it('should handle "ALTER INDEX baa ON boo.ba PARTITION (bla=1) REBUILD;|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER INDEX baa ON boo.ba PARTITION (bla=1) REBUILD;',
        afterCursor: '',
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REBUILD']
        }
      });
    });
  });

  describe('ALTER TABLE', () => {
    it('should handle "ALTER TABLE foo ALTER COLUMN bar SET COMMENT \'boo\'; |"', () => {
      assertAutoComplete({
        beforeCursor: "ALTER TABLE foo ALTER COLUMN bar SET COMMENT 'boo';  ",
        afterCursor: '',
        noErrors: true,
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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

    describe('Hive specific', () => {
      it('should handle "ALTER TABLE foo PARTITION (ds=\'2008-04-08\', hr) CHANGE COLUMN dec_column_name dec_column_name DECIMAL;|"', () => {
        assertAutoComplete({
          beforeCursor:
            "ALTER TABLE foo PARTITION (ds='2008-04-08', hr) CHANGE COLUMN dec_column_name dec_column_name DECIMAL;",
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it("should handle \"ALTER TABLE page_view DROP PARTITION (dt='2008-08-08', country='us');|\"", () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE page_view DROP PARTITION (dt='2008-08-08', country='us');",
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it("should handle \"ALTER TABLE page_view ADD PARTITION (dt='2008-08-08', country='us') location '/path/to/us/part080808'\nPARTITION (dt='2008-08-09', country='us') location '/path/to/us/part080809';|\"", () => {
        assertAutoComplete({
          beforeCursor:
            "ALTER TABLE page_view ADD PARTITION (dt='2008-08-08', country='us') location '/path/to/us/part080808'\nPARTITION (dt='2008-08-09', country='us') location '/path/to/us/part080809';",
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "ALTER TABLE bar SET OWNER ROLE boo;|"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar SET OWNER ROLE boo;',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
              'SET SERDE',
              'SET SERDEPROPERTIES',
              'SET SKEWED LOCATION',
              'SET TBLPROPERTIES',
              'SKEWED BY',
              'TOUCH',
              'UNARCHIVE PARTITION'
            ]
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar ADD ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          containsKeywords: ['INT', 'STRUCT<>'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo INT |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar ADD COLUMNS (boo INT ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo INT) |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar ADD COLUMNS (boo INT) ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CASCADE', 'RESTRICT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo FOREIGN |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo FOREIGN ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['REFERENCES']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo FOREIGN KEY (bla) REFERENCES tbl(col) DISABLE NOVALIDATE |"', () => {
        assertAutoComplete({
          beforeCursor:
            'ALTER TABLE bar ADD CONSTRAINT boo FOREIGN KEY (bla) REFERENCES tbl(col) DISABLE NOVALIDATE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NORELY', 'RELY']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar ADD CONSTRAINT boo PRIMARY KEY (id) ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DISABLE NOVALIDATE']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD IF |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar ADD IF ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT', 'AFTER', 'FIRST', 'CASCADE', 'RESTRICT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa INT COMMENT \'ble\' |"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar CHANGE boo baa INT COMMENT 'ble' ",
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "ALTER TABLE bar CHANGE boo baa INT FIRST |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar CHANGE boo baa INT FIRST ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa INT FIRST ba |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar CHANGE boo baa INT FIRST ba ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CASCADE', 'RESTRICT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar CHANGE COLUMN boo baa INT AFTER ba |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar CHANGE COLUMN boo baa INT AFTER ba ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
              'SET SERDEPROPERTIES'
            ]
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar COMPACT \'boo\' |"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar COMPACT 'boo' ",
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo INT) |"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar PARTITION (col='val') ADD COLUMNS (boo INT) ",
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT', 'AFTER', 'FIRST', 'CASCADE', 'RESTRICT']
          }
        });
      });

      it("should suggest keywords for \"ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT COMMENT 'ble' |\"", () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT COMMENT 'ble' ",
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT FIRST |"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT FIRST ",
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] }
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT FIRST ba |"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE boo baa INT FIRST ba ",
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['CASCADE', 'RESTRICT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE COLUMN boo baa INT AFTER ba |"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar PARTITION (col='val') CHANGE COLUMN boo baa INT AFTER ba ",
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo INT) |"', () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE bar PARTITION (col='val') REPLACE COLUMNS (boo INT) ",
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT']
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar REPLACE COLUMNS (boo INT) |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar REPLACE COLUMNS (boo INT) ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: [
              'FILEFORMAT',
              'LOCATION',
              'OWNER',
              'SERDE',
              'SERDEPROPERTIES',
              'SKEWED LOCATION',
              'TBLPROPERTIES'
            ]
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar SET FILEFORMAT |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar SET FILEFORMAT ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITION']
          }
        });
      });
    });

    describe('Impala specific', () => {
      it("should handle \"ALTER TABLE db.tbl SET COLUMN STATS foo ('numDVs'='2','numNulls'='0'); |\"", () => {
        assertAutoComplete({
          beforeCursor: "ALTER TABLE db.tbl SET COLUMN STATS foo ('numDVs'='2','numNulls'='0'); ",
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: true
          }
        });
      });

      it('should handle "alter table sales_data add partition (zipcode = cast(9021 * 10 as string));|"', () => {
        assertAutoComplete({
          beforeCursor:
            'alter table sales_data add partition (zipcode = cast(9021 * 10 as string));',
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "ALTER TABLE bar ADD PARTITION (a=1) |"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE bar ADD PARTITION (a=1) ',
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['PARTITIONS']
          }
        });
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

    describe('Hive specific', () => {
      it('should handle "ALTER VIEW boo SET TBLPROPERTIES ("baa"=\'boo\');|"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER VIEW boo SET TBLPROPERTIES ("baa"=\'boo\');',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TBLPROPERTIES']
          }
        });
      });
    });

    describe('Impala specific', () => {
      it('should suggest handle "ALTER VIEW bloo.boo RENAME TO baa.bla;|"', () => {
        assertAutoComplete({
          beforeCursor: 'ALTER VIEW bloo.boo RENAME TO baa.bla;',
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROLE', 'USER']
          }
        });
      });
    });
  });

  describe('MSCK', () => {
    it('should handle "MSCK REPAIR TABLE boo.baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'MSCK REPAIR TABLE boo.baa;',
        afterCursor: '',
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });
  });

  describe('RELOAD FUNCTION', () => {
    it('should handle "RELOAD FUNCTION;|"', () => {
      assertAutoComplete({
        beforeCursor: 'RELOAD FUNCTION;',
        afterCursor: '',
        dialect: 'hive',
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
        dialect: 'hive',
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
        dialect: 'hive',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['FUNCTION']
        }
      });
    });
  });

  describe('COMMENT ON', () => {
    it('should handle "COMMENT ON DATABASE boo IS \'foo\';|"', () => {
      assertAutoComplete({
        beforeCursor: "COMMENT ON DATABASE boo IS 'foo';",
        afterCursor: '',
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
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
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NULL']
        }
      });
    });
  });
});
