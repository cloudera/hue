---
title: Get a mode to allow easy profiling of requests
author: admin
type: post
date: 2018-09-14T18:28:42+00:00
url: /get-a-mode-to-allow-easy-profiling-of-requests/
sf_caption_position:
  - caption-right
sf_right_sidebar:
  - Sidebar-1
sf_left_sidebar:
  - Sidebar-2
sf_sidebar_config:
  - left-sidebar
sf_related_articles:
  - 1
sf_social_sharing:
  - 1
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4

---
<span style="font-weight: 400;">If Hue is running slow, how to find out the root cause? Now, in 4.3, Hue comes with a handy tool for profiling HTTP requests and responses thanks to </span>[<span style="font-weight: 400;">Django Debug Toolbar</span>][1] <span style="font-weight: 400;">and </span>[<span style="font-weight: 400;">Django Debug Panel</span>][2]<span style="font-weight: 400;">.</span>

<img class="" /><img class="" /><img class="" />[<img class="aligncenter wp-image-5551" src="https://cdn.gethue.com/uploads/2018/09/image1.png"/>][3]

&nbsp;

[<img class="aligncenter wp-image-5552" src="https://cdn.gethue.com/uploads/2018/09/image2.png"/>][4]

<span style="font-weight: 400;">As the screenshots above, the Django Debug panel captures requests and list them on the left column, and it provides a list of panels on the right column that display various debug information about the each of request/response, like version, time, settings, header, SQL, and static files. And when click on each of the panel, more detail information will display in the middle.</span>

<span style="font-weight: 400;">This tool replies on a Chrome extension, so use Chrome and install </span><span style="font-weight: 400;">Django Debug Panel</span>] <span style="font-weight: 400;">from Chrome store.</span>

<span style="font-weight: 400;">To enable this debug panel, set following to hue.ini. If you are using Cloudera Manager, put them in Safety Valve.</span>

<pre><code class="bash">

[desktop]

\# Enable or disable debug mode.

django_debug_mode=true

\# Allow use django debug tool with Chrome browser for debugging issue, django_debug_mode must be true also

enable_django_debug_tool=true

\# Comma separated list of users' username that allow to use django debug tool. If it is empty, all users are allowed.

django_debug_tool_users=admin,ying

</code></pre>

Reference:

[<span style="font-weight: 400;">https://github.com/jazzband/django-debug-toolbar</span>][1]

[<span style="font-weight: 400;">https://github.com/recamshak/django-debug-panel</span>][2]

[<span style="font-weight: 400;">https://issues.cloudera.org/browse/HUE-8139</span>][6]

 [1]: https://github.com/jazzband/django-debug-toolbar
 [2]: https://github.com/recamshak/django-debug-panel
 [3]: https://cdn.gethue.com/uploads/2018/09/image1.png
 [4]: https://cdn.gethue.com/uploads/2018/09/image2.png
 [6]: https://issues.cloudera.org/browse/HUE-8139
