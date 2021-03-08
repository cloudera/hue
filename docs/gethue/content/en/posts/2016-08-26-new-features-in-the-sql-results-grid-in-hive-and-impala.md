---
title: Accessing and Refining your SQL results in Hive and Impala
author: admin
type: post
date: 2016-08-26T06:14:17+00:00
url: /new-features-in-the-sql-results-grid-in-hive-and-impala/
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

---
Aloha Big Questions Askers!

The [SQL Editor][1] in [Hue 3.11][2] brings a completely re-written result grid that improves the performances allowing big tables to be displayed without the browser to crash, plus some nifty tools for you.

You can now lock some rows: this will help you compare data with other rows. When you hover a row id, you get a new lock icon. If you click on it, the row automatically sticks to the top of the table.

<img data-gifffer="https://cdn.gethue.com/uploads/2016/08/lock_rows.gif"  />

<h4 style="margin-top: 100px;">
  The column list follows the result grid, can be filtered by data type and can be resized (finally!)
</h4>

<img data-gifffer="https://cdn.gethue.com/uploads/2016/08/column_list.gif"  />

<h4 style="margin-top: 100px;">
  The headers of fields with really long content will follow your scroll position and always be visible
</h4>

<img class="aligncenter size-large wp-image-4373" data-gifffer="https://cdn.gethue.com/uploads/2016/08/headers.gif"  />

<h4 style="margin-top: 100px;">
  You can now search in the table and the results are highlighted
</h4>

You can activate the new search either by clicking on the magnifier icon on the results tab, or pressing Ctrl/Cmd + F

<img class="aligncenter size-large wp-image-4374" data-gifffer="https://cdn.gethue.com/uploads/2016/08/search.gif"  />

<h4 style="margin-top: 100px;">
  The virtual renderer display just the cells you need at that moment
</h4>

The table you see here has hundreds of columns

<img data-gifffer="https://cdn.gethue.com/uploads/2016/08/virtual_renderer.gif"  />

<h4 style="margin-top: 100px;">
  If the download to Excel or CSV takes too long, you will have a nice message now
</h4>

<img data-gifffer="https://cdn.gethue.com/uploads/2016/08/downloadwait.gif"  />

And Hue will tell you in the download has been truncated too!

[<img class="aligncenter size-medium wp-image-4441" src="https://cdn.gethue.com/uploads/2016/08/Screenshot-2016-08-25-19.37.26-300x129.jpg"  />][3]

As usual you can send feedback and participate on the [hue-user][4] list or [@gethue][5]!

&nbsp;

 [1]: https://gethue.com/sql-editor/
 [2]: https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/
 [3]: https://cdn.gethue.com/uploads/2016/08/Screenshot-2016-08-25-19.37.26.jpg
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue
