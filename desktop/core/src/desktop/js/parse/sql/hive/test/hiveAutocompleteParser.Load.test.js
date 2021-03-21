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
describe('hiveAutocompleteParser.js LOAD statements', () => {
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

  it("should handle \"LOAD DATA LOCAL INPATH '/filepath' OVERWRITE INTO TABLE db.tablename PARTITION (partcol1='baa', partcol2=1);|\"", () => {
    assertAutoComplete({
      beforeCursor:
        "LOAD DATA LOCAL INPATH '/filepath' OVERWRITE INTO TABLE db.tablename PARTITION (partcol1='baa', partcol2=1);",
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it(
    "should handle \"LOAD DATA LOCAL INPATH '/filepath' OVERWRITE INTO TABLE db.tablename PARTITION (partcol1='baa', partcol2=1) " +
      "INPUTFORMAT 'foo' SERDE 'bar';|\"",
    () => {
      assertAutoComplete({
        beforeCursor:
          "LOAD DATA LOCAL INPATH '/filepath' OVERWRITE INTO TABLE db.tablename PARTITION (partcol1='baa', partcol2=1) INPUTFORMAT 'foo' SERDE 'bar';",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
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
      expectedResult: {
        lowerCase: false,
        suggestHdfs: { path: '/' }
      }
    });
  });

  it('should suggest hdfs paths for "LOAD DATA INPATH "/|""', () => {
    assertAutoComplete({
      beforeCursor: 'LOAD DATA INPATH "/',
      afterCursor: '"',
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
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['INPUTFORMAT', 'PARTITION']
      }
    });
  });

  it('should suggest columns for "LOAD DATA INPATH \'baa\' INTO TABLE boo.baa PARTITION (|"', () => {
    assertAutoComplete({
      beforeCursor: "LOAD DATA INPATH 'baa' INTO TABLE boo.baa PARTITION (",
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }, { name: 'baa' }] }] }
      }
    });
  });

  it("should suggest keywords for \"LOAD DATA INPATH 'baa' INTO TABLE baa INPUTORMAT 'foo' |\"", () => {
    assertAutoComplete({
      beforeCursor: "LOAD DATA INPATH 'baa' INTO TABLE baa INPUTFORMAT '\foo' ",
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['SERDE']
      }
    });
  });
});
