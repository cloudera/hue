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

import prestoSyntaxParser from '../prestoSyntaxParser';

describe('prestoSyntaxParser.js', () => {
  const expectedToStrings = function (expected) {
    return expected.map(ex => ex.text);
  };

  it('should not find errors for ""', () => {
    const result = prestoSyntaxParser.parseSyntax('', '');

    expect(result).toBeFalsy();
  });

  it('should report incomplete statement for "SEL"', () => {
    const result = prestoSyntaxParser.parseSyntax('SEL', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should report incomplete statement for "SELECT"', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should report incomplete statement for "SELECT "', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT ', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should not report incomplete statement for "SELECT * FROM tbl"', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT * FROM tbl', '');

    expect(result.incompleteStatement).toBeFalsy();
  });

  it('should not report incomplete statement for "SELECT * FROM tbl LIMIT 1"', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT * FROM tbl LIMIT 1', '');

    expect(result.incompleteStatement).toBeFalsy();
  });

  it('should report incomplete statement for "SELECT * FROM tbl LIMIT "', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT * FROM tbl LIMIT ', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should report incomplete statement for "SELECT * FROM tbl GROUP"', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT * FROM tbl GROUP', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should not find errors for "SELECT *"', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT *', '');

    expect(result).toBeFalsy();
  });

  it('should not report incomplete statement for "SELECT * FR"', () => {
    const result = prestoSyntaxParser.parseSyntax('SELECT * FR', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should find errors for "SLELECT "', () => {
    const result = prestoSyntaxParser.parseSyntax('SLELECT ', '');

    expect(result).toBeTruthy();
    expect(result.text).toEqual('SLELECT');
    expect(result.expected.length).toBeGreaterThan(0);
    expect(result.loc.first_column).toEqual(0);
    expect(result.loc.last_column).toEqual(7);
  });

  it('should find errors for "alter tabel "', () => {
    const result = prestoSyntaxParser.parseSyntax('alter tabel ', '');

    expect(result).toBeTruthy();
    expect(result.text).toEqual('tabel');
    expect(result.expected.length).toBeGreaterThan(0);
    expect(result.loc.first_column).toEqual(6);
    expect(result.loc.last_column).toEqual(11);
  });

  it('should find errors for "select *  form "', () => {
    const result = prestoSyntaxParser.parseSyntax('select *  form ', '');

    expect(result).toBeTruthy();
    expect(result.loc.first_column).toEqual(10);
    expect(result.loc.last_column).toEqual(14);
    expect(expectedToStrings(result.expected)).toEqual([
      'from',
      'sort',
      'group',
      'order',
      'where',
      'insert',
      'limit',
      'union',
      'having',
      'window',
      'cluster',
      'distribute'
    ]);
  });

  it('should find errors for "select * from customers c cultster by awasd asd afd;"', () => {
    const result = prestoSyntaxParser.parseSyntax(
      'select * from customers c cultster by awasd asd afd;',
      ''
    );

    expect(result).toBeTruthy();
  });

  it('should find errors for "select asdf wer qwer qewr   qwer"', () => {
    const result = prestoSyntaxParser.parseSyntax('select asdf wer qwer qewr   qwer', '');

    expect(result).toBeTruthy();
  });

  it('should suggest expected words for "SLELECT "', () => {
    const result = prestoSyntaxParser.parseSyntax('SLELECT ', '');

    expect(result).toBeTruthy();
    expect(expectedToStrings(result.expected)).toEqual([
      'SELECT',
      'DELETE',
      'SET',
      'ALTER',
      'INSERT',
      'RELOAD',
      'ABORT',
      'ANALYZE',
      'CREATE',
      'EXPLAIN',
      'EXPORT',
      'GRANT',
      'IMPORT',
      'LOAD',
      'MERGE',
      'MSCK',
      'REVOKE',
      'SHOW',
      'USE',
      'DROP',
      'FROM',
      'TRUNCATE',
      'UPDATE',
      'WITH',
      'DESCRIBE'
    ]);
  });

  it('should suggest expected words for "slelect "', () => {
    const result = prestoSyntaxParser.parseSyntax('slelect ', '');

    expect(result).toBeTruthy();
    expect(expectedToStrings(result.expected)).toEqual([
      'select',
      'delete',
      'set',
      'alter',
      'insert',
      'reload',
      'abort',
      'analyze',
      'create',
      'explain',
      'export',
      'grant',
      'import',
      'load',
      'merge',
      'msck',
      'revoke',
      'show',
      'use',
      'drop',
      'from',
      'truncate',
      'update',
      'with',
      'describe'
    ]);
  });

  it('should suggest expected that the statement should end for "use somedb extrastuff "', () => {
    const result = prestoSyntaxParser.parseSyntax('use somedb extrastuff  ', '');

    expect(result).toBeTruthy();
    expect(result.expectedStatementEnd).toBeTruthy();
  });

  it('should find errors for "select * from sample_07 where and\\n\\nselect unknownCol from sample_07;"', () => {
    const result = prestoSyntaxParser.parseSyntax(
      'select * from sample_07 where and\n\nselect unknownCol from sample_07;',
      '',
      false
    );

    expect(result).toBeTruthy();
  });

  const expectEqualIds = function (beforeA, afterA, beforeB, afterB) {
    const resultA = prestoSyntaxParser.parseSyntax(beforeA, afterA);
    const resultB = prestoSyntaxParser.parseSyntax(beforeB, afterB);

    expect(resultA).toBeTruthy();
    expect(resultB).toBeTruthy();
    expect(resultA.ruleId).toEqual(resultB.ruleId);
  };

  const expectNonEqualIds = function (beforeA, afterA, beforeB, afterB) {
    const resultA = prestoSyntaxParser.parseSyntax(beforeA, afterA);
    const resultB = prestoSyntaxParser.parseSyntax(beforeB, afterB);

    expect(resultA).toBeTruthy();
    expect(resultB).toBeTruthy();
    expect(resultA.ruleId).not.toEqual(resultB.ruleId);
  };

  it('should have unique rule IDs when the same rule is failing in different locations', () => {
    expectEqualIds('SLELECT ', '', 'dlrop ', '');
    expectEqualIds('SELECT * FORM ', '', 'SELECT * bla ', '');
    expectEqualIds('DROP TABLE b.bla ERRROROR ', '', 'DROP TABLE c.cla OTHERERRRRORRR ', '');
    expectEqualIds(
      'SELECT * FROM a WHERE id = 1, a b SELECT ',
      '',
      'SELECT id, foo FROM a WHERE a b SELECT',
      ''
    );
    expectEqualIds(
      'SELECT * FROM a WHERE id = 1, a b SELECT ',
      '',
      'SELECT id, foo FROM a WHERE a b SELECT',
      ''
    );

    expectNonEqualIds('slelect ', '', 'select * form ', '');
  });

  it('should suggest expected words for "SLELECT "', () => {
    const result = prestoSyntaxParser.parseSyntax('SLELECT ', '');

    expect(result).toBeTruthy();
    expect(expectedToStrings(result.expected)).toEqual([
      'SELECT',
      'DELETE',
      'SET',
      'ALTER',
      'INSERT',
      'RELOAD',
      'ABORT',
      'ANALYZE',
      'CREATE',
      'EXPLAIN',
      'EXPORT',
      'GRANT',
      'IMPORT',
      'LOAD',
      'MERGE',
      'MSCK',
      'REVOKE',
      'SHOW',
      'USE',
      'DROP',
      'FROM',
      'TRUNCATE',
      'UPDATE',
      'WITH',
      'DESCRIBE'
    ]);
  });
});
