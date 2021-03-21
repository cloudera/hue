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

import prestoAutocompleteParser from '../prestoAutocompleteParser';

describe('prestoAutocompleteParser.js locations', () => {
  beforeAll(() => {
    prestoAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;
    expect(
      prestoAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  const assertLocations = function (options) {
    assertAutoComplete({
      beforeCursor: options.beforeCursor,
      afterCursor: options.afterCursor || '',
      locationsOnly: true,
      noErrors: true,
      expectedLocations: options.expectedLocations,
      expectedDefinitions: options.expectedDefinitions
    });
  };

  it('should report locations for "select cos(1) as foo from customers order by foo;"', () => {
    assertLocations({
      beforeCursor: 'select cos(1) as foo from customers order by foo; ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 49 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 21 }
        },
        {
          type: 'function',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
          function: 'cos'
        },
        {
          type: 'functionArgument',
          location: { first_line: 1, last_line: 1, first_column: 12, last_column: 13 },
          function: 'cos',
          argumentPosition: 0,
          identifierChain: [{ name: 'cos' }],
          expression: { types: ['NUMBER'], text: '1' }
        },
        {
          type: 'alias',
          source: 'column',
          alias: 'foo',
          location: { first_line: 1, last_line: 1, first_column: 18, last_column: 21 },
          parentLocation: { first_line: 1, last_line: 1, first_column: 8, last_column: 14 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 36 },
          identifierChain: [{ name: 'customers' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 36, last_column: 36 }
        },
        {
          type: 'alias',
          location: { first_line: 1, last_line: 1, first_column: 46, last_column: 49 },
          alias: 'foo',
          source: 'column',
          parentLocation: { first_line: 1, last_line: 1, first_column: 8, last_column: 14 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 49, last_column: 49 }
        }
      ]
    });
  });

  it('should report locations for "SELECT * FROM tbl WHERE tbl.mp[\'key\'].bla;"', () => {
    assertLocations({
      beforeCursor: "SELECT * FROM tbl WHERE tbl.mp['key'].bla; ",
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 42 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          tables: [{ identifierChain: [{ name: 'tbl' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 },
          identifierChain: [{ name: 'tbl' }]
        },
        {
          type: 'whereClause',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 42 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 },
          identifierChain: [{ name: 'tbl' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 29, last_column: 31 },
          identifierChain: [{ name: 'mp', keySet: true }],
          qualified: true,
          tables: [{ identifierChain: [{ name: 'tbl' }] }]
        },
        {
          type: 'complex',
          location: { first_line: 1, last_line: 1, first_column: 39, last_column: 42 },
          identifierChain: [{ name: 'mp', keySet: true }, { name: 'bla' }],
          qualified: true,
          tables: [{ identifierChain: [{ name: 'tbl' }] }]
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 42, last_column: 42 }
        }
      ]
    });
  });

  it('should report locations for "WITH boo AS (SELECT * FROM tbl) SELECT * FROM boo; |"', () => {
    assertLocations({
      beforeCursor: 'WITH boo AS (SELECT * FROM tbl) SELECT * FROM boo; ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 50 }
        },
        {
          type: 'alias',
          source: 'cte',
          alias: 'boo',
          location: { first_line: 1, last_line: 1, first_column: 6, last_column: 9 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 21, last_column: 22 },
          subquery: true
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 21, last_column: 22 },
          tables: [{ identifierChain: [{ name: 'tbl' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 28, last_column: 31 },
          identifierChain: [{ name: 'tbl' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 31, last_column: 31 },
          subquery: true
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 31, last_column: 31 },
          subquery: true
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 40, last_column: 41 }
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 40, last_column: 41 },
          tables: [{ identifierChain: [{ name: 'boo' }] }]
        },
        {
          type: 'alias',
          target: 'cte',
          alias: 'boo',
          location: { first_line: 1, last_line: 1, first_column: 47, last_column: 50 }
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 50, last_column: 50 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 50, last_column: 50 }
        }
      ]
    });
  });

  it('should report locations for "SELECT * FROM testTable1 JOIN db1.table2; |"', () => {
    assertLocations({
      beforeCursor: 'SELECT * FROM testTable1 JOIN db1.table2; ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 41 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          tables: [
            { identifierChain: [{ name: 'testTable1' }] },
            { identifierChain: [{ name: 'db1' }, { name: 'table2' }] }
          ]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 25 },
          identifierChain: [{ name: 'testTable1' }]
        },
        {
          type: 'database',
          location: { first_line: 1, last_line: 1, first_column: 31, last_column: 34 },
          identifierChain: [{ name: 'db1' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 35, last_column: 41 },
          identifierChain: [{ name: 'db1' }, { name: 'table2' }]
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
    });
  });

  it('should report locations for "SELECT a.col FROM db.tbl a; |"', () => {
    assertLocations({
      beforeCursor: 'SELECT a.col FROM db.tbl a; ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 27 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 13 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          identifierChain: [{ name: 'db' }, { name: 'tbl' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 10, last_column: 13 },
          identifierChain: [{ name: 'col' }],
          tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }], alias: 'a' }],
          qualified: true
        },
        {
          type: 'database',
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 21 },
          identifierChain: [{ name: 'db' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 22, last_column: 25 },
          identifierChain: [{ name: 'db' }, { name: 'tbl' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 'a',
          location: { first_line: 1, last_line: 1, first_column: 26, last_column: 27 },
          identifierChain: [{ name: 'db' }, { name: 'tbl' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 27 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 27 }
        }
      ]
    });
  });

  it('should report locations for "SELECT tbl.col FROM db.tbl a; |"', () => {
    assertLocations({
      beforeCursor: 'SELECT tbl.col FROM db.tbl a; ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 29 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 15 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
          identifierChain: [{ name: 'tbl' }],
          tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }], alias: 'a' }],
          qualified: false
        },
        {
          type: 'complex',
          location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
          identifierChain: [{ name: 'tbl' }, { name: 'col' }],
          tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }], alias: 'a' }],
          qualified: true
        },
        {
          type: 'database',
          location: { first_line: 1, last_line: 1, first_column: 21, last_column: 23 },
          identifierChain: [{ name: 'db' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 24, last_column: 27 },
          identifierChain: [{ name: 'db' }, { name: 'tbl' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 'a',
          location: { first_line: 1, last_line: 1, first_column: 28, last_column: 29 },
          identifierChain: [{ name: 'db' }, { name: 'tbl' }]
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
      ]
    });
  });

  it('should report locations for "select x from x;"', () => {
    assertLocations({
      beforeCursor: 'select x from x;',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 16 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          identifierChain: [{ name: 'x' }],
          tables: [{ identifierChain: [{ name: 'x' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 },
          identifierChain: [{ name: 'x' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 16, last_column: 16 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 16, last_column: 16 }
        }
      ]
    });
  });

  it('should report locations for "select x from x;select y from y;"', () => {
    assertLocations({
      beforeCursor: 'select x from x;select y from y;',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 16 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          identifierChain: [{ name: 'x' }],
          tables: [{ identifierChain: [{ name: 'x' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 },
          identifierChain: [{ name: 'x' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 16, last_column: 16 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 16, last_column: 16 }
        },
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 17, last_column: 32 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 24, last_column: 25 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 24, last_column: 25 },
          identifierChain: [{ name: 'y' }],
          tables: [{ identifierChain: [{ name: 'y' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 31, last_column: 32 },
          identifierChain: [{ name: 'y' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 32, last_column: 32 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 32, last_column: 32 }
        }
      ]
    });
  });

  it('should report locations for "-- comment\nselect x from x;\n\n\nselect y from y;"', () => {
    assertLocations({
      beforeCursor: '-- comment\nselect x from x;\n\n\nselect y from y;',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 2, first_column: 1, last_column: 16 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 2, last_line: 2, first_column: 8, last_column: 9 }
        },
        {
          type: 'column',
          location: { first_line: 2, last_line: 2, first_column: 8, last_column: 9 },
          identifierChain: [{ name: 'x' }],
          tables: [{ identifierChain: [{ name: 'x' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 2, last_line: 2, first_column: 15, last_column: 16 },
          identifierChain: [{ name: 'x' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 2, last_line: 2, first_column: 16, last_column: 16 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 2, last_line: 2, first_column: 16, last_column: 16 }
        },
        {
          type: 'statement',
          location: { first_line: 2, last_line: 5, first_column: 17, last_column: 16 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 5, last_line: 5, first_column: 8, last_column: 9 }
        },
        {
          type: 'column',
          location: { first_line: 5, last_line: 5, first_column: 8, last_column: 9 },
          identifierChain: [{ name: 'y' }],
          tables: [{ identifierChain: [{ name: 'y' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 5, last_line: 5, first_column: 15, last_column: 16 },
          identifierChain: [{ name: 'y' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 5, last_line: 5, first_column: 16, last_column: 16 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 5, last_line: 5, first_column: 16, last_column: 16 }
        }
      ]
    });
  });

  it('should report locations for "select x from x, y;"', () => {
    assertLocations({
      beforeCursor: 'select x from x, y;',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 19 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          identifierChain: [{ name: 'x' }],
          tables: [{ identifierChain: [{ name: 'x' }] }, { identifierChain: [{ name: 'y' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 },
          identifierChain: [{ name: 'x' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 },
          identifierChain: [{ name: 'y' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 19 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 19 }
        }
      ]
    });
  });

  it('should report locations for "SELECT t3.id, id FROM testTable1, db.testTable2, testTable3 t3;|"', () => {
    assertLocations({
      beforeCursor: 'SELECT t3.id, id FROM testTable1, db.testTable2, testTable3 t3;',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 63 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 17 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
          identifierChain: [{ name: 'testTable3' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 11, last_column: 13 },
          identifierChain: [{ name: 'id' }],
          tables: [{ identifierChain: [{ name: 'testTable3' }], alias: 't3' }],
          qualified: true
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 17 },
          identifierChain: [{ name: 'id' }],
          tables: [
            { identifierChain: [{ name: 'testTable1' }] },
            { identifierChain: [{ name: 'db' }, { name: 'testTable2' }] },
            { identifierChain: [{ name: 'testTable3' }], alias: 't3' }
          ],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 23, last_column: 33 },
          identifierChain: [{ name: 'testTable1' }]
        },
        {
          type: 'database',
          location: { first_line: 1, last_line: 1, first_column: 35, last_column: 37 },
          identifierChain: [{ name: 'db' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 38, last_column: 48 },
          identifierChain: [{ name: 'db' }, { name: 'testTable2' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 50, last_column: 60 },
          identifierChain: [{ name: 'testTable3' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 't3',
          location: { first_line: 1, last_line: 1, first_column: 61, last_column: 63 },
          identifierChain: [{ name: 'testTable3' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 63, last_column: 63 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 63, last_column: 63 }
        }
      ]
    });
  });

  it('should report locations for "SELECT * FROM foo WHERE bar IN (1+1, 2+2);|"', () => {
    assertLocations({
      beforeCursor: 'SELECT * FROM foo WHERE bar IN (1+1, 2+2);',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 42 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          tables: [{ identifierChain: [{ name: 'foo' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 },
          identifierChain: [{ name: 'foo' }]
        },
        {
          type: 'whereClause',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 42 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 },
          identifierChain: [{ name: 'bar' }],
          tables: [{ identifierChain: [{ name: 'foo' }] }],
          qualified: false
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 42, last_column: 42 }
        }
      ]
    });
  });

  it('should report locations for "SELECT * FROM foo WHERE bar IN (id+1-1, id+1-2);|"', () => {
    assertLocations({
      beforeCursor: 'SELECT * FROM foo WHERE bar IN (id+1-1, id+1-2);',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 48 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          tables: [{ identifierChain: [{ name: 'foo' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 },
          identifierChain: [{ name: 'foo' }]
        },
        {
          type: 'whereClause',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 48 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 },
          identifierChain: [{ name: 'bar' }],
          tables: [{ identifierChain: [{ name: 'foo' }] }],
          qualified: false
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 33, last_column: 35 },
          identifierChain: [{ name: 'id' }],
          tables: [{ identifierChain: [{ name: 'foo' }] }],
          qualified: false
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 41, last_column: 43 },
          identifierChain: [{ name: 'id' }],
          tables: [{ identifierChain: [{ name: 'foo' }] }],
          qualified: false
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 48, last_column: 48 }
        }
      ]
    });
  });

  it(
    'should report locations for "SELECT s07.description, s07.salary, s08.salary,\\r\\n' +
      '  s08.salary - s07.salary\\r\\n' +
      'FROM\\r\\n' +
      '  sample_07 s07 JOIN sample_08 s08\\r\\n' +
      'ON ( s07.code = s08.code)\\r\\n' +
      'WHERE\\r\\n' +
      '  s07.salary < s08.salary\\r\\n' +
      'ORDER BY s08.salary-s07.salary DESC\\r\\n' +
      'LIMIT 1000;|"',
    () => {
      assertLocations({
        beforeCursor:
          'SELECT s07.description, s07.salary, s08.salary,\r\n' +
          '  s08.salary - s07.salary\r\n' +
          'FROM\r\n' +
          '  sample_07 s07 JOIN sample_08 s08\r\n' +
          'ON ( s07.code = s08.code)\r\n' +
          'WHERE\r\n' +
          '  s07.salary < s08.salary\r\n' +
          'ORDER BY s08.salary-s07.salary DESC\r\n' +
          'LIMIT 1000;',
        expectedLocations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 9, first_column: 1, last_column: 11 }
          },
          {
            type: 'selectList',
            missing: false,
            location: { first_line: 1, last_line: 2, first_column: 8, last_column: 26 }
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 12, last_column: 23 },
            identifierChain: [{ name: 'description' }],
            tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 29, last_column: 35 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 37, last_column: 40 },
            identifierChain: [{ name: 'sample_08' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 41, last_column: 47 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 2, last_line: 2, first_column: 3, last_column: 6 },
            identifierChain: [{ name: 'sample_08' }]
          },
          {
            type: 'column',
            location: { first_line: 2, last_line: 2, first_column: 7, last_column: 13 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 2, last_line: 2, first_column: 16, last_column: 19 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'column',
            location: { first_line: 2, last_line: 2, first_column: 20, last_column: 26 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 4, last_line: 4, first_column: 3, last_column: 12 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'alias',
            source: 'table',
            alias: 's07',
            location: { first_line: 4, last_line: 4, first_column: 13, last_column: 16 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'table',
            location: { first_line: 4, last_line: 4, first_column: 22, last_column: 31 },
            identifierChain: [{ name: 'sample_08' }]
          },
          {
            type: 'alias',
            source: 'table',
            alias: 's08',
            location: { first_line: 4, last_line: 4, first_column: 32, last_column: 35 },
            identifierChain: [{ name: 'sample_08' }]
          },
          {
            type: 'table',
            location: { first_line: 5, last_line: 5, first_column: 6, last_column: 9 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'column',
            location: { first_line: 5, last_line: 5, first_column: 10, last_column: 14 },
            identifierChain: [{ name: 'code' }],
            tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 5, last_line: 5, first_column: 17, last_column: 20 },
            identifierChain: [{ name: 'sample_08' }]
          },
          {
            type: 'column',
            location: { first_line: 5, last_line: 5, first_column: 21, last_column: 25 },
            identifierChain: [{ name: 'code' }],
            tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }],
            qualified: true
          },
          {
            type: 'whereClause',
            missing: false,
            location: { first_line: 6, last_line: 7, first_column: 1, last_column: 26 }
          },
          {
            type: 'table',
            location: { first_line: 7, last_line: 7, first_column: 3, last_column: 6 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'column',
            location: { first_line: 7, last_line: 7, first_column: 7, last_column: 13 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 7, last_line: 7, first_column: 16, last_column: 19 },
            identifierChain: [{ name: 'sample_08' }]
          },
          {
            type: 'column',
            location: { first_line: 7, last_line: 7, first_column: 20, last_column: 26 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 8, last_line: 8, first_column: 10, last_column: 13 },
            identifierChain: [{ name: 'sample_08' }]
          },
          {
            type: 'column',
            location: { first_line: 8, last_line: 8, first_column: 14, last_column: 20 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 8, last_line: 8, first_column: 21, last_column: 24 },
            identifierChain: [{ name: 'sample_07' }]
          },
          {
            type: 'column',
            location: { first_line: 8, last_line: 8, first_column: 25, last_column: 31 },
            identifierChain: [{ name: 'salary' }],
            tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }],
            qualified: true
          },
          {
            type: 'limitClause',
            missing: false,
            location: { first_line: 9, last_line: 9, first_column: 1, last_column: 11 }
          }
        ]
      });
    }
  );

  it('should handle "select bl from blablabla join (select * from blablabla) s1;', () => {
    assertLocations({
      beforeCursor: 'select bl from blablabla join (select * from blablabla) s1;',
      afterCursor: '',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 59 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
          identifierChain: [{ name: 'bl' }],
          tables: [{ identifierChain: [{ name: 'blablabla' }] }, { subQuery: 's1' }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 16, last_column: 25 },
          identifierChain: [{ name: 'blablabla' }]
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 39, last_column: 40 },
          subquery: true
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 39, last_column: 40 },
          tables: [{ identifierChain: [{ name: 'blablabla' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 46, last_column: 55 },
          identifierChain: [{ name: 'blablabla' }]
        },
        {
          type: 'whereClause',
          subquery: true,
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 55, last_column: 55 }
        },
        {
          type: 'limitClause',
          subquery: true,
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 55, last_column: 55 }
        },
        {
          type: 'alias',
          source: 'subquery',
          alias: 's1',
          location: { first_line: 1, last_line: 1, first_column: 57, last_column: 59 }
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 59, last_column: 59 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 59, last_column: 59 }
        }
      ]
    });
  });

  it(
    'should report locations for "SELECT CASE cos(boo.a) > baa.boo \\n' +
      '\\tWHEN baa.b THEN true \\n' +
      '\\tWHEN boo.c THEN false \\n' +
      '\\tWHEN baa.blue THEN boo.d \\n' +
      '\\tELSE baa.e END \\n' +
      '\\t FROM db1.foo boo, bar baa WHERE baa.bla IN (SELECT ble FROM bla);|"',
    () => {
      assertLocations({
        beforeCursor:
          'SELECT CASE cos(boo.a) > baa.boo \n\tWHEN baa.b THEN true \n\tWHEN boo.c THEN false \n\tWHEN baa.blue THEN boo.d \n\tELSE baa.e END \n\t FROM db1.foo boo, bar baa WHERE baa.bla IN (SELECT ble FROM bla);',
        expectedLocations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 6, first_column: 1, last_column: 67 }
          },
          {
            type: 'selectList',
            missing: false,
            location: { first_line: 1, last_line: 5, first_column: 8, last_column: 16 }
          },
          {
            type: 'function',
            location: { first_line: 1, last_line: 1, first_column: 13, last_column: 15 },
            function: 'cos'
          },
          {
            type: 'functionArgument',
            location: { first_line: 1, last_line: 1, first_column: 17, last_column: 22 },
            function: 'cos',
            argumentPosition: 0,
            identifierChain: [{ name: 'cos' }],
            expression: { types: ['COLREF'], columnReference: [{ name: 'boo' }, { name: 'a' }] }
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 17, last_column: 20 },
            identifierChain: [{ name: 'db1' }, { name: 'foo' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 21, last_column: 22 },
            identifierChain: [{ name: 'a' }],
            tables: [{ identifierChain: [{ name: 'db1' }, { name: 'foo' }], alias: 'boo' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 26, last_column: 29 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 30, last_column: 33 },
            identifierChain: [{ name: 'boo' }],
            tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 2, last_line: 2, first_column: 7, last_column: 10 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'column',
            location: { first_line: 2, last_line: 2, first_column: 11, last_column: 12 },
            identifierChain: [{ name: 'b' }],
            tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 3, last_line: 3, first_column: 7, last_column: 10 },
            identifierChain: [{ name: 'db1' }, { name: 'foo' }]
          },
          {
            type: 'column',
            location: { first_line: 3, last_line: 3, first_column: 11, last_column: 12 },
            identifierChain: [{ name: 'c' }],
            tables: [{ identifierChain: [{ name: 'db1' }, { name: 'foo' }], alias: 'boo' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 4, last_line: 4, first_column: 7, last_column: 10 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'column',
            location: { first_line: 4, last_line: 4, first_column: 11, last_column: 15 },
            identifierChain: [{ name: 'blue' }],
            tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 4, last_line: 4, first_column: 21, last_column: 24 },
            identifierChain: [{ name: 'db1' }, { name: 'foo' }]
          },
          {
            type: 'column',
            location: { first_line: 4, last_line: 4, first_column: 25, last_column: 26 },
            identifierChain: [{ name: 'd' }],
            tables: [{ identifierChain: [{ name: 'db1' }, { name: 'foo' }], alias: 'boo' }],
            qualified: true
          },
          {
            type: 'table',
            location: { first_line: 5, last_line: 5, first_column: 7, last_column: 10 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'column',
            location: { first_line: 5, last_line: 5, first_column: 11, last_column: 12 },
            identifierChain: [{ name: 'e' }],
            tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }],
            qualified: true
          },
          {
            type: 'database',
            location: { first_line: 6, last_line: 6, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'db1' }]
          },
          {
            type: 'table',
            location: { first_line: 6, last_line: 6, first_column: 12, last_column: 15 },
            identifierChain: [{ name: 'db1' }, { name: 'foo' }]
          },
          {
            type: 'alias',
            source: 'table',
            alias: 'boo',
            location: { first_line: 6, last_line: 6, first_column: 16, last_column: 19 },
            identifierChain: [{ name: 'db1' }, { name: 'foo' }]
          },
          {
            type: 'table',
            location: { first_line: 6, last_line: 6, first_column: 21, last_column: 24 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'alias',
            source: 'table',
            alias: 'baa',
            location: { first_line: 6, last_line: 6, first_column: 25, last_column: 28 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'whereClause',
            missing: false,
            location: { first_line: 6, last_line: 6, first_column: 29, last_column: 67 }
          },
          {
            type: 'table',
            location: { first_line: 6, last_line: 6, first_column: 35, last_column: 38 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'column',
            location: { first_line: 6, last_line: 6, first_column: 39, last_column: 42 },
            identifierChain: [{ name: 'bla' }],
            tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }],
            qualified: true
          },
          {
            type: 'selectList',
            missing: false,
            location: { first_line: 6, last_line: 6, first_column: 54, last_column: 57 },
            subquery: true
          },
          {
            type: 'column',
            location: { first_line: 6, last_line: 6, first_column: 54, last_column: 57 },
            identifierChain: [{ name: 'ble' }],
            tables: [{ identifierChain: [{ name: 'bla' }] }],
            qualified: false
          },
          {
            type: 'table',
            location: { first_line: 6, last_line: 6, first_column: 63, last_column: 66 },
            identifierChain: [{ name: 'bla' }]
          },
          {
            type: 'whereClause',
            subquery: true,
            missing: true,
            location: { first_line: 6, last_line: 6, first_column: 66, last_column: 66 }
          },
          {
            type: 'limitClause',
            subquery: true,
            missing: true,
            location: { first_line: 6, last_line: 6, first_column: 66, last_column: 66 }
          },
          {
            type: 'limitClause',
            missing: true,
            location: { first_line: 6, last_line: 6, first_column: 67, last_column: 67 }
          }
        ]
      });
    }
  );

  it('should report locations for "SELECT tta.* FROM testTableA tta, testTableB; |"', () => {
    assertLocations({
      beforeCursor: 'SELECT tta.* FROM testTableA tta, testTableB; ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 45 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 13 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 12, last_column: 13 },
          tables: [{ alias: 'tta', identifierChain: [{ name: 'testTableA' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 29 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 'tta',
          location: { first_line: 1, last_line: 1, first_column: 30, last_column: 33 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 35, last_column: 45 },
          identifierChain: [{ name: 'testTableB' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 45, last_column: 45 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 45, last_column: 45 }
        }
      ]
    });
  });

  it('should report locations for "SELECT COUNT(*) FROM testTable; |"', () => {
    assertLocations({
      beforeCursor: 'SELECT COUNT(*) FROM testTable;',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 31 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 16 }
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
          location: { first_line: 1, last_line: 1, first_column: 22, last_column: 31 },
          identifierChain: [{ name: 'testTable' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 31, last_column: 31 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 31, last_column: 31 }
        }
      ]
    });
  });

  describe('File paths', () => {
    it('should report locations for "LOAD DATA LOCAL INPATH \'/some/path/file.ble\' OVERWRITE INTO TABLE bla; |"', () => {
      assertLocations({
        beforeCursor: "LOAD DATA LOCAL INPATH '/some/path/file.ble' OVERWRITE INTO TABLE bla;",
        expectedLocations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 70 }
          },
          {
            type: 'file',
            location: { first_line: 1, last_line: 1, first_column: 25, last_column: 44 },
            path: '/some/path/file.ble'
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 67, last_column: 70 },
            identifierChain: [{ name: 'bla' }]
          }
        ]
      });
    });
  });

  it('should report locations for "SELECT * FROM testTable t1 ORDER BY t1.a ASC, t1.b, t1.c DESC, t1.d;\nSELECT t1.bla FROM testTable2 t1;\\nSELECT * FROM testTable3 t3, testTable4 t4; |"', () => {
    assertLocations({
      beforeCursor:
        'SELECT * FROM testTable t1 ORDER BY t1.a ASC, t1.b, t1.c DESC, t1.d;\nSELECT t1.bla FROM testTable2 t1;\nSELECT * FROM testTable3 t3, testTable4 t4; ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 68 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          tables: [{ alias: 't1', identifierChain: [{ name: 'testTable' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 24 },
          identifierChain: [{ name: 'testTable' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 't1',
          location: { first_line: 1, last_line: 1, first_column: 25, last_column: 27 },
          identifierChain: [{ name: 'testTable' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 27 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 37, last_column: 39 },
          identifierChain: [{ name: 'testTable' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 40, last_column: 41 },
          identifierChain: [{ name: 'a' }],
          tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 47, last_column: 49 },
          identifierChain: [{ name: 'testTable' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 50, last_column: 51 },
          identifierChain: [{ name: 'b' }],
          tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 53, last_column: 55 },
          identifierChain: [{ name: 'testTable' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 56, last_column: 57 },
          identifierChain: [{ name: 'c' }],
          tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 64, last_column: 66 },
          identifierChain: [{ name: 'testTable' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 67, last_column: 68 },
          identifierChain: [{ name: 'd' }],
          tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }],
          qualified: true
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 68, last_column: 68 }
        },
        {
          type: 'statement',
          location: { first_line: 1, last_line: 2, first_column: 69, last_column: 33 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 2, last_line: 2, first_column: 8, last_column: 14 }
        },
        {
          type: 'table',
          location: { first_line: 2, last_line: 2, first_column: 8, last_column: 10 },
          identifierChain: [{ name: 'testTable2' }]
        },
        {
          type: 'column',
          location: { first_line: 2, last_line: 2, first_column: 11, last_column: 14 },
          identifierChain: [{ name: 'bla' }],
          tables: [{ identifierChain: [{ name: 'testTable2' }], alias: 't1' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 2, last_line: 2, first_column: 20, last_column: 30 },
          identifierChain: [{ name: 'testTable2' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 't1',
          location: { first_line: 2, last_line: 2, first_column: 31, last_column: 33 },
          identifierChain: [{ name: 'testTable2' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 2, last_line: 2, first_column: 33, last_column: 33 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 2, last_line: 2, first_column: 33, last_column: 33 }
        },
        {
          type: 'statement',
          location: { first_line: 2, last_line: 3, first_column: 34, last_column: 43 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 3, last_line: 3, first_column: 8, last_column: 9 }
        },
        {
          type: 'asterisk',
          location: { first_line: 3, last_line: 3, first_column: 8, last_column: 9 },
          tables: [
            { alias: 't3', identifierChain: [{ name: 'testTable3' }] },
            { alias: 't4', identifierChain: [{ name: 'testTable4' }] }
          ]
        },
        {
          type: 'table',
          location: { first_line: 3, last_line: 3, first_column: 15, last_column: 25 },
          identifierChain: [{ name: 'testTable3' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 't3',
          location: { first_line: 3, last_line: 3, first_column: 26, last_column: 28 },
          identifierChain: [{ name: 'testTable3' }]
        },
        {
          type: 'table',
          location: { first_line: 3, last_line: 3, first_column: 30, last_column: 40 },
          identifierChain: [{ name: 'testTable4' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 't4',
          location: { first_line: 3, last_line: 3, first_column: 41, last_column: 43 },
          identifierChain: [{ name: 'testTable4' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 3, last_line: 3, first_column: 43, last_column: 43 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 3, last_line: 3, first_column: 43, last_column: 43 }
        }
      ]
    });
  });

  it('should report locations for "SELECT t1.foo FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (t1.c1 = table2.c2); |"', () => {
    assertLocations({
      beforeCursor:
        'SELECT t1.foo FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (t1.c1 = table2.c2); ',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 108 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 14 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 },
          identifierChain: [{ name: 'table1' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 11, last_column: 14 },
          identifierChain: [{ name: 'foo' }],
          tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 20, last_column: 26 },
          identifierChain: [{ name: 'table1' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 't1',
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 29 },
          identifierChain: [{ name: 'table1' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 41, last_column: 47 },
          identifierChain: [{ name: 'table2' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 64, last_column: 70 },
          identifierChain: [{ name: 'table3' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 76, last_column: 82 },
          identifierChain: [{ name: 'table4' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 't4',
          location: { first_line: 1, last_line: 1, first_column: 83, last_column: 85 },
          identifierChain: [{ name: 'table4' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 90, last_column: 92 },
          identifierChain: [{ name: 'table1' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 93, last_column: 95 },
          identifierChain: [{ name: 'c1' }],
          tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 98, last_column: 104 },
          identifierChain: [{ name: 'table2' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 105, last_column: 107 },
          identifierChain: [{ name: 'c2' }],
          tables: [{ identifierChain: [{ name: 'table2' }] }],
          qualified: true
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 108, last_column: 108 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 108, last_column: 108 }
        }
      ]
    });
  });

  it('should report locations for "SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);|"', () => {
    assertLocations({
      beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 51 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          tables: [{ identifierChain: [{ name: 'foo' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 },
          identifierChain: [{ name: 'foo' }]
        },
        {
          type: 'whereClause',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 51 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 },
          identifierChain: [{ name: 'bar' }],
          tables: [{ identifierChain: [{ name: 'foo' }] }],
          qualified: false
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 40, last_column: 41 },
          subquery: true
        },
        {
          type: 'asterisk',
          location: { first_line: 1, last_line: 1, first_column: 40, last_column: 41 },
          tables: [{ identifierChain: [{ name: 'bla' }] }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 47, last_column: 50 },
          identifierChain: [{ name: 'bla' }]
        },
        {
          type: 'whereClause',
          subquery: true,
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 50, last_column: 50 }
        },
        {
          type: 'limitClause',
          subquery: true,
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 50, last_column: 50 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 51, last_column: 51 }
        }
      ]
    });
  });

  it('should report locations for "SELECT   |    FROM    testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT   ',
      afterCursor: '    FROM    testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 32 }
        },
        {
          type: 'selectList',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 7, last_column: 7 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 22, last_column: 32 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 32, last_column: 32 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 32, last_column: 32 }
        }
      ]
    });
  });

  it('should report locations for "SELECT   a.|    FROM    testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT   a.',
      afterCursor: '    FROM    testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 34 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 10, last_column: 13 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 10, last_column: 11 },
          identifierChain: [{ name: 'a' }],
          tables: [{ identifierChain: [{ name: 'testTableA' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 24, last_column: 34 },
          identifierChain: [{ name: 'testTableA' }]
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
    });
  });

  it('should report locations for "SELECT aaa| FROM testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT aaa',
      afterCursor: ' FROM testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 27 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 17, last_column: 27 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 27 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 27 }
        }
      ]
    });
  });

  it('should report locations for "SELECT aaa| \\nFROM testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT aaa',
      afterCursor: ' \nFROM testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 2, first_column: 1, last_column: 16 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 }
        },
        {
          type: 'table',
          location: { first_line: 2, last_line: 2, first_column: 6, last_column: 16 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 2, last_line: 2, first_column: 16, last_column: 16 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 2, last_line: 2, first_column: 16, last_column: 16 }
        }
      ]
    });
  });

  it('should report locations for "SELECT |bbbb FROM testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT ',
      afterCursor: 'bbbb FROM testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 28 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 12 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 18, last_column: 28 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 28, last_column: 28 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 28, last_column: 28 }
        }
      ]
    });
  });

  it('should report locations for "SELECT aaaaa|bbbb FROM testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT aaaaa',
      afterCursor: 'bbbb FROM testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 33 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 17 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 23, last_column: 33 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 33, last_column: 33 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 33, last_column: 33 }
        }
      ]
    });
  });

  it('should report locations for "SELECT foo.aaaaa|bbbb FROM testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT foo.aaaaa',
      afterCursor: 'bbbb FROM testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 37 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 13 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
          identifierChain: [{ name: 'foo' }],
          tables: [{ identifierChain: [{ name: 'testTableA' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 27, last_column: 37 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 37, last_column: 37 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 37, last_column: 37 }
        }
      ]
    });
  });

  it('should report locations for "SELECT b, foo.aaaaa|bbbb FROM testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT b, foo.aaaaa',
      afterCursor: 'bbbb FROM testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 40 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 16 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 },
          identifierChain: [{ name: 'b' }],
          tables: [{ identifierChain: [{ name: 'testTableA' }] }],
          qualified: false
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 11, last_column: 14 },
          identifierChain: [{ name: 'foo' }],
          tables: [{ identifierChain: [{ name: 'testTableA' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 30, last_column: 40 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 40, last_column: 40 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 40, last_column: 40 }
        }
      ]
    });
  });

  it('should report locations for "SELECT foo, aaaaa|bbbb FROM testTableA"', () => {
    assertLocations({
      beforeCursor: 'SELECT foo, aaaaa',
      afterCursor: 'bbbb FROM testTableA',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 38 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 15 }
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
          identifierChain: [{ name: 'foo' }],
          tables: [{ identifierChain: [{ name: 'testTableA' }] }],
          qualified: false
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 28, last_column: 38 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 38, last_column: 38 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 38, last_column: 38 }
        }
      ]
    });
  });

  it('should report locations for "SELECT tbl.col FROM some_tbl tbl;"', () => {
    assertLocations({
      beforeCursor: 'SELECT tbl.col FROM some_tbl tbl;',
      afterCursor: '',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 33 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 15 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
          identifierChain: [{ name: 'col' }],
          tables: [{ identifierChain: [{ name: 'some_tbl' }], alias: 'tbl' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 21, last_column: 29 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 'tbl',
          location: { first_line: 1, last_line: 1, first_column: 30, last_column: 33 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 33, last_column: 33 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 33, last_column: 33 }
        }
      ]
    });
  });

  it('should report locations for "SELECT tbl.col.cplx FROM some_tbl tbl;"', () => {
    assertLocations({
      beforeCursor: 'SELECT tbl.col.cplx FROM some_tbl tbl;',
      afterCursor: '',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 38 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 20 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
          identifierChain: [{ name: 'col' }],
          tables: [{ identifierChain: [{ name: 'some_tbl' }], alias: 'tbl' }],
          qualified: true
        },
        {
          type: 'complex',
          location: { first_line: 1, last_line: 1, first_column: 16, last_column: 20 },
          identifierChain: [{ name: 'col' }, { name: 'cplx' }],
          tables: [{ identifierChain: [{ name: 'some_tbl' }], alias: 'tbl' }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 26, last_column: 34 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 'tbl',
          location: { first_line: 1, last_line: 1, first_column: 35, last_column: 38 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 38, last_column: 38 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 38, last_column: 38 }
        }
      ]
    });
  });

  it('should report locations for "SELECT some_tbl.col.cplx FROM some_tbl;"', () => {
    assertLocations({
      beforeCursor: 'SELECT some_tbl.col.cplx FROM some_tbl;',
      afterCursor: '',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 39 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 25 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 16 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 17, last_column: 20 },
          identifierChain: [{ name: 'col' }],
          tables: [{ identifierChain: [{ name: 'some_tbl' }] }],
          qualified: true
        },
        {
          type: 'complex',
          location: { first_line: 1, last_line: 1, first_column: 21, last_column: 25 },
          identifierChain: [{ name: 'col' }, { name: 'cplx' }],
          tables: [{ identifierChain: [{ name: 'some_tbl' }] }],
          qualified: true
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 31, last_column: 39 },
          identifierChain: [{ name: 'some_tbl' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 39, last_column: 39 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 39, last_column: 39 }
        }
      ]
    });
  });

  it('should report locations for "SELECT testTableB.a, cos(1), tta.abcdefg|hijk, tta.bla, cos(1) FROM testTableA tta, testTableB;"', () => {
    assertLocations({
      beforeCursor: 'SELECT testTableB.a, cos(1), tta.abcdefg',
      afterCursor: 'hijk, tta.bla, cos(1) FROM testTableA tta, testTableB;',
      expectedLocations: [
        {
          type: 'statement',
          location: { first_line: 1, last_line: 1, first_column: 1, last_column: 94 }
        },
        {
          type: 'selectList',
          missing: false,
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 52 }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 8, last_column: 18 },
          identifierChain: [{ name: 'testTableB' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 19, last_column: 20 },
          identifierChain: [{ name: 'a' }],
          tables: [{ identifierChain: [{ name: 'testTableB' }] }],
          qualified: true
        },
        {
          type: 'function',
          location: { first_line: 1, last_line: 1, first_column: 22, last_column: 24 },
          function: 'cos'
        },
        {
          type: 'functionArgument',
          location: { first_line: 1, last_line: 1, first_column: 26, last_column: 27 },
          function: 'cos',
          argumentPosition: 0,
          identifierChain: [{ name: 'cos' }],
          expression: { types: ['NUMBER'], text: '1' }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 30, last_column: 33 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 47, last_column: 50 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'column',
          location: { first_line: 1, last_line: 1, first_column: 51, last_column: 54 },
          identifierChain: [{ name: 'bla' }],
          tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }],
          qualified: true
        },
        {
          type: 'function',
          location: { first_line: 1, last_line: 1, first_column: 56, last_column: 58 },
          function: 'cos'
        },
        {
          type: 'functionArgument',
          location: { first_line: 1, last_line: 1, first_column: 60, last_column: 61 },
          function: 'cos',
          argumentPosition: 0,
          identifierChain: [{ name: 'cos' }],
          expression: { types: ['NUMBER'], text: '1' }
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 68, last_column: 78 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'alias',
          source: 'table',
          alias: 'tta',
          location: { first_line: 1, last_line: 1, first_column: 79, last_column: 82 },
          identifierChain: [{ name: 'testTableA' }]
        },
        {
          type: 'table',
          location: { first_line: 1, last_line: 1, first_column: 84, last_column: 94 },
          identifierChain: [{ name: 'testTableB' }]
        },
        {
          type: 'whereClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 94, last_column: 94 }
        },
        {
          type: 'limitClause',
          missing: true,
          location: { first_line: 1, last_line: 1, first_column: 94, last_column: 94 }
        }
      ]
    });
  });
});
