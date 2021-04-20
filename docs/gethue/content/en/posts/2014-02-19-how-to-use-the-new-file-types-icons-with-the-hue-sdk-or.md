---
title: How to use the new file types icons with the Hue SDK or in standalone
author: admin
type: post
date: 2014-02-19T22:03:00+00:00
url: /how-to-use-the-new-file-types-icons-with-the-hue-sdk-or/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/77209676786/how-to-use-the-new-file-types-icons-with-the-hue-sdk-or
tumblr_gethue_id:
  - 77209676786
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
  <span>Hue 3.5+ ships with two font icon sets: Font Awesome 4 (</span><a href="http://fontawesome.io/">http://fontawesome.io/</a><span>) and the Hue Filetypes font that includes some basic file types you might need.</span>
</p>

The icons are available in the Hue [master][1] or in this [zip file][2]:

<img alt="" src="https://lh4.googleusercontent.com/43JXsa-J7epO0SzwjzPMQRCRM-2_EJLjiebZ___F6MDwIRAAg7MjfhYM21EKZgwECq2SKDcn-48-TI9DlJfvHRQabEEMyoFZZODBDMPL2Vi7cOo0wJ8PcTO9sQ" width="483px;" height="240px;" />

When you want to use the new icons in your app, you have first to import the Hue Filetypes css in your .mako template:

&nbsp;

<pre class="code">&lt;link href="/static/ext/css/hue-filetypes.css" rel="stylesheet"&gt;</pre>

and then define you icons with the same way you would do with Font Awesome.

<span>In our case you need to write a prefix (</span><span>hfo</span> <span>instead of </span><span>fa)</span>

&nbsp;

<pre class="code">&lt;i class="hfo .."&gt;&lt;/i&gt;</pre>

and then you can specify the icon you want. To render a JSON file icon for instance you should use

&nbsp;

<pre class="code">&lt;i class="hfo hfo-file-json"&gt;&lt;/i&gt;</pre>

&nbsp;

<span>You can also use the modifiers from Font Awesome, so you can create a larger rotated PDF icon like this:</span>

&nbsp;

<pre class="code">&lt;i class="hfo hfo-file-json fa-2x fa-rotate-90"&gt;&lt;/i&gt;</pre>

&nbsp;

<span>Which other icons would you like to see implemented? We would also be glad to contribute them </span>[<span>back</span>][2]<span>. Please let us </span>[<span>know</span>][3] <span>or</span>[<span>comment</span>][4]<span>!</span>

&nbsp;

 [1]: https://github.com/cloudera/hue
 [2]: https://cdn.gethue.com/downloads/HueFiletypes.zip
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
