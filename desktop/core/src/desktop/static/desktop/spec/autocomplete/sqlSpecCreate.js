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

(function () {
  describe('sql.js CREATE statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    it('should suggest keywords for "|"', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        containsKeywords: ['CREATE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "CREATE |"', function () {
      assertAutoComplete({
        beforeCursor: 'CREATE ',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']
        }
      });
    });

    it('should handle "CREATE ROLE baaa;|', function () {
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

    describe('Hive specific', function () {
      it('should suggest keywords for "CREATE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'INDEX', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY EXTERNAL TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'TEMPORARY TABLE', 'VIEW']
          }
        });
      });
    });

    describe('Impala specific', function () {
      it('should suggest keywords for "CREATE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AGGREGATE FUNCTION', 'DATABASE', 'EXTERNAL TABLE', 'FUNCTION', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']
          }
        });
      });
    });

    describe('CREATE DATABASE', function () {
      it('should suggest keywords for "CREATE DATABASE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE DATABASE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE DATABASE IF |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE DATABASE IF ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE SCHEMA |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE SCHEMA ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE DATABASE | bla;"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE DATABASE ',
          afterCursor: ' bla;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF NOT EXISTS']
          }
        });
      });

      describe('Impala specific', function () {
        it('should suggest keywords for "CREATE DATABASE foo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE DATABASE foo ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT', 'LOCATION']
            }
          });
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords for "CREATE DATABASE foo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE DATABASE foo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "CREATE DATABASE foo COMMENT \'bla\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE DATABASE foo COMMENT \'bla\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['LOCATION', 'WITH DBPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "CREATE DATABASE foo COMMENT \'bla\' LOCATION \'/bla\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE DATABASE foo COMMENT \'bla\' LOCATION \'/bla\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['WITH DBPROPERTIES']
            }
          });
        });
      })
    });

    describe('CREATE FUNCTION', function () {
      describe('Hive specific', function () {
        it('should handle "CREATE TEMPORARY FUNCTION baaa AS \'boo.baa\'; |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY FUNCTION baaa AS \'boo.baa\'; ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE FUNCTION boo.baaa AS \'boo.baa\' USING JAR \'boo.jar\', FILE \'booo\', ARCHIVE \'baa\'; |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo.baaa AS \'boo.baa\' USING JAR \'boo.jar\', FILE \'booo\', ARCHIVE \'baa\'; ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo.baa |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo.baa ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS']
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo.baa AS \'baa.boo\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo.baa AS \'baa.boo\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['USING']
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo.baa AS \'baa.boo\' USING |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo.baa AS \'baa.boo\' USING ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ARCHIVE', 'FILE', 'JAR']
            }
          });
        });

        xit('should suggest hdfs for "CREATE FUNCTION boo.baa AS \'baa.boo\' USING FILE \'|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo.baa AS \'baa.boo\' USING FILE \'',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: '' }
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo.baa AS \'baa.boo\' USING FILE \'boo\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo.baa AS \'baa.boo\' USING FILE \'boo\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ARCHIVE', 'FILE', 'JAR']
            }
          });
        });

        it('should suggest keywords for "CREATE TEMPORARY FUNCTION boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY FUNCTION boo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS']
            }
          });
        });

        it('should not suggest keywords for "CREATE TEMPORARY FUNCTION boo AS \'boo.baa\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY FUNCTION boo AS \'boo.baa\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should handle "CREATE FUNCTION foo.boo(INT, BOOLEAN) RETURNS INT LOCATION \'/boo\' SYMBOL=\'baaa\'; |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION \'/boo\' SYMBOL=\'baaa\'; ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE AGGREGATE FUNCTION baa.boo(INT, DOUBLE) RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'sin\' ' +
            'MERGE_FN=\'cos\' PREPARE_FN=\'cos\' CLOSE_FN=\'cos\' SERIALIZE_FN=\'cos\' FINALIZE_FN=\'cos\'; |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'sin\' MERGE_FN=\'cos\' PREPARE_FN=\'cos\' CLOSE_FN=\'cos\' SERIALIZE_FN=\'cos\' FINALIZE_FN=\'cos\'; ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FUNCTION']
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IF NOT EXISTS'],
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION IF |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION IF ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['NOT EXISTS']
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION IF NOT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION IF NOT ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['EXISTS']
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo(|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo(',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['RETURNS']
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS INT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['LOCATION']
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['INIT_FN', 'UPDATE_FN']
            }
          });
        });

        it('should suggest functions for "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestAnalyticFunctions: true,
              suggestAggregateFunctions: { tables: [] },
              suggestFunctions: {}
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['UPDATE_FN']
            }
          });
        });

        it('should suggest functions for "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestAnalyticFunctions: true,
              suggestAggregateFunctions: { tables: [] },
              suggestFunctions: {}
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'sin\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'sin\' ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['MERGE_FN']
            }
          });
        });

        it('should suggest keywords for "CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'sin\' MERGE_FN=\'tan\' ' +
            'PREPARE_FN=\'boo\' SERIALIZE_FN=\'baa\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE AGGREGATE FUNCTION boo() RETURNS INT LOCATION \'/boo\' INIT_FN=\'cos\' UPDATE_FN=\'sin\' MERGE_FN=\'tan\' PREPARE_FN=\'boo\' SERIALIZE_FN=\'baa\' ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FINALIZE_FN']
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IF NOT EXISTS'],
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION IF |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION IF ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['NOT EXISTS']
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION IF NOT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION IF NOT ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['EXISTS']
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            doesNotContainKeywords: ['ARRAY<>', '...'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['...']
            }
          });
        });

        it('should not suggest keywords for "CREATE FUNCTION boo(INT |, BOOLEAN"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT ',
            afterCursor: ', BOOLEAN',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN, |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION  boo(INT, BOOLEAN, ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            doesNotContainKeywords: ['ARRAY<>', '...'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN, STRING |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION  boo(INT, BOOLEAN, STRING ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['...']
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['RETURNS']
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) RETURNS ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['LOCATION']
            }
          });
        });

        it('should suggest hdfs for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION \'|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION \'',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: '' }
            }
          });
        });

        it('should suggest keywords for "CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION \'/boo\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE FUNCTION boo(INT, BOOLEAN) RETURNS INT LOCATION \'/boo\' ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SYMBOL']
            }
          });
        });
      });
    });

    describe('CREATE INDEX', function () {
      it('should handle "CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS \'COMPACT\' WITH DEFERRED REBUILD IDXPROPERTIES ("boo.baa"="ble", "blaa"=1) IN TABLE dbTwo.tblTwo ROW FORMAT DELIMITED STORED AS PARQUET LOCATION \'/baa/boo\' TBLPROPERTIES ("bla"=1) COMMENT \"booo\"; |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS \'COMPACT\' WITH DEFERRED REBUILD IDXPROPERTIES ' +
          '("boo.baa"="ble", "blaa"=1) IN TABLE dbTwo.tblTwo ROW FORMAT DELIMITED STORED AS PARQUET LOCATION \'/baa/boo\' ' +
          'TBLPROPERTIES ("bla"=1) COMMENT \"booo\"; ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS \'boo.baa.bitmap\'; |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE db.tbl (a, b, c) AS \'boo.baa.bitmap\'; ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla  |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ON TABLE']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables for "CREATE INDEX bla ON TABLE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest columns for "CREATE INDEX bla ON TABLE foo.bar (|"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE foo.bar (',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'foo' }, { name: 'bar' }] }] }
          }
        });
      });

      it('should suggest columns for "CREATE INDEX bla ON TABLE foo.bar (a, b, c, |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE foo.bar (a, b, c, ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestColumns: { tables: [{ identifierChain: [{ name: 'foo' }, { name: 'bar' }] }] }
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['\'BITMAP\'', '\'COMPACT\'']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BIT|"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BIT',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['\'BITMAP\'', '\'COMPACT\'']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['WITH DEFERRED REBUILD', 'IDXPROPERTIES', 'IN TABLE', 'ROW FORMAT', 'STORED AS', 'STORED BY', 'LOCATION', 'TBLPROPERTIES', 'COMMENT']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DEFERRED REBUILD']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH DEFERRED |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH DEFERRED ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['REBUILD']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH DEFERRED REBUILD |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' WITH DEFERRED REBUILD ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IDXPROPERTIES', 'IN TABLE', 'ROW FORMAT', 'STORED AS', 'STORED BY', 'LOCATION', 'TBLPROPERTIES', 'COMMENT']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IDXPROPERTIES ("baa"="boo") |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IDXPROPERTIES ("baa"="boo") ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IN TABLE', 'ROW FORMAT', 'STORED AS', 'STORED BY', 'LOCATION', 'TBLPROPERTIES', 'COMMENT']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TABLE']
          }
        });
      });

      it('should suggest tables for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN TABLE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN TABLE ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestTables: {},
            suggestDatabases: { appendDot: true }
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN TABLE boo |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' IN TABLE boo ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ROW FORMAT', 'STORED AS', 'STORED BY', 'LOCATION', 'TBLPROPERTIES', 'COMMENT']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['FORMAT']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DELIMITED', 'SERDE']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT DELIMITED |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT DELIMITED ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['MAP KEYS TERMINATED BY', 'NULL DEFINED AS', 'LOCATION', 'TBLPROPERTIES', 'COMMENT'],
          doesNotContainKeywords: ['AS'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT DELIMITED NULL |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'BITMAP\' ROW FORMAT DELIMITED NULL ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DEFINED AS']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' ROW FORMAT DELIMITED STORED |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' ROW FORMAT DELIMITED STORED ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' STORED |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' STORED ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['AS', 'BY']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' ROW FORMAT DELIMITED STORED AS |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' ROW FORMAT DELIMITED STORED AS ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['ORC', 'PARQUET'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest hdfs for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' LOCATION \'|"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' LOCATION \'',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestHdfs: { path: '' }
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' LOCATION \'/baa\' |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' LOCATION \'/baa\' ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TBLPROPERTIES', 'COMMENT']
          }
        });
      });

      it('should suggest keywords for "CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' TBLPROPERTIES ("baa"="boo") |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE INDEX bla ON TABLE boo (a, b, c) AS \'COMPACT\' TBLPROPERTIES ("baa"="boo") ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['COMMENT']
          }
        });
      });
    });

    describe('CREATE ROLE', function () {
      it('should handle "CREATE ROLE boo; |"', function () {
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

    describe('CREATE TABLE', function () {
      it('should suggest keywords for "CREATE TABLE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TABLE ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE TABLE IF |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TABLE IF ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE TABLE IF NOT |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TABLE IF NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should handle for "CREATE TABLE foo (id INT);|"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TABLE foo (id INT);',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE TABLE foo (id |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TABLE foo (id ',
          afterCursor: '',
          containsKeywords: ['BOOLEAN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE TABLE foo (id INT, some FLOAT, bar |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TABLE foo (id INT, some FLOAT, bar ',
          afterCursor: '',
          containsKeywords: ['BOOLEAN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      describe('Impala specific', function () {
        it('should suggest keywords for "CREATE EXTERNAL |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TABLE']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['LIKE', 'LIKE PARQUET']
            }
          });
        });

        it('should suggest tables for "CREATE TABLE boo LIKE |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo LIKE ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true },
              suggestKeywords: ['PARQUET']
            }
          });
        });

        it('should suggest tables for "CREATE TABLE boo LIKE dbOne.|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo LIKE dbOne.',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestTables: { identifierChain: [{ name: 'dbOne' }] }
            }
          });
        });

        it('should suggest hdfs for "CREATE TABLE boo LIKE PARQUET \'|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo LIKE PARQUET \'',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: ''}
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) LOCATION \'|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo LOCATION \'',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: ''}
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo LIKE PARQUET \'/blabla/\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo LIKE PARQUET \'/blabla/\' ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['COMMENT', 'CACHED IN'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) LOCATION \'/baa\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) LOCATION \'/baa\' ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TBLPROPERTIES', 'CACHED IN', 'AS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) PARTITIONED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) PARTITIONED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) PARTITIONED BY (boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) PARTITIONED BY (boo ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) WITH |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) WITH ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SERDEPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) PARTITIONED BY (boo INT, baa BIGINT |, boo INT) AS SELECT * FROM baa;"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) PARTITIONED BY (boo INT, baa BIGINT ',
            afterCursor: ', boo INT) AS SELECT * FROM baa;',
            dialect: 'impala',
            containsKeywords: ['COMMENT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) STORED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) STORED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) STORED AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) STORED AS ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AVRO', 'KUDU', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FORMAT']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['DELIMITED']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['AS', 'FIELDS TERMINATED BY', 'LINES TERMINATED BY' ],
            doestNotContainKeywords: ['ROW FORMAT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TERMINATED BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY \'b\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY \'b\' ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['AS', 'LINES TERMINATED BY' ],
            doestNotContainKeywords: ['FIELDS TERMINATED BY', 'ROW FORMAT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY \'b\' LINES TERMINATED BY \'c\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED FIELDS TERMINATED BY \'b\' LINES TERMINATED BY \'c\' ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['AS' ],
            doestNotContainKeywords: ['FIELDS TERMINATED BY', 'LINES TERMINATED BY', 'ROW FORMAT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED BY \'z\' STORED AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED LINES TERMINATED BY \'z\' STORED AS ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['PARQUET'],
            doesNotContainKeywords: ['ORC'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CACHED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CACHED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IN']
            }
          });
        });

        it('should suggest keywords for "CREATE ... TABLE ... PARTITIONED BY ... ROW FORMAT ... CACHED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName (id INT, col2 STRING COMMENT \'booo\', col3 BIGINT) ' +
            'COMMENT \'Table comment...\' PARTITIONED BY (boo DOUBLE COMMENT \'booo boo\', baa INT) ' +
            'WITH SERDEPROPERTIES ( \'key\' = \'value\', \'key2\' = \'value 2\' ) ' +
            'ROW FORMAT DELIMITED FIELDS TERMINATED BY \'a\' ESCAPED BY \'c\' LINES TERMINATED BY \'q\' STORED AS PARQUET ' +
            'LOCATION \'/baa/baa\' TBLPROPERTIES (\'key\' = \'value\', \'key2\' = \'value 2\') ' +
            'CACHED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IN']
            }
          });
        });

        it('should suggest keywords for "CREATE ... TABLE ... LIKE PARQUET ... PARTITIONED BY ... ROW FORMAT ... CACHED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE PARQUET \'/boo/baa\' ' +
            'COMMENT \'Table comment...\' PARTITIONED BY (boo DOUBLE COMMENT \'booo boo\', baa INT) ' +
            'WITH SERDEPROPERTIES ( \'key\' = \'value\', \'key2\' = \'value 2\' ) ' +
            'ROW FORMAT DELIMITED FIELDS TERMINATED BY \'a\' ESCAPED BY \'c\' LINES TERMINATED BY \'q\' STORED AS PARQUET ' +
            'LOCATION \'/baa/baa\' TBLPROPERTIES (\'key\' = \'value\', \'key2\' = \'value 2\') ' +
            'CACHED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IN']
            }
          });
        });

        it('should suggest tables for "CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo',
            afterCursor: '',
            dialect: 'impala',
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

        it('should suggest keywords for "CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo.baa COMMENT \'Table comment...\' STORED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE IF NOT EXISTS dbOne.tableName LIKE boo.baa COMMENT \'Table comment...\' STORED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS']
            }
          });
        });

        it('should suggest keywords for "CREATE ... TABLE ... ROW FORMAT ... CACHED IN ... AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE dbOne.tableName ' +
            'COMMENT \'Table comment...\' ' +
            'WITH SERDEPROPERTIES ( \'key\' = \'value\', \'key2\' = \'value 2\' ) ' +
            'ROW FORMAT DELIMITED FIELDS TERMINATED BY \'a\' ESCAPED BY \'c\' LINES TERMINATED BY \'q\' STORED AS PARQUET ' +
            'LOCATION \'/baa/baa\' TBLPROPERTIES (\'key\' = \'value\', \'key2\' = \'value 2\') ' +
            'CACHED IN \'boo\' AS ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SELECT']
            }
          });
        });

        it('should handle "create table four_k as select 4096 as x;|"', function () {
          assertAutoComplete({
            beforeCursor: 'create table four_k as select 4096 as x;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: true
            }
          });
        });

        it('should handle "CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY RANGE (a, b) (PARTITION 1 <= VALUES < 2) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY RANGE (a, b) (PARTITION 1 <= VALUES < 2) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY RANGE (a) (PARTITION VALUE = 50, PARTITION 50 < VALUES <= 100) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE IF NOT EXISTS tbl (i INT PRIMARY KEY, b INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY RANGE (a) (PARTITION VALUE = 50, PARTITION 50 < VALUES <= 100) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE IF NOT EXISTS tbl (i INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY HASH (a, b) PARTITIONS 10 STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE IF NOT EXISTS tbl (i INT ENCODING bla COMPRESSION zip DEFAULT 10 BLOCK_SIZE 4 NOT NULL,' +
            ' PRIMARY KEY (b)) PARTITION BY HASH (a, b) PARTITIONS 10 STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE foo (i INT) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE foo (i INT PRIMARY KEY) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE foo (i INT, j INT, PRIMARY KEY (i, j)) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT, j INT, PRIMARY KEY (i, j)) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE foo (i INT PRIMARY KEY, PRIMARY KEY(i)) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, PRIMARY KEY(i)) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS KUDU;|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS KUDU;',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            noErrors: true,
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BLOCK_SIZE', 'COMMENT', 'COMPRESSION', 'DEFAULT', 'ENCODING', 'NOT NULL', 'NULL', 'PRIMARY KEY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT', 'COMPRESSION', 'DEFAULT', 'ENCODING', 'PRIMARY KEY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL PRIMARY |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT BLOCK_SIZE 10 NOT NULL PRIMARY ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['KEY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['KEY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT, "', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT, ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PRIMARY KEY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT, PRIMARY |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT, PRIMARY ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['KEY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) STORED AS ',
            afterCursor: '',
            dialect: 'impala',
            noErrors: true,
            containsKeywords: ['KUDU'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) ',
            afterCursor: '',
            dialect: 'impala',
            noErrors: true,
            containsKeywords: ['PARTITION BY', 'PARTITIONED BY', 'STORED AS'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION ',
            afterCursor: '',
            dialect: 'impala',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY ',
            afterCursor: '',
            dialect: 'impala',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['HASH', 'RANGE']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PARTITION']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['VALUE', 'VALUES']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['<', '<=']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 < |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION 1 < ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['VALUES'],
              suggestFunctions: { types: ['NUMBER']}
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['=']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE = |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION VALUE = ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {}
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION cos(10) < VALUES, PARTITION VALUES |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY RANGE (i) (PARTITION cos(10) < VALUES, PARTITION VALUES ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['<', '<=']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY HASH (i) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (i INT PRIMARY KEY, j INT PRIMARY KEY) PARTITION BY  HASH (i) ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PARTITIONS']
            }
          });
        });
      });

      describe('Hive specific', function () {
        it('should suggest keywords for "CREATE EXTERNAL |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TABLE']
            }
          });
        });

        it('should suggest keywords for "CREATE TEMPORARY |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['EXTERNAL TABLE', 'FUNCTION', 'MACRO', 'TABLE']
            }
          });
        });

        it('should suggest keywords for "CREATE TEMPORARY EXTERNAL |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY EXTERNAL ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TABLE']
            }
          });
        });

        it('should suggest tables for "CREATE TEMPORARY TABLE foo.boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY TABLE foo.boo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['LIKE']
            }
          });
        });

        it('should suggest tables for "CREATE TABLE boo LIKE |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo LIKE dbOne.',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestTables: { identifierChain: [{ name: 'dbOne' }] }
            }
          });
        });

        it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT']
            }
          });
        });

        it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['COMMENT', 'CLUSTERED BY'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int) COMMENT \'boo\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) COMMENT \'boo\' ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['PARTITIONED BY', 'CLUSTERED BY'],
            doesNotContainKeywords: ['COMMENT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE EXTERNAL TABLE foo (id int) PARTITIONED BY (boo INT) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE EXTERNAL TABLE foo (id int) PARTITIONED BY (boo INT) ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['CLUSTERED BY', 'SKEWED BY'],
            doesNotContainKeywords: ['COMMENT', 'PARTITIONED BY'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) INTO 10 BUCKETS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) INTO 10 BUCKETS ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SKEWED BY'],
            doesNotContainKeywords: ['CLUSTERED BY', 'PARTITIONED BY'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) LOCATION \'/baa\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) LOCATION \'/baa\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TBLPROPERTIES', 'AS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SORTED BY', 'INTO']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ASC', 'DESC']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a ASC, b |, c)"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ASC, b ',
            afterCursor: ', c)',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ASC', 'DESC']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a ASC, b DESC, c) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ASC, b DESC, c) ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['INTO']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) INTO 10 |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) INTO 10 ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BUCKETS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) CLUSTERED (a, b, c) SORTED BY (a ASC, b DESC, c) INTO 10 |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) CLUSTERED BY (a, b, c) SORTED BY (a ASC, b DESC, c) INTO 10 ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BUCKETS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) SKEWED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) SKEWED ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) SKEWED BY (a, b, c) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) SKEWED BY (a, b, c) ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ON']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) SKEWED BY (a, b, c) ON ((1,2), (2,3)) |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) SKEWED BY (a, b, c) ON ((1,2), (2,3)) ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['STORED AS DIRECTORIES'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) STORED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) STORED ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS', 'BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) STORED AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) STORED AS ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AVRO', 'INPUTFORMAT', 'ORC', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FORMAT']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['DELIMITED', 'SERDE']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FIELDS TERMINATED BY', 'COLLECTION ITEMS TERMINATED BY', 'MAP KEYS TERMINATED BY', 'LINES TERMINATED BY', 'NULL DEFINED AS', 'STORED AS', 'LOCATION', 'TBLPROPERTIES', 'AS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['KEYS TERMINATED BY']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' NULL DEFINED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' NULL DEFINED ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['STORED AS'],
            doesNotContainKeywords: ['STORED BY'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' STORED |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' STORED ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' STORED AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) ROW FORMAT DELIMITED MAP KEYS TERMINATED BY \'a\' STORED AS ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['ORC'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) STORED BY \'handler\' |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) STORED BY \'handler\' ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['WITH SERDEPROPERTIES'],
            doesNotContainKeywords: ['STORED BY'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id int) STORED BY \'handler\' WITH |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id int) STORED BY \'handler\' WITH ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SERDEPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "CREATE ... TABLE ... PARTITIONED BY ... ROW FORMAT ... AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.foo (id INT COMMENT \'an int\', baa ARRAY<BIGINT>) COMMENT \'a table\' ' +
              'PARTITIONED BY (boo DOUBLE, baa INT) ' +
              'CLUSTERED BY (boo, baa) SORTED BY (boo ASC, baa) INTO 10 BUCKETS ' +
              'SKEWED BY (a, b, c) ON ((\'val1\', \'val2\'), (1, 2, 3)) STORED AS DIRECTORIES ' +
              'ROW FORMAT DELIMITED FIELDS TERMINATED BY \'b\' ESCAPED BY \'o\' COLLECTION ITEMS TERMINATED BY \'d\' ' +
              'MAP KEYS TERMINATED BY \'a\' LINES TERMINATED BY \'a\' NULL DEFINED AS \'o\' ' +
              'STORED AS ORC LOCATION \'/asdf/boo/\' TBLPROPERTIES ("comment"="boo") AS ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SELECT']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE boo PARTITIONED BY ... STORED BY \'storage.handler\' WITH SERDEPROPERTIES ... AS |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo PARTITIONED BY (boo DOUBLE, baa INT) STORED BY \'storage.handler\' ' +
              'WITH SERDEPROPERTIES (\'foo.bar\' = \'booo\', \'bar.foo\' = \'bla\') ' +
              'LOCATION \'/asdf/boo/\' TBLPROPERTIES ("comment"="boo") AS ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SELECT']
            }
          });
        });

        it('should suggest tables for "CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.boo LIKE | LOCATION \'/some/loc\';"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY EXTERNAL TABLE IF NOT EXISTS db.boo LIKE ',
            afterCursor: ' LOCATION \'/some/loc\';',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo(id |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo(id ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla ARRAY<INT>, boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla ARRAY<INT>, boo ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla ARRAY<|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla ARRAY<',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla MAP<|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla MAP<',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT'],
            doesNotContainKeywords: ['MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla MAP<STRING, STRING>, boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla MAP<STRING, STRING>, boo ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should not suggest keywords for "CREATE TABLE boo (baa STRUCT<foo:INT, |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE boo (baa STRUCT<foo:INT, ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id INT, bla MAP<|, boo BIGINT, bla INT"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id INT, bla MAP<',
            afterCursor: ', boo BIGINT, bla INT)',
            dialect: 'hive',
            containsKeywords: ['BIGINT'],
            doesNotContainKeywords: ['MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id INT, bla MAP<|>, boo BIGINT, bla INT"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id INT, bla MAP<',
            afterCursor: '>, boo BIGINT, bla INT)',
            dialect: 'hive',
            containsKeywords: ['BIGINT'],
            doesNotContainKeywords: ['MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla STRUCT<foo:|"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla STRUCT<foo:',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla MAP<BIGINT, STRUCT<foo:ARRAY<|, bla DOUBLE"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla MAP<BIGINT, STRUCT<foo:ARRAY<',
            afterCursor: ', bla DOUBLE',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla MAP<BIGINT, STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE |, bla:DOUBLE>"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla MAP<BIGINT, STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE ',
            afterCursor: ', bla:DOUBLE>',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla BIGINT, blabla INT |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla BIGINT, blabla INT ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT']
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla MAP<|, STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE, doo:VARCHAR, bla:DOUBLE>"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla MAP<',
            afterCursor: ', STRUCT<boo: INT, foo:STRUCT<blo:DOUBLE, doo:VARCHAR, bla:DOUBLE>',
            dialect: 'hive',
            containsKeywords: ['BIGINT'],
            doesNotContainKeywords: ['MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id INT, ba STRUCT<boo:INT COMMENT \'Some Comment\', bla:BIGINT>, bla MAP<INT,|>, boo BIGINT, bla INT"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id INT, ba STRUCT<boo:INT COMMENT \'Some Comment\', bla:BIGINT>, bla MAP<INT,',
            afterCursor: '>, boo BIGINT, bla INT)',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (id UNIONTYPE<INT, BIGINT, |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (id UNIONTYPE<INT, BIGINT, ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TEMPORARY EXTERNAL TABLE foo (id UNIONTYPE<,,,STRUCT<boo:|>,BIGINT"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TEMPORARY EXTERNAL TABLE foo (id UNIONTYPE<,,,STRUCT<boo:',
            afterCursor: '>,BIGINT',
            dialect: 'hive',
            containsKeywords: ['BIGINT', 'MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE TABLE foo (bla ARRAY<MAP<|>>"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE TABLE foo (bla ARRAY<MAP<',
            afterCursor: '>>',
            dialect: 'hive',
            containsKeywords: ['BIGINT'],
            doesNotContainKeywords: ['MAP<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });
      });
    });

    describe('CREATE TEMPORARY MACRO', function () {
      it('should suggest handle "CREATE TEMPORARY MACRO boo(x INT, y INT) x + cos(y);|"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y INT) x + cos(y);',
          afterCursor: '',
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['TEMPORARY MACRO'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE TEMPORARY |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TEMPORARY ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['MACRO'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE TEMPORARY MACRO boo(x |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TEMPORARY MACRO boo(x ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['INT', 'STRING'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "CREATE TEMPORARY MACRO boo(x INT, y |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['INT', 'STRING'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest functions for "CREATE TEMPORARY MACRO boo(x INT, y STRING) |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y STRING) ',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {}
          }
        });
      });

      it('should suggest functions for "CREATE TEMPORARY MACRO boo(x INT, y STRING) cos(x) + y - |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE TEMPORARY MACRO boo(x INT, y STRING) cos(x) + y - ',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: { types: ['NUMBER'] }
          }
        });
      });
    });

    describe('CREATE VIEW', function () {
      it('should handle "CREATE VIEW foo AS SELECT a, | FROM tableOne"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE VIEW foo AS SELECT a, ',
          afterCursor: ' FROM tableOne',
          hasLocations:true,
          expectedResult: {
            lowerCase: false,
            suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
            suggestAnalyticFunctions: true,
            suggestFunctions: {},
            suggestColumns:  { source: 'select', tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
            suggestKeywords: ['*']
          }
        });
      });

      it('should suggest keywords for "CREATE VIEW |"', function () {
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

      it('should suggest keywords for "CREATE VIEW | boo AS select * from baa;"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE VIEW ',
          afterCursor: ' boo AS SELECT * FROM baa;',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['IF NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE VIEW IF |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE VIEW IF ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['NOT EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE VIEW IF NOT |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE VIEW IF NOT ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['EXISTS']
          }
        });
      });

      it('should suggest keywords for "CREATE VIEW boo AS |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE VIEW boo AS ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest keywords for "CREATE VIEW IF NOT EXISTS boo AS |"', function () {
        assertAutoComplete({
          beforeCursor: 'CREATE VIEW IF NOT EXISTS boo AS ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      describe('Hive specific', function () {
        it('should suggest columns for "CREATE VIEW IF NOT EXISTS db.foo (baa COMMENT \'foo bar\', ble) COMMENT \'baa\' TBLPROPERTIES ("boo.baa"="buu") AS SELECT a, | FROM tableOne"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE VIEW IF NOT EXISTS db.foo (baa COMMENT \'foo bar\', ble) COMMENT \'baa\' TBLPROPERTIES ("boo.baa"="buu") AS SELECT a, ',
            afterCursor: ' FROM tableOne',
            dialect: 'hive',
            hasLocations:true,
            expectedResult: {
              lowerCase: false,
              suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
              suggestAnalyticFunctions: true,
              suggestFunctions: {},
              suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
              suggestKeywords: ['*']
            }
          });
        });

        it('should handle "CREATE VIEW v1 AS WITH q1 AS ( SELECT key FROM src WHERE key = \'5\') SELECT * FROM q1;|', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE VIEW v1 AS WITH q1 AS ( SELECT key FROM src WHERE key = \'5\') SELECT * FROM q1;',
            afterCursor: '',
            dialect: 'hive',
            hasLocations:true,
            containsKeywords: ['SELECT', 'WITH'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "CREATE VIEW IF NOT EXISTS boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE VIEW IF NOT EXISTS boo ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT', 'TBLPROPERTIES', 'AS']
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should suggest keywords for "CREATE VIEW IF NOT EXISTS boo |"', function () {
          assertAutoComplete({
            beforeCursor: 'CREATE VIEW IF NOT EXISTS boo ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS']
            }
          });
        });
      });
    });

  });
})();