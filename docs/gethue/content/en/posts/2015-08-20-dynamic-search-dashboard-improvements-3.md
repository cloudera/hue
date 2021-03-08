---
title: Dynamic Search Dashboard improvements!
author: admin
type: post
date: 2015-08-20T14:33:17+00:00
url: /dynamic-search-dashboard-improvements-3/
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

[Apache Solr][1] is getting easier to use! This new version of the Search app provides a general improved dashboard experience by refreshing only the widgets that changed and integrating better with live indexing. A series of additional new functionalities are detailed below.

See it all in action in the video demo and the [Bike Data analysis with Analytics Facets widgets][2] and [Real time indexing of Tweet with Spark Streaming][3] posts!

&nbsp;

{{< youtube P4uhBLDKbZ0 >}}

&nbsp;

### Live filtering when moving on the map

Points close to each other are grouped together and will expand when zooming-in. A Yelp-like search filtering experience can also be created by checking the box.

[<img src="https://cdn.gethue.com/uploads/2015/08/search-marker-map.png" />][4]

&nbsp;

&nbsp;

### Edit indexed records and link to original documents

Indexed records can be directly edited in the Grid or HTML widgets by admins.

Links to the original documents can also be inserted. Add to the record a field named 'link-meta' that contains some json describing the URL or address of a table or file that can be open in the [HBase Browser][5], [Metastore App][6] or File Browser:

Any link

<pre><code class="javascript">{'type': 'link', 'link': 'gethue.com'}</code></pre>

HBase Browser

<pre><code class="javascript">{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527'}

{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1'}

{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1', 'col': 'c1'}

</code></pre>

File Browser

<pre><code class="javascript">{'type': 'hdfs', 'path': '/data/hue/file.txt'}</code></pre>

Metastore

<pre><code class="javascript">{'type': 'hive', 'database': 'default', 'table': 'sample_07'}</code></pre>

<img src="https://cdn.gethue.com/uploads/2015/08/search-link-1024x630.png" />

&nbsp;

&nbsp;

### Export/import/Share saved dashboards

Dashboard can be selected and exported as a Hue document (a 'json' file', like in the [Oozie Editor][7]) directly from the interface. This allow to back-up them more easily until we introduce git support. It is also convenient for transferring dashboards between clusters.

<img src="https://cdn.gethue.com/uploads/2015/08/search-export-1024x411.png" />

<img src="https://cdn.gethue.com/uploads/2015/08/search-import-1024x196.png" />

&nbsp;

### Save and reload the full search query definition

Current selected facets and filters, query strings can be saved with a name within the dashboard. These are useful for defining "cohorts" or pre-selection of records and quickly reloading them.

<img src="https://cdn.gethue.com/uploads/2015/08/search-query-def-1024x507.png" />

### 'Fixed' or 'rolling' time window filtering

Real time indexing can now shine with the rolling window filter and the automatic refresh of the dashboard every N seconds. See it in action in the [real time Twitter indexing with Spark streaming][3] post.

<img src="https://cdn.gethue.com/uploads/2015/08/search-rolling-time.png" /><img src="https://cdn.gethue.com/uploads/2015/08/search-fixed-time.png" />

&nbsp;

### Full mode Player display

The dashboard experience is even more real with this new browser full screen mode (and even better with full screen with the F11 key).

<img src="https://cdn.gethue.com/uploads/2015/08/search-full-mode-1024x504.png" />

&nbsp;

### Preview of nested Analytics facets

Solr 5.1 is seeing new [Analytics Facets][8]. A beta support for them has been added and can be enabled in the hue.ini with:

<pre><code class="bash">[search]

latest=true

</code></pre>

A more comprehensive demo is available on the [BikeShare data visualization][2] post.

<img src="https://cdn.gethue.com/uploads/2015/08/search-nested-facet-1024x304.png" /> <img src="https://cdn.gethue.com/uploads/2015/08/search-hit-widget.png" />

&nbsp;

&nbsp;

So it is time to create more [dashboards][9]! Feel free to send feedback on the [hue-user][10] list or [@gethue][11]!

[1]: http://lucene.apache.org/solr/
[2]: https://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/
[3]: https://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
[4]: https://cdn.gethue.com/uploads/2015/08/search-marker-map.png
[5]: https://gethue.com/hbase-browsing-with-doas-impersonation-and-kerberos/
[6]: https://gethue.com/category/metastore/
[7]: https://gethue.com/exporting-and-importing-oozie-workflows/
[8]: http://yonik.com/solr-subfacets/
[9]: http://demo.gethue.com/search/new_search
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
[11]: https://twitter.com/gethue
