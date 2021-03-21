---
title: Improved Oozie Workflow display of large Graphs
author: admin
type: post
date: 2018-07-06T19:54:31+00:00
url: /improved-oozie-workflow-graph-display-in-hue-4-3/
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
<span style="font-weight: 400;">Hello Job Scheduler/Oozie users,</span>

<span style="font-weight: 400;">Previously, the Hue </span>[<span style="font-weight: 400;">Job browser</span>][1] <span style="font-weight: 400;">didn’t display the Oozie workflow Graph in the Graph tab for complex Oozie workflows (when the number of nodes are more than 30 or the workflow depth is more than 24).</span>

<span style="font-weight: 400;">Since Hue 4.3 and Oozie 5, Oozie provides an API to get an SVG image of the workflows. This new feature helps to display an SVG image of complex workflows in the </span>[<span style="font-weight: 400;">Dasboard</span>][2] interface<span style="font-weight: 400;">. This also alleviates the server memory issues while processing and displaying complex workflows.</span>

[<img class="alignnone size-full wp-image-5448" src="https://cdn.gethue.com/uploads/2018/07/screencapture-localhost-8000-hue-jobbrowser-2018-06-12-11_54_26-1.png"/>][3]

 [1]: https://gethue.com/scheduling/
 [2]: https://gethue.com/improved-job-scheduling-monitoring/
 [3]: https://cdn.gethue.com/uploads/2018/07/screencapture-localhost-8000-hue-jobbrowser-2018-06-12-11_54_26-1.png
