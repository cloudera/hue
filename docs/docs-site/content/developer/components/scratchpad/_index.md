---
title: "SQL Scratchpad"
draft: false
weight: 1
---

The shareable lightweight SQL Editor also called "SQL Scratchpad" comes as its own `<sql-scratchpad />` Web component.

The SQL Scratchpad component is in beta and rapidly evolving. Now is a great time to give it a try and [send feedback](https://github.com/cloudera/hue/issues)!

## Live Demo

The Scratchpad is hosted within this page and points to [demo.gethue.com](https://demo.gethue.com/):

{{< rawhtml >}}
<p>
  <div style="position: absolute; height: 25%; width: 70%">
    <sql-scratchpad api-url="https://demo.gethue.com" username="demo" password="demo" dialect="mysql" />
  </div>

  <script type="text/javascript" src="https://unpkg.com/gethue/lib/components/SqlScratchpadWebComponent.js"></script>

  <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
</p>
{{< /rawhtml >}}


## Importing

First install the [NPM package](/developer/components/#npm-registry) and import the component lib and its HTML element directly into the Web page:

```html
<!DOCTYPE html>
<html>

<head>
  <title>SQL Scratchpad</title>
  <script type="text/javascript" src="./node_modules/gethue/lib/components/SqlScratchpadWebComponent.js"></script>
</head>

<body>
  <div style="position: absolute; height: 100%; width: 100%">
    <sql-scratchpad api-url="https://demo.gethue.com" username="demo" password="demo" dialect="mysql" />
  </div>
</body>

</html>
```

Then make sure `api-url` points to a running Hue server. The API is the middleware between your Data Warehouse and Web Browser client and will provide the dynamic content like the list of tables and columns and enrich the autocomplete. The autocomplete is static and powered by the [parser](/developer/components/parsers/) selected by the value of `dialect`.

Specify the credentials for the authentication via `username` and `password` (e.g. `username="demo" password="demo"`).

Options to look up a local JWT token, or to use a login modal and so not require the credentials, are coming shortly.


You can also skip `npm install` and load the module directly via:

```html
<script type="text/javascript" src="https://unpkg.com/gethue/lib/components/SqlScratchpadWebComponent.js"></script>
```

!["SQL Scratchpad"](https://cdn.gethue.com/uploads/2021/05/sql-scratchpad-v0.5.png)
