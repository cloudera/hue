---
title: A new UI for Oozie
author: admin
type: post
date: 2013-05-22T22:42:00+00:00
url: /tutorial-a-new-ui-for-oozie/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/51101760198/tutorial-a-new-ui-for-oozie
tumblr_gethue_id:
  - 51101760198
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
  - Release
---

<p id="docs-internal-guid-49be0c2f-ce57-b599-b202-4938fdfe4c02">
  <a href="http://oozie.apache.org/">Apache Oozie</a> is a great tool for building workflows of Hadoop jobs and scheduling them repeatedly. However, the user experience could be improved. In particular, all the job management happens on the command line and the default UI is readonly and requires a non-Apache licensed javascript library that makes it even more difficult to use.
</p>

<img src="https://lh6.googleusercontent.com/XTc_SBu10_xK7H21EAirZZPUamkuvGV7wOI4lxQkkVbE-yLw2X9kHJ6h-7QVAnIQAH1wjSdPT-Jk0ZdU7nW8TlocXWaMWEEOnO0ROne0BZgM6As7EMsEzBAX" alt="image" width="629px;" height="358px;" />

Current Oozie UI

<img src="https://lh3.googleusercontent.com/7x0W6YTh2Bbo8pUHK9IqvIUetRglQAaki5acklfPUuzHQ4fwJdSGElSJam5EmdjcBgWu9-jvVBVEBUWhMwpSloz0-wHsmiC8n_9O5ylRyH10olT_h6Bku2uu" alt="image" width="644px;" height="323px;" />

New Oozie UI

&nbsp;

Here is a short video demo:

{{< youtube wXJzqMQpssc >}}

The UI just sits on top of Oozie like the current Oozie UI. You can download a [release here][1]{.trackLink}.

The [README][2] is available online as well as the source code on [github][3] and details how to install and start the UI.

&nbsp;

Feature list

- Workflows, Coordinators, Bundles dashboards
- Built with standard and current Web technologies
- Filtering, sorting, progress bars, XML highlighting
- Kill, suspend, and re-run jobs from the UI
- One click access to Oozie logs or MapReduce launcher logs
- One click access to the HDFS outputs of the jobs
- Spotlight search about Oozie instrumentation/configuration

&nbsp;

We hope that you give a try to this new standalone UI. In the next version, we can see for providing some packages for a quicker install. As a side note, Oozie users who would like to try a Workflow/Coordinator/Bundle editor could have a look to the [Hue Oozie app][4].

&nbsp;

As usual, we are welcoming any [feedback][5]!

[1]: https://cdn.gethue.com/downloads/releases/hue-oozie/hue-oozie-1.1.tgz
[2]: https://github.com/cloudera/hue/blob/hue-oozie/dist/README
[3]: https://github.com/cloudera/hue/tree/hue-oozie
[4]: https://gethue.com/the-dynamic-workflow-builder-in-hue/
[5]: http://groups.google.com/a/cloudera.org/group/hue-user
