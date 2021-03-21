---
title: 10 years of Data Querying Experience Evolution with Hue
author: Romain
type: post
date: 2020-01-28T00:00:00+00:00
url: /blog/2020-01-28-ten-years-data-querying-ux-evolution/
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
#  - Version 4.7

---

[Hue](http://gethue.com/) has just blown its 10th candle. Hue was created when Apache Hadoop was still in its infancy before becoming mainstream (read more about the Hadoop story in [Hadoop is Dead. Long live Hadoop](https://medium.com/@acmurthy/hadoop-is-dead-long-live-hadoop-f22069b264ac)).

Hue originally was a part of Cloudera Manager, which was proprietary and focused more on the administrators but was then moved out to its own [open source](https://github.com/cloudera/hue) project in [version 0.3](https://docs.gethue.com/releases/release-notes-0.3.0/). Hue then gradually evolved from being a desktop like application to a modern single page SQL Editor (and is at [version 4.6](https://docs.gethue.com/releases/release-notes-4.6.0/) as of today).

Through continuous iterations, Hue kept improving on its main goal: facilitating the ease of use to the data platform. The user base primarily consists of anybody looking at querying data: e.g.:

* Data Analyst answering some ad-hoc questions
* Program Managers looking at usage stats
* IT/SQL Developers building some Data apps
* Data Architects poking at the whole usability of the system
* Data Engineers nurturing the Data Warehouse table creations

The second category consists of more technical users wanting to see job logs, upload data to the distributed file systems like HDFS or AWS S3, build workflows, create search dashboards, optimize queries...

![Hue 1 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-1.png)

Hue 1 (2009) - A desktop-feel application with an Apache Hive Editor, Hadoop File and Job browsers.

![Hue 2 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-2.png)
Hue 2 (2012) - Flat design, advanced SQL Editor and adding more than 15 new apps/connectors to the data platform with proper security (e.g. for browsing tables, building workflows and search dashboards)

![Hue 3 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-3.png)
Hue 3 (2013) - Aggregating and inter-linking the apps together into a single experience and providing a single page Editor and a much more powerful SQL intellisense

![Hue 4 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-4.png)
Hue 4 (2017) - Major revamp of the interface turning Hue into a modern and simpler single page app. Next steps of SQL intellisense with smart recommendations, risk alerts and data catalog integration

## More users and More SQL
With the merging of Cloudera (CDH) and Hortonworks (HDP) distributions into CDP (Cloudera Data Platform, then available in [Data Center](https://www.cloudera.com/products/cloudera-data-platform/cdp-data-center.html) or Cloud), Hue is becoming ubiquitous and available to even more users via:

* 1000+ combined customers (including an important part of the Fortune 500)
* 100 000s of SQL queries are being executed manually via Hue daily

Upstream Hue is also shipped in several other distributions like AWS EMR, IBM Open Data Hub and has an active community.

![Hue 4.6 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-4.6.png)
Hue 4.6 (2019) - Componentization continues and stronger Data Warehouse integration for SQL querying and browsing files in the Cloud

In 2020, the upcoming Hue 5 is specializing even more into Data Warehousing and has for focus to provide the best SQL Cloud Editor:

* First with deeper and deeper support of the Apache Hive and Apache Impala SQL engines. The SQL interfaces are also being revamped into stable components allowing an easy welcome of other engines of the Apache Calcite family and more like Apache Phoenix, Apache Druid, Apache Flink SQL. More collaboration with richer query sharing as well as an even smarter intellisense and assistant to optimize queries.
* Secondly by being “Cloud Ready” and fitting well in the world of scaling up and down containers and automated infrastructure. The first version of Hue on Kubernetes has already been shipped and more scale and simpler operation management are coming.

We will deep dive in greater details on the querying capabilities of the SQL Cloud Editor in part two of this series of 10 years of evolution of Hue. Until then, feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!


Romain, from the Hue Team
