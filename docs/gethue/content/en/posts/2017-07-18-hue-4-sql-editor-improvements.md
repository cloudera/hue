---
title: Hue 4 SQL Editor improvements
author: admin
type: post
date: 2017-07-18T17:59:36+00:00
url: /hue-4-sql-editor-improvements/
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
categories:
  - Version 4
tags:
  - autocomplete
  - metadata
  - navigator optimizer
  - popular

---
Aloha SQL experts!

For [Hue 4][1] we've made numerous improvements to the Hive and Impala SQL editors greatly improving the SQL editor user experience. When working with Hive and Impala queries Hue will now provide you with autocomplete suggestions based on popularity as well as risk evaluation from [Navigator Optimizer][2].

A brand new assist panel has been added on the right hand side, containing details about the active statement as well as documentation for UDFs.

#### Enriched autocomplete

The autocompleter will suggest popular tables, columns, filters, joins, group by, order by etc. based on metadata from Navigator Optimizer. A new "Popular" tab has been added to the autocomplete result dropdown which will be shown when there are popular suggestions available.

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png"><img src="https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png"/></a><figcaption>Popular joins, showing the popularity score when selected</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2017/07/hue_4_popular_filter_agg.png"><img src="https://cdn.gethue.com/uploads/2017/07/hue_4_popular_filter_agg.png"/></a><figcaption>Autocomplete results suggesting popular aggregate function on the left and popular filters on the right</figcaption></figure>

<h4 style="margin-top: 100px;">
  Risk and suggestions
</h4>

While editing, Hue will run your queries through Navigator Optimizer in the background to identify potential risks that could affect the performance of your query. If a risk is identified an exclamation mark is shown above the query editor and suggestions on how to improve it is displayed in the lower part of the right assistant panel.

<img width="750" height="286" data-gifffer="https://cdn.gethue.com/uploads/2017/07/hue_4_risk_6.gif"  />

<h4 style="margin-top: 100px;">
  Data where you need it when you need it
</h4>

You can now find your Hue documents, HDFS and S3 files and more in the left assist panel, right-clicking items will show a list of actions, you can also drag-and-drop a file to get the path in your editor and more.

<figure><a href="https://cdn.gethue.com/uploads/2017/07/hue_4_left_assist.png"><img src="https://cdn.gethue.com/uploads/2017/07/hue_4_left_assist.png"/></a><figcaption>The left assist showing details for a Hue document</figcaption></figure>

The Functions panel on the right side will let you browse and filter functions for Hive, Impala and Pig. Double-click or drag to insert it in the editor.

<figure><a href="https://cdn.gethue.com/uploads/2017/07/hue_4_functions.png"><img src="https://cdn.gethue.com/uploads/2017/07/hue_4_functions.png"/></a><figcaption>The new Functions panel in the right assist panel</figcaption></figure>

<h4 style="margin-top: 100px;">
  Improved multi-query editing
</h4>

The right Assistant panel will identify and display the active tables in the statement that you're editing, this gives you a quick overview and you can find details such as samples and columns by hovering over a table.

<figure><img width="800" height="295" data-gifffer="https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif"  /><figcaption>The new Assistant panel showing the tables in the active statement</figcaption></figure>

When you have multiple statements it's enough to put the cursor in the statement you want to execute, the active statement is indicated with a blue gutter marking.

&nbsp;

As usual you can send feedback and participate on the [hue-user][3] list or [@gethue][4]!

&nbsp;

 [1]: https://gethue.com/hue-4-and-its-new-interface-is-out/
 [2]: https://optimizer.cloudera.com/
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
