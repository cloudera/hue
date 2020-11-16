import { ParsedLocation } from 'parse/types';

export = sqlStatementsParser;

declare const sqlStatementsParser = {
  parse(statement: string): sqlStatementsParser.ParsedSqlStatement[];
};

declare namespace sqlStatementsParser {
  export interface ParsedSqlStatement {
    firstToken: string;
    statement: string;
    location: ParsedLocation;
    type: string;
  }
}
