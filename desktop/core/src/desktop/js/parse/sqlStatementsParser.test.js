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

import sqlStatementsParser from './sqlStatementsParser';
import { testParser, runSharedStatementsParserTests } from './sharedStatementsParserTests.ts';

describe('sqlStatementsParser.js', () => {
  runSharedStatementsParserTests(sqlStatementsParser);

  it('should handle "/" correctly', () => {
    testParser(sqlStatementsParser, '/', [
      {
        statement: '/',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }
    ]);
  });

  it('should split escaped \\ correctly in single quotes', () => {
    testParser(sqlStatementsParser, "SELECT '\\\\';\n SELECT 1;", [
      {
        type: 'statement',
        statement: "SELECT '\\\\';",
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 12 },
        firstToken: 'SELECT'
      },
      {
        type: 'statement',
        statement: '\n SELECT 1;',
        location: { first_line: 1, first_column: 12, last_line: 2, last_column: 10 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split escaped \\ correctly in double quotes', () => {
    testParser(sqlStatementsParser, 'SELECT "\\\\";\n SELECT 1;', [
      {
        type: 'statement',
        statement: 'SELECT "\\\\";',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 12 },
        firstToken: 'SELECT'
      },
      {
        type: 'statement',
        statement: '\n SELECT 1;',
        location: { first_line: 1, first_column: 12, last_line: 2, last_column: 10 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split ";   \\n;   \\r\\n;" correctly', () => {
    testParser(sqlStatementsParser, ';   \n;   \r\n;', [
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

  it('should split ";;select * from bla" correctly', () => {
    testParser(sqlStatementsParser, ';;select * from bla', [
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

  it('should split "select * from bla;select * from ble" correctly', () => {
    testParser(sqlStatementsParser, 'select * from bla;select * from ble', [
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
    testParser(sqlStatementsParser, 'select * from bla;;select * from ble', [
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
    testParser(sqlStatementsParser, 'select * from bla;\n;select * from ble', [
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
    testParser(sqlStatementsParser, 'select * \nfrom bla;\r\nselect * from ble;\n', [
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

  it('should split "select * from bla where x = \';\';\\n\\nSELECT bla FROM foo WHERE y = `;` AND true = false;" correctly', () => {
    testParser(
      sqlStatementsParser,
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

  it('should split "-- Some comment\\n\\n    CREATE TABLE bla (id int); /* some \\nother comment*/ ALTER TABLE boo" correctly', () => {
    testParser(
      sqlStatementsParser,
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
      sqlStatementsParser,
      'USE `db;`;\r\nSELECT " \\" ;; ", \'"\', \' ;\' from bla; /* \n\n"" ; \n;  FROM other;*/',
      [
        {
          statement: 'USE `db;`;',
          location: { first_line: 1, first_column: 0, last_line: 1, last_column: 10 },
          firstToken: 'USE',
          database: 'db;'
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

  it('should find databases in use statements "-- commented USE statement\\nUSE boo;" correctly', () => {
    testParser(sqlStatementsParser, '-- commented USE statement\nUSE boo;/* USE baa; */use `foo`', [
      {
        statement: '-- commented USE statement\nUSE boo;',
        location: { first_line: 1, first_column: 0, last_line: 2, last_column: 8 },
        firstToken: 'USE',
        database: 'boo'
      },
      {
        statement: '/* USE baa; */use `foo`',
        location: { first_line: 2, first_column: 8, last_line: 2, last_column: 31 },
        firstToken: 'use',
        database: 'foo'
      }
    ]);
  });
});
