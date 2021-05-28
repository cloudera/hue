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

import dasksqlAutocompleteParser from '../dasksqlAutocompleteParser';

describe('dasksqlAutocompleteParser.js SELECT statements', () => {
  beforeAll(() => {
    dasksqlAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      dasksqlAutocompleteParser.parseSql(
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

  it('should suggest keywords for "SELECT * FROM testTableA tta, testTableB |"', () => {
    assertAutoComplete({
      beforeCursor: 'SELECT * FROM testTableA tta, testTableB ',
      afterCursor: '',
      expectedResult: {
        suggestJoins: {
          prependJoin: true,
          tables: [{ identifierChain: [{ name: 'testTableB' }] }]
        },
        suggestFilters: {
          prefix: 'WHERE',
          tables: [
            { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
            { identifierChain: [{ name: 'testTableB' }] }
          ]
        },
        suggestGroupBys: {
          prefix: 'GROUP BY',
          tables: [
            { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
            { identifierChain: [{ name: 'testTableB' }] }
          ]
        },
        suggestOrderBys: {
          prefix: 'ORDER BY',
          tables: [
            { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
            { identifierChain: [{ name: 'testTableB' }] }
          ]
        },
        suggestKeywords: [
          'AS',
          'WHERE',
          'GROUP BY',
          'HAVING',
          'ORDER BY',
          'LIMIT',
          'UNION',
          'FULL JOIN',
          'FULL OUTER JOIN',
          'INNER JOIN',
          'JOIN',
          'LEFT JOIN',
          'LEFT OUTER JOIN',
          'RIGHT JOIN',
          'RIGHT OUTER JOIN'
        ],
        lowerCase: false
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
  });

  describe('Select List Completion', () => {
    it('should handle "select testUdf(not id), cos(-1), sin(1+id) from autocomp_test;"', () => {
      assertAutoComplete({
        beforeCursor: 'select testUdf(not id), cos(-1), sin(1+id) from autocomp_test;',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['SELECT'],
        expectedResult: {
          locations: [
            {
              type: 'statement',
              location: { first_line: 1, last_line: 1, first_column: 1, last_column: 62 }
            },
            {
              type: 'selectList',
              missing: false,
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 43 }
            },
            {
              type: 'function',
              location: { first_line: 1, last_line: 1, first_column: 8, last_column: 14 },
              function: 'testudf'
            },
            {
              type: 'functionArgument',
              location: { first_line: 1, last_line: 1, first_column: 16, last_column: 22 },
              function: 'testudf',
              argumentPosition: 0,
              identifierChain: [{ name: 'testUdf' }],
              expression: { types: ['BOOLEAN'], text: 'not id' }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 20, last_column: 22 },
              identifierChain: [{ name: 'id' }],
              qualified: false,
              tables: [{ identifierChain: [{ name: 'autocomp_test' }] }]
            },
            {
              type: 'function',
              location: { first_line: 1, last_line: 1, first_column: 25, last_column: 27 },
              function: 'cos'
            },
            {
              type: 'functionArgument',
              location: { first_line: 1, last_line: 1, first_column: 29, last_column: 31 },
              function: 'cos',
              argumentPosition: 0,
              identifierChain: [{ name: 'cos' }],
              expression: { types: ['NUMBER'], text: '- 1' }
            },
            {
              type: 'function',
              location: { first_line: 1, last_line: 1, first_column: 34, last_column: 36 },
              function: 'sin'
            },
            {
              type: 'functionArgument',
              location: { first_line: 1, last_line: 1, first_column: 38, last_column: 42 },
              function: 'sin',
              argumentPosition: 0,
              identifierChain: [{ name: 'sin' }],
              expression: { types: ['NUMBER'], text: '1 + id' }
            },
            {
              type: 'column',
              location: { first_line: 1, last_line: 1, first_column: 40, last_column: 42 },
              identifierChain: [{ name: 'id' }],
              qualified: false,
              tables: [{ identifierChain: [{ name: 'autocomp_test' }] }]
            },
            {
              type: 'table',
              location: { first_line: 1, last_line: 1, first_column: 49, last_column: 62 },
              identifierChain: [{ name: 'autocomp_test' }]
            },
            {
              type: 'whereClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 62, last_column: 62 }
            },
            {
              type: 'limitClause',
              missing: true,
              location: { first_line: 1, last_line: 1, first_column: 62, last_column: 62 }
            }
          ],
          lowerCase: true
        }
      });
    });

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

    it('should suggest columns for "SELECT | FROM db.tbl1, db.tbl2"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT ',
        afterCursor: ' FROM db.tbl1, db.tbl2',
        containsKeywords: ['*', 'ALL', 'DISTINCT'],
        expectedResult: {
          lowerCase: false,
          suggestAggregateFunctions: {
            tables: [
              { identifierChain: [{ name: 'db' }, { name: 'tbl1' }] },
              { identifierChain: [{ name: 'db' }, { name: 'tbl2' }] }
            ]
          },
          suggestAnalyticFunctions: true,
          suggestFunctions: {},
          suggestColumns: {
            source: 'select',
            tables: [
              { identifierChain: [{ name: 'db' }, { name: 'tbl1' }] },
              { identifierChain: [{ name: 'db' }, { name: 'tbl2' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'tbl1.', type: 'table' },
            { name: 'tbl2.', type: 'table' }
          ]
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
        containsKeywords: ['INT', 'STRING'],
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

    it('should suggest columns for "SELECT <GeneralSetFunction>(|) FROM testTable"', () => {
      const aggregateFunctions = [
        { name: 'AVG', containsKeywords: ['DISTINCT'] },
        { name: 'COUNT', containsKeywords: ['*', 'DISTINCT'] },
        { name: 'STDDEV_POP', containsKeywords: ['DISTINCT'] },
        { name: 'STDDEV_SAMP', containsKeywords: ['DISTINCT'] },
        { name: 'SUM', containsKeywords: ['DISTINCT'] },
        { name: 'MAX', containsKeywords: ['DISTINCT'] },
        { name: 'MIN', containsKeywords: ['DISTINCT'] },
        { name: 'VAR_POP', containsKeywords: ['DISTINCT'] },
        { name: 'var_samp', containsKeywords: ['DISTINCT'] }
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

    it('should suggest keywords for "SELECT bar FROM foo WHERE id = 1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT bar FROM foo WHERE id = 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
          suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
          suggestKeywords: [
            'GROUP BY',
            'HAVING',
            'ORDER BY',
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

    it('should suggest keywords for "SELECT * FROM foo WHERE id <=> 1 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE id <=> 1 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
          suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
          suggestKeywords: [
            'GROUP BY',
            'HAVING',
            'ORDER BY',
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

    it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'UNION']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo + |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo + ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'order by',
            types: ['NUMBER'],
            tables: [{ identifierChain: [{ name: 'database_two' }, { name: 'testTable' }] }]
          }
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

    it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['ASC', 'DESC', 'LIMIT', 'UNION']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo DESC, bar |, bla"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo DESC, bar ',
        afterCursor: ', bla',
        containsKeywords: ['ASC', 'DESC'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM database_two.testTable ORDER BY foo LIMIT 10 |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM database_two.testTable ORDER BY foo LIMIT 10 ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['UNION']
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

    it('should suggest identifiers for "SELECT * FROM testTableA tta, testTableB GROUP BY |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'group by',
            tables: [
              { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
              { identifierChain: [{ name: 'testTableB' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'tta.', type: 'alias' },
            { name: 'testTableB.', type: 'table' }
          ],
          suggestGroupBys: {
            tables: [
              { identifierChain: [{ name: 'testTableA' }], alias: 'tta' },
              { identifierChain: [{ name: 'testTableB' }] }
            ]
          }
        }
      });
    });

    it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla, |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla, ',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'group by',
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

    it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla+|"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla+',
        afterCursor: '',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: { types: ['NUMBER'] },
          suggestColumns: {
            source: 'group by',
            types: ['NUMBER'],
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

    it('should suggest identifier for "SELECT * FROM testTableA tta, testTableB GROUP BY bla+foo, |, foo"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTableA tta, testTableB GROUP BY bla, ',
        afterCursor: ', foo',
        containsKeywords: ['CASE'],
        expectedResult: {
          lowerCase: false,
          suggestFunctions: {},
          suggestColumns: {
            source: 'group by',
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
  });

  describe('LIMIT clause', () => {
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
    it('should suggest tables for "SELECT * FROM testTable1 JOIN |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 JOIN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: false,
            joinType: 'JOIN',
            tables: [{ identifierChain: [{ name: 'testTable1' }] }]
          },
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest joins for "SELECT * FROM testTable1 JOIN testTable2 JOIN |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 JOIN testTable2 JOIN ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: false,
            joinType: 'JOIN',
            tables: [
              { identifierChain: [{ name: 'testTable1' }] },
              { identifierChain: [{ name: 'testTable2' }] }
            ]
          },
          suggestTables: {},
          suggestDatabases: { appendDot: true }
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

    it('should suggest keywords for "SELECT * FROM testTable1 FULL OUTER |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 FULL OUTER ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN']
        }
      });
    });

    it('should suggest keywords for "SELECT * FROM testTable1 LEFT |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 LEFT ',
        afterCursor: '',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['JOIN', 'OUTER JOIN']
        }
      });
    });

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

    it('should suggest keywords for "SELECT * FROM testTable1 RIGHT OUTER |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM testTable1 RIGHT OUTER ',
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
            'FULL',
            'FULL OUTER',
            'INNER',
            'LEFT',
            'LEFT OUTER',
            'RIGHT',
            'RIGHT OUTER'
          ]
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 | JOIN table2 t2 ON t1.bla = t2.bla"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 ',
        afterCursor: ' JOIN table2 t2 ON t1.bla = t2.bla',
        expectedResult: {
          lowerCase: false,
          suggestJoins: {
            prependJoin: true,
            tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]
          },
          suggestKeywords: [
            'FULL',
            'FULL OUTER',
            'INNER',
            'LEFT',
            'LEFT OUTER',
            'RIGHT',
            'RIGHT OUTER'
          ]
        }
      });
    });

    it('should suggest keywords for "SELECT t1.* FROM table1 t1 JOIN table2 t2 | JOIN table3"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT t1.* FROM table1 t1 JOIN table2 t2 ',
        afterCursor: ' JOIN table3',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: [
            'ON',
            'FULL',
            'FULL OUTER',
            'INNER',
            'LEFT',
            'LEFT OUTER',
            'RIGHT',
            'RIGHT OUTER'
          ],
          suggestJoinConditions: {
            prependOn: true,
            tables: [
              { identifierChain: [{ name: 'table1' }], alias: 't1' },
              { identifierChain: [{ name: 'table2' }], alias: 't2' }
            ]
          }
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
  });

  describe('SubQueries in WHERE Clause', () => {
    it('should suggest keywords for "SELECT * FROM foo WHERE bar |"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT * FROM foo WHERE bar ',
        afterCursor: '',
        containsKeywords: ['IN', 'NOT IN'],
        containsColRefKeywords: true,
        expectedResult: {
          lowerCase: false,
          colRef: { identifierChain: [{ name: 'foo' }, { name: 'bar' }] },
          suggestGroupBys: { prefix: 'GROUP BY', tables: [{ identifierChain: [{ name: 'foo' }] }] },
          suggestOrderBys: { prefix: 'ORDER BY', tables: [{ identifierChain: [{ name: 'foo' }] }] }
        }
      });
    });

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

    it('should suggest identifiers for "SELECT cos(| FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar"', () => {
      assertAutoComplete({
        beforeCursor: 'SELECT cos(',
        afterCursor: ' FROM (SELECT b FROM foo) boo, (SELECT a FROM bla) bar',
        containsKeywords: ['CASE'],
        expectedResult: {
          suggestColumns: {
            source: 'select',
            tables: [
              { identifierChain: [{ subQuery: 'boo' }] },
              { identifierChain: [{ subQuery: 'bar' }] }
            ]
          },
          suggestIdentifiers: [
            { name: 'boo.', type: 'sub-query' },
            { name: 'bar.', type: 'sub-query' }
          ],
          suggestFunctions: {},
          udfArgument: {
            name: 'cos',
            position: 1
          },
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
          suggestColumns: { source: 'select', tables: [{ identifierChain: [{ subQuery: 's2' }] }] },
          suggestKeywords: ['*'],
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
          ],
          lowerCase: false
        }
      });
    });
  });
});
