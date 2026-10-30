---
title: "Querying"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

Use Hue to query databases and data warehouses. You can first explore your data sources with the [browsers](/user/browsing/).

* The Editor runs SQL queries. It provides autocomplete, syntax checking, and query assistance.
* The Notebook mode of the Editor runs small programming snippets. It is hidden by default (`show_notebooks=false` in `[notebook]`).
* Dashboards visualize indexed data. They can also query SQL databases.

Your [administrator](/administrator/configuration/connectors/) configures the connectors.

## Editor

![Editor](https://cdn.gethue.com/uploads/2019/08/hue_4.5.png)

### Running queries

Running SQL is the main use of the Editor. See the list of supported [databases and data warehouses](/administrator/configuration/connectors/).

1.  Type your query. The active statement has a blue marker in the left gutter. To run only part of the editor content, select one or more statements.
2.  Click **Execute**, or press `Ctrl + Enter` (`Cmd + Enter` on macOS). The results appear below the editor:
    -   Click the caret on the left of the progress bar to show the log.
    -   Click a column label in the **Columns** list to scroll to that column. You can filter the list by name and type.
    -   Click the **Chart** icon to plot the results.
    -   Click a row number to expand the row.
    -   Click the lock icon in the row number column to lock the row.
    -   Click the magnifier icon on the results tab, or press `Ctrl/Cmd + F`, to search the results.
3.  If the editor contains **multiple statements** separated by semicolons, click **Next** in the multi-statement pane to run the next statement.

To run a single statement, put the cursor in it and execute.

For more on working with results, see [Refining](#refining).

> **Note**: A link at the top of the log panel opens the query profile in the [Query Browser](/user/browsing/#sql-queries).

### Results

#### Refining

Lock rows to compare them with other rows. Hover a row number and click the lock icon. The row sticks to the top of the table.

![Result row locking](https://cdn.gethue.com/uploads/2016/08/lock_rows.gif)

The column list follows the result grid. You can filter it by data type and resize it.

![Smart headers](https://cdn.gethue.com/uploads/2016/08/column_list.gif)

Headers of columns with long content stay visible as you scroll.

![Cell content search](https://cdn.gethue.com/uploads/2016/08/headers.gif)

Search for cell values in the table. Matches are highlighted.

To search, click the magnifier icon on the results tab, or press `Ctrl/Cmd + F`.

![Virtual cell rendering](https://cdn.gethue.com/uploads/2016/08/search.gif)

The grid renders only the visible cells, so tables with hundreds of columns stay responsive.

![Many cells](https://cdn.gethue.com/uploads/2016/08/virtual_renderer.gif)

If a download to Excel or CSV takes long, Hue shows a message while it prepares the file.

![Many cells](https://cdn.gethue.com/uploads/2016/08/downloadwait.gif)

#### Downloading

Use the **Export results** (download) icon to get the results of a query.

For small results:

* Download as CSV or XLS to your computer. Your administrator sets the row and size limits of downloads.
* Copy the displayed rows to the clipboard.

For larger results, select **Export** to save the result:

* To an empty folder on your file system.
* To a table. You can choose an existing table or a new one.

![Downloading and Exporting Results](https://cdn.gethue.com/uploads/2019/04/editor_export_results.png)

### Autocomplete

The autocompleter understands the structure of the statement and the cursor position. It suggests keywords, functions, columns, tables, and databases. It supports the Hive and Impala dialects, and covers DDL and DML statements such as `INSERT`, `CREATE`, `ALTER`, and `DROP`, not only `SELECT`.

![Autocomplete and context assist](https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif)

**Smart column suggestions**

If several tables appear in the `FROM` clause, including derived and joined tables, Hue merges their columns and adds prefixes where needed. It knows your aliases, lateral views, and complex types. It adds backticks around reserved words and unusual column names.

**Smart keyword completion**

Keyword suggestions depend on the cursor position. Hue can suggest several words at once, such as `IF NOT EXISTS`. Where keywords are optional but ordered, it lists them in the expected order. For example, after `FROM tbl`, `WHERE` is listed above `GROUP BY`.

**Functions**

The autocompleter suggests functions. Each suggestion shows the function documentation and signature in an extra panel. It knows the expected argument types and only suggests columns or functions that match the argument at the cursor.

<img src="https://cdn.gethue.com/uploads/2017/07/hue_4_functions.png" alt="SQL functions reference" height="400"/>

**Sub-queries, correlated or not**

In a subquery, suggestions are limited to the scope of the subquery. For correlated subqueries, the outer tables are included.

**Context popup**

Right-click any part of a query, such as a table name, to see its metadata. Use it to read descriptions and check the values in a table or column.

The popup also shows column samples. You can view distinct, minimum, and maximum values of the sample.

![Sample column popup](https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif)

**Syntax checker**

Hue underlines incorrect syntax in red so you can fix the query before you run it. Right-click the underlined text to see suggestions.

![Syntax checker](https://cdn.gethue.com/uploads/2018/01/syntax_checkerhigh.png)

![Syntax checker](https://cdn.gethue.com/uploads/2018/01/checker_help.png)

**Advanced Settings**

To change autocomplete, syntax checker, dark theme, and other editor settings, press `Ctrl + ,` (`Cmd + ,` on macOS) while the editor has focus. Press `Ctrl + Space` to trigger autocomplete when live autocompletion is off.

The autocompleter caches table and database metadata from the backend. If a table was created outside of Hue and does not show up, click the refresh icon in the left assist panel to clear the cache. Hue also clears the cache regularly.

### Sharing

You can share any query with other users and groups. See [Sharing](/user/concept/#sharing).


### Assist

The assist panel shows primary keys, foreign keys, partition keys, nested types, and views for your tables. These examples use transactional tables, which support `INSERT`, `DELETE`, and `UPDATE` statements. They show how the [assist panels](/user/concept/) and [autocomplete](#autocomplete) help you write them.


![Assist All Keys](https://cdn.gethue.com/uploads/2019/11/sql_column_pk.png)


#### Primary keys

Primary keys show with a lock icon:

![Assist Primary Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_pks.png)

Here is an example of SQL for using them:

```sql
CREATE TABLE customer (
    first_name string,
    last_name string,
    website string,
    PRIMARY KEY (first_name, last_name) DISABLE NOVALIDATE
);
```

[Apache Kudu](https://kudu.apache.org/) is supported as well:

```sql
CREATE TABLE students (
  id BIGINT,
  name STRING,
  PRIMARY KEY(id)
)
PARTITION BY HASH PARTITIONS 16
STORED AS KUDU
TBLPROPERTIES ('kudu.num_tablet_replicas' = '1')
;
```

#### Foreign keys

A foreign key column points to a column in another table. In this example, the head of a business unit must exist in the `person` table:

![Assist Foreign Keys](https://cdn.gethue.com/uploads/2020/03/assist_foreign_keys_icons.png)


```sql
CREATE TABLE person (
  id INT NOT NULL,
  name STRING NOT NULL,
  age INT,
  creator STRING DEFAULT CURRENT_USER(),
  created_date DATE DEFAULT CURRENT_DATE(),

  PRIMARY KEY (id) DISABLE NOVALIDATE
);

CREATE TABLE business_unit (
  id INT NOT NULL,
  head INT NOT NULL,
  creator STRING DEFAULT CURRENT_USER(),
  created_date DATE DEFAULT CURRENT_DATE(),

  PRIMARY KEY (id) DISABLE NOVALIDATE,
  CONSTRAINT fk FOREIGN KEY (head) REFERENCES person(id) DISABLE NOVALIDATE
);
```

#### Partition keys

Partitioning of the data is a key concept for optimizing the querying. Partition columns are shown with a key icon:

![Assist Column Partition Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_keys.png)

Here is an example of SQL for using them:

```sql
CREATE TABLE web_logs (
    _version_ BIGINT,
    app STRING,
    bytes SMALLINT,
    city STRING,
    client_ip STRING,
    code TINYINT,
    country_code STRING,
    country_code3 STRING,
    country_name STRING,
    device_family STRING,
    extension STRING,
    latitude FLOAT,
    longitude FLOAT,
    `METHOD` STRING,
    os_family STRING,
    os_major STRING,
    protocol STRING,
    record STRING,
    referer STRING,
    region_code BIGINT, request STRING,
    subapp STRING,
    TIME STRING,
    url STRING,
    user_agent STRING,
    user_agent_family STRING,
    user_agent_major STRING,
    id STRING
)
PARTITIONED BY ( `date` STRING);

INSERT INTO web_logs
PARTITION (`date`='2019-11-14') VALUES
(1480895575515725824,'metastore',1041,'Singapore','128.199.234.236',127,'SG','SGP','Singapore','Other',NULL,1.2930999994277954,103.85579681396484,'GET','Other',NULL,'HTTP/1.1',NULL,'-',0,'GET /metastore/table/default/sample_07 HTTP/1.1','table','2014-05-04T06:35:49Z','/metastore/table/default/sample_07','Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)','Other',NULL,'8836e6ce-9a21-449f-a372-9e57641389b3')
```

#### Nested types

Complex (nested) types store related data together. Expand the column tree in the assist panel to see their fields:

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_nested_types.png)

Here is an example of SQL for using them:

```sql
CREATE TABLE subscribers (
  id INT,
  name STRING,
  email_preferences STRUCT<email_format:STRING,frequency:STRING,categories:STRUCT<promos:BOOLEAN,surveys:BOOLEAN>>,
  addresses MAP<STRING,STRUCT<street_1:STRING,street_2:STRING,city:STRING,state:STRING,zip_code:STRING>>,
  orders ARRAY<STRUCT<order_id:STRING,order_date:STRING,items:ARRAY<STRUCT<product_id:INT,sku:STRING,name:STRING,price:DOUBLE,qty:INT>>>>
)
STORED AS PARQUET
```

#### Views

Views are shown with an eye icon so that you can tell them apart from tables:

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_assist_view_icon.png)

Here is an example of SQL for using them:

```sql
CREATE VIEW web_logs_november AS
SELECT * FROM web_logs
WHERE `date` BETWEEN '2019-11-01' AND '2019-12-01'
```


#### Transactional operations

Transactional tables support these statements to change data.

##### Inserts

Add rows to a table:

```sql
INSERT INTO TABLE customer
VALUES
  ('Elli', 'SQL', 'gethue.com'),
  ('John', 'SELECT', 'docs.gethue.com')
;
```

##### Deletes

Deletion of rows of data:

```sql
DELETE FROM customer
WHERE first_name = 'John';
```

##### Updates

Update column values in selected rows:

```sql
UPDATE customer
SET website = 'helm.gethue.com'
WHERE first_name = 'Elli';
```

#### Language reference

The language reference is in the right assist panel. Click the active icon on the left of the panel to minimize it.

The filter at the top filters topic titles only. This example finds the documentation about joins in `SELECT` statements:

![Language Reference Panel](https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_joins.gif)

To open the reference for the current statement type, right-click the first word of the statement. The reference appears in a popover:

![Language Reference context](https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png)

### Variables

Use variables to set query parameters at run time. They are ideal for saving reports that you share or run repeatedly.

**Single value**

```sql
select * from web_logs where country_code = "${country_code}"
```

![Single valued variable](https://cdn.gethue.com/uploads/2017/10/var_defaults.png)

**Default value**

```sql
select * from web_logs where country_code = "${country_code=US}"
```

**Multiple values**

```sql
select * from web_logs where country_code = "${country_code=CA, FR, US}"
```

**Custom display text for multiple values**

```sql
select * from web_logs where country_code = "${country_code=CA(Canada), FR(France), US(United States)}"
```

![Multi valued variables](https://cdn.gethue.com/uploads/2018/04/variables_multi.png)

**Non-text values (omit the quotes)**

```sql
select * from boolean_table where boolean_column = ${boolean_column}
```

### Charting

Click the **Chart** icon on the results to plot them. Available chart types:

* Bar chart
* Timeline chart
* Pie chart
* Scatter plot
* Marker map
* Gradient map

![Charts](https://cdn.gethue.com/uploads/2019/04/editor_charting.png)

### Query troubleshooting

#### Before running a query

**Popular values**

> **Note**: Popular values and risk alerts need an optimizer service. The optimizer is off by default (`mode=off` in `[optimizer]`). Ask your administrator whether it is enabled.

When an optimizer is enabled, the autocompleter suggests popular tables, columns, filters, joins, `GROUP BY`, and `ORDER BY` clauses. A **Popular** tab appears in the autocomplete dropdown when suggestions are available.

This helps you join unfamiliar datasets and find the most useful columns in tables with hundreds of columns.

![Popular joins suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png)
![Popular columns suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_popular_filter_agg.png)


**Risk alerts**

While you type, Hue checks the query in the background for risks that could affect performance. If it finds a risk, an exclamation mark appears above the editor. Suggestions to improve the query appear in the lower part of the right assist panel.

![Query Risk alerts](https://cdn.gethue.com/uploads/2017/07/hue_4_risk_6.gif)

#### While the query runs

The [Query Browser](/user/browsing/#sql-queries) shows the query plan and its bottlenecks. When detected, "Health" risks are listed with suggestions to fix them.

![Pretty Query Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-11.40.24-AM.png)

#### Tutorial

If a query is slow, the Impala query profile helps you find out why. This scenario walks through the profile:

**Execution Timeline**

Run a few queries:

```sql
SELECT *
FROM
  transactions1g s07 left JOIN transactions1g s08
ON ( s07.field_1 = s08.field_1) limit 100
```

transactions1g is a 1GB table and the self join with no predicates will force a network transfer of the whole table.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.08.01-PM.png)

Looking at the profile, you can see a number on the top right of each node that represent its IO and CPU time. There’s also a timeline that gives an estimated representation of when that node was processed during execution. The dark blue color is the CPU time, while the lighter blue is the network or disk IO time. In this example, we can see that the hash join ran for 2.5s. The exchange node, which does the network transfer between 2 hosts, was the most expensive node at 7.2s.

**Detail pane**

The detail pane on the right is closed by default. Click its header to open or close it. It lists all nodes sorted by execution time, which helps you navigate large execution graphs. Click a node in the list to jump to it.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.12.38-PM.png)

**Events**

Pressing on the exchange node, we find the execution timeline with a bit more detail.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.13.40-PM.png)

We see that the IO was the most significant portion of the exchange.

**Statistics by host**

The detail pane also contains detailed statistics aggregated per host per node such as memory consumption and network transfer speed.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-06-at-4.16.11-PM.png)

**Risks**

For each node, the detail pane has a **Risks** section with hints to improve the performance of the operator. It is disabled by default. Your administrator can enable it in the Hue ini file:

```ini
[notebook]
enable_query_analysis=true
```

**Codegen**

These queries show some of the risks that Hue can identify.

```sql
SELECT s07.description, s07.salary, s08.salary,
  s08.salary - s07.salary
FROM
  sample_07 s07 left outer JOIN sample_08 s08
ON ( s07.code = s08.code)
where s07.salary > 100000
```

sample_07 & sample_08 are small sample tables that come with Hue.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-9.35.23-AM.png)

Looking at the graph, the timelines are mostly empty. If we open one of the nodes we see that all the time is taken by “CodeGen”.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-9.40.50-AM.png)

Impala compiles SQL requests to native code to execute each node in the graph. On queries with large table this gives a large performance boost. On smaller tables, we can see that CodeGen is the main contributor to execution time. Normally, Impala disables CodeGen with tables of small sizes, but Impala doesn’t know it’s a small table as is pointed out in the risks section by the statement “Statistics missing”. Two solutions are available here:

Adding the missing statistics. One way to do this is to execute the following command:

```sql
compute stats sample_07;
compute stats sample_08;
```

This is usually the right thing to do, but on larger tables it can be quite expensive.

Disable codegen for the query via:

```sql
set DISABLE_CODEGEN=true
```

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-9.52.37-AM.png)

After rerunning the query, we see that CodeGen is now gone.

**Join order**

If we open the join node, there’s a warning for wrong join order.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-4.50.54-PM.png)

Impala prefers having the table with the larger size on the right hand side of the graph, but in this case the reverse is true. Normally, Impala would optimize this automatically, but we saw that the statistics were missing for the tables being joined. There a few ways we could fix this:

* Add the missing statistics as described earlier.
* Rewrite the query to change the join order:

```sql
SELECT s07.description, s07.salary, s08.salary,
  s08.salary - s07.salary
FROM
  sample_08 s08 left outer JOIN sample_07 s07
ON ( s07.code = s08.code)
where s07.salary > 100000
```

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-9.57.14-AM.png)

The warning is gone and the execution time for the join is down.

**Spilling**

Impala will execute all of its operators in memory if enough is available. If the execution does not all fit in memory, Impala will use the available disk to store its data temporarily. To see this in action, we’ll use the same query as before, but we’ll set a memory limit to trigger spilling:

```sql
set MEM_LIMIT=1g;
select *
FROM
  transactions1g s07 left JOIN transactions1g s08
ON ( s07.field_1 = s08.field_1);
```

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-11.40.24-AM.png)

Looking at the join node, we can see that there’s an entry in the risk section about a spilled partition. Typically, the join only has CPU time, but in this case it also has IO time due to the spill.

**Kudu filtering**

Kudu is one of the supported storage backends for Impala. While Impala stand alone can query a variety of file data formats, Impala on Kudu allows fast updates and inserts on your data, and also is a better choice if small files are involved. When using Impala on Kudu, Impala will push down some of the operations to Kudu to reduce the data transfer between the two.

However, Kudu does not support all the operators that Impala support. For example, at the time of writing, Impala support the ‘like’ operator, but Kudu does not. In those cases, all the data that cannot be natively filtered in Kudu is transferred to Impala where it will be filtered. Let’s look at a behavior difference between the two.

```sql
SELECT * FROM transactions1g_kudu s07 left JOIN transactions1g_kudu s08 on s07.field_1 = s08.field_1
where s07.field_5 LIKE '2000-01%';
```

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-5.00.59-PM.png)

When we look at the graph, we see that on the Kudu node we have both IO, which represent the time spent in Kudu, and CPU, which represent the time spent in Impala, for a total of 2.1s. In the risk section, we can also find a warning that Kudu could not evaluate the predicate.

```sql
SELECT * FROM transactions1g_kudu s07 left JOIN transactions1g_kudu s08 on s07.field_1 = s08.field_1
where s07.field_5 <= '2000-01-31' and s07.field_5 >= '2000-01-01';
```

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-4.02.33-PM.png)

When we look a the graph, we see that on the Kudu node now mostly has IO for a total time 727ms.

**Others**

You might also have queries where the nodes have short execution time, but the total duration time is long. Using the same query, we see all the nodes have sub 10ms execution time, but the query execution was 7.9s.

![Impala Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-10.56.07-AM.png)

Looking at the global timeline, we see that the planning phase took 3.8s with most of the time in metadata load. When Impala doesn’t have metadata about a table, which can happen after a user executes:

```sql
invalidate metadata;
```

Impala has to refetch the metadata from the metastore. Furthermore, we see that the second most expensive item at 4.1s is first row fetched. This is the time it took the client, Hue in this case, to fetch the results. While both of these events are not things that a user can change, it’s good to see where the time is spent.

#### After the query runs

An experimental panel can offer risk analysis and recommendations to speed up the query after it ran. It is available only when `enable_query_analysis` is enabled.

### Modes

#### Presentation

Presentation mode turns a list of semicolon-separated queries into an interactive presentation. Click the 'Dashboard' icon, or press `Ctrl + Shift + P` (`Cmd + Shift + P` on macOS), to switch to or from it. Use it for live demos or to run a series of queries in one click.

Your administrator can turn it off with `enable_presentation` in `[notebook]`.

![Editor Presentation Mode](https://cdn.gethue.com/uploads/2020/02/editor_presentation_mode.png)

#### Dark

Dark mode applies to the editor area only.

![Editor Dark Mode](https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png)

To toggle dark mode, press `Ctrl + Alt + T` (`Cmd + Option + T` on macOS) while the editor has focus. You can also change it in the settings menu, which opens with `Ctrl + ,` (`Cmd + ,` on macOS).

## Dashboard

Dashboards let you query indexed data interactively. You build the analysis with drag and drop and clicks, without programming. The Dashboard link appears automatically when the Search app is available, or when the administrator sets `has_sql_enabled=true` in the `[dashboard]` section. It can also be set with `is_enabled` in the same section.

![Search Full](https://cdn.gethue.com/uploads/2015/08/search-full-mode.png)

Widgets are connected to each other, so you can explore a new dataset or monitor data without typing.

![Analytics dimensions](https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dnd.gif)

Apache Solr is the best supported engine. SQL databases are supported when `has_sql_enabled` is set in `[dashboard]` (beta). To add SQL support, see the [dashboard connector](/developer/development/#connectors) section.

These tutorials showcase the capabilities:

* The top search bar offers a [full autocomplete](http://gethue.com/intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/) on all the values of the index
* Seeing [real time data](http://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/)
* Comprehensive demo of [BikeShare data visualization post](http://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/)


### Analytics facets

Drill down the dimensions of the datasets and apply aggregates functions on top of it:

![Analytics dimensions](https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dimensions.gif)

Some facets can be nested:

![Nested Analytics facets](https://cdn.gethue.com/uploads/2015/08/search-nested-facet-1024x304.png)
![Nested Analytics Counts](https://cdn.gethue.com/uploads/2015/08/search-hit-widget.png)


### Autocomplete

The top bar supports faceted and free-text search with autocomplete.

![Search Autocomplete](https://cdn.gethue.com/uploads/2018/01/dashboard_autocomplete.png)

### Marker map
Nearby points are grouped and expand when you zoom in. Select the checkbox to filter the records by the visible map area.

![Marker Map](https://cdn.gethue.com/uploads/2015/08/search-marker-map.png)

### Edit records

Indexed records can be directly edited in the Grid or HTML widgets by admins.

### Links

Links to the original documents can also be inserted. Add to the record a field named ‘link-meta’ that contains some json describing the URL or address of a table or file that can be open in the HBase Browser, Metastore App or File Browser:

Any link

```text
{'type': 'link', 'link': 'gethue.com'}
```

HBase Browser

```text
{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527'}
{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1'}
{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1', 'col': 'c1'}
```

File Browser

```text
{'type': 'hdfs', 'path': '/data/hue/file.txt'}
```

Table Catalog

```text
{'type': 'hive', 'database': 'default', 'table': 'sample_07'}
```

![Data Links](https://cdn.gethue.com/uploads/2015/08/search-link-1024x630.png)

### Saved queries

Current selected facets and filters, query strings can be saved with a name within the dashboard. These are useful for defining “cohorts” or pre-selection of records and quickly reloading them.

![Rolling time](https://cdn.gethue.com/uploads/2015/08/search-query-def-1024x507.png)

### Fixed or rolling window

Use a rolling window filter and automatic refresh every N seconds to follow data that is indexed in real time.

![Fixed time](https://cdn.gethue.com/uploads/2015/08/search-fixed-time.png)

### 'More like this'

Select the fields to use to find similar records, such as similar issues, customers, or people.

![More like this](https://cdn.gethue.com/uploads/2018/01/solr_more_like_this.png)


## Notebook

Use Notebooks to experiment with small programming snippets, in particular Spark, and to run interactive demos. Notebooks are lightweight compared to other notebook systems.

You can add snippets of different dialects (for example PySpark and Hive SQL) to a single page. The Notebook menu is hidden by default (`show_notebooks=false` in `[notebook]`).

![Notebook mode](https://cdn.gethue.com/uploads/2015/10/notebook-october.png)

Every language configured in the Editor is available as a dialect. Each snippet has a code editor with autocomplete, syntax highlighting, and shortcut links to HDFS paths and Hive tables.

![Notebook Screen](https://cdn.gethue.com/uploads/2015/08/notebook.png)

Example of SparkR shell with inline plot

![Notebook r snippet](https://cdn.gethue.com/uploads/2015/08/spark-r-snippet.png)

All the spark-submit, spark-shell, pyspark, sparkR properties of jobs & shells can be added to the sessions of a Notebook. This will for example let you add files, modules and tweak the memory and number of executors.

![Notebook sessions](https://cdn.gethue.com/uploads/2015/08/notebook-sessions.png)

### Spark

Hue relies on [Livy](https://livy.incubator.apache.org/) for the interactive Scala, Python, SparkSQL and R snippets.

Livy is an open source REST interface for interacting with Apache Spark from anywhere. It started in the Hue project and is now the separate Apache Livy project.

Your administrator must [configure](/administrator/configuration/connectors/#apache-spark) the Notebook and its interpreters.

#### Livy

Starting the Livy REST server is detailed on the [get started](http://livy.incubator.apache.org/get-started/) page.

**Executing some Spark**

As the REST server is running, we can communicate with it. We are on the same machine so will use ‘localhost’ as the address of Livy.

Let’s list our open sessions

```bash
curl localhost:8998/sessions

{"from":0,"total":0,"sessions":[]}
```

> **Note**: Append `| python -m json.tool` to a command to format the output, for example:

```bash
curl localhost:8998/sessions/0 | python -m json.tool
```

There is zero session. We create an interactive PySpark session

```bash
curl -X POST --data '{"kind": "pyspark"}' -H "Content-Type: application/json" localhost:8998/sessions

{"id":0,"state":"starting","kind":"pyspark","log":[]}
```

Sessions ids are incrementing numbers starting from 0. We can then reference the session later by its id.

We check the status of the session until its state becomes idle: it means it is ready to be execute snippet of PySpark:

```bash
curl localhost:8998/sessions/0 | python -m json.tool


% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current

                                Dload  Upload   Total   Spent    Left  Speed

100  1185    0  1185    0     0  72712      0 --:--:-- --:--:-- --:--:-- 79000

{

    "id": 5,

    "kind": "pyspark",

    "log": [

      "15/09/03 17:44:14 INFO util.Utils: Successfully started service 'SparkUI' on port 4040.",

      "15/09/03 17:44:14 INFO ui.SparkUI: Started SparkUI at http://172.21.2.198:4040",

      "15/09/03 17:44:14 INFO spark.SparkContext: Added JAR file:/home/romain/projects/hue/apps/spark/java-lib/livy-assembly.jar at http://172.21.2.198:33590/jars/livy-assembly.jar with timestamp 1441327454666",

      "15/09/03 17:44:14 WARN metrics.MetricsSystem: Using default name DAGScheduler for source because spark.app.id is not set.",

      "15/09/03 17:44:14 INFO executor.Executor: Starting executor ID driver on host localhost",

      "15/09/03 17:44:14 INFO util.Utils: Successfully started service 'org.apache.spark.network.netty.NettyBlockTransferService' on port 54584.",

      "15/09/03 17:44:14 INFO netty.NettyBlockTransferService: Server created on 54584",

      "15/09/03 17:44:14 INFO storage.BlockManagerMaster: Trying to register BlockManager",

      "15/09/03 17:44:14 INFO storage.BlockManagerMasterEndpoint: Registering block manager localhost:54584 with 530.3 MB RAM, BlockManagerId(driver, localhost, 54584)",

      "15/09/03 17:44:15 INFO storage.BlockManagerMaster: Registered BlockManager"

    ],

    "state": "idle"

}
```

![Livy Architecture sessions](https://cdn.gethue.com/uploads/2015/09/20150818_scalabythebay.024.png)

**Session properties**

All the properties supported by spark shells like the number of executors, the memory, etc can be changed at session creation. Their format is the same as when typing spark-shell -h

```bash
curl -X POST --data '{"kind": "pyspark", "numExecutors": "3", "executorMemory": "2G"}' -H "Content-Type: application/json" localhost:8998/sessions
{"id":0,"state":"starting","kind":"pyspark","numExecutors":"3","executorMemory":"2G","log":[]}
```

**Executing statements**

In YARN mode, Livy creates a remote Spark Shell in the cluster that can be accessed easily with REST

When the session state is idle, it means it is ready to accept statements! Lets compute 1 + 1

```bash
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 + 1"}'

{"id":0,"state":"running","output":null}
```

We check the result of statement 0 when its state is available

```bash
curl localhost:8998/sessions/0/statements/0

{"id":0,"state":"available","output":{"status":"ok","execution_count":0,"data":{"text/plain":"2"}}}
```

> **Note**: If a statement takes only a few milliseconds, Livy returns the result directly in the response to the `POST` command.

Statements are incrementing and all share the same context, so we can have a sequences

```bash
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"a = 10"}'

{"id":1,"state":"available","output":{"status":"ok","execution_count":1,"data":{"text/plain":""}}}
```

Spanning multiple statements

```bash
curl localhost:8998/sessions/5/statements -X POST -H 'Content-Type: application/json' -d '{"code":"a + 1"}'

{"id":2,"state":"available","output":{"status":"ok","execution_count":2,"data":{"text/plain":"11"}}}
```

Let’s close the session to free up the cluster. Note that Livy will automatically inactive idle sessions after 1 hour (configurable).

```bash
curl localhost:8998/sessions/0 -X DELETE

{"msg":"deleted"}
```

#### Tutorial: sharing RDDs

This section shows how to share Spark RDDs and contexts. Livy offers remote Spark sessions to users. They usually have one each (or one by Notebook):

```bash
# Client 1
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 + 1"}'
# Client 2
curl localhost:8998/sessions/1/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'
# Client 3
curl localhost:8998/sessions/2/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'
```

![Livy shared context](https://cdn.gethue.com/uploads/2015/10/livy_shared_contexts2.png)

##### ...and so sharing RDDs

If the users were pointing to the same session, they would interact with the same Spark context. This context would itself manages several RDDs. Users simply need to use the same session id, e.g. 0, and issue commands there:

```bash
# Client 1
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 + 1"}'

# Client 2
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'

# Client 3
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"..."}'
```

![Livy multi rdds](https://cdn.gethue.com/uploads/2015/10/livy_multi_rdds2.png)

##### ...Accessing them from anywhere

Now we can even make it more sophisticated while keeping it simple. Imagine we want to simulate a shared in memory key/value store. One user can start a named RDD on a remote Livy PySpark session and anybody could access it.

![Livy anywhere rdds](https://cdn.gethue.com/uploads/2015/10/livy_shared_rdds_anywhere2.png)

To make it prettier, we can wrap it in a few lines of Python and call it ShareableRdd. Then users can directly connect to the session and set or retrieve values.

```python
class ShareableRdd():

  def __init__(self):
    self.data = sc.parallelize([])

  def get(self, key):
    return self.data.filter(lambda row: row[0] == key).take(1)

  def set(self, key, value):
    new_key = sc.parallelize([[key, value]])
    self.data = self.data.union(new_key)
```

set() adds a value to the shared RDD, while get() retrieves it.

```python
srdd = ShareableRdd()

srdd.set('ak', 'Alaska')
srdd.set('ca', 'California')

srdd.get('ak')
```

If using the REST Api directly someone can access it with just these commands:

```bash
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"srdd.get(\"ak\")"}'
{"id":3,"state":"running","output":null}

curl localhost:8998/sessions/0/statements/3
{"id":3,"state":"available","output":{"status":"ok","execution_count":3,"data":{"text/plain":"[['ak', 'Alaska']]"}}}
```

We can even get prettier data back, directly in json format by adding the %json magic keyword:

```bash
curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d  '{"code":"data = srdd.get(\"ak\")\n%json data"}'
{"id":4,"state":"running","output":null}

curl localhost:8998/sessions/0/statements/4
{"id":4,"state":"available","output":{"status":"ok","execution_count":2,"data":{"application/json":[["ak","Alaska"]]}}}
```

##### Even from any languages

As Livy is providing a simple REST Api, we can quickly implement a little wrapper around it to offer the shared RDD functionality in any languages. Let’s do it with regular Python:

```bash
pip install requests
python
```

Then in the Python shell just declare the wrapper:

```python
import requests
import json

class SharedRdd():
  """
  Perform REST calls to a remote PySpark shell containing a Shared named RDD.
  """
  def __init__(self, session_url, name):
    self.session_url = session_url
    self.name = name

  def get(self, key):
    return self._curl('%(rdd)s.get("%(key)s")' % {'rdd': self.name, 'key': key})

  def set(self, key, value):
    return self._curl('%(rdd)s.set("%(key)s", "%(value)s")' % {'rdd': self.name, 'key': key, 'value': value})

  def _curl(self, code):
    statements_url = self.session_url + '/statements'
    data = {'code': code}
    r = requests.post(statements_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    resp = r.json()
    statement_id = str(resp['id'])
    while resp['state'] == 'running':
      r = requests.get(statements_url + '/' + statement_id)
      resp = r.json()
    return r.json()['data']
```

Instantiate it and make it point to a live session that contains a ShareableRdd:

```python
states = SharedRdd('http://localhost:8998/sessions/0', 'states')
```

And just interact with the RDD transparently:

```python
states.get('ak')
states.set('hi', 'Hawaii')
```

### Others

These snippet types are available only if your administrator configured them as Oozie-based interpreters.

**Apache Pig**: Type [Apache Pig](https://pig.apache.org/) Latin statements to load and merge data for ETL or analytics.

**Apache Sqoop**: Run an [SQL import](/user/browsing/#relational-databases) from a relational database with an [Apache Sqoop](https://sqoop.apache.org/) command.
