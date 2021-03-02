import React from 'react';
import './App.css';
import { SqlScratchpad } from "./components/SqlScratchpad";

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <p>
          SQL Scratchpad Example
        </p>
      </header>
      <SqlScratchpad />
    </div>
  );
}

export default App;
