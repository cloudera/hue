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

describe('genericAutocompleteParser.js', () => {
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
      expect(genericAutocompleteParser.identifyPartials('', '')).toEqual({ left: 0, right: 0 });
      expect(genericAutocompleteParser.identifyPartials('foo', '')).toEqual({ left: 3, right: 0 });
      expect(genericAutocompleteParser.identifyPartials(' foo', '')).toEqual({ left: 3, right: 0 });
      expect(genericAutocompleteParser.identifyPartials('asdf 1234', '')).toEqual({
        left: 4,
        right: 0
      });
      expect(genericAutocompleteParser.identifyPartials('foo', 'bar')).toEqual({
        left: 3,
        right: 3
      });
      expect(genericAutocompleteParser.identifyPartials('fo', 'o()')).toEqual({
        left: 2,
        right: 3
      });
      expect(genericAutocompleteParser.identifyPartials('fo', 'o(')).toEqual({ left: 2, right: 2 });
      expect(genericAutocompleteParser.identifyPartials('fo', 'o(bla bla)')).toEqual({
        left: 2,
        right: 10
      });
      expect(genericAutocompleteParser.identifyPartials('foo ', '')).toEqual({ left: 0, right: 0 });
      expect(genericAutocompleteParser.identifyPartials("foo '", "'")).toEqual({
        left: 0,
        right: 0
      });
      expect(genericAutocompleteParser.identifyPartials('foo "', '"')).toEqual({
        left: 0,
        right: 0
      });
      limitChars.forEach(char => {
        expect(genericAutocompleteParser.identifyPartials('bar foo' + char, '')).toEqual({
          left: 0,
          right: 0
        });
        expect(genericAutocompleteParser.identifyPartials('bar foo' + char + 'foofoo', '')).toEqual(
          {
            left: 6,
            right: 0
          }
        );
        expect(
          genericAutocompleteParser.identifyPartials('bar foo' + char + 'foofoo ', '')
        ).toEqual({
          left: 0,
          right: 0
        });
        expect(genericAutocompleteParser.identifyPartials('', char + 'foo bar')).toEqual({
          left: 0,
          right: 0
        });
        expect(genericAutocompleteParser.identifyPartials('', 'foofoo' + char)).toEqual({
          left: 0,
          right: 6
        });
        expect(genericAutocompleteParser.identifyPartials('', ' foofoo' + char)).toEqual({
          left: 0,
          right: 0
        });
      });
    });
  });
});
