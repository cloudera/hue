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

    var stringifySplitResult = function (result) {
      var s = '[';
      var first = true;
      result.forEach(function (entry) {
        s += first ? '{\n' : ', {\n';
        s += '  statement: \'' + entry.statement.replace(/\n/g, '\\n') + '\',\n';
        s += '  location: { first_line: ' + entry.location.first_line + ', first_column: ' + entry.location.first_column + ', last_line: ' + entry.location.last_line + ', last_column: ' + entry.location.last_column + ' }'
        s += '\n}';
        first = false;
      });
      s += ']';
      return s;
    };

    var testParser = function (input, expectedOutput) {
      try {
        expectedOutput.forEach(function (entry) {
          entry.type = 'statement';
        });
        var result = sqlStatementsParser.parse(input);
        var because = '\n\nParser output: ' + stringifySplitResult(result) + '\nExpected output: ' + stringifySplitResult(expectedOutput);
        expect(result).toEqual(expectedOutput, because);
      } catch (error) {
        console.error(error);
        console.log(error.message);

        fail('Got error');
      }
    };

    it('should split "" correctly', function () {
      testParser('', []);
    });

    it('should split ";" correctly', function () {
      testParser(';', [{
        statement: ';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }]);
    });

    it('should split ";   \\n;   \\r\\n;" correctly', function () {
      testParser(';   \n;   \r\n;', [{
        statement: ';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }, {
        statement: '   \n;',
        location: { first_line: 1, first_column: 1, last_line: 2, last_column: 1 }
      }, {
        statement: '   \r\n;',
        location: { first_line: 2, first_column: 1, last_line: 3, last_column: 1 }
      }]);
    });

    it('should split "select * from bla" correctly', function () {
      testParser('select * from bla', [{
        statement: 'select * from bla',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 17 }
      }]);
    });

    it('should split ";;select * from bla" correctly', function () {
      testParser(';;select * from bla', [{
        statement: ';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 1 }
      }, {
        statement: ';',
        location: { first_line: 1, first_column: 1, last_line: 1, last_column: 2 }
      }, {
        statement: 'select * from bla',
        location: { first_line: 1, first_column: 2, last_line: 1, last_column: 19 }
      }]);
    });

    it('should split "select * from bla;" correctly', function () {
      testParser('select * from bla;', [{
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 }
      }]);
    });

    it('should split "select * from bla;select * from ble" correctly', function () {
      testParser('select * from bla;select * from ble', [{
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 }
      }, {
        statement: 'select * from ble',
        location: { first_line: 1, first_column: 18, last_line: 1, last_column: 35 }
      }]);
    });

    it('should split "select * from bla;;select * from ble" correctly', function () {
      testParser('select * from bla;;select * from ble', [{
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 }
      }, {
        statement: ';',
        location: { first_line: 1, first_column: 18, last_line: 1, last_column: 19 }
      },{
        statement: 'select * from ble',
        location: { first_line: 1, first_column: 19, last_line: 1, last_column: 36 }
      }]);
    });

    it('should split "select * from bla;\\n;select * from ble" correctly', function () {
      testParser('select * from bla;\n;select * from ble', [{
        statement: 'select * from bla;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 18 }
      }, {
        statement: '\n;',
        location: { first_line: 1, first_column: 18, last_line: 2, last_column: 1 }
      },{
        statement: 'select * from ble',
        location: { first_line: 2, first_column: 1, last_line: 2, last_column: 18 }
      }]);
    });

    it('should split "select * \\nfrom bla;\\r\\nselect * from ble;\\n" correctly', function () {
      testParser('select * \nfrom bla;\r\nselect * from ble;\n', [{
        statement: 'select * \nfrom bla;',
        location: { first_line: 1, first_column: 0, last_line: 2, last_column: 9 }
      }, {
        statement: '\r\nselect * from ble;',
        location: { first_line: 2, first_column: 9, last_line: 3, last_column: 18 }
      }]);
    });

    it('should split "select * from bla where x = ";";" correctly', function () {
      testParser('select * from bla where x = ";";', [{
        statement: 'select * from bla where x = ";";',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 32 }
      }]);
    });

    it('should split "select * from bla where x = \';\';\\n\\nSELECT bla FROM foo WHERE y = `;` AND true = false;" correctly', function () {
      testParser('select * from bla where x = \';\';\n\nSELECT bla FROM foo WHERE y = `;` AND true = false;', [{
        statement: 'select * from bla where x = \';\';',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 32 }
      }, {
        statement: '\n\nSELECT bla FROM foo WHERE y = `;` AND true = false;',
        location: { first_line: 1, first_column: 32, last_line: 3, last_column: 51 }
      }]);
    });

    it('should split "select * from bla where x = "; AND boo = 1;\\n\\nUSE db" correctly', function () {
      testParser('select * from bla where x = "; AND boo = 1;\n\nUSE db', [{
        statement: 'select * from bla where x = "; AND boo = 1;\n\nUSE db',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 6 }
      }]);
    });

    it('should split "--- Some comment with ; ; \\nselect * from bla where x = ";";" correctly', function () {
      testParser('--- Some comment with ; ; \nselect * from bla where x = ";";', [{
        statement: '--- Some comment with ; ; \nselect * from bla where x = ";";',
        location: { first_line: 1, first_column: 0, last_line: 2, last_column: 32 }
      }]);
    });

    it('should split "select *\n-- bla\n from bla;" correctly', function () {
      testParser('select *\n-- bla\n from bla;', [{
        statement: 'select *\n-- bla\n from bla;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 10 }
      }]);
    });

    it('should split "select *\\n/* bla \\n\\n*/\\n from bla;" correctly', function () {
      testParser('select *\n/* bla \n\n*/\n from bla;', [{
        statement: 'select *\n/* bla \n\n*/\n from bla;',
        location: { first_line: 1, first_column: 0, last_line: 5, last_column: 10 }
      }]);
    });

    it('should split "SELECT\\n id -- some ID\\n FROM customers;" correctly', function () {
      testParser('SELECT\n id -- some ID\n FROM customers;', [{
        statement: 'SELECT\n id -- some ID\n FROM customers;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 16 }
      }]);
    });

    it('should split "SELECT\n id -- some ID;\n FROM customers;" correctly', function () {
      testParser('SELECT\n id -- some ID;\n FROM customers;', [{
        statement: 'SELECT\n id -- some ID;\n FROM customers;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 16 }
      }]);
    });

    it('should split "SELECT id\\n\\n /* from customers; */ FROM other;" correctly', function () {
      testParser('SELECT id\n\n /* from customers; */ FROM other;', [{
        statement: 'SELECT id\n\n /* from customers; */ FROM other;',
        location: { first_line: 1, first_column: 0, last_line: 3, last_column: 34 }
      }]);
    });

    it('should split "SELECT `   " correctly', function () {
      testParser('SELECT `   ', [{
        statement: 'SELECT `   ',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 }
      }]);
    });

    it('should split "SELECT "   " correctly', function () {
      testParser('SELECT "   ', [{
        statement: 'SELECT "   ',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 }
      }]);
    });

    it('should split "SELECT \'   " correctly', function () {
      testParser('SELECT \'   ', [{
        statement: 'SELECT \'   ',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 11 }
      }]);
    });

    it('should split "SELECT " \\" ;; ", \'"\', \' ;\' from bla; /* \\n\\n"" ; \\n; */ FROM other;" correctly', function () {
      testParser('USE `db;`;\r\nSELECT " \\" ;; ", \'"\', \' ;\' from bla; /* \n\n"" ; \n;  FROM other;*/', [{
        statement: 'USE `db;`;',
        location: { first_line: 1, first_column: 0, last_line: 1, last_column: 10 }
      }, {
        statement: '\r\nSELECT " \\" ;; ", \'"\', \' ;\' from bla;',
        location: { first_line: 1, first_column: 10, last_line: 2, last_column: 37 }
      }, {
        statement: ' /* \n\n"" ; \n;  FROM other;*/',
        location: { first_line: 2, first_column: 37, last_line: 5, last_column: 16 }
      }]);
    });
  });
})();