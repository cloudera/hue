export interface CommonParser {
  identifyPartials(
    beforeCursor: string,
    afterCursor: string
  ): { backtickAfter: boolean; backtickBefore: boolean; left: number; right: number };
}

export const assertPartials = (parser: CommonParser): void => {
  const limitChars = [
    ' ',
    '\n',
    '\t',
    '&',
    '~',
    '%',
    '!',
    '.',
    ',',
    '+',
    '-',
    '*',
    '/',
    '=',
    '<',
    '>',
    ')',
    '[',
    ']',
    ';'
  ];

  expect(parser.identifyPartials('', '')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 0,
    right: 0
  });
  expect(parser.identifyPartials('foo', '')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 3,
    right: 0
  });
  expect(parser.identifyPartials(' foo', '')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 3,
    right: 0
  });
  expect(parser.identifyPartials('asdf 1234', '')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 4,
    right: 0
  });

  expect(parser.identifyPartials('foo', 'bar')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 3,
    right: 3
  });

  expect(parser.identifyPartials('fo', 'o()')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 2,
    right: 3
  });

  expect(parser.identifyPartials('fo', 'o(')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 2,
    right: 2
  });
  expect(parser.identifyPartials('fo', 'o(bla bla)')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 2,
    right: 10
  });

  expect(parser.identifyPartials('foo ', '')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 0,
    right: 0
  });
  expect(parser.identifyPartials("foo '", "'")).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 0,
    right: 0
  });

  expect(parser.identifyPartials('foo "', '"')).toEqual({
    backtickAfter: false,
    backtickBefore: false,
    left: 0,
    right: 0
  });
  limitChars.forEach(char => {
    expect(parser.identifyPartials('bar foo' + char, '')).toEqual({
      backtickAfter: false,
      backtickBefore: false,
      left: 0,
      right: 0
    });

    expect(parser.identifyPartials('bar foo' + char + 'foofoo', '')).toEqual({
      backtickAfter: false,
      backtickBefore: false,
      left: 6,
      right: 0
    });

    expect(parser.identifyPartials('bar foo' + char + 'foofoo ', '')).toEqual({
      backtickAfter: false,
      backtickBefore: false,
      left: 0,
      right: 0
    });

    expect(parser.identifyPartials('', char + 'foo bar')).toEqual({
      backtickAfter: false,
      backtickBefore: false,
      left: 0,
      right: 0
    });

    expect(parser.identifyPartials('', 'foofoo' + char)).toEqual({
      backtickAfter: false,
      backtickBefore: false,
      left: 0,
      right: 6
    });

    expect(parser.identifyPartials('', ' foofoo' + char)).toEqual({
      backtickAfter: false,
      backtickBefore: false,
      left: 0,
      right: 0
    });
  });
};
