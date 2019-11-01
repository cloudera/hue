+++
title = "Developer"
date = 2019-03-13T18:27:26-07:00
weight = 4
chapter = false
pre = "<b>3. </b>"
+++

Hue services are generic and let you integrate with other analytics systems for [querying](/user/querying/) and [browsing](/user/browsing/). Here is a list of the main APIs:

* Connect or create SQL [autocompletes](/developer/parsers/) or connectors to any database (Impala, MySQL, Presto...)
* Browse additional storage systems (HDFS, S3, ADLS, GS...)
* List any jobs or queries (YARN, SQL queries, Kubernetes...)
* Integrate with a [Data Catalog](user/browsing/#data-catalog) (Cloudera Navigator, Apache Atlas...) or a Query Optimization service

In addition, whole new apps can also be created in order to provide end to end solutions.

Majoritively, this section would be useful for:

* Ramping-up with the overall Hue [development](/developer/development) project
* How to improve the [SQL autocomplete](/developer/parsers/) for your own database
* SqlAlchemy is becoming the [standard API](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/sql_alchemy.py) for databases other than Hive and Impala
* Check some [contribution ideas](https://github.com/cloudera/hue/blob/master/CONTRIBUTING.md)
