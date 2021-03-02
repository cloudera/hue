import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';
import Executable from 'gethue/src/apps/editor/execution/executable';

export interface ExecuteProgressProps {
  activeExecutable?: Executable
}

interface ProgressBarElement extends HTMLElement {
  executable?: Executable;
}

export const ExecuteProgress: FC<ExecuteProgressProps> = ({ activeExecutable }) => {
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
};