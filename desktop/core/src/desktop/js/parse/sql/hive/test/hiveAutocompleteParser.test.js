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

import { assertPartials } from 'parse/sql/sharedParserTests';
import hiveAutocompleteParser from '../hiveAutocompleteParser';
import { extractTestCases, runTestCases } from '../../testUtils';
import structure from '../../hive/jison/structure.json';

const jisonFolder = 'desktop/core/src/desktop/js/parse/sql/hive/jison';
const groupedTestCases = extractTestCases(jisonFolder, structure.autocomplete);

describe('hiveAutocompleteParser.js', () => {
  runTestCases(hiveAutocompleteParser, groupedTestCases);

  beforeAll(() => {
    hiveAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
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
    it('should handle "set hive.exec.compress.output=true;|"', () => {
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

  it('should ignore multi-line comments for local suggestions', () => {
    assertAutoComplete({
      beforeCursor: '/* line 1\nline 2\n*/\nSELECT * from testTable1;\n',
      afterCursor: '',
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
      assertPartials(hiveAutocompleteParser);
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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

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

      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

      expect(result).toEqual([{ name: 'testMap' }, { name: 'value' }]);
    });

    it('should expand 03', () => {
      const identifierChain = [{ name: 'testMap', keySet: true }];
      const result = hiveAutocompleteParser.expandLateralViews([], identifierChain);

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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

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
      const result = hiveAutocompleteParser.expandLateralViews(lateralViews, identifierChain);

      expect(result).toEqual([{ name: 'testArray' }, { name: 'item' }]);
    });
  });
});
