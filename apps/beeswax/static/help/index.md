Beeswax for Hive
================
<a target="Beeswax"><img src="/beeswax/static/art/icon_huge.png" class="help-logo"/></a>
Beeswax is a UI for querying [Hive](http://wiki.apache.org/hadoop/Hive), a 
data warehousing system built on top of Hadoop.  

Navigate to different views in the beeswax UI by using the toolbar at the top of the application window.

Running Queries
---------------
The "Query" view lets you enter queries in Hive's Query Language, 
[HQL](http://wiki.apache.org/hadoop/Hive/LanguageManual), which
is quite similar to SQL.  Queries can be named and saved.

When you submit a query, a server ("the Beeswax Server") uses
Hive to run the queries.  You can either wait for the query
to complete, or come back later to find the queries
in the "History" view.
<img src="/beeswax/static/help/images/new_query.gif"/>

Creating New Tables
-------------------
Though you can create tables by issuing the appropriate
HQL DDL query, it is easier to create a table using 
the Table Creation Wizard.  You will be asked to name
the table, specify storage parameters (essentially,
how columns and rows are formatted), and specify
the regular and partition columns.

Browsing Tables
---------------
Use the "Tables" tab to see the available tables, preview
their data, and examine their metadata.  You can load
more data into the tables from here as well.  
<img src="/beeswax/static/help/images/table_info.gif"/>

History
-------
The History tab presents queries that have been run
previously.  Results for these queries are often
available for some time, and then are automatically
expired.  
<img src="/beeswax/static/help/images/query_history.gif"/>

Saved Queries, My Queries
-------------------------
Queries can be saved, and then browsed using
these views.  If a query is not yours to edit,
you may "clone" it to edit your own version.  
<img src="/beeswax/static/help/images/saved_queries.gif"/>


Results View
------------
When viewing the results for a query,
notice the "Log" tab to see logs presented
by Hive.  These will help you to debug 
your query.  The results view will also have
links to any MR jobs started by the query.  
<img src="/beeswax/static/help/images/query_results.gif"/>

Hive Version
------------
Underneath the covers, Beeswax is using a very slightly
modified version of Hive 0.5.0.
