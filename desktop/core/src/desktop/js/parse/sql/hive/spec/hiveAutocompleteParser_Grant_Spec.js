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

describe('hiveAutocompleteParser.js GRANT statements', () => {
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

  describe('GRANT', () => {
    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['GRANT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "GRANT |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ALL',
            'ALTER',
            'CREATE',
            'DELETE',
            'DROP',
            'INDEX',
            'INSERT',
            'LOCK',
            'ROLE',
            'SELECT',
            'UPDATE'
          ]
        }
      });
    });

    it('should suggest keywords for "GRANT ALL, |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALL, ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ALL',
            'ALTER',
            'CREATE',
            'DELETE',
            'DROP',
            'INDEX',
            'INSERT',
            'LOCK',
            'SELECT',
            'SHOW_DATABASE',
            'UPDATE'
          ]
        }
      });
    });

    it('should suggest keywords for "GRANT CREATE, DELETE |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT CREATE, DELETE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON', 'TO']
        }
      });
    });

    it('should suggest keywords for "GRANT ALTER ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALTER ON ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'TABLE'],
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "GRANT ALTER ON DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALTER ON DATABASE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest keywords for "GRANT ALTER ON DATABASE bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALTER ON DATABASE bla ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO']
        }
      });
    });

    it('should suggest keywords for "GRANT ALTER ON TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALTER ON TABLE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "GRANT ALTER ON TABLE bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALTER ON TABLE bla ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO']
        }
      });
    });

    it('should suggest keywords for "GRANT INDEX ON TABLE bla TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT INDEX ON TABLE bla TO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "GRANT INDEX ON TABLE bla TO USER bla, |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT INDEX ON TABLE bla TO USER bla, ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "GRANT INDEX ON TABLE bla TO USER bla, ROLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT INDEX ON TABLE bla TO USER bla, ROLE boo ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH GRANT OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT INDEX ON TABLE bla TO USER bla, ROLE boo WITH |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT INDEX ON TABLE bla TO USER bla, ROLE boo WITH ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GRANT OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT SHOW_DATABASE ON DATABASE boo TO USER bla, ROLE boo WITH GRANT |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT SHOW_DATABASE ON DATABASE boo TO USER bla, ROLE boo WITH GRANT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT bla, ble TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT bla, ble TO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "GRANT bla, ble TO USER baa, |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT bla, ble TO USER baa, ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "GRANT bla, ble TO USER baa, ROLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT bla, ble TO USER baa, ROLE boo  ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH ADMIN OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT ble TO ROLE baa WITH |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ble TO ROLE baa WITH ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ADMIN OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT ble TO ROLE baa WITH ADMIN |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ble TO ROLE baa WITH ADMIN ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT ROLE bla, ble TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE bla, ble TO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "GRANT ROLE bla, ble TO USER baa, |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE bla, ble TO USER baa, ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "GRANT ROLE bla, ble TO USER baa, ROLE boo |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE bla, ble TO USER baa, ROLE boo  ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH ADMIN OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT ROLE ble TO ROLE baa WITH |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE ble TO ROLE baa WITH ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ADMIN OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT ROLE ble TO ROLE baa WITH ADMIN |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE ble TO ROLE baa WITH ADMIN ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OPTION']
        }
      });
    });

    it('should handle "GRANT ROLE foo TO GROUP bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE foo TO GROUP bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "GRANT ROLE foo, bar TO USER bla, ROLE boo WITH ADMIN OPTION;|"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE foo, bar TO USER bla, ROLE boo WITH ADMIN OPTION;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "GRANT SELECT TO ROLE baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT SELECT TO ROLE baa;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "GRANT ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 TO USER baa, ROLE boo WITH GRANT OPTION;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'GRANT ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 TO USER baa, ROLE boo WITH GRANT OPTION;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('REVOKE', () => {
    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['REVOKE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "REVOKE |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ADMIN OPTION FOR',
            'ALL',
            'ALL GRANT OPTION FROM',
            'ALL PRIVILEGES FROM',
            'ALTER',
            'CREATE',
            'DELETE',
            'DROP',
            'GRANT OPTION FOR',
            'INDEX',
            'INSERT',
            'LOCK',
            'ROLE',
            'SELECT',
            'UPDATE'
          ]
        }
      });
    });

    it('should suggest keywords for "REVOKE ADMIN |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ADMIN ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM', 'OPTION FOR']
        }
      });
    });

    it('should suggest keywords for "REVOKE ADMIN OPTION |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ADMIN OPTION ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOR']
        }
      });
    });

    it('should suggest keywords for "REVOKE ADMIN OPTION FOR |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ADMIN OPTION FOR ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE']
        }
      });
    });

    it('should suggest keywords for "REVOKE ADMIN OPTION FOR ROLE bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ADMIN OPTION FOR ROLE bla ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest keywords for "REVOKE ADMIN OPTION FOR ROLE bla FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ADMIN OPTION FOR ROLE bla FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "REVOKE ADMIN OPTION FOR ROLE bla, ble FROM GROUP baa, |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ADMIN OPTION FOR ROLE bla, ble FROM GROUP baa, ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "REVOKE ALL |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM', 'GRANT OPTION', 'ON', 'PRIVILEGES FROM']
        }
      });
    });

    it('should suggest keywords for "REVOKE ALL PRIVILEGES |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL PRIVILEGES ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest keywords for "REVOKE ALL GRANT |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL GRANT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OPTION']
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OPTION FOR']
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOR']
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION FOR |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ALL',
            'ALTER',
            'CREATE',
            'DELETE',
            'DROP',
            'INDEX',
            'INSERT',
            'LOCK',
            'SELECT',
            'SHOW_DATABASE',
            'UPDATE'
          ]
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ALL',
            'ALTER',
            'CREATE',
            'DELETE',
            'DROP',
            'INDEX',
            'INSERT',
            'LOCK',
            'SELECT',
            'SHOW_DATABASE',
            'UPDATE'
          ]
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM', 'ON']
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'TABLE'],
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest tables for "REVOKE CREATE(col1), SELECT ON DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE CREATE(col1), SELECT ON DATABASE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest tables for "REVOKE CREATE(col1), SELECT ON DATABASE db1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE CREATE(col1), SELECT ON DATABASE db1 ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM USER baa, |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM USER baa, ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP', 'ROLE', 'USER']
        }
      });
    });

    it('should handle "REVOKE ROLE baa FROM GROUP bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ROLE baa FROM GROUP bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REVOKE ADMIN OPTION FOR ROLE baa, boo FROM ROLE bla, USER ble;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ADMIN OPTION FOR ROLE baa, boo FROM ROLE bla, USER ble;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REVOKE GRANT OPTION FOR ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 FROM USER baa, ROLE boo;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'REVOKE GRANT OPTION FOR ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 FROM USER baa, ROLE boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REVOKE ALL FROM GROUP ble;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL FROM GROUP ble;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REVOKE ALL PRIVILEGES FROM boo, baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL PRIVILEGES FROM boo, baa;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REVOKE ALL GRANT OPTION FROM boo;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL GRANT OPTION FROM boo;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });
});
