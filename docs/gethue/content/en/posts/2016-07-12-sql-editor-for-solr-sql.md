---
title: SQL Editor for Solr SQL
author: admin
type: post
date: 2016-07-12T14:29:47+00:00
url: /sql-editor-for-solr-sql/
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

Hue already integrates with Apache Solr and provide [Dynamic Search Dashboards][1]. With the [new SQL Editor][2] of Hue 3.10, Hue opens up to [any database][3], which is great as Solr 6 now provides a [SQL interface][4].

Here is demo where we query a Solr collection like we would query a regular Hive or Impala table.

&nbsp;

{{< youtube u4ctEYl5Mlo >}}

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/05/solr-sql-editor-1024x693.png"><img src="https://cdn.gethue.com/uploads/2016/05/solr-sql-editor-1024x693.png" /></a><figcaption>In the Editor</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/05/solr-sql-notebook-1024x691.png"><img class="wp-image-4110 size-large" src="https://cdn.gethue.com/uploads/2016/05/solr-sql-notebook-1024x691.png" /></a><figcaption>In the notebook</figcaption></figure>

&nbsp;

&nbsp;

As Solr SQL is pretty recent, there are some caveats, notably Solr lacks support of:

- SELECT \*
- WHERE close with a LIKE
- resultset pagination

which prevents a SQL UX experience comparable to the standard other databases (but we track it in [HUE-3686][7]).

&nbsp;

But we still hope that you play around with this new promising feature. If you have any questions, feel free to comment here or on the [hue-user][8] list, [Solr community][9] or [@gethue][10]!

[1]: https://gethue.com/dynamic-search-dashboard-improvements-3/
[2]: https://gethue.com/new-sql-editor/
[3]: https://gethue.com/custom-sql-query-editors/
[4]: http://yonik.com/solr-6/
[5]: https://cdn.gethue.com/uploads/2016/05/solr-sql-editor.png
[6]: https://cdn.gethue.com/uploads/2016/05/solr-sql-notebook.png
[7]: https://issues.cloudera.org/browse/HUE-3686
[8]: http://groups.google.com/a/cloudera.org/group/hue-user
[9]: http://lucene.apache.org/solr/resources.html
[10]: https://twitter.com/gethue
