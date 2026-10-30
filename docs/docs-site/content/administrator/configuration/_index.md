---
title: "Configuration"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

You configure Hue in the `hue.ini` file. It is based on this [template](https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini). To check the values the server actually uses, open the [Dump Config](/administrator/administration/operations/#configuration) page.

The most important sections to configure are:

* [Server](/administrator/configuration/server/): for example, the relational database where Hue saves users and queries, the login method (such as LDAP), the look and feel, special features, and the apps to disable.
* [Connectors](/administrator/configuration/connectors/): the data warehouse services you want users to query or browse. These are typically the databases users query with SQL and the filesystems they browse.

> **Note**: Restart the server after you change `hue.ini`.

> **Note**: In development mode (when you start Hue with `./build/env/bin/hue runserver`), the ini file is `desktop/conf/pseudo-distributed.ini`.
