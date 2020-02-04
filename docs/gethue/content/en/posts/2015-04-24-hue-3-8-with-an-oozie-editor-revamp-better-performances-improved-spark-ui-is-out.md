---
title: 'Hue 3.8 with an Oozie Editor revamp, better performances & improved Spark UI is out!'
author: admin
type: post
date: 2015-04-24T06:53:41+00:00
url: /hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
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
_Edit: 3.8.1 was released May 4th 2015 and is now the default version_

&nbsp;

Hi Big Data Munchers,

&nbsp;

The Hue Team is glad to release Hue 3.8 and its improved [Oozie Editor][1] and [better performances][2]!

A new <a href="https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server" target="_blank" rel="noopener noreferrer">Spark REST Job Server</a> with a [Notebook UI][3] are also appearing in a Beta version for all the eager Spark developers that would like to give it a try.

A [tarball][4] is available as well as [documentation][5] and [release notes][6]. This release is a big step forwards and comes with more than 1000 commits!

&nbsp;

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/releases/3.8.1/hue-3.8.1.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

&nbsp;

**Note**

If you built [custom apps][7], follow the [upgrade guide][8]!

&nbsp;

Here is a summary of the main improvements (got on the [3.8 blog][9] for more details):

&nbsp;

**Oozie**

<figure><a href="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor-1024x602.png"><img src="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor-1024x602.png" /></a><figcaption>New Editor (edit mode)</figcaption></figure>

Editor

  * [New look][1] and less knowledge of Oozie required
  * [Importing / exporting workflows is easier][11]
  * Workflows supports tens of [new functionalities][12]
  * Support of the new HiveServer2 and Spark Action
  * Coordinator user experience is simpler

&nbsp;

Dashboard

  * Easy way to differentiate workflows submitted manually or by coordinators
  * Sub-workflow links to corresponding workflows and logs
  * Update end time of coordinator
  * Hive jobs ids are visible

&nbsp;

See more details about the [Editor][1] and [Dashboard][13].

&nbsp;

**Stability/performance**

[<img src="https://cdn.gethue.com/uploads/2015/03/with-nginx.png" />][14]

  * [Hue HA][15]
  * [Static files caching and running with NGINX][2]
  * [Hive 1.1 support][16]
  * [Major upgrade of Django 1.6][8]
  * [Run with Apache Server][17]
  * Fixed a number of deadlocks
  * Fixed some non-standard Oracle DB issues

&nbsp;

**Search**

[<img src="https://cdn.gethue.com/uploads/2015/04/search-v2.2-1024x558.png"  />][18]

  * Regular users can now also create dashboards
  * Range & Up facet
  * 2D maps
  * Collection aliases querying
  * Multiple widgets using the same fields
  * [Enable only the Search app][19]
  * [Export and import dashboard][20]

&nbsp;

[More detailed information here...][21]

&nbsp;

**Spark Notebook (beta)**

[<img src="https://cdn.gethue.com/uploads/2015/04/notebook-1-1024x572.png"  />][22]

  * [New REST Spark Job Server][23] (beta)
  * [Notebook Web UI][3] (beta)
  * Scala, Java, Python
  * YARN cluster

&nbsp;

**Security**

[<img src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12-1024x610.png"  />][24]

  * Sensitive data redaction in logs and SQL editors (PCI)
  * [HTTPS/SSL configuration][25]
  * [Use Impala/Hive with LDAP authentication and SSL][26]
  * [HCatalog with Pig Editor and security][27]
  * [SAML 2.0 support][28]
  * [LDAP Debugging][29]
  * [Add a customized top banner][30]

&nbsp;

**HBase**

[<img src="https://cdn.gethue.com/uploads/2015/03/hbase-1024x525.png" />][31]

  * [Impersonation with or without Kerberos][32]

&nbsp;

**New ways to install Hue**

  * [EMR][33]
  * [HDP][34]
  * [On a Mac][35]
  * [Ubuntu 14.04][36]

&nbsp;

**Conferences**

It was a pleasure to present at [Lucene Solr Revolution][37] in Washington DC and [Big Data Spain][38] in Madrid.

&nbsp;

## **Next!**

&nbsp;

Next release (3.9) will mostly focus on Spark & Search and bring general improvements/feature completeness in [all the apps][39].

&nbsp;

In parallel, the design & development of Hue 4 is kicking in with the goal of becoming the equivalent of “Excel for Big Data”. A fresh new look, a unification of all the apps, wizards for ingesting data... will let you use the full platform in a single UI for fast Big Data querying and prototyping!

&nbsp;

Onwards!!

&nbsp;

As usual feel free to contribute to the project and participate on the [hue-user][40] list or [@gethue][41]!

&nbsp;

 [1]: https://gethue.com/new-apache-oozie-workflow-coordinator-bundle-editors/
 [2]: https://gethue.com/using-nginx-to-speed-up-hue-3-8-0/
 [3]: https://gethue.com/new-notebook-application-for-spark-sql
 [4]: https://cdn.gethue.com/downloads/releases/3.8.1/hue-3.8.1.tgz
 [5]: http://cloudera.github.io/hue/docs-3.8.0/index.html
 [6]: http://cloudera.github.io/hue/docs-3.8.0/release-notes/release-notes-3.8.0.html
 [7]: https://gethue.com/app-store/
 [8]: https://gethue.com/developer-guide-on-upgrading-apps-for-django-1-6/
 [9]: https://gethue.com/category/hue-3-8/
 [10]: https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor.png
 [11]: https://gethue.com/export-and-import-your-oozie-workflows/
 [12]: https://issues.cloudera.org/browse/HUE-2180
 [13]: https://gethue.com/oozie-dashboard-improvements/
 [14]: https://cdn.gethue.com/uploads/2015/03/with-nginx.png
 [15]: https://gethue.com/automatic-high-availability-with-hue-and-cloudera-manager/
 [16]: https://gethue.com/hive-1-1-and-impala-2-2-support/
 [17]: https://gethue.com/how-to-run-hue-with-the-apache-server/
 [18]: https://cdn.gethue.com/uploads/2015/04/search-v2.2.png
 [19]: https://gethue.com/solr-search-ui-only/
 [20]: https://gethue.com/export-and-import-your-search-dashboards/
 [21]: https://gethue.com/more-solr-search-dashboards-possibilities/
 [22]: https://cdn.gethue.com/uploads/2015/04/notebook-1.png
 [23]: https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server
 [24]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12.png
 [25]: https://gethue.com/configure-hue-with-https-ssl/
 [26]: https://gethue.com/how-to-use-hue-with-hive-and-impala-configured-with-ldap-authentication-and-ssl/
 [27]: https://gethue.com/how-to-use-hcatalog-with-pig-in-a-secured-cluster/
 [28]: https://gethue.com/updated-saml-2-0-support/
 [29]: https://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/#t12b
 [30]: https://gethue.com/add-a-top-banner-to-hue/
 [31]: https://cdn.gethue.com/uploads/2015/03/hbase.png
 [32]: https://gethue.com/hbase-browsing-with-doas-impersonation-and-kerberos/
 [33]: http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-hue.html
 [34]: https://gethue.com/hadoop-hue-3-on-hdp-installation-tutorial/
 [35]: https://gethue.com/start-developing-hue-on-a-mac-in-a-few-minutes/
 [36]: https://gethue.com/how-to-build-hue-on-ubuntu-14-04-trusty/
 [37]: https://gethue.com/presentation-solr-lucene-revolution-interactively-search-and-visualize-your-big-data/
 [38]: https://gethue.com/big-data-spain-2014-big-data-web-applications-for-interactive-hadoop/
 [39]: https://issues.cloudera.org/secure/IssueNavigator.jspa?mode=hide&requestId=10930
 [40]: http://groups.google.com/a/cloudera.org/group/hue-user
 [41]: https://twitter.com/gethue