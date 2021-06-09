import React, { FC, useEffect, useRef } from 'react';

import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';
import { setWebCompProp } from './utils';

export interface ResultTableProps {
  activeExecutable?: SqlExecutable;
}

interface ResultTableElement extends HTMLElement {
  executable?: SqlExecutable;
}

export const ResultTable: FC<ResultTableProps> = ({ activeExecutable }) => {
  const containerElement = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setWebCompProp<ResultTableElement>(containerElement.current?.firstElementChild, 'executable', activeExecutable);
  }, [activeExecutable, containerElement]);

  useEffect(() => {
    if (containerElement.current) {
      containerElement.current.innerHTML = '<query-editor-result-table />';
    }
  }, [containerElement]);

  return <div ref={ containerElement }/>
}
