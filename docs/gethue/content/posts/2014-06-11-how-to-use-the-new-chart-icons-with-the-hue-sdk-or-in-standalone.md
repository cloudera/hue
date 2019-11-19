---
title: How to use the new chart icons with the Hue SDK or in standalone
author: admin
type: post
date: 2014-06-11T23:29:35+00:00
url: /how-to-use-the-new-chart-icons-with-the-hue-sdk-or-in-standalone/
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
slide_template:
  - default
categories:
  - Development

---
<p id="docs-internal-guid-2d78f639-4c29-7375-9428-f6c418c4470f">
  <span>Hue 3.6+ ships with three font icon sets: Font Awesome 4 (</span><a href="http://fontawesome.io/">http://fontawesome.io/</a><span>), the <a href="https://gethue.com/?p=408">Hue Filetypes font</a> and the Hue Chart font that includes some basic charts you might need.</span>
</p>

The icons are available in the Hue [master][1] or in this [zip file][2]:

<img src="https://cdn.gethue.com/uploads/2014/06/Screenshot-2014-03-31-13.12.38.png" width="733" height="238" class="alignnone" />

When you want to use the new icons in your app, you have first to import the Hue Charts css in your .mako template:

&nbsp;

<pre class="code">&lt;link href="/static/ext/css/hue-charts.css" rel="stylesheet"&gt;</pre>

and then define you icons with the same way you would do with Font Awesome.

<span>In our case you need to write a prefix (</span><span>hfo</span> <span>instead of </span><span>fa)</span>

&nbsp;

<pre class="code">&lt;i class="hcha .."&gt;&lt;/i&gt;</pre>

and then you can specify the icon you want. To render an area chart icon for instance you should use

&nbsp;

<pre class="code">&lt;i class="hcha hcha-area-chart"&gt;&lt;/i&gt;</pre>

&nbsp;

<span>You can also use the modifiers from Font Awesome, so you can create a larger rotated PDF icon like this:</span>

&nbsp;

<pre class="code">&lt;i class="hcha hcha-area-chart fa-2x fa-rotate-90"&gt;&lt;/i&gt;</pre>

&nbsp;

<span>Which other icons would you like to see implemented? We would also be glad to contribute them </span>[<span>back</span>][2]<span>. Please let us </span>[<span>know</span>][3] <span>or </span>[<span>comment</span>][4]<span>!</span>

&nbsp;

 [1]: https://github.com/cloudera/hue
 [2]: https://cdn.gethue.com/downloads/HueCharts.zip
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
