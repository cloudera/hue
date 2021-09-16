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

import hplsqlStatementsParser from './hplsqlStatementsParser';

describe('hplsqlStatementsParser.js', () => {
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

  const testParser = function (input, expectedOutput) {
    try {
      expectedOutput.forEach(entry => {
        entry.type = 'statement';
      });
      const result = hplsqlStatementsParser.parse(input);
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

  it('should split "CREATE PROCEDURE greet(name STRING)\\nBEGIN\\n  PRINT \'Hello \' || name;END;" correctly', () => {
    testParser("CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;END;", [
      {
        statement: "CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;END;",
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 29 },
        firstToken: 'CREATE'
      }
    ]);
  });

  it('should split "CREATE PROCEDURE greet(name STRING)\\nBEGIN\\n  PRINT \'Hello \' || name;\\nEND;/\\nprint "world";" correctly', () => {
    testParser(
      "CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;\nEND;/\nprint 'world';",
      [
        {
          statement: "CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;\nEND;;",
          location: { first_line: 1, first_column: 0, last_line: 4, last_column: 5 },
          firstToken: 'CREATE'
        },
        {
          statement: "\nprint 'world';",
          location: { first_line: 4, first_column: 5, last_line: 5, last_column: 14 },
          firstToken: 'print'
        }
      ]
    );
  });
});
