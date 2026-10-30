---
title: "Browsing"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

Browsers let you search, explore and import datasets, and monitor jobs.

You can enrich the browsers with an external catalog or metadata service. See the [connectors configuration](/administrator/configuration/connectors/).

## Catalogs

### Tables

The Table Browser lets you manage the databases, tables, and partitions of the metastore shared by Hive and Impala. You can perform the following operations:

-   Search and display metadata like tags and descriptions
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

### Data catalogs

Before you write a query, you need to find the right dataset. The Data Catalog search is in the top bar of the interface. It offers free text search of SQL tables, columns, tags and saved queries. This is particularly useful for quickly looking up a table among thousands or finding existing queries already analyzing a certain dataset.

Existing tags, descriptions and indexed objects show up automatically. Tags that you add are also sent back to the metadata server, and the metadata server search syntax is supported.

![Data Catalog top search](https://cdn.gethue.com/uploads/2018/04/blog_top_search_.png)

Searching all the available queries and data in the cluster.

![Data Catalog tags](https://cdn.gethue.com/uploads/2018/04/blog_tag_listing.png)

Listing the tags to filter on. This also works for types.

#### Unification of metadata

Hue shows the list of tables and their columns in multiple parts of the interface. This data comes from different sources, such as Apache Hive and Apache Atlas. Hue caches it in a single object and reuses it in all components, so it displays faster.

You can edit the tags of any SQL object, like tables, views and columns. You can also edit table descriptions. This lets you document the metadata yourself, without the admin privileges that editing Hive comments directly requires on a secure cluster.

![Data Catalog](https://cdn.gethue.com/uploads/2018/04/blog_metadata.png)

#### Search

By default, only tables and views are returned. To search for columns, partitions or databases, use the `type:` filter.

Examples of searches:

**Apache Atlas**

* `sample`: any table or Hue document with the prefix `sample`
* `type:database`: all databases on this cluster
* `type:table`: all tables on this cluster
* `type:field name`: tables with a field (column) named `name`
* `tag:classification_testdb5` or `classification:classification_testdb5`: entities with the classification `classification_testdb5`
* `owner:admin`: all tables owned by the `admin` user

**Cloudera Navigator** (deprecated in favor of the `[[catalog]]` configuration)

* `table:customer`: the `customer` table
* `table:tax* tags:finance`: all tables starting with `tax` and tagged with `finance`
* `owner:admin type:field usage`: all fields created by the `admin` user that match `usage`
* `parentPath:"/default/web_logs" type:FIELD originalName:b*`: all columns starting with `b` of the table `web_logs` in the database `default`

![Data Catalog Search](https://cdn.gethue.com/uploads/2019/06/SearchWithType_field_name.png)

Learn more on the [Search](http://gethue.com/realtime-catalog-search-with-hue-and-apache-atlas/).

#### Tagging

You can tag objects with names to categorize them and group them by project. Tags are searchable, which makes discovery easier.

![Data Catalog](https://cdn.gethue.com/uploads/2016/04/tags.png)

### Importing data

The Importer lets you query data that is not yet in the cluster. It creates a table from a file in a few steps.

To import your own data, open the importer from the left menu or from the `+` in the left assist panel.

To learn more, watch the video on [Data Import Wizard](http://gethue.com/import-data-to-be-queried-via-the-self-service-drag-drop-create-table-wizard/).

> **Note:** You can select files from the configured storage (for example HDFS or S3) or upload a small file. Hue detects the file format automatically. The wizard also helps with table partitioning, Kudu tables and nested types.

#### New importer

When the administrator sets `enable_new_importer=true` in the `[desktop]` section of `hue.ini` (the default is `false`), a new importer is available. It adds a second entry named **Import**, which opens the page at `/newimporter`. The existing importer stays available.

To import a file with the new importer:

1. Open the importer and select a source. Depending on your configuration, the choices are **Upload from File**, **HDFS**, **Amazon S3**, **Azure Storage**, **Google Storage** and **Ozone**.
2. Select the file. Hue opens the **Preview** tab with a preview of the data.
3. In the **Preview** tab, choose the database, the table name, the engine and the compute. Review and edit the column names, types and comments.
4. In the **Settings** tab, check the file format: file type (CSV, JSON or Excel), whether the file has a header, the field separator and the quote character.
5. Optional: add partitions in the **Partitions** tab.
6. Click **Finish Import**.

The new table is created in the selected database.

> **Note:** Files above the supported size limit can't be uploaded in the importer. Use a file browser to upload them instead.

#### CSV file

You can ingest any small CSV file into a new index in a few clicks.

#### Relational databases

You can import data from relational databases into an HDFS file or a Hive table with Apache Sqoop. The imports run on YARN and are scheduled by Oozie. This option requires `enable_sqoop=true` in the `[indexer]` section of `hue.ini`.

Learn more in the post on [ingesting data from traditional databases](http://gethue.com/importing-data-from-traditional-databases-into-hdfshive-in-just-a-few-clicks/).

#### Apache Solr indexes

You can index data into Solr and then explore it with a [Dynamic Dashboard](/user/querying/#dashboard). The indexer builds the Solr schema and the Morphlines file for you and runs the indexing job on YARN.

Before you start, your administrator needs to:

- Configure Hue with a running Solr cluster.
- Place the required libraries in a directory on HDFS and set `config_indexer_libs_path` in the `[indexer]` section of `hue.ini` to that path (the default is `/tmp/smart_indexer_lib`).
- Keep `enable_new_indexer` set to `true` in the `[indexer]` section (this is the default).

```ini
[indexer]
# Flag to turn on the morphline based Solr indexer.
## enable_new_indexer=true

# Filesystem directory containing Solr Morphline indexing libs.
## config_indexer_libs_path=/tmp/smart_indexer_lib
```

In this example, you pick a name for the new collection, select the reviews data file from HDFS and click **Next**.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-wizard.png)

**Field selection and ETL**

This tab lists all the fields that the indexer found in the file. Hue also guesses the field types. Check that the types are correct.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-wizard-fields.png)

In this example, you apply four operations to make the collection easy to search.

**Convert date**

This operation is implicit. When you set the field type to date, Hue converts the value to a Solr date. Hue converts most standard date formats automatically. For a custom date format, add the convert date operation explicitly.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-op-date.png)

**Translate star ratings to integer ratings**

Under the rating field, change the field type from string to long and click add operation. Select the translate operation and set up the following translation mapping.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-translate-date.png)

**Grok the city from the full address field**

Add a grok operation to the full address field, enter the regex `.* (?<city>\w+),.*` and set the number of expected fields to 1.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-op-grok.png)

In the new child field, set the name to `city`. This field contains the value of the `city` capture group.

**Split the latitude and longitude into two fields**

The data file has the latitude and longitude in one field, separated by a comma. Add a split operation, set the split value to `,` and the number of output fields to 2. Change the child field types to double and give them clear names. Clear the **keep in index** box for the parent field.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-op-split.png)

**Add the country from the IP address**

Add a geo ip operation and select `iso_code` as the output. This gives you the country code.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-op-geoip.png)

Check the preview to catch typos. Then click **Index** and wait. A progress bar at the bottom of the screen shows the status: yellow means Hue is indexing the data and green means it is done. You can close the window. The indexing continues on the cluster.

After the data is indexed into a Solr collection, you can use all the search features of Hue and build an analytics dashboard.

![Solr Dashboard](https://cdn.gethue.com/uploads/2016/08/indexer-dash.png)

**Dependencies**

The indexer libs path contains all the libraries required for indexing. You can assemble this directory yourself. It has three main components:

1. JAR files required by the [MapReduceIndexerTool](http://www.cloudera.com/documentation/enterprise/5-5-x/topics/search_mapreduceindexertool.html)

The required JAR files ship with the Hadoop distribution that provides Solr search. The list of required JARs is:

    argparse4j-0.4.3.jar
    readme.txt
    httpmime-4.2.5.jar
    search-mr-1.0.0-cdh5.8.0-job.jar
    kite-morphlines-core-1.0.0-cdh5.8.0.jar
    solr-core-4.10.3-cdh5.8.0.jar
    kite-morphlines-solr-core-1.0.0-cdh5.8.0.jar
    solr-solrj-4.10.3-cdh5.8.0.jar
    noggit-0.5.jar

If you get a missing class error, search the JARs of your distribution for the missing class.

2. Maxmind GeoLite2 database

This file is required for the GeoIP lookup command and can be found on [MaxMind’s website](https://dev.maxmind.com/geoip/geoip2/geolite2/).

3. Grok Dictionaries

Any grok commands can be defined in text files within the grok_dictionaries sub directory.

### Streams

You can list Kafka topics, streams and tables with the [`ksql` connector](/administrator/configuration/connectors/#ksqldb).

### Permissions

You can edit Sentry roles and privileges in the Security interface.

> **Note:** If the administrator sets `enable_new_storage_browser=true`, the Storage Browser replaces the separate file browser entries in the menu.

> **Note:** Apache Sentry is being replaced by Apache Ranger.

#### Sentry tables

It can be tricky to grant a new user the right permissions on a secure cluster. This walkthrough enables a new user to create tables on a Kerberized cluster. Creating the user and group on each node can be tedious on a large cluster, so the example uses pssh (parallel ssh).

1. Install the tool and prepare a file that contains all your hosts.

    On macOS:

    ```bash
    brew install pssh
    ```

    On Debian or Ubuntu:

    ```bash
    sudo apt-get install pssh
    ```

    ```bash
    cat ~/Documents/nodeshue.txt
    hue-1.test.cloudera.com
    hue-2.test.cloudera.com
    hue-3.test.cloudera.com
    hue-4.test.cloudera.com
    ```

2. Run the following commands to create user: t1 and group: grp1 on your cluster:

    ```
    pssh -h ~/Documents/nodeshue.txt -i useradd t1
    [1] 13:58:48 [SUCCESS] hue-1.test.cloudera.com
    [2] 13:58:48 [SUCCESS] hue-2.test.cloudera.com
    [3] 13:58:48 [SUCCESS] hue-3.test.cloudera.com
    [4] 13:58:48 [SUCCESS] hue-4.test.cloudera.com

    pssh --hosts ~/Documents/nodes.txt -i groupadd grp1
    [1] 13:59:20 [SUCCESS] hue-1.test.cloudera.com
    [2] 13:59:20 [SUCCESS] hue-2.test.cloudera.com
    [3] 13:59:20 [SUCCESS] hue-3.test.cloudera.com
    [4] 13:59:20 [SUCCESS] hue-4.test.cloudera.com

    pssh --hosts ~/Documents/nodes.txt -i usermod -a -G grp1 t1
    [1] 13:59:28 [SUCCESS] hue-1.test.cloudera.com
    [2] 13:59:28 [SUCCESS] hue-2.test.cloudera.com
    [3] 13:59:28 [SUCCESS] hue-3.test.cloudera.com
    [4] 13:59:28 [SUCCESS] hue-4.test.cloudera.com
    ```

3. Create the same Hue user `t1` and group `grp1`, and make `t1` a member of `grp1`.

4. Log in as a user with Sentry admin permission and run the following statements in the Hive editor:

    ```
    create role write_role;
    GRANT ROLE write_role TO GROUP grp1;
    GRANT ALL ON SERVER server1 TO ROLE write_role;
    ```

Now the user `t1`, or any user in `grp1`, can log in and create tables with Hive or Impala DDL queries or with the importer.

In most cases, you grant narrower permissions than `ALL` on `SERVER`. The next examples create a `read_only_role` and a `read_write_role` for specific databases.

Create the user `t2` in group `grp2` and the user `t3` in group `grp3` on the cluster and in Hue, with similar commands. Then grant the permissions to each group:

1. Read and write access to the database `s3db` for any user in group `grp3`:

    ```
    create role read_write_s3db_role;
    GRANT ROLE read_write_s3db_role TO GROUP grp3;
    GRANT ALL ON DATABASE s3db TO ROLE read_write_s3db_role;
    GRANT ALL ON URI 'hdfs://hue-1.test.cloudera.com:8020/user/t3' to ROLE read_write_s3db_role;
    ```

2. Read-only permission for the database `default` for any user in group `grp2`:

    ```
    create role read_only_defaultDb_role;
    GRANT ROLE read_only_defaultDb_role TO GROUP grp2;
    GRANT SELECT ON DATABASE default TO ROLE read_only_defaultDb_role;
    GRANT REFRESH ON DATABASE default TO ROLE read_only_defaultDb_role;
    ```

Now `t3` can read and create tables in the database `s3db`, and `t2` can only read the database `default`.

You can also grant these permissions in the Hue Security page. The result looks like this:

![Listing of Sentry Table privileges](https://cdn.gethue.com/uploads/2019/04/HueSecurityRoles.png)

> **Note:** You must grant the URI permission. Otherwise, creating a table fails with this error:

    Error while compiling statement: FAILED: SemanticException No valid privileges User t3 does not have privileges for CREATETABLE The required privileges: Server=server1->URI=hdfs://hue-1.gce.cloudera.com:8020/user/t3/t3_dir->action=*->grantOption=false;


#### Sentry Solr privileges

You can edit [Apache Solr](http://gethue.com/ui-to-edit-sentry-privilege-of-solr-collections/) privileges in the interface.

To list collections, query and create a collection, grant:

    Admin=*->action=*
    Collection=*->action=*
    Schema=*->action=*
    Config=*->action=*


![Listing of Solr collection](https://cdn.gethue.com/uploads/2016/05/solr-secu-1024x624.png)
Listing of Solr collections and configs with their related privileges.

![Listing of all the roles and their privileges.](https://cdn.gethue.com/uploads/2016/05/solr-secu2-e1464909489928.png)
Listing of all the roles and their privileges. Possibility to filter by groups.

![Apply privilege to all the collections or configs with *](https://cdn.gethue.com/uploads/2016/06/solr-sentry-all.png)
Apply privilege to all the collections or configs with *

![End user error when querying a collection without the QUERY privilege](https://cdn.gethue.com/uploads/2016/06/solr-sentry-query-error.png)
End user error when querying a collection without the QUERY privilege

![End user error when modifying a record without the UPDATE privilege](https://cdn.gethue.com/uploads/2016/06/solr-sentry-update-error.png)
End user error when modifying a record without the UPDATE privilege


#### HDFS ACLs

You can edit [HDFS ACLs](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsPermissionsGuide.html#ACLs_.28Access_Control_Lists.29) in the Security app.


![HDFS Acls](https://cdn.gethue.com/docs/user/storage_hdfs_acls.png)

## Data

The File Browser lets you work with these file systems: HDFS, Amazon S3, Azure (ABFS and ADLS), Google Cloud Storage and Apache Ozone. An administrator must [configure the connection](/administrator/configuration/connectors/#storage) first. You can:

-   Create files and directories, upload and download files, upload zip archives and extract them, rename, move, copy and delete files and directories.
-   Change the owner, group and permissions of a file or directory (HDFS).
-   View and edit files as text or binary.
-   Create external tables or export query results.

### Browse files

To browse files:

1. Open the file browser from the left menu (**Storage Browser** if it is enabled, see below).
2. Click the root of the storage to list the accessible folders.
3. Click a folder to open it, or a file to view it.

You can then create, rename, move, copy or delete directories and files, and upload files directly to the storage.

![Browse files](https://cdn.gethue.com/uploads/2016/08/image2.png)

### Storage Browser

When the administrator sets `enable_new_storage_browser=true` in the `[desktop]` section of `hue.ini` (the default is `false`), the left menu shows **Storage Browser** instead of the separate file browser entries. The Storage Browser shows one tab per configured file system. In it you can:

-   Search in the current folder and refresh the list.
-   Create a new file or folder. Depending on the location, you can also create a bucket (S3, Google Storage, Ozone), a volume (Ozone) or a file system (ABFS).
-   Upload files and download files.
-   Rename, copy, move, compress and extract files and folders.
-   Preview files and edit text files.
-   Change the owner, group and permissions, and set the replication factor (HDFS).
-   View the summary of a folder, such as the number of files and the disk space used.
-   Move items to the trash, restore them and empty the trash (HDFS).

> **Note:** The available actions depend on the file system and your permissions. Archive extraction requires `enable_extract_uploaded_archive` to be `true` in the `[filebrowser]` section. It is on by default only when the Oozie app is enabled, and the Storage Browser offers it only for HDFS.

### Create SQL tables from files

The table import wizard can create external Hive tables directly from files in the storage. You can then query the data with SQL without copying it into HDFS or the Hive warehouse.

To create an external table from a file:

1. Open the Table Browser and select the database.
2. Click the plus icon in the upper right.
3. Use the file picker to select a file on the storage.
4. Choose the delimiter of the file and click **Next**.
5. Clear **Store in Default location** to keep the file where it is.
6. Update the column definitions and click **Submit**.

The new table appears in the Table Browser.

![Create tables from external files](https://cdn.gethue.com/uploads/2017/11/image4-1.png)

### Save query results to storage

After you create external tables, you can query them in the Hive or Impala editor, including joins. You can then save the query results back to the storage.

![Save results to storage](https://cdn.gethue.com/uploads/2017/11/image1-1.png)

### HDFS

You can browse HDFS, peek at the content of files, and upload and download data.

### AWS S3

When the administrator configures an S3 account, you can read and write data on S3. You get autocomplete, and you can query and save data on S3 without moving it to HDFS first.

### Azure

ABFS (ADLS Gen2) and ADLS Gen1 are supported.

### Google Cloud Storage

Google Cloud Storage (`gs://` paths) is supported when the administrator configures it.

### Apache Ozone

Apache Ozone (`ofs://` paths) is supported when the administrator configures it.

### HBase

#### Smart view

The smartview is the view that you land on when you first enter a table.
On the left hand side are the row keys and hovering over a row reveals a
list of controls on the right. Click a row to select it, and once
selected you can perform batch operations, sort columns, or do any
amount of standard database operations. To explore a row, simple scroll
to the right. By scrolling, the row should continue to lazily-load cells
until the end.

![HBase](https://cdn.gethue.com/uploads/2021/10/hbase_7.png)

#### Adding Data

To initially populate the table, you can insert a new row or bulk upload
CSV/TSV/etc. type data into your table.

![HBase](https://cdn.gethue.com/uploads/2021/10/hbase_2.png)

On the right hand side of a row is a '+' sign that lets you insert columns into your row.


#### Mutating Data

To edit a cell, simply click to edit inline.

![HBase](https://cdn.gethue.com/uploads/2021/10/hbase_3.png)

If you need more control or data about your cell, click “Full Editor” to
edit.

![HBase](https://cdn.gethue.com/uploads/2021/10/hbase_5.png)

In the full editor, you can view cell history or upload binary data to
the cell. Binary data of certain MIME Types are detected, meaning you
can view and edit images, PDFs, JSON, XML, and other types directly in
your browser!

![HBase](https://cdn.gethue.com/uploads/2021/10/hbase_6.png)

Hovering over a cell also reveals some more controls (such as the delete
button or the timestamp). Click the title to select a few and do batch
operations:

![HBase](https://cdn.gethue.com/uploads/2021/10/hbase_4.png)


#### Smart searchbar

The "Smart Searchbar" is a sophisticated tool that helps you zero-in on
your data. The smart search supports a number of operations. The most
basic ones include finding and scanning row keys. Here I am selecting
two row keys with:


    domain.100, domain.200


![HBase](https://cdn.gethue.com/uploads/2021/10/hbase_1.png)

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
[HBase filter language](https://hbase.apache.org/book.html#thrift.filter_language), by typing your filter
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

### Indexes

You can create Apache Solr indexes with the [importer](/user/browsing/#importing-data). They are listed in the interface.

![Solr Indexer](https://cdn.gethue.com/uploads/2016/08/indexer-op-grok.png)

## Jobs

The Job Browser lets you examine the jobs that run in the cluster. It presents jobs and tasks in layers, so you can quickly reach the logs and troubleshoot.

### SQL queries

You can open the query browser in three ways:

* Click the query ID after you run a SQL query in the editor. This opens the mini job browser overlay at the current query. You see the execution details next to the SQL editor, which helps you understand the performance of your query. This is the recommended way.
* Open the mini job browser overlay and go to the **Queries** tab.
* Open the Job Browser and go to the **Queries** tab.

The Impala query section requires `enable_query_browser=true` in the `[jobbrowser]` section of `hue.ini` (the default). The Hive query history requires `enable_hive_query_browser=true`.

![Pretty Query Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-11.40.24-AM.png)

**Query capabilities**

The query browser displays the list of currently running queries on your current Impala coordinator, and a number of completed queries based on your configuration (25 by default).

![Query list](https://cdn.gethue.com/uploads/2017/12/JB.png)

Display the explain plan, which shows the logical execution steps. Check that the execution does not proceed in an unexpected way, such as a wrong join type, join order or projection order. This can happen when the table statistics are out of date, as the image below shows with "cardinality: unavailable". To update the statistics, run:

```sql
COMPUTE STATS <TABLE_NAME>
```

![Explain plan](https://cdn.gethue.com/uploads/2017/11/Explain.png)

Display the summary report, which shows the physical timing and memory information of each operation of the explain plan. You can find bottlenecks and fix them by replacing expensive operations, repartitioning, changing the file format or moving data.

![Summary report](https://cdn.gethue.com/uploads/2017/11/Summary.png)

Display the query plan, a condensed graphical version of the summary report.

![Query plan](https://cdn.gethue.com/uploads/2017/12/Plan.png)

Display the memory profile, which shows the memory used during the execution of the query. Use it to check whether the memory available to your query is sufficient.

![Memory profile](https://cdn.gethue.com/uploads/2017/11/Memory.png)

Display the profile, which gives the physical execution of the query in great detail. Use it to analyze data exchange between operators and I/O performance (disk, network, CPU). You can use it to reorganize the location of your data (on disk, in memory, different partitions or file formats).

![Query profile](https://cdn.gethue.com/uploads/2017/12/Profile.png)

You can also manually close an open query.

### YARN (Spark, MapReduce, Tez)

Any job running on the Resource Manager is listed automatically. If the job moved to a history server, Hue fetches the information from there.

### Oozie workflows and schedules

You can list submitted workflows, schedules and bundles.

![Oozie jobs](https://cdn.gethue.com/uploads/2016/04/hue-dash-oozie.png)

### Spark and Livy

You can list [Spark Livy](/user/querying/#spark) sessions and submitted statements.
