[![CircleCI](https://img.shields.io/circleci/build/github/cloudera/hue/master.svg)](https://circleci.com/gh/cloudera/hue/tree/master)
[![DockerPulls](https://img.shields.io/docker/pulls/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)
![GitHub contributors](https://img.shields.io/github/contributors-anon/cloudera/hue.svg)

![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


Query. Explore. Repeat.
-----------------------

Hue is an open source SQL Workbench for browsing, querying and visualizing data in cloud/on-prem Data Warehouses: [gethue.com](http://gethue.com)

It features:

   * [Editors](http://gethue.com/sql-editor/) to query with SQL [any database](http://cloudera.github.io/hue/latest/admin-manual/manual.html#connectors) and submit jobs
   * [Dashboards](http://gethue.com/search-dashboards/) to dynamically interact and visualize data
   * [Scheduler](http://gethue.com/scheduling/) of jobs and workflows
   * [Browsers](http://gethue.com/browsers/) for data and a Data Catalog


![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/sql-editor.png "Hue Editor")

![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/dashboard.png "Hue Dashboard")


Who is using Hue
----------------
Thousands of companies and organizations use Hue to open-up their data and provide self service querying in order to make smarter decisions. Just at Cloudera, Hue is heavily used by thousand of customers executing millions of queries daily. Hue directly ships in Cloudera, Amazon, MapR, BigTop and is compatible with the other distributions.


Getting Started
---------------
Add the development packages, build and get the development server running:
```
git clone https://github.com/cloudera/hue.git
cd hue
make apps
build/env/bin/hue runserver
```
Now Hue should be running on [http://localhost:8000](http://localhost:8000) ! The configuration in development mode is `desktop/conf/pseudo-distributed.ini`.

Read more in the [installation documentation](http://cloudera.github.io/hue/latest/administrator/installation/).


Docker
------
Start Hue in a single click with the [Docker Guide](https://github.com/cloudera/hue/tree/master/tools/docker) or the
[video blog post](http://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/).


Kubernetes
----------
Configurations to start a Hue server are available at [``tools/kubernetes``](tools/kubernetes/). The Kubernetes [hue.yaml](tools/kubernetes/helm/hue/templates/hue.yaml)
configuration is available in the template directory.


Community
-----------
   * Help Forum: https://discourse.gethue.com/ ([previous mailing list](http://groups.google.com/a/cloudera.org/group/hue-user))
   * High level [roadmap](docs/ROADMAP.md)
   * How to [contribute](docs/CONTRIBUTING.md)
   * Jira: https://issues.cloudera.org/browse/HUE


License
-----------
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
