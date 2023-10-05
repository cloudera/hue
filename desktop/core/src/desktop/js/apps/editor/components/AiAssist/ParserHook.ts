import { useState, useEffect } from 'react';
import huePubSub from 'utils/huePubSub';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { SyntaxParser } from 'parse/types';
import SqlExecutable from '../../execution/sqlExecutable';

// TODO: why not use a state for lastDialect?
export const useParser = (activeExecutable: SqlExecutable) => {
  const [hasMissingNameError, setMissingNameError] = useState<boolean>(false);
  const [hasParseError, setHasParseError] = useState<boolean>(false);
  const [syntaxParser, setSyntaxParser] = useState<SyntaxParser>();
  const [sqlDialect, setSqlDialect] = useState<string>('');

  const parsedStatement = activeExecutable?.parsedStatement;
  const selectedStatement: string = parsedStatement?.statement || '';

  const loadParser = async executor => {
    const connector = executor?.connector();
    const executorDialect = connector?.dialect;

    if (sqlDialect !== executorDialect) {
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

  useEffect(() => {
    loadParser(activeExecutable?.executor);
    if (syntaxParser) {
      const newParseError = !!syntaxParser?.parseSyntax('', selectedStatement.trim());
      setHasParseError(newParseError);
    }
  }, [selectedStatement, syntaxParser]);

  const hasIncorrectSql = hasMissingNameError || hasParseError;

  return [syntaxParser, sqlDialect, hasIncorrectSql];
};
