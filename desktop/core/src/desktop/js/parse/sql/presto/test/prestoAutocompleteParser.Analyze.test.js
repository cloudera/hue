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
import prestoAutocompleteParser from '../prestoAutocompleteParser';

describe('prestoAutocompleteParser.js ANALYZE statements', () => {
  beforeAll(() => {
    prestoAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      prestoAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  describe('ANALYZE TABLE', () => {
    it('should handle "ANALYZE TABLE boo.baa PARTITION (bla=1, boo=\'baa\') COMPUTE STATISTICS FOR COLUMNS CACHE METADATA NOSCAN;|"', () => {
      assertAutoComplete({
        beforeCursor:
          "ANALYZE TABLE boo.baa PARTITION (bla=1, boo='baa') COMPUTE STATISTICS FOR COLUMNS CACHE METADATA NOSCAN;",
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
        noErrors: true,
        containsKeywords: ['ANALYZE TABLE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "analyze |"', () => {
      assertAutoComplete({
        beforeCursor: 'analyze ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest keywords for "analyze | tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'analyze ',
        afterCursor: ' tbl',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest keywords for "analyze tab| tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'analyze tab',
        afterCursor: ' tbl',
        noErrors: true,
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['TABLE']
        }
      });
    });

    it('should suggest tables for "ANALYZE TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "ANALYZE TABLE boo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo.',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }], onlyTables: true }
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PARTITION', 'COMPUTE STATISTICS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE boo PARTITION (baa = 1) |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo PARTITION (baa = 1) ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COMPUTE STATISTICS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE boo PARTITION (baa = 1) COMPUTE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE boo PARTITION (baa = 1) COMPUTE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['STATISTICS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOR COLUMNS', 'CACHE METADATA', 'NOSCAN']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['COLUMNS']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CACHE METADATA', 'NOSCAN']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['METADATA']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE METADATA |"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS CACHE METADATA ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOSCAN']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS | NOSCAN"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS ',
        afterCursor: ' NOSCAN',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOR COLUMNS', 'CACHE METADATA']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS CACHE | NOSCAN"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS CACHE ',
        afterCursor: ' NOSCAN',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['METADATA']
        }
      });
    });

    it('should suggest keywords for "ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS | NOSCAN"', () => {
      assertAutoComplete({
        beforeCursor: 'ANALYZE TABLE baa.boo COMPUTE STATISTICS FOR COLUMNS ',
        afterCursor: ' NOSCAN',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CACHE METADATA']
        }
      });
    });
  });
});
