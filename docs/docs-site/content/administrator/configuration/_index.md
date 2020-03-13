---
title: "Configuration"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

The file to edit is `hue.ini` (wich is based on this [template](https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini)) and the actual values used can be checked on the [Dump Config](/administrator/administration/operations/#configuration) page.

Note: in development mode (when using `runserver` and not `runcpserver`), the correct hue.ini is `desktop/conf/pseudo-distributed.ini`

The most important sections to configure are about the:

* [Hue service](/administrator/configuration/server/). e.g. pointing the application to a relational database where Hue saves users and queries, selecting the login method, customizing the look & feel, activating the task server service...
* [Connectors](/administrator/configuration/connectors/). e.g. pointing to Data Warehouse services you want to make easy to query or browse. Those are typically which databases we want users to query with SQL or filesystems to browse.
