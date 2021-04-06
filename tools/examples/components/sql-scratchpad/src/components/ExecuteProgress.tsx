import React, { FC, useEffect, useRef } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';
import { setWebCompProp } from './utils';

export interface ExecuteProgressProps {
  activeExecutable?: SqlExecutable
}

interface ProgressBarElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ExecuteProgress: FC<ExecuteProgressProps> = ({ activeExecutable }) => {
  const containerElement = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setWebCompProp<ProgressBarElement>(containerElement.current?.firstElementChild, 'executable', activeExecutable);
  }, [activeExecutable, containerElement]);

  useEffect(() => {
    if (containerElement.current) {
      containerElement.current.innerHTML = '<query-editor-progress-bar />';
    }
  }, [containerElement]);

  return <div ref={ containerElement }/>
};
