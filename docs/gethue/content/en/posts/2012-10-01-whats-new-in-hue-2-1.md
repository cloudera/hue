---
title: What’s new in Hue 2.1
author: admin
type: post
date: 2012-10-01T04:00:00+00:00
url: /whats-new-in-hue-2-1/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/49800494117/whats-new-in-hue-2-1
tumblr_gethue_id:
  - 49800494117
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
[Hue][1] is a Web-based interface that makes it easier to use [Apache Hadoop][2]. [Hue 2.1][3] (included in [CDH4.1][4]) provides a new application on top of [Apache Oozie][5] (a workflow scheduler system for Apache Hadoop) for creating workflows and scheduling them repetitively. For example, Hue makes it easy to group a set of MapReduce jobs and Hive scripts and run them every day of the week.

In this post, we’re going to focus on the Workflow component of the new application.

## Workflow Editor

Workflows consist of one or multiple actions that can be executed sequentially or in parallel. Each action will run a program that can be configured with parameters (e.g. output=${OUTPUT} instead of hardcoding a directory path) in order to be easily reusable.

The current types of programs are:

  * MapReduce
  * Pig
  * Hive
  * Sqoop
  * Java
  * Shell
  * Ssh
  * Streaming jobs
  * DistCp

The application comes with a set of examples:

[<img class="aligncenter size-medium wp-image-19229" title="hue1" alt="" src="http://www.cloudera.com/wp-content/uploads/2012/10/hue13-300x148.png" width="300" height="148" />][6][

][7]

Workflows can be shared with other users and cloned. Forks are supported and enable actions to run at the same time. The Workflow Editor lets you compose your workflow.

Let’s take the Sequential Java (aka TeraSort) example and add an Hive action, HiveGen, that will generate some random data. TeraGen is a MapReduce job doing the same thing and both actions will run in parallel. Finally, the TeraSort action will read both outputs and sort them together You can see how this would look in Hue via the screenshot below.

[<img class="aligncenter size-medium wp-image-19230" title="hue2" alt="" src="http://www.cloudera.com/wp-content/uploads/2012/10/hue22-300x178.png" width="300" height="178" />][8]

## Workflow Dashboard

Our TeraGen workflow can then be submitted and controlled in the Dashboard. Parameters values (e.g. ${OUTPUT} of the output path of the TeraSort action) are prompted when clicking on the submit button.

Jobs can be filtered/killed/restarted and detailed information (progress, logs) is available within the application and in the Job Browser Application.

[<img class="aligncenter size-medium wp-image-19228" title="hue3" alt="" src="http://www.cloudera.com/wp-content/uploads/2012/10/hue32-300x184.png" width="300" height="184" />][9]

Individual management of a workflow can be done on its specific page. We can see the active actions in orange below:

[<img class="aligncenter size-medium wp-image-19231" title="hue4" alt="" src="http://www.cloudera.com/wp-content/uploads/2012/10/hue42-300x211.png" width="300" height="211" />][10]

## Summary

Before CDH4.1, Oozie users had to deal with XML files and command line programs. Now, this new application allows users to build, monitor and control their workflows within a single Web application. Moreover, the Hue File Browser (for listing and uploading workflows) and Job Browser (for accessing fine grained details of the jobs) are leveraged.

The next version of the Oozie application will focus on improving the general experience, increasing the number of supported Oozie workflows and prettifying the Editor.

In the meantime, feel free to report feedback and wishes to [hue-user][11]!

 [1]: https://gethue.com
 [2]: http://hadoop.apache.org/
 [3]: https://gethue.comindex.html#releases-2.1.0
 [4]: https://ccp.cloudera.com/display/CDH4DOC/CDH4+Installation+Guide
 [5]: http://incubator.apache.org/oozie/
 [6]: http://www.cloudera.com/wp-content/uploads/2012/10/hue13.png
 [7]: http://www.cloudera.com/wp-content/uploads/2012/10/hue1.png
 [8]: http://www.cloudera.com/wp-content/uploads/2012/10/hue22.png
 [9]: http://www.cloudera.com/wp-content/uploads/2012/10/hue32.png
 [10]: http://www.cloudera.com/wp-content/uploads/2012/10/hue42.png
 [11]: https://groups.google.com/a/cloudera.org/group/hue-user/topics
