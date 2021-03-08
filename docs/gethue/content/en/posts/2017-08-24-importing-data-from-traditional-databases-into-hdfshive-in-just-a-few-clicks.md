---
title: Importing data from traditional databases into HDFS/Hive in just a few clicks
author: admin
type: post
date: 2017-08-24T14:57:19+00:00
url: /importing-data-from-traditional-databases-into-hdfshive-in-just-a-few-clicks/
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
ampforwp-amp-on-off:
  - default
sf_social_sharing:
  - 1
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
categories:
  - Version 4
  - Tutorial
---

<span style="font-weight: 400;">There are exciting new features coming in <a href="https://gethue.com/hue-4-1-is-out/">Hue 4.1</a> and later in CDH 6 next year. One of which is Hue’s brand new tool to import data from relational databases to HDFS file or Hive table using <a href="http://sqoop.apache.org/">Apache Sqoop</a> 1. It enables us to bring large amount of data into the cluster in just few clicks via interactive UI. This Sqoop connector was added to the existing </span>[<span style="font-weight: 400;">import data wizard</span>][1] <span style="font-weight: 400;">of Hue.</span>

&nbsp;

<span style="font-weight: 400;">In the past, importing data using Sqoop command line interface could be a cumbersome and inefficient process. The task expected users to have a good knowledge of Sqoop . For example they would need put together a series of required parameters with specific syntax that would result in errors easy to make. Often times getting those correctly can take a few hours of work. Now with Hue’s new feature you can submityour Sqoop job in minutes. The imports run on YARN and are scheduled by Oozie. This tutorial offers a step by step guide on how to do it.</span>

&nbsp;

{{< youtube c4K6p99TN_g >}}

## <span style="font-weight: 400;">Tutorial</span>

### <span style="font-weight: 400;">What you’ll need</span>

<span style="font-weight: 400;">First you’ll need to have a running cluster with Apache Sqoop, Apache YARN, Apache  Oozie and Hue configured in it.</span>

<span style="font-weight: 400;">Next you’ll need to install your database specific JDBC jars. To do so place them in a directory somewhere on HDFS.</span>

And to get the MySQL autocomplete would need to configure the Lib RDBMS and notebook: <https://gethue.com/custom-sql-query-editors/>

<img class="aligncenter wp-image-4937" src="https://cdn.gethue.com/uploads/2017/08/sqoop-fb-one.png"/>

<span style="font-weight: 400;">Additionally, you would need to turn on the feature by setting enable_sqoop to true under the indexer section in the </span>[<span style="font-weight: 400;">Hue ini</span>][2]<span style="font-weight: 400;">.</span>

<img class="aligncenter wp-image-4938" src="https://cdn.gethue.com/uploads/2017/08/sqoop-ini-two.png"/>

**Note:**

<span style="font-weight: 400;">If using Cloudera Manager, check how to add properties in hue.ini safety valve and put the above parameter value there.</span>

&nbsp;

### <span style="font-weight: 400;">Selecting source Tables</span>

<span style="font-weight: 400;">Now let’s get started! </span>

<span style="font-weight: 400;">In this tutorial, we’ll be importing a table from Teradata to Apache Hive. Click on the hamburger menu on the left pane and select the option on the bottom-left corner of your screen to navigate to Hue’s indexer section. Select External Database from the Type drop-down.</span>

<img class="aligncenter wp-image-4939" src="https://cdn.gethue.com/uploads/2017/08/sqoop-select-three.png"/>

<span style="font-weight: 400;">There are two modes for selecting the database:</span>

<img class="aligncenter wp-image-4940" src="https://cdn.gethue.com/uploads/2017/08/sqopp-source-four.png"/>

<li style="font-weight: 400;">
  <span style="font-weight: 400;">Pre-configured - Allows you to quickly select the databases which are already configured in Hue by the admin.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">Custom- Allows you to access any database you want by providing the necessary credentials in a true self service mode.</span>
</li>

<span style="font-weight: 400;">Note: The JDBC option in either of the modes allows us to point to database using JDBC specific credentials.</span>

<img class="aligncenter wp-image-4941" src="https://cdn.gethue.com/uploads/2017/08/sqoop-credentials-five.png"/>

<span style="font-weight: 400;">We’ll choose the custom mode for now, give the database credentials and initiate a Test Connection. Once the test passes, a dropdown gets populated with list of database names. On database selection, the list of table names populates up. On table selection, a quick preview comes handy. You can also check the All Tables option to import all the tables of a particular database in one go.</span>

&nbsp;

### <span style="font-weight: 400;">Selecting Destination</span>

<span style="font-weight: 400;">Once we are done with the source page, click on Next to navigate to the destination page. Here, select the Destination type which could be a HDFS file or Hive table. Also select all the database specific jars which are needed by Sqoop to run the import job. Since we selected Teradata, we’ll select all the teradata-specific jars.</span>

<img class="aligncenter wp-image-4942" src="https://cdn.gethue.com/uploads/2017/08/sqoop-jars-six.png"/>

<span style="font-weight: 400;">We can also add extra options like mapper number, output data format, delimiters, verbose mode, split-by option, compress mode, etc to our import job. This is explained in detail in documentation section.</span>

<img class="aligncenter wp-image-4943" src="https://cdn.gethue.com/uploads/2017/08/sqoop-properties-seven.png"/>

<span style="font-weight: 400;">We can even rename column names and filter out the columns which are not needed by unchecking the Keep checkbox.</span>

<img class="aligncenter wp-image-4944" src="https://cdn.gethue.com/uploads/2017/08/sqoop-fields-8.png"/>

<span style="font-weight: 400;">Now, let’s click on the Submit button. On doing so, a Sqoop job is generated which could be tracked in </span>[<span style="font-weight: 400;">Hue’s Job Browser</span>][3]<span style="font-weight: 400;">. </span>

<img class="aligncenter wp-image-4945" src="https://cdn.gethue.com/uploads/2017/08/sqoop-job-10.png"/>

<span style="font-weight: 400;">After the completion of the job, we can leverage </span>[<span style="font-weight: 400;">Hue’s Editor</span>][4] <span style="font-weight: 400;">for data processing and query analytics by executing Hive/Impala queries on the freshly imported data.</span>

<img class="aligncenter wp-image-4946" src="https://cdn.gethue.com/uploads/2017/08/sqoop-query-11.png"/>

## <span style="font-weight: 400;">Documentation</span>

### <span style="font-weight: 400;">Assembling the lib directory yourself</span>

<span style="font-weight: 400;">We’ll need all the required libraries for the Sqoop import job to execute. The requirement is specific to the database which is being used. The jars needed for some of the popular databases are listed below:</span>

- **Oracle:** <span style="font-weight: 400;">oracle-connector-java.jar</span>
- **MySQL:** <span style="font-weight: 400;">mysql-connector-java.jar</span>
- **Teradata:** <span style="font-weight: 400;">teradata-connector-java.jar, sqoop-connector-teradata-1.3c5.jar, tdgssconfig.jar, terajdbc4.jar</span>
- **PostgreSQL:** <span style="font-weight: 400;">postgresql-connector-java.jar</span>

### <span style="font-weight: 400;">Settings</span>

<span style="font-weight: 400;">Properties provide many other options to further tune the import operations to suit your specific workload.</span>

- **Libs:** <span style="font-weight: 400;">Database specific libraries needed by Sqoop 1</span>
- **Mappers:** <span style="font-weight: 400;">Uses n map tasks to import in parallel</span>
- **Split By:** <span style="font-weight: 400;">Column of the table used to split work units</span>
- **Verbose Mode:** <span style="font-weight: 400;">Print more information while working</span>
- **Compress Mode:** <span style="font-weight: 400;">Enables compression</span>
- **Format:** <span style="font-weight: 400;">Data can be imported in 3 different formats: text, avro, sequence</span>
- **Fields:** <span style="font-weight: 400;">Sets the field separator character (enabled only when format is text)</span>
- **Line:** <span style="font-weight: 400;">Sets the end-of-line character (enabled only when format is text)</span>
- **Optionally Enclosed By:** <span style="font-weight: 400;">Sets a field enclosing character (enabled only when format is text)</span>

&nbsp;

### <span style="font-weight: 400;">Supported Databases</span>

<span style="font-weight: 400;">Any database which is supported by Sqoop 1.</span>

&nbsp;

### <span style="font-weight: 400;">Troubleshooting</span>

<span style="font-weight: 400;">During the importing process, datatypes of the columns could be changed to HDFS/Hive compatible datatypes. When importing a table, the primary key is used to create the splits for mapper. If there is no primary key, the split-by column needs to be chosen explicitly; failing to do so results in import failure. While doing an all-table import, if all the tables don’t have primary key, the import job fails. Also, if for some reason the job fails, you can figure out the reason for failure from the logs in job tracker. For further assistance, please visit </span>[<span style="font-weight: 400;">https://sqoop.apache.org/docs/1.4.6/</span>][5]

&nbsp;

[1]: https://gethue.com/sql-autocomplete-popup-revamp-and-new-create-table-wizard/
[2]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
[3]: https://gethue.com/browsers/
[4]: https://gethue.com/sql-editor/
[5]: https://sqoop.apache.org/docs/1.4.6/
