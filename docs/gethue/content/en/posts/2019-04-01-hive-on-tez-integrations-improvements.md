---
title: Hive on Tez integrations improvements
author: admin
type: post
date: 2019-04-01T16:12:55+00:00
url: /hive-on-tez-integrations-improvements/
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

---
<span style="font-weight: 400;">We’ve made some improvements when using </span>[<span style="font-weight: 400;">Apache TEZ</span>][1] <span style="font-weight: 400;">as the query engine of the </span>[<span style="font-weight: 400;">SQL Editor</span>][2]<span style="font-weight: 400;">:</span>

<li style="list-style-type: none;">
  <ol>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">When running a query, the job id will now show up in the query log. Pressing the id will show the job in the mini job browser.</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">TEZ, does not update its progress in the log, but if you’ve opened the mini job browser, Hue will be able to update the job’s progress right in the editor.</span>
    </li>
  </ol>
</li>

[<img class="aligncenter wp-image-5834" src="https://cdn.gethue.com/uploads/2019/04/Screen-Shot-2019-03-29-at-3.53.54-PM.png"/>][3]

<li style="font-weight: 400;">
  <span style="font-weight: 400;">TEZ jobs will now show their full detail in the job browser.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">TEZ jobs create more logs. The job browser will now dynamically fetch and display them.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">The first result of a TEZ queries was missing and it was fixed so that all the results are now displayed.</span>
</li>

&nbsp;

[<img class="aligncenter wp-image-5835" src="https://cdn.gethue.com/uploads/2019/04/Screen-Shot-2019-03-29-at-3.50.35-PM.png"/>][4]

**Note**<span style="font-weight: 400;">: as TEZ requires one session per query, do not forget to configure Hue to allow more than </span>[<span style="font-weight: 400;">one SQL session</span>][5] <span style="font-weight: 400;">per user (to not be confused with the number of </span>[<span style="font-weight: 400;">Hue Browser sessions</span>][6]<span style="font-weight: 400;">).</span>

<span style="font-weight: 400;">Happy Querying!</span>

 [1]: https://tez.apache.org/
 [2]: https://gethue.com/sql-editor/
 [3]: https://cdn.gethue.com/uploads/2019/04/Screen-Shot-2019-03-29-at-3.53.54-PM.png
 [4]: https://cdn.gethue.com/uploads/2019/04/Screen-Shot-2019-03-29-at-3.50.35-PM.png
 [5]: http://cloudera.github.io/hue/latest/administrator/configuration/editor/#hive
 [6]: https://gethue.com/restrict-number-of-concurrent-sessions-per-user/
