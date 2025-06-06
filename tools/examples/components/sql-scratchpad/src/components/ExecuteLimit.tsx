import React, { FC, useEffect, useRef } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';
import { setWebCompProp } from './utils';

export interface ExecuteLimitProps {
  activeExecutable?: SqlExecutable
}

interface ExecuteLimitElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ExecuteLimit: FC<ExecuteLimitProps> = ({ activeExecutable }) => {
  const containerElement = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setWebCompProp<ExecuteLimitElement>(containerElement.current?.firstElementChild, 'executable', activeExecutable);
  }, [activeExecutable, containerElement]);

  useEffect(() => {
    if (containerElement.current) {
      containerElement.current.innerHTML = '<query-editor-limit-input />';
    }
  }, [containerElement]);

  return <div ref={ containerElement }/>
};