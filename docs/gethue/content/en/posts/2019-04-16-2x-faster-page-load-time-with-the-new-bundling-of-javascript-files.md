---
title: 2x Faster page load time with the new bundling of JavaScript files
author: admin
type: post
date: 2019-04-16T15:54:50+00:00
url: /2x-faster-page-load-time-with-the-new-bundling-of-javascript-files/
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
  # - Version 4.5

---
Fast page loads are notorious for providing a much nicer user experience. Who likes to wait or have a slow display of the page?

In the continuous offer to render Hue snappier and at the same time modernize and improve the developer experience, JavaScript files are now bundled together and are importer only when needed (under the cover this is done by leveraging <https://webpack.js.org/>).

This is a lot of requests not happening anymore when opening Hue the first time!

&nbsp;

<h2 style="text-align: center;">
  188 requests and 13s (before) vs 89 requests and 7s (after)
</h2>

&nbsp;

The change is already in [master][1] and will be fully part of Hue 4.5.

&nbsp;

Note: these static files are then cached and served when using a balancer like [NGINX][2] and since the [version 4.0][3] Hue is a single page app with no reloads.

&nbsp;

<figure>
  <a href="https://cdn.gethue.com/uploads/2019/04/hue_load_before.png"><img src="https://cdn.gethue.com/uploads/2019/04/hue_load_before.png" /></a>
  <figcaption>Before: seeing a lot of requests when opening the editor page</figcaption>
</figure>

&nbsp;

  [<img src="https://cdn.gethue.com/uploads/2019/04/hue_load_after-1.png" />][5]

&nbsp;

As usual feel free to comment here or [@gethue][6]!

&nbsp;

 [1]: https://github.com/cloudera/hue
 [2]: https://gethue.com/using-nginx-to-speed-up-hue-3-8-0/
 [3]: https://gethue.com/hue-4-and-its-new-interface-is-out/
 [4]: https://cdn.gethue.com/uploads/2019/04/hue_load_before.png
 [5]: https://cdn.gethue.com/uploads/2019/04/hue_load_after-1.png
 [6]: https://twitter.com/gethue
