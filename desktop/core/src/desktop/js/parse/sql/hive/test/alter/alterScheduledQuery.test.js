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

describe('hiveAutocompleteParser.js ALTER SCHEDULED QUERY statements', () => {
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

  it('should handle "ALTER SCHEDULED QUERY sc1 CRON \'0 */10 * * * ? *\'; |"', () => {
    assertAutoComplete({
      beforeCursor: "ALTER SCHEDULED QUERY sc1 CRON '0 */10 * * * ? *'; ",
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "ALTER SCHEDULED QUERY sc1 AS INSERT INTO t VALUES (1); |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY sc1 AS INSERT INTO t VALUES (1); ',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "ALTER SCHEDULED QUERY sc1 EXECUTE; |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY sc1 EXECUTE; ',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "ALTER SCHEDULED QUERY test EVERY 10 MINUTES; |', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY test EVERY 10 MINUTES; ',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "ALTER SCHEDULED QUERY test EXECUTED AS bar; |', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY test EXECUTED AS bar; ',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "ALTER SCHEDULED QUERY test ENABLE; |', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY test ENABLE; ',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "ALTER SCHEDULED QUERY test DEFINED AS SELECT * FROM foo; |', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY test DEFINED AS SELECT * FROM foo; ',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "ALTER |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER ',
      afterCursor: '',
      containsKeywords: ['SCHEDULED QUERY'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "ALTER SCHEDULED |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['QUERY']
      }
    });
  });

  it('should suggest keywords for "ALTER SCHEDULED QUERY foo |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY foo ',
      afterCursor: '',
      containsKeywords: ['CRON', 'EVERY', 'EXECUTE', 'ENABLE', 'DEFINED AS', 'EXECUTED AS'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "ALTER SCHEDULED QUERY foo EVERY 10 |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY foo EVERY 10 ',
      afterCursor: '',
      containsKeywords: ['MINUTE', 'DAY'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "ALTER SCHEDULED QUERY foo EXECUTED |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY foo EXECUTED ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['AS']
      }
    });
  });

  it('should suggest keywords for "ALTER SCHEDULED QUERY foo DEFINED |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY foo DEFINED ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['AS']
      }
    });
  });

  it('should suggest keywords for "ALTER SCHEDULED QUERY foo DEFINED AS |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY foo DEFINED AS ',
      afterCursor: '',
      containsKeywords: ['SELECT', 'INSERT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "ALTER SCHEDULED QUERY foo AS SELECT |"', () => {
    assertAutoComplete({
      beforeCursor: 'ALTER SCHEDULED QUERY foo AS SELECT ',
      afterCursor: '',
      containsKeywords: ['*'],
      expectedResult: {
        lowerCase: false,
        suggestAggregateFunctions: { tables: [] },
        suggestAnalyticFunctions: true,
        suggestFunctions: {},
        suggestTables: { prependQuestionMark: true, prependFrom: true },
        suggestDatabases: { prependQuestionMark: true, prependFrom: true, appendDot: true }
      }
    });
  });
});
