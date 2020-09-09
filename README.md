[![CircleCI](https://img.shields.io/circleci/build/github/cloudera/hue/master.svg)](https://circleci.com/gh/cloudera/hue/tree/master)
[![DockerPulls](https://img.shields.io/docker/pulls/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)
![GitHub contributors](https://img.shields.io/github/contributors-anon/cloudera/hue.svg)

![Hue Logo](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png)


Query. Explore. Share.
----------------------

Hue is a mature open source SQL Assistant for [querying](https://docs.gethue.com/user/querying/) any [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/) and collaborating: [gethue.com](http://gethue.com)

Many companies and organizations use Hue to quickly answer questions via self-service querying e.g.:

* 1000+ customers
* Top Fortune 500

are executing 100s of 1000s of queries daily. It also [ships](https://docs.gethue.com/administrator/installation/) in Cloudera Data Platform, Amazon AWS, Open Data Hub...

Hue is also ideal for building your own [Cloud SQL Editor](https://docs.gethue.com/developer/api/) and any [contributions](https://docs.gethue.com/developer/) are welcome.


![Hue Editor](https://cdn.gethue.com/uploads/2020/04/hue-4.7.png)

Getting Started
---------------

You can start Hue in 3 ways - From source, Docker or Kubernetes. Once setup you would have to configure Hue to point to the desired databases you want to query.

The [Forum](https://discourse.gethue.com/) is here in case you are looking for help.

Building From Source
-----------

First, clone Hue repo, install the [dependencies](https://docs.gethue.com/administrator/installation/dependencies/), build and get the development server running.

```
# Install dependencies
git clone https://github.com/cloudera/hue.git
cd hue
make apps
build/env/bin/hue runserver
```

Now Hue should be running on [http://localhost:8000](http://localhost:8000)!

Read more about configurations in the [development documentations](https://docs.gethue.com/developer/development/).

Docker
------
Start Hue in a single click with the [Docker Guide](https://github.com/cloudera/hue/tree/master/tools/docker/hue) or the
[video blog post](http://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/).

    docker run -it -p 8888:8888 gethue/hue:latest

Now Hue should be up and running on your default Docker IP on the port 8888 [http://localhost:8888](http://localhost:8888)!

Read more about [configurations](https://github.com/cloudera/hue/tree/master/tools/docker/hue#configuration) then.

Development Docker
------------------

For a very Quick Start and not even bother with installing a dev environment, go with the [Dev Docker](https://docs.gethue.com/developer/development/#dev-docker).

Kubernetes
----------

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install gethue/hue

Read more about configurations at [``tools/kubernetes``](tools/kubernetes/).


Community
-----------
   * How to [contribute](CONTRIBUTING.md)
   * Help Forum: https://discourse.gethue.com/
   * High level [roadmap](docs/ROADMAP.md)
   * Jira: https://issues.cloudera.org/browse/HUE


License
-----------
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
