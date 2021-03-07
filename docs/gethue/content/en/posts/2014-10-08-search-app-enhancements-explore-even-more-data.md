---
title: 'Search App Enhancements: Explore even more Data'
author: admin
type: post
date: 2014-10-08T19:12:46+00:00
url: /search-app-enhancements-explore-even-more-data/
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
slide_template:
  - default
categories:
---

Hi Big Data Explorers,

Hue [Search dashboards][1] introduced new ways to quickly explore a lot of data by drag & dropping some graphical widgets and leveraging Solr capabilities. The application received a lot of feedback and has been greatly improved.

Here is a short video detailing all the new stuff:

{{< youtube K6YVZq8wymw >}}

&nbsp;

You can see a quick summary of the main novelties below:

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1-1024x596.png"  />][2]

&nbsp;

**Top Bar**

It was re-organized in order to split widgets displaying records or facets.

<img src="https://cdn.gethue.com/uploads/2014/10/hue-bar-1024x64.png" />

&nbsp;

**Three new widgets**

- Heatmap
- Tree
- Marker Map

Based on the Pivot facet feature of Solr, the Heatmap and Tree let you explore in 2D or nDimensions your data. For example you can plot the distribution of  OS by Browser by country, IP by cities… They are both clickable, meaning you can filter the results by selecting certain values.

<img src="https://cdn.gethue.com/uploads/2014/10/hue-heatmap-1024x254.png" />

<img src="https://cdn.gethue.com/uploads/2014/10/hue-tree-1-1024x214.png"  />

&nbsp;

The Marker Map is great for automatically plotting the result rows on a leaflet.

<img src="https://cdn.gethue.com/uploads/2014/10/hue-marker.png" />

**Field analysis**

Index fields can now have their terms and stats retrieved in a single click. Accessible from the list of fields of the Grid Layout. Values can also be in/out excluded, prefix filtered or faceted by another field.

<img class="aligncenter  wp-image-1746" src="https://cdn.gethue.com/uploads/2014/10/hue-analysist-terms.png" />  <img class="aligncenter  wp-image-1745" src="https://cdn.gethue.com/uploads/2014/10/hue-analysis-stats.png" />

**Exclude facets**

Previously it was only possible to included selected facets. Now a little minus ‘-’ appears on hover on each value and let you filter out some values. These can be combined for filtering out some large values that make your graph difficult to read.

<img src="https://cdn.gethue.com/uploads/2014/10/hue-exclude-0.png"  /> <img src="https://cdn.gethue.com/uploads/2014/10/hue-exclude-1.png"  />

**Note**

The indexer is now smarter and will pick up the good ZooKeeper server: search examples are installable in one click (a few more clicks still with [Kerberos/Sentry][3]).

&nbsp;

**What’s next?**

New facets like ‘this value & up!’, map plotting of new type of data, making it easier to [create and index data][4], autocomplete (and ideally one day [Analytics Facets][5]) are in the pipeline!

&nbsp;

We hope that you like the latest additions to the Search App. Feel free to continue to send us questions and feedback to the [hue-user][6] list or [@gethue][7]!

&nbsp;

[1]: https://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr
[2]: https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1.png
[3]: https://gethue.com/hadoop-tutorial-kerberos-security-and-sentry-authorization-for-solr-search-app/
[4]: https://gethue.com/analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr/
[5]: http://heliosearch.org/solr-facet-functions/
[6]: http://groups.google.com/a/cloudera.org/group/hue-user
[7]: https://twitter.com/gethue
