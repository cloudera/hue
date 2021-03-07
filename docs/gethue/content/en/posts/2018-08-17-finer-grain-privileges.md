---
title: Finer grain privileges in the Sentry App
author: admin
type: post
date: 2018-08-17T18:43:24+00:00
url: /finer-grain-privileges/
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

---
Aloha Security junkies!

In an upcoming release of Hue we've added some Sentry finer grain privileges in the Security app and, as a bonus, we've embedded viewing privileges directly in the Table Browser.

<a href="https://cdn.gethue.com/uploads/2018/06/Screenshot-2018-06-22-13.46.38.jpg" target="_blank" rel="noopener noreferrer"><img src="https://cdn.gethue.com/uploads/2018/06/Screenshot-2018-06-22-13.46.38.jpg" alt="" width="600" /></a>

Accordingly to what object you are applying privileges to, you will get only the available options now.

<a href="https://cdn.gethue.com/uploads/2018/06/Screenshot-2018-06-22-13.34.58.jpg" target="_blank" rel="noopener noreferrer"><img src="https://cdn.gethue.com/uploads/2018/06/Screenshot-2018-06-22-13.34.58.jpg" alt="" width="600" /></a>

To summarize what's new, `CREATE` will work at the SERVER/DB scopes, while `REFRESH/ALTER/DROP` will work at the SERVER/DB/TABLE scopes.

We hope that these new improvements will help you manage better who can do what on your data. As always, if you have any questions or feedback, feel free to comment here, on the [hue-user][1] list or [@gethue][2]!

 [1]: http://groups.google.com/a/cloudera.org/group/hue-user
 [2]: https://twitter.com/gethue
