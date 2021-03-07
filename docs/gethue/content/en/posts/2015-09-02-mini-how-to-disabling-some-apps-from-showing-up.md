---
title: 'Mini how-to: disabling some apps from showing up'
author: admin
type: post
date: 2015-09-02T15:58:56+00:00
url: /mini-how-to-disabling-some-apps-from-showing-up/
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
In the Hue ini [configuration file][1], in the `[desktop]` section, you can enter the names of the app to hide:

&nbsp;

<pre><code class="bash">[desktop]

\# Comma separated list of apps to not load at server startup.

app_blacklist=beeswax,impala,security,filebrowser,jobbrowser,rdbms,jobsub,pig,hbase,sqoop,zookeeper,metastore,spark,oozie,indexer

</code></pre>

&nbsp;

And the main menu will go from

[<img src="https://cdn.gethue.com/uploads/2015/09/menu-standard-1024x18.png" />][2]

to

[<img src="https://cdn.gethue.com/uploads/2015/09/menu-disabled-1024x19.png" />][3]

&nbsp;

You can see a live demo of [enabling only the Search App][4].

&nbsp;

**Note**

Some apps might currently still depend on another app and you will get an error if you disable them. For example, 'beeswax' app is used by the 'impala' app.

**Note**

You can find the list of the app names on the `/desktop/dump_config` page.

&nbsp;

 [1]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [2]: https://cdn.gethue.com/uploads/2015/09/menu-standard.png
 [3]: https://cdn.gethue.com/uploads/2015/09/menu-disabled.png
 [4]: https://gethue.com/solr-search-ui-only/
