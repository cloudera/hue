---
title: Quickstart Hue in Docker and query any of your Database
author: admin
type: post
date: 2020-08-19T00:00:00+00:00
url: /quickstart-hue-in-docker/
ampforwp-amp-on-off:
  - default
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
sf_author_info:
  - 1
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
categories:
  - Version 4
#  - Version 4.8
tags:
  - cloud
  - container
  - docker

---

Query any Data Warehouse in minutes!

In this tutorial we configure Hue to use an existing MySQL database and point to an [Apache Hive](https://hive.apache.org/) data warehouse that we want to query.

![Autocomplete and context assist](https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif)

**Note** If you are looking another warehouse than Hive, check out all the [other connectors](https://docs.gethue.com/administrator/configuration/connectors/).

There are two important concepts:

* Persistence: Hue needs an existing database with transactions like MySQL to support concurrent requests and also not lose the registered users, saved queries, sharing permissions... when the server gets stopped.
* Compute: this is done by running the server image in a container. This one can be started or stopped or replicated multiple times depending on the load or high availability requirements.

Let's pull and start the latest Hue container and open a shell inside it:

    docker run -it -p 8888:8888 gethue/hue:latest /bin/bash

This puts us into the `/usr/share/hue` home folder of the Hue installation. Now let's open the configuration file:

    apt-get install -y vim

    vim desktop/conf/hue.ini

First let's make sure that Hue is backed by a relational database supporting transactions like MySQL, PostgreSql or Oracle. Here we go with MySQL and fill-up the `[[database]]` section with the credentials:

    [desktop]
    [[database]]
    host=demo.gethue.com  # Use 127.0.0.1 and not localhost if on the same host
    engine=mysql
    user=hue
    password=password
    name=hue

**Note** An alternative way to boot a production ready Hue with its own MySQL database is to use the [Docker compose](https://github.com/cloudera/hue/tree/master/tools/docker/hue#docker-compose).

Then, we add the following block to the `[beeswax]` and `[notebook]` sections so that we can query the Apache Hive instance running in one server we have access to. If you don't have a running HiveServer2, check the development quickstart that demoes how to [boot one quickly](https://docs.gethue.com/developer/development/#first-sql-queries) with (Docker too ;):

    [beeswax]
    hive_server_host=demo.gethue.com

    [notebook]
    [[interpreters]]
    [[[hive]]]
    name=Hive
    interface=hiveserver2

**Note** As a bonus, feel free to also add a MySql interpreter pointing to the Hue database, it can queries itself with no issues:

    [[[mysql]]]
    name=MySQL
    interface=sqlalchemy
    options='{"url": "mysql://hue:password@demo.gethue.com:3306/hue"}'

Now from another terminal use `docker ps` to identify the Hue container id and commit its state to remember the configuration even after stopping it:

    docker ps

    docker commit 368f0d568a5f hue-hive

**Note** An alternative way of using `docker commit` is to keep the hue.ini configuration file outside of the docker image and simply mount it inside when starting the container as shown in the [Docker How-to](https://github.com/cloudera/hue/tree/master/tools/docker/hue#configuration).

Now you can start the saved container which will expose the Hue interface on [localhost:8888](localhost:8888).

    docker run -it -p 8888:8888 hue-hive ./startup.sh


And that's it, now it is time to execute some [SQL queries](https://docs.gethue.com/user/querying/)!

![Hue login page](https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png)

Any feedback? Feel free to comment here or on [@gethue](https://twitter.com/gethue)!

Romain from the Hue Team
