---
title: SQL Editor for Apache Impala
author: Romain
type: post
date: 2020-04-30T00:00:00+00:00
url: /blog/quickstart-sql-editor-for-apache-impala/
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
  - Impala
#  - Version 4.8

---

## Impala SQL

[Apache Impala](https://impala.apache.org/) is a fast SQL engine for your data warehouse. Want to give it a quick try in 3 minutes? Here is how!

### Starting Impala

First make sure your have docker installed in your system. Then, based on the great [tutorial](https://github.com/apache/kudu/tree/master/examples/quickstart/impala) of [Apache Kudu](https://kudu.apache.org/) (which we will cover next, but in the meantime the [Kudu Quickstart](https://kudu.apache.org/docs/quickstart.html) is worth a look), just execute:

    docker run -d --name kudu-impala -p 21000:21000 -p 21050:21050 -p 25000:25000 -p 25010:25010 -p 25020:25020 --memory=4096m apache/kudu:impala-latest impala

Afterwards, `docker ps` should show:

    > docker ps
    CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS              PORTS                                                                                                                              NAMES
    fe7b68d167b3        apache/kudu:impala-latest   "/impala-entrypoint.…"   4 seconds ago       Up 3 seconds        0.0.0.0:21000->21000/tcp, 0.0.0.0:21050->21050/tcp, 0.0.0.0:25000->25000/tcp, 0.0.0.0:25010->25010/tcp, 0.0.0.0:25020->25020/tcp   kudu-impala

Then just enter the running container and start the SQL shell:

    > docker exec -it kudu-impala impala-shell

    Starting Impala Shell without Kerberos authentication
    Opened TCP connection to fe7b68d167b3:21000
    Connected to fe7b68d167b3:21000
    Server version: impalad version 3.3.0-RELEASE RELEASE (build 0f840c5a0f5e673c67cbd482e62065fd47b98e1a)
    ***********************************************************************************
    Welcome to the Impala shell.
    (Impala Shell v3.4.0-SNAPSHOT (b0c6740) built on Thu Oct 17 10:56:02 PDT 2019)

    When you set a query option it lasts for the duration of the Impala shell session.
    ***********************************************************************************

And run some [SQL instructions](https://impala.apache.org/docs/build/html/topics/impala_langref.html):

    [fe7b68d167b3:21000] default> show tables;
    Query: show tables
    Fetched 0 row(s) in 0.36s
    [fe7b68d167b3:21000] default> create table a (a int);
    Query: create table a (a int)
    +-------------------------+
    | summary                 |
    +-------------------------+
    | Table has been created. |
    +-------------------------+
    Fetched 1 row(s) in 1.31s

    [fe7b68d167b3:21000] default> insert into a values (1);
    Query: insert into a values (1)
    Query submitted at: 2020-04-30 17:42:59 (Coordinator: http://fe7b68d167b3:25000)
    Query progress can be monitored at: http://fe7b68d167b3:25000/query_plan?query_id=cb410a4f8b0b0d6a:1a8a909e00000000
    Modified 1 row(s) in 1.60s

    [fe7b68d167b3:21000] default> select * from a;
    Query: select * from a
    Query submitted at: 2020-04-30 17:43:08 (Coordinator: http://fe7b68d167b3:25000)
    Query progress can be monitored at: http://fe7b68d167b3:25000/query_plan?query_id=7242c5151534b8db:bef9c91000000000
    +---+
    | a |
    +---+
    | 1 |
    +---+
    Fetched 1 row(s) in 0.33s

    [fe7b68d167b3:21000] default> exit

## SQL Editor

Typing SQL with a Query Assistant is even more productive.

 cf. above `docker ps`, get the container ID and retrieve its IP via:

    > docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 638574b31cd6
    172.17.0.2

As Impala is deeply integrated with Hue, in the [hue.ini](https://docs.gethue.com/administrator/configuration/) simply configure the hostname of the container:

    [impala]
    server_host=172.17.0.2

And restart Hue and that's it, the editor will appear:

![Hue Impala SQL Editor](https://cdn.gethue.com/uploads/2020/04/hue-4.7.png)


To read more in depth about the SQL Experience follow this [blog post](/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/).


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> querying!


Romain from the Hue Team
