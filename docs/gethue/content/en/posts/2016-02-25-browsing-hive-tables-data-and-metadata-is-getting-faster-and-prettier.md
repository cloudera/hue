---
title: Browsing Hive tables data and metadata is getting faster and prettier
author: admin
type: post
date: 2016-02-25T19:25:35+00:00
url: /browsing-hive-tables-data-and-metadata-is-getting-faster-and-prettier/
sf_sidebar_config:
  - left-sidebar
sf_social_sharing:
  - 1
sf_background_image_size:
  - cover
sf_page_title_text_style:
  - light
sf_page_title_bg:
  - none
sf_no_breadcrumbs:
  - 1
sf_page_title_style:
  - standard
sf_page_title:
  - 1
sf_detail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_thumbnail_type:
  - none
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
sf_left_sidebar:
  - Sidebar-2
categories:
---

Hue continues to boost the experience of SQL users with its improved autocompletes, smarter assist panel, [SQL notebooks][1]... and now a revamped Hive Metastore Browser.

The app is now single page and offers speed and more accessible statistics and data preview. See more of the improvements below or take a look at the following video demo.

{{< youtube MykO9McaxCk >}}

### New UI

**Fresh restart**

The front-end has been rewritten to be slicker and more user-friendly. More information is displayed and navigating across tabs is seamless as it no longer entails a page refresh.

<figure><a href="https://cdn.gethue.com/uploads/2016/02/blog-57-metastore-table.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-57-metastore-table-1024x511.png" /></a><figcaption>Table specific page after</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2016/02/blog-55-metastore-table.png.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-55-metastore-table.png-1024x511.png" /></a><figcaption>Table specific page before</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/02/blog-57-metastore-tables.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-57-metastore-tables-1024x511.png" /></a><figcaption>List of tables page after</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2016/02/blog-55-metastore-tables.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-55-metastore-tables-1024x514.png" /></a><figcaption>List of tables page before</figcaption></figure>

&nbsp;

**Easy edition**

Table and column comments can be edited in a single click.

<a href="https://cdn.gethue.com/uploads/2016/02/blog-edit-comments.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-edit-comments.png" /></a>

**Getting pretty**

Scrolling bars are not flaky and ugly like in the previous version. They are invisible by default, and subtle when displayed

<figure><a href="https://cdn.gethue.com/uploads/2016/02/blog-57-scrollbar-e1456443073846.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-57-scrollbar-e1456443073846.png" /></a><figcaption>New</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2016/02/blog-55-scrollbar.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-55-scrollbar.png" /></a><figcaption>Old</figcaption></figure>

&nbsp;

**Creation wizards**

We also refreshed the wizard for creating tables and databases quickly, whether designing the schema manually or automatically from a sample file.

<a href="https://cdn.gethue.com/uploads/2016/02/blog-57-create-table.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-57-create-table-1024x545.png"  /></a>

&nbsp;

### Speed

&nbsp;

**Single page app**: first, now the initial page loads very quickly and fetches asynchronously the list of tables, table statistics, data sample, partition list. We are not blocking anymore until everything is queried in Hive. Subsequent navigation clicks will trigger only 1 or 2 calls to the server, instead of reloading all the page resources again. As an added bonus, the browser history now works on all the pages.

<a href="https://cdn.gethue.com/uploads/2016/02/meta-slow-1024x260.png"><img src="https://cdn.gethue.com/uploads/2016/02/meta-slow-1024x260.png" /></a>
<a href="https://cdn.gethue.com/uploads/2016/02/meta-quick.png"><img src="https://cdn.gethue.com/uploads/2016/02/meta-quick.png" /></a>

**Caching**: The new assist caches all the Hive metadata. The pages listing tables and database also point to the same cache, as well as the editor autocomplete. This means that now the fetching of thousand of Hive tables and databases will only happen once. On the Hive side, these calls have even been optimized for taking seconds instead of previously minutes ([HIVE-7575][2]).

<a href="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1.png" ><img src="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1.png" /></a>

**Don't freeze my browser**: on top of the caching, Hue is now much smarter thanks to its custom foreachVisible Ko Js [link] binding that displays only the elements visible on the screen. For example if the user has a list of 5000 tables, only tens of them will actually be rendered (the rendering is a costly part). The binding operates a sliding window of top of all this data, supports scrolling and won't block your browser tab or even crash it anymore when displaying large list of objects.

<a href="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each.png" ><img src="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each.png" /></a>

### Data rich

**Statistics**

Stats are easier to access than before. Most of the database and table metadata are displayed on top. Top values, min, max can also be retrieved and refreshed directly from the UI. Links to HDFS locations are automatically added.<a href="https://cdn.gethue.com/uploads/2016/02/blog-metastore-stats.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-metastore-stats.png" /></a>

<a href="https://cdn.gethue.com/uploads/2016/02/blog-col-stats.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-col-stats.png" /></a>

&nbsp;

**Preview data**

The first few rows of table data are displayed on the first page to provide users with a convenient quick preview.

<a href="https://cdn.gethue.com/uploads/2016/02/blog-metastore-preview-data.png" ><img src="https://cdn.gethue.com/uploads/2016/02/blog-metastore-preview-data-1024x466.png" /></a>

**Preview partitions**

Partitions keys and a sample of partition values can also be found on the main page. Advanced users can filter and query all the partitions in the [partition browser][3].

<a href="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21.png" ><img src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21-1024x224.png" /></a>

&nbsp;

The Hue team hopes that these new features will make your SQL data search and discovery easier! The metastore app will keep getting better by making data partitions and indexes easier to access and by adding more table, column, usage, top queries statistics. More is on a way, with a brand new SQL Editor!

Feel free to send feedback on the [hue-user][4] list or [@gethue][5]!

[1]: https://gethue.com/bay-area-bike-share-data-analysis-with-spark-notebook-part-2/
[2]: https://issues.apache.org/jira/browse/HIVE-7575
[3]: https://gethue.com/filter-sort-browse-hive-partitions-with-hues-metastore/
[4]: http://groups.google.com/a/cloudera.org/group/hue-user
[5]: https://twitter.com/gethue
