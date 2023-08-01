import React, { useState, useEffect, useRef } from 'react';
import classNames from 'classnames';
import huePubSub from 'utils/huePubSub';
import { SyntaxParser } from 'parse/types';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import { generativeFunctionFactory } from 'api/apiAIHelper';
import SqlExecutable from '../../execution/sqlExecutable';
import { getLeadingEmptyLineCount } from '../editorUtils';
import AiPreviewModal from './PreviewModal/AiPreviewModal';
import { useKeywordCase } from './hooks';
import AnimatedLauncher from './AnimatedLauncher/AnimatedLauncher';
import AnimatedCloseButton from './AnimatedCloseButton/AnimatedCloseButton';
import AssistToolbar from './AiAssistToolbar/AiAssistToolbar';
import { nqlCommentRegex } from './sharedRegexes';

import './AiAssistBar.scss';

export interface ParseError {
  line: number;
  loc: {
    last_column: number;
  };
  text: string;
}

let sug = "";

const {
  generateExplanation,
  generateCorrectedSql,
  generateOptimizedSql,
  generateSQLfromNQL,
  generateEditedSQLfromNQL
} = generativeFunctionFactory();

const getSelectedLineNumbers = (parsedStatement: ParsedSqlStatement) => {
  if (!parsedStatement) {
    return { firstLine: 0, lastLine: 0 };
  }
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

const extractLeadingNqlComments = (sql: string): string => {
  const comments = sql.match(nqlCommentRegex) || [];
  const prefixSingleLine = '-- NQL:';
  const prefixMultiLine = '/* NQL:';
  const commentsTexts = comments
    .map(comment => comment.trim())
    .filter(comment => comment.startsWith(prefixSingleLine) || comment.startsWith(prefixMultiLine))
    .map(comment => {
      return comment.startsWith(prefixSingleLine)
        ? comment.slice(prefixSingleLine.length).trim()
        : comment.slice(prefixMultiLine.length, -2).trim();
    });

  return commentsTexts.join('\n');
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
  const { firstLine, lastLine } = getSelectedLineNumbers(parsedStatement);
  const [isExpanded, setIsExpanded] = useState(
    getFromLocalStorage('hue.aiAssistBar.isExpanded', false)
  );
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
  const [nql, setNql] = useState('');
  const [inputValue, setInputValue] = useState<string>('');
  const cursorPosition = useRef<{ row: number; column: number } | undefined>();
  const keywordCase = useKeywordCase(parser, selectedStatement);
  const inputExpanded = isEditMode || isGenerateMode;
  const inputPrefill = inputExpanded ? extractLeadingNqlComments(selectedStatement) : '';

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
    const { summary, error } = await generateExplanation({
      statement,
      dialect,
      executor,
      databaseName,
      onStatusChange: handleStatusUpdate
    });
    if (error) {
      handleApiError(error.message);
    } else {
      setSuggestion(statement);
      setExplanation(breakLines(summary));
      setShowSuggestedSqlModal(true);
    }
    setIsLoading(false);
  };

  const extractTextBetweenTags = (htmlString, startTag, endTag) => {
    const startIndex = htmlString.indexOf(startTag);
  
    if (startIndex === -1) {
      return ""; // Start tag not found
    }
  
    const endIndex = endTag ? htmlString.indexOf(endTag, startIndex) : -1;
    const textEndIndex = endIndex !== -1 ? endIndex : htmlString.length;
  
    const text = htmlString.substring(startIndex + startTag.length, textEndIndex);
    // text.append("<span className='testing'>test</span>");
    return text ? text.trim() : 'Generating...';
  };

  const setNewSuggestion = (value, done) => {
    sug = sug + value;
    let codeText = extractTextBetweenTags(sug, '<code>', '</code>');
    codeText = codeText;
    setSuggestion(codeText);

    let assumptionsText = extractTextBetweenTags(sug, '<assumptions>', '</assumptions>');
    assumptionsText = assumptionsText;
    setAssumptions(assumptionsText);
  };


  const generateSqlQuery = async (nql: string, activeExecutable: SqlExecutable) => {
    setIsLoading(true);
    const executor = activeExecutable?.executor;
    const databaseName = activeExecutable?.database || '';
    const dialect = lastDialect.current;

    const { sql, assumptions, error } = generateSQLfromNQL({
      nql,
      databaseName,
      executor,
      dialect,
      onStatusChange: handleStatusUpdate,
      setNewSuggestion: setNewSuggestion
    });
    // debugger;
    if (error) {
      handleApiError(error.message);
    } else {
      setNql(nql);
      setSuggestion("Generating...");
      setAssumptions("Generating...");
      setShowSuggestedSqlModal(true);
    }
    setIsLoading(false);
    setInputValue('');
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
    const { sql, assumptions, error } = await generateEditedSQLfromNQL({
      nql,
      sql: sqlToModify,
      databaseName,
      executor,
      dialect,
      onStatusChange: handleStatusUpdate
    });
    if (error) {
      handleApiError(error.message);
    } else {
      setNql(nql);
      setSuggestion(sql);
      setAssumptions(assumptions);
      setShowSuggestedSqlModal(true);
    }

    setIsLoading(false);
    setInputValue('');
  };

  const loadOptimization = async (statement: string) => {
    setIsLoading(true);
    const executor = activeExecutable?.executor;
    const databaseName = activeExecutable?.database || '';
    const dialect = lastDialect.current;
    const { sql, explain, error } = await generateOptimizedSql({
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
      setSuggestionExplanation(explain);
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
    let lineNrToMoveTo = firstLine;
    if (isGenerateMode) {
      const zeroBasedLineNr = 1;
      const lineNrOfCursor = cursorPosition.current?.row || 0;
      // TODO: lineNrToMoveTo fails if the user inserts new lines without moving the cursor afterwards.
      // We need to find a way to get the current cursor position from the editor
      // when the code is changed using keyboar interactactions
      lineNrToMoveTo = lineNrOfCursor + zeroBasedLineNr || 1;
      huePubSub.publish('editor.insert.at.cursor', { text: statement });
    } else {
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
    }
    setShowSuggestedSqlModal(false);
    huePubSub.publish('ace.cursor.move', {
      column: 0,
      row: lineNrToMoveTo
    });

    resetAll();
  };

  const handleToobarInputSubmit = (userInput: string) => {
    const sqlStatmentToModify = parsedStatement.statement;
    if (isGenerateMode) {
      generateSqlQuery(userInput, currentExecutable);
    } else if (isEditMode) {
      editSqlQuery(userInput, sqlStatmentToModify, currentExecutable);
    }
  };

  const handleInsert = (sql: string, rawExplain: string) => {
    const leadingEmptyLines = getLeadingEmptyLineCount({ statement: sql });
    const leadingLineBreaks = '\n'.repeat(leadingEmptyLines);
    const comment = rawExplain ? `${leadingLineBreaks}/* ${rawExplain} */\n` : '';
    const textToInsert = comment ? `${comment}${sql.trim()}\n` : sql;

    acceptSuggestion(textToInsert);
  };

  const resetAll = () => {
    setIsEditMode(false);
    setIsGenerateMode(false);
    setShowSuggestedSqlModal(false);
    setExplanation('');
    setSuggestion('');
    setSuggestionExplanation('');
    setAssumptions('');
    setNql('');
    setIsLoading(false);
    setLoadingStatusText('');
    setErrorStatusText('');
    setParser(undefined);
    setParseError(undefined);
    setInputValue('');
  };

  const toggleOpen = () => {
    setIsAnimating(prev => {
      return prev === 'no' ? (isExpanded ? 'contract' : 'expand') : prev;
    });
    if (isExpanded) {
      resetAll();
    }
    setIsExpanded(prev => {
      const expanded = !prev;
      setInLocalStorage('hue.aiAssistBar.isExpanded', expanded);
      return expanded;
    });
  };

  const updateInputModeOnStatementChange = (
    previousSelection: string | undefined,
    newSelection: string
  ) => {
    const editorWasEmpty = previousSelection?.trim() === '';
    const userClearedEditor = !editorWasEmpty && newSelection === '';
    const userTypedInEmptyEditor = editorWasEmpty && newSelection !== '';

    if (userClearedEditor) {
      setIsEditMode(false);
    } else if (userTypedInEmptyEditor) {
      setIsGenerateMode(false);
    }
  };

  useEffect(() => {
    loadParser();

    const selectionChanged = lastSelectedStatement.current !== selectedStatement;
    if (selectionChanged) {
      updateInputModeOnStatementChange(lastSelectedStatement?.current, selectedStatement);

      setSuggestion('');
      setAssumptions('');
      lastSelectedStatement.current = selectedStatement;

      if (parser) {
        const newParseError = parser?.parseSyntax('', selectedStatement.trim()) as ParseError;
        setParseError(newParseError);
      }
    }

    if (parser) {
      lastSelectedStatement.current = selectedStatement;
      const newParseError = parser?.parseSyntax('', selectedStatement.trim()) as ParseError;
      setParseError(newParseError);
    }
  }, [selectedStatement, parser]);

  useEffect(() => {
    const EDITOR_CURSOR_POSITION_CHANGE_EVENT = 'cursor-changed';
    const handleEditorCursorPostionChange = (event: CustomEvent) => {
      cursorPosition.current = event.detail;
    };
    document.addEventListener(
      EDITOR_CURSOR_POSITION_CHANGE_EVENT,
      handleEditorCursorPostionChange as any
    );
    return () => {
      document.removeEventListener(
        EDITOR_CURSOR_POSITION_CHANGE_EVENT,
        handleEditorCursorPostionChange as any
      );
    };
  }, []);

  return (
    <>
      <AnimatedLauncher
        onAnimationEnd={() => {
          setIsAnimating('no');
          const barStatus = isExpanded ? 'expanded' : 'collapsed';
          huePubSub.publish(`aiassistbar.bar.${barStatus}`);
        }}
        isAnimating={isAnimating}
        isExpanded={isExpanded}
        isLoading={isLoading}
        loadingStatusText={loadingStatusText}
        errorStatusText={errorStatusText}
        onExpandClick={toggleOpen}
        onCloseErrorClick={() => setErrorStatusText('')}
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
            'hue-ai-assist-bar__content--expanded': isExpanded,
            'hue-ai-assist-bar__content--contracting': isAnimating === 'contract'
          })}
        >
          <AssistToolbar
            isGenerateMode={isGenerateMode}
            isLoading={isLoading}
            inputValue={inputValue}
            setErrorStatusText={setErrorStatusText}
            setIsGenerateMode={setIsGenerateMode}
            setIsEditMode={setIsEditMode}
            isEditMode={isEditMode}
            onInputSubmit={handleToobarInputSubmit}
            onInputChanged={setInputValue}
            inputExpanded={inputExpanded}
            loadExplanation={loadExplanation}
            parsedStatement={parsedStatement}
            loadOptimization={loadOptimization}
            loadFixSuggestion={loadFixSuggestion}
            parseError={parseError}
            inputPrefill={inputPrefill}
          />
        </div>
        <AnimatedCloseButton
          title="Close AI assistbar"
          className={classNames('hue-ai-assistbar__close-btn', {
            'hue-ai-assistbar__close-btn--showing': isExpanded,
            'hue-ai-assistbar__close-btn--hiding': isAnimating === 'contract'
          })}
          onClick={toggleOpen}
        />
      </div>
      {showSuggestedSqlModal && (
        <AiPreviewModal
          autoFormat={!explanation}
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
          nql={nql}
          lineNumberStart={getSelectedLineNumbers(parsedStatement).firstLine}
          showCopyToClipboard={!explanation}
          dialect={lastDialect.current}
          keywordCase={keywordCase}
        />
      )}
    </>
  );
};
export default AiAssistBar;
