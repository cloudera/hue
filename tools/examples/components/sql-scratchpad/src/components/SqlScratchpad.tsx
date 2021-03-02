import React, {FC, useState} from 'react';

import 'gethue/lib/components/query-editor-components';

import Executor from 'gethue/lib/execution/executor';

import { QueryEditor } from './QueryEditor';
import { ExecuteActions } from './ExecuteActions';
import { ExecuteProgress } from './ExecuteProgress';
import { ResultTable } from './ResultTable';
import Executable from 'gethue/src/apps/editor/execution/executable';

const executor = new Executor({
  compute: (() => ({ id: 'default' })) as KnockoutObservable<any>,
  connector: (() => ({
    dialect: 'hive',
    id: 'hive',
    is_sql: true
  })) as KnockoutObservable<any>,
  database: (() => 'default') as KnockoutObservable<any>,
  namespace: (() => ({ id: 'default' })) as KnockoutObservable<any>,
});

export const SqlScratchpad: FC = () => {
  const [activeExecutable, setActiveExecutable] = useState<Executable | undefined>(undefined);

  return <React.Fragment>
    <div className="ace-editor">
      <QueryEditor executor={executor} setActiveExecutable={setActiveExecutable}/>
    </div>
    <div className="executable-progress-bar">
      <ExecuteProgress activeExecutable={activeExecutable}/>
    </div>
    <div className="executable-actions">
      <ExecuteActions/>
    </div>
    <div className="result-table">
      <ResultTable/>
    </div>
  </React.Fragment>
};