---
title: "Querying"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

The goal of the Editor is to make data querying easy and productive.

It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, risk alerts and self service troubleshooting and query assistance. The Editor is also available in Notebook mode.

Any editor can be starred next to its name so that it becomes the default editor and the landing page when logging in.

The list of databases and configuration of the connectors is currently done by the [Administrator](/administrator/configuration/connectors/).

## Editor

![Editor](https://cdn.gethue.com/uploads/2019/08/hue_4.5.png)

### Running Queries

1.  The currently selected statement has a **left blue** border. To execute a portion of a query, highlight one or more query
    statements.
2.  Click **Execute**. The Query Results window appears.
    -   There is a Log caret on the left of the progress bar.
    -   Expand the **Columns** by clicking on the column label will scroll to the column. Names and types can be filtered.
    -   Select the **Chart** icon to plot the results
    -   To expand a row, click on the row number.
    -   To lock a row, click on the lock icon in the row number column.
    -   Search either by clicking on the magnifier icon on the results tab, or pressing Ctrl/Cmd + F
    -   [See more how to refine your results](http://gethue.com/new-features-in-the-sql-results-grid-in-hive-and-impala/).

3.  If there are multiple statements in the query (separated by semi-colons), click Next in the
    Multi-statement query pane to execute the remaining statements.

When you have multiple statements it's enough to put the cursor in the statement you want to execute, the active statement is indicated with a blue gutter marking.

**Note**: Use `CTRL/Cmd + ENTER` to execute queries.

**Note**: On top of the logs panel, there is a link to open the query profile in the Query Browser.

### Downloading and Exporting Results

There are several ways you can export results of a query.

The most common:

* Download to your computer as a CSV or XLS
* Copy the currently fetched rows to the clipboard

Two of them offer greater scalability:

 * Export to an empty folder on your cluster's file system.
 * Export to a table. You can choose an already existing table or a new one.

![Downloading and Exporting Results](https://cdn.gethue.com/uploads/2019/04/editor_export_results.png)

### Autocomplete

To make your SQL editing experience, Hue comes with one of the best SQL autocomplete on the planet. The new autocompleter knows all the ins and outs of the Hive and Impala SQL dialects and will suggest keywords, functions, columns, tables, databases, etc. based on the structure of the statement and the position of the cursor.

The result is improved completion throughout. We now have completion for more than just SELECT statements, it will help you with the other DDL and DML statements too, INSERT, CREATE, ALTER, DROP etc.

![Autocomplete and context assist](https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif)

**Smart column suggestions**

If multiple tables appear in the FROM clause, including derived and joined tables, it will merge the columns from all the tables and add the proper prefixes where needed. It also knows about your aliases, lateral views and complex types and will include those. It will now automatically backtick any reserved words or exotic column names where needed to prevent any mistakes.

**Smart keyword completion**

The autocompleter suggests keywords based on where the cursor is positioned in the statement. Where possible it will even suggest more than one word at at time, like in the case of IF NOT EXISTS, no one likes to type too much right? In the parts where order matters but the keywords are optional, for instance after FROM tbl, it will list the keyword suggestions in the order they are expected with the first expected one on top. So after FROM tbl the WHERE keyword is listed above GROUP BY etc.

**UDFs**

The improved autocompleter will now suggest functions, for each function suggestion an additional panel is added in the autocomplete dropdown showing the documentation and the signature of the function. The autocompleter know about the expected types for the arguments and will only suggest the columns or functions that match the argument at the cursor position in the argument list.

![SQL functions reference](https://cdn.gethue.com/uploads/2017/07/hue_4_functions.png)

**Sub-queries, correlated or not**

When editing subqueries it will only make suggestions within the scope of the subquery. For correlated subqueries the outside tables are also taken into account.

**Context popup**

Right click on any fragement of the queries (e.g. a table name) to gets all its metadata information. This is a handy shortcut to get more description or check what types of values are contained in the table or columns.

**Syntax checker**

A little red underline will display the incorrect syntax so that the query can be fixed before submitting. A right click offers suggestions.

**Advanced Settings**

The live autocompletion is fine-tuned for a better experience advanced settings an be accessed via `CTRL +` , (or on Mac `CMD + ,`) or clicking on the '?' icon.

The autocompleter talks to the backend to get data for tables and databases etc and caches it to keep it quick. Clicking on the refresh icon in the left assist will clear the cache. This can be useful if a new table was created outside of Hue and is not yet showing-up (Hue will regularly clear his cache to automatically pick-up metadata changes done outside of Hue).

### Sharing

Any query can be shared with permissions, as detailed in the [concepts](/user/concepts).

### Language reference

You can find the Language Reference in the right assist panel. The right panel itself has a new look with icons on the left hand side and can be minimised by clicking the active icon.

The filter input on top will only filter on the topic titles in this initial version. Below is an example on how to find documentation about joins in select statements.

![Language Reference Panel](https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_joins.gif)

While editing a statement there’s a quicker way to find the language reference for the current statement type, just right-click the first word and the reference appears in a popover below:

![Language Reference context](https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png)

### Variables
Variables are used to easily configure parameters in a query. They are ideal for saving reports that can be shared or executed repetitively:

**Single Valued**

    select * from web_logs where country_code = "${country_code}"

![Single valued variable](https://cdn.gethue.com/uploads/2017/10/var_defaults.png)

**The variable can have a default value**

    select * from web_logs where country_code = "${country_code=US}"

**Multi Valued**

    select * from web_logs where country_code = "${country_code=CA, FR, US}"

**In addition, the displayed text for multi valued variables can be changed**

    select * from web_logs where country_code = "${country_code=CA(Canada), FR(France), US(United States)}"

![Multi valued variables](https://cdn.gethue.com/uploads/2018/04/variables_multi.png)

**For values that are not textual, omit the quotes.**

    select * from boolean_table where boolean_column = ${boolean_column}

### Charting

These visualizations are convenient for plotting chronological data or when subsets of rows have the same attribute: they will be stacked together.

* Pie
* Bar/Line with pivot
* Timeline
* Scattered plot
* Maps (Marker and Gradient)

![Charts](https://cdn.gethue.com/uploads/2019/04/editor_charting.png)

### Context popup

It’s quite handy to be able to look at column samples while writing a query to see what type of values you can expect. Hue now has the ability to perform some operations on the sample data, you can now view distinct values as well as min and max values. Expect to see more operations in coming releases.

![Sample column popup](https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif)

### Notebook mode

Snippets of different dialects can be added into a single page:

![Notebook mode](https://cdn.gethue.com/uploads/2015/10/notebook-october.png)

### Dark mode

Initially this mode is limited to the actual editor area and we’re considering extending this to cover all of Hue.

![Editor Dark Mode](https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png)

To toggle the dark mode you can either press `Ctrl-Alt-T` or `Command-Option-T` on Mac while the editor has focus. Alternatively you can control this through the settings menu which is shown by pressing `Ctrl-`, or `Command-`, on Mac.

### Query troubleshooting

#### Pre-query execution

**Popular values**

The autocompleter will suggest popular tables, columns, filters, joins, group by, order by etc. based on metadata from Navigator Optimizer. A new “Popular” tab has been added to the autocomplete result dropdown which will be shown when there are popular suggestions available.

This is particularly useful for doing joins on unknown datasets or getting the most interesting columns of tables with hundreds of them.

![Popular joins suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png)
![Popular columns suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_popular_filter_agg.png)


**Risk alerts**

While editing, Hue will run your queries through Navigator Optimizer in the background to identify potential risks that could affect the performance of your query. If a risk is identified an exclamation mark is shown above the query editor and suggestions on how to improve it is displayed in the lower part of the right assistant panel.

![Query Risk alerts](https://cdn.gethue.com/uploads/2017/07/hue_4_risk_6.gif)

#### During execution

The Query Browser details the plan of the query and the bottle necks. When detected, "Health" risks are listed with suggestions on how to fix them.

![Pretty Query Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-11.40.24-AM.png)

#### Post-query execution

A new experimental panel when enabled can offer post risk analysis and recommendation on how to tweak the query for better speed.

### Presentation Mode

Turns a list of semi-colon separated queries into an interactive presentation by clicking on the 'Dashboard' icon. It is great for doing demos or reporting.

## Databases & Datawarehouses

### List
Use the query editor with [any database or datawarehouse](/administrator/configuration/connectors/). Those databases currently need to be first configured by the administrator.

### Autocompletes & Connectors
Also read about building some [better autocompletes](/developer/parsers/) or extending the connectors with SQL Alchemy, JDBC or building your own [connectors](/developer/sdk).


## Dashboards

Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.

![Search Full](https://cdn.gethue.com/uploads/2015/08/search-full-mode.png)

Simply drag & drop widgets that are interconnected together. This is great for exploring new datasets or monitoring without having to type.

The top search bar offers a [full autocomplete](http://gethue.com/intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/) on all the values of the index.

The “More like This” feature lets you selected fields you would like to use to find similar records. This is a great way to find similar issues, customers, people... with regard to a list of attributes.

### Marker Map
Points close to each other are grouped together and will expand when zooming-in. A Yelp-like search filtering experience can also be created by checking the box.

![Marker Map](https://cdn.gethue.com/uploads/2015/08/search-marker-map.png)

### Edit records

Indexed records can be directly edited in the Grid or HTML widgets by admins.

### link to original documents

Links to the original documents can also be inserted. Add to the record a field named ‘link-meta’ that contains some json describing the URL or address of a table or file that can be open in the HBase Browser, Metastore App or File Browser:

Any link

    {'type': 'link', 'link': 'gethue.com'}

HBase Browser

    {'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527'}
    {'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1'}
    {'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1', 'col': 'c1'}

File Browser

    {'type': 'hdfs', 'path': '/data/hue/file.txt'}

Table Catalog

    {'type': 'hive', 'database': 'default', 'table': 'sample_07'}

![Data Links](https://cdn.gethue.com/uploads/2015/08/search-link-1024x630.png)

### Save queries

Current selected facets and filters, query strings can be saved with a name within the dashboard. These are useful for defining “cohorts” or pre-selection of records and quickly reloading them.

![Rolling time](https://cdn.gethue.com/uploads/2015/08/search-query-def-1024x507.png)

### ‘Fixed’ or ‘rolling’ time window

Real time indexing can now shine with the rolling window filter and the automatic refresh of the dashboard every N seconds. See it in action in the real time Twitter indexing with Spark streaming post.

![Rolling time](https://cdn.gethue.com/uploads/2015/08/search-fixed-time.png)

### Nested Analytics facets

![Nested Analytics facets](https://cdn.gethue.com/uploads/2015/08/search-nested-facet-1024x304.png)
![Nested Analytics Counts](https://cdn.gethue.com/uploads/2015/08/search-hit-widget.png)

A more comprehensive demo is available on the [BikeShare data visualization post](http://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/).



## Jobs

In addition to SQL queries, the Editor application enables you to create and submit batch jobs to the cluster.

### Spark

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
      show_notebooks=true

    [[interpreters]]

      [[[hive]]]
        name=Hive
        interface=hiveserver2

      [[[spark]]]
        name=Scala
        interface=livy

      [[[pyspark]]]
        name=PySpark
        interface=livy

#### Batch

This is a quick way to submit any Jar or Python jar/script to a cluster via the Scheduler or Editor.

How to run Spark jobs with Spark on YARN? This often requires trial and error in order to make it work.

Hue is leveraging Apache Oozie to submit the jobs. It focuses on the yarn-client mode, as Oozie is already running the spark-summit command in a MapReduce2 task in the cluster. You can read more about the Spark modes here.

[Here is how to get started successfully](http://gethue.com/how-to-schedule-spark-jobs-with-spark-on-yarn-and-oozie/).
And how to use the [Spark Action](http://gethue.com/use-the-spark-action-in-oozie/).

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

### MapReduce

A MapReduce job design consists of MapReduce functions written in Java.
You can create a MapReduce job design from existing mapper and reducer
classes without having to write a main Java class. You must specify the
mapper and reducer classes as well as other MapReduce properties in the
Job Properties setting.

### DistCp

A DistCp job design consists of a DistCp command.
