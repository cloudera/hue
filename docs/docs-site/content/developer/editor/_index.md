---
title: "Editor"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

They provide SQL integration with any database via several connectors (native, JDBC, SQL Alchemy...).

Other modes like MapReduce, Java, Shell, Sqoop are also available. Here is a list of the [existing connectors](https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors).

Connectors are pluggable and can new engines can be supported. Feel free to comment on the [Hue list](https://groups.google.com/a/cloudera.org/forum/#!forum/hue-user) of [github](https://github.com/cloudera/hue/issues) about it.

## SQL

The [Editor Configuration]({{% param baseURL %}}administrator/configuration/editor/) also describes the configuration steps.

Close to 100% of [Hive and Impala grammar](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/static/desktop/js/autocomplete/jison) is supported which makes the autocomplete extremly powerful. Other languages defaults to a generic SQL grammar.

**Coming Soon**
How to write your own SQL parser.

### HiveServer2 API
Hive, Impala, SparkSQL

### SQL Alchemy
SQL Alchemy is the prefered way if the HiveServer2 API is not supported by the database. More enterprise support will come with [HUE-8740](https://issues.cloudera.org/browse/HUE-8740).

### Python Connectors
MySQL, Oracle, PostgreSQL, Phoenix, Presto, Kylin, Redshift, BigQuery, Drill

### JDBC
Use the query editor with any JDBC compatible database. View the [JDBC connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py).

**Note** Going forward, SQL Alchemy is prefered as more "Python native".

### Solr SQL
[Solr connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/solr.py)

### Others

## Jobs

The Job Browser is generic and can list any type of jobs, queries and provide bulk operations like kill, pause, delete... and access to logs and recommendations.

### Oozie
MapReduce, Pig, Java, Shell, Sqoop, DistCp [Oozie connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/oozie_batch.py)

### Spark / Livy

Based on the [Livy REST API](https://livy.incubator.apache.org/docs/latest/rest-api.html)

* [Notebook connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_shell.py)
  * PySpark
  * Scala
  * Spark SQL
* [Batch connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_batch.py)

## Dashboard

Dashboards are generic and support [Solr and any SQL](http://gethue.com/search-dashboards):

The API was influenced by Solr but is now generic:

[Dashboard API](https://github.com/cloudera/hue/blob/master/desktop/libs/dashboard/src/dashboard/dashboard_api.py)

### SQL

[SQL API](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/dashboard_api.py)

Implementations:

* [Impala API](https://github.com/cloudera/hue/blob/master/apps/impala/src/impala/dashboard_api.py)
* [Hive API](https://github.com/cloudera/hue/blob/master/apps/beeswax/src/beeswax/dashboard_api.py)

When HS2, RDBMS, and JDBC Are Not Enough

If the built-in HiveServer2 (Hive, Impala, Spark SQL), RDBMS (MySQL, PostgreSQL, Oracle, SQLite), and JDBC interfaces don’t meet your needs, you can implement your own connector to the notebook app: [Notebook Connectors](https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors). Each connector API subclasses the [Base API](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/base.py) and must implement the methods defined within; refer to the [JdbcApi](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py) or [RdbmsApi](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/rdbms.py) for representative examples.

### Solr

[Solr Dashboard API](https://github.com/cloudera/hue/blob/master/apps/search/src/search/dashboard_api.py)

### Elastic Search

A connector similar to Solr or SQL Alchemy binding would need to be developed [HUE-7828](https://issues.cloudera.org/browse/HUE-7828)
