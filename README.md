[![CircleCI](https://img.shields.io/circleci/build/github/cloudera/hue/master.svg)](https://circleci.com/gh/cloudera/hue/tree/master)
[![DockerPulls](https://img.shields.io/docker/pulls/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)
![GitHub contributors](https://img.shields.io/github/contributors-anon/cloudera/hue.svg)

![Hue Logo](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png)


# Query. Explore. Share.

Hue is a mature SQL Assistant for querying Databases & Data Warehouses.

* 1000+ customers
* Top Fortune 500

use Hue to quickly answer questions via self-service querying and are executing 100s of 1000s of queries daily.

Read more on [gethue.com](http://gethue.com) and
- Connect to a [database](https://docs.gethue.com/administrator/configuration/connectors/)
- Build your own Editor with the [SQL Scratchpad](https://docs.gethue.com/developer/components/scratchpad/)
- Boot the [Query Service](https://docs.gethue.com/administrator/installation/cloud/#kubernetes) and query via the UI/[API](https://docs.gethue.com/developer/api/)

![Hue Editor](https://cdn.gethue.com/uploads/2021/02/hue-4.9.png)

# Getting Started

Quick Demos:

* Docker Compose: [Impala](https://gethue.com/blog/quickstart-sql-editor-for-apache-impala/), [Flink SQL](https://gethue.com/blog/sql-querying-live-kafka-logs-and-sending-live-updates-with-flink-sql/), [ksqlDB](https://gethue.com/blog/tutorial-query-live-data-stream-with-kafka-sql/), [Phoenix SQL / HBase](https://gethue.com/blog/querying-live-kafka-data-in-apache-hbase-with-phoenix/), [Spark SQL](https://gethue.com/blog/querying-spark-sql-with-spark-thrift-server-and-hue-editor/)
* Live instance: [demo.gethue.com](https://demo.gethue.com/)

Three ways to start the server then configure the [databases](https://docs.gethue.com/administrator/configuration/connectors/) you want to query:

## Docker
Start Hue in a single click with the [Docker Guide](https://github.com/cloudera/hue/tree/master/tools/docker/hue) or the
[video blog post](http://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/).

    docker run -it -p 8888:8888 gethue/hue:latest

Now Hue should be up and running on your default Docker IP on [http://localhost:8888](http://localhost:8888)!

## Kubernetes

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue

Read more about configurations at [tools/kubernetes](tools/kubernetes/).

## Development

For a very Quick Start go with the [Dev Environment Docker](https://docs.gethue.com/developer/development/#dev-docker).

Or install the [dependencies](https://docs.gethue.com/administrator/installation/dependencies/), clone the repository, build and get the server running.

    # <install OS dependencies>
    git clone https://github.com/cloudera/hue.git
    cd hue
    make apps
    build/env/bin/hue runserver

Now Hue should be running on [http://localhost:8000](http://localhost:8000)!

Read more in the [documentation](https://docs.gethue.com/developer/development/).

# Components

SQL Editor, Parsers [components](https://docs.gethue.com/developer/components/) and REST/Python/CLI [APIs](https://docs.gethue.com/developer/api/).

# License
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
