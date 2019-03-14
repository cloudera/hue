---
title: "Browser"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

## Data Importer

The goal of the importer is to allow ad hoc queries on data not yet in the clusters thereby expedite self-service analytics.

If you want to import your own data instead of installing the sample
tables, open the importer from the left menu or from the little `+` in the left assist.

If you've ever struggled with creating new SQL tables from files, you'll be happy to learn that this is now much easier. The wizard has been revamped to two simple steps and also offers more formats. Now users just need to:

1. Select a source type
2. Select the type of object for the destination

And that's it!

To learn more, watch the video on [Data Import Wizard](http://gethue.com/import-data-to-be-queried-via-the-self-service-drag-drop-create-table-wizard/).

## SQL Tables

Although you can create tables by executing the appropriate Hive HQL DDL
query commands, it is easier to create a table using the create table wizard.

**From a File**

If you've ever struggled with creating new SQL tables from files, you'll be happy to learn that this is now much easier. With the latest Hue release, you can now create these in an ad hoc way and thereby expedite self-service analytics. The wizard has been revamped to two simple steps and also offers more formats. Now users just need to:

1. In the Importer Manager selects source from a 'File'
1. Select the type of table

Files can be dragged & dropped, selected from HDFS or S3 (if configured), and their formats are automatically detected. The wizard also assists when performing advanced functionalities like table partitioning, Kudu tables, and nested types.


**Manually**

1.  In the Importer Manager selects 'Manually'
2.  Follow the instructions in the wizard to create the table. The basic
    steps are:
    -   Name the table.
    -   Choose the record format.
    -   Configure record serialization by specifying delimiters for
        columns, collections, and map keys.
    -   Choose the file format.
    -   Specify the location for your table's data.
    -   Specify the columns, providing a name and selecting the type for
        each column.
    -   Specify partition columns, providing a name and selecting the
        type for each column.


## Indexing

In the past, indexing data into Solr to then explore it with a [Dynamic Dashboard](http://gethue.com/search-dashboards/) has been quite difficult. The task involved writing a Solr schema and a Morphlines file then submitting a job to YARN to do the indexing. Often times getting this correct for non trivial imports could take a few days of work. Now with Hue's new feature you can start your YARN indexing job in minutes. This tutorial offers a step by step guide on how to do it.

[Read more about it here](http://gethue.com/easy-indexing-of-data-into-solr/).

## Traditional Databases

Read more about [ingesting data from traditional databases](http://gethue.com/importing-data-from-traditional-databases-into-hdfshive-in-just-a-few-clicks/).


# Dashboards
Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.

Read more about [Dashboards](http://gethue.com/search-dashboards/).

## Concepts

Simply drag & drop widgets that are interconnected together. This is great for exploring new datasets or monitoring without having to type.

### Importing

Any CSV file can be dragged & dropped and ingested into an index in a few clicks via the Data Import Wizard [link]. The indexed data is immediately queryable and its facets/dimensions will be very fast to explore.

### Browsing

The Collection browser got polished in the last releases and provide more information on the columns. The left metadata assist of Hue 4 makes it handy to list them and peak at their content via the sample popup.

### Querying

The search box support live prefix filtering of field data and comes with a Solr syntax autocomplete in order to make the querying intuitive and quick. Any field can be inspected for its top values of statistic. This analysis happens very fast as the data is indexed.

## Databases

### Solr

#### Autocomplete

The top search bar offers a [full autocomplete](http://gethue.com/intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/) on all the values of the index.

#### More Like This
The “More like This” feature lets you selected fields you would like to use to find similar records. This is a great way to find similar issues, customers, people... with regard to a list of attributes.

### SQL

## Reports

This is work in progress but dashboards will soon offer a classic reporting option.

## SDK
Read more about extending [connectors](../sdk/sdk.html#dashboard).


# Browsers
Hue's Browsers powers your Data Catalog. They let you easily search, glance and perform actions on data or jobs in Cloud or on premise clusters.

## Tables

The Table Browser enables you to manage the databases,
tables, and partitions of the metastore shared by
the Hive and Impala. You can use Metastore
Manager to perform the following operations:

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


## Files

The File Browser application lets you browse and manipulate files and
directories in the Hadoop Distributed File System (HDFS), S3 or ADLS.
With File Browser, you can:

-   Create files and directories, upload and download files, upload zip
    archives, and rename, move, and delete files and directories. You
    can also change a file's or directory's owner, group, and
    permissions. See [Files and Directories](#filesAndDirectories).
-   Search for files, directories, owners, and groups. See [Searching
    for Files and Directories](#searching).
-   View and edit files as text or binary. See [Viewing and Editing
    Files](#viewAndEdit).

### File systems
#### HDFS
#### S3

Hue can be setup to read and write to a configured S3 account, and users get autocomplete capabilities and can directly query from and save data to S3 without any intermediate moving/copying to HDFS.

[Read more about it](http://gethue.com/introducing-s3-support-in-hue/).

** Create Hive Tables Directly From S3**
Hue's Metastore Import Data Wizard can create external Hive tables directly from data directories in S3. This allows S3 data to be queried via SQL from Hive or Impala, without moving or copying the data into HDFS or the Hive Warehouse.

To create an external Hive table from S3, navigate to the Metastore app, select the desired database and then click the “Create a new table from a file” icon in the upper right.

Enter the table name and optional description, and in the “Input File or Directory” filepicker, select the S3A filesystem and navigate to the parent directory containing the desired data files and click the “Select this folder” button. The “Load Data” dropdown should automatically select the “Create External Table” option which indicates that this table will directly reference an external data directory.

Choose your input files' delimiter and column definition options and finally click “Create Table” when you're ready to create the Hive table. Once created, you should see the newly created table details in the Metastore.

**Save Query Results to S3**

Now that we have created external Hive tables created from our S3 data, we can jump into either the Hive or Impala editor and start querying the data directly from S3 seamlessly. These queries can join tables and objects that are backed either by S3, HDFS, or both. Query results can then easily be saved back to S3.


** S3 Configuration **

[Hue S3 Documentation](../admin-manual/manual.html#s3).


#### ADLS

Learn more about it on the [ADLS integration post](http://gethue.com/browsing-adls-data-querying-it-with-sql-and-exporting-the-results-back-in-hue-4-2/).

 Users gets autocomplete capabilities and more:

** Exploring ADLS in Hue's file browser **
Once Hue is successfully configured to connect to ADLS, we can view all accessible folders within the account by clicking on the ADLS root. From here, we can view the existing keys (both directories and files) and create, rename, move, copy, or delete existing directories and files. Additionally, we can directly upload files to ADLS.

** Create Hive Tables Directly From ADLS **
Hue's table browser import wizard can create external Hive tables directly from files in ADLS. This allows ADLS data to be queried via SQL from Hive or Impala, without moving or copying the data into HDFS or the Hive Warehouse. To create an external Hive table from ADLS, navigate to the table browser, select the desired database and then click the plus icon in the upper right. Select a file using the file picker and browse to a file on ADLS.

** Save Query Results to ADLS **
Now that we have created external Hive tables created from our ADLS data, we can jump into either the Hive or Impala editor and start querying the data directly from ADLS seamlessly. These queries can join tables and objects that are backed either by ADLS, HDFS, or both. Query results can then easily be saved back to ADLS.


** ADLS Configuration **

[Hue ADLS Documentation](../admin-manual/manual.html#adls).

<a id="fileAndDirectories"></a>
### Files and Directories

You can use File Browser to view the input and output files of your
MapReduce jobs. Typically, you can save your output files in /tmp or in
your home directory if your system administrator set one up for you. You
must have the proper permissions to manipulate other user's files.

#### Creating Directories

1.  In the File Browser window, select **New > Directory**.
2.  In the **Create Directory** dialog box, enter a directory name and
    then click **Submit**.

#### Changing Directories

-   Click the directory name or parent directory dots in the **File
    Browser** window.
-   Click the ![image](images/edit.png) icon, type a directory name, and
    press **Enter**.

To change to your home directory, click **Home** in the path field at
the top of the **File Browser** window.

![image](images/note.jpg) **Note**:

The **Home** button is disabled if you do not have a home directory. Ask
a Hue administrator to create a home directory for you.

#### Creating Files

1.  In the File Browser window, select **New > File**.
2.  In the **Create File** dialog box, enter a file name and then click
    **Submit**.


#### Uploading Files

You can upload text and binary files to the HDFS.

1.  In the **File Browser** window, browse to the directory where you
    want to upload the file.
2.  Select **Upload \> Files**.
3.  In the box that opens, click **Upload a File** to browse to and
    select the file(s) you want to upload, and then click **Open**.

#### Downloading Files

You can download text and binary files to the HDFS.

1.  In the **File Browser** window, check the checkbox next to the file
    you want to download.
2.  Click the **Download** button.

### Uploading Zip Archives

You can extract zip archives to the HDFS. The archive is
extracted to a directory named archivename.

1.  In the **File Browser** window, browse to the directory where you
    want to upload the archive.
2.  Select **Upload > Zip file**.
3.  In the box that opens, click **Upload a zip file** to browse to and
    select the archive you want to upload, and then click **Open**.

### Trash Folder

File Browser supports the HDFS trash folder (*home directory*/.Trash) to
contain files and directories before they are permanently deleted. Files
in the folder have the full path of the deleted files (in order to be
able to restore them if needed) and checkpoints. The length of time a
file or directory stays in the trash depends on HDFS properties.

In the **File Browser** window, click ![image](images/fbtrash.png).


### Changing Owner, Group, or Permissions

![image](images/note.jpg) **Note**:

Only the Hadoop superuser can change a file's or directory's owner,
group, or permissions. The user who starts Hadoop is the Hadoop
superuser. The Hadoop superuser account is not necessarily the same as a
Hue superuser account. If you create a Hue user (in User Admin) with the
same user name and password as the Hadoop superuser, then that Hue user
can change a file's or directory's owner, group, or permissions.

**Owner or Group**

1.  In the **File Browser** window, check the checkbox next to the
    select the file or directory whose owner or group you want to
    change.
2.  Choose **Change Owner/Group** from the Options menu.
3.  In the **Change Owner/Group** dialog box:
    -   Choose the new user from the **User** drop-down menu.
    -   Choose the new group from the **Group** drop-down menu.
    -   Check the **Recursive** checkbox to propagate the change.

4.  Click **Submit** to make the changes.

**Permissions**

1.  In the **File Browser** window, check the checkbox next to the file
    or directory whose permissions you want to change.
2.  Click the **Change Permissions** button.
3.  In the **Change Permissions** dialog box, select the permissions you
    want to assign and then click **Submit**.

### Viewing and Editing Files

You can view and edit files as text or binary.


**View**

1.  In the **File Browser** window, click the file you want to view.
    File Browser displays the first 4,096 bytes of the file in the
    **File Viewer** window.
    -   If the file is larger than 4,096 bytes, use the Block navigation
        buttons (First Block, Previous Block, Next Block, Last Block) to
        scroll through the file block by block. The **Viewing Bytes**
        fields show the range of bytes you are currently viewing.
    -   To switch the view from text to binary, click **View as Binary**
        to view a hex dump.
    -   To switch the view from binary to text, click **View as Text**.

**Edit**

1.  If you are viewing a text file, click **Edit File**. File Browser
    displays the contents of the file in the **File Editor** window.
2.  Edit the file and then click **Save** or **Save As** to save the
    file.

## Indexes / Collections

## Sentry Permissions

Sentry roles and privileges can directly be edited in the Security interface.

### SQL

[Hive UI](http://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/).

### Solr

[Solr](http://gethue.com/ui-to-edit-sentry-privilege-of-solr-collections/) privileges can be edited directly via the interface.

For listing collections, query and creating collection:

    Admin=*->action=*
    Collection=*->action=*
    Schema=*->action=*
    Config=*->action=*


## Jobs

The Job Browser application lets you to examine multiple types of jobs
jobs running in the cluster. Job Browser presents the job and
tasks in layers. The top layer is a list of jobs, and you can link to a
list of that job's tasks. You can then view a task's attempts and the
properties of each attempt, such as state, start and end time, and
output size. To troubleshoot failed jobs, you can also view the logs of
each attempt.


If there are jobs running, then the Job Browser list appears.


### Dashboard

-   To filter the jobs by their state (such as **Running** or
    **Completed**), choose a state from the **Job status** drop-down
    menu.
-   To filter by a user who ran the jobs, enter the user's name in the
    **User Name** query box.
-   To filter by job name, enter the name in the **Text** query box.
-   To clear the filters, choose **All States** from the **Job status**
    drop-down menu and delete any text in the **User Name** and **Text**
    query boxes.

### Viewing Job Information

![image](images/note.jpg) **Note**: At any level you can view the log
for an object by clicking the ![image](images/log.png) icon in the Logs
column.

**To view job information for an individual job:**

1.  In the **Job Browser** window, click **View** at the right of the
    job you want to view. This shows the **Job** page for the job, with
    the recent tasks associated with the job are displayed in the
    **Tasks** tab.
2.  Click the **Logs** tab to view the logs for this job.
3.  Click the **Counters** tab to view the counter metrics for the job.


### Types
#### YARN (Spark, MapReduce)
#### Impala Queries

There are three ways to access the new browser:

Best: Click on the query ID after executing a SQL query in the editor. This will open the mini job browser overlay at the current query. Having the query execution information side by side the SQL editor is especially helpful to understand the performance characteristics of your queries.
Open the mini job browser overlay and navigate to the queries tab.
Open the job browser and navigate to the queries tab.

Query capabilities

* Display the list of currently running queries on the user's current Impala coordinator and a certain number of completed queries based on your configuration (25 by default).
* Display the summary report which shows physical timing and memory information of each operation of the explain plan. You can quickly find bottlenecks in the execution of the query which you can resolve by replacing expensive operations, repartitioning, changing file format or moving data.
* Display the query plan which is a condensed version of the summary report in graphical form
* Display the memory profile which contains information about the memory usage during the execution of the query. You can use this to determine if the memory available to your query is sufficient.
* Display the profile which gives you physical execution of the query in great detail. This view is used to analyze data exchange between the various operator and the performance of the IO (disk, network, CPU). You can use this to reorganize the location of your data (on disk, in memory, different partitions or file formats).
* Manually close an opened query.

Read more about it on [Browsing Impala Query Execution within the SQL Editor
](http://gethue.com/browsing-impala-query-execution-within-the-sql-editor/).

#### Workflow / Schedules (Oozie)

List submitted workflows, schedules and bundles.

#### Livy / Spark

List Livy sessions and submitted statements.