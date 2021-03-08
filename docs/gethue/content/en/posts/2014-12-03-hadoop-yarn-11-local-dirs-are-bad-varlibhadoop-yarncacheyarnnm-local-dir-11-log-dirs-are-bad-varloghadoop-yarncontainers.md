---
title: 'Hadoop YARN: 1/1 local-dirs are bad: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir; 1/1 log-dirs are bad: /var/log/hadoop-yarn/containers'
author: admin
type: post
date: 2014-12-03T23:59:42+00:00
url: /hadoop-yarn-11-local-dirs-are-bad-varlibhadoop-yarncacheyarnnm-local-dir-11-log-dirs-are-bad-varloghadoop-yarncontainers/
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
If you are getting this error, make some disk space!

<pre><code class="bash">

1/1 local-dirs are bad: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir; 1/1 log-dirs are bad: /var/log/hadoop-yarn/containers

</code></pre>

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2014/12/yarn-rm-unhealty-1024x331.png" />][1]

## Node Manager logs

<pre><code class="bash">

yarn.server.nodemanager.DirectoryCollection: Directory /var/lib/hadoop-yarn/cache/yarn/nm-local-dir error, used space above threshold of 90.0%, removing from list of valid directories

2014-11-17 17:45:00,713 WARN org.apache.hadoop.yarn.server.nodemanager.DirectoryCollection: Directory /var/log/hadoop-yarn/containers error, used space above threshold of 90.0%, removing from list of valid directories

2014-11-17 17:45:00,713 INFO org.apache.hadoop.yarn.server.nodemanager.LocalDirsHandlerService: Disk(s) failed: 1/1 local-dirs are bad: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir; 1/1 log-dirs are bad: /var/log/hadoop

</code></pre>

&nbsp;

## Resource Manager logs

<pre><code class="bash">

2014-11-17 16:57:07,301 INFO org.apache.hadoop.yarn.server.resourcemanager.rmnode.RMNodeImpl: Node localhost:34650 reported UNHEALTHY with details: 1/1 local-dirs are bad: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir; 1/1 log-dirs are bad: /var/log/hadoop-yarn/containers

</code></pre>

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2014/12/yarn-rm-unhealty.png
