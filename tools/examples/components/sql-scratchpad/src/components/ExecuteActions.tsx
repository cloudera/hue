import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';
import Executable from 'gethue/src/apps/editor/execution/executable';

export interface ExecuteActionsProps {
  activeExecutable?: Executable
}

interface ExecuteActionsElement extends HTMLElement {
  executable?: Executable;
}

export const ExecuteActions: FC<ExecuteActionsProps> = ({ activeExecutable }) => {
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
};