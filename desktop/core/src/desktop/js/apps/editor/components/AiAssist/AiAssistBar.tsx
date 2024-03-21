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

import React, { useState, useEffect, useRef } from 'react';
import classNames from 'classnames';
import huePubSub from 'utils/huePubSub';
import { AutocompleteParser } from 'parse/types';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import { generativeFunctionFactory } from 'api/apiAIHelper';
import SqlExecutable from '../../execution/sqlExecutable';
import {
  getRowInterval,
  modifyEditorContents,
  convertToOneBased,
  prependCommentToSql
} from './editorIntegrationUtils';
import AiPreviewModal from './PreviewModal/AiPreviewModal';
import GuardrailsModal from './GuardrailsModal/GuardrailsModal';
import { useKeywordCase } from './hooks';
import { useParser } from './ParserHook';
import AnimatedLauncher from './AnimatedLauncher/AnimatedLauncher';
import AnimatedCloseButton from './AnimatedCloseButton/AnimatedCloseButton';
import AssistToolbar from './AiAssistToolbar/AiAssistToolbar';
import UntrustedAiModal from './UntrustedAiModal/UntrustedAiModal';
import { withGuardrails, GuardrailAlert, GuardrailAlertType } from './guardRails';
import {
  extractLeadingNqlComments,
  removeComments,
  breakLongComments
} from './PreviewModal/formattingUtils';
import { AiActionModes } from './sharedTypes';
import { CURSOR_POSITION_CHANGED_EVENT } from '../../../../ko/bindings/ace/aceLocationHandler';
import { getLastKnownConfig } from '../../../../config/hueConfig';

import './AiAssistBar.scss';

const {
  generateExplanation,
  generateCorrectedSql,
  generateOptimizedSql,
  generateSQLfromNQL,
  generateEditedSQLfromNQL,
  generateCommentedSql
} = generativeFunctionFactory();

const extractTablesAndViews = (sql: string, parser: AutocompleteParser): Array<string> => {
  const result = parser.parseSql(sql, '');
  const tableNames = result.locations
    .filter(loc => loc.type === 'table' || loc.type === 'view')
    .map(loc =>
      // The identifierChain is actually never undefined when the type is table,
      // but the typescript type definition doesn't consider that.
      loc.identifierChain ? loc.identifierChain[loc.identifierChain.length - 1].name : ''
    );
  return tableNames;
};

const breakLines = (input: string): string => {
  const words = input.split(' ');
  let result = '';
  let line = '';

  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (line.length + word.length <= 90) {
      line += word + ' ';
    } else {
      result += line + '\n';
      line = word + ' ';
    }
  }
  return (result += line);
};

const getDbName = (activeExecutable: SqlExecutable | undefined) => {
  // In safari the activeExecutable?.database is null when reloading the
  // editor page, but the executor still has the database name.
  return activeExecutable?.database || activeExecutable?.executor?.database() || '';
};

export interface AiAssistBarProps {
  activeExecutable: SqlExecutable;
}

// This is a react root component and it will be rendered each time the wrapping KO binding
// is responding to an KO observable update. This means that this compoenent will be re-rendered
// even if the activeExecutable is just modified and not replaced (unlike normal react props).
// NOTE that for any future child components the activeExecutable will be considered unmodified.
const AiAssistBar = ({ activeExecutable }: AiAssistBarProps): JSX.Element => {
  const parsedStatement = activeExecutable?.parsedStatement;
  const selectedStatement: string = parsedStatement?.statement || '';
  const lastSelectedStatement = useRef(selectedStatement);

  const [isExpanded, setIsExpanded] = useState(() => {
    const expanded = getFromLocalStorage('hue.aiAssistBar.isExpanded', true);
    huePubSub.publish('aiassistbar.bar.toggled', expanded);
    return expanded;
  });
  const [isAnimating, setIsAnimating] = useState<'no' | 'expand' | 'contract'>('no');
  const [actionMode, setActionMode] = useState<AiActionModes | undefined>();
  const [showSuggestedSqlModal, setShowSuggestedSqlModal] = useState(false);
  const [showGuardrailsModal, setShowGuardrailsModal] = useState(false);
  const [explanation, setExplanation] = useState('');
  const [summary, setSummary] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const [suggestionExplanation, setSuggestionExplanation] = useState('');
  const [assumptions, setAssumptions] = useState('');
  const [guardrailAlert, setGuardrailAlert] = useState<GuardrailAlert>();
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatusText, setLoadingStatusText] = useState('');
  const [errorStatusText, setErrorStatusText] = useState('');
  const [nql, setNql] = useState('');
  const [inputValue, setInputValue] = useState<string>('');
  const { syntaxParser, sqlDialect, hasIncorrectSql, autocompleteParser } =
    useParser(activeExecutable);

  const cursorPosition = useRef<{ row: number; column: number }>({ row: 1, column: 1 });
  const keywordCase = useKeywordCase(syntaxParser, selectedStatement);
  const inputExpanded = actionMode === AiActionModes.EDIT || actionMode === AiActionModes.GENERATE;
  const inputPrefill = inputExpanded ? extractLeadingNqlComments(selectedStatement) : '';

  const handleStatusUpdate = (status: string) => {
    setLoadingStatusText(status);
  };

  const handleApiError = (status: string) => {
    setErrorStatusText(status);
  };

  const loadExplanation = async (statement: string) => {
    setIsLoading(true);
    const executor = activeExecutable?.executor;
    const databaseName = getDbName(activeExecutable);
    const dialect = sqlDialect;
    try {
      const { explain, summary } = await generateExplanation({
        statement,
        dialect,
        executor,
        databaseName,
        onStatusChange: handleStatusUpdate
      });

      setSuggestion(statement);
      setExplanation(breakLines(explain));
      setSummary(breakLines(summary));
      setShowSuggestedSqlModal(true);
      setActionMode(AiActionModes.EXPLAIN);
    } catch (error) {
      handleApiError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const generateSqlQuery = async (nql: string, activeExecutable: SqlExecutable) => {
    setIsLoading(true);
    setGuardrailAlert(undefined);
    setErrorStatusText('');
    const executor = activeExecutable?.executor;
    const databaseName = getDbName(activeExecutable);
    const dialect = sqlDialect;
    let sql, assumptions, guardrailAlert;
    try {
      ({ sql, assumptions, guardrailAlert } = await withGuardrails(generateSQLfromNQL)({
        nql,
        databaseName,
        executor,
        dialect,
        onStatusChange: handleStatusUpdate
      }));

      if (guardrailAlert?.type !== GuardrailAlertType.INVALID_AI_RESPONSE) {
        setNql(nql);
        setSuggestion(sql);
        setAssumptions(assumptions);
        setShowSuggestedSqlModal(true);
        setInputValue('');
      }
    } catch (error) {
      handleApiError(error.message);
    } finally {
      setGuardrailAlert(guardrailAlert);
      setIsLoading(false);
    }
  };

  const editSqlQuery = async (
    nql: string,
    sqlToModify: string,
    activeExecutable: SqlExecutable
  ) => {
    setIsLoading(true);
    setGuardrailAlert(undefined);
    const executor = activeExecutable?.executor;
    const databaseName = getDbName(activeExecutable);
    const dialect = sqlDialect;
    const tableNamesUsed = extractTablesAndViews(sqlToModify, autocompleteParser);

    let sql, assumptions, guardrailAlert;
    try {
      ({ sql, assumptions, guardrailAlert } = await withGuardrails(generateEditedSQLfromNQL)({
        nql,
        previousNql: inputPrefill,
        tableNamesUsed,
        sql: sqlToModify,
        databaseName,
        executor,
        dialect,
        onStatusChange: handleStatusUpdate
      }));
      if (guardrailAlert?.type !== GuardrailAlertType.INVALID_AI_RESPONSE) {
        setNql(nql);
        setSuggestion(sql);
        setAssumptions(assumptions);
        setShowSuggestedSqlModal(true);
      }
    } catch (error) {
      handleApiError(error.message);
    } finally {
      setGuardrailAlert(guardrailAlert);
      setIsLoading(false);
      setInputValue('');
    }
  };

  const loadOptimization = async (statement: string) => {
    setIsLoading(true);
    setActionMode(AiActionModes.OPTIMIZE);
    setGuardrailAlert(undefined);
    const executor = activeExecutable?.executor;
    const databaseName = getDbName(activeExecutable);
    const dialect = sqlDialect;
    let sql, explain, guardrailAlert;
    try {
      ({ sql, explain, guardrailAlert } = await withGuardrails(generateOptimizedSql)({
        statement,
        databaseName,
        executor,
        dialect,
        onStatusChange: handleStatusUpdate
      }));

      if (guardrailAlert?.type !== GuardrailAlertType.INVALID_AI_RESPONSE) {
        setSuggestion(sql);
        setSuggestionExplanation(explain);
        setShowSuggestedSqlModal(true);
      }
    } catch (error) {
      handleApiError(error.message);
    } finally {
      setGuardrailAlert(guardrailAlert);
      setIsLoading(false);
    }
  };

  const loadFixSuggestion = async (statement: string) => {
    setIsLoading(true);
    setGuardrailAlert(undefined);
    const dialect = sqlDialect;
    const executor = activeExecutable?.executor;
    const databaseName = getDbName(activeExecutable);
    let sql, explain, guardrailAlert;
    try {
      ({ sql, explain, guardrailAlert } = await withGuardrails(generateCorrectedSql)({
        statement,
        databaseName,
        executor,
        dialect,
        onStatusChange: handleStatusUpdate
      }));
      if (guardrailAlert?.type !== GuardrailAlertType.INVALID_AI_RESPONSE) {
        setSuggestion(sql);
        setSuggestionExplanation(explain);
        setShowSuggestedSqlModal(true);
        setActionMode(AiActionModes.FIX);
      }
    } catch (error) {
      handleApiError(error.message);
    } finally {
      setGuardrailAlert(guardrailAlert);
      setIsLoading(false);
    }
  };

  const loadComments = async (statement: string) => {
    setIsLoading(true);
    setGuardrailAlert(undefined);
    const dialect = sqlDialect;
    let sql, guardrailAlert;
    try {
      ({ sql, guardrailAlert } = await withGuardrails(generateCommentedSql)({
        statement,
        dialect,
        onStatusChange: handleStatusUpdate
      }));
      if (guardrailAlert?.type !== GuardrailAlertType.INVALID_AI_RESPONSE) {
        const properlyCommentedSql = breakLongComments(sql);
        setSuggestion(properlyCommentedSql);
        setShowSuggestedSqlModal(true);
        setActionMode(AiActionModes.EXPLAIN);
      }
    } catch (error) {
      handleApiError(error.message);
    } finally {
      setGuardrailAlert(guardrailAlert);
      setIsLoading(false);
    }
  };

  const handleToobarInputSubmit = (userInput: string) => {
    const sqlStatmentToModify = parsedStatement.statement;
    if (actionMode === AiActionModes.GENERATE) {
      generateSqlQuery(userInput, activeExecutable);
    } else if (actionMode === AiActionModes.EDIT) {
      editSqlQuery(userInput, sqlStatmentToModify, activeExecutable);
    }
  };

  const handleInsert = (sql: string, rawExplain: string) => {
    const sqlToInsert = prependCommentToSql(rawExplain, sql);
    modifyEditorContents({
      sqlToInsert: sqlToInsert,
      actionMode,
      activeStatementInEditor: parsedStatement,
      cursorPosition: convertToOneBased(cursorPosition.current),
      autocompleteParser
    });
    setShowSuggestedSqlModal(false);
    resetAll();
  };

  const resetAll = () => {
    setActionMode(undefined);
    setShowSuggestedSqlModal(false);
    setExplanation('');
    setSummary('');
    setSuggestion('');
    setSuggestionExplanation('');
    setAssumptions('');
    setGuardrailAlert(undefined);
    setNql('');
    setIsLoading(false);
    setLoadingStatusText('');
    setErrorStatusText('');
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
      huePubSub.publish('aiassistbar.bar.toggled', expanded);
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
    const nqlPrompt = extractLeadingNqlComments(newSelection);
    const statementOnlyContainsNql =
      nqlPrompt.length && removeComments(newSelection.trim()).length === 0;

    if (actionMode === AiActionModes.EDIT && (userClearedEditor || statementOnlyContainsNql)) {
      setActionMode(undefined);
    } else if (actionMode === AiActionModes.GENERATE && userTypedInEmptyEditor) {
      setActionMode(undefined);
    }
  };

  useEffect(() => {
    updateInputModeOnStatementChange(lastSelectedStatement?.current, selectedStatement);
    setSuggestion('');
    setAssumptions('');
    setGuardrailAlert(undefined);
    lastSelectedStatement.current = selectedStatement;
  }, [selectedStatement]);

  useEffect(() => {
    // FOR EDITOR v2
    // const EDITOR_CURSOR_POSITION_CHANGE_EVENT = 'cursor-changed';
    // const handleEditorCursorPostionChange = (event: CustomEvent) => {
    //   cursorPosition.current = event.detail;
    // };
    // document.addEventListener(
    //   EDITOR_CURSOR_POSITION_CHANGE_EVENT,
    //   handleEditorCursorPostionChange as EventListener
    // );
    // return () => {
    //   document.removeEventListener(
    //     EDITOR_CURSOR_POSITION_CHANGE_EVENT,
    //     handleEditorCursorPostionChange as EventListener
    //   );
    // };

    // FOR EDITOR v1
    const subscription = huePubSub.subscribe(CURSOR_POSITION_CHANGED_EVENT, ({ position }) => {
      const { row, column } = position || { row: 0, column: 0 };
      cursorPosition.current = { row, column };
    });

    return () => {
      subscription.remove();
    };
  }, []);

  const showBarInlineWarning = guardrailAlert?.type === GuardrailAlertType.INVALID_AI_RESPONSE;
  const diffSource = actionMode !== AiActionModes.GENERATE ? parsedStatement?.statement : undefined;

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
        warningStatusText={showBarInlineWarning ? guardrailAlert?.title : ''}
        onExpandClick={toggleOpen}
        onCloseErrorClick={() => setErrorStatusText('')}
        onMoreWarningInfoClick={() => {
          setShowGuardrailsModal(true);
        }}
        onCloseWarningClick={() => setGuardrailAlert(undefined)}
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
            showActions={getLastKnownConfig()?.hue_config?.ai_enabled_SQL_tasks as AiActionModes[]}
            actionMode={actionMode}
            setActionMode={setActionMode}
            isLoading={isLoading}
            inputValue={inputValue}
            setErrorStatusText={setErrorStatusText}
            onInputSubmit={handleToobarInputSubmit}
            onInputChanged={setInputValue}
            inputExpanded={inputExpanded}
            loadExplanation={loadExplanation}
            parsedStatement={parsedStatement}
            loadOptimization={loadOptimization}
            loadFixSuggestion={loadFixSuggestion}
            loadComments={loadComments}
            isSqlError={hasIncorrectSql}
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
      <UntrustedAiModal
        aiAssistBarExpanded={isExpanded}
        onCloseBar={() => isExpanded && toggleOpen()}
      />
      {showGuardrailsModal && guardrailAlert && (
        <GuardrailsModal
          open
          alert={guardrailAlert}
          onClose={() => {
            setShowGuardrailsModal(false);
            setGuardrailAlert(undefined);
          }}
        />
      )}
      {showSuggestedSqlModal && actionMode && (
        <AiPreviewModal
          actionMode={actionMode}
          open
          onCancel={resetAll}
          onInsert={sql => handleInsert(sql, explanation)}
          primaryButtonLabel={explanation ? 'Insert as comment' : 'Insert'}
          suggestion={suggestion}
          showDiffFrom={diffSource}
          assumptions={assumptions}
          explanation={explanation || suggestionExplanation}
          summary={summary}
          nql={nql}
          lineNumberStart={getRowInterval(parsedStatement).firstRow}
          dialect={sqlDialect}
          keywordCase={keywordCase}
          guardrailAlert={guardrailAlert}
        />
      )}
    </>
  );
};
export default AiAssistBar;
