---
title: A better collaborative Data Warehouse Experience with SQL query sharing via links or gists
author: Romain
type: post
date: 2020-03-04T02:36:35+00:00
url: /blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/
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
Hi Data Crunchers,

For the [past 10 years](https://gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/), Hue's SQL Editor has been targeting the [SQL Data Warehouse Experience](https://gethue.com/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/). It recently got better support for typing SQL queries by showing [column keys](/2019-11-13-sql-column-assist-icons/). The latest improvement is about better collaboration.

Via the [document sharing](https://docs.gethue.com/user/concept/#sharing) capabilities and [query parameterization](https://docs.gethue.com/user/querying/#variables), Hue allows teams to build their own query bank of knowledge. To complement this, something quicker and easier is now also available: Public link & Gist sharing.


## Public links

Goal: quickly sharing parameterized saved reports, customer analyses links.

Public links are the same as in Google documents. They only require the recipient to have a Hue login. People can then reuse the queries on their own by executing them to see the results, fork and adapt them.

* No need to select groups or list of individual users
* Read, write permissions
* Linked documents won't show up in your home
* Can be turned off globally
* Can be combined with traditional user/group sharing

Here is an example:

Saved queries can be shared directly via the editor or the left document assist. Notice that documents already shared are showing-up with a little person icon:

![Editor share menu](https://cdn.gethue.com/uploads/2020/03/editor_share_menu.png)

![Assist share menu](https://cdn.gethue.com/uploads/2020/03/editor_assist_share_menu.png)

Document preview is also smoother now and indicates owner, permissions and last update time:

![Editor share menu popup](https://cdn.gethue.com/uploads/2020/03/assist_document_popup.png)

Here is the sharing popup with the public link option on the top:

![Editor share menu popup](https://cdn.gethue.com/uploads/2020/03/editor_sharing_popup.png)


## SQL Snippet - Gist

Goal: quickly share SQL snippets, with a direct link to the SQL editor.

Answering a question via a query result? Showing some weird data to a slack channel? Gist are a great quick way to do that.

* Works with an SQL snippet: one or more statements
* The link automatically point to the editor and the SQL content
* The query is displayed in the friendlier [presentation mode](https://docs.gethue.com/user/querying/#presentation)
* Slack unfurling will show a mini preview (can be turned off globally)
* Gists are stored in a Gist directory in your home

Here is an example:

Select a portion of statements to quick share with a Slack channel:

![Editor share gist menu](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_menu.png)

The link to the SQL fragment is automatically generated:

![Editor share gist popup](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_popup.png)

Just paste the link in the Slack channel and users will get a mini preview:

![Open gist in Slack](https://cdn.gethue.com/uploads/2020/03/editor_gist_slack.png)

Clicking on the link will open-up the SQL selection:

![Open gist](https://cdn.gethue.com/uploads/2020/03/editor_gist_open_presentation_mode.png)



Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Romain, from the Hue Team
