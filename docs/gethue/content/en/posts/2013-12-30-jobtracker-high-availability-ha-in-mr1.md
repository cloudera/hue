---
title: JobTracker High Availability (HA) in MR1
author: admin
type: post
date: 2013-12-30T15:02:46+00:00
url: /jobtracker-high-availability-ha-in-mr1/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/71637613809/jobtracker-high-availability-ha-in-mr1
tumblr_gethue_id:
  - 71637613809
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
<p id="docs-internal-guid-60fb361f-4405-815e-a36b-72434b0895db">
  When the Job Tracker goes down, Hue cannot display the Jobs in File Browser or submit to the correct cluster.
</p>

&nbsp;

In MR1, Hadoop can support two Job Trackers, a master Job Tracker that can fail over to a standby Job Tracker and hence provide Job Tracker HA. Let’s see how [Hue 3.5][1] and [CDH5beta1][2] (and probably CDH4.6) can take advantage of this.

Note: in MR1 Hue is using a [plugin][3] to communicate with the Job Tracker. This can be configured in CDH or Hadoop 0.23 / 1.2.0 ([MAPREDUCE-461][4]).

&nbsp;

We configure two Job Trackers in the [hue.ini][5]:

<pre><code class="bash">[hadoop]

...

[[mapred_clusters]]

[[[default]]]

\# Enter the host on which you are running the Hadoop JobTracker

jobtracker_host=host-1

\# Whether to submit jobs to this cluster

submit_to=True

[[[ha-standby]]]

\# Enter the host on which you are running the Hadoop JobTracker

jobtracker_host=host-2

\# Whether to submit jobs to this cluster

submit_to=True

</code></pre>

&nbsp;

And that’s it! Hue will communicate with the available Job Tracker automatically!

&nbsp;

Notice that in the case of Oozie jobs, Oozie will try to re-submit the job but will need a logical name ([HUE-1631][6]). To enable this in Hue, specify it in each MapReduce cluster, e.g.:

<pre><code class="bash">[hadoop]

[[mapred_clusters]]

[[[default]]]

\# JobTracker logical name.

\## logical_name=MY_NAME

</code></pre>

&nbsp;

As usual feel free to comment on the [hue-user][7] list or[@gethue][8]!

 [1]: http://gethue.tumblr.com/post/69115755563/hue-3-5-and-its-redesign-are-out
 [2]: http://www.cloudera.com/content/support/en/documentation/cdh5-documentation/cdh5-documentation-v5-latest.html
 [3]: http://cloudera.github.io/hue/docs-3.5.0/manual.html#_configure_mapreduce_0_20_mr1
 [4]: https://issues.apache.org/jira/browse/MAPREDUCE-461
 [5]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L336
 [6]: https://issues.cloudera.org/browse/HUE-1631
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue
