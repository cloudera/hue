import React, { FC } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';

export interface ResultTableProps {
  activeExecutable?: SqlExecutable
}

interface ResultTableElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ResultTable: FC<ResultTableProps> = React.memo(({ activeExecutable }) => {
  const newNode = document.createElement('query-editor-result-table');
  newNode.setAttribute('executable', '');
  (newNode as ResultTableElement).executable = activeExecutable;

  return <div
    ref={
      (element: HTMLDivElement | null) => {
        if (element) {
          element.innerHTML = '';
          element.appendChild(newNode)
        }
      }
    }
  />
})
