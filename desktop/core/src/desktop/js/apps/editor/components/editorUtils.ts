import { ParsedSqlStatement } from 'parse/sqlStatementsParser';

export const LINE_BREAK_REGEX = /(\r\n)|(\n)|(\r)/g;
const LEADING_WHITE_SPACE_REGEX = /^\s+/;

export const getLeadingEmptyLineCount = (parsedStatement: ParsedSqlStatement): number => {
  let leadingEmptyLineCount = 0;
  const leadingWhiteSpace = parsedStatement.statement.match(LEADING_WHITE_SPACE_REGEX);
  if (leadingWhiteSpace) {
    const lineBreakMatch = leadingWhiteSpace[0].match(LINE_BREAK_REGEX);
    if (lineBreakMatch) {
      leadingEmptyLineCount = lineBreakMatch.length;
    }
  }
  return leadingEmptyLineCount;
};
