---
title: The Hue SQL Query Experience for your Data Warehouse
author: Romain
type: post
date: 2020-02-10T00:00:00+00:00
url: /blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
#  - Version 4.7

---

[Hue](http://gethue.com/) has just [blown its 10th candle](https://gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/)! In this follow-up #2 of the series, let's describe what a SQL Cloud Editor is.

The top two capabilities of a SQL Cloud Editor are:

* `Data Querying Experience`: offer a SQL querying assistant that helps users self service their own query need while educating them on the data and syntax know-how.
* `Cloud Native`: scale by providing as much as “no-ops” as possible by automating the operation of the service. Easy to run and monitor, auto scale in capacity, automatic rolling upgrades...

This post is about detailing the Querying Experience from the point of a end user. #3 post of the series will focus on the Cloud Experience.


## Focus on SQL Data Warehousing

Many Data Platforms are typically configured in a [Data Hub](https://www.cloudera.com/products/data-hub.html) model. This means a centralized cluster with all the data, computes and satellite services like workflow scheduling, indexing, streams... altogether.

This is a lot of components to access via a full blown Hue:

!["Full Hue"](https://cdn.gethue.com/uploads/2019/12/hue4.6.png)

Hue's apps range from [Dashboards](https://docs.gethue.com/user/querying/#dashboard) for light calculation or charting of indexed or SQL data, browser for the Cloud storages of AWS, Azure, Google Cloud, scheduling workflows of jobs, a dataset importer wizard...

However in the case of SQL Data Warehousing, we want to restrict Hue to mostly the Editor and Data Catalog:

!["Data Warehousing Hue"](https://cdn.gethue.com/uploads/2020/02/hue_dwx.png)

That way, the SQL Compute Engines and Data Storages can be easily queried or browsed.

## SQL Querying Experience

`Querying Data is hard`. It is not simple to have the knowledge of the existing datasets and how to query them. Traditional SQL Editors targeted advanced and full time users like SQL Developers of Data Analysts and provided interfaces filled-up with options.

Now the modern trend is to provide the simplest interface to a wider range of end users and basically hide under the cover a maximum of the complexity of the big data ecosystem. Typically, non full time Data Analysts don't even know how to get started, so a smart editor should crowdsource the data descriptions as well as how to query it.

`Ad-hoc queries` are also a major use case, where various professions in the organization just want an answer to a basic question. e.g.

* How many clicks did we get on the blog post this week vs last week?
* What are the sales in the Japan region for product X?
* What are the top cases of our customers in Salesforce for my team?...

and it is much faster if they can answer it by themselves rather than asking for a new dashboard or SQL query to the Analytics team. What prevents them from achieving self service is often how to:

* Find the data
* Find the query

## Finding the Data

Among 1000s of databases containing 10s of 1000s of tables with cryptic names, it is not an easy task. Before typing any query to get insights, users need to find and explore the correct datasets.

Data Browsers & Catalogs are here to help tackle this and Hue has built in integration to these services. [Apache Atlas](https://atlas.apache.org/) is powering the Search and Commenting of tables, columns. New Catalogs can be integrated via [connectors](https://docs.gethue.com/administrator/configuration/connectors/).

### Top search

Have you ever struggled to remember table names related to your project? Does it take much too long to find those columns or views? Hue lets you easily search for any table, view, or column across all databases in the cluster. With the ability to search across tens of thousands of tables, you're able to quickly find the tables that are relevant for your needs for faster data discovery.

The search bar is always accessible on the top of the screen, and it offers a document search and metadata search too if Hue is configured to access a metadata server.

![Data Catalog top search](https://cdn.gethue.com/uploads/2018/04/blog_top_search_.png)

<p class="text-center">
  Searching all the available queries or data in the cluster
</p>

![Data Catalog tags](https://cdn.gethue.com/uploads/2018/04/blog_tag_listing.png)

<p class="text-center">
  Listing the possible tags to filter on.
</p>

#### Search

By default, only tables and views are returned. To search for columns, partitions, databases use the ‘type:' filter.

Example of search syntax:

Apache Atlas

* sample → Any table or Hue document with prefix ‘sample’ will be returned
* type:database → List all databases on this cluster
* type:table → List all tables on this cluster
* type:field name→ List tables with field(column): ‘name’
* ‘tag:classification_testdb5‘ or ‘classification:classification_testdb5’→ List entities with classification ‘classification_testdb5’
* owner:admin→ List all tables owned by ‘admin’ user

Cloudera Navigator

* table:customer → Find the customer table
* table:tax* tags:finance → List all the tables starting with tax and tagged with ‘finance'
* owner:admin type:field usage → List all the fields created by the admin user that matches the usage string
* parentPath:"/default/web_logs" type:FIELD  originalName:b* → List all the columns starting with `b` of the table `web_logs` in the database `default`.

<img alt="Data Catalog Searc" src="https://cdn.gethue.com/uploads/2019/06/SearchWithType_field_name.png" width="800px">

#### Additional Metadata

In addition to editing the tags of any SQL objects like tables, views, columns… which has been available since version one, table descriptions can now also be edited. This allows a self service documentation of the metadata by the end users.

![Data Catalog Metadata](https://cdn.gethue.com/uploads/2018/04/blog_metadata.png)

### Left assist

Data where you need it when you need it.

Find your queries, tables and files in the left assist panel without leaving the page. Right-clicking items will show a list of actions, you can also drag-and-drop a file to get the path in your editor and more.

![Left assist Navigation and drop](https://cdn.gethue.com/uploads/2018/05/HDFS_Context_Change_Path_2.gif)

### Sample popup

This popup offers a quick way to see samples of the data and other statistics on databases, tables, and columns. You can open the popup from the SQL Assist or with a right-click on any SQL object (table, column, function…). In this release, it also opens faster and caches the data.

![Sample popup Navigation](https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif)

#### Tagging

In addition, you can also now tag objects with names to better categorize them and group them to different projects. These tags are searchable, expediting the exploration process through easier, more intuitive discovery.

![Data Catalog](https://cdn.gethue.com/uploads/2016/04/tags.png)

### Browsing Data

The File Browser application lets you interact with these File Systems: HDFS, AWS S3, Azure ADLS v1 and v2 (ABFS). Google Cloud Storage is currently a work in progress [HUE-8978](https://issues.cloudera.org/browse/HUE-8978).

View all accessible folders within the account by clicking on the storage root. From here, create, rename, move, copy, or delete existing directories and files. Additionally, directly upload files to the storage.

![Browse files](https://cdn.gethue.com/uploads/2016/08/image2.png)


### Importing Data

The goal of the importer is to allow ad-hoc queries on data not yet in the clusters and simplifies self-service analytics.

If you want to import your own data or reference existing data not in a table, open the importer from the left menu or from the little `+` in the left assist. The import wizard can create external Hive tables directly from files in the storage.

![Create tables from external files](https://cdn.gethue.com/uploads/2017/11/image4-1.png)

## Querying the Data

Now that the tables are found, it is time to query them to answer our questions or discover insights.

### Running Queries

SQL query execution is the primary use case of the Editor. See the list of most common [Databases and Datawarehouses](https://docs.gethue.com/administrator/configuration/connectors/).

* The currently selected statement has a **left blue** border. To execute a portion of a query, highlight one or more query statements.
* **Execute**. Then the Query Results window appears. Perform refining operations like scroll to column, column names and types filtering, plotting, row locking/expanding, cell content search.
* If there are **multiple statements** in the query (separated by semicolons), click Next in the multi-statement query pane to execute the remaining statements.

When you have multiple statements it is enough to put the cursor in the statement you want to execute, the active statement is indicated with a blue gutter marking.

![Editor](https://cdn.gethue.com/uploads/2020/02/hue4.6-editor.png)

**Note**: Use `CTRL/Cmd + ENTER` to execute queries.

**Note**: On top of the logs panel, there is a link to open the query profile in the [Query Browser](https://docs.gethue.com/user/browsing/#sql-queries).


### Autocomplete

This is where Hue shines the best, Hue comes with one of the best SQL autocomplete on the planet. The autocompleter knows all the ins and outs of the Hive and Impala SQL dialects and will suggest keywords, functions, columns, tables, databases, etc. based on the structure of the statement and the position of the cursor.

![Autocomplete and context assist](https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif)

**Smart column suggestions**

If multiple tables appear in the FROM clause, including derived and joined tables, it will merge the columns from all the tables and add the proper prefixes where needed. It also knows about your aliases, lateral views and complex types and will include those. It will now automatically backtick any reserved words or exotic column names where needed to prevent any mistakes.

**Smart keyword completion**

The autocompleter suggests keywords based on where the cursor is positioned in the statement. Where possible it will even suggest more than one word at a time, like in the case of IF NOT EXISTS, no one likes to type too much right?

**Functions**

The improved autocompleter will now suggest functions, for each function suggestion an additional panel is added in the autocomplete dropdown showing the documentation and the signature of the function. The autocompleter knows about the expected types for the arguments and will only suggest the columns or functions that match the argument at the cursor position in the argument list.

<p class="text-center">
 <img src="https://cdn.gethue.com/uploads/2017/07/hue_4_functions.png" alt="SQL functions reference" height="500"/>
</p>

**Sub-queries, correlated or not**

When editing subqueries it will only make suggestions within the scope of the subquery. For correlated subqueries the outside tables are also taken into account.

**Context popup**

Right click on any fragment of the queries (e.g. a table name) to get all its metadata information. This is a handy shortcut to get more description or check what types of values are contained in the table or columns.

It’s quite handy to be able to look at column samples while writing a query to see what type of values you can expect. Hue now has the ability to perform some operations on the sample data, you can now view distinct values as well as min and max values.

![Sample column popup](https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif)

**Syntax checker**

A little red underline will display the incorrect syntax so that the query can be fixed before submitting. A right click offers suggestions.

![Syntax checker highlight](https://cdn.gethue.com/uploads/2018/01/syntax_checkerhigh.png)

<p class="text-center">
  Syntax checker highlight
</p>

![Syntax checker](https://cdn.gethue.com/uploads/2018/01/checker_help.png)

<p class="text-center">
  Syntax checker correction suggestion
</p>

### Table Assist

The Datawarehouse ecosystem is getting more complete with the introduction of transactions. In practice, this means your tables can now support `Primary Keys`, `INSERTs`, `DELETEs` and `UPDATEs` as well as `Partition Keys`.

![Assist All Keys](https://cdn.gethue.com/uploads/2019/11/sql_column_pk.png)

Primary Keys shows up like Partition Keys with the lock icon:

![Assist Primary Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_pks.png)

Partitioning of the data is a key concept for optimizing the querying. Those special columns are also shown with a key icon:

![Assist Column Partition Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_keys.png)

Complex or Nested Types are handy for storing associated data close together. The assist lets you expand the tree of columns:

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_nested_types.png)

It can be sometimes confusing to not recognize that a table is instead a view. Views are shown with this little eye icon:

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_assist_view_icon.png)

### Language reference

You can find the Language Reference in the right assist panel. This assistant content depends on the selected SQL Engines and queries. It will display the current tables, the language and UDFs documentation.

The filter input on top will only filter on the topic titles in this initial version. Below is an example on how to find documentation about joins in select statements.

![Language Reference Panel](https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_joins.gif)

While editing a statement there’s a quicker way to find the language reference for the current statement type, just right-click the first word and the reference appears in a popover below:

<p class="text-center">
  <img src="https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png" alt="Language Reference context" height="500"/>
</p>

### Variables

Variables are used to easily configure parameters in a query. They are ideal for saving reports that can be shared or executed repetitively:

**Single Valued**

    SELECT * FROM web_logs WHERE country_code = "${country_code}"

![Single valued variable](https://cdn.gethue.com/uploads/2017/10/var_defaults.png)

**The variable can have a default value**

    SELECT * FROM web_logs WHERE country_code = "${country_code=US}"

**Multi Valued**

    SELECT * FROM web_logs WHERE country_code = "${country_code=CA, FR, US}"

**In addition, the displayed text for multi valued variables can be changed**

    SELECT * FROM web_logs WHERE country_code = "${country_code=CA(Canada), FR(France), US(United States)}"

![Multi valued variables](https://cdn.gethue.com/uploads/2018/04/variables_multi.png)

**For values that are not textual, omit the quotes.**

    SELECT * FROM boolean_table WHERE boolean_column = ${boolean_column}

### Charting

These visualizations are convenient for plotting chronological data or when subsets of rows have the same attribute: they will be stacked together.

* Pie
* Bar/Line with pivot
* Timeline
* Scattered plot
* Maps (Marker and Gradient)

![Charts](https://cdn.gethue.com/uploads/2019/04/editor_charting.png)

### Modes

#### Presentation

Turns a list of semi-colon separated queries into an interactive presentation by clicking on the 'Dashboard' icon. It is great for doing presentations with a scenario and live results to prove a point or executing reports containing a suite of sequential queries in one click.

![Editor Presentation Mode](https://cdn.gethue.com/uploads/2020/02/editor_presentation_mode.png)

#### Dark

Initially this mode is limited to the actual editor area before extending it to cover all of Hue.

![Editor Dark Mode](https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png)

To toggle the dark mode you can either press `Ctrl-Alt-T` or `Command-Option-T` on Mac while the editor has focus. Alternatively you can control this through the settings menu which is shown by pressing `Ctrl-`, or `Command-`, on Mac.


### Query troubleshooting

#### Pre-query execution

**Popular values**

The autocompleter will suggest popular tables, columns, filters, joins, group by, order by etc. based on metadata from Navigator Optimizer. A new “Popular” tab has been added to the autocomplete result dropdown which will be shown when there are popular suggestions available.

This is particularly useful for doing joins on unknown datasets or getting the most interesting columns of tables with hundreds of them.

![Popular joins suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png)

<p class="text-center">
  Popular joins suggestion
</p>

![Popular columns suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_popular_filter_agg.png)

<p class="text-center">
  Popular columns and filters suggestion
</p>

**Risk alerts**

While editing, Hue will run your queries through Navigator Optimizer in the background to identify potential risks that could affect the performance of your query. If a risk is identified an exclamation mark is shown above the query editor and suggestions on how to improve it is displayed in the lower part of the right assistant panel.

![Query Risk alerts](https://cdn.gethue.com/uploads/2017/07/hue_4_risk_6.gif)

#### During execution

The [Query Browser](https://docs.gethue.com/user/browsing/#sql-queries) details the plan of the query and the bottle necks. When detected, "Health" risks are listed with suggestions on how to fix them.

![Pretty Query Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-11.40.24-AM.png)

You can find in the documentation a [detailed troubleshooting](https://docs.gethue.com/user/querying/#query-troubleshooting) scenario.

### Sharing

Similarly to Google Documents, any query can be shared with other users or groups, with read only or edit permissions. Sharing happens on the main page or via the top right menu of the selected application. Shared documents will show-up with a little blue icon.

![Sharing](https://cdn.gethue.com/uploads/2019/04/editor_sharing.png)

**Note**: Public links and Gist sharing should be released in the next Hue 4.7!


## Next (SQL) steps

Hue 5 and an enhanced SQL Cloud Editor are coming in 2020 for an even more modern Data Query Experience. A Data Warehouse dedicated Hue has also just been released in the [Cloudera Cloud Data Warehouse](https://www.cloudera.com/products/data-warehouse.html).

Hue is also getting more pluggable with many [connectors](https://docs.gethue.com/administrator/configuration/connectors/) to the most popular Databases and their dedicated [SQL autocomplete](https://docs.gethue.com/developer/development/#sql-parsers).

We will deep dive in greater details on the Cloud capabilities of the SQL Cloud Editor in part three of this series of the 10 years of evolution of Hue. Until then, feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!


Romain, from the Hue Team
