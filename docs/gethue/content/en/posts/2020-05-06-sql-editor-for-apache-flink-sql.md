---
title: SQL Editor for Apache Flink SQL
author: Romain
type: post
date: 2020-05-06T00:00:00+00:00
url: /blog/sql-editor-for-apache-flink-sql/
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
  - Version 4
  - Flink SQL
#  - Version 4.8

---

# Flink SQL Editor

This is the very first version of the SQL Editor for Flink.

The goal is to demo how to execute Flink SQL queries. We use the new Flink SQL gateway project and point to a Flink cluster with live data in a docker container. Hue is used as the SQL Editor for querying Flink tables.

Feel free to read more about Flink [SQL](https://ci.apache.org/projects/flink/flink-docs-master/dev/table/sql/queries.html#queries) and [continuous](https://ci.apache.org/projects/flink/flink-docs-master/dev/table/streaming/dynamic_tables.html#continuous-queries) queries.

{{< youtube fKHD-fOdDY0 >}}

## Setup

Any Flink 1.10 cluster would work and the demo is based on [Ververica SQL Training](https://github.com/ververica/sql-training) which has some easy [setup instructions](https://github.com/ververica/sql-training/wiki/Setting-up-the-Training-Environment):

    git clone https://github.com/ververica/sql-training.git
    cd sql-training
    docker-compose up -d

Then [http://localhost:8081](http://localhost:8081) should be up.

![Flink Dashboard](https://cdn.gethue.com/uploads/2020/05/flink_dashboard.png)

Here we start a SQL client container and install the gateway inside (to avoid installing a local Flink as the gateway needs a FLINK_HOME) but this could be done locally or in another containers.

    docker-compose exec sql-client bash

We grab a [release](https://github.com/ververica/flink-sql-gateway/releases) of the gateway:

    cd /opt
    wget https://github.com/ververica/flink-sql-gateway/releases/download/flink-1.11.1/flink-sql-gateway-0.2-SNAPSHOT-bin.zip
    unzip flink-sql-gateway-0.2-SNAPSHOT-bin.zip
    cd flink-sql-gateway-0.2-SNAPSHOT

    echo $FLINK_HOME

Then from another shell we copy the Flink SQL config to the gateway so that we get the demo tables by default:

    wget https://raw.githubusercontent.com/romainr/flink-sql-gateway/master/docs/demo/sql-gateway-defaults.yaml

    docker cp sql-gateway-defaults.yaml sql-training_sql-client_1:/opt/flink-sql-gateway-0.2-SNAPSHOT/conf/

Now we can go back to the shell in the container and are ready to start it:

    cd bin
    ./sql-gateway.sh --library /opt/sql-client/lib

Putting the server in the background with `CTRL-Z` and then:

    bg

And now we can issue a few commands to validate the setup:

    curl sql-training_sql-client_1:8083/v1/info
    > {"product_name":"Apache Flink","version":"1.10.0"}

    curl -X POST sql-training_sql-client_1:8083/v1/sessions -d '{"planner":"blink","execution_type":"streaming"}'
    > {"session_id":"7eea0827c249e5a8fcbe129422f049e8"}


**Note**

It "should" also be possible to deploy the SQL gateway not in the SQL client container by:

1. Having a local Flink [binary package](https://www.apache.org/dyn/closer.lua/flink/flink-1.10.0/flink-1.10.0-bin-scala_2.11.tgz) with FLINK_HOME configured

2. Updating the `jobmanager.rpc.address` to the real jobmanager address in `$FLINK_HOME/conf/flink-conf.yaml`

3. Changing the two address properties in `sql-gateway-defaults.yaml`

<pre>
    server:
      # The address that the gateway binds itself.
      bind-address: 172.18.0.7
      # The address that should be used by clients to connect to the gateway.
      address: 172.18.0.7
</pre>

## Query Editor

As detailed in the [connector](https://docs.gethue.com/administrator/configuration/connectors/) section of Hue, we add a Flink interpreter:

    [notebook]

    [[interpreters]]

    [[[flink]]]
    name=Flink
    interface=flink
    options='{"url": "http://172.18.0.7:8083"}'

If we are setting up the gateway in the client container and want to access it via your localhost, we need to update its bind IP with the IP of the SQL client container.

The IP of the gateway service is the one of the running container. We inspect the `sql-training_sql-client_1` to retrieve its IP:

    docker ps
    > CONTAINER ID        IMAGE                                                COMMAND                  CREATED              STATUS              PORTS                                                NAMES
    > 638574b31cd6        fhueske/sql-training:1-FLINK-1.10-scala_2.11   "/docker-entrypoint.…"   About a minute ago   Up About a minute   6123/tcp, 8081/tcp                                   sql-training_sql-client_1
    > 59d1627c412a        wurstmeister/kafka:2.12-2.2.1                        "start-kafka.sh"         About a minute ago   Up About a minute   0.0.0.0:9092->9092/tcp                               sql-training_kafka_1
    > 6711c0707f1e        flink:1.10.0-scala_2.11                              "/docker-entrypoint.…"   About a minute ago   Up About a minute   6121-6123/tcp, 8081/tcp                              sql-training_taskmanager_1
    > 6a8149af6c1e        flink:1.10.0-scala_2.11                              "/docker-entrypoint.…"   About a minute ago   Up About a minute   6123/tcp, 0.0.0.0:8081->8081/tcp                     sql-training_jobmanager_1
    > 3de8275dff26        wurstmeister/zookeeper:3.4.6                         "/bin/sh -c '/usr/sb…"   About a minute ago   Up About a minute   22/tcp, 2888/tcp, 3888/tcp, 0.0.0.0:2181->2181/tcp   sql-training_zookeeper_1
    > a28cee7627a0        mysql:8.0.19                                         "docker-entrypoint.s…"   About a minute ago   Up About a minute   3306/tcp, 33060/tcp                                  sql-training_mysql_1

    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' sql-training_sql-client_1
    > 172.18.0.7

![Flink SQL Editor](https://cdn.gethue.com/uploads/2020/05/flink_editor_v1.png)

And now we can use the left assist to browse the tables, drag and drop one to query it easily as well as leverage the autocomplete for writing more powerful queries:

    SELECT taxiId, isStart
    FROM default_database.Rides
    LIMIT 100
    ;

    SELECT
      psgCnt,
      COUNT(*) AS cnt
    FROM Rides
    WHERE isInNYC(lon, lat) AND isStart
    GROUP BY
      psgCnt
    ;

The Flink Dashboard will show the SQL queries running as regular jobs:

![Flink Job Dashboard](https://cdn.gethue.com/uploads/2020/05/flink_dashboard_one_query.png)

## Next

There are lot of [future iterations](https://github.com/cloudera/hue/blob/master/docs/designs/apache_flink.md) on this first version to make it production ready but the base is getting there.

One that should be of popular interest would be to improve the [SQL autocomplete](https://ci.apache.org/projects/flink/flink-docs-master/dev/table/sql/queries.html#supported-syntax) which is based on [Apache Calcite](https://calcite.apache.org/docs/reference.html). Hue comes with a SDK for writing better [grammars](https://docs.gethue.com/developer/development/#sql-parsers) and even ships with a default [Flink SQL dialect](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/jison/sql/flink).

Another one coming soon will be a more user friendly display of the live data in the result grid.


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> Live SQL querying!


Romain from the Hue Team
