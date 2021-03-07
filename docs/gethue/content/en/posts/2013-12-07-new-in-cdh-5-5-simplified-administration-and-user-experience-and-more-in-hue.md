---
title: 'New in CDH 5.5: Simplified administration and user experience and More in Hue'
author: admin
type: post
date: 2013-12-07T19:58:13+00:00
url: /new-in-cdh-5-5-simplified-administration-and-user-experience-and-more-in-hue/
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
#  - News

---
&nbsp;

CDH5.5 improves the life of the administrator with a deeper integration of Hue in Cloudera Manager and a rebase on version [3.9][1]. The setup of Hue in High Availability mode for more stability and performances was redesigned as well as the built-in monitoring. Auditing through Cloudera Navigator is now offered for better security and reporting. A lof of optimizations and user experience bumps have been added in all Hue. Here is an overview of the main improvements:

&nbsp;

### Cloudera Manager Load balancing

In just a few clicks, a built-in load balancer can be added and provide out of the box Automatic fail over to an available healthy Hue in case of crash, network or host glitch, and transparent serving of the static files for much better request performances and more slickness. The monitoring of the Hue service was improved by adding the tracking of the number of active users, requests and other statistics warning about potential health problems. (Read more [here][2]).

[<img src="https://cdn.gethue.com/uploads/2015/12/hue-cmlb-e1449521110230-1024x335.png" />][3]

### Auditing with Navigator

Hue user administration operations can now be audited and written to a configurable audit log. This then enable auditing tools like [Cloudera Navigator’s][4] to view, search, filter, and generate reports on these audited events. Most importantly, admins can easily detect when unauthorized attempts at these operations have been made, and capture the related metadata for those unauthorized attempts. (Read more [here][5]).

[<img class="size-large wp-image-3562 aligncenter" src="https://cdn.gethue.com/uploads/2015/12/navigator1-1024x361.png" />][6]

&nbsp;

<div class="itemizedlist">
</div>

&nbsp;

**Search**

Users can now search "like in Yelp" with a new live filtering applying when moving on the map. For better performances, now only the widgets that changed are being refreshed on each search. A full time mode displays the dashboard in full screen and can be set to refresh automatically every N seconds. Indexed records are editable in the UI and can link to the original document. Saved dashboards can be exported or imported directly from the UI for an easier backup or sharing. (Learn more [here][7]).

[<img class="aligncenter wp-image-2942" src="https://cdn.gethue.com/uploads/2015/08/search-full-mode-1024x504.png" />][8]

&nbsp;

&nbsp;

**Oozie**

Performances! All the dashboard jobs filtering as well as the pagination now happen in the Oozie backend. Monitoring a large number of jobs is now fast. Various features improves the Coordinator user experience, like updating the job end time, ignoring some actions. Exporting and importing workflows can now be done [directly from the UI][9] for an easier backup. (Learn more [here][10]).

[<img src="https://cdn.gethue.com/uploads/2015/08/ignore-e1449521034696.png" />][11]

**SQL**

Statistics on tables and columns can be accessed directly from the assist, as well as the top terms of a column. Hive partitions are much easier to explore with a [new editor filter][12]. Links to partitions are now always correct, as well as in strict mode.

&nbsp;

[<img class="aligncenter wp-image-2822" src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21-1024x224.png" />][13]

&nbsp;

**Spark (beta)**

The Notebook UI is still being revamped. Spark versions like 1.5 and more are supported and the YARN integration was improved. A basic R shell was added as well as the support for submitting jars or python apps. (Learn more about the [Notebook][14] and the [REST Spark Job Server Livy][15]).

[<img class="aligncenter wp-image-2984" src="https://cdn.gethue.com/uploads/2015/08/notebook-1024x505.png" />][16]

&nbsp;

**HBase**

Several impersonations issues have been fixed on the HBase side. Binary upload into cells (like pictures) are now supported as well as emptying a cell. (Read more [here][17]).

[<img class="aligncenter wp-image-2977" src="https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44-1024x491.png"  />][18]

&nbsp;

**Sentry**

Support for COLUMN scope privilege for finer grain permissions on tables has been added. The URI scope privilege is now consistent through all the app.

[<img class="aligncenter wp-image-2991" src="https://cdn.gethue.com/uploads/2015/08/sentry-multi-cols-1024x490.png" />][19]

###

###

### **Next!**

&nbsp;

The underlying work for Hue 4 is well under way. It unifies all the apps together for a nicer global user experience. In particular, this will allow you to see at the next release a next much better SQL and Notebook experience. More performances and optimizations are also in the pipeline! Onwards!

&nbsp;

 [1]: https://gethue.com/hue-3-9-with-all-its-improvements-is-out/
 [2]: https://gethue.com/automatic-high-availability-and-load-balancing-of-hue-in-cloudera-manager-with-monitoring/
 [3]: https://cdn.gethue.com/uploads/2015/12/hue-cmlb.png
 [4]: http://www.cloudera.com/content/www/en-us/documentation/enterprise/latest/topics/cn_iu_audit_arch.html
 [5]: https://gethue.com/auditing-user-administration-operations-with-hue-and-cloudera-navigator-2/
 [6]: https://cdn.gethue.com/uploads/2015/12/navigator1.png
 [7]: https://gethue.com/dynamic-search-dashboard-improvements-3/
 [8]: https://cdn.gethue.com/uploads/2015/08/search-full-mode.png
 [9]: https://gethue.com/exporting-and-importing-oozie-workflows/
 [10]: https://gethue.com/oozie-dashboard-improvements-in-hue-3-9/
 [11]: https://cdn.gethue.com/uploads/2015/08/ignore.png
 [12]: https://gethue.com/filter-sort-browse-hive-partitions-with-hues-metastore/
 [13]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21.png
 [14]: https://gethue.com/spark-notebook-and-livy-rest-job-server-improvements/
 [15]: https://gethue.com/big-data-scala-by-the-bay-interactive-spark-in-your-browser/
 [16]: https://cdn.gethue.com/uploads/2015/08/notebook.png
 [17]: https://gethue.com/improved-hbase-cell-editor-history
 [18]: https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44.png
 [19]: https://cdn.gethue.com/uploads/2015/08/sentry-multi-cols.png
