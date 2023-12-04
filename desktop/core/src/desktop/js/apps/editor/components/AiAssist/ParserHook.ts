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

import { useState, useEffect, useRef } from 'react';
import huePubSub from 'utils/huePubSub';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { SyntaxParser, AutocompleteParser } from 'parse/types';
import SqlExecutable from '../../execution/sqlExecutable';

const hasError = (syntaxParser: React.RefObject<SyntaxParser | undefined>, sql: string): boolean =>
  !!syntaxParser.current?.parseSyntax('', sql.trim());

export const useParser = (
  activeExecutable: SqlExecutable
): {
  autocompleteParser: AutocompleteParser | undefined;
  hasIncorrectSql: boolean;
  sqlDialect: string;
  syntaxParser: SyntaxParser | undefined;
} => {
  const [hasMissingNameError, setMissingNameError] = useState<boolean>(false);
  const [hasParseError, setHasParseError] = useState<boolean>(false);
  const syntaxParserRef = useRef<SyntaxParser>();
  const autocompleteParserRef = useRef<AutocompleteParser>();
  const previousSqlDialectRef = useRef<string>('');

  const parsedStatement = activeExecutable?.parsedStatement;
  const selectedStatement: string = parsedStatement?.statement || '';
  const connector = activeExecutable?.executor?.connector();
  const sqlDialect = connector?.dialect;

  const updateAndParse = async (sqlDialect: string) => {
    const syntaxParser = await sqlParserRepository.getSyntaxParser(sqlDialect);
    syntaxParserRef.current = syntaxParser;
    setHasParseError(hasError(syntaxParserRef, selectedStatement));

    const autocompleteParser = await sqlParserRepository.getAutocompleteParser(sqlDialect);
    autocompleteParserRef.current = autocompleteParser;
  };

  // Subscribe once to be notified when the editor finds that a
  // table or column name is missing.
  useEffect(() => {
    const subscription = huePubSub.subscribe('sql.error.missing.name', isShowing => {
      setMissingNameError(isShowing);
    });
    return () => {
      subscription.remove();
    };
  }, []);

  useEffect(() => {
    if (previousSqlDialectRef.current !== sqlDialect) {
      previousSqlDialectRef.current = sqlDialect;

      // To check if there are any parse errors when a new parser is loaded async
      // we use an async function outside of the sync useEfect hook.
      updateAndParse(sqlDialect);
    }

    // If the parser is already loaded but the selectedStatement
    // has changed we can check for parse errors immediately.
    if (syntaxParserRef.current) {
      setHasParseError(hasError(syntaxParserRef, selectedStatement));
    }
  }, [selectedStatement, sqlDialect]);

  return {
    syntaxParser: syntaxParserRef.current,
    sqlDialect,
    hasIncorrectSql: hasMissingNameError || hasParseError,
    autocompleteParser: autocompleteParserRef.current
  };
};
