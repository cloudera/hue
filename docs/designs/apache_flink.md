
# A modern SQL Editor for Apache Flink SQL

## Background

* https://docs.cloudera.com/csa/1.1.0/flink-overview/topics/csa-flink-overview.html
* https://github.com/ververica/flink-sql-gateway
* https://twitter.com/rmetzger_/status/1253013022697807879

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
  * Note: initial tables needs to be defined and loaded via a config file (which I could [not make it work](https://github.com/cloudera/hue/issues/1010#issuecomment-620042416) so far)
  * Could be turned to a SqlAchemy module for more standardization
  * List of [supported statements](https://github.com/ververica/flink-sql-gateway#supported-statements)
* Security support?
* Fetching more results

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

Note: some ways to iteratively get some progress could be to start with these static modules which don't necessarily require a running Hue.

![Flink SQL Scratchpad Editor](https://cdn.gethue.com/uploads/2020/04/flink_cloudera.jpeg)

* Autocomplete Parser module
  * https://docs.gethue.com/developer/api/#npm-package

* Scratchpad Editor
  * https://docs.gethue.com/developer/api/


### Admin

* CDP auto configuration of properties (e.g. Flink Gateway service config, Hue...)
