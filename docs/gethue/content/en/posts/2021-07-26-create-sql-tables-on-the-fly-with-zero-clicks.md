---
title: Create SQL tables on the fly with zero clicks
author: Hue Team
type: post
date: 2021-07-26T00:00:00+00:00
url: /blog/2021-07-26-create-sql-tables-on-the-fly-with-zero-clicks
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
  - Version 4.11
  - Development
  - Query

---

Last month, we introduced [creating a table from the local file](/blog/2021-05-26-improved-hue-importer-select-a-file-choose-a-dialect-create-a-table/) using importer. [Previously](/import-data-to-be-queried-via-the-self-service-drag-drop-create-table-wizard/), creating a new table required you to set up a storage account such as HDFS, S3, or ADLS to upload data. The list of SQL dialects was also restrictive, with no support for Apache Phoenix. Now, creating a table is even easier. Just drag and drop a CSV file on the table listing, and Hue automatically creates a SQL table for you!

![Importer direct upload steps gif](https://cdn.gethue.com/uploads/2021/07/drag_and_drop_importer2.gif)


You can try this feature in the latest Hue version or at [demo.gethue.com](https://demo.gethue.com/hue/indexer/importer).  
</br>
</br>
For feedback, questions, or suggestions, feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Onwards!

Ayush from the Hue Team