---
title: "SQL Scratchpad"
draft: false
---

The lightweight SQL Editor also called "Quick Query" comes as its own `<SqlScratchpad />` Web component.

e.g.

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


Check the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/components/sql-scratchpad) about how to integrate it in your own Vue.js, React, JavaScript... project.

Notes

- Currently expects a running Hue on [http://localhost:8888](https://github.com/cloudera/hue/blob/master/tools/examples/components/sql-scratchpad/src/components/SqlScratchpad.tsx#L14)
- The `SqlScratchpad` in itself composed of other [smaller components](https://github.com/cloudera/hue/tree/master/tools/examples/components/sql-scratchpad/src/components), e.g. QueryEditor, ExecuteButton...

!["SQL Scratchpad component"](https://cdn.gethue.com/uploads/2020/02/quick-query-component.jpg)
