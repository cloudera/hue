---
title: Realtime catalog search with Hue and Apache Atlas
author: Hue Team
type: post
date: 2019-06-20T00:14:35+00:00
url: /realtime-catalog-search-with-hue-and-apache-atlas/
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
With the latest Hue (future 4.5 release), we are glad to announce that Hue integrates with [Apache Atlas][1] as backend to enable SQL users for real time data catalog searching.

Previously Hue&#8217;s catalog was powered by Cloudera Navigator only, but now the API is generic and could potentially support other Catalog services too. The [nice end user experience][2] for finding content to query can be transparently re-used.

<span style="font-weight: 400;">With this first integration, Hue lists properties of entities like classifications and provides real time search among thousands of possible tables or databases:</span>

<a href="https://cdn.gethue.com/uploads/2019/06/Newly_createdTable_with_classification2.png"><img src="https://cdn.gethue.com/uploads/2019/06/Newly_createdTable_with_classification2.png" /></a>

Here is the search UI from Atlas for Data Stewards:
<a href="https://cdn.gethue.com/uploads/2019/06/Atlas_Search_for_new_tag.png"><img src="https://cdn.gethue.com/uploads/2019/06/Atlas_Search_for_new_tag.png" /></a>

It is accessible from the top global search bar of the interface and offers free text search of SQL databases, tables, fields(columns), classifications and saved queries(Hue documents) similar to Hue-Navigator integration.

<span style="font-weight: 400;">Here are a few examples to get you started:</span>

<li style="font-weight: 400;">
  <span style="font-weight: 400;"><strong>&#8216;sample&#8217; → Any table or Hue document with prefix &#8216;sample&#8217; will be returned</strong>
  <a href="https://cdn.gethue.com/uploads/2019/06/Free_text_search_sample.png"><img src="https://cdn.gethue.com/uploads/2019/06/Free_text_search_sample.png" /></a><br /> </span>
</li>
 <li> <strong>&#8216;type:database&#8217;<span style="font-weight: 400;">→ </span>List all databases on this cluster</strong>

  <a href="https://cdn.gethue.com/uploads/2019/06/Search_By_Type_Database.png"><img src="https://cdn.gethue.com/uploads/2019/06/Search_By_Type_Database.png" /></a>

  </li>

<li> <strong>&#8216;type:table &#8217;<span style="font-weight: 400;">→ </span>List all tables on this cluster</strong>

  <a href="https://cdn.gethue.com/uploads/2019/06/Atlas_search_for_type_table-1.png"><img src="https://cdn.gethue.com/uploads/2019/06/Atlas_search_for_type_table-1.png" /></a>

  </li>

  <li> <strong>&#8216;type:field name&#8217;<span style="font-weight: 400;">→ </span>List tables with field(column): &#8216;name&#8217;</strong>

  <a href="https://cdn.gethue.com/uploads/2019/06/SearchWithType_field_name.png"><img src="https://cdn.gethue.com/uploads/2019/06/SearchWithType_field_name.png" /></a>

  </li>

  <li> <strong>&#8216;tag:classification\_testdb5&#8217; or &#8216;classification:classification\_testdb5&#8217;<span style="font-weight: 400;">→ </span> List entities with classification &#8216;classification_testdb5&#8217;</strong>

  <a href="https://cdn.gethue.com/uploads/2019/06/SearchBy_Classification_Tag.png"><img src="https://cdn.gethue.com/uploads/2019/06/SearchBy_Classification_Tag.png" /></a>

  </li>

  <li> <strong>&#8216;owner:admin&#8217;<span style="font-weight: 400;">→ </span>List all tables owned by &#8216;admin&#8217; user</strong>

  <a href="https://cdn.gethue.com/uploads/2019/06/SearchBy_ownerAdmin.png"><img src="https://cdn.gethue.com/uploads/2019/06/SearchBy_ownerAdmin.png" /></a>

  </li>


&nbsp;

<span style="font-weight: 400;">As always, thank you for your interest and if you have any questions please feel free to comment and send feedback here</span><span style="font-weight: 400;"> or </span>[<span style="font-weight: 400;">@gethue</span>][10]<span style="font-weight: 400;">!</span>

&nbsp;

&nbsp;

 [1]: https://atlas.apache.org/
 [2]: https://gethue.com/simplifying-the-end-user-data-catalog-search/
 [3]: https://cdn.gethue.com/uploads/2019/06/Newly_createdTable_with_classification2.png
 [4]: https://cdn.gethue.com/uploads/2019/06/Atlas_Search_for_new_tag.png
 [5]: https://cdn.gethue.com/uploads/2019/06/Search_By_Type_Database.png
 [6]: https://cdn.gethue.com/uploads/2019/06/Atlas_search_for_type_table-1.png
 [7]: https://cdn.gethue.com/uploads/2019/06/SearchWithType_field_name.png
 [8]: https://cdn.gethue.com/uploads/2019/06/SearchBy_Classification_Tag.png
 [9]: https://cdn.gethue.com/uploads/2019/06/SearchBy_ownerAdmin.png
 [10]: https://twitter.com/gethue
