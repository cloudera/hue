import React, { FC } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';

export interface ExecuteLimitProps {
  activeExecutable?: SqlExecutable
}

interface ExecuteLimitElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ExecuteLimit: FC<ExecuteLimitProps> = React.memo(({ activeExecutable }) => {
  const newNode = document.createElement('query-editor-limit-input');
  newNode.setAttribute('executable', '');
  (newNode as ExecuteLimitElement).executable = activeExecutable;

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
