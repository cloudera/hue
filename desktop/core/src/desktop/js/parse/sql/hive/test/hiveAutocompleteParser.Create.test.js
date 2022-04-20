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

describe('hiveAutocompleteParser.js CREATE statements', () => {
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

  it('should handle "CREATE EXTERNAL TABLE ice_t_identity_part (a int) PARTITIONED BY (b string) STORED BY ICEBERG; |"', () => {
    assertAutoComplete({
      beforeCursor:
        'CREATE EXTERNAL TABLE ice_t_identity_part (a int) PARTITIONED BY (b string) STORED BY ICEBERG; ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "create external table tbl_ice ... stored by iceberg ...; |"', () => {
    assertAutoComplete({
      beforeCursor:
        "create external table tbl_ice(a int, b string, c int) partitioned by spec (bucket(16, a), truncate(3, b)) stored by iceberg stored as avro tblproperties ('format-version'='2'); ",
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: true
      }
    });
  });

  it('should handle "create external table tbl_ice_other(a int, b string) stored by iceberg; |"', () => {
    assertAutoComplete({
      beforeCursor: 'create external table tbl_ice_other(a int, b string) stored by iceberg; ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: true
      }
    });
  });

  it('should handle "CREATE EXTERNAL TABLE ice_orc (i int, s string, ts timestamp, d date) STORED BY ICEBERG STORED AS ORC; |"', () => {
    assertAutoComplete({
      beforeCursor:
        'CREATE EXTERNAL TABLE ice_orc (i int, s string, ts timestamp, d date) STORED BY ICEBERG STORED AS ORC; ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "CREATE EXTERNAL TABLE ice_t (i int, s string, ts timestamp, d date) STORED BY \'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler\' STORED AS AVRO; |"', () => {
    assertAutoComplete({
      beforeCursor:
        "CREATE EXTERNAL TABLE ice_t (i int, s string, ts timestamp, d date) STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler' STORED AS AVRO; ",
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it("should handle \"CREATE EXTERNAL TABLE ice_t (i int, s string, ts timestamp, d date) STORED BY ICEBERG WITH SERDEPROPERTIES('dummy'='dummy_value') STORED AS ORC; |\"", () => {
    assertAutoComplete({
      beforeCursor:
        "CREATE EXTERNAL TABLE ice_t (i int, s string, ts timestamp, d date) STORED BY ICEBERG WITH SERDEPROPERTIES('dummy'='dummy_value') STORED AS ORC; ",
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it("should handle \"create external table tbl_ice(a int, b string, c int) partitioned by spec (bucket(16, a), truncate(3, b)) stored by iceberg tblproperties ('format-version'='2'); |\"", () => {
    assertAutoComplete({
      beforeCursor:
        "create external table tbl_ice(a int, b string, c int) partitioned by spec (bucket(16, a), truncate(3, b)) stored by iceberg tblproperties ('format-version'='2'); ",
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: true
      }
    });
  });

  it('should handle "CREATE EXTERNAL TABLE ice_t_transform (year_field date, month_field date, day_field date, hour_field timestamp, truncate_field string, bucket_field int, identity_field int) PARTITIONED BY SPEC (year(year_field), month(month_field), day(day_field), hour(hour_field), truncate(2, truncate_field), bucket(2, bucket_field), identity_field) STORED BY ICEBERG; |"', () => {
    assertAutoComplete({
      beforeCursor:
        'CREATE EXTERNAL TABLE ice_t_transform (year_field date, month_field date, day_field date, hour_field timestamp, truncate_field string, bucket_field int, identity_field int) PARTITIONED BY SPEC (year(year_field), month(month_field), day(day_field), hour(hour_field), truncate(2, truncate_field), bucket(2, bucket_field), identity_field) STORED BY ICEBERG; ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "CREATE EXTERNAL TABLE ice_t_transform_prop (id int, year_field date, month_field date, day_field date, hour_field timestamp, truncate_field string, bucket_field int, identity_field int) STORED BY ICEBERG TBLPROPERTIES (\'iceberg.mr.table.partition.spec\'=\'{"spec-id":0,"fields":[{"name":"year_field_year","transform":"year","source-id":1,"field-id":1000},{"name":"month_field_month","transform":"month","source-id":2,"field-id":1001},{"name":"day_field_day","transform":"day","source-id":3,"field-id":1002},{"name":"hour_field_hour","transform":"hour","source-id":4,"field-id":1003},{"name":"truncate_field_trunc","transform":"truncate[2]","source-id":5,"field-id":1004},{"name":"bucket_field_bucket","transform":"bucket[2]","source-id":6,"field-id":1005},{"name":"identity_field","transform":"identity","source-id":7,"field-id":1006}]}\'); |"', () => {
    assertAutoComplete({
      beforeCursor:
        'CREATE EXTERNAL TABLE ice_t_transform_prop (id int, year_field date, month_field date, day_field date, hour_field timestamp, truncate_field string, bucket_field int, identity_field int) STORED BY ICEBERG TBLPROPERTIES (\'iceberg.mr.table.partition.spec\'=\'{"spec-id":0,"fields":[{"name":"year_field_year","transform":"year","source-id":1,"field-id":1000},{"name":"month_field_month","transform":"month","source-id":2,"field-id":1001},{"name":"day_field_day","transform":"day","source-id":3,"field-id":1002},{"name":"hour_field_hour","transform":"hour","source-id":4,"field-id":1003},{"name":"truncate_field_trunc","transform":"truncate[2]","source-id":5,"field-id":1004},{"name":"bucket_field_bucket","transform":"bucket[2]","source-id":6,"field-id":1005},{"name":"identity_field","transform":"identity","source-id":7,"field-id":1006}]}\'); ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "CREATE TABLE target STORED BY ICEBERG AS SELECT * FROM source; |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE TABLE target STORED BY ICEBERG AS SELECT * FROM source; ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "CREATE EXTERNAL TABLE foo PARTITIONED BY SPEC (year(year_field), month(month_field), day(day_field), hour(hour_field), truncate(2, truncate_field), bucket(2, bucket_field), identity_field) STORED BY ICEBERG; |"', () => {
    assertAutoComplete({
      beforeCursor:
        'CREATE EXTERNAL TABLE foo PARTITIONED BY SPEC (year(year_field), month(month_field), day(day_field), hour(hour_field), truncate(2, truncate_field), bucket(2, bucket_field), identity_field) STORED BY ICEBERG; ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "CREATE ROLE baaa;|', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE ROLE baaa;',
      afterCursor: '',
      noErrors: true,
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
          'CONNECTOR',
          'DATABASE',
          'EXTERNAL TABLE',
          'FUNCTION',
          'INDEX',
          'MATERIALIZED VIEW',
          'REMOTE DATABASE',
          'ROLE',
          'SCHEDULED QUERY',
          'SCHEMA',
          'TABLE',
          'TEMPORARY EXTERNAL TABLE',
          'TEMPORARY FUNCTION',
          'TEMPORARY MACRO',
          'TEMPORARY TABLE',
          'TRANSACTIONAL TABLE',
          'VIEW'
        ]
      }
    });
  });

  describe('CREATE CONNECTOR', () => {
    it("should handle \"CREATE CONNECTOR IF NOT EXISTS foo TYPE 'mysql' URL 'http://someURl' COMMENT 'Connector comment ' WITH DCPROPERTIES ('foo'='bar'); |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE CONNECTOR IF NOT EXISTS foo TYPE 'mysql' URL 'http://someURl' COMMENT 'Connector comment ' WITH DCPROPERTIES ('foo'='bar'); ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE CONNECTOR |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE CONNECTOR ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['IF NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE CONNECTOR IF |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE CONNECTOR IF ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT EXISTS']
        }
      });
    });

    it('should suggest keywords for "CREATE CONNECTOR foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE CONNECTOR foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TYPE', 'URL', 'COMMENT', 'WITH DCPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "CREATE CONNECTOR foo TYPE \'bar\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE CONNECTOR foo TYPE 'bar' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['URL', 'COMMENT', 'WITH DCPROPERTIES']
        }
      });
    });

    it("should suggest keywords for \"CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT', 'WITH DCPROPERTIES']
        }
      });
    });

    it("should suggest keywords for \"CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' COMMENT 'some comment' |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' COMMENT 'some comment' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH DCPROPERTIES']
        }
      });
    });

    it("should suggest keywords for \"CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' COMMENT 'some comment' WITH |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' COMMENT 'some comment' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DCPROPERTIES']
        }
      });
    });

    it("should suggest keywords for \"CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' WITH |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE CONNECTOR foo TYPE 'bar' URL 'http://someurl' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DCPROPERTIES']
        }
      });
    });
  });

  describe('CREATE DATABASE', () => {
    it("should handle \"CREATE REMOTE DATABASE postgres_db1 USING foo WITH DBPROPERTIES ('connector.remoteDbName'='db1'); |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE REMOTE DATABASE postgres_db1 USING foo WITH DBPROPERTIES ('connector.remoteDbName'='db1'); ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

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
          suggestKeywords: ['COMMENT', 'LOCATION', 'MANAGEDLOCATION', 'WITH DBPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "CREATE DATABASE foo COMMENT \'bla\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE DATABASE foo COMMENT 'bla' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LOCATION', 'MANAGEDLOCATION', 'WITH DBPROPERTIES']
        }
      });
    });

    it("should suggest keywords for \"CREATE DATABASE foo COMMENT 'bla' LOCATION '/bla' |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE DATABASE foo COMMENT 'bla' LOCATION '/bla' ",
        afterCursor: '',
        containsKeywords: ['WITH DBPROPERTIES'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should suggest keywords for \"CREATE DATABASE foo COMMENT 'bla' MANAGEDLOCATION '/bla' |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE DATABASE foo COMMENT 'bla' MANAGEDLOCATION '/bla' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH DBPROPERTIES']
        }
      });
    });
  });

  describe('CREATE FUNCTION', () => {
    it('should handle "CREATE TEMPORARY FUNCTION baaa AS \'boo.baa\'; |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TEMPORARY FUNCTION baaa AS 'boo.baa'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"CREATE FUNCTION boo.baaa AS 'boo.baa' USING JAR 'boo.jar', FILE 'booo', ARCHIVE 'baa'; |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE FUNCTION boo.baaa AS 'boo.baa' USING JAR 'boo.jar', FILE 'booo', ARCHIVE 'baa'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo.baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE FUNCTION boo.baa ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo.baa AS \'baa.boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE FUNCTION boo.baa AS 'baa.boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['USING']
        }
      });
    });

    it('should suggest keywords for "CREATE FUNCTION boo.baa AS \'baa.boo\' USING |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE FUNCTION boo.baa AS 'baa.boo' USING ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ARCHIVE', 'FILE', 'JAR']
        }
      });
    });

    xit("should suggest hdfs for \"CREATE FUNCTION boo.baa AS 'baa.boo' USING FILE '|\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE FUNCTION boo.baa AS 'baa.boo' USING FILE '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it("should suggest keywords for \"CREATE FUNCTION boo.baa AS 'baa.boo' USING FILE 'boo' |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE FUNCTION boo.baa AS 'baa.boo' USING FILE 'boo' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ARCHIVE', 'FILE', 'JAR']
        }
      });
    });

    it('should suggest keywords for "CREATE TEMPORARY FUNCTION boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY FUNCTION boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should not suggest keywords for "CREATE TEMPORARY FUNCTION boo AS \'boo.baa\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TEMPORARY FUNCTION boo AS 'boo.baa' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('CREATE INDEX', () => {
    it('should handle "CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS \'COMPACT\' WITH DEFERRED REBUILD IDXPROPERTIES ("boo.baa"="ble", "blaa"=1) IN TABLE dbTwo.tblTwo ROW FORMAT DELIMITED STORED AS PARQUET LOCATION \'/baa/boo\' TBLPROPERTIES ("bla"=1) COMMENT "booo"; |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS 'COMPACT' WITH DEFERRED REBUILD IDXPROPERTIES " +
          '("boo.baa"="ble", "blaa"=1) IN TABLE dbTwo.tblTwo ROW FORMAT DELIMITED STORED AS PARQUET LOCATION \'/baa/boo\' ' +
          'TBLPROPERTIES ("bla"=1) COMMENT "booo"; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS \'boo.baa.bitmap\'; |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS 'boo.baa.bitmap'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla  |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE INDEX bla ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON TABLE']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE INDEX bla ON ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "CREATE INDEX bla ON TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE INDEX bla ON TABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest columns for "CREATE INDEX bla ON TABLE foo.bar (|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE INDEX bla ON TABLE foo.bar (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'foo' }, { name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "CREATE INDEX bla ON TABLE foo.bar (a, b, c, |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE INDEX bla ON TABLE foo.bar (a, b, c, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'foo' }, { name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ["'BITMAP'", "'COMPACT'"]
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BIT|"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BIT",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ["'BITMAP'", "'COMPACT'"]
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'WITH DEFERRED REBUILD',
            'IDXPROPERTIES',
            'IN TABLE',
            'ROW FORMAT',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'COMMENT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DEFERRED REBUILD']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH DEFERRED |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' WITH DEFERRED ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REBUILD']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH DEFERRED REBUILD |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' WITH DEFERRED REBUILD ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'IDXPROPERTIES',
            'IN TABLE',
            'ROW FORMAT',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'COMMENT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IDXPROPERTIES ("baa"="boo") |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IDXPROPERTIES ("baa"="boo") ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'IN TABLE',
            'ROW FORMAT',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'COMMENT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' IN ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' IN TABLE ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN TABLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' IN TABLE boo ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ROW FORMAT',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'COMMENT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' ROW ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FORMAT']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' ROW FORMAT ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DELIMITED', 'SERDE']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT DELIMITED |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' ROW FORMAT DELIMITED ",
        afterCursor: '',
        containsKeywords: [
          'MAP KEYS TERMINATED BY',
          'NULL DEFINED AS',
          'LOCATION',
          'TBLPROPERTIES',
          'COMMENT'
        ],
        doesNotContainKeywords: ['AS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT DELIMITED NULL |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'BITMAP' ROW FORMAT DELIMITED NULL ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DEFINED AS']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' ROW FORMAT DELIMITED STORED |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'COMPACT' ROW FORMAT DELIMITED STORED ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' STORED |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'COMPACT' STORED ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS', 'BY']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' ROW FORMAT DELIMITED STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'COMPACT' ROW FORMAT DELIMITED STORED AS ",
        afterCursor: '',
        containsKeywords: ['ORC', 'PARQUET'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should suggest hdfs for \"CREATE INDEX bla ON TABLE boo (a, b, c) AS 'COMPACT' LOCATION '|\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'COMPACT' LOCATION '",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it("should suggest keywords for \"CREATE INDEX bla ON TABLE boo (a, b, c) AS 'COMPACT' LOCATION '/baa' |\"", () => {
      assertAutoComplete({
        beforeCursor: "CREATE INDEX bla ON TABLE boo (a, b, c) AS 'COMPACT' LOCATION '/baa' ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TBLPROPERTIES', 'COMMENT']
        }
      });
    });

    it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' TBLPROPERTIES ("baa"="boo") |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' TBLPROPERTIES ("baa"="boo") ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT']
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

    it('should handle "CREATE TABLE foo (id DOUBLE DEFAULT CURRENT_DATE() NOT NULL COMMENT \'foo\'); |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE foo (id DOUBLE DEFAULT CURRENT_DATE() NOT NULL COMMENT 'foo'); ",
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (id DOUBLE, foo INT, PRIMARY KEY (id), CONSTRAINT boo UNIQUE (foo)); |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (id DOUBLE, foo INT, PRIMARY KEY (id), CONSTRAINT boo UNIQUE (foo)); ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (id DOUBLE, foo INT, CONSTRAINT boo UNIQUE (foo, id) DISABLE NOVALIDATE, CONSTRAINT baa CHECK (id > 0) DISABLE NOVALIDATE); |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (id DOUBLE, foo INT, CONSTRAINT boo UNIQUE (foo, id) DISABLE NOVALIDATE, CONSTRAINT baa CHECK (id > 0) DISABLE NOVALIDATE); ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (id DOUBLE CHECK (id > 0)); |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id DOUBLE CHECK (id > 0)); ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (id DOUBLE, CONSTRAINT foo CHECK (id > 0)); |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id DOUBLE, CONSTRAINT foo CHECK (id > 0)); ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (id INT);|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id INT);',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "CREATE TABLE foo (id INTEGER);|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id INTEGER);',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
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

    it(
      'should handle "CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.tbl (id INT, col VARCHAR, ' +
        'bla DOUBLE PRECISION, PRIMARY KEY (id, col) DISABLE NOVALIDATE, CONSTRAINT cnstrnt FOREIGN KEY (id, bla) ' +
        "REFERENCES sometbl (id, ble) DISABLE NOVALIDATE) COMMENT 'table comment';|\"",
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.tbl (id INT, col VARCHAR, ' +
            'bla DOUBLE PRECISION, PRIMARY KEY (id, col) DISABLE NOVALIDATE, CONSTRAINT cnstrnt FOREIGN KEY (id, bla) ' +
            "REFERENCES sometbl (id, ble) DISABLE NOVALIDATE) COMMENT 'table comment';",
          noErrors: true,
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it('should handle "CREATE TRANSACTIONAL TABLE transactional_table_test(key string, value string) PARTITIONED BY(ds string) STORED AS ORC;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TRANSACTIONAL TABLE transactional_table_test(key string, value string) PARTITIONED BY(ds string) STORED AS ORC;',
        noErrors: true,
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it(
      'should handle "CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.tbl (id INT, col VARCHAR, ' +
        'bla DOUBLE PRECISION, CONSTRAINT cnstrnt FOREIGN KEY (id, bla) ' +
        "REFERENCES sometbl (id, ble) DISABLE NOVALIDATE) COMMENT 'table comment';|\"",
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.tbl (id INT, col VARCHAR, ' +
            'bla DOUBLE PRECISION, CONSTRAINT cnstrnt FOREIGN KEY (id, bla) ' +
            "REFERENCES sometbl (id, ble) DISABLE NOVALIDATE) COMMENT 'table comment';",
          noErrors: true,
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

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

    it('should suggest keywords for "CREATE TEMPORARY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTERNAL TABLE', 'FUNCTION', 'MACRO', 'TABLE']
        }
      });
    });

    it('should suggest keywords for "CREATE TEMPORARY EXTERNAL |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY EXTERNAL ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "CREATE TEMPORARY TABLE foo.boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY TABLE foo.boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LIKE']
        }
      });
    });

    it('should suggest tables for "CREATE TABLE boo LIKE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE boo LIKE dbOne.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'dbOne' }] }
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'DEFAULT', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE', 'COMMENT']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PRIMARY KEY', 'CONSTRAINT']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int, PRIMARY ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['KEY']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOVALIDATE', 'DISABLE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOVALIDATE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CONSTRAINT']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'FOREIGN KEY', 'UNIQUE']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['KEY']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REFERENCES']
        }
      });
    });

    it('should suggest tables for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DISABLE', 'NOVALIDATE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (id int, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) DISABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOVALIDATE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE foo (id int, PRIMARY KEY (id) DISABLE NOVALIDATE, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) DISABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOVALIDATE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE EXTERNAL TABLE foo (id int, CONSTRAINT boo FOREIGN KEY (bla) REFERENCES sometbl(boo) DISABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOVALIDATE', 'NORELY', 'RELY']
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) ',
        afterCursor: '',
        containsKeywords: ['COMMENT', 'CLUSTERED BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int) COMMENT \'boo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE EXTERNAL TABLE foo (id int) COMMENT 'boo' ",
        afterCursor: '',
        containsKeywords: ['PARTITIONED BY', 'CLUSTERED BY'],
        doesNotContainKeywords: ['COMMENT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int) PARTITIONED BY (boo INT) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) PARTITIONED BY (boo INT) ',
        afterCursor: '',
        containsKeywords: ['CLUSTERED BY', 'SKEWED BY'],
        doesNotContainKeywords: ['COMMENT', 'PARTITIONED BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) INTO 10 BUCKETS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) INTO 10 BUCKETS ',
        afterCursor: '',
        containsKeywords: ['SKEWED BY'],
        doesNotContainKeywords: ['CLUSTERED BY', 'PARTITIONED BY'],
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
          suggestKeywords: ['TBLPROPERTIES', 'AS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SORTED BY', 'INTO']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ASC', 'DESC']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a ASC, b |, c)"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ASC, b ',
        afterCursor: ', c)',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ASC', 'DESC']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a ASC, b DESC, c) |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ASC, b DESC, c) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) INTO 10 |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) INTO 10 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BUCKETS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a ASC, b DESC, c) INTO 10 |"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ASC, b DESC, c) INTO 10 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BUCKETS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) SKEWED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) SKEWED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) SKEWED BY (a, b, c) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) SKEWED BY (a, b, c) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) SKEWED BY (a, b, c) ON ((1,2), (2,3)) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) SKEWED BY (a, b, c) ON ((1,2), (2,3)) ',
        afterCursor: '',
        containsKeywords: ['STORED AS DIRECTORIES'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) STORED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS', 'BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) STORED AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'AVRO',
            'INPUTFORMAT',
            'JSONFILE',
            'ORC',
            'PARQUET',
            'RCFILE',
            'SEQUENCEFILE',
            'TEXTFILE'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED BY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) STORED BY ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ICEBERG']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED BY ICEBERG STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) STORED BY ICEBERG STORED AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'AVRO',
            'INPUTFORMAT',
            'JSONFILE',
            'ORC',
            'PARQUET',
            'RCFILE',
            'SEQUENCEFILE',
            'TEXTFILE'
          ]
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
          suggestKeywords: ['DELIMITED', 'SERDE']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'FIELDS TERMINATED BY',
            'COLLECTION ITEMS TERMINATED BY',
            'MAP KEYS TERMINATED BY',
            'LINES TERMINATED BY',
            'NULL DEFINED AS',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'AS'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['KEYS TERMINATED BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' NULL DEFINED |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY 'a' NULL DEFINED ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY 'a' ",
        afterCursor: '',
        containsKeywords: ['STORED AS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' STORED |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY 'a' STORED ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS', 'BY']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' STORED AS |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY 'a' STORED AS ",
        afterCursor: '',
        containsKeywords: ['ORC'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED BY \'handler\' |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) STORED BY 'handler' ",
        afterCursor: '',
        containsKeywords: ['WITH SERDEPROPERTIES'],
        doesNotContainKeywords: ['STORED BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id int) STORED BY \'handler\' WITH |"', () => {
      assertAutoComplete({
        beforeCursor: "CREATE TABLE foo (id int) STORED BY 'handler' WITH ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SERDEPROPERTIES']
        }
      });
    });

    it('should suggest keywords for "CREATE ... TABLE ... PARTITIONED BY ... ROW FORMAT ... AS |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.foo (id INT COMMENT 'an int', baa ARRAY<BIGINT>) COMMENT 'a table' " +
          'PARTITIONED BY (boo DOUBLE, baa INT) ' +
          'CLUSTERED BY (boo, baa) SORTED BY (boo ASC, baa) INTO 10 BUCKETS ' +
          "SKEWED BY (a, b, c) ON (('val1', 'val2'), (1, 2, 3)) STORED AS DIRECTORIES " +
          "ROW FORMAT DELIMITED FIELDS TERMINATED BY 'b' ESCAPED BY 'o' COLLECTION ITEMS TERMINATED BY 'd' " +
          "MAP KEYS TERMINATED BY 'a' LINES TERMINATED BY 'a' NULL DEFINED AS 'o' " +
          'STORED AS ORC LOCATION \'/asdf/boo/\' TBLPROPERTIES ("comment"="boo") AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE boo PARTITIONED BY ... STORED BY \'storage.handler\' WITH SERDEPROPERTIES ... AS |"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE boo PARTITIONED BY (boo DOUBLE, baa INT) STORED BY 'storage.handler' " +
          "WITH SERDEPROPERTIES ('foo.bar' = 'booo', 'bar.foo' = 'bla') " +
          'LOCATION \'/asdf/boo/\' TBLPROPERTIES ("comment"="boo") AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest tables for "CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.boo LIKE | LOCATION \'/some/loc\';"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.boo LIKE ',
        afterCursor: " LOCATION '/some/loc';",
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id ',
        afterCursor: '',
        containsKeywords: ['BIGINT', 'MAP<>', 'DOUBLE PRECISION'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id DOUBLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id DOUBLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'PRECISION',
            'CHECK',
            'DEFAULT',
            'NOT NULL',
            'PRIMARY KEY',
            'UNIQUE',
            'COMMENT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id DOUBLE DEFAULT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id DOUBLE DEFAULT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'CURRENT_DATE()',
            'CURRENT_TIMESTAMP()',
            'CURRENT_USER()',
            'LITERAL',
            'NULL',
            'CHECK',
            'DEFAULT',
            'NOT NULL',
            'PRIMARY KEY',
            'UNIQUE',
            'COMMENT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo(baa DOUBLE PRECISION, id |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo(baa DOUBLE PRECISION, id ',
        afterCursor: '',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla ARRAY<INT>, boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla ARRAY<INT>, boo ',
        afterCursor: '',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla ARRAY<|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla ARRAY<',
        afterCursor: '',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla MAP<|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla MAP<',
        afterCursor: '',
        containsKeywords: ['BIGINT'],
        doesNotContainKeywords: ['MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla MAP<STRING, STRING>, boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla MAP<STRING, STRING>, boo ',
        afterCursor: '',
        containsKeywords: ['BIGINT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should not suggest keywords for "CREATE TABLE boo (baa STRUCT<foo:INT, |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE boo (baa STRUCT<foo:INT, ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id INT, bla MAP<|, boo BIGINT, bla INT"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id INT, bla MAP<',
        afterCursor: ', boo BIGINT, bla INT)',
        containsKeywords: ['BIGINT'],
        doesNotContainKeywords: ['MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id INT, bla MAP<|>, boo BIGINT, bla INT"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id INT, bla MAP<',
        afterCursor: '>, boo BIGINT, bla INT)',
        containsKeywords: ['BIGINT'],
        doesNotContainKeywords: ['MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla STRUCT<foo:|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla STRUCT<foo:',
        afterCursor: '',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla MAP<BIGINT, STRUCT<foo:ARRAY<|, bla DOUBLE"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla MAP<BIGINT, STRUCT<foo:ARRAY<',
        afterCursor: ', bla DOUBLE',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla MAP<BIGINT, STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE |, bla:DOUBLE>"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla MAP<BIGINT, STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE ',
        afterCursor: ', bla:DOUBLE>',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla BIGINT, blabla INT |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla BIGINT, blabla INT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CHECK', 'DEFAULT', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE', 'COMMENT']
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla MAP<|, STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE, doo:VARCHAR, bla:DOUBLE>"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla MAP<',
        afterCursor: ', STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE, doo:VARCHAR, bla:DOUBLE>',
        containsKeywords: ['BIGINT'],
        doesNotContainKeywords: ['MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id INT, ba STRUCT<boo:INT COMMENT \'Some Comment\', bla:BIGINT>, bla MAP<INT,|>, boo BIGINT, bla INT"', () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE TABLE foo (id INT, ba STRUCT<boo:INT COMMENT 'Some Comment', bla:BIGINT>, bla MAP<INT,",
        afterCursor: '>, boo BIGINT, bla INT)',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (id UNIONTYPE<INT, BIGINT, |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (id UNIONTYPE<INT, BIGINT, ',
        afterCursor: '',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TEMPORARY EXTERNAL TABLE foo (id UNIONTYPE<,,,STRUCT<boo:|>,BIGINT"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY EXTERNAL TABLE foo (id UNIONTYPE<,,,STRUCT<boo:',
        afterCursor: '>,BIGINT',
        containsKeywords: ['BIGINT', 'MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TABLE foo (bla ARRAY<MAP<|>>"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TABLE foo (bla ARRAY<MAP<',
        afterCursor: '>>',
        containsKeywords: ['BIGINT'],
        doesNotContainKeywords: ['MAP<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('CREATE TEMPORARY MACRO', () => {
    it('should suggest handle "CREATE TEMPORARY MACRO boo(x INT, y INT) x + cos(y);|"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y INT) x + cos(y);',
        afterCursor: '',
        noErrors: true,
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
        containsKeywords: ['TEMPORARY MACRO'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TEMPORARY |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY ',
        afterCursor: '',
        containsKeywords: ['MACRO'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TEMPORARY MACRO boo(x |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY MACRO boo(x ',
        afterCursor: '',
        containsKeywords: ['INT', 'STRING'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE TEMPORARY MACRO boo(x INT, y |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y ',
        afterCursor: '',
        containsKeywords: ['INT', 'STRING'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest functions for "CREATE TEMPORARY MACRO boo(x INT, y STRING) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y STRING) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {}
        }
      });
    });

    it('should suggest functions for "CREATE TEMPORARY MACRO boo(x INT, y STRING) cos(x) + y - |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y STRING) cos(x) + y - ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] }
        }
      });
    });
  });

  describe('CREATE MATERIALIZED VIEW', () => {
    it(
      'should handle "CREATE MATERIALIZED VIEW IF NOT EXISTS foo.bar DISABLE REWRITE \n' +
        "COMMENT 'comment' PARTITIONED ON (a, b) CLUSTERED ON (c) ROW FORMAT DELIMITED \n" +
        'STORED AS PARQUET LOCATION \'/baa/boo\' TBLPROPERTIES ("bla"=1) AS SELECT * from foo; |',
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE MATERIALIZED VIEW IF NOT EXISTS foo.bar DISABLE REWRITE \n' +
            "COMMENT 'comment' PARTITIONED ON (a, b) CLUSTERED ON (c) ROW FORMAT DELIMITED \n" +
            'STORED AS PARQUET LOCATION \'/baa/boo\' TBLPROPERTIES ("bla"=1) AS SELECT * from foo; ',
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it(
      'should handle "CREATE MATERIALIZED VIEW foo.bar DISABLE REWRITE \n' +
        "COMMENT 'comment' DISTRIBUTED ON (a, b) SORTED ON (c) AS SELECT * from foo; |",
      () => {
        assertAutoComplete({
          beforeCursor:
            'CREATE MATERIALIZED VIEW IF NOT EXISTS foo.bar DISABLE REWRITE \n' +
            "COMMENT 'comment' DISTRIBUTED ON (a, b) SORTED ON (c) AS SELECT * from foo; ",
          afterCursor: '',
          hasLocations: true,
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      }
    );

    it('should suggest keywords for "CREATE MATERIALIZED |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE MATERIALIZED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['VIEW']
        }
      });
    });

    it('should suggest keywords for "CREATE MATERIALIZED VIEW foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE MATERIALIZED VIEW foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'DISABLE REWRITE',
            'COMMENT',
            'PARTITIONED ON',
            'CLUSTERED ON',
            'DISTRIBUTED ON',
            'ROW FORMAT',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'AS SELECT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE MATERIALIZED VIEW bar DISABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE MATERIALIZED VIEW bar DISABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['REWRITE']
        }
      });
    });

    it('should suggest keywords for "CREATE MATERIALIZED VIEW foo DISABLE REWRITE |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE MATERIALIZED VIEW foo DISABLE REWRITE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'COMMENT',
            'PARTITIONED ON',
            'CLUSTERED ON',
            'DISTRIBUTED ON',
            'ROW FORMAT',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'AS SELECT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE MATERIALIZED VIEW foo DISABLE REWRITE CLUSTERED ON (a) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE MATERIALIZED VIEW foo DISABLE REWRITE CLUSTERED ON (a) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ROW FORMAT',
            'STORED AS',
            'STORED BY',
            'LOCATION',
            'TBLPROPERTIES',
            'AS SELECT'
          ]
        }
      });
    });

    it('should suggest keywords for "CREATE MATERIALIZED VIEW foo.bar DISABLE REWRITE DISTRIBUTED ON (a) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE MATERIALIZED VIEW foo.bar DISABLE REWRITE DISTRIBUTED ON (a) ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SORTED ON']
        }
      });
    });

    it('should suggest keywords for "CREATE MATERIALIZED VIEW foo DISABLE REWRITE CLUSTERED ON (a) |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE MATERIALIZED VIEW foo DISABLE REWRITE CLUSTERED ON (a) AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });
  });

  describe('CREATE VIEW', () => {
    it('should suggest columns "CREATE VIEW foo AS SELECT a, | FROM tableOne"', () => {
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

    it('should suggest columns for "CREATE VIEW IF NOT EXISTS db.foo (baa COMMENT \'foo bar\', ble) COMMENT \'baa\' TBLPROPERTIES ("boo.baa"="buu") AS SELECT a, | FROM tableOne"', () => {
      assertAutoComplete({
        beforeCursor:
          'CREATE VIEW IF NOT EXISTS db.foo (baa COMMENT \'foo bar\', ble) COMMENT \'baa\' TBLPROPERTIES ("boo.baa"="buu") AS SELECT a, ',
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

    it("should handle \"CREATE VIEW v1 AS WITH q1 AS ( SELECT key FROM src WHERE key = '5') SELECT * FROM q1;|", () => {
      assertAutoComplete({
        beforeCursor:
          "CREATE VIEW v1 AS WITH q1 AS ( SELECT key FROM src WHERE key = '5') SELECT * FROM q1;",
        afterCursor: '',
        hasLocations: true,
        containsKeywords: ['SELECT', 'WITH'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE VIEW IF NOT EXISTS boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'CREATE VIEW IF NOT EXISTS boo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMMENT', 'TBLPROPERTIES', 'AS']
        }
      });
    });
  });
});
