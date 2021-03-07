---
title: How to fix the Map chart on Hue 3.5
author: admin
type: post
date: 2014-04-04T14:39:16+00:00
url: /how-to-fix-map/
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
  - Development

---
Hue 3.5 ships with <a href="https://issues.cloudera.org/browse/HUE-2063" target="_blank" rel="noopener noreferrer">a bug</a> in the Map Chart widget that prevents the users to correctly display the map in their browsers.

Don't despair though! We've come up with a bookmarklet that solves the problem. Just drag this button

<p style="text-align:center">
  <a href="javascript:(function()%7Bfunction%20callback()%7B%7Dvar%20s%3Ddocument.createElement(%22script%22)%3Bs.src%3D%22https%3A%2F%2Fcdn.gethue.com%2Fuploads%2Fjs%2Ffixmap.js%22%3Bif(s.addEventListener)%7Bs.addEventListener(%22load%22%2Ccallback%2Cfalse)%7Delse%20if(s.readyState)%7Bs.onreadystatechange%3Dcallback%7Ddocument.body.appendChild(s)%3B%7D)()" class="sf-button accent" style="color:#FFF!important"><i class="fa fa-globe"></i> Fix the Hue Map!</a>
</p>

to your bookmarks bar. When you are on the Chart panel of the Hive or Impala app in Hue, click on the Map icon, select the latitude and longitude columns and then click on the newly created bookmarklet to fix the bug!

As usual feel free to comment on the [hue-user][1] list or [@gethue][2]!

 [1]: http://groups.google.com/a/cloudera.org/group/hue-user
 [2]: https://twitter.com/gethue
