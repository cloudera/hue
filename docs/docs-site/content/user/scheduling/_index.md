---
title: "Scheduling"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

Scheduling of queries or jobs (e.g. run this SQL query everyday at 5am) is currently done via Apache Oozie and will be open to other schedulers with [HUE-3797](https://issues.cloudera.org/browse/HUE-3797). [Apache Oozie](http://oozie.apache.org) is a very robust scheduler for Data Warehouses.

## Editor

Workflows can be built by pointing to query scripts on the file systems or saved queries. A workflow can then be scheduled to run regularly via a schedule.

![Oozie workflows](https://cdn.gethue.comuploads/2016/04/hue-workflows.png)

Many users leverage the workflow editor to get the Oozie XML configuration of their workflows.

## Browser

Submitted workflows, schedules and bundles can be managed directly via an interface:

![Oozie jobs](https://cdn.gethue.com/uploads/2016/04/hue-dash-oozie.png)
