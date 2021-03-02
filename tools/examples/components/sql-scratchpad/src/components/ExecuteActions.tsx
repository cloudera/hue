import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';
import SqlExecutable from 'gethue/src/apps/editor/execution/sqlExecutable';

export interface ExecuteActionsProps {
  activeExecutable?: SqlExecutable
}

interface ExecuteActionsElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ExecuteActions: FC<ExecuteActionsProps> = React.memo(({ activeExecutable }) => {
  const newNode = document.createElement('query-editor-actions');
  newNode.setAttribute('executable', '');
  (newNode as ExecuteActionsElement).executable = activeExecutable;

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