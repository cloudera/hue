---
title: "Scheduling"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

Scheduling of queries or jobs (e.g. run this SQL query everyday at 5am) is currently done via Apache Oozie and will be open to other schedulers with [HUE-3797](https://issues.cloudera.org/browse/HUE-3797). [Apache Oozie](http://oozie.apache.org) is a very robust scheduler for Data Warehouses.

## Editor

Workflows can be built by pointing to query scripts on the file systems or just selecting one of your saved queries. A workflow can then be scheduled to run regularly via a schedule.

![Oozie workflows](https://cdn.gethue.com/uploads/2016/04/hue-workflows.png)

Many users leverage the workflow editor to get the Oozie XML configuration of their workflows.

### Tutorial

How to run Spark jobs with Spark on YARN? This often requires trial and error in order to make it work.

Hue is leveraging Apache Oozie to submit the jobs. It focuses on the yarn-client mode, as Oozie is already running the spark-summit command in a MapReduce2 task in the cluster. You can read more about the Spark modes here.

Here is how to get started successfully:

#### PySpark

Simple script with no dependency.

![Oozie workflows](https://cdn.gethue.com/uploads/2016/08/oozie-pyspark-simple.png)

Script with a dependency on another script (e.g. hello imports hello2).

![Oozie workflows](https://cdn.gethue.com/uploads/2016/08/oozie-pyspark-dependencies.png)

For more complex dependencies, like Panda, have a look at this documentation.


#### Jars (Java or Scala)

Add the jars as File dependency and specify the name of the main jar:

![Oozie workflows](https://cdn.gethue.com/uploads/2016/08/spark-action-jar.png)

Another solution is to put your jars in the ‘lib’ directory in the workspace (‘Folder’ icon on the top right of the editor).

![Oozie workflows](https://cdn.gethue.com/uploads/2016/08/oozie-spark-lib2.png)

### Shell

If the executable is a standard Unix command, you can directly enter it in the `Shell Command` field and click Add button.

![Shell action](https://cdn.gethue.com/uploads/2015/10/1.png)

Arguments to the command can be added by clicking the `Arguments+` button.

![Shell action](https://cdn.gethue.com/uploads/2015/10/2.png)

`${VARIABLE}` syntax will allow you to dynamically enter the value via Submit popup.

![Shell action](https://cdn.gethue.com/uploads/2015/10/31.png)
![Shell action](https://cdn.gethue.com/uploads/2015/10/4.png)

If the executable is a script instead of a standard UNIX command, it needs to be copied to HDFS and the path can be specified by using the File Chooser in Files+ field.

    #!/usr/bin/env bash
    sleep

![Shell action](https://cdn.gethue.com/uploads/2015/10/5.png)

Additional Shell-action properties can be set by clicking the settings button at the top right corner.

## Browser

Submitted workflows, schedules and bundles can be managed directly via an interface:

![Oozie jobs](https://cdn.gethue.com/uploads/2016/04/hue-dash-oozie.png)

### Extra Coordinator actions

Update Concurrency and PauseTime of running Coordinator.

![Oozie jobs](https://cdn.gethue.com/uploads/2015/08/edit-coord.png)

Ignore a terminated Coordinator action.

![Oozie jobs](https://cdn.gethue.com/uploads/2015/08/ignore.png)
