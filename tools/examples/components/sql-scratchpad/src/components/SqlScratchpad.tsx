import React, { FC, useEffect, useState } from 'react';

import hueComponents from 'gethue/lib/components/QueryEditorWebComponents';
import Executor from 'gethue/lib/execution/executor';
import SqlExecutable from 'gethue/apps/editor/execution/sqlExecutable';

import { QueryEditor } from './QueryEditor';
import { ExecuteButton } from './ExecuteButton';
import { ExecuteProgress } from './ExecuteProgress';
import { ResultTable } from './ResultTable';
import { ExecuteLimit } from "./ExecuteLimit";

const { configure, refreshConfig, findEditorConnector, createExecutor, getNamespaces } = hueComponents;

const HUE_BASE_URL = 'http://localhost:8888'

configure({
  baseUrl: HUE_BASE_URL
});

export const SqlScratchpad: FC = () => {
  const [activeExecutable, setActiveExecutable] = useState<SqlExecutable | undefined>(undefined);
  const [executor, setExecutor] = useState<Executor | undefined>(undefined);

  const setup = async () => {
    try {
      await refreshConfig(HUE_BASE_URL);
    } catch {
      console.warn('Failed loading the Hue config')
      return;
    }

    const connector = findEditorConnector(() => true); // Returns the first connector

    if (!connector) {
      console.warn('No connector found!');
      return;
    }

    try {
      const { namespaces } = await getNamespaces({connector})
      if (!namespaces.length || !namespaces[0].computes.length) {
        console.warn('No namespace and/or compute found!');
        return;
      }

      setExecutor(createExecutor({
        compute: () => namespaces[0].computes[0],
        connector: () => connector,
        database: () => 'default',
        namespace: () => namespaces[0],
      }))
    } catch {
      console.warn('Failed loading namespaces.')
    }
  }

  useEffect(() => {
    setup().catch();
  }, []);

  if (executor) {
    return <React.Fragment>
      <div className="ace-editor">
        <QueryEditor executor={executor} setActiveExecutable={setActiveExecutable} />
      </div>
      <div className="executable-progress-bar">
        <ExecuteProgress activeExecutable={activeExecutable} />
      </div>
      <div className="executable-actions">
        <ExecuteButton activeExecutable={activeExecutable} />
        <ExecuteLimit activeExecutable={activeExecutable} />
      </div>
      <div className="result-table">
        <ResultTable activeExecutable={activeExecutable} />
      </div>
    </React.Fragment>
  } else {
    return <div>Loading Config...</div>
  }
}
