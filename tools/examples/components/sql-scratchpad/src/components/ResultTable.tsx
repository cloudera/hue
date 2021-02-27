import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';

export const ResultTable: FC = () => {
  const newNode = document.createElement('span');
  newNode.innerText = 'ResultTable'

  return <div
    ref={
      (nodeElement: HTMLDivElement | null) => {
        nodeElement && nodeElement.appendChild(newNode)
      }
    }
  />
}