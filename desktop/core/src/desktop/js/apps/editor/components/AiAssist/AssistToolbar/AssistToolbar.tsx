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
import ToolbarInput from './ToolbarInput';

import { ParseError } from 'utils/parseError';

import './AssistToolbar.scss';

interface AssistToolbarProps {
  isGenerateMode: boolean;
  isLoading: boolean;
  setErrorStatusText: React.Dispatch<React.SetStateAction<string>>;
  setIsGenerateMode: React.Dispatch<React.SetStateAction<boolean>>;
  setIsEditMode: React.Dispatch<React.SetStateAction<boolean>>;
  isEditMode: boolean;
  inputExpanded: boolean;
  loadExplanation: (statement: string) => Promise<void>;
  parsedStatement: any;
  loadOptimization: (statement: string) => Promise<void>;
  loadFixSuggestion: (statement: string) => Promise<void>;
  parseError: ParseError | undefined;
  className?: string;
  onInputSubmit: (value: string) => void;
}

function AssistToolbar({
  isGenerateMode,
  isLoading,
  setErrorStatusText,
  setIsGenerateMode,
  setIsEditMode,
  isEditMode,
  inputExpanded,
  loadExplanation,
  parsedStatement,
  loadOptimization,
  loadFixSuggestion,
  parseError,
  onInputSubmit
}: AssistToolbarProps) {
  return (
    <Toolbar
      className="hue-ai-assist-bar__toolbar"
      content={() => (
        <>
          <ToolbarButton
            className={classNames({
              'hue-ai-assist-bar__toolbar-button--active': isGenerateMode
            })}
            disabled={isLoading}
            title="Generate SQL using natural language"
            aria-label="Generate SQL using natural language"
            icon={<CommentOutlined />}
            onClick={() => {
              setErrorStatusText('');
              setIsGenerateMode(prev => !prev);
              setIsEditMode(false);
            }}
          >
            {!isEditMode ? 'Generate' : ''}
          </ToolbarButton>
          <ToolbarInput
            expanded={isGenerateMode && inputExpanded}
            placeholder="E.g. How many of our unique website vistors are using Mac?"
            onSubmit={onInputSubmit}
          />
          <ToolbarButton
            className={classNames({
              'hue-ai-assist-bar__toolbar-button--active': isEditMode
            })}
            disabled={isLoading}
            title="Edit SQL using natural language"
            aria-label="Edit SQL using natural language"
            icon={<EditOutlined />}
            onClick={() => {
              setErrorStatusText('');
              setIsEditMode(prev => !prev);
              setIsGenerateMode(false);
            }}
          >
            {!isGenerateMode ? 'Edit' : ''}
          </ToolbarButton>
          <ToolbarInput
            expanded={isEditMode && inputExpanded}
            placeholder="E.g. only inlcude people under 50 years"
            onSubmit={onInputSubmit}
          />
          <ToolbarButton
            disabled={isLoading}
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
            disabled={isLoading}
            icon={<ThunderboltOutlined />}
          >
            {!inputExpanded ? 'Optimize' : ''}
          </ToolbarButton>
          <ToolbarButton
            onClick={() => {
              setErrorStatusText('');
              loadFixSuggestion(parsedStatement?.statement);
            }}
            disabled={!parseError || isLoading}
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
