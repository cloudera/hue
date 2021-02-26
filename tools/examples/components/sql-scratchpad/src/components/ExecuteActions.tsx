import React, { FC } from 'react';

import 'gethue/lib/components/query-editor-components';

export const ExecuteActions: FC = () => {
  const newNode = document.createElement('span');
  newNode.innerText = 'ExecuteActions';

  return <div
    ref={
      (nodeElement: HTMLDivElement | null) => {
        nodeElement && nodeElement.appendChild(newNode)
      }
    }
  />
}