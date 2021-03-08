---
title: More Solr Search dashboards possibilities
author: admin
type: post
date: 2015-03-30T17:22:54+00:00
url: /more-solr-search-dashboards-possibilities/
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
sf_remove_promo_bar:
  - 1
categories:
---

The [Search dashboards][1] got a series of new options and long awaited features in Hue 3.8. Here is a summary of the major improvements.

{{< youtube T1fPqlWhFiM >}}

&nbsp;

**Regular users can now also create dashboards**

Previously, only Hue admin could access the editor, which was not very practical.

[<img src="https://cdn.gethue.com/uploads/2015/03/search-create-menu.png" />][2]

&nbsp;

**Range & Up facet**

Interval facets on any type of data has been supported since the first versions. However, some use cases would benefit more of range facets with one upper or lower bound open. Think like getting all the logs younger than 1 day or restaurants with ratings above 4 stars.

[<img src="https://cdn.gethue.com/uploads/2015/03/search-and-up-1024x268.png" />][3]

&nbsp;

**2D maps**

The gradient map is handy for displaying the traffic by location. It now supports another dimension that way you can plot the Top Browsers, Operating Systems by country

[<img src="https://cdn.gethue.com/uploads/2015/03/search-2d-map.png"  />][4]

&nbsp;

**Multiple widgets using the same fields**

This feature is particularly useful for using a country code code field with several widgets or a date fields for a timeline and also a text facet. Previously each field could be used only once in a widget!

[<img src="https://cdn.gethue.com/uploads/2015/03/search-multi-names-1024x239.png" />][5]

&nbsp;

**Collection aliases**

All the aliased [group of collections][6] will now appear in the list of available collections. So just pick the name like any other collection. The UI also hides the core list by default to save some space.

[<img src="https://cdn.gethue.com/uploads/2015/03/search-aliases-1024x198.png" />][7]

&nbsp;

**Enable only the Search app**

Hue only uses the [standard Solr API][8]. This means that any Solr or Solr Cloud setup can also benefit from the dashboard UI. Here is how to customize Hue to only [show the Search app][9] and get started in a few clicks!

[<img src="https://cdn.gethue.com/uploads/2015/03/search-only-1024x530.png" />][10]

&nbsp;

**Export and import dashboard**

Until we get the builtin support for [exporting/importing][11] any Hue documents, here is a new way to [backup or move][12] your existing dashboard to other installations.

[<img src="https://cdn.gethue.com/uploads/2015/03/search-export-1024x353.png" />][13]

&nbsp;

**Next!**

A lot more is coming up, with a Date Widget for easily setting up a rolling timeline, more statistics and analytics facets!

Also in the pipeline is a revamp of the [indexer designer][14] for making collection index creation a 3-click operation.

Happy Searching!

&nbsp;

As usual feel free to comment on the [hue-user][15] list or [@gethue][16]!

[1]: https://gethue.com/search-app-enhancements-explore-even-more-data/
[2]: https://cdn.gethue.com/uploads/2015/03/search-create-menu.png
[3]: https://cdn.gethue.com/uploads/2015/03/search-and-up.png
[4]: https://cdn.gethue.com/uploads/2015/03/search-2d-map.png
[5]: https://cdn.gethue.com/uploads/2015/03/search-multi-names.png
[6]: http://blog.cloudera.com/blog/2013/10/collection-aliasing-near-real-time-search-for-really-big-data/
[7]: https://cdn.gethue.com/uploads/2015/03/search-aliases.png
[8]: https://cwiki.apache.org/confluence/display/solr/Searching
[9]: https://gethue.com/solr-search-ui-only/
[10]: https://cdn.gethue.com/uploads/2015/03/search-only.png
[11]: https://issues.cloudera.org/browse/HUE-1660
[12]: https://gethue.com/export-and-import-your-search-dashboards/
[13]: https://cdn.gethue.com/uploads/2015/03/search-export.png
[14]: https://gethue.com/analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr/
[15]: http://groups.google.com/a/cloudera.org/group/hue-user
[16]: https://twitter.com/gethue
