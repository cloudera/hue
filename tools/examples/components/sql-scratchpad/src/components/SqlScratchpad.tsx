import React from 'react';

import hueComponents from 'gethue/lib/components/QueryEditorWebComponents';
import hueConfig from 'gethue/lib/config/hueConfig';
import Executor from 'gethue/lib/execution/executor';

import { QueryEditor } from './QueryEditor';
import { ExecuteActions } from './ExecuteActions';
import { ExecuteProgress } from './ExecuteProgress';
import { ResultTable } from './ResultTable';
import SqlExecutable from 'gethue/src/apps/editor/execution/sqlExecutable';

const HUE_BASE_URL = 'http://localhost:8888'

hueComponents.configure({
  baseUrl: HUE_BASE_URL
});

interface SqlScratchpadState {
  activeExecutable?: SqlExecutable;
  executor?: Executor;
}

export class SqlScratchpad extends React.Component<{}, SqlScratchpadState> {
  state = {
    activeExecutable: undefined,
    executor: undefined
  }

  constructor(props: {}) {
    super(props);
    this.setActiveExecutable = this.setActiveExecutable.bind(this);
  }

  componentDidMount() {
    console.info('Refreshing config');

    hueConfig.refreshConfig(HUE_BASE_URL).then(() => {
      const connector = hueConfig.findEditorConnector(() => true); // Returns the first connector

      this.setState({
        executor: hueComponents.createExecutor({
          compute: (() => ({ id: 'default' })) as KnockoutObservable<any>,
          connector: (() => connector) as KnockoutObservable<any>,
          database: (() => 'default') as KnockoutObservable<any>,
          namespace: (() => ({ id: 'default' })) as KnockoutObservable<any>,
        })
      })
    }).catch(() => {
      console.warn('Failed loading the Hue config')
    })
  }

  setActiveExecutable(activeExecutable: SqlExecutable) {
    this.setState({
      activeExecutable
    })
  }

  render() {
    const executor = this.state.executor;
    if (executor) {
      return <React.Fragment>
        <div className="ace-editor">
          <QueryEditor executor={executor} setActiveExecutable={this.setActiveExecutable}/>
        </div>
        <div className="executable-progress-bar">
          <ExecuteProgress activeExecutable={this.state.activeExecutable}/>
        </div>
        <div className="executable-actions">
          <ExecuteActions activeExecutable={this.state.activeExecutable}/>
        </div>
        <div className="result-table">
          <ResultTable/>
        </div>
      </React.Fragment>
    } else {
      return <div>Loading Config...</div>
    }
  }
}