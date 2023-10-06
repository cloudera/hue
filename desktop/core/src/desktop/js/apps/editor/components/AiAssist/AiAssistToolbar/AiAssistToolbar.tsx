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

import React from 'react';
import {
  BugOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  EditOutlined,
  CommentOutlined
} from '@ant-design/icons';

import Toolbar, { ToolbarButton } from '../../../../../reactComponents/Toolbar/Toolbar';
import AiAssistToolbarInput from './AiAssistToolbarInput';
import { useKeyboardShortcuts } from '../hooks';
import { extractLeadingNqlComments, removeComments } from '../PreviewModal/FormattingUtils';

import './AiAssistToolbar.scss';

interface AssistToolbarProps {
  isGenerateMode: boolean;
  isLoading: boolean;
  setErrorStatusText: React.Dispatch<React.SetStateAction<string>>;
  setIsGenerateMode: React.Dispatch<React.SetStateAction<boolean>>;
  setIsEditMode: React.Dispatch<React.SetStateAction<boolean>>;
  isEditMode: boolean;
  inputExpanded: boolean;
  inputPrefill: string;
  inputValue: string;
  loadExplanation: (statement: string) => Promise<void>;
  parsedStatement: any;
  loadOptimization: (statement: string) => Promise<void>;
  loadFixSuggestion: (statement: string) => Promise<void>;
  isSqlError: boolean;
  className?: string;
  onInputSubmit: (value: string) => void;
  onInputChanged: (value: string) => void;
}

function AssistToolbar({
  isGenerateMode,
  isLoading,
  setErrorStatusText,
  setIsGenerateMode,
  setIsEditMode,
  isEditMode,
  inputExpanded,
  inputValue,
  inputPrefill,
  loadExplanation,
  parsedStatement,
  loadOptimization,
  loadFixSuggestion,
  isSqlError,
  onInputSubmit,
  onInputChanged
}: AssistToolbarProps) {
  const [isAnimatingInput, setIsAnimatingInput] = React.useState(false);
  const handOnCancelInput = () => {
    setIsGenerateMode(false);
    setIsEditMode(false);
  };

  const toggleGenerateMode = () => {
    setErrorStatusText('');
    setIsGenerateMode(prev => !prev);
    setIsEditMode(false);
    setIsAnimatingInput(true);
  };

  const toggleEditMode = () => {
    setErrorStatusText('');
    setIsEditMode(prev => !prev);
    setIsGenerateMode(false);
    setIsAnimatingInput(true);
  };

  const handleExplainClick = () => {
    setErrorStatusText('');
    loadExplanation(parsedStatement?.statement);
  };

  const handleOptimizeClick = () => {
    setErrorStatusText('');
    loadOptimization(parsedStatement?.statement);
  };

  const handleFixClick = () => {
    setErrorStatusText('');
    loadFixSuggestion(parsedStatement?.statement);
  };

  useKeyboardShortcuts({
    e: toggleEditMode,
    g: toggleGenerateMode,
    x: handleExplainClick,
    o: handleOptimizeClick,
    f: handleFixClick
  });

  const selectedStatement = parsedStatement?.statement?.trim() || '';
  const selectedStatementHasContent = !!selectedStatement;
  const nqlPrompt = extractLeadingNqlComments(selectedStatement);
  const selectedStatementHasNqlCommentOnly =
    nqlPrompt.length > 0 && removeComments(selectedStatement.trim()).length === 0;
  const selectedStatementMissingSql: boolean =
    !selectedStatementHasContent || selectedStatementHasNqlCommentOnly;

  return (
    <Toolbar
      className="hue-ai-assist-toolbar"
      content={() => (
        <>
          <ToolbarButton
            disabled={isLoading || (selectedStatement && !selectedStatementHasNqlCommentOnly)}
            title="Generate SQL using natural language (Command-Ctrl-G)"
            aria-label="Generate SQL using natural language"
            icon={<CommentOutlined />}
            onClick={toggleGenerateMode}
          >
            {!isEditMode ? 'Generate' : ''}
          </ToolbarButton>
          <AiAssistToolbarInput
            isAnimating={isAnimatingInput}
            isLoading={isLoading}
            isExpanded={isGenerateMode && inputExpanded}
            placeholder="E.g. How many of our unique website vistors are using Mac?"
            onSubmit={onInputSubmit}
            onCancel={handOnCancelInput}
            onInputChanged={onInputChanged}
            value={inputValue}
            onAnimationEnded={() => setIsAnimatingInput(false)}
            prefill={inputPrefill}
          />
          <ToolbarButton
            disabled={isLoading || selectedStatementMissingSql}
            title="Edit selected SQL statement using natural language (Command-Ctrl-E)"
            aria-label="Edit SQL using natural language"
            icon={<EditOutlined />}
            onClick={toggleEditMode}
          >
            {!isGenerateMode ? 'Edit' : ''}
          </ToolbarButton>
          <AiAssistToolbarInput
            isAnimating={isAnimatingInput}
            isExpanded={isEditMode && inputExpanded}
            isLoading={isLoading}
            value={inputValue}
            placeholder="E.g. only inlcude people under 50 years"
            onSubmit={onInputSubmit}
            onCancel={handOnCancelInput}
            onInputChanged={onInputChanged}
            onAnimationEnded={() => setIsAnimatingInput(false)}
            prefill={inputPrefill}
          />
          <ToolbarButton
            disabled={isLoading || selectedStatementMissingSql}
            title="Explain selected SQL statement (Command-Ctrl-X)"
            aria-label="Explain SQL statement"
            icon={<BulbOutlined />}
            onClick={handleExplainClick}
          >
            {!inputExpanded ? 'Explain' : ''}
          </ToolbarButton>
          <ToolbarButton
            onClick={handleOptimizeClick}
            title="Optimize selected SQL statement (Command-Ctrl-O)"
            disabled={isLoading || selectedStatementMissingSql}
            icon={<ThunderboltOutlined />}
          >
            {!inputExpanded ? 'Optimize' : ''}
          </ToolbarButton>
          <ToolbarButton
            title="Fix selected SQL statement (Command-Ctrl-F)"
            onClick={handleFixClick}
            disabled={!isSqlError || isLoading || selectedStatementMissingSql}
            icon={<BugOutlined />}
          >
            {!inputExpanded ? 'Fix' : ''}
          </ToolbarButton>
        </>
      )}
    />
  );
}

export default AssistToolbar;
