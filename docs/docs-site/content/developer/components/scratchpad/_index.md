---
title: "SQL Scratchpad"
draft: false
---

The lightweight SQL Editor also called "SQL Scratchpad" comes as its own `<sql-scratchpad />` Web component.

The SQL Scratchpad component is in **beta** and rapidly evolving. Now is a great time to give it a try and [send feedback](https://github.com/cloudera/hue/issues)!

UI:

We have the `gethue` [dependency](/developer/components/) in `packages.json` or run `npm install gethue`. Then just load it similarly to:

    <!DOCTYPE html>
    <html>

    <head>
      <title>SQL Scratchpad</title>
      <script type="text/javascript" src="./node_modules/gethue/lib/components/SqlScratchpadWebComponent.js"></script>
    </head>

    <body>
      <div style="position: absolute; height: 100%; width: 100%">
        <sql-scratchpad api-url="http://localhost:8005" dialect="mysql" />
      </div>
    </body>

    </html>

Note: even simpler you could just skip nom and grab the latest via:

    <script type="text/javascript" src="https://cdn.gethue.com/components/SqlScratchpadWebComponent.js"></script>


API:

Above expects a running Hue or [Compose](https://github.com/gethue/compose) APIs on http://locahost:8005.

Note: if using Hue, it currently temporarily requires a hue/hue user and this ini settings:

    [desktop]
    cors_enabled=true

    [[auth]]
    auto_login_enabled=true

!["SQL Scratchpad"](https://cdn.gethue.com/uploads/2021/05/sql-scratchpad-v0.5.png)
