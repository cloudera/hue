import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';
import Executable from 'gethue/src/apps/editor/execution/executable';

export interface ResultTableProps {
  activeExecutable?: Executable
}

interface ResultTableElement extends HTMLElement {
  executable?: Executable;
}

export const ResultTable: FC<ResultTableProps> = ({ activeExecutable }) => {
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
}