---
title: New SQL Editor
author: admin
type: post
date: 2016-06-30T17:49:47+00:00
url: /new-sql-editor/
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

Here is the new SQL Editor!

Hue now has a generic editor that supports any languages but currently focuses on [SQL][1]. It is a single page app that is much faster than before and simpler to use. Here is a list of some important functionalities and a video demo that show them in action:

- No page reload when switching between queries
- Live history of running and past queries
- Enhanced support for Hive and [Impala][2]
- Extendable to any programming language

{{< youtube LvTWPgkrdvM >}}

Summary

- Metadata Browsing
  - Support listing and filtering thousands of databases or tables
  - Quick links to table browsers
  - Statistics
- Query edition
  - Smart autocomplete
  - Format a query, search and replace
  - Parameterization
  - Expanded view, fixed column/row headers, jump to a column..
  - Bar, pie, marker map, gradient map, scater plots charting
  - Links to jobs and logs
  - [Solr SQL support][3]
  - [JDBC support (beta)][4]
- Result manipulation
  - Share
  - Excel, csv downloads
  - Export to an HDFS file or new table
  - [Drag & Drop a saved query into a workflow][5]

&nbsp;

We hope that this new editor makes you SQL on Hadoop even more productive! If you want to connect with other databases and engines, feel free to write a [new connector][6] or engage the community on the [hue-user][7] list. The next iteration in Hue 3.11 (~Q3 2016) will polish even more the user experience so any feedback (bug, feature..) is [welcomed][8]!

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/06/editor-grid-1024x524.png"><img src="https://cdn.gethue.com/uploads/2016/06/editor-grid-1024x524.png" /></a><figcaption>Grid result view</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/06/editor-map-1024x479.png"><img src="https://cdn.gethue.com/uploads/2016/06/editor-map-1024x479.png" /></a><figcaption>Result widget view</figcaption></figure>

[1]: https://gethue.com/category/sql/
[2]: http://impala.io
[3]: https://gethue.com/sql-editor-for-solr-sql/
[4]: https://gethue.com/custom-sql-query-editors/
[5]: https://gethue.com/drag-drop-saved-hive-queries-into-your-workflows/
[6]: https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
[9]: https://cdn.gethue.com/uploads/2016/06/editor-grid.png
[10]: https://cdn.gethue.com/uploads/2016/06/editor-map.png
