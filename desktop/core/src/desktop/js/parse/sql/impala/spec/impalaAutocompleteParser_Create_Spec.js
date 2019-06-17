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

describe('impalaAutocompleteParser.js CREATE statements', () => {
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

  it('should handle "CREATE ROLE baaa;|', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE ROLE baaa;',
      afterCursor: '',
      noError: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: [
          'AGGREGATE FUNCTION',
          'DATABASE',
          'EXTERNAL TABLE',
          'FUNCTION',
          'ROLE',
          'SCHEMA',
          'TABLE',
          'VIEW'
        ]
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

    it('should suggest keywords for "CREATE DATABASE foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE DATABASE foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT', 'LOCATION']
        }
      });
    });
  });

  describe('CREATE FUNCTION', () => {
    it("should handle \"CREATE FUNCTION foo.boo(INT, BOOLEAN) RETURNS INT LOCATION '/boo' SYMBOL='baaa'; |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION '/boo' SYMBOL='baaa'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it(
      "should handle \"CREATE AGGREGATE FUNCTION baa.boo(INT, DOUBLE) RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' " +
        "MERGE_FN='cos' PREPARE_FN='cos' CLOSE_FN='cos' SERIALIZE_FN='cos' FINALIZE_FN='cos'; |\"",
      () => {
        assertAutoComplete({
          beforeCursor:
            "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' MERGE_FN='cos' PREPARE_FN='cos' CLOSE_FN='cos' SERIALIZE_FN='cos' FINALIZE_FN='cos'; ",
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it(
      "should handle \"CREATE AGGREGATE FUNCTION baa.boo(INT, DOUBLE) RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' " +
        "MERGE_FN='cos' PREPARE_FN='cos' CLOSE_FN='cos' SERIALIZE_FN='cos' FINALIZE_FN='cos' INTERMEDIATE bigint; |\"",
      () => {
        assertAutoComplete({
          beforeCursor:
            "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' MERGE_FN='cos' PREPARE_FN='cos' CLOSE_FN='cos' SERIALIZE_FN='cos' FINALIZE_FN='cos' INTERMEDIATE bigint; ",
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it('should suggest keywords for "CREATE AGGREGATE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FUNCTION']
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE FUNCTION ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS'],
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE FUNCTION IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION IF NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE FUNCTION IF NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo(|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE FUNCTION boo(',
        afterCursor: '',
        containsKeywords: ['INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE FUNCTION boo() ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['RETURNS']
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS ',
        afterCursor: '',
        containsKeywords: ['INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LOCATION']
        }
      });
    });

    it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INIT_FN', 'UPDATE_FN']
        }
      });
    });

    it("should suggest functions for \"CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='|\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestAnalyticFunctions: true,
          suggestAggregateFunctions: { tables: [] },
          suggestFunctions: {}
        }
      });
    });

    it("should suggest keywords for \"CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['UPDATE_FN']
        }
      });
    });

    it("should suggest functions for \"CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='|\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestAnalyticFunctions: true,
          suggestAggregateFunctions: { tables: [] },
          suggestFunctions: {}
        }
      });
    });

    it("should suggest keywords for \"CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['MERGE_FN']
        }
      });
    });

    it(
      "should suggest keywords for \"CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' MERGE_FN='tan' " +
        "PREPARE_FN='boo' SERIALIZE_FN='baa' |\"",
      () => {
        assertAutoComplete({
          beforeCursor:
            "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION '/boo' INIT_FN='cos' UPDATE_FN='sin' MERGE_FN='tan' PREPARE_FN='boo' SERIALIZE_FN='baa' ",
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FINALIZE_FN', 'INTERMEDIATE']
          }
        });
      }
    );

    it('should suggest keywords for "CREATE FUNCTION |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS'],
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION IF NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION IF NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION boo(',
        afterCursor: '',
        containsKeywords: ['INT'],
        doesNotContainKeywords: ['ARRAY<>', '...'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['...']
        }
      });
    });

    it('should not suggest keywords for "CREATE FUNCTION boo(INT |, BOOLEAN"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION boo(INT ',
        afterCursor: ', BOOLEAN',
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN, |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION  boo(INT, BOOLEAN, ',
        afterCursor: '',
        containsKeywords: ['INT'],
        doesNotContainKeywords: ['ARRAY<>', '...'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN, STRING |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION  boo(INT, BOOLEAN, STRING ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['...']
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['RETURNS']
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) RETURNS ',
        afterCursor: '',
        containsKeywords: ['INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LOCATION']
        }
      });
    });

    it('should suggest hdfs for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION \'|"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION \'/boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION '/boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SYMBOL']
        }
      });
    });
  });

  describe('CREATE ROLE', () => {
    it('should handle "CREATE ROLE boo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE ROLE boo; ',
        afterCursor: '',
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

    it('should handle "CREATE TABLE foo (baa MAP <STRING, STRUCT<id: int>>, arr ARRAY<STRUCT<foo:STRUCT<bar: INT>>>, strc STRUCT<boo:STRING>);|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (baa MAP <STRING, STRUCT<id: int>>, arr ARRAY<STRUCT<foo:STRUCT<bar: INT>>>, strc STRUCT<boo:STRING>);',
        noErrors: true,
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE ... TABLE ... PARTITIONED BY ... ROW FORMAT ... UNCACHED ...;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE IF NOT EXISTS foo.bar ' +
          "(foo int COMMENT 'col_comment', bar int COMMENT 'col_comment') " +
          "PARTITIONED BY (foo int COMMENT 'col_comment', bar int COMMENT 'col_comment') " +
          'SORT BY (foo, bar) ' +
          "COMMENT 'table_comment' " +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'c' ESCAPED BY 'c' " +
          "LINES TERMINATED BY 'c' " +
          "WITH SERDEPROPERTIES ('key1'='value1', 'key2'='value2') " +
          'STORED AS PARQUET ' +
          "LOCATION '/hdfs_path' " +
          'UNCACHED ' +
          "TBLPROPERTIES ('key1'='value1', 'key2'='value2');",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE ... TABLE ... PARTITIONED BY ... ROW FORMAT ... CACHED ...;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE IF NOT EXISTS foo.bar ' +
          "(foo int COMMENT 'col_comment', bar int COMMENT 'col_comment') " +
          "PARTITIONED BY (foo int COMMENT 'col_comment', bar int COMMENT 'col_comment') " +
          'SORT BY (foo, bar) ' +
          "COMMENT 'table_comment' " +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'c' ESCAPED BY 'c' " +
          "LINES TERMINATED BY 'c' " +
          "WITH SERDEPROPERTIES ('key1'='value1', 'key2'='value2') " +
          'STORED AS PARQUET ' +
          "LOCATION '/hdfs_path' " +
          "CACHED IN 'pool_name' WITH REPLICATION = 1 " +
          "TBLPROPERTIES ('key1'='value1', 'key2'='value2');",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE ... TABLE ... PARTITIONED BY ... ROW FORMAT ... AS SELECT ...;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE IF NOT EXISTS foo.bar ' +
          "PARTITIONED BY (foo int COMMENT 'col_comment', bar int COMMENT 'col_comment') " +
          'SORT BY (foo, bar) ' +
          "COMMENT 'table_comment' " +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'c' ESCAPED BY 'c' " +
          "LINES TERMINATED BY 'c' " +
          "WITH SERDEPROPERTIES ('key1'='value1', 'key2'='value2') " +
          'STORED AS PARQUET ' +
          "LOCATION '/hdfs_path' " +
          "CACHED IN 'pool_name' WITH REPLICATION = 1 " +
          "TBLPROPERTIES ('key1'='value1', 'key2'='value2') " +
          'AS SELECT * FROM boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE ... TABLE ... LIKE PARQUET ... PARTITIONED BY ... ROW FORMAT ...;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE IF NOT EXISTS foo.bar ' +
          "LIKE PARQUET '/hdfs_path_of_parquet_file' " +
          "PARTITIONED BY (foo int COMMENT 'col_comment', bar int COMMENT 'col_comment') " +
          'SORT BY (foo, bar) ' +
          "COMMENT 'table_comment' " +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'c' ESCAPED BY 'c' " +
          "LINES TERMINATED BY 'c' " +
          "WITH SERDEPROPERTIES ('key1'='value1', 'key2'='value2') " +
          'STORED AS PARQUET ' +
          "LOCATION '/hdfs_path' " +
          "CACHED IN 'pool_name' WITH REPLICATION = 1 " +
          "TBLPROPERTIES ('key1'='value1', 'key2'='value2');",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE ... TABLE ... PARTITIONED BY ... STORED AS KUDU ...;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE IF NOT EXISTS bar\n' +
          "(foo int NOT NULL COMMENT 'col_comment', bar int BLOCK_SIZE 1 COMMENT 'col_comment', PRIMARY KEY (foo))\n" +
          'PARTITION BY HASH (id) PARTITIONS 3,\n' +
          '  RANGE (year) (PARTITION 1980 <= VALUES < 1990,\n' +
          '    PARTITION 1990 <= VALUES < 2000,\n' +
          '    PARTITION VALUE = 2001,\n' +
          '    PARTITION 2001 < VALUES)\n' +
          "COMMENT 'table_comment'\n" +
          'STORED AS KUDU\n' +
          "TBLPROPERTIES ('key1'='value1', 'key2'='value2');",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LIKE', 'LIKE PARQUET']
        }
      });
    });

    it('should suggest tables for "CREATE TABLE boo LIKE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE boo LIKE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestKeywords: ['PARQUET']
        }
      });
    });

    it('should suggest tables for "CREATE TABLE boo LIKE dbOne.|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE boo LIKE dbOne.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'dbOne' }] }
        }
      });
    });

    it('should suggest hdfs for "CREATE TABLE boo LIKE PARQUET \'|"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE boo LIKE PARQUET '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (baa ',
        afterCursor: '',
        containsKeywords: ['ARRAY<>', 'STRUCT<>', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (baa ARRAY <|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (baa ARRAY <',
        afterCursor: '',
        containsKeywords: ['STRING', 'STRUCT<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (baa MAP <|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (baa MAP <',
        afterCursor: '',
        containsKeywords: ['STRING'],
        doesNotContainKeywords: ['MAP<>', 'STRUCT<>', 'ARRAY<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (baa MAP <STRING, |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (baa ARRAY <',
        afterCursor: '',
        containsKeywords: ['STRING', 'MAP<>', 'STRUCT<>', 'ARRAY<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (baa STRUCT <id:|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (baa STRUCT <id:',
        afterCursor: '',
        containsKeywords: ['INT', 'STRUCT<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) LOCATION \'|"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE boo LOCATION '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo LIKE PARQUET \'/blabla/\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo LIKE PARQUET '/blabla/' ",
        afterCursor: '',
        containsKeywords: ['COMMENT', 'CACHED IN', 'UNCACHED'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) LOCATION \'/baa\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) LOCATION '/baa' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CACHED IN', 'UNCACHED', 'TBLPROPERTIES', 'AS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) PARTITIONED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) PARTITIONED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) PARTITIONED BY (boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) PARTITIONED BY (boo ',
        afterCursor: '',
        containsKeywords: ['INT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) WITH |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) WITH ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SERDEPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) PARTITIONED BY (boo INT, baa BIGINT |, boo INT) AS SELECT * FROM baa;"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) PARTITIONED BY (boo INT, baa BIGINT ',
        afterCursor: ', boo INT) AS SELECT * FROM baa;',
        containsKeywords: ['COMMENT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) PARTITIONED BY (boo INT, baa BIGINT, boo INT) SORT "', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (id int) PARTITIONED BY (boo INT, baa BIGINT, boo INT) SORT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) STORED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) STORED AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AVRO', 'KUDU', 'ORC', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FORMAT']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DELIMITED']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED ',
        afterCursor: '',
        containsKeywords: [
          'FIELDS TERMINATED BY',
          'LINES TERMINATED BY',
          'WITH SERDEPROPERTIES',
          'STORED AS',
          'LOCATION',
          'CACHED IN',
          'UNCACHED',
          'TBLPROPERTIES',
          'AS'
        ],
        doestNotContainKeywords: ['ROW FORMAT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TERMINATED BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY \'b\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY 'b' ",
        afterCursor: '',
        containsKeywords: ['AS', 'LINES TERMINATED BY'],
        doestNotContainKeywords: ['FIELDS TERMINATED BY', 'ROW FORMAT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should suggest keywords for \"CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY 'b' LINES TERMINATED BY 'c' |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY 'b' LINES TERMINATED BY 'c' ",
        afterCursor: '',
        containsKeywords: ['AS'],
        doestNotContainKeywords: ['FIELDS TERMINATED BY', 'LINES TERMINATED BY', 'ROW FORMAT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED BY \'z\' STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED BY 'z' STORED AS ",
        afterCursor: '',
        containsKeywords: ['PARQUET'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CACHED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CACHED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IN']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CACHED IN \'boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) CACHED IN 'boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH REPLICATION =', 'TBLPROPERTIES', 'AS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CACHED IN \'boo\' WITH |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) CACHED IN 'boo' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REPLICATION =']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CACHED IN \'boo\' WITH REPLICATION |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) CACHED IN 'boo' WITH REPLICATION ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest keywords for "CREATE ... TABLE ... PARTITIONED BY ... ROW FORMAT ... CACHED |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName\n' +
          "  (id INT, col2 STRING COMMENT 'booo', col3 BIGINT)\n" +
          "PARTITIONED BY (boo DOUBLE COMMENT 'booo boo', baa INT)\n" +
          "COMMENT 'Table comment...' \n" +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'a' ESCAPED BY 'c' LINES TERMINATED BY 'q'\n" +
          "WITH SERDEPROPERTIES ( 'key' = 'value', 'key2' = 'value 2' ) \n" +
          'STORED AS PARQUET\n' +
          "LOCATION '/baa/baa'\n" +
          'CACHED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IN']
        }
      });
    });

    it('should suggest keywords for "CREATE ... TABLE ... LIKE PARQUET ... PARTITIONED BY ... ROW FORMAT ... CACHED |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName \n' +
          "LIKE PARQUET '/boo/baa'\n" +
          "PARTITIONED BY (boo DOUBLE COMMENT 'booo boo', baa INT)\n" +
          'SORT BY (baa, boo, ble)\n' +
          "COMMENT 'Table comment...' \n" +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'a' ESCAPED BY 'c' LINES TERMINATED BY 'q'\n" +
          "WITH SERDEPROPERTIES ('key' = 'value', 'key2' = 'value 2')\n" +
          'STORED AS PARQUET \n' +
          "LOCATION '/baa/baa'\n" +
          'CACHED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IN']
        }
      });
    });

    it('should suggest tables for "CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARQUET'],
          suggestTables: {},
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo.baa COMMENT \'Table comment...\' STORED |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo.baa COMMENT 'Table comment...' STORED ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "CREATE ... TABLE ... ROW FORMAT ... CACHED IN ... AS |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE dbOne.tableName\n' +
          "COMMENT 'Table comment...'\n" +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'a' ESCAPED BY 'c' LINES TERMINATED BY 'q'\n" +
          "WITH SERDEPROPERTIES ('key' = 'value', 'key2' = 'value 2')\n" +
          'STORED AS PARQUET\n' +
          "LOCATION '/baa/baa'\n" +
          "CACHED IN 'boo'\n" +
          "TBLPROPERTIES ('key' = 'value', 'key2' = 'value 2')\n" +
          'AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should handle "create table four_k as select 4096 as x;|"', () => {
      assertAutoComplete({
        beforeCursor: 'create table four_k as select 4096 as x;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it(
      'should handle "CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
        ' PRIMARY KEY (b)) STORED AS KUDU;|"',
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) STORED AS KUDU;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it(
      'should handle "CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
        ' PRIMARY KEY (b)) PARTITION BY RANGE (a, b) (PARTITION 1 <= VALUES < 2) STORED AS KUDU;|"',
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY RANGE (a, b) (PARTITION 1 <= VALUES < 2) STORED AS KUDU;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it(
      'should handle "CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
        ' PRIMARY KEY (b)) PARTITION BY RANGE (a) (PARTITION VALUE = 50, PARTITION 50 < VALUES <= 100) STORED AS KUDU;|"',
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY RANGE (a) (PARTITION VALUE = 50, PARTITION 50 < VALUES <= 100) STORED AS KUDU;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it(
      'should handle "CREATE TABLE IF NOT EXISTS tbl (i INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
        ' PRIMARY KEY (b)) PARTITION BY HASH (a, b) PARTITIONS 10 STORED AS KUDU;|"',
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE TABLE IF NOT EXISTS tbl (i INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY HASH (a, b) PARTITIONS 10 STORED AS KUDU;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          noErrors: true,
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it('should handle "CREATE TABLE foo (i INT) STORED AS KUDU;|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT) STORED AS KUDU;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (i INT PRIMARY KEY) STORED AS KUDU;|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY) STORED AS KUDU;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (i INT, j INT, PRIMARY KEY (i, j)) STORED AS KUDU;|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT, j INT, PRIMARY KEY (i, j)) STORED AS KUDU;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (i INT PRIMARY KEY, PRIMARY KEY(i)) STORED AS KUDU;|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, PRIMARY KEY(i)) STORED AS KUDU;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS KUDU;|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS KUDU;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'BLOCK_SIZE',
            'COMMENT',
            'COMPRESSION',
            'DEFAULT',
            'ENCODING',
            'NOT NULL',
            'NULL',
            'PRIMARY KEY'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT', 'COMPRESSION', 'DEFAULT', 'ENCODING', 'PRIMARY KEY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL PRIMARY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL PRIMARY ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['KEY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['KEY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT, "', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PRIMARY KEY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT, PRIMARY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT, PRIMARY ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['KEY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['KUDU'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['PARTITION BY', 'PARTITIONED BY', 'STORED AS', 'SORT BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['HASH', 'RANGE']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VALUE', 'VALUES']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['<', '<=']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 < |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 < ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VALUES'],
          suggestFunctions: { types: ['NUMBER'] }
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['=']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE = |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE = ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {}
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION cos(10) < VALUES, PARTITION VALUES |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION cos(10) < VALUES, PARTITION VALUES ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['<', '<=']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY HASH (i) |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY  HASH (i) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITIONS']
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

    it('should suggest keywords for "CREATE VIEW IF NOT EXISTS boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW IF NOT EXISTS boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT', 'AS']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW boo (id |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW boo (id ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT']
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW boo (id COMMENT \'boo\') |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE VIEW boo (id COMMENT 'boo') ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT', 'AS']
        }
      });
    });

    it("should suggest keywords for \"CREATE VIEW boo (id COMMENT 'boo') COMMENT 'foo' |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE VIEW boo (id COMMENT 'boo') COMMENT 'foo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });
  });
});
