import React, { FunctionComponent } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { stackoverflowDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import Alert from 'cuix/dist/components/Alert/Alert';
import LinkButton from 'cuix/dist/components/Button/LinkButton';
import BorderlessButton from 'cuix/dist/components/Button/BorderlessButton';

import { fluidxSlate800, fluidxSpacingS, fluidxSpacingXs } from '@cloudera/cuix-core/variables';
import GetStartedIcon from '@cloudera/cuix-core/icons/react/GetStartedIcon';
import SqlAssistantIcon from '@cloudera/cuix-core/icons/react/SqlAssistantIcon';
import FaultToleranceIcon from '@cloudera/cuix-core/icons/react/FaultToleanceIcon';

import './SqlCodeSnippet.scss';

interface SqlCodeSnippetProps {
  acceptMsg?: string;
  onSuggestFixClick?(statement: string): void;
  onAcceptClick?(statement: string): void;
  onGenerateSqlClick?(statement: string): void;
  onExplainSqlClick?(statement: string): void;
  onOptimizeSqlClick?(statement: string): void;
  children: string;
  firstLine: number;
  lastLine: number;
  isSuggestion?: boolean;
  isNLQ?: boolean;
  parseError?:
    | {
        line: number;
        loc: {
          last_column: number;
        };
        text: string;
      }
    | undefined;
  hideSuggestFix?: boolean;
  explanation?: string;
  topInfoBar: string;
  isLoading?: boolean;
}

const SqlCodeSnippet = ({
  acceptMsg,
  children: sqlStatement,
  firstLine,
  isSuggestion,
  isNLQ,
  lastLine,
  hideSuggestFix = false,
  onSuggestFixClick = () => {},
  onAcceptClick = () => {},
  onGenerateSqlClick = () => {},
  onExplainSqlClick = () => {},
  onOptimizeSqlClick = () => {},
  topInfoBar,
  parseError,
  explanation
}: SqlCodeSnippetProps) => {
  const renderParseError = () => {
    // TODO: i18n
    const msg = `The SQL statement contains a syntax error on line ${firstLine + parseError.line}:${
      parseError.loc.last_column
    }, see '${parseError.text}'.`;
    return (
      <div className="hue-explain-sql--parse-alert">
        {msg}
        <div className="hue-flex-expander"></div>
        {!hideSuggestFix && (
          <BorderlessButton
            size="small"
            className="hue-explain-sql--alert-button"
            icon={<GetStartedIcon />}
            onClick={() => onSuggestFixClick(sqlStatement)}
          >
            Help me fix it
          </BorderlessButton>
        )}
      </div>
    );
  };

  // TODO: don't use the alert. Use custom action component...
  const renderSuggestion = () => (
    <div className="hue-explain-sql--suggestion-alert">
      <div className="hue-flex-expander"></div>
      <BorderlessButton
        size="small"
        className="hue-explain-sql--alert-button"
        icon={<GetStartedIcon />}
        onClick={() => onAcceptClick(sqlStatement)}
      >
        Accept suggessted change
      </BorderlessButton>
    </div>
  );

  const renderSqlActionBar = () => (
    <div className="hue-explain-sql--sql-actions-bar">
      <div className="hue-flex-expander"></div>

      <BorderlessButton
        size="small"
        disabled={!!explanation}
        className="hue-explain-sql--alert-button"
        icon={<SqlAssistantIcon />}
        onClick={() => onExplainSqlClick(sqlStatement)}
      >
        Explain
      </BorderlessButton>

      <BorderlessButton
        size="small"
        className="hue-explain-sql--alert-button"
        icon={<FaultToleranceIcon />}
        onClick={() => onOptimizeSqlClick(sqlStatement)}
      >
        Optimize
      </BorderlessButton>
    </div>
  );

  const renderNqlActionBar = () => (
    <div className="hue-explain-sql--nql-actions-bar">
      <div className="hue-flex-expander"></div>
      <BorderlessButton
        size="small"
        className="hue-explain-sql--alert-button"
        icon={<GetStartedIcon />}
        onClick={() => onGenerateSqlClick(sqlStatement)}
      >
        Generate SQL
      </BorderlessButton>
    </div>
  );

  // console.info(!explanation && !parseError && !isNLQ);

  return (
    <div className="hue-explain-sql__code-wrapper">
      <p className="hue-explain-sql__top-info-bar">{topInfoBar}</p>
      <SyntaxHighlighter
        className="hue-explain-sql__highlighter"
        language={isNLQ ? 'text' : 'SQL'}
        style={stackoverflowDark}
        customStyle={{
          backgroundColor: fluidxSlate800,
          padding: `${fluidxSpacingXs} ${fluidxSpacingS}`
        }}
        codeTagProps={{ className: 'hue-explain-sql__code' }}
      >
        {sqlStatement}
      </SyntaxHighlighter>
      {explanation && <div className="hue-explain-sql--explanation">{explanation}</div>}
      {!isSuggestion && !parseError && !isNLQ && renderSqlActionBar()}
      {parseError && renderParseError()}
      {isSuggestion && renderSuggestion()}
      {isNLQ && !hideSuggestFix && renderNqlActionBar()}
    </div>
  );
};

export default SqlCodeSnippet;
