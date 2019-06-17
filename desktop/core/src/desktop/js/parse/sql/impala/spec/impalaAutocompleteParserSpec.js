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

import impalaAutocompleteParser from '../impalaAutocompleteParser';
import SqlTestUtils from '../../../spec/sqlTestUtils';

describe('impalaAutocompleteParser.js', () => {
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
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

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
    it('should handle "EXPLAIN SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;|"', () => {
      assertAutoComplete({
        beforeCursor:
          'EXPLAIN SELECT key, count(1) FROM srcpart WHERE ds IS NOT NULL GROUP BY key;',
        afterCursor: '',
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
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });
  });

  describe('SET', () => {

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

  it('should suggest keywords for "|"', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: '',
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

  it('should ignore line comments for local suggestions', () => {
    assertAutoComplete({
      beforeCursor: '-- line comment\nSELECT * from testTable1;\n',
      afterCursor: '\n-- other line comment',
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
      expect(impalaAutocompleteParser.identifyPartials('', '')).toEqual({ left: 0, right: 0 });
      expect(impalaAutocompleteParser.identifyPartials('foo', '')).toEqual({ left: 3, right: 0 });
      expect(impalaAutocompleteParser.identifyPartials(' foo', '')).toEqual({ left: 3, right: 0 });
      expect(impalaAutocompleteParser.identifyPartials('asdf 1234', '')).toEqual({
        left: 4,
        right: 0
      });
      expect(impalaAutocompleteParser.identifyPartials('foo', 'bar')).toEqual({ left: 3, right: 3 });
      expect(impalaAutocompleteParser.identifyPartials('fo', 'o()')).toEqual({ left: 2, right: 3 });
      expect(impalaAutocompleteParser.identifyPartials('fo', 'o(')).toEqual({ left: 2, right: 2 });
      expect(impalaAutocompleteParser.identifyPartials('fo', 'o(bla bla)')).toEqual({
        left: 2,
        right: 10
      });
      expect(impalaAutocompleteParser.identifyPartials('foo ', '')).toEqual({ left: 0, right: 0 });
      expect(impalaAutocompleteParser.identifyPartials("foo '", "'")).toEqual({ left: 0, right: 0 });
      expect(impalaAutocompleteParser.identifyPartials('foo "', '"')).toEqual({ left: 0, right: 0 });
      limitChars.forEach(char => {
        expect(impalaAutocompleteParser.identifyPartials('bar foo' + char, '')).toEqual({
          left: 0,
          right: 0
        });
        expect(impalaAutocompleteParser.identifyPartials('bar foo' + char + 'foofoo', '')).toEqual({
          left: 6,
          right: 0
        });
        expect(impalaAutocompleteParser.identifyPartials('bar foo' + char + 'foofoo ', '')).toEqual({
          left: 0,
          right: 0
        });
        expect(impalaAutocompleteParser.identifyPartials('', char + 'foo bar')).toEqual({
          left: 0,
          right: 0
        });
        expect(impalaAutocompleteParser.identifyPartials('', 'foofoo' + char)).toEqual({
          left: 0,
          right: 6
        });
        expect(impalaAutocompleteParser.identifyPartials('', ' foofoo' + char)).toEqual({
          left: 0,
          right: 0
        });
      });
    });
  });
});
