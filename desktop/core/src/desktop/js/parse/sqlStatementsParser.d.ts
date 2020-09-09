import { ParsedLocation } from 'parse/types';

declare module 'parse/sqlStatementsParser' {
  export interface ParsedSqlStatement {
    firstToken: string;
    statement: string;
    location: ParsedLocation;
    type: string;
  }

  export function parse(statement: string): ParsedSqlStatement[];
}
