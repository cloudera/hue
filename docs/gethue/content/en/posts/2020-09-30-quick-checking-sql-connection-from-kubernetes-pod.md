---
title: Quick checking Hue's SQL Editor connections to Databases in Kubernetes
author: Romain
type: post
date: 2020-09-30T00:00:00+00:00
url: /blog/quick-checking-sql-connection-from-kubernetes-pod/
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
  - Version 4.9
  - Hive

---
Let's see one way to quickly check why Hue can't connect to a SQL Database in the Kubernetes world.

We previously documented how to run Hue in [Kubernetes](/hue-in-kubernetes/) or [Docker](/quickstart-hue-in-docker/).

The concept is to use the Database specific command shell on the command line to try to send some queries.

[Apache Hive](https://docs.gethue.com/administrator/configuration/connectors/#apache-hive) is the Data Warehouse used as example (but this would work the same with `psql`, `mysql`, ...) or any other Database Hue can [connect to](https://docs.gethue.com/administrator/configuration/connectors/).

This will install extra files in the current Hue pod but will enable you to test the interaction from the exact same location as the Hue service (so good for troubleshooting `connectivity` or `authentication` issues).

&nbsp;

First check your Hive version in the SQL Editor:

    SELECT version()

    > 2.3.2 r857a9fd8ad725a53bd95c1b2d6612f9b1155f44d

Then list the Hue pods:

    kubectl get pods

    > NAME                                        READY   STATUS      RESTARTS   AGE
    hue-758466dc77-wpcx8                        2/2     Running     0          22h
    ingress-nginx-controller-5d6fbbddb6-8kd86   1/1     Running     0          23h
    postgres-hue-64c9cc8744-dpk47               1/1     Running     1          47d

Connect to one:

    kubectl exec -it hue-758466dc77-wpcx8 hue -- bash

Then get the client files of the same Hive version from:

* https://archive.apache.org/dist/hadoop/core
* https://archive.apache.org/dist/hive

And install them:

    sudo apt-get install wget
    wget https://archive.apache.org/dist/hadoop/core/hadoop-2.7.4/hadoop-2.7.4.tar.gz
    wget https://archive.apache.org/dist/hive/hive-2.3.2/apache-hive-2.3.2-bin.tar.gz

    tar -xvzf hadoop-2.7.4.tar.gz
    tar -xvzf apache-hive-2.3.2-bin.tar.gz

    export HADOOP_HOME=`pwd`/hadoop-2.7.4
    export HIVE_HOME=`pwd`/apache-hive-2.3.2-bin
    export JAVA_HOME=/usr/lib/jvm/java-1.11.0-openjdk-amd64

    PATH=$PATH:$HIVE_HOME/bin

Now you are ready to connect:

    beeline -u 'jdbc:hive2://172.21.0.3:10000'

    > SLF4J: Class path contains multiple SLF4J bindings.
    SLF4J: Found binding in [jar:file:/usr/share/hue/apache-hive-2.3.2-bin/lib/log4j-slf4j-impl-2.6.2.jar!/org/slf4j/impl/StaticLoggerBinder.class]
    SLF4J: Found binding in [jar:file:/usr/share/hue/hadoop-2.7.4/share/hadoop/common/lib/slf4j-log4j12-1.7.10.jar!/org/slf4j/impl/StaticLoggerBinder.class]
    SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.
    SLF4J: Actual binding is of type [org.apache.logging.slf4j.Log4jLoggerFactory]
    Connecting to jdbc:hive2://172.21.0.3:10000
    Connected to: Apache Hive (version 2.3.2)
    Driver: Hive JDBC (version 2.3.2)
    Transaction isolation: TRANSACTION_REPEATABLE_READ
    Beeline version 2.3.2 by Apache Hive
    0: jdbc:hive2://172.21.0.3:10000> SHOW TABLES;
    +--------------------+
    |      tab_name      |
    +--------------------+
    | about              |
    | amandine_test      |
    | city_cases         |
    | cricketer          |
    | cust1              |
    | cust2              |
    | customer           |
    | customers          |
    | student_info       |
    | ........           |
    | web_logs           |
    | yash_contact_test  |
    +--------------------+
    52 rows selected (0.098 seconds)

... and your SQL users can [start self service querying](/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/) again!

![Hue Editor](https://cdn.gethue.com/uploads/2020/09/hue-4.8.png)

Read more on the Hive wiki about the [beeline command line](https://cwiki.apache.org/confluence/display/Hive/HiveServer2+Clients#HiveServer2Clients-Beeline%E2%80%93CommandLineShell).


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Onwards!

Romain from the Hue Team
