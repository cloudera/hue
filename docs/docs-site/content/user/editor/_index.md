---
title: "Editor"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

The goal of Hue's Editor is to make data querying easy and productive.

It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, [risk alerts and self service troubleshooting](http://gethue.com/hue-4-sql-editor-improvements/) and query assistance.

Any editor can be `starred` next to its name so that it becomes the default editor and the landing page when logging in.

Configuration of the connectors is currently done by the [Administrator]({{% param baseURL %}}administrator/configuration/editor/).

## Concepts
### Running Queries

1.  The currently selected statement has a left blue order. To execute a portion of a query, highlight one or more query
    statements.
2.  Click **Execute**. The Query Results window appears.
    -   There is a **Log** caret on the left of the progress bar.
    -   To view the columns of the query, expand the **Columns** icon. Clicking
        on the column label will scroll to the column. Names and types can be filtered.
    -   Select the chart icon to plot the results
    -   To expand a row, click on the row number.
    -   To lock a row, click on the lock icon in the row number column.
    -   Search either by clicking on the magnifier icon on the results tab, or pressing Ctrl/Cmd + F
    -   [See more how to refine your results](http://gethue.com/new-features-in-the-sql-results-grid-in-hive-and-impala/).

3.  If there are multiple statements in the query (separated by semi-colons), click Next in the
    Multi-statement query pane to execute the remaining statements.

When you have multiple statements it's enough to put the cursor in the statement you want to execute, the active statement is indicated with a blue gutter marking.

**Note**: Use CTRL/Cmd + ENTER to execute queries.

**Note**: Under the logs panel, you can view any
MapReduce or [Impala jobs](#impala-queries) that the query generated.

**Advanced Query Settings**

The pane to the top of the Editor lets you specify the following
options:

* Settings: depends on the query engines. For information about [Hive configuration variables](http://wiki.apache.org/hadoop/Hive/AdminManual/Configuration).
* Files: load a jar of files to use as UDF
* UDFs: register a custom function

### Downloading and Exporting Results

To get things started, press the export icon, the bottom last element of the action bar to the top left of the results. There are several ways you can export results of a query.

Two of them offer great scalability:
1.  Export to an empty folder on your cluster's file system. This exports the results using multiple files. In the export icon, choose Export and then All.
2.  Export to a table. You can choose an already existing table or a new one. In the export icon, choose Export and then Table.

Two of them offer limited scalability:
1.  Export to a file on your cluster's file systems. This exports the results to a single file. In the export icon, choose Export and then First XXX.
2.  Download to your computer as a CSV or XLS. This exports the results to a single file in comma-separated values or Microsoft Office Excel format. In the export icon, choose Download as CSV or Download as XLS.


### Autocomplete

To make your SQL editing experience, Hue comes with one of the best SQL autocomplete on the planet. The new autocompleter knows all the ins and outs of the Hive and Impala SQL dialects and will suggest keywords, functions, columns, tables, databases, etc. based on the structure of the statement and the position of the cursor.

The result is improved completion throughout. We now have completion for more than just SELECT statements, it will help you with the other DDL and DML statements too, INSERT, CREATE, ALTER, DROP etc.

**Smart column suggestions**

If multiple tables appear in the FROM clause, including derived and joined tables, it will merge the columns from all the tables and add the proper prefixes where needed. It also knows about your aliases, lateral views and complex types and will include those. It will now automatically backtick any reserved words or exotic column names where needed to prevent any mistakes.

**Smart keyword completion**

The autocompleter suggests keywords based on where the cursor is positioned in the statement. Where possible it will even suggest more than one word at at time, like in the case of IF NOT EXISTS, no one likes to type too much right? In the parts where order matters but the keywords are optional, for instance after FROM tbl, it will list the keyword suggestions in the order they are expected with the first expected one on top. So after FROM tbl the WHERE keyword is listed above GROUP BY etc.

**UDFs**

The improved autocompleter will now suggest functions, for each function suggestion an additional panel is added in the autocomplete dropdown showing the documentation and the signature of the function. The autocompleter know about the expected types for the arguments and will only suggest the columns or functions that match the argument at the cursor position in the argument list.

**Sub-queries, correlated or not**

When editing subqueries it will only make suggestions within the scope of the subquery. For correlated subqueries the outside tables are also taken into account.

**Context popup**

Right click on any fragement of the queries (e.g. a table name) to gets all its metadata information. This is a handy shortcut to get more description or check what types of values are contained in the table or columns.

**Syntax checker**

A little red underline will display the incorrect syntax so that the query can be fixed before submitting. A right click offers suggestions.

**All about quality**

The live autocompletion is fine-tuned for a better experience advanced settings an be accessed via CTRL + , (or on Mac CMD + ,) or clicking on the '?' icon.

The autocompleter talks to the backend to get data for tables and databases etc and caches it to keep it quick. Clicking on the refresh icon in the left assist will clear the cache. This can be useful if a new table was created outside of Hue and is not yet showing-up (Hue will regularly clear his cache to automatically pick-up metadata changes done outside of Hue).

### Variables
Variables are used to easily configure parameters in a query. They are ideal for saving reports that can be shared or executed repetitively:

**Single Valued**

    select * from web_logs where country_code = "${country_code}"

**The variable can have a default value**

    select * from web_logs where country_code = "${country_code=US}"

**Multi Valued**

    select * from web_logs where country_code = "${country_code=CA, FR, US}"

**In addition, the displayed text for multi valued variables can be changed**

    select * from web_logs where country_code = "${country_code=CA(Canada), FR(France), US(United States)}"

**For values that are not textual, omit the quotes.**

    select * from boolean_table where boolean_column = ${boolean_column}

### Charting

These visualizations are convenient for plotting chronological data or when subsets of rows have the same attribute: they will be stacked together.

* Pie
* Bar/Line with pivot
* Timeline
* Scattered plot
* Maps (Marker and Gradient)

Read more about extending [charts](../../developer/).

### Self service troubleshooting

#### Pre-query execution

**Popular values**

The autocompleter will suggest popular tables, columns, filters, joins, group by, order by etc. based on metadata from Navigator Optimizer. A new “Popular” tab has been added to the autocomplete result dropdown which will be shown when there are popular suggestions available.

This is particularly useful for doing joins on unknown datasets or getting the most interesting columns of tables with hundreds of them.

**Risk alerts**

While editing, Hue will run your queries through Navigator Optimizer in the background to identify potential risks that could affect the performance of your query. If a risk is identified an exclamation mark is shown above the query editor and suggestions on how to improve it is displayed in the lower part of the right assistant panel.

See a video on  [Self service troubleshooting](http://gethue.com/hue-4-sql-editor-improvements/).

#### During execution

The Query Profile visualizer details the plan of the query and the bottle necks. When detected, "Health" risks are listed with suggestions on how to fix them.

#### Post-query execution

A new experimental panel when enabled can offer post risk analysis and recommendation on how to tweak the query for better speed.


### Presentation Mode

Turns a list of semi-colon separated queries into an interactive presentation. It is great for doing demos or basic reporting.

## SQL Databases

Use the query editor with any database. Those databases need to be configured by the [administratior]({{% param baseURL %}}administrator/configuration/editor/)

### Apache Hive
### Apache Impala
### MySQL
### Oracle
### KSQL / Apache Kafka SQL
### Apache Solr SQL

With Solr 5+, query collections like we would query a regular Hive or Impala table.

[Read more about it here](http://gethue.com/sql-editor-for-solr-sql/).

As Solr SQL is pretty recent, there are some caveats, notably Solr lacks support of:

* SELECT *
* WHERE close with a LIKE
* resultset pagination

which prevents a SQL UX experience comparable to the standard other databases (but we track it in [HUE-3686](https://issues.cloudera.org/browse/HUE-3686)).

### Apache Presto

Presto is a high performance, distributed SQL query engine for big data.

[Read more about it here](https://prestosql.io/)

### PostgreSQL
### Redshift
### BigQuery
### AWS Athena
### Spark SQL
### Apache Phoenix
### Apache Druid

Apache Druid is an ["OLAP style"](http://druid.io/) database.

### Apache Kylin
Apache Kylin is an open-source online analytical processing (OLAP) engine.
See how to configure the [Kylin Query Editor](http://gethue.com/using-hue-to-interact-with-apache-kylin/).

### Others
Extend with SQL Alchemy, JDBC or build your own [connectors](../../developer/).

## Jobs

In addition to SQL queries, the Editor application enables you to create and submit batch jobs to the cluster.

### Pig

Type [Apache Pig](https://pig.apache.org/) Latin instructions to load/merge data to perform ETL or Analytics.

### Sqoop

Run an SQL import from a traditional relational database via an [Apache Sqoop](https://sqoop.apache.org/) command.

### Shell

Type or specify a path to a regular shell script.

[Read more about it here](http://gethue.com/use-the-shell-action-in-oozie/).

### Java

A Java job design consists of a main class written in Java.

<table>
<tr><td>Jar path</td><td>The fully-qualified path to a JAR file containing the main class.</td></tr>
<tr><td>Main class</td><td>The main class to invoke the program.</td></tr>
<tr><td>Args</td><td>The arguments to pass to the main class.</td></tr>
<tr><td>Java opts</td><td>The options to pass to the JVM.</td></tr>
</table>

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

### MapReduce

A MapReduce job design consists of MapReduce functions written in Java.
You can create a MapReduce job design from existing mapper and reducer
classes without having to write a main Java class. You must specify the
mapper and reducer classes as well as other MapReduce properties in the
Job Properties setting.

### DistCp

A DistCp job design consists of a DistCp command.
