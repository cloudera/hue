---
title:  Hue 4.11 and its new dialects and features are out!
author: Hue Team
type: post
date: 2023-01-23T00:00:00+00:00
url: /blog/hue-4-11-hplsql-sparksql-iceberg/
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
  - Release

---

Hi Data Explorers,

The Hue team is glad to release Hue 4.11. Thanks to all the contributors!

<a href="https://cdn.gethue.com/uploads/2021/02/hue-4.9.png">
  <img src="https://cdn.gethue.com/uploads/2021/02/hue-4.9.png" />
</a>

&nbsp;

**Note: Hue 4.11 is the last release to support Python 2.7. New releases will be based on Python 3.8 and higher.**


Here's a summary of [what's new](/categories/version-4.11/) in Hue 4.11:


#### Ability to import and query Iceberg tables from Hue

Apache Iceberg is a high-performance table format and extends multifunction analytics to a petabyte scale for multi-cloud and hybrid use cases. You can now create an Iceberg table using the Hue Importer.

We've also updated the autocomplete and syntax checker for Hive and Impala to support the latest Iceberg syntax when you write queries.

For more information, see [Creating Iceberg tables in Hue](https://gethue.com/blog/2022-10-11-creating-iceberg-tables-in-hue/).

![Iceberg-Hue integration](https://cdn.gethue.com/uploads/2022/10/iceberg1.gif).


#### SparkSQL improvements

Hue leverages Apache Livy 3 to support Spark SQL queries in Hue on the Apache Spark 3 engine. Booting a new Livy session was slow, and took around 30-45s. Hue now caches the session details per user for a faster query experience. Caching session details also helps in autocompleting databases, tables, and column names, improving the search experience.

Hue automatically cleans up unused Livy sessions.

Hue has a dedicated autocomplete and syntax checker for Spark SQL. Hue supports all Spark SQL statement types, up-to-date with version 3.3.1.

We've also integrated the UDF library for Spark SQL in the autocomplete code, as well as in the right assist panel. The inline help includes all built-in functions of Spark SQL 3.3.1.

![functioning SparkSQL query editor](https://cdn.gethue.com/uploads/2023/01/sparksql_left_right_assist.gif)


#### Added support for HPL/SQL

HPL/SQL is an Apache open source procedural extension for SQL for Hive users. It has its own grammar. It is included with Apache Hive from version 2.0. 

You can enable the HPL/SQL dialect by adding the following lines in the desktop/conf/hue.ini configuration file:
        
        [notebook]
        [[interpreters]]
        [[[hplsql]]]
        name=Hplsql
        interface=hiveserver2

Read more about the [HPL/SQL Support](https://gethue.com/blog/2022-02-01-hplsql-support/).

![Example](https://cdn.gethue.com/uploads/2022/02/Hplsql_example1.png)


#### Improvements to the tech stack and tooling

- [Create SQL tables from excel files](https://gethue.com/blog/2021-11-15-create-sql-tables-from-execl-files/)
- [Access your data in ABFS without any credential keys](https://gethue.com/blog/2021-09-21-access-your-data-in-abfs-without-any-credential-keys/)
- [Create Phoenix tables in Just 2 steps](https://gethue.com/blog/2021-08-17-create-phoenix-tables-in-just-2-steps/)
- [Open In Importer and Copy Path Options in Filebrowser](https://gethue.com/blog/2021-08-10-open-in-importer-and-copy-path-options-in-filebrowser/)
- [Create SQL tables on the fly with zero clicks](https://gethue.com/blog/2021-07-26-create-sql-tables-on-the-fly-with-zero-clicks/)
- [Azure Storage sharing by leveraging SAS tokens so that your users don’t need credentials](https://gethue.com/blog/2021-06-30-how-to-use-azure-storage-rest-api-with-shared-access-sginature-sas-tokens/)


This release of Hue has 650+ commits and 100+ bug fixes. For a complete list, see the [release notes](https://docs.gethue.com/releases/release-notes-4.11.0/).

Go grab it and give it a spin!

* Docker
    ```
    docker run -it -p 8888:8888 gethue/4.11.0
    ```
* Kubernetes :
    ```
    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue
    ```
* [demo.gethue.com](demo.gethue.com)
* [Tarball](https://cdn.gethue.com/downloads/hue-4.11.0.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.11.0.zip)

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Onwards!

Ayush from the Hue Team