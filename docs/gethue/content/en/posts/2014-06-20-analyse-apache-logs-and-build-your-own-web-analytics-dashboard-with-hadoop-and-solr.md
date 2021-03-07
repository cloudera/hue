---
title: Analyse Apache logs and build your own Web Analytics dashboard with Hadoop and Solr
author: admin
type: post
date: 2014-06-20T15:46:18+00:00
url: /analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr/
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
slide_template:
  - default
categories:
---

Hue (3.6 or upcoming CDH5.1) ships with a dynamic dashboard builder for search. We presented the new interface in the previous <a href="https://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr/" target="_blank" rel="noopener noreferrer">Search episode</a>.

Here is the second part! We show how to index [Apache][1] log data and recreate the same dashboard in a few clicks. In this video, we are using real Apache logs from [demo.gethue.com][2], the live [Hadoop cluster][3]:

{{< youtube wwi2K0UPG0E >}}

For those wishing to skip to the end, a log file ready to be ingested is available [here][4].

As explained in the [How to Proxy Hue][5] blog post we are getting Apache logs for every page view. We retrieve the logs from the production machine and download the [script][6] that is going to clean them up, extract the Solr schema fields and geolocalize each page.

With this new indexer library we can now install the Hue [search examples][7] without any manual steps. Next features will include automatic geolocalization at query time, indexing of Hive or HBase tables and maybe a [Morphline][8] editor (basically all for getting rid of the Python part and allowing data ingestion of gigabytes or more).

As usual feel free to send any feedback on the [hue-user][9] list or [@gethue][10]!

[1]: https://httpd.apache.org/
[2]: http://demo.gethue.com
[3]: https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/
[4]: https://raw.githubusercontent.com/cloudera/hue/master/apps/search/examples/collections/solr_configs_log_analytics_demo/index_data.csv
[5]: https://gethue.com/i-put-a-proxy-on-hue/
[6]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/search/indexing
[7]: https://gethue.com/tutorial-live-demo-of-search-on-hadoop/
[8]: http://cloudera.github.io/cdk/docs/current/cdk-morphlines/index.html
[9]: http://groups.google.com/a/cloudera.org/group/hue-user
[10]: https://twitter.com/gethue
