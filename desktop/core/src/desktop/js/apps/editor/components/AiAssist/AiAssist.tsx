import React, { FunctionComponent, useState, useEffect, useRef, cloneElement } from 'react';
import { Skeleton } from 'antd';
import Alert from 'cuix/dist/components/Alert/Alert';

import huePubSub from 'utils/huePubSub';
import { SyntaxParser } from 'parse/types';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { generativeFunctionFactory } from 'api/apiAIHelper';
import SqlExecutable from '../../execution/sqlExecutable';
import { getLeadingEmptyLineCount } from '../editorUtils';

import SqlCodeSnippet from './SqlCodeSnippet/SqlCodeSnippet';
import './AiAssist.scss';

export interface ParseError {
  line: number;
  loc: {
    last_column: number;
  };
  text: string;
}

const { generateExplanation, generateCorrectedSql, generateOptimizedSql, generateSQLfromNQL } =
  generativeFunctionFactory();

// Matches comments like '/* comment1 */' and '-- comment2'
const SQL_COMMENTS_REGEX = /\/\*[\s\S]*?\*\/\n?|--.*?\n/g;
const EDITOR_LEADING_LINEBREAKS_REGEX = /^((\r\n)|(\n)|(\r))*/;

const EXTRACT_NQL_REGEX = /^--([^\S\r\n]*)nql:([^\S\r\n])(.*)/;
const TYPING_NQL_KEYWORD_REGEX = /^(-- nql: |-- nql:|-- nql|-- nq|-- n|-- |--|-)$/;

const removeComments = (statement: string) => {
  const sqlComments = SQL_COMMENTS_REGEX;
  return statement.replace(sqlComments, '');
};

const getEditorLineNumbers = (parsedStatement: ParsedSqlStatement) => {
  const { first_line: firstLineInlcudingEmptyLines, last_line: lastLine } =
    parsedStatement?.location || {};
  const firstLine = firstLineInlcudingEmptyLines + getLeadingEmptyLineCount(parsedStatement);
  return { firstLine, lastLine };
};

const removeLeadingLineBreaks = (statement: string) =>
  statement.replace(EDITOR_LEADING_LINEBREAKS_REGEX, '');

const isUserTypingNqlKeyword = (rawStatement: string) => {
  const statement = removeLeadingLineBreaks(rawStatement).toLowerCase();
  return !!TYPING_NQL_KEYWORD_REGEX.test(statement);
};

const isStartingWithNqlKeyword = (rawStatement: string) => {
  const statement = removeLeadingLineBreaks(rawStatement).toLowerCase();
  return statement.startsWith('-- nql:') || statement.startsWith('--nql:');
};

const extractNqlFromStatement = (rawStatement: string) => {
  const statement = removeLeadingLineBreaks(rawStatement);
  const matches = EXTRACT_NQL_REGEX.exec(statement);
  return matches ? matches[3].trim() : '';
};

export interface AiAssistProps {
  activeExecutable?: SqlExecutable;
}
const AiAssist = ({ activeExecutable }: AiAssistProps) => {
  const currentExecutable =
    activeExecutable instanceof Function ? activeExecutable() : activeExecutable;

  // console.info('currentExecutable', currentExecutable);
  const parsedStatement = currentExecutable?.parsedStatement;
  const selectedStatement: string = parsedStatement?.statement || '';
  const nqlStatement: string = extractNqlFromStatement(selectedStatement);
  const nqlKeywordDetected: boolean = isStartingWithNqlKeyword(selectedStatement);
  const isTypingNqlKeyword: boolean = isUserTypingNqlKeyword(selectedStatement);
  const lastSelectedStatement = useRef(selectedStatement);
  const lastDialect = useRef('');
  const { firstLine, lastLine } = getEditorLineNumbers(parsedStatement);

  const [explanation, setExplanation] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const [suggestionExplanation, setSuggestionExplanation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingSuggestion, setIsLoadingSuggestion] = useState(false);
  const [isGeneratingSql, setIsGeneratingSql] = useState(false);
  const [parser, setParser] = useState<SyntaxParser>();
  const [parseError, setParseError] = useState<ParseError | undefined>();

  const loadParser = async () => {
    const executor = activeExecutable?.executor;
    const connector = executor?.connector();
    const dialect = connector?.dialect;

    if (lastDialect.current !== dialect) {
      const matchingParser = await sqlParserRepository.getSyntaxParser(dialect);
      setParser(matchingParser);
      lastDialect.current = dialect;
    }
  };

  const loadExplanation = async (statement: string) => {
    setIsLoading(true);
    const dialect = lastDialect.current;
    const explanation = await generateExplanation({ statement, dialect });
    setExplanation(explanation);
    setIsLoading(false);
  };

  const loadFixSuggestion = async (statement: string) => {
    setIsLoadingSuggestion(true);
    const dialect = lastDialect.current;
    const { sql, explanation } = await generateCorrectedSql({ statement, dialect });
    // TODO: handle if (!sql)
    setSuggestion(sql);
    setSuggestionExplanation(explanation);
    setIsLoadingSuggestion(false);
  };

  const loadSqlFromNql = async (nql: string, activeExecutable: SqlExecutable) => {
    setIsGeneratingSql(true);
    const executor = activeExecutable?.executor;
    const databaseName = activeExecutable?.database || '';
    const dialect = lastDialect.current;
    const { sql, assumptions } = await generateSQLfromNQL({
      nql,
      databaseName,
      executor,
      dialect
    });
    console.info(sql, assumptions);
    setSuggestion(sql);
    setSuggestionExplanation(assumptions);
    setIsGeneratingSql(false);
  };

  const loadOptimization = async (statement: string) => {
    setIsLoadingSuggestion(true);
    const dialect = lastDialect.current;
    const { sql, explanation } = await generateOptimizedSql({ statement, dialect });
    // TODO: handle if (!sql)
    setSuggestion(sql);
    setSuggestionExplanation(explanation);
    setIsLoadingSuggestion(false);
  };

  const acceptSuggestion = (statement: string) => {
    huePubSub.publish('ace.replace', {
      text: statement,
      location: {
        first_line: firstLine,
        first_column: 1,
        last_line: lastLine,
        // TODO: what to use here?
        last_column: 10000
      }
    });
  };

  const renderCodeSnippets = () => {
    return (
      <>
        <SqlCodeSnippet
          topInfoBar={`Editor lines ${firstLine} to ${lastLine}`}
          firstLine={firstLine}
          lastLine={lastLine}
          parseError={parseError}
          hideSuggestFix={isLoadingSuggestion || !!suggestion}
          onSuggestFixClick={loadFixSuggestion}
          onExplainSqlClick={loadExplanation}
          onOptimizeSqlClick={loadOptimization}
          explanation={parseError || isLoading ? '' : explanation}
        >
          {cleanedSqlStatement}
        </SqlCodeSnippet>
        <Skeleton active loading={isLoading || isLoadingSuggestion} paragraph={false} />
        {suggestion && (
          <SqlCodeSnippet
            topInfoBar={`Suggested change for editor lines ${firstLine} to ${lastLine}`}
            firstLine={firstLine}
            lastLine={lastLine}
            onAcceptClick={acceptSuggestion}
            isSuggestion
            explanation={suggestionExplanation}
          >
            {suggestion}
          </SqlCodeSnippet>
        )}
      </>
    );
  };

  const renderNQLinput = () => {
    // console.info('isGeneratingSql || !!suggestion', isGeneratingSql || !!suggestion);
    return (
      <>
        <SqlCodeSnippet
          topInfoBar={
            isTypingNqlKeyword ? 'Waiting for input' : `NQL input from ${firstLine} to ${lastLine}`
          }
          firstLine={firstLine}
          lastLine={lastLine}
          isNLQ
          hideSuggestFix={isGeneratingSql || !!suggestion}
          onGenerateSqlClick={nqlStatement => {
            loadSqlFromNql(nqlStatement, currentExecutable);
          }}
          // explanation="Write your query in plain english, or any aother language."
        >
          {nqlStatement}
        </SqlCodeSnippet>
        <Skeleton active loading={isLoading || isGeneratingSql} paragraph={false} />
        {suggestion && (
          <SqlCodeSnippet
            // acceptMsg="Please manually verify generated SQL before using it."
            topInfoBar={`Suggested SQL for lines ${firstLine} to ${lastLine}`}
            firstLine={firstLine}
            lastLine={lastLine}
            onAcceptClick={acceptSuggestion}
            isSuggestion
            explanation={suggestionExplanation}
          >
            {suggestion}
          </SqlCodeSnippet>
        )}
      </>
    );
  };

  useEffect(() => {
    // TODO: CLEAN THIS MESS UP
    if (!lastSelectedStatement.current) {
      lastSelectedStatement.current = selectedStatement;
    }
    loadParser();

    const selectionChanged = lastSelectedStatement.current !== selectedStatement;

    if (
      !(isTypingNqlKeyword || nqlKeywordDetected) &&
      parser &&
      (selectionChanged || !explanation)
    ) {
      lastSelectedStatement.current = selectedStatement;

      // Clear any leftover sugestions
      const newParseError = parser?.parseSyntax('', selectedStatement.trim()) as ParseError;
      setParseError(newParseError);
    }

    // RESET STUFF
    if (nqlKeywordDetected) {
      lastSelectedStatement.current = selectedStatement;
    }
    if (selectionChanged) {
      setSuggestion('');
      setExplanation('');
      setSuggestionExplanation('');
    }
  }, [selectedStatement, parser, nqlKeywordDetected]);

  const cleanedSqlStatement = removeLeadingLineBreaks(removeComments(selectedStatement));

  return (
    <>
      <div className="hue-explain-sql-panel">
        <Alert
          message="The natural language explanation feature is experimental. The content is generated by an AI and is not guaranteed to be accurate."
          showIcon
        />
        {selectedStatement === '' && (
          <p>
            Select a statement in the editor or type "-- nql:" followed by your natural language
            question{' '}
          </p>
        )}
        {(isTypingNqlKeyword || nqlKeywordDetected) && renderNQLinput()}
        {!(isTypingNqlKeyword || nqlKeywordDetected) && renderCodeSnippets()}
      </div>
    </>
  );
};
export default AiAssist;
