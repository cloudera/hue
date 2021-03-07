---
title: Export and import your Search dashboards
author: admin
type: post
date: 2015-02-06T17:56:26+00:00
url: /export-and-import-your-search-dashboards/
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
<span style="color: #ff0000;">Update August 2015</span>: It is not much easier to import or export your [dashboards][1], it is the same interface as the [Oozie workflows exporter][2].

&nbsp;

**Using Hue 3.8 or CDH5.4**

20000013 is the id you can see in the URL of the dashboard. If you don't specify -pks it will export all your dashboards.

<pre><code class="bash">

./build/env/bin/hue dumpdata search.Collection -indent 2 -pks=20000013 -natural > data.json

</code></pre>

**Using Hue 3.7 or less**

<pre><code class="bash">./build/env/bin/hue dumpdata search -indent 2 > data.json

</code></pre>

&nbsp;

then

<pre><code class="bash">./build/env/bin/hue loaddata data.json

</code></pre>

&nbsp;

And that's it, the dashboards with the same IDs will be refreshed with the imported ones!

[<img src="https://cdn.gethue.com/uploads/2015/02/search-dashboard-list-1024x298.png" />][3]

&nbsp;

**Note**:

If using CM, export this variable in order to point to the correct database:

<pre><code class="bash">HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id

echo $HUE_CONF_DIR

export HUE_CONF_DIR</code></pre>

Where <id> is the most recent ID in that process directory for hue-HUE_SERVER.

&nbsp;

Have any questions? Feel free to contact us on [hue-user][4] or [@gethue][5]!

 [1]: https://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr
 [2]: https://gethue.com/exporting-and-importing-oozie-workflows/
 [3]: https://cdn.gethue.com/uploads/2015/02/search-dashboard-list.png
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue
