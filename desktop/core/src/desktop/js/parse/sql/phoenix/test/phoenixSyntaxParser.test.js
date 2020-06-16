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

import phoenixSyntaxParser from '../phoenixSyntaxParser';

describe('phoenixSyntaxParser.js', () => {
  const expectedToStrings = function (expected) {
    return expected.map(ex => ex.text);
  };

  it('should not find errors for ""', () => {
    const result = phoenixSyntaxParser.parseSyntax('', '');

    expect(result).toBeFalsy();
  });

  it('should report incomplete statement for "SEL"', () => {
    const result = phoenixSyntaxParser.parseSyntax('SEL', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should report incomplete statement for "SELECT"', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should report incomplete statement for "SELECT "', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT ', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should not report incomplete statement for "SELECT * FROM tbl"', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT * FROM tbl', '');

    expect(result.incompleteStatement).toBeFalsy();
  });

  it('should not report incomplete statement for "SELECT * FROM tbl LIMIT 1"', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT * FROM tbl LIMIT 1', '');

    expect(result.incompleteStatement).toBeFalsy();
  });

  it('should report incomplete statement for "SELECT * FROM tbl LIMIT "', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT * FROM tbl LIMIT ', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should report incomplete statement for "SELECT * FROM tbl GROUP"', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT * FROM tbl GROUP', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should not find errors for "SELECT *"', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT *', '');

    expect(result).toBeFalsy();
  });

  it('should not report incomplete statement for "SELECT * FR"', () => {
    const result = phoenixSyntaxParser.parseSyntax('SELECT * FR', '');

    expect(result.incompleteStatement).toBeTruthy();
  });

  it('should find errors for "SLELECT "', () => {
    const result = phoenixSyntaxParser.parseSyntax('SLELECT ', '');

    expect(result).toBeTruthy();
    expect(result.text).toEqual('SLELECT');
    expect(result.expected.length).toBeGreaterThan(0);
    expect(result.loc.first_column).toEqual(0);
    expect(result.loc.last_column).toEqual(7);
  });

  it('should find errors for "alter tabel "', () => {
    const result = phoenixSyntaxParser.parseSyntax('alter tabel ', '');

    expect(result).toBeTruthy();
    expect(result.text).toEqual('tabel');
    expect(result.expected.length).toBeGreaterThan(0);
    expect(result.loc.first_column).toEqual(6);
    expect(result.loc.last_column).toEqual(11);
  });

  it('should find errors for "select *  form "', () => {
    const result = phoenixSyntaxParser.parseSyntax('select *  form ', '');

    expect(result).toBeTruthy();
    expect(result.loc.first_column).toEqual(10);
    expect(result.loc.last_column).toEqual(14);
    expect(expectedToStrings(result.expected)).toEqual(['from', 'union']);
  });

  it('should find errors for "select * from customers c cultster by awasd asd afd;"', () => {
    const result = phoenixSyntaxParser.parseSyntax(
      'select * from customers c cultster by awasd asd afd;',
      ''
    );

    expect(result).toBeTruthy();
  });

  it('should find errors for "select asdf wer qwer qewr   qwer"', () => {
    const result = phoenixSyntaxParser.parseSyntax('select asdf wer qwer qewr   qwer', '');

    expect(result).toBeTruthy();
  });

  it('should suggest expected words for "SLELECT "', () => {
    const result = phoenixSyntaxParser.parseSyntax('SLELECT ', '');

    expect(result).toBeTruthy();
    expect(expectedToStrings(result.expected)).toEqual([
      'SELECT',
      'SET',
      'ALTER',
      'INSERT',
      'CREATE',
      'USE',
      'DROP',
      'TRUNCATE',
      'UPDATE',
      'WITH'
    ]);
  });

  it('should suggest expected words for "slelect "', () => {
    const result = phoenixSyntaxParser.parseSyntax('slelect ', '');

    expect(result).toBeTruthy();
    expect(expectedToStrings(result.expected)).toEqual([
      'select',
      'set',
      'alter',
      'insert',
      'create',
      'use',
      'drop',
      'truncate',
      'update',
      'with'
    ]);
  });

  it('should suggest expected that the statement should end for "use somedb extrastuff "', () => {
    const result = phoenixSyntaxParser.parseSyntax('use somedb extrastuff  ', '');

    expect(result).toBeTruthy();
    expect(result.expectedStatementEnd).toBeTruthy();
  });

  const expectEqualIds = function (beforeA, afterA, beforeB, afterB) {
    const resultA = phoenixSyntaxParser.parseSyntax(beforeA, afterA);
    const resultB = phoenixSyntaxParser.parseSyntax(beforeB, afterB);

    expect(resultA).toBeTruthy();
    expect(resultB).toBeTruthy();
    expect(resultA.ruleId).toEqual(resultB.ruleId);
  };

  const expectNonEqualIds = function (beforeA, afterA, beforeB, afterB) {
    const resultA = phoenixSyntaxParser.parseSyntax(beforeA, afterA);
    const resultB = phoenixSyntaxParser.parseSyntax(beforeB, afterB);

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
});
