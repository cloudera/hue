---
title: Hue 3.9 with some general overall improvements is out!
author: admin
type: post
date: 2015-08-24T16:45:28+00:00
url: /hue-3-9-with-all-its-improvements-is-out/
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
  - Release

---
Hi Big Data Aficionados,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 3.9! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

The focus of this release was to improve the experience everywhere (no new app were added) and the stability. More than [700 commits][2] on top of [3.8][3] are in and some apps like the Notebook Editor and Spark Job Server got a serious lift! Go grab the [tarball release][4] and give it a spin!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/releases/3.9.0/hue-3.9.0.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

You can find below a detailed description of what happened. For all the changes, check out the [release notes][5] or the [documentation][6].

&nbsp;

### Tutorials

[Explore San Francisco Bike share data with a dynamic visual dashboard][7]

[Build a real time Tweet dashboard with Search and Spark][8]

&nbsp;

### Main improvements

&nbsp;

**Spark (beta)**

[<img class="aligncenter wp-image-2984" src="https://cdn.gethue.com/uploads/2015/08/notebook-1024x505.png" />][9]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Revamp of Notebook UI
    </li>
    <li class="listitem">
      Support for closing session and specifying Spark properties
    </li>
    <li class="listitem">
      Support for Spark 1.3, 1.4, 1.5
    </li>
    <li class="listitem">
      Impersonation with YARN
    </li>
    <li class="listitem">
      Support for R shell
    </li>
    <li class="listitem">
      Support for submitting jars or python apps
    </li>
  </ul>
  
  <p>
    Learn more about the <a href="https://gethue.com/spark-notebook-and-livy-rest-job-server-improvements/">Notebook</a> and the <a href="https://gethue.com/big-data-scala-by-the-bay-interactive-spark-in-your-browser/">REST Spark Job Server Livy</a>.
  </p>
</div>

&nbsp;

**Search**

[<img class="aligncenter wp-image-2942" src="https://cdn.gethue.com/uploads/2015/08/search-full-mode-1024x504.png" />][10]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Live filtering when moving on the map
    </li>
    <li class="listitem">
      Refresh only widgets that changed, refresh every N seconds
    </li>
    <li class="listitem">
      Edit document
    </li>
    <li class="listitem">
      Link to original document
    </li>
    <li class="listitem">
      Export/import saved dashboards
    </li>
    <li class="listitem">
      Share dashboards
    </li>
    <li class="listitem">
      Save and reload the full query search definition
    </li>
    <li class="listitem">
      Fixed or rolling time window filtering
    </li>
    <li class="listitem">
      Marker clustering on Leaflet Map widget
    </li>
    <li class="listitem">
      Support 2-letter country code in gradient map widget
    </li>
    <li class="listitem">
      Full mode Player display
    </li>
    <li class="listitem">
      <a href="https://gethue.com/enhance-search-results/">Simpler Mustache integration to enhance your result style</a>
    </li>
    <li class="listitem">
      Big IDs support
    </li>
    <li class="listitem">
      Preview of nested analytics facets
    </li>
  </ul>
  
  <p>
    <a href="https://gethue.com/dynamic-search-dashboard-improvements-3/">Read more in this post...</a>
  </p>
</div>

&nbsp;

**Stability/performance**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Fix deadlock fetching Thrift clients and waiting for Thrift connections
    </li>
    <li class="listitem">
      New set of integrations tests
    </li>
    <li class="listitem">
      Add optional /desktop/debug/check_config JSON response
    </li>
    <li class="listitem">
      MariaDB support
    </li>
    <li class="listitem">
      Configuration check to confirm that MySql engine is InnoDB
    </li>
    <li class="listitem">
      Faster Home page
    </li>
    <li class="listitem">
      Series of Oracles and DB migration fixes
    </li>
  </ul>
</div>

&nbsp;

**Security**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Explicitly set cipher list to Mozilla recommendation
    </li>
    <li class="listitem">
      Fix uploading large files to a kerberized HTTPFS
    </li>
    <li class="listitem">
      Set X-Frame-Options to all responses
    </li>
    <li class="listitem">
      <a href="https://gethue.com/configuring-hue-multiple-authentication-backends-and-ldap/">Support multiple authentication backends in order of priority</a>
    </li>
    <li class="listitem">
      Add global ssl_validate config option
    </li>
    <li class="listitem">
      Default to using secure session cookies if HTTPS is enabled
    </li>
  </ul>
</div>

&nbsp;

**Oozie**

[<img src="https://cdn.gethue.com/uploads/2015/08/ignore.png" />][11]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Filter dashboard jobs in the backend
    </li>
    <li class="listitem">
      <a href="https://gethue.com/exporting-and-importing-oozie-workflows/">Integrate the import/export of Workflows, Coordinators and Bundles into the UI</a>
    </li>
    <li class="listitem">
      Paginate Coordinator dashboard tables
    </li>
    <li class="listitem">
      Paginate Coordinator actions
    </li>
    <li class="listitem">
      Update end time of running coordinator
    </li>
    <li class="listitem">
      Series of improvements to the Editor
    </li>
  </ul>
  
  <p>
    <a href="https://gethue.com/oozie-dashboard-improvements-in-hue-3-9/">Read more in this post...</a>
  </p>
</div>

&nbsp;

**SQL**

[<img class="aligncenter wp-image-2822" src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21-1024x224.png" />][12]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Table / column statistics and Top terms available in assist
    </li>
    <li class="listitem">
      Select <span class="emphasis">default</span> as first assist database if available
    </li>
    <li class="listitem">
      <a href="https://gethue.com/filter-sort-browse-hive-partitions-with-hues-metastore/">Offer to filter partition on the list of partitions page</a>
    </li>
    <li class="listitem">
      Partitions names and links are now always correct
    </li>
    <li class="listitem">
      Allow sample on partitioned tables in strict mode
    </li>
  </ul>
</div>

&nbsp;

**HBase**

[<img class="aligncenter wp-image-2977" src="https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44-1024x491.png"  />][13]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Upload binary into cells
    </li>
    <li class="listitem">
      Allow to empty a cell
    </li>
  </ul>
  
  <p>
    <a href="https://gethue.com/improved-hbase-cell-editor-history">Read more in this post...</a>
  </p>
</div>

&nbsp;

**Sentry**

[<img class="aligncenter wp-image-2991" src="https://cdn.gethue.com/uploads/2015/08/sentry-multi-cols-1024x490.png" />][14]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Better support of URI scope privilege
    </li>
    <li class="listitem">
      Support COLUMN scope privilege for finer grain permissions on tables
    </li>
    <li class="listitem">
      Support HA
    </li>
    <li class="listitem">
      Easier navigation between sections
    </li>
    <li class="listitem">
      Support new sentry.hdfs.integration.path.prefixes hdfs-site.xml property
    </li>
  </ul>
</div>

&nbsp;

**Indexer**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Directly upload configurations without requiring the solrctl command
    </li>
  </ul>
</div>

&nbsp;

**ZooKeeper**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Creation of a lib for easily pulling or editing ZooKeeper information
    </li>
  </ul>
</div>

&nbsp;

**Pig**

[<img class="aligncenter wp-image-2902" src="https://cdn.gethue.com/uploads/2015/08/pig-editor-declare-1024x514.png" />][15]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Support %default parameters in the submission popup
    </li>
    <li class="listitem">
      Do not show %declare parameters in the submission popup
    </li>
    <li class="listitem">
      Automatically generate hcat auth credentials
    </li>
  </ul>
</div>

&nbsp;

**Sqoop**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Support Kerberos authentication
    </li>
  </ul>
</div>

&nbsp;

### Conferences

It was a pleasure to present at Big Data Budapest Meetup, [Big Data Amsterdam][16], [Hadoop Summit San Jose][17] and [Big Data LA][8].

&nbsp;

### New distributions

  * [Docker image of HUE filebrowser for IBM Analytics for Apache Service][18]
  * [Big Data IBM insights][19]
  * [Pivotal HD3.0][20]
  * [HDP update][21]

&nbsp;

### Team Retreat

Hummus and yogurt were at the menu in [Israel][22]!

&nbsp;

## **Next!**

&nbsp;

Next release (3.10) will focus on making the v1 of the Spark Notebook and adding simpler Solr indexing on top of the general improvements.

Hue 4 design is also getting kicked in with the goal of becoming the equivalent of “Excel for Big Data”. A fresh new look, a unification of all the apps, wizards for ingesting data... will let you use the full platform (Ingest, Spark, SQL, Search) in a single UI for fast Big Data querying and prototyping!

&nbsp;

Onwards!

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][23] list or [@gethue][24]!

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://github.com/cloudera/hue/compare/release-3.8.0...release-3.9.0
 [3]: https://gethue.com/hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
 [4]: https://cdn.gethue.com/downloads/releases/3.9.0/hue-3.9.0.tgz
 [5]: http://cloudera.github.io/hue/docs-3.9.0/release-notes/release-notes-3.9.0.html
 [6]: http://cloudera.github.io/hue/docs-3.9.0/index.html
 [7]: https://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/
 [8]: https://gethue.com/big-data-day-la-solr-search-with-spark-for-big-data-analytics-in-action-with-hue/
 [9]: https://cdn.gethue.com/uploads/2015/08/notebook.png
 [10]: https://cdn.gethue.com/uploads/2015/08/search-full-mode.png
 [11]: https://cdn.gethue.com/uploads/2015/08/ignore.png
 [12]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21.png
 [13]: https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44.png
 [14]: https://cdn.gethue.com/uploads/2015/08/sentry-multi-cols.png
 [15]: https://cdn.gethue.com/uploads/2015/08/pig-editor-declare.png
 [16]: https://gethue.com/harness-the-power-of-spark-and-solr-in-hue-big-data-amsterdam-v-2-0-meeetup/
 [17]: https://gethue.com/hadoop-summit-san-jose-2015-interactively-query-and-search-your-big-data/
 [18]: https://github.com/ibmecod/bluemix-hue-filebrowser
 [19]: https://gethue.com/how-to-install-hue-3-on-ibm-biginsights-4-0-to-explore-big-data/
 [20]: https://gethue.com/install-hue-3-on-pivotal-hd-3-0/
 [21]: https://gethue.com/hadoop-hue-3-on-hdp-installation-tutorial/
 [22]: https://gethue.com/team-retreat-in-israel/
 [23]: http://groups.google.com/a/cloudera.org/group/hue-user
 [24]: https://twitter.com/gethue