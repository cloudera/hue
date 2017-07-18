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
  describe('sqlAutocompleteParser.js locations', function() {

    beforeAll(function () {
      sqlAutocompleteParser.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
    });

    var assertLocations = function (options) {
      SqlTestUtils.assertAutocomplete({
        dialect: options.dialect,
        beforeCursor: options.beforeCursor,
        afterCursor: options.afterCursor || '',
        locationsOnly: true,
        noErrors: true,
        expectedLocations: options.expectedLocations
      });
    };

    it('should report locations for "SELECT * FROM testTable1 JOIN db1.table2; |"', function() {
      assertLocations({
        beforeCursor: 'SELECT * FROM testTable1 JOIN db1.table2; ',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 41 } },
          { type: 'asterisk', location: { first_line:1, last_line:1, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'testTable1' }] }, { identifierChain: [{ name: 'db1' }, { name: 'table2' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 25 }, identifierChain: [{ name: 'testTable1' }] },
          { type: 'database', location: { first_line: 1, last_line: 1, first_column: 31, last_column: 34}, identifierChain: [{ name: 'db1' }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 35, last_column: 41 }, identifierChain: [{ name: 'db1' }, { name: 'table2' }] }
        ]
      });
    });

    it('should report locations for "SELECT db.tbl.col FROM db.tbl; |"', function() {
      assertLocations({
        dialect: 'impala',
        beforeCursor: 'SELECT db.tbl.col FROM db.tbl; ',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 30 } },
          { type: 'database', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'db' }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 11, last_column: 14 }, identifierChain: [{ name: 'db' }, { name: 'tbl' }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 }, identifierChain: [{ name: 'col'}], tables: [{ identifierChain: [{ name: 'db' }, { name: 'tbl' }]}]},
          { type: 'database', location: { first_line: 1, last_line: 1, first_column: 24, last_column: 26 }, identifierChain: [{ name: 'db' }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 27, last_column: 30 }, identifierChain: [{ name: 'db' }, { name: 'tbl' }]}
        ]
      });
    });

    it('should report locations for "select x from x;"', function () {
      assertLocations({
        beforeCursor: 'select x from x;',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 16 } },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, identifierChain: [{ name: 'x' }], tables: [{ identifierChain: [{ name: 'x' }] }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 }, identifierChain: [{ name: 'x' }]}
        ]
      });
    });

    it('should report locations for "select x from x;select y from y;"', function () {
      assertLocations({
        beforeCursor: 'select x from x;select y from y;',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 16 } },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, identifierChain: [{ name: 'x' }], tables: [{ identifierChain: [{ name: 'x' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 }, identifierChain: [{ name: 'x' }] },
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 17, last_column: 32 } },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 24, last_column: 25 }, identifierChain: [{ name: 'y' }], tables: [{ identifierChain: [{ name: 'y' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 31, last_column: 32 }, identifierChain: [{ name: 'y' }] }
        ]
      });
    });

    it('should report locations for "-- comment\nselect x from x;\n\n\nselect y from y;"', function () {
      assertLocations({
        beforeCursor: '-- comment\nselect x from x;\n\n\nselect y from y;',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 2, first_column: 1, last_column: 16 } },
          { type: 'column', location: { first_line: 2, last_line: 2, first_column: 8, last_column: 9 }, identifierChain: [{ name: 'x' }], tables: [{ identifierChain: [{ name: 'x' }] }] },
          { type: 'table', location: { first_line: 2, last_line: 2, first_column: 15, last_column: 16 }, identifierChain: [{ name: 'x' }] },
          { type: 'statement', location: { first_line: 2, last_line: 5, first_column: 17, last_column: 16 } },
          { type: 'column', location: { first_line: 5, last_line: 5, first_column: 8, last_column: 9 }, identifierChain: [{ name: 'y' }], tables: [{ identifierChain: [{ name: 'y' }] }] },
          { type: 'table', location: { first_line: 5, last_line: 5, first_column: 15, last_column: 16 }, identifierChain: [{ name: 'y' }] }
        ]
      });
    });

    it('should report locations for "select x from x, y;"', function () {
      assertLocations({
        beforeCursor: 'select x from x, y;',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 19 } },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, identifierChain: [{ name: 'x' }], tables: [{ identifierChain: [{ name: 'x' }] }, { identifierChain: [{ name: 'y' }] }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 16 }, identifierChain: [{ name: 'x' }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 19 }, identifierChain: [{ name: 'y' }]}
        ]
      });
    });

    it('should report locations for "SELECT t3.id, id FROM testTable1, db.testTable2, testTable3 t3;|"', function() {
      assertLocations({
        beforeCursor: 'SELECT t3.id, id FROM testTable1, db.testTable2, testTable3 t3;',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 63 } },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'testTable3' }] },
          { type:'column', location: { first_line: 1, last_line: 1, first_column: 11, last_column: 13 }, identifierChain: [{ name: 'id' }], tables: [{ identifierChain: [{ name: 'testTable3' }], alias: 't3' }] },
          { type:'column', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 17 }, identifierChain: [{ name: 'id' }], tables: [{ identifierChain: [{ name: 'testTable1' }]}, { identifierChain: [{ name: 'db' }, { name: 'testTable2' }]}, { identifierChain: [{ name: 'testTable3' }], alias: 't3'}] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 23, last_column: 33 }, identifierChain: [{ name: 'testTable1' }] },
          { type: 'database', location: { first_line: 1, last_line: 1, first_column: 35, last_column: 37 }, identifierChain: [{ name: 'db' }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 38, last_column: 48 }, identifierChain: [{ name: 'db' },{ name: 'testTable2'}] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 50, last_column: 60 }, identifierChain: [{ name: 'testTable3' }] }
        ]
      });
    });

    it('should report locations for "SELECT * FROM foo WHERE bar IN (1+1, 2+2);|"', function() {
      assertLocations({
        beforeCursor: 'SELECT * FROM foo WHERE bar IN (1+1, 2+2);',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 42 } },
          { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'foo' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 }, identifierChain: [{ name: 'foo' }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 }, identifierChain:[{ name: 'bar'}], tables: [{ identifierChain: [{ name: 'foo' }] }]}
        ]
      });
    });

    it('should report locations for "SELECT * FROM foo WHERE bar IN (id+1-1, id+1-2);|"', function() {
      assertLocations({
        beforeCursor: 'SELECT * FROM foo WHERE bar IN (id+1-1, id+1-2);',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 48 } },
          { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'foo' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 }, identifierChain: [{ name: 'foo' }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 }, identifierChain:[{ name: 'bar'}], tables: [{ identifierChain: [{ name: 'foo' }] }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 33, last_column: 35 }, identifierChain: [{ name: 'id'}], tables: [{ identifierChain: [{ name: 'foo' }] }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 43 }, identifierChain: [{ name: 'id'}], tables: [{ identifierChain: [{ name: 'foo' }] }]}
        ]
      });
    });

    it('should report locations for "SELECT s07.description, s07.salary, s08.salary,\\r\\n' +
        '  s08.salary - s07.salary\\r\\n' +
        'FROM\\r\\n' +
        '  sample_07 s07 JOIN sample_08 s08\\r\\n' +
        'ON ( s07.code = s08.code)\\r\\n' +
        'WHERE\\r\\n' +
        '  s07.salary < s08.salary\\r\\n' +
        'ORDER BY s08.salary-s07.salary DESC\\r\\n' +
        'LIMIT 1000;|"', function() {
      assertLocations({
        beforeCursor: 'SELECT s07.description, s07.salary, s08.salary,\r\n' +
        '  s08.salary - s07.salary\r\n' +
        'FROM\r\n' +
        '  sample_07 s07 JOIN sample_08 s08\r\n' +
        'ON ( s07.code = s08.code)\r\n' +
        'WHERE\r\n' +
        '  s07.salary < s08.salary\r\n' +
        'ORDER BY s08.salary-s07.salary DESC\r\n' +
        'LIMIT 1000;',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 9, first_column: 1, last_column: 11 } },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 }, identifierChain: [{ name: 'sample_07' }] },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 12, last_column: 23 }, identifierChain: [{ name: 'description' }], tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 }, identifierChain: [{ name: 'sample_07' }] },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 29, last_column: 35 }, identifierChain: [{ name: 'salary' }], tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 37, last_column: 40 }, identifierChain: [{ name: 'sample_08' }] },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 47 }, identifierChain: [{ name: 'salary' }], tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }] },
          { type: 'table', location: { first_line: 2, last_line: 2, first_column: 3, last_column: 6 }, identifierChain: [{ name: 'sample_08' }] },
          { type: 'column', location: { first_line: 2, last_line: 2, first_column: 7, last_column: 13 }, identifierChain: [{ name: 'salary' }], tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }] },
          { type: 'table', location: { first_line: 2, last_line: 2, first_column: 16, last_column: 19 }, identifierChain: [{ name: 'sample_07' }] },
          { type: 'column', location: { first_line: 2, last_line: 2, first_column: 20, last_column: 26 }, identifierChain: [{ name: 'salary' }], tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }] },
          { type: 'table', location: { first_line: 4, last_line: 4, first_column: 3, last_column: 12 }, identifierChain: [{ name: 'sample_07' }] },
          { type: 'table', location: { first_line: 4, last_line: 4, first_column: 22, last_column: 31 }, identifierChain: [{ name: 'sample_08' }] },
          { type: 'table', location: { first_line: 5, last_line: 5, first_column: 6, last_column: 9 }, identifierChain: [{ name: 'sample_07' }] },
          { type: 'column', location: { first_line: 5, last_line: 5, first_column: 10, last_column: 14 }, identifierChain: [{ name: 'code' }], tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }] },
          { type: 'table', location: { first_line: 5, last_line: 5, first_column: 17, last_column: 20 }, identifierChain: [{ name: 'sample_08' }] },
          { type: 'column', location: { first_line: 5, last_line: 5, first_column: 21, last_column: 25 }, identifierChain: [{ name: 'code' }], tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }] },
          { type: 'table', location: { first_line: 7, last_line: 7, first_column: 3, last_column: 6 }, identifierChain: [{ name: 'sample_07' }] },
          { type: 'column', location: { first_line: 7, last_line: 7, first_column: 7, last_column: 13 }, identifierChain: [{ name: 'salary' }], tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }] },
          { type: 'table', location: { first_line: 7, last_line: 7, first_column: 16, last_column: 19 }, identifierChain: [{ name: 'sample_08' }] },
          { type: 'column', location: { first_line: 7, last_line: 7, first_column: 20, last_column: 26 }, identifierChain: [{ name: 'salary' }], tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }] },
          { type: 'table', location: { first_line: 8, last_line: 8, first_column: 10, last_column: 13 }, identifierChain: [{ name: 'sample_08' }] },
          { type: 'column', location: { first_line: 8, last_line: 8, first_column: 14, last_column: 20 }, identifierChain: [{ name: 'salary' }], tables: [{ identifierChain: [{ name: 'sample_08' }], alias: 's08' }] },
          { type: 'table', location: { first_line: 8, last_line: 8, first_column: 21, last_column: 24 }, identifierChain: [{ name: 'sample_07' }] },
          { type: 'column', location: { first_line: 8, last_line: 8, first_column: 25, last_column: 31 }, identifierChain: [{ name: 'salary'}], tables: [{ identifierChain: [{ name: 'sample_07' }], alias: 's07' }]}
        ]
      });
    });

    it('should report locations for "SELECT * FROM foo WHERE bar IN (id+1-1, id+1-2);|"', function() {
      assertLocations({
        beforeCursor: 'SELECT * FROM foo WHERE bar IN (id+1-1, id+1-2);',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 48 } },
          { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'foo' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 }, identifierChain: [{ name: 'foo' }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 }, identifierChain:[{ name: 'bar'}], tables: [{ identifierChain: [{ name: 'foo' }] }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 33, last_column: 35 }, identifierChain: [{ name: 'id'}], tables: [{ identifierChain: [{ name: 'foo' }] }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 43 }, identifierChain: [{ name: 'id'}], tables: [{ identifierChain: [{ name: 'foo' }] }]}
        ]
      });
    });

    it('should handle "select bl from blablabla join (select * from blablabla) s1;', function () {
      assertLocations({
        beforeCursor: 'select bl from blablabla join (select * from blablabla) s1;',
        afterCursor: '',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 59 } },
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'bl' }], tables: [{ identifierChain: [{ name: 'blablabla' }] }, { subQuery: 's1' }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 16, last_column: 25 }, identifierChain: [{ name: 'blablabla' }] },
          { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 39, last_column: 40 }, tables: [{ identifierChain: [{ name: 'blablabla' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 46, last_column: 55 }, identifierChain: [{ name: 'blablabla' }] }]

      });
    });

    it('should report locations for "SELECT CASE cos(boo.a) > baa.boo \\n' +
        '\\tWHEN baa.b THEN true \\n' +
        '\\tWHEN boo.c THEN false \\n' +
        '\\tWHEN baa.blue THEN boo.d \\n' +
        '\\tELSE baa.e END \\n' +
        '\\t FROM db1.foo boo, bar baa WHERE baa.bla IN (SELECT ble FROM bla);|"', function() {
      assertLocations({
        beforeCursor: 'SELECT CASE cos(boo.a) > baa.boo \n\tWHEN baa.b THEN true \n\tWHEN boo.c THEN false \n\tWHEN baa.blue THEN boo.d \n\tELSE baa.e END \n\t FROM db1.foo boo, bar baa WHERE baa.bla IN (SELECT ble FROM bla);',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 6, first_column: 1, last_column: 67 } },
          { type: 'function', location: { first_line: 1, last_line: 1, first_column: 13, last_column: 15 }, function: 'cos'},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 17, last_column: 20 }, identifierChain: [{ name: 'db1' },{ name: 'foo' }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 21, last_column: 22 }, identifierChain: [{ name: 'a' }], tables: [{ identifierChain: [{ name: 'db1' }, { name: 'foo' }], alias: 'boo' }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 29 }, identifierChain: [{ name: 'bar' }]},
          { type: 'column', location: { first_line: 1, last_line: 1, first_column: 30, last_column: 33 }, identifierChain: [{ name: 'boo' }], tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }]},
          { type: 'table', location: { first_line: 2, last_line: 2, first_column: 7, last_column: 10 }, identifierChain: [{ name: 'bar' }]},
          { type: 'column', location: { first_line: 2, last_line: 2, first_column: 11, last_column: 12 }, identifierChain: [{ name: 'b' }], tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }]},
          { type: 'table', location: { first_line: 3, last_line: 3, first_column: 7, last_column: 10 }, identifierChain: [{ name: 'db1' },{ name: 'foo' }]},
          { type: 'column', location: { first_line: 3, last_line: 3, first_column: 11, last_column: 12 }, identifierChain: [{ name: 'c' }], tables: [{ identifierChain: [{ name: 'db1' }, { name: 'foo' }], alias: 'boo' }] },
          { type: 'table', location: { first_line: 4, last_line: 4, first_column: 7, last_column: 10 }, identifierChain: [{ name: 'bar' }]},
          { type: 'column', location: { first_line: 4, last_line: 4, first_column: 11, last_column: 15 }, identifierChain: [{ name: 'blue' }], tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }] },
          { type: 'table', location: { first_line: 4, last_line: 4, first_column: 21, last_column: 24 }, identifierChain: [{ name: 'db1' },{ name: 'foo' }]},
          { type: 'column', location: { first_line: 4, last_line: 4, first_column: 25, last_column: 26 }, identifierChain: [{ name: 'd'}], tables: [{ identifierChain: [{ name: 'db1' }, { name: 'foo' }], alias: 'boo' }] },
          { type: 'table', location: { first_line: 5, last_line: 5, first_column: 7, last_column: 10 }, identifierChain: [{ name: 'bar' }]},
          { type: 'column', location: { first_line: 5, last_line: 5, first_column: 11, last_column: 12 }, identifierChain: [{ name: 'e' }], tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }] },
          { type: 'database', location: { first_line: 6, last_line: 6, first_column: 8, last_column: 11 }, identifierChain: [{ name: 'db1' }]},
          { type: 'table', location: { first_line: 6, last_line: 6, first_column: 12, last_column: 15 }, identifierChain: [{ name: 'db1' }, { name: 'foo' }]},
          { type: 'table', location: { first_line: 6, last_line: 6, first_column: 21, last_column: 24 }, identifierChain: [{ name: 'bar' }]},
          { type: 'table', location: { first_line: 6, last_line: 6, first_column: 35, last_column: 38 }, identifierChain: [{ name: 'bar' }]},
          { type: 'column', location: { first_line: 6, last_line: 6, first_column: 39, last_column: 42 }, identifierChain: [{ name: 'bla' }], tables: [{ identifierChain: [{ name: 'bar' }], alias: 'baa' }] },
          { type: 'column', location: { first_line: 6, last_line: 6, first_column: 54, last_column: 57 }, identifierChain: [{ name: 'ble' }], tables: [{ identifierChain: [{ name: 'bla' }] }] },
          { type: 'table', location: { first_line: 6, last_line: 6, first_column: 63, last_column: 66 }, identifierChain: [{ name: 'bla' }]}
        ]
      });
    });

    it('should report locations for "SELECT tta.* FROM testTableA tta, testTableB; |"', function() {
      assertLocations({
        beforeCursor: 'SELECT tta.* FROM testTableA tta, testTableB; ',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 45 } },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11}, identifierChain: [{ name: 'testTableA' }]},
          { type: 'asterisk', location:{ first_line: 1, last_line: 1, first_column: 12, last_column: 13 }, tables: [{ alias: 'tta', identifierChain: [{ name: 'testTableA' }] }] },
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 19, last_column: 29}, identifierChain: [{ name: 'testTableA' }]},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 35, last_column: 45}, identifierChain: [{ name: 'testTableB' }]}
        ]
      });
    });

    it('should report locations for "SELECT COUNT(*) FROM testTable; |"', function () {
      assertLocations({
        beforeCursor: 'SELECT COUNT(*) FROM testTable;',
        expectedLocations: [
          { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 31 } },
          { type: 'function', location:{ first_line: 1, last_line: 1, first_column: 8, last_column: 12}, function: 'count'},
          { type: 'table', location: { first_line: 1, last_line: 1, first_column: 22, last_column: 31}, identifierChain: [{ name: 'testTable' }]}
        ]
      });
    });

    describe('HDFS paths', function () {
      it('should report locations for "LOAD DATA LOCAL INPATH \'/some/path/file.ble\' OVERWRITE INTO TABLE bla; |"', function () {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'LOAD DATA LOCAL INPATH \'/some/path/file.ble\' OVERWRITE INTO TABLE bla;',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 70 } },
            { type: 'hdfs', location: {first_line: 1, last_line: 1, first_column: 25, last_column: 44}, path: '/some/path/file.ble' },
            { type: 'table', location: {first_line: 1, last_line: 1, first_column: 67, last_column: 70}, identifierChain: [{name: 'bla'}] }
          ]
        });
      });

      it('should report locations for "CREATE TABLE bla (id INT) LOCATION \'/bla/bla/\'; |"', function () {
        assertLocations({
          dialect: 'impala',
          beforeCursor: 'CREATE TABLE bla (id INT) LOCATION \'/bla/bla/\';',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 47 } },
            { type: 'hdfs', location: {first_line: 1, last_line: 1, first_column: 37, last_column: 46}, path: '/bla/bla/' }
          ]
        });
      });
    });

    describe('Hive specific', function () {
      it('should report locations for "SELECT * FROM testTable t1 ORDER BY t1.a ASC, t1.b, t1.c DESC, t1.d;\nSELECT t1.bla FROM testTable2 t1;\\nSELECT * FROM testTable3 t3, testTable4 t4; |"', function () {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT * FROM testTable t1 ORDER BY t1.a ASC, t1.b, t1.c DESC, t1.d;\nSELECT t1.bla FROM testTable2 t1;\nSELECT * FROM testTable3 t3, testTable4 t4; ',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 68 } },
            { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, tables: [{ alias: 't1', identifierChain: [{ name: 'testTable' }] }] },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 24 }, identifierChain: [{ name: 'testTable' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 37, last_column: 39 }, identifierChain: [{ name: 'testTable' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 40, last_column: 41 }, identifierChain: [{ name: 'a' }], tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 47, last_column: 49 }, identifierChain: [{ name: 'testTable' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 50, last_column: 51 }, identifierChain: [{ name: 'b' }], tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 53, last_column: 55 }, identifierChain: [{ name: 'testTable' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 56, last_column: 57 }, identifierChain: [{ name: 'c' }], tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 64, last_column: 66 }, identifierChain: [{ name: 'testTable' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 67, last_column: 68 }, identifierChain: [{ name: 'd' }], tables: [{ identifierChain: [{ name: 'testTable' }], alias: 't1' }]},
            { type: 'statement', location: { first_line: 1, last_line: 2, first_column: 69, last_column: 33 } },
            { type: 'table', location: { first_line: 2, last_line: 2, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'testTable2' }]},
            { type: 'column', location: { first_line: 2, last_line: 2, first_column: 11, last_column: 14 }, identifierChain: [{ name: 'bla' }], tables: [{ identifierChain: [{ name: 'testTable2' }], alias: 't1' }]},
            { type: 'table', location: { first_line: 2, last_line: 2, first_column: 20, last_column: 30 }, identifierChain: [{ name: 'testTable2' }]},
            { type: 'statement', location: { first_line: 2, last_line: 3, first_column: 34, last_column: 43 } },
            { type: 'asterisk', location: { first_line: 3, last_line: 3, first_column: 8, last_column: 9 }, tables: [{ alias: 't3', identifierChain: [{ name: 'testTable3' }]}, { alias: 't4', identifierChain: [{ name: 'testTable4' }] }] },
            { type: 'table', location: { first_line: 3, last_line: 3, first_column: 15, last_column: 25 }, identifierChain: [{ name: 'testTable3' }]},
            { type: 'table', location: { first_line: 3, last_line: 3, first_column: 30, last_column: 40 }, identifierChain: [{ name: 'testTable4' }]}
          ]
        });
      });

      it('should report locations for "SELECT t1.foo FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (t1.c1 = table2.c2); |"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT t1.foo FROM table1 t1 CROSS JOIN table2 LEFT OUTER JOIN table3 JOIN table4 t4 ON (t1.c1 = table2.c2); ',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 108 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 10 }, identifierChain: [{ name: 'table1' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 11, last_column: 14 }, identifierChain: [{ name: 'foo' }], tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 20, last_column: 26 }, identifierChain: [{ name: 'table1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 47 }, identifierChain: [{ name: 'table2' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 64, last_column: 70 }, identifierChain: [{ name: 'table3' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 76, last_column: 82 }, identifierChain: [{ name: 'table4' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 90, last_column: 92 }, identifierChain: [{ name: 'table1' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 93, last_column: 95 }, identifierChain: [{ name: 'c1' }], tables: [{ identifierChain: [{ name: 'table1' }], alias: 't1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 98, last_column: 104 }, identifierChain: [{ name: 'table2' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 105, last_column: 107 }, identifierChain: [{ name: 'c2' }], tables: [{ identifierChain: [{ name: 'table2' }] }]}
          ]
        });
      });

      it('should report locations for "SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);|"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT * FROM foo WHERE bar IN (SELECT * FROM bla);',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 51 } },
            { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'foo' }] }] },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 18 }, identifierChain: [{ name: 'foo' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 25, last_column: 28 }, identifierChain:[{ name: 'bar'}], tables: [{ identifierChain: [{ name: 'foo' }] }]},
            { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 40, last_column: 41 }, tables: [{ identifierChain: [{ name: 'bla' }] }] },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 47, last_column: 50 }, identifierChain: [{ name: 'bla' }]}
          ]
        });
      });

      it('should report locations for "SELECT   |    FROM    testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT   ',
          afterCursor: '    FROM    testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 32 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 22, last_column: 32}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT   a.|    FROM    testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT   a.',
          afterCursor: '    FROM    testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 34 } },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 10, last_column: 11 }, identifierChain: [{ name: 'a' }], tables: [{ identifierChain: [{ name: 'testTableA' }] }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 24, last_column: 34}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT aaa| FROM testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT aaa',
          afterCursor: ' FROM testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 27 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 17, last_column: 27}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT aaa| \\nFROM testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT aaa',
          afterCursor: ' \nFROM testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 2, first_column: 1, last_column: 16 } },
            { type: 'table', location: { first_line: 2, last_line: 2, first_column: 6, last_column: 16}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT |bbbb FROM testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT ',
          afterCursor: 'bbbb FROM testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 28 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 18, last_column: 28}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT aaaaa|bbbb FROM testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 33 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 23, last_column: 33}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT foo.aaaaa|bbbb FROM testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT foo.aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 37 } },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11}, identifierChain: [{ name: 'foo' }], tables: [{ identifierChain: [{ name: 'testTableA' }] }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 27, last_column: 37}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT b, foo.aaaaa|bbbb FROM testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT b, foo.aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 40 } },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9}, identifierChain: [{ name: 'b' }], tables: [{ identifierChain: [{ name: 'testTableA' }] }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 11, last_column: 14}, identifierChain: [{ name: 'foo' }], tables: [{ identifierChain: [{ name: 'testTableA' }] }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 30, last_column: 40}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT foo, aaaaa|bbbb FROM testTableA"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT foo, aaaaa',
          afterCursor: 'bbbb FROM testTableA',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 38 } },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11}, identifierChain: [{ name: 'foo' }], tables: [{ identifierChain: [{ name: 'testTableA' }] }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 28, last_column: 38}, identifierChain: [{ name: 'testTableA' }]}
          ]
        });
      });

      it('should report locations for "SELECT tbl.col FROM some_tbl tbl;"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT tbl.col FROM some_tbl tbl;',
          afterCursor: '',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 33 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 }, identifierChain: [{ name: 'some_tbl' }] },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 }, identifierChain: [{ name: 'col' }], tables: [{ identifierChain: [{ name: 'some_tbl' }], alias: 'tbl' }] },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 21, last_column: 29 }, identifierChain: [{ name: 'some_tbl' }] }
          ]
        });
      });

      it('should report locations for "SELECT tbl.col.cplx FROM some_tbl tbl;"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT tbl.col.cplx FROM some_tbl tbl;',
          afterCursor: '',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 38 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 }, identifierChain: [{ name: 'some_tbl' }] },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 }, identifierChain: [{ name: 'col' }], tables: [{ identifierChain: [{ name: 'some_tbl' }], alias: 'tbl' }] },
            { type: 'complex', location: { first_line: 1, last_line: 1, first_column: 16, last_column: 20 }, identifierChain: [{ name: 'col' }, { name: 'cplx' }], tables: [{ identifierChain: [{ name: 'some_tbl' }], alias: 'tbl' }] },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 34 }, identifierChain: [{ name: 'some_tbl' }] }
          ]
        });
      });

      it('should report locations for "SELECT some_tbl.col.cplx FROM some_tbl;"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT some_tbl.col.cplx FROM some_tbl;',
          afterCursor: '',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 39 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 16 }, identifierChain: [{ name: 'some_tbl' }] },
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 17, last_column: 20 }, identifierChain: [{ name: 'col' }], tables: [{ identifierChain: [{ name: 'some_tbl' }] }] },
            { type: 'complex', location: { first_line: 1, last_line: 1, first_column: 21, last_column: 25 }, identifierChain: [{ name: 'col' }, { name: 'cplx' }], tables: [{ identifierChain: [{ name: 'some_tbl' }] }] },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 31, last_column: 39 }, identifierChain: [{ name: 'some_tbl' }] }
          ]
        });
      });


      it('should report locations for "SELECT testTableB.a, cos(1), tta.abcdefg|hijk, tta.bla, cos(1) FROM testTableA tta, testTableB;"', function() {
        assertLocations({
          dialect: 'hive',
          beforeCursor: 'SELECT testTableB.a, cos(1), tta.abcdefg',
          afterCursor: 'hijk, tta.bla, cos(1) FROM testTableA tta, testTableB;',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 94 } },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 18 }, identifierChain: [{ name: 'testTableB' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 19, last_column: 20 }, identifierChain: [{ name: 'a' }], tables: [{ identifierChain: [{ name: 'testTableB' }] }]},
            { type: 'function', location: { first_line: 1, last_line: 1, first_column: 22, last_column: 24 }, function: 'cos' },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 30, last_column: 33 }, identifierChain: [{ name: 'testTableA' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 47, last_column: 50 }, identifierChain: [{ name: 'testTableA' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 51, last_column: 54 }, identifierChain: [{ name: 'bla' }], tables: [{ identifierChain: [{ name: 'testTableA' }], alias: 'tta' }]},
            { type: 'function', location: { first_line: 1, last_line: 1, first_column: 56, last_column: 58 }, function: 'cos' },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 68, last_column: 78 }, identifierChain: [{ name: 'testTableA' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 84, last_column: 94 }, identifierChain: [{ name: 'testTableB' }]}
          ]
        });
      });
    });

    describe('Impala specific', function () {
      it('should report locations for "SELECT tmp.bc, ROUND(tmp.r, 2) AS r FROM ( SELECT tstDb1.b1.cat AS bc, SUM(tstDb1.b1.price * tran.qua) AS r FROM tstDb1.b1 JOIN [SHUFFLE] tran ON ( tran.b_id = tstDb1.b1.id AND YEAR(tran.tran_d) BETWEEN 2008 AND 2010) GROUP BY tstDb1.b1.cat) tmp ORDER BY r DESC LIMIT 60; |"', function () {
        assertLocations({
          dialect: 'impala',
          beforeCursor: 'SELECT tmp.bc, ROUND(tmp.r, 2) AS r FROM ( SELECT tstDb1.b1.cat AS bc, SUM(tstDb1.b1.price * tran.qua) AS r FROM tstDb1.b1 JOIN [SHUFFLE] tran ON ( tran.b_id = tstDb1.b1.id AND YEAR(tran.tran_d) BETWEEN 2008 AND 2010) GROUP BY tstDb1.b1.cat) tmp ORDER BY r DESC LIMIT 60;',
          afterCursor: '',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 271 } },
            { type: 'subQuery', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 }, identifierChain: [{ subQuery: 'tmp' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 12, last_column: 14 }, identifierChain: [{ name: 'bc' }], tables: [{ subQuery: 'tmp' }]},
            { type: 'function', location: { first_line: 1, last_line: 1, first_column: 16, last_column: 20 }, function: 'round' },
            { type: 'subQuery', location: { first_line: 1, last_line: 1, first_column: 22, last_column: 25 }, identifierChain: [{ subQuery: 'tmp' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 26, last_column: 27 }, identifierChain: [{ name: 'r' }], tables: [{ subQuery: 'tmp' }]},
            { type: 'database', location: { first_line: 1, last_line: 1, first_column: 51, last_column: 57 }, identifierChain: [{ name: 'tstDb1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 58, last_column: 60 }, identifierChain: [{ name:'tstDb1' }, { name: 'b1' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 61, last_column: 64 }, identifierChain: [{ name: 'cat' }], tables: [{ identifierChain: [{ name:'tstDb1' }, {name: 'b1' }] }]},
            { type: 'function', location: { first_line: 1, last_line: 1, first_column: 72, last_column: 74 }, function: 'sum' },
            { type: 'database', location: { first_line: 1, last_line: 1, first_column: 76, last_column: 82 }, identifierChain: [{ name: 'tstDb1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 83, last_column: 85 }, identifierChain: [{ name:'tstDb1' }, { name: 'b1' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 86, last_column: 91 }, identifierChain: [{ name: 'price' }], tables: [{ identifierChain: [{ name:'tstDb1' }, {name: 'b1' }] }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 94, last_column: 98 }, identifierChain: [{ name:'tran' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 99, last_column: 102 }, identifierChain: [{name: 'qua' }], tables: [{ identifierChain: [{ name:'tran' }] }]},
            { type: 'database', location: { first_line: 1, last_line: 1, first_column: 114, last_column: 120 }, identifierChain: [{ name: 'tstDb1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 121, last_column: 123 }, identifierChain: [{ name:'tstDb1' },{ name: 'b1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 139, last_column: 143 }, identifierChain: [{ name:'tran' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 149, last_column: 153 }, identifierChain: [{ name:'tran' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 154, last_column: 158 }, identifierChain: [{ name: 'b_id' }], tables: [{ identifierChain: [{ name:'tran' }] }]},
            { type: 'database', location: { first_line: 1, last_line: 1, first_column: 161, last_column: 167 }, identifierChain: [{ name: 'tstDb1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 168, last_column: 170 }, identifierChain: [{ name:'tstDb1' },{ name: 'b1' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 171, last_column: 173 }, identifierChain: [{ name: 'id' }], tables: [{ identifierChain: [{ name:'tstDb1' }, {name: 'b1' }] }]},
            { type: 'function', location: { first_line: 1, last_line: 1, first_column: 178, last_column: 181 }, function: 'year' },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 183, last_column: 187 }, identifierChain: [{ name:'tran' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 188, last_column: 194 }, identifierChain: [{ name: 'tran_d' }], tables: [{ identifierChain: [{ name:'tran' }] }]},
            { type: 'database', location: { first_line: 1, last_line: 1, first_column: 228, last_column: 234 }, identifierChain: [{ name: 'tstDb1' }]},
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 235, last_column: 237 }, identifierChain: [{ name:'tstDb1' },{ name: 'b1' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 238, last_column: 241 }, identifierChain: [{ name: 'cat' }], tables: [{ identifierChain: [{ name:'tstDb1' }, {name: 'b1' }] }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 256, last_column: 257 }, identifierChain: [{ name: 'r' }], tables: [{ subQuery: 'tmp' }]}
          ]
        });
      });

      it('should report locations for "SELECT * FROM testTable ORDER BY a ASC, b, c DESC, d; |"', function () {
        assertLocations({
          dialect: 'impala',
          beforeCursor: 'SELECT * FROM testTable ORDER BY a ASC, b, c DESC, d; ',
          afterCursor: '',
          expectedLocations: [
            { type: 'statement', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 53 } },
            { type: 'asterisk', location: { first_line: 1, last_line: 1, first_column: 8, last_column: 9 }, tables: [{ identifierChain: [{ name: 'testTable' }] }] },
            { type: 'table', location: { first_line: 1, last_line: 1, first_column: 15, last_column: 24 }, identifierChain: [{ name: 'testTable' }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 34, last_column: 35 }, identifierChain: [{ name: 'a'}], tables: [{ identifierChain: [{ name:'testTable' }] }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 41, last_column: 42 }, identifierChain: [{ name: 'b'}], tables: [{ identifierChain: [{ name:'testTable' }] }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 44, last_column: 45 }, identifierChain: [{ name: 'c'}], tables: [{ identifierChain: [{ name:'testTable' }] }]},
            { type: 'column', location: { first_line: 1, last_line: 1, first_column: 52, last_column: 53 }, identifierChain: [{ name: 'd'}], tables: [{ identifierChain: [{ name:'testTable' }] }]}
          ]
        });
      });
    })
  });
})();