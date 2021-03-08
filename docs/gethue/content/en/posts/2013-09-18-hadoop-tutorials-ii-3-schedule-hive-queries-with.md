---
title: 'Season II: 3. Schedule Hive queries with Oozie coordinators'
author: admin
type: post
date: 2013-09-18T17:13:00+00:00
url: /hadoop-tutorials-ii-3-schedule-hive-queries-with/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/61597968730/hadoop-tutorials-ii-3-schedule-hive-queries-with
tumblr_gethue_id:
  - 61597968730
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
categories:
  - Tutorial
---

<p id="docs-internal-guid-4887476c-320c-a45c-febf-e2e58849f7a2">
  <span>In the previous </span><a href="http://gethue.tumblr.com/post/60937985689/video-series-ii-2-execute-hive-queries-and-schedule"><span>episode</span></a><span> we saw how to create an Hive action in an Oozie workflow. These workflows can then be repeated automatically with an Oozie coordinator. This post describes how to schedule Hadoop jobs (e.g. run this job everyday at midnight).</span>
</p>

{{< youtube IOF7WMp9VNQ >}}

# <span>Oozie Coordinators</span>

<span>Our goal: compute the 10 coolest restaurants of the day everyday for 1 month:</span>

&nbsp;

<span>From </span>[<span>episode 2</span>][1]<span>, now have a workflow ready to be ran everyday. We create a ‘</span><span>daily_top</span><span>’ coordinator and select our previous Hive workflow. Our frequency is daily, and we can start from </span><span>November 1st 2012 12:00 PM</span> <span>to </span><span>November 30th 2012 12:00 PM</span><span>.</span>

&nbsp;

<span>The most important part is to recreate a URI that represents the date of the data. Notice that there is more efficient way to do this but we have an example easier to understand.</span>

&nbsp;

<span>As our data is already present, we just need to create an output dataset named ‘</span><span>daily_days</span><span>’ (which contrary to the input dataset won’t check if the input is available). We pick the URI of the data set to be like the date format of the episode one (e.g. </span><span>$YEAR-$MONTH-\$DAY</span><span>). These parameters are going to be automatically filled in our workflow by the coordinator. </span>

&nbsp;

<span>We now link our ‘</span><span>daily_days</span><span>’ dataset to our workflow variable ‘</span><span>date</span><span>’ and save the coordinator.</span>

&nbsp;

Notice that on Step 5 the  ’Oozie parameters’ list which is the equivalent of the coordinator.properties file. The values will appear in the submission pop-up an can be overridden. There are also ‘Workflow properties’  for fill-up workflow parameters directly (which can be parameterized themselves by ‘Oozie parameters’ or <a href="http://blog.cloudera.com/blog/2013/09/how-to-write-an-el-function-in-apache-oozie/" target="_blank" rel="noopener noreferrer">EL functions</a> or constants). We will have more on this in the upcoming Oozie bundle episode.

&nbsp;

<span>Now submit the coordinator and see the 30 instances (one for each day of November) being  created and triggering the workflow with the Hive query for the corresponding day. Coordinators can also be stopped and re-ran through the UI. Each workflow can be individually accessed by simply clicking on the date instance.</span>

&nbsp;

# <span>Sum-up</span>

<span>With their input and output datasets Coordinators are great for scheduling repetitive workflows in a few clicks. Hue offers a UI and wizard that lets you avoid any Oozie XML. At some point, Hue will also make it even simpler by automating the creation of the workflow and coordinator: </span>[HUE-1389][2]<span>.</span>

Next, let’s do fast SQL with [Impala][3]!

[1]: http://gethue.tumblr.com/post/60937985689/video-series-ii-2-execute-hive-queries-and-schedule
[2]: https://issues.cloudera.org/browse/HUE-1389
[3]: http://gethue.tumblr.com/post/62452792255/fast-sql-with-the-impala-query-editor
