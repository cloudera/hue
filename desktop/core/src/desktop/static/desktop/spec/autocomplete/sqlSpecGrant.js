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

(function () {
  describe('sql.js GRANT statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

    describe('GRANT', function () {

      it('should suggest keywords for "|"', function() {
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

      describe('Hive specific', function () {

        it('should suggest keywords for "GRANT |"', function() {
          assertAutoComplete({
            beforeCursor: 'GRANT ',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'ROLE', 'SELECT', 'UPDATE']
            }
          });
        });

        it('should suggest keywords for "GRANT ALL, |"', function() {
          assertAutoComplete({
            beforeCursor: 'GRANT ALL, ',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'SELECT', 'SHOW_DATABASE', 'UPDATE']
            }
          });
        });

        it('should suggest keywords for "GRANT CREATE, DELETE |"', function() {
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

        it('should suggest keywords for "GRANT ALTER ON |"', function() {
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

        it('should suggest keywords for "GRANT ALTER ON DATABASE |"', function() {
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

        it('should suggest keywords for "GRANT ALTER ON DATABASE bla |"', function() {
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

        it('should suggest keywords for "GRANT ALTER ON TABLE |"', function() {
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

        it('should suggest keywords for "GRANT ALTER ON TABLE bla |"', function() {
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

        it('should suggest keywords for "GRANT INDEX ON TABLE bla TO |"', function() {
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

        it('should suggest keywords for "GRANT INDEX ON TABLE bla TO USER bla, |"', function() {
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

        it('should suggest keywords for "GRANT INDEX ON TABLE bla TO USER bla, ROLE boo |"', function() {
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

        it('should suggest keywords for "GRANT INDEX ON TABLE bla TO USER bla, ROLE boo WITH |"', function() {
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

        it('should suggest keywords for "GRANT SHOW_DATABASE ON DATABASE boo TO USER bla, ROLE boo WITH GRANT |"', function() {
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

        it('should suggest keywords for "GRANT bla, ble TO |"', function() {
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

        it('should suggest keywords for "GRANT bla, ble TO USER baa, |"', function() {
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

        it('should suggest keywords for "GRANT bla, ble TO USER baa, ROLE boo |"', function() {
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

        it('should suggest keywords for "GRANT ble TO ROLE baa WITH |"', function() {
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

        it('should suggest keywords for "GRANT ble TO ROLE baa WITH ADMIN |"', function() {
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

        it('should suggest keywords for "GRANT ROLE bla, ble TO |"', function() {
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

        it('should suggest keywords for "GRANT ROLE bla, ble TO USER baa, |"', function() {
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

        it('should suggest keywords for "GRANT ROLE bla, ble TO USER baa, ROLE boo |"', function() {
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

        it('should suggest keywords for "GRANT ROLE ble TO ROLE baa WITH |"', function() {
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

        it('should suggest keywords for "GRANT ROLE ble TO ROLE baa WITH ADMIN |"', function() {
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

        it('should handle "GRANT ROLE foo TO GROUP bla;|"', function() {
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

        it('should handle "GRANT ROLE foo, bar TO USER bla, ROLE boo WITH ADMIN OPTION;|"', function() {
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

        it('should handle "GRANT SELECT TO ROLE baa;|"', function() {
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

        it('should handle "GRANT ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 TO USER baa, ROLE boo WITH GRANT OPTION;|"', function() {
          assertAutoComplete({
            beforeCursor: 'GRANT ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 TO USER baa, ROLE boo WITH GRANT OPTION;',
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

      describe('Impala specific', function () {
        it('should suggest keywords for "GRANT |"', function() {
          assertAutoComplete({
            beforeCursor: 'GRANT ',
            afterCursor: '',
            noErrors: true,
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ALL', 'INSERT', 'ROLE', 'SELECT']
            }
          });
        });

        it('should suggest keywords for "GRANT ROLE baa |"', function() {
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

        it('should suggest keywords for "GRANT ROLE baa TO |"', function() {
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

        it('should suggest keywords for "GRANT SELECT |"', function() {
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

        it('should suggest keywords for "GRANT INSERT ON |"', function() {
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

        it('should suggest tables for "GRANT INSERT ON TABLE |"', function() {
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

        it('should suggest databases for "GRANT INSERT ON DATABASE |"', function() {
          assertAutoComplete({
            beforeCursor: 'GRANT INSERT ON DATABASE ',
            afterCursor: '',
            noErrors: true,
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestDatabases: { }
            }
          });
        });

        it('should suggest keywords for "GRANT ALL ON TABLE tbl |"', function() {
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

        it('should suggest keywords for "GRANT ALL ON TABLE tbl TO |"', function() {
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

        it('should suggest keywords for "GRANT ALL ON TABLE tbl TO bla |"', function() {
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

        it('should suggest keywords for "GRANT ALL ON TABLE tbl TO bla WITH |"', function() {
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

        it('should suggest keywords for "GRANT ALL ON TABLE tbl TO bla WITH GRANT |"', function() {
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

        it('should handle "GRANT ROLE baa TO GROUP ble;|"', function() {
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

        it('should handle "GRANT SELECT(id) ON TABLE tbl TO ROLE bla WITH GRANT OPTION;|"', function() {
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

        it('should handle "GRANT ALL ON DATABASE db1 TO bla;|"', function() {
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

    describe('REVOKE', function () {
      it('should suggest keywords for "|"', function() {
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

      describe('Hive specific', function () {
        it('should suggest keywords for "REVOKE |"', function() {
          assertAutoComplete({
            beforeCursor: 'REVOKE ',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ADMIN OPTION FOR', 'ALL', 'ALL GRANT OPTION FROM', 'ALL PRIVILEGES FROM', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'GRANT OPTION FOR', 'INDEX', 'INSERT', 'LOCK', 'ROLE', 'SELECT', 'UPDATE']
            }
          });
        });

        it('should suggest keywords for "REVOKE ADMIN |"', function() {
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

        it('should suggest keywords for "REVOKE ADMIN OPTION |"', function() {
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

        it('should suggest keywords for "REVOKE ADMIN OPTION FOR |"', function() {
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

        it('should suggest keywords for "REVOKE ADMIN OPTION FOR ROLE bla |"', function() {
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

        it('should suggest keywords for "REVOKE ADMIN OPTION FOR ROLE bla FROM |"', function() {
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

        it('should suggest keywords for "REVOKE ADMIN OPTION FOR ROLE bla, ble FROM GROUP baa, |"', function() {
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

        it('should suggest keywords for "REVOKE ALL |"', function() {
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

        it('should suggest keywords for "REVOKE ALL PRIVILEGES |"', function() {
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

        it('should suggest keywords for "REVOKE ALL GRANT |"', function() {
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

        it('should suggest keywords for "REVOKE GRANT |"', function() {
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

        it('should suggest keywords for "REVOKE GRANT OPTION |"', function() {
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

        it('should suggest keywords for "REVOKE GRANT OPTION FOR |"', function() {
          assertAutoComplete({
            beforeCursor: 'REVOKE GRANT OPTION FOR ',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'SELECT', 'SHOW_DATABASE', 'UPDATE']
            }
          });
        });

        it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), |"', function() {
          assertAutoComplete({
            beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), ',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ALL', 'ALTER', 'CREATE', 'DELETE', 'DROP', 'INDEX', 'INSERT', 'LOCK', 'SELECT', 'SHOW_DATABASE', 'UPDATE']
            }
          });
        });

        it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT |"', function() {
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

        it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON |"', function() {
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

        it('should suggest tables for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE |"', function() {
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

        it('should suggest tables for "REVOKE CREATE(col1), SELECT ON DATABASE |"', function() {
          assertAutoComplete({
            beforeCursor: 'REVOKE CREATE(col1), SELECT ON DATABASE ',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestDatabases: { }
            }
          });
        });

        it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 |"', function() {
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

        it('should suggest tables for "REVOKE CREATE(col1), SELECT ON DATABASE db1 |"', function() {
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

        it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM |"', function() {
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

        it('should suggest keywords for "REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM USER baa, |"', function() {
          assertAutoComplete({
            beforeCursor: 'REVOKE GRANT OPTION FOR CREATE(col1), SELECT ON TABLE tbl1 FROM USER baa, ',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['GROUP', 'ROLE', 'USER']
            }
          });
        });

        it('should handle "REVOKE ROLE baa FROM GROUP bla;|"', function() {
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

        it('should handle "REVOKE ADMIN OPTION FOR ROLE baa, boo FROM ROLE bla, USER ble;|"', function() {
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

        it('should handle "REVOKE GRANT OPTION FOR ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 FROM USER baa, ROLE boo;|"', function() {
          assertAutoComplete({
            beforeCursor: 'REVOKE GRANT OPTION FOR ALTER (col1, col2), LOCK, ALL (col3, col4) ON TABLE tbl1 FROM USER baa, ROLE boo;',
            afterCursor: '',
            dialect: 'hive',
            noErrors: true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should handle "REVOKE ALL FROM GROUP ble;|"', function() {
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

        it('should handle "REVOKE ALL PRIVILEGES FROM boo, baa;|"', function() {
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

        it('should handle "REVOKE ALL GRANT OPTION FROM boo;|"', function() {
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

      describe('Impala specific', function () {
        it('should suggest keywords for "REVOKE |"', function() {
          assertAutoComplete({
            beforeCursor: 'REVOKE ',
            afterCursor: '',
            dialect: 'impala',
            noErrors: true,
            expectedResult: {
              lowerCase: false,
              suggestKeywords: ['ALL', 'INSERT', 'ROLE', 'SELECT']
            }
          });
        });

        it('should suggest keywords for "REVOKE ALL |"', function() {
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

        it('should suggest keywords for "REVOKE ALL ON |"', function() {
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

        it('should suggest databases for "REVOKE ALL ON DATABASE |"', function() {
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

        it('should suggest tables for "REVOKE INSERT ON TABLE |"', function() {
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

        it('should suggest keywords for "REVOKE INSERT ON TABLE tbl1 |"', function() {
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

        it('should suggest keywords for "REVOKE SELECT ON DATABASE db1 FROM |"', function() {
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

        it('should suggest keywords for "REVOKE SELECT ON DATABASE db1 FROM |"', function() {
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

        it('should suggest keywords for "REVOKE ROLE bla |"', function() {
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

        it('should suggest keywords for "REVOKE ROLE bla FROM |"', function() {
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

        it('should handle "REVOKE ROLE bla FROM GROUP ble;|"', function() {
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

        it('should handle "REVOKE SELECT(id) ON SERVER ble FROM ROLE bla;|"', function() {
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

        it('should handle "REVOKE INSERT ON TABLE ble FROM bla;|"', function() {
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
})();