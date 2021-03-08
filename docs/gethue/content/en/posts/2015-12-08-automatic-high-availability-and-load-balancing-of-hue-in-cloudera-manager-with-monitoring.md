---
title: Automatic High Availability and Load Balancing of Hue in Cloudera Manager with monitoring
author: admin
type: post
date: 2015-12-08T16:55:58+00:00
url: /automatic-high-availability-and-load-balancing-of-hue-in-cloudera-manager-with-monitoring/
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
---

The release of [Hue 3.9][1] and CDH5.5 makes Hue noticeably faster and easy to monitor.

A built-in load balancer can be added in just a few clicks. In the past, setting up a load balancer had still some [manual pieces][2]. These are still valid and recommended if you use your own Hue. However, if you use Cloudera Manager this new load balancer provides theses advantages out of the box:

- Automatic fail-over to an available healthy Hue in case of crash, network or host glitch
- Transparent serving of the static files for [much better request performances][3] and more responsiveness (cut down average number of Web request by page from 60 to 5, that's a lot of saving with many concurrent users!)

<figure><a href="https://cdn.gethue.com/uploads/2015/03/without-nginx.png"><img src="https://cdn.gethue.com/uploads/2015/03/without-nginx.png" /></a><figcaption>Before (without load balancer)</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2015/03/with-nginx.png"><img src="https://cdn.gethue.com/uploads/2015/03/with-nginx.png" /></a><figcaption>After (with load balancer)</figcaption></figure>

&nbsp;

The monitoring of the Hue service was also improved by tracking the number of active users, requests and other statistics warning about potential problems.

Here is a video explaining and demonstrating the improvements:

{{< youtube VLOGvlXrQeM >}}

<figure><a href="https://cdn.gethue.com/uploads/2015/12/hue-cm-monitoring2.png"><img src="https://cdn.gethue.com/uploads/2015/12/hue-cm-monitoring2.png" /></a><figcaption>Monitoring of number of active users and requests</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2015/12/hue-cm-1-instance-1024x404.png"><img src="https://cdn.gethue.com/uploads/2015/12/hue-cm-1-instance-1024x404.png" /></a><figcaption>A single Hue server</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2015/12/hue-cmlb-e1449521110230-1024x335.png"><img src="https://cdn.gethue.com/uploads/2015/12/hue-cmlb-e1449521110230-1024x335.png" /></a><figcaption>Adding redundant Hue servers and balancers for more performances and availability</figcaption></figure>

&nbsp;

Next versions will continue to focus on stability and performances with more optimizations for an even better end user experience!

If you have any question, feel free to comment here or on the [hue-user][6] list or [@gethue][7]!

[1]: https://gethue.com/hue-3-9-with-all-its-improvements-is-out/
[2]: https://gethue.com/automatic-high-availability-with-hue-and-cloudera-manager/
[3]: https://gethue.com/using-nginx-to-speed-up-hue-3-8-0/
[4]: https://cdn.gethue.com/uploads/2015/12/hue-cm-1-instance.png
[5]: https://cdn.gethue.com/uploads/2015/12/hue-cmlb.png
[6]: http://groups.google.com/a/cloudera.org/group/hue-user
[7]: https://twitter.com/gethue
