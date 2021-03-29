import React, { FC } from 'react';

export interface SqlContextSelectorProps {}

interface SqlContextSelectorElement extends HTMLElement {}

export const ContextSelector: FC<SqlContextSelectorProps> = () => {
  const newNode = document.createElement('sql-context-selector');

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
