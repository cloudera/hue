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
  describe('sqlSyntaxParser.js', function() {

    var expectedToStrings = function (expected) {
      return $.map(expected, function(ex) { return ex.text; })
    };

    it('should not find errors for ""', function () {
      var result = sqlSyntaxParser.parseSyntax('', '');
      expect(result).toBeFalsy();
    });

    it('should report incomplete statement for "SEL"', function () {
      var result = sqlSyntaxParser.parseSyntax('SEL', '');
      expect(result.incompleteStatement).toBeTruthy();
    });

    it('should report incomplete statement for "SELECT"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT', '');
      expect(result.incompleteStatement).toBeTruthy();
    });

    it('should report incomplete statement for "SELECT "', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT ', '');
      expect(result.incompleteStatement).toBeTruthy();
    });

    it('should not report incomplete statement for "SELECT * FROM tbl"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT * FROM tbl', '');
      expect(result.incompleteStatement).toBeFalsy();
    });

    it('should not report incomplete statement for "SELECT * FROM tbl LIMIT 1"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT * FROM tbl LIMIT 1', '');
      expect(result.incompleteStatement).toBeFalsy();
    });

    it('should report incomplete statement for "SELECT * FROM tbl LIMIT "', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT * FROM tbl LIMIT ', '');
      expect(result.incompleteStatement).toBeTruthy();
    });

    it('should report incomplete statement for "SELECT * FROM tbl GROUP"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT * FROM tbl GROUP', '');
      expect(result.incompleteStatement).toBeTruthy();
    });

    it('should not find errors for "SELECT *"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT *', '');
      expect(result).toBeFalsy();
    });

    it('should not report incomplete statement for "SELECT * FR"', function () {
      var result = sqlSyntaxParser.parseSyntax('SELECT * FR', '');
      expect(result.incompleteStatement).toBeTruthy();
    });

    it('should find errors for "SLELECT "', function() {
      var result = sqlSyntaxParser.parseSyntax('SLELECT ', '');
      expect(result).toBeTruthy();
      expect(result.text).toEqual('SLELECT');
      expect(result.expected.length).toBeGreaterThan(0);
      expect(result.loc.first_column).toEqual(0);
      expect(result.loc.last_column).toEqual(7);
    });

    it('should find errors for "alter tabel "', function() {
      var result = sqlSyntaxParser.parseSyntax('alter tabel ', '');
      expect(result).toBeTruthy();
      expect(result.text).toEqual('tabel');
      expect(result.expected.length).toBeGreaterThan(0);
      expect(result.loc.first_column).toEqual(6);
      expect(result.loc.last_column).toEqual(11);
    });

    it('should find errors for "select *  form "', function () {
      var result = sqlSyntaxParser.parseSyntax('select *  form ', '');
      expect(result).toBeTruthy();
      expect(result.loc.first_column).toEqual(10);
      expect(result.loc.last_column).toEqual(14);
      expect(expectedToStrings(result.expected)).toEqual(['from', 'group', 'order', 'where', 'limit', 'union', 'having']);
    });

    it('should find errors for "select * from customers c cultster by awasd asd afd;"', function () {
      var result = sqlSyntaxParser.parseSyntax('select * from customers c cultster by awasd asd afd;', '');
      expect(result).toBeTruthy();
    });

    it('should find errors for "select asdf wer qwer qewr   qwer"', function () {
      var result = sqlSyntaxParser.parseSyntax('select asdf wer qwer qewr   qwer', '');
      expect(result).toBeTruthy();
    });

    it('should find errors for "select * from foo where method = 1;"', function () {
      var result = sqlSyntaxParser.parseSyntax('select * from foo where method = 1;', '', 'impala');
      expect(result).toBeTruthy();
      expect(result.expected.some(function (expected) { return expected.text === '`method`' })).toBeTruthy();
      expect(result.expectedIdentifier).toBeTruthy();
      expect(result.possibleReserved).toBeTruthy();
    });

    it('should find errors for "select * from using where a = 1;"', function () {
      var result = sqlSyntaxParser.parseSyntax('select * from using where a = 1;', '', 'hive');
      expect(result).toBeTruthy();
      expect(result.expected.some(function (expected) { return expected.text === '`using`' })).toBeTruthy();
      expect(result.expectedIdentifier).toBeTruthy();
      expect(result.possibleReserved).toBeTruthy();
    });

    it('should suggest expected words for "SLELECT "', function() {
      var result = sqlSyntaxParser.parseSyntax('SLELECT ', '');
      expect(result).toBeTruthy();
      expect(expectedToStrings(result.expected)).toEqual(['SELECT', 'SET', 'ALTER', 'INSERT', 'CREATE', 'SHOW', 'USE', 'DROP', 'FROM', 'TRUNCATE', 'UPDATE', 'WITH']);
    });

    it('should suggest expected words for "slelect "', function() {
      var result = sqlSyntaxParser.parseSyntax('slelect ', '');
      expect(result).toBeTruthy();
      expect(expectedToStrings(result.expected)).toEqual(['select', 'set', 'alter', 'insert', 'create', 'show', 'use', 'drop', 'from', 'truncate', 'update', 'with']);
    });

    it('should suggest expected that the statement should end for "use somedb extrastuff "', function() {
      var result = sqlSyntaxParser.parseSyntax('use somedb extrastuff  ', '');
      expect(result).toBeTruthy();
      expect(result.expectedStatementEnd).toBeTruthy();
    });

    it('should find errors for "select * from sample_07 where and\\n\\nselect unknownCol from sample_07;"', function () {
      var result = sqlSyntaxParser.parseSyntax('select * from sample_07 where and\n\nselect unknownCol from sample_07;', '', 'hive', false);
      expect(result).toBeTruthy();
    });

    var expectEqualIds = function (beforeA, afterA, beforeB, afterB) {
      var resultA = sqlSyntaxParser.parseSyntax(beforeA, afterA);
      var resultB = sqlSyntaxParser.parseSyntax(beforeB, afterB);
      expect(resultA).toBeTruthy('"' + beforeA + '|' + afterA +'" was not reported as an error');
      expect(resultB).toBeTruthy('"' + beforeB + '|' + afterB +'" was not reported as an error');
      expect(resultA.ruleId).toEqual(resultB.ruleId);
    };

    var expectNonEqualIds = function (beforeA, afterA, beforeB, afterB) {
      var resultA = sqlSyntaxParser.parseSyntax(beforeA, afterA);
      var resultB = sqlSyntaxParser.parseSyntax(beforeB, afterB);
      expect(resultA).toBeTruthy('"' + beforeA + '|' + afterA +'" was not reported as an error');
      expect(resultB).toBeTruthy('"' + beforeB + '|' + afterB +'" was not reported as an error');
      expect(resultA.ruleId).not.toEqual(resultB.ruleId);
    };


    it('should have unique rule IDs when the same rule is failing in different locations', function() {
      expectEqualIds('SLELECT ', '', 'dlrop ', '');
      expectEqualIds('SELECT * FORM ', '', 'SELECT * bla ', '');
      expectEqualIds('DROP TABLE b.bla ERRROROR ', '', 'DROP TABLE c.cla OTHERERRRRORRR ', '');
      expectEqualIds('SELECT * FROM a WHERE id = 1, a b SELECT ', '', 'SELECT id, foo FROM a WHERE a b SELECT', '');
      expectEqualIds('SELECT * FROM a WHERE id = 1, a b SELECT ', '', 'SELECT id, foo FROM a WHERE a b SELECT', '');

      expectNonEqualIds('slelect ', '', 'select * form ', '');
    });


    describe('Hive specific', function () {
      it('should suggest expected words for "SLELECT "', function() {
        var result = sqlSyntaxParser.parseSyntax('SLELECT ', '', 'hive');
        expect(result).toBeTruthy();
        expect(expectedToStrings(result.expected)).toEqual(['SELECT', 'DELETE', 'SET', 'ALTER', 'INSERT', 'RELOAD', 'ABORT', 'ANALYZE', 'CREATE', 'EXPLAIN', 'EXPORT', 'GRANT', 'IMPORT', 'LOAD', 'MERGE', 'MSCK', 'REVOKE', 'SHOW', 'USE', 'DROP', 'FROM', 'TRUNCATE', 'UPDATE', 'WITH', 'DESCRIBE']);
      });
    });

    describe('Impala specific', function () {
      it('should suggest expected words for "SLELECT "', function() {
        var result = sqlSyntaxParser.parseSyntax('SLELECT ', '', 'impala');
        expect(result).toBeTruthy();
        expect(expectedToStrings(result.expected)).toEqual(['SELECT', 'DELETE', 'SET', 'ALTER', 'COMMENT', 'INSERT', 'UPSERT', 'CREATE', 'EXPLAIN', 'GRANT', 'LOAD', 'REFRESH', 'REVOKE', 'SHOW', 'USE', 'COMPUTE', 'DROP', 'FROM', 'TRUNCATE', 'UPDATE', 'WITH', 'DESCRIBE', 'INVALIDATE']);
      });
    })

  });
})();