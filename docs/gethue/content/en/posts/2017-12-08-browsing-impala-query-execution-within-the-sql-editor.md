---
title: Browsing Impala Query Execution within the SQL Editor
author: admin
type: post
date: 2017-12-08T00:00:09+00:00
url: /browsing-impala-query-execution-within-the-sql-editor/
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
sf_author_info:
  - 1
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4

---
<p class="p1">
  Greetings SQL aficionados!
</p>

<p class="p1">
  In Hue 4.2, along with <a href="https://gethue.com/browsing-adls-data-querying-it-with-sql-and-exporting-the-results-back-in-hue-4-2/">ADLS</a> support, we're introducing a new feature that is sure to make query troubleshooting easier: Impala query execution details right inside of the <a href="https://gethue.com/sql-editor/">SQL Editor</a>.
</p>

<img src="https://cdn.gethue.com/uploads/2017/11/General.png"/>

&nbsp;

<p class="p1">
  There are three ways to access the new browser:
</p>

  * Best: Click on the query ID after executing a SQL query in the editor. This will open the mini job [browser][1] overlay at the current query. Having the query execution information side by side the SQL editor is especially helpful to understand the performance characteristics of your queries.
  * Open the mini job browser overlay and navigate to the queries tab.
  * Open the job browser and navigate to the queries tab.

&nbsp;

## Query capabilities {.p1}

<p class="p1">
  Display the list of currently running queries on the user's current Impala <a href="https://www.cloudera.com/documentation/enterprise/5-12-x/topics/impala_components.html#intro_impalad">coordinator</a> and a certain number of completed queries based on your <a href="https://www.cloudera.com/documentation/enterprise/5-12-x/topics/impala_webui.html">configuration</a> (25 by default).
</p>

<img src="https://cdn.gethue.com/uploads/2017/12/JB.png"/>

Display the [explain][2] plan which outlines logical execution steps. You can verify here that the execution will not proceed in an unexpected way (i.e. wrong join type, join order, projection order). This can happen if the statistics for the table are out of date as shown in the image below by the mention of "cardinality: unavailable". You can obtain statistics by running:

<pre><code class="bash">

COMPUTE STATS <TABLE_NAME>

</code></pre>

<img class="aligncenter wp-image-5077" src="https://cdn.gethue.com/uploads/2017/11/Explain.png"/>

Display the [summary][3] report which shows physical timing and memory information of each operation of the explain plan. You can quickly find bottlenecks in the execution of the query which you can resolve by replacing expensive operations, repartitioning, changing file format or moving data.

<li style="list-style-type: none;">
  <img class="aligncenter wp-image-5081" src="https://cdn.gethue.com/uploads/2017/11/Summary.png"/>
</li>

Display the query plan which is a condensed version of the summary report in graphical form.

<li style="list-style-type: none;">
  <img src="https://cdn.gethue.com/uploads/2017/12/Plan.png"/>
</li>

Display the memory profile which contains information about the memory usage during the execution of the query. You can use this to determine if the [memory][4] available to your query is sufficient.

<li style="list-style-type: none;">
  <img src="https://cdn.gethue.com/uploads/2017/11/Memory.png"/>
</li>

Display the [profile][3] which gives you physical execution of the query in great detail. This view is used to analyze data exchange between the various operator and the performance of the IO (disk, network, CPU). You can use this to reorganize the location of your data (on disk, [in memory][5], different [partitions][6] or [file formats][7]).

<li style="list-style-type: none;">
  <img src="https://cdn.gethue.com/uploads/2017/12/Profile.png"/>
</li>

Manually close an opened query.

&nbsp;

<p class="p1">
  The enable_query_browser flag should be on by default. All you need to access the new browser is to make sure Impala is configured inside of Hue.
</p>

<pre><code class="bash">

[impala]

server_host=<impala_host>

server_port=<impala_port>

[jobbrowser]

enable_query_browser=true

</code></pre>

As always, if you have any questions, feel free to comment here or on the [hue-user list][8] or [@gethue][9]!

 [1]: https://gethue.com/browsers/
 [2]: https://www.cloudera.com/documentation/enterprise/5-12-x/topics/impala_explain.html#explain
 [3]: https://www.cloudera.com/documentation/enterprise/5-12-x/topics/impala_shell_commands.html#shell_commands
 [4]: https://www.cloudera.com/documentation/enterprise/5-12-x/topics/impala_perf_resources.html
 [5]: https://www.cloudera.com/documentation/enterprise/5-12-x/topics/impala_perf_hdfs_caching.html#hdfs_caching_ddl
 [6]: https://www.cloudera.com/documentation/enterprise/5-12-x/topics/impala_partitioning.html
 [7]: https://www.cloudera.com/documentation/enterprise/5-8-x/topics/impala_file_formats.html#file_format_choosing
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user
 [9]: https://twitter.com/gethue
