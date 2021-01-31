---
title: "4.6.0"
date: 2019-12-05T18:28:08-07:00
draft: false
weight: -4060
tags: ['skipIndexing']
---

## Hue v4.6.0, released December 5th 2019

Hue is an open source SQL Cloud Assistant for developing and accessing [Databases & Data Warehouses](/administrator/configuration/connectors/)/Data Apps and collaborating: https://gethue.com


### Summary

The focus of this release was to keep building on top of 4.5 and modularize the tech stack, improve SQL integrations and prepare major upcoming features of Hue 5. In particular now:

* Python 3 support can be tested
* There is a new version of [gethue.com](https://gethue.com) and the content of [docs.gethue.com](https://docs.gethue.com) was revamped
* The new version of the Editor with multi execution contexts and more robustness is 66% done
* Build your own or improve [SQL parsers with highlighter](/developer/parsers/)


Read the complete list of improvements on [Hue 4.6 is out!](https://gethue.com/hue-4-6-and-its-improvements-are-out/).

Download the [tarball](https://cdn.gethue.com/downloads/hue-4.6.0.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.6.0.zip) releases.


### Notable Changes

* SQL
  * Apache Hive Tez improvements
  * Apache Hive LLAP improvements
  * Autocompletes
    * Tutorial on how to [improve/create a new SQL parser](/developer/parsers/) with [Highlighter](https://gethue.com/how-to-improve-or-add-your-own-sql-syntax-highlighter/)
    * Skeletons of dedicated parsers for Apache Druid, Phoenix, Elastic Serch, Presto, KSQL, Calcite are present
  * [Primary Keys, Partition Keys icons showing in the assists](https://gethue.com/2019-11-13-sql-column-assist-icons/)
* Collaboration
  * The Sharing icons as well as sharing action are now showing-up in left assistant
  * Copy result to Clipboard now properly keeps the table formatting
* Cloud
  * [Tracing calls](https://gethue.com/introducing-request-tracing-with-opentracing-and-jaeger-in-kubernetes/)
  * [Retrieving and searching Logs](https://gethue.com/collecting-hue-metrics-with-prometheus-in-kubernetes/)
  * [Collecting health and performance Metrics](https://gethue.com/collecting-and-querying-hue-logs-with-fluentd-in-kubernetes/)
  * [Azure ADLS v2 / ABFS v1](https://gethue.com/integration-with-microsoft-azure-data-lake-store-gen2/) has been integrated
* Infra
  * Python 3: support is making progress and now can be beta tested. `py3-ci` [CI branch](https://circleci.com/gh/cloudera/hue/tree/py3-ci), how to compile it and send feedback:
  ```
  export PYTHON_VER=python3.6
  make apps
  ```
  * Javascript testing switched to Jest and now supports headless
  * [docs.gethue.com](https://docs.gethue.com) has been revamped
* Bugs
  * The erratic behaviour of the horizontal result scrollbar in the SQL Editor has been fixed
  * Several Dashboard layout issues and IE 11 support fixes
  * [HUE-8727](https://issues.cloudera.org/browse/HUE-8727) Prevent chrome autofill in the assist documents


### Compatibility

Runs on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7), and Ubuntu 16.04 and 18.04.

Tested with CDH6 and CDP1. Specifically:

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
* Safari
* Microsoft Edge



Runs with Python 2.7+. 3.6+ is getting ready.

Note: CentOS 6 and RHEL 6 require EPEL python 2.7 package.


### List of 650+ Commits

* c90e81a8f5 [HUE-9095](https://issues.cloudera.org/browse/HUE-9095) [docs] Bump version to release 4.6
* 3656b39039 [HUE-9095](https://issues.cloudera.org/browse/HUE-9095) [docs] 4.6 release notes
* b1eb1a171a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [gethue] Avoid dead link to the deleted sql-editor page
* b893fdb5e1 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Avoiding setting all the right outline to bold
* fc72e795d8 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Fix Add more link to point to the connector docs
* 784fedfd6f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Reformulate the landing page
* cf15b74367 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Update main README to avoid deadlinks in description
* ac40032707 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Adding sharing and permission tests
* bc4df82c04 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Adding link sharing API
* 8b4c277aac [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Adding is_link_on to share method
* e26766be42 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Fix bug in get_or_create group
* 2e5d040e40 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Protect against missing oozie app when running tests
* 897045b387 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Adding schema migration for link permission
* a738f5775c [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Index the new link field
* 6502b02a63 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Adding test skeleton for Link permission
* 84fad2d822 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Avoid warning about flags being of type bool
* 8d0087ab6f PR1007 [core] Fix the URL for "Add more" button . Issue #1006 (#1007)
* 9014bfa9b9 Revert "[HUE-8905](https://issues.cloudera.org/browse/HUE-8905) [core] Apply HUE-8772 to Django-1.11.22 for fixing 'user is missing in mako context'"
* bde563b8b1 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Add monkey patch django_template_context.RequestContext.__init__
* ff7d021fae [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix admin check_config, dump_config and user_list
* 59ebe432c5 [HUE-9092](https://issues.cloudera.org/browse/HUE-9092) [core] Fix Hue ProgrammingError at /hue/accounts/login when opening first time when db connectivity is down
* e0bd664575 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Adopt py3 changes encoding function and open file
* d4b62903c4 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding a spec for SHOW and LIST
* 04ab447238 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding show and list .jison
* 3bbef730a3 [HUE-9095](https://issues.cloudera.org/browse/HUE-9095) [gethue] Improving 4.6 release notes
* 119854f10e [HUE-9094](https://issues.cloudera.org/browse/HUE-9094) [k8s] Modernize mardown syntax of Hue Docker README
* 92fa06b452 [HUE-9094](https://issues.cloudera.org/browse/HUE-9094) [k8s] Upgrade website cert manager to v11.0
* d0c00f31cc [HUE-9094](https://issues.cloudera.org/browse/HUE-9094) [k8s] Remove extra service name from the website config files
* e4df7e6d86 [HUE-9094](https://issues.cloudera.org/browse/HUE-9094) [k8s] Rename gethue-website service to website
* 3c2354b676 [HUE-9094](https://issues.cloudera.org/browse/HUE-9094) [k8s] Rename gethue-docs service to docs
* 35aea96b54 [HUE-9094](https://issues.cloudera.org/browse/HUE-9094) [k8s] Upgrade cert manager to v0.11.0
* 96f778417c [HUE-9094](https://issues.cloudera.org/browse/HUE-9094) [k8s] Adding some basic CPU limits
* 0d514af995 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Fix git conflict leftovers
* 698f13afa0 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Adjust stylelint rules to be less agressive
* 2555476188 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Add additional ko binding tests
* 60d3c9477e [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Add tests for the event-based modal components
* 172c5805c0 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Add tests for the reminding simple ko components
* d3662341a0 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Update keywords in Ace
* 5c2582b15e [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Update syntax highlighter tokens
* 58732b33d2 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding new keywords to the syntax highlighter
* d2fce06a6b [HUE-9089](https://issues.cloudera.org/browse/HUE-9089) [thrift] Update information about major Hive Thrift change version
* 221ba05b3e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding column and https details for Druid connector
* 38f6524104 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [ci] Adding --runInBand parameter to js tests
* 4f7d157009 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [parser] Skipping CI js tests on new skeletons for now
* bc05d4ebfc [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [ci] Adding jest.config.js to the image sync
* 60b4fa5069 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Update the docs with js testing changes
* 349976dcb8 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Add additional ko component tests
* 95444a6540 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Enable js test coverage gathering
* 21b42cfc45 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Introduce snapshot testing for ko components
* 11509af6ed [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Don't re-run js tests on static content changes
* 930220bcf7 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Replace deprecated polyfill lib
* 4064195145 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Fix flaky test
* b84c6accc1 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Add the jest plugin to eslint
* 7bde5d3d3c [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Switch to jest for js testing
* 34d1c2c3b4 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Bump less and less linter version and fix less linting issues
* ceb9c91b43 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Bump babel and webpack versions
* f3800054f1 [HUE-9088](https://issues.cloudera.org/browse/HUE-9088) [frontend] Upgrade Knockout to 3.5.1
* fdf96a469b [HUE-9051](https://issues.cloudera.org/browse/HUE-9051) [search] Keep dashboard top nav buttons in one row
* 56ffd27b40 [HUE-8727](https://issues.cloudera.org/browse/HUE-8727) [frontend] Prevent chrome from autofilling username in select2 search inputs
* b15edd5c4d [HUE-9092](https://issues.cloudera.org/browse/HUE-9092) [core] Fix Hue ProgrammingError at /hue/accounts/login when opening first time when db connectivity is down
* fe52c11488 [HUE-9092](https://issues.cloudera.org/browse/HUE-9092) [core] Fix Hue ProgrammingError at /hue/accounts/login when opening first time when db connectivity is down
* e80f711480 [HUE-9091](https://issues.cloudera.org/browse/HUE-9091) [core] Remove astroid, isort, six dependencies
* 9c90490a34 [HUE-9089](https://issues.cloudera.org/browse/HUE-9089) [hive] Add thrift version error message.
* 947b820893 [HUE-9089](https://issues.cloudera.org/browse/HUE-9089) [editor] Propagate hasResultSet changes.
* cf110e7df4 [HUE-9089](https://issues.cloudera.org/browse/HUE-9089) [editor] Use uuid for check_status
* ebbca5722a [HUE-9089](https://issues.cloudera.org/browse/HUE-9089) [hive] Upgrade Thrift protocol to V11 to support LLAP
* b7a9bd5834 [HUE-9072](https://issues.cloudera.org/browse/HUE-9072) [jb] Fix Oozie coordinator pagination
* d046be45ef [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Simplify the connector type matching logic
* 823a211aa3 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [pylint] Improve command to support a list of files
* 6a26e82e30 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Add Python linting script
* 4a655b8764 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding compiled ace highlighters
* 535d218c1d [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding highlighter skeleton to BigQuery
* 16da4d68a1 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding highlighter skeleton to Druid
* eda4eb1635 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding highlighter skeleton to ElasticSearch
* cce00cd298 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding highlighter skeleton to Phoenix
* 6541b78119 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding highlighter skeleton to Presto
* c0e096f9e4 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Send the executable to the execute endpoint for proper handle placement
* b83729c207 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Use the operationId for check status
* bde27793a5 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Show a spinner in the result after execute
* 86449967d9 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Add the optimizer enabled flag to the executor
* 1f78401a67 [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Change stop button color to red in notebook 2
* 65b5c63970 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Fix issue where the result header is shown on top when switching between chart and grid
* 7b64997a58 [HUE-9005](https://issues.cloudera.org/browse/HUE-9005) [editor] Fix issue with cancelling statement execution in notebook 2
* 2d68f7db06 [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Disable the execute button when the editor is empty
* 4ca506d76d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh Python API example
* db5f6b39be [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix the download links of the 4.5 release
* c609a98c8f [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Clearing Editor history is erroring
* 0992616ffa [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Use desktop lib smart_unicode to not crash admin page
* 9d3d9c651d [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding Apache Phoenix parser skeleton
* 39fd7494ee [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding Presto parser skeleton
* 3bfd2cc48d [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding Elastic Search parser skeleton
* 3d0d9ec1a3 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding Apache Druid parser skeleton
* 9a7cb64ca3 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [calcite] Adding calcite parser skeleton
* 1279e7b502 [HUE-9051](https://issues.cloudera.org/browse/HUE-9051) [search] Fix broken top nav layout in IE 11
* 87ee9fb9d7 [HUE-9082](https://issues.cloudera.org/browse/HUE-9082) [frontend] Prevent the same app from initializing twice
* 16ac085ce2 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor2] Fix properly sending operation context in fetchLogs
* 0efca3c4f8 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Propagate the sync results into the handle
* 9e0ccae922 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] A few missing links in the roadmap
* d1d978371a [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix missing module mock in py3
* f724abb72f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [hdfs] Fix py3 unit tests
* de9291d89e [HUE-9086](https://issues.cloudera.org/browse/HUE-9086) [docs] Adding gethue website source
* f9ee6af463 [HUE-9085](https://issues.cloudera.org/browse/HUE-9085) [fb] Improve S3 bucket 301 & 400 error message
* a7fbd72101 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Update helm install instruction for MicroK8s
* dcf5de313f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding information about Hive and Impala HA
* 6a8eee8258 [HUE-9083](https://issues.cloudera.org/browse/HUE-9083) Fix concurrent query with Hive on Tez when `max_number_of_sessions > 1`
* 7be8353641 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [azure] Skip fs home creation on login in Azure only configuration
* 49a8793569 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding transaction and assist icon knowledge
* c0a4f4e7ac [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Reorganize the main roadmap sections
* 9edda90b43 [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [optimizer] Making the optimizer client REST compatible
* 533379d05b [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Skeleton of adding optional optimizer query upload
* c99b471758 [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [optimizer] Revamp the dummy Client to support topTables
* d9e9e5c01f [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Skeleton for adding an operationId in the API
* 63bcf03493 [HUE-9073](https://issues.cloudera.org/browse/HUE-9073) [fb] Only enable IDBroker when on cloud.
* 981951a43a [HUE-9073](https://issues.cloudera.org/browse/HUE-9073) [fb] Add ABFS core_site config.
* 23bf1ed465 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [azure] Skip fs home creation on login in Azure only configuration
* cda614fc52 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [aws] Skip fs home creation on login in S3 only configuration
* 79ec4bc206 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Remove some tmp localization files checked in
* 2a62b4af34 [HUE-9073](https://issues.cloudera.org/browse/HUE-9073) [fb] Remove unnecessary logging in ABFS.
* d4673da97d [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Cleaner SELECT results
* 221554ac21 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Support SHOW QUERIES
* 9d7e00fe21 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Support SHOW TABLES
* f7c9156300 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Support SHOW STREAMS
* fbea472423 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding commandStatus message to the result
* e353417f89 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Basic support for DESCRIBE
* 9edc526f72 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Basic stream query support
* 5c53710234 [HUE-9080](https://issues.cloudera.org/browse/HUE-9080) [impala] Workaround missing PK information in table description
* 68605ed7a7 [HUE-9070](https://issues.cloudera.org/browse/HUE-9070) [editor] Integrate primary keys info in the interface
* 1c7a5573f9 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [dashboard] Avoid TypeError: '<' not supported between instances of 'dict' and 'dict'
* b204157a73 [HUE-9080](https://issues.cloudera.org/browse/HUE-9080) [editor] PK icons are now missing in Kudu tables
* 90e0e6dc81 [HUE-9075](https://issues.cloudera.org/browse/HUE-9075) [solr] Fix Solr query return 414 response code when GET parameters is too long
* f49561fa07 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [editor] Fix _unpack_guid_secret_in_handle in py3
* 272fb4fd08 [HUE-9079](https://issues.cloudera.org/browse/HUE-9079) [doc] Improve ABFS connector
* 4304bdc92a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Update the end user section of file browsing
* 20e94a0d33 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Open SQL gist in presentation mode by default
* 644ab8c3ee [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Adding copy link to clipboard button
* b243231a41 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [editor] Avoid adding extra snippet when new editor already has one
* 77a41e832e [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Port functionality to Editor 2
* 6db70177fc [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Make it optional to submit notebook and snippet on execute for history in editor v2
* 1700377748 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Add CSV and XLS download actions in editor v2
* 5f520e4634 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Fix issue with switching to result tab after execute in editor v2
* e637b31ff2 [HUE-8900](https://issues.cloudera.org/browse/HUE-8900) [editor] Make sure the notebook has a name set in editor v2
* 61fbe4955b [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Handle sync result in editor v2
* 46ce0c6800 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Add copy result to clipboard action in editor v2
* 66f4ef2f22 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Hide column selection by default in the result grid
* dc92a4aae6 [HUE-9073](https://issues.cloudera.org/browse/HUE-9073) [fs] Avoid missing user argument in _get_client_cached
* 92e7df5184 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding some parsers file to the lintignore
* 9f8854146d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Tweak website ingress template to be compatible
* 1fdbfa11db [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Implement executing a SHOW TOPICS
* 758ca0d23b [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Implementing the autocomplete piece of the Editor API
* fde074c8c5 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [connector] Adding initial ksql connector
* 3afba3527b [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding initial Python client
* 3118289e4e [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [kafka] Adding new parser skeleton
* 9538e43ed7 [HUE-9073](https://issues.cloudera.org/browse/HUE-9073) [fb] Enable unit tests for ADLS
* e02c1fdb23 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [jb] Avoid js error when the Resource Manager is down
* 27ba9e83a8 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Parameterize the website helm chart services
* 4ab1cb00c5 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Add missing import in test util
* 7f3fdc3946 [HUE-9076](https://issues.cloudera.org/browse/HUE-9076) [editor] Support domain in azure URL
* 2869507272 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Adding gethue.com website
* a18700f1e3 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add other types of supported batch connectors
* 5b0a130869 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix and update instructions for making a release
* 09e48a9381 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Improve the Administrator landing page
* ab5a9be55f [HUE-9073](https://issues.cloudera.org/browse/HUE-9073) [fb] Add IDBroker support for azure
* b8119cd166 [HUE-9073](https://issues.cloudera.org/browse/HUE-9073) [fb] Add IDBroker support for azure
* 3edcf3a026 [HUE-9070](https://issues.cloudera.org/browse/HUE-9070) [editor] API for retrieving Table Primary Keys
* 21b8afe105 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Update tests and also fix bug in test login client
* 8ac779539f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Listing Apache Solr in the list of connectors
* 8741d0a1c0 [HUE-9069](https://issues.cloudera.org/browse/HUE-9069) [hive] Partition Key icons are missing in Hive tables in Assist
* 52d6c5b992 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Properly load back the SQL gist
* 18f395b1ad [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Adding link in popup
* d1f38e8b16 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [notebook] Load gist id as new editor with default values
* 9ad9b51ac0 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [desktop] Move __paginate util to the model instead of api module
* 739f55cfc5 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [notebook] Open gist in editor
* 56352f5bc2 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Create a get method
* ac68b9c276 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Adding create API
* f8804e8832 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Adding link button in sub execute dropdown
* b243e14308 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Large revamp of the browser section
* cde95dc2ce [docs] Fixed image size in featherlite
* 60e0a48b1e [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [metadata] Adding missing base file
* 2f7c903832 [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [metadata] Proper load of default navopt POST param values
* 73882df23c [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [metadata] Start refactoring of optimizer API
* ca83744100 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplify and remove old job submission references
* b16bdde9f8 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactoring of the connector API section
* c0f3a6de27 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding a scheduling section skeleton
* 6097380bd2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Revamp of the Browsing user section
* 63324cda79 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Large revamp of the Querying section
* 1cc6e29893 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding initial version of Spark docs
* 35ba3446dc [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Document the Too many connections issue
* 5ed31b4320 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Document about the too many document issue
* 295f7e6e4c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add list of known issues to Phoenix connector
* 869bf62221 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [aws] has_key() was removed in py3
* 5c39c92a90 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Metastore and indexer should not crash even if no network
* 53ab87253c [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Avoid NameError: Undefined when opening jobbrowser
* e4727ec78b [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Avoid double 500 on traceback with py3
* 35eb79871b PR [docs] Fix broken connector link in README (#993)
* 5ab6ff78d2 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Add query explain in notebook 2
* a021e4859f [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Fix loading queries with 0 results
* cff5758e2e [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Remove dead code in notebook 2
* 659b88d429 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Fix issue with undefined chart settings when switching between results
* 0a009304a1 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Add save/load logic for executables in notebook 2
* 4cf41fe59d [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Fix issue with opening queries from left assist in notebook 2
* 810f6fac5d [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Anchor gutter and range markings in the Ace editor for executables
* d7e6f0920e [HUE-9063](https://issues.cloudera.org/browse/HUE-9063) [fb] Lazy load aws client.
* f3112c94d8 [HUE-9068](https://issues.cloudera.org/browse/HUE-9068) [beeswax] Fix execute_statement default argument
* b45284f61a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Adding a check for Python 3 build
* 94d553da7a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Move app creation to bottom of APIs
* 9d3c39a99d [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] open function mode should be 'r' and not 'read'
* 8d78b968aa [HUE-9059](https://issues.cloudera.org/browse/HUE-9059) [hive] Adding mock tests for column listing
* f6d6c20069 [HUE-9065](https://issues.cloudera.org/browse/HUE-9065) [libopenid] Remove opendId lib
* ebfa758ad3 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [thrift] Adding test for retry paths of thrift_util.SuperClient
* 31aab53ba9 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Avoid unbound exception on Thrift connection error
* 1cdf0198ad [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding missing user section on HDFS acls
* 0fe07060fa [HUE-9059](https://issues.cloudera.org/browse/HUE-9059) [hive] Tables are missing first column in Assist with Hive on Tez
* dcf5b55fe5 [HUE-9059](https://issues.cloudera.org/browse/HUE-9059) [hive] Rename _get_partition_column to _get_partition_columns
* 85d602f5da [HUE-9063](https://issues.cloudera.org/browse/HUE-9063) [fb] Fix aws get_default_region when no config
* 6368aef66b [HUE-9062](https://issues.cloudera.org/browse/HUE-9062) [beeswax] Add http thrift port configuration
* 1383cc848f [HUE-9064](https://issues.cloudera.org/browse/HUE-9064) [ws] Parameterize channels config to be setup
* 8e8761fb4d [HUE-9064](https://issues.cloudera.org/browse/HUE-9064) [ws] Adding channels to requirement.txt
* 5bd494dd40 [HUE-9064](https://issues.cloudera.org/browse/HUE-9064) [core] V1 of Websockets infra
* ef7fd6ebdd [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fixed right TOC layout on mobile
* e740964026 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Split developer SDK docs into Connectors SDK and API sections
* 01c4ed98f2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplification of contribution guidelines
* 8a80340b06 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Remove built with info for now
* 11d84a5e33 [HUE-9061](https://issues.cloudera.org/browse/HUE-9061) [beeswax] connector adoption Change-Id: I88c337d629f8449e9db2ba354a01fba6fdcee7de
* 59d9929d2d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Started revamp of the SDK
* 2b70b31c72 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] More info about Solr and Sentry
* 7940ff76a9 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding Admin Metadata configuration information
* 5828259250 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding Data Catalog to the User Browsing section
* 1130d904d2 [HUE-9058](https://issues.cloudera.org/browse/HUE-9058) [frontend] Update the left assist after a doc share settings have been changed
* f5fd386cb2 [HUE-9058](https://issues.cloudera.org/browse/HUE-9058) [frontend] Prevent share modal conflict
* 76d2fcdac1 [HUE-9058](https://issues.cloudera.org/browse/HUE-9058) [assist] Add share to the doc assist right-click context menu
* 7a2533cd44 [HUE-9058](https://issues.cloudera.org/browse/HUE-9058) [assist] Show sharing status in the doc assist
* 8fb7e36b41 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Sort the requirement.txt file
* 8d79c47428 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Removing invalid and duplicated import
* ec8aee906b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add more images to the Querying section
* 17705c64ff [HUE-9060](https://issues.cloudera.org/browse/HUE-9060) [fb] ABFS Handle missing properties
* 201b6af279 [HUE-9056](https://issues.cloudera.org/browse/HUE-9056) [impala] Fix exception when impala conf path is missing.
* 828dcb9458 [HUE-9046](https://issues.cloudera.org/browse/HUE-9046) [jb] Add link to queries-hive in editor.
* 66cadc6837 [HUE-9046](https://issues.cloudera.org/browse/HUE-9046) [jb] Use sample user to do admin queries. Change-Id: I8b9fa0f3874071769a20b7fb543c4acd91118eb0
* 48166029d7 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fixing a bunch of bad identations
* fd1f38f0cf [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Aggregation of the connector list
* b72d4e811c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add more images and description to the Queyring section
* e2b623a7cb [HUE-9057](https://issues.cloudera.org/browse/HUE-9057) [docs] Documentation about updating or creating editor highlighters
* 2e76a9e99e [HUE-9053](https://issues.cloudera.org/browse/HUE-9053) [docs] Adding a tip on trying to use Oracle 11 module with v12
* d8e683c11d [HUE-9051](https://issues.cloudera.org/browse/HUE-9051) [frontend] Fix issue with overridden setInterval in IE 11
* 8defae4156 [HUE-9052](https://issues.cloudera.org/browse/HUE-9052) [editor] Indicate column partition keys in the assist panels
* 685365a9ff [HUE-9051](https://issues.cloudera.org/browse/HUE-9051) [frontend] Replace ES6 arrow function used outside babel
* 27cc3ea991 [HUE-9055](https://issues.cloudera.org/browse/HUE-9055) [hive] INTEGER is introduced as a synonym for INT in 2.2
* 26af50e510 [HUE-9049](https://issues.cloudera.org/browse/HUE-9049) [ci] Convert check for non ASCII to check for non UTF
* 4f0580ae9f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding more info about the left assist
* 9b454df067 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding reference to inline Language manual
* ffa7f72c5d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [py3] Remove some un-used imports
* ecdee483ac [HUE-9053](https://issues.cloudera.org/browse/HUE-9053) [docs] More clarity about Oracle DB client 12 upgrade
* 34c6bad74f PR991 [editor] Fix description doc of from_unixtime (#991)
* 66f6b281bf PR992 [editor] Use ascii hyphen instead of EN DASH (U+2013) in date_format desc (#992)
* 0df6aeef84 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Promote more the help forum in the README
* 13cea769b0 [HUE-9043](https://issues.cloudera.org/browse/HUE-9043) [ci] Skips files that are deleted, binary in ASCII check
* f7fce54f3e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Removing non ascii characters from files
* 92150d534e Revert "Revert "[HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Switch clipboard copy from text to formatted html table (#987)""
* dc681aafcb [HUE-9049](https://issues.cloudera.org/browse/HUE-9049) [ci] Add a check for updated files non utf8 compatible
* 7873a9639f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [fb] Fix imported libraries in filebrowser view
* d6a084828f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix Hive Thrift (step 2) for Python 3.5
* 69153d2df9 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [hive] Fix Hive thrift for Python 3.5
* 91d754a2ba [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Enable make apps with py3 on Mac and fix read file in pth.py   * export PYTHON_VER=python3.5 (or above for make apps in py3)
* 5afb9e5845 [HUE-9046](https://issues.cloudera.org/browse/HUE-9046) [jb] Hive query history
* c2695f94c1 [HUE-9050](https://issues.cloudera.org/browse/HUE-9050) [core] Add 80 to trusted port for CSRF token
* b3ccb6f35a [HUE-9045](https://issues.cloudera.org/browse/HUE-9045) [core] Remove chardet import from requests-2.18.4
* 686c4929f1 [HUE-9044](https://issues.cloudera.org/browse/HUE-9044) [core] Remove ext lib chardet-3.0.4
* 26554ee1ab  [HUE-9039](https://issues.cloudera.org/browse/HUE-9039) [jb] Fix the link to sub-workflow
* b54a398bf4 [HUE-9048](https://issues.cloudera.org/browse/HUE-9048) [docker] Optimize documentation image size and config
* 4062bf133a [HUE-9048](https://issues.cloudera.org/browse/HUE-9048) [docker] Combine several similar RUN commands to optimize image
* bed1fb4cb3 Revert "[HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Switch clipboard copy from text to formatted html table (#987)"
* d104675e6d [HUE-9047](https://issues.cloudera.org/browse/HUE-9047) [core] Fix knox principal verification
* 5b9ae89e6d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding section about notion of cursor in autocomplete
* 08505b010f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Move some description our of the code highlighting
* de0a2d1caf [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] More parser documentation readability tweaks
* 129e9c840a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix the right toc padding of title 1
* 04b6aa07b1 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Clean-up the HBase configuration section
* a40acb5344 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Typo in makefile about Python3 versions variable
* 4d55bc9b4d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Small polishing of the SQL parser guide
* 9315a494b2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [design] Updating CICD about documentation
* d3de446b0c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add admin information on CLI document export
* 0b7c8f4bbf [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix Sybase connector description
* e15ac5c8fb [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Switch clipboard copy from text to formatted html table (#987)
* 5e65364e51 [HUE-9042](https://issues.cloudera.org/browse/HUE-9042) [search] Prevent users from changing the first metric aggregate function in some widgets
* 99a760b738 [HUE-9043](https://issues.cloudera.org/browse/HUE-9043) [search] Fix issue where it sometimes is impossible to close the aggregate settings
* a4207c1d6d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Do not run a staging clusterissuer in prod
* b8faa6f380 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add information about checking for 404 in docs
* 58770c9ddb [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Simplify the hue helm chart docs
* 05eb5d88d6 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Fix ssl certificate conflict between hue and docs
* d6fe4ca9d6 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix a series of broken links
* 919f19e712 [HUE-9041](https://issues.cloudera.org/browse/HUE-9041) [frontend] Don't show the jobs links in the top nav when the job browser is blacklisted
* e878aaf1ab [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Enable https for the docs ingress
* d373d3db60 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix Hue logo alternative text in README
* 33c87c4e13 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8] Website ingress should not conflict with hue ingress
* 73ccc6afeb [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Avoid hardcoding the static file container source
* a8206d23f0 [HUE-9040](https://issues.cloudera.org/browse/HUE-9040) [search] Fix issue where charts sometimes spins forever
* 13d995a57f [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Add execution errors to the logs component and properly mark them in the gutter
* 01761b405b [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Notify on executable refresh while editing
* f96f0e57fd [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Indicate execution status in the gutter
* e995c4340c [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Switch to the result tab after the active executable has results available
* f48120b3e7 [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Add stop functionality for batch executions
* 8a93433e73 [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Add support for select to execute multiple in notebook 2
* e7d9a465e5 [HUE-9004](https://issues.cloudera.org/browse/HUE-9004) [editor] Remove execution progress tracking from the snippet in notebook 2
* 9a02e0d38d [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Fix issue with re-execution of a statement in Notebook 2
* 3408ff507a [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Enable parallel click to execute in notebook 2
* 13ba597752 [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Remove old result and execution logic from the snippet in notebook2
* 24053ea24f [HUE-9005](https://issues.cloudera.org/browse/HUE-9005) [editor] Extract log handling to a separate log component
* 89d0279cc6 [HUE-9028](https://issues.cloudera.org/browse/HUE-9028) [editor] Switch to fixed executor per snippet
* 4045c00a19 [HUE-9038](https://issues.cloudera.org/browse/HUE-9038) [catalog] Supported engines are getting duplicated
* 92d5254c07 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add link to fsmanager in File SDK section
* ec31dbb0fb [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ui] Adding help link to documentation in left menu
* 19fc1ee3f2 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [fb] Fix python3 port creating 500 on down HDFS
* cffe7381a1 [HUE-9037](https://issues.cloudera.org/browse/HUE-9037) [core] Add .cloudera.com to trusted host for CSRF token
* 8a4e668594 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Small tweaks missed in the previous merge
* dea9f9643b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Major simplification on how to configure
* 43a152e032 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh landing page
* d4666d2631 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix several broken links
* c46c89459a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplification of developer sections
* a773eb687f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Combine the running and install sections
* 7039a78f1e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplify the end user guide
* e1d5ac68d3 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactor the quick start section
* 6f87da85aa [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Major simplification on how to configure
* 9bdc174437 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Remove duplicated dashboard section
* 8b848a3675 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Move common dev section to the bottom of the page
* 94962325f5 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding info about pinot
* eb5170daba [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Enrich some more the end user section
* 4e0dc7d415 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh the readme to promote Docker and SQL
* 44320b07c5 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplify and clarify how to run the tests
* 57352747b9 [HUE-9030](https://issues.cloudera.org/browse/HUE-9030) [docker] Rename website to documentation
* 26a85c926b [HUE-9029](https://issues.cloudera.org/browse/HUE-9029) [hive] Workaround Hive on Tez not performing HDFS impersonation
* 8b64e3ff12 [HUE-9030](https://issues.cloudera.org/browse/HUE-9030) [docker] Trim some size to the image by removing node modules
* f03bce6ccd [HUE-9030](https://issues.cloudera.org/browse/HUE-9030) [k8s] v1 of helm chart for the website
* 66a3cc1372 [HUE-9030](https://issues.cloudera.org/browse/HUE-9030) [k8s] Preparing helm chart for the website
* 66bc0d0c68 [HUE-9030](https://issues.cloudera.org/browse/HUE-9030) [k8s] Preparing daphne websockets service
* 678d99e8c2 [HUE-9030](https://issues.cloudera.org/browse/HUE-9030) [k8s] Add default secret key to avoid hue relogins
* 979aeea1cb [HUE-9027](https://issues.cloudera.org/browse/HUE-9027) [editor] Fix erratic behaviour of the horizontal result scrollbar
* 1c5b0c1444 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Improve additional row fetching on scroll in notebook 2
* 9c4ea4c849 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Properly dispose the table extender plugin
* 2b0fab775e [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Fix rendering of subsequent results in the notebook2 result grid
* 2207d910bb [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Switch to event based result handling for the result grid and chart components
* 37a98fcb6a [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Improve result layout in notebook 2
* 40e37b7892 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Move chart logic into the ko.resultChart component
* db769cc9e6 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Move grid result column list logic into the ko.resultGrid component
* 10d1019e3e [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Introduce a snippet result component for notebook 2
* 85ecb17da5 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Contain data table generation within the new result grid component
* 18b838e13f [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Improve result lifecycle for the executor in notebook 2
* 4fc80f8cf4 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Remove snippet references from the resultChart component
* ec81841bf5 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Show result settings to the left of the grid and chart in notebook 2
* 5f92f4bb18 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Fix snippet JS exception in notebook 2
* b32dbe3fe2 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Extract grid component for notebook 2
* 9590af8634 [HUE-9013](https://issues.cloudera.org/browse/HUE-9013) [editor] Extract chart component for notebook 2
* b392db3b47 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix instrumentation setting in py3 and remove unused import in proxyfs.py
* 4309f2f4a6 [HUE-9026](https://issues.cloudera.org/browse/HUE-9026) [core] Use str instead of unicode for password Change-Id: I2089d25eb507bc56a852e021b3875b703eefa19e
* d16d61dbbb [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix byte string cause migration fail in Python 3.5
* e05f890287 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Default to sqlite for booting out of the box
* c320069bee [HUE-9024](https://issues.cloudera.org/browse/HUE-9024) [core] Prevent AnonymousUser object is not iterable on login
* 319a29bbbf [HUE-9025](https://issues.cloudera.org/browse/HUE-9025) [editor] Fix multi query statement with invalidate metadata
* 76ce738491 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix supervisor.py py3 compatible issue
* 7d72b25c5f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] app_reg open file issue for py3
* 5bb6034362 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Install navoptapi-1.0.0 as wheel file
* 9cf00ec3ad [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] make Hue install third party libs via requirement.txt
* f7045b0590 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] make Hue can be built on both py2 and py3
* a288f0b985 [HUE-9023](https://issues.cloudera.org/browse/HUE-9023) [core] Logging HTTP requests code and size separately
* 6bf2922d86 [HUE-9023](https://issues.cloudera.org/browse/HUE-9023) [core] Add proper logging of HTTP requests code and size
* 88274a08b0 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Add yaml for docs website service
* 88cac25a42 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Promote more the SQL parser API
* 51eed39cdc [HUE-9018](https://issues.cloudera.org/browse/HUE-9018) [docker] Tweak build instruction for the docs website
* 94d8924c07 [HUE-9020](https://issues.cloudera.org/browse/HUE-9020) [core] Improve Hue and Hue Load Balancer docker image generation.
* ad771efe56 [HUE-9020](https://issues.cloudera.org/browse/HUE-9020) [core] Improve Hue and Hue Load Balancer docker image generation.
* c997cff9d6 [HUE-9020](https://issues.cloudera.org/browse/HUE-9020) [core] Improve Hue and Hue Load Balancer docker image generation.
* c1c2dcd79b [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Remove guppy since no update in PYPI
* 53c91ff74d [HUE-9021](https://issues.cloudera.org/browse/HUE-9021) [docs] Add list of potential items to improve the metrics
* 52bd3c0720 [HUE-9018](https://issues.cloudera.org/browse/HUE-9018) [docs] Remove additional baseUrl for images as not needed anymore
* 38e4a89266 [HUE-9018](https://issues.cloudera.org/browse/HUE-9018) [docs] Update URL config to omit latest
* b7c40363a0 [HUE-9022](https://issues.cloudera.org/browse/HUE-9022) [editor] Set transactional flag to customer sampletable to false
* 0a2aff8bc1 [HUE-9020](https://issues.cloudera.org/browse/HUE-9020) [core] Improve Hue and Hue Load Balancer docker image generation.
* 292db6d788 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix beeswax, hdfs, oozie and desktop libs py3 compatible code
* 9a92dc1208 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [fb] Fix file browser for Python 3.5
* f58252c459 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix desktop log open file and conf bytes issue
* 058bfa93af [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [tools] Add a github issue templates (#975)
* 7c2c40d936 [HUE-9018](https://issues.cloudera.org/browse/HUE-9018) [docs] Add recommended extensions for Visual Code
* c1cff6793a [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Set trace validation to true
* 93f9233f24 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [docker] Missing lib in images for running the tracing
* 14cf372940 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [k8s] Inject Jaeger profiler as side card to Hue deployment
* 9b0a260045 [HUE-9020](https://issues.cloudera.org/browse/HUE-9020) [core] Improve Hue and Hue Load Balancer docker image generation.
* abb5760e03 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/metadata for Python 3.5
* c6df845c07 [HUE-9019](https://issues.cloudera.org/browse/HUE-9019) [core] Fix concurrent_user_session_limit failed after Django upgrade
* 513e5d1d02 [HUE-9018](https://issues.cloudera.org/browse/HUE-9018) [docker] Adding .dockerignore to speed up builds from dev env
* ac5d6d2400 [HUE-9018](https://issues.cloudera.org/browse/HUE-9018) [docker] Containerize documentation website
* 78b4aee657 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Add hierarchy to roadmap
* 08eb1b90f4 [HUE-8790](https://issues.cloudera.org/browse/HUE-8790) [core] Fix custom logo displaying on the sidebar
* 762890bbc5 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [core] Stop posting metrics in the /is_alive call
* d752199cc6 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Use v1 for Deployment version
* 3ea767b31b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Ordered intrepreter is not valid anymore with connectors
* b481d1d5c1 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Improve sync task to properly work with beat
* c405ebecf0 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Adding tracing documentation
* defef81095 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Promote more SQL autocomplete section
* e5ccc58414 [HUE-8815](https://issues.cloudera.org/browse/HUE-8815) [docs] Add a reference architecture diagram
* 30589e1e62 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [docs] Document about Kubernetes metrics
* e4386ede0e [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Extract executor base class with sqlExecutor for sql connectors
* a64fc69af6 [HUE-9009](https://issues.cloudera.org/browse/HUE-9009) [frontend] Add support for testing ko bindings
* 4f65e504bd [HUE-9009](https://issues.cloudera.org/browse/HUE-9009) [frontend] Add example of testing ko components to the sdk docs
* de1a0a5b92 [HUE-8727](https://issues.cloudera.org/browse/HUE-8727) [frontend] Prevent chrome autofill in the assist documents, functions and language reference panels
* 74881f6fdb [HUE-9004](https://issues.cloudera.org/browse/HUE-9004) [editor] Migrate status bar to new executor for notebook 2
* 47f9a85c75 [HUE-8980](https://issues.cloudera.org/browse/HUE-8980) [jb] Fix coordinator cannot sync with saved documents
* 93c0eb402c [HUE-9010](https://issues.cloudera.org/browse/HUE-9010) [core] Handle failure of gethostbyaddr
* 36b8094225 [HUE-9011](https://issues.cloudera.org/browse/HUE-9011) [hive] Fix invalid delimiters in create Hive table
* bc635c83ba [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Adding missing beat_api module
* 55ee255cd4 Merge remote-tracking branch 'origin/master'
* 4c6c8ba4c2 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Avoid variable name conflicting with each other
* 9073c5614b [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Plugin-in all the job action
* a4f8d76484 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Adding job management operations
* 10edc8b24a [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Adding basic celery beat page in Job browser
* 075c96012b [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Display periodic task as Scheduled Tasks in job browser
* 137ce70c9a [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Beat interface skeleton in Job Browser
* 4d90b323c2 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Adding action and list to beat schedule API
* c7b70f4ed8 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Retrieve saved document to be scheduled
* 5cba6a1131 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Update previous task is there when submitting a beat
* e7fd4aaef1 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [notebook] Snippet with sqlalchemy interface should be batchable
* 54e5322c4d [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [notebook] Move some dependencies out of the views module
* 65277b686b [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Basics to support cron scheduled queries
* a5604d9841 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Preparing submit API for beat
* 65bc5ddd0b [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Add minimal celery beat submission API implementation
* e61384189c [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Fix missing imports
* 700265bfbb [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Keep monkey patching of Django User model as-is
* bbdd0e4d04 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add more info on special username test fail
* cb88b09435 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] dump_config test needs a default connector
* d974083da3 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Keep default group signal set
* 9aa3ffa78b [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Simplify imports by handling logic in useradmin
* 3e9fd3e29b [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Handle forms import dependencies when off
* 23cbdebc51 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Move user change forms swap logic directly into imports
* 21672d4bd1 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Limit dump_config to desktop section
* a4be134361 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add default organization when creating a new user
* 0743318fa7 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Avoid 500 error on csrf missing on login page
* 7d0f0da2d9 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Port S3 proxy user lookup
* 9a3d6994a0 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Rename imports to not confict with models2
* 39af21b5ef [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support creating a new group
* b366a4955b [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support editing a group
* a2f5c2d8e3 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support listing permissions
* e8cb892165 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support creating a new user
* d334cc2af8 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support for Edit user page
* 09facb194f [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Port User and Group model switch everywhere
* 93a6d340fa [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Proper imports of get_defaut_group
* 98c1edcc74 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [useradmin] Fix py3 unicode in ensure_home_directory
* 3a9bbc85e3 [HUE-9002](https://issues.cloudera.org/browse/HUE-9002) [fb] Get region of host as default for S3
* 02b86dd45b [HUE-9008](https://issues.cloudera.org/browse/HUE-9008) [hive] Add service when using thrift over http
* 319aea6373 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Simplify imports by handling logic in useradmin
* eaa808df09 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Handle forms import dependencies when off
* 8c4a4fb5b1 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Move user change forms swap logic directly into imports
* 46210b46ba [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Limit dump_config to desktop section
* 8653c4ddb5 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add default organization when creating a new user
* 347bb8f4e5 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Avoid 500 error on csrf missing on login page
* 8b80c65c57 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Port S3 proxy user lookup
* 9fc22defac [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Rename imports to not confict with models2
* a058348e5b [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support creating a new group
* ec83c29cd5 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support editing a group
* 3d9c49a2de [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support listing permissions
* 71647438c1 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support creating a new user
* a993516bb2 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support for Edit user page
* 672df534b9 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Port User and Group model switch everywhere
* 571cc7a13e [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Proper imports of get_defaut_group
* 19c02387b5 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Update link to Django session documentation
* f8b7722aea [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Plugged-in the HDFS files icons to the left menu
* 72c0cd6175 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Adding first part of Hive metastore connector
* d5c19346d4 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Plugged-in HDFS connector when activated
* d81c27b295 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add configuration of a HDFS connector
* f9d930b41b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Small code styling refactoring in lib fs
* ce4d359abd [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Semi-port to use the use_sasl property
* 6aad52a7dd [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Properly handle TypeError which does not contain message
* f4f55b4887 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Remove check for beeswax module as invalid syntax
* b9aa258dc9 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Workaround snappy and avro modules missing
* ec0409c37f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Workaround navoptapi module not present
* 237383cf2a [HUE-9006](https://issues.cloudera.org/browse/HUE-9006) [catalog] update Atlas api endpoint to enable hue-atlas integration
* 075b8ac0cb [HUE-9001](https://issues.cloudera.org/browse/HUE-9001) [editor] Move editor related actions to dropdown button underneath the editor and improve the layout in notebook 2
* c1b6a14297 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Add separate serializer for notebooks to support changed execution structure
* a22fd30ee2 [HUE-9001](https://issues.cloudera.org/browse/HUE-9001) [editor] Move snippet actions to underneath the editor in notebook 2
* 8e75f131bc [HUE-9001](https://issues.cloudera.org/browse/HUE-9001) [editor] Add ko component for controlling execution in notebook 2
* 55d387f46a [HUE-9001](https://issues.cloudera.org/browse/HUE-9001) [editor] Improve executor logic in notebook 2 when failing
* 5344841095 [HUE-9003](https://issues.cloudera.org/browse/HUE-9003) [k8s] Use session affinity in load balancing service
* 27040f10a7 [HUE-9003](https://issues.cloudera.org/browse/HUE-9003) [k8s] Move nginx to a side car in Hue container
* 8f055acbc8 [HUE-9003](https://issues.cloudera.org/browse/HUE-9003) [k8s] Move Hue from ReplicationControler to Deployment
* 327cfae259 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [docs] Add log collection and visualization in k8s
* 834f6f58d8 [HUE-8997](https://issues.cloudera.org/browse/HUE-8997) [importer] Support transaction table
* c50f89ddd1 [HUE-8999](https://issues.cloudera.org/browse/HUE-8999) [importer] Fix table already exists check
* a04c389557 [HUE-8998](https://issues.cloudera.org/browse/HUE-8998) [fb] Add test for S3 + IDBroker + Conf
* 7db91758d1 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [docs] Add design concepts for Organizations
* d39a4073af [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Fix import lost during the rebase
* 7a964afdd0 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Keep migrations like before
* e625bb103f [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Move model to models2.py
* 1a92ca9929 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Create get_organization(email) utilitly
* 4697e849db [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Backward compatibility in backend when no email set
* 201d7e65c3 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add property to get username as email value
* 3c46e00cd6 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add OrganizationGroups to OrganizationUser
* eb6662e1da [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Adding support to AllowFirstUserBackend
* 69b95fca95 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Adding create user and login forms
* da5f3d028d [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add new migrations with tweaks to models
* 249a115a84 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Remove ALL migrations
* e6aae4db7b [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Consolidate models together
* 22ecd2d2b3 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Tweak older migration to pass make_migration command
* 198b78da72 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Update references to User and Group classes
* 16ee30da14 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add switch to organizational groups and users
* 21f5e1a17c [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Skeleton of Organization model
* 14a1feab7f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] List some ideas of connectors to contribute
* 0d00f17b6d [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Add missing yaml servicemonitor template
* 813bcd1e49 [HUE-8908](https://issues.cloudera.org/browse/HUE-8908) [abfs] Fix permissions, rename, add chmod (#967)
* a254a96152 [HUE-8981](https://issues.cloudera.org/browse/HUE-8981) [editor] Add setup for headless testing of ko components and initial tests for sessionPanel
* 3977b8a40d [HUE-8992](https://issues.cloudera.org/browse/HUE-8992) [jb] Improve job listing status colors and visibility
* b75cb744eb [HUE-8988](https://issues.cloudera.org/browse/HUE-8988) [editor] Add export and import to query history tab
* 811c673349 [HUE-8988](https://issues.cloudera.org/browse/HUE-8988) [frontend] Extract import documents modal to a ko component
* b903bd708e [HUE-8790](https://issues.cloudera.org/browse/HUE-8790) [home] Remove inline search
* 36a2cb3f02 [HUE-8790](https://issues.cloudera.org/browse/HUE-8790) [sharing] Improve private link unfurling description
* cb84a0ca02 [HUE-8996](https://issues.cloudera.org/browse/HUE-8996) [core] Turn off django_prometheus migrations
* 476e26a46c [HUE-8946](https://issues.cloudera.org/browse/HUE-8946) [useradmin] Fix argument as list in import_ldap_user and import_ldap_group
* 6dad162a89 [HUE-8993](https://issues.cloudera.org/browse/HUE-8993) [core] Add supervisor based Hue process management inside docker container
* 8bc31d146c [HUE-8994](https://issues.cloudera.org/browse/HUE-8994) [catalog] get_catalog_url returns true when nothing configured in the ini
* 675aa91588 [HUE-8968](https://issues.cloudera.org/browse/HUE-8968) [core] Fix give previous traceback to PopupException
* e4412a982c [HUE-8993](https://issues.cloudera.org/browse/HUE-8993) [core] Add supervisor based Hue process management inside docker container
* 40eba71336 [HUE-8991](https://issues.cloudera.org/browse/HUE-8991) [autocomplete] Add support for file paths surrounded by double quotes
* 997bdf6064 [HUE-8990](https://issues.cloudera.org/browse/HUE-8990) [oozie] Fix issue with missing global viewModel variable in the workflow editor
* a68f442c1f [HUE-8981](https://issues.cloudera.org/browse/HUE-8981) [editor] Extract the session authorization modal from the editor view model to a separate component
* 22cf8ddbe9 [HUE-8981](https://issues.cloudera.org/browse/HUE-8981) [editor] Extract session handling from the editor view model
* 7b5b80b4d6 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Use ENABLE_NOTEBOOK_2 feature flag for split in editor html
* e75178afe5 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Extract notebook and snippet ajax calls to ApiHelper
* f6a60c9097 Fixed issue where not having the configuration for ABFS doesn't allow Hue to start (#964)
* 03916b59be [HUE-8983](https://issues.cloudera.org/browse/HUE-8983) [fb] Handle s3 with ListAllMyBuckets denied
* f6d655d611 [HUE-8987](https://issues.cloudera.org/browse/HUE-8987) [jb] Fix knox impala URL
* 85dd1064d8 [HUE-8945](https://issues.cloudera.org/browse/HUE-8945) [useradmin] Fix global_js_constants apps
* 145eff605b [HUE-8989](https://issues.cloudera.org/browse/HUE-8989) [editor] Fix missing editor assistant panel
* 976e54d788 [HUE-8978](https://issues.cloudera.org/browse/HUE-8978) [abfs] Fix Chmod, result export & editor autocomplete  (#962)
* 67105bf010 [HUE-8968](https://issues.cloudera.org/browse/HUE-8968) [core] Give previous traceback to PopupException
* 40ce21bc23 [HUE-8968](https://issues.cloudera.org/browse/HUE-8968) [core] Print more information on outbound HTTP request
* 4e7effde5d [HUE-8969](https://issues.cloudera.org/browse/HUE-8969) [catalog] Add more information on error
* bf4099d478 [HUE-8979](https://issues.cloudera.org/browse/HUE-8979) [jb] Fix Oozie spark jobs display an NoneType object is not iterable
* 03cb53e847 [HUE-8978](https://issues.cloudera.org/browse/HUE-8978) [doc] Update docs for ABFS / GCS
* d276904f77 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add more details on the CI and integration tests
* 21dfc367d4 [HUE-8976](https://issues.cloudera.org/browse/HUE-8976) [libsaml] Change default to avoid SignatureError Signature missing for response
* b257bdca55 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Update next step for better tracing
* 19465b0de3 [HUE-8978](https://issues.cloudera.org/browse/HUE-8978) [core] Adding socks module to ext-py
* b27b3cdf00 docs
* a0d7cd1ea8 [HUE-8978](https://issues.cloudera.org/browse/HUE-8978) [fb] First commit for Google Storage support.
* ab639af720 [HUE-8978](https://issues.cloudera.org/browse/HUE-8978) [fb] Adding Google Cloud authentication dependencies
* b265ff93e5 [HUE-8977](https://issues.cloudera.org/browse/HUE-8977) [fb] Minor fix for going to the next or previous page (#956)
* cd8ab9c8ed [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Adding opentracing lib
* 582c681e9d [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Adding jaeger-client to extpy
* a887eda542 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Adding django_opentracing lib to extpy
* 03384815dc [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Add tracing to notebook API close_statement
* 09a1ff0d7f [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Add traces with query and used ids to notebook API
* affecc1a44 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Adding ini configuration
* 8b676510e4 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Disable global logging of each trace
* e52eee3590 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Fix typo in function decorator
* 9a8f8029b0 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Rename execution tags
* f3bb1c4b7d [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Convert api_error_handler with @wraps function
* 81216517cc [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Convert check_document_access_permission with @wraps function
* 047e1782f2 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Add span for additional trace in execute
* a7cf79720b [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Add query id to execute statement trace
* d5832d868a [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [tracing] Adding OpenTracing app
* b7ce984d0a [HUE-8975](https://issues.cloudera.org/browse/HUE-8975) [metastore] Only show engine dropdown is there are more than one
* 38a59bb18a [HUE-8974](https://issues.cloudera.org/browse/HUE-8974) [tb] Fix drop database and table actions
* f56a58129e [HUE-8973](https://issues.cloudera.org/browse/HUE-8973) [tb] Fix reload button for the table listing
* c8e5273590 [HUE-8943](https://issues.cloudera.org/browse/HUE-8943) [menu] Update icons for Job Browser
* 2e06723798 [HUE-8947](https://issues.cloudera.org/browse/HUE-8947) [docs] Updating Editor screenshot with 4.5 version
* 1b7773eaad [HUE-8962](https://issues.cloudera.org/browse/HUE-8962) [core] Remove the embedded mode from API
* 867922f797 [HUE-8967](https://issues.cloudera.org/browse/HUE-8967) [search] Fix broken marker map widget
* fa22c3287f [HUE-8966](https://issues.cloudera.org/browse/HUE-8966) [assist] Fix document type filter triggered from apps
* 2990d2bc6c [HUE-8965](https://issues.cloudera.org/browse/HUE-8965) [frontend] Remove draggable functionality from the top search results
* 5fd68212af [HUE-8970](https://issues.cloudera.org/browse/HUE-8970) [catalog] Avoid long empty description column in sample popup
* dcb3ad2325 [HUE-8970](https://issues.cloudera.org/browse/HUE-8970) [core] Remove ANALYTIC_DB flag from the server
* a633b37afa [HUE-8970](https://issues.cloudera.org/browse/HUE-8970) [sqlalchemy] Avoid TypeError is not JSON serializable on column sample popup
* cad67da615 [HUE-8963](https://issues.cloudera.org/browse/HUE-8963) [frontend] Prevent leaking viewModel in the global js scope
* 76e452b67e [HUE-8962](https://issues.cloudera.org/browse/HUE-8962) [core] Remove the frontend embedded mode
* c8a49bd575 [HUE-8959](https://issues.cloudera.org/browse/HUE-8959) [autocomplete] Update the Impala parser to support new GRANT and REVOKE syntax
* b6492890d6 [HUE-8958](https://issues.cloudera.org/browse/HUE-8958) [editor] Honor the closest preceding USE statement when executing and editing statements
* 071c1f0d08 [HUE-8790](https://issues.cloudera.org/browse/HUE-8790) [sharing] Cursor pointer is missing in Editor button
* 9d47818cb8 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [docs] Add flower to task server documentation
* f2319e3413 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [docs] Move Kubernetes roadmap item to done
* a7e4c597b9 PR951 [docs] Presto over HTTPS from HUE throws SSL Exception (#951)
* 03981c392e [HUE-8945](https://issues.cloudera.org/browse/HUE-8945) [importer] Metadata app should not be blacklistable
* 11926fc14e [HUE-8882](https://issues.cloudera.org/browse/HUE-8882) [impala] Fix get_hive_metastore_interpreters filtering
* b45f39f25d [HUE-8926](https://issues.cloudera.org/browse/HUE-8926) [frontend] Update the app switcher icons and URLs
* 4ff4fb110c [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/core/src/desktop for Python 3.5
* 0c24379e97 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/notebook for Python 3.5
* b368a07152 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/libzookeeper for Python 3.5
* bd839631ea [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/libsolr for Python 3.5
* 3689b66a3d [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/libsentry for Python 3.5
* 6a62bc3927 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/libsaml for Python 3.5
* 9301554843 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/librdbms for Python 3.5
* 6a952d7d37 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/libopenid for Python 3.5
* 43a84e8184 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/liboozie for Python 3.5
* b62de27428 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/liboauth for Python 3.5
* aacc862e9e [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/libanalyze for Python 3.5
* 8930373b1d [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/kafka for Python 3.5
* 11ff9648e1 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/indexer for Python 3.5
* e476ead4f2 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize desktop/libs/hadoop for Python 3.5
* 57fb03fe2c [HUE-8949](https://issues.cloudera.org/browse/HUE-8949) [catalog] Add support for atlas-application.properties
* 51e6f32954 [HUE-8856](https://issues.cloudera.org/browse/HUE-8856) [autocomplete] login_notrequired for dynamic_bundle
* cbfeb03b73 [HUE-8953](https://issues.cloudera.org/browse/HUE-8953) [jb] Allow user to kill DDL Impala query
* 99942b87f9 [HUE-8952](https://issues.cloudera.org/browse/HUE-8952) [editor] Fix close_statement
* 7e1407adce [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Futurize tools/app_reg for Python 3.5
* ba725f3bb0 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Add logger for boto
* d4bac9d0dd [HUE-8948](https://issues.cloudera.org/browse/HUE-8948) [hive] Fix INSERT data into customer table which is partitioned
* 87d8f648eb [HUE-8948](https://issues.cloudera.org/browse/HUE-8948) [impala] Fix errors in sample data of table samples
* c42dd534e8 [HUE-8948](https://issues.cloudera.org/browse/HUE-8948) [hive] Skip customer query if transactional table
* 4fd0f32fa6 [HUE-8948](https://issues.cloudera.org/browse/HUE-8948) [hive] Skip customer table for now as nested types
* 2c1c3905e4 [HUE-8948](https://issues.cloudera.org/browse/HUE-8948) [hive] Support transaction tables as examples
* e999cb92f7 [HUE-8948](https://issues.cloudera.org/browse/HUE-8948) [hive] Pick-up if transactional table support from hive-site.xml
* fae59a5bc1 [HUE-8908](https://issues.cloudera.org/browse/HUE-8908) [fb] ABFS in Hue (#932)
* 5bf976c00c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [hdfs] Remove warning about not being a hdfs superuser
* e28e4deaad [HUE-8948](https://issues.cloudera.org/browse/HUE-8948) [beeswax] Properly name dbms test file
* 6a10e983d6 [HUE-8950](https://issues.cloudera.org/browse/HUE-8950) [core] Fix error of saving copied document (#886)
* ba8d960b77 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Fix AWS IDBroker expiration.
* d5e9460c8a [HUE-8949](https://issues.cloudera.org/browse/HUE-8949) [catalog] Add kerberos support to Atlas
* e573871a68 [HUE-3228](https://issues.cloudera.org/browse/HUE-3228) [editor] Add test for column name backtick escapating
* c9f9ebad63 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [connectors] Remove old reference to is_k8s cluster in create session
* 60ad6b6bd5 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [oozie] Do not 500 on new workflow page when HDFS is not accessible
* cc98c704e5 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [oozie] Update link to cron syntax scheduler
* 902d9e6d92 [HUE-3228](https://issues.cloudera.org/browse/HUE-3228) [notebook] Proper dedentation of SQL sample generated code
* 4fd345cef1 [HUE-3228](https://issues.cloudera.org/browse/HUE-3228) [dashboard] Add other engine that does not support backticks
* 7dc14772a0 [HUE-3228](https://issues.cloudera.org/browse/HUE-3228) [dashboard] Display grid result automatically when browsing a table
* d522467fa4 [HUE-3228](https://issues.cloudera.org/browse/HUE-3228) [dashboard] Support opening other databases than the fist one
* 39367d4271 [HUE-3228](https://issues.cloudera.org/browse/HUE-3228) [dashboard] Non hardcoded backticks
* 717c49212e [HUE-8943](https://issues.cloudera.org/browse/HUE-8943) [importer] Avoid 500 error when filebrowser is not configured
* a1553605b8 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Tweak default configs to avoid service errors out of the box
* 7869f13c1e [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Add a proper flag to enable the stats emailing cron job
* 86603bd65d [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Clean-up and Remove local mysql database interpreter from helm values
* 8f9802cc22 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Rename hue-postgres service to postgres-hue
* c7cacf7bf3 [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Add servicemonitor yaml template
* 00da0656db [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Updating hostname and cert-manager URL configs
* 160663d562 [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [design] Adding list of tracing follow-ups items
* 0507ab111c [HUE-8936](https://issues.cloudera.org/browse/HUE-8936) [docs] Adding Tracing to the Roadmap
* a4478f48ca [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Assign unique id when loading initial ones
* fd7467b21c [HUE-8882](https://issues.cloudera.org/browse/HUE-8882) [editor] Replace invalidate on DDL with clearCache
* 48a82fb4a2 [HUE-8750](https://issues.cloudera.org/browse/HUE-8750) [useradmin] Fix 404 after creating a user.
* 1c499788f7 [HUE-8925](https://issues.cloudera.org/browse/HUE-8925) [fb] Fix config validation for Hive & AWS.
* c9d788b76f [HUE-8947](https://issues.cloudera.org/browse/HUE-8947) [docs] Perform 4.5 release

### Contributors

This Hue release is made possible thanks to the contribution from:

* 10sr
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
* batou9150
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
* sandeepreddy3647
* Santiago Ciciliani
* Scott Kahler
* Sean Mackrory
* Shahab Tajik
* Shawarma
* Shawn Van Ittersum
* Shin So
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
* TAK LON WU
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
