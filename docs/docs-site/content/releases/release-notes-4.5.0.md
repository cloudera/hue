---
title: "4.5.0"
date: 2019-08-08T18:28:08-07:00
draft: false
weight: -4050
tags: ['skipIndexing']
---

### Hue v4.5.0, released August 12th 2019


Hue, http://gethue.com, is an open source SQL Cloud Assistant for developing and accessing SQL/Data Apps.

Its main features:

* Editors to query with SQL any database and submit jobs
* Dashboards to dynamically interact and visualize data
* Scheduler of jobs and workflows
* Browsers for data and a Data Catalog

Read the complete list of improvements on [Hue 4.5 is out!](http://gethue.com/hue-4-5-and-its-improvements-are-out/).


Summary
-------
The focus of this release was to modularize the tech stack, improve SQL integrations and prepare major upcoming features.


Notable Changes
---------------

* SQL
  * Apache Atlas integratation and Catalog API
  * Hive LLAP + Service discovery
  * Hive language reference
  * HBase Phoenix querying example
* Interface
  * Left menu revamp
  * Left assist panel aggregating storage (HDFS, ADLS, S3)
  * Webpack inegration
* Documentation Revamp
    * Architecture
    * Building SQL Autocompletes
    * SQL connectors refresh
* Cloud
  * Kubernetes Helm
  * CI


Compatibility
-------------

Runs on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7), and Ubuntu 16.04 and 18.04.

Tested with CDH6. Specifically:

- Hadoop 3.0
- Hive 2.1 / 3.0
- Oozie 5.0
- HBase 2.0
- Pig 0.17
- Impala 3.0
- Solr 7.4
- Spark 2.2

Other versions should work, but not tested.


Supported Browsers:

Hue works with the two most recent versions of the following browsers.

* Chrome
* Firefox LTS
* Safari (not supported on Windows)
* Internet Explorer / Edge



Runs with Python 2.7+

Note: CentOS 6 and RHEL 6 require EPEL python 2.7 package.


List of 666+ Commits
---------------------

* 8151b7c82c [HUE-8947](https://issues.cloudera.org/browse/HUE-8947) [docs] Perform 4.5 release
* ce7362e32e [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Add cron jobs for running the email stats command
* fb98cd8577 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Support for SendGrid email backend
* cb8634aa34 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Do not enable traefik deployment when not set
* 7982301cfa [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Properly enable trafeik cluster roles only when needed
* 517fc1b894 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Clean-up notes.txt and disable task server per default
* 3e1d7d326b [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding readinessProbe to Hue deployment
* b01c78b421 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Also add ingress and ssl Hue address in the notes if configured
* 4ba812acc7 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Use load balanced Hue address in thenotes if configured
* 12fb57c67f [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Configure and refactor all the options
* cb1234ff1b [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding postgres yaml definitions
* 8b331aebbe [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding helm postgres storage definitions
* d434ab72f1 [HUE-8943](https://issues.cloudera.org/browse/HUE-8943) [core] Update menu app active selection to not conflict
* 26f59f4983 [HUE-8943](https://issues.cloudera.org/browse/HUE-8943) [core] Update icons for jobs and HBase
* c1af5fc748 [HUE-8943](https://issues.cloudera.org/browse/HUE-8943) [importer] Add importer to the new left menu
* dad396718d [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Give S3 access to default group when IDBroker enabled.
* 7d50ff8322 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Removing calling_format from connect_to_region
* d1894df599 [HUE-8944](https://issues.cloudera.org/browse/HUE-8944) [impala] Hide INVALIDATE METADATA refresh option
* a6ea8a9549 [HUE-8945](https://issues.cloudera.org/browse/HUE-8945) [core] Avoid 500 when blacklisting zookeeper,proxy,rdbms,indexer
* 77d766a5f8 [HUE-8945](https://issues.cloudera.org/browse/HUE-8945) [useradmin] Only list permissions of enabled apps
* 3298e3ea0c [HUE-8942](https://issues.cloudera.org/browse/HUE-8942) [editor] Opening query when editor is not loaded yet can throw 403
* 64798571ab [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Rename nginx-deployment to nginx-hue
* a96977707c [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Set to use Gunicorn
* df36e4210a [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding ingress configuration for http and https
* 5193ff4762 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Splitting nginx deployment in several yaml files
* 00b309a2c3 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding postgres service
* 2d990dbea7 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding cert-manager for SSL
* b21bb2bd51 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Start removing global connector list
* 5030f84bac [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Remove hardcoding of connector instances
* 717407e89c [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add a flag to turn the feature on
* e2e2cbd240 PR941 [fix] fix bug -- table browser can not add discription (#941)
* 731263bfa4 [HUE-8913](https://issues.cloudera.org/browse/HUE-8913) [assist] Fixed manual reload for side panel (#940)
* 70a9e784e6 [HUE-8939](https://issues.cloudera.org/browse/HUE-8939) [oozie] Avoid exception when hive is not configured.
* e7ef4d45c9 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [design] Adding high level goal of tracing framework
* 917eed1b9e [HUE-8941](https://issues.cloudera.org/browse/HUE-8941) [libsaml] Protect xmlsec dynamic default when which is not present
* 49190c3daf [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [admin] Update Configuration link to docs.gethue.com
* 31e001ed0c [HUE-8940](https://issues.cloudera.org/browse/HUE-8940) [core] Temporaly disable js optimization has hanging the build
* ab2acd5a21 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Fix typo in values for balancer enabling flag
* 0ad8e49722 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Set celery result backend as Redis
* 7bb2ba1450 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding celery flower k8s service
* 277639334e [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding celery flower yaml service
* d81c0b0056 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Using Redis for Task Server query storage
* 221c568c92 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Update hue chart description
* da038d149d [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [docker] Adding django_redis module
* 2bfde3054e [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Clean-up charts and add missing image and replica values
* d8ceeee01b [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Add celery beat deployment
* 9b804adde1 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding connector value for testing querying
* 8d0a6b4ba7 [HUE-8935](https://issues.cloudera.org/browse/HUE-8935) [hadoop] Small code formatting in exception libs
* 9174ac3bc1 [HUE-8935](https://issues.cloudera.org/browse/HUE-8935) [hadoop] Fix default KeyError at /notebook/api/execute
* a55b18197f [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Fix _parse_core_site when no HDFS_CLUSTERS
* 9431165f83 [HUE-8937](https://issues.cloudera.org/browse/HUE-8937) [frontend] Fix document sharing when selecting from autocomplete
* 0639906576 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Only get AWS client when uploading to AWS.
* 3cac9d3e51 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] enable S3 by default when IDBroker is configured.
* 218a969ad8 [HUE-8934](https://issues.cloudera.org/browse/HUE-8934) [editor] Fix impala install_samples
* b2d0bd1b26 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Add additional error information to user
* 82c5ccf669 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Move the user menu to the left sidebar
* 6dafa3594f [HUE-8933](https://issues.cloudera.org/browse/HUE-8933) [editor] Make sure to clear any previous result when the execute call returns
* 3cc0f4a118 [HUE-8932](https://issues.cloudera.org/browse/HUE-8932) [impala] Add use_sasl configuration
* 6c5a5e295a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix impala _get_api
* 12276eb870 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Add configurable base URLs for the app-switcher
* ce650fb5e5 [HUE-8923](https://issues.cloudera.org/browse/HUE-8923) [assist] Make sure the tags spinner isn't hidden behind the filter input
* 9c04d9372e [HUE-8924](https://issues.cloudera.org/browse/HUE-8924) [editor] Only show language reference popover for Impala tokens
* ee1f531b28 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Default to PROD environment for the app switcher
* b3d28728d7 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Adjust some colors to fit the new color scheme
* 137958f0a2 [HUE-8931](https://issues.cloudera.org/browse/HUE-8931) [impala] Invalidate API has a wrong parameter
* 0adf53d4ad [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding redis and celery basic configs
* e8944fc03c [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Polishing redis service
* dc0943ca14 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Polishing celery worker service
* 2844628f15 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding basic ingress for hue
* 1a67ad9922 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Added basic nginx deployment
* ce13b9ce83 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Basic nginx for the Helm chart
* 70d95cecad [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Adding missing hue ini configmap yaml file
* 4e368e33c2 [HUE-8930](https://issues.cloudera.org/browse/HUE-8930) [importer] Fix import using impala without hive
* bdd3d3d69d [HUE-8927](https://issues.cloudera.org/browse/HUE-8927) [oozie] Fix Oozie bundle cannot be submitted
* f1444eda7a [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [core] Add test for public views access
* 892f9bd0fc [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [docker] Do not install openssl as breaking crytograhpy module
* 6d6dd8494c [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [monitoring] Make /metrics page public
* 04ed8ec022 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [metrics] Add django-prometheus and prometheus_client to ext-py
* d3256eaa94 [HUE-8929](https://issues.cloudera.org/browse/HUE-8929) [home] Remove "Hive Query" from drop down of "New Documents" icon if not configured
* 08dc965c33 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [monitoring] Prometheus database monitoring only compatible with MySql
* e1d0e9f78b [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Support user credentials from IDBroker for S3
* cd2ddbc478 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Show the Hue logo when the app switcher is enabled
* 02e881bf30 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Add new app switcher header
* 3f7a9668bf [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Use json source for app switcher URLs
* 6b37c1a097 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Improve logo design when there's no app switcher
* f8530c8622 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Improve sidebar active item marking
* 142b15023f [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Adjust the sidebar collapsed icon size and spacing
* 5f8f585d86 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Introduce a hueAppIcon binding
* 7efa0bd863 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Clean-up the sidebar and app switcher less styles
* 4a5c30292c [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Update the Hue colour scheme
* 0cd648a73e [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Add the new app switcher
* 33bd18297c [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Add config flag to enable the app switcher
* 81cf9c60a6 [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Add new left navigation sidebar
* c939c59c37 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Use connector server_config when has_connectors
* be382aa5f4 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [core] Add .babelrc to tarball
* 5dd28c6c43 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sqlalchemy] Set None Database names to empty string
* ab65c82d47 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [docs] Add reference to sqlalchemy connector for Phoenix
* 2328ee3145 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Update impala URLs in current template
* 7e852a96aa [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding instruction on how to build SQL parsers
* 2b310a6f11 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Move dev docker section to the Developer guide
* c74c70e793 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add two sections to top configuration page
* 968f45ec94 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Level up quick start section
* ad67850045 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add connector dialect to get_config editor
* 6bf2b53273 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add document clean-up info to the reference archi
* d1246b2d4d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Improve the reference architecture
* 3a9dacb701 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Add basic Prometheus metric endpoint
* f1b2dde3ea [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Add local install of eslint-plugin
* 60706f69fe [HUE-8915](https://issues.cloudera.org/browse/HUE-8915) [frontend] Add linting rules for jasmine tests
* f34724e24c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Getting default pylintrc from pylint project
* 09c4926e76 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [docs] Add official helm chart repo URL
* c126bc7b0d [HUE-8922](https://issues.cloudera.org/browse/HUE-8922) [frontend] Show dates and times in local format with timezone offset details
* 92e9fa0d13 [connectors] Update get_query_server_config signature and snippet wheel
* 2acebe66f8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Remove unused _get_server import in impala app
* fa3dcda9c7 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add CI items thoughts for Browser testing
* e23c89f132 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] List computes and use the selected one
* b020f81242 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Use the selected compute when selected in the editor
* bdca8acd17 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] List computes via the connector name
* 07b4e118a8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Cast the port of the server in HiveServer2 connector
* f34cfbdad1 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Start simplifying get_clusters
* 727ae97297 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Start using has_computes flag in API
* 6412dc2c3e [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Simplify current definition
* 6f41dff63b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Prevent kojs error on add new connector page
* 8335fe7ead [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Port the fetch_result_size API
* 03b8758e9d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Remove compute name combined to snippet type
* db39e44022 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix ids of new connector instances
* fe2b0d4824 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Update page with the new attributes like dialect
* 03e46428f5 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Remove hardcoding of snippet type in make_notebook
* 0f0c4317a3 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Refactor attributes of connector class and instance
* fcffc4ad2e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix get_sample() Snippet type impala is not configured
* a5a2ed4563 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add test_sample_data_table_sync_impala test to hs2
* 291fde7b1c [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [catalog] Refactoring for connectors and test for show_table
* 77b0f9321f [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connetors] Fix autocomplete and add mock unit test
* 8c262990ff [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Move hiverserver2 tests to connectors
* 05575ba429 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Move connector tests one level up
* 83504e7582 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [impala] Add end to end unit test to execute API connector
* 8e18eba6e0 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [impala] First end to end via connector interface only
* 529091c170 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [multi] Convert has_multi_cluster to current cluster having computes
* 0a5b24af56 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add back minimal list of contexes and start refactoring
* ebb3e75b38 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Grouping button
* 8fa0e28517 [HUE-8915](https://issues.cloudera.org/browse/HUE-8915) [frontend] Add eslilnt-plugin-jasmine to package.json
* fd53c97929 [HUE-8919](https://issues.cloudera.org/browse/HUE-8919) [editor] Fix visibility of the column filter in the asterisk expansion popover
* dd712803fa [HUE-8918](https://issues.cloudera.org/browse/HUE-8918) [autocomplete] Extract stringDistance to a separate module
* f7fbad777b [HUE-8917](https://issues.cloudera.org/browse/HUE-8917) [assist] Fix issue with missing templates in right assist
* 01d61c8a53 [HUE-8916](https://issues.cloudera.org/browse/HUE-8916) [assist] Make the language reference assist panel depend on cluster config
* ac18163f41 [HUE-8916](https://issues.cloudera.org/browse/HUE-8916) [assist] Make the functions assist panel depend on cluster config
* f77abaebf3 [HUE-8913](https://issues.cloudera.org/browse/HUE-8913) [assist] Combine ADLS, HDFS and S3 panels into one
* 5d8d2fb238 PR924 [editor] Add Vertica JDBC connector (#924)
* f7be5a24db [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [editor] Fix SQL editor list when all editors are SQL
* 0a6470e7e7 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Do not populate namespaces all the time
* b230f1290f [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Only populate computes depending on the correct type of cluster
* 390d54daaf [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Update conf to properly list connectors
* 4b43191786 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Renamed CONNECTOR_INSTANCES and preparing notebook integration
* ae19b16c6b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Replace enable flag by checking if configured
* 44a940595d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Adding default values
* dc67fde101 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Tweak dropdown style to fit on one line
* 2f0b401ab7 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Display multi cluster configs
* 3a2d368e49 Revert "[HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix tools/app_reg/app_reg.py str issue"
* 7e1a0b820f Revert "[HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize tools/app_reg for Python 3.5"
* 4e281114d9 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [core] Fix Makefile tab indentation of babelrc copy
* 32a71507cb [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [core] Add babelrc to the list of files to copy
* ab6508b15d [HUE-8890](https://issues.cloudera.org/browse/HUE-8890) [fb] Fixed test cases for compress hdfs files and Fixed compress_files utils (#917)
* de193b7ff5 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Do not fetch query result from file when using global cache
* f72c6b7863 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [task] Remove series of extra spaces
* 8654d4c83a [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [task] Catch query already expired on close tentative
* 967df969fc [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [task] Adding result storage cache service for query results
* 1cd53c868a [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [fb] Fix urllib.parse and io issue in py2
* 4ba35fa6ca [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [frontend] Fix issue with missing bundles in common_header.mako
* 6428e22eda [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Sync tools directory
* e6fafc2b93 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Sync webpack config files in refresh source step
* 249dc0d258 [HUE-8847](https://issues.cloudera.org/browse/HUE-8847) [catalog] Fix js exception when a classification has no attributes
* c09bade2ad [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Fix parser generation when cloning a parser with generateParsers.js
* 3747514e8b [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Also clone jasmine tests when generating a new parser
* cf28bc3821 [HUE-8911](https://issues.cloudera.org/browse/HUE-8911) [frontend] Upgrade jQuery to 3.4.1
* 2bad642ecb [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [tb] Create a separate table browser entry in webpack
* ae47566a37 [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [tb] Extract the Table Browser view model to a webpack modules
* 55a5b9cf2a [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [tb] Extract Table Browser entity models to webpack modules
* 8a871cec34 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Support both IP & hostname in Knox verification (part 2)
* d1fa02d17a [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/dashboard for Python 3.5
* a29410d19d [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/azure for Python 3.5
* 058fee64e0 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/aws for Python 3.5
* c7e7967a67 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Use a gif to show demo screens on README to save space
* 4ce1bd7bfb [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Move Hive config check to hive lib
* ce32754c9c [HUE-8912](https://issues.cloudera.org/browse/HUE-8912) [yarn] Avoid default config warning when there is no YARN cluster
* 970c92a8e2 [HUE-8912](https://issues.cloudera.org/browse/HUE-8912) [hdfs] Avoid default config warning when there is no HDFS cluster
* f636c8aec7 [HUE-8912](https://issues.cloudera.org/browse/HUE-8912) [hive] Hide Hive examples install if Hive is blacklisted
* a621b5d94f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/impala for Python 3.5
* b0ce261dfc [HUE-8912](https://issues.cloudera.org/browse/HUE-8912) [core] Constant URL template should support app blacklisting
* cd913670e2 [HUE-8912](https://issues.cloudera.org/browse/HUE-8912) [editor] Hide Add More link in Editor top button action when there is only one interpreter
* 01b26f530a [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/proxy for Python 3.5
* 0e79b17b45 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/sqoop for Python 3.5
* fb7d8df37a [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/zookeeper for Python 3.5
* ef0f9e1a97 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/useradmin for Python 3.5
* 5b2b62eaa2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplify contributing guidelines and move them to root
* f8e4e3794f Bump lodash from 4.17.11 to 4.17.13 (#921)
* 15397db37b [HUE-8904](https://issues.cloudera.org/browse/HUE-8904) [oozie] Fix hive operations when using http thrift
* 22d29d04be [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Support both IP & hostname in Knox verification
* c361cd38bc [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/security for Python 3.5
* 1348771c90 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/search for Python 3.5
* 69b904f28c [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/rdbms for Python 3.5
* 289c0b1dd9 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/pig for Python 3.5
* e27c8ded30 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/oozie for Python 3.5
* a7bd456556 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/metastore for Python 3.5
* ba82744e09 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/jobsub for Python 3.5
* 5b314775d4 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/jobbrowser for Python 3.5
* c36fbf3979 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [ci] Move .babelrc copy before run webpack
* 524631b492 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [frontend] Add support for any base url in the web workers
* ce2a9512aa [HUE-8909](https://issues.cloudera.org/browse/HUE-8909) [frontend] Add console.log check to eslint
* fba02ddf06 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Use the new parsers in the syntax web worker
* 1e6cfcc8f1 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Switch to using new separated autocompleters in the editor
* f7d9bc4084 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Include bundle config name when loading bundles dynamically
* 15a5906c6b [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Use dynamic import in location web worker
* e2f01be2fd [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [frontend] Add python endpoint for dynamic imports
* 02f6874fa1 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Update the makefile to support new parser generation
* 7d3fce3924 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Add option to create new parser in generateParser.js
* eb6bef9ec6 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Add sqlParserRepository for dynamic loading of SQL parsers on demand
* c18c48cb69 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Update eslintignore and fix linting issues
* a6f19f8e62 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract and fix all the tests for Impala
* fe60316ac6 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract and fix all the tests for Hive
* 230a607994 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Add the remaining jasmine tests for the generic dialect
* 117a0cd6fe [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Use a dedicated sqlParseSupport.js for each dialect
* 18fcfe5d5d [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Add new parsers to .eslintignore
* 34b68a36d5 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Add initial set of tests for the generic SQL autocompleter
* 60b9e57346 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Solve grammar conflicts and generate initial set of parsers
* bf9e633c57 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Have parser generator identify autocomplete and syntax definitions dynamically
* 5d18f6936a [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Adjust header and footer jison for extracted parsers
* f8721ba3ae [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for remaining generic statements
* 94469d720a [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for generic SELECT
* a11aa88a95 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for generic ALTER, CREATE and DROP
* 04cf3dfe49 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for Hive SELECT, SET, SHOW, UPDATE and USE
* 3b49117152 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for Hive DROP, GRANT, INSERT and LOAD
* efbfa6b0d6 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for Hive ALTER, ANALYZE and CREATE
* 614c630aa6 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for Impala SELECT, SET, SHOW, UPDATE and USE
* 1e42581e96 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for Impala DROP, LOAD, GRANT and INSERT
* 8c9108108a [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] Extract jison for Impala lexer, ALTER, ANALYZE and CREATE
* 3f9869e8a3 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [frontend] Add required npm packages for dynamic loading of JS bundles
* e843c5cc58 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [ci] Add sync copy of the latest tools directory
* 9fe0447b75 [HUE-8908](https://issues.cloudera.org/browse/HUE-8908) [fb] First commit for ABFS (backend)
* 10aca7bb47 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connectors] Step 2 is listed as step 1 in the admin wizard
* 73cda71bf2 [HUE-8887](https://issues.cloudera.org/browse/HUE-8887) [doc] Document Hive LLAP and service discovery
* c2d23a010e [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/help for Python 3.5
* 8656ce7a7f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [fb] Futurize apps/filebrowser for Python 3.5
* 26e5f7a096 [HUE-8905](https://issues.cloudera.org/browse/HUE-8905) [core] Apply HUE-8836 to Django-1.11.22 for HTTP_X_FORWARDED_HOST contains multiple hosts
* cf717de5cd [HUE-8905](https://issues.cloudera.org/browse/HUE-8905) [core] Apply HUE-8772 to Django-1.11.22 for fixing 'user is missing in mako context'
* 4010e211cc [HUE-8905](https://issues.cloudera.org/browse/HUE-8905) [core] Upgrade Django from 1.11.20 to 1.11.22
* 91af4c43b2 [HUE-8882](https://issues.cloudera.org/browse/HUE-8882) [impala] Fix invalidate delta when hive is missing (part 2)
* b930a22977 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [hbase] Futurize apps/hbase for Python 3.5
* 60b27081f1 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [beeswax] Fix itertools.ifilter object has no attribute __getitem__
* ebbca95860 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [beeswax] Futurize apps/beeswax for Python 3.5
* 068de915a3 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize apps/about/ for Python 3.5
* 36d69d250e [HUE-8906](https://issues.cloudera.org/browse/HUE-8906) [assist] Fix broken filter in the language reference panel
* f8013f036d [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Create componentUtils helper for static ko component registration
* 1adbf6d630 [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Move remaining right assist panels into webpack and drop assist.mako
* f6ab4505bb [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Move the editor context panel to a webpack module
* 179546585c [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Extract the language ref and functions panel into separate components
* 27b668175d [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Lazy load all the left assist panels
* 21c6e8aa1a [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Extract all the left assist panels to ko components
* 1e000cd3c8 [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Move the remaining assist subpanels into webpack
* 5217e21508 [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Move AssistDbPanel, AssistInnerPanel and assist specific ko bindings to webpack
* e1f765c309 [HUE-8893](https://issues.cloudera.org/browse/HUE-8893) [assist] Move HueDocument and HueFileEntry into webpack
* a1355e7a5e [HUE-8882](https://issues.cloudera.org/browse/HUE-8882) [impala] Fix invalidate delta when hive is missing.
* f9978a4c3a [HUE-8847](https://issues.cloudera.org/browse/HUE-8847) [catalog] Display classification name as tooltip when hovering over properties in the table browser
* cc2ea0e74c [HUE-8901](https://issues.cloudera.org/browse/HUE-8901) [notebook] Rename interpreter sqlalchemyapi to sql_alchemy
* de1890add5 [HUE-8901](https://issues.cloudera.org/browse/HUE-8901) [sqlalchemy] Make sure we dont have has_more True on empty results
* 2f0c2ab96c [HUE-8901](https://issues.cloudera.org/browse/HUE-8901) [sqlalchemy] Stop infinite calls when fetch_result has zero rows
* a77e6152e1 [HUE-8903](https://issues.cloudera.org/browse/HUE-8903) [catalog] Fix issue where no spinner is shown when loading databases in the table browser
* 05b7608508 [HUE-8882](https://issues.cloudera.org/browse/HUE-8882) [tb] Improve invalidate logic when refreshing missing tables in the table browser
* 6bc477be26 [HUE-8887](https://issues.cloudera.org/browse/HUE-8887) [hive] Adding LLAP Interpreter to Hue.ini and PseudoDistributed.ini.tmpl (#913)
* b8d1e165bb Update README.md
* 57e28c6c54 [HUE-8900](https://issues.cloudera.org/browse/HUE-8900) [editor] Fix date picker for variables not working
* ff4fcd3942 Fixed typo in README.md
* f737381042 [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [editor] Set the active language ref dialect based on active snippet type
* 0004200f89 [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [editor] Add information to development docs on how to generate the SQL language ref
* 70da642bd6 [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [editor] Style tables and notes in the Hive language reference
* 7c38b6f004 [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [editor] Improve the headers in the Hive language reference
* 601f5cda24 [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [editor] Fix all the links in the Hive reference manual
* 7267e3681e [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [editor] Flatten the main Hive doc tree
* 777f0ff78a [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [frontend] Add js tools folder to eslint and fix linting issues
* ad00e556b0 [HUE-8818](https://issues.cloudera.org/browse/HUE-8818) [assist] Initial Hive Language Manual for the right assist
* 832f6ae359 HUE-989 [editot] Scroll to column in result set does not update the horizontal scroll bar (#904)
* 31eab13e80 [HUE-8887](https://issues.cloudera.org/browse/HUE-8887) [llap] Use default LocMem cache for now
* 23a0136ac6 [HUE-8899](https://issues.cloudera.org/browse/HUE-8899) [hive] Test of get_query_server_config(name='llap') discovery
* efdfb709b4 [HUE-8899](https://issues.cloudera.org/browse/HUE-8899) [hive] Unit testing of get_query_server_config(name='llap')
* 49507f95d4 [HUE-8899](https://issues.cloudera.org/browse/HUE-8899) [hive] Unit testing of get_query_server_config(name='impala')
* 8213658098 [HUE-8899](https://issues.cloudera.org/browse/HUE-8899) [hive] Unit testing of get_query_server_config()
* 5ae61cc38d [HUE-8890](https://issues.cloudera.org/browse/HUE-8890) [fb] Fix compress/extract with files with spaces
* bc0586e5e4 [HUE-8892](https://issues.cloudera.org/browse/HUE-8892) [fb] Fix path when folder is deleted
* a4ed47a6b9 [HUE-8898](https://issues.cloudera.org/browse/HUE-8898) [core] Magic mock lib requires funcsigs
* 02a2782fd2 [HUE-8898](https://issues.cloudera.org/browse/HUE-8898) [core] Add magic mock lib
* e59f071e81 Add files via upload
* fc72b75a3c [HUE-8887](https://issues.cloudera.org/browse/HUE-8887) [hive] Fixes for LLAP Server/Thrift Server ports (#903)
* a4efe57c98 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix tools/app_reg/app_reg.py str issue
* d50ee7b8e2 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize tools/app_reg for Python 3.5
* 8787dd6d0c [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [oozie] Update to use common scheduler submission template
* aaa03af862 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Moving beat schedules to a submodule config
* 6ed7a4ad90 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Do not error if oozie is not present
* c6b4288cb2 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Refactored and moved Oozie submit coordinator to API
* 7aa0df52cc [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Get schedule document via generic interface
* 3ff0918ce4 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Skeleton of a schedulable SQL task
* d4b19aee98 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [task] Add a generic execute Django command task
* a8deaff734 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Refactor the scheduling API to be more abstracted
* 628e28a290 [HUE-8887](https://issues.cloudera.org/browse/HUE-8887) [hive] Updating default cache directory (#900)
* f948da7d5a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [docs] Roadmap update with Hive and Editor
* 6f0a0b4880 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [core] Remove a series of spammy debug logging traces
* 46be273007 [editor] Failed to list query history when there is some Chinese in comment (#897)
* 70d518e13d [hbase] Api error throw when search with rowkey startswith '0' (#895)
* 93a8c37071 [HUE-8887](https://issues.cloudera.org/browse/HUE-8887) [editor] Hive LLAP and Hive Service Discovery connectors (#888)
* 9c4a89e4bc [HUE-8886](https://issues.cloudera.org/browse/HUE-8886) [importer] Changing the "Has Header" checkbox should refresh the importer preview
* 09c3302384 [HUE-8885](https://issues.cloudera.org/browse/HUE-8885) [frontend] Downgrade knockout to 3.4.2
* 03edba8415 [HUE-8884](https://issues.cloudera.org/browse/HUE-8884) [editor] Prevent errors when executing multiple quick statements
* e0f5ea395b [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [fb] Fix encoding compress / extract
* d06f8b3806 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Remove double encoding onsuccessurl
* 11734c6949 [HUE-8883](https://issues.cloudera.org/browse/HUE-8883) [docs] Update the requirements and headers troubleshoot for MacOS (#890)
* 52d99e281c [HUE-8878](https://issues.cloudera.org/browse/HUE-8878) [oozie] Fix Hive Document Action variable with prefilled value
* 24af246126 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Add link to new help forum
* 970ac95415 [HUE-8881](https://issues.cloudera.org/browse/HUE-8881) [search] Solr examples cannot be loaded back
* 29ec0be728 [HUE-8879](https://issues.cloudera.org/browse/HUE-8879) [core] Fix ldaptest not allow space in user_filter
* d78228d93c [HUE-8880](https://issues.cloudera.org/browse/HUE-8880) [oozie] Fix KeyError when execute coordinator
* 692f13e3ce [HUE-8873](https://issues.cloudera.org/browse/HUE-8873) [jobbrowser] Fix selectedJobs undefined JS error causes workflow never update to complete state
* a57ffd4073 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Update knox dispatch for Ha
* 0fbc5e54cf [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Add Atlas, CI, Knox to the done Roadmap items
* fed973d101 [HUE-8877](https://issues.cloudera.org/browse/HUE-8877) [jb] Remove yarn dependency - Hide oozie
* d0b724dab8 [HUE-8877](https://issues.cloudera.org/browse/HUE-8877) [jb] Remove yarn dependency
* f4e3d2fc29 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Add LDAP Troubleshooting
* 9ebc86afa7 [HUE-8863](https://issues.cloudera.org/browse/HUE-8863) [catalog] Avoid UnboundLocalError: local variable 'data' referenced before assignment
* c0473eb287 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add cancel button to create connector section
* 7ee0463198 [HUE-8875](https://issues.cloudera.org/browse/HUE-8875) [indexer] /hue/indexer/indexes is not found
* e357c4a652 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [fb] Remove double encoding opening file from assist
* 750d70e23d [HUE-8876](https://issues.cloudera.org/browse/HUE-8876) [core] Fix redirect for is_embeddable when 401
* bc3c7a44d6 Revert "[HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix tools/app_reg/app_reg.py str issue"
* dbe2aeba9d Revert "[HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize tools/app_reg for Python 3.5"
* 64854673cf [docs] Remove Jobsub and Beeswax names (#885)
* bf11b2d7eb [HUE-8874](https://issues.cloudera.org/browse/HUE-8874) [security] Privilege checker is not cachable anymore
* 0d73b2a38f [HUE-8855](https://issues.cloudera.org/browse/HUE-8855) [ci] Adding linting of js files
* ecfde999df [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix tools/app_reg/app_reg.py str issue
* 49465bf419 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize tools/app_reg for Python 3.5
* 24090d309f [HUE-8872](https://issues.cloudera.org/browse/HUE-8872) [editor] Show correct column count in the result column selector
* c7fea1b362 [HUE-8871](https://issues.cloudera.org/browse/HUE-8871) [frontend] Search with "tag" facet should work with navigator
* 16e954c4f7 [HUE-8870](https://issues.cloudera.org/browse/HUE-8870) [frontend] Fix chart update timing issue
* 5c2f6e957d [HUE-8869](https://issues.cloudera.org/browse/HUE-8869) [frontend] Improve the editor icon
* a675430526 [HUE-8873](https://issues.cloudera.org/browse/HUE-8873) [jobbrowser] Auto refresh deselects your selection for rerun workflows and schedulers if job is running (#882)
* 90c5b7485f [HUE-8868](https://issues.cloudera.org/browse/HUE-8868) [search] Fix TestLibSolrWithSolr
* bdb5029248 [HUE-8829](https://issues.cloudera.org/browse/HUE-8829) [core] Fix TestLoginWithHadoop
* c7af756ee9 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Fix TestFileBrowserWithHadoop
* 0ec36852e5 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [fb] ensure_home_directory for Knox
* eba720107f [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [fb] Fix go to Home
* d9f22fcd8c [HUE-8867](https://issues.cloudera.org/browse/HUE-8867) [metastore] Expanding columns of a table in left assist fails
* 5ce208777e [HUE-8866](https://issues.cloudera.org/browse/HUE-8866) [build] Support static files for both building dev and releases
* 175a2c7cc0 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Add CSRF_TRUSTED_ORIGINS for Knox
* 9e919798be [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [dashboard] Avoid missing collection in a saved dashboard
* cdc62bd7eb [HUE-8860](https://issues.cloudera.org/browse/HUE-8860) [beeswax] Truncate column size to 5000 if too large
* eb1c0821a1 Merge branch 'ci-commit-master-hue8863' of https://github.com/cloudera/hue into ci-commit-master-hue8863
* 7a9c65ae6d [HUE-8863](https://issues.cloudera.org/browse/HUE-8863) [catalog] search by owner returns hive tables only instead of db/table/columns
* 71f8a06327 [HUE-8862](https://issues.cloudera.org/browse/HUE-8862) [ci] Remove currently not used requirement file
* 16ad3fad59 [HUE-8863](https://issues.cloudera.org/browse/HUE-8863) [catalog] search by owner returns hive tables only instead of db/table/columns
* f0f3902d15 [HUE-8865](https://issues.cloudera.org/browse/HUE-8865) [ci] Provide auto push to master when tests pass
* d9c9a06d0a [HUE-8862](https://issues.cloudera.org/browse/HUE-8862) [test] Add js testing to CI
* 5b2f8134f6 [HUE-8864](https://issues.cloudera.org/browse/HUE-8864) [search] Fix broken layout when loading a saved dashboard
* f3433497e3 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [frontend] Fix broken jasmine tests
* 7a4d153274 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [ui] Avoid false positive of 'you are accessing an older version of Hue'
* e157c21f36 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [search] Fix /dashboard/new_search
* 35f2443a1a [HUE-8848](https://issues.cloudera.org/browse/HUE-8848) [catalog] Add support for "owner" faceted search
* 128748b6c9 [HUE-8848](https://issues.cloudera.org/browse/HUE-8848) [catalog] Add support for whitespace in classification search for Atlas
* 12ddf8d4df [HUE-8848](https://issues.cloudera.org/browse/HUE-8848) [catalog] Use attribute criterion instead of free text search for Atlas
* ea1dff1a8e [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [importer] Fix submit database redirect source_type
* 058e5ed135 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Fix simplePost with no options.
* b621aa99de [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [editor] Add knox service definition.
* f3fc957bfe [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Add ProxyMiddleware for user.name GET param
* c77204bf1c [HUE-8859](https://issues.cloudera.org/browse/HUE-8859) [build] Add removeNPMAbsolutePaths utility to clean package.json
* 31142bef21 [HUE-8859](https://issues.cloudera.org/browse/HUE-8859) [build] Add to prod target webpack configs to allow packaging later
* 22a4b622d6 [HUE-8859](https://issues.cloudera.org/browse/HUE-8859) [build] Copy webpack config files to enable the packaging steps later
* d02506b1f3 [HUE-8859](https://issues.cloudera.org/browse/HUE-8859) [build] Add local path to webpack generated stats files
* 0925f65a39 [HUE-8855](https://issues.cloudera.org/browse/HUE-8855) [catalog] Add optional search_cluster config for catalog to limit results to a specific cluster
* 56a99251ba [HUE-8837](https://issues.cloudera.org/browse/HUE-8837) [catalog] Fix error when Atlas can't find any entities
* 18bed68bd2 [catalog] [HUE-8857](https://issues.cloudera.org/browse/HUE-8857) return accurate owner from atlas entity
* 6bb5432308 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Refactoring of the heml chart to offer any ini properties
* ce7262bdea [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [docker] Basic Nginx docker image to serve files and proxy api
* a7f9734757 [HUE-8829](https://issues.cloudera.org/browse/HUE-8829) [core] Fix redirect stops at /hue/accounts/login
* 1a1ecd4b79 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Update badges to include docker in main README
* abf5a0418b [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Ignore generated to in git
* 582ceec08b [k8s] Path typo in helm path for Hue
* 90c25c3b2a [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [impala] Do not error on show logs when Job Browser is disabled
* ae298ca240 [HUE-8848](https://issues.cloudera.org/browse/HUE-8848) [catalog] Enable faceted classification search for Atlas
* e3a55f7f20 [HUE-8848](https://issues.cloudera.org/browse/HUE-8848) [catalog] Switch to basic atlas API endpoint to include wildcard classification search
* af8686c801 [HUE-8848](https://issues.cloudera.org/browse/HUE-8848) [catalog] Implement search/entities API endpoint for Atlas
* ab538ea45f [HUE-8842](https://issues.cloudera.org/browse/HUE-8842) [editor] The sparksql option should be available in the spark permission (#869)
* 6bb46b5309 [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [docs] Prepare move to dedicated doc website
* 4a61429b03 [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [doc] Fix link to helm chart folder
* 034aeedec2 Revert "[HUE-8829](https://issues.cloudera.org/browse/HUE-8829) [core] Fix redirect stops at /hue/accounts/login"
* 71041937c7 [HUE-8829](https://issues.cloudera.org/browse/HUE-8829) [core] Fix redirect stops at /hue/accounts/login
* 6abe51acbb [HUE-8837](https://issues.cloudera.org/browse/HUE-8837) [catalog] Add get_databas,get_table, get_field for atlas to enable find_entity
* c2b581275e [HUE-8847](https://issues.cloudera.org/browse/HUE-8847) [catalog] Enable type faceted search in top search for Atlas
* dc6b419f84 [HUE-8847](https://issues.cloudera.org/browse/HUE-8847) [catalog] Disable tags search for Atlas
* 64f43d9eca [HUE-8847](https://issues.cloudera.org/browse/HUE-8847) [catalog] Use classifications as tags when Atlas is enabled
* 3352c2bed2 [HUE-8847](https://issues.cloudera.org/browse/HUE-8847) [catalog] Improve Atlas table search
* 193d20043e [HUE-8847](https://issues.cloudera.org/browse/HUE-8847) [catalog] Implement entities_interactive for Atlas and add entity adaption
* c9e961baee [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [catalog] Fix URL param when switching between source_type
* eb6987985b [HUE-8839](https://issues.cloudera.org/browse/HUE-8839) [core] Move collectstatic to its own target
* 7b23ee56cc [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Disable Javascript lint and test for now
* 016112c924 Revert "PR865 [aws] change exception error to AssertionError and modify regex (#865)"
* 9270d00de4 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Fix environment of last non standard unit tests
* 17e3c31cce [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Adding build status to the top README
* e85e1fda2b [HUE-8782](https://issues.cloudera.org/browse/HUE-8782) [hbase] Add back decorator to Thrift calls to set the doAs header
* c8318171f0 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [doc] v1 with js, Python unit tests and js lint
* edbae28030 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Add doc site building
* 4e73a5ceec [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Adding linting in for js
* 53bc4675f6 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Update circleci to run both unit tests for js and python
* 33ce4ff6dc [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Add auth test requiring Hadoop to integration
* 5013826ad2 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Remove old make js test target
* ee806e500c [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Set more LDAP, FS tests as integration tests
* dfd88119fd [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Tag oozie create workflow test as integration
* 2d514ffd2e [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Tag notebook test exporting data to a file as integration
* 0feea2f4c5 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Properly configuring solr tests
* 58458a1c80 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Tag series of metadata inegration tests
* 789870a0a3 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Set optimizer API test as integration test
* 1c8962e753 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Add integration flag to current tests requiring Hadoop
* 9126654519 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Tweak to run Hue from the docker image
* 0c416a9384 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Update design proposal
* 51193ab010 [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Adding custom image of precompiled dependencies
* 426a7cc04f [HUE-8846](https://issues.cloudera.org/browse/HUE-8846) [ci] Skeleton of circleci
* 5ac24678b1 [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [importer] Fix submit redirect source_type
* 3911e37ea2 [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [catalog] Fix import to non hive tables
* 6fcc56f7b7 [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [catalog] Fix change database description
* ccc0b2318f [HUE-8841](https://issues.cloudera.org/browse/HUE-8841) [metadata] Add read-only mode for descriptions
* 4c719c43b5 [HUE-8841](https://issues.cloudera.org/browse/HUE-8841) [metadata] Add read-only mode to properties
* c66259f8d4 [HUE-8841](https://issues.cloudera.org/browse/HUE-8841) [metadata] Only show tags when Navigator is configured
* b5e9bd6371 [HUE-8841](https://issues.cloudera.org/browse/HUE-8841) [frontend] Rename HAS_NAVIGATOR to HAS_CATALOG
* 26eee97bdb PR865 [aws] change exception error to AssertionError and modify regex (#865)
* fd5cbb9edf [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [core] Fix empty catalog list in table browser.
* 77557b05ee [HUE-8839](https://issues.cloudera.org/browse/HUE-8839) [docker] Remove temporary redundant recompiling of webpack
* 3e36e75bb3 [HUE-8839](https://issues.cloudera.org/browse/HUE-8839) [core] Integrate npm builds into the makefiles
* ef769fb93e [HUE-8727](https://issues.cloudera.org/browse/HUE-8727) [frontend] Fix return of chrome autofill username in search inputs
* 3359c5a5bc [HUE-8831](https://issues.cloudera.org/browse/HUE-8831) [search] Support all SQL dialects in the dashboard autocomplete
* eab1070643 [HUE-8830](https://issues.cloudera.org/browse/HUE-8830) [search] Fix js exception from right assist in the dashboard
* 53fdf1e1f0 Revert "[HUE-8835](https://issues.cloudera.org/browse/HUE-8835) [core] Minor fixes to cm-managed"
* beae190188 Revert "[HUE-8835](https://issues.cloudera.org/browse/HUE-8835) [core] Avoid breaking runserver when no HUE_CONF_DIR set"
* 814e57b365 [HUE-8836](https://issues.cloudera.org/browse/HUE-8836) [core] request.get_host() is broken when HTTP_X_FORWARDED_HOST contains multiple hosts
* ecff05e44d [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [core] Integrate with Apache Knox
* a6c52bf62b [HUE-8835](https://issues.cloudera.org/browse/HUE-8835) [core] Avoid breaking runserver when no HUE_CONF_DIR set
* 10e629bf6f [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Split objects into individual yaml files
* ca84b660a2 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Big clean-up and restructure of the config files
* ac44c7b869 [HUE-8835](https://issues.cloudera.org/browse/HUE-8835) [core] Minor fixes to cm-managed
* 72e5733c3a [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [editor] Improve Postgres SqlAlchemy integration
* a3fc8145de [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Limit default interpreters
* e05ac6c41a [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [docker] Change config to allow updating the interpreter list
* 675a356d4e [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [core] Do not configure all the interpreters to be on
* 4d5cb316c5 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Provide the config for the out of the box postgres DB
* 93e3e51542 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Clean-up bunch of typos in the configs
* d02022285c [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [k8s] Fix indentation in Hue configmap
* fa869d074c [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [k8s] Adding skeletons of YAML configs for multiple services
* fa3478c820 [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [k8s] Adding redis yaml configs
* 425773e831 [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [k8s] Split Hue yaml into different files
* 7fe6a9640b [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Help when seeing user home dir missing in editor
* 596951834c [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Instruction update for releasing doc changes
* 64ffc262c0 [HUE-8832](https://issues.cloudera.org/browse/HUE-8832) [doc] Clarify SparkSql configuration
* 43fb3c0954 [HUE-8834](https://issues.cloudera.org/browse/HUE-8834) [docker] Improve instructions for getting started with compose
* 0e7c2f6401 [core] Fixing 500 server error when listing admin configs (#862)
* 56099d1e1d [[HUE-5128](https://issues.cloudera.org/browse/HUE-5128)] [sqoop] Allows job creation and updates (#547)
* 95de9514c0 [HUE-8834](https://issues.cloudera.org/browse/HUE-8834) [docker] Refactor the ini to simplify the configurations
* 29008bf1eb [HUE-8834](https://issues.cloudera.org/browse/HUE-8834) [docker] Persist database volumne
* 2b37413fc0 [HUE-8834](https://issues.cloudera.org/browse/HUE-8834) [docker] Docker compose update to boot natively with MySql
* d439df8c11 [HUE-8832](https://issues.cloudera.org/browse/HUE-8832) [spark] Support SparkSql in Livy
* 970ae9ca70 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Rename the server configuration options to be simpler
* 9c413367e6 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] More explicit task server result configuration
* 45d7001ab9 [HUE-8833](https://issues.cloudera.org/browse/HUE-8833): [editor] Error - hidden popup menu in the presentation section
* e7c7c55624 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [docker] Temp fix until npm-install can use PREFIX
* b03adf2d37 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Simplify some of the README, user and admin content
* 271a04d43c [HUE-8823](https://issues.cloudera.org/browse/HUE-8823) [fs] Allow to start without an HDFS cluster
* 4a22d47efc [HUE-8743](https://issues.cloudera.org/browse/HUE-8743) [docker] Small docker README typo fixes
* 31b1803404 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Add more configuration content and prepare new TOC
* cd48fa139b [HUE-8820](https://issues.cloudera.org/browse/HUE-8820) [stats] Adding number of queries in past 30 days
* ab31b404cf [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [doc] Beginning description of the SQL task
* 17be465110 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [design] Fix typos in CI-CD proposal
* ffb9cd9c07 [HUE-8828](https://issues.cloudera.org/browse/HUE-8828) [editor] Fix notebook user's searching not displaying
* a0692149d0 [HUE-8827](https://issues.cloudera.org/browse/HUE-8827) [docs] Update presto website links
* f30d3557b0 [HUE-8826](https://issues.cloudera.org/browse/HUE-8826): [frontend] Can't close log block on services page
* 68aff4f48c [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [hms] Update interpreter list properties in test
* c5b5b41b09 [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [notebook] Update test to support hive permission
* ea3ecf0176 Revert "[HUE-8825](https://issues.cloudera.org/browse/HUE-8825) [oozie] Fix unit test oozie.models2_tests:TestEditor.test_share_workflow"
* 8abf9f17c6 [HUE-8825](https://issues.cloudera.org/browse/HUE-8825) [oozie] Fix unit test oozie.models2_tests:TestEditor.test_share_workflow
* 3d0447c86d [HUE-8822](https://issues.cloudera.org/browse/HUE-8822) [core] Fix other LDAP unit tests
* a64ddfc72c [HUE-8821](https://issues.cloudera.org/browse/HUE-8821) [core] Fix Hue LDAP StartTLS implementation
* 45fbdc24c8 [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [metastore] Display database, table, column via HMS only
* 5b45bfe163 [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [metastore] Add more empty properties to the describe table
* 2f0f7e9ded [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Prepare getting connector type via its name
* 3ed152f7b6 [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [metastore] Implement listing detailed tables of a table
* cee9a1fdcd [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [metastore] Implement listing detailed tables of a database
* e04b71483c [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [notebook] Integrate Hive Metastore connector
* 4afcdb82a9 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [catalog] Adding the Catalog/Browser category
* 8275063eb0 [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [metastore] Preparing browsing tables via HMS only
* 141b69dbdd [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [core] Fix download test.
* a5a9ea08ae [HUE-8822](https://issues.cloudera.org/browse/HUE-8822) [core] Fix unit test TestLdapLogin.test_login_home_creation_failure
* 11d077eb30 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Simplify title of LDAP import sections
* cc8edd376a [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] Fix jdbc / sqlalchemy describe db.
* cda4774b52 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Less aggressive log fetching.
* 28bf38fead [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [doc] Add celery --cm-managed command to doc
* 9069b3ad8a [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix test_export_csv.export_csvxls
* 94bf7dc0e0 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix sql_utils_test.test_split_statements
* 99fc7b2142 [HUE-8745](https://issues.cloudera.org/browse/HUE-8745) [editor] Support AWS Athena using JDBC Driver
* fc4906dc79 [HUE-3228](https://issues.cloudera.org/browse/HUE-3228) [dashboard] Also list SqlAlchemy connectors
* 05a91bde27 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Refresh and simplify the contribution guidelines
* 41e99f5c58 [HUE-8820](https://issues.cloudera.org/browse/HUE-8820) [analytics] Cleaning-up skeleton of Admin analytics page
* d44ddd9ea4 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Update the roadmap and split out done items
* d5265e4fc7 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix download test.
* 8cc274c30b [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [design] Iterate on better continuous testing
* 4ad2d021c6 [HUE-8821](https://issues.cloudera.org/browse/HUE-8821) [core] Fix Hue LDAP StartTLS implementation
* b69d2076dd [HUE-8111](https://issues.cloudera.org/browse/HUE-8111) [core] Update Jenkins snapshot URLs to 5.17.0
* 6ba6591397 [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [hive] Add hive permission in the HiveServer2 tests
* 7d8596a135 [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [hive] Update app permission test with the new hive app
* 403191c8d5 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [kubernetes] Add basic Hue YAML configuration
* d0dfd13766 [HUE-8820](https://issues.cloudera.org/browse/HUE-8820) [stats] Adding daily query stats
* 7d090998aa [HUE-8820](https://issues.cloudera.org/browse/HUE-8820) [analytics] Add skeleton of analytics page
* 84a7f3fa63 [HUE-8819](https://issues.cloudera.org/browse/HUE-8819) [assist] Show the right assistant for all SQL type editors
* 4dc4575d99 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Move task to django storage.
* 923e3c1622 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [kubernetes] Tweak the doc to remove typo in microk8s install
* 553728e141 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docker] Update instructions about pointing to a local database
* 6cea9c74d7 [HUE-8817](https://issues.cloudera.org/browse/HUE-8817) [core] Improve get_ordered_interpreters performance
* 3eed52bc11 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Improve performance of ApiWrapper
* 732f3d25ca [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [stats] Also add the number of login sessions
* a2203ac610 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix result count off by one.
* 2143067f2f [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Move fetch progress to django cache
* 9e3c523088 [HUE-8816](https://issues.cloudera.org/browse/HUE-8816) [notebook] Do not break on describing columns in catalog
* c02f50d41b [HUE-8816](https://issues.cloudera.org/browse/HUE-8816) [catalog] Support parsing columns with varchar type
* 495c216877 [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [catalog] Avoid erroring on Navigator config property
* 391d90c8f9 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docker] Upgrade image OS to Ubuntu 18.04
* b0711c7c5a [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [tools] Add initial NGINX configuration
* 8b813bf3a7 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Add design directory with initial CI/CD
* 0552257a34 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [doc] Add reference to roadmap
* 2777756f46 [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [doc] Add post release task to update release date on wikipedia
* 64d56a82b5 [HUE-7712](https://issues.cloudera.org/browse/HUE-7712): [spark] Livy-batch not available in HUE
* 47ab44a793 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [doc] Improve the scheduler server description
* e4cb78427b [HUE-8805](https://issues.cloudera.org/browse/HUE-8805) [editor] Fix typo in Notebook stats
* 9f064b7ce4 [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [core] Bump Java version restriction
* da453ddf8f [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [doc] Update dependencies install instructions for Ubuntu 18.04
* 955764de36 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] drop_privilege for tasks.
* 79c1033d2e [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix support oozie jobs for tasks.
* 01c7f18191 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Add auto reload to celery
* c617453173 [HUE-8805](https://issues.cloudera.org/browse/HUE-8805) [notebook] Add query execution counts of shared queries
* ef35ea2834 [HUE-8805](https://issues.cloudera.org/browse/HUE-8805) [notebook] Single query number of execution and copies
* e705ddccdf [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [ui] Update series of links to not use sharp as url
* ce64b815ce [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Avoid page refresh when clicking on caret actions
* 432157ae92 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Do not show task error in log.
* d34e0d9e50 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Support oozie jobs for tasks.
* f11007c58f [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Handle empty result sets in tasks.
* 80c4bf105d [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Increase csv field size limit
* 029e7faa4e [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix task run as batch.
* 378a07af86 [HUE-8814](https://issues.cloudera.org/browse/HUE-8814) [backend] Allow OIDC username attribute to be customizable
* 69c9d926f7 [HUE-8813](https://issues.cloudera.org/browse/HUE-8813): [hbase] HBase examples are not installed on secure cluster
* 3faaea2788 [HUE-8798](https://issues.cloudera.org/browse/HUE-8798) [core] Graceful fail when locate_java process returned nothing
* 01beaefcb1 [HUE-8805](https://issues.cloudera.org/browse/HUE-8805) [core] Add cluster prefix to email subject prefix
* 0074b6a4e4 Revert "[HUE-8803](https://issues.cloudera.org/browse/HUE-8803) [frontend] Bundle common third party css into hue.css"
* ccb0f61beb [HUE-8812](https://issues.cloudera.org/browse/HUE-8812) [autocomplete] Add support for Hive CREATE TRANSACTIONAL TABLE
* bd3a7e34e1 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Temporarily disable executor tests for notebook 2
* d430480e1f [HUE-8812](https://issues.cloudera.org/browse/HUE-8812) [autocomplete] Update Hive reserved words
* 5f9cc452c1 [HUE-8812](https://issues.cloudera.org/browse/HUE-8812) [autocomplete] Add support for Hive tables stored as JSONFILE
* 7519281e00 [HUE-8811](https://issues.cloudera.org/browse/HUE-8811) [tb] Don't show Hive views as tables in the table browser
* 801e0e3b1e [HUE-8810](https://issues.cloudera.org/browse/HUE-8810) [tb] Fix js exception when refreshing tables in the table browser
* 9724236bbb [HUE-8809](https://issues.cloudera.org/browse/HUE-8809) [fb] Fix js exception when dropping a file in the file browser
* 0e77031113 [HUE-8808](https://issues.cloudera.org/browse/HUE-8808) [assist] Fix js exception from show in assist action
* 04f0c4f071 [HUE-8807](https://issues.cloudera.org/browse/HUE-8807) [frontend] Upgrade Knockout to 3.5
* 7836fd80cc [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [hive] Do not show the Hive app as another app
* d24364c600 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Support task multi statement execution
* 50ed002157 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix missing import for base connector
* c76ebae826 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix task user id passing.
* c08e4d01dd [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Add celery to managed_entry
* c2f2a38ffe [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Refactor to combine both saved and available connectors templates
* 0b900c0ba2 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Make top filters and search fixed
* b3e9a6dc7b [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Implement status and progress update logic in notebook 2
* 01acf59c02 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Add result size to notebook 2
* 13518086cb [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Switch to backend execution status for notebook 2
* f38759be48 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Include sessions when executing in notebook 2
* dba7b55a78 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Remove task user id logging.
* d6f9657d76 [HUE-8806](https://issues.cloudera.org/browse/HUE-8806) [editor] R session for R Editor in Hue cannot start (#841)
* d30c535d4a [HUE-8805](https://issues.cloudera.org/browse/HUE-8805) [config] Dev settings for getting emailing to print on the console by default
* 4eb981e32a [HUE-8803](https://issues.cloudera.org/browse/HUE-8803) [frontend] Bundle common third party css into hue.css
* faae2521aa [HUE-8802](https://issues.cloudera.org/browse/HUE-8802) [assist] Fix js exception on assist index refresh
* bc2241f014 [HUE-8792](https://issues.cloudera.org/browse/HUE-8792): [notebook] Error while share documents(user can save document with only read permissions)
* 25ce120af8 [HUE-8805](https://issues.cloudera.org/browse/HUE-8805) [sql] Add basic Query Analytics reporting
* 05bb363af4 [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [docs] Fixing bunch of internal links
* 40f65ca22d [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [docs] Do not show main documentation title in the right TOC
* 92b228217a [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [hive] Hive interpreter can be disabled by blacklisting the hive app
* 03acd22966 [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [ui] Package-lock small update
* a86c83355a [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [hive] Add an Hive app to allow disabling Hive but not other connectors
* ae3033de57 PR-840 Modifying documentation around hbase thrift https/http
* b68e96ff90 [HUE-8804](https://issues.cloudera.org/browse/HUE-8804): [filebrowser] Can't save file after use 'Save as' button
* 4d0fcf6375 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Switch to showing the results from the executor in notebook 2
* baf91bf2f5 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Implement the execute and check status functionality for notebook 2
* eb4331dfa2 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Add initial version executor and executableStatement for notebook 2
* 4cd4f696c8 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Improve notebook and view model structure for notebook 2
* dac20a2c2c [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Clean up the snippet model to prepare for notebook 2
* 93b3764704 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Add a feature flag for notebook2
* daab25929c [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [docs] Fix content size for right hand side toc.
* cd2b04f6fe [HUE-8801](https://issues.cloudera.org/browse/HUE-8801) [dashboard] Fix symlink to point to the proper version
* ec04a50637 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connectors] Add link to config page and documentation
* a323b4ae39 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connectors] Properly load the full list
* 35c756b6e3 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [quickstart] Add connector setup step
* 72ab357008 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [config] Hook-in connectors to the cluster config
* c0671d615c [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connectors] Refactor to properly list installed and configured connectors
* 85d6ffb856 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connector] APIs to update connectors
* 632ac45562 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connector] APIs to update and delete connectors
* 9954730087 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connector] Move category listing to the left side
* 1a419d73db [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connectors] Adding skeleton of Hive connector
* bb7559bc7a [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [connectors] Add Edit connector instance page
* 47f941ad99 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [clusters] Preparing instances of Connector page
* 9ac286cd89 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [clusters] Add initial Connectors page
* 9e89a65b62 [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [docs] Add padding for toc on right hand side.
* acc4a82e05 [HUE-8800](https://issues.cloudera.org/browse/HUE-8800) [docs] Move toc to right hand side.
* c114f275c8 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] sqlalchemy add basic support for table browser.
* 03af72ffc5 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix download arguments for task.
* 79dfa617e6 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [docs] Update contributing link
* e84f657283 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] Fix sqlalchemy left assist.
* bc1fc228e4 [HUE-8799](https://issues.cloudera.org/browse/HUE-8799): [metastore] Сannot create a table in a newly created database
* dc67dc6ad4 [HUE-8797](https://issues.cloudera.org/browse/HUE-8797) [autocomplete] Remove deprecated AES functions from the Hive UDF Lib
* b370314c66 [HUE-8795](https://issues.cloudera.org/browse/HUE-8795) [frontend] Fix user autocomplete width and height in the sharing modal
* d7f9a158f0 [HUE-8794](https://issues.cloudera.org/browse/HUE-8794) [frontend] Prevent babel from trying to compact the parsers
* 16ff40072e [HUE-8793](https://issues.cloudera.org/browse/HUE-8793) [autocomplete] Add support for quoted column and table aliases
* c65ad90614 PR836 [docker] Add saml dependencies (#836)
* d39dd642ba [HUE-8796](https://issues.cloudera.org/browse/HUE-8796) [hive] Remove in place handle guid base64 conversion
* 7fc948ac30 Fixes download() got an unexpected keyword argument 'file_format'
* a7aa8c0a66 Revert "[HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] Add create_session to sqlalchemy & cache engine."
* df31a484b4 [HUE-8788](https://issues.cloudera.org/browse/HUE-8788) [fb] Disable fb download redirect by default.
* 739d4f6a24 [HUE-8788](https://issues.cloudera.org/browse/HUE-8788) [fb] Fix security error with webhdfs redirect
* d523248427 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] Add create_session to sqlalchemy & cache engine.
* ca2ea6c5e3 Implement download for jdbc notebook connector
* 66e56e529e [HUE-8791](https://issues.cloudera.org/browse/HUE-8791) [admin] Avoid truncating right border of bottom form
* 999a118f3d [HUE-8791](https://issues.cloudera.org/browse/HUE-8791) [admin] Consistent header styling of Configuration tab
* 407436fcae [HUE-8791](https://issues.cloudera.org/browse/HUE-8791) [core] Simplify a bit the user menu
* 83fc8f59d2 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [doc] Adding missing jiras to the roadmap
* 404d391ad6 [HUE-8789](https://issues.cloudera.org/browse/HUE-8789) [jobbrowser] Can't kill job in mini job browser (#830)
* e83788547e [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [catalog] Basic Atlas search with text query working
* bb1d99b5a3 [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [catalog] Filling-up entity search attributes
* c03fe20455 [HUE-8784](https://issues.cloudera.org/browse/HUE-8784) [metadata] Fix refresh at root level of table browser.
* c613080c58 [HUE-8785](https://issues.cloudera.org/browse/HUE-8785) [editor] Show the interpreter type instead of just "SQL" in the editor header
* 49db0ab1bc [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] Enable sqlalchemy result streaming
* c8b5de5cc5 [HUE-8777](https://issues.cloudera.org/browse/HUE-8777) [jb] Improve diagnostics display on yarnv2 jobs
* 45dc9b3fd7 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] Fix create engine when credentials are provided.
* fb56110de3 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix download arguments for task.
* 8f33fde8cd [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Fix task invalid query handle.
* 737535205e [HUE-8782](https://issues.cloudera.org/browse/HUE-8782) [hbase] Support Python 3 in Thrift bindings
* 10caef2ef4 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [docker] Remove workaround for webpack stats file inclusion
* 3f1913844d [HUE-8769](https://issues.cloudera.org/browse/HUE-8769) [docs] Release Docker instructions are not styled
* 3517b519dc [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [docs] Check Webpack integration roadmap item
* 83f43641bc PR826 [hdfs] Tweak imports to just use the variable name
* 87ccf2e09e PR826 [hdfs] Adding HTTPS options for WebHDFS (#826)
* f420009547 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [core] Include the webpack stats files in the build output
* d0c74976b9 [HUE-8772](https://issues.cloudera.org/browse/HUE-8772) [core] Webworkers are failing to start
* 5334ab22a1 [HUE-8776](https://issues.cloudera.org/browse/HUE-8776) [jobbrowser] No redirect after changing url in command line in job browser (#825)
* 407717da72 [HUE-8781](https://issues.cloudera.org/browse/HUE-8781) [assist] Can't close context menu (#827)
* 349ad64905 [HUE-8771](https://issues.cloudera.org/browse/HUE-8771) [jobbrowser] Can't reload job in mini job browser (#824)
* e4ebeb7f91 [HUE-8775](https://issues.cloudera.org/browse/HUE-8775) [editor] Workaround to make interface optional until new catalog commit
* 39f055c162 [HUE-8775](https://issues.cloudera.org/browse/HUE-8775) [notebook] Link HMS connector to autocomplete view
* 888a0897ed [HUE-8775](https://issues.cloudera.org/browse/HUE-8775) [hive] Regenerate Thrift with older Hive 2 than upstream master
* f91ccffdb5 [HUE-8775](https://issues.cloudera.org/browse/HUE-8775) [notebook] Add HMS connector implementation
* c3f9fbc90d [HUE-8775](https://issues.cloudera.org/browse/HUE-8775) [hive] Add back interface to talk to Hive Metastore
* 888a3046cd [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Download query result as task
* 0ffcd8dd97 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix ko.foreachvisible endIndex.
* a66d30e129 [HUE-8747](https://issues.cloudera.org/browse/HUE-8747) [editor] Download query result as task
* d5e23e3378 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Move scroll to top button a bit to the right
* 865b51ec76 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [docs] Describe more how to use the sql connectors
* 76e3c87560 [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [metadata] Adding an Atlas implementation of the Catalog Api
* 4c311ed918 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [docs] Document username prompting feature
* 97b42ae9b1 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sql] Add prompt for credentials to MySQL
* c74b43ca04 [HUE-8769](https://issues.cloudera.org/browse/HUE-8769) [doc] Prevent Javascript error when visiting the 4.0 release notes
* 0fd2fb317f [HUE-8769](https://issues.cloudera.org/browse/HUE-8769) [docs] Add more instruction on how to do a release
* f3d39024b3 [HUE-8769](https://issues.cloudera.org/browse/HUE-8769) [core] Set version numbers to 4.4
* 9211afef0c [HUE-8767](https://issues.cloudera.org/browse/HUE-8767) [editor] Fix icon alignment in the query type drop down
* 40747e3583 [HUE-8769](https://issues.cloudera.org/browse/HUE-8769) [core] Perform 4.4 release


Contributors
------------

This Hue release is made possible thanks to the contribution from:

* Aaron Newton
* Aaron Peddle
* Aaron T. Myers
* abec
* Abraham Elmahrek
* Aditya Acharya
* Adrian Yavorskyy
* aig
* airokey
* Alex Breshears
* Alex Newman
* Alex (posi) Newman
* alheio
* alphaskade
* Ambreen Kazi
* Amit Kabra
* Andrei Savu
* Andrew Bayer
* Andrew Yao
* Andy Braslavskiy
* Ann McCown
* antbell
* Antonio Bellezza
* arahuja
* Ashu Pachauri
* Atupal
* Avindra Goolcharan
* bcwalrus
* bc Wong
* Ben Bishop
* Ben Gooley
* Ben White
* Bhargava Kalathuru
* Bruce Mitchener
* Bruno Mahé
* bschell
* bwang
* cconner
* Chris Conner
* Chris Stephens
* Christopher Conner
* Christopher McConnell
* Christopherwq Conner
* cmconner156
* Craig Minihan
* cwalet
* Daehan Kim
* dbeech
* denniszag
* dependabot[bot]
* Derek Chen-Becker
* Diego Sevilla Ruiz
* Dominik Gehl
* Eli Collins
* Enrico Berti
* Erick Tryzelaar
* Ewan Higgs
* fatherfox
* gdgt
* Gilad Wolff
* grundprinzip
* Grzegorz Kokosiński
* Guido Serra
* happywind
* Harsh
* Harsh J
* Hector Acosta
* Henry Robinson
* hueadmin
* Igor Wiedler
* ihacku
* Ilkka Turunen
* Istvan
* Ivan Dzikovsky
* Ivan Orlov
* Jack McCracken
* Jaguar Xiong
* Jakub Kukul
* Jarcek
* jdesjean
* Jean-Francois Desjeans Gauthier
* jeff.melching
* Jenny Kim
* jheyming
* jkm
* Joe Crobak
* Joey Echeverria
* Johan Ahlen
* Johan Åhlén
* Jon Natkins
* Jordan Moore
* Josh Walters
* Karissa McKelvey
* Kevin Wang
* Khwunchai Jaengsawang
* Kostas Sakellis
* krish
* Lars Francke
* Li Jiahong
* linchan-ms
* Linden Hillenbrand
* linwukang
* Luca Natali
* Luke Carmichael
* lvziling
* maiha
* Marcus McLaughlin
* Mariusz Strzelecki
* Martin Traverso
* Mathias Rangel Wulff
* Matías Javier Rossi
* Maulik Shah
* Max T
* Michael Prim
* Michal Ferlinski
* Michalis Kongtongk
* MoA
* Mobin Ranjbar
* motta
* mrmrs
* Mykhailo Kysliuk
* Nicolas Fouché
* Nicolas Landier
* NikolayZhebet
* Olaf Flebbe
* Oli Steadman
* OOp001
* Oren Mazor
* oxpa
* Pala M Muthaia Chettiar
* Patricia Sz
* Patrick Carlson
* Patrycja Szabłowska
* pat white
* Paul Battaglia
* Paul McCaughtry
* peddle
* Peter Slawski
* Philip Zeyliger
* Piotr Ackermann
* pkuwm
* Prachi Poddar
* Prakash Ranade
* Prasad Mujumdar
* Qi Xiao
* rainysia
* raphi
* Rentao Wu
* Renxia Wang
* Rick Bernotas
* Ricky Saltzer
* robrotheram
* Romain
* Romain Rigaux
* Roman Shaposhnik
* Roohi
* Roohi Syeda
* Rui Pereira
* Sai Chirravuri
* Santiago Ciciliani
* Scott Kahler
* Sean Mackrory
* Shahab Tajik
* Shawarma
* Shawn Van Ittersum
* shobull
* Shrijeet
* Shrijeet Paliwal
* Shuo Diao
* Siddhartha Sahu
* Simon Beale
* Simon Whittaker
* sky4star
* spaztic1215
* Stefano Palazzo
* Stephanie Bodoff
* Suhas Satish
* TAKLON STEPHEN WU
* Tamas Sule
* Tatsuo Kawasaki
* Taylor Ainsworth
* Thai Bui
* thinker0
* Thomas Aylott
* Thomas Poepping
* Tianjin Gu
* tjphilpot
* todaychi
* Todd Lipcon
* Tom Mulder
* travisle22
* Vadim Markovtsev
* van Orlov
* vinithra
* voyageth
* vybs
* Wang, Xiaozhe
* Weixia
* Weixia Xu
* William Bourque
* wilson
* Word
* Xavier Morera
* Xhxiong
* Xiao Kang
* Xingang Zhang
* xq262144
* Ying Chen
* Yixiao Lin
* Yoer
* Yuriy Hupalo
* ywheel
* Zachary York
* Zach York
* Zhang Bo
* Zhang Ruiqiang
* zhengkai
* Zhihai Xu
* z-york
* 小龙哥
* 白菜
* 鸿斌
