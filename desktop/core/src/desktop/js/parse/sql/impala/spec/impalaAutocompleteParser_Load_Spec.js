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

describe('impalaAutocompleteParser.js LOAD statements', () => {
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
        suggestKeywords: ['DATA INPATH']
      }
    });
  });

  it('should suggest keywords for "LOAD DATA |"', () => {
    assertAutoComplete({
      beforeCursor: 'LOAD DATA ',
      afterCursor: '',
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
      expectedResult: {
        lowerCase: false,
        suggestHdfs: { path: '/' }
      }
    });
  });
});
