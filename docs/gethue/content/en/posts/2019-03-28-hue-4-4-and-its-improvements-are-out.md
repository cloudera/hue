---
title: Hue 4.4 and its improvements are out!
author: admin
type: post
date: 2019-03-28T15:37:03+00:00
url: /hue-4-4-and-its-improvements-are-out/
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
  # - Version 4.4
  - Release

---
Hi Big Data Explorers,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 4.4! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

&nbsp;

The focus of this release was to improve the self service SQL troubleshooting and stability.

This release comes with 450 commits and 80+ bug fixes! For all the changes, check out the [release notes][2].

Go grab the tarball or [source][3], and give it a spin! And for <span style="font-weight: 400;">a quick try, '<a href="https://github.com/cloudera/hue/tree/master/tools/docker">docker pull gethue/4.4.0</a>' or open-up </span>[<span style="font-weight: 400;">demo.gethue.com</span>][4]<span style="font-weight: 400;">.</span>

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://www.dropbox.com/s/n6uvr709ng2p2j2/hue-4.4.0.tgz?dl=0" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

Here is a list of the main improvements.

&nbsp;

## <span style="font-weight: 400;">Easier Self Service Query Troubleshooting</span>

<span style="font-weight: 400;">Hue has great assistance for finding tables in the </span>[<span style="font-weight: 400;">Data Catalog</span>][5] <span style="font-weight: 400;">and getting recommendations on how to write (better) queries with the </span>[<span style="font-weight: 400;">smart autocomplete</span>][6]<span style="font-weight: 400;">, providing popular values and notifying of </span>[<span style="font-weight: 400;">dangerous operations</span>][7]<span style="font-weight: 400;">. When executing queries, however, it might be difficult to understand why they would be slow.</span>

<span style="font-weight: 400;">A new feature in 6.2 introduces a prettier display of the SQL Query Profile, which helps understand why/where the query bottlenecks are and how to optimize the query.</span>

<span style="font-weight: 400;">Example of how query plan displayed in the previous release:</span>

[<img src="https://cdn.gethue.com/uploads/2019/03/Impala_old_plan_visualization.png"/>][8]

<span style="font-weight: 400;">And what it looks like now:</span>

[<img src="https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.08.01-PM-1.png"/>][9]

<span style="font-weight: 400;">Note that on top of the much simpler visualization, tips are provided when available:</span>

[<img src="https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.13.40-PM-1.png"/>][10]

<span style="font-weight: 400;">Please read more about this feature in this </span>[<span style="font-weight: 400;">complete self-troubleshooting scenario</span>][11]<span style="font-weight: 400;">.</span>

<span style="font-weight: 400;">Additionally, one of the most requested fixes was implemented: releasing query resources after the query has finished and they are no longer needed.</span>

<span style="font-weight: 400;">First, on the </span>[<span style="font-weight: 400;">Apache Impala</span>][12] <span style="font-weight: 400;">side, the query execution status will properly say if the query is actively running ("processing" data) or just "open but finished" (meaning just "keeping" the results but not using resources).</span>

<span style="font-weight: 400;">In addition, the new parameter NUM_ROWS_PRODUCED_LIMIT will even notify Impala to truncate any query execution as soon as this maximum number of result rows has been returned. This will release resources early on large SELECT operations where only the first few rows are actually displayed (which is the primary use case in Hue).</span>

&nbsp;

## <span style="font-weight: 400;">Better compatibility with Hive in HDP</span>

<span style="font-weight: 400;">Apache Hive has typically been very innovative in the Hortonworks distribution. In upstream the support for Hive on Tez and Hive LLAP was improved. Now:</span>

[<img src="https://cdn.gethue.com/uploads/2019/02/Screen-Shot-2019-02-27-at-3.10.39-PM.png"/>][13]

<li style="font-weight: 400;">
  <span style="font-weight: 400;">The jobs will show up in Job Browser</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">The query ID is printed</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">The progress is displayed</span>
</li>

<span style="font-weight: 400;">Note that currently Hue is not officially supported in HDP. However, if you want to experiment, you can learn </span>[<span style="font-weight: 400;">how to configure Hue in HDP</span>][14] <span style="font-weight: 400;">and set it up on your own, or get help from </span>[<span style="font-weight: 400;">Cloudera Professional Services</span>][15] <span style="font-weight: 400;">to do it for you. </span>

## <span style="font-weight: 400;">Misc Improvements</span>

<span style="font-weight: 400;">More than 80 bugs were fixed to improve the supportability and stability of Hue. The full list is in the release notes but here are the top ones:</span>

<li style="font-weight: 400;">
  <a href="https://issues.cloudera.org/browse/HUE-7414"><span style="font-weight: 400;">HUE-7474</span></a><span style="font-weight: 400;"> [core] Add ability to enable/disable Hue data/file "download" options globally</span>
</li>
<li style="font-weight: 400;">
  <a href="https://issues.cloudera.org/browse/HUE-7128"><span style="font-weight: 400;">HUE-7128</span></a><span style="font-weight: 400;"> [core] Apply config ENABLE_DOWNLOAD to search dashboard</span>
</li>
<li style="font-weight: 400;">
  <a href="https://issues.cloudera.org/browse/HUE-8680"><span style="font-weight: 400;">HUE-8680</span></a><span style="font-weight: 400;"> [core] Fill in Impalad WEBUI username passwords automatically</span>
</li>
<li style="font-weight: 400;">
  <a href="https://issues.cloudera.org/browse/HUE-8585"><span style="font-weight: 400;">HUE-8585</span></a><span style="font-weight: 400;"> [useradmin] Bubbling up errors for Add Sync Ldap Users</span>
</li>
<li style="font-weight: 400;">
  <a href="https://issues.cloudera.org/browse/HUE-8690"><span style="font-weight: 400;">HUE-8690</span></a><span style="font-weight: 400;"> [backend] Fix Hue allows unsigned SAML assertions</span>
</li>
<li style="font-weight: 400;">
  <a href="https://issues.cloudera.org/browse/HUE-8140"><span style="font-weight: 400;">HUE-8140</span></a><span style="font-weight: 400;"> [editor] Improve multi-statement execution</span>
</li>
<li style="font-weight: 400;">
  <a href="https://issues.cloudera.org/browse/HUE-8662"><span style="font-weight: 400;">HUE-8662</span></a><span style="font-weight: 400;"> [core] Fix missing static URLs</span>
</li>

&nbsp;

<span style="font-weight: 400;">In addition, the </span>[<span style="font-weight: 400;">Hue Docker image</span>][16] <span style="font-weight: 400;">was simplified, so that it is easier to quickly get started and play/test the latest features.</span>

[<img src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png"/>][17]

<span style="font-weight: 400;">Last but not least, the </span>[<span style="font-weight: 400;">upstream</span>][18] <span style="font-weight: 400;">and </span>[<span style="font-weight: 400;">downstream</span>][19] <span style="font-weight: 400;">documentation just got the first pass of a revamp, with a better table of contents, restyling, and updated instructions. In particular, on the upstream docs, reporting issues or sending a suggestion is one click away via GitHub, so feel free to send some pull requests!</span>

<span style="font-weight: 400;">Thank you to everybody using the product and who contributed to this release. Now off to the next one!</span>

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][20] list or [@gethue][21]!

&nbsp;

Onwards!

&nbsp;

&nbsp;

&nbsp;

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: http://cloudera.github.io/hue/latest/releases/release-notes-4.4.0/index.html
 [3]: https://github.com/cloudera/hue/archive/release-4.4.0.zip
 [4]: http://demo.gethue.com/
 [5]: https://blog.cloudera.com/blog/2018/06/new-in-cloudera-5-15-simplifying-the-end-user-data-catalog-for-the-self-service-analytic-database/
 [6]: https://blog.cloudera.com/blog/2018/02/new-in-cloudera-5-14-query-assistance-improvements-and-adls-integration-for-the-self-service-analytic-database/
 [7]: https://blog.cloudera.com/blog/2017/08/new-in-cloudera-enterprise-5-12-hue-4-interface-and-query-assistant/
 [8]: https://cdn.gethue.com/uploads/2019/03/Impala_old_plan_visualization.png
 [9]: https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.08.01-PM-1.png
 [10]: https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.13.40-PM-1.png
 [11]: https://gethue.com/self-service-impala-sql-query-troubleshooting/
 [12]: https://impala.apache.org/
 [13]: https://cdn.gethue.com/uploads/2019/02/Screen-Shot-2019-02-27-at-3.10.39-PM.png
 [14]: https://gethue.com/configure-ambari-hdp-with-hue/
 [15]: https://www.cloudera.com/about/services-and-support/professional-services.html
 [16]: https://gethue.com/hue-in-docker/
 [17]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png
 [18]: http://cloudera.github.io/hue/docs-4.4.0/
 [19]: https://www.cloudera.com/documentation/enterprise/latest/topics/hue.html
 [20]: http://groups.google.com/a/cloudera.org/group/hue-user
 [21]: https://twitter.com/gethue
