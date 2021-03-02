import React, {FC, useState} from 'react';

import hueComponents from 'gethue/lib/components/QueryEditorWebComponents';
import hueConfig from 'gethue/lib/config/hueConfig';
import Executor from 'gethue/lib/execution/executor';

import { QueryEditor } from './QueryEditor';
import { ExecuteActions } from './ExecuteActions';
import { ExecuteProgress } from './ExecuteProgress';
import { ResultTable } from './ResultTable';
import SqlExecutable from 'gethue/src/apps/editor/execution/sqlExecutable';

const HUE_BASE_URL = 'http://localhost:8888/'

hueComponents.configure({
  baseUrl: HUE_BASE_URL
});

export const SqlScratchpad: FC = () => {
  const [activeExecutable, setActiveExecutable] = useState<SqlExecutable | undefined>(undefined);
  const [executor, setExecutor] = useState<Executor | undefined>(undefined);

  React.useEffect(() => {
    console.info('Refreshing config');
    hueConfig.refreshConfig(HUE_BASE_URL).then(() => {
      const connector = hueConfig.findEditorConnector(() => true); // Returns the first connector

      setExecutor(new Executor({
        compute: (() => ({ id: 'default' })) as KnockoutObservable<any>,
        connector: (() => connector) as KnockoutObservable<any>,
        database: (() => 'default') as KnockoutObservable<any>,
        namespace: (() => ({ id: 'default' })) as KnockoutObservable<any>,
      }));
    }).catch(err => {
      console.warn('Failed loading the Hue config')
    })
  })

  if (executor) {
    return <React.Fragment>
      <div className="ace-editor">
        <QueryEditor executor={executor} setActiveExecutable={setActiveExecutable}/>
      </div>
      <div className="executable-progress-bar">
        <ExecuteProgress activeExecutable={activeExecutable}/>
      </div>
      <div className="executable-actions">
        <ExecuteActions activeExecutable={activeExecutable}/>
      </div>
      <div className="result-table">
        <ResultTable/>
      </div>
    </React.Fragment>
  } else {
    return <div>Loading Config...</div>
  }

};