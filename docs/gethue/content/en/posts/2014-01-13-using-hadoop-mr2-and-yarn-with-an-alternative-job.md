---
title: Using Hadoop MR2 and YARN with an alternative Job Browser interface
author: admin
type: post
date: 2014-01-13T17:52:00+00:00
url: /using-hadoop-mr2-and-yarn-with-an-alternative-job/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/73219285865/using-hadoop-mr2-and-yarn-with-an-alternative-job
tumblr_gethue_id:
  - 73219285865
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

<p id="docs-internal-guid-15de28ba-8cb7-247f-caf6-d0f1c5b75f25">
  <span>Hue now defaults to using </span><a href="https://hadoop.apache.org/docs/current2/hadoop-yarn/hadoop-yarn-site/YARN.html"><span>Yarn</span></a><span> since </span><a href="http://gethue.tumblr.com/post/69115755563/hue-3-5-and-its-redesign-are-out"><span>version 3</span></a><span>.</span>
</p>

&nbsp;

{{< youtube BiyUyys85eI >}}

First, it is a bit simpler to configure Hue with MR2 than in MR1 as Hue does not need to use the [Job Tracker plugin][1] since Yarn provides a REST API. Yarn is also going to provide an equivalent of <a href="http://gethue.tumblr.com/post/71637613809/jobtracker-high-availability-ha-in-mr1" target="_blank" rel="noopener noreferrer">Job Tracker HA</a> with [<span>YARN-149</span>][2].

Here is how to configure the clusters in [hue.ini][3]. Mainly, if you are using a pseudo distributed cluster it will work by default. If not, you will just need to update all the localhost to the hostnames of the Resource Manager and History Server:

<pre><code class="bash">[hadoop]

...

\# Configuration for YARN (MR2)

\# ------------------------

[[yarn_clusters]]

[[[default]]]

\# Enter the host on which you are running the ResourceManager

resourcemanager_host=localhost

\# The port where the ResourceManager IPC listens on

resourcemanager_port=8032

\# Whether to submit jobs to this cluster

submit_to=True

\# URL of the ResourceManager API

resourcemanager_api_url=http://localhost:8088

\# URL of the ProxyServer API

proxy_api_url=http://localhost:8088

\# URL of the HistoryServer API

history_server_api_url=http://localhost:19888

\# Configuration for MapReduce (MR1)

\# ------------------------

[[mapred_clusters]]

[[[default]]]

\# Whether to submit jobs to this cluster

submit_to=False

</code></pre>

<span>And that’s it! You can now look at jobs in Job Browser, get logs and submit jobs to Yarn!</span>

&nbsp;

<span>As usual feel free to comment on the</span>[<span>hue-user</span>][4] <span>list or</span>[<span>@gethue</span>][5]<span>!</span>

[1]: http://cloudera.github.io/hue/docs-3.5.0/manual.html#_configure_mapreduce_0_20_mr1
[2]: https://issues.apache.org/jira/browse/YARN-149
[3]: https://github.com/cloudera/hue/blob/master/desktop/conf/pseudo-distributed.ini.tmpl#L433
[4]: http://groups.google.com/a/cloudera.org/group/hue-user
[5]: https://twitter.com/gethue
