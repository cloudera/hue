import React from 'react';
import './App.css';
import Executor from "gethue/lib/execution/executor";
import { QueryEditor } from "./components/QueryEditor";
import { ExecuteActions } from "./components/ExecuteActions";
import { ExecuteProgress } from "./components/ExecuteProgress";
import { ResultTable } from "./components/ResultTable";

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

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <p>
          SQL Scratchpad Example
        </p>
      </header>
      <div className="ace-editor">
        <QueryEditor executor={ executor } />
      </div>
      <div className="executable-progress-bar">
        <ExecuteProgress />
      </div>
      <div className="executable-actions">
        <ExecuteActions />
      </div>
      <div className="result-table">
        <ResultTable />
      </div>
    </div>
  );
}

export default App;
