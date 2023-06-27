import React from 'react';
import classNames from 'classnames';
import {
  BugOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  EditOutlined,
  CommentOutlined
} from '@ant-design/icons';

import Toolbar, { ToolbarButton } from '../../../../../reactComponents/Toolbar/Toolbar';
import AiAssistToolbarInput from './AiAssistToolbarInput';

import { ParseError } from 'utils/parseError';

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
  parseError: ParseError | undefined;
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
  parseError,
  onInputSubmit,
  onInputChanged,
}: AssistToolbarProps) {
  const [isAnimatingInput, setIsAnimatingInput] = React.useState(false);
  const handOnCancelInput = () => {
    setIsGenerateMode(false);
    setIsEditMode(false);
  };

  const hasSelectedStatement = parsedStatement?.statement?.trim();

  return (
    <Toolbar
      className="hue-ai-assist-toolbar"
      content={() => (
        <>
          <ToolbarButton
            className={classNames({
              'hue-ai-assist-toolbar__button--active': isGenerateMode
            })}
            disabled={isLoading || hasSelectedStatement}
            title="Generate SQL using natural language"
            aria-label="Generate SQL using natural language"
            icon={<CommentOutlined />}
            onClick={() => {
              setErrorStatusText('');
              setIsGenerateMode(prev => !prev);
              setIsEditMode(false);
              setIsAnimatingInput(true);
            }}
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
          />
          <ToolbarButton
            className={classNames({
              'hue-ai-assist-toolbar__button--active': isEditMode
            })}
            disabled={isLoading || !hasSelectedStatement}
            title="Edit SQL using natural language"
            aria-label="Edit SQL using natural language"
            icon={<EditOutlined />}
            onClick={() => {
              setErrorStatusText('');
              setIsEditMode(prev => !prev);
              setIsGenerateMode(false);
              setIsAnimatingInput(true);
            }}
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
            disabled={isLoading || !hasSelectedStatement}
            title="Explain SQL statements"
            aria-label="Explain SQL statement"
            icon={<BulbOutlined />}
            onClick={() => {
              setErrorStatusText('');
              loadExplanation(parsedStatement?.statement);
            }}
          >
            {!inputExpanded ? 'Explain' : ''}
          </ToolbarButton>
          <ToolbarButton
            onClick={() => {
              setErrorStatusText('');
              loadOptimization(parsedStatement?.statement);
            }}
            title="Optimize your SQL statement"
            disabled={isLoading || !hasSelectedStatement}
            icon={<ThunderboltOutlined />}
          >
            {!inputExpanded ? 'Optimize' : ''}
          </ToolbarButton>
          <ToolbarButton
            onClick={() => {
              setErrorStatusText('');
              loadFixSuggestion(parsedStatement?.statement);
            }}
            disabled={!parseError || isLoading || !hasSelectedStatement}
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
