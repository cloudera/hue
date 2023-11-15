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

import { useState, useEffect } from 'react';
import huePubSub from 'utils/huePubSub';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { SyntaxParser, AutocompleteParser } from 'parse/types';
import SqlExecutable from '../../execution/sqlExecutable';

// TODO: why not use a state for lastDialect?
export const useParser = (activeExecutable: SqlExecutable) => {
  const [hasMissingNameError, setMissingNameError] = useState<boolean>(false);
  const [hasParseError, setHasParseError] = useState<boolean>(false);
  const [syntaxParser, setSyntaxParser] = useState<SyntaxParser>();
  const [autocompleteParser, setAutocompleteParser] = useState<AutocompleteParser>();
  const [sqlDialect, setSqlDialect] = useState<string>('');

  const parsedStatement = activeExecutable?.parsedStatement;
  const selectedStatement: string = parsedStatement?.statement || '';

  const updateParserAndDialect = async (executorDialect: string) => {
    if (sqlDialect !== executorDialect) {
      const autocompleteParser = await sqlParserRepository.getAutocompleteParser(executorDialect);
      setAutocompleteParser(autocompleteParser);
      const matchingParser = await sqlParserRepository.getSyntaxParser(executorDialect);
      setSyntaxParser(matchingParser);
      setSqlDialect(executorDialect);
    }
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

  const connector = activeExecutable?.executor?.connector();
  const executorDialect = connector?.dialect;

  useEffect(() => {
    updateParserAndDialect(executorDialect);
    if (syntaxParser) {
      const newParseError = !!syntaxParser?.parseSyntax('', selectedStatement.trim());
      setHasParseError(newParseError);
    }
  }, [selectedStatement, executorDialect]);

  const hasIncorrectSql = hasMissingNameError || hasParseError;

  return [syntaxParser, sqlDialect, hasIncorrectSql, autocompleteParser];
};
