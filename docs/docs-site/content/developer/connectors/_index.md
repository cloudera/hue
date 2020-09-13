---
title: "Connectors"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 5
---

Connectors provide pluggable integration to any external data service so that an admin can easily allow end users to interact with them.

* List of all the [existing connectors](/administrator/configuration/connectors/)
* Check "Potential connectors" ideas in each section
* Feel free to contact the [community](https://discourse.gethue.com/c/developer-sdk-api)

## Databases

### SqlAlchemy

[SqlAlchemy](https://www.sqlalchemy.org) is the prefered way if the Hive API is not supported by the database. The core implementation is in [`sql_alchemy.py`](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/sql_alchemy.py) and relies on each respective SqlAlchemy dialect.

### Hive Interface

This [asynchronous API](https://github.com/cloudera/hue/tree/master/apps/beeswax) based on the Thrift API of Hive is very mature and powers an excellent integration of Apache Hive and Apache Impala.

### Custom

If the built-in HiveServer2 (Hive, Impala, Spark SQL), SqlAlchemy (MySQL, PostgreSQL, Oracle, Presto...) don’t meet your needs, you can implement your own connector to the notebook app:

* List of [all connectors](https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors)
* Each connector API subclasses the [Base API](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/base.py) and must implement the methods defined within. Refer to the [JDBC](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py) or [RdbmsApi](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/rdbms.py) for representative examples

* [Kafka SQL](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/ksql.py)
* [Solr SQL](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/solr.py)
* [JDBC](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py)

The JDBC API relies on a small JDBC proxy running next to the Hue API. By default it won't be built without setting the `BUILD_DB_PROXY` flag, e.g.:

    export BUILD_DB_PROXY=true make install

**Note** In the long term, SqlAlchemy is prefered as more "Python native".

### Potential connectors

It is recommended to develop an SqlAlchemy connector if yours is not already [existing](/administrator/configuration/connectors/#databases).

## Catalogs

The backends is pluggable by providing alternative [client interfaces](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata/src/metadata/catalog):

* [Apache Atlas](https://atlas.apache.org/)
* Cloudera Navigator
* Dummy (skeleton for integrating new catalogs)

### Apache Atlas

* [Client API](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata/src/metadata/catalog/atlas_client.py)

### Potential connectors

* [Linkedin DataHub](https://github.com/linkedin/datahub)
* [Lift Amundsen](https://github.com/lyft/amundsen)
* AWS Glue
* Google Cloud Data Catalog
* Alation

## Storages

Various storage systems can be interacted with. The [`fsmanager.py`](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/lib/fsmanager.py) is the main router to each API.

**Note** Apache Ozone as well as Ceph can be used via the S3 browser.

### Hadoop HDFS

* [WebHdfs API](https://github.com/cloudera/hue/blob/master/desktop/libs/hadoop/src/hadoop/fs/webhdfs.py)

### AWS S3

* [S3 API](https://github.com/cloudera/hue/blob/master/desktop/libs/aws/src/aws/s3)

### Azure ADLS

* [ADLS v2](https://github.com/cloudera/hue/blob/master/desktop/libs/azure/src/azure/abfs)
* [ADLS v1](https://github.com/cloudera/hue/blob/master/desktop/libs/azure/src/azure/adls)

### HBase / Key Value Stores

With just a few changes in the [Python API](https://github.com/cloudera/hue/blob/master/apps/hbase/src/hbase/api.py), the HBase browser could be compatible with Apache Kudu or Google Big Table.

### Potential connectors

* Google Cloud Storage is currently a work in progress with [HUE-8978](https://issues.cloudera.org/browse/HUE-8978)

## Jobs

### Apache Spark / Livy

Based on the [Livy REST API](/administrator/configuration/connectors/#apache-spark).

* [Notebook connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_shell.py)
  * PySpark
  * Scala
  * Spark SQL
* [Batch connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_batch.py)

### Schedulers

Currently only Apache Oozie is supported for your Datawarehouse, but the API is getting generic with [HUE-3797](https://issues.cloudera.org/browse/HUE-3797).

### Potential connectors

* Elastic Search: a connector similar to Solr for Searching [HUE-7828](https://issues.cloudera.org/browse/HUE-7828). SQL querying is already supported.
* [Livy Browser API](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/livy_api.py)
* [Celery API](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/lib/scheduler/lib/beat.py)
* Apache Hive native support of query scheduling [HIVE-21884](https://issues.apache.org/jira/browse/HIVE-21884)
