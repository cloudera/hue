import React, { useState, useEffect, useRef } from 'react';
import {
  BugOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  EditOutlined,
  CommentOutlined
} from '@ant-design/icons';
import classNames from 'classnames';
import huePubSub from 'utils/huePubSub';
import { SyntaxParser } from 'parse/types';
import Toolbar, { ToolbarButton } from '../../../../reactComponents/Toolbar/Toolbar';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { generativeFunctionFactory } from 'api/apiAIHelper';
import SqlExecutable from '../../execution/sqlExecutable';
import { getLeadingEmptyLineCount } from '../editorUtils';
import AiPreviewModal from './PreviewModal/AiPreviewModal';
import { useKeywordCase } from './hooks';
import AnimatedLauncher from './AnimatedLauncher/AnimatedLauncher';
import AnimatedCloseButton from './AnimatedCloseButton/AnimatedCloseButton';
import AssistToolbar from './AssistToolbar/AssistToolbar';

import './AiAssistBar.scss';

export interface ParseError {
  line: number;
  loc: {
    last_column: number;
  };
  text: string;
}

const {
  generateExplanation,
  generateCorrectedSql,
  generateOptimizedSql,
  generateSQLfromNQL,
  generateEditedSQLfromNQL
} = generativeFunctionFactory();

const getEditorLineNumbers = (parsedStatement: ParsedSqlStatement) => {
  const { first_line: firstLineInlcudingEmptyLines, last_line: lastLine } =
    parsedStatement?.location || {};
  const firstLine = firstLineInlcudingEmptyLines + getLeadingEmptyLineCount(parsedStatement);
  return { firstLine, lastLine };
};

const breakLines = (input: string): string => {
  let words = input.split(' ');
  let result = '';
  let line = '';

  for (let i = 0; i < words.length; i++) {
    let word = words[i];
    if (line.length + word.length <= 90) {
      line += word + ' ';
    } else {
      result += line + '\n';
      line = word + ' ';
    }
  }
  return (result += line);
};

export interface AiAssistBarProps {
  activeExecutable?: SqlExecutable;
}
const AiAssistBar = ({ activeExecutable }: AiAssistBarProps) => {
  const currentExecutable =
    activeExecutable instanceof Function ? activeExecutable() : activeExecutable;

  const parsedStatement = currentExecutable?.parsedStatement;
  const selectedStatement: string = parsedStatement?.statement || '';
  const lastSelectedStatement = useRef(selectedStatement);
  const lastDialect = useRef('');
  const { firstLine, lastLine } = getEditorLineNumbers(parsedStatement);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isAnimating, setIsAnimating] = useState<'no' | 'expand' | 'contract'>('no');
  const [isEditMode, setIsEditMode] = useState(false);
  const [isGenerateMode, setIsGenerateMode] = useState(false);
  const [showSuggestedSqlModal, setShowSuggestedSqlModal] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const [suggestionExplanation, setSuggestionExplanation] = useState('');
  const [assumptions, setAssumptions] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatusText, setLoadingStatusText] = useState('');
  const [errorStatusText, setErrorStatusText] = useState('');
  const [parser, setParser] = useState<SyntaxParser>();
  const [parseError, setParseError] = useState<ParseError | undefined>();

  const keywordCase = useKeywordCase(parser, selectedStatement);
  const inputExpanded = isEditMode || isGenerateMode;

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

  const handleStatusUpdate = (status: string) => {
    setLoadingStatusText(status);
  };

  const handleApiError = (status: string) => {
    setErrorStatusText(status);
  };

  const loadExplanation = async (statement: string) => {
    setIsLoading(true);
    const executor = activeExecutable?.executor;
    const databaseName = activeExecutable?.database || '';
    const dialect = lastDialect.current;
    const explanation = await generateExplanation({
      statement,
      dialect,
      executor,
      databaseName,
      onStatusChange: handleStatusUpdate
    });
    setSuggestion(statement);
    setExplanation(breakLines(explanation));
    setShowSuggestedSqlModal(true);
    setIsLoading(false);
  };

  const generateSqlQuery = async (nql: string, activeExecutable: SqlExecutable) => {
    setIsLoading(true);
    const executor = activeExecutable?.executor;
    const databaseName = activeExecutable?.database || '';
    const dialect = lastDialect.current;
    const { sql, assumptions } = await generateSQLfromNQL({
      nql,
      databaseName,
      executor,
      dialect,
      onStatusChange: handleStatusUpdate
    });
    setSuggestion(sql);
    setAssumptions(assumptions);
    setShowSuggestedSqlModal(true);

    setIsLoading(false);
  };

  const editSqlQuery = async (
    nql: string,
    sqlToModify: string,
    activeExecutable: SqlExecutable
  ) => {
    setIsLoading(true);
    const executor = activeExecutable?.executor;
    const databaseName = activeExecutable?.database || '';
    const dialect = lastDialect.current;
    const { sql, assumptions } = await generateEditedSQLfromNQL({
      nql,
      sql: sqlToModify,
      databaseName,
      executor,
      dialect,
      onStatusChange: handleStatusUpdate
    });
    setSuggestion(sql);
    setAssumptions(assumptions);
    setShowSuggestedSqlModal(true);

    setIsLoading(false);
  };

  const loadOptimization = async (statement: string, activeExecutable: SqlExecutable) => {
    setIsLoading(true);
    const executor = activeExecutable?.executor;
    const databaseName = activeExecutable?.database || '';
    const dialect = lastDialect.current;
    const { sql, explanation, error } = await generateOptimizedSql({
      statement,
      databaseName,
      executor,
      dialect,
      onStatusChange: handleStatusUpdate
    });

    if (error) {
      handleApiError(error.message);
    } else {
      setSuggestion(sql);
      setSuggestionExplanation(explanation);
      setShowSuggestedSqlModal(true);
    }
    setIsLoading(false);
  };

  const loadFixSuggestion = async (statement: string) => {
    setIsLoading(true);
    const dialect = lastDialect.current;
    const { sql, explanation, error } = await generateCorrectedSql({
      statement,
      dialect,
      onStatusChange: handleStatusUpdate
    });
    if (error) {
      handleApiError(error.message);
    } else {
      setSuggestion(sql);
      setSuggestionExplanation(explanation);
      setShowSuggestedSqlModal(true);
    }
    setIsLoading(false);
  };

  const acceptSuggestion = (statement: string) => {
    setShowSuggestedSqlModal(false);
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
    setSuggestion('');
    setIsGenerateMode(false);
    setIsGenerateMode(false);
  };

  // const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
  //   if (event.key === 'Enter' && inputExpanded) {
  //     const userInput = (event.target as HTMLInputElement).value;
  //     const sqlStatmentToModify = parsedStatement.statement;
  //     if (isGenerateMode) {
  //       generateSqlQuery(userInput, currentExecutable);
  //     } else if (isEditMode) {
  //       editSqlQuery(userInput, sqlStatmentToModify, currentExecutable);
  //     }
  //   }
  // };

  const handleToobarInputSubmit = (userInput: string) => {
    const sqlStatmentToModify = parsedStatement.statement;
    if (isGenerateMode) {
      generateSqlQuery(userInput, currentExecutable);
    } else if (isEditMode) {
      editSqlQuery(userInput, sqlStatmentToModify, currentExecutable);
    }
  }

  const handleInsert = (sql: string, rawExplain: string) => {
    const leadingEmptyLines = getLeadingEmptyLineCount({ statement: sql });
    const leadingLineBreaks = '\n'.repeat(leadingEmptyLines);
    const comment = rawExplain ? `${leadingLineBreaks}/* ${rawExplain} */\n` : '';
    const textToInsert = comment ? `${comment}${sql.trim()}\n` : sql;

    acceptSuggestion(textToInsert);
    setExplanation('');
  };

  useEffect(() => {
    if (!lastSelectedStatement.current) {
      lastSelectedStatement.current = selectedStatement;
    }
    loadParser();

    const selectionChanged = lastSelectedStatement.current !== selectedStatement;

    if (parser && (selectionChanged || !explanation)) {
      lastSelectedStatement.current = selectedStatement;
      const newParseError = parser?.parseSyntax('', selectedStatement.trim()) as ParseError;
      setParseError(newParseError);
    }

    if (selectionChanged) {
      setSuggestion('');
      setAssumptions('');
    }
  }, [selectedStatement, parser]);



  return (
    <>
      <AnimatedLauncher
        isAnimating={isAnimating}
        isExpanded={isExpanded}
        isLoading={isLoading}
        loadingStatusText={loadingStatusText}
        errorStatusText={errorStatusText}
        setIsExpanded={setIsExpanded}
        setIsAnimating={setIsAnimating}
        setErrorStatusText={setErrorStatusText}
      />
      <div
        className={classNames('hue-ai-assist-bar', {
          'hue-ai-assist-bar--expanded': isExpanded,
          'hue-ai-assist-bar--expanding': isAnimating === 'expand',
          'hue-ai-assist-bar--contracting': isAnimating === 'contract'
        })}
      >
        <div
          className={classNames('hue-ai-assist-bar__content', {
            'hue-ai-assist-bar__content--expanded': isExpanded
          })}
        >
          <AssistToolbar
            isGenerateMode={isGenerateMode}
            isLoading={isLoading}
            setErrorStatusText={setErrorStatusText}
            setIsGenerateMode={setIsGenerateMode}
            setIsEditMode={setIsEditMode}
            isEditMode={isEditMode}
            onInputSubmit={handleToobarInputSubmit}
            inputExpanded={inputExpanded}
            loadExplanation={loadExplanation}
            parsedStatement={parsedStatement}
            loadOptimization={loadOptimization}
            loadFixSuggestion={loadFixSuggestion}
            parseError={parseError}
          />
        </div>
        <AnimatedCloseButton
          title="Close AI assistbar"
          className={classNames('hue-ai-assistbar__close-btn', {
            'hue-ai-assistbar__close-btn--expanded': isExpanded
          })}
          onClick={() => {
            setIsExpanded(false);
          }}
        />
      </div>
      {showSuggestedSqlModal && (
        <AiPreviewModal
          title="Suggestion"
          open={true}
          onCancel={() => {
            setExplanation('');
            setShowSuggestedSqlModal(false);
          }}
          onInsert={sql => handleInsert(sql, explanation)}
          primaryButtonLabel={explanation ? 'Insert as comment' : 'Insert'}
          suggestion={suggestion}
          showDiffFrom={!isGenerateMode && !explanation ? parsedStatement?.statement : undefined}
          assumptions={assumptions}
          explanation={explanation || suggestionExplanation}
          lineNumberStart={getEditorLineNumbers(parsedStatement).firstLine}
          showCopyToClipboard={!explanation}
          dialect={lastDialect.current}
          keywordCase={keywordCase}
        />
      )}
    </>
  );
};
export default AiAssistBar;
