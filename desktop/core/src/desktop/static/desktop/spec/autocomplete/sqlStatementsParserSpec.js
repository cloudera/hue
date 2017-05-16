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
(function () {
  describe('sqlStatementsParser.js', function () {

    var splitTests = [
      {
        id: 1,
        statements: '',
        expectedResult: []
      }, {
        id: 2,
        statements: 'select * from bla',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 17 } }
        ]
      }, {
        id: 3,
        statements: 'select * from bla;',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla;', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 18 } }
        ]
      }, {
        id: 4,
        statements: 'select * from bla;select * from ble',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla;', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 18 } },
          { type: 'statement', statement: 'select * from ble', location: { first_line: 1, last_line: 1, first_column: 18,  last_column: 35 } }
        ]
      }, {
        id: 5,
        statements: 'select * from bla;;select * from ble',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla;', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 18 } },
          { type: 'statement', statement: ';', location: { first_line: 1, last_line: 1, first_column: 18,  last_column: 19 } },
          { type: 'statement', statement: 'select * from ble', location: { first_line: 1, last_line: 1, first_column: 19,  last_column: 36 } }
        ]
      }, {
        id: 6,
        statements: 'select * from bla;\n;select * from ble',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla;', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 18 } },
          { type: 'statement', statement: '\n;', location: { first_line: 1, last_line: 2, first_column: 18,  last_column: 1 } },
          { type: 'statement', statement: 'select * from ble', location: { first_line: 2, last_line: 2, first_column: 1,  last_column: 18 } }
        ]
      }, {
        id: 5,
        statements: 'select * \nfrom bla;\r\nselect * from ble;\n',
        expectedResult: [
          { type: 'statement', statement: 'select * \nfrom bla;', location: { first_line: 1, last_line: 2, first_column: 0,  last_column: 9 } },
          { type: 'statement', statement: '\r\nselect * from ble;', location: { first_line: 2, last_line: 3, first_column: 9,  last_column: 18 } }
        ]
      }, {
        id: 7,
        statements: 'select * from bla where x = ";";',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla where x = ";";', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 32 } }
        ]
      }, {
        id: 8,
        statements: 'select * from bla where x = \';\';\n\nSELECT bla FROM foo WHERE y = `;` AND true = false;',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla where x = \';\';', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 32 } },
          { type: 'statement', statement: '\n\nSELECT bla FROM foo WHERE y = `;` AND true = false;', location: { first_line: 1, last_line: 3, first_column: 32,  last_column: 51 } }
        ]
      }, {
        id: 9,
        statements: 'select * from bla where x = "; AND boo = 1;\n\nUSE db',
        expectedResult: [
          { type: 'statement', statement: 'select * from bla where x = ', location: { first_line: 1, last_line: 1, first_column: 0,  last_column: 28 } },
          { type: 'statement', statement: ';', location: { first_line: 1, last_line: 1, first_column: 29,  last_column: 30 } },
          { type: 'statement', statement: ' AND boo = 1;', location: { first_line: 1, last_line: 1, first_column: 30,  last_column: 43 } },
          { type: 'statement', statement: '\n\nUSE db', location: { first_line: 1, last_line: 3, first_column: 43,  last_column: 6 } }
        ]
      }, {
        id: 10,
        statements: '--- Some comment with ; ; \nselect * from bla where x = ";";',
        expectedResult: [
          { type: 'statement', statement: '\nselect * from bla where x = ";";', location: { first_line: 1, last_line: 2, first_column: 26,  last_column: 32 } }
        ]
      }, {
        id: 11,
        statements: 'select *\n-- bla\n from bla;',
        expectedResult: [
          { type: 'statement', statement: 'select *\n-- bla\n from bla;', location: { first_line: 1, last_line: 3, first_column: 0,  last_column: 10 } }
        ]
      }, {
        id: 12,
        statements: 'select *\n/* bla \n\n*/\n from bla;',
        expectedResult: [
          { type: 'statement', statement: 'select *\n/* bla \n\n*/\n from bla;', location: { first_line: 1, last_line: 5, first_column: 0,  last_column: 10 } }
        ]
      }
    ];

    splitTests.forEach(function (splitTest) {
      it('should split correctly, test ' + splitTest.id, function () {
        try {
          var result = sqlStatementsParser.parse(splitTest.statements);
          expect(result).toEqual(splitTest.expectedResult);
        } catch (error) {
          fail('Got error');
        }
      });
    });
  });
})();