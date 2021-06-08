---
title: "SQL Querying Improvements: Phoenix, Flink, SparkSql, ERD Table..."
author: Hue Team
type: post
date: 2020-09-15T00:00:00+00:00
url: /blog/sql-querying-improvements-phoenix-flink-sparksql-erd-table/
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
  - Phoenix
  - Flink SQL
  - ksqlDB
  - Spark SQL
#  - Version 4.8

---
Hi Data Crunchers,

Are you looking at executing your SQL queries more easily? Here is a series of various querying improvements coming in the next release of Hue!

## New Databases

Hue is getting a more polished experience with [Apache Phoenix](https://phoenix.apache.org/), [Apacke Flink](https://flink.apache.org/) SQL and [Apache Spark](https://spark.apache.org/) SQL (via [Apache Livy](https://livy.apache.org/)).

{{< youtube fKHD-fOdDY0 >}}

### Apache Phoenix

Apache Phoenix makes it easy to query the [Apache HBase](https://hbase.apache.org/) database via SQL. Now the [integration](/sql-querying-apache-hbase-with-apache-phoenix/) is fully working out of the box and several corner cases (e.g. handle the default Phoenix database, list tables and column in the left assist, impersonation support...) have been fixed.

### Apache Flink SQL

Apache Flink support for [SQL querying](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sql/) data streams is maturing and also getting a first integration with the Editor.

**Note** Support for [KsqlDB](https://docs.gethue.com/administrator/configuration/connectors/#ksqldb) is also making progress as they both share similar functionalities: live queries and result grid

### Apache SparkSql

SparkSql is very popular and getting a [round of improvements](/blog/quick-task-sql-editor-for-apache-spark-sql-with-livy/) when executing SQL queries via Apache Livy. Note that the traditional SqlAlchemy [connectors](https://docs.gethue.com/administrator/configuration/connectors/#apache-spark-sql) or HiveServer Thrift are working too.

## UDF / Functions

**Dynamic listing**

Not all the functions are listed in the editor (some are registered at the session/company level, some have been created after a Hue release, some are missing and [can be added](https://docs.gethue.com/developer/development/#sql-parsers) etc...).

Now the editor will ask the Database for its full list of functions and add the missing ones in the `General` section.

![UDF Assist](https://cdn.gethue.com/uploads/2020/09/right-assist-udf.png)
![UDF Dynamic Assist](https://cdn.gethue.com/uploads/2020/09/assist-udf-dynamic.png)

**Arguments**

Argument positioning is now understood and the constant arguments of popular functions are also available. For example the formats for date conversion in position two will now be showcased to the user.

![UDF argument positions](https://cdn.gethue.com/uploads/2020/09/udf-trunc-args.png)

## Autocomplete

**Build your own parser**

The parser is being extracted in smaller reusable pieces [structure.json](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/parse/jison/sql/generic/structure.json) with first goal of supporting [Apache Calcite](https://calcite.apache.org/) SQL subsets. The [Parser SDK](https://docs.gethue.com/developer/development/#sql-parsers#structure) has more more detailed information.

e.g. `structure.json` is composed of generic and specific grammar pieces that are reusable across SQL parsers.

structure.json

    [...],
    "../generic/select/select.jison",
    "../generic/select/select_conditions.jison",
    "select/select_stream.jison",
    "../generic/select/union_clause.jison",
    "../generic/select/where_clause.jison",
    [...]

select_stream.jison

    SelectStatement
    : 'SELECT' 'STREAM' OptionalAllOrDistinct SelectList
    ;

    SelectStatement_EDIT
    : 'SELECT' 'STREAM' OptionalAllOrDistinct 'CURSOR'
    {
      if (!$3) {
        parser.suggestKeywords(['ALL', 'DISTINCT']);
      }
    }
    ;

It is moving away from the non scalable stategy of building big independent parsers to building parsers with shared grammar operations:

![Parser Evolution v2 Beta](https://cdn.gethue.com/uploads/2020/09/parser_evolution.png)

**Scheduled Hive Queries**

Hive 4 natively supports [scheduling queries](https://cwiki.apache.org/confluence/display/Hive/Scheduled+Queries) via SQL statements. The autocomplete now supports the SQL syntax as well as the right assist documentation.

    * create
    create scheduled query Q1 executed as joe scheduled '1 1 * * *' as update t set a=1;
    * change schedule
    alter scheduled query Q1 cron '2 2 * * *'
    * change query
    alter scheduled query Q1 defined as select 2
    * disable
    alter scheduled query Q1 set disabled
    * enable
    alter scheduled query Q1 set enabled
    * list status
    select * from sysdb.scheduled_queries;
    * drop
    drop scheduled query Q1

Note that a fancier mini UI will come with [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) so that monitoring or scheduling queries is only two clicks away (cf. the right Assist Panel).

![Integrated Scheduling](https://cdn.gethue.com/uploads/2020/09/scheduled_queries.png)

**Limit N autocomplete**

Now when autocompleting and adding a 'LIMIT' to your query, actual sizes will also be proposed.

![UDF argument positions](https://cdn.gethue.com/uploads/2020/09/sql-limit-n.png)

**Column Key Icons**

Additional icons are available for showing the [Foreign Keys](https://gethue.com/2019-11-13-sql-column-assist-icons/), when a column value points to another column in another table. e.g. The head of the business unit must exist in the person table:

![Assist Foreign Keys](https://cdn.gethue.com/uploads/2020/03/assist_foreign_keys_icons.png)

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

The sample popup now also supports navigating the relationships:

{{< youtube 4xgjvM51Rnw >}}

## ERD Table

A visual listing of the columns and the foreign key links helps understand quicker the schema and relationships while crafting SQL queries. See a live demo on the [documentation page](https://docs.gethue.com/developer/components/er-diagram/).

![ERD Table Components](https://cdn.gethue.com/uploads/2020/09/erd_table_viz.png)

**Note** The new shareable components system will be detailed in a follow-up blog post.

## Smart suggestions

A local assistant provides autocomplete suggestions for JOINs and simple Risk alerts (e.g. LIMIT clause missing).

![Popular joins suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png)

This is a beta feature. Here is how to enable it in the `hue.ini`.

    [medatata]
    [[optimizer]]
    # Requires Editor v2
    mode=local

## Importer

Some fixes were done on the Data Import Wizard so that creating new SQL tables is easier. Feel free to read more in the previous [post](https://gethue.com/querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/)

![Table Create Wizard](https://cdn.gethue.com/uploads/2019/03/insta_importer_step1.png)

## Editor v2 with Connectors

These are beta features and quite a bit of polishing is still needed but it is stable enough that we encourage users to try it and send feedback.

The query execution has been rewritten for better stability and running more than one query at the same time. More details about the new version will be released after the beta.

![Editor v2 Beta](https://cdn.gethue.com/uploads/2020/09/editor-v2-beta.png)

Here is how to enable it in the `hue.ini`.

    [notebook]
    enable_notebook_2=true

    [desktop]
    enable_connectors=true

**Note** [https://demo.gethue.com/](https://demo.gethue.com/) has the new Editor enabled




Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Onwards!

Romain from the Hue Team
