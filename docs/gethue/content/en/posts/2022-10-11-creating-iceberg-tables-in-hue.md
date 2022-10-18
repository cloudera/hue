---
title:  Creating Iceberg tables in Hue
author: Hue Team
type: post
date: 2022-10-11T00:00:00+00:00
url: /blog/2022-10-11-creating-iceberg-tables-in-hue
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
  - Query

---

### Overview of Iceberg
[Apache Iceberg](https://iceberg.apache.org/) is a high-performance format for huge analytic tables. Iceberg brings the reliability and simplicity of SQL tables to big data, while making it possible for engines like Spark, Trino, Flink, Presto, Hive and Impala to safely work with the same tables, at the same time.

Hue supports various dialects such as Hive, Impala, SparkSQL, Phoenix, and so on. In the past year, Hue importer has been upgraded with new features and improvements. You can import [local files](/blog/2021-05-26-improved-hue-importer-select-a-file-choose-a-dialect-create-a-table/), [drag and drop files into the Hue importer](/blog/2021-07-26-create-sql-tables-on-the-fly-with-zero-clicks/), [create Phoenix tables](/blog/2021-08-17-create-phoenix-tables-in-just-2-steps/), and [create tables from excel files](/blog/2021-11-15-create-sql-tables-from-execl-files/) for these dialects in a few clicks. You just need to load the data and submit it. In this release, Hue supports creating Iceberg tables in Hive, and Impala dialects.

### Steps
1. Go to the Hue importer and select Remote file from drop down menu.
2. Select a file from which you want to create a table.
3. Click Next and select the Iceberg table option.
4. Configure the column types and tweak other parameters as needed.
5. Click Submit.


![Iceberg Hue integration](https://cdn.gethue.com/uploads/2022/10/iceberg1.gif)


You can try this feature in the latest Hue version.  
</br>
</br>
For feedback, questions, or suggestions, feel free to comment here or on the [Forum](https://discourse.gethue.com/) or on the [Discussion](https://github.com/cloudera/hue/discussions) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Onwards!

Ayush from the Hue Team
