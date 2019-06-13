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
import genericAutocompleteParser from '../genericAutocompleteParser';

describe('genericAutocompleteParser.js ALTER statements', () => {
  beforeAll(() => {
    genericAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;
    expect(
      genericAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  describe('ALTER TABLE', () => {
    it('should suggest keywords for "ALTER |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER ',
        afterCursor: '',
        containsKeywords: ['TABLE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "ALTER TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyTables: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "ALTER TABLE foo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER TABLE foo.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'foo' }], onlyTables: true }
        }
      });
    });
  });

  describe('ALTER VIEW', () => {
    it('should handle "ALTER VIEW baa.boo AS SELECT * FROM bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW baa.boo AS SELECT * FROM bla;',
        afterCursor: '',
        noErrors: true,
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
        containsKeywords: ['VIEW'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest views for "ALTER VIEW |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { onlyViews: true },
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest views for "ALTER VIEW boo.|"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'boo' }], onlyViews: true }
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW boo ',
        afterCursor: '',
        containsKeywords: ['AS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "ALTER VIEW baa.boo AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW baa.boo AS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest databases for "ALTER VIEW baa.boo AS SELECT * FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'ALTER VIEW baa.boo AS SELECT * FROM ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });
  });
});
