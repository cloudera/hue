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
import SyntaxHighlighter from 'react-syntax-highlighter';
import { stackoverflowDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { fluidxRed800, fluidxSlate600 } from '@cloudera/cuix-core/variables';

import { diffLines, Change } from 'diff';
import classNames from 'classnames';

import './SyntaxHighlighterDiff.scss';

export const DIFF_INLINE_STYLE = {
  row: { display: 'block' },
  rowEmpty: { backgroundColor: '#212c35' },
  rowAdded: { backgroundColor: fluidxSlate600 },
  rowDeleted: { backgroundColor: fluidxRed800 }
};
const alignLineNumbers = (lineNumber, maxNumberOfLines) => {
  const maxLineNumberCharCount = maxNumberOfLines.toString().length;
  const lineNumberCharCount = lineNumber.toString().length;
  const spacesToAddCount = maxLineNumberCharCount - lineNumberCharCount;
  const spacesToAdd = ' '.repeat(spacesToAddCount);
  return `${lineNumber}${spacesToAdd}`;
};

interface SyntaxHighlighterDiffProps {
  newCode: string;
  oldCode: string;
  lineNumberStart?: number;
}
const SyntaxHighlighterDiff = ({
  newCode,
  oldCode,
  lineNumberStart = 1
}: SyntaxHighlighterDiffProps): JSX.Element => {
  const diff = diffLines(oldCode, newCode);
  const maxNumberOfLines = diff.reduce((total, obj) => total + (obj.count || 1), 0);
  const maxLineNumber = maxNumberOfLines + lineNumberStart;
  const lineColumnNew: string[] = [];
  const lineColumnOld: string[] = [];
  const formattedDiffNew: string[] = [];
  const formattedDiffOld: string[] = [];
  let previousLinesNew = lineNumberStart;
  let previousLinesOld = lineNumberStart;

  diff.forEach((part: Change) => {
    const { removed, added, count } = part;
    const safeCount = count || 1;
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
      previousLinesOld += safeCount;
      previousLinesNew += safeCount;
    } else if (!added) {
      previousLinesOld += safeCount;
    } else if (!removed) {
      previousLinesNew += safeCount;
    }
  });

  const renderModifiedLineNumberColumn = (lineColum, type) => {
    return (
      <pre
        data-testid={`syntax-highlighter-row-nr-col-${type}`}
        className={classNames('hue-syntax-highlighter-diff__line-numbers', {})}
      >
        {lineColum.map(val => {
          const style = {
            ...(val.includes('+') ? DIFF_INLINE_STYLE.rowAdded : {}),
            ...(val.includes('-') ? DIFF_INLINE_STYLE.rowDeleted : {}),
            ...(val === '' ? DIFF_INLINE_STYLE.rowEmpty : {})
          };
          return <div style={style}>{val ? val : ' '}</div>;
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
        {renderModifiedLineNumberColumn(lineColum, type)}
        <SyntaxHighlighter
          data-testid={`syntax-highlighter-${type}`}
          className={classNames('hue-syntax-highlighter-diff__code', {})}
          language="SQL"
          style={stackoverflowDark}
          customStyle={{
            backgroundColor: 'initial',
            padding: 'initial'
          }}
          lineProps={(): React.HTMLProps<HTMLElement> => {
            const line = formattedDiff[lineNumber - 1];
            const diffLine = diff.find(part => {
              const lines: Array<string> = part.value.split('\n');

              return !!lines.find(currLine => {
                return currLine === line;
              });
            });
            const style = {
              ...DIFF_INLINE_STYLE.row,
              ...(!diffLine ? DIFF_INLINE_STYLE.rowEmpty : {}),
              ...(diffLine?.added ? DIFF_INLINE_STYLE.rowAdded : {}),
              ...(diffLine?.removed ? DIFF_INLINE_STYLE.rowDeleted : {})
            };

            lineNumber++;
            // Can't use className prop because of this issue, so styling is set here in JS code
            // https://github.com/react-syntax-highlighter/react-syntax-highlighter/issues/391
            return { style };
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
