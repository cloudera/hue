[![CircleCI](https://img.shields.io/circleci/build/github/cloudera/hue/master.svg)](https://circleci.com/gh/cloudera/hue/tree/master)
[![DockerPulls](https://img.shields.io/docker/pulls/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)
![GitHub contributors](https://img.shields.io/github/contributors-anon/cloudera/hue.svg)

![Hue Logo](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png)


Query. Explore. Share.
----------------------

The Hue Editor is a mature open source SQL Assistant for querying any [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/).

Many companies and organizations use Hue to quickly answer questions via self-service querying.

* 1000+ customers
* Top Fortune 500

are executing 1000s of queries daily. It ships in Cloudera Data Platform, Google DataProc, Amazon EMR, Open Data Hub...

Hue is also ideal for building your own [Cloud SQL Editor](https://docs.gethue.com/developer/components/) and any contributions are welcome.

Read more on [gethue.com](http://gethue.com).

![Hue Editor](https://cdn.gethue.com/uploads/2021/02/hue-4.9.png)

Getting Started
---------------

You can start Hue via three ways described below. Once setup, you would then need to configure Hue to point to the [desired databases](https://docs.gethue.com/administrator/configuration/connectors/) you want to query.

Quick Demos:

* Docker Compose: [Impala](https://gethue.com/blog/quickstart-sql-editor-for-apache-impala/), [Flink SQL](https://gethue.com/blog/sql-querying-live-kafka-logs-and-sending-live-updates-with-flink-sql/), [ksqlDB](https://gethue.com/blog/tutorial-query-live-data-stream-with-kafka-sql/), [Phoenix SQL / HBase](https://gethue.com/blog/querying-live-kafka-data-in-apache-hbase-with-phoenix/), [Spark SQL](https://gethue.com/blog/querying-spark-sql-with-spark-thrift-server-and-hue-editor/)
* Live instance: [demo.gethue.com](https://demo.gethue.com/)

The Forum [is here](https://discourse.gethue.com/) in case you are looking for help.

Docker
------
Start Hue in a single click with the [Docker Guide](https://github.com/cloudera/hue/tree/master/tools/docker/hue) or the
[video blog post](http://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/).

    docker run -it -p 8888:8888 gethue/hue:latest

Now Hue should be up and running on your default Docker IP on the port 8888 [http://localhost:8888](http://localhost:8888)!

Read more about [configurations](https://github.com/cloudera/hue/tree/master/tools/docker/hue#configuration) then.

Kubernetes
----------

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install gethue/hue

Read more about configurations at [tools/kubernetes](tools/kubernetes/).

Development
-----------

First install the [dependencies](https://docs.gethue.com/administrator/installation/dependencies/), clone the Hue repo, build and get the development server running.

    # <install OS dependencies>
    git clone https://github.com/cloudera/hue.git
    cd hue
    make apps
    build/env/bin/hue runserver

Now Hue should be running on [http://localhost:8000](http://localhost:8000)!

Read more in the [development documentation](https://docs.gethue.com/developer/development/).

Note: For a very Quick Start and not even bother with installing a dev environment, go with the [Dev Docker](https://docs.gethue.com/developer/development/#dev-docker)


Community
-----------
   * How to [contribute](CONTRIBUTING.md)
   * Help Forum: https://discourse.gethue.com/
   * High level [roadmap](docs/ROADMAP.md)


License
-----------
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
