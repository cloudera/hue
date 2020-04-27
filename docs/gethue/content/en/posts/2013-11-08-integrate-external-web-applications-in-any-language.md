---
title: Integrate external Web applications in any language
author: admin
type: post
date: 2013-11-08T13:36:00+00:00
url: /integrate-external-web-applications-in-any-language/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/66367939672/integrate-external-web-applications-in-any-language
tumblr_gethue_id:
  - 66367939672
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

<p id="docs-internal-guid-711cc362-37b7-d05c-55d3-ea64d369838b">
  Completed in <a href="http://gethue.tumblr.com/post/66661140648/hue-team-retreat-thailand">Thailand</a>, <a href="https://issues.cloudera.org/browse/HUE-826">HUE-826</a> brings a new way to integrate external Web application into Hue. Java apps or already existing websites can now be shown as a Hue app with little effort.
</p>

&nbsp;

{{< youtube Y1FT7yAJc7s >}}

&nbsp;

For example, let’s integrate Tableau:

<span>To create a new app:</span>

<pre class="code">build/env/bin/hue create_proxy_app my_hue <a href="http://gethue.com">http://gethue.com</a>
tools/app_reg/app_reg.py --install my_hue --relative-paths</pre>

<span>If you want to update the url later, change it in the ini:</span>

<pre class="code">[my_hue]
url=http://gethue.com</pre>

<span>As usual feel free to comment on the </span>[<span>hue-user</span>][1] <span>list or </span>[<span>@gethue</span>][2]<span>!</span>

[1]: http://groups.google.com/a/cloudera.org/group/hue-user
[2]: https://twitter.com/gethue
