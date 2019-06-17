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

describe('impalaAutocompleteParser.js GRANT statements', () => {
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
            'DROP',
            'INSERT',
            'REFRESH',
            'ROLE',
            'SELECT'
          ]
        }
      });
    });

    it('should suggest keywords for "GRANT ALTER ON SERVER svr TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALTER ON SERVER svr TO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE']
        }
      });
    });

    it('should suggest keywords for "GRANT DROP ON SERVER svr |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT DROP ON SERVER svr ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO']
        }
      });
    });

    it('should suggest keywords for "GRANT ROLE baa |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE baa ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO GROUP']
        }
      });
    });

    it('should suggest keywords for "GRANT ROLE baa TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE baa TO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP']
        }
      });
    });

    it('should suggest keywords for "GRANT SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT SELECT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']
        }
      });
    });

    it('should suggest keywords for "GRANT INSERT ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT INSERT ON ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'SERVER', 'TABLE', 'URI']
        }
      });
    });

    it('should suggest tables for "GRANT INSERT ON TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT INSERT ON TABLE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest databases for "GRANT INSERT ON DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT INSERT ON DATABASE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest keywords for "GRANT ALL ON TABLE tbl |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALL ON TABLE tbl ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['TO']
        }
      });
    });

    it('should suggest keywords for "GRANT ALL ON TABLE tbl TO |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALL ON TABLE tbl TO ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE']
        }
      });
    });

    it('should suggest keywords for "GRANT ALL ON TABLE tbl TO bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALL ON TABLE tbl TO bla ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WITH GRANT OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT ALL ON TABLE tbl TO bla WITH |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALL ON TABLE tbl TO bla WITH ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GRANT OPTION']
        }
      });
    });

    it('should suggest keywords for "GRANT ALL ON TABLE tbl TO bla WITH GRANT |"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALL ON TABLE tbl TO bla WITH GRANT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OPTION']
        }
      });
    });

    it('should handle "GRANT ROLE baa TO GROUP ble;|"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ROLE baa TO GROUP ble;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "GRANT SELECT(id) ON TABLE tbl TO ROLE bla WITH GRANT OPTION;|"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT SELECT(id) ON TABLE tbl TO ROLE bla WITH GRANT OPTION;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "GRANT ALL ON DATABASE db1 TO bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'GRANT ALL ON DATABASE db1 TO bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        //hasLocations: true, // TODO: should have database location
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
            'ALL',
            'ALTER',
            'CREATE',
            'DROP',
            'INSERT',
            'REFRESH',
            'ROLE',
            'SELECT'
          ]
        }
      });
    });

    it('should suggest keywords for "REVOKE CREATE |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE CREATE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON DATABASE', 'ON SERVER']
        }
      });
    });

    it('should suggest keywords for "REVOKE REFRESH |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE REFRESH ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']
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
          suggestKeywords: ['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']
        }
      });
    });

    it('should suggest keywords for "REVOKE ALL ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL ON ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['DATABASE', 'SERVER', 'TABLE', 'URI']
        }
      });
    });

    it('should suggest databases for "REVOKE ALL ON DATABASE |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ALL ON DATABASE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestDatabases: {}
        }
      });
    });

    it('should suggest tables for "REVOKE INSERT ON TABLE |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE INSERT ON TABLE ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "REVOKE INSERT ON TABLE tbl1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE INSERT ON TABLE tbl1 ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest keywords for "REVOKE SELECT ON DATABASE db1 FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE INSERT ON TABLE tbl1 FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE']
        }
      });
    });

    it('should suggest keywords for "REVOKE SELECT ON DATABASE db1 FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE INSERT ON TABLE tbl1 FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROLE']
        }
      });
    });

    it('should suggest keywords for "REVOKE ROLE bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ROLE bla ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM GROUP']
        }
      });
    });

    it('should suggest keywords for "REVOKE ROLE bla FROM |"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ROLE bla FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['GROUP']
        }
      });
    });

    it('should handle "REVOKE ROLE bla FROM GROUP ble;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE ROLE bla FROM GROUP ble;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REVOKE SELECT(id) ON SERVER ble FROM ROLE bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE SELECT ON SERVER ble FROM ROLE bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        hasLocations: false,
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "REVOKE INSERT ON TABLE ble FROM bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'REVOKE INSERT ON TABLE ble FROM bla;',
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
