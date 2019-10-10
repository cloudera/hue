---
title: "Quick Start"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 1
---

## Get

Via [Kubernetes](/administrator/installation/cloud/#kubernetes):

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install gethue/hue

Or [Docker](/administrator/installation/cloud/#docker):

    docker run -it -p 8888:8888 gethue/hue:latest

## Configure

Then [configure the server](/administrator/configuration/) and point connectors to your [Databases, Warehouses, Storages](/administrator/configuration/connectors/).

## Use or Develop

Some tutorials on how to:

* [Query a Customer 360](http://gethue.com/self-service-bi-doing-a-customer-360-by-querying-and-joining-salesforce-marketing-and-log-datasets/)
* [Troubleshoot SQL](http://gethue.com/self-service-impala-sql-query-troubleshooting/)
* [Ingest data](http://gethue.com/querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/)
* [Bike Data Analysis](https://docs.cloudera.com/runtime/7.0.1/using-hue/topics/hue-using.html)

How to improve and contribute the [SQL autocomplete](/developer/parsers/) for your own database.
