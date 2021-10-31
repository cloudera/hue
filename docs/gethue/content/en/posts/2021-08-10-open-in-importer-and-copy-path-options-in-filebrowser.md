---
title: Open In Importer and Copy Path Options in Filebrowser
author: Hue Team
type: post
date: 2021-08-10T00:00:00+00:00
url: /blog/2021-08-10-open-in-importer-and-copy-path-options-in-filebrowser
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

We simplify object storage and DW integration. Now you can create a table from filebrowser, just select a file and click the "Open in Importer" option and also you can copy the path of a file by clicking the "Copy Path" option in fileborwser.

![Filebrowser Copy Path and Open In Importer Options](https://cdn.gethue.com/uploads/2021/08/Filebrowser_copypath_openinimporter.png)

If you want to create a table then you can use either "Open in Importer" option or [Importer](https://demo.gethue.com/hue/indexer/importer) directly but if you want a table from your SQL then just copy the path of a file as described above and use it in the [editor](https://demo.gethue.com/hue/editor/?type=1).

    create EXTERNAL TABLE book ( id BIGINT, isbn STRING, category STRING, publish_date TIMESTAMP, publisher STRING, price FLOAT ) 
    ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
    stored as textfile
    LOCATION  's3a://cldr-demo/books/books.csv';

You can try this feature in the latest Hue version or at [demo.gethue.com](https://demo.gethue.com/hue/filebrowser/).  
</br>
</br>
For feedback, questions, or suggestions, feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Onwards!

Ayush from the Hue Team