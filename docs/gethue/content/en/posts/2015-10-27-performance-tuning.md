---
title: Hue performance tuning guide
author: admin
type: post
date: 2015-10-27T22:20:55+00:00
url: /performance-tuning/
sf_remove_promo_bar:
  - 1
sf_caption_position:
  - caption-right
sf_right_sidebar:
  - Sidebar-1
sf_left_sidebar:
  - Sidebar-2
sf_sidebar_config:
  - left-sidebar
sf_social_sharing:
  - 1
sf_background_image_size:
  - cover
sf_page_title_text_style:
  - light
sf_page_title_bg:
  - none
sf_no_breadcrumbs:
  - 1
sf_page_title_style:
  - standard
sf_page_title:
  - 1
sf_detail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_thumbnail_type:
  - none
ampforwp-amp-on-off:
  - default
categories:
  - Development

---
<span style="color: #ff0000;"><em>Last update Aug 30th 2018</em></span>

### Latest

A major improvement in 4.2 is [IMPALA-1575][1], meaning that Impala queries not closed by Hue have their resources actually released after 10min (vs never until then). This is a major improvement when having many users. It is worth the upgraded even just for this one.

Hue in [4.2][2] got 500+ bug fixes. Hue also now comes with  caching of SQL metadata throughout all the application, meaning the list of tables or a database or the column description of a table are only fetched once and re-used in the autocomplete, table browser, left and right panels etc.. The profiling of calls is simpler in 4.2 with a total time taken by each request automatically logged.

Typical setups range from 2 to 10 Hue servers, e.g. 10 Hue servers, 250 unique users / week, peaks at 125 users/hour with 300 queries

In practice ~25 users / Hue peak time is the rule of thumb. This is accounting for the worse case scenarios and it will go much higher with the upcoming <http://gunicorn.org/> integration. Most of the scale issues are actually related to resource intensive operations like large download of query results or when an RPC call from Hue to a service is slow (e.g. submitting a query hangs), not by the number of users.

&nbsp;

Here you can find a list of tips regarding some performance tuning of Hue:

### General Performance

  1. Each Hue instance will support by default 5**0+ concurrent users** by following this [guide][3]. Adding more Hue instances behind the load balancer will increase performances by 50 concurrent users. If not using Cloudera Manager, you can manually setup [NGINX][4] or [Apache][5] in front of Hue.
  2. Move the database from the default database across to another database backend such as MySql/Postgres/Oracle, which handles locking better than the default SQLite DB. **Hue should not be run on SQLite in an environment with more than 1 concurrent user.** Read more about

    [using an External Database for Hue Using Cloudera Manager][6]
  3. There are some memory fragmentation issues in Python that manifest in Hue. Check the memory usage of Hue periodically. Browsing HDFS dir with many files, downloading a query result, copying a HDFS files are costly operations memory wise.
  4. Upgrade to later versions of Hue. There are significant performance gains available in every release.

[<img src="https://cdn.gethue.com/uploads/2015/03/with-nginx.png" />][7]

### Query Editor Performance

  1. Compare performance of the Hive Query Editor in Hue with the exact same query in a beeline shell against the exact same HiveServer2 instance that Hue is pointing to. This will determine if Hue needs to be investigated or HiveServer2 needs to be investigated.
  2. Check the logging configuration for HiveServer2 by going to **Hive service Configuration** in Cloudera Manager. Search for **HiveServer2 Logging Threshold** and make sure that it is not set to `DEBUG or TRACE`. If it is, drop the logging level to `INFO` at a minimum.
  3. Configure individual dedicated HiveServer2 instances for each Hue instance separate from HiveServer2 instances used by other 3rd party tools or clients, or [configure Hue to point to multiple HS2 instances behind a Load Balancer][8].
  4. Tune the query timeouts for HiveServer2 (in `hive-site.xml`) and Impala on the hue_safety_valve or hue.ini: [Query Life Cycle][9]
  5. Downloading queries past a [few thousands rows][10] will lag and increase CPU/memory usage in Hue by a lot. It is for this we are truncating the results until [further improvements][11].

###

Feel free to ask any questions about the architecture, usage of the server in the comments, [@gethue][12] or the [hue-user][13] list!

 [1]: https://issues.apache.org/jira/browse/IMPALA-1575
 [2]: https://gethue.com/hue-4-2-and-its-self-service-bi-improvements-are-out/.
 [3]: https://gethue.com/automatic-high-availability-and-load-balancing-of-hue-in-cloudera-manager-with-monitoring/
 [4]: https://gethue.com/using-nginx-to-speed-up-hue-3-8-0/
 [5]: https://gethue.com/how-to-run-hue-with-the-apache-server/
 [6]: http://www.cloudera.com/content/www/en-us/documentation/enterprise/latest/topics/cm_mc_hue_service.html
 [7]: https://cdn.gethue.com/uploads/2015/03/with-nginx.png
 [8]: https://gethue.com/how-to-optimally-configure-your-analytic-database-for-high-availability-with-hue-and-other-sql-clients/
 [9]: https://gethue.com/hadoop-tutorial-hive-and-impala-queries-life-cycle/
 [10]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L746
 [11]: https://issues.cloudera.org/browse/HUE-2142
 [12]: http://twitter.com/gethue
 [13]: http://groups.google.com/a/cloudera.org/group/hue-user
