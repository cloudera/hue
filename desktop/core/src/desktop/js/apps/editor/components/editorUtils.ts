/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

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
