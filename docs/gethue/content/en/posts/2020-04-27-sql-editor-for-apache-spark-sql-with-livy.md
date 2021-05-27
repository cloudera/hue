---
title: SQL Editor for Apache Spark SQL with Livy
author: Romain
type: post
date: 2020-04-27T00:00:00+00:00
url: /blog/quick-task-sql-editor-for-apache-spark-sql-with-livy/
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
  - Spark SQL
#  - Version 4.8

---

## Spark SQL

**Update December 2020** [Executing Spark SQL via the Spark Thrift Server](https://gethue.com/blog/querying-spark-sql-with-spark-thrift-server-and-hue-editor/)

[Spark SQL](https://spark.apache.org/docs/latest/sql-programming-guide.html) is convenient for embedding clean data querying logic within your Spark apps. Hue brings an Editor so that it is easier to develop your SQL snippets.

As detailed in the documentation, Spark SQL comes with different [connectors](https://docs.gethue.com/administrator/configuration/connectors/#apache-spark-sql). Here we will just show with Livy.

[Apache Livy](https://livy.incubator.apache.org/) provides a bridge to a running Spark interpreter so that SQL, pyspark and scala snippets can be executed interactively.

In the [hue.ini](https://docs.gethue.com/administrator/configuration/) configure the API url:

    [spark]
    # The Livy Server URL.
    livy_server_url=http://localhost:8998

And as always, make sure you have an interpreter configured:

    [notebook]
    [[interpreters]]
    [[[sparksql]]]
    name=Spark SQL
    interface=livy

And that's it, the editor will appear:

![Hue Spark Sql Editor](https://cdn.gethue.com/uploads/2020/04/editor_spark_sql_livy.png)

One advantage of using Hue is its [File Browser](https://docs.gethue.com/user/browsing/#data) for HDFS / S3 / Azure and full security (Kerberos and even using the real user credentials via [Knox IdBroker](https://docs.cloudera.com/runtime/7.1.0/cdp-security-overview/topics/security_how_identity_federation_works_in_cdp.html) integration).

![Hue Phoenix Editor](https://cdn.gethue.com/uploads/2016/08/image2.png)

Here are some of the future improvements:

* Database/table/column autocomplete is currently empty
* SQL grammar autocomplete can [be extended](https://docs.gethue.com/developer/development/#sql-parsers)
* [SQL Scratchpad](https://docs.gethue.com/developer/api/#scratchpad) module to allow a mini SQL Editor popup is in progress


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Romain from the Hue Team
