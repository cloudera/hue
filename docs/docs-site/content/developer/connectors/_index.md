---
title: "Connectors"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

They provide integration with any SQL database or Job execution engine. Here is a list of the [existing connectors](https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors).

Connectors are pluggable and new engines can be added. Feel free to contact the [community](https://discourse.gethue.com/c/developer-sdk-api).

## Querying

### SQL

#### SqlAlchemy

[SqlAlchemy](https://www.sqlalchemy.org) is the prefered way if the HiveServer2 API is not supported by the database. The implementation is in [`sql_alchemy.py`](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/sql_alchemy.py) and is depends on the repective SqlAlchemy dialects.

#### Kafka SQL

[Kafka connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/ksql.py).

#### Solr SQL

[Solr connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/solr.py).

#### Custom

If the built-in HiveServer2 (Hive, Impala, Spark SQL), RDBMS (MySQL, PostgreSQL, Oracle, SQLite), and JDBC interfaces don’t meet your needs, you can implement your own connector to the notebook app:

* List of the existing [Notebook Connectors](https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors)
* Each connector API subclasses the [Base API](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/base.py) and must implement the methods defined within
* Refer to the [JdbcApi](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py) or [RdbmsApi](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/rdbms.py) for representative examples

#### JDBC

With the JDBC proxy, query editor with any JDBC compatible database. View the [JDBC connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py).

**Note** In the long term, SqlAlchemy is prefered as more "Python native".


### Jobs

#### Spark / Livy

Based on the [Livy REST API](/administrator/configuration/connectors/#apache-spark).

* [Notebook connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_shell.py)
  * PySpark
  * Scala
  * Spark SQL
* [Batch connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_batch.py)

#### Oozie

MapReduce, Pig, Java, Shell, Sqoop, DistCp [Oozie connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/oozie_batch.py).


## Job Browser

The Job Browser is generic and can list any type of jobs, queries and provide bulk operations like kill, pause, delete... and access to logs and recommendations.

Here is its [API](https://github.com/cloudera/hue/tree/master/apps/jobbrowser/src/jobbrowser/apis).

## File Browser

Various storage systems like Hadoop HDFS, AWS S3 and Azure [ADLS](https://issues.cloudera.org/browse/HUE-7248) can be interacted with. The [`fsmanager.py`](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/lib/fsmanager.py) is the main router to each API.

**Note** Ceph can be used via the S3 browser.

## Dashboard

[Dashboards](/user/querying/#dashboards) are generic and support Apache Solr and SQL:

The API was influenced by Solr but is now generic:

[Dashboard API](https://github.com/cloudera/hue/blob/master/desktop/libs/dashboard/src/dashboard/dashboard_api.py)

### SQL

[SQL API](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/dashboard_api.py)

Implementations:

* [Impala API](https://github.com/cloudera/hue/blob/master/apps/impala/src/impala/dashboard_api.py)
* [Hive API](https://github.com/cloudera/hue/blob/master/apps/beeswax/src/beeswax/dashboard_api.py)

### Apache Solr

[Solr Dashboard API](https://github.com/cloudera/hue/blob/master/apps/search/src/search/dashboard_api.py)

### Elastic Search

A connector similar to Solr or SQL Alchemy binding would need to be developed [HUE-7828](https://issues.cloudera.org/browse/HUE-7828).
