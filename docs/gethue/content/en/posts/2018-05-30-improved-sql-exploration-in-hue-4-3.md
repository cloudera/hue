---
title: 'Improved SQL Exploration: SQL Context Popover & Data Catalog'
author: admin
type: post
date: 2018-05-30T13:44:34+00:00
url: /improved-sql-exploration-in-hue-4-3/
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
Greetings SQL masters!

In Hue 4.3 we've made a bunch of improvements to SQL browsing and discovery. The SQL Context Popover, available throughout Hue from the assist panels, editor etc. has a simplified layout with one-click access to the most important information about your SQL entities. We've also introduced a new File Context Popover that allows you to browse and preview files without context switching.

The Table Browser has been refreshed, it's been simplified and a couple of new feature have been introduced for Navigator and Navigator Optimizer users.

## Improved SQL Context Popover

We've simplified the layout and removed the top tabs, now the most important information has been merged into one panel. A preview of column samples are now shown in the column list, you can always click a column to see a full sample.

<div class="wp-caption aligncenter">
  <p>
    <img width="848" height="426" data-gifffer="https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif"  />
  </p>

  <p class="wp-caption-text">
    Navigate by either clicking entities in the list or using the breadcrumbs
  </p>
</div>

For each entity various actions are available in the footer, to see more details just click "Table Browser" or to show highlight an entity in the assist click "Assist" .

The same SQL preview panel is shown for search results in the top search bar, from there you can use the footer action or just drag the entry into the editor.

<img width="850" height="450" data-gifffer="https://cdn.gethue.com/uploads/2018/05/Top_Search_Drag.gif"  />

## New File Context Popover

There's a new File Context Popover in town! You can access it from the left assist panel or directly from within the editor. Just like the SQL Context Popover you can navigate the tree through the listing or the title breadcrumb. For files it'll show a preview allowing you to quickly look at a sample of a file contents without leaving your task at hand. For more details about a file or folder just click the "File Browser" link in the footer.

[<img src="https://cdn.gethue.com/uploads/2018/05/HDFS_Context_From_Assist.png"/>][1]

In the editor you can replace an existing path with a new one by clicking "Insert in the editor" from the footer actions.

<img width="846" height="568" data-gifffer="https://cdn.gethue.com/uploads/2018/05/HDFS_Context_Change_Path_2.gif"  />

## Table Browser Refresh

In Hue 4.3 we've also made various improvements to the Table Browser. The focus has been on simplification with plain language titles and labels. The database, table and columns lists are new and similar to the ones found in the new SQL context popover. The description editor is new with automatic detection of links and we've added editable custom key-value pairs from Navigator.

[<img src="https://cdn.gethue.com/uploads/2018/05/Table_Browser_map_2.png"/>][2]

There's a new relationships tab that's available when Hue is configured with Navigator Optimizer. Based on statistics from popular joins it shows you related tables and which columns are the most popular ones in the joins.

[<img src="https://cdn.gethue.com/uploads/2018/05/Table_Browser_Relationships.png"/>][3]

We hope that these new improvements will help you explore and manage your data. As always, if you have any questions or feedback, feel free to comment here, on the [hue-user][4] list or [@gethue][5]!

 [1]: https://cdn.gethue.com/uploads/2018/05/HDFS_Context_From_Assist.png
 [2]: https://cdn.gethue.com/uploads/2018/05/Table_Browser_map_2.png
 [3]: https://cdn.gethue.com/uploads/2018/05/Table_Browser_Relationships.png
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue
