---
title: Create SQL tables from excel files
author: Hue Team
type: post
date: 2021-11-15T00:00:00+00:00
url: /blog/2021-11-15-create-sql-tables-from-execl-files
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

If you are a Hue user then you might be familiar with the Hue [Importer](https://docs.gethue.com/developer/api/rest/#file-import). It lets you create tables from a CSV file. Now you can also create SQL tables by importing Excel files into Hue.

We have 2 options for file import

1. [Direct Importer](/blog/2021-05-26-improved-hue-importer-select-a-file-choose-a-dialect-create-a-table/)

![Importer direct upload steps gif](https://cdn.gethue.com/uploads/2021/11/direct_importer_xlsx.gif)

**Note:** Supports (.xlsx) excel file type only.

2. [Remote Importer](https://gethue.com/hadoop-tutorial-create-hive-tables-with-headers-and)

![Importer remote upload steps gif](https://cdn.gethue.com/uploads/2021/11/remote_importer_xlsx1.gif)

**Note:** Python2 based Hue does not support remote excel file importer.

You can try this feature in the latest Hue version or at [demo.gethue.com](https://demo.gethue.com/hue/indexer/importer).  
</br>
</br>
For feedback, questions, or suggestions, feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Onwards!

Ayush from the Hue Team