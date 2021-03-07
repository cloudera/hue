---
title: 'Season II: 5. Bundle Oozie coordinators with Hue'
author: admin
type: post
date: 2013-10-14T03:23:25+00:00
url: /hadoop-tutorial-bundle-oozie-coordinators-with-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/63988110361/hadoop-tutorial-bundle-oozie-coordinators-with-hue
tumblr_gethue_id:
  - 63988110361
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

<p id="docs-internal-guid-4ab313a2-b4f9-6636-ef5e-6ec66cd3ea40">
  <a href="http://gethue.com"><span>Hue</span></a><span> provides a </span><a href="http://gethue.tumblr.com/tagged/oozie"><span>great Oozie UI</span></a><span> in order to use Oozie without typing any XML. In </span><a href="http://gethue.tumblr.com/post/61597968730/hadoop-tutorials-ii-3-schedule-hive-queries-with"><span>Tutorial 3</span></a><span>, we demonstrate how to use an Oozie coordinator for scheduling a daily top 10 of restaurants. Now lets imagine that we also want to compute a top 10 and 100. How can we do this? One solution is to use Oozie bundles.</span>
</p>

&nbsp;

{{< youtube cVS10q9s478 >}}

&nbsp;

# <span>Workflow and Coordinator updates</span>

<span>Bundles are are way to group coordinators together into a set. This set is easier to manage as a unique instance and can be parameterized too.</span>

&nbsp;

<span>The first step is to replace 10 by a variable \${n} in our Hive </span>[<span>script</span>][1]<span>:</span>

<pre class="code">CREATE TABLE top_cool AS
SELECT r.business_id, name, SUM(cool) AS coolness, '${date}' as `date`
FROM review r JOIN business b
ON (r.business_id = b.business_id)
WHERE categories LIKE '%Restaurants%'
AND `date` = '${date}'
GROUP BY r.business_id, name
ORDER BY coolness DESC
LIMIT ${n}</pre>

<span>Then, in the workflow, we add a parameter in the Hive action: </span><span>n=\${n}</span><span>. You can test the workflow by submitting it and providing 10 for the value n.</span>

&nbsp;

<span>We now need to tell the Coordinator to fill-up with a value. For testing purpose, going to Step #5 of the editor and adding a ‘</span><span>Workflow properties</span><span>’ named ‘</span><span>n</span><span>’ and with value ‘</span><span>10</span><span>’ would produce the same result as in </span>[<span>Tutorial 1</span>][2]<span>. In practice these properties are mostly used for entering constants and </span>[<span>EL functions</span>][3] <span>that will directly provide a value to the workflow.</span>

&nbsp;

## <span>Bundle Editor</span>

<span>Lets create a new Bundle named ‘</span><span>daily_tops</span><span>’ with a kickoff date of 20121201. On the left panel, click on ‘</span><span>Add</span><span>’ in the Coordinator section. Select our ‘</span><span>daily_top</span><span>’ coordinator and a property named ‘</span><span>n</span><span>’ and with value ‘</span><span>10</span><span>’.</span>

&nbsp;

<span>Add again the same coordinator and this time pick ‘</span><span>10</span><span>’ for the value of ‘</span><span>n</span><span>’. Repeat with ‘</span><span>n</span><span>’ set to ‘</span><span>100</span><span>’.</span>

&nbsp;

## <span>Bundle Dashboard</span>

<span>You are now ready to go and submit the bundle! You can follow the overall progress in the Bundle dashboard. Bundles can be stopped, killed and re-run. Clicking on an instantiation will link to the corresponding coordinator which is also linking to its generated workflows.</span>

&nbsp;

# <span>Sum-up</span>

<span>Of course, more efficient solutions exist than those in our simplified example. In practice Bundles are great for parameterizing non-date variables like market names (e.g. US, France). Another use case it to group together a series of coordinators in order to make them easier to manage (e.g. start, stop, re-run). Notice that the latest version of Hue that contains </span>[<span>HUE-1546</span>][4] <span>was used in the video.</span>

&nbsp;

<span>Hue comes up with a full set of Workflow/Coordinator/Bundle examples, ready to be submitted or copied. Hue can even be used with only its Oozie UI Dashboard, making it a breeze to manage Oozie in your browser. </span>

<span>Next, we will see how to browse our Yelp data in HBase! As usual feel free to comment on the </span>[<span>hue-user</span>][5] <span>list or </span>[<span>@gethue</span>][6]<span>!</span>

[1]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hive-workflow/select_top_n.sql
[2]: http://gethue.tumblr.com/post/60937985689/hadoop-tutorials-ii-2-execute-hive-queries-and
[3]: http://blog.cloudera.com/blog/2013/09/how-to-write-an-el-function-in-apache-oozie/
[4]: https://issues.cloudera.org/browse/HUE-1546
[5]: http://groups.google.com/a/cloudera.org/group/hue-user
[6]: https://twitter.com/gethue
