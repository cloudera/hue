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

import { SqlStatementsParser } from './types';
import { ParsedSqlStatement } from './sqlStatementsParser';

const stringifySplitResult = function (result) {
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
    if (entry.database) {
      s += ",\n  database: '" + entry.database + "'";
    }
    s += '\n}';
    first = false;
  });
  s += ']';
  return s;
};

export const testParser = function (
  parser: SqlStatementsParser,
  input: string,
  expectedOutput: Array<Partial<ParsedSqlStatement>>
): void {
  try {
    expectedOutput.forEach(entry => {
      entry.type = 'statement';
    });
    const result = parser.parse(input);
    const because =
      '\n\nParser output: ' +
      stringifySplitResult(result) +
      '\nExpected output: ' +
      stringifySplitResult(expectedOutput);

    expect(result).toEqual(expectedOutput, because);
  } catch (error) {
    console.error(error);
    console.warn(error.message);

    fail('Got error');
  }
};

export const runSharedStatementsParserTests = (parser: SqlStatementsParser): void => {
  it('should split "" correctly', () => {
    testParser(parser, '', [
      {
        statement: '',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 0 }
      }
    ]);
  });

  it('should split ";" correctly', () => {
    testParser(parser, ';', [
      {
        statement: ';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }
    ]);
  });

  it('should handle "-" correctly', () => {
    testParser(parser, '-', [
      {
        statement: '-',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }
    ]);
  });

  it('should split "select * from bla" correctly', () => {
    testParser(parser, 'select * from bla', [
      {
        statement: 'select * from bla',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 17 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla;" correctly', () => {
    testParser(parser, 'select * from bla;', [
      {
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla where x = ";";" correctly', () => {
    testParser(parser, 'select * from bla where x = ";";', [
      {
        statement: 'select * from bla where x = ";";',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 32 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select * from bla where x = "; AND boo = 1;\\n\\nUSE db" correctly', () => {
    testParser(parser, 'select * from bla where x = "; AND boo = 1;\n\nUSE db', [
      {
        statement: 'select * from bla where x = "; AND boo = 1;\n\nUSE db',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 6 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "--- Some comment with ; ; \\nselect * from bla where x = ";";" correctly', () => {
    testParser(parser, '--- Some comment with ; ; \nselect * from bla where x = ";";', [
      {
        statement: '--- Some comment with ; ; \nselect * from bla where x = ";";',
        location: { first_line: 1, first_column: 0, last_line: 2, last_column: 32 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select *\n-- bla\n from bla;" correctly', () => {
    testParser(parser, 'select *\n-- bla\n from bla;', [
      {
        statement: 'select *\n-- bla\n from bla;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 10 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "select *\\n/* bla \\n\\n*/\\n from bla;" correctly', () => {
    testParser(parser, 'select *\n/* bla \n\n*/\n from bla;', [
      {
        statement: 'select *\n/* bla \n\n*/\n from bla;',
        location: { first_line: 1, first_column: 0, last_line: 5, last_column: 10 },
        firstToken: 'select'
      }
    ]);
  });

  it('should split "SELECT\\n id -- some ID\\n FROM customers;" correctly', () => {
    testParser(parser, 'SELECT\n id -- some ID\n FROM customers;', [
      {
        statement: 'SELECT\n id -- some ID\n FROM customers;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 16 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT\n id -- some ID;\n FROM customers;" correctly', () => {
    testParser(parser, 'SELECT\n id -- some ID;\n FROM customers;', [
      {
        statement: 'SELECT\n id -- some ID;\n FROM customers;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 16 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT id\\n\\n /* from customers; */ FROM other;" correctly', () => {
    testParser(parser, 'SELECT id\n\n /* from customers; */ FROM other;', [
      {
        statement: 'SELECT id\n\n /* from customers; */ FROM other;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 34 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT `   " correctly', () => {
    testParser(parser, 'SELECT `   ', [
      {
        statement: 'SELECT `   ',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT "   " correctly', () => {
    testParser(parser, 'SELECT "   ', [
      {
        statement: 'SELECT "   ',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 },
        firstToken: 'SELECT'
      }
    ]);
  });

  it('should split "SELECT \'   " correctly', () => {
    testParser(parser, "SELECT '   ", [
      {
        statement: "SELECT '   ",
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 },
        firstToken: 'SELECT'
      }
    ]);
  });
};
