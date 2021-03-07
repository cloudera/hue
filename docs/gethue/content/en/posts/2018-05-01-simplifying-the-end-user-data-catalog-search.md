---
title: Simplifying the end user Data Catalog search
author: admin
type: post
date: 2018-05-01T14:23:28+00:00
url: /simplifying-the-end-user-data-catalog-search/
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
use_ampforwp_page_builder:
  - yes
amp-page-builder:
  - '{"rows":[],"totalrows":"1","totalmodules":"1","settingdata":{"front_class":"","front_css":""}}'
categories:
  - Version 4

---
## <span style="font-weight: 400;">Data Catalog Search</span>

<span style="font-weight: 400;">Before typing any query to get insights, users need to find and explore the correct datasets. The Data Catalog search </span><span style="font-weight: 400;">usability experience has been improved in each release since. It is accessible from th</span><span style="font-weight: 400;">e top bar of the interface and offers free text search of SQL tables, columns, tags and saved queries. This is particularly useful for quickly looking up a table among thousands or finding existing queries already analysing a certain dataset.</span>

<span style="font-weight: 400;">In this iteration, the search now provides more results directly via the 'Show more' link. Existing tags can be faceted simply by typing 'tags:'.</span>

<span style="font-weight: 400;">Some example of searches:</span>

<li style="font-weight: 400;">
  <span style="font-weight: 400;">usage → Returns any table matching 'usage' in its name, description or tags.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">type:view customer → Find the customer view</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">tax* tags:finance → List all the tables and views starting with tax and tagged with ‘finance’</span>
</li>

&nbsp;

[<img class="wp-image-5343 size-full aligncenter" src="https://cdn.gethue.com/uploads/2018/04/blog_top_search_.png"/>][1]

<p style="text-align: center;">
  <span style="font-weight: 400;">Searching all the available queries or data in the cluster</span>
</p>

<p style="text-align: center;">
  <a href="https://cdn.gethue.com/uploads/2018/04/blog_tag_listing.png"><img class="alignnone size-full wp-image-5341" src="https://cdn.gethue.com/uploads/2018/04/blog_tag_listing.png"/></a>
</p>

<p style="text-align: center;">
  <span style="font-weight: 400;">Listing the possible tags to filter on. This also works for 'types'.</span>
</p>

## <span style="font-weight: 400;">Unification and Caching of all SQL metadata </span>

<span style="font-weight: 400;">The list of tables and their columns is displayed in multiple part of the interface. This data is pretty costly to fetch and comes from different sources. In this new version, the information is now cached and reused by all the Hue components. As the sources are diverse, e.g. Apache Hive, Cloudera Navigator, Cloudera Optimizer those are stored into a single object, so that it is easier and faster to display without caring about the underlying technical details.</span>

&nbsp;

<span style="font-weight: 400;">In addition to editing the tags of any SQL objects like tables, views, columns... which has been available since version one, table descriptions can now also be edited. This allows a self service documentation of the metadata by the end users, which was not possible until know as directly editing Hive comments require some admin Sentry privileges which are not granted to regular users in a secure cluster.</span>

&nbsp;

<span style="font-weight: 400;">In the upcoming version,this information is also reused on the Catalog pages.</span>

[<img class="alignnone wp-image-5342 size-full" src="https://cdn.gethue.com/uploads/2018/04/blog_metadata.png"/>][2]

<p style="text-align: center;">
  <span style="font-weight: 400;">Showing all the common data now cached and unified for a slicker experience</span>
</p>

&nbsp;

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][3] list or [@gethue][4]!

 [1]: https://cdn.gethue.com/uploads/2018/04/blog_top_search_.png
 [2]: https://cdn.gethue.com/uploads/2018/04/blog_metadata.png
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
