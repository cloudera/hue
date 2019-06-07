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

describe('sqlAutocompleteParser.js LOAD statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  describe('Impala specific', () => {
    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        dialect: 'impala',
        containsKeywords: ['LOAD'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "LOAD |"', () => {
      assertAutoComplete({
        beforeCursor: 'LOAD ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATA INPATH']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA |"', () => {
      assertAutoComplete({
        beforeCursor: 'LOAD DATA ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INPATH']
        }
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'|\'"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH '",
        afterCursor: "'",
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'/|"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH '/",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/' }
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'/some/path\' |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH '/some/path' ",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO TABLE', 'OVERWRITE INTO TABLE']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'/some/path\' OVERWRITE |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH '/some/path' OVERWRITE ",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO TABLE']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'some/path\' INTO |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'some/path' INTO ",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'some/path\' INTO TABLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'some/path' INTO TABLE boo ",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest columns for "LOAD DATA INPATH \'some/path\' INTO TABLE boo PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'some/path' INTO TABLE boo PARTITION (",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }] }] }
        }
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'/|/bar\' INTO TABLE foo"', () => {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: "LOAD DATA INPATH '/",
        afterCursor: "/bar' INTO TABLE foo",
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/' }
        }
      });
    });
  });

  describe('Hive specific', () => {
    it("should handle \"LOAD DATA LOCAL INPATH '/filepath' OVERWRITE INTO TABLE db.tablename PARTITION (partcol1='baa', partcol2=1);|\"", () => {
      assertAutoComplete({
        beforeCursor:
          "LOAD DATA LOCAL INPATH '/filepath' OVERWRITE INTO TABLE db.tablename PARTITION (partcol1='baa', partcol2=1);",
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
        containsKeywords: ['LOAD'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "LOAD |"', () => {
      assertAutoComplete({
        beforeCursor: 'LOAD ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATA INPATH', 'DATA LOCAL INPATH']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA |"', () => {
      assertAutoComplete({
        beforeCursor: 'LOAD DATA ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INPATH', 'LOCAL INPATH']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA LOCAL |"', () => {
      assertAutoComplete({
        beforeCursor: 'LOAD DATA LOCAL ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INPATH']
        }
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'/|\'"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH '/",
        afterCursor: "'",
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/' }
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'baa\' |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'baa' ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO TABLE', 'OVERWRITE INTO TABLE']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'baa\' OVERWRITE |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'baa' OVERWRITE ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['INTO TABLE']
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'baa\' INTO |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'baa' INTO ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "LOAD DATA INPATH \'baa\' OVERWRITE INTO TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'baa' OVERWRITE INTO TABLE ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "LOAD DATA INPATH \'baa\' INTO TABLE baa |"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'baa' INTO TABLE baa ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION']
        }
      });
    });

    it('should suggest columns for "LOAD DATA INPATH \'baa\' INTO TABLE boo.baa PARTITION (|"', () => {
      assertAutoComplete({
        beforeCursor: "LOAD DATA INPATH 'baa' INTO TABLE boo.baa PARTITION (",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
        }
      });
    });
  });
});

describe('sqlAutocompleteParser.js IMPORT and EXPORT statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  describe('Hive specific', () => {
    it("should handle \"IMPORT EXTERNAL TABLE foo PARTITION (bar=1, boo=2) FROM '/bla/bla' LOCATION '/ble/ble';|\"", () => {
      assertAutoComplete({
        beforeCursor:
          "IMPORT EXTERNAL TABLE foo PARTITION (bar=1, boo=2) FROM '/bla/bla' LOCATION '/ble/ble';",
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"IMPORT TABLE foo PARTITION (bar=1, boo=2) FROM '/bla/bla' LOCATION '/ble/ble';|\"", () => {
      assertAutoComplete({
        beforeCursor:
          "IMPORT TABLE foo PARTITION (bar=1, boo=2) FROM '/bla/bla' LOCATION '/ble/ble';",
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"IMPORT TABLE foo FROM '/bla/bla' LOCATION '/ble/ble';|\"", () => {
      assertAutoComplete({
        beforeCursor: "IMPORT TABLE foo FROM '/bla/bla' LOCATION '/ble/ble';",
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"IMPORT FROM '/bla/bla' LOCATION '/ble/ble';|\"", () => {
      assertAutoComplete({
        beforeCursor: "IMPORT FROM '/bla/bla' LOCATION '/ble/ble';",
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "IMPORT FROM \'/bla/bla\';|"', () => {
      assertAutoComplete({
        beforeCursor: "IMPORT FROM '/bla/bla';",
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
        containsKeywords: ['EXPORT', 'IMPORT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "IMPORT |"', () => {
      assertAutoComplete({
        beforeCursor: 'IMPORT ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['EXTERNAL TABLE', 'FROM', 'TABLE']
        }
      });
    });

    it('should suggest keywords for "IMPORT EXTERNAL |"', () => {
      assertAutoComplete({
        beforeCursor: 'IMPORT EXTERNAL ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "IMPORT TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'IMPORT TABLE ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "IMPORT EXTERNAL TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'IMPORT EXTERNAL TABLE ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "IMPORT TABLE bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'IMPORT TABLE bla ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'FROM']
        }
      });
    });

    it('should suggest keywords for "IMPORT EXTERNAL TABLE bla PARTITION (bla=1) |"', () => {
      assertAutoComplete({
        beforeCursor: 'IMPORT EXTERNAL TABLE bla PARTITION (bla=1) ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest hdfs for "IMPORT EXTERNAL TABLE bla PARTITION (bla=1) FROM \'|"', () => {
      assertAutoComplete({
        beforeCursor: "IMPORT EXTERNAL TABLE bla PARTITION (bla=1) FROM '",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "IMPORT FROM \'/bla/bla\' |"', () => {
      assertAutoComplete({
        beforeCursor: "IMPORT FROM '/bla/bla' ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['LOCATION']
        }
      });
    });

    it("should suggest hdfs for \"IMPORT EXTERNAL TABLE bla PARTITION (bla=1) FROM '/bla/bla' LOCATION '|\"", () => {
      assertAutoComplete({
        beforeCursor: "IMPORT EXTERNAL TABLE bla PARTITION (bla=1) FROM '/bla/bla' LOCATION '/bla/",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/bla/' }
        }
      });
    });

    it("should handle \"EXPORT TABLE db.tbl PARTITION (foo=1, bar=2) TO '/bla/bla' FOR REPLICATION('blaaa');|\"", () => {
      assertAutoComplete({
        beforeCursor:
          "EXPORT TABLE db.tbl PARTITION (foo=1, bar=2) TO '/bla/bla' FOR REPLICATION('blaaa');",
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"EXPORT TABLE db.tbl TO '/bla/bla' FOR REPLICATION('blaaa');|\"", () => {
      assertAutoComplete({
        beforeCursor: "EXPORT TABLE db.tbl TO '/bla/bla' FOR REPLICATION('blaaa');",
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "EXPORT TABLE db.tbl TO \'/bla/bla\';|"', () => {
      assertAutoComplete({
        beforeCursor: "EXPORT TABLE db.tbl TO '/bla/bla';",
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "EXPORT |"', () => {
      assertAutoComplete({
        beforeCursor: 'EXPORT ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "EXPORT TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'EXPORT TABLE ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "EXPORT TABLE db.tbl |"', () => {
      assertAutoComplete({
        beforeCursor: 'EXPORT TABLE db.tbl ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'TO']
        }
      });
    });

    it('should suggest keywords for "EXPORT TABLE db.tbl PARTITION (bla=1) |"', () => {
      assertAutoComplete({
        beforeCursor: 'EXPORT TABLE db.tbl PARTITION (bla=1) ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO']
        }
      });
    });

    it('should suggest hdfs for "EXPORT TABLE db.tbl PARTITION (bla=1) TO \'|"', () => {
      assertAutoComplete({
        beforeCursor: "EXPORT TABLE db.tbl PARTITION (bla=1) TO '",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '' }
        }
      });
    });

    it('should suggest keywords for "EXPORT TABLE db.tbl TO \'/bla/bla\' |"', () => {
      assertAutoComplete({
        beforeCursor: "EXPORT TABLE db.tbl TO '/bla/bla' ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOR replication()']
        }
      });
    });

    it('should suggest keywords for "EXPORT TABLE db.tbl TO \'/bla/bla\' FOR |"', () => {
      assertAutoComplete({
        beforeCursor: "EXPORT TABLE db.tbl TO '/bla/bla' FOR ",
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['replication()']
        }
      });
    });
  });
});
