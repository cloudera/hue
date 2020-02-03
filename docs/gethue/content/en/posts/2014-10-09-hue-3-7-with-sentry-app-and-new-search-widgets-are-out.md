---
title: Hue 3.7 with Sentry App and new Search widgets is out!
author: admin
type: post
date: 2014-10-09T17:09:01+00:00
url: /hue-3-7-with-sentry-app-and-new-search-widgets-are-out/
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
  - Release

---
Hi Big Data Surfers,

The Hue Team is glad to release Hue 3.7 and its new [Sentry App][1] and improved [Search App][2]!

A [tarball][3] is available as well as [documentation][4] and [release notes][5]. On top of shipping a brand new app, this release is particularly feature-packed. This is possible with all the good feedback and requests that we are receiving!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important;" href="https://cdn.gethue.com/downloads/releases/3.7.1/hue-3.7.1.tgz" target="_blank" rel="noopener noreferrer"><span class="text">Download 3.7.1 tarball</span></a>
</p>

&nbsp;

Here is a list of the main improvements:

**Security**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-sentry-1024x541.png" />][6]

  * New Sentry App
  * Bulk edit roles and privileges
  * Visualize/edit roles and privileges on a database tree
  * WITH GRANT OPTION support
  * Impersonate a user to see which databases and table he can see
  * [More details here...][1]

&nbsp;

**Search**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1-1024x596.png"  />][7]

  * Three new widgets 
      * Heatmap
      * Tree
      * Marker Map
  * Field Analysis
  * Exclude Facets
  * [More details here…][2]

&nbsp;

**Oozie**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-oozie-1024x579.png" />][8]

  * Bulk suspend/kill/resume actions on dashboards
  * Faster dashboards
  * Rerun failed coordinator instances in bulk
  * [More details here…][9]

&nbsp;

**Job Browser**

Kill application button for YARN

&nbsp;

**File Browser**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-fb-1024x571.png" />][10]

  * ACLs Edition
  * Drag & Drop upload
  * Navigation History
  * Simpler interface
  * [More details here…][11]

&nbsp;

**HBase**

Kerberos support. Next step will be impersonation!

&nbsp;

**Indexer**

Pickup the configured Zookeeper and give a hint if pointing to the wrong Solr. Useful for [installing examples][12] in one click.

&nbsp;

**Hive / Impala**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-impala-charts-1024x573.png" />][13]

  * LDAP passthrough
  * [SSL encryption with HiveServer2][14]
  * New graphs
  * [Automatic query timeout][15]

&nbsp;

**SDK**

We are also trying to make the Hue project easier to develop:

  * [Code reviews][16]
  * [Run tests][17]
  * [Ubuntu 14.04 support][18]
  * Configure with [any Hadoop][19]

&nbsp;

&nbsp;

**What’s next?**

Next planned features will bring a new and elegant Oozie Workflow Editor, faster performances and High Availability (HA), a surprise app, a simpler Spark App, more integration with Sentry and Search, and tons of polishing and ironing.

As usual, feel free to comment and send feedback on the [hue-user][20] list or [@gethue][21]!

 [1]: https://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/
 [2]: https://gethue.com/search-app-enhancements-explore-even-more-data/
 [3]: https://cdn.gethue.com/downloads/releases/3.7.1/hue-3.7.1.tgz
 [4]: http://cloudera.github.io/hue/docs-3.7.0/index.html
 [5]: http://cloudera.github.io/hue/docs-3.7.0/release-notes/release-notes-3.7.0.html
 [6]: https://cdn.gethue.com/uploads/2014/10/hue-sentry.png
 [7]: https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1.png
 [8]: https://cdn.gethue.com/uploads/2014/10/hue-oozie.png
 [9]: https://gethue.com/improved-oozie-dashboard-bulk-manipulate-your-jobs/
 [10]: https://cdn.gethue.com/uploads/2014/10/hue-fb.png
 [11]: https://gethue.com/file-browser-enhancements-hdfs-operations-made-easy/
 [12]: https://gethue.com/hadoop-tutorial-kerberos-security-and-sentry-authorization-for-solr-search-app/
 [13]: https://cdn.gethue.com/uploads/2014/10/hue-impala-charts.png
 [14]: https://gethue.com/hadoop-tutorial-ssl-encryption-between-hue-and-hive/
 [15]: https://gethue.com/hadoop-tutorial-hive-and-impala-queries-life-cycle/
 [16]: https://gethue.com/rbtools-example-how-do-easily-do-code-reviews-with-review-board/
 [17]: https://gethue.com/tutorial-how-to-run-the-hue-integration-tests/
 [18]: https://gethue.com/how-to-build-hue-on-ubuntu-14-04-trusty/
 [19]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [20]: http://groups.google.com/a/cloudera.org/group/hue-user
 [21]: https://twitter.com/gethue