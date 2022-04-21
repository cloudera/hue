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

import hiveAutocompleteParser from '../hiveAutocompleteParser';
describe('hiveAutocompleteParser.js SELECT statements', () => {
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

  it('should suggest keywords for "|"', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: '',
      containsKeywords: ['SELECT'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest tables and databases for "SELECT * |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * ',
      afterCursor: '',
      containsKeywords: ['FROM'],
      expectedResult: {
        lowerCase: false,
        suggestTables: {
          prependFrom: true
        },
        suggestDatabases: {
          prependFrom: true,
          appendDot: true
        }
      }
    });
  });

  it('should suggest tables and databases for "SELECT *\\r\\n |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT *\r\n',
      afterCursor: '',
      containsKeywords: ['FROM'],
      expectedResult: {
        lowerCase: false,
        suggestTables: {
          prependFrom: true
        },
        suggestDatabases: {
          prependFrom: true,
          appendDot: true
        }
      }
    });
  });

  it('should not suggest anything for "SELECT u.|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT u.',
      afterCursor: '',
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "SELECT foo, bar |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT foo, bar ',
      afterCursor: '',
      containsKeywords: ['AS', '+', 'FROM', 'DIV'],
      expectedResult: {
        lowerCase: false,
        suggestTables: {
          prependFrom: true
        },
        suggestDatabases: {
          prependFrom: true,
          appendDot: true
        }
      }
    });
  });

  it('should suggest keywords for "SELECT foo AS a, bar |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT foo AS a, bar ',
      afterCursor: '',
      containsKeywords: ['AS', '+'],
      expectedResult: {
        lowerCase: false,
        suggestTables: {
          prependFrom: true
        },
        suggestDatabases: {
          prependFrom: true,
          appendDot: true
        }
      }
    });
  });

  it('should suggest databases or tables for "SELECT * fr|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * fr',
      afterCursor: '',
      containsKeywords: ['FROM'],
      expectedResult: {
        lowerCase: false,
        suggestTables: {
          prependFrom: true
        },
        suggestDatabases: {
          prependFrom: true,
          appendDot: true
        }
      }
    });
  });

  it('should suggest databases or tables for "SELECT * FROM |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: {},
        suggestDatabases: {
          appendDot: true
        }
      }
    });
  });

  it('should suggest databases or tables for "SELECT * FROM tes|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM tes',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: {},
        suggestDatabases: {
          appendDot: true
        }
      }
    });
  });

  it('should suggest databases or tables for "SELECT * FROM `tes|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM `tes',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { appendBacktick: true },
        suggestDatabases: {
          appendBacktick: true,
          appendDot: true
        }
      }
    });
  });

  it('should suggest tables for "SELECT * FROM database_two.|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM database_two.',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: 'database_two' }] }
      }
    });
  });

  it('should suggest tables for "SELECT * FROM `database_two`.|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM `database_two`.',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: 'database_two' }] }
      }
    });
  });

  it('should suggest tables for "SELECT * FROM 33abc.|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM 33abc.',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: '33abc' }] }
      }
    });
  });

  it('should suggest tables for "SELECT * FROM `database_two`.`bla |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM `database_two`.`bla ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: 'database_two' }] }
      }
    });
  });

  describe('Complete Statements', () => {
    it('should handle "SELECT 4 / 2; |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT 4 / 2; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT 4 DIV 2; |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT 4 DIV 2; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT * FROM (VALUES(1,2,3),(4,5,6)) as foo; |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM (VALUES(1,2,3),(4,5,6)) as foo; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"SELECT * FROM (VALUES(1,2,3),(4,5,6)) as foo JOIN (VALUES(1,'a'),(4,'b')) as bar ON foo.col1 = bar.col1; |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "SELECT * FROM (VALUES(1,2,3),(4,5,6)) as foo JOIN (VALUES(1,'a'),(4,'b')) as bar ON foo.col1 = bar.col1; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"WITH t1 AS (VALUES('a', 'b'), ('b', 'c')) SELECT * FROM t1 WHERE col1 = 'a' UNION ALL SELECT * from t1 WHERE col1 = 'b'; |\"", () => {
      assertAutoComplete({
        beforeCursor:
          "WITH t1 AS (VALUES('a', 'b'), ('b', 'c')) SELECT * FROM t1 WHERE col1 = 'a' UNION ALL SELECT * from t1 WHERE col1 = 'b'; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT t1.bigint_col FROM alltypestiny t1 WHERE t1.bigint_col > 1 AND NOT EXISTS (SELECT SUM(smallint_col) AS int_col FROM alltypestiny WHERE t1.date_string_col = string_col AND t1.timestamp_col = timestamp_col) GROUP BY t1.bigint_col; |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT t1.bigint_col FROM alltypestiny t1 WHERE t1.bigint_col > 1 AND NOT EXISTS (SELECT SUM(smallint_col) AS int_col FROM alltypestiny WHERE t1.date_string_col = string_col AND t1.timestamp_col = timestamp_col) GROUP BY t1.bigint_col; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it("should handle \"SELECT bla NOT RLIKE 'ble', ble NOT REGEXP 'b' FROM tbl; |\"", () => {
      assertAutoComplete({
        beforeCursor: "SELECT bla NOT RLIKE 'ble', ble NOT REGEXP 'b' FROM tbl; ",
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT * FROM tbl limit ${limit=20}; |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM tbl limit ${limit=20}; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns "SELECT IF(baa, boo, bee) AS b, | FROM testTable;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT IF(baa, boo, bee) AS b, ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAnalyticFunctions: true,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns "SELECT IF(baa > 2, boo, bee) AS b, | FROM testTable;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT IF(baa > 2, boo, bee) AS b, ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAnalyticFunctions: true,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    // Enable to check performance
    xit('should handle 100k rows before and after "SELECT * FROM foo WHERE (bar = \'bla\') AND (ble = 1);|"', () => {
      let beforeCursor = '';
      let afterCursor = ';\n';
      for (let i = 0; i < 100000; i++) {
        beforeCursor += "SELECT * FROM foo WHERE (bar = 'bla') AND (ble = 1);\n";
        afterCursor += "SELECT * FROM foo WHERE (bar = 'bla') AND (ble = 1);\n";
      }
      assertAutoComplete({
        beforeCursor: beforeCursor,
        afterCursor: afterCursor,
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('Select List Completion', () => {
    it('should handle "select count(*), tst.count, avg (id), avg from autocomp_test tst;"', () => {
      assertAutoComplete({
        beforeCursor: 'select count(*), tst.count, avg (id), avg from autocomp_test tst;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 65 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 42 }
            },
            {
              type: 'function',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 12 },
              function: 'count'
            },
            {
              type: 'functionArgument',
              location: { first_line: 1, last_line: 1, first_column: 14, last_column: 15 },
              function: 'count',
              argumentPosition: 0,
              identifierChain: [{ name: 'count' }],
              expression: { text: '*' }
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 18, last_column: 21 },
              identifierChain: [{ name: 'autocomp_test' }]
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 22, last_column: 27 },
              identifierChain: [{ name: 'count' }],
              tables: [{ identifierChain: [{ name: 'autocomp_test' }], alias: 'tst' }],
              qualified: true
            },
            {
              type: 'function',
              location: { first_line: 1, last_line: 1, first_column: 29, last_column: 32 },
              function: 'avg'
            },
            {
              type: 'functionArgument',
              location: { first_line: 1, last_line: 1, first_column: 34, last_column: 36 },
              function: 'avg',
              argumentPosition: 0,
              identifierChain: [{ name: 'avg' }],
              expression: { types: ['COLREF'], columnReference: [{ name: 'id' }] }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 34, last_column: 36 },
              identifierChain: [{ name: 'id' }],
              tables: [{ identifierChain: [{ name: 'autocomp_test' }], alias: 'tst' }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 39, last_column: 42 },
              identifierChain: [{ name: 'avg' }],
              tables: [{ identifierChain: [{ name: 'autocomp_test' }], alias: 'tst' }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 48, last_column: 61 },
              identifierChain: [{ name: 'autocomp_test' }]
            },
            {
              type: 'alias',
              source: 'table',
              alias: 'tst',
              location: { first_line: 1, last_line: 1, first_column: 62, last_column: 65 },
              identifierChain: [{ name: 'autocomp_test' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 65, last_column: 65 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 65, last_column: 65 }
            }
          ],
          lowerCase: true
        }
      });
    });

    it('should suggest tables for "SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: '',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT |;\n\nSELECT * FROM foo;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ';\n\nSELECT * FROM foo;',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM foo;\n\nSELECT |;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo;\n\nSELECT ',
        afterCursor: ';',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT |;\n\nSELECT * FROM foo boo;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ';\n\nSELECT * FROM foo boo;',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM foo boo;\n\nSELECT |;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo boo;\n\nSELECT ',
        afterCursor: ';',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest lowerCase for "select |"', () => {
      assertAutoComplete({
        beforeCursor: 'select ',
        afterCursor: '',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: true,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT ALL |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ALL ',
        afterCursor: '',
        containsKeywords: ['*', 'CASE'],
        doesNotContainKeywords: ['ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT DISTINCT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT DISTINCT ',
        afterCursor: '',
        containsKeywords: ['*'],
        doesNotContainKeywords: ['ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest keywords for "SELECT DISTINCT | a, b, c FROM tbl"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT DISTINCT ',
        afterCursor: ' a, b, c FROM tbl',
        containsKeywords: ['*'],
        doesNotContainKeywords: ['ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tbl' }] }] },
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 34 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 15, last_column: 25 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 },
              identifierChain: [{ name: 'a' }],
              tables: [{ identifierChain: [{ name: 'tbl' }] }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 21, last_column: 22 },
              identifierChain: [{ name: 'b' }],
              tables: [{ identifierChain: [{ name: 'tbl' }] }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 24, last_column: 25 },
              identifierChain: [{ name: 'c' }],
              tables: [{ identifierChain: [{ name: 'tbl' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 31, last_column: 34 },
              identifierChain: [{ name: 'tbl' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 34, last_column: 34 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 34, last_column: 34 }
            }
          ]
        }
      });
    });

    it('should suggest tables for "SELECT | FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM tableA;',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableA' }] }] }
        }
      });
    });

    it('should suggest tables for "SELECT | AS boo FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' AS boo FROM tableA;',
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableA' }] }] }
        }
      });
    });

    it('should suggest tables for "SELECT | boo FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' boo FROM tableA;',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableA' }] }] }
        }
      });
    });

    it('should suggest tables for "SELECT bla| AS boo FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bla',
        afterCursor: ' AS boo FROM tableA;',
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableA' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT | FROM testWHERE"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM testWHERE',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testWHERE' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testWHERE' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT (bl|a AND boo FROM testWHERE"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT (bl',
        afterCursor: ' AND boo FROM testWHERE',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testWHERE' }] }]
          }
        }
      });
    });

    // TODO: Parser can't handle multiple errors in a row, in this case 2 missing ')')
    xit('should suggest columns for "SELECT ((| FROM testWHERE"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ((',
        afterCursor: ' FROM testWHERE',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testWHERE' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT (bla| AND boo FROM testWHERE"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT (bla',
        afterCursor: ' AND boo FROM testWHERE',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testWHERE' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT | FROM testON"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM testON',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testON' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'testON' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT | FROM transactions"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM transactions',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'transactions' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'transactions' }] }]
          }
        }
      });
    });

    it('should suggest aliases for "SELECT | FROM testTableA tta, testTableB"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM testTableA tta, testTableB',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: {
            tables: [
              { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
              { identifierChain: [{ name: 'testTableB' }] }
            ]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [
              { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
              { identifierChain: [{ name: 'testTableB' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'tta.', type: 'alias' },
            { name: 'testTableB.', type: 'table' }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT TTA.| FROM testTableA tta"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT TTA.',
        afterCursor: ' FROM testTableA tta',
        containsKeywords: ['*'],
        expectedResult: {
          lowerCase: false,
          // TODO: add alias on table in suggestColumns (needs support in sqlAutocomplete3.js)
          // Case is: select cu.| from customers
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTableA' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT tta.| FROM testTableA TTA"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT tta.',
        afterCursor: ' FROM testTableA TTA',
        containsKeywords: ['*'],
        expectedResult: {
          lowerCase: false,
          // TODO: add alias on table in suggestColumns (needs support in sqlAutocomplete3.js)
          // Case is: select cu.| from customers
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTableA' }] }]
          }
        }
      });
    });

    it('should suggest columns for "select | from database_two.testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'select ',
        afterCursor: ' from database_two.testTable',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: true,
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "select | from `database one`.`test table`"', () => {
      assertAutoComplete({
        beforeCursor: 'select ',
        afterCursor: ' from `database one`.`test table`',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: true,
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'database one' }, { name: 'test table' }] }]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'database one' }, { name: 'test table' }] }]
          },
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 41 }
            },
            {
              type: 'selectList',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 7, last_column: 7 }
            },
            {
              type: 'database',
              location: { first_line: 1, last_line: 1, first_column: 14, last_column: 28 },
              identifierChain: [{ name: 'database one' }]
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 29, last_column: 41 },
              identifierChain: [{ name: 'database one' }, { name: 'test table' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 41, last_column: 41 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 41, last_column: 41 }
            }
          ]
        }
      });
    });

    it('should suggest aliases for "SELECT | FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.arr) ttaSum, testTableB ttb"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          ' FROM testTableA tta, (SELECT SUM(A*B) total FROM tta.arr) ttaSum, testTableB ttb',
        ignoreErrors: true,
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: {
            tables: [
              { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
              { identifierChain: [{ name: 'testTableB' }], alias: 'ttb' }
            ]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [
              { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
              { identifierChain: [{ subQuery: 'ttaSum' }] },
              { identifierChain: [{ name: 'testTableB' }], alias: 'ttb' }
            ]
          },
          subQueries: [
            {
              alias: 'ttaSum',
              columns: [{ alias: 'total', type: 'UDFREF', udfRef: 'sum' }]
            }
          ],
          suggestIdentifiers: [
            { name: 'tta.', type: 'alias' },
            { name: 'ttaSum.', type: 'sub-query' },
            { name: 'ttb.', type: 'alias' }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT a, | FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, ',
        afterCursor: ' FROM tableA;',
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableA' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT a,| FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a,',
        afterCursor: ' FROM testTable',
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT *, | FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT *, ',
        afterCursor: ' FROM tableA;',
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableA' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'tableA' }] }] }
        }
      });
    });

    it('should suggest keywords for "SELECT a | FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a ',
        afterCursor: ' FROM tableA;',
        containsKeywords: ['AS', '='],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'tableA' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest keywords for "SELECT a |, FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a ',
        afterCursor: ', FROM tableA;',
        containsKeywords: ['AS', '='],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'tableA' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest keywords for "SELECT a, b | FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b ',
        afterCursor: ' FROM tableA;',
        containsKeywords: ['AS', '='],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'tableA' }, { name: 'b' }] }
        }
      });
    });

    it('should suggest keywords for "SELECT a |, b, c AS foo, d FROM tableA;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a ',
        afterCursor: ', b, c AS foo, d FROM tableA;',
        containsKeywords: ['AS', '='],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'tableA' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest columns for "SELECT | a, cast(b as int), c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          " a, cast(b as int), c, d FROM testTable WHERE a = 'US' AND b >= 998 ORDER BY c DESC LIMIT 15",
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, |,c, d FROM testTable WHERE a = \'US\' AND b >= 998 ORDER BY c DESC LIMIT 15"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, ',
        afterCursor: ",c, d FROM testTable WHERE a = 'US' AND b >= 998 ORDER BY c DESC LIMIT 15",
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 87 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 22 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
              identifierChain: [{ name: 'a' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 11, last_column: 12 },
              identifierChain: [{ name: 'b' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 },
              identifierChain: [{ name: 'c' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 },
              identifierChain: [{ name: 'd' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 25, last_column: 34 },
              identifierChain: [{ name: 'testTable' }]
            },
            {
              type: 'whereClause',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 35, last_column: 62 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 41, last_column: 42 },
              identifierChain: [{ name: 'a' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 54, last_column: 55 },
              identifierChain: [{ name: 'b' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 72, last_column: 73 },
              identifierChain: [{ name: 'c' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'limitClause',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 79, last_column: 87 }
            }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT col.cplx.| from tbl1"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT col.cplx.',
        afterCursor: ' from tbl1',
        containsKeywords: ['*'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'col' }, { name: 'cplx' }],
            tables: [{ identifierChain: [{ name: 'tbl1' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT col.cplx.| from tbl1, tbl2 t2"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT col.cplx.',
        afterCursor: ' from tbl1, tbl2 t2',
        containsKeywords: ['*'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'col' }, { name: 'cplx' }],
            tables: [
              { identifierChain: [{ name: 'tbl1' }] },
              { identifierChain: [{ name: 'tbl2' }], alias: 't2' }
            ]
          }
        }
      });
    });
  });

  describe('Variable References', () => {
    it('should suggest tables for "SELECT | FROM ${some_variable};"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM ${some_variable};',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: '${some_variable}' }] }]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: '${some_variable}' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable WHERE ${some_variable} |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE ${some_variable} ',
        afterCursor: '',
        containsKeywords: ['<', 'BETWEEN'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: '${some_variable}' }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE ${some_variable} + 1 = |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE ${some_variable} + 1 = ',
        afterCursor: '',
        containsKeywords: ['CASE', 'NULL'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });
  });

  describe('Window and analytic functions', () => {
    it('should handle "SELECT row_number() OVER (PARTITION BY a) FROM testTable;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a) FROM testTable;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT COUNT(DISTINCT a) OVER (PARTITION by c) FROM testTable;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(DISTINCT a) OVER (PARTITION by c) FROM testTable;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest analytical functions for "SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: '',
        containsKeywords: ['*'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: { prependQuestionMark: true, prependFrom: true },
          suggestDatabases: { prependQuestionMark: true, prependFrom: true, appendDot: true }
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() ',
        afterCursor: '',
        containsKeywords: ['OVER'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['OVER'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() |, b, c FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() ',
        afterCursor: ', b, c FROM testTable',
        containsKeywords: ['OVER'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT count(DISTINCT a) |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT count(DISTINCT a) ',
        afterCursor: '',
        containsKeywords: ['OVER'],
        expectedResult: {
          lowerCase: false,
          suggestTables: { prependFrom: true },
          suggestDatabases: { prependFrom: true, appendDot: true }
        }
      });
    });

    it('should suggest keywords for "SELECT count(DISTINCT a) | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT count(DISTINCT a) ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['OVER'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT count(DISTINCT a) |, b, c FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT count(DISTINCT a) ',
        afterCursor: ', b, c FROM testTable',
        containsKeywords: ['OVER'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (| FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER ( ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['PARTITION BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a, b ORDER | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a, b ORDER ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT row_number() OVER (ORDER BY | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (ORDER BY ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT row_number() OVER (ORDER BY |) FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (ORDER BY ',
        afterCursor: ') FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          } // TODO: source: 'order by'
        }
      });
    });

    it('should suggest columns for "SELECT row_number() OVER (ORDER BY foo |) FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (ORDER BY a ',
        afterCursor: ') FROM testTable',
        containsKeywords: ['ASC', 'DESC'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT row_number() OVER (PARTITION BY | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT row_number() OVER (PARTITION BY a, | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a, ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ',
        afterCursor: '',
        containsKeywords: ['ASC', 'ROWS BETWEEN', 'RANGE BETWEEN'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CURRENT ROW', 'UNBOUNDED PRECEDING']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PRECEDING']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PRECEDING']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROW']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AND']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AND']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AND']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CURRENT ROW', 'UNBOUNDED FOLLOWING']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CURRENT ROW', 'UNBOUNDED FOLLOWING']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['CURRENT ROW', 'UNBOUNDED FOLLOWING']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND CURRENT |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN 1 PRECEDING AND CURRENT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ROW']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOLLOWING']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND 1 |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS BETWEEN CURRENT ROW AND 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FOLLOWING']
        }
      });
    });

    it('should suggest keywords for "SELECT count(id) OVER w FROM customers |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT count(id) OVER w FROM customers ',
        afterCursor: '',
        containsKeywords: ['WINDOW'],
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: true,
            tables: [{ identifierChain: [{ name: 'customers' }] }]
          },
          suggestFilters: {
            prefix: 'WHERE',
            tables: [{ identifierChain: [{ name: 'customers' }] }]
          },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'customers' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'customers' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT count(id) OVER w FROM customers WINDOW w |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT count(id) OVER w FROM customers WINDOW w ',
        afterCursor: '',
        containsKeywords: ['AS'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT count(id) OVER w FROM customers WINDOW w AS (|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT count(id) OVER w FROM customers WINDOW w AS (',
        afterCursor: '',
        containsKeywords: ['ORDER BY', 'PARTITION BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BETWEEN', 'UNBOUNDED']
        }
      });
    });

    it('should suggest keywords for "SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS UNBOUNDED |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT row_number() OVER (PARTITION BY a ORDER BY b ROWS UNBOUNDED ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PRECEDING']
        }
      });
    });
  });

  describe('Functions', () => {
    it('should suggest tables for "SELECT COUNT(*) |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(*) ',
        afterCursor: '',
        containsKeywords: ['AS', '+'],
        expectedResult: {
          lowerCase: false,
          suggestTables: {
            prependFrom: true
          },
          suggestDatabases: {
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest keywords for "SELECT COUNT(foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(foo ',
        afterCursor: '',
        containsKeywords: ['AND', '='],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT COUNT(foo, |) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(foo, ',
        afterCursor: ') FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT COUNT(foo, bl|, bla) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(foo, bl',
        afterCursor: ',bla) FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "SELECT COUNT(foo, bla |, bar)"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(foo ',
        afterCursor: ', bar)',
        containsKeywords: ['AND', '='],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns and values for "SELECT COUNT(foo, bl = |,bla) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(foo, bl = ',
        afterCursor: ',bla) FROM bar;',
        containsKeywords: ['CASE'],
        hasErrors: false,
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            source: 'select',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'bar' }] }]
          },
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
        }
      });
    });

    it('should suggest columns and values for "SELECT bl = \'| FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT bl = '",
        afterCursor: ' FROM bar;',
        hasErrors: false,
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 23 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 15 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
              identifierChain: [{ name: 'bl' }],
              tables: [{ identifierChain: [{ name: 'bar' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 20, last_column: 23 },
              identifierChain: [{ name: 'bar' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 23, last_column: 23 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 23, last_column: 23 }
            }
          ],
          lowerCase: false,
          suggestValues: { partialQuote: "'", missingEndQuote: true },
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
        }
      });
    });

    it('should suggest columns and values for "SELECT bl = \'|\' FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT bl = '",
        afterCursor: "' FROM bar;",
        hasErrors: false,
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 24 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 16 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
              identifierChain: [{ name: 'bl' }],
              tables: [{ identifierChain: [{ name: 'bar' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 21, last_column: 24 },
              identifierChain: [{ name: 'bar' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 24, last_column: 24 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 24, last_column: 24 }
            }
          ],
          lowerCase: false,
          suggestValues: { partialQuote: "'", missingEndQuote: false },
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
        }
      });
    });

    it('should suggest columns and values for "SELECT bl = \'bl| bl\' FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT bl = 'bl",
        afterCursor: " bl' FROM bar;",
        hasErrors: false,
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 29 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 19 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
              identifierChain: [{ name: 'bl' }],
              tables: [{ identifierChain: [{ name: 'bar' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 26, last_column: 29 },
              identifierChain: [{ name: 'bar' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 29, last_column: 29 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 29, last_column: 29 }
            }
          ],
          lowerCase: false,
          suggestValues: { partialQuote: "'", missingEndQuote: false },
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
        }
      });
    });

    it('should suggest columns and values for "SELECT bl = "| FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bl = "',
        afterCursor: ' FROM bar;',
        hasErrors: false,
        expectedResult: {
          lowerCase: false,
          suggestValues: { partialQuote: '"', missingEndQuote: true },
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
        }
      });
    });

    it('should suggest columns and values for "SELECT bl = "|" FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bl = "',
        afterCursor: '" FROM bar;',
        hasErrors: false,
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 24 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 16 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
              identifierChain: [{ name: 'bl' }],
              tables: [{ identifierChain: [{ name: 'bar' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 21, last_column: 24 },
              identifierChain: [{ name: 'bar' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 24, last_column: 24 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 24, last_column: 24 }
            }
          ],
          lowerCase: false,
          suggestValues: { partialQuote: '"', missingEndQuote: false },
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
        }
      });
    });

    it('should suggest columns and values for "SELECT bl = "bl| bl" FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bl = "bl',
        afterCursor: ' bl" FROM bar;',
        hasErrors: false,
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 29 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 19 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
              identifierChain: [{ name: 'bl' }],
              tables: [{ identifierChain: [{ name: 'bar' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 26, last_column: 29 },
              identifierChain: [{ name: 'bar' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 29, last_column: 29 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 29, last_column: 29 }
            }
          ],
          lowerCase: false,
          suggestValues: { partialQuote: '"', missingEndQuote: false },
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bl' }] }
        }
      });
    });

    it('should suggest functions for "SELECT CAST(|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {}
        }
      });
    });

    it('should suggest columns for "SELECT CAST(| FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(',
        afterCursor: ' FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT CAST(bla| FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(bla',
        afterCursor: ' FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT CAST(| AS FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(',
        afterCursor: ' AS FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT CAST(| AS INT FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(',
        afterCursor: ' AS INT FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT CAST(| AS STRING) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(',
        afterCursor: ' AS STRING) FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT CAST(bla| AS STRING) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(bla',
        afterCursor: ' AS STRING) FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "SELECT CAST(bla |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(bla ',
        afterCursor: '',
        containsKeywords: ['AS', 'AND'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT CAST(bla | FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(bla ',
        afterCursor: ' FROM bar;',
        containsKeywords: ['AS', '='],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bla' }] }
        }
      });
    });

    it('should suggest keywords for "select cast(bla as |"', () => {
      assertAutoComplete({
        beforeCursor: 'select cast(bla as ',
        afterCursor: '',
        containsKeywords: ['INT', 'INTEGER', 'STRING'],
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it('should suggest keywords for "SELECT CAST(bla AS | FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(bla AS ',
        afterCursor: ' FROM bar;',
        containsKeywords: ['INT', 'STRING'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT CAST(bla AS ST|) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(bla AS ST',
        afterCursor: ') FROM bar;',
        containsKeywords: ['INT', 'STRING'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT CAST(AS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(AS ',
        afterCursor: '',
        containsKeywords: ['INT', 'STRING'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest handle "SELECT db.customUdf(col) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT db.customUdf(col) FROM bar;',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 34 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 25 }
            },
            {
              type: 'database',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
              identifierChain: [{ name: 'db' }]
            },
            {
              type: 'function',
              location: { first_line: 1, last_line: 1, first_column: 11, last_column: 19 },
              identifierChain: [{ name: 'db' }, { name: 'customUdf' }],
              function: 'customudf'
            },
            {
              type: 'functionArgument',
              location: { first_line: 1, last_line: 1, first_column: 21, last_column: 24 },
              function: 'customudf',
              argumentPosition: 0,
              identifierChain: [{ name: 'db' }, { name: 'customUdf' }],
              expression: { types: ['COLREF'], columnReference: [{ name: 'col' }] }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 21, last_column: 24 },
              identifierChain: [{ name: 'col' }],
              tables: [{ identifierChain: [{ name: 'bar' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 31, last_column: 34 },
              identifierChain: [{ name: 'bar' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 34, last_column: 34 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 34, last_column: 34 }
            }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT db.customUdf(| FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT db.customUdf(',
        afterCursor: ' FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'bar' }] }]
          },
          udfArgument: {
            name: 'customudf',
            position: 1
          }
        }
      });
    });

    it('should suggest columns for "SELECT db.customUdf(1, | FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT db.customUdf(1, ',
        afterCursor: ' FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'bar' }] }]
          },
          udfArgument: {
            name: 'customudf',
            position: 2
          }
        }
      });
    });

    it('should suggest keywords for "SELECT extract(| FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT extract( ',
        afterCursor: ' FROM bar;',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'DAY',
            'DAYOFWEEK',
            'HOUR',
            'MINUTE',
            'MONTH',
            'QUARTER',
            'SECOND',
            'WEEK',
            'YEAR'
          ]
        }
      });
    });

    it('should suggest keywords for "SELECT extract(month | FROM bar"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT extract(month ',
        afterCursor: ' FROM bar;',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FROM']
        }
      });
    });

    it('should suggest columns for "SELECT extract(month FROM | FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT extract(month FROM ',
        afterCursor: ' FROM bar;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ name: 'bar' }] }] }
        }
      });
    });

    it('should suggest keywords for "SELECT extract(| FROM boo) FROM bar;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT extract( ',
        afterCursor: ' FROM boo) FROM bar;',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'DAY',
            'DAYOFWEEK',
            'HOUR',
            'MINUTE',
            'MONTH',
            'QUARTER',
            'SECOND',
            'WEEK',
            'YEAR'
          ]
        }
      });
    });

    it('should suggest columns for "SELECT <GeneralSetFunction>(|) FROM testTable"', () => {
      const aggregateFunctions = [
        { name: 'AVG', containsKeywords: ['DISTINCT'] },
        { name: 'collect_set', containsKeywords: ['DISTINCT'] },
        { name: 'COLLECT_LIST', containsKeywords: ['DISTINCT'] },
        { name: 'COUNT', containsKeywords: ['*', 'DISTINCT'] },
        { name: 'STDDEV_POP', containsKeywords: ['DISTINCT'] },
        { name: 'STDDEV_SAMP', containsKeywords: ['DISTINCT'] },
        { name: 'sum', containsKeywords: ['DISTINCT'] },
        { name: 'MAX', containsKeywords: ['DISTINCT'] },
        { name: 'MIN', containsKeywords: ['DISTINCT'] },
        { name: 'VAR_POP', containsKeywords: ['DISTINCT'] },
        { name: 'VAR_SAMP', containsKeywords: ['DISTINCT'] }
      ];
      aggregateFunctions.forEach(aggregateFunction => {
        if (aggregateFunction.name === 'COUNT') {
          assertAutoComplete({
            beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
            afterCursor: ') FROM testTable',
            containsKeywords: aggregateFunction.containsKeywords.concat(['*', 'CASE']),
            expectedResult: {
              lowerCase: false,
              suggestFunctions: {},
              suggestColumns: {
                source: 'select',
                tables: [{ identifierChain: [{ name: 'testTable' }] }]
              }
            }
          });
        } else {
          const expectedResult = {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: {
              source: 'select',
              tables: [{ identifierChain: [{ name: 'testTable' }] }]
            },
            udfArgument: {
              name: aggregateFunction.name.toLowerCase(),
              position: 1
            }
          };
          assertAutoComplete({
            beforeCursor: 'SELECT ' + aggregateFunction.name + '(',
            afterCursor: ') FROM testTable',
            containsKeywords: aggregateFunction.containsKeywords.concat(['CASE']),
            expectedResult: expectedResult
          });
        }
      });
    });

    it('should suggest columns for "SELECT <BinarySetFunction>(|,col) FROM testTable"', () => {
      const binaryFunctions = [{ name: 'CORR' }, { name: 'COVAR_POP' }, { name: 'COVAR_SAMP' }];

      binaryFunctions.forEach(binaryFunction => {
        assertAutoComplete({
          beforeCursor: 'SELECT ' + binaryFunction.name + '(',
          afterCursor: ',col) FROM testTable',
          containsKeywords: ['DISTINCT', 'CASE'],
          doesNotContainKeywords: ['ALL'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: {
              source: 'select',
              tables: [{ identifierChain: [{ name: 'testTable' }] }]
            },
            udfArgument: {
              name: binaryFunction.name.toLowerCase(),
              position: 1
            }
          }
        });
      });
    });

    it('should suggest columns for "SELECT <BinarySetFunction>(,|) FROM testTable"', () => {
      const binaryFunctions = [{ name: 'CORR' }, { name: 'COVAR_POP' }, { name: 'COVAR_SAMP' }];

      binaryFunctions.forEach(binaryFunction => {
        assertAutoComplete({
          beforeCursor: 'SELECT ' + binaryFunction.name + '(,',
          afterCursor: ') FROM testTable',
          containsKeywords: ['CASE'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: {
              source: 'select',
              tables: [{ identifierChain: [{ name: 'testTable' }] }]
            },
            udfArgument: {
              name: binaryFunction.name.toLowerCase(),
              position: 2
            }
          }
        });
      });
    });

    it('should suggest columns for "SELECT <BinarySetFunction>(| FROM testTable"', () => {
      const binaryFunctions = [{ name: 'CORR' }, { name: 'COVAR_POP' }, { name: 'COVAR_SAMP' }];

      binaryFunctions.forEach(binaryFunction => {
        assertAutoComplete({
          beforeCursor: 'SELECT ' + binaryFunction.name + '(',
          afterCursor: ' FROM testTable',
          containsKeywords: ['CASE', 'DISTINCT'],
          doesNotContainKeywords: ['ALL'],
          expectedResult: {
            lowerCase: false,
            suggestFunctions: {},
            suggestColumns: {
              source: 'select',
              tables: [{ identifierChain: [{ name: 'testTable' }] }]
            },
            udfArgument: {
              name: binaryFunction.name.toLowerCase(),
              position: 1
            }
          }
        });
      });
    });

    it('should suggest columns for "SELECT id, SUM(a * | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT id, SUM(a * ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'select',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE ',
        afterCursor: ' FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestKeywords: ['WHEN']
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN a = b AND | THEN FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN a = b AND ',
        afterCursor: ' THEN FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = b AND | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = b AND ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT CASE a = b | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = b ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['WHEN', 'AND', '<>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN a = b OR | THEN boo FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN a = b OR ',
        afterCursor: ' THEN boo FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN a = b OR c THEN boo OR | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN a = b OR c THEN boo OR ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a =| WHEN c THEN d END FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a =',
        afterCursor: ' WHEN c THEN d END FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            source: 'select',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a =| WHEN c THEN d ELSE e END FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a =',
        afterCursor: ' WHEN c THEN d ELSE e END FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            source: 'select',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c THEN d | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN d ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['END', '<>'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c THEN d=| ELSE FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN d=',
        afterCursor: ' ELSE FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            source: 'select',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest keywords for "SELECT CASE a = c WHEN c THEN d=1 | bla=foo FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN d=1 ',
        afterCursor: ' bla=foo FROM testTable',
        containsKeywords: ['AND', 'WHEN', 'ELSE', 'END', '<'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT CASE a = c WHEN c THEN d=1 | bla=foo END FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN d=1 ',
        afterCursor: ' bla=foo FROM testTable',
        containsKeywords: ['AND', 'WHEN', 'ELSE', '>'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE e AND | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE e AND ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE ELSE | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE ELSE ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE | ELSE a FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE ',
        afterCursor: ' ELSE a FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestKeywords: ['WHEN']
        }
      });
    });

    it('should suggest columns for "SELECT CASE | ELSE FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE ',
        afterCursor: ' ELSE FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestKeywords: ['WHEN']
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c THEN d ELSE e | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN d ELSE e ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['END', '='],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'e' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN THEN boo OR | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN THEN boo OR ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT CASE | a = b THEN FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE ',
        afterCursor: ' a = b THEN FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WHEN']
        }
      });
    });

    it('should suggest keywords for "SELECT CASE | a = b THEN boo FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE ',
        afterCursor: ' a = b THEN boo FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WHEN']
        }
      });
    });

    it('should suggest keywords for "SELECT CASE | THEN boo FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE ',
        afterCursor: ' THEN boo FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['WHEN'],
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN | boo FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN ',
        afterCursor: ' boo FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['THEN'],
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN bla| boo WHEN b THEN c END FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN bla',
        afterCursor: ' boo WHEN b THEN c END FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['THEN'],
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a WHEN b THEN c WHEN | boo ELSE c FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a WHEN b THEN c WHEN ',
        afterCursor: ' boo ELSE c FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['THEN'],
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a WHEN b THEN c WHEN | boo WHEN d THEN e END FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a WHEN b THEN c WHEN ',
        afterCursor: ' boo WHEN d THEN e END FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['THEN'],
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT CASE a WHEN b THEN c | WHEN d THEN e END FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a WHEN b THEN c ',
        afterCursor: ' WHEN d THEN e END FROM testTable',
        containsKeywords: ['WHEN', '<'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'c' }] }
        }
      });
    });

    it('should suggest keywords for "SELECT CASE a WHEN b THEN c | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a WHEN b THEN c ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['WHEN', '>'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'c' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN | THEN FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN ',
        afterCursor: ' THEN FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest values for "SELECT CASE WHEN | = a FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN ',
        afterCursor: ' = a FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            source: 'select',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN ab| THEN bla ELSE foo FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN ab',
        afterCursor: ' THEN bla ELSE foo FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE bla WHEN ab| THEN bla ELSE foo END FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE bla WHEN ab',
        afterCursor: ' THEN bla ELSE foo END FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a WHEN | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a WHEN ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN a = | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN a = ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            source: 'select',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN a = b | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN a = b ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['AND', 'THEN', '<'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c | d FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c ',
        afterCursor: ' d FROM testTable',
        containsKeywords: ['THEN', '>'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'c' }] }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c THEN | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE a = c WHEN c THEN | g FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE a = c WHEN c THEN ',
        afterCursor: ' g FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN THEN | g FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN THEN ',
        afterCursor: ' g FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT CASE WHEN THEN | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CASE WHEN THEN ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });
  });

  it('should suggest keywords for "SELECT bar FROM foo |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM foo ',
      afterCursor: '',
      expectedResult: {
        suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestKeywords: [
          'AS',
          'WHERE',
          'GROUP BY',
          'HAVING',
          'WINDOW',
          'ORDER BY',
          'CLUSTER BY',
          'DISTRIBUTE BY',
          'SORT BY',
          'LIMIT',
          'UNION',
          'LATERAL VIEW',
          'TABLESAMPLE',
          'CROSS JOIN',
          'FULL JOIN',
          'FULL OUTER JOIN',
          'INNER JOIN',
          'JOIN',
          'LEFT JOIN',
          'LEFT OUTER JOIN',
          'LEFT SEMI JOIN',
          'RIGHT JOIN',
          'RIGHT OUTER JOIN'
        ],
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM db.foo f |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM db.foo f ',
      afterCursor: '',
      expectedResult: {
        suggestJoins: {
          prependJoin: true,
          tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }]
        },
        suggestFilters: {
          prefix: 'WHERE',
          tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }]
        },
        suggestGroupBys: {
          prefix: 'GROUP BY',
          tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }]
        },
        suggestOrderBys: {
          prefix: 'ORDER BY',
          tables: [{ identifierChain: [{ name: 'db' }, { name: 'foo' }], alias: 'f' }]
        },
        suggestKeywords: [
          'WHERE',
          'GROUP BY',
          'HAVING',
          'WINDOW',
          'ORDER BY',
          'CLUSTER BY',
          'DISTRIBUTE BY',
          'SORT BY',
          'LIMIT',
          'UNION',
          'LATERAL VIEW',
          'CROSS JOIN',
          'FULL JOIN',
          'FULL OUTER JOIN',
          'INNER JOIN',
          'JOIN',
          'LEFT JOIN',
          'LEFT OUTER JOIN',
          'LEFT SEMI JOIN',
          'RIGHT JOIN',
          'RIGHT OUTER JOIN'
        ],
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM foo JOIN baz |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM foo JOIN baz ',
      afterCursor: '',
      containsKeywords: ['ON'],
      expectedResult: {
        lowerCase: false,
        suggestFilters: {
          prefix: 'WHERE',
          tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }]
        },
        suggestGroupBys: {
          prefix: 'GROUP BY',
          tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }]
        },
        suggestOrderBys: {
          prefix: 'ORDER BY',
          tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }]
        },
        suggestJoinConditions: {
          prependOn: true,
          tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }]
        }
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM foo JOIN baz | JOIN bla"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM foo JOIN baz ',
      afterCursor: ' JOIN bla',
      containsKeywords: ['ON'],
      expectedResult: {
        lowerCase: false,
        suggestJoinConditions: {
          prependOn: true,
          tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'baz' }] }]
        }
      }
    });
  });

  it('should suggest keywords for "SELECT bar\\nFROM foo\\n|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar\nFROM foo\n',
      afterCursor: '',
      containsKeywords: ['WHERE', 'HAVING'],
      expectedResult: {
        lowerCase: false,
        suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM foo LATERAL |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM foo LATERAL ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['VIEW']
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM db.foo f LATERAL |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM db.foo f LATERAL ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['VIEW']
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM db.foo AS f LATERAL |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM db.foo AS f LATERAL ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['VIEW']
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM foo LATERAL VIEW |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM foo LATERAL VIEW ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['OUTER', 'explode', 'posexplode']
      }
    });
  });

  it('should suggest keywords for "SELECT bar FROM foo LATERAL VIEW explode(bar) b |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT bar FROM foo LATERAL VIEW explode(bar) b ',
      afterCursor: '',
      containsKeywords: ['AS', 'WHERE'],
      expectedResult: {
        lowerCase: false,
        suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
        suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
      }
    });
  });

  it('should suggest columns for "SELECT testMap[].| FROM testTable"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT testMap[].',
      afterCursor: ' FROM testTable',
      expectedResult: {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          identifierChain: [{ name: 'testMap', keySet: true }],
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        },
        suggestKeywords: ['*']
      }
    });
  });

  it('should suggest values for "SELECT testMap[|] FROM testTable"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT testMap[',
      afterCursor: '] FROM testTable',
      expectedResult: {
        lowerCase: false,
        suggestFunctions: {}, // TODO: types: ['COLREF_KEY']
        suggestColumns: {
          source: 'select',
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        },
        suggestKeyValues: { identifierChain: [{ name: 'testTable' }, { name: 'testMap' }] }
      }
    });
  });

  it('should suggest columns for "SELECT testMap[\'anyKey\'].| FROM testTable"', () => {
    assertAutoComplete({
      beforeCursor: "SELECT testMap['anyKey'].",
      afterCursor: ' FROM testTable',
      expectedResult: {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          identifierChain: [{ name: 'testMap', keySet: true }],
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        },
        suggestKeywords: ['*']
      }
    });
  });

  it('should suggest columns for "SELECT testMap[substr(\'bla\', 1)].| FROM testTable"', () => {
    assertAutoComplete({
      beforeCursor: "SELECT testMap[substr('bla', 1)].",
      afterCursor: ' FROM testTable',
      expectedResult: {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          identifierChain: [{ name: 'testMap', keySet: true }],
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        },
        suggestKeywords: ['*']
      }
    });
  });

  it('should suggest columns for "SELECT testMap["anyKey"].fieldC.| FROM testTable"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT testMap["anyKey"].fieldC.',
      afterCursor: ' FROM testTable',
      expectedResult: {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          identifierChain: [{ name: 'testMap', keySet: true }, { name: 'fieldC' }],
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        },
        suggestKeywords: ['*']
      }
    });
  });

  it('should suggest columns for "SELECT testArray[1].fieldC.| FROM testTable"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT testArray[1].fieldC.',
      afterCursor: ' FROM testTable',
      expectedResult: {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          identifierChain: [{ name: 'testArray', keySet: true }, { name: 'fieldC' }],
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        },
        suggestKeywords: ['*']
      }
    });
  });

  it('should suggest columns for "SELECT testFoo[1].testBar["key"].| FROM testTable"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT testFoo[1].testBar["key"].',
      afterCursor: ' FROM testTable',
      expectedResult: {
        lowerCase: false,
        suggestColumns: {
          source: 'select',
          identifierChain: [
            { name: 'testFoo', keySet: true },
            { name: 'testBar', keySet: true }
          ],
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        },
        suggestKeywords: ['*']
      }
    });
  });

  it('should suggest columns for "SELECT * FROM testTable WHERE testMap[].|"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM testTable WHERE testMap[].',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestColumns: {
          source: 'where',
          identifierChain: [{ name: 'testMap', keySet: true }],
          tables: [{ identifierChain: [{ name: 'testTable' }] }]
        }
      }
    });
  });

  describe('lateral views', () => {
    it('should suggest aliases for "SELECT | FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 81 }
            },
            {
              type: 'selectList',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 7, last_column: 7 }
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 14, last_column: 23 },
              identifierChain: [{ name: 'testTable' }]
            },
            {
              type: 'function',
              location: { first_line: 1, last_line: 1, first_column: 37, last_column: 43 },
              function: 'explode'
            },
            {
              type: 'functionArgument',
              location: { first_line: 1, last_line: 1, first_column: 45, last_column: 54 },
              function: 'explode',
              argumentPosition: 0,
              identifierChain: [{ name: 'explode' }],
              expression: { types: ['COLREF'], columnReference: [{ name: 'testArray' }] }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 45, last_column: 54 },
              identifierChain: [{ name: 'testArray' }],
              tables: [{ identifierChain: [{ name: 'testTable' }] }],
              qualified: false
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 81, last_column: 81 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 81, last_column: 81 }
            }
          ],
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestIdentifiers: [
            { name: 'explodedTable.', type: 'alias' },
            { name: 'testItem', type: 'alias' }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest aliases for "SELECT | FROM testTable LATERAL VIEW EXPLODE(testTable.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          ' FROM testTable LATERAL VIEW EXPLODE(testTable.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;',
        noErrors: true,
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestIdentifiers: [
            { name: 'a.', type: 'alias' },
            { name: 'arr_exp', type: 'alias' },
            { name: 'i.', type: 'alias' },
            { name: 'arr_items', type: 'alias' }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest aliases for "SELECT | FROM testTable t LATERAL VIEW EXPLODE(t.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          ' FROM testTable t LATERAL VIEW EXPLODE(t.arr) a AS arr_exp LATERAL VIEW EXPLODE(arr_exp.items) i AS arr_items;',
        noErrors: true,
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't' }]
          },
          suggestIdentifiers: [
            { name: 't.', type: 'alias' },
            { name: 'a.', type: 'alias' },
            { name: 'arr_exp', type: 'alias' },
            { name: 'i.', type: 'alias' },
            { name: 'arr_items', type: 'alias' }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT | FROM testTable LATERAL VIEW explode("', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM testTable LATERAL VIEW explode(',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW explode(|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'explode',
            position: 1
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW explode(a.b.|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable LATERAL VIEW explode(a.b.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            identifierChain: [{ name: 'a' }, { name: 'b' }],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'explode',
            position: 1
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable LATERAL VIEW posexplode(|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable LATERAL VIEW posexplode(',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'posexplode',
            position: 1
          }
        }
      });
    });

    it('should suggest aliases for "SELECT | FROM testTable LATERAL VIEW explode(testMap) explodedTable AS testKey, testValue"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          ' FROM testTable LATERAL VIEW explode(testMap) explodedTable AS testKey, testValue',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestIdentifiers: [
            { name: 'explodedTable.', type: 'alias' },
            { name: 'testKey', type: 'alias' },
            { name: 'testValue', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT testItem.| FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testItem.',
        afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'testArray' }, { name: 'item' }],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT testItemA.| FROM testTable LATERAL VIEW explode(testArrayA) explodedTableA AS testItemA LATERAL VIEW explode(testArrayB) explodedTableB AS testItemB"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testItemA.',
        afterCursor:
          ' FROM testTable' +
          ' LATERAL VIEW explode(testArrayA) explodedTableA AS testItemA' +
          ' LATERAL VIEW explode(testArrayB) explodedTableB AS testItemB',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'testArrayA' }, { name: 'item' }],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT\\n testItemA,\\n testItemB.|\\n\\tFROM\\n\\t testTable2 tt2\\n\\t LATERAL VIEW EXPLODE(tt2.testArrayA) explodedTableA AS testItemA\\n\\t LATERAL VIEW EXPLODE(tt2.testArrayB) explodedTableB AS testItemB"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT\n testItemA,\n testItemB.',
        afterCursor:
          '\n\tFROM\n\t testTable2 tt2\n' +
          '\t LATERAL VIEW EXPLODE(tt2.testArrayA) explodedTableA AS testItemA\n' +
          '\t LATERAL VIEW EXPLODE(tt2.testArrayB) explodedTableB AS testItemB',
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 7, first_column: 1, last_column: 67 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 2, last_line: 3, first_column: 2, last_column: 13 }
            },
            {
              type: 'complex',
              location: { first_line: 2, last_line: 2, first_column: 2, last_column: 11 },
              identifierChain: [{ name: 'testArrayA' }, { name: 'item' }],
              tables: [{ identifierChain: [{ name: 'testTable2' }], alias: 'tt2' }],
              qualified: false
            },
            {
              type: 'complex',
              location: { first_line: 3, last_line: 3, first_column: 2, last_column: 11 },
              identifierChain: [{ name: 'testArrayB' }, { name: 'item' }],
              tables: [{ identifierChain: [{ name: 'testTable2' }], alias: 'tt2' }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 5, last_line: 5, first_column: 3, last_column: 13 },
              identifierChain: [{ name: 'testTable2' }]
            },
            {
              type: 'alias',
              source: 'table',
              alias: 'tt2',
              location: { first_line: 5, last_line: 5, first_column: 14, last_column: 17 },
              identifierChain: [{ name: 'testTable2' }]
            },
            {
              type: 'function',
              location: { first_line: 6, last_line: 6, first_column: 16, last_column: 22 },
              function: 'explode'
            },
            {
              type: 'functionArgument',
              location: { first_line: 6, last_line: 6, first_column: 24, last_column: 38 },
              function: 'explode',
              argumentPosition: 0,
              identifierChain: [{ name: 'EXPLODE' }],
              expression: {
                types: ['COLREF'],
                columnReference: [{ name: 'tt2' }, { name: 'testArrayA' }]
              }
            },
            {
              type: 'table',
              location: { first_line: 6, last_line: 6, first_column: 24, last_column: 27 },
              identifierChain: [{ name: 'testTable2' }]
            },
            {
              type: 'column',
              location: { first_line: 6, last_line: 6, first_column: 28, last_column: 38 },
              identifierChain: [{ name: 'testArrayA' }],
              tables: [{ identifierChain: [{ name: 'testTable2' }], alias: 'tt2' }],
              qualified: true
            },
            {
              type: 'function',
              location: { first_line: 7, last_line: 7, first_column: 16, last_column: 22 },
              function: 'explode'
            },
            {
              type: 'functionArgument',
              location: { first_line: 7, last_line: 7, first_column: 24, last_column: 38 },
              function: 'explode',
              argumentPosition: 0,
              identifierChain: [{ name: 'EXPLODE' }],
              expression: {
                types: ['COLREF'],
                columnReference: [{ name: 'tt2' }, { name: 'testArrayB' }]
              }
            },
            {
              type: 'table',
              location: { first_line: 7, last_line: 7, first_column: 24, last_column: 27 },
              identifierChain: [{ name: 'testTable2' }]
            },
            {
              type: 'column',
              location: { first_line: 7, last_line: 7, first_column: 28, last_column: 38 },
              identifierChain: [{ name: 'testArrayB' }],
              tables: [{ identifierChain: [{ name: 'testTable2' }], alias: 'tt2' }],
              qualified: true
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 7, last_line: 7, first_column: 67, last_column: 67 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 7, last_line: 7, first_column: 67, last_column: 67 }
            }
          ],
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'testArrayB' }, { name: 'item' }],
            tables: [{ identifierChain: [{ name: 'testTable2' }] }]
          },
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT ta2_exp.| FROM    testTable tt LATERAL VIEW explode(tt.testArray1) ta1 AS ta1_exp\\n   LATERAL VIEW explode(ta1_exp.testArray2)    ta2   AS  ta2_exp"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ta2_exp.',
        afterCursor:
          ' FROM ' +
          '   testTable tt' +
          ' LATERAL VIEW explode(tt.testArray1) ta1 AS ta1_exp\n' +
          '   LATERAL VIEW explode(ta1_exp.testArray2)    ta2   AS  ta2_exp',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [
              { name: 'testArray1' },
              { name: 'item' },
              { name: 'testArray2' },
              { name: 'item' }
            ],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT explodedTable.testItem.| FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT explodedTable.testItem.',
        afterCursor: ' FROM testTable LATERAL VIEW explode(testArray) explodedTable AS testItem',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'testArray' }, { name: 'item' }],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest identifiers for "SELECT testValue.| FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS testIndex, testValue"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testValue.',
        afterCursor:
          ' FROM testTable LATERAL VIEW posexplode(testArray) explodedTable AS testIndex, testValue',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'testArray' }, { name: 'item' }],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT boo.| FROM customers LATERAL VIEW explode(baa) boo;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT boo.',
        afterCursor: ' FROM customers LATERAL VIEW explode(baa) boo;',
        expectedResult: {
          lowerCase: false,
          suggestIdentifiers: [
            { name: 'key', type: 'alias' },
            { name: 'value', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT boo.| FROM customers LATERAL VIEW posexplode(baa) boo;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT boo.',
        afterCursor: ' FROM customers LATERAL VIEW posexplode(baa) boo;',
        expectedResult: {
          lowerCase: false,
          suggestIdentifiers: [
            { name: 'pos', type: 'alias' },
            { name: 'val', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT testMapValue.| FROM testTable LATERAL VIEW explode(testMap) bla AS testMapKey, testMapValue"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testMapValue.',
        afterCursor: ' FROM testTable LATERAL VIEW explode(testMap) AS testMapKey, testMapValue',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'testMap' }, { name: 'value' }],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT explodedMap.testMapValue.| FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT explodedMap.testMapValue.',
        afterCursor:
          ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'testMap' }, { name: 'value' }],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest identifier for "SELECT explodedMap.| FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT explodedMap.',
        afterCursor:
          ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue',
        expectedResult: {
          lowerCase: false,
          suggestIdentifiers: [
            { name: 'testMapKey', type: 'alias' },
            { name: 'testMapValue', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest identifiers for "SELECT | FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          ' FROM testTable LATERAL VIEW explode(testMap) explodedMap AS testMapKey, testMapValue',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestIdentifiers: [
            { name: 'explodedMap.', type: 'alias' },
            { name: 'testMapKey', type: 'alias' },
            { name: 'testMapValue', type: 'alias' }
          ],
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });
  });

  describe('Struct Completion', () => {
    it('should suggest columns for "SELECT columnA.fieldC.| FROM database_two.testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT columnA.fieldC.',
        afterCursor: ' FROM database_two.testTable',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            identifierChain: [{ name: 'columnA' }, { name: 'fieldC' }],
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          },
          suggestKeywords: ['*'] // TODO: Verify that this is true
        }
      });
    });
  });

  describe('Value Expression Completion', () => {
    it("should suggest functions for \"SELECT 'boo \\' baa' = |\"", () => {
      assertAutoComplete({
        beforeCursor: "SELECT 'boo \\' baa' = ",
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['STRING'] }
        }
      });
    });

    it('should suggest functions for "SELECT "boo \\" baa" = |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT "boo \\" baa" = ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['STRING'] }
        }
      });
    });

    it('should suggest identifiers for "SELECT 1 = | OR false FROM tableOne boo, tableTwo baa;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT 1 = ',
        afterCursor: ' OR false FROM tableOne boo, tableTwo baa;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'select',
            types: ['NUMBER'],
            tables: [
              { identifierChain: [{ name: 'tableOne' }], alias: 'boo' },
              { identifierChain: [{ name: 'tableTwo' }], alias: 'baa' }
            ]
          },
          suggestIdentifiers: [
            { name: 'boo.', type: 'alias' },
            { name: 'baa.', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'where',
            types: ['T'],
            tables: [{ identifierChain: [{ name: 'tbl2' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE id = atbl2.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'where',
            types: ['T'],
            tables: [{ identifierChain: [{ name: 'tbl2' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE cos(1) = atbl2.bla.|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM tbl1, tbl2 atbl2, tbl3 WHERE cos(1) = atbl2.bla.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'where',
            types: ['UDFREF'],
            udfRef: 'cos',
            identifierChain: [{ name: 'bla' }],
            tables: [{ identifierChain: [{ name: 'tbl2' }] }]
          }
        }
      });
    });

    it('should suggest values for "SELECT * FROM testTable WHERE id = |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE id =',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE -|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE -',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT -| FROM testTable WHERE id = 1;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT -',
        afterCursor: ' FROM testTable WHERE id = 1;',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'select',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT 1 < | FROM testTable WHERE id = 1;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT 1 < ',
        afterCursor: ' FROM testTable WHERE id = 1;',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'select',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "select foo from tbl where | % 2 = 0"', () => {
      assertAutoComplete({
        beforeCursor: 'select foo from tbl where ',
        afterCursor: ' % 2 = 0',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: true,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'tbl' }] }]
          }
        }
      });
    });

    it('should suggest values for "SELECT * FROM testTable WHERE -id = |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE -id = ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
        }
      });
    });

    it('should suggest values for "SELECT * FROM testTable WHERE \'foo\' = |"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT * FROM testTable WHERE 'foo' = ",
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['STRING'] },
          suggestColumns: {
            source: 'where',
            types: ['STRING'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT cast(\'1\' AS |"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT cast('1' AS ",
        afterCursor: '',
        containsKeywords: ['BIGINT', 'DATE'],
        doesNotContainKeywords: ['REAL'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT cos(| FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT cos(',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'cos',
            position: 1
          }
        }
      });
    });

    it('should suggest columns for "SELECT ceiling(| FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ceiling(',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'ceiling',
            position: 1
          }
        }
      });
    });

    it('should suggest arg ref for "SELECT cos(1, | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT cos(1, ',
        afterCursor: ' FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestFunctions: {},
          suggestKeywords: ['CASE', 'FALSE', 'NULL', 'TRUE', 'EXISTS', 'NOT'],
          udfArgument: {
            name: 'cos',
            position: 2
          }
        }
      });
    });

    it('should suggest columns for "SELECT greatest(1, 2, a, 4, | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT greatest(1, 2, a, 4, ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'greatest',
            position: 5
          }
        }
      });
    });

    it('should suggest columns for "SELECT greatest(1, |, a, 4) FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT greatest(1, ',
        afterCursor: ', a, 4) FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'greatest',
            position: 2
          }
        }
      });
    });

    it('should suggest columns for "SELECT log(a, |) FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT log(a, ',
        afterCursor: ') FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          udfArgument: {
            name: 'log',
            position: 2
          }
        }
      });
    });

    it('should suggest columns with arg ref for "SELECT log(a, b, | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT log(a, b, ',
        afterCursor: ' FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestFunctions: {},
          suggestKeywords: ['CASE', 'FALSE', 'NULL', 'TRUE', 'EXISTS', 'NOT'],
          udfArgument: {
            name: 'log',
            position: 3
          }
        }
      });
    });

    it('should suggest columns for "SELECT cast(a AS BIGINT) = | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT cast(a AS BIGINT) = ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['BIGINT'] },
          suggestColumns: {
            source: 'select',
            types: ['BIGINT'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest typed columns for "SELECT CAST(18446744073709001000BD AS DECIMAL(38,0)) = | FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT CAST(18446744073709001000BD AS DECIMAL(38,0)) = ',
        afterCursor: ' FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['DECIMAL'] },
          suggestColumns: {
            source: 'select',
            types: ['DECIMAL'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT | > id FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' > id FROM testTable',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            source: 'select',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT * FROM testTable WHERE | = id"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE ',
        afterCursor: ' = id',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'id' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d = |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d < |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d < ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <= |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <= ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <=> |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <=> ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d <> |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d <> ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d >= |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d >= ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d > |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d > ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest values and columns for "SELECT a, b, c FROM testTable WHERE d != |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d != ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + 1 != |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + 1 != ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE bla| + 1 != 3"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE bla',
        afterCursor: ' + 1 != 3',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d + |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d + ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d - |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d - ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d * |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d * ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d / |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d / ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d % |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d % ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d | |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d | ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d & |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d & ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d ^ |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ^ ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE ~|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE ~',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE -|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE -',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'where',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    // TODO: This one causes an unrecoverable error after the cursor, we should suggest group by etc.
    it('should suggest columns for "SELECT a, b, c FROM testTable WHERE d | RLIKE \'bla bla\'"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c FROM testTable WHERE d ',
        afterCursor: " RLIKE 'bla bla'",
        containsKeywords: ['<', 'IN'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'd' }] },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE id IS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id IS ',
        afterCursor: '',
        containsKeywords: ['NOT NULL', 'NULL', 'NOT TRUE', 'TRUE', 'NOT FALSE', 'FALSE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE id IS NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id IS NOT ',
        afterCursor: '',
        containsKeywords: ['NULL', 'FALSE', 'TRUE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE id IS | NULL"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id IS ',
        afterCursor: ' NULL',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE id IS | FALSE"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id IS ',
        afterCursor: ' FALSE',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE id IS | TRUE"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id IS ',
        afterCursor: ' TRUE',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['NOT']
        }
      });
    });

    // Fails because "NOT" is missing
    xit('should suggest keywords for "SELECT * FROM foo WHERE id | LIKE \'bla bla\'"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id ',
        afterCursor: " LIKE 'bla bla'",
        containsKeywords: ['<', 'IN', 'NOT'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'id' }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM foo WHERE id LIKE |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id LIKE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['STRING'] },
          suggestColumns: {
            source: 'where',
            types: ['STRING'],
            tables: [{ identifierChain: [{ name: 'foo' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE id LIKE \'\' GROUP |"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT * FROM foo WHERE id LIKE '' GROUP ",
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: { prefix: 'BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
          suggestKeywords: ['BY']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE id LIKE (\'bla bla\') |"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT * FROM foo WHERE id LIKE ('bla bla') ",
        afterCursor: '',
        containsKeywords: ['AND'],
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
          suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
        }
      });
    });

    it('should suggest identifiers for "SELECT * FROM foo bla, bar WHERE id IS NULL AND |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo bla, bar WHERE id IS NULL AND ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestFilters: {
            tables: [
              { identifierChain: [{ name: 'foo' }], alias: 'bla' },
              { identifierChain: [{ name: 'bar' }] }
            ]
          },
          suggestColumns: {
            source: 'where',
            tables: [
              { identifierChain: [{ name: 'foo' }], alias: 'bla' },
              { identifierChain: [{ name: 'bar' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'bla.', type: 'alias' },
            { name: 'bar.', type: 'table' }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL && |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL && ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }] },
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }]
          },
          suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL OR | AND 1 + 1 > 1"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL OR ',
        afterCursor: ' AND 1 + 1 > 1',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }] },
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }]
          },
          suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM foo AS bla WHERE id IS NULL || |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo AS bla WHERE id IS NULL || ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }] },
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bla' }]
          },
          suggestIdentifiers: [{ name: 'bla.', type: 'alias' }]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM foo bar WHERE NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo bar WHERE NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bar' }]
          },
          suggestKeywords: ['EXISTS'],
          suggestIdentifiers: [{ name: 'bar.', type: 'alias' }]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM foo bar WHERE ! |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo bar WHERE ! ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['BOOLEAN'] },
          suggestColumns: {
            source: 'where',
            types: ['BOOLEAN'],
            tables: [{ identifierChain: [{ name: 'foo' }], alias: 'bar' }]
          },
          suggestIdentifiers: [{ name: 'bar.', type: 'alias' }]
        }
      });
    });

    it('should suggest functions for "SELECT 100Y = |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT 100Y = ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] }
        }
      });
    });

    it('should suggest functions for "SELECT 100BD = |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT 100BD = ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] }
        }
      });
    });

    it('should suggest keywords for "SELECT bar FROM foo WHERE id = 1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'foo' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'foo' }] }]
          },
          suggestKeywords: [
            'GROUP BY',
            'HAVING',
            'WINDOW',
            'ORDER BY',
            'CLUSTER BY',
            'DISTRIBUTE BY',
            'SORT BY',
            'LIMIT',
            'UNION',
            '<',
            '<=',
            '<=>',
            '<>',
            '=',
            '>',
            '>=',
            'AND',
            'BETWEEN',
            'IN',
            'IS FALSE',
            'IS NOT FALSE',
            'IS NOT NULL',
            'IS NOT TRUE',
            'IS NULL',
            'IS TRUE',
            'NOT BETWEEN',
            'NOT IN',
            'OR'
          ]
        }
      });
    });
  });

  describe('Field Completion', () => {
    it('should suggest columns for "SELECT * FROM testTable WHERE |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestKeywords: ['EXISTS', 'NOT EXISTS'],
          suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE a|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE a',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestKeywords: ['EXISTS', 'NOT EXISTS'],
          suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE baa = 1 AND |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE baa = 1 AND ',
        afterCursor: '',
        containsKeywords: ['CASE', 'EXISTS', 'NOT', 'NULL'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE | AND baa = 1"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE ',
        afterCursor: ' AND baa = 1',
        containsKeywords: ['CASE', 'EXISTS', 'NOT', 'NULL'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE baa = 1 OR |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE baa = 1 OR ',
        afterCursor: '',
        containsKeywords: ['CASE', 'EXISTS', 'NOT', 'NULL'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE | OR baa = 1"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE ',
        afterCursor: ' OR baa = 1',
        containsKeywords: ['CASE', 'EXISTS', 'NOT', 'NULL'],
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable WHERE NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE NOT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestKeywords: ['EXISTS']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable WHERE foo = \'bar\' |"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT * FROM testTable WHERE foo = 'bar' ",
        afterCursor: '',
        containsKeywords: ['AND', '<'],
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT a, b, c, d, e FROM tableOne WHERE c >= 9998 an|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, c, d, e FROM tableOne WHERE c >= 9998 an',
        afterCursor: '',
        containsKeywords: ['AND', '='],
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'tableOne' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'tableOne' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE foo = \'bar\' AND |"', () => {
      assertAutoComplete({
        beforeCursor: "SELECT * FROM testTable WHERE foo = 'bar' AND ",
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestFilters: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestColumns: {
            source: 'where',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a, b, \\nc,\\nd, |\\ng,\\nf\\nFROM testTable WHERE a > 1 AND b = \'b\' ORDER BY c;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a, b, \nc,\nd, ',
        afterCursor: "\ng,\nf\nFROM testTable WHERE a > 1 AND b = 'b' ORDER BY c;",
        containsKeywords: ['*', 'CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT a,b, | c FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a,b, ',
        afterCursor: ' c FROM testTable',
        containsKeywords: ['*'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT | a, b, c FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' a, b, c FROM testTable',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT a |, b, c FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT a ',
        afterCursor: ', b, c FROM testTable',
        containsKeywords: ['AS', '>'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable WHERE | = \'bar\' AND "', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE ',
        afterCursor: " = 'bar' AND ",
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['STRING'] },
          suggestColumns: {
            source: 'where',
            types: ['STRING'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable WHERE a |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE a ',
        afterCursor: '',
        containsKeywords: ['BETWEEN', 'NOT BETWEEN'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable WHERE a NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE a NOT ',
        afterCursor: '',
        containsKeywords: ['BETWEEN', 'EXISTS', 'IN', 'LIKE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest values for "SELECT * FROM testTable WHERE a BETWEEN |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE a BETWEEN ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable WHERE a OR NOT EXISTS (|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable WHERE a OR NOT EXISTS (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest columns for "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.|"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM testTable1 t1 JOIN testTable2 t2 ON t1.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.|"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT t1.testTableColumn1, t2.testTableColumn3 FROM database_two.testTable1 t1 JOIN testTable2 t2 ON t1.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: {
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable1' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT testTable.| FROM testTable"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testTable.',
        afterCursor: ' FROM testTable',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['*'],
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns "SELECT tt.| FROM testTable tt"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT tt.',
        afterCursor: ' FROM testTable tt',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['*'],
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT tt.| FROM database_two.testTable tt"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT tt.',
        afterCursor: ' FROM database_two.testTable tt',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['*'],
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT tta.| FROM testTableA tta, testTableB ttb"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT tta.',
        afterCursor: ' FROM testTableA tta, testTableB ttb',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['*'],
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTableA' }] }]
          }
        }
      });
      assertAutoComplete({
        beforeCursor: 'SELECT ttb.',
        afterCursor: ' FROM testTableA tta, testTableB ttb',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['*'],
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'testTableB' }] }]
          }
        }
      });
    });
  });

  describe('ORDER BY Clause', () => {
    it('should suggest keywords for "SELECT * FROM testTable GROUP BY a | LIMIT 10"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable GROUP BY a ',
        afterCursor: ' LIMIT 10',
        doesNotContainKeywords: ['LIMIT'],
        containsKeywords: ['ORDER BY'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          colRef: { identifierChain: [{ name: 'testTable' }, { name: 'a' }] }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable ORDER |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable ORDER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY'],
          suggestOrderBys: { prefix: 'BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable ORDER BY |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable ORDER BY ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'order by',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestOrderBys: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          suggestColumns: {
            source: 'order by',
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          },
          suggestFunctions: {},
          suggestAnalyticFunctions: true,
          suggestOrderBys: {
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          },
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo, |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo, ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'order by',
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo + baa ASC, |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo + baa ASC, ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'order by',
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM database_two.testTable ORDER BY foo ASC, |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ASC, ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAnalyticFunctions: true,
          suggestColumns: {
            source: 'order by',
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |, bla"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
        afterCursor: ', bla',
        containsKeywords: ['ASC', 'DESC', 'NULLS FIRST', 'NULLS LAST'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar NULLS |, bla"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar NULLS ',
        afterCursor: ', bla',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['FIRST', 'LAST']
        }
      });
    });
  });

  describe('CLUSTER BY, DISTRIBUTE BY and SORT BY', () => {
    it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC ',
        afterCursor: '',
        containsKeywords: ['CLUSTER BY', 'DISTRIBUTE BY', 'LIMIT'],
        doesNotContainKeywords: ['SORT BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC CLUSTER BY a |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC CLUSTER BY a ',
        afterCursor: '',
        containsKeywords: ['LIMIT'],
        doesNotContainKeywords: ['DISTRIBUTE BY', 'SORT BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC DISTRIBUTE BY a |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC DISTRIBUTE BY a ',
        afterCursor: '',
        containsKeywords: ['SORT BY', 'LIMIT'],
        doesNotContainKeywords: ['CLUSTER BY', 'DISTRIBUTE BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM t1 ORDER BY foo ASC SORT BY a DESC |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 ORDER BY foo ASC SORT BY a DESC ',
        afterCursor: '',
        containsKeywords: ['LIMIT'],
        doesNotContainKeywords: ['CLUSTER BY', 'DISTRIBUTE BY', 'NULLS FIRST', 'SORT BY'],
        expectedResult: {
          lowerCase: false
        }
      });
    });
  });

  describe('GROUP BY Clause', () => {
    it('should suggest keywords for "SELECT * FROM testTable GROUP |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable GROUP ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BY'],
          suggestGroupBys: { prefix: 'BY', tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM testTable GROUP BY |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable GROUP BY ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'group by',
            tables: [{ identifierChain: [{ name: 'testTable' }] }]
          },
          suggestGroupBys: { tables: [{ identifierChain: [{ name: 'testTable' }] }] }
        }
      });
    });

    it('should suggest columns for "SELECT * FROM database_two.testTable GROUP BY |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'group by',
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          },
          suggestGroupBys: {
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          }
        }
      });
    });

    describe('GROUPING SETS', () => {
      it('should handle "SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH CUBE;"', () => {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH CUBE;',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH ROLLUP;"', () => {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b WITH ROLLUP;',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should handle "SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b GROUPING SETS ( (a, b), a, b, ( ) );"', () => {
        assertAutoComplete({
          beforeCursor:
            'SELECT a, b, SUM( c ) FROM tab1 GROUP BY a, b GROUPING SETS ( (a, b), a, b, ( ) );',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM database_two.testTable GROUP BY a, b |"', () => {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b ',
          afterCursor: '',
          containsKeywords: ['GROUPING SETS', 'WITH CUBE', 'WITH ROLLUP', '<'],
          containsColRefKeywords: true,
          expectedResult: {
            lowerCase: false,
            suggestOrderBys: {
              prefix: 'ORDER BY',
              tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
            },
            colRef: {
              identifierChain: [{ name: 'database_two' }, { name: 'testTable' }, { name: 'b' }]
            }
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM database_two.testTable GROUP BY a, b WITH |"', () => {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b WITH ',
          afterCursor: '',
          containsKeywords: ['CUBE', 'ROLLUP'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "SELECT * FROM database_two.testTable GROUP BY a, b GROUPING |"', () => {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b GROUPING ',
          afterCursor: '',
          containsKeywords: ['SETS'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest columns for "SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS (|"', () => {
        assertAutoComplete({
          beforeCursor: 'SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS (',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              source: 'group by',
              tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
            }
          }
        });
      });

      it('should suggest columns for "SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS ((a, b), |"', () => {
        assertAutoComplete({
          beforeCursor:
            'SELECT * FROM database_two.testTable GROUP BY a, b GROUPING SETS ((a, b), ',
          afterCursor: '',
          expectedResult: {
            lowerCase: false,
            suggestColumns: {
              source: 'group by',
              tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
            }
          }
        });
      });

      it('should suggest keywords for "SELECT a, b, SUM(c) FROM tab1 GROUP BY a, b GROUPING SETS (a,b) |"', () => {
        assertAutoComplete({
          beforeCursor: 'SELECT a, b, SUM(c) FROM tab1 GROUP BY a, b GROUPING SETS (a,b) ',
          afterCursor: '',
          containsKeywords: ['LIMIT'],
          expectedResult: {
            lowerCase: false,
            suggestOrderBys: {
              prefix: 'ORDER BY',
              tables: [{ identifierChain: [{ name: 'tab1' }] }]
            }
          }
        });
      });
    });
  });

  describe('HAVING clause', () => {
    it('should suggest identifiers for "SELECT COUNT(*) AS boo FROM testTable GROUP BY baa HAVING |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable GROUP BY baa HAVING ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable' }] }] },
          suggestColumnAliases: [{ name: 'boo', udfRef: 'count', types: ['UDFREF'] }]
        }
      });
    });
  });

  describe('LIMIT clause', () => {
    it('should handle "SELECT * FROM testTable LIMIT 5,6; |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable LIMIT 5,6; ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest values for "SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT COUNT(*) AS boo FROM testTable GROUP BY baa LIMIT ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['10', '100', '1000', '10000', '5000']
        }
      });
    });
  });

  describe('TABLESAMPLE', () => {
    it('should handle "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 32 ON baa) baa JOIN bla;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 32 ON baa) baa JOIN bla;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT * FROM boo TABLESAMPLE (0.1 PERCENT) baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (0.1 PERCENT) baa;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT * FROM boo TABLESAMPLE (5 ROWS) baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (5 ROWS) baa;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT * FROM boo TABLESAMPLE (205B) baa;|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (205B) baa;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['TABLESAMPLE', 'AS'],
        expectedResult: {
          lowerCase: false,
          suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'boo' }] }] },
          suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'boo' }] }] },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'boo' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'boo' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo |, baa', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo ',
        afterCursor: ', baa',
        containsKeywords: ['TABLESAMPLE', 'AS'],
        expectedResult: {
          lowerCase: false,
          suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'boo' }] }] },
          suggestFilters: { prefix: 'WHERE', tables: [{ identifierChain: [{ name: 'boo' }] }] },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'boo' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'boo' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (|', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['BUCKET']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (0.1 |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (0.1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PERCENT']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (1 |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['PERCENT', 'ROWS']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OUT OF']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OF']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ON']
        }
      });
    });

    it('should suggest columns for "SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 ON |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM boo TABLESAMPLE (BUCKET 1 OUT OF 16 ON ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: { tables: [{ identifierChain: [{ name: 'boo' }] }] }
        }
      });
    });
  });

  describe('UNION clause', () => {
    // TODO: Fix locations
    xit('should handle "SELECT * FROM (SELECT x FROM few_ints UNION ALL SELECT x FROM few_ints) AS t1 ORDER BY x;|', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT * FROM (SELECT x FROM few_ints UNION ALL SELECT x FROM few_ints) AS t1 ORDER BY x;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT key FROM (SELECT key FROM src ORDER BY key LIMIT 10)subq1 UNION SELECT key FROM (SELECT key FROM src1 ORDER BY key LIMIT 10)subq2;|', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT key FROM (SELECT key FROM src ORDER BY key LIMIT 10)subq1 UNION SELECT key FROM (SELECT key FROM src1 ORDER BY key LIMIT 10)subq2;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT * FROM t1 UNION DISTINCT SELECT * FROM t2;|', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 UNION DISTINCT SELECT * FROM t2;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "SELECT * FROM t1 UNION SELECT * FROM t2;|', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 UNION SELECT * FROM t2;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM t1 UNION |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 UNION ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ALL', 'DISTINCT', 'SELECT']
        }
      });
    });

    it('should suggest tables for "SELECT * FROM t1 UNION ALL SELECT |', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM t1 UNION ALL SELECT ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });
  });

  describe('WITH clause', () => {
    it('should handle "WITH q1 AS ( SELECT key FROM src WHERE something) SELECT * FROM q1;|', () => {
      assertAutoComplete({
        beforeCursor: 'WITH q1 AS ( SELECT key FROM src WHERE something) SELECT * FROM q1;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "WITH q1 AS (SELECT * FROM src WHERE something), q2 AS (SELECT * FROM src s2 WHERE something) SELECT * FROM q1 UNION ALL SELECT * FROM q2;|', () => {
      assertAutoComplete({
        beforeCursor:
          'WITH q1 AS (SELECT * FROM src WHERE something), q2 AS (SELECT * FROM src s2 WHERE something) SELECT * FROM q1 UNION ALL SELECT * FROM q2;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should handle "WITH t1 AS (SELECT 1) (WITH t2 AS (SELECT 2) SELECT * FROM t2) UNION ALL SELECT * FROM t1;|', () => {
      assertAutoComplete({
        beforeCursor:
          'WITH t1 AS (SELECT 1) (WITH t2 AS (SELECT 2) SELECT * FROM t2) UNION ALL SELECT * FROM t1;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "WITH t1 |', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['AS']
        }
      });
    });

    it('should suggest keywords for "WITH t1 AS (|', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 AS (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "WITH t1 AS (SELECT * FROM boo) |', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 AS (SELECT * FROM boo) ',
        afterCursor: '',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest identifiers for "WITH t1 AS (SELECT * FROM FOO) SELECT |', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 AS (SELECT * FROM FOO) SELECT ',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: { prependQuestionMark: true, prependFrom: true },
          suggestDatabases: { prependQuestionMark: true, prependFrom: true, appendDot: true },
          suggestCommonTableExpressions: [
            { name: 't1', prependFrom: true, prependQuestionMark: true }
          ],
          commonTableExpressions: [
            { alias: 't1', columns: [{ tables: [{ identifierChain: [{ name: 'FOO' }] }] }] }
          ]
        }
      });
    });

    it('should suggest identifiers for "WITH t1 AS (SELECT * FROM FOO), t2 AS (SELECT |', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 AS (SELECT * FROM FOO), t2 AS (SELECT ',
        afterCursor: '',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: { prependQuestionMark: true, prependFrom: true },
          suggestDatabases: { prependQuestionMark: true, prependFrom: true, appendDot: true },
          lowerCase: false,
          suggestCommonTableExpressions: [
            { name: 't1', prependFrom: true, prependQuestionMark: true }
          ],
          commonTableExpressions: [
            { alias: 't1', columns: [{ tables: [{ identifierChain: [{ name: 'FOO' }] }] }] }
          ]
        }
      });
    });

    it('should suggest identifiers for "WITH t1 AS (SELECT id FROM foo), t2 AS (SELECT | FROM t1)', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 AS (SELECT id FROM foo), t2 AS (SELECT ',
        afterCursor: ' FROM t1)',
        noErrors: true,
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ cte: 't1' }] }] },
          commonTableExpressions: [
            {
              alias: 't1',
              columns: [{ identifierChain: [{ name: 'foo' }, { name: 'id' }], type: 'COLREF' }]
            }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest identifiers for "WITH t1 AS (SELECT * FROM FOO) SELECT * FROM |', () => {
      assertAutoComplete({
        beforeCursor: 'WITH t1 AS (SELECT * FROM FOO) SELECT * FROM ',
        afterCursor: '',
        noErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          suggestCommonTableExpressions: [{ name: 't1' }],
          commonTableExpressions: [
            { alias: 't1', columns: [{ tables: [{ identifierChain: [{ name: 'FOO' }] }] }] }
          ]
        }
      });
    });

    it('should suggest keywords for "with s as (select * from foo join bar) select * from |"', () => {
      assertAutoComplete({
        beforeCursor: 'with s as (select * from foo join bar) select * from ',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          commonTableExpressions: [
            {
              columns: [
                {
                  tables: [
                    { identifierChain: [{ name: 'foo' }] },
                    { identifierChain: [{ name: 'bar' }] }
                  ]
                }
              ],
              alias: 's'
            }
          ],
          suggestCommonTableExpressions: [{ name: 's' }]
        }
      });
    });

    it('should suggest keywords for "with s as (select * from foo join bar) select * from |;', () => {
      assertAutoComplete({
        beforeCursor: 'with s as (select * from foo join bar) select * from ',
        afterCursor: ';',
        expectedResult: {
          lowerCase: true,
          suggestTables: {},
          suggestDatabases: { appendDot: true },
          commonTableExpressions: [
            {
              columns: [
                {
                  tables: [
                    { identifierChain: [{ name: 'foo' }] },
                    { identifierChain: [{ name: 'bar' }] }
                  ]
                }
              ],
              alias: 's'
            }
          ],
          suggestCommonTableExpressions: [{ name: 's' }]
        }
      });
    });
  });

  describe('Joins', () => {
    it('should suggest keywords for "SELECT * FROM testTable1 LEFT OUTER |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 LEFT OUTER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN']
        }
      });
    });

    it('should suggest tables for "SELECT * FROM testTable1 JOIN db1.|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 JOIN db1.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db1' }] }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM testTable1 JOIN db1.| JOIN foo"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 JOIN db1.',
        afterCursor: ' JOIN foo',
        expectedResult: {
          lowerCase: false,
          suggestTables: { identifierChain: [{ name: 'db1' }] }
        }
      });
    });

    it('should suggest join conditions for "SELECT testTable1.* FROM testTable1 JOIN testTable2 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ',
        afterCursor: '',
        containsKeywords: ['ON'],
        expectedResult: {
          lowerCase: false,
          suggestJoinConditions: {
            prependOn: true,
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestFilters: {
            prefix: 'WHERE',
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          }
        }
      });
    });

    it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestFunctions: {},
          suggestJoinConditions: {
            prependOn: false,
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'testTable1.', type: 'table' },
            { name: 'testTable2.', type: 'table' }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'testTable1.', type: 'table' },
            { name: 'testTable2.', type: 'table' }
          ]
        }
      });
    });

    it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND |"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'testTable1.', type: 'table' },
            { name: 'testTable2.', type: 'table' }
          ]
        }
      });
    });

    it('should suggest tables for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (| AND testTable1.testColumn1 = testTable2.testColumn3"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (',
        afterCursor: ' AND testTable1.testColumn1 = testTable2.testColumn3',
        containsKeywords: ['CASE'],
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 109 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 20 }
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 18 },
              identifierChain: [{ name: 'testTable1' }]
            },
            {
              type: 'asterisk',
              location: { first_line: 1, last_line: 1, first_column: 19, last_column: 20 },
              tables: [{ identifierChain: [{ name: 'testTable1' }] }]
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 26, last_column: 36 },
              identifierChain: [{ name: 'testTable1' }]
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 42, last_column: 52 },
              identifierChain: [{ name: 'testTable2' }]
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 62, last_column: 72 },
              identifierChain: [{ name: 'testTable1' }]
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 73, last_column: 84 },
              identifierChain: [{ name: 'testColumn1' }],
              tables: [{ identifierChain: [{ name: 'testTable1' }] }],
              qualified: true
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 87, last_column: 97 },
              identifierChain: [{ name: 'testTable2' }]
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 98, last_column: 109 },
              identifierChain: [{ name: 'testColumn3' }],
              tables: [{ identifierChain: [{ name: 'testTable2' }] }],
              qualified: true
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 109, last_column: 109 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 109, last_column: 109 }
            }
          ],
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'testTable1.', type: 'table' },
            { name: 'testTable2.', type: 'table' }
          ],
          suggestFunctions: {},
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable2.',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable2' }] }] }
        }
      });
    });

    it('should suggest columns for "select * from testTable1 cross join testTable2 on testTable1.|"', () => {
      assertAutoComplete({
        beforeCursor: 'select * from testTable1 cross join testTable2 on testTable1.',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }] }
        }
      });
    });

    it('should suggest identifiers for "select * from testTable1 join db.testTable2 on |"', () => {
      assertAutoComplete({
        beforeCursor: 'select * from testTable1 join db.testTable2 on ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: true,
          suggestFunctions: {},
          suggestJoinConditions: {
            prependOn: false,
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'db' }, { name: 'testTable2' }] }
            ]
          },
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'db' }, { name: 'testTable2' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'testTable1.', type: 'table' },
            { name: 'testTable2.', type: 'table' }
          ]
        }
      });
    });

    it('should suggest identifiers for "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = |"', () => {
      assertAutoComplete({
        beforeCursor: 'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          suggestValues: {},
          colRef: { identifierChain: [{ name: 'testTable1' }, { name: 'testColumn1' }] },
          suggestFunctions: { types: ['COLREF'] },
          suggestColumns: {
            types: ['COLREF'],
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'testTable1.', type: 'table' },
            { name: 'testTable2.', type: 'table' }
          ],
          lowerCase: true
        }
      });
    });

    it('should suggest columns for "select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.|"', () => {
      assertAutoComplete({
        beforeCursor:
          'select * from testTable1 JOIN testTable2 on (testTable1.testColumn1 = testTable2.',
        afterCursor: '',
        ignoreErrors: true,
        expectedResult: {
          lowerCase: true,
          colRef: { identifierChain: [{ name: 'testTable1' }, { name: 'testColumn1' }] },
          suggestColumns: {
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'testTable2' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.|"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT testTable1.* FROM testTable1 JOIN testTable2 ON (testTable1.testColumn1 = testTable2.testColumn3 AND testTable1.',
        afterCursor: '',
        ignoreErrors: true,
        expectedResult: {
          lowerCase: false,
          suggestColumns: { tables: [{ identifierChain: [{ name: 'testTable1' }] }] }
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla = t2.bla | JOIN table3"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla = t2.bla ',
        afterCursor: ' JOIN table3',
        containsKeywords: [
          'AND',
          '=',
          'IN',
          'FULL',
          'FULL OUTER',
          'LEFT',
          'LEFT OUTER',
          'RIGHT',
          'RIGHT OUTER'
        ],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla | JOIN table3"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 ON t1.bla ',
        afterCursor: ' JOIN table3',
        containsKeywords: ['=', 'LEFT OUTER'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'table1' }, { name: 'bla' }] }
        }
      });
    });

    it('should suggest joins for "SELECT * FROM testTable1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 ',
        afterCursor: '',
        containsKeywords: ['JOIN'],
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: true,
            tables: [{ identifierChain: [{ name: 'testTable1' }] }]
          },
          suggestFilters: {
            prefix: 'WHERE',
            tables: [{ identifierChain: [{ name: 'testTable1' }] }]
          },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'testTable1' }] }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'testTable1' }] }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 ',
        afterCursor: '',
        containsKeywords: ['LEFT SEMI JOIN', 'CROSS JOIN'], // Tested in full above
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: true,
            tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]
          },
          suggestFilters: {
            prefix: 'WHERE',
            tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]
          },
          suggestGroupBys: {
            prefix: 'GROUP BY',
            tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]
          },
          suggestOrderBys: {
            prefix: 'ORDER BY',
            tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]
          }
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable1 INNER |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 INNER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable1 FULL |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 FULL ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN', 'OUTER JOIN']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable1 LEFT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 LEFT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN', 'OUTER JOIN', 'SEMI JOIN']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable1 RIGHT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 RIGHT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN', 'OUTER JOIN']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable1 CROSS |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 CROSS ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN']
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 ',
        afterCursor: ' JOIN',
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: true,
            tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]
          },
          suggestKeywords: [
            'LATERAL VIEW',
            'CROSS',
            'FULL',
            'FULL OUTER',
            'INNER',
            'LEFT',
            'LEFT OUTER',
            'LEFT SEMI',
            'RIGHT',
            'RIGHT OUTER'
          ]
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 FULL | JOIN"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 FULL ',
        afterCursor: ' JOIN',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OUTER']
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 LEFT | JOIN"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT ',
        afterCursor: ' JOIN',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OUTER', 'SEMI']
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 RIGHT | JOIN"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 RIGHT ',
        afterCursor: ' JOIN',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['OUTER']
        }
      });
    });

    it('should suggest identifiers for "SELECT t1.* FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (| AND t1.c1 = t2.c2"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT t1.* FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (',
        afterCursor: ' AND t1.c1 = t2.c2',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            tables: [
              { identifierChain: [{ name: 'table1' }], alias: 't1' },
              { identifierChain: [{ name: 'table2' }] },
              { identifierChain: [{ name: 'table3' }] },
              { identifierChain: [{ name: 'table4' }], alias: 't4' }
            ]
          },
          suggestIdentifiers: [
            { name: 't1.', type: 'alias' },
            { name: 'table2.', type: 'table' },
            { name: 'table3.', type: 'table' },
            { name: 't4.', type: 'alias' }
          ]
        }
      });
    });

    it('should suggest tables for "SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab| CROSS JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 LEFT OUTER JOIN tab',
        afterCursor: ' CROSS JOIN table3 JOIN table4 t4 ON (t1.c1 = t2.c2',
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: false,
            joinType: 'LEFT OUTER JOIN',
            tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]
          },
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });
  });

  describe('SubQueries in WHERE Clause', () => {
    it('should suggest keywords for "SELECT * FROM foo WHERE bar NOT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE bar NOT ',
        afterCursor: '',
        containsKeywords: ['IN'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM foo WHERE bar IN (|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE bar IN (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT'],
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'foo' }] }]
          },
          colRef: { identifierChain: [{ name: 'foo' }, { name: 'bar' }] }
        }
      });
    });

    it('should suggest keywords for "select * from foo, bar where bar.bla in (|"', () => {
      assertAutoComplete({
        beforeCursor: 'select * from foo, bar where bar.bla in (',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['SELECT'],
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'bar' }] }]
          },
          suggestIdentifiers: [
            { name: 'foo.', type: 'table' },
            { name: 'bar.', type: 'table' }
          ],
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bla' }] }
        }
      });
    });

    it('should suggest values for "select * from foo, bar where bar.bla in (\'a\', |"', () => {
      assertAutoComplete({
        beforeCursor: "select * from foo, bar where bar.bla in ('a', ",
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: true,
          suggestFunctions: { types: ['COLREF'] },
          suggestValues: {},
          suggestColumns: {
            source: 'where',
            types: ['COLREF'],
            tables: [{ identifierChain: [{ name: 'foo' }] }, { identifierChain: [{ name: 'bar' }] }]
          },
          suggestIdentifiers: [
            { name: 'foo.', type: 'table' },
            { name: 'bar.', type: 'table' }
          ],
          colRef: { identifierChain: [{ name: 'bar' }, { name: 'bla' }] }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM foo WHERE bar IN (SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT ',
        afterCursor: '',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest tables for "SELECT * FROM bar WHERE foo NOT IN (SELECT |)"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM bar WHERE foo NOT IN (SELECT ',
        afterCursor: ')',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });
  });

  describe('SubQueries in FROM Clause', () => {
    it('should suggest keywords for "SELECT * FROM (|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM (',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "select * from (|"', () => {
      assertAutoComplete({
        beforeCursor: 'select * from (',
        afterCursor: '',
        expectedResult: {
          lowerCase: true,
          suggestKeywords: ['SELECT']
        }
      });
    });

    it('should suggest keywords for "select foo.* from (|) foo"', () => {
      assertAutoComplete({
        beforeCursor: 'select foo.* from (',
        afterCursor: ') foo',
        containsKeywords: ['SELECT'],
        expectedResult: {
          lowerCase: true
        }
      });
    });

    it('should suggest tables for "SELECT * FROM (SELECT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM (SELECT ',
        afterCursor: '',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    // TODO: In this case the WHERE clause exists but isn't completely defined both for the query and the subquery
    it('should suggest columns for "SELECT "contains an even number" FROM t1, t2 AS ta2 WHERE EXISTS (SELECT t3.foo FROM t3 WHERE | % 2 = 0"', () => {
      assertAutoComplete({
        beforeCursor:
          'SELECT "contains an even number" FROM t1, t2 AS ta2 WHERE EXISTS (SELECT t3.foo FROM t3 WHERE ',
        afterCursor: ' % 2 = 0',
        containsKeywords: ['CASE'],
        expectedResult: {
          suggestColumns: {
            types: ['NUMBER'],
            source: 'where',
            tables: [
              { identifierChain: [{ name: 't1' }] },
              { identifierChain: [{ name: 't2' }], alias: 'ta2' },
              { identifierChain: [{ name: 't3' }] }
            ]
          },
          suggestFunctions: { types: ['NUMBER'] },
          suggestIdentifiers: [
            { name: 't1.', type: 'table' },
            { name: 'ta2.', type: 'alias' },
            { name: 't3.', type: 'table' }
          ],
          lowerCase: false,
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 103 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 33 }
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 39, last_column: 41 },
              identifierChain: [{ name: 't1' }]
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 43, last_column: 45 },
              identifierChain: [{ name: 't2' }]
            },
            {
              type: 'alias',
              source: 'table',
              alias: 'ta2',
              location: { first_line: 1, last_line: 1, first_column: 49, last_column: 52 },
              identifierChain: [{ name: 't2' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 52, last_column: 52 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 52, last_column: 52 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 74, last_column: 80 },
              subquery: true
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 74, last_column: 76 },
              identifierChain: [{ name: 't3' }]
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 77, last_column: 80 },
              identifierChain: [{ name: 'foo' }],
              tables: [{ identifierChain: [{ name: 't3' }] }],
              qualified: true
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 86, last_column: 88 },
              identifierChain: [{ name: 't3' }]
            },
            {
              type: 'whereClause',
              subquery: true,
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 88, last_column: 88 }
            },
            {
              type: 'limitClause',
              subquery: true,
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 88, last_column: 88 }
            }
          ]
        }
      });
    });

    it('should suggest identifiers for "SELECT | FROM testTable tt, (SELECT bla FROM abc WHERE foo > 1) bar"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM testTable tt, (SELECT bla FROM abc WHERE foo > 1) bar',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 67 }
            },
            {
              type: 'selectList',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 7, last_column: 7 }
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 14, last_column: 23 },
              identifierChain: [{ name: 'testTable' }]
            },
            {
              type: 'alias',
              source: 'table',
              alias: 'tt',
              location: { first_line: 1, last_line: 1, first_column: 24, last_column: 26 },
              identifierChain: [{ name: 'testTable' }]
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 36, last_column: 39 },
              subquery: true
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 36, last_column: 39 },
              identifierChain: [{ name: 'bla' }],
              tables: [{ identifierChain: [{ name: 'abc' }] }],
              qualified: false
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 45, last_column: 48 },
              identifierChain: [{ name: 'abc' }]
            },
            {
              type: 'whereClause',
              subquery: true,
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 49, last_column: 62 }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 55, last_column: 58 },
              identifierChain: [{ name: 'foo' }],
              tables: [{ identifierChain: [{ name: 'abc' }] }],
              qualified: false
            },
            {
              type: 'limitClause',
              subquery: true,
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 62, last_column: 62 }
            },
            {
              type: 'alias',
              source: 'subquery',
              alias: 'bar',
              location: { first_line: 1, last_line: 1, first_column: 64, last_column: 67 }
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 67, last_column: 67 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 67, last_column: 67 }
            }
          ],
          suggestAggregateFunctions: {
            tables: [{ identifierChain: [{ name: 'testTable' }], alias: 'tt' }]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [
              { identifierChain: [{ name: 'testTable' }], alias: 'tt' },
              { identifierChain: [{ subQuery: 'bar' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'tt.', type: 'alias' },
            { name: 'bar.', type: 'sub-query' }
          ],
          subQueries: [
            {
              alias: 'bar',
              columns: [{ identifierChain: [{ name: 'abc' }, { name: 'bla' }], type: 'COLREF' }]
            }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "select | from (select id i, name as n, bla from foo) bar"', () => {
      assertAutoComplete({
        beforeCursor: 'select ',
        afterCursor: ' from (select id i, name as n, bla from foo) bar',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ subQuery: 'bar' }] }]
          },
          subQueries: [
            {
              alias: 'bar',
              columns: [
                { alias: 'i', identifierChain: [{ name: 'foo' }, { name: 'id' }], type: 'COLREF' },
                {
                  alias: 'n',
                  identifierChain: [{ name: 'foo' }, { name: 'name' }],
                  type: 'COLREF'
                },
                { identifierChain: [{ name: 'foo' }, { name: 'bla' }], type: 'COLREF' }
              ]
            }
          ],
          suggestIdentifiers: [{ name: 'bar.', type: 'sub-query' }],
          lowerCase: true
        }
      });
    });

    it('should suggest sub-query columns for "SELECT bar.| FROM (SELECT col1, col2, (col3 + 1) col3alias FROM foo) bar"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bar.',
        afterCursor: ' FROM (SELECT col1, col2, (col3 + 1) col3alias FROM foo) bar',
        expectedResult: {
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ subQuery: 'bar' }] }]
          },
          suggestKeywords: ['*'],
          lowerCase: false,
          subQueries: [
            {
              alias: 'bar',
              columns: [
                { identifierChain: [{ name: 'foo' }, { name: 'col1' }], type: 'COLREF' },
                { identifierChain: [{ name: 'foo' }, { name: 'col2' }], type: 'COLREF' },
                { alias: 'col3alias', type: 'NUMBER' }
              ]
            }
          ]
        }
      });
    });

    it('should suggest sub-query columns for "SELECT bar.| FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bar.',
        afterCursor: ' FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar',
        expectedResult: {
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ subQuery: 'bar' }] }]
          },
          suggestKeywords: ['*'],
          subQueries: [
            {
              alias: 'boo',
              columns: [{ identifierChain: [{ name: 'foo' }, { name: 'b' }], type: 'COLREF' }]
            },
            {
              alias: 'bar',
              columns: [{ identifierChain: [{ name: 'bla' }, { name: 'a' }], type: 'COLREF' }]
            }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "SELECT * FROM (SELECT |)"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM (SELECT ',
        afterCursor: ')',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestTables: {
            prependQuestionMark: true,
            prependFrom: true
          },
          suggestDatabases: {
            prependQuestionMark: true,
            prependFrom: true,
            appendDot: true
          }
        }
      });
    });

    it('should suggest identifiers for "SELECT | FROM (SELECT * FROM tableOne) AS subQueryOne, someDb.tableTwo tAlias, tableThree, (SELECT * FROM t3 JOIN table4 t4 ON t3.id = t4.id) subQueryTwo;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          ' FROM (SELECT * FROM tableOne) AS subQueryOne, someDb.tableTwo tAlias, tableThree, (SELECT * FROM t3 JOIN table4 t4 ON t3.id = t4.id) subQueryTwo;',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: {
            tables: [
              { identifierChain: [{ name: 'someDb' }, { name: 'tableTwo' }], alias: 'tAlias' },
              { identifierChain: [{ name: 'tableThree' }] }
            ]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [
              { identifierChain: [{ subQuery: 'subQueryOne' }] },
              { identifierChain: [{ name: 'someDb' }, { name: 'tableTwo' }], alias: 'tAlias' },
              { identifierChain: [{ name: 'tableThree' }] },
              { identifierChain: [{ subQuery: 'subQueryTwo' }] }
            ]
          },
          subQueries: [
            {
              columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }],
              alias: 'subQueryOne'
            },
            {
              columns: [
                {
                  tables: [
                    { identifierChain: [{ name: 't3' }] },
                    { alias: 't4', identifierChain: [{ name: 'table4' }] }
                  ]
                }
              ],
              alias: 'subQueryTwo'
            }
          ],
          suggestIdentifiers: [
            { name: 'subQueryOne.', type: 'sub-query' },
            { name: 'tAlias.', type: 'alias' },
            { name: 'tableThree.', type: 'table' },
            { name: 'subQueryTwo.', type: 'sub-query' }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT * FROM (SELECT | FROM tableOne) subQueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subQueryTwo;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM (SELECT ',
        afterCursor:
          ' FROM tableOne) subQueryOne, someDb.tableTwo talias, (SELECT * FROM t3 JOIN t4 ON t3.id = t4.id) AS subQueryTwo;',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [{ identifierChain: [{ name: 'tableOne' }] }] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ name: 'tableOne' }] }]
          }
        }
      });
    });

    it('should suggest columns for "SELECT | FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ subQuery: 'subQueryTwo' }] }]
          },
          suggestIdentifiers: [{ name: 'subQueryTwo.', type: 'sub-query' }],
          subQueries: [
            {
              alias: 'subQueryTwo',
              columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryOne' }] }] }],
              subQueries: [
                {
                  alias: 'subQueryOne',
                  columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
                }
              ]
            }
          ],
          lowerCase: false
        }
      });
    });

    it('should suggest columns for "SELECT | FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor:
          ' FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ subQuery: 'subQueryThree' }] }]
          },
          suggestIdentifiers: [{ name: 'subQueryThree.', type: 'sub-query' }],
          subQueries: [
            {
              alias: 'subQueryThree',
              columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryTwo' }] }] }],
              subQueries: [
                {
                  alias: 'subQueryTwo',
                  columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryOne' }] }] }],
                  subQueries: [
                    {
                      alias: 'subQueryOne',
                      columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
                    }
                  ]
                }
              ]
            }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM (SELECT | FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM (SELECT ',
        afterCursor:
          ' FROM (SELECT * FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ subQuery: 'subQueryTwo' }] }]
          },
          suggestIdentifiers: [{ name: 'subQueryTwo.', type: 'sub-query' }],
          subQueries: [
            {
              alias: 'subQueryTwo',
              columns: [{ tables: [{ identifierChain: [{ subQuery: 'subQueryOne' }] }] }],
              subQueries: [
                {
                  alias: 'subQueryOne',
                  columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
                }
              ]
            }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT * FROM (SELECT * FROM (SELECT | FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM (SELECT * FROM (SELECT ',
        afterCursor: ' FROM (SELECT * FROM tableOne) subQueryOne) subQueryTwo) subQueryThree',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: { tables: [] },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [{ identifierChain: [{ subQuery: 'subQueryOne' }] }]
          },
          suggestIdentifiers: [{ name: 'subQueryOne.', type: 'sub-query' }],
          subQueries: [
            {
              alias: 'subQueryOne',
              columns: [{ tables: [{ identifierChain: [{ name: 'tableOne' }] }] }]
            }
          ]
        }
      });
    });

    it('should suggest columns for "SELECT s2.| FROM (SELECT a, bla FROM (SELECT a, b, abs(1) as bla FROM testTable) s1) s2;"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT s2.',
        afterCursor:
          ' FROM (SELECT a, bla FROM (SELECT a, b, abs(1) as bla FROM testTable) s1) s2;',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['*'],
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 's2' }] }] },
          subQueries: [
            {
              alias: 's2',
              columns: [
                { identifierChain: [{ subQuery: 's1' }, { name: 'a' }], type: 'COLREF' },
                { identifierChain: [{ subQuery: 's1' }, { name: 'bla' }], type: 'COLREF' }
              ],
              subQueries: [
                {
                  alias: 's1',
                  columns: [
                    { identifierChain: [{ name: 'testTable' }, { name: 'a' }], type: 'COLREF' },
                    { identifierChain: [{ name: 'testTable' }, { name: 'b' }], type: 'COLREF' },
                    { alias: 'bla', type: 'UDFREF', udfRef: 'abs' }
                  ]
                }
              ]
            }
          ]
        }
      });
    });
  });
});
