import { getLeadingEmptyLineCount } from './editorUtils';

describe('getLeadingEmptyLineCount', () => {
  test('returns 0 when there are no leading empty lines', () => {
    const parsedStatement = {
      statement: 'SELECT * FROM my_table;',
      type: 'SELECT',
    };
    const result = getLeadingEmptyLineCount(parsedStatement);
    expect(result).toBe(0);
  });

  test('returns the number of leading empty lines', () => {
    const parsedStatement = {
      statement: '\n\n  SELECT * FROM my_table;',
      type: 'SELECT',
    };
    const result = getLeadingEmptyLineCount(parsedStatement);
    expect(result).toBe(2);
  });

  test('returns the number of leading empty lines with mixed line breaks', () => {
    const parsedStatement = {
      statement: '\r\n\r\n\nSELECT * FROM my_table;',
      type: 'SELECT',
    };
    const result = getLeadingEmptyLineCount(parsedStatement);
    expect(result).toBe(3);
  });

  test('returns 0 when the statement starts with non-empty whitespace', () => {
    const parsedStatement = {
      statement: '  SELECT * FROM my_table;',
      type: 'SELECT',
    };
    const result = getLeadingEmptyLineCount(parsedStatement);
    expect(result).toBe(0);
  });

  test('returns 0 when the statement is empty', () => {
    const parsedStatement = {
      statement: '',
      type: 'SELECT',
    };
    const result = getLeadingEmptyLineCount(parsedStatement);
    expect(result).toBe(0);
  });
});