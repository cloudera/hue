
# A modern SQL Editor for Apache Flink SQL

## Background

* https://ci.apache.org/projects/flink/flink-docs-master/dev/table/sql/queries.html#queries
* https://github.com/ververica/flink-sql-gateway
* https://github.com/cloudera/hue/issues/1010

![Hue Flink Editor](https://cdn.gethue.com/uploads/2020/04/editor_flink_sql_select.png)

This document is about the Query UX specific improvements and assumes a running Flink cluster is available.

## Demo

https://github.com/romainr/flink-sql-gateway/tree/master/docs/demo

## Tasks

The big pieces would be to stabilize a query API, improve the SQL autocomplete, make the full setup work out of the box.


### API

* Currently leveraging the [Flink SQL Gateway](https://github.com/ververica/flink-sql-gateway)
  * Early stage
  * From Ververica (Apache 2)
  * Could be turned to a SqlAchemy module for more standardization
  * List of [supported statements](https://github.com/ververica/flink-sql-gateway#supported-statements)
  * See some of the [open issues](https://github.com/ververica/flink-sql-gateway/issues/created_by/romainr)
* Security support
* Fetching results
  * Use the proper result grid instead of list items
  * Move counter to query handle
  * Fetch N
  * Live queries

### UI

* Full Editor
  * Calcite SQL Autocomplete subset (grammar, built ins... https://ci.apache.org/projects/flink/flink-docs-master/dev/table/sql/)
    * Some pieces can be re-used with other Calcite Dialects (Phoenix...)
  * Right panel UDF/Language references
  * Mini Query Browser
  * Risk Alerts
* Support and display of "live" query/streams
* Addition of Task Server and Websockets for smoother support
* Importer support

Non Full Editor: some ways to iteratively get some progress could be to start with these static modules which don't necessarily require a running Hue.

![Flink SQL Scratchpad Editor](https://cdn.gethue.com/uploads/2020/04/flink_cloudera.jpeg)

* Autocomplete Parser module
  * https://docs.gethue.com/developer/api/#npm-package

* Scratchpad Editor
  * https://docs.gethue.com/developer/api/


### Admin

* CDP auto configuration of properties (e.g. Flink Gateway service config, Hue...)
