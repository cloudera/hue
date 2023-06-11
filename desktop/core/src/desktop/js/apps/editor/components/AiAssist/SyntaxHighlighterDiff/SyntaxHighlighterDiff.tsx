import React from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import {
  stackoverflowDark,
  stackoverflowLight
} from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { diffLines, Change } from 'diff';
import classNames from 'classnames';

import './SyntaxHighlighterDiff.scss';

const DIFF_STYLE = {
  row: 'hue-syntax-highlighter-diff__row',
  rowEmpty: 'hue-syntax-highlighter-diff__row--empty',
  rowAdded: 'hue-syntax-highlighter-diff__row--added',
  rowDeleted: 'hue-syntax-highlighter-diff__row--deleted'
};

const alignLineNumbers = (lineNumber, maxNumberOfLines) => {
  const maxLineNumberCharCount = maxNumberOfLines.toString().length;
  const lineNumberCharCount = lineNumber.toString().length;
  const spacesToAddCount = maxLineNumberCharCount - lineNumberCharCount;
  const spacesToAdd = ' '.repeat(spacesToAddCount);
  return `${lineNumber}${spacesToAdd}`;
};

const SyntaxHighlighterDiff = ({
  newCode,
  oldCode,
  lineNumberStart = 1,
}) => {
  const diff = diffLines(oldCode, newCode);
  const maxNumberOfLines = diff.reduce((total, obj) => total + obj.count, 0);
  const maxLineNumber = maxNumberOfLines + lineNumberStart;
  const lineColumnNew: string[] = [];
  const lineColumnOld: string[] = [];
  const formattedDiffNew: string[] = [];
  const formattedDiffOld: string[] = [];
  let previousLinesNew = lineNumberStart;
  let previousLinesOld = lineNumberStart;
  diff.forEach((part: Change, index: number) => {
    const { removed, added, count } = part;
    const lines = part.value.split('\n');

    lines.forEach((line, index) => {
      const oldLineNumber = alignLineNumbers(previousLinesOld + index, maxLineNumber);
      const newLineNumber = alignLineNumbers(previousLinesNew + index, maxLineNumber);

      if (line) {
        if (removed) {
          formattedDiffNew.push(' ');
          lineColumnNew.push('');
          lineColumnOld.push(` ${oldLineNumber} - `);
          formattedDiffOld.push(line);
        } else if (added) {
          lineColumnOld.push('');
          lineColumnNew.push(` ${newLineNumber} + `);
          formattedDiffNew.push(line);
          formattedDiffOld.push(' ');
        } else {
          lineColumnNew.push(` ${newLineNumber}   `);
          lineColumnOld.push(` ${oldLineNumber}   `);
          formattedDiffNew.push(line);
          formattedDiffOld.push(line);
        }
      }
    });
    if (!added && !removed) {
      previousLinesOld += count;
      previousLinesNew += count;
    } else if (!added) {
      previousLinesOld += count;
    } else if (!removed) {
      previousLinesNew += count;
    }
  });

  const renderModifiedLineNumberColumn = lineColum => {
    return (
      <pre className={classNames('hue-syntax-highlighter-diff__line-numbers', {})}>
        {lineColum.map(val => {
          const className = classNames({
            [DIFF_STYLE.rowAdded]: val.includes('+'),
            [DIFF_STYLE.rowDeleted]: val.includes('-'),
            [DIFF_STYLE.rowEmpty]: val === ''
          });
          return <div className={className}>{val ? val : ' '}</div>;
        })}
      </pre>
    );
  };

  const renderSyntaxHighlighterDiff = ({ type }) => {
    let lineNumber = 1;
    const formattedDiff = type === 'old' ? formattedDiffOld : formattedDiffNew;
    const lineColum = type === 'old' ? lineColumnOld : lineColumnNew;

    return (
      <div className="hue-syntax-highlighter-diff__container">
        {renderModifiedLineNumberColumn(lineColum)}
        <SyntaxHighlighter
          className={classNames('hue-syntax-highlighter-diff__code', {})}
          language="SQL"
          style={stackoverflowDark}
          customStyle={{
            backgroundColor: 'initial',
            padding: 'initial'
          }}
          lineProps={() => {
            const line = formattedDiff[lineNumber - 1];
            const diffLine = diff.find(part => {
              const lines: Array<string> = part.value.split('\n');

              return !!lines.find(currLine => {
                return currLine === line;
              });
            });

            let htmlClassname = [
              DIFF_STYLE.row,
              !diffLine ? DIFF_STYLE.rowEmpty : '',
              diffLine?.added ? DIFF_STYLE.rowAdded : '',
              diffLine?.removed ? DIFF_STYLE.rowDeleted : ''
            ]
              .filter(Boolean)
              .join(' ');

            lineNumber++;
            return { class: htmlClassname };
          }}
          wrapLines={true}
        >
          {formattedDiff.join('\n')}
        </SyntaxHighlighter>
      </div>
    );
  };

  return (
    <div className="hue-syntax-highlighter-diff">
      {renderSyntaxHighlighterDiff({ type: 'old' })}
      {renderSyntaxHighlighterDiff({ type: 'new' })}
    </div>
  );
};

export default SyntaxHighlighterDiff;
