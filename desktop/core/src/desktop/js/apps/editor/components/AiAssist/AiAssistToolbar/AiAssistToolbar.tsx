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
import TourIcon from '@cloudera/cuix-core/icons/react/TourIcon';
import Toolbar, { ToolbarButton } from '../../../../../reactComponents/Toolbar/Toolbar';

import AiAssistToolbarInput from './AiAssistToolbarInput';
import { extractLeadingNqlComments, removeComments } from '../PreviewModal/formattingUtils';
import { AiActionModes } from '../sharedTypes';

import './AiAssistToolbar.scss';

type ActionModes = AiActionModes | undefined;
interface AssistToolbarProps {
  showActions: AiActionModes[];
  actionMode: ActionModes;
  setActionMode: React.Dispatch<React.SetStateAction<AiActionModes | undefined>>;
  isLoading: boolean;
  setErrorStatusText: React.Dispatch<React.SetStateAction<string>>;
  inputExpanded: boolean;
  inputPrefill: string;
  inputValue: string;
  loadExplanation: (statement: string) => Promise<void>;
  parsedStatement: { statement: string };
  loadOptimization: (statement: string) => Promise<void>;
  loadFixSuggestion: (statement: string) => Promise<void>;
  loadComments: (statement: string) => Promise<void>;
  isSqlError: boolean;
  className?: string;
  onInputSubmit: (value: string) => void;
  onInputChanged: (value: string) => void;
}

function AssistToolbar({
  showActions,
  actionMode,
  setActionMode,
  isLoading,
  setErrorStatusText,
  inputExpanded,
  inputValue,
  inputPrefill,
  loadExplanation,
  loadComments,
  parsedStatement,
  loadOptimization,
  loadFixSuggestion,
  isSqlError,
  onInputSubmit,
  onInputChanged
}: AssistToolbarProps): JSX.Element {
  const [isAnimatingInput, setIsAnimatingInput] = React.useState(false);

  const handleCancelInput = () => {
    setActionMode(undefined);
  };

  const toggleMode = (modeClicked: AiActionModes) => {
    setErrorStatusText('');
    actionMode === modeClicked ? setActionMode(undefined) : setActionMode(modeClicked);
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

  const handleCommentClick = () => {
    setErrorStatusText('');
    loadComments(parsedStatement?.statement);
  };

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
          {showActions?.includes(AiActionModes.GENERATE) && (
            <>
              <ToolbarButton
                disabled={isLoading}
                title="Generate SQL using natural language"
                aria-label="Generate SQL using natural language"
                icon={<CommentOutlined />}
                onClick={() => toggleMode(AiActionModes.GENERATE)}
              >
                {actionMode === AiActionModes.EDIT ? '' : 'Generate'}
              </ToolbarButton>
              <AiAssistToolbarInput
                isAnimating={isAnimatingInput}
                isLoading={isLoading}
                isExpanded={actionMode === AiActionModes.GENERATE && inputExpanded}
                placeholder="E.g. How many of our unique website vistors are using Mac?"
                onSubmit={onInputSubmit}
                onCancel={handleCancelInput}
                onInputChanged={onInputChanged}
                value={inputValue}
                onAnimationEnded={() => setIsAnimatingInput(false)}
                prefill={inputPrefill}
              />
            </>
          )}
          {showActions?.includes(AiActionModes.EDIT) && (
            <>
              <ToolbarButton
                disabled={isLoading || selectedStatementMissingSql}
                title="Edit selected SQL statement using natural language"
                aria-label="Edit SQL using natural language"
                icon={<EditOutlined />}
                onClick={() => toggleMode(AiActionModes.EDIT)}
              >
                {actionMode === AiActionModes.GENERATE ? '' : 'Edit'}
              </ToolbarButton>
              <AiAssistToolbarInput
                isAnimating={isAnimatingInput}
                isExpanded={actionMode === AiActionModes.EDIT && inputExpanded}
                isLoading={isLoading}
                value={inputValue}
                placeholder="E.g. Only inlcude people under 50 years"
                onSubmit={onInputSubmit}
                onCancel={handleCancelInput}
                onInputChanged={onInputChanged}
                onAnimationEnded={() => setIsAnimatingInput(false)}
                prefill={inputPrefill}
              />
            </>
          )}

          {showActions?.includes(AiActionModes.EXPLAIN) && (
            <ToolbarButton
              disabled={isLoading || selectedStatementMissingSql}
              title="Explain the selected SQL statement"
              aria-label="Explain SQL statement"
              icon={<BulbOutlined />}
              onClick={handleExplainClick}
            >
              {!inputExpanded ? 'Explain' : ''}
            </ToolbarButton>
          )}
          {showActions?.includes(AiActionModes.OPTIMIZE) && (
            <ToolbarButton
              onClick={handleOptimizeClick}
              title="Optimize the selected SQL statement"
              disabled={isLoading || selectedStatementMissingSql}
              icon={<ThunderboltOutlined />}
            >
              {!inputExpanded ? 'Optimize' : ''}
            </ToolbarButton>
          )}
          {showActions?.includes(AiActionModes.FIX) && (
            <ToolbarButton
              title="Fix the selected SQL statement"
              onClick={handleFixClick}
              disabled={!isSqlError || isLoading || selectedStatementMissingSql}
              icon={<BugOutlined />}
            >
              {!inputExpanded ? 'Fix' : ''}
            </ToolbarButton>
          )}
          {showActions?.includes(AiActionModes.COMMENT) && (
            <ToolbarButton
              title="Comment SQL"
              onClick={handleCommentClick}
              disabled={isLoading || selectedStatementMissingSql}
              icon={<TourIcon />}
            >
              {!inputExpanded ? 'Comment' : ''}
            </ToolbarButton>
          )}
        </>
      )}
    />
  );
}

export default AssistToolbar;
