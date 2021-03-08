---
title: 'Querying & Exploring the Instacart dataset Part 1: Ingesting the data'
author: admin
type: post
date: 2019-03-22T01:02:02+00:00
url: /querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/
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
  # - Version 4.4

---
Self-service exploratory analytics is one of the most common use cases of the Hue users. In this tutorial, let's see how to get started on the analysis. We will use the free [Instacart][1] dataset and start with the [Importer][2] feature.

## Getting the data

This steps was made particularly easy by Instacart. Just go on their [dataset page of 3 million orders][3] and download the 200 MBs.

## Making it queryable

Next step is not always trivial. In our case, there is no data team adding the dataset to the [Data Catalog][4] for us, but hopefully we can use the Data Importer of Hue.

## Upload to the object store

First upload the dataset to the cluster. This is easy via the [File Browser][5].

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_upload.png"/>][6]

Then, the next step is to uncompress the archive. This is also convenient to do in two clicks via the File Browser. Note that the processing is happening in the cluster, not on your machine, and it is an efficient way to upload multiple files.

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_extract.png"/>][7]

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_extraction.png"/>][8]

## Load via the importer

Via the top left Hamburger icon that will open this menu, click in the very bottom. Or use '+' icon in the top of the left SQL Assist. This will open-up the Importer.

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_importer.png"/>][9]

From there, go select the 'orders' file that was extracted from the Instacart archive. A File and Table previews are shown automatically.

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_importer_step1.png"/>][10]

Click next to go to step 2. Hue auto-detects the types of the columns and checks if the names are valid. In more advanced scenarios, the user could also change the type of the table (e.g. by selecting the [Apache Parquet][11] or [Apache Kudu][12] format)

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_importer_step2.png"/>][13]

Click 'Submit' and afterwards the table will appear in the Data Catalog!

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_table_created.png"/>][14]

**Note**: for advanced users, the SQL command to create the table and import the data can also be printed.

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_cart_show_command.png"/>][15]

## In next episode

Repeat with the 'products' file and now you are ready to start querying! We will start from there in the upcoming post of this series.

**Note**: the importer supports multiple outputs like Solr [Dashboards][16] or inputs like [regular databases][17].

&nbsp;

As usual feel free to comment here or to send feedback to the [hue-user][18] list or [@gethue][19]!

[<img src="https://cdn.gethue.com/uploads/2019/03/insta_basic_querying.png"/>][20]

 [1]: https://www.instacart.com
 [2]: https://gethue.com/import-data-to-be-queried-via-the-self-service-drag-drop-create-table-wizard/
 [3]: https://www.instacart.com/datasets/grocery-shopping-2017
 [4]: https://gethue.com/improved-sql-exploration-in-hue-4-3/
 [5]: https://gethue.com/browsers/
 [6]: https://cdn.gethue.com/uploads/2019/03/insta_upload.png
 [7]: https://cdn.gethue.com/uploads/2019/03/insta_extract.png
 [8]: https://cdn.gethue.com/uploads/2019/03/insta_extraction.png
 [9]: https://cdn.gethue.com/uploads/2019/03/insta_importer.png
 [10]: https://cdn.gethue.com/uploads/2019/03/insta_importer_step1.png
 [11]: https://parquet.apache.org/
 [12]: https://kudu.apache.org/
 [13]: https://cdn.gethue.com/uploads/2019/03/insta_importer_step2.png
 [14]: https://cdn.gethue.com/uploads/2019/03/insta_table_created.png
 [15]: https://cdn.gethue.com/uploads/2019/03/insta_cart_show_command.png
 [16]: https://gethue.com/search-dashboards/
 [17]: https://gethue.com/importing-data-from-traditional-databases-into-hdfshive-in-just-a-few-clicks/
 [18]: http://groups.google.com/a/cloudera.org/group/hue-user
 [19]: https://twitter.com/gethue
 [20]: https://cdn.gethue.com/uploads/2019/03/insta_basic_querying.png
