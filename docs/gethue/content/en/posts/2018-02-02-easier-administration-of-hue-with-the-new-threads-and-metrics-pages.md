---
title: Easier administration of Hue with the new Threads and Metrics pages
author: admin
type: post
date: 2018-02-02T01:09:46+00:00
url: /easier-administration-of-hue-with-the-new-threads-and-metrics-pages/
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

---
<span style="font-weight: 400;">If you are an Administrator this post is for you! (in the contrary, the </span>[<span style="font-weight: 400;">SQL Editor</span>][1]<span style="font-weight: 400;"> would be a great starting point).</span>

<span style="font-weight: 400;">In our last post we talked about </span>[<span style="font-weight: 400;">how to optimally configure Hue with the Analytic Database engines Impala and Hive.</span>][2] <span style="font-weight: 400;">This post describes how troubleshooting is getting easier for administrators, with the new Threads and Metrics pages. Those are in the Administration section, which can be accessed from the user menu:</span>

<p style="text-align: center;">
  <a href="https://cdn.gethue.com/uploads/2018/02/Admin_menu.png"><img class="alignnone size-medium wp-image-5273" src="https://cdn.gethue.com/uploads/2018/02/Admin_menu.png"/></a>
</p>

<p style="text-align: center;">
  <span style="font-weight: 400;">The Administration page link when logged-in as an admin</span>
</p>

&nbsp;

**Threads**

<span style="font-weight: 400;">Threads page can be very helpful in debugging purposes. It includes a </span><span style="font-weight: 400;">daemonic thread and the thread objects serving concurrent requests. The host name, thread name identifier and current stack frame of each are displayed. Those are useful when Hue "hangs", sometimes in case of a request too CPU intensive.</span>

<p style="text-align: center;">
  <a href="https://cdn.gethue.com/uploads/2018/01/hue_metric_page.png"><img class="alignnone size-full wp-image-5252" src="https://cdn.gethue.com/uploads/2018/01/hue_metric_page.png"/></a>
</p>

&nbsp;

<span style="font-weight: 400;">There is also a REST API to get the dump of Threads using ‘desktop/debug/threads’</span>

&nbsp;

**Metrics**

<span style="font-weight: 400;">Hue uses the </span>[<span style="font-weight: 400;">PyFormance</span>][3] <span style="font-weight: 400;">Python library to collect the metrics. These metrics are represented as gauge, counters, meter, rate of events over time, histogram, statistical distribution of values. A REST API endpoint ‘/desktop/metrics/’ to get all the metrics dump as json is also exposed. </span>

<span style="font-weight: 400;">The below metrics of most concern to us are displayed on the page</span>

<li style="font-weight: 400;">
  <span style="font-weight: 400;">requests.active</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">requests.exceptions</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">requests.response-time</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">threads.daemon</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">threads.total</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">users</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">users.active</span>
</li>

One of the most useful ones are the percentiles of response time of requests and the count of active users.

<span style="font-weight: 400;">Admins can either filter a particular property in all the metrics:</span>

[<img class="wp-image-5272 aligncenter" src="https://cdn.gethue.com/uploads/2018/02/Metrics_filter.png"/>][4]

<span style="font-weight: 400;">Or select a particular metric for all properties:</span>

[<img class="wp-image-5267 aligncenter" src="https://cdn.gethue.com/uploads/2018/02/Metrics_selected_page.png"/>][5]

&nbsp;

 [1]: https://gethue.com/sql-editor/
 [2]: https://gethue.com/how-to-optimally-configure-your-analytic-database-for-high-availability-with-hue-and-other-sql-clients/
 [3]: https://pyformance.readthedocs.io/
 [4]: https://cdn.gethue.com/uploads/2018/02/Metrics_filter.png
 [5]: https://cdn.gethue.com/uploads/2018/02/Metrics_selected_page.png
