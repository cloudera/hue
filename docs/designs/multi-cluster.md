# Multi Cluster Hue

Goal: clusters of configurations of external services

* Multi clusters [HUE-8330](https://issues.cloudera.org/browse/HUE-8330)

## In the classic world

###  Cluster with no Hive, just Impala

Create a 'apps/hive', when this one is blacklisted, there is no Hive Editor
'apps/beeswax' is seen like the HiveServer2 lib, and so should never be blacklisted (one day to move to libs). Impala, HMS also depends on it.
Add HMS configuration in the 'apps/metastore'

To work with CM to have them blacklist 'hive' instead of 'beeswax' now. To also have them provide the HMS info into [metastore].

One trick is that the HMS should not be seen as an interpreter, but more like a namespace.

## In the new world

Multi tenant, multi cluster. In practice, 1 cluster means CM instance, 1 GCP Project, 1 Altus instance, 1 Azure resource (less ambiguity with "computes" this way).

e.g.

- CM instance with 1 base storage and 2 compute only clusters. Each compute cluster can consist of combos of at least 1 HS2 LLAP, 1 HS2 batch, 1 Impala services.
- Altus SaaS instance, we have one Data warehouse service with 2 possible engines
- GCP instance: we have one Project with one BigQuery and File storage
- AWS instance: we have a general Glue, Athena, S3 and combinations of Redshifts. Even S3 and Athenas could be multiple with services. Each compute services is tights to the storages.

hue.ini

    [desktop]

      [[tenants]]

        [[[[extra]]]]

        [[[clusters]]]

          [[[[storages]]]]

          [[[[interpreters]]]]

          [[[[extra]]]]

**[extra]** TBD stuff. Could be several sections too of global stuff, like Hue specific stuff, common service catalogs / NavOpts, schedulers...
**note** We have default tenant and cluster to work with the new format. Work to do to par app configs in the new sub-sections instead of classic top sections like [search], [impala]... but this is the way to go. Will be done without braking the current classic way of writing in the full ini.

Each instance of the sections:

- tenants
- clusters

can also be edited via the UI interface [HUE-8758](https://issues.cloudera.org/browse/HUE-8769) and saved into 2 new tables. In practice either the ini or the UI should be used (or read only if config coming from ini). It is simpler to start with interpreters (similar to Superset, Periscope, e.g. https://superset.incubator.apache.org/installation.html#deeper-sqlalchemy-integration).


## Mockups

1 CM multi cluster from above
3 interpreters (1 HS2 LLAP, 1 HS2 batch, 1 Impal), multi cluster dropdown hidden.
Can browse Catalog via HMS or the 3 other interpreters
Can browse the base HDFS.

1 DP2 Hive & Impala
2 interpreters (1 Hive, 1 Impala), multi cluster listing computes of each one.
Can browse Catalog via HMS or any running computes (to get samples)
Can browse each S3 of each namespace.

The **concept** is to drive the flow via the metadata (top search, left assist...), where selecting a namespace automatically restricts the computes (and if possible even hides their concept). e.g. like we do when selecting Impala Editor, we auto switch the left assist to the Impala view of table. It would be the same for all the data/metadata (tables, files,...).


    [desktop]

    enabled_connectors = ['hive-tez', 'impala', 'hdfs'....]
    desktop/connectors Python class? with fields to display in UI

    [clusters]

      [[cm-classic]]

        # One section by connector API category: notebook, catalog, optimizer, browsers, scheduler, apps

        [[[connectors]]   ## Classes

          [[[[hive]]]]
          class=query
          interface=hiveserver2
          type=hive-tez

          # r/w pemrs to generate: DWX? create-cluster perm to pull?

            [[[[hive-Tez]]]] ## Instances
            server_host=...
            # beeswax config?
            [[[[hive-Tez2]]]]

          [[[[[impala]]]]]
          class=query
          type=impala
          interface=hiveserver

          [[[[[solr]]]]]
          type=query
          interface=solr

          [[[[[impala-3]]]]]

            ## instance 3
            ## instance 4

        [[[hms]]]
        type=browser
        interface=hiveserver2


          [[[[[[hdfs]]]]]]

          [[[[[[yarn]]]]]]

        [[[[[metadata]]]]]]

            [[[[[[atlas]]]]]]

      [[[[cm-mutli]]]]

        [[[[[interpreters]]]]]   ## Classes

          [[[[[[[hive-tez]]]]]]

                                 ## Instances

          [[[[[[hive-llap]]]]]]

          [[[[[[impala-1]]]]]]

          [[[[[[impala-2]]]]]]

          [[[[[[impala-3]]]]]]

            ## instance 3
            ## instance 4

        [[[[[browsers]]]]]]

          [[[[[[hms]]]]]]

          [[[[[[hdfs]]]]]]

          [[[[[[yarn]]]]]]

        [[[[[metadata]]]]]]

            [[[[[[atlas]]]]]]

      [[[snowball]]]

        [[[[interpreters]]]]

          [[[[[hive-llap]]]]]

          [[[[[impala]]]]]

          [[[[[druid]]]]]

        [[[[browsers]]]]]

          [[[[s3]]]]

        [[[[[metadata]]]]]]

            [[[[[[atlas]]]]]]

            [[[[[[ranger]]]]]]


      [[[aws]]]

          [[[[interpreters]]]]

            [[[[[redshift-1]]]]]

            [[[[[redshift-2]]]]]

            [[[[[athena]]]]]

          [[[[browsers]]]]]

            [[[[s3]]]]

          [[[[metadata]]]]]

              [[[[[glue]]]]]

      [[[gcp]]]

          [[[[interpreters]]]]

            [[[[[bigquery-1]]]]]

            [[[[[bigquery-2]]]]]

          [[[[browsers]]]]]

            [[[[gfs]]]]
