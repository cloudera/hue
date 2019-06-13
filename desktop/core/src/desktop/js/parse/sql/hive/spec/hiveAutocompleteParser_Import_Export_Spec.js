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
import SqlTestUtils from '../../../spec/sqlTestUtils';

describe('hiveAutocompleteParser.js IMPORT and EXPORT statements', () => {
  beforeAll(() => {
    hiveAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
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

  it("should handle \"IMPORT EXTERNAL TABLE foo PARTITION (bar=1, boo=2) FROM '/bla/bla' LOCATION '/ble/ble';|\"", () => {
    assertAutoComplete({
      beforeCursor:
        "IMPORT EXTERNAL TABLE foo PARTITION (bar=1, boo=2) FROM '/bla/bla' LOCATION '/ble/ble';",
      afterCursor: '',
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
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['replication()']
      }
    });
  });
});
