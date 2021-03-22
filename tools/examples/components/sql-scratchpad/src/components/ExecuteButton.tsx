import React, { FC } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';

export interface ExecuteButtonProps {
  activeExecutable?: SqlExecutable
}

interface ExecuteButtonElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ExecuteButton: FC<ExecuteButtonProps> = React.memo(({ activeExecutable }) => {
  const newNode = document.createElement('query-editor-execute-button');
  newNode.setAttribute('executable', '');
  (newNode as ExecuteButtonElement).executable = activeExecutable;

  return <div
    ref={
      (element: HTMLDivElement | null) => {
        if (element) {
          element.innerHTML = '';
          element.appendChild(newNode);
        }
      }
    }
  />
});
