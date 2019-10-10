---
title: "Configuration"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

## Hue

The source of truth sits in the main [hue.ini](https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini).
It consists in several ini sections. Lines needs to be uncommented to be active.

The most important things to configure are:

* pointing to a relational database (where Hue saves users and queries)
* pointing to external services to query or browse (which databases we want users to query with SQL, or filesystems to browse...)

## Services

Sometimes some Hadoop components need to be configured to properly work with Hue. Hue is using Hadoop `impersonation` to be able to communicate properly with certain services. This is described in the following [Service Configuration](/administrator/configuration/).
