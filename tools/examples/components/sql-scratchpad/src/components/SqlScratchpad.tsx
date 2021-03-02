import React, {FC, useState} from 'react';

import hueComponents from 'gethue/lib/components/QueryEditorWebComponents';

import Executor from 'gethue/lib/execution/executor';

import { QueryEditor } from './QueryEditor';
import { ExecuteActions } from './ExecuteActions';
import { ExecuteProgress } from './ExecuteProgress';
import { ResultTable } from './ResultTable';
import SqlExecutable from 'gethue/src/apps/editor/execution/sqlExecutable';

hueComponents.configure({
  baseUrl: 'http://localhost:1234/'
});

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
  const [activeExecutable, setActiveExecutable] = useState<SqlExecutable | undefined>(undefined);

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
};