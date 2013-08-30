
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

Beeswax
=======

The Beeswax application enables you to perform queries on Apache Hive, a
data warehousing system designed to work with Hadoop. For information
about Hive, see [Hive
Documentation](http://archive.cloudera.com/cdh4/cdh/4/hive/). You can
create Hive databases, tables and partitions, load data, create, run,
and manage queries, and download the results in a Microsoft Office Excel
worksheet file or a comma-separated values file.

Beeswax and Hive Installation and Configuration
-----------------------------------------------

Beeswax is installed and configured as part of Hue. For information
about installing and configuring Hue, see the Hue Installation
manual.

Beeswax assumes an existing Hive installation. The Hue installation
instructions include the configuration necessary for Beeswax to access
Hive. You can view the current Hive configuration from the **Settings**
tab in the Beeswax application.

By default, a Beeswax user can see the saved queries for all users -
both his/her own queries and those of other Beeswax users. To restrict
viewing saved queries to the query owner and Hue administrators, set the
share\_saved\_queries property under the [beeswax] section in the Hue
configuration file to false.

Starting Beeswax
----------------

Click the **Beeswax** icon (![image](images/icon_beeswax_24.png)) in the
navigation bar at the top of the Hue browser page.

Managing Databases, Tables, and Partitions
------------------------------------------

You can create databases, tables, partitions, and load data by executing
[Hive data manipulation
statements](http://archive.cloudera.com/cdh4/cdh/4/hive/language_manual/data-manipulation-statements.html)
in the Beeswax application.

You can also use the [Metastore
Manager](../metastore_manager.html)
application to manage the databases, tables, and partitions and load
data.

Installing Example Queries and Tables
-------------------------------------

![image](images/note.jpg) **Note**: You must be a superuser to perform
this task.

1.  Click ![image](images/quick_start.png). The Quick Start Wizard
    opens.
2.  Click **Step 2: Examples**.
3.  Click **Beeswax (Hive UI)**.

Query Editor
------------

The Query Editor view lets you create, save, and submit queries in the
[Hive Query Language
(HQL)](http://wiki.apache.org/hadoop/Hive/LanguageManual), which is
similar to Structured Query Language (SQL). When you submit a query, the
Beeswax Server uses Hive to run the queries. You can either wait for the
query to complete, or return later to find the queries in the History
view. You can also request to receive an email message after the query
is completed.

In the box to the left of the Query field, you can select a database,
override the default Hive and Hadoop settings, specify file resources
and user-defined functions, enable users to enter parameters at
run-time, and request email notification when the job is complete. See
[Advanced Query Settings](#advancedQuerySettings) for details on using these
settings.

### Creating Queries

1.  In the Query Editor window, type a query or multiple queries
    separated by a semicolon ";". To be presented with a drop-down of
    autocomplete options, type CTRL+spacebar when entering a query.
2.  To save your query and advanced settings to use again later, click
    **Save As**, enter a name and description, and then click **OK**. To
    save changes to an existing query, click **Save.**
3.  If you want to view the execution plan for the query, click
    **Explain**. For more information, see
    [http://wiki.apache.org/hadoop/Hive/LanguageManual/Explain](http://wiki.apache.org/hadoop/Hive/LanguageManual/Explain).

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

![image](images/note.jpg) **Note**: Under **MR JOBS**, you can view any
MapReduce jobs that the query generated.

### Downloading and Saving Query Results

![image](images/important.jpg) **Important**:

-   You can only save results to a file when the results were generated
    by a MapReduce job.
-   This is the preferred way to save when the result is large (for
    example \> 1M rows).

1.  Do any of the following to download or save the query results:
    -   Click **Download as CSV** to download the results in a
        comma-separated values file suitable for use in other
        applications.
    -   Click **Download as XLS** to download the results in a Microsoft
        Office Excel worksheet file.
    -   Click **Save** to save the results in a table or HDFS file.
        -   To save the results in a new table, select **In a new
            table**, enter a table name, and then click **Save**.
        -   To save the results in an HDFS file, select **In an HDFS
            directory**, enter a path and then click **Save**. You can
            then download the file with [File Browser](../filebrowser.html).

<a id="advancedQuerySettings"></a>
### Advanced Query Settings

The pane to the left of the Query Editor lets you specify the following
options:


<table>
<tr><td>DATABASE</td><td>The database containing the table definitions.</td></tr>
<tr><td>SETTINGS</td><td>Override the Hive and Hadoop default settings. To configure a new
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
the page. For information about Hive configuration variables, see:
[http://wiki.apache.org/hadoop/Hive/AdminManual/Configuration](http://wiki.apache.org/hadoop/Hive/AdminManual/Configuration).
For information about Hadoop configuration variables, see:
[http://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml](http://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml).</td></tr>
<tr><td>FILE RESOURCES</td><td>Make files locally accessible at query execution time available on the
Hadoop cluster. Hive uses the Hadoop Distributed Cache to distribute the
added files to all machines in the cluster at query execution time.

<ol>
<li>  Click Add to configure a new setting.
<li>   From the Type drop-down menu, choose one of the following:
<ul>
   <li>jar - Adds the specified resources to the Java classpath.
   <li>archive - Unarchives the specified resources when
        distributing them.
    <li>file - Adds the specified resources to the distributed
        cache. Typically, this might be a transform script (or similar)
        to be executed.

<li>   For Path, enter the path to the file or click
    ![image](images/browse.png) to browse and select the file.
</ol>

![image](images/note.jpg) Note: It is not necessary to specify files
used in a transform script if the files are available in the same path
on all machines in the Hadoop cluster.</td></tr>
<tr><td>USER-DEFINED FUNCTIONS</td><td>Specify user-defined functions. Click Add to configure a new
setting. Specify the function name in the Name field, and specify
the class name for Classname.

You *must* specify a JAR file for the user-defined functions in FILE RESOURCES.

To include a user-defined function in a query, add a $ (dollar sign)
before the function name in the query. For example, if MyTable is a
user-defined function name in the query, you would type: SELECT $MyTable
</td></tr>
<tr><td>PARAMETERIZATION</td><td>Indicate that a dialog box should display to enter parameter values when
a query containing the string $parametername is executed. Enabled by
default.</td></tr>
<tr><td>EMAIL NOTIFICATION</td><td>Indicate that an email message should be sent after a query completes.
The email is sent to the email address specified in the logged-in user's
profile.</td></tr>
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
