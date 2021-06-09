
# A modern SQL Editor for Apache Phoenix

## Background

* https://blog.cloudera.com/apache-phoenix-for-cdh/
* https://blog.cloudera.com/operational-database-accessibility/
* http://gethue.com/sql-querying-apache-hbase-with-apache-phoenix/

![Hue Phoenix Editor](https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png)

This document is about the Hue specific improvements and assumes a running Phoenix server is available.

## Tasks

The most crucial is to stabilize the querying API, improve the Editor assistant (Phoenix SQL Autocomplete) and make the full setup work out of the box.

[ Phoenix <-> Hue <-> User Browser ]

### API

* SqlAchemy API
  * Improve Session and closing statements similarly to https://github.com/cloudera/hue/issues/1020
  * Caching or storage of larger resultsets
  * Impersonation support http://phoenix.apache.org/server.html#Impersonation

* Phoenix connector
  * to ship
  * to "battle test" ([pyPhoenix](https://github.com/Pirionfr/pyPhoenix#known-issues), reuse [DB 2.0 API](https://phoenix.apache.org/python.html) [PhoenixDB](https://github.com/apache/phoenix/tree/master/python)?)
  * with Hue Editor API to polish ([dev reference](https://docs.gethue.com/developer/development/#connectors))
  * all SQL supported?
* Security support?
* Install samples?

### UI

* Calcite SQL Autocomplete subset ([grammar](https://phoenix.apache.org/language/index.html) + [builtins](https://phoenix.apache.org/language/functions.html)) ([dev reference](https://docs.gethue.com/developer/development/#sql-parsers))
* Left SQL assist panel
* Trim the semicolon `;`
* Right panel UDF/Language references

* HBase <-> Phoenix UX (simplify Phoenix onboarding, leverage current HBase integration)
  * Existing HBase tables need to be mapped to views
  * Tables are seeing as uppercase by Phoenix

### Admin

* CM CDP auto configuration of Hue properties (e.g. Phoenix service config)
