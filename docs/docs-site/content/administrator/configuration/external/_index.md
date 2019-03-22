---
title: "Other services"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

## YARN Cluster

Hue supports one or two Yarn clusters (two for HA). These clusters should be defined
under the `[[[default]]]` and `[[[ha]]]` sub-sections.

    # Configuration for YARN (MR2)
    # ------------------------------------------------------------------------
    [[yarn_clusters]]

      [[[default]]]

        resourcemanager_host=yarn-rm.com
        resourcemanager_api_url=http://yarn-rm.com:8088/
        proxy_api_url=http://yarn-proxy.com:8088/
        resourcemanager_port=8032
        history_server_api_url=http://yarn-rhs-com:19888/

## Oozie

In the `[liboozie]` section of the configuration file, you should
specify:

    [liboozie]
      oozie_url=http://oozie-server.com:11000/oozie


## Solr

In the `[search]` section of the configuration file, you should
specify:

    [search]
      # URL of the Solr Server
      solr_url=http://solr-server.com:8983/solr/

## Spark

The `[spark]` section details how to point to [https://livy.incubator.apache.org/](https://livy.incubator.apache.org/) in order to execute interactive Spark snippets in Scala or Python.

    [spark]
      # Host address of the Livy Server.
      ## livy_server_host=localhost

      # Port of the Livy Server.
      ## livy_server_port=8998

## Catalog

In the `[metadata]` section, Hue is supporting Cloudera Navigator data catalog and soon Apache Atlas ([HUE-8749](https://issues.cloudera.org/browse/HUE-8749)).

## Query Optimization

In the `[metadata]` section, Hue is supporting Cloudera Navigator Optimiser and soon other services. The goal is to provide recommendation on how to write better queries and get risk alerts on dangerous operations.

## Kafka

The configuration is in `[kafka]` but the service is still experiemental.
