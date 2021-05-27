---
title: "SQL Scratchpad"
draft: false
weight: 1
---

The shareable lightweight SQL Editor also called "SQL Scratchpad" comes as its own `<sql-scratchpad />` Web component.

The SQL Scratchpad component is in beta and rapidly evolving. Now is a great time to give it a try and [send feedback](https://github.com/cloudera/hue/issues)!

## Live Demo

The Scratchpad is hosted within this page and points to [demo.gethue.com](https://demo.gethue.com/).

{{< rawhtml >}}
<p>
  <div style="position: absolute; height: 40%; width: 100%">
    <sql-scratchpad api-url="https://demo.gethue.com" username="demo" password="demo" dialect="mysql" />
  </div>

  <script type="text/javascript" src="/js/gethue/components/SqlScratchpadWebComponent.js"></script>

  <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
</p>
{{< /rawhtml >}}


## Importing

First install the NPM [package](/developer/components/) and import the component lib and its HTML element directly into the Web page:

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

For quick testing, it is possible to skip the `npm install` and directly grab the module via:

    <script type="text/javascript" src="https://cdn.gethue.com/components/SqlScratchpadWebComponent.js"></script>

Then make sure `api-url` points to a running Hue or [Compose](https://github.com/gethue/compose) APIs on [http://localhost:8005](http://localhost:8005). The API is the middleware between your Data Warehouse and Web Browser client and will provide the dynamic content like the list of tables and columns and enrich the static autocomplete powered by the [parser](/developer/components/parsers/) selected by the `dialect`.

If using Hue as the API, this [ini settings](/administrator/configuration/) is currently required:

    [desktop]
    cors_enabled=true

!["SQL Scratchpad"](https://cdn.gethue.com/uploads/2021/05/sql-scratchpad-v0.5.png)
