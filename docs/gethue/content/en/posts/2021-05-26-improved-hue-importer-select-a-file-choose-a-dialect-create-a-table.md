---
title: Improved Hue Importer -- Select a file, choose a dialect, create a table
author: Hue Team
type: post
date: 2021-05-26T00:00:00+00:00
url: /blog/2021-05-26-improved-hue-importer-select-a-file-choose-a-dialect-create-a-table
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
  - Version 4.10
  - Development
  - Query

---

If you’ve ever struggled with configuring Hue to allow your users to create new SQL tables from CSV files on their own in the public Cloud, you’ll be happy to learn that this is now much easier.

If you're a pro Hue user, then you might be familiar with the Hue [Importer](https://docs.gethue.com/developer/api/rest/#data-importer). It lets you create tables from a file. Until now, the file had to be available on [HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) or cloud object storage, such as [S3](https://gethue.com/introducing-s3-support-in-hue/) or [ABFS](https://docs.gethue.com/administrator/configuration/connectors/#azure-file-systems). Now you can browse and select files from your computer to create tables with different SQL [dialects](https://docs.gethue.com/administrator/configuration/connectors/) in Hue. Apache Hive, Apache Impala, Apache Phoenix, MySql dialects are supported.

### Goal

* Upload files using the Hue Importer independent of the source.

### Why
* Not everyone has access to HDFS or S3/ABFS. Often, Business Analysts need to quickly analyze data sets that they have on their computers and skip data cleanup or other data engineering tasks.
* This feature enables you to import files from your computer and create tables in a few clicks.

### Steps to create a table

![Importer direct upload steps gif](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_steps.gif)

### Workflow
![Importer direct upload steps app diagram](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_workflow-2.png)

### Files and APIs

  * We have used three APIs to implement this feature.
    * [Guess_format](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/api3.py#L121) (to guess the file format)
    * [Guess_field_types](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/api3.py#L228) (to guess the column types)
    * [Importer_submit](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/api3.py#L444) (to create a table)
  * If you are curious about how various SQL dialects have been implemented, then take a look at the [sql.py](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/indexers/sql.py) file.  

  **Note-** Currently, Hue supports smaller CSV files containing a few thousand rows.


### Intermediate steps
  * step 1
  ![Importer direct upload step1](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_step1.png)  
You select a file, Hue guesses the file format, identifies the delimiters, and generates a table preview.  
  * step 2
  ![Importer direct upload step2](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_step2-2.png)  
You select a SQL dialect and Hue auto-detects the column data types. You can edit column names and their data type.  


Now it’s time to play with this feature in the latest Hue or at [demo.gethue.com](https://demo.gethue.com/hue/indexer/importer).  
</br>
</br>
This project gladly welcome [contributions](https://github.com/cloudera/hue/#development) for supporting more SQL dialects.  
Any feedback or question? Feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Onwards!

Ayush from the Hue Team
