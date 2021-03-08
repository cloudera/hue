---
title: 'Hadoop Tutorial: Schedule your Hadoop jobs intuitively with the new Oozie crontab!'
author: admin
type: post
date: 2014-03-04T23:59:38+00:00
url: /hadoop-tutorial-schedule-your-hadoop-jobs-intuitively/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/78593185931/hadoop-tutorial-schedule-your-hadoop-jobs-intuitively
tumblr_gethue_id:
  - 78593185931
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

<p id="docs-internal-guid-be480bc2-8f87-c4e1-42a3-9789aa72a148">
  Hue is taking advantage of a new way to specify the frequency of a coordinator in Oozie (<a href="https://issues.apache.org/jira/browse/OOZIE-1306">OOZIE-1306</a>). Here is how to put it in practice:
</p>

&nbsp;

{{< youtube Nnzd_q6vSHU >}}

The crontab requires Oozie 4. In order to use the previous Frequency drop-down from Oozie 3, the feature can be disabled in [hue.ini][1]:

&nbsp;

<pre class="code">[oozie]

 # Use Cron format for defining the frequency of a Coordinator instead of the old frequency number/unit.

 enable_cron_scheduling=false</pre>

&nbsp;

<span>As usual feel free to comment on the</span>[<span>hue-user</span>][2] <span>list or</span>[<span>@gethue</span>][3]<span>!</span>

[1]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L589
[2]: http://groups.google.com/a/cloudera.org/group/hue-user
[3]: https://twitter.com/gethue
