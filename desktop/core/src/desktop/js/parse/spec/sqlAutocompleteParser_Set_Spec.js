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

describe('sqlAutocompleteParser.js SET statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  it('should suggest keywords for "|"', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: '',
      containsKeywords: ['SET'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  describe('Impala specific', () => {
    it('should handle "SET ALL; |"', () => {
      assertAutoComplete({
        beforeCursor: 'SET ALL; ',
        afterCursor: '',
        noErrors: true,
        dialect: 'impala',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'SET ',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestSetOptions: true,
          suggestKeywords: ['ALL']
        }
      });
    });
  });

  describe('SET ROLE', () => {
    it('should handle "SET ROLE baaa;', () => {
      assertAutoComplete({
        beforeCursor: 'SET ROLE baaa;',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SET ROLE ALL;', () => {
      assertAutoComplete({
        beforeCursor: 'SET ROLE ALL;',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SET ROLE NONE;', () => {
      assertAutoComplete({
        beforeCursor: 'SET ROLE NONE;',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SET |"', () => {
      assertAutoComplete({
        beforeCursor: 'SET ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE'],
          suggestSetOptions: true
        }
      });
    });

    it('should suggest keywords for "set role |"', () => {
      assertAutoComplete({
        beforeCursor: 'set role ',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['ALL', 'NONE']
        }
      });
    });
  });
});
