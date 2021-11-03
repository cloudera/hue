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
import { testParser, runSharedStatementsParserTests } from './sharedStatementsParserTests.ts';

describe('hplsqlStatementsParser.js', () => {
  runSharedStatementsParserTests(hplsqlStatementsParser);

  it('should split "CREATE PROCEDURE greet(name STRING)\\nBEGIN\\n  PRINT \'Hello \' || name;END;" correctly', () => {
    testParser(
      hplsqlStatementsParser,
      "CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;END;",
      [
        {
          type: 'statement',
          statement: "CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;END;",
          location: { first_line: 1, first_column: 0, last_line: 3, last_column: 29 },
          firstToken: 'CREATE'
        }
      ]
    );
  });

  it('should split "CREATE PROCEDURE greet(name STRING)\\nBEGIN\\n  PRINT \'Hello \' || name;\\nEND;/\\nprint "world";" correctly', () => {
    testParser(
      hplsqlStatementsParser,
      "CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;\nEND;/\nprint 'world';",
      [
        {
          type: 'statement',
          statement: "CREATE PROCEDURE greet(name STRING)\nBEGIN\n  PRINT 'Hello ' || name;\nEND;;",
          location: { first_line: 1, first_column: 0, last_line: 4, last_column: 5 },
          firstToken: 'CREATE'
        },
        {
          type: 'statement',
          statement: "\nprint 'world';",
          location: { first_line: 4, first_column: 5, last_line: 5, last_column: 14 },
          firstToken: 'print'
        }
      ]
    );
  });
});
