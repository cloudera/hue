---
title: Interactively Querying HBase via SQL - Tech Talk
author: Hue Team
type: post
date: 2021-04-05T00:00:00+00:00
url: /blog/2021-04-05-interactively-querying-hbase-via-sql-tech-talk
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
  - Version 4.10
  - Phoenix

---
Grow your user base able to leverage data stored in HBase via SQL queries with Apache Phoenix and the Hue Web SQL Editor.

April 1st 2021 (not a joke ;) we did a [tech talk](https://phoenix.apache.org/tech_talks.html) (nicely organized by the [Apache Phoenix](https://phoenix.apache.org/) project) on the underlying technology enabling SQL queries on [Apache HBase](https://hbase.apache.org/) tables.

See the slides:

[**Executing Phoenix queries in Hue SQL Editor**](https://drive.google.com/file/d/1-3OwisGp1D5za2ukFW7DukrQkF3AJg9O/view)

For people not familiar with HBase, imagine a giant big table specialized in storing and updating in real time any type of records. But how to operate it?

SQL queries are much shorter and easier for implementing/maintaining the logic than using lower level API (e.g. think HBase shell commands or programming in Java with the HBase objects). Embedding SQL queries into your HBase applications is very efficient: it takes only a few lines in a universal declarative language close to English for creating tables, inserting data etc…

The SQL Editor let’s you quickly edit and test these queries in an interactive fashion from the comfort of your browser (i.e. no need to VPN, open a shell and remember which host to point to or how to authenticate...) or memorize the instructions/”where is what” thanks to all the autocompletes, schema browsers, collab features.

![](https://cdn-images-1.medium.com/max/2000/1*2ADf80ARS-sZEl9PZIh1hQ.png)

Long story short, by adopting a [Web SQL interface](https://gethue.com/sql-querying-apache-hbase-with-apache-phoenix/) supporting the Phoenix SQL dialect you potentially grew your user base able to query data and leverage it in your domain knowledge from a handful to hundreds.

Towards the end of the talk, we did a live log analysis demo, which you can also run locally in 1 minute, as [published previously](https://medium.com/data-querying/phoenix-brings-sql-to-hbase-and-let-you-query-kafka-data-streams-8fd2edda1401)!

Note: there is also a parallel effort to make the SQL Editor available as a [Scratchpad component](https://docs.gethue.com/developer/components/scratchpad/), so that it becomes even simpler to edit embedded SQL!

Now go grab it and give it a spin!

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Onwards!

Romain from the Hue Team
