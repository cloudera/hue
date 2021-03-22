import React, { FC } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';

export interface ExecuteProgressProps {
  activeExecutable?: SqlExecutable
}

interface ProgressBarElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ExecuteProgress: FC<ExecuteProgressProps> = React.memo(({ activeExecutable }) => {
  const newNode = document.createElement('query-editor-progress-bar');
  newNode.setAttribute('executable', '');
  (newNode as ProgressBarElement).executable = activeExecutable;

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
});
