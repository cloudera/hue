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
  'desktop/spec/autocomplete/sqlSpecAlter',
  'desktop/spec/autocomplete/sqlSpecAnalyze',
  'desktop/spec/autocomplete/sqlSpecCreate',
  'desktop/spec/autocomplete/sqlSpecDescribe',
  'desktop/spec/autocomplete/sqlSpecDrop',
  'desktop/spec/autocomplete/sqlSpecError',
  'desktop/spec/autocomplete/sqlSpecInsert',
  'desktop/spec/autocomplete/sqlSpecLoad',
  'desktop/spec/autocomplete/sqlSpecSelect',
  'desktop/spec/autocomplete/sqlSpecSet',
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

    it('should suggest keywords for ";;|"', function() {
      assertAutoComplete({
        beforeCursor: ';;',
        afterCursor: '',
        containsKeywords: ['SELECT', 'WITH'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for ";|;"', function() {
      assertAutoComplete({
        beforeCursor: ';',
        afterCursor: ';',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "|;;;;', function() {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: ';;;;',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "foo|bar"', function() {
      assertAutoComplete({
        beforeCursor: 'foo',
        afterCursor: 'bar',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    describe('Error Handling', function () {
      it('should suggest keywords for "bla; |"', function() {
        assertAutoComplete({
          beforeCursor: 'bla; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "bla bla bla;bla; |"', function() {
        assertAutoComplete({
          beforeCursor: 'bla bla bla;bla; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "Åäö; |"', function() {
        assertAutoComplete({
          beforeCursor: 'Åäö; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "bla bla bla;bla;\\n|;bladiblaa blaa"', function() {
        assertAutoComplete({
          beforeCursor: 'bla bla bla;bla;\n',
          afterCursor: ';bladiblaa blaa',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "FROM; |"', function() {
        assertAutoComplete({
          beforeCursor: 'FROM; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "INTO USE; |"', function() {
        assertAutoComplete({
          beforeCursor: 'INTO USE; ',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "INTO SELECT; OR FROM FROM; |"', function() {
        assertAutoComplete({
          beforeCursor: 'INTO SELECT; OR FROM FROM;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "INTO SELECT; OR FROM FROM; |;BLAAA; AND;"', function() {
        assertAutoComplete({
          beforeCursor: 'INTO SELECT; OR FROM FROM;',
          afterCursor: ';BLAAA; AND;',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
      
      it('should suggest keywords for "INTO bla bla;AND booo; |"', function() {
        assertAutoComplete({
          beforeCursor: 'INTO bla bla;AND booo;',
          afterCursor: '',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "|; SELECT LIMIT 10"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '; SELECT LIMIT 10',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

    describe('EXPLAIN', function () {
      describe('Hive specific', function () {
        it('should handle "EXPLAIN DEPENDENCY SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;|"', function() {
          assertAutoComplete({
            beforeCursor: 'EXPLAIN DEPENDENCY SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;',
            afterCursor: '',
            dialect: 'hive',
            hasLocations: true,
            noErrors: true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "|"', function() {
          assertAutoComplete({
            beforeCursor: '',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['EXPLAIN'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "EXPLAIN |"', function() {
          assertAutoComplete({
            beforeCursor: 'EXPLAIN ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['AUTHORIZATION', 'DEPENDENCY', 'EXTENDED', 'SELECT'],
            doesNotContainKeywords: ['EXPLAIN'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "EXPLAIN AUTHORIZATION |"', function() {
          assertAutoComplete({
            beforeCursor: 'EXPLAIN AUTHORIZATION ',
            afterCursor: '',
            dialect: 'hive',
            containsKeywords: ['SELECT'],
            doesNotContainKeywords: ['AUTHORIZATION', 'DEPENDENCY', 'EXTENDED', 'EXPLAIN'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest tables for "EXPLAIN EXTENDED SELECT * FROM |"', function() {
          assertAutoComplete({
            beforeCursor: 'EXPLAIN EXTENDED SELECT * FROM ',
            afterCursor: '',
            dialect: 'hive',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });
      });

      describe('Impala specific', function () {
        it('should handle "EXPLAIN SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;|"', function() {
          assertAutoComplete({
            beforeCursor: 'EXPLAIN SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;',
            afterCursor: '',
            dialect: 'impala',
            hasLocations: true,
            noErrors: true,
            containsKeywords: ['SELECT'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "|"', function() {
          assertAutoComplete({
            beforeCursor: '',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['EXPLAIN'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest keywords for "EXPLAIN |"', function() {
          assertAutoComplete({
            beforeCursor: 'EXPLAIN ',
            afterCursor: '',
            dialect: 'impala',
            containsKeywords: ['SELECT'],
            doesNotContainKeywords: ['AUTHORIZATION', 'DEPENDENCY', 'EXTENDED', 'EXPLAIN'],
            expectedResult: {
              lowerCase: false
            }
          });
        });

        it('should suggest tables for "EXPLAIN SELECT * FROM |"', function() {
          assertAutoComplete({
            beforeCursor: 'EXPLAIN SELECT * FROM ',
            afterCursor: '',
            dialect: 'impala',
            expectedResult: {
              lowerCase: false,
              suggestTables: {},
              suggestDatabases: { appendDot: true }
            }
          });
        });
      });
    });

    describe('Impala specific', function () {
      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ALTER', 'COMPUTE', 'CREATE', 'DELETE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'INSERT', 'INVALIDATE', 'LOAD', 'REFRESH',
              'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE', 'WITH']
          }
        });
      });
    });

    describe('Hive specific', function () {
      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'hive',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['ALTER', 'ANALYZE', 'CREATE', 'DELETE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'EXPORT', 'FROM', 'IMPORT', 'INSERT', 'LOAD', 'MSCK',
              'RELOAD FUNCTION', 'RESET', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE', 'WITH']
          }
        });
      });
    });

    it('should ignore line comments for local suggestions', function () {
      assertAutoComplete({
        beforeCursor: '-- line comment\nSELECT * from testTable1;\n',
        afterCursor: '\n-- other line comment',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false,
          locations: [{ type: 'table', location: { first_line:2, last_line:2, first_column:15, last_column:25 }, table: 'testTable1' }]
        }
      });
    });

    it('should ignore multi-line comments for local suggestions', function () {
      assertAutoComplete({
        beforeCursor: '/* line 1\nline 2\n*/\nSELECT * from testTable1;\n',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false,
          locations: [{ type: 'table', location: { first_line:4, last_line:4, first_column:15, last_column:25 }, table: 'testTable1' }]
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

        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
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

        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
        expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
      });

      it('should expand 3', function () {
        var tablePrimaries = [{ identifierChain: [{ name: 'testTable' }] }];
        var identifierChain = [{ name: 'testMap', keySet: true }];
        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
        expect(result).toEqual([{ name: 'testMap', keySet: true }]);
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
        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
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
        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
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
        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
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

        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
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

        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
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

        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
        expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
      });


      it('should expand 10', function () {
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

        var identifierChain = [{ name: 'testItem' }];

        var tablePrimariesBefore = tablePrimaries.concat();
        var result = sql.expandLateralViews(tablePrimaries, identifierChain);
        expect(tablePrimariesBefore).toEqual(tablePrimaries);
        expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
      });

      it('should expand a simple map reference', function () {
        var tablePrimaries = [
          { alias: 't', identifierChain: [{ name: 'someDb' }, { name: 'someTable' }] },
          { alias: 'm', identifierChain: [{ name: 't' }, { name: 'someMap' }] }
        ];

        var identifierChain = [{ name: 'm', keySet: true }, { name: 'bar' }];

        var actual = sql.expandImpalaIdentifierChain(tablePrimaries, identifierChain);

        expect(actual).toEqual([{ name: 't' }, { name: 'someMap', keySet: true }, { name: 'bar' }]);
      });

      it('should expand a simple map reference 2', function () {
        var tablePrimaries = [
          { alias: 't', identifierChain: [{ name: 'testTable' }] },
          { alias: 'tm', identifierChain: [{ name: 't' }, { name: 'testMap' }] }
        ];

        var identifierChain = [{ name: 'tm' }];

        var actual = sql.expandImpalaIdentifierChain(tablePrimaries, identifierChain);

        expect(actual).toEqual([{ name: 't' }, { name: 'testMap' }]);
      });

      it('should not expand without map reference', function () {
        var tablePrimaries = [
          { alias: 't1', identifierChain: [{ name: 'databaseTwo' }, { name: 'testTable1' }] },
          { alias: 't2', identifierChain: [{ name: 'testTable2' }] }
        ];

        var identifierChain = [{ name: 't1' }];

        var actual = sql.expandImpalaIdentifierChain(tablePrimaries, identifierChain);

        expect(actual).toEqual([{ name: 't1' }]);
      });
    });
  });
});