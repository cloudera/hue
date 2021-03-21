---
title: YARN Resource Manager High Availability (HA) in MR2
author: admin
type: post
date: 2014-06-18T21:20:43+00:00
url: /hadoop-tutorial-yarn-resource-manager-high-availability-ha-in-mr2/
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
slide_template:
  - default
categories:

---
Similarly to the [JobTracker High Availability configuration for MR1][1], Hue supports (since today’s date in master or Hue 3.7 or CDH5.1) more than one Resource Manager in case the Resource Manager goes down.

Hue will automatically pick up the active Resource Manager even if it failed over. This is possible because:

  * When submitting Oozie jobs, the logical name of the Resource Manager is used instead of the hostname of the current Resource Manager
  * Job Browser will automatically look for the active Resource Manager API if needed

Here is an example of configuration for the [[yarn_clusters]] section in hue.ini:

<pre><code class="bash">[hadoop]

\# Configuration for YARN (MR2)

\# ------------------------

[[yarn_clusters]]

[[[default]]]

\# Whether to submit jobs to this cluster

submit_to=True

\# Name used when submitting jobs

logical_name=ha-rm

\# URL of the ResourceManager API

resourcemanager_api_url=http://gethue-1.com:8088

\# URL of the ProxyServer API

proxy_api_url=http://gethue-1.com:8088

\# URL of the HistoryServer API

history_server_api_url=http://gethue-1.com:19888

[[[ha]]]

\# Enter the host on which you are running the failover Resource Manager

resourcemanager_api_url=http://gethue-2.com:8088

logical_name=ha-rm

submit_to=True

</code></pre>

We hope that the multi Resource Manager support will make your life with Hadoop easier!

As usual feel free to send feedback on the [hue-user][2] list or [@gethue][3]!

 [1]: https://gethue.com/jobtracker-high-availability-ha-in-mr1/
 [2]: http://groups.google.com/a/cloudera.org/group/hue-user
 [3]: https://twitter.com/gethue
