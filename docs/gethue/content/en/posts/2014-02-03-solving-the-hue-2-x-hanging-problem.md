---
title: Solving the Hue 2.X hanging problem
author: admin
type: post
date: 2014-02-03T17:25:00+00:00
url: /solving-the-hue-2-x-hanging-problem/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/75493515493/solving-the-hue-2-x-hanging-problem
tumblr_gethue_id:
  - 75493515493
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
slide_template:
  - default
categories:

---
In the Hue versions before [3][1], Hue is sometimes getting slow and “stuck”. To fix this problem, it is recommended to switch Hue to use the CherryPy server instead of Spawning. In the [hue.ini][2] or the Hue Safety Valve in CM, enter:

<pre><code class="bash">[desktop]

use_cherrypy_server = true

</code></pre>

**Cause**:

Most of the time some timeout/Thrift errors can be seen in the Hue logs (/logs page). These errors are due to Beeswax crashing or being very slow and blocking all the requests as the Spawing Server is not perfectly [greenified][3] in Hue 2 (the unique Thread is blocked in the RPC IO call). This is fixed in CDH5 and improved in CDH4.5 by switching to [HiveServer2][4].

CherryPy use 10 threads which is a good default. For more performance, 30 can be used.

Note: switching to CherryPy will disable the Shell Application but this one is replaced by the [HBase Browser][5], [Sqoop2 Editor][6] and [Pig Editor][7] applications.

 [1]: http://gethue.tumblr.com/post/69115755563/hue-3-5-and-its-redesign-are-out
 [2]: https://github.com/cloudera/hue/blob/branch-2.5/desktop/conf.dist/hue.ini#L45
 [3]: http://eventlet.net/
 [4]: http://gethue.tumblr.com/post/64916325309/hadoop-tutorial-hive-query-editor-with-hiveserver2-and
 [5]: http://gethue.tumblr.com/post/59071544309/the-web-ui-for-hbase-hbase-browser
 [6]: http://gethue.tumblr.com/post/63064228790/move-data-in-out-your-hadoop-cluster-with-the-sqoop
 [7]: http://gethue.tumblr.com/post/51559235973/tutorial-apache-pig-editor-in-hue-2-3
