import { ParsedLocation } from 'parse/types';

export interface ParsedSqlStatement {
  firstToken: string;
  statement: string;
  location: ParsedLocation;
  type: string;
}

export function parse(statement: string): ParsedSqlStatement[];
