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

import hiveAutocompleteParser from '../../hiveAutocompleteParser';

describe('hiveAutocompleteParser.js DROP SCHEDULED QUERY statements', () => {
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

  it('should handle "DROP SCHEDULED QUERY foo; |"', () => {
    assertAutoComplete({
      beforeCursor: 'DROP SCHEDULED QUERY foo;  ',
      afterCursor: '',
      noErrors: true,
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "DROP |"', () => {
    assertAutoComplete({
      beforeCursor: 'DROP ',
      afterCursor: '',
      containsKeywords: ['SCHEDULED QUERY'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "DROP SCHEDULED |"', () => {
    assertAutoComplete({
      beforeCursor: 'DROP SCHEDULED ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['QUERY']
      }
    });
  });
});
