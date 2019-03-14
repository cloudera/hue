---
title: "SQL Editor / Notebook"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

The goal of Hue's Editor is to make data querying easy and productive.

It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, search & tagging of data and query assistance.

The [custom SQL Editor page](http://gethue.com/custom-sql-query-editors/) also describes the configuration steps. Any editor can be `starred`
next to its name so that it becomes the default editor and the landing page when logging in.

First, in your hue.ini file, you will need to add the relevant database connection information under the librdbms section:

    [librdbms]
      [[databases]]
        [[[postgresql]]]
        nice_name=PostgreSQL
        name=music
        engine=postgresql_psycopg2
        port=5432
        user=hue
        password=hue
        options={}

Secondly, we need to add a new interpreter to the notebook app. This will allow the new database type to be registered as a snippet-type in the Notebook app. For query editors that use a Django-compatible database, the name in the brackets should match the database configuration name in the librdbms section (e.g. – postgresql). The interface will be set to rdbms. This tells Hue to use the librdbms driver and corresponding connection information to connect to the database. For example, with the above postgresql connection configuration in the librdbms section, we can add a PostgreSQL interpreter with the following notebook configuration:

    [notebook]
      [[interpreters]]
        [[[postgresql]]]
        name=PostgreSQL
        interface=rdbms

## Concepts
### Running Queries

![image](images/note.jpg) **Note**: To run a query, you must be logged
in to Hue as a user that also has a Unix user account on the remote
server.

1.  To execute a portion of the query, highlight one or more query
    statements.
2.  Click **Execute**. The Query Results window appears with the results
    of your query.
    -   To view a log of the query execution, toggle the **Log** caret on the
        left of the progress bar. You can use the information in this tab
        to debug your query.
    -   To view the columns of the query, expand the **Columns** icon. Clicking
        on the column label will scroll to the column. Names and types can be filtered.
    -   To expand a row, double click on it or click on the row number.
    -   To lock a row, click on the lock icon in the row number column.
    -   Search either by clicking on the magnifier icon on the results tab, or pressing Ctrl/Cmd + F
    -   [See more how to refine your results](http://gethue.com/new-features-in-the-sql-results-grid-in-hive-and-impala/).

3.  If there are multiple statements in the query (separated by semi-colons), click Next in the
    Multi-statement query pane to execute the remaining statements.

When you have multiple statements it's enough to put the cursor in the statement you want to execute, the active statement is indicated with a blue gutter marking.

![image](images/note.jpg) **Note**: Use CTRL/Cmd + ENTER to execute queries.

![image](images/note.jpg) **Note**: Under the logs panel, you can view any
MapReduce or [Impala jobs](#impala-queries) that the query generated.

### Downloading and Exporting Query Results

To get things started, press the export icon, the bottom last element of the action bar to the top left of the results. There are several ways you can export results of a query.

![image](images/note.jpg) Two of them offer great scalability:
1.  Export to an empty folder on your cluster's file system. This exports the results using multiple files. In the export icon, choose Export and then All.
2.  Export to a table. You can choose an already existing table or a new one. In the export icon, choose Export and then Table.

![image](images/note.jpg) Two of them offer limited scalability:
1.  Export to a file on your cluster's file systems. This exports the results to a single file. In the export icon, choose Export and then First XXX.
2.  Download to your computer as a CSV or XLS. This exports the results to a single file in comma-separated values or Microsoft Office Excel format. In the export icon, choose Download as CSV or Download as XLS.


<a id="advancedQuerySettings"></a>
### Advanced Query Settings

The pane to the top of the Editor lets you specify the following
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
</table>

### Autocomplete

To make your SQL editing experience better we've created a  new autocompleter for Hue 3.11. The old one had some limitations and was only aware of parts of the statement being edited. The new autocompleter knows all the ins and outs of the Hive and Impala SQL dialects and will suggest keywords, functions, columns, tables, databases, etc. based on the structure of the statement and the position of the cursor.

The result is improved completion throughout. We now have completion for more than just SELECT statements, it will help you with the other DDL and DML statements too, INSERT, CREATE, ALTER, DROP etc.

**Smart column suggestions**

If multiple tables appear in the FROM clause, including derived and joined tables, it will merge the columns from all the tables and add the proper prefixes where needed. It also knows about your aliases, lateral views and complex types and will include those. It will now automatically backtick any reserved words or exotic column names where needed to prevent any mistakes.


**Smart keyword completion**

The new autocompleter suggests keywords based on where the cursor is positioned in the statement. Where possible it will even suggest more than one word at at time, like in the case of IF NOT EXISTS, no one likes to type too much right? In the parts where order matters but the keywords are optional, for instance after FROM tbl, it will list the keyword suggestions in the order they are expected with the first expected one on top. So after FROM tbl the WHERE keyword is listed above GROUP BY etc.


**UDFs**

The improved autocompleter will now suggest functions, for each function suggestion an additional panel is added in the autocomplete dropdown showing the documentation and the signature of the function. The autocompleter know about the expected types for the arguments and will only suggest the columns or functions that match the argument at the cursor position in the argument list.


**Sub-queries, correlated or not**

When editing subqueries it will only make suggestions within the scope of the subquery. For correlated subqueries the outside tables are also taken into account.

**All about quality**

We've fine-tuned the live autocompletion for a better experience and we've introduced some options under the editor settings where you can turn off live autocompletion or disable the autocompleter altogether (if you're adventurous). To access these settings open the editor and focus on the code area, press CTRL + , (or on Mac CMD + ,) and the settings will appear.

The autocompleter talks to the backend to get data for tables and databases etc. by default it will timeout after 5 seconds but once it has been fetched it's cached for the next time around. The timeout can be adjusted in the Hue server configuration.

We've got an extensive test suite but not every possible statement is covered, if the autocompleter can't interpret a statement it will be silent and no drop-down will appear. If you encounter a case where you think it should suggest something but doesn't or if it gives incorrect suggestions then please let us know.

Learn more about it in [Autocompleter for Hive and Impala](http://gethue.com/brand-new-autocompleter-for-hive-and-impala/).

### Variables
Variables are used to easily configure parameters in a query. They can be of two types:


<b>Single Valued</b>
<pre>
select * from web_logs where country_code = "${country_code}"
</pre>
The variable can have a default value.
<pre>
select * from web_logs where country_code = "${country_code=US}"
</pre>
<b>Multi Valued</b>
<pre>
select * from web_logs where country_code = "${country_code=CA, FR, US}"
</pre>
In addition, the displayed text for multi valued variables can be changed.
<pre>
select * from web_logs where country_code = "${country_code=CA(Canada), FR(France), US(United States)}"
</pre>
For values that are not textual, omit the quotes.
<pre>
select * from boolean_table where boolean_column = ${boolean_column}
</pre>

### Syntax checker

A little red underline will display the incorrect syntax so that the query can be fixed before submitting. A right click offers suggestions.

### Query Assist

Read more about the [Query Assistant with Navigator Optimizer Integration
](https://blog.cloudera.com/blog/2017/08/new-in-cloudera-enterprise-5-12-hue-4-interface-and-query-assistant/).

### Charting

These visualizations are convenient for plotting chronological data or when subsets of rows have the same attribute: they will be stacked together.

* Pie
* Bar/Line with pivot
* Timeline
* Scattered plot
* Maps (Marker and Gradient)

Read more about extending [charts](../sdk/sdk.html).

### Risk Alerts

The autocompleter will suggest popular tables, columns, filters, joins, group by, order by etc. based on metadata from Navigator Optimizer. A new “Popular” tab has been added to the autocomplete result dropdown which will be shown when there are popular suggestions available.

**Risk and suggestions**

While editing, Hue will run your queries through Navigator Optimizer in the background to identify potential risks that could affect the performance of your query. If a risk is identified an exclamation mark is shown above the query editor and suggestions on how to improve it is displayed in the lower part of the right assistant panel.

### Presentation Mode

Turns a list of semi-colon separated queries into an interactive presentation. It is great for doing demos or basic reporting.

## SQL Databases

Use the query editor with any database.

### Hive
### Impala
### MySQL
### Oracle
### KSQL / Kafka SQL
### Solr SQL

With Solr 5+, query collections like we would query a regular Hive or Impala table.

[Read more about it here](http://gethue.com/sql-editor-for-solr-sql/).

As Solr SQL is pretty recent, there are some caveats, notably Solr lacks support of:

* SELECT *
* WHERE close with a LIKE
* resultset pagination

which prevents a SQL UX experience comparable to the standard other databases (but we track it in [HUE-3686](https://issues.cloudera.org/browse/HUE-3686)).

### Presto

Presto is a high performance, distributed SQL query engine for big data.

[Read more about it here](https://prestosql.io/)

### PostgreSQL
### Redshift
### BigQuery
### AWS Athena
### Spark SQL
### Phoenix
### Kylin
Apache Kylin is an open-source online analytical processing (OLAP) engine.
See how to configure the [Kylin Query Editor](http://gethue.com/using-hue-to-interact-with-apache-kylin/).

### Others
Extend with SQL Alchemy, JDBC or build your own [connectors](../sdk/sdk.html#sql).

## Jobs

The Editor application enables you to create and submit jobs to
the cluster. You can include variables with your jobs to enable
you and other users to enter values for the variables when they run your
job.

All job design settings except Name and Description support the use of
variables of the form $variable\_name. When you run the job, a dialog
box will appear to enable you to specify the values of the variables.

<table>
<tr><td>Name</td><td>Identifies the job and its collection of properties and parameters.</td></tr>
<tr><td>Description</td><td>A description of the job. The description is displayed in the dialog box
that appears if you specify variables for the job.</td></tr>
<tr><td>Advanced</td><td>Advanced settings:<ul><li>Is shared- Indicate whether to share the action with all users.<li>Oozie parameters - parameters to pass to Oozie</td></tr>
<tr><td>Prepare</td><td>Specifies paths to create or delete before starting the workflow job.</td></tr>
<tr><td>Params</td><td>Parameters to pass to a script or command. The parameters are expressed
using the <a href="http://jcp.org/aboutJava/communityprocess/final/jsr152/">JSP 2.0 Specification (JSP.2.3) Expression
Language</a>,
allowing variables, functions, and complex expressions as parameters.</td></tr>
<tr><td>Job Properties</td><td>Job properties. To set a property value, click <b>Add Property</b>.<ol><li>Property name -  a configuration property name. This field provides autocompletion, so you can type the first few characters of a property name and then select the one you want from the drop-down
    list.<li>Valuethe property value.</td></tr>
<tr><td>Files</td><td>Files to pass to the job. Equivalent to the Hadoop -files option.</td></tr>
<tr><td>Archives</td><td>Files to pass to the job. Archives to pass to the job. Equivalent to the Hadoop -archives option.</td></tr></table>

### MapReduce

A MapReduce job design consists of MapReduce functions written in Java.
You can create a MapReduce job design from existing mapper and reducer
classes without having to write a main Java class. You must specify the
mapper and reducer classes as well as other MapReduce properties in the
Job Properties setting.

<table>
<tr><td>Jar path</td><td>The fully-qualified path to a JAR file containing the classes that
implement the Mapper and Reducer functions.</td></tr>
</table>

### Java

A Java job design consists of a main class written in Java.

<table>
<tr><td>Jar path</td><td>The fully-qualified path to a JAR file containing the main class.</td></tr>
<tr><td>Main class</td><td>The main class to invoke the program.</td></tr>
<tr><td>Args</td><td>The arguments to pass to the main class.</td></tr>
<tr><td>Java opts</td><td>The options to pass to the JVM.</td></tr>
</table>

### Pig

A Pig job design consists of a Pig script.

<table>
<tr><td>Script name</td><td>Script name or path to the Pig script.</td></tr>
</table>

### Sqoop

A Sqoop job design consists of a Sqoop command.

<table>
<tr><td>Command</td><td>The Sqoop command.</td></tr>
</table>

### Shell

A Shell job design consists of a shell command.

<table>
<tr><td>Command</td><td>The shell command.</td></tr>
<tr><td>Capture output</td><td>Indicate whether to capture the output of the command.</td></tr>
</table>

[Read more about it here](http://gethue.com/use-the-shell-action-in-oozie/).

### DistCp

A DistCp job design consists of a DistCp command.


### Spark

#### Batch

This is a quick way to submit any Jar or Python jar/script to a cluster via the Scheduler or Editor.

How to run Spark jobs with Spark on YARN? This often requires trial and error in order to make it work.

Hue is leveraging Apache Oozie to submit the jobs. It focuses on the yarn-client mode, as Oozie is already running the spark-summit command in a MapReduce2 task in the cluster. You can read more about the Spark modes here.

[Here is how to get started successfully](http://gethue.com/how-to-schedule-spark-jobs-with-spark-on-yarn-and-oozie/).
And how to use the [Spark Action](http://gethue.com/use-the-spark-action-in-oozie/).

#### Interactive

Hue relies on [Livy](http://livy.io/) for the interactive Scala, Python and R snippets.

Livy got initially developed in the Hue project but got a lot of traction and was moved to its own project on livy.io. Here is a tutorial on how to use a notebook to perform some Bike Data analysis.

Read more about it:

* [How to use the Livy Spark REST Job Server API for doing some interactive Spark with curl](http://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark-2-2/)
* [How to use the Livy Spark REST Job Server API for submitting batch jar, Python and Streaming Jobs](http://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-submitting-batch-jar-python-and-streaming-spark-jobs/)

Make sure that the Notebook and interpreters are set in the hue.ini, and Livy is up and running:

<pre>
[spark]
  # Host address of the Livy Server.
  livy_server_host=localhost

[notebook]

 ## Show the notebook menu or not
 show_notebooks=true

[[interpreters]]
    # Define the name and how to connect and execute the language.

    [[[hive]]]
      # The name of the snippet.
      name=Hive
      # The backend connection to use to communicate with the server.
      interface=hiveserver2

   [[[spark]]]
     name=Scala
     interface=livy

    [[[pyspark]]]
      name=PySpark
      interface=livy
</pre>
