---
title: "4.8.0"
date: 2020-09-23T00:00:00+00:00
draft: false
weight: -4080
tags: ['skipIndexing']
---

## Hue v4.8.0, released September 23rd 2020

Hue is an open source SQL Cloud Assistant for developing and accessing [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/)/Data Apps and collaborating: http://gethue.com


### Summary

This release brings all these improvements on top of [4.7](https://gethue.com/blog/hue-4-7-and-its-improvements-are-out/).

Download the [tarball](https://cdn.gethue.com/downloads/hue-4.8.0.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.8.0.zip) releases.

#### SQL
  * Initial support of Flink, Phoenix, SparkSql SQL dialects
  * Parser refactoring to make Apache Calcite grammar improvements easier
  * Navigate Foreign Keys, Schedule Queries, Smart Suggestions Preview...
  * [Read more](https://gethue.com/blog/sql-querying-improvements-phoenix-flink-sparksql-erd-table/)

{{< youtube fKHD-fOdDY0 >}}

{{< youtube 4xgjvM51Rnw >}}

#### Components

* New component framework:
  * ERD table
  * SQL Parser
  * SQL Scratchpad in progress

![ERD Table Components](https://cdn.gethue.com/uploads/2020/09/erd_table_viz.png)

* Registries for npm, Docker
  * https://www.npmjs.com/package/gethue
  * https://github.com/cloudera/hue/packages/

#### API

New documentation on how to perform these operations via [REST](https://gethue.com/blog/rest-api-execute-sql-queries-browse-files/):
* Execute SQL queries
* List or Download files
* Importe some CSV data into a new SQL table

![Curling Hue API](https://cdn.gethue.com/uploads/2020/09/hue-curl.png)

#### Misc

* Username max length is 150 chars now.
* Impala profile can be downloaded/copied
* SqlAlchemy support of additional arguments:
  * Sessions/engine
  * iImpersonation
  * Json credentials (e.g. BigQuery)
  * LDAP credentials (e.g. Presto)
* CI:
  * [Python linting and Commit names checks](https://gethue.com/automated-checking-python-style-and-title-format-of-git-commits-continuous-integration/)
  * [JavaScript licenses checks](https://gethue.com/automated-checking-javascript-licenses-absolute-paths-continuous-integration/)
* Python 3.8 support and many other Python 3 fixes
* S3 custom home path
* Quickstart [Hue in Docker](https://gethue.com/quickstart-hue-in-docker/) and query any of your Database
* New [Grafana templates](https://gethue.com/monitoring-hue-activity-with-grafana-dashboards/)
* New dev onboarding process docs
* [How to login](https://gethue.com/blog/how-to-configure-hue-to-use-knoxspnegodjango-backend/) with Apache Knox in a secure cluster

#### Preview

* [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) The new version of the Editor with multi execution contexts got 50+ commits and is in beta
* [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) SQL connectors configuration API instead of using hue.ini is in beta
* [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) Sections of the private API were documented while the public API is getting scoped
* [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) Python 3 compatibilities has been added to the importer, wsgiserver and Oozie scheduler

### Compatibility

Runs on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7), and Ubuntu 18.04 and 20.04.

Supported Browsers:

Hue works with the two most recent versions of the following browsers.

* Chrome
* Firefox LTS
* Safari
* Microsoft Edge

Runs with Python 2.7+. 3.6+.


### List of commits

* f017739444 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [release] Perform 4.8 release
* 235e7f4ba3 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [docs] Update README screenshot with 4.8
* a176efb0fd [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [release] Adding the 4.8 release notes
* e9324a0308 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [blog] 4.8 release post
* 69b8b662b0 [HUE-9477](https://issues.cloudera.org/browse/HUE-9477) [ci] Allow rebase on master in Pull Requests
* 3933571b28 [HUE-9483](https://issues.cloudera.org/browse/HUE-9483) [test] Adding pytest libs to requirements.txt
* 15a321b919 [HUE-9483](https://issues.cloudera.org/browse/HUE-9483) [test] Adding pytest configuration
* cf328f371d [HUE-9483](https://issues.cloudera.org/browse/HUE-9483) [test] Adding pytest-django compatible with Python 2
* 95a2d35f15 [HUE-9483](https://issues.cloudera.org/browse/HUE-9483) [test] Adding pytest 4.6 compatible with Python 2
* 739cc9e746 [HUE-9482](https://issues.cloudera.org/browse/HUE-9482) [ui] Add queries interface in Job Browser
* 369b2986cc [HUE-9455](https://issues.cloudera.org/browse/HUE-9455) [filebrowser] part-1 File system user home directory is wrong in S3 only configuration
* 802bfe24e3 [HUE-9476](https://issues.cloudera.org/browse/HUE-9476) [importer] Indexer file format guess API call errors with Python 3
* 481393a563 [HUE-9468](https://issues.cloudera.org/browse/HUE-9468) [phoenix] Pull phoenixdb module from pypy with Python 3
* 82f132a2b7 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Renaming Hue to Hue Editor
* afd4601b77 [HUE-9477](https://issues.cloudera.org/browse/HUE-9477) [indexer] SQL code formatting errors with StopIteration with Python 3
* b196a43762 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [blog] SQL improvements overview in 4.8
* e48f518a8d [HUE-9475](https://issues.cloudera.org/browse/HUE-9475) [core] Add JCEKS keystore reading capability in Hue (#1268)
* 0a1e9128ce [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [blog] Adding image to API blog post
* 5616dba057 [ci] Skip wsgiserver.py from the CI (#1244)
* 99ad0fde71 [core] Add back Python 3 compatibility to wsgiserver (#1244)
* d9a0662d87 [core] Revert re-formating of wsgiserver (#1244)
* e02ef1e5d3 [oozie] Fix workflow graph rendering with Python 3 - part 2 (#1262) (#1267)
* 5c1b422d6e [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [docs] Refresh REST API with more details on the authentication
* 02369f7774 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [blog] REST API for sending SQL queries and browsing files
* c8b7ba97bf [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [blog] Consolidate 4.6 version tag into the global 4
* e996974da1 [HUE-9474](https://issues.cloudera.org/browse/HUE-9474) [importer] Error with Python 3 when trying to upload file to S3 bucket
* fbbc08ce22 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Update backend to get proper connector type id
* 4627408002 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Update Flink connector URL
* c68dea5f5e [HUE-9468](https://issues.cloudera.org/browse/HUE-9468) [ui] Empty database cannot be open in Browser as link is on empty string
* fca954f03b [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [docs] Add SQL prefix to the Scratchpad component page
* 01c1594965 [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [docs] Display the TOC on the API page
* 6399333863 [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [docs] Document the current Execute Query API
* 9079de385d [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [docs] Document the File Importer API with curl
* 71e7b87684 [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [docs] Document the File Browser API with curl
* 82eebc416c [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [docs] Document the API authentication with curl
* 238846f9b8 [HUE-9473](https://issues.cloudera.org/browse/HUE-9473) [flink] Listing table column fails with release 0.2
* 4d72314392 [oozie] Fix workflow graph rendering with Python 3 (#1262) (#1266)
* b4b515b700 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Updating the Flink SQL gateway setup instruction
* 845403de65 [desktop] Fix oozie api when Py3 is used (#1262) (#1263)
* 8a5731c1ba [HUE-9464](https://issues.cloudera.org/browse/HUE-9464) [editor] Add Hive parser support for DROP SCHEDULED QUERY
* cff3b41bdd [HUE-9464](https://issues.cloudera.org/browse/HUE-9464) [editor] Add Hive parser support for ALTER SCHEDULED QUERY
* 6356585cdc [HUE-9464](https://issues.cloudera.org/browse/HUE-9464) [editor] Add Hive parser support for CREATE SCHEDULED QUERY
* ab96d016cb [HUE-9464](https://issues.cloudera.org/browse/HUE-9464) [editor] Update Hive ALTER parser with the latest syntax
* a12a075ae9 [HUE-9464](https://issues.cloudera.org/browse/HUE-9464) [editor] Update TRUNCATE syntax for the Hive parser
* 298d58ac70 [HUE-9464](https://issues.cloudera.org/browse/HUE-9464) [editor] Add support for MANAGEDLOCATION in the Hive parser
* 798b247de7 [desktop] Fix code not compatible with py3 (#1239) (#1260)
* 5e83f68915 [HUE-9455](https://issues.cloudera.org/browse/HUE-9455) [filebrowser] part-1 File system user home directory is wrong in S3 only configuration
* f72022a938 [HUE-9455](https://issues.cloudera.org/browse/HUE-9455) [filebrowser] part-2 fixed the bug of manual refresh button
* 84e3d1870e [HUE-9465](https://issues.cloudera.org/browse/HUE-9465) [editor] Update the Hive documentation to the latest version
* 59e3a54196 [HUE-9465](https://issues.cloudera.org/browse/HUE-9465) [editor] Update paths in the Hive documentation extractor
* a0f4372dd1 [HUE-9466](https://issues.cloudera.org/browse/HUE-9466) [impala] Use Impala as the name of the editor when FENG is on
* 53a004339f [HUE-9466](https://issues.cloudera.org/browse/HUE-9466) [impala] Avoid Cannot parse job IDs for execution engine impala
* c04d89a277 [core] Fix some code not compatible with python 3 (#1244)
* aa45633e79 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Allow rebase commit message in pull requests
* 44b3e9ef72 [HUE-9461](https://issues.cloudera.org/browse/HUE-9461) [editor] Update the Impala documentation to the latest version
* 181f650a21 [HUE-9461](https://issues.cloudera.org/browse/HUE-9461) [tools] Fix the sql reference generator tool for Impala
* dc6e28041f [HUE-9463](https://issues.cloudera.org/browse/HUE-9463) [assist] Fix js exception in the reference repository for non-defined dialects
* c601ba99a1 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Use the default editor if not specified in the URL in editor v2
* 8cad54283c [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Fix issue with constant spinner in autocompletion of popular entries
* 85c6f5f386 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Send the actual snippet and notebook for executables in the editor
* 866cf29236 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Include the raw statement when executing in editor v2
* 7b8cfe9b8f [HUE-9454](https://issues.cloudera.org/browse/HUE-9454) [editor] Always resolve promises in the autocompleter when closed or re-opened
* d4ffa8332e [HUE-9457](https://issues.cloudera.org/browse/HUE-9457) [importer] Improve visibility of path input in the importer file chooser
* 259136abba [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Implement variable substitution in editor V2
* 08ea596d88 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Make sure executable ID doesn't change after loading from history in editor v2
* d5d7211729 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Set initial handle optionals and add session verification in editor v2
* 24578d96b8 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Clean up editor V2 execution logic and enable roundtrip test
* 2b7b7b97ce [HUE-9454](https://issues.cloudera.org/browse/HUE-9454) [editor] Make it possible to define reserved keyword per dialect
* beadebba66 [HUE-9454](https://issues.cloudera.org/browse/HUE-9454) [editor] Refactor the autocompleter to use async/await instead of jQuery deferred
* 526e74ffae [HUE-9408](https://issues.cloudera.org/browse/HUE-9408) [ui] Column comments are not displayed in Table browser
* 35d3e9fdb0 [HUE-9458](https://issues.cloudera.org/browse/HUE-9458) [ui] UI build - Support custom webpack config files (sree)
* 307cdec392 [HUE-9460](https://issues.cloudera.org/browse/HUE-9460) [ui] HiveQueryPlan - Split Vue component and web-component wrapper (sree)
* 09ae1da0bc [HUE-9454](https://issues.cloudera.org/browse/HUE-9454) [editor] Use the identifier escape char from the connector properties in the editor
* f569327cfa [HUE-9449](https://issues.cloudera.org/browse/HUE-9449) [tb] Use the last active editor or assist database as default when opening the table browser from the left nav
* 4ab093738b [HUE-9459](https://issues.cloudera.org/browse/HUE-9459) [editor] Make sure return types are unique when UDFs are merged
* 0f1315f6dc [HUE-9459](https://issues.cloudera.org/browse/HUE-9459) [editor] Set a max width on the autocomplete meta column in the suggestions
* 07f1909a8f [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract and split DESCRIBE, INSERT, MERGE, SET and UPDATE for Hive and Presto
* 3bd95c2484 [HUE-9449](https://issues.cloudera.org/browse/HUE-9449) [tb] Include connector id in "Open in table browser" links
* 7c49cf4c36 [HUE-9445](https://issues.cloudera.org/browse/HUE-9445) [docker] Adding modules for Phoenix connector
* a63f69088b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Format onboarding to be easier to read
* cdbc212ae3 [HUE-9453](https://issues.cloudera.org/browse/HUE-9453) [docs] Refresh the docker How To
* e1a9ed258d [HUE-9453](https://issues.cloudera.org/browse/HUE-9453) [blog] Quickstart Hue in Docker and query any of your Database
* ea739b2082 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Upper case ER diagram name
* c819792658 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [docs] Add the concept of structure.json syntax modules
* 6332c98626 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Remove duplicated post
* cdbe8ae145 [HUE-1246](https://issues.cloudera.org/browse/HUE-1246) [presto] Support additional arguments for pyhive sqlalchemy library (#1250)
* 13f33561d4 [HUE-9451](https://issues.cloudera.org/browse/HUE-9451) [blog] Adding python syntax and commit title checking to CI
* 9ffaab59cb [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactor the component registry sections
* df74ef0e59 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Docker ini example styling
* 89dc3f6d0b [HUE-9452](https://issues.cloudera.org/browse/HUE-9452) [core] Python2 no longer compile because of ipython and traitlets
* abee0ba12f [HUE-9451](https://issues.cloudera.org/browse/HUE-9451) [blog] CI for python lint and git commit format
* 172e34be7d [HUE-9451](https://issues.cloudera.org/browse/HUE-9451) [ci] Split pytlint and commit format checks into sections
* c4c77540ee [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Clean-up of the database op section
* 0ee86e9203 [HUE-9450](https://issues.cloudera.org/browse/HUE-9450) [k8s] Add checksum of both ini configs
* 19831a70b5 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [pylint] Get linting return code result just after the linting
* a5cfb6e85c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Fix wrong prefix for AWS section in config map
* 7b46ca50ac [HUE-9450](https://issues.cloudera.org/browse/HUE-9450) [jb] Avoid failure to start when app is blacklisted
* ece65d4c43 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Do not use localhost in nginx config map
* b69a9d9917 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract and split GRANT, REVOKE, LOAD, IMPORT, MSCK and EXPORT for Hive and Presto
* afc9105efd [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract and split CREATE for Hive and Presto
* c5dbbf3752 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract and split ALTER, SHOW and DROP for Hive and Presto
* a5a994c7df [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Split Impala SELECT grammar and reduce duplication with the generic parser
* 94875014af [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Split Impala UDF grammar and reduce duplication with the generic parser
* 157385d93b [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract SHOW and UPDATE into separate grammar files for Impala
* 7506957ace [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract INSERT, UPSERT and SET into separate grammar files for Impala
* c4750f8f45 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract GRANT, REVOKE and LOAD into separate grammar files for Impala
* 082b1c7bb4 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Expect api to run on standart port 8888
* cef644d603 [HUE-9447](https://issues.cloudera.org/browse/HUE-9447) [ci] Allow more than one digit number to github PR
* f8986b9a26 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [ci] Sync-up the .pylintrc
* e4afbb8288 [HUE-9447](https://issues.cloudera.org/browse/HUE-9447) [ci] Add pip install of pylint and pylint_django
* e0abb85a76 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [ci] Extract the git home path so that it is not hardcoded
* c5e0dd2e66 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [ci] Whitelist demo.gethue.com links for now
* 8f0c1f038a [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [ci] Make sure that failing lints fail the CI
* 7c4bfdb85f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Disable monitoring and tracing by default
* e69c1d9218 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix typos in the code review section
* 7b81844696 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Moving how to register components to main section
* 030bebae78 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Move the parser component section to its own page
* 1522399d76 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh the website install instructions
* f4a10466fc [HUE-9423](https://issues.cloudera.org/browse/HUE-9423). [editor] Parser demo app build is failing with gethue (sree)
* b433b9285e Merge branch 'master' into ci-commit-master-ayush
* 96aba14cf3 [HUE-9445](https://issues.cloudera.org/browse/HUE-9445) [phoenix] Listing table sample in Table Browser errors
* e1ef3bd769 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [pylint] Move .pylintrc to repo root
* 9edcbd254b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Show how to use credentials with SqlAlchemy
* 5483984624 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [docs] Reference the commit message hooks
* de26b79603 [HUE-9446](https://issues.cloudera.org/browse/HUE-9446) [docs] Add linter config files locations
* 1acafd5743 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [ci] Running both linters in the repo
* 2aada27088 [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [ci] Add commit message check to the ci
* cb8512489a [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [ci] Adding script to validate commit messages
* 50d533053f [HUE-9447](https://issues.cloudera.org/browse/HUE-9447) [ci] Check for commit message
* dd0100915b [HUE-9371](https://issues.cloudera.org/browse/HUE-9371) [pylint] Add 3 rules to get started
* e80a41bb43 CDPD-15032 [metastore] Drop selected Databases errors
* e638982a12 [HUE-9446](https://issues.cloudera.org/browse/HUE-9446) [ci] Add python linting to the ci
* cdea845d9a [HUE-9446](https://issues.cloudera.org/browse/HUE-9446) [ci] Improve Python lint checking detection script
* a7c02b8798 [HUE-9374](https://issues.cloudera.org/browse/HUE-9374) [impala] Use 26000 as default for thrift-over-http
* 59dd1d13f0 [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [lib] Get addendum for 2 bugs in PHOENIX-5994
* e0d6825e6b [HUE-9444](https://issues.cloudera.org/browse/HUE-9444) [notebook] Teradata and Athena jdbc interfaces are not working (#1240)
* 954aa6bc9b [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Remove intermediary parser rules for each statement type to improve pluggability
* aaa697307f [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract and split DROP statements for the impala parser
* 2f509089c8 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract and split CREATE and analyze type statements for Impala
* e332d3304e [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Fix issue with structure definition of hive related parsers
* 28da7be2e6 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract and split ALTER for Impala
* e7c494a72b [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Delete old unused jison files
* 605abaa154 [livy] Add numExecutors options (#1238)
* 15eaa59861 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add note about phoenix connector and Python 3
* f00377a7eb [HUE-9441](https://issues.cloudera.org/browse/HUE-9441) [editor] Don't suggest empty database in the autocomplete
* c7009e8ea3 [HUE-9441](https://issues.cloudera.org/browse/HUE-9441) [editor] Support empty database URLs for Notebook and Table Browser APIs
* 557d631355 [HUE-9441](https://issues.cloudera.org/browse/HUE-9441) [editor] Switch to empty string when there's no database name for Phoenix
* a07a74659f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adjust path for phoenix connector example
* 4765f2f28b [HUE-9434](https://issues.cloudera.org/browse/HUE-9434) [jb] Fix issue in getting the logs if the job had failed
* 4e10db173b [HUE-9435](https://issues.cloudera.org/browse/HUE-9435) [aws] Fix issue with aws behind proxy and make S3_USE_SIGV4 default when region is set
* 111416a2bf [HUE-9432](https://issues.cloudera.org/browse/HUE-9432) [core] Detect if chardet is installed
* 19e43ee69a [HUE-9433](https://issues.cloudera.org/browse/HUE-9433) [assist] Fix exceptions in the UDF assist filter
* 6c5f768841 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Remove all duplication from the Calcite parser
* eba122bd89 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Split out all the UDFs and make most of the statements pluggable via structure.json in the generic parser
* c8030b46d6 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Split ALTER, CREATE and DROP into parts for the generic parser
* bafbb8ea9e [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Merge the generic2 parser back into generic
* 5a6af42023 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract cte, joins, from and union to separate grammar files for the generic 2 parser
* 8e0cc1a4e2 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract the generic 2 select conditions to separate jison files
* b39e355563 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Extract SELECT grammar to a separate file in generic 2
* 8fcc5660d3 [HUE-9429](https://issues.cloudera.org/browse/HUE-9429) [editor] Introduce a new generic2 parser as base for improved structure
* ed834efc38 [HUE-9425](https://issues.cloudera.org/browse/HUE-9425) [ui] Fix issue with rendering dynamic bundles in the login page
* e4c296b743 [HUE-9425](https://issues.cloudera.org/browse/HUE-9425) [ui] Don't throw exception when detecting bundles if webpack isn't ready
* 542f0f6bfb [HUE-9425](https://issues.cloudera.org/browse/HUE-9425) [ui] Automatically detect and load webpack chunks per app
* fdf029bf1e [HUE-9425](https://issues.cloudera.org/browse/HUE-9425) [ui] Fix issue with the CleanWebpackPlugin trying to clean the wrong folder
* d91655b458 [HUE-9409](https://issues.cloudera.org/browse/HUE-9409) [docs] Add the Development Process to development guide
* 4bf7ed0ac7 [HUE-9409](https://issues.cloudera.org/browse/HUE-9409) [blog] Fix links and bad formatting in the code review blog post
* 58d8e23599 hue-9409-RBTools
* e10ddd1abd [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Harmonize link sections in developer index
* 086395e9ae [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Reorganize the list of dependencies
* 181e5afdb8 [parser] Handle partition columns only in Impala insert statement (#1231)
* 7af5cced77 [HUE-9373](https://issues.cloudera.org/browse/HUE-9373) [core] Rename keytab_reinit_frequency variable at Python level
* 89d4bded51 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding example of ops command to reset a user password
* 6b7060ad50 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Give output of the command listing
* bdcab12926 Revert "[HUE-9373](https://issues.cloudera.org/browse/HUE-9373) [core] keytab_reinit_frequency is ignored in hue.ini (#1161)"
* a4a734312b [HUE-9425](https://issues.cloudera.org/browse/HUE-9425) [ui] Fix issue with bundle loading in table and job browser
* a7ebd79d88 Bump elliptic from 6.5.2 to 6.5.3 (#1229)
* 8394ac0f39 [HUE-9426](https://issues.cloudera.org/browse/HUE-9426) [doc] Exclude gethue content from 'make docs'
* faf09df471 [HUE-9422](https://issues.cloudera.org/browse/HUE-9422) [core] Apply HUE-9045 on requests-2.23.0
* d2a2298599 [HUE-9421](https://issues.cloudera.org/browse/HUE-9421) [core] Remove ext lib chardet-3.0.4 * revert partial commit of PR 1095
* 8ba5f91a66 [HUE-9428](https://issues.cloudera.org/browse/HUE-9428) [editor] Fix issue where the syntax parsers fails parsing statements with UDFs
* 2b63f2e617 [HUE-9427](https://issues.cloudera.org/browse/HUE-9427) [ui] Fix the hue_dep API example
* 27e0109470 [docs] Fix some typographical errors (#1228)
* 7ff706e96e [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [phoenix] Handle empty DB as ' ' (not 'NULL'?)
* 76bd01532c [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [lib] Update phoenixdb with PHOENIX-5994
* 66fdfa46a8 [HUE-9381](https://issues.cloudera.org/browse/HUE-9381). ERD - Add event listeners for all entities (sree)
* 8ede4cd9e9 [HUE-9420](https://issues.cloudera.org/browse/HUE-9420) [ui] Limit webpack chunk name length
* 210c557935 [HUE-9381](https://issues.cloudera.org/browse/HUE-9381). ERD - Hide current DB name in table box (sree)
* cf7e3ccb03 [HUE-9381](https://issues.cloudera.org/browse/HUE-9381). ERD - Add className based styling for each entity (sree)
* 745126ba90 [HUE-9381](https://issues.cloudera.org/browse/HUE-9381). ERD - Table box interaction changes (sree)
* 35ed72d6cc [HUE-9381](https://issues.cloudera.org/browse/HUE-9381). Replace Relationships tab with ERD (sree)
* 524c489d07 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix hue dependency path in the parser demo project
* 6d07836395 [HUE-8390](https://issues.cloudera.org/browse/HUE-8390) [hive] Use database instead of schema for argument names
* 0faba5c6e3 [HUE-8390](https://issues.cloudera.org/browse/HUE-8390) [hive] Rename getStatus() to get_status()
* 434138a479 [HUE-8390](https://issues.cloudera.org/browse/HUE-8390) [hive] Implement Get Primary Keys via Thrift GetPrimaryKeys
* 4509256382 [HUE-8390](https://issues.cloudera.org/browse/HUE-8390) [hive] Implement Get Foreign Keys via Thrift TGetCrossReferenceReq
* c2b92df630 [doc] Fix typo in install section (#1216)
* 952cafb4d3 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding link to Python API in the Operation section
* e13e9b5b86 [HUE-9418](https://issues.cloudera.org/browse/HUE-9418). [docs] Tech to render web components in docs (sree)
* dd68c85d4e [HUE-9414](https://issues.cloudera.org/browse/HUE-9414). Remove style tags in ERD demo app (sree)
* b10c9fcda8 [HUE-9381](https://issues.cloudera.org/browse/HUE-9381). [ui] ERD: Add fallback for font awesome (sree)
* c50b3c4f53 [HUE-9414](https://issues.cloudera.org/browse/HUE-9414) [npm] Adding screenshots to each category
* 71befaf166 [HUE-9414](https://issues.cloudera.org/browse/HUE-9414) [docs] Clean-up the release checklist
* ee67ff180a [HUE-9414](https://issues.cloudera.org/browse/HUE-9414) [npm] Add some description and keywords
* 6cc1169078 [HUE-9368](https://issues.cloudera.org/browse/HUE-9368). [docs] Fix for runserver stopping abruptly (sree)
* 353fd2c29d [HUE-9417](https://issues.cloudera.org/browse/HUE-9417). Make NPM-README generic (sree)
* 586e332b10 [HUE-9414](https://issues.cloudera.org/browse/HUE-9414). Fixed parse path in npm package (sree)
* 600d245852 [HUE-9415](https://issues.cloudera.org/browse/HUE-9415) [impala] Adding default value to daemon_api_auth_scheme in inis
* 61a92137ae [HUE-9415](https://issues.cloudera.org/browse/HUE-9415) [impala] Support connecting to Impala's webui with basic auth (#1214)
* 2155207715 [HUE-9417](https://issues.cloudera.org/browse/HUE-9417). [docs] Introduce the Web components (sree)
* bf2a8467d9 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactoring and simplifying the quick start guide
* 054c26fe75 [HUE-8020](https://issues.cloudera.org/browse/HUE-8020) [core] Increase username length to 150 characters (#1208)
* fe4aba768c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Promote more the quick docker dev setup
* 5d382e8e84 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Rewrite the dev onboarding to be simpler
* d47543208c [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] Adding test suites for the Hive dialect
* 1649459b6d [HUE-9416](https://issues.cloudera.org/browse/HUE-9416) [doc] Add SLES 12 dependencies
* cabdc5e3a2 [HUE-9414](https://issues.cloudera.org/browse/HUE-9414). [ui] Add ERD demo app (sree)
* cefe6179e3 [HUE-9414](https://issues.cloudera.org/browse/HUE-9414). [ui] Publish ERD component to NPM (sree)
* 9cde62d7ca [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Shorten-up language reference build section title
* c3e5a374c3 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [gethue] Fix link pointing to Phoenix connector install
* ac98e2a257 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [gethue] Fix anchor link to ksqlDB connector doc
* d14f14f2e6 [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] Add minimal info to the query detail page
* 39b01a8813 [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] Parameterize the Query History DB connection
* 274a6ed2bb [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] Plug in the ORM into the list query API
* bcc61ada1a [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] Add query DB routing
* 3426d62e0e [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] Just show the Hive Query browser when flag is on
* 1653140f85 [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] Schema model tweaks to be valid
* f999ac696c [HUE-9413](https://issues.cloudera.org/browse/HUE-9413) [qb] First model for HiveQuery
* 0502e4caab [HUE-9412](https://issues.cloudera.org/browse/HUE-9412). [ui] Add tests for ERD component (sree)
* b9e3934d53 [core] Bump lodash from 4.17.13 to 4.17.19 (#1213)
* 87e9ff3d13 [HUE-9411](https://issues.cloudera.org/browse/HUE-9411) [core] Add missing oozie and pig migrations (sree)
* 40f9a18fec [HUE-9410](https://issues.cloudera.org/browse/HUE-9410). Doc changes for - Add unit testing base to vue components (sree)
* 7a6ed40112 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [jb] Rename webpack bundle not built to avoid 500
* 2466670e43 [HUE-9410](https://issues.cloudera.org/browse/HUE-9410). [ui] Add unit testing base to vue components (sree)
* 86b4f07add [blog] Localized in Japanese monitoring activity with Grafana blog (#1211)
* f757edb26d git commit -m "[HUE-9381](https://issues.cloudera.org/browse/HUE-9381) [ui] Add limits and ellipsis to ERD component (sree)
* b6f769d83e [notebook] Fix Deleted method SparkApi.get_properties #1206 (#1209)
* 635805574a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Harmonize titles of reference section
* 85e179cf99 [HUE-9381](https://issues.cloudera.org/browse/HUE-9381). [frontend] Table ERD (sree)
* 171a4e5156 [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [docs] Properly indent Note about connector impersonation
* d4af4b684d [HUE-9390](https://issues.cloudera.org/browse/HUE-9390) [docs] Update some MS sqlserver connector dead links
* 12435be4d1 [HUE-9390](https://issues.cloudera.org/browse/HUE-9390) [docs] Explains the mysqllib update to do with latest OSs
* f7c68d3f2a [HUE-9369](https://issues.cloudera.org/browse/HUE-9369) [editor] Fix some missing tokens in the Airline SQL query sample   - change MONTH to month   - change count to count(*)
* a2d46e1b7f [HUE-9394](https://issues.cloudera.org/browse/HUE-9394). [ui] Cannot pass complex data into web components (sree)
* 45153325c9 [HUE-9383](https://issues.cloudera.org/browse/HUE-9383) [core] Avoid potential script execution in Share Document UI  (#1203)
* de7e0b6ac7 Revert "[HUE-9383](https://issues.cloudera.org/browse/HUE-9383) potential Script execution in Share Document UI (asnaik) (#1190)" (#1204)
* c3d0a6fa63 [HUE-9392](https://issues.cloudera.org/browse/HUE-9392) [ui] Adjust Vue indentation linter rules
* 52af454fe0 [HUE-9392](https://issues.cloudera.org/browse/HUE-9392) [ui] Switch Vue web component wrapper to support styling
* 3d45d9c56a [HUE-9392](https://issues.cloudera.org/browse/HUE-9392) [core] Move UI config repo to Typescript
* 163cfbfecd [HUE-9396](https://issues.cloudera.org/browse/HUE-9396) [core] Implement SAML groups check and redirect them to 403 page if not permitted. (#1202)
* b00308afdf [HUE-9396](https://issues.cloudera.org/browse/HUE-9396) [core] Implement SAML groups check and redirect them to 403 page if not permitted. (#1201)
* f83a017722 [HUE-9386](https://issues.cloudera.org/browse/HUE-9386) [blog] Add post of Hue Grafana dashboard
* 8eae082a7e [HUE-9399](https://issues.cloudera.org/browse/HUE-9399) [fs] Run the config check for ABFS as the logged in user
* c74260530b [HUE-9399](https://issues.cloudera.org/browse/HUE-9399) [fs] Fix issue with missing user argument in _get_client_cached
* beaa889d7f [HUE-9397](https://issues.cloudera.org/browse/HUE-9397) [ui] Only show share action when sharing is enabled or for admins
* e56ec82de3 [HUE-9397](https://issues.cloudera.org/browse/HUE-9397) [core] Have the sharing related APIs serve a 403 if document sharing is disabled for non-admins
* fc822ba779 [HUE-9397](https://issues.cloudera.org/browse/HUE-9397) [core] Add a config flag to enable/disable document sharing
* 24c0344d07 [HUE-9398](https://issues.cloudera.org/browse/HUE-9398) [core] Add attribute_map_dir saml configuration. (#1196)
* cd12de9cef [HUE-9396](https://issues.cloudera.org/browse/HUE-9396) [core] Implement SAML groups check and redirect them to 403 page if not permitted. (#1195)
* c4a9150c86 [HUE-9395](https://issues.cloudera.org/browse/HUE-9395) [core] Update the notice file
* 8b46e3a54e [HUE-9366](https://issues.cloudera.org/browse/HUE-9366) [libsaml] SAML Authentication with additional group checks
* 778c7c8709 [HUE-9366](https://issues.cloudera.org/browse/HUE-9366) [saml] Add redirect of denied SAML login to a 403 page
* 09a8044ff1 [HUE-9393](https://issues.cloudera.org/browse/HUE-9393) [core] Upgrade SQLAlchemy to SQLAlchemy-1.3.17 (#1194)
* 9fdbc3abcc [HUE-9366](https://issues.cloudera.org/browse/HUE-9366) [design] Redirect denied SAML login to a 403 page
* 9d0136c135 [oozie] Fixing UnboundLocalError issue in coordinator from HDFS submission (#1191)
* 97041e5b7a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [site] Adding link to Apache Flink Editor
* 52c75305f1 [HUE-9392](https://issues.cloudera.org/browse/HUE-9392) [ui] Include Typescript files in the linter
* 5f8c150ea5 [HUE-9392](https://issues.cloudera.org/browse/HUE-9392) [ui] Apply new TS linter rules
* 5a30e411ae [HUE-9392](https://issues.cloudera.org/browse/HUE-9392) [ui] Include Vue files in the linter
* 3433438a31 [HUE-9392](https://issues.cloudera.org/browse/HUE-9392) [ui] Apply new Vue related linting rules
* 1d070ac86c [HUE-9379](https://issues.cloudera.org/browse/HUE-9379) [ui] Add absolute path in file detection to ci checks
* 21ed570fe2 [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [ui] Enable Typescript for vue components
* 65adceb01b [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [ui] Switch the hive query plan component from ko to a vue web component
* b58139ccde [HUE-9391](https://issues.cloudera.org/browse/HUE-9391) [ui] Possible Script Execution on Documents Page in Description Field	 (#1193)
* 2f5a563892 [HUE-9385](https://issues.cloudera.org/browse/HUE-9385) [blog] Fix typo in nmp license screenshot title
* 0ca7241dc5 [blog] Translated licence and absolute path CI blog into Japanese (#1192)
* b554c8ec8c [HUE-9385](https://issues.cloudera.org/browse/HUE-9385) [blog] Adding ci nmp license checker screenshot
* ed020d94d1 [HUE-9389](https://issues.cloudera.org/browse/HUE-9389) [ui] Fix missing connector id for the indexes and streams assist panels
* dd13bbacf8 [HUE-9388](https://issues.cloudera.org/browse/HUE-9388) [search] Disable webworkers in the dashboard ace editor
* 1533466dd2 [HUE-9387](https://issues.cloudera.org/browse/HUE-9387) [tb] Fix bug where the Table browser always thinks navigator and optimizer is enabled
* 429a6a2123 [HUE-9387](https://issues.cloudera.org/browse/HUE-9387) [tb] Fix js exception for undefined metastoreViewodel
* df10924d81 [HUE-9384](https://issues.cloudera.org/browse/HUE-9384) [ui] Fix js exceptions from document empty trash and create folder
* 41d0f83058 [HUE-9377](https://issues.cloudera.org/browse/HUE-9377) [ui] Reduce webpack config duplication
* cc661b00ee [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [useradmin] Light refactoring of message strings
* e81e94fd3c [HUE-9385](https://issues.cloudera.org/browse/HUE-9385) [blog] Automated checks for JavaScript modules compatible licenses and non absolute paths
* 70c3224075 [HUE-9382](https://issues.cloudera.org/browse/HUE-9382) Possible Script Execution on Add/Sync LDAP users (asnaik) (#1189)
* 2ffd30378f [HUE-9383](https://issues.cloudera.org/browse/HUE-9383) potential Script execution in Share Document UI (asnaik) (#1190)
* 621d95ee0a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Small CSV export lib restyling
* 4264dea710 [HUE-9368](https://issues.cloudera.org/browse/HUE-9368) [docs] How to run Hive queries in dev section (sree) (#1188)
* 86b2077b24 [HUE-9379](https://issues.cloudera.org/browse/HUE-9379) [ui] Add a tool for absolute path in file detection
* 19089ffa12 [HUE-9377](https://issues.cloudera.org/browse/HUE-9377) [ui] Translate all absolute paths added by Vue to relative paths in the js.map files
* 6dbf75b902 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [sqlalchemy] Return empty functions instead of error
* e97e4f582e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix link to gethue in 4.6 release note
* 04db0b7677 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sqlalchemy] Support complex types in the autocomplete
* ca8d13c094 [HUE-9374](https://issues.cloudera.org/browse/HUE-9374) [editor] Fix transport mode error in query_server config
* 608b1287d3 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add 'beeswax' to supported describe udf dialects
* 4982839577 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Describe functions if needed when opened in the UDF assist panel
* 421231651e [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add pub sub events for describing individual UDFs
* 61c10c148c [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [assist] Fix cache issue in the assist udf reference panel
* c9a2789a51 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Cache the UDF categories instead of the API response to support individual describe
* d8437091a2 [HUE-9377](https://issues.cloudera.org/browse/HUE-9377) [ui] Prevent absolute paths from Vue in the js.map files
* 9a3909d352 [HUE-9374](https://issues.cloudera.org/browse/HUE-9374) [editor] Support Thrift on HTTP to Impala
* 5f53b669ee [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sqlalchemy] Do not fail autocomplete on non DB prefixed tables
* 505a84e82f [HUE-9378](https://issues.cloudera.org/browse/HUE-9378) [core] Removing python-crontab lib
* 3c5df49881 [HUE-9377](https://issues.cloudera.org/browse/HUE-9377) [ui] Improve source map generation
* 9c33e2d9c0 [HUE-9376](https://issues.cloudera.org/browse/HUE-9376) [ui] Include tsconfig.json in the build scripts
* 6d34924d40 [HUE-9377](https://issues.cloudera.org/browse/HUE-9377) [ui] Apply new linting rules
* ed826b50f1 [HUE-9377](https://issues.cloudera.org/browse/HUE-9377) [ui] Upgrade jest and linters to latest versions
* 22fbea5b77 [HUE-9377](https://issues.cloudera.org/browse/HUE-9377) [ui] Upgrade webpack and babel to the latest versions
* 3be8d30d38 [HUE-9376](https://issues.cloudera.org/browse/HUE-9376) [ui] Move the SQL reference repository to Typescript
* 9efb96f7dc [HUE-9376](https://issues.cloudera.org/browse/HUE-9376) [ui] Add Typescript support
* 750073b49e [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [editor] Add details about UDF argument locations to the Hive, Presto and Impala parsers
* 441af44217 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add keywords suggestions to the Hive UDF reference
* aaaa2a2032 [fb] Changed assert target stat from numRows to numFiles (#1178)
* becfdbf7c1 [beeswax] Set localhost for default expected value (#1181)
* ea4cbeb23b [filebrowser] test_compress_hdfs_files need to access jobbrowser (#1174)
* 7f0becea9b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix title of foreign key section in Editor
* 7d8210b6ea [hive] TestHive.test_install_examples need to access to beeswax (#1176)
* fc8a5a1ac8 added builtin str for compatiblity with python2 and python3 (#1172)
* d3cc8ff366 [HUE-9375](https://issues.cloudera.org/browse/HUE-9375) [editor] Fix js exception on filter in the UDF assist panel
* a885302aee [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add keywords suggestions to the Impala UDF reference
* 762d1762c8 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add support for UDF keyword suggestions in the autocompleter
* f30d7051d5 [blog] Localize phoenix post (#1169)
* 413277e440 [about] Update admin_wizard.mako content test case (#1168)
* 6ff04f3c57 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add function description in autocomplete API
* c8a0a031cc [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [editor] Fix npm webworker bundle generation
* 4a3ca309d0 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [editor] Add details about UDF argument locations to the generic parser and its relatives
* 3e950bcdd7 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [editor] Improve the structure of shared parse support utils and extract additional functions
* 6077d9bde2 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [editor] Add UDF argument grammar to the generic parser
* 3c73d709cf [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [editor] Extract UDF grammar to separate files
* 936a3aefeb [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [editor] Reduce duplication for ALTER, DROP and SHOW in the Presto parser
* e2c9cd929f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Update video link of HDFS Browser post
* c9043a35e0 [auth] Deactivate login error's form doesn't have 'username'. (related to #1164) (#1165)
* 57a24ccc06 [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [phoenix] Adding PHOENIX-5938 Support impersonation in the python driver
* 0ed12f7c19 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add Phoenix impersonation example
* 97fb3b3043 [HUE-9372](https://issues.cloudera.org/browse/HUE-9372). [frontend] Auto complete values for LIMIT Clause (sree)
* 8e8f270193 [metastore] Added grant_access to TestApi.test_show_tables (#1162)
* f15be02274 [HUE-9373](https://issues.cloudera.org/browse/HUE-9373) [core] keytab_reinit_frequency is ignored in hue.ini (#1161)
* 332fa7c0cd [HUE-9369](https://issues.cloudera.org/browse/HUE-9369) [editor] Adding Airline sample queries
* 71e1a9542e [HUE-9369](https://issues.cloudera.org/browse/HUE-9369) [editor] Configuration to auto install sample queries and tables
* d4541e1006 [HUE-9365](https://issues.cloudera.org/browse/HUE-9365) [core] Fix check config if warehouse is in S3
* 711ebe31d8 [proxy] Changed login to make_logged_in_client with is_superuser=True in proxy_test (#1158)
* 1315356ea7 [tools] Removed pylint from jenkins.sh (#1154)
* dde4d07b6b [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [jb] Add a skeleton Hive query plan component
* 9e7ee7d38e [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [ui] Enable webpack for the job browser code
* 133f7f571b [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for hive, impala and the generic parsers
* 5edddcead1 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for the elasticsearch parser
* b5ad2a58e8 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for the druid parser
* 0280d489e7 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for the flink parser
* beedb684b1 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for the calcite parser
* 18b8a4abe8 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for the presto parser
* 365e970cb8 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for the phoenix parser
* 2dbf3b6ead [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Switch to structure.json for the ksql parser
* 8ce1d058c3 [HUE-9370](https://issues.cloudera.org/browse/HUE-9370) [frontend] Add parser generation based on structure.json file definition
* 0823db268a [core] Changed jenkins.sh variable names to be more general (#1153)
* 572815e65b [HUE-9346](https://issues.cloudera.org/browse/HUE-9346) [ui] Add npm license checker to circleci config
* c0c404f732 [editor] Updated test with proper exception message (#1141)
* a795011efd [HUE-9368](https://issues.cloudera.org/browse/HUE-9368) [docs] Improve dev onboarding experience (sree) (#1151)
* ed3c2fe249 [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [phoenix] Include PHOENIX-5936 sqlAlchemy get_columns KeyError
* 24ee8960f9 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Extract argument and return types from the UDF API response
* 344604a551 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add a refresh button in the assist UDF panel
* 0bd98e8673 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Cache the responses from the UDF autocomplete endpoint
* 6e99ff3b34 [#1149] added a filebrowse_action method to MockFS for oozie.models2_tests.TestEditor.test_create_new_workflow (#1150)
* 965e50f2e2 IS-1142 [test] Added install pylint for jenkin.sh (#1143)
* 0040dba555 IS-1147 [hive] Fixed TestHiveserver2ApiWithHadoop failed during unit tests (#1148)
* db4b01d884 IS-1139 [core] Fixed ERROR: desktop.auth.views_test.TestMultipleBackendLoginNoHadoop.test_login (#1144)
* 5dcaeeafdb IS1146 [filebrowser] Fixed XxdTest:test_compare_to_xxd failed (#1146)
* f061e63b5a [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [phoenix] Updating connector blog post and documentation
* 2ce46f129c [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [phoenix] Bundle SqlAlchemy connector
* 52946f02fe [HUE-9367](https://issues.cloudera.org/browse/HUE-9367) [phoenix] Trim the semi colon in the dialect
* 2c18427dd1 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix phoenix pip install command section
* ee4e5ff207 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add result from the autocomplete functions API to the udf repository
* 19dddfab7d [HUE-9198](https://issues.cloudera.org/browse/HUE-9198) [assist] Fix ABFS upload issue in left assist
* 85f0f7d0bc [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Use async UDF return type resolution for the autocompleter results
* 13961a69c8 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Remove the dependency on sqlFunctions from all parsers
* bc9968e21d [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Extract shared type logic from the parsers into one place
* ada62a31b1 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Switch autocompleter to async set option resolution
* 2bface0f0b [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Switch to the async functions repository in the function context popover
* 23592fad4c [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Remove argument type resolution from sqlFunctions
* 5840203300 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Switch to async function resolution in the autocomplete results
* 604e2eef57 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Remove unused suggestFunctions from SqlFunctions
* 3485c7f144 [HUE-9364](https://issues.cloudera.org/browse/HUE-9364) [editor] Use spaces instead of tab in the compose area
* c06f39cae9 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [notebook] Adding new api and hiveserver2 tests
* c861e1e9a9 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [impala] Adding function listing for Impala
* 214b0efdc6 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [hive] Support GetFunction execution and fetching
* 8e261a8161 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [hive] Adding Thrift call to GetFunctions
* 94ed383ec6 [HUE-9295](https://issues.cloudera.org/browse/HUE-9295) [docker] Avoid pulling Django 3 by mistake with Python 3
* dd82d768d4 [HUE-9295](https://issues.cloudera.org/browse/HUE-9295) [hive] Python 3.8 support on initial create session
* 2a92e3fd5b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [hive] Fix missing % typo in log printing
* bf4cefe6ab [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Function autocomplete test in hiveserver connector
* b12709aec8 PR1125 [spark] Fix merging of custom configuration for connectors with default (#1125)
* 4e69ffe3aa [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Add function listing in autocomplete API
* a26094172e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [bquery] Load credentials via json text instead of file
* 9fb9b827e6 [HUE-9358](https://issues.cloudera.org/browse/HUE-9358) [design] Adding HiveServer2 HA failover
* d521ee60e5 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactor Solr connector configuration section
* 5d6c5383cf [HUE-9355](https://issues.cloudera.org/browse/HUE-9355) [design] Restrict access based on a list of SAML groups
* 7f7edc4c02 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Align dialect impersonation flag name
* 29ff3952d7 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Bubble up autocomplete errors
* 5086985bcf [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Extract server url from the connector options
* 814aedacae [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Move type resolution from parsers to the autocompleter
* 8c9648fbb6 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Extract type conversion tables from SqlFunctions to one per dialect
* 0ff59cd0f4 [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Update the functions panel to use the new sql functions repository
* 865210556a [HUE-7738](https://issues.cloudera.org/browse/HUE-7738) [editor] Extract udf and set option reference to a per dialect structure
* 589201b4ff [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix js exception from jobs panel
* 775b3efe7f [HUE-9354](https://issues.cloudera.org/browse/HUE-9354) [editor] Prevent grayed out result when fetch_result_data returns empty data in editor v2
* f2dd9f6a54 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Fix issue where non streaming results are flagged as streaming in editor v2
* 3e44df0295 [HUE-9358](https://issues.cloudera.org/browse/HUE-9358) [hive] Proper message with LLAP HA discovery when all servers down
* 497a933ec9 [#1133] variables in REMOTE_DEPLOYMENT_DIR is not properly replaced (#1135)
* 1eb103ae4d [HUE-9357](https://issues.cloudera.org/browse/HUE-9357) [hive] Add logging to HIVE_DISCOVERY_HIVESERVER2_ZNODE discovery
* 677514c551 [HUE-9356](https://issues.cloudera.org/browse/HUE-9356) [core] 4.7.1 release
* 33f8b4d956 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh latest microk8s install step
* cf6b898030 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Rename container name to just 'sql-training'
* 96381e8914 [HUE-9353](https://issues.cloudera.org/browse/HUE-9353) [ranger] how to grant ranger permissions for a new user on a secure cluster
* cd0cd2f237 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Show a message while waiting for streaming data
* efadcdca9f [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Add live filtering of streaming data in the result grid
* c168d73c7e [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Disable result search for streaming data
* 2d1c3fbc96 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Refresh the install instructions
* 470290b62f [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Add a default limit of 1000 records for streaming data in the result grid
* 7a5f68fa5f [HUE-9352](https://issues.cloudera.org/browse/HUE-9352) [editor] Wait with showing the execute button until the session is loaded in editor v2
* e9250141f3 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Reverse the result table rows for streaming results
* 2a43dc2bb9 [HUE-9351](https://issues.cloudera.org/browse/HUE-9351) [editor] Insert history records after execute instead of refetching all
* a5327836e8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Prevent js exception for "missing snippets" on jobs update
* d583c9b1b7 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Adding Druid SQL Editor demo video
* 9623d985e8 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [flink] Set semicolon stripping to true for the dialect
* cb6d034be3 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [flink] Provide check_status results in a result attribute
* 530e1819a3 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [flink] Add streaming status in check status
* bfaeeb88fa [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [hive] Avoid trying to close a session not found
* 84c50fdde2 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Append streaming results in the result grid component
* 434ed73a1c [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Introduce 'streaming' execution status in the UI
* 56c17be270 [HUE-9064](https://issues.cloudera.org/browse/HUE-9064) [ui] Add a global js flag for web sockets
* 60d5ef43df PR1130 [helm] Fix typo in Chart.yml description (#1130)
* 0c24e6347e [HUE-9350](https://issues.cloudera.org/browse/HUE-9350) [core] Update notice and license files
* 0596c9955e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [gethue] Remove extra right parenthesis in links
* 61b8ed5b8c ISSUE-1127 [oozie] Submit a coordinator from HDFS does not work  (#1128)
* ef8c8da113 PR1129 [blog] Localized Knox and Flink SQL in posts in Japanese (#1129)
* 6c280d66f0 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Use quotes as identifier quotes in Druid dialect
* 3cc3dd349e [HUE-9347](https://issues.cloudera.org/browse/HUE-9347) [task] Use getattr and not __getattr__
* 92a8dbe8df [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Initial handling of runtime query errors
* fc01add284 [HUE-9349](https://issues.cloudera.org/browse/HUE-9349) [editor] Fix flaky result header in editor v2
* a0cbd3e148 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Don't persist local optimizer results in the IndexedDB
* e5ee775264 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Switch to using connectors in the web workers
* 65f4b01c49 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Switch to using connector id in the UI where applicable
* bcdd410468 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Use is_sql check in simple ace editor to determine if syntax checking is active
* 777b8eae72 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [assist] Switch to connectors in the get assist database event
* f9797730b4 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [assist] Use connector when remembering last opened db in the assist panel
* 318b59ce6d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [assist] Publish catalog entry with connector on assist selections
* 38e7cc6bbe [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Fix popular joins in the local optimizer strategy
* a03775b53d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fix issue with popular columns and tables in editor v2
* 94ced036a4 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [frontend] Use connector instead of sourceType in the contextCatalog
* 3e669d12ed [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Switch from sourceType to connector only in the data catalog and entries
* 0af0dd3388 [HUE-9347](https://issues.cloudera.org/browse/HUE-9347) [task] Avoid importing the celery libs when task server if off
* af799e546a [HUE-9347](https://issues.cloudera.org/browse/HUE-9347) [task] Raise QueryError with an argument
* 335cfef9d2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [spark] Add a create session test to the connector
* 419c0a3a35 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Adding id attribute to deprecate type one
* 1244b9db02 PR1126 [hive] Retrieve the proper LLAP session (#1126)
* b82defbdb1 [HUE-9345](https://issues.cloudera.org/browse/HUE-9345) [knox] how to configure hue to use knoxspnegodjango backend on secure cluster
* 4bd9699855 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [blog] Fix docker cp typo in Flink SQL Editor post
* 2292e896d1 [HUE-9287](https://issues.cloudera.org/browse/HUE-9287) [frontend] Adjust jquery plugins for recent jquery upgrade
* 6280f8e185 [HUE-9290](https://issues.cloudera.org/browse/HUE-9290) [frontend] Properly terminate additional html elements
* 1da6589d99 [HUE-9346](https://issues.cloudera.org/browse/HUE-9346) [ui] Add licence-checker tool for npm packages
* 4313352e59 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Blog post on initial SQL Editor
* 957de0e75e [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Design update with first version
* 68a40540ef [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Strip semicolon in Druid dialect
* e3ed4b62e9 PR1124 [blog] Translate the Impala SQL editor blog into Japanese (#1124)
* acbb4d77e0 PR1123 [aws] s3datetime_to_timestamp parse timestamp with Z(minio.io) (#1123)
* 436704c40b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Prepare a is Hive LLAP flag
* 043977fb17 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Send live results via check status
* 81498725f3 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Support describe table in left assist
* 11a13829cd [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Cancel and check status calls
* 6b4b6b1463 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Prepare a is Hive LLAP flag
* ebde13a188 [HUE-9293](https://issues.cloudera.org/browse/HUE-9293) [editor] Fix issue where additional fetched rows are not rendered after scroll in editor v2
* 56a5529c34 [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [ui] Make sure entries are loaded when clicking on the key in the context popover
* 033acbb3ec [HUE-9292](https://issues.cloudera.org/browse/HUE-9292) [editor] Support autocompletion of files from the root for adl, abfs and s3a
* ae46f57b90 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [frontend] Add connector support in the quick query component
* fcc76001c3 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Only set the result type when defined
* 1ebdf5a124 [HUE-9291](https://issues.cloudera.org/browse/HUE-9291) [editor] Don't error for sync results
* f411939ff7 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Handle PEP 479 Py3.8 generator raised StopIteration
* 48f2f2df9b [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Support rendering template with Python 3.8
* 5b48b92029 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Avoid blind TypeError concatenating 'NoneType' and 'str'
* e1296ea83f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] How to quick start querying Apache Impala in 3 minutes
* baf21fb0fd [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Support compiling with Python 3.8
* d70fbcc72f [HUE-9290](https://issues.cloudera.org/browse/HUE-9290) [frontend] Properly close certain html tags
* 531f000ef7 [HUE-9289](https://issues.cloudera.org/browse/HUE-9289) [assist] Fix HDFS file preview in the left assist
* c5d920c60e [HUE-9289](https://issues.cloudera.org/browse/HUE-9289) [editor] Fix editor context popover for files with a root path other than /
* 080fb745ca [HUE-9267](https://issues.cloudera.org/browse/HUE-9267) [editor] Add sanity check for delayed ddl execution
* 611ad1b12b [HUE-9288](https://issues.cloudera.org/browse/HUE-9288) [editor] Fix selection type variable substitution in the editor
* bdc2527840 [HUE-9287](https://issues.cloudera.org/browse/HUE-9287) [frontend] Upgrade jQuery to 3.5
* 57f78ffda4 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Remove wrong import of has ssh missing util
* 8ed2e0ee6e [HUE-9286](https://issues.cloudera.org/browse/HUE-9286) [sqlalchemy] Provide an ability to configure outbound impersonation (#1120)
* 523a342d93 [HUE-9285](https://issues.cloudera.org/browse/HUE-9285) [editor] Properly dispose the jquery tablescroller plugin
* 8817ef4c9e [HUE-9285](https://issues.cloudera.org/browse/HUE-9285) [editor] Limit result grid rows in notebook mode for editor v2
* da042ff66d [HUE-9285](https://issues.cloudera.org/browse/HUE-9285) [editor] Only show result controls after execution in presentation mode for editor v2
* 8527fe4f14 [HUE-9284](https://issues.cloudera.org/browse/HUE-9284) [editor] Only update the history panel when the status of an executable has changed in editor v2
* f5d6b4efd0 [HUE-9249](https://issues.cloudera.org/browse/HUE-9249) [browser] Enable highlight overflow in the query browser
* 1afc620638 [HUE-9249](https://issues.cloudera.org/browse/HUE-9249) [browser] Prevent onbeforeunload when downloading the query profile
* fbf1a6df6b [HUE-9182](https://issues.cloudera.org/browse/HUE-9182) [ui] Have the left assist context popover stick if clicked to open
* 6636cf0530 [HUE-9141](https://issues.cloudera.org/browse/HUE-9141) [frontend] Indicate read-only status in the document context popover
* 0cbe8b945b [HUE-9283](https://issues.cloudera.org/browse/HUE-9283) [ui] Fix issue with missing source map slowing down initial render
* e41446f258 [HUE-9283](https://issues.cloudera.org/browse/HUE-9283) [ui] Use the correct SPDX licence expression in package.json
* 8695a02c03 I1116 [notebook] Fix not rendering Markdown in notebook's snippet (Issue #1116) (#1117)
* 786003ac9c [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Support async fetch results
* b7dcf4406a [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Create and cache session
* c283218fc3 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] List tables of tables with underscore in the name
* 75235033ce [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Fetch result in a sync way
* bf32ab86e0 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [flink] Properly send back SQL error messages
* 08b2553280 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [docs] Adding proper link to image mockup
* 5fd2ef6967 [HUE-9280](https://issues.cloudera.org/browse/HUE-9280) [docs] Adding more scoping for Flink SQL
* ba0335ca96 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Add CPU limit to email stats cron and flower
* 43e893eef5 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add connector id to document when saving query
* f40198dbe4 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [admin] Link to configuration section when hitting misconfig
* 19748b25b8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix connector initialization in editor v2
* 7ea17da197 [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [tb] Use the key component for keys in column lists
* cc7739c67a [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [ui] Use the key component in the context popover
* 48dc4465f7 [HUE-9281](https://issues.cloudera.org/browse/HUE-9281) [core] Users home directory becomes created with the wrong owner on LDAP environment (#1115)
* b126ead3a5 PR1114 [blog] Localized Editor for Spark SQL with Livy into Japanese (#1114)
* 5b36ae0ba5 [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [ui] Show foreign key details in a tooltip for entries in the DB assist
* 31322751dc [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Prevent js exception when the editor is opened for a non-existing connector
* ca0a5a5e9c [HUE-9274](https://issues.cloudera.org/browse/HUE-9274) [ui] Prevent real ajax requests from the jest tests
* 4edcb07bdb [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Switch to synchronized initial hueConfig
* ae6711191b [HUE-9277](https://issues.cloudera.org/browse/HUE-9277) [docs] Scope Livy Spark Sql Editor
* f84016f993 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Scope SQL autocomplete for Livy
* 7f44c7fcec [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Avoid key error when saving query without connector
* 8b443dd091 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Clear executables when saving a query
* 4da4fbbd75 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Show Livy Sql as a SQL supporting dialect
* 814e26cd7a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Avoid js error when refreshing right assist
* 911408940b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Adding check connection to livy dialect
* 8740cc04cc [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Protect against missing query key in check status
* acd1ab23b5 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Bump jaeger lib thas has a simpler tornado dependency
* cbbbf639bb [HUE-9275](https://issues.cloudera.org/browse/HUE-9275) [editor] Silence end user autocomplete calls that timeout
* 5561edf832 PR111 [docs] Grammar improvements in CONTRIBUTING.md (#1111)
* baeccd42c8 PR1109 [jdbc] Fix next() interface in result iteration (#1109)
* c3adc42a91 [HUE-8020](https://issues.cloudera.org/browse/HUE-8020) [admin] Adding test of username login length
* 1ca909f1eb [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [test] Avoid all the debug output of the DB migrations
* ea0b39982f [HUE-8020](https://issues.cloudera.org/browse/HUE-8020) [core] Increase username login input length (#1104)
* a9756c709c [HUE-9273](https://issues.cloudera.org/browse/HUE-9273) [notebook] Encoding Error when use non-ascii characters in sql-editor-variables (#1108)
* 61c1cdbaee [HUE-9273](https://issues.cloudera.org/browse/HUE-9273) [editor] Add test to check for backend variable replacement
* 3bdf4f2ba3 [HUE-9271](https://issues.cloudera.org/browse/HUE-9271) [core] Use UBI base images for Hue images (#1107)
* 36b85ea45d [HUE-9272](https://issues.cloudera.org/browse/HUE-9272) [core] Reduce Hue docker image size (#1106)
* 49e20f2475 [HUE-9271](https://issues.cloudera.org/browse/HUE-9271) [core] Use UBI base images for Hue images (#1105)
* a058e41cb2 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [sqlalchemy] Fix missing self.interpreter in rebase
* 10df3fbfda [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [hive] Skeleton of mini job browser interface
* 116fd6e938 [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [jb] Do not show live history job counter when flag is off
* 99354c6dd2 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [core] Fix eslint in jobBrowserLinks
* 97324505d5 [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [history] Change job counter to be about running queries
* d5918f94ea [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [history] Show submission time
* 822cb3d77a [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [history] Left zero pad history ids so that sorting and refresh are consistent
* 3970d457cc [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [history] Allow to fetch the history for all the type of queries
* 91b6c5423f [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Persist query history status changes
* e4e6c1ad58 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Add has_impersonation setting to sqlalchemy
* 0a33d80099 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [sqlalchemy] Add support for connector semicolon statement trim
* 98c9a858da [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Add apt-get update to unblock missing dev packages
* e4d046ab60 [HUE-9270](https://issues.cloudera.org/browse/HUE-9270) [sqlalchemy] Add impersonation flag
* 0d0b0a89c5 [HUE-9270](https://issues.cloudera.org/browse/HUE-9270) [sqlalchemy] Update tests with new parameters
* b846fc7a16 [HUE-9270](https://issues.cloudera.org/browse/HUE-9270) [sqlalchemy] Close session of a user closes his engine
* 92857c1f75 [HUE-9270](https://issues.cloudera.org/browse/HUE-9270) [sqlalchemy] Rename CONNECTION_CACHE to CONNECTIONS
* c46b8ad8c9 [HUE-9270](https://issues.cloudera.org/browse/HUE-9270) [sqlalchemy] Reuse close_statement in cancel API
* a0610f34dc [HUE-9270](https://issues.cloudera.org/browse/HUE-9270) [sqlalchemy] Proper engine cache
* b04de721c8 [HUE-9270](https://issues.cloudera.org/browse/HUE-9270) [sqlalchemy] Session revamp
* 57c8bc8ee7 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Rely on error decorator to catch autocomplete exception
* a4433618ce [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Move API connection out of constructor
* 3033026a9a [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Fix metadata format of query result
* 90ab6708cb [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Remove unused SavedQuery import
* a9e3c295c8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Update execute_and_wait base tests
* 16657f22eb [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Save connector id of saved and history queries
* 7645ebbf00 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Adding connector to saved queries
* 6cd67f1cba [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [notebook] Option to avoid HTML escaping the query result
* 52e653e933 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [browser] Hive query browser query syntax highlight
* f82d5937f1 [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [browser] Add listing of past Hive schedule executions
* 29e079d7bb [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Skeleton of Hive Scheduled queries browser
* 79a2af292c [HUE-9266](https://issues.cloudera.org/browse/HUE-9266) [jb] Adding skeleton of Query History as Job Browser type
* f2e47ecd0c [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Show human friendly title in the left assist
* 13032037fd [HUE-9182](https://issues.cloudera.org/browse/HUE-9182) [ui] Improve click handling for left assist context popover
* 69a88ec49d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Remove function usage in editor v2
* c254bba123 [HUE-9263](https://issues.cloudera.org/browse/HUE-9263) [frontend] Prevent disposal of static components
* f128a19d71 [HUE-9263](https://issues.cloudera.org/browse/HUE-9263) [assist] Fix issue where the reference panels won't update after editor type change
* 11dd055152 [HUE-9263](https://issues.cloudera.org/browse/HUE-9263) [assist] Switch from type to connector when setting assist source via events
* d963142d65 [HUE-9263](https://issues.cloudera.org/browse/HUE-9263) [assist] Consolidate assist events into constants to prevent spelling mistakes
* 5e423f4e9a [HUE-9262](https://issues.cloudera.org/browse/HUE-9262) [editor] Set the lastExecuted timestamp in editor v2
* 74e1262de0 [HUE-9265](https://issues.cloudera.org/browse/HUE-9265) [assist] Add multiline statement to drag and drop from left assist
* 215a266446 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Revamp the admin database page
* 0bbaf0db7f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Support for Oracle RAC
* 8beacf19af [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Avoid AttributeError when logging REST call
* a6a614202d [HUE-9758](https://issues.cloudera.org/browse/HUE-9758) [connector] Set SQL dialect optimization flags to true
* cfa2b3c6fa [HUE-9259](https://issues.cloudera.org/browse/HUE-9259) [impala] Removing incremental refresh
* 3dbf982a8f [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Use https for websocket accordingly
* 471b0079f6 [HUE-9264](https://issues.cloudera.org/browse/HUE-9264) [parser] Add impala missing string function (#1103)
* a44cbf710e [HUE-9758](https://issues.cloudera.org/browse/HUE-9758) [metastore] Avoid 'Config' error when refreshing the page
* 27b3e146ad [HUE-9758](https://issues.cloudera.org/browse/HUE-9758) [connector] Flags if dialect language and function available
* f52078fb53 [HUE-9249](https://issues.cloudera.org/browse/HUE-9249) [browser] Trim impala query and protect when missing
* 19e7f1b437 [HUE-9238](https://issues.cloudera.org/browse/HUE-9238) [docs] Adding SqlAlchemy connector specific tasks
* 20fc250071 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Flink sql v1
* 1393866fda [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [spark] Add Livy sql connector type
* e4fd81769b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [spark] Properly rename job server to LivyClient
* 92967a2d14 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [catalog] Support window.dataCatalog.disableCache() for optimizer calls
* ede69d2b3a [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [editor] Use connector dialect_properties to determine if risks should be shown or not
* f689920fcb [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Track connector changes instead of dialect changes
* 247b708051 [HUE-9256](https://issues.cloudera.org/browse/HUE-9256) [editor] Fix js exception in the file preview context popover
* 812cd39fa4 [HUE-9225](https://issues.cloudera.org/browse/HUE-9225) [core] Upgrade certain third party python libraries that has identified vulnerabilities (#1102)
* e0dcda9619 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Removing deprecated yaml files
* 1b1accbbe3 [HUE-9205](https://issues.cloudera.org/browse/HUE-9205) [editor] Add query error propagation test in hive connector
* c5bbb86374 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix autocomplete issue when connectors are enabled
* 515e540f85 [HUE-9297](https://issues.cloudera.org/browse/HUE-9297) [optimizer] Prevent constant autocomplete spinner if top columns call is rejected
* 6f0052a2e0 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Ensure config is always loaded
* 3547be28b5 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Consolidate common connector logic into hueConfig
* 922ed37479 [HUE-9255](https://issues.cloudera.org/browse/HUE-9255) [assist] Use dialect instead of type in the language reference assist panel
* 672ac98b27 [HUE-9255](https://issues.cloudera.org/browse/HUE-9255) [assist] Switch from connector type to dialect in the right assist functions panel
* dcc96a0159 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Fix context issues for local optimizer strategy
* 857bd707cd [HUE-9249](https://issues.cloudera.org/browse/HUE-9249) [browser] API to download a query profile
* fc82768e27 [HUE-9249](https://issues.cloudera.org/browse/HUE-9249) [browser] Download or copy Impala profile
* 5f05bffcfe [HUE-9249](https://issues.cloudera.org/browse/HUE-9249) [browser] Add SQL highlighting to Impala query profile
* 7b8e2b408b [HUE-9246](https://issues.cloudera.org/browse/HUE-9246) [core] Enable SAML certificate creation with passphrase support. (#1099)
* 92c3c06a0d [HUE-9254](https://issues.cloudera.org/browse/HUE-9254) [doc] Remove flickity from gethue as GPL
* a62c397383 [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [blog] Localize Hue 4.7 blog into Japanese (#1100)
* 560a233721 [HUE-9250](https://issues.cloudera.org/browse/HUE-9250) [useradmin] Prevent login failed due to user.last_login is None type
* ca356c56d9 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Do not show no result message when filtering matches all values
* 8f29487358 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Add a spinner when performing test connection
* 60572cc272 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Reset connector test result when changing section
* 738bdb80b0 [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [docs] Update README screenshot with 4.7
* 3b275b1bfe [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) [scheduler] Fix wrong url prefix of list schedules
* 3f126a1d94 [HUE-9246](https://issues.cloudera.org/browse/HUE-9246) [core] Enable SAML certificate creation with passphrase support. (#1096) (#1098)
* b7bc3ac98d [HUE-9251](https://issues.cloudera.org/browse/HUE-9251) [core] Fix Hue can't be launched under openshift (#1097)
* 2d56caefd7 [HUE-9245](https://issues.cloudera.org/browse/HUE-9245) [core] Add back Django Database metrics from clean up list
* c0691f4ac7 [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [docs] Fix version number in release notes page title
* ed5a333e8e [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [docs] Update links to connector docs on gethue

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
* agl29
* aig
* airokey
* Ajay Jadhav
* Alex Breshears
* Alex Newman
* Alex (posi) Newman
* alheio
* Aliaksei
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
* Asnaik HWX
* Atupal
* Avindra Goolcharan
* ayush.goyal
* Ayush Goyal
* batou9150
* bcwalrus
* bc Wong
* Ben Bishop
* Ben Gooley
* Ben White
* Bhargava Kalathuru
* BirdZhang
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
* e11it
* Eli Collins
* Emmanuel Bessah
* Enrico Berti
* Eric Chen
* Erick Tryzelaar
* Ewan Higgs
* fatherfox
* gdgt
* Gilad Wolff
* gnieto
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
* Jamie Davenport
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
* Kevin Risden
* Kevin Wang
* Khwunchai Jaengsawang
* Kostas Sakellis
* krish
* Lars Francke
* Li Jiahong
* linchan-ms
* Linden Hillenbrand
* linwukang
* Louis de Charsonville
* Luca Natali
* Luca Toscano
* Luke Carmichael
* lvziling
* Mahesh Balakrishnan
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
* Naoki Takezoe
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
* rdeva
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
* rpoluri
* Rui Pereira
* sachinunravel
* Sai Chirravuri
* sandeepreddy3647
* Santiago Ciciliani
* sbaudoin
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
* skyyws
* spaztic1215
* sreenaths
* Sreenath Somarajapuram
* Stefano Palazzo
* Stephanie Bodoff
* Suhas Satish
* Sungpeo Kook
* TAKLON STEPHEN WU
* TAK LON WU
* Tamas Sule
* Tatsuo Kawasaki
* Taylor Ainsworth
* Thai Bui
* theyaa
* thinker0
* Thomas Aylott
* Thomas Poepping
* Thomas Tauber-Marshall
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
* weixia
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
* Yuanhao Lu
* Yubi Lee
* Yuriy Hupalo
* ywheel
* z00484332
* Zachary York
* Zach York
* Zhang Bo
* Zhang Ruiqiang
* zhengkai
* Zhihai Xu
* z-york
* 小龙哥
* 王添
* 白菜
* 鸿斌
