---
title: Hue Active Users Metric Improvements
author: Ying Chen
type: post
date: 2020-04-01T00:00:00+00:00
url: /hue-active-users-metric-improvements/
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
#  - Version 4.7

---


To understand the performance of Hue, we want to know how many active users in Hue--and more specifically--how many on each host. An active user is who sends requests from his/her browser to the Hue server in the last one hour. Recently, Hue got some improvements for providing and displaying better metrics.

1. On premise, Hue is using [PyFormance](https://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/) implements /desktop/metrics endpoint. Cloudera Manager collects data via the endpoint and displays the metric “Active Users” in the Charts Library, but all hosts show the same number of active users. With [HUE-9210](https://issues.cloudera.org/browse/HUE-9210), the active users metric on each host is collected based on its hostname (see screenshot).

	![cm_active_users.png](https://cdn.gethue.com/uploads/2020/04/cm_active_users.png)

	Here we can see three users on the blue Hue API server role and one on the green

2. In Kubernetes, Hue is using [django-prometheus](https://gethue.com/collecting-hue-metrics-with-prometheus-in-kubernetes/) to implement endpoint /metrics. With [HUE-9194](https://issues.cloudera.org/browse/HUE-9194), we added two new active users metrics to display in Prometheus server. You may [set up your Prometheus server](https://gethue.com/set-up-prometheus-server-without-kubernetes/) without Kubernetes. Once setup is done and the server is started, open your browser at localhost:9090. From the drop down menu of metrics, you may find hue_active_users and hue_local_active_users.

	![prometheus_active_users.png](https://cdn.gethue.com/uploads/2020/04/prometheus_active_users.png)

	This hue\_local\_active\_users is showing active users in specific container bases on its hostname, while hue\_active\_users will show all users in the data warehouse.

Any feedback or questions? Feel free to comment here or on the Forum or @gethue and quick start SQL querying!

Ying Chen from the Hue Team
