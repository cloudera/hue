
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

Metastore Manager
=================

The Metastore Manager application enables you to manage the databases,
tables, and partitions of the
[Hive](http://archive.cloudera.com/cdh4/cdh/4/hive/) metastore shared by
the ([Beeswax](../beeswax.html) and [Cloudera Impala Query
UI](../impala.html)) applications. You can use Metastore
Manager to perform the following operations:

-   Databases
    -   [Select a database](#selectDatabase)
    -   [Create a database](#createDatabase)
    -   [Drop databases](#dropDatabase)

-   Tables
    -   [Create tables](#createTables)
    -   [Browse tables](#browseTables)
    -   [Import data into a table](#importDataIntoTables)
    -   [Drop tables](#dropTables)
    -   [View the location of a table](#viewTableLocation)

Metastore Manager Installation and Configuration
------------------------------------------------

Metastore Manager is one of the applications installed as part of Hue.
For information about installing and configuring Hue, see the Hue Installation
manual.

Starting Metastore Manager
--------------------------

Click the **Metastore Manager** icon
(![image](images/icon_table_browser_24.png)) in the navigation bar at
the top of the Hue browser page.

### Installing Sample Tables

![image](images/note.jpg) **Note**: You must be a superuser to perform
this task.

1.  Click ![image](images/quick_start.png). The Quick Start Wizard
    opens.
2.  Click **Step 2: Examples**.
3.  Click **Beeswax (Hive UI)** or **Cloudera Impala Query UI**.

### Importing Data

If you want to import your own data instead of installing the sample
tables, follow the procedure in [Creating Tables](#createTables).

<a id="selectDatabase"></a>
Selecting a Database
--------------------

1.  In the pane on the left, select the database from the DATABASE
    drop-down list.

<a id="createDatabase"></a>
Creating a Database
-------------------

1.  Click ![image](images/databases.png).
2.  Click **Create a new database**.
    1.  Specify a database name and optional description. Database names
        are not case-sensitive. Click **Next**.
    2.  Do one of the following:
        -   Keep the default location in the Hive warehouse folder.
        -   Specify an external location within HDFS:
            1.  Uncheck the **Location** checkbox.
            2.  In the External location field, type a path to a folder
                on HDFS or click ![image](images/browse.png) to browse
                to a folder and click **Select this folder**.

    3.  Click the **Create Database** button.
    
<a id="selectDatabase"></a>
Dropping Databases
------------------

1.  Click ![image](images/databases.png).
2.  In the list of databases, check the checkbox next to one or more
    databases.
3.  Click the ![image](images/trash.png) Drop button.
4.  Confirm whether you want to delete the databases.

<a id="createTables"></a>
Creating Tables
---------------

Although you can create tables by executing the appropriate Hive HQL DDL
query commands, it is easier to create a table using the Metastore
Manager table creation wizard.

There are two ways to create a table: from a file or manually. If you
create a table from a file, the format of the data in the file will
determine some of the properties of the table, such as the record and
file formats. The data from the file you specify is imported
automatically upon table creation. When you create a file manually, you
specify all the properties of the table, and then execute the resulting
query to actually create the table. You then import data into the table
as an additional step.

**From a File**

1.  In the ACTIONS pane in the Metastore Manager window, click **Create
    a new table from a file**. The table creation wizard starts.
2.  Follow the instructions in the wizard to create the table. The basic
    steps are:
    -   Choose your input file. The input file you specify must exist.
        Note that you can choose to have Beeswax create the table
        definition only based on the import file you select, without
        actually importing data from that file.
    -   Specify the column delimiter.
    -   Define your columns, providing a name and selecting the type.

3.  Click **Create Table** to create the table. The new table's metadata
    displays on the right side of the **Table Metadata** window. At this
    point, you can view the metadata or a sample of the data in the
    table. From the ACTIONS pane you can import new data into the table,
    browse the table, drop it, or go to the File Browser to see the
    location of the data.

**Manually**

1.  In the ACTIONS pane in the Metastore Manager window, click **Create
    a new table manually**. The table creation wizard starts.
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

3.  Click **Create table**. The Table Metadata window displays.

<a id="browseTables"></a>
Browsing Tables
---------------

**To browse table data:**

In the Table List window, check the checkbox next to a table name and
click **Browse Data**. The table's data displays in the Query Results
window.

**To browse table metadata:**

Do one of the following:

-   In the Table List window, click a table name.
-   Check the checkbox next to a table name and click **View**.

-   The table's metadata displays in the **Columns** tab. You can view
    the table data by selecting the **Sample** tab.
-   If the table is partitioned, you can view the partition columns by
    clicking the **Partition Columns** tab and display the partitions by
    clicking **Show Partitions(n)**, where n is the number of partitions
    in the ACTIONS pane on the left.

<a id="importDataIntoTables"></a>
Importing Data into a Table
---------------------------

When importing data, you can choose to append or overwrite the table's
data with data from a file.

1.  In the Table List window, click the table name. The Table Metadata
    window displays.
2.  In the ACTIONS pane, click **Import Data**.
3.  For **Path**, enter the path to the file that contains the data you
    want to import.
4.  Check **Overwrite existing data** to replace the data in the
    selected table with the imported data. Leave unchecked to append to
    the table.
5.  Click **Submit**.

<a id="dropTables"></a>
Dropping Tables
---------------

1.  In the Table List window, click the table name. The Table Metadata
    window displays.
2.  In the ACTIONS pane, click **Drop Table**.
3.  Click **Yes** to confirm the deletion.

<a id="viewTableLocation"></a>
Viewing a Table's Location
--------------------------

1.  In the Table List window, click the table name. The Table Metadata
    window displays.
2.  Click **View File Location**. The file location of the selected
    table displays in its directory in the File Browser window.
