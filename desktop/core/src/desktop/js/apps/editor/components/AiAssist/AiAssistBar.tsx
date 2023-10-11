import React, { FunctionComponent, useState, useEffect, useRef } from 'react';
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

  const [isLoadingSuggestion, setIsLoadingSuggestion] = useState(false);
  const [isGeneratingSql, setIsGeneratingSql] = useState(false);
  const [parser, setParser] = useState<SyntaxParser>();
  const [parseError, setParseError] = useState<ParseError | undefined>();

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

  const handleStatusUpdate = (status: string) => {
    setLoadingStatusText(status);
  };

  const handleApiError = (status: string) => {
    setErrorStatusText(status);
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
    // console.info(sql, assumptions);
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
    // console.info(nql, sqlToModify);
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
    // console.info('setSuggestion:', sql);
    // console.info('setAssumptions', assumptions);
    setSuggestion(sql);
    setAssumptions(assumptions);
    setShowSuggestedSqlModal(true);

    setIsLoading(false);
  };

  const loadOptimization = async (statement: string) => {
    setIsLoading(true);
    const dialect = lastDialect.current;
    const { sql, explanation, error } = await generateOptimizedSql({
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

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && inputExpanded) {
      const userInput = (event.target as HTMLInputElement).value;
      const sqlStatmentToModify = parsedStatement.statement;
      if (isGenerateMode) {
        generateSqlQuery(userInput, currentExecutable);
      } else if (isEditMode) {
        // console.info('parsedStatement:', parsedStatement);
        // return;
        editSqlQuery(userInput, sqlStatmentToModify, currentExecutable);
      }
    }
  };

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

      // Clear any leftover sugestions
      const newParseError = parser?.parseSyntax('', selectedStatement.trim()) as ParseError;
      setParseError(newParseError);
    }

    if (selectionChanged) {
      setSuggestion('');
      setAssumptions('');
    }
  }, [selectedStatement, parser]);

  // const cleanedSqlStatement = removeLeadingLineBreaks(removeComments(selectedStatement));

  const renderMovingCircle = () => {
    return (
      <svg
        className="hue-ai-assist-bar__icon-loading-dots"
        xmlns="http://www.w3.org/2000/svg"
        width="14"
        height="14"
        viewBox="0 0 24 24"
      >
        <circle cx="18" cy="12" r="0" fill="#EDF7FF">
          <animate
            attributeName="r"
            begin=".67"
            calcMode="spline"
            dur="1.5s"
            keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8"
            repeatCount="indefinite"
            values="0;2;0;0"
          />
        </circle>
        <circle cx="12" cy="12" r="0" fill="#EDF7FF">
          <animate
            attributeName="r"
            begin=".33"
            calcMode="spline"
            dur="1.5s"
            keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8"
            repeatCount="indefinite"
            values="0;2;0;0"
          />
        </circle>
        <circle cx="6" cy="12" r="0" fill="#EDF7FF">
          <animate
            attributeName="r"
            begin="0"
            calcMode="spline"
            dur="1.5s"
            keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8"
            repeatCount="indefinite"
            values="0;2;0;0"
          />
        </circle>
      </svg>
    );
  };

  const renderInputField = ({ expanded, placeholder }) => {
    return (
      <li
        className={classNames(
          'hue-toolbar-button__wrapper',
          'hue-ai-assist-bar__toolbar__input-wrapper',
          {
            'hue-ai-assist-bar__toolbar__input-wrapper--expanded': expanded
          }
        )}
      >
        {expanded && (
          <input
            placeholder={placeholder}
            type="text"
            autoFocus
            spellCheck="false"
            className="hue-ai-assist-bar__generate-text-input"
            // onChange={evt => console.info(evt.target.value, evt)}
            onKeyDown={handleKeyDown}
          />
        )}
      </li>
    );
  };

  const renderCloseButton = () => {
    return (
      <div
        title="Close AI assisbar"
        id="icon"
        className={classNames('hue-ai-assistbar__close-btn', {
          'hue-ai-assistbar__close-btn--expanded': isExpanded
        })}
        onClick={() => {
          setIsExpanded(false);
        }}
      >
        {
          // TODO: the spans are needed for the close arrow. Move to separate component. -->
        }
        <span></span>
        <span></span>
        <span></span>
      </div>
    );
  };

  const renderCloseErrorButton = () => {
    return (
      <div
        title="Close error message"
        id="icon"
        className="hue-ai-assistbar__error-close-btn"
        onClick={() => {
          setErrorStatusText('');
        }}
      >
        {
          // TODO: the spans are needed for the close arrow. Move to separate component. -->
        }
        <span></span>
        <span></span>
        <span></span>
      </div>
    );
  };

  return (
    <>
      <div
        onAnimationEnd={event => {
          // event.stopPropagation();
          // if (event.target === event.currentTarget) {
          // setIsLoading(false);
        }}
        className={classNames('hue-ai-assist-bar__icon', {
          'hue-ai-assist-bar__icon--expanding': isAnimating === 'expand',
          'hue-ai-assist-bar__icon--expanded': isExpanded,
          'hue-ai-assist-bar__icon--loading': isExpanded && isLoading,
          'hue-ai-assist-bar__icon--loading-with-status':
            isExpanded && isLoading && loadingStatusText,
          'hue-ai-assist-bar__icon--error': !!errorStatusText
        })}
        onClick={() => {
          if (isExpanded) {
            setIsLoading(false);
          } else {
            setIsExpanded(true);
            setIsAnimating(prev => (prev === 'no' ? (isExpanded ? 'contract' : 'expand') : prev));
          }
        }}
      >
        {isExpanded && isLoading && renderMovingCircle()}
        {isExpanded && isLoading && (
          <div className="hue-ai-assist-bar__icon-loading-status">{loadingStatusText}</div>
        )}
        {isExpanded && errorStatusText && (
          <>
            {renderCloseErrorButton()}
            <div className="hue-ai-assist-bar__icon-error-text">{errorStatusText}</div>
          </>
        )}
      </div>
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
                {renderInputField({
                  expanded: isGenerateMode && inputExpanded,
                  placeholder: 'E.g. How many of our unique website vistors are using Mac?'
                })}

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

                {renderInputField({
                  expanded: isEditMode && inputExpanded,
                  placeholder: 'E.g. only inlcude people under 50 years'
                })}

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
        </div>
        {renderCloseButton()}
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

          // suggestion={`
          // SELECT *
          // FROM (select * from
          //   (select * from people where date_of_birth > '1990-01-15')
          //     where gender = 'Male'
          //   )
          // WHERE height_in_feet BETWEEN 5 AND 6;
          // `}
          //         showDiffFrom={`
          // SELECT *
          // FROM people
          // WHERE date_of_birth > '1990-01-15'
          //   AND gender = 'Male'
          //   AND height_in_feet BETWEEN 5 AND 6;
          // `}
          //         assumptions={`
          // 1. That the employees and salaries tables have a shared id column
          // 2. That the salaries table has a gender and amount column
          // 3. That the average salary of male employees is to be calculated from the salaries table`}
          // suggestion={`
          // SELECT COUNT(*) FROM employees
          // INNER JOIN salaries ON employees.id = salaries.employee_id
          // WHERE employees.gender = 'female'
          // AND salaries.amount > (SELECT AVG(amount) FROM salaries WHERE employees.gender = 'male');`.trim()}
        />
      )}
    </>
  );
};
export default AiAssistBar;
