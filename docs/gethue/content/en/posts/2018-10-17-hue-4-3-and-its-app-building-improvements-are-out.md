---
title: Hue 4.3 and its Analytics and Django improvements are out!
author: admin
type: post
date: 2018-10-17T03:07:26+00:00
url: /hue-4-3-and-its-app-building-improvements-are-out/
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
  - Release

---
Hi Big Data Explorers,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 4.3! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

&nbsp;

The focus of this release was a big refresh to upgrade [Django][2] to 1.11, the latest Python 2.7 compatible version at the time.

It contains a log of improvements for the SQL [Editor][3] variables and catalog, as well as for the [Dashboarding][4]. It also prepares the ground for multi cluster support ([HUE-8330][5]) and building data apps more easily.

This [release][6] comes with 900 commits and 200+ bug fixes! Go grab the tarball and give it a spin!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://www.dropbox.com/s/bv2al5bvc7uwgls/hue-4.3.0.tgz?dl=0" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

Here is a list of the main improvements. For all the changes, check out the [release notes][7] and for <span style="font-weight: 400;">a quick try open-up </span>[<span style="font-weight: 400;">demo.gethue.com</span>][8]<span style="font-weight: 400;">.</span>

# Summary

  * Upgraded core backend to Django 1.11 and now requires Python 2.7.x ([doc][9] for installing Python 2.7 on Centos/RHEL 6).
  * [Language Reference built-in, Column Sampling, black theme for Editor][10]

    [<img src="https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif"/>][11]
  * [Simplifying the end user Data Catalog search][12]

    [<img src="https://cdn.gethue.com/uploads/2018/05/Top_Search_Drag.gif"/>][13]
  * [SQL editor variables][14]

    [<img src="https://cdn.gethue.com/uploads/2018/04/variables_multi.png"/>][15]
  * [Improved SQL Exploration][16]

    [<img src="https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif"/>][17]
  * [Get a mode to allow easy profiling of requests][18]
  * [Finer grain privileges in the Sentry App][19]
  * [Improved dashboards layouts][20]

    [<img src="https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dnd.gif"/>][21]
  * [Improved job scheduling monitoring][22]
  * [Improved Oozie Workflow Graph display][23]

&nbsp;

Onwards!

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][24] list or [@gethue][25]!

&nbsp;

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://www.djangoproject.com/
 [3]: https://gethue.com/sql-editor/
 [4]: https://gethue.com/search-dashboards/
 [5]: https://issues.cloudera.org/browse/HUE-8330
 [6]: https://github.com/cloudera/hue/commits/release-4.3.0
 [7]: http://cloudera.github.io/hue/docs-4.3.0/release-notes/release-notes-4.3.0.html
 [8]: http://demo.gethue.com/
 [9]: http://cloudera.github.io/hue/latest/admin-manual/manual.html#centosoracleredhat-6x
 [10]: https://gethue.com/additional-sql-improvements-in-hue-4-3/
 [11]: https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif
 [12]: https://gethue.com/simplifying-the-end-user-data-catalog-search/
 [13]: https://cdn.gethue.com/uploads/2018/05/Top_Search_Drag.gif
 [14]: https://gethue.com/sql-editor-variables/
 [15]: https://cdn.gethue.com/uploads/2018/04/variables_multi.png
 [16]: https://gethue.com/improved-sql-exploration-in-hue-4-3/
 [17]: https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif
 [18]: https://gethue.com/get-a-mode-to-allow-easy-profiling-of-requests/
 [19]: https://gethue.com/finer-grain-privileges/
 [20]: http://Improved dashboards layouts
 [21]: https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dnd.gif
 [22]: https://gethue.com/improved-job-scheduling-monitoring/
 [23]: https://gethue.com/improved-oozie-workflow-graph-display-in-hue-4-3/
 [24]: http://groups.google.com/a/cloudera.org/group/hue-user
 [25]: https://twitter.com/gethue
