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
  describe('sql.js ALTER statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    describe('ALTER INDEX', function () {
      it('should handle "ALTER INDEX baa ON boo.ba PARTITION (bla=1) REBUILD;|"', function() {
        assertAutoComplete({
          beforeCursor: 'ALTER INDEX baa ON boo.ba PARTITION (bla=1) REBUILD;',
          afterCursor: '',
          dialect: 'hive',
          noErrors:true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "ALTER INDEX |"', function() {
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

      it('should suggest keywords for "ALTER INDEX boo |"', function() {
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

      it('should suggest tables for "ALTER INDEX boo ON |"', function() {
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

      it('should suggest keywords for "ALTER INDEX boo ON bla |"', function() {
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

      it('should suggest keywords for "ALTER INDEX boo ON bla PARTITION (baa = 1) |"', function() {
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

    describe('ALTER TABLE', function () {
      it('should suggest keywords for "ALTER |"', function() {
        assertAutoComplete({
          beforeCursor: 'ALTER ',
          afterCursor: '',
          containsKeywords: ['TABLE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest tables for "ALTER TABLE |"', function() {
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

      it('should suggest tables for "ALTER TABLE foo.|"', function() {
        assertAutoComplete({
          beforeCursor: 'ALTER TABLE foo.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'foo' }], onlyTables: true  }
          }
        });
      });

      describe('Hive specific', function () {
        it('should handle "ALTER TABLE foo PARTITION (ds=\'2008-04-08\', hr) CHANGE COLUMN dec_column_name dec_column_name DECIMAL;|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE foo PARTITION (ds=\'2008-04-08\', hr) CHANGE COLUMN dec_column_name dec_column_name DECIMAL;',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "ALTER TABLE page_view DROP PARTITION (dt=\'2008-08-08\', country=\'us\');|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE page_view DROP PARTITION (dt=\'2008-08-08\', country=\'us\');',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "ALTER TABLE page_view ADD PARTITION (dt=\'2008-08-08\', country=\'us\') location \'/path/to/us/part080808\'\nPARTITION (dt=\'2008-08-09\', country=\'us\') location \'/path/to/us/part080809\';|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE page_view ADD PARTITION (dt=\'2008-08-08\', country=\'us\') location \'/path/to/us/part080808\'\nPARTITION (dt=\'2008-08-09\', country=\'us\') location \'/path/to/us/part080809\';',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ADD COLUMNS', 'ADD IF NOT EXISTS', 'ADD PARTITION', 'ARCHIVE PARTITION', 'CHANGE',
                'CLUSTERED BY', 'COMPACT', 'CONCATENATE', 'DISABLE NO_DROP', 'DISABLE OFFLINE', 'DROP',  'ENABLE NO_DROP',
                'ENABLE OFFLINE', 'EXCHANGE PARTITION', 'NOT SKEWED', 'NOT STORED AS DIRECTORIES',  'PARTITION',
                'RECOVER PARTITIONS', 'RENAME TO', 'REPLACE COLUMNS', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDE',
                'SET SERDEPROPERTIES', 'SET SKEWED LOCATION', 'SET TBLPROPERTIES', 'SKEWED BY', 'TOUCH', 'UNARCHIVE PARTITION']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar ADD |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IF NOT EXISTS', 'COLUMNS', 'PARTITION']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo INT |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (boo INT) |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar ADD IF |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar ADD IF NOT |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar ADD IF NOT EXISTS |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\', country=\'us\') |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\', country=\'us\')  ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['LOCATION', 'PARTITION']
            }
          });
        });

        it('should suggest hdfs for "ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\', country=\'us\') LOCATION \'|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\', country=\'us\') LOCATION \'',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: '' }
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar ADD PARTITION (dt=\'2008-08-08\', |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\', ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] } ,
              lowerCase: false
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar ADD PARTITION (dt=\'2008-08-08\') LOCATION \'/boo\' PARTITION (|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\') LOCATION \'/boo\' PARTITION  (',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar ADD PARTITION (dt=\'2008-08-08\') LOCATION \'/boo\' PARTITION (baa=1) "', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\') LOCATION \'/boo\' PARTITION (baa=1) ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['LOCATION', 'PARTITION']
            }
          });
        });

        it('should suggest hdfs for "ALTER TABLE bar ADD PARTITION (dt=\'2008-08-08\') LOCATION \'/boo\' PARTITION (country=\'us\') LOCATION \'"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD IF NOT EXISTS PARTITION (dt=\'2008-08-08\') LOCATION \'/boo\' PARTITION (country=\'us\') LOCATION \'',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: '' }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar ARCHIVE |"', function() {
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

        it('should suggest columns for "ALTER TABLE bar CHANGE |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar CHANGE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] },
              suggestKeywords: ['COLUMN']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa INT |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa INT COMMENT \'ble\' |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar CHANGE boo baa INT COMMENT \'ble\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AFTER', 'FIRST', 'CASCADE', 'RESTRICT']
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar CHANGE boo baa INT COMMENT \'ble\' AFTER |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar CHANGE boo baa INT COMMENT \'ble\' AFTER ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar CHANGE boo baa INT FIRST |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar CHANGE boo baa INT FIRST ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar CHANGE boo baa INT FIRST ba |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar CHANGE COLUMN boo baa INT AFTER ba |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar CLUSTERED |"', function() {
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

        it('should suggest columns for "ALTER TABLE bar CLUSTERED BY (|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar CLUSTERED BY (',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar CLUSTERED BY (a, b, |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar CLUSTERED BY (a, b, ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar CLUSTERED BY (a, b, c) |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar CLUSTERED BY (a, b, c) INTO 10 |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar CLUSTERED BY (a, b, c) SORTED |"', function() {
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

        it('should suggest columns for "ALTER TABLE foo.bar CLUSTERED BY (a, b, c) SORTED BY (|"', function() {
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

        it('should suggest keywords for "ALTER TABLE foo.bar CLUSTERED BY (a, b, c) SORTED BY (a) |"', function() {
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

        it('should suggest keywords for "ALTER TABLE foo.bar CLUSTERED BY (a, b, c) SORTED BY (a) INTO 10 |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar DROP |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar DROP ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IF EXISTS', 'PARTITION']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar DROP IF |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar DROP IF EXISTS |"', function() {
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
        it('should suggest columns for "ALTER TABLE bar DROP IF EXISTS PARTITION (|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar DROP IF EXISTS PARTITION (',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar DROP IF EXISTS PARTITION (a=\'baa\'), |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar DROP IF EXISTS PARTITION (a=\'baa\'), ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PARTITION']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar DROP PARTITION (a=\'baa\') |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar DROP PARTITION (a=\'baa\') ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PURGE']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar DROP PARTITION (a=\'baa\'), PARTITION (b=\'boo\') |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar DROP PARTITION (a=\'baa\'), PARTITION (b=\'boo\') ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PURGE']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar EXCHANGE |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar EXCHANGE PARTITION ((boo=\'baa\'), (baa=\'boo\')) |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar EXCHANGE PARTITION ((boo=\'baa\'), (baa=\'boo\')) ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['WITH TABLE']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar EXCHANGE PARTITION ((boo=\'baa\'), (baa=\'boo\')) WITH |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar EXCHANGE PARTITION ((boo=\'baa\'), (baa=\'boo\')) WITH ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TABLE']
            }
          });
        });

        it('should suggest tables for "ALTER TABLE bar EXCHANGE PARTITION ((boo=\'baa\'), (baa=\'boo\')) WITH TABLE |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar EXCHANGE PARTITION ((boo=\'baa\'), (baa=\'boo\')) WITH TABLE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar NOT |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar NOT STORED |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar NOT STORED AS |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ADD COLUMNS', 'CHANGE', 'COMPACT', 'CONCATENATE', 'DISABLE NO_DROP', 'DISABLE OFFLINE',
                'ENABLE NO_DROP', 'ENABLE OFFLINE', 'RENAME TO PARTITION', 'REPLACE COLUMNS', 'SET FILEFORMAT',
                'SET LOCATION', 'SET SERDE', 'SET SERDEPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') ADD ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COLUMNS']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['INT', 'STRUCT<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo INT |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo INT ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo INT) |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') ADD COLUMNS (boo INT) ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CASCADE', 'RESTRICT']
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] },
              suggestKeywords: ['COLUMN']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col1, col2) CHANGE boo baa |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['ARRAY<>', 'INT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT', 'AFTER', 'FIRST', 'CASCADE', 'RESTRICT']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT COMMENT \'ble\' |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT COMMENT \'ble\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AFTER', 'FIRST', 'CASCADE', 'RESTRICT']
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT COMMENT \'ble\' AFTER |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT COMMENT \'ble\' AFTER ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT FIRST |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT FIRST ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT FIRST ba |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE boo baa INT FIRST ba ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CASCADE', 'RESTRICT']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') CHANGE COLUMN boo baa INT AFTER ba |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') CHANGE COLUMN boo baa INT AFTER ba ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CASCADE', 'RESTRICT']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') DISABLE |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') DISABLE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['NO_DROP', 'OFFLINE']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') ENABLE |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') ENABLE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['NO_DROP', 'OFFLINE']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') RENAME |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') RENAME ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['TO PARTITION']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') RENAME TO |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') RENAME TO ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['PARTITION']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') REPLACE ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COLUMNS']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['INT', 'STRUCT<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo INT |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo INT ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COMMENT']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo INT) |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') REPLACE COLUMNS (boo INT) ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CASCADE', 'RESTRICT']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') SET |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') SET ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (col=\'val\') SET FILEFORMAT |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') SET FILEFORMAT ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['ORC', 'PARQUET'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest hdfs for "ALTER TABLE bar PARTITION (col=\'val\') SET LOCATION \'|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (col=\'val\') SET LOCATION \'',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: '' }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar RECOVER |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar RENAME |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar REPLACE |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar REPLACE COLUMNS (boo |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar REPLACE COLUMNS (boo INT |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar REPLACE COLUMNS (boo INT) |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar SET |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar SET ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['FILEFORMAT', 'LOCATION', 'SERDE', 'SERDEPROPERTIES', 'SKEWED LOCATION', 'TBLPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar SET FILEFORMAT |"', function() {
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

        it('should suggest hdfs for "ALTER TABLE bar SET LOCATION \'|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar SET LOCATION \'',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: '' }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar SET SERDE \'boo\' |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar SET SERDE \'boo\' ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['WITH SERDEPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar SET SERDE \'boo\' WITH |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar SET SERDE \'boo\' WITH ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SERDEPROPERTIES']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar SET SKEWED |"', function() {
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

        it('should suggest columns for "ALTER TABLE bar SET SKEWED LOCATION (|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar SET SKEWED LOCATION (',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar SET SKEWED LOCATION (a=\'/boo\', |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar SET SKEWED LOCATION (a=\'/boo\', ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar SKEWED |"', function() {
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

        it('should suggest columns for "ALTER TABLE bar SKEWED BY (|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar SKEWED BY (',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestColumns:  { tables: [{ identifierChain: [{ name: 'bar' }] }] }
            }
          });
        });

        it('should suggest columns for "ALTER TABLE foo.bar SKEWED BY (a, |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) "', function() {
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

        it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) STORED "', function() {
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

        it('should suggest keywords for "ALTER TABLE bar SKEWED BY (a, b) ON ((1, 2), (2, 3)) STORED AS "', function() {
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

        it('should suggest keywords for "ALTER TABLE bar TOUCH |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar UNARCHIVE |"', function() {
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

      describe('Impala specific', function () {
        it('should handle "alter table d2.mobile rename to d3.mobile;|"', function() {
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

        it('should handle "alter table p1 partition (month=1, day=1) set location \'/usr/external_data/new_years_day\';|"', function() {
          assertAutoComplete({
            beforeCursor: 'alter table p1 partition (month=1, day=1) set location \'/usr/external_data/new_years_day\';',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: true
            }
          });
        });

        it('should handle "alter table sales_data add partition (zipcode = cast(9021 * 10 as string));|"', function() {
          assertAutoComplete({
            beforeCursor: 'alter table sales_data add partition (zipcode = cast(9021 * 10 as string));',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: true
            }
          });
        });

        it('should handle "ALTER TABLE table_name SET TBLPROPERTIES(\'EXTERNAL\'=\'FALSE\');|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE table_name SET TBLPROPERTIES(\'EXTERNAL\'=\'FALSE\');',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ADD COLUMNS', 'ADD PARTITION', 'CHANGE', 'DROP COLUMN', 'DROP PARTITION', 'PARTITION', 'RENAME TO', 'REPLACE COLUMNS', 'SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDEPROPERTIES', 'SET TBLPROPERTIES', 'SET UNCACHED' ]
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar ADD |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['COLUMNS', 'PARTITION']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar ADD COLUMNS (a INT, b |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar ADD COLUMNS (a INT, b ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['INT'],
            doesNotContainKeywords: ['ARRAY<>'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest columns for "ALTER TABLE bar ADD PARTITION (|"', function() {
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

        it('should suggest columns for "ALTER TABLE bar CHANGE |"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar CHANGE foo bar |"', function() {
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

        it('should suggest columns for "ALTER TABLE bar DROP |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar DROP ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }] }] },
              suggestKeywords: ['COLUMN', 'PARTITION']
            }
          });
        });

        // TODO: Should suggest partitions
        it('should suggest columns for "ALTER TABLE bar DROP PARTITION (|"', function() {
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

        it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (a=\'b\') ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['SET CACHED IN', 'SET FILEFORMAT', 'SET LOCATION', 'SET SERDEPROPERTIES', 'SET TBLPROPERTIES', 'SET UNCACHED']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') SET |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (a=\'b\') SET ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['CACHED IN', 'FILEFORMAT', 'LOCATION', 'SERDEPROPERTIES', 'TBLPROPERTIES', 'UNCACHED']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') SET CACHED |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (a=\'b\') SET CACHED ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['IN']
            }
          });
        });

        it('should suggest keywords for "ALTER TABLE bar PARTITION (a=\'b\') SET FILEFORMAT |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (a=\'b\') SET FILEFORMAT ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['PARQUET'],
            doesNotContainKeywords: ['ORC'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest hdfs for "ALTER TABLE bar PARTITION (a=\'b\') SET LOCATION \'|"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER TABLE bar PARTITION (a=\'b\') SET LOCATION \'',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestHdfs: { path: '' }
            }
          });
        });
      });
    });

    describe('ALTER VIEW', function () {
      it('should handle "ALTER VIEW baa.boo AS SELECT * FROM bla;|"', function() {
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

      it('should suggest keywords for "ALTER |"', function() {
        assertAutoComplete({
          beforeCursor: 'ALTER ',
          afterCursor: '',
          containsKeywords: ['VIEW'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest views for "ALTER VIEW |"', function() {
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

      it('should suggest views for "ALTER VIEW boo.|"', function() {
        assertAutoComplete({
          beforeCursor: 'ALTER VIEW boo.',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestTables: { identifierChain: [{ name: 'boo' }], onlyViews: true }
          }
        });
      });

      it('should suggest keywords for "ALTER VIEW boo |"', function() {
        assertAutoComplete({
          beforeCursor: 'ALTER VIEW boo ',
          afterCursor: '',
          containsKeywords: ['AS'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "ALTER VIEW baa.boo AS |"', function() {
        assertAutoComplete({
          beforeCursor: 'ALTER VIEW baa.boo AS ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['SELECT']
          }
        });
      });

      it('should suggest databases for "ALTER VIEW baa.boo AS SELECT * FROM |"', function() {
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

      describe('Hive specific', function () {
        it('should handle "ALTER VIEW boo SET TBLPROPERTIES ("baa"=\'boo\');|"', function() {
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

        it('should suggest keywords for "ALTER VIEW boo |"', function() {
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

        it('should suggest keywords for "ALTER VIEW boo SET |"', function() {
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

      describe('Impala specific', function () {
        it('should suggest handle "ALTER VIEW bloo.boo RENAME TO baa.bla;|"', function() {
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

        it('should suggest keywords for "ALTER VIEW boo |"', function() {
          assertAutoComplete({
            beforeCursor: 'ALTER VIEW boo ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['AS', 'RENAME TO']
            }
          });
        });

        it('should suggest keywords for "ALTER VIEW boo RENAME |"', function() {
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

        it('should suggest databases for "ALTER VIEW boo RENAME TO |"', function() {
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
      });
    });

    describe('MSCK', function () {
      it('should handle "MSCK REPAIR TABLE boo.baa;|"', function() {
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

      it('should suggest keywords for "|"', function() {
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

      it('should suggest keywords for "MSCK |"', function() {
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

      it('should suggest keywords for "MSCK REPAIR |"', function() {
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

      it('should suggest tables for "MSCK REPAIR TABLE |"', function() {
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

    describe('RELOAD FUNCTION', function () {
      it('should handle "RELOAD FUNCTION;|"', function() {
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

      it('should suggest keywords for "|"', function() {
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

      it('should suggest keywords for "reload |"', function() {
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
    })
  });
})();