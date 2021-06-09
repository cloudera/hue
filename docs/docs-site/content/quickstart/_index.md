---
title: "Quick Start"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 1
---

## Get

Via [Docker](/administrator/installation/cloud/#docker):

    docker run -it -p 8888:8888 gethue/hue:latest

Or [Kubernetes](/administrator/installation/cloud/#kubernetes):

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue

## Configure

Then [configure the server](/administrator/configuration/) and point connectors to your [Databases, Warehouses, Storages](/administrator/configuration/connectors/).

## Use

Here are some tutorials on how to:

* [Create and Query a Customer 360](http://gethue.com/self-service-bi-doing-a-customer-360-by-querying-and-joining-salesforce-marketing-and-log-datasets/)
* [Upload data and turn it into a SQL table](http://gethue.com/querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/)
* [Ingest and analyse bike data](https://docs.cloudera.com/runtime/7.0.1/using-hue/topics/hue-using.html)

For development please check how to [install](/administrator/installation/dependencies/) or [contribute](/developer/).
