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

describe('sqlAutocompleteParser.js GRANT statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

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

    describe('Hive specific', () => {
      it('should suggest keywords for "GRANT |"', () => {
        assertAutoComplete({
          beforeCursor: 'GRANT ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

    describe('Impala specific', () => {
      it('should suggest keywords for "GRANT |"', () => {
        assertAutoComplete({
          beforeCursor: 'GRANT ',
          afterCursor: '',
          noErrors: true,
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          //hasLocations: true, // TODO: should have database location
          expectedResult: {
            lowerCase: false
          }
        });
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

    describe('Hive specific', () => {
      it('should suggest keywords for "REVOKE |"', () => {
        assertAutoComplete({
          beforeCursor: 'REVOKE ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          noErrors: true,
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['GROUP', 'ROLE', 'USER']
          }
        });
      });

      it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM USER baa, |"', () => {
        assertAutoComplete({
          beforeCursor:
            'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM USER baa, ',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
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
          dialect: 'hive',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

    describe('Impala specific', () => {
      it('should suggest keywords for "REVOKE |"', () => {
        assertAutoComplete({
          beforeCursor: 'REVOKE ',
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
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
          dialect: 'impala',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });
  });
});
