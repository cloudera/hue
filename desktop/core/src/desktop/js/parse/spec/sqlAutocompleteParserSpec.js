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

describe('sqlAutocompleteParser.js', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  it('should suggest keywords for ";;|"', () => {
    assertAutoComplete({
      beforeCursor: ';;',
      afterCursor: '',
      containsKeywords: ['SELECT', 'WITH'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for ";|;"', () => {
    assertAutoComplete({
      beforeCursor: ';',
      afterCursor: ';',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "|;;;;', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: ';;;;',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "foo|bar"', () => {
    assertAutoComplete({
      beforeCursor: 'foo',
      afterCursor: 'bar',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  describe('Error Handling', () => {
    it('should suggest keywords for "bla; |"', () => {
      assertAutoComplete({
        beforeCursor: 'bla; ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "bla bla bla;bla; |"', () => {
      assertAutoComplete({
        beforeCursor: 'bla bla bla;bla; ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "Åäö; |"', () => {
      assertAutoComplete({
        beforeCursor: 'Åäö; ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "bla bla bla;bla;\\n|;bladiblaa blaa"', () => {
      assertAutoComplete({
        beforeCursor: 'bla bla bla;bla;\n',
        afterCursor: ';bladiblaa blaa',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "FROM; |"', () => {
      assertAutoComplete({
        beforeCursor: 'FROM; ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INTO USE; |"', () => {
      assertAutoComplete({
        beforeCursor: 'INTO USE; ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INTO SELECT; OR FROM FROM; |"', () => {
      assertAutoComplete({
        beforeCursor: 'INTO SELECT; OR FROM FROM;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INTO SELECT; OR FROM FROM; |;BLAAA; AND;"', () => {
      assertAutoComplete({
        beforeCursor: 'INTO SELECT; OR FROM FROM;',
        afterCursor: ';BLAAA; AND;',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "INTO bla bla;AND booo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'INTO bla bla;AND booo;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "|; SELECT LIMIT 10"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '; SELECT LIMIT 10',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "| * FROM boo; SELECT LIMIT 10"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: ' * FROM boo; SELECT LIMIT 10',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "bla| * FROM boo; SELECT LIMIT 10"', () => {
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

  describe('EXPLAIN', () => {
    describe('Hive specific', () => {
      it('should handle "EXPLAIN DEPENDENCY SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;|"', () => {
        assertAutoComplete({
          beforeCursor:
            'EXPLAIN DEPENDENCY SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;',
          afterCursor: '',
          dialect: 'hive',
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
          dialect: 'hive',
          containsKeywords: ['EXPLAIN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "EXPLAIN |"', () => {
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

      it('should suggest keywords for "EXPLAIN AUTHORIZATION |"', () => {
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

      it('should suggest tables for "EXPLAIN EXTENDED SELECT * FROM |"', () => {
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

    describe('Impala specific', () => {
      it('should handle "EXPLAIN SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;|"', () => {
        assertAutoComplete({
          beforeCursor:
            'EXPLAIN SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;',
          afterCursor: '',
          dialect: 'impala',
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
          dialect: 'impala',
          containsKeywords: ['EXPLAIN'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "EXPLAIN |"', () => {
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

      it('should suggest tables for "EXPLAIN SELECT * FROM |"', () => {
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

  describe('SET', () => {
    it('should handle "set hive.exec.compress.output=true;|"', () => {
      assertAutoComplete({
        beforeCursor: 'set hive.exec.compress.output=true;',
        afterCursor: '',
        dialect: 'hive',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it('should handle "set bla.bla="ble";|"', () => {
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

    it('should handle "set bla.bla=\'ble\';|"', () => {
      assertAutoComplete({
        beforeCursor: "set bla.bla='ble';",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it('should handle "set mem_limit=64g;|"', () => {
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

    it('should handle "set DISABLE_UNSAFE_SPILLS=true;|"', () => {
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

    it('should handle "set RESERVATION_REQUEST_TIMEOUT=900000;|"', () => {
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

  describe('Impala specific', () => {
    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ALTER',
            'COMMENT ON',
            'COMPUTE',
            'CREATE',
            'DELETE',
            'DESCRIBE',
            'DROP',
            'EXPLAIN',
            'GRANT',
            'INSERT',
            'INVALIDATE METADATA',
            'LOAD',
            'REFRESH',
            'REVOKE',
            'SELECT',
            'SET',
            'SHOW',
            'TRUNCATE',
            'UPDATE',
            'UPSERT',
            'USE',
            'WITH'
          ]
        }
      });
    });
  });

  describe('Hive specific', () => {
    it('should suggest keywords for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ABORT',
            'ALTER',
            'ANALYZE TABLE',
            'CREATE',
            'DELETE',
            'DESCRIBE',
            'DROP',
            'EXPLAIN',
            'EXPORT',
            'FROM',
            'GRANT',
            'IMPORT',
            'INSERT',
            'LOAD',
            'MERGE',
            'MSCK',
            'RELOAD FUNCTION',
            'RESET',
            'REVOKE',
            'SELECT',
            'SET',
            'SHOW',
            'TRUNCATE',
            'UPDATE',
            'USE',
            'WITH'
          ]
        }
      });
    });
  });

  it('should ignore line comments for local suggestions', () => {
    assertAutoComplete({
      beforeCursor: '-- line comment\nSELECT * from testTable1;\n',
      afterCursor: '\n-- other line comment',
      dialect: 'impala',
      containsKeywords: ['SELECT'],
      expectedResult: {
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 2, first_column: 1, last_column: 25 }
          },
          {
            type: 'statementType',
            location: { first_line: 2, last_line: 2, first_column: 1, last_column: 7 },
            identifier: 'SELECT'
          },
          {
            type: 'selectList',
            missing: false,
            location: { first_line: 2, last_line: 2, first_column: 8, last_column: 9 }
          },
          {
            type: 'asterisk',
            location: { first_line: 2, last_line: 2, first_column: 8, last_column: 9 },
            tables: [{ identifierChain: [{ name: 'testTable1' }] }]
          },
          {
            type: 'table',
            location: { first_line: 2, last_line: 2, first_column: 15, last_column: 25 },
            identifierChain: [{ name: 'testTable1' }]
          },
          {
            type: 'whereClause',
            missing: true,
            location: { first_line: 2, last_line: 2, first_column: 25, last_column: 25 }
          },
          {
            type: 'limitClause',
            missing: true,
            location: { first_line: 2, last_line: 2, first_column: 25, last_column: 25 }
          }
        ],
        lowerCase: false
      }
    });
  });

  it('should ignore multi-line comments for local suggestions', () => {
    assertAutoComplete({
      beforeCursor: '/* line 1\nline 2\n*/\nSELECT * from testTable1;\n',
      afterCursor: '',
      dialect: 'hive',
      containsKeywords: ['SELECT'],
      expectedResult: {
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 4, first_column: 1, last_column: 25 }
          },
          {
            type: 'selectList',
            missing: false,
            location: { first_line: 4, last_line: 4, first_column: 8, last_column: 9 }
          },
          {
            type: 'asterisk',
            location: { first_line: 4, last_line: 4, first_column: 8, last_column: 9 },
            tables: [{ identifierChain: [{ name: 'testTable1' }] }]
          },
          {
            type: 'table',
            location: { first_line: 4, last_line: 4, first_column: 15, last_column: 25 },
            identifierChain: [{ name: 'testTable1' }]
          },
          {
            type: 'whereClause',
            missing: true,
            location: { first_line: 4, last_line: 4, first_column: 25, last_column: 25 }
          },
          {
            type: 'limitClause',
            missing: true,
            location: { first_line: 4, last_line: 4, first_column: 25, last_column: 25 }
          }
        ],
        lowerCase: false
      }
    });
  });

  describe('partial removal', () => {
    it('should identify part lengths', () => {
      const limitChars = [
        ' ',
        '\n',
        '\t',
        '&',
        '~',
        '%',
        '!',
        '.',
        ',',
        '+',
        '-',
        '*',
        '/',
        '=',
        '<',
        '>',
        ')',
        '[',
        ']',
        ';'
      ];
      expect(sqlAutocompleteParser.identifyPartials('', '')).toEqual({ left: 0, right: 0 });
      expect(sqlAutocompleteParser.identifyPartials('foo', '')).toEqual({ left: 3, right: 0 });
      expect(sqlAutocompleteParser.identifyPartials(' foo', '')).toEqual({ left: 3, right: 0 });
      expect(sqlAutocompleteParser.identifyPartials('asdf 1234', '')).toEqual({
        left: 4,
        right: 0
      });
      expect(sqlAutocompleteParser.identifyPartials('foo', 'bar')).toEqual({ left: 3, right: 3 });
      expect(sqlAutocompleteParser.identifyPartials('fo', 'o()')).toEqual({ left: 2, right: 3 });
      expect(sqlAutocompleteParser.identifyPartials('fo', 'o(')).toEqual({ left: 2, right: 2 });
      expect(sqlAutocompleteParser.identifyPartials('fo', 'o(bla bla)')).toEqual({
        left: 2,
        right: 10
      });
      expect(sqlAutocompleteParser.identifyPartials('foo ', '')).toEqual({ left: 0, right: 0 });
      expect(sqlAutocompleteParser.identifyPartials("foo '", "'")).toEqual({ left: 0, right: 0 });
      expect(sqlAutocompleteParser.identifyPartials('foo "', '"')).toEqual({ left: 0, right: 0 });
      limitChars.forEach(char => {
        expect(sqlAutocompleteParser.identifyPartials('bar foo' + char, '')).toEqual({
          left: 0,
          right: 0
        });
        expect(sqlAutocompleteParser.identifyPartials('bar foo' + char + 'foofoo', '')).toEqual({
          left: 6,
          right: 0
        });
        expect(sqlAutocompleteParser.identifyPartials('bar foo' + char + 'foofoo ', '')).toEqual({
          left: 0,
          right: 0
        });
        expect(sqlAutocompleteParser.identifyPartials('', char + 'foo bar')).toEqual({
          left: 0,
          right: 0
        });
        expect(sqlAutocompleteParser.identifyPartials('', 'foofoo' + char)).toEqual({
          left: 0,
          right: 6
        });
        expect(sqlAutocompleteParser.identifyPartials('', ' foofoo' + char)).toEqual({
          left: 0,
          right: 0
        });
      });
    });
  });

  describe('identifierChain expansion', () => {
    it('should expand 01', () => {
      const lateralViews = [
        {
          columnAliases: ['testItem'],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testArray' }] },
            function: 'explode'
          }
        }
      ];

      const identifierChain = [{ name: 'testItem' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
    });

    it('should expand 02', () => {
      const lateralViews = [
        {
          columnAliases: ['testMapKey', 'testMapValue'],
          tableAlias: 'explodedMap',
          udtf: {
            expression: { columnReference: [{ name: 'testMap' }] },
            function: 'explode'
          }
        }
      ];

      const identifierChain = [{ name: 'explodedMap' }, { name: 'testMapValue' }];

      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
    });

    it('should expand 03', () => {
      const identifierChain = [{ name: 'testMap', keySet: true }];
      const result = sqlAutocompleteParser.expandLateralViews([], identifierChain);
      expect(result).toEqual([{ name: 'testMap', keySet: true }]);
    });

    it('should expand 04', () => {
      const lateralViews = [
        {
          columnAliases: ['testItem'],
          tableAlias: 'explodedTable',
          udtf: {
            function: 'explode',
            expression: { columnReference: [{ name: 'testArray' }] }
          }
        }
      ];

      const identifierChain = [{ name: 'testItem' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
    });

    it('should expand 05', () => {
      const lateralViews = [
        {
          columnAliases: ['testItemB'],
          tableAlias: 'explodedTableB',
          udtf: {
            function: 'explode',
            expression: { columnReference: [{ name: 'testArrayB' }] }
          }
        },
        {
          columnAliases: ['testItemA'],
          tableAlias: 'explodedTableA',
          udtf: {
            function: 'explode',
            expression: { columnReference: [{ name: 'testArrayA' }] }
          }
        }
      ];

      const identifierChain = [{ name: 'testItemA' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'testArrayA' }, { name: 'item' }]);
    });

    it('should expand 06', () => {
      const lateralViews = [
        {
          columnAliases: ['testItemB'],
          tableAlias: 'explodedTableB',
          udtf: {
            function: 'explode',
            expression: { columnReference: [{ name: 'tt2' }, { name: 'testArrayB' }] }
          }
        },
        {
          columnAliases: ['testItemA'],
          tableAlias: 'explodedTableA',
          udtf: {
            function: 'explode',
            expression: { columnReference: [{ name: 'tt2' }, { name: 'testArrayA' }] }
          }
        }
      ];
      const identifierChain = [{ name: 'testItemB' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'tt2' }, { name: 'testArrayB' }, { name: 'item' }]);
    });

    it('should expand 07', () => {
      const lateralViews = [
        {
          columnAliases: ['ta1_exp'],
          tableAlias: 'ta1',
          udtf: {
            expression: { columnReference: [{ name: 'tt' }, { name: 'testArray1' }] },
            function: 'explode'
          }
        },
        {
          columnAliases: ['ta2_exp'],
          tableAlias: 'ta2',
          udtf: {
            expression: { columnReference: [{ name: 'ta1_exp' }, { name: 'testArray2' }] },
            function: 'explode'
          }
        }
      ];

      const identifierChain = [{ name: 'ta2_exp' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([
        { name: 'tt' },
        { name: 'testArray1' },
        { name: 'item' },
        { name: 'testArray2' },
        { name: 'item' }
      ]);
    });

    it('should expand 08', () => {
      const lateralViews = [
        {
          columnAliases: ['testIndex', 'testValue'],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testArray' }] },
            function: 'posexplode'
          }
        }
      ];

      const identifierChain = [{ name: 'testValue' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
    });

    it('should expand 09', () => {
      const lateralViews = [
        {
          columnAliases: ['testMapKey', 'testMapValue'],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testMap' }] },
            function: 'explode'
          }
        }
      ];

      const identifierChain = [{ name: 'testMapValue' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
    });

    it('should expand 10', () => {
      const lateralViews = [
        {
          columnAliases: ['testItem'],
          tableAlias: 'explodedTable',
          udtf: {
            expression: { columnReference: [{ name: 'testArray' }] },
            function: 'explode'
          }
        }
      ];

      const identifierChain = [{ name: 'testItem' }];
      const result = sqlAutocompleteParser.expandLateralViews(lateralViews, identifierChain);
      expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
    });

    it('should expand a simple map reference', () => {
      const tablePrimaries = [
        { alias: 't', identifierChain: [{ name: 'someDb' }, { name: 'someTable' }] },
        { alias: 'm', identifierChain: [{ name: 't' }, { name: 'someMap' }] }
      ];

      const identifierChain = [{ name: 'm', keySet: true }, { name: 'bar' }];

      const actual = sqlAutocompleteParser.expandImpalaIdentifierChain(
        tablePrimaries,
        identifierChain
      );

      expect(actual).toEqual([{ name: 't' }, { name: 'someMap', keySet: true }, { name: 'bar' }]);
    });

    it('should expand a simple map reference 2', () => {
      const tablePrimaries = [
        { alias: 't', identifierChain: [{ name: 'testTable' }] },
        { alias: 'tm', identifierChain: [{ name: 't' }, { name: 'testMap' }] }
      ];

      const identifierChain = [{ name: 'tm' }];

      const actual = sqlAutocompleteParser.expandImpalaIdentifierChain(
        tablePrimaries,
        identifierChain
      );

      expect(actual).toEqual([{ name: 't' }, { name: 'testMap' }]);
    });

    it('should expand a simple map reference without alias', () => {
      const tablePrimaries = [
        { alias: 't', identifierChain: [{ name: 'testTable' }] },
        { identifierChain: [{ name: 't' }, { name: 'testMap' }] }
      ];

      const identifierChain = [{ name: 'testMap' }];

      const actual = sqlAutocompleteParser.expandImpalaIdentifierChain(
        tablePrimaries,
        identifierChain
      );

      expect(actual).toEqual([{ name: 't' }, { name: 'testMap' }]);
    });

    it('should not expand without map reference', () => {
      const tablePrimaries = [
        { alias: 't1', identifierChain: [{ name: 'databaseTwo' }, { name: 'testTable1' }] },
        { alias: 't2', identifierChain: [{ name: 'testTable2' }] }
      ];

      const identifierChain = [{ name: 't1' }];

      const actual = sqlAutocompleteParser.expandImpalaIdentifierChain(
        tablePrimaries,
        identifierChain
      );

      expect(actual).toEqual([{ name: 't1' }]);
    });
  });
});
