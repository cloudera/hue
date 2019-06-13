---
title: "Configuration"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

The source of truth sits in the main [hue.ini](https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini).
It consists in several [ini sections](https://en.wikipedia.org/wiki/INI_file#Sections). Lines needs to be uncommented to be active.

Hue is using Hadoop `impersonation` to be able to communicate properly with certain services. This is described in the following [Service Configuration]({{% param baseURL %}}administrator/configuration/).
