---
title: "Data Catalog"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

Hue Browsers power the Data Catalog. They let you easily search, glance and perform actions on data or jobs in Cloud or on premise clusters.

The browsers can be "enriched" with [Search and Tagging](http://gethue.com/improved-sql-exploration-in-hue-4-3/) by metadata services.

## SQL Tables

The Table Browser enables you to manage the databases, tables, and partitions of the metastore shared by the Hive and Impala. You can perform the following operations:

-   Search and display metadata like tags and additional description from [Catalog backends]({{% param baseURL %}}administrator/configuration/external/).

-   Databases
    -   Select a database
    -   Create a database
    -   Drop databases

-   Tables
    -   Create tables
    -   Browse tables
    -   Drop tables
    -   Browse table data and metadata (columns, partitions...)
    -   Import data into a table
    -   [Filter, Sort and Browse Partitions](http://gethue.com/filter-sort-browse-hive-partitions-with-hues-metastore/)


## Data Importer

The goal of the importer is to allow ad-hoc queries on data not yet in the clusters and simplifies self-service analytics.

If you want to import your own data instead of installing the sample
tables, open the importer from the left menu or from the little `+` in the left assist.


To learn more, watch the video on [Data Import Wizard](http://gethue.com/import-data-to-be-queried-via-the-self-service-drag-drop-create-table-wizard/).

**Note** Files can be dragged & dropped, selected from HDFS or S3 (if configured), and their formats are automatically detected. The wizard also assists when performing advanced functionalities like table partitioning, Kudu tables, and nested types.

### Traditional Databases

Import data from relational databases to HDFS file or Hive table using Apache Sqoop. It enables to bring large amount of data into the cluster in just few clicks via interactive UI. The imports run on YARN and are scheduled by Oozie.

Learn more about it on the [ingesting data from traditional databases](http://gethue.com/importing-data-from-traditional-databases-into-hdfshive-in-just-a-few-clicks/) post.

### Indexing

In the past, indexing data into Solr to then explore it with a [Dynamic Dashboard](http://gethue.com/search-dashboards/) has been quite difficult. The task involved writing a Solr schema and a Morphlines file then submitting a job to YARN to do the indexing. Often times getting this correct for non trivial imports could take a few days of work. Now with Hue's new feature you can start your YARN indexing job in minutes.

[Read more about it here](http://gethue.com/easy-indexing-of-data-into-solr/).


## Dashboards
Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.

Read more about [Dashboards](http://gethue.com/search-dashboards/).

### Concepts

Simply drag & drop widgets that are interconnected together. This is great for exploring new datasets or monitoring without having to type.

### Querying

The search box support live prefix filtering of field data and comes with a Solr syntax autocomplete in order to make the querying intuitive and quick. Any field can be inspected for its top values of statistic. This analysis happens very fast as the data is indexed.

### Autocomplete

The top search bar offers a [full autocomplete](http://gethue.com/intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/) on all the values of the index.

### More Like This
The “More like This” feature lets you selected fields you would like to use to find similar records. This is a great way to find similar issues, customers, people... with regard to a list of attributes.


## Files

The File Browser application lets you interact with these file systems HDFS, S3 or ADLS:

-   Create files and directories, upload and download files, upload zip
    archives and extract them, rename, move, and delete files and directories.
-   Change a file's or directory's owner, group, and
    permissions.
-   View and edit files as text or binary.
-   Create external tables or export query results

### HDFS

Hue is fully compatible with HDFS and is handy for browsing, peeking at file content, upload or downloading data.

### S3

Hue can be setup to read and write to a configured S3 account, and users get autocomplete capabilities and can directly query from and save data to S3 without any intermediate moving/copying to HDFS.

[Read more about it](http://gethue.com/introducing-s3-support-in-hue/).

### ADLS

Learn more about it on the [ADLS integration post](http://gethue.com/browsing-adls-data-querying-it-with-sql-and-exporting-the-results-back-in-hue-4-2/).

**Note** ADLS gen2 is currently not supported.

### GFS

Google file system is currently not supported.

### HBase Browser

We'll take a look at the [HBase Browser App](http://gethue.com/the-web-ui-for-hbase-hbase-browser).

**Note**: With just a few changes in the [Python API](https://github.com/cloudera/hue/blob/master/apps/hbase/src/hbase/api.py),
the HBase browser could be compatible with Apache Kudu or Google Big Table.


#### SmartView

The smartview is the view that you land on when you first enter a table.
On the left hand side are the row keys and hovering over a row reveals a
list of controls on the right. Click a row to select it, and once
selected you can perform batch operations, sort columns, or do any
amount of standard database operations. To explore a row, simple scroll
to the right. By scrolling, the row should continue to lazily-load cells
until the end.

#### Adding Data

To initially populate the table, you can insert a new row or bulk upload
CSV/TSV/etc. type data into your table.


On the right hand side of a row is a '+' sign that lets you insert
columns into your
row

#### Mutating Data

To edit a cell, simply click to edit inline.

If you need more control or data about your cell, click “Full Editor” to
edit.

In the full editor, you can view cell history or upload binary data to
the cell. Binary data of certain MIME Types are detected, meaning you
can view and edit images, PDFs, JSON, XML, and other types directly in
your browser!

Hovering over a cell also reveals some more controls (such as the delete
button or the timestamp). Click the title to select a few and do batch
operations:

If you need some sample data to get started and explore, check out this
howto create [HBase table
tutorial](http://gethue.com/hadoop-tutorial-how-to-create-example-tables-in-hbase).


#### Smart Searchbar

The "Smart Searchbar" is a sophisticated tool that helps you zero-in on
your data. The smart search supports a number of operations. The most
basic ones include finding and scanning row keys. Here I am selecting
two row keys with:


    domain.100, domain.200


Submitting this query gives me the two rows I was looking for. If I want
to fetch rows after one of these, I have to do a scan. This is as easy
as writing a '+' followed by the number of rows you want to fetch.


    domain.100, domain.200 +5


Fetches domain.100 and domain.200 followed by the next 5 rows. If you're
ever confused about your results, you can look down below and the query
bar and also click in to edit your query.

The Smart Search also supports column filtering. On any row, I can
specify the specific columns or families I want to retrieve. With:


    domain.100[column_family:]   


I can select a bare family, or mix columns from different families like
so:


    domain.100[family1:, family2:, family3:column_a]


Doing this will restrict my results from one row key to the columns I
specified. If you want to restrict column families only, the same effect
can be achieved with the filters on the right. Just click to toggle a
filter.


Finally, let's try some more complex column filters. I can query for
bare columns:


    domain.100[column_a]

This will multiply my query over all column families. I can also do
prefixes and scans:


    domain.100[family: prefix* +3]


This will fetch me all columns that start with prefix\* limited to 3
results. Finally, I can filter on range:


    domain.100[family: column1 to column100]


This will fetch me all columns in 'family:' that are lexicographically
\>= column1 but <= column100. The first column ('column1') must be a
valid column, but the second can just be any string for comparison.

The Smart Search also supports prefix filtering on rows. To select a
prefixed row, simply type the row key followed by a star \*. The prefix
should be highlighted like any other searchbar keyword. A prefix scan is
performed exactly like a regular scan, but with a prefixed row.


    domain.10* +10


Finally, as a new feature, you can also take full advantage of the
[HBase filtering](denied:about:blank)language, by typing your filter
string between curly braces. HBase Browser autocompletes your filters
for you so you don't have to look them up every time. You can apply
filters to rows or scans.


    domain.1000 {ColumnPrefixFilter('100-') AND ColumnCountGetFilter(3)}


This doc only covers a few basic features of the Smart Search. You can
take advantage of the full querying language by referring to the help
menu when using the app. These include column prefix, bare columns,
column range, etc. Remember that if you ever need help with the
searchbar, you can use the help menu that pops up while typing, which
will suggest next steps to complete your query.

## Solr Indexes / Collections

Solr indexes can be created and are listed in the interface.

## Sentry Permissions

Sentry roles and privileges can directly be edited in the Security interface.

**Note** Sentry is going to be replaced by Apache Ranger in [HUE-8748](https://issues.cloudera.org/browse/HUE-8748).

### SQL

[Hive UI](http://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/).

### Solr

[Solr](http://gethue.com/ui-to-edit-sentry-privilege-of-solr-collections/) privileges can be edited directly via the interface.

For listing collections, query and creating collection:

    Admin=*->action=*
    Collection=*->action=*
    Schema=*->action=*
    Config=*->action=*

### Kafka

Kafka topics can be listed.

**Note** This is currently an experimental feature.


## Jobs

The Job Browser application lets you to examine multiple types of jobs
jobs running in the cluster. Job Browser presents the job and
tasks in layers for quick access to the logs and troubleshooting.

### YARN (Spark, MapReduce, Tez)

Any job running on the Resource Manager will be automatically listed. The information will be fetched accordingly if the job got moved to one of the history servers.

### Impala Queries

There are three ways to access the Query browser:

* Best: Click on the query ID after executing a SQL query in the editor. This will open the mini job browser overlay at the current query. Having the query execution information side by side the SQL editor is especially helpful to understand the performance characteristics of your queries.
* Open the mini job browser overlay and navigate to the queries tab.
* Open the job browser and navigate to the queries tab.

Query capabilities

* Display the list of currently running queries on the user's current Impala coordinator and a certain number of completed queries based on your configuration (25 by default).
* Display the summary report which shows physical timing and memory information of each operation of the explain plan. You can quickly find bottlenecks in the execution of the query which you can resolve by replacing expensive operations, repartitioning, changing file format or moving data.
* Display the query plan which is a condensed version of the summary report in graphical form
* Display the memory profile which contains information about the memory usage during the execution of the query. You can use this to determine if the memory available to your query is sufficient.
* Display the profile which gives you physical execution of the query in great detail. This view is used to analyze data exchange between the various operator and the performance of the IO (disk, network, CPU). You can use this to reorganize the location of your data (on disk, in memory, different partitions or file formats).
* Manually close an opened query.

Read more about it on [Browsing Impala Query Execution within the SQL Editor
](http://gethue.com/browsing-impala-query-execution-within-the-sql-editor/).

### Workflow / Schedules (Oozie)

List submitted workflows, schedules and bundles.

### Livy / Spark

List Livy sessions and submitted statements.
