---
title: Admin improvements coming in 4.7!
author: Hue Team
type: post
date: 2020-04-07T02:36:35+00:00
url: /blog/2020-04-07-some-4-7-admin-improvements/
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
#  - Version 4.7

---

Hi SQL crunchers,

The upcoming 4.7 release brings a series of improvements to make the life of the admin better. Here is a selection:


![Config filtering](https://cdn.gethue.com/uploads/2020/04/4.7_admin_config_filter.png)

All the server properties are listed on the admin page as well as the location of the config page. This is a lot of parameters and sections! Now those can be spot light search via a filter.


![Admin user statuses](https://cdn.gethue.com/uploads/2020/04/4.7_admin_users_status.png)

The delete flow of a user now disables instead of deleting (to avoid losing the saved documents and queries). User admin page now displays ACTIVE and SUPERUSER statuses


![Active user](https://cdn.gethue.com/uploads/2020/04/cm_active_users.png)

The number of active users metric per API instance was revamped. Now it is possible to differentiate on a per instance basis instead of a global unique counter. More details in its [own post](https://gethue.com/hue-active-users-metric-improvements/).


![sharing modal](https://cdn.gethue.com/uploads/2020/04/4.7_sharing_popup.png)

The document sharing modal was restyled to be friendlier with proper full names of users and icons. This is a great collaboration improvement on top of the [Query Gist and Public Link sharing](https://gethue.com/blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/).




Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Romain from the Hue Team
