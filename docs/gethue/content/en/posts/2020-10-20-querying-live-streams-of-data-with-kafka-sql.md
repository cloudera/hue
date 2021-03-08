---
title: Tutorial on querying live streams of data with ksql (Kafka SQL)
author: Romain
type: post
date: 2020-10-20T00:00:00+00:00
url: /blog/tutorial-query-live-data-stream-with-kafka-sql/
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
  - ksqlDB

---
Real time data querying is becoming a modern standard. Who wants to wait until the next day or week when needing to take decision now?

The stream of data comes from an [Apache Kafka](https://kafka.apache.org/) topic which can be queried via [ksqlDB](https://ksqldb.io/).


## Components

To keep things simple, all the pieces have been put together in a "one-click" Docker Compose project which contains:

* ksqlDB from the [ksqlDB quickstart](https://ksqldb.io/quickstart.html#quickstart-content)
* A [Hue Editor](https://github.com/cloudera/hue/tree/master/tools/docker/hue) already configured with the ksqlDB Editor


![Stream SQL Editor](https://cdn.gethue.com/uploads/2020/10/ksql-editor.png)

## One-line setup

For fetching the configurations and starting everything:

    mkdir stream-sql-demo
    cd stream-sql-demo
    wget https://raw.githubusercontent.com/romainr/query-demo/master/stream-sql-demo/docker-compose.yml


    docker-compose up -d
    >
    Creating network "stream-sql-demo_default" with the default driver
    Creating hue-database                  ... done
    Creating stream-sql-demo_jobmanager_1 ... done
    Creating stream-sql-demo_mysql_1       ... done
    Creating ksqldb-server                 ... done
    Creating stream-sql-demo_zookeeper_1   ... done
    Creating flink-sql-api                 ... done
    Creating stream-sql-demo_taskmanager_1 ... done
    Creating hue                           ... done
    Creating ksqldb-cli                    ... done
    Creating stream-sql-demo_kafka_1       ... done
    Creating stream-sql-demo_datagen_1     ... done


Then the Hue Editor will be up at [http://localhost:8888/](http://localhost:8888/).

As well as the ksqlDB API:

    curl http://localhost:8088/info
    > {"KsqlServerInfo":{"version":"0.12.0","kafkaClusterId":"DJzUX-zaTDCC5lqfVwf8kw","ksqlServiceId":"default_","serverStatus":"RUNNING"}}

For stopping everything:

    docker-compose down

## Query Experience

Notice that the Live SQL requires the New Editor which is in beta. In addition to soon offer multiple statements running at the same time on the same editor page and more robustness, it also bring the live result grid.

More improvements are on the way, in particular in the SQL autocomplete and Editor 2. In the future, the [Task Server](https://docs.gethue.com/administrator/administration/reference/#task-server) with Web Sockets will allow long running queries to run as separate tasks and prevent them from timing-out in the API server.

**Note**

In case you have an existing Hue Editor and want to point to the ksqlDB, just activate it via this config change:

    [notebook]
    enable_notebook_2=true

    [[interpreters]]

    [[[ksqlDB]]]
    name=ksqlDB
    interface=ksql
    options='{"url": "http://localhost:8088"}'

### ksql

{{< youtube k714Zw1bFVU >}}

One nicety of ksqDB is its close integration with Kafka, for example we can list the topics:

    SHOW TOPICS

The SQL syntax is a bit different but here is one way to create a similar table as above:

    CREATE STREAM user_behavior (
      user_id BIGINT,
      item_id BIGINT,
      category_id BIGINT,
      behavior STRING,
      ts STRING
    ) WITH (kafka_topic='user_behavior', value_format='json', partitions=1)


And peek at it:

    SELECT *
    FROM user_behavior
    EMIT CHANGES
    LIMIT 30


In another statement within Hue's Editor or by booting the SQL shell:

    docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

You can also insert your own records and notice the live updates of the results:

    INSERT INTO user_behavior (
      user_id ,
      item_id ,
      category_id ,
      behavior ,
      ts
    )
    VALUES
    (1, 10, 20, 'buy', '1602998392')



&nbsp;

In the next episodes, we will demo how to easily create tables directly from raw streams of data via the [importer](https://gethue.com/querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/).


Any feedback or question? Feel free to comment here!

All these projects are also open source and welcome feedback and contributions. In the case of the Hue editor the [Forum](https://discourse.gethue.com/) or [Github issues](https://github.com/cloudera/hue/issues) are good places for that.


Onwards!

Romain
