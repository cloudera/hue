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
define([
  'knockout',
  'desktop/js/autocomplete/sql',
  'desktop/spec/autocompleterTestUtils',
  'desktop/spec/autocomplete/sqlSpecCreate',
  'desktop/spec/autocomplete/sqlSpecDescribe',
  'desktop/spec/autocomplete/sqlSpecDrop',
  'desktop/spec/autocomplete/sqlSpecLoad',
  'desktop/spec/autocomplete/sqlSpecSelect',
  'desktop/spec/autocomplete/sqlSpecShow',
  'desktop/spec/autocomplete/sqlSpecUpdate',
  'desktop/spec/autocomplete/sqlSpecUse'
], function(ko, sql, testUtils) {

  describe('sql.js', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = testUtils.assertAutocomplete;

    describe('Impala specific', function () {
      it('should suggest keywords for empty statement', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ALTER', 'COMPUTE', 'CREATE', 'DELETE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'INSERT', 'INVALIDATE', 'LOAD', 'REFRESH',
              'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE']
          }
        });
      });

      it('should suggest keywords for partial statement', function() {
        assertAutoComplete({
          beforeCursor: 'foo',
          afterCursor: 'bar',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ALTER', 'COMPUTE', 'CREATE', 'DELETE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'INSERT', 'INVALIDATE', 'LOAD', 'REFRESH',
              'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE']
          }
        });
      });
    });

    describe('Hive specific', function () {
      it('should suggest keywords for empty statement', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ALTER', 'ANALYZE', 'CREATE', 'DELETE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'EXPORT', 'IMPORT', 'INSERT', 'LOAD', 'MSCK',
              'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE']
          }
        });
      });

      it('should suggest keywords for partial statement', function() {
        assertAutoComplete({
          beforeCursor: 'foo',
          afterCursor: 'bar',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ALTER', 'ANALYZE', 'CREATE', 'DELETE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'EXPORT', 'IMPORT', 'INSERT', 'LOAD', 'MSCK',
              'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE']
          }
        });
      });
    });

    it('should ignore line comments for local suggestions', function () {
      assertAutoComplete({
        beforeCursor: '-- line comment\nSELECT * from testTable1;\n',
        afterCursor: '\n-- other line comment',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ALTER', 'CREATE', 'DELETE', 'DESCRIBE', 'DROP',
            'EXPLAIN', 'INSERT', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE',
            'UPDATE', 'USE']
        }
      });
    });

    it('should ignore multi-line comments for local suggestions', function () {
      assertAutoComplete({
        beforeCursor: '/* line 1\nline 2\n*/\nSELECT * from testTable1;\n',
        afterCursor: '',
        dialect: 'generic',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ALTER', 'CREATE', 'DELETE', 'DESCRIBE', 'DROP',
            'EXPLAIN', 'INSERT', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE',
            'UPDATE', 'USE']
        }
      });
    });

    describe('partial removal', function () {
      it('should identify part lengths', function () {
        var limitChars = [' ', '\n', '\t', '&', '~', '%', '!', '.', ',', '+', '-', '*', '/', '=', '<', '>', '(', ')', '[', ']', ';'];
        expect(sql.identifyPartials('', '')).toEqual({left: 0, right: 0});
        expect(sql.identifyPartials('foo', '')).toEqual({left: 3, right: 0});
        expect(sql.identifyPartials(' foo', '')).toEqual({left: 3, right: 0});
        expect(sql.identifyPartials('asdf 1234', '')).toEqual({left: 4, right: 0});
        expect(sql.identifyPartials('foo', 'bar')).toEqual({left: 3, right: 3});
        expect(sql.identifyPartials('foo ', '')).toEqual({left: 0, right: 0});
        expect(sql.identifyPartials('foo \'', '\'')).toEqual({left: 0, right: 0});
        expect(sql.identifyPartials('foo "', '"')).toEqual({left: 0, right: 0});
        limitChars.forEach(function (char) {
          expect(sql.identifyPartials('bar foo' + char, '')).toEqual({left: 0, right: 0});
          expect(sql.identifyPartials('bar foo' + char + 'foofoo', '')).toEqual({left: 6, right: 0});
          expect(sql.identifyPartials('bar foo' + char + 'foofoo ', '')).toEqual({left: 0, right: 0});
          expect(sql.identifyPartials('', char + 'foo bar')).toEqual({left: 0, right: 0});
          expect(sql.identifyPartials('', 'foofoo' + char)).toEqual({left: 0, right: 6});
          expect(sql.identifyPartials('', ' foofoo' + char)).toEqual({left: 0, right: 0});
        });
      });
    });

    describe('identifierChain expansion', function () {
      it('should expand 1', function () {
        var tablePrimaries = [{
          identifierChain: [{ name: 'testTable' }],
          lateralViews: [{
            columnAliases: [ 'testItem' ],
            tableAlias: 'explodedTable',
            udtf: {
              expression: { columnReference: [{ name: 'testArray' }] },
              function: 'explode'
            }
          }]
        }];

        var identifierChain = [{ name: 'explodedTable' }, { name: 'testItem' }];

        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
      });

      it('should expand 2', function () {
        var tablePrimaries = [{
          identifierChain: [{ name: 'testTable' }],
          lateralViews: [{
            columnAliases: [ 'testMapKey', 'testMapValue' ],
            tableAlias: 'explodedMap',
            udtf: {
              expression: { columnReference: [{ name: 'testMap' }] },
              function: 'explode'
            }
          }]
        }];

        var identifierChain = [{ name: 'explodedMap' }, { name: 'testMapValue' }];

        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
      });

      it('should expand 3', function () {
        var tablePrimaries = [{ identifierChain: [{ name: 'testTable' }] }];
        var identifierChain = [{ name: 'testMap', key: 'anyKey' }];
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'testMap', key: 'anyKey' }]);
      });

      it('should expand 4', function () {
        var tablePrimaries = [{
          identifierChain: [{ name: 'testTable' }],
          lateralViews: [{
            columnAliases: [ 'testItem' ],
            tableAlias: 'explodedTable',
            udtf: {
              function: 'explode',
              expression: { columnReference: [{ name: 'testArray' }] }
            }
          }]
        }];
        var identifierChain = [{ name: 'testItem' }];
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
      });

      it('should expand 5', function () {
        var tablePrimaries = [{
          identifierChain: [{ name: 'testTable' }],
          lateralViews: [{
            columnAliases: [ 'testItemB' ],
            tableAlias: 'explodedTableB',
            udtf: {
              function: 'explode',
              expression: { columnReference: [{ name: 'testArrayB' }] }
            }
          }, {
            columnAliases: [ 'testItemA' ],
            tableAlias: 'explodedTableA',
            udtf: {
              function: 'explode',
              expression: { columnReference: [{ name: 'testArrayA' }] }
            }
          }]
        }];
        var identifierChain = [{ name: 'testItemA' }];
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'testArrayA' }, { name: 'item' }]);
      });

      it('should expand 6', function () {
        var tablePrimaries = [{
          alias: 'tt2',
          identifierChain: [{ name: 'testTable2' }],
          lateralViews: [{
            columnAliases: [ 'testItemB' ],
            tableAlias: 'explodedTableB',
            udtf: {
              function: 'explode',
              expression: { columnReference: [{ name: 'tt2' }, { name: 'testArrayB' }] }
            }
          }, {
            columnAliases: [ 'testItemA' ],
            tableAlias: 'explodedTableA',
            udtf: {
              function: 'explode',
              expression: { columnReference: [{ name: 'tt2' }, { name: 'testArrayA' }] }
            }
          }]
        }];
        var identifierChain = [{ name: 'testItemB' }];
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'tt2' }, { name: 'testArrayB' }, { name: 'item' }]);
      });

      it('should expand 7', function () {
        var tablePrimaries = [{
          alias: 'tt',
          identifierChain: [{ name: 'testTable' }],
          lateralViews: [{
            columnAliases: [ 'ta1_exp' ],
            tableAlias: 'ta1',
            udtf: {
              expression: { columnReference: [{ name: 'tt' }, { name: 'testArray1' }] },
              function: 'explode'
            }
          }, {
            columnAliases: [ 'ta2_exp' ],
            tableAlias: 'ta2',
            udtf: {
              expression: { columnReference: [{ name: 'ta1_exp' },{ name: 'testArray2' }] },
              function: 'explode'
            }
          }]
        }];

        var identifierChain = [{ name: 'ta2_exp' }];

        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'tt' }, { name: 'testArray1' }, { name: 'item' }, { name: 'testArray2' }, { name: 'item' }]);
      });

      it('should expand 8', function () {
        var tablePrimaries = [{
          identifierChain: [{ name: 'testTable' }],
          lateralViews: [{
            columnAliases: [ 'testIndex', 'testValue' ],
            tableAlias: 'explodedTable',
            udtf: {
              expression: { columnReference: [{ name: 'testArray' }] },
              function: 'posexplode'
            }
          }]
        }];

        var identifierChain = [{ name: 'testValue' }];

        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
      });

      it('should expand 9', function () {
        var tablePrimaries = [{
          identifierChain: [{ name: 'testTable' }],
          lateralViews: [{
            columnAliases: [ 'testMapKey', 'testMapValue' ],
            tableAlias: 'explodedTable',
            udtf: {
              expression: { columnReference: [{ name: 'testMap' }] },
              function: 'explode'
            }
          }]
        }];

        var identifierChain = [{ name: 'testMapValue' }];

        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
      });

      it('should expand a simple map reference', function () {
        var tablePrimaries = [
          { alias: 't', identifierChain: [{ name: 'someDb' }, { name: 'someTable' }] },
          { alias: 'm', identifierChain: [{ name: 't' }, { name: 'someMap' }] }
        ];

        var identifierChain = [{ name: 'm', key: 'foo' }, { name: 'bar' }];

        var actual = sql.expandImpalaIdentifierChain(tablePrimaries, identifierChain);

        expect(actual).toEqual([{ name: 't' }, { name: 'someMap', key: 'foo' }, { name: 'bar' }]);
      });

      it('should expand without map reference', function () {
        var tablePrimaries = [
          { alias: 't1', identifierChain: [{ name: 'databaseTwo' }, { name: 'testTable1' }] },
          { alias: 't2', identifierChain: [{ name: 'testTable2' }] }
        ];

        var identifierChain = [{ name: 't1' }];

        var actual = sql.expandImpalaIdentifierChain(tablePrimaries, identifierChain);

        expect(actual).toEqual([{ name: 'databaseTwo' }, { name: 'testTable1' }]);
      });
    });
  });
});