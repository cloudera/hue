---
title: A Spark SQL Editor via Hue and the Spark SQL Server
author: Romain
type: post
date: 2020-12-31T00:00:00+00:00
url: /blog/querying-spark-sql-with-spark-thrift-server-and-hue-editor/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Tutorial
  - Version 4.9
  - Spark SQL

---
Write and Execute some Spark SQL quickly in your own Web Editor.

*Initially published on https://medium.com/data-querying/a-sparksql-editor-via-hue-and-the-spark-sql-server-f82e72bbdfc7*

[Apache Spark](https://spark.apache.org/) is popular for wrangling/preparing data, especially when embedding some SQL snippets to keep the data manipulation programs declarative and simpler.

One good news is that the SQL syntax is very similar to [Apache Hive](https://hive.apache.org/) so the very powerful Hive autocomplete of Hue works very well.

![SparkSql Editor in action via both types of connection](https://cdn.gethue.com/uploads/2020/12/spark-sql-editor.gif)

Here we will describe how to integrate with the [Spark SQL Thrift Server](https://spark.apache.org/docs/latest/sql-distributed-sql-engine.html) interface that might be already available in your stack.

The article comes with a One click demo setup. The scenario is pretty simple and about batch querying, we will see for more live data in a dedicated follow-up episode.

![Two connectors possible for communicating with the SparkSql Thrift Server](https://cdn.gethue.com/uploads/2020/12/blog-spark-hue-archi.png)

For fetching the Docker Compose [configuration](https://raw.githubusercontent.com/romainr/query-demo/master/big-table-hbase/docker-compose.yml) and starting everything:

    mkdir spark
    cd spark
    wget https://raw.githubusercontent.com/romainr/query-demo/master/spark/docker-compose.yml
    docker-compose up -d
    >
    Creating network "spark_default" with the default driver
    Creating hue-database ... done
    Creating livy-spark   ... done
    Creating spark-master ... done
    Creating spark-sql    ... done
    Creating hue          ... done

Then those URLs will be up:

* http://127.0.0.1:8080/ Spark Master Web UI
* http://127.0.0.1:4040/environment/ Thrift SQL UI
* http://127.0.0.1:7070 Spark Master
* http://localhost:8998 Livy REST Server

For stopping everything:

    docker-compose down

## Hello World

How to create a SQL table representing some cities and number of inhabitants:

    CREATE TABLE IF NOT EXISTS us_population (
      state CHAR(2),
      city VARCHAR(20),
      population BIGINT
    )
    ;


    INSERT INTO us_population
    VALUES
    ('NY', 'New York', 8143197),
    ('CA', 'Los Angeles', 3844829),
    ('IL', 'Chicago', 2842518),
    ('TX', 'Houston', 2016582),
    ('PA', 'Philadelphia', 1463281),
    ('AZ', 'Phoenix', 1461575),
    ('TX', 'San Antonio', 1256509),
    ('CA', 'San Diego', 1255540),
    ('TX', 'Dallas', 1213825),
    ('CA', 'San Jose', 91233)
    ;


    SELECT
      state as State,
      count(city) as CityCount,
      sum(population) as PopulationSum
    FROM
      us_population
    GROUP BY
      state
    ORDER BY
      sum(population) DESC
    ;

## Which interface for connecting with the Spark SQL Server?

We previously demoed how to leverage Apache Livy to submit some [Spark SQL via Hue](https://medium.com/data-querying/an-sql-editor-for-apache-spark-sql-with-livy-534c56f7d251). As detailed there, Livy was initially created within the Hue project and offers a lightweight submission of interactive or batch PySpark / Scala Spark /SparkSql statements.

However one main drawback is that it might appear less official than the [Distributed SQL Engine](https://spark.apache.org/docs/latest/sql-distributed-sql-engine.html) (also known as “Thrift Server”) shipped within Spark.

Hue can connect to the Spark SQL Thrift Server via two interfaces:

- SqlAlchemy: [connector](https://github.com/dropbox/PyHive) based on the [universal Python](https://www.sqlalchemy.org/) lib
- HiveServer2: Hue’s native connector for Hive

Long story short: the main advantage of SqlAlchemy is to be have more SparkSql nits ironed out but queries are submitted synchronously (i.e. queries of more than a few seconds don’t have progress report yet and long ones will time out, unless the Hue [Task Server](https://docs.gethue.com/administrator/administration/reference/#task-server) is setup).

So we recommend to get started with SqlAlchemy but help [report/contribute](https://github.com/cloudera/hue/pulls) back small fixes on the HiveServer2 API which is more native/advanced.

Note: SqlAlchemy interface requires the Hive connector which does not work out of the box because of the issue [#150](https://github.com/dropbox/PyHive/issues/150). But Hue ships and show a slightly patched module that works: https://github.com/gethue/PyHive


![Spark SQL Editor](https://cdn.gethue.com/uploads/2020/12/spark-sql-editor.png)

## Configurations

In the hue.ini configure the connectors and make sure you installed the PyHive connector as shown in the [docs](https://docs.gethue.com/administrator/configuration/connectors/#apache-spark-sql):

    [notebook]
    [[interpreters]]

    [[[sparksql-alchemy]]]
    name=SparkSql (via SqlAlchemy)
    interface=sqlalchemy
    options='{"url": "hive://localhost:10000/default"}'

    [[[sparksql]]]
    # Must be named 'sparksql', hostname and more options are
    # in the 'spark' section
    name=SparkSql (via HiveServer2)
    interface=hiveserver2


    [spark]
    sql_server_host=localhost
    sql_server_port=10000


## What’s next?

Et voila!

Next time we will describe the progress on the Hue [SQL Scratchpad](https://docs.gethue.com/developer/components/parsers/) component that can be leveraged for easily editing and quick testing embedded SparkSql snippets as well as how to [query live data](https://gethue.com/blog/tutorial-query-live-data-stream-with-flink-sql/).

Onwards!

Romain
