
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

Cloudera Impala Query UI
========================

The Cloudera Impala Query UI application enables you to perform queries
on Apache Hadoop data stored in HDFS or HBase using Cloudera Impala. For
information about Cloudera Impala, see [Installing and Using Cloudera
Impala](/content/support/en/documentation/cloudera-impala/cloudera-impala-documentation-v1-latest.html).
You can create, run, and manage queries, and download the results in a
Microsoft Office Excel worksheet file or a comma-separated values file.

Cloudera Impala Query UI Installation and Configuration
-------------------------------------------------------

The Cloudera Impala Query UI application is one of the applications
installed as part of Hue. For information about installing and
configuring Hue, see the Hue Installation
manual..

The Cloudera Impala Query UI assumes an existing Cloudera Impala
installation. The Hue installation instructions include the
configuration necessary for Impala. You can view the current
configuration from the **Settings** tab.

Starting Cloudera Impala Query UI
---------------------------------

Click the **Cloudera Impala Query UI** icon
(![image](images/icon_impala_24.png)) in the navigation bar at the top
of the Hue browser page.

Managing Databases, Tables, and Partitions
------------------------------------------

You can create databases, tables, partitions, and load data by executing
[Hive data manipulation
statements](http://archive.cloudera.com/cdh4/cdh/4/hive/language_manual/data-manipulation-statements.html)
in the Beeswax application.

You can also use the [Metastore
Manager]()
application to manage the databases, tables, and partitions and load
data.

When you change the metastore using one of these applications, you must
click the Refresh button under METASTORE CATALOG in the pane to the left
of the Query Editor to make the metastore update visible to the Cloudera
Impala server.

Installing Example Queries and Tables
-------------------------------------

![image](images/note.jpg) **Note**: You must be a superuser to perform
this task.

1.  Click ![image](images/quick_start.png). The Quick Start Wizard
    opens.
2.  Click **Step 2: Examples**.
3.  Click **Cloudera Impala Query UI**.

Query Editor
------------

The Query Editor view lets you create queries in the Cloudera Impala
Query Language, which is based on the Hive Standard Query Language
(HiveQL) and described in the Cloudera Impala Language Reference topic
in [Installing and Using Cloudera
Impala](http://www.cloudera.com/content/cloudera-content/cloudera-docs/Impala/latest/Installing-and-Using-Impala/Installing-and-Using-Impala.html).

You can name and save your queries to use later.

When you submit a query, you can either wait for the query to complete,
or return later to find the queries in the **History** view.

In the box to the left of the Query field, you can select a database,
override the default Cloudera Impala settings, enable users to enter
parameters at run-time. See [Advanced Query Settings](#advancedQuerySettings) for
details on using these settings.

### Creating Queries

1.  In the Query Editor window, type a query or multiple queries
    separated by a semicolon ";". To be presented with a drop-down of
    autocomplete options, type CTRL+spacebar when entering a query.
2.  To save your query and advanced settings to use again later, click
    **Save As**, enter a name and description, and then click **OK**. To
    save changes to an existing query, click **Save.**

### Loading Queries into the Query Editor

1.  Do one of the following:
    -   Click the My Queries tab.
        1.  Click the Recent Saved Queries or Recent Run Queries tab to
            display the respective queries.

    -   Click the Saved Queries tab.

2.  Click a query name. The query is loaded into the Query Editor.

### Running Queries

![image](images/note.jpg) **Note**: To run a query, you must be logged
in to Hue as a user that also has a Unix user account on the remote
server.

1.  To execute a portion of the query, highlight one or more query
    statements.
2.  Click **Execute**. The Query Results window appears with the results
    of your query.
    -   To view a log of the query execution, click **Log** at the top
        of the results display. You can use the information in this tab
        to debug your query.
    -   To view the query that generated these results, click **Query**
        at the top of the results display.
    -   To view the columns of the query, click **Columns**.
    -   To return to the query in the Query Editor, click **Unsaved
        Query**.

3.  If there are multiple statements in the query, click Next in the
    Multi-statement query pane to execute the remaining statements.

<a id="advancedQuerySettings"></a>
### Advanced Query Settings

The pane to the left of the Query Editor lets you specify the following
options:

<table>
<tr><td>DATABASE</td><td>The database containing the table definitions.</td></tr>
<tr><td>SETTINGS</td><td>Override the Cloudera Impala  default settings. To configure a new
setting:

<ol>
<li> Click Add.
<li> For Key, enter a Hive or Hadoop configuration variable name.
<li> For Value, enter the value you want to use for the variable.

For example, to override the directory where structured Hive query logs
are created, you would enter hive.querylog.location for Key, and a
path for Value.
</ol>
To view the default settings, click the Settings tab at the top of
the page. 
</td></tr>  
<tr><td>PARAMETERIZATION</td><td>Indicate that a dialog box should display to enter parameter values when
a query containing the string $parametername is executed. Enabled by
default.</td></tr>
<tr><td>METASTORE CATALOG</td><td>Refresh metadata. It is best to refresh metadata after making changes to
databases such as adding or dropping a table.</td></tr>
</table>


### Viewing Query History

You can view the history of queries that you have run previously.
Results for these queries are available for one week or until Hue is
restarted.

1.  Click **History**. A list of your saved and unsaved queries displays
    in the Query History window.
2.  To display the queries for all users, click **Show everyone's
    queries**. To display your queries only, click **Show my queries**.
3.  To display the automatically generated actions performed on a user's
    behalf, click **Show auto actions**. To display user queries again,
    click **Show user queries**.

### Viewing, Editing, Copying, and Deleting Saved Queries

You can view a list of saved queries of all users by clicking **My
Queries** and then selecting either Recent Saved Queries or Recent Run
Queries tab to display the respective queries or clicking **Saved
Queries**. You can copy any query, but you can edit, delete, and view
the history of only your own queries.


**Edit**

1.  Click **Saved Queries**. The Queries window displays.
2.  Check the checkbox next to the query and click **Edit**. The query
    displays in the Query Editor window.
3.  Change the query and then click **Save.** You can also click **Save
    As**, enter a new name, and click **OK** to save a copy of the
    query.

**Copy**

1.  Click **Saved Queries**. The Queries window displays.
2.  Check the checkbox next to the query and click **Copy**. The query
    displays in the Query Editor window.
3.  Change the query as necessary and then click **Save.** You can also
    click **Save As**, enter a new name, and click **OK** to save a copy
    of the query.

**Copy in Query History**

1.  Click **History**. The Query History window displays.
2.  To display the queries for all users, click **Show everyone's
    queries**. The queries for all users display in the History window.
3.  Click the query you want to copy. A copy of the query displays in
    the Query Editor window.
4.  Change the query, if necessary, and then click **Save As**, enter a
    new name, and click **OK** to save the query.

**Delete**

1.  Click **Saved Queries**. The Queries window displays.
2.  Check the checkbox next to the query and click **Delete**.
3.  Click **Yes** to confirm the deletion.
