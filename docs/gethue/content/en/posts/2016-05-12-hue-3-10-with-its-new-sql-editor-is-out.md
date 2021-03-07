---
title: Hue 3.10 with its new SQL Editor is out!
author: admin
type: post
date: 2016-05-12T20:08:49+00:00
url: /hue-3-10-with-its-new-sql-editor-is-out/
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
sf_related_articles:
  - 1
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
categories:
  - Release

---
Hi Big Data Aficionados,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 3.10! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

The focus of this release was to prepared the core of a new SQL user experience and the performances. More than [2000 commits][2] on top of [3.9][3] went in! Go grab the [tarball release][4] and give it a spin!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/releases/3.10.0/hue-3.10.0.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

You can find below a detailed description of what happened. For all the changes, check out the [release notes][2] or the [documentation][5].

An upcoming series of video tutorials with more details is also on the way!

## SQL Editor

[<img src="https://cdn.gethue.com/uploads/2014/03/sql-editor-1024x535.png" />][6]

  * Full revamped
  * [Support of any type of SQL, integrate with other SQL databases][7]
  * Query: Multi queries, Search and Replace, live history, fold, format, table assist
  * Results: Fixed headers, scroll to columns, charting, download in Excel/CSV
  * [Autocomplete of values, nested types][8]

Read more [about it here...][9]

## SQL Browser

[<img src="https://cdn.gethue.com/uploads/2016/04/sql-browser-1024x536.png" />][10]

  * [Revamped UI for speed, statistics display and ease of use][11]
  * Single page app
  * Optimized for large number of databases and tables

## Home

[<img src="https://cdn.gethue.com/uploads/2016/05/home2-1024x502.png"  />][12]

  * Folder and directories
  * Share document for collaboration
  * Export and import documents

Read more [about it here...][13]

&nbsp;

## Spark

[<img src="https://cdn.gethue.com/uploads/2015/10/notebook-october-1024x512.png" />][14]

  * Because of its success, Livy is been moved to a dedicated repository: <https://github.com/cloudera/livy>
  * [How to use the Livy Spark REST Job Server API for submitting batch jar, Python and Streaming Job][15]
  * [How to use the Livy Spark REST Job Server API for sharing Spark RDDs and contexts][16]
  * [How to use the Livy Spark REST Job Server API for doing some interactive Spark with curl][17]

## Search

[<img src="https://cdn.gethue.com/uploads/2014/04/search-grid-plot-1024x331.png" />][18]

  * [Hue supports Solr Suggesters and makes your data easier to search! Suggester assists the user by proposing an auto-completable list of queries][19]
  * Result in the Grid Widget can be plotted like in the SQL editor. This is ideal for clicking visualizing the rows returned by the search query.

## Security & Scalability

[<img src="https://cdn.gethue.com/uploads/2016/02/meta-quick.png" />][20]

  * [Performance tuning][21]
  * Solr Sentry privilege edition
  * A timeout now logs out inactive user after `idle_session_timeout seconds`
  * Optional custom security splash screen at log-in with `login_splash_html`
  * [TLS certificate chain][22] support for HUE
  * SAML
      * Password for the key_file was introduced with `key_file_password`
      * Customize your xmlsec1 binary by changing `xmlsec_binary`
      * Customize your [SAML username mapping][23]. It also supports syncing groups on login
  * [Getting started with Hue in 1 minute with Docker][24]
  * [LDAP or PAM pass-through authentication with Hive or Impala and Impersonation][25]
  * [Storing passwords in file script rather than in hue.ini configuration][26]

## Oozie

[<img src="https://cdn.gethue.com/uploads/2016/04/hue-workflows-1024x521.png" />][27]

  * External Workflow Graph: This feature enables us to see the graph for workflows submitted form File-browser as well as the ones submitted from CLI.
  * Dryrun Oozie job: The <tt>dryrun</tt> option tests running a workflow/coordinator/bundle job with given properties and does not create the job.
  * Timezone improvements: All the times on the dashboard are now defaulted to browser timezone and submitting a coordinator/bundle no longer need UTC times.
  * Emailing automatically on failure: Each kill node now embeds an optional email action. Edit a kill node to insert a custom message if case it gets called.

Read more [about it here...][28]

## HDFS

[<img src="https://cdn.gethue.com/uploads/2014/04/fb-summary-icon.png" />][29]

Right click on a file or directory to access their disk space consumed, quotas and number of directories and files.

####

## Tutorials

[<img src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-22.37.38-1024x326.png" />][30]

  * [Bay Area bike share analysis with the Hadoop Notebook and Spark & SQL][31] Part 1
  * [Bay Area bike share analysis with the Hadoop Notebook and Spark & SQL][32] Part 2
  * [Use the Shell Action in Oozie][33]
  * [Use the Spark Action in Oozie][34]

## Conferences

[<img src="https://cdn.gethue.com/uploads/2015/11/IMG_5690-1024x768.jpg"  />][35]

It was a pleasure to present at the Spark Summit, Solr SF and Big Data Scala:

  * [Spark Summit Europe: Building a REST Job Server for interactive Spark as a service][36]
  * [Solr SF Meetup: Interactively Search and Visualize Your Big Data][37]
  * [Big Data Scala by the Bay: Interactive Spark in your Browser][38]

## Team Retreats

[<img src="https://cdn.gethue.com/uploads/2015/12/2015-11-20-11.50.09-1024x768.jpg"  />][39]

  * [Vietnam][40] with a bustling Ho Chi Minh City, banh mis, pho bos, warm waters, gorgeous weather.
  * [Spain beaches and Amsterdam][41].
  * Tulips and beers were great [in Bloemendaal][42] in Holland.

&nbsp;

## **Next!**

Next iteration (Hue 3.11, estimated for end of Q3) will focus on SQL improvements, job monitoring and Cloud integration.

Hue 4 design is also continuing, with the goal of becoming the equivalent of “Excel for Big Data”. A fresh new look, a unification of all the apps, wizards for ingesting data... will let you use the full platform (SQL, Search, Spark, Ingest) in a single UI for fast Big Data querying and prototyping!

&nbsp;

Onwards!

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][43] list or [@gethue][44]!

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: http://cloudera.github.io/hue/docs-3.10.0/release-notes/release-notes-3.10.0.html
 [3]: https://gethue.com/hue-3-9-with-all-its-improvements-is-out/
 [4]: https://cdn.gethue.com/downloads/releases/3.10.0/hue-3.10.0.tgz
 [5]: http://cloudera.github.io/hue/docs-3.10.0/index.html
 [6]: https://cdn.gethue.com/uploads/2014/03/sql-editor.png
 [7]: https://gethue.com/custom-sql-query-editors/
 [8]: https://gethue.com/assist-and-autocomplete-improvements/
 [9]: https://gethue.com/new-sql-editor/
 [10]: https://cdn.gethue.com/uploads/2016/04/sql-browser.png
 [11]: https://gethue.com/browsing-hive-tables-data-and-metadata-is-getting-faster-and-prettier/
 [12]: https://cdn.gethue.com/uploads/2016/05/home2.png
 [13]: https://gethue.com/introducing-hues-new-home-page/
 [14]: https://cdn.gethue.com/uploads/2015/10/notebook-october.png
 [15]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-submitting-batch-jar-python-and-streaming-spark-jobs/
 [16]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-sharing-spark-rdds-and-contexts/
 [17]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark-2-2/
 [18]: https://cdn.gethue.com/uploads/2014/04/search-grid-plot.png
 [19]: https://cwiki.apache.org/confluence/display/solr/Suggester
 [20]: https://cdn.gethue.com/uploads/2016/02/meta-quick.png
 [21]: https://gethue.com/performance-tuning/
 [22]: https://issues.cloudera.org/browse/HUE-2582
 [23]: https://github.com/romainr/custom_saml_backend
 [24]: https://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/
 [25]: https://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/
 [26]: https://gethue.com/storing-passwords-in-script-rather-than-hue-ini-files/
 [27]: https://cdn.gethue.com/uploads/2016/04/hue-workflows.png
 [28]: https://gethue.com/oozie-improvements-in-hue-3-10/
 [29]: https://cdn.gethue.com/uploads/2014/04/fb-summary-icon.png
 [30]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-22.37.38.png
 [31]: https://gethue.com/bay-area-bike-share-analysis-with-the-hadoop-notebook-and-spark-sql/
 [32]: https://gethue.com/bay-area-bike-share-data-analysis-with-spark-notebook-part-2/
 [33]: https://gethue.com/use-the-shell-action-in-oozie/
 [34]: https://gethue.com/use-the-spark-action-in-oozie/
 [35]: https://cdn.gethue.com/uploads/2015/11/IMG_5690.jpg
 [36]: https://gethue.com/spark-summit-europe-building-a-rest-job-server-for-interactive-spark-as-a-service/
 [37]: https://gethue.com/solr-sf-meetup-interactively-search-and-visualize-your-big-data/
 [38]: https://gethue.com/big-data-scala-by-the-bay-interactive-spark-in-your-browser/
 [39]: https://cdn.gethue.com/uploads/2015/12/2015-11-20-11.50.09.jpg
 [40]: https://gethue.com/team-retreat-in-vietnam/
 [41]: https://gethue.com/team-retreat-in-spain-amsterdam/
 [42]: https://gethue.com/mini-team-retreat-in-bloemendaal/
 [43]: http://groups.google.com/a/cloudera.org/group/hue-user
 [44]: https://twitter.com/gethue
