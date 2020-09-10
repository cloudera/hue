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

describe('hiveAutocompleteParser.js CREATE SCHEDULED QUERY statements', () => {
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

  it('should handle "CREATE SCHEDULED QUERY sc1 CRON \'0 */10 * * * ? *\' AS INSERT INTO t VALUES (1); |"', () => {
    assertAutoComplete({
      beforeCursor:
        "CREATE SCHEDULED QUERY sc1 CRON '0 */10 * * * ? *' AS INSERT INTO t VALUES (1); ",
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should handle "CREATE SCHEDULED QUERY test EVERY 10 MINUTES EXECUTED AS bar DISABLED DEFINED AS SELECT * FROM foo; |', () => {
    assertAutoComplete({
      beforeCursor:
        'CREATE SCHEDULED QUERY test EVERY 10 MINUTES EXECUTED AS bar DISABLED DEFINED AS SELECT * FROM foo; ',
      afterCursor: '',
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
      containsKeywords: ['SCHEDULED QUERY'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['QUERY']
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['CRON', 'EVERY']
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 10 |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 10 ',
      afterCursor: '',
      containsKeywords: ['MINUTE', 'DAY'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 10 DAY |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 10 DAY ',
      afterCursor: '',
      containsKeywords: ['EXECUTED AS', 'ENABLED', 'DISABLE', 'DEFINED AS', 'AS'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo CRON \'Some cron\' |"', () => {
    assertAutoComplete({
      beforeCursor: "CREATE SCHEDULED QUERY foo CRON 'Some cron' ",
      afterCursor: '',
      containsKeywords: ['EXECUTED AS', 'ENABLED', 'DISABLE', 'DEFINED AS', 'AS'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo CRON \'Some cron\' EXECUTED |"', () => {
    assertAutoComplete({
      beforeCursor: "CREATE SCHEDULED QUERY foo CRON 'Some cron' EXECUTED ",
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['AS']
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 1 MINUTE EXECUTED AS bar |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 1 MINUTE EXECUTED AS bar ',
      afterCursor: '',
      containsKeywords: ['ENABLED', 'DISABLE', 'DEFINED AS', 'AS'],
      doesNotContainKeywords: ['EXECUTED AS'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 1 MINUTE EXECUTED AS bar DISABLE |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 1 MINUTE EXECUTED AS bar DISABLE ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['AS', 'DEFINED AS']
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['AS', 'DEFINED AS']
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED DEFINED |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED DEFINED ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['AS']
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED DEFINED AS |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED DEFINED AS ',
      afterCursor: '',
      containsKeywords: ['SELECT', 'INSERT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED AS |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED AS ',
      afterCursor: '',
      containsKeywords: ['SELECT', 'INSERT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED AS SELECT |"', () => {
    assertAutoComplete({
      beforeCursor: 'CREATE SCHEDULED QUERY foo EVERY 1 MINUTE ENABLED AS SELECT ',
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
