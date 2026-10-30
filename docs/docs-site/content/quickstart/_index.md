---
title: "Quick start"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 1
---

## Get Hue

Start Hue with [Docker](/administrator/installation/cloud/#docker):

```bash
docker run -it -p 8888:8888 gethue/hue:latest
```

Open [http://localhost:8888](http://localhost:8888). The first user who logs in becomes the superuser.

Or start Hue on [Kubernetes](/administrator/installation/cloud/#kubernetes) with Helm:

```bash
helm repo add gethue https://helm.gethue.com
helm repo update
helm install hue gethue/hue
```

The command prints how to reach the Hue service. To build Hue from source instead, see the [installation guide](/administrator/installation/).

> **Note:** The Docker image uses an embedded SQLite database by default. Connect Hue to [MySQL or PostgreSQL](/administrator/administration/database/) before real use.

## Configure Hue

[Configure the server](/administrator/configuration/) and point the connectors to your [databases, warehouses, and storages](/administrator/configuration/connectors/).

## Use Hue

These tutorials show how to:

* [Create and query a Customer 360](https://gethue.com/self-service-bi-doing-a-customer-360-by-querying-and-joining-salesforce-marketing-and-log-datasets/)
* [Upload data and turn it into a SQL table](https://gethue.com/querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/)

To build Hue from source, see the [dependencies](/administrator/installation/dependencies/). To contribute, see the [developer guide](/developer/).
