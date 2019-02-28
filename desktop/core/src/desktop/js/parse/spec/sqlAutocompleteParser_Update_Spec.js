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

import SqlTestUtils from './sqlTestUtils';
import sqlAutocompleteParser from '../sqlAutocompleteParser';

describe('sqlAutocompleteParser.js UPDATE statements', () => {
  beforeAll(() => {
    sqlAutocompleteParser.yy.parseError = function(msg) {
      throw Error(msg);
    };
    jasmine.addMatchers(SqlTestUtils.testDefinitionMatcher);
  });

  const assertAutoComplete = SqlTestUtils.assertAutocomplete;

  it('should suggest keywords for "|"', () => {
    assertAutoComplete({
      beforeCursor: '',
      afterCursor: '',
      containsKeywords: ['UPDATE'],
      expectedResult: {
        lowerCase: false
      }
    });
  });

  it('should suggest keywords for "UPDATE bar  |"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE bar  ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['SET'],
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 12 }
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          }
        ]
      }
    });
  });

  it('should suggest keywords for "UPDATE bar SET id=1, foo=2 |"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE bar SET id=1, foo=2 ',
      afterCursor: '',
      containsKeywords: ['WHERE'],
      expectedResult: {
        lowerCase: false,
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 27 }
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 16, last_column: 18 },
            identifierChain: [{ name: 'id' }],
            tables: [{ identifierChain: [{ name: 'bar' }] }],
            qualified: false
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 22, last_column: 25 },
            identifierChain: [{ name: 'foo' }],
            tables: [{ identifierChain: [{ name: 'bar' }] }],
            qualified: false
          }
        ]
      }
    });
  });

  it('should suggest keywords for "UPDATE bar SET id |"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE bar SET id ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestKeywords: ['='],
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 18 }
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 16, last_column: 18 },
            identifierChain: [{ name: 'id' }],
            tables: [{ identifierChain: [{ name: 'bar' }] }],
            qualified: false
          }
        ]
      }
    });
  });

  it('should suggest tables for "UPDATE |"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: {},
        suggestDatabases: {
          appendDot: true
        }
      }
    });
  });

  it('should suggest tables for "UPDATE bla|"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE bla',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: {},
        suggestDatabases: {
          appendDot: true
        }
      }
    });
  });

  it('should suggest tables for "UPDATE bar.|"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE bar.',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: 'bar' }] }
      }
    });
  });

  it('should suggest tables for "UPDATE bar.foo|"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE bar.foo',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestTables: { identifierChain: [{ name: 'bar' }] }
      }
    });
  });

  it('should suggest columns for "UPDATE bar.foo SET |"', () => {
    assertAutoComplete({
      beforeCursor: 'UPDATE bar.foo SET ',
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }] },
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 19 }
          },
          {
            type: 'database',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
            identifierChain: [{ name: 'bar' }, { name: 'foo' }]
          }
        ]
      }
    });
  });

  it('should suggest columns for "UPDATE bar.foo SET id = 1, bla = \'foo\', |"', () => {
    assertAutoComplete({
      beforeCursor: "UPDATE bar.foo SET id = 1, bla = 'foo', ",
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }] },
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 40 }
          },
          {
            type: 'database',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
            identifierChain: [{ name: 'bar' }, { name: 'foo' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 20, last_column: 22 },
            identifierChain: [{ name: 'id' }],
            tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }],
            qualified: false
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 28, last_column: 31 },
            identifierChain: [{ name: 'bla' }],
            tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }],
            qualified: false
          }
        ]
      }
    });
  });

  it('should suggest columns for "UPDATE bar.foo SET bla = \'foo\' WHERE |"', () => {
    assertAutoComplete({
      beforeCursor: "UPDATE bar.foo SET bla = 'foo' WHERE ",
      afterCursor: '',
      expectedResult: {
        lowerCase: false,
        suggestFunctions: {},
        suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }] },
        suggestFilters: { tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }] },
        suggestKeywords: ['EXISTS', 'NOT EXISTS'],
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 37 }
          },
          {
            type: 'database',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
            identifierChain: [{ name: 'bar' }, { name: 'foo' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 20, last_column: 23 },
            identifierChain: [{ name: 'bla' }],
            tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }],
            qualified: false
          }
        ]
      }
    });
  });

  it('should suggest values for "UPDATE bar.foo SET bla = \'foo\' WHERE id = |"', () => {
    assertAutoComplete({
      beforeCursor: "UPDATE bar.foo SET bla = 'foo' WHERE id = ",
      afterCursor: '',
      containsKeywords: ['CASE'],
      expectedResult: {
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 42 }
          },
          {
            type: 'database',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
            identifierChain: [{ name: 'bar' }, { name: 'foo' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 20, last_column: 23 },
            identifierChain: [{ name: 'bla' }],
            tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }],
            qualified: false
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 38, last_column: 40 },
            identifierChain: [{ name: 'id' }],
            tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }],
            qualified: false
          }
        ],
        suggestFunctions: { types: ['COLREF'] },
        suggestValues: {},
        colRef: { identifierChain: [{ name: 'bar' }, { name: 'foo' }, { name: 'id' }] },
        suggestColumns: {
          types: ['COLREF'],
          tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }]
        },
        lowerCase: false
      }
    });
  });

  it('should suggest columns for "UPDATE bar.foo SET bla = \'foo\' WHERE id = 1 AND |"', () => {
    assertAutoComplete({
      beforeCursor: "UPDATE bar.foo SET bla = 'foo' WHERE id = 1 AND ",
      afterCursor: '',
      containsKeywords: ['CASE'],
      expectedResult: {
        lowerCase: false,
        suggestFunctions: {},
        suggestColumns: { tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }] },
        suggestFilters: { tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }] },
        locations: [
          {
            type: 'statement',
            location: { first_line: 1, last_line: 1, first_column: 1, last_column: 48 }
          },
          {
            type: 'database',
            location: { first_line: 1, last_line: 1, first_column: 8, last_column: 11 },
            identifierChain: [{ name: 'bar' }]
          },
          {
            type: 'table',
            location: { first_line: 1, last_line: 1, first_column: 12, last_column: 15 },
            identifierChain: [{ name: 'bar' }, { name: 'foo' }]
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 20, last_column: 23 },
            identifierChain: [{ name: 'bla' }],
            tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }],
            qualified: false
          },
          {
            type: 'column',
            location: { first_line: 1, last_line: 1, first_column: 38, last_column: 40 },
            identifierChain: [{ name: 'id' }],
            tables: [{ identifierChain: [{ name: 'bar' }, { name: 'foo' }] }],
            qualified: false
          }
        ]
      }
    });
  });

  describe('Impala specific', () => {
    it('should suggest keywords for "UPDATE bar.foo SET bla = \'foo\' |"', () => {
      assertAutoComplete({
        beforeCursor: "UPDATE bar.foo SET bla = 'foo' ",
        afterCursor: '',
        dialect: 'impala',
        containsKeywords: ['FROM', 'WHERE'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

    it('should suggest tables for "UPDATE bar.foo SET bla = \'foo\' FROM |"', () => {
      assertAutoComplete({
        beforeCursor: "UPDATE bar.foo SET bla = 'foo' FROM ",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestTables: {},
          suggestDatabases: {
            appendDot: true
          }
        }
      });
    });

    it('should suggest keywords for "UPDATE bar.foo SET bla = \'foo\' FROM boo |"', () => {
      assertAutoComplete({
        beforeCursor: "UPDATE bar.foo SET bla = 'foo' FROM boo ",
        afterCursor: '',
        dialect: 'impala',
        containsKeywords: ['JOIN'],
        expectedResult: {
          lowerCase: false,
          suggestJoins: { prependJoin: true, tables: [{ identifierChain: [{ name: 'boo' }] }] }
        }
      });
    });

    it('should suggest keywords for "UPDATE bar.foo SET bla = \'foo\' FROM boo JOIN |"', () => {
      assertAutoComplete({
        beforeCursor: "UPDATE bar.foo SET bla = 'foo' FROM boo JOIN ",
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestKeywords: ['[BROADCAST]', '[SHUFFLE]'],
          suggestJoins: {
            prependJoin: false,
            joinType: 'JOIN',
            tables: [{ identifierChain: [{ name: 'boo' }] }]
          },
          suggestTables: {},
          suggestDatabases: { appendDot: true }
        }
      });
    });

    it('should suggest keywords for "UPDATE bar.foo SET bla = \'foo\' FROM boo JOIN blaa |"', () => {
      assertAutoComplete({
        beforeCursor: "UPDATE bar.foo SET bla = 'foo' FROM boo JOIN blaa ",
        afterCursor: '',
        dialect: 'impala',
        containsKeywords: ['ON', 'JOIN'],
        expectedResult: {
          lowerCase: false,
          suggestJoinConditions: {
            prependOn: true,
            tables: [
              { identifierChain: [{ name: 'bar' }, { name: 'foo' }] },
              { identifierChain: [{ name: 'boo' }] },
              { identifierChain: [{ name: 'blaa' }] }
            ]
          }
        }
      });
    });
  });
});
