import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';

export const ExecuteProgress: FC = () => {
  const newNode = document.createElement('span');
  newNode.innerText = 'ExecuteProgress';

  return <div
    ref={
      (nodeElement: HTMLDivElement | null) => {
        nodeElement && nodeElement.appendChild(newNode)
      }
    }
  />
}