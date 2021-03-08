---
title: SQL Improvements with row counts, sample popup and more
author: admin
type: post
date: 2016-12-22T01:03:02+00:00
url: /sql-improvements-with-row-counts-sample-popup-and-more/
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
categories:

---
<span style="font-weight: 400;">The Hue editor keeps getting better. Previously, we showed the </span>[<span style="font-weight: 400;">new autocomplete</span>][1] <span style="font-weight: 400;">and </span>[<span style="font-weight: 400;">result refining</span>][2]<span style="font-weight: 400;">. Here is a list of improvements coming in Hue 3.12:</span>

&nbsp;

## <span style="font-weight: 400;">Row count</span>

<span style="font-weight: 400;">The number of rows returned is displayed so you can quickly seehe size of the dataset. If the database engine does not provide the number of rows, Hue estimates the value and appends a plus sign, e.g. 100+.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/result-count.png" />][3]

## <span style="font-weight: 400;">Sample popup</span>

<span style="font-weight: 400;">This popup offers a quick way to see sample of the data and other statistics on databases, tables, and columns. You can open the popup from the SQL Assist or with a right-click on any SQL object (table, column, function...). In this release, it also opens faster and caches the data.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/right_click_editor_assist-1.png" width="658" height="544"  />][4]

&nbsp;

## <span style="font-weight: 400;">SQL Assist </span>

<span style="font-weight: 400;">The rendering of the items was rewritten and optimized. You should not experience any lag on databases with thousands of columns. The footer provides direct links to the metastore page or to the table in the assist. The popup can now be pinned iso that it is always visible while you edit your queries.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/dragdrop_from_asssist.png" />][5]

<span style="font-weight: 400;">The Drag & Drop of tables and columns directly into the editor now works well with older browsers.</span>

&nbsp;

## <span style="font-weight: 400;">SQL Formatter</span>

<span style="font-weight: 400;">The SQL Formatter has a new and smarter algorithm that will make your queries look pretty with a single click!</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/sql_formatter_before-1024x59.png" />][6]

<span style="font-weight: 400;">Before</span>

<img src="https://cdn.gethue.com/uploads/2016/12/sql_formatter2_after.png" />

<span style="font-weight: 400;">After</span>

## <span style="font-weight: 400;">Tez</span>

<span style="font-weight: 400;">An </span>[<span style="font-weight: 400;">external contribution</span>][7] <span style="font-weight: 400;">provided support for sending multiple queries when using Tez (instead of a maximum of just one at the time). You can turn it on with this setting:</span>

<pre><code class="bash">[beeswax]

max_number_of_sessions=10

</code></pre>

&nbsp;

## <span style="font-weight: 400;">Timeline and Pivot graphing</span>

<span style="font-weight: 400;">These visualizations are convenient for plotting chronological data or when subsets of rows have the same attribute: they will be stacked together.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/sql_timeline_chart-1024x351.png" />][8]

<span style="font-weight: 400;">Timeline</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/pivot_graph-1024x275.png" />][9]

Pivot

## <span style="font-weight: 400;">Create external table</span>

<span style="font-weight: 400;">The improved </span>[<span style="font-weight: 400;">support for S3</span>][10] <span style="font-weight: 400;">introduced the possibility of directly creating an external table in HDFS or S3.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/create_external_table-1024x387.png" />][11]

&nbsp;

## <span style="font-weight: 400;">Scalable export of query results in CSV format</span>

<span style="font-weight: 400;">Previous field delimiter of the output was hardcoded to the ^A character, large output of queries are now in JSON format which is more standard format and so can be more easily processed.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/export_large_query_result.png" />][12]

 [1]: https://gethue.com/brand-new-autocompleter-for-hive-and-impala/
 [2]: https://gethue.com/new-features-in-the-sql-results-grid-in-hive-and-impala/
 [3]: https://cdn.gethue.com/uploads/2016/12/result-count.png
 [4]: https://cdn.gethue.com/uploads/2016/12/right_click_editor_assist-1.png
 [5]: https://cdn.gethue.com/uploads/2016/12/dragdrop_from_asssist.png
 [6]: https://cdn.gethue.com/uploads/2016/12/sql_formatter_before.png
 [7]: https://github.com/cloudera/hue/pull/436
 [8]: https://cdn.gethue.com/uploads/2016/12/sql_timeline_chart.png
 [9]: https://cdn.gethue.com/uploads/2016/12/pivot_graph.png
 [10]: https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/
 [11]: https://cdn.gethue.com/uploads/2016/12/create_external_table.png
 [12]: https://cdn.gethue.com/uploads/2016/12/export_large_query_result.png
