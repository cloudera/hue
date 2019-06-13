---
title: "Other services"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 5
---


## Data Catalog

In the `[metadata]` section, Hue is supporting Cloudera Navigator and soon Apache Atlas ([HUE-8749](https://issues.cloudera.org/browse/HUE-8749)) in order to enrich the [data catalog]({{% param baseURL %}}user/browsers/).

## Spark

The `[spark]` section details how to point to [Livy](https://livy.incubator.apache.org/) in order to execute interactive Spark snippets in Scala or Python.

    [spark]
      # Host address of the Livy Server.
      ## livy_server_host=localhost

      # Port of the Livy Server.
      ## livy_server_port=8998

## Kafka

The configuration is in `[kafka]` but the service is still experiemental.


## Oozie

In oder to schedule workflows, the `[liboozie]` section of the configuration file:

    [liboozie]
      oozie_url=http://oozie-server.com:11000/oozie

Make sure that the [Share Lib](https://oozie.apache.org/docs/5.1.0/DG_QuickStart.html#Oozie_Share_Lib_Installation) is installed.

To configure Hue as a default proxy user, add the following properties to /etc/oozie/conf/oozie-site.xml:

    <!-- Default proxyuser configuration for Hue -->
    <property>
        <name>oozie.service.ProxyUserService.proxyuser.hue.hosts</name>
        <value>*</value>
    </property>
    <property>
        <name>oozie.service.ProxyUserService.proxyuser.hue.groups</name>
        <value>*</value>
    </property>

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
