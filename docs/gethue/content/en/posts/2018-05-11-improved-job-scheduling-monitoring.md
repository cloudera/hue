---
title: Improved job scheduling monitoring
author: admin
type: post
date: 2018-05-11T14:57:26+00:00
url: /improved-job-scheduling-monitoring/
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
Two popular medium improvements are coming in the [Job Browser][1] to ease the monitoring of submitted jobs.

## Listing of the running jobs on top

With [HUE-8268][2] the experience is getting back to pre-[Hue 4][3] where jobs were split in two categories:

  * Running
  * Completed (Succeeded or Failed)

This simplifies monitoring a lot of running jobs.

<figure><a href="https://cdn.gethue.com/uploads/2018/05/js_jobs.png"><img src="https://cdn.gethue.com/uploads/2018/05/js_jobs.png"/></a><figcaption>Splitting the list of jobs in "Running" and "Completed"</figcaption></figure>

&nbsp;

## Disabling filtering of schedules and bundles

With [HUE-8267][5] the default time filters of schedules and bundles are removed. By default those were filtering out jobs submitted more than a week ago, which was not practical.

<figure><a href="https://cdn.gethue.com/uploads/2018/05/jb_schedules.png"><img src="https://cdn.gethue.com/uploads/2018/05/jb_schedules.png"/></a><figcaption>Duration filter is now removed for scheduled jobs</figcaption></figure>

&nbsp;

As usual feel free to send feedback to the [hue-user][7] list or [@gethue][8] or send [improvements][9]!

 [1]: https://gethue.com/browsers/
 [2]: https://issues.cloudera.org/browse/HUE-8268
 [3]: https://gethue.com/hue-4-and-its-new-interface-is-out/
 [4]: https://cdn.gethue.com/uploads/2018/05/js_jobs.png
 [5]: https://issues.cloudera.org/browse/HUE-8267
 [6]: https://cdn.gethue.com/uploads/2018/05/jb_schedules.png
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue
 [9]: https://github.com/cloudera/hue
