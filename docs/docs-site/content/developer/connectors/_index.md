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

#### SQL Queries

The API currently supports:

* [Apache Impala](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/query_api.py)
* [Apache Hive](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/beeswax_query_api.py)

#### Spark / Livy

* [Livy API](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/livy_api.py)

#### Oozie

* [Workflow API](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/workflow_api.py)
* [Coordinators API](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/schedule_api.py)
* [Bundles API](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/bundle_api.py)

## File Browser

Various storage systems can be interacted with. The [`fsmanager.py`](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/lib/fsmanager.py) is the main router to each API.

**Note** Ceph can be used via the S3 browser.

### Hadoop HDFS

* [WebHdfs API](https://github.com/cloudera/hue/blob/master/desktop/libs/hadoop/src/hadoop/fs/webhdfs.py)

### AWS S3

* [S3 API](https://github.com/cloudera/hue/blob/master/desktop/libs/aws/src/aws/s3)

### Azure ADLS

* [ADLS v2](https://github.com/cloudera/hue/blob/master/desktop/libs/azure/src/azure/abfs)
* [ADLS v1](https://github.com/cloudera/hue/blob/master/desktop/libs/azure/src/azure/adls)

### HBase / Key Value Stores

With just a few changes in the [Python API](https://github.com/cloudera/hue/blob/master/apps/hbase/src/hbase/api.py),
the HBase browser could be compatible with Apache Kudu or Google Big Table.

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

## Data Catalog

The backends is pluggable by providing alternative [client interfaces](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata/src/metadata/catalog):

* Cloudera Navigator (default)
* Dummy (skeleton for integrating new catalogs)

### Apache Atlas

* [Client API](desktop/libs/metadata/src/metadata/catalog/atlas_client.py)

## Scheduling

### Oozie

Currently only Apache Oozie is supported for your Datawarehouse, but the API is getting generic with [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) that is bringing Celery Beat integration.

* [API](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/lib/scheduler/lib/beat.py)
