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
  describe('sql.js', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = SqlTestUtils.assertAutocomplete;

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

      it('should suggest keywords for "| * FROM boo; SELECT LIMIT 10"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: ' * FROM boo; SELECT LIMIT 10',
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "bla| * FROM boo; SELECT LIMIT 10"', function() {
        assertAutoComplete({
          beforeCursor: 'bla',
          afterCursor: ' * FROM boo; SELECT LIMIT 10',
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

    describe('SET', function () {
      it('should handle "set hive.exec.compress.output=true;|"', function () {
        assertAutoComplete({
          beforeCursor: 'set hive.exec.compress.output=true;',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: true
          }
        });
      });

      it('should handle "set bla.bla="ble";|"', function () {
        assertAutoComplete({
          beforeCursor: 'set bla.bla="ble";',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: true
          }
        });
      });

      it('should handle "set bla.bla=\'ble\';|"', function () {
        assertAutoComplete({
          beforeCursor: 'set bla.bla=\'ble\';',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: true
          }
        });
      });

      it('should handle "set mem_limit=64g;|"', function () {
        assertAutoComplete({
          beforeCursor: 'set mem_limit=64g;',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: true
          }
        });
      });

      it('should handle "set DISABLE_UNSAFE_SPILLS=true;|"', function () {
        assertAutoComplete({
          beforeCursor: 'set DISABLE_UNSAFE_SPILLS=true;',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: true
          }
        });
      });

      it('should handle "set RESERVATION_REQUEST_TIMEOUT=900000;|"', function () {
        assertAutoComplete({
          beforeCursor: 'set RESERVATION_REQUEST_TIMEOUT=900000;',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: true
          }
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
            suggestKeywords: ['ALTER', 'COMPUTE', 'CREATE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'GRANT', 'INSERT', 'INVALIDATE METADATA', 'LOAD', 'REFRESH',
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
            suggestKeywords: ['ALTER', 'ANALYZE TABLE', 'CREATE', 'DELETE', 'DESCRIBE',
              'DROP', 'EXPLAIN', 'EXPORT', 'FROM', 'GRANT', 'IMPORT', 'INSERT', 'LOAD', 'MSCK',
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
          locations: [
            { type: 'statement', location: { first_line: 1, last_line: 2, first_column: 1, last_column: 25 } },
            { type: 'asterisk', location: { first_line: 2, last_line: 2, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
            { type: 'table', location: { first_line:2, last_line:2, first_column:15, last_column:25 }, identifierChain: [{ name: 'testTable1' }] }
          ],
          lowerCase: false
        }
      });
    });

    it('should ignore multi-line comments for local suggestions', function () {
      assertAutoComplete({
        beforeCursor: '/* line 1\nline 2\n*/\nSELECT * from testTable1;\n',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          locations: [
            { type: 'statement', location: { first_line: 1, last_line: 4, first_column: 1, last_column: 25 } },
            { type: 'asterisk', location: { first_line: 4, last_line: 4, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'testTable1' }] }] },
            { type: 'table', location: { first_line:4, last_line:4, first_column:15, last_column:25 }, identifierChain: [{ name: 'testTable1' }] }
          ],
          lowerCase: false
        }
      });
    });

    describe('partial removal', function () {
      it('should identify part lengths', function () {
        var limitChars = [' ', '\n', '\t', '&', '~', '%', '!', '.', ',', '+', '-', '*', '/', '=', '<', '>', ')', '[', ']', ';'];
        expect(sql.identifyPartials('', '')).toEqual({left: 0, right: 0});
        expect(sql.identifyPartials('foo', '')).toEqual({left: 3, right: 0});
        expect(sql.identifyPartials(' foo', '')).toEqual({left: 3, right: 0});
        expect(sql.identifyPartials('asdf 1234', '')).toEqual({left: 4, right: 0});
        expect(sql.identifyPartials('foo', 'bar')).toEqual({left: 3, right: 3});
        expect(sql.identifyPartials('fo', 'o()')).toEqual({left: 2, right: 3});
        expect(sql.identifyPartials('fo', 'o(')).toEqual({left: 2, right: 2});
        expect(sql.identifyPartials('fo', 'o(bla bla)')).toEqual({left: 2, right: 10});
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
      it('should expand 01', function () {
        var lateralViews = [{
          columnAliases: [ 'testItem' ],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testArray' }] },
            function: 'explode'
          }
        }];

        var identifierChain = [{ name: 'testItem' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
      });

      it('should expand 02', function () {
        var lateralViews = [{
          columnAliases: [ 'testMapKey', 'testMapValue' ],
          tableAlias: 'explodedMap',
          udtf: {
            expression: { columnReference: [{ name: 'testMap' }] },
            function: 'explode'
          }
        }];

        var identifierChain = [{ name: 'explodedMap' }, { name: 'testMapValue' }];

        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
      });

      it('should expand 03', function () {
        var identifierChain = [{ name: 'testMap', keySet: true }];
        var result = sql.expandLateralViews([], identifierChain);
        expect(result).toEqual([{ name: 'testMap', keySet: true }]);
      });

      it('should expand 04', function () {
        var lateralViews = [{
          columnAliases: [ 'testItem' ],
          tableAlias: 'explodedTable',
          udtf: {
            function: 'explode',
            expression: { columnReference: [{ name: 'testArray' }] }
          }
        }];

        var identifierChain = [{ name: 'testItem' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
      });

      it('should expand 05', function () {
        var lateralViews = [{
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
        }];

        var identifierChain = [{ name: 'testItemA' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'testArrayA' }, { name: 'item' }]);
      });

      it('should expand 06', function () {
        var lateralViews = [{
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
        }];
        var identifierChain = [{ name: 'testItemB' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'tt2' }, { name: 'testArrayB' }, { name: 'item' }]);
      });

      it('should expand 07', function () {
        var lateralViews = [{
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
        }];

        var identifierChain = [{ name: 'ta2_exp' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'tt' }, { name: 'testArray1' }, { name: 'item' }, { name: 'testArray2' }, { name: 'item' }]);
      });

      it('should expand 08', function () {
        var lateralViews = [{
          columnAliases: [ 'testIndex', 'testValue' ],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testArray' }] },
            function: 'posexplode'
          }
        }];

        var identifierChain = [{ name: 'testValue' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
      });

      it('should expand 09', function () {
        var lateralViews = [{
          columnAliases: [ 'testMapKey', 'testMapValue' ],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testMap' }] },
            function: 'explode'
          }
        }];

        var identifierChain = [{ name: 'testMapValue' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
        expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
      });


      it('should expand 10', function () {
        var lateralViews = [{
          columnAliases: [ 'testItem' ],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testArray' }] },
            function: 'explode'
          }
        }];

        var identifierChain = [{ name: 'testItem' }];
        var result = sql.expandLateralViews(lateralViews, identifierChain);
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
})();