---
title: Monitoring Hue activity with Grafana Dashboards
author: Ying Chen
type: post
date: 2020-06-23T00:00:00+00:00
url: /monitoring-hue-activity-with-grafana-dashboards/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
  - Development
#  - Version 4.8

---

Besides [Hue Active Users Metric Improvements](https://gethue.com/hue-active-users-metric-improvements/), we’ve also added a new [Prometheus](https://prometheus.io/) metrics number of queries, which shows how many queries were executed in the last ten minutes. Now both of them are available in Hue’s <a href="https://grafana.com/">Grafana</a> dashboard.

Let’s go to the Grafana dashboard list, you will find Hue’s Home dashboard in the Hue folder.

![grafana_dashboard_list.png](https://cdn.gethue.com/uploads/2020/06/grafana_dashboard_list.png)

After opening the Home dashboard, you will see four panels which list CPU, memory, active users, and number of queries. You may upload [hue-home.json](https://github.com/cloudera/hue/blob/master/tools/kubernetes/grafana/hue-home.json) to Grafana to generate the same graphs.

![hue_grafana_graphs.png](https://cdn.gethue.com/uploads/2020/06/hue_grafana_graphs.png)

This dashboard will help administrators monitor Hue’s performance in the data warehouse.

Any feedback or question? Feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) Live SQL querying!

Ying Chen from the Hue Team
