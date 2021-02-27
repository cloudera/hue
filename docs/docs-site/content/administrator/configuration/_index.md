---
title: "Configuration"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

The file to edit is `hue.ini` (which is based on this [template](https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini)). The actual values used by the API server can be checked on the [Dump Config](/administrator/administration/operations/#configuration) page.


The most important sections to configure are about the:

* [API Server](/administrator/configuration/server/). e.g. pointing to a relational database where Hue saves users and queries, selecting the login method like LDAP, customizing the look & feel, activating special features, disabling some apps...
* [Connectors](/administrator/configuration/connectors/). e.g. pointing to Data Warehouse services you want to make easy to query or browse. Those are typically which databases we want users to query with SQL or filesystems to browse.

**Notes**

* Restarting the server is currently required after for taking ini changes into consideration
* In development mode (i.e. when using `./build/env/bin/hue runserver` and not `runcpserver`), the correct ini file is `desktop/conf/pseudo-distributed.ini`
