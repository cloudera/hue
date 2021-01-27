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

import flinkAutocompleteParser from '../flinkAutocompleteParser';

describe('flinkAutocompleteParser.js SHOW statements', () => {
  beforeAll(() => {
    flinkAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      flinkAutocompleteParser.parseSql(
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
      containsKeywords: ['SHOW'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "SHOW |"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: [
          'CATALOGS',
          'CURRENT CATALOG',
          'CURRENT DATABASE',
          'DATABASES',
          'FUNCTIONS',
          'TABLES',
          'VIEWS'
        ]
      }
    });
  });

  it('should handle "SHOW CA"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW CA',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['CATALOGS', 'CURRENT CATALOG'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "SHOW TAB"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW TAB',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['TABLES', 'CURRENT DATABASE', 'DATABASES'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "SHOW DAT"', () => {
    assertAutoComplete({
      beforeCursor: 'SHOW DAT',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['DATABASES', 'CURRENT DATABASE'],
      expectedResult: {
        lowerCase: false
      }
    });
  });
});
