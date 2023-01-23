---
title:  Hue 4.11 and its new dialects and features are out!
author: Hue Team
type: post
date: 2023-01-23T00:00:00+00:00
url: /blog/2023-01-23-hue-4.11-hplsql-sparksql-iceberg/
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

The Hue Team is glad to thanks all the contributors and release Hue 4.11!

<a href="https://cdn.gethue.com/uploads/2021/02/hue-4.9.png">
  <img src="https://cdn.gethue.com/uploads/2021/02/hue-4.9.png" />
</a>

&nbsp;

**Note: This is the last Hue release supporting Python2.7. From future releases, Hue will support Python3.8+**


Here is a summary of the [main improvements](/categories/version-4.11/) of 4.11 on top of the previous [4.10](/blog/hue-4-10-sql-scratchpad-component-rest-api-small-file-importer-slack-app/) release:


#### Supporting Iceberg Syntax in Hue importer

Apache Iceberg is a high-performance format for huge analytic tables. Now you can create a Iceberg Table through Hue importer.
We’ve also updated the autocomplete and syntax checker for Hive and Impala to support the latest Iceberg syntax.

Read more about the [Creating Iceberg tables in Hue](https://gethue.com/blog/2022-10-11-creating-iceberg-tables-in-hue/).

![Iceberg Hue integration](https://cdn.gethue.com/uploads/2022/10/iceberg1.gif)


#### SparkSQL Support

We now have a dedicated autocomplete and syntax checker available for Spark SQL! It supports all Spark SQL statement types up to date with version 3.3.1.

On top of this we’ve also included the UDF library for Spark SQL, accessible in the autocomplete as well as the right assist panel. It covers documentation of the built in functions of Spark SQL 3.3.1.


#### HPL/SQL Support

HPL/SQL is an Apache open source procedural extension for SQL for Hive users. It has its own grammar. It is included with Apache Hive from version 2.0. 

You can enable the HPL/SQL dialect via desktop/conf/hue.ini config file section.
        
        [notebook]
        [[interpreters]]
        [[[hplsql]]]
        name=Hplsql
        interface=hiveserver2

Read more about the [HPL/SQL Support](https://gethue.com/blog/2022-02-01-hplsql-support/).

![Example](https://cdn.gethue.com/uploads/2022/02/Hplsql_example1.png)


#### Tech stack & Tooling

- [Create SQL tables from excel files](https://gethue.com/blog/2021-11-15-create-sql-tables-from-execl-files/)
- [Access your data in ABFS without any credential keys](https://gethue.com/blog/2021-09-21-access-your-data-in-abfs-without-any-credential-keys/)
- [Create Phoenix tables in Just 2 steps](https://gethue.com/blog/2021-08-17-create-phoenix-tables-in-just-2-steps/)
- [Open In Importer and Copy Path Options in Filebrowser](https://gethue.com/blog/2021-08-10-open-in-importer-and-copy-path-options-in-filebrowser/)
- [Create SQL tables on the fly with zero clicks](https://gethue.com/blog/2021-07-26-create-sql-tables-on-the-fly-with-zero-clicks/)
- [Azure Storage sharing by leveraging SAS tokens so that your users don’t need credentials](https://gethue.com/blog/2021-06-30-how-to-use-azure-storage-rest-api-with-shared-access-sginature-sas-tokens/)


It has more than 650+ commits and 100+ bug fixes! For more details on all the changes, check out the [release notes](https://docs.gethue.com/releases/release-notes-4.11.0/).

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