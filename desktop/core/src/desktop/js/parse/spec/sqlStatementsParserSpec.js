// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import sqlStatementsParser from '../sqlStatementsParser';

describe('sqlStatementsParser.js', () => {
  const stringifySplitResult = function(result) {
    let s = '[';
    let first = true;
    result.forEach(entry => {
      s += first ? '{\n' : ', {\n';
      s += "  statement: '" + entry.statement.replace(/\n/g, '\\n') + "',\n";
      s +=
        '  location: { first_line: ' +
        entry.location.first_line +
        ', first_column: ' +
        entry.location.first_column +
        ', last_line: ' +
        entry.location.last_line +
        ', last_column: ' +
        entry.location.last_column +
        ' }';
      if (entry.firstToken) {
        s += ",\n  firstToken: '" + entry.firstToken + "'";
      }
      s += '\n}';
      first = false;
    });
    s += ']';
    return s;
  };

  const testParser = function(input, expectedOutput) {
    try {
      expectedOutput.forEach(entry => {
        entry.type = 'statement';
      });
      const result = sqlStatementsParser.parse(input);
      const because =
        '\n\nParser output: ' +
        stringifySplitResult(result) +
        '\nExpected output: ' +
        stringifySplitResult(expectedOutput);
      expect(result).toEqual(expectedOutput, because);
    } catch (error) {
      console.error(error);
      console.log(error.message);

      fail('Got error');
    }
  };

  it('should split "" correctly', () => {
    testParser('', []);
  });

  it('should split ";" correctly', () => {
    testParser(';', [
      {
        statement: ';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }
    ]);
  });

  it('should handle "-" correctly', () => {
    testParser('-', [
      {
        statement: '-',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }
    ]);
  });

  it('should handle "/" correctly', () => {
    testParser('/', [
      {
        statement: '/',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }
    ]);
  });

  it('should split ";   \\n;   \\r\\n;" correctly', () => {
    testParser(';   \n;   \r\n;', [
      {
        statement: ';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      },
      {
        statement: '   \n;',
        location: { first_line: 1, first_column: 1, last_line: 2, last_column: 1 }
      },
      {
        statement: '   \r\n;',
        location: { first_line: 2, first_column: 1, last_line: 3, last_column: 1 }
      }
    ]);
  });

  it('should split "select * from bla" correctly', () => {
    testParser('select * from bla', [
      {
        statement: 'select * from bla',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 17 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split ";;select * from bla" correctly', () => {
    testParser(';;select * from bla', [
      {
        statement: ';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      },
      {
        statement: ';',
        location: { first_line: 1, first_column: 1, last_line: 1, last_column: 2 }
      },
      {
        statement: 'select * from bla',
        location: { first_line: 1, first_column: 2, last_line: 1, last_column: 19 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla;" correctly', () => {
    testParser('select * from bla;', [
      {
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla;select * from ble" correctly', () => {
    testParser('select * from bla;select * from ble', [
      {
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 },
        firstToken: 'select'
      },
      {
        statement: 'select * from ble',
        location: { first_line: 1, first_column: 18, last_line: 1, last_column: 35 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla;;select * from ble" correctly', () => {
    testParser('select * from bla;;select * from ble', [
      {
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 },
        firstToken: 'select'
      },
      {
        statement: ';',
        location: { first_line: 1, first_column: 18, last_line: 1, last_column: 19 }
      },
      {
        statement: 'select * from ble',
        location: { first_line: 1, first_column: 19, last_line: 1, last_column: 36 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla;\\n;select * from ble" correctly', () => {
    testParser('select * from bla;\n;select * from ble', [
      {
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 },
        firstToken: 'select'
      },
      {
        statement: '\n;',
        location: { first_line: 1, first_column: 18, last_line: 2, last_column: 1 }
      },
      {
        statement: 'select * from ble',
        location: { first_line: 2, first_column: 1, last_line: 2, last_column: 18 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * \\nfrom bla;\\r\\nselect * from ble;\\n" correctly', () => {
    testParser('select * \nfrom bla;\r\nselect * from ble;\n', [
      {
        statement: 'select * \nfrom bla;',
        location: { first_line: 1, first_column: 0, last_line: 2, last_column: 9 },
        firstToken: 'select'
      },
      {
        statement: '\r\nselect * from ble;',
        location: { first_line: 2, first_column: 9, last_line: 3, last_column: 18 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla where x = ";";" correctly', () => {
    testParser('select * from bla where x = ";";', [
      {
        statement: 'select * from bla where x = ";";',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 32 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla where x = \';\';\\n\\nSELECT bla FROM foo WHERE y = `;` AND true = false;" correctly', () => {
    testParser(
      "select * from bla where x = ';';\n\nSELECT bla FROM foo WHERE y = `;` AND true = false;",
      [
        {
          statement: "select * from bla where x = ';';",
          location: { first_line: 1, first_column: 0, last_line: 1, last_column: 32 },
          firstToken: 'select'
        },
        {
          statement: '\n\nSELECT bla FROM foo WHERE y = `;` AND true = false;',
          location: { first_line: 1, first_column: 32, last_line: 3, last_column: 51 },
          firstToken: 'SELECT'
        }
      ]
    );
  });

  it('should split "select * from bla where x = "; AND boo = 1;\\n\\nUSE db" correctly', () => {
    testParser('select * from bla where x = "; AND boo = 1;\n\nUSE db', [
      {
        statement: 'select * from bla where x = "; AND boo = 1;\n\nUSE db',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 6 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "--- Some comment with ; ; \\nselect * from bla where x = ";";" correctly', () => {
    testParser('--- Some comment with ; ; \nselect * from bla where x = ";";', [
      {
        statement: '--- Some comment with ; ; \nselect * from bla where x = ";";',
        location: { first_line: 1, first_column: 0, last_line: 2, last_column: 32 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select *\n-- bla\n from bla;" correctly', () => {
    testParser('select *\n-- bla\n from bla;', [
      {
        statement: 'select *\n-- bla\n from bla;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 10 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select *\\n/* bla \\n\\n*/\\n from bla;" correctly', () => {
    testParser('select *\n/* bla \n\n*/\n from bla;', [
      {
        statement: 'select *\n/* bla \n\n*/\n from bla;',
        location: { first_line: 1, first_column: 0, last_line: 5, last_column: 10 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "SELECT\\n id -- some ID\\n FROM customers;" correctly', () => {
    testParser('SELECT\n id -- some ID\n FROM customers;', [
      {
        statement: 'SELECT\n id -- some ID\n FROM customers;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 16 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT\n id -- some ID;\n FROM customers;" correctly', () => {
    testParser('SELECT\n id -- some ID;\n FROM customers;', [
      {
        statement: 'SELECT\n id -- some ID;\n FROM customers;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 16 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT id\\n\\n /* from customers; */ FROM other;" correctly', () => {
    testParser('SELECT id\n\n /* from customers; */ FROM other;', [
      {
        statement: 'SELECT id\n\n /* from customers; */ FROM other;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 34 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT `   " correctly', () => {
    testParser('SELECT `   ', [
      {
        statement: 'SELECT `   ',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT "   " correctly', () => {
    testParser('SELECT "   ', [
      {
        statement: 'SELECT "   ',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT \'   " correctly', () => {
    testParser("SELECT '   ", [
      {
        statement: "SELECT '   ",
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "-- Some comment\\n\\n    CREATE TABLE bla (id int); /* some \\nother comment*/ ALTER TABLE boo" correctly', () => {
    testParser(
      '-- Some comment\n\n    CREATE TABLE bla (id int); /* some \nother comment*/ ALTER TABLE boo',
      [
        {
          statement: '-- Some comment\n\n    CREATE TABLE bla (id int);',
          location: { first_line: 1, first_column: 0, last_line: 3, last_column: 30 },
          firstToken: 'CREATE'
        },
        {
          statement: ' /* some \nother comment*/ ALTER TABLE boo',
          location: { first_line: 3, first_column: 30, last_line: 4, last_column: 31 },
          firstToken: 'ALTER'
        }
      ]
    );
  });

  it('should split "SELECT " \\" ;; ", \'"\', \' ;\' from bla; /* \\n\\n"" ; \\n; */ FROM other;" correctly', () => {
    testParser(
      'USE `db;`;\r\nSELECT " \\" ;; ", \'"\', \' ;\' from bla; /* \n\n"" ; \n;  FROM other;*/',
      [
        {
          statement: 'USE `db;`;',
          location: { first_line: 1, first_column: 0, last_line: 1, last_column: 10 },
          firstToken: 'USE'
        },
        {
          statement: '\r\nSELECT " \\" ;; ", \'"\', \' ;\' from bla;',
          location: { first_line: 1, first_column: 10, last_line: 2, last_column: 37 },
          firstToken: 'SELECT'
        },
        {
          statement: ' /* \n\n"" ; \n;  FROM other;*/',
          location: { first_line: 2, first_column: 37, last_line: 5, last_column: 16 }
        }
      ]
    );
  });
});
