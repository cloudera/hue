---
title: Solr Search UI – How to configure Hue with only the Search App
author: admin
type: post
date: 2015-03-12T16:49:33+00:00
url: /solr-search-ui-only/
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
ampforwp-amp-on-off:
  - default
categories:
---

The [Solr Search App][1] is having a great success and users often wonder if they could use it without the Hadoop related apps. As the app is only using the standard Apache Solr REST API and Hue allows to customize which apps to show, the answer is yes!

**Note**: this is an alternative to configure the [groups and application permissions][2] directly in the User Admin.

{{< youtube lZTHhOtmFN4 >}}

&nbsp;

**1.** Install Hue from the links on the 'Download' section menu

[<img src="https://cdn.gethue.com/uploads/2015/03/hue-download-1024x375.png" />][3]

&nbsp;

**2.** Only enable the Solr Search App

In the hue.ini (See '[Where is my hue.ini][4]'?), blacklist all the other apps:

<pre><code class="bash">

[desktop]

app_blacklist=beeswax,impala,security,filebrowser,jobbrowser,rdbms,jobsub,pig,hbase,sqoop,zookeeper,metastore,spark,oozie

</code></pre>

At the same time, double check Hue is pointing to your correct Solr:

<pre><code class="bash">

[search]

solr_url=http://localhost:8983/solr/

</code></pre>

&nbsp;

Restart Hue and voila! Drag & drop widgets and build dynamic search dashboards in seconds!

[<img src="https://cdn.gethue.com/uploads/2015/03/search-only-1024x530.png" />][5]

&nbsp;

Have any questions? Feel free to contact us on [hue-user][6] or [@gethue][7]!

&nbsp;

**Note**

If you want to install the examples you could enable the [indexer][8]

<pre><code class="bash">indexer</code></pre>

\*\*

Note\*\*

The app is primarily tested on Solr Cloud mode but works on regular Solr

[1]: https://gethue.com/search-app-enhancements-explore-even-more-data/
[2]: https://gethue.com/how-to-manage-permissions-in-hue/
[3]: https://cdn.gethue.com/uploads/2015/03/hue-download.png
[4]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
[5]: https://cdn.gethue.com/uploads/2015/03/search-only.png
[6]: http://groups.google.com/a/cloudera.org/group/hue-user
[7]: https://twitter.com/gethue
[8]: https://gethue.com/analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr/
