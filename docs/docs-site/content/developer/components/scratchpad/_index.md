---
title: "SQL Scratchpad"
draft: false
weight: 1
---

The lightweight SQL Editor also called "SQL Scratchpad" comes as its own `<sql-scratchpad />` Web component.

The SQL Scratchpad component is in **beta** and rapidly evolving. Now is a great time to give it a try and [send feedback](https://github.com/cloudera/hue/issues)!

!["SQL Scratchpad"](https://cdn.gethue.com/uploads/2021/05/sql-scratchpad-v0.5.png)

Adding into a Web page:

We have the `gethue` [dependency](/developer/components/) in `packages.json` or run `npm install gethue`. Then just load it similarly to:

    <!DOCTYPE html>
    <html>

    <head>
      <title>SQL Scratchpad</title>
      <script type="text/javascript" src="./node_modules/gethue/lib/components/SqlScratchpadWebComponent.js"></script>
    </head>

    <body>
      <div style="position: absolute; height: 100%; width: 100%">
        <sql-scratchpad api-url="http://localhost:8005" username="demo" password="demo" dialect="mysql" />
      </div>
    </body>

    </html>

Note: even simpler you could just skip `npm` and grab the latest via:

    <script type="text/javascript" src="https://cdn.gethue.com/components/SqlScratchpadWebComponent.js"></script>


Above expects a running Hue or [Compose](https://github.com/gethue/compose) APIs on [http://locahost:8005](http://locahost:8005) as the middleware between your Data Warehouse and client.

Note: if using Hue, it currently temporarily requires this ini settings:

    [desktop]
    cors_enabled=true
