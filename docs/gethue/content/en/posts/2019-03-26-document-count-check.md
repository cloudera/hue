---
title: 'Quick Task: Document Count Check'
author: admin
type: post
date: 2019-03-26T23:23:23+00:00
url: /document-count-check/
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
  # - Version 4.4

---
When Hue database has too many entries in certain tables, it will cause performance issue. Now Hue config check will help superuser to find this issue. Login as superuser and go to "Hue Administration", this sample screenshot will be displayed in the quick start wizard when the tables have too many entries.

[<img class="size-full wp-image-5802 aligncenter" src="https://cdn.gethue.com/uploads/2019/03/Doc2CountCheck.png"/>][1]

****

**Warning:** <span style="font-weight: 400;">Hue database Document2 has too many entries which may cause performance issue, please run command line tool to clean up.</span>

**Clean up Hue database:**

<li style="font-weight: 400;">
  <span style="font-weight: 400;">Stop the Hue service in Cloudera Manager: go to </span><b>Cluster</b><span style="font-weight: 400;"> > </span><b>Hue</b><span style="font-weight: 400;"> and select </span><b>Actions</b><span style="font-weight: 400;"> > </span><b>Stop</b><span style="font-weight: 400;">.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">Log on to the host of your Hue server.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">Go to Hue directory and run following clean up command</span>
</li>

<pre><code class="bash">cd /opt/cloudera/parcels/CDH/lib/hue # Hue home directory

./build/env/bin/hue desktop_document_cleanup

</code></pre>

Note: if using Cloudera Manager you probably need the instructions detailed in the [Hue Shell][2] post.

 [1]: https://cdn.gethue.com/uploads/2019/03/Doc2CountCheck.png
 [2]: https://gethue.com/quick-task-how-to-count-the-documents-of-a-user-via-the-shell/
