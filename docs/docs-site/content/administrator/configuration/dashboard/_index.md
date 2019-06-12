---
title: "Dashboard"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

Manually typing SQL is not always the most efficient way to explore a dataset. Dashboards offer visual explorations without typing code.

They consist in 3 types:

* Interactive multi-widget querying of one source of data
* Query Builder (alpha)
* Multi-widget reporting (alpha)

## Solr Search

In the `[search]` section of the configuration file, you should
specify:

    [search]
      # URL of the Solr Server
      solr_url=http://solr-server.com:8983/solr/

## SQL

This application is getting improved via SQL Dashboards and Query Builder [HUE-3228](https://issues.cloudera.org/browse/HUE-3228).

      [dashboard]

      # Activate the Dashboard link in the menu.
      ## is_enabled=true

      # Activate the SQL Dashboard (beta).
      ## has_sql_enabled=false

      # Activate the Query Builder (beta).
      ## has_query_builder_enabled=false

      # Activate the static report layout (beta).
      ## has_report_enabled=false

      # Activate the new grid layout system.
      ## use_gridster=true

      # Activate the widget filter and comparison (beta).
      ## has_widget_filter=false

      # Activate the tree widget (to drill down fields as dimensions, alpha).
      ## has_tree_widget=false

      [[engines]]

      #  [[[solr]]]
      #  Requires Solr 6+
      ##  analytics=true
      ##  nesting=false

      #  [[[sql]]]
      ##  analytics=true
      ##  nesting=false
