---
title: "SQL Scratchpad"
draft: false
---

The lightweight SQL Editor also called "SQL Scratchpad Query" comes as its own `<sql-scratchpad />` Web component.

It is in **beta** and now is a great time to give it a try and [send feedback](https://github.com/cloudera/hue/issues)!

Concept:

We have the `gethue` dependency in `packages.json` or run `npm install gethue`. Then just load it similarly to:

    import sqlScratchpadComp from 'gethue/lib/components/SqlScratchpadWebComponent';

    window.onload = async function (){
      sqlScratchpadComp.setBaseUrl('http://locahost:9000');
      await sqlScratchpadComp.login('hue', 'hue');
    |

In HTML:

    <sql-scratchpad dialect="mysql" />

API:

Currently expects a running Hue on http://locahost:9000 with a hue/hue user and this ini setting:

    [desktop]
    cors_enabled=true

!["SQL Scratchpad component"](https://cdn.gethue.com/uploads/2020/02/quick-query-component.jpg)


Notes:

Check the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/components/sql-scratchpad) about how to integrate it in your own Vue.js, React, JavaScript... projects.

The `SqlScratchpad` in itself composed of other [smaller components](https://github.com/cloudera/hue/tree/master/tools/examples/components/sql-scratchpad/src/components), e.g. QueryEditor, ExecuteButton...
