---
title: Build a Real Time Analytic dashboard with Solr Search and Spark Streaming
author: admin
type: post
date: 2015-05-21T17:59:27+00:00
url: /build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
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
categories:
  - Tutorial
---

Search is a great way to interactively explore your data. The Search App is [continuously improving][1] and now comes with a better support for real time!

In this video, we are collecting tweets with Spark Streaming and directly indexing them into Solr with the [Spark Solr][2] app. Note that we are using a slightly [modified version][3] that adds more [tweet information][4].

{{< youtube qnGEx-3Refg >}}

&nbsp;

You can see the tweets rolling in! Compared to the previous version:

- the dashboard updates its widgets only when the data changes without any page jumping
- the dashboard can refresh itself automatically every N seconds
- a main date filter lets you quickly select a rolling date range for all the dashboard

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2015/05/live-search-1024x509.png"><img src="https://cdn.gethue.com/uploads/2015/05/live-search-1024x509.png" /></a><figcaption>Tweets coming in</figcaption></figure>

&nbsp;

**Instructions**

Download a [nightly Solr 5.x][6], uncompress it and start it:

<pre><code class="bash">

bin/solr start -cloud

bin/solr create -c tweets

</code></pre>

Then compile the [Spark Solr app][7].

Enable the analytic widgets in hue.ini:

<pre><code class="bash">[search]

latest=true

</code></pre>

**Sum-up**

They are other ways to index data in [near real time][8] but we took this approach as the scenario was working out of the box with just Spark Streaming and the Solr app. Next time, we will preview the new [Analytics Features][9] of Solr 5.2 and show how we can use Python Spark to index some data!

As usual feel free to comment on the [hue-user][10] list or [@gethue][11]!

[1]: https://gethue.com/more-solr-search-dashboards-possibilities/
[2]: https://github.com/LucidWorks/spark-solr
[3]: https://github.com/romainr/spark-solr
[4]: https://github.com/romainr/spark-solr/commits/master
[5]: https://cdn.gethue.com/uploads/2015/05/live-search.png
[6]: https://builds.apache.org/job/Solr-Artifacts-5.x/lastSuccessfulBuild/artifact/solr/package/
[7]: https://github.com/romainr/spark-solr#example-applications
[8]: http://www.cloudera.com/content/cloudera/en/documentation/cloudera-search/v1-latest/Cloudera-Search-User-Guide/csug_flume_nrt_index_ref.html
[9]: http://yonik.com/solr-facet-functions/
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
[11]: https://twitter.com/gethue
