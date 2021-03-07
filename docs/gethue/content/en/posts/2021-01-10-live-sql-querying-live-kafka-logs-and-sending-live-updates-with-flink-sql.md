---
title: SQL Querying a log stream and outputting Calculations to another stream
author: Romain
type: post
date: 2021-01-10T00:00:00+00:00
url: /blog/sql-querying-live-kafka-logs-and-sending-live-updates-with-flink-sql/
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
  - Flink SQL
  - ksqlDB

---

*Initially published on https://medium.com/data-querying/live-sql-querying-live-logs-and-sending-live-updates-easily-e6297150cf92*

Log analysis tutorial from an Apache Kafka data stream via Flink SQL, ksqlDB & Hue Editor.

Real time queries on streams on data is a modern way to perform powerful analyses as demoed in the [previous post](https://medium.com/data-querying/how-to-easily-query-live-streams-of-data-with-kafka-and-flink-sql-7fa80731e9bd). This time we will see a more personalized scenario by querying our own logs generated in the Web Query Editor.

First, thank you to the community for all the improvements on the open source projects mentioned below, with in particular [Flink Version 1.12](https://flink.apache.org/news/2020/12/10/release-1.12.0.html) and the [SQL gateway](https://github.com/ververica/flink-sql-gateway/) as well as the [Hue Editor](http://gethue.com/).
> The goal is to demo the current SQL capabilities and ease of use of interactively building queries on streams of data.

![Querying a data log stream via Flink SQL and ksqlDB](https://cdn-images-1.medium.com/max/3690/1*968GTr1dtA1zfKTCVk-V9A.gif)

*Querying a data log stream via Flink SQL and ksqlDB*

## Architecture

The article comes with a live demo setup so that you can play with the products easily locally.

Raw logs from the Hue Editor..

    [29/Dec/2020 22:43:21 -0800] access  INFO   172.21.0.1 romain - "POST /notebook/api/get_logs HTTP/1.1" returned in 30ms 200 81

.. are being collected via [Fluentd](https://www.fluentd.org/), which [forwards](https://docs.fluentd.org/output/kafka) them directly to a Kafka topic after filtering out the non access/INFO rows (to keep the data simpler).

    {"container_id":"7d4fa988b26e2034670bbe8df3f1d0745cd30fc9645c19d35e8004e7fcf8c71d","container_name":"/hue","source":"stdout","log":"[29/Dec/2020 22:43:21 -0800] access  INFO   172.21.0.1 romain - \"POST /notebook/api/get_logs HTTP/1.1\" returned in 30ms 200 81"}

This data is then picked from the Kafka topic, then analyzed interactively before being turned into a long running query calculating how many API calls per logged-in user are being made within [rolling windows](https://ci.apache.org/projects/flink/flink-docs-release-1.12/concepts/timely-stream-processing.html#windowing) of 10 seconds.

![Live stream analysis Architecture](https://cdn-images-1.medium.com/max/2000/1*AdoZQxikyBixQSCOUwiRpg.png)

*Live stream analysis Architecture*

## Demo

For fetching the Docker Compose [configuration](https://raw.githubusercontent.com/romainr/query-demo/master/stream-sql-logs/docker-compose.yml) and starting everything:

    mkdir stream-sql-logs
    cd stream-sql-logs

    wget https://raw.githubusercontent.com/romainr/query-demo/master/stream-sql-logs/docker-compose.yml

    docker-compose up -d
    >
    Creating network "stream-sql-logs_default" with the default driver
    Creating hue-database                 ... done
    Creating stream-sql-logs_jobmanager_1 ... done
    Creating stream-sql-logs_fluentd_1    ... done
    Creating stream-sql-logs_zookeeper_1   ... done
    Creating ksqldb-server                 ... done
    Creating hue                           ... done
    Creating stream-sql-logs_taskmanager_1 ... done
    Creating flink-sql-api                 ... done
    Creating stream-sql-logs_kafka_1       ... done

Then those URLs will be up:

* [http://localhost:8888/](http://localhost:8888/) Hue Editor
* [http://localhost:8081/](http://localhost:8081/) Flink Dashboard

For stopping everything:

    docker-compose down

## Scenario

While interacting with the Web Editor, Web logs are being generated. We will ingest a subset of them into a Kafka Topic that we will query via Flink SQL. ksqlDB is used to prove that at the end of the day all the SQL SELECTs and INSERTs are purely going through standard Kafka topics.

Once again, the [TUMBLE](https://ci.apache.org/projects/flink/flink-docs-release-1.12/dev/table/sql/queries.html#group-windows) function is used to easily create live windows of aggregation.

We logged-in as two separate users (‘demo’ and ‘romain’) to show the grouping by username.

One of the novelty in Flink is the new [UPSERT into Kafka](https://ci.apache.org/projects/flink/flink-docs-release-1.12/dev/table/connectors/upsert-kafka.html#key-and-value-formats) connector, which will let us send the rolling aggregated data back into Kafka. This enables further downwards consumption by reporting or alerting systems which can simply read from the topic.

![Calculating and inserting a rolling window of live stats into a Kafka Topic](https://cdn-images-1.medium.com/max/3296/1*G1nW-KMRFrWl7g6MTcCYiA.png)*Calculating and inserting a rolling window of live stats into a Kafka Topic*

As a follow-up, the querying could be more elaborate via the extraction of the real datetime and HTTP code fields as well as outputting alert messages when the counts go above/below a certain threshold, which is perfect for building a [live application](https://flink.apache.org/2020/07/28/flink-sql-demo-building-e2e-streaming-application.html) on top of it.

One of niceties of the editor is to let you interactively fiddle with [SQL functions](https://ci.apache.org/projects/flink/flink-docs-release-1.12/dev/table/functions/systemFunctions.html) like REGEXP_EXTRACT, DATE_FORMAT… which can be time consuming to get right.

## SQL

Here is the SQL source typed in the Query Editor:

<script src="https://gist.github.com/romainr/dc5087f26c3bcaf90906b83c489f2413.js"></script>

<script src="https://gist.github.com/romainr/fff457cd69d7328cce8652e93f555692.js"></script>

## Et voila!

Any feedback or question? Feel free to comment here!

All these projects are also open source and welcome feedback and contributions.

In the case of the Hue Editor, the [Forum](https://discourse.gethue.com/) or [Github issues](https://github.com/cloudera/hue/issues) are good places for that. More sophisticated SQL autocompletes and connectors, Web Socket and Celery Task server integrations are some improvement ideas.

Onwards!

Romain
