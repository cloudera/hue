import React, { FC, useEffect, useRef } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';
import { setWebCompProp } from './utils';

export interface ExecuteButtonProps {
  activeExecutable?: SqlExecutable
}

interface ExecuteButtonElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ExecuteButton: FC<ExecuteButtonProps> = ({ activeExecutable }) => {
  const containerElement = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setWebCompProp<ExecuteButtonElement>(containerElement.current?.firstElementChild, 'executable', activeExecutable);
  }, [activeExecutable, containerElement]);

  useEffect(() => {
    if (containerElement.current) {
      containerElement.current.innerHTML = '<query-editor-execute-button />';
    }
  }, [containerElement]);

  return <div ref={ containerElement }/>
};
