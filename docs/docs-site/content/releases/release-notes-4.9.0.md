---
title: "4.9.0"
date: 2021-02-02T00:00:00+00:00
draft: false
weight: -4090
tags: ['skipIndexing']
---

## Hue v4.9.0, released February 2nd 2021

Hue is an open source SQL Cloud Assistant for querying [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/): [gethue.com](https://gethue.com)


### Summary

This release brings all these improvements on top of [4.8](https://gethue.com/blog/hue-4-8-phoenix-flink-sparksql-components/).

4.9 brings several improvements on top of the previous release. Several blog posts already detailed some of them, but here is a general summary.

First, the support of many SQL dialects has been improved, with in particular Apache Phoenix, Dask SQL, Apache Flink SQL. Complete end to end tutorials with Docker compose environments have been developed so that you can start poking around in 2 clicks.

* [Querying a live Kafka stream and outputting back calculations on a rolling window](https://gethue.com/blog/sql-querying-live-kafka-logs-and-sending-live-updates-with-flink-sql/)
* [Query live HBase data with Phoenix SQL](https://gethue.com/blog/querying-live-kafka-data-in-apache-hbase-with-phoenix/)
* [Getting started with the Spark SQL Editor](https://gethue.com/blog/querying-spark-sql-with-spark-thrift-server-and-hue-editor/)

!["Flink SQL - SELECT and INSERT data into Kafka Topics"](https://cdn.gethue.com/uploads/2021/02/peek-log-streams.gif)

The Editor is also getting split up into components, so that they are cleaner and easier to reuse (e.g. SQL parsers, SQL Scratchpad...). This will bring a new version of the Editor, which is currently in beta. Another improvement in the introduction of the Connectors (in beta too) so that SQL dialects can be easily added without any server restart.

Secondly, special thanks to the community who contributed a brand new Dask SQL autocomplete (ISSUE-1480) and also Prometheus Alerting for Kubernetes (PR-1648).

Dask SQL is a great way to leverage your existing Python libs by directly calling them via SQL. You can even create your own ML models like you would create a table. Read more on the documentation.

Flink SQL is getting friendlier with more sophisticated syntax autocomplete for critical functions like TUMBLE().

!["Flink SQL - Autocomplete improvements"](https://cdn.gethue.com/uploads/2021/02/flink_udf_tumble.png)

The autocomplete is also getting smart enough to suggest JOINs on tables with Foreign Keys.

!["Foreign Keys JOINs autocomplete](https://cdn.gethue.com/uploads/2021/02/fk_joins.png)

The tech stack continues to get modernized as Python 3 is now the default in the latest Docker image and the port from Django 1 to Django 2 was done (and Django 3 is next).


Go grab it and give it a spin!

Docker:

    docker run -it -p 8888:8888 gethue/4.9.0

Kubernetes:
    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install gethue/hue

[demo.gethue.com](https://demo.gethue.com/)

[tarball](https://cdn.gethue.com/downloads/hue-4.9.0.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.9.0.zip) releases


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

* 157eee72ee [release] Perform 4.9 release
* a9e2b3647d [docs] Move notion of Jira to GitHub issues
* e8a1cdf6e5 [docs] Improve release process
* 2eaa4dd509 [jb] GH-1721 HUE-9419 curvedArrow issues when Job Dashboard has horizontal Scrollbar (asnaik) (#1722)
* 63b03e8c4b Update snapshots
* ceb5e6d30f [frontend] Option to pass tooltip in params now
* 1350a9ed0a [metadata] Adding a predict API skeleton
* 6ec6d7a0fa [docs] Add how to update test snapshots
* a1f2e6ad91 [editor] Add errors to the execution analysis tab in editor v2
* f44af925de [editor] Add an execution analysis panel with logs and job links
* e20e0b094a [editor] Properly dispose the result table component
* be516aecbe [frontend] Add an autoscrolling log panel Vue component
* b5ffd663e1 [frontend] Fix js error on job browser links
* 8fd7533762 'Sump' typo fix to 'Sum-up'
* bdea1d599d '?' moved in top-right dropdown menu as "Help"
* 74e26319e8 [connector] Keep ordering deterministic
* 9aa3651014 [desktop] Fix pylint styling in tests
* a08d1b0271 [dekstop] Make sure test runner DB options are Python2 compatible
* 994fd8ff75 Applying pylint fixes to the file and change the setting_dict['OPTIONS'] to dict type from str
* db1ff97aa6 [lib] Adding django-app conf for latest django-axe
* 26278446b2 [oozie] Whitelist old test file from lint
* 21b15e5898 add new file generated through makemigrations command after django-axes version upgrade
* 447e37baf4 CommandParser not requires cmd argument in django2.1
* 18d886f8e7 Upgrading django-axes version for Django1
* 65d5db3c9f [HUE-9715](https://issues.cloudera.org/browse/HUE-9715) [Django Upgrade] [django-axes] 'django.contrib.auth.views' has no attribute 'login'
* fc101bb221 [editor] Fix explain panel scrolling in editor v2
* 0b8e05ed6a [editor] Add remaining autocomplete popularity details panels in editor v2
* d751bf9e8a [editor] Add the autocomplete join details panel in editor v2
* 5b07f63ae6 [frontend] Add support for any available highlight rules in the SqlText vue component
* 6a394bd985 [examples] Avoid Could not install phoenix query
* 2666a41f45 [Git] Creating an Pull Request Template for Hue (#1704)
* d21d8e95e9 #1683 - update live parsers demo with latest parsers (#1703)
* d39e01803c [editor] Combine local and api risk analysis
* fc8f6ffd26 [editor] Combine local and api top joins
* 1b328dfaf4 [editor] Combine the local and api strategies into a new SqlAnalyzer
* 7eed6f731d [shell] Upgrade ipython to not break
* 1d4db8783b [docs] Update the broken documentation link and fixed typo
* 870f7b19ec [flink] Describe Function autocomplete for flink (#1684)
* 89440b8aa3 [frontend] Fix incorrect import in component docs
* 810edd5abd [frontend] Change npm module generation to put the source in root of the library
* d3c8aafe2a [editor] Externalize the SQL references repositories
* a6afc3bc3b [editor] Add expand/collapse actions for editor area and bottom tabs
* b4e172dd4e [editor] Add missing status texts to the new result table component
* ce25259169 [editor] Split the results grid and charts across two tabs
* 2f1bb2c9cb [frontend] Prevent empty class attribute generation in the HueTable component
* 3a30cc993d [frontend] Improve Firefox rendering of the ResultGrid component
* 46f57dfd02 [frontend] Add sticky first column option to the HueTable component
* 6c32136e99 [frontend] Fetch more results when scroll to end in the new ResultGrid component
* 383f3f4c16 [frontend] Add scroll to end event to the HueTable Vue component
* 18deba819d [editor] Improve scrolling and layout of the result grid component in editor v2
* 0dd6dd7e77 [frontend] Add a sticky header option to the HueTable vue component
* f6cdd7e553 [editor] Switch to a column based flex layout for the editor page
* 82f3081c39 [frontend] Remove wrapping <span> for all apps
* 4eabc4e89e [editor] Have the AceEditor component fill the container space
* 0a9a8a7c20 [editor] Separate the editor v2 from the notebook
* a0848bfe0e [editor] First version of the execution result grid component
* ec912357f8 [editor] Create a dedicated editor mako
* 3f4fb99823 [django] CommandParser still requires cmd argument in 2.0
* 5a2a33df50 [HUE-9714](https://issues.cloudera.org/browse/HUE-9714) [Django Upgrade] [CommandParser] __init__() takes 1 positional argument but 2 were given
* 1a2fa4d012 [HUE-9716](https://issues.cloudera.org/browse/HUE-9716) [Django Upgrade] include django-ipware dependency for upgrading django-axes version
* 7bd40066b5 [flink] #1685 - The DB assist panel lists wrong list of columns for flink table's (#1686)
* b682f4b5c6 [query] Table sample data preview incorrectly rounds bigint value (#1680)
* 56ce816f0f  Adding TUMBLE Function to autocomplete  (#1678) (asnaik)
* cfb7c76dba [flink] adding TUMBLE,HOP,SESSION to keywords and addding associated builtinFunctions (#1671)
* a8a1d667cb [editor] Query builder should also be off at the API level defaults
* 175c5df01a Revert "[hive] Using minimal version of transational sample tables"
* 71192229b9 [HUE-9710](https://issues.cloudera.org/browse/HUE-9710) [Django Upgrade] on_delete will be a required arg for ForeignKey in Django 2.0
* d3bbf63d31 [phoenix] Adding create table and upsert as demos
* 637c6cbbe0 [HUE-9709](https://issues.cloudera.org/browse/HUE-9709) [Django Upgrade] Importing from django.core.urlresolvers is deprecated (#1669)
* 008ed8af11 [organization] Add migration for 150 chars username
* 29018aa227 [organization] Add explicit FK constraint for Django 2
* 54f7de58f6 [frontend] Fix issue with incorrect logo color in sidebar after generation of css
* 03d9045195 [login] Do not hardcode the splash screen background
* 9364480ffe [auth] Do not fail on backends without usernames
* c85c4139d9 [editor] Fix issue of query-10 vs query-hive in samples
* e7c4bd1cee [HUE-9680](https://issues.cloudera.org/browse/HUE-9680) [Django Upgrade] upgrading Django 1.11.29 to 2.0.13
* 4a94e44796 Applying pylint styling fix to files
* 7d41081166 [HUE-9683](https://issues.cloudera.org/browse/HUE-9683) [Django Upgrade] Hive tests failed after Django upgrade (1.11.29 -> 2.0.13)
* bd6ffc6755 [HUE-9682](https://issues.cloudera.org/browse/HUE-9682) [Django Upgrade] RemovedInDjango21Warning: The host argument is deprecated, use allowed_hosts instead
* 929ce11960 [HUE-9706](https://issues.cloudera.org/browse/HUE-9706) [Phoenix] Right assist does not list current table
* 0fdf1b8508 [HUE-9708](https://issues.cloudera.org/browse/HUE-9708) [Django Upgrade] RemovedInDjango21Warning: The logout() view is superseded by the class-based LogoutView()
* 1d1ad543be [ui] Login page restyling to make it inline with new sidebar style
* 85f4effdd6 [blog] Fix link to fetch Flink SQL docker compose yaml
* a05bf9c1d7 [editor] Do not auto load sample when creating a brand new editor
* 1a2fc3b1c8 remove prometheusrule from values.yaml
* 8dcd139b53 Move promtheus rules to template
* 1b2f0a861e Update template enable condidition
* f99e17fa7c Moved Rules to values file and changing the expression to be simple for a given example
* b12b03b52a Addressing comments section-1
* 1cfda0bb98 Adding a extra line in prometheus-alert-rule.yaml
* 9d1e6d1fc9 Feature-Example-Promethusrule
* 6f23d90495 Feature-Example-Promethusrule
* eff69b580d [HUE-9681](https://issues.cloudera.org/browse/HUE-9681) [Django Upgrade] desktop.auth.backend.AllowFirstUserDjangoBackend.authenticate() to accept a positional  argument RemovedInDjango21Warning
* c89b12b046 [sqlalchemy] Provide minimal user feedback on auth connection failing
* e74502c722 [HUE-9705](https://issues.cloudera.org/browse/HUE-9705) [Django Upgrade] Remove old unused commit option to loaddata.handle
* 404cd916c9 [editor] Avoid duplication of query examples
* 1e7da42034 [login] Hide bottom link in modal
* dfe9461c74 [hive] Fix wrong use of positional argument in describe table
* 1ea6306ac7 [ui] Just have a gethue link on the login page
* 437d6357e6 [dasksql] Adding SELECT and CREATE model examples
* 90265747d9 [docker] Point to ksql module working with INSERT
* a86b08813e [dasksql] Adding NYC taxi data query example
* 77b5f6749b [editor] Use proper uuid for creating query examples
* 4fdeb6988b [editor] Also load dialect sample when editor already loaded
* a143fe3e5c [ksql] Adding ksqDB SQL examples
* 33654c7a00 [flink] Adding Flink SQL examples
* accd0cc483 [core] Styling idbroker files
* 2bfe50ddce [core] Avoid django.core.exceptions.AppRegistryNotReady when hdfs off
* b7c71cf8af [connectors] Support global enable flag in dashboard access
* fbcb310cb4 [connectors] Allow to configure dashboard access
* 799c7ffc69 [connectors] SqlFlow dialect connector
* d8ac372643 [connectors] Offer a minimal natural key mapping
* 9f2034b57d [editor] Hook in auto load dialect example
* 5270a6b22c [editor] Refresh examples content when re-installing them
* bd3b9dd9a2 [editor] Refactoring for Auto install examples
* 76caf75b15 Update ServiceMonitor Label
* 4e46b94d7e [organization] Workaround creating org of sample user on first login
* 15ffd17a21 [editor] Do not fail when dialects dont have samples
* 7ba88e00d7 [notebook] Adding hive and impala dialects to their sample queries
* e0ae8160db [notebook] Allow to pick a certain dialect in install examples
* bd46cdbcda [notebook] Install all samples command
* bd9c6611be [phoenix] Add a test checking for the UPSERT sample data
* 3b6a5fda34 [editor] Swapping file names of create table data files
* 2bfd5f368e [phoenix] Add sql sample tables and queries
* 9d2e3017d6 [connectors] Hive sqlalchemy should not have Thrift use_sasl property
* 5fe570dbef [connector] Support connectors in Describe API
* bd3f2ea360 [assist] Show model feature columns in the ContextPopOver
* 13e09e604f [frontend] Increase the sidebar logo size
* 42b57cc4f1 [frontend] Add spacer support in sidebar accordion items and adjust the left padding slightly
* d98310a6ac [frontend] Expand sidebar item click area and increase sub item font size
* 25e7f5bfc6 [frontend] Fix issue with item non-unique item naming in the sidebar
* f16024da72 [blog] Add reference to follow-up post on Flink SQL
* 23bce99e94 [blog] Fix mention of Phoenix SQL
* 9a7856180f [flink] Avoid mixing public and private API
* b2393bf6e3 [flink] Add get_sample_data skeleton API
* b83bbf3351 [docker] Re-indent all the default ini properties
* 4960b23407 [hdfs] Fix Python styling
* d5aede2c96 [hdfs] Add a config flag to cleanly disable while using connectors
* 0bdc98f14a [connector] Fix use sasl property
* fdc909daa7 [connector] Add use Sasl property to Impala dialect
* 0baa873739 [docs] Updating and fixing Parser page links
* 1a2fb83770 [blog] correct parser execution way
* 51d210b15f [blog] correct parser execution way
* 2197384ca3 [editor] SELECT 1 will fail with the auto LIMIT with Impala
* c094d271fa [HUE-9679](https://issues.cloudera.org/browse/HUE-9679) [ui] Add 'show tables' to autocomplete for Flink (#1610)
* 51c252de17 [blog] Adding self live log analysis querying post
* 1e96100576 [connector] Support fetching logs in Task Server
* ace5092754 [task] Connector support
* 288fbdeeed [k8s] Task Server for Python 3
* 2f0d1bd8b6 [docs] Harmonize the connection string credentials
* ab50e069b6 [docs] Translation of blogs into Japanese after October 2020
* e70536f2a2 [connector] Adding Trino to connector name
* dbf0ac4ae1 [docs] Adding references to Trino
* a86eff82c9 [metadata] Add connector param to all the API
* 0251cc52dc Applying pylint styling fix to file
* cf75f7c9ed [HUE-9678](https://issues.cloudera.org/browse/HUE-9678) [Django Upgrade] Direct assignment to the forward side of a many-to-many set is deprecated due to the implicit save() that happens
* a90d36e4ce [editor] Deprecate query builder
* be4b8ccd02 [connector] Add use Sasl property to Hive dialect
* eb633599dc [connector] Rename Editor menu to edit list
* 82939530fc GH-1424 [api] Query kill is broken
* 2027e03026 GH-1424 [api] Query kill is broken
* 162cee02de GH-1506 [api] Stream query_store_download_bundle
* ad625d77bb [metastore] Fix styling of views
* 9164dda4fe [connector] Avoid data sample failure
* ee1b5c5ca4 Bump lxml from 4.5.0 to 4.6.2 in /desktop/core
* 0038557143 [docker] Swap Python 2 and 3 files so that Py3 is now the default
* 83f1dd29f4 [notebook] Fix install custom examples when database is new (#1587)
* 6c5d82c854 [HUE-9675](https://issues.cloudera.org/browse/HUE-9675) [Django Upgrade] __init__() takes 1 positional argument but 2 were given
* 4f8fe28cec Upgrading pre-Django 1.10-style middleware
* d24d6db999 [HUE-9650](https://issues.cloudera.org/browse/HUE-9650) [Django Upgrade] Old-style middleware using settings.MIDDLEWARE_CLASSES is deprecated
* bfc327865d [docs] Explain the language translation sources
* 03174efbe1 [frontend] Switch to the new sidebar
* 3ece738942 [frontend] Add event listener tracking in the SubscriptionTracker
* ef24732d51 [frontend] Add an overflow on hover Vue directive
* 39275bc106 [frontend] Add the vue-fragment package
* 43eb6e7893 [frontend] Send connector with all optimizer API calls
* b554fc443d [HUE-9674](https://issues.cloudera.org/browse/HUE-9674) [Django Upgrade] manager inheritance behavior set by Meta.manager_inheritance_from_future
* 996483ea5d GH-1583 Loginpage improvements
* 0693779120 [sqlalchemy] Avoid broken connector config check
* ed9f14fade [sqlalchemy] Auto delete session key only if key present
* 338135cb63 [sqlalchemy] Add note about bug when updating a connector
* d228fb15e6 [impala] Listing tables does not accept table name filters
* 83323e32b4 Bump axios from 0.20.0 to 0.21.1
* f327a49b5a [HUE-9650](https://issues.cloudera.org/browse/HUE-9650)-2 [Django Upgrade] updating the Django Babel version for py2
* 8f2d948a7c [editor] Add scroll into view for arrow button navigation of autocomplete results
* d63b4ae4c8 [editor2] Avoid disabling cancel button in stream queries
* 2690e2c39a [docs] Add link to Impala docker demo
* a8987fe646 Rename Presto to Trino
* 0a85782542 Raise AuthenticationRequired error whenever invalid credentials to datasource throws exception
* fda86fc7d0 [docs] Adding references to Spark SQL blog to the docs
* 331ebf86a6 [blog] A Spark SQL Editor via Hue and the Spark SQL Server
* c7c4e40ee3 [docs] Add new lines before link to gethue.com in README
* 03f70e6152 [docs] Leaner description of the project in the README
* 721e06ad25 [docs] Refresh the main README
* 2ed15ee345 [sqlalchemy] Avoid potential 'NoneType' object has no attribute 'poll'
* 2456f4c779 [connector] Metadata lib should be accessible
* 69a9daed1c [docker] Also set number of gunicorn workers to 1
* 741bf4c37b [dashboard] Use proper dialect name instead of id in menu
* d33b19113f [docker] Switch to gunicorn sync
* d99bf59670 [parser] Finish dask-sql parser with tests
* bdeaa3ec9c [presto] fix download csv function
* 807c2a7833 [presto] Avoid exception when no progress stats
* d462f3010b [sqlalchemy] fix presto progress error message when query is short
* 228aef3c51 [metadata] Fix python styling of client API
* 7543a023d5 [metadata] Add connectors to suggestion API
* 25720e11a2 [presto] Avoid progress report exception when query just stopped
* b4160a2def [py3] Avoid missing glob module
* 040793093e [ci] Switch to dedicated latest build
* 07a812cc71 [connector] Disable auto USE database in presto dialect
* 8f97dea0c3 [sparksql] Strip semi colon automatically via sqlalchemy to avoid error
* 1a7aba3735 [editor] Fix Non-ASCII character in file
* 89e197e4a1 [optimizer] Fix pylint issues in api file
* 076fd2fccb [editor] Display popular table suggestions in editor2
* 853b237d05 [frontend] Remove flaky test
* 1c69549dca [frontend] Fix deXSS of falsy values
* 77c69c554d [hive] Using minimal version of transational sample tables
* 3c7918fcbc [docs] Favor pull requests instead of review board
* 18c1e21259 [notebook] Add proper dialect and connector id make_notebook
* 0a2f131eac [HUE-9653](https://issues.cloudera.org/browse/HUE-9653) [filebrowser] Issue with fileupload when Large Files are uploaded (#1540)
* 325cc5cc98 [docs] Programmatically set permissions to a group
* 941a7c1d24 [connector] Set Edit user permission to always off until supported
* 3725dca740 [phoenix] Adding Table sample data file
* 8041227b48 Applying pylint styling fix to files
* dbb3980ddb [HUE-9644](https://issues.cloudera.org/browse/HUE-9644) [Django Upgrade] Port remaining apps to proper URL namespacing
* 31a591b1f8 [sparksql] Strip semi colon automatically via sqlalchemy to avoid error
* 712c6a2cf3 [docs] Update sparksql SqlAlchemy connector address
* 93899460f4 [docs] Update of github issue for task server
* 9e72f2c35f [hiveserver2] SparkSql get_tables not returning empty
* 6f67404d9a [py3] Adding pylint modules dependencies
* 9cd09280d0 use url.startswith('presto://') honor the other code
* add27d689d fix sqlalchemy presto test case
* 76f4bd29be presto support progress
* 2fad528101 [dask] Tiny styling whitespace fix
* 2323cb445e [parser] Added CREATE TABLE and CREATE VIEW
* 4d5ea44f0d [parser] Unfinished draft for #1480
* 97935adf2f [ci] Whitelist github links for now
* a2197fd36e [ci] Whitelist gethue twitter handle
* de9f90ac73 [frontend] Potential fix for ko.catalogEntriesList test flakiness
* ae4ae1f674 [editor] Fix issue where autocomplete spins forever on column popularity in editor v2
* 3679507a93 [connector] Harmonize quoting style in all the types
* 02c760949a [hive] Also add Hive via SqlAlchemy connector
* c0128f6698 [connectors] Put better default values for the hostnames
* 7abd95808d Raise exception if mpu request fails
* 51535fa069 [core] Avoid failure of loading back the user starred app
* 1a1fb64166 [frontend] Fix issue where the html binding returns an "undefined" string for undefined values
* d45eba0fbf [editor] Display suggestions in editor2
* e699a62fff [frontend] Improve resiliency in the dataCatalog and add tests
* cdd632a52d [frontend] Fix issue in breadcrumb logic of SQL Context Popover
* 9d8fa93ba6 [catalog] Clean up and move Optimizer API strategy to Axios
* dca097e71d [frontend] Improve logic in cancellablePromise and add tests
* f14bf62fc2 [frontend] Add pubSub to trigger error alerts
* 322fd1abf8 [catalog] Move the samples fetch function to Axios
* add2c39005 [catalog] Move the partions fetch function to Axios
* 24c9f31ebb [catalog] Move the analyze and describe fetch function to Axios
* 6ee1f411b0 [catalog] Move navigator meta fetch function to Axios
* 24784de6db [catalog] Move autocomplete api handling to Axios and fix and issue where an error is shown on missing entity
* 0029d4d26d [frontend] Validate if a cached MultiStoreEntry exists before trying to merge it
* 2c4b2e140d [editor] Add custom response handler option to the API utils post
* f8341d8293 [editor] Fix exception when fetching comment in the autocomplete details panel
* 368afbe6c9 [catalog] Move the data catalog code to typescript and switch form jQuery deferrals to Promises
* 0342c875b4 [frontend] Have jest tests fail for unhandled promise rejections
* 04681e40ea [frontend] Fix API related types
* 678f46013d [frontend] Add cancel related improvements to CancellablePromise
* 5a9b778c06 [catalog] Replace string references with actual functions in the data catalog
* 6e7455639e [jb] Kill any running "jobs" in job browser errors
* 197f07d9fe [sqlalchemy] Use proper backticks when sending USE db statement
* 7b12cd1f31 Bump ini from 1.3.5 to 1.3.8
* add4f5ed3f [docker] Thrift sasl Python module needed for plain SASL sessions
* 1010c54d55 [stats] Adding monthly dialect execution to the stats
* 42daf782d5 [ci] Also show Python warning in Python 2 builds
* 05a6ae764d [notebook] Standardize fetch_result api to accept a request argument
* 77c22a3799 [HUE-9628](https://issues.cloudera.org/browse/HUE-9628) [Deprecation Warning] Using user.is_authenticated() and user.is_anonymous() as a method is deprecated
* e2462750b8 [ci] Show Python warnings when building with Python 3
* b2662de894 [docs] Slightly simpler toc for the admin section index page
* 0519528f61 [docs] Show how to test Editor 2 and the connector UI beta
* ea9d886ae0 [es] Add connector to docker image
* f1fd91a8c3 [docs] Fix indentations of connector examples
* 042a6ded61 [docs] Add dask-sql #1480 (#1489)
* 22669160f9 [hive] Show EXPLAIN errors as a regular message and not error popup
* a41b929f57 [con] Use upper case
* 192049ea55 [con] Fix styling
* b5a5a882f2 [con] Add dask-sql to the config tmpl
* 78205ab45b [con] Add dask-sql conn type #1480
* 32a8b39ef2 [sqlalchemy] 'NoneType' object has no attribute 'get'
* b64dbb35a9 [editor] Only display executed statement in query history
* f5e71367f3 [sql] Only auto perform USE db statement for dialect supporting it
* f388260de9 [dashboard] Convert _get_aggregate_function to method
* 08a0dad0cc [HUE-9561](https://issues.cloudera.org/browse/HUE-9561) [SQLAlchemy] Default selected DB does not seem to be used
* 74bd48e93c [HUE-9619](https://issues.cloudera.org/browse/HUE-9619) [Deprecation Warning] Importing from django.core.urlresolvers is deprecated
* f77e3ed1bc [HUE-9620](https://issues.cloudera.org/browse/HUE-9620) [Deprecation Warning] Passing a 3-tuple to django.conf.urls.include() is deprecated
* fa87482247 [HUE-9614](https://issues.cloudera.org/browse/HUE-9614) [Deprecation Warning] on_delete will be a required arg for ForeignKey in Django 2.0
* 771c3d75c5 [hdfs] Do not use object store home as home when not HDFS
* 42eb854867 [user] Default app loading can fail
* 575bef9cef [HUE-9623](https://issues.cloudera.org/browse/HUE-9623) [aws] Show S3 browser when IDBroker is enabled (#1467)
* dc1958b766 [HUE-9569](https://issues.cloudera.org/browse/HUE-9569) [core] Upgrade cx_Oracle from 5.2.1 to 6.4.1 (#1456)
* c67a4f79d3 [kafka] Use the proper notebook api client
* c8cf483016 [HUE-9608](https://issues.cloudera.org/browse/HUE-9608) [core] Sensitive Information Stored in Local Storage  (asnaik)
* c7ed2c5915 [opt] Dummy interface has some incorrect Python statements
* 24c8c42f81 [frontend] Upgrade Mustache to 4.1.0
* 9c31deb093 [editor] Switch to Axios for executor API logic in editor v2
* ad2c3a39a3 [frontend] Add qs lib for handling axios request data
* 7afaf074da [editor] Fix issue with reading back errors from saved queries in editor v2
* 6979b5fe09 [frontend] Switch to using the sqlParserRepository for the local optimizer strategy
* 38beadd444 [editor] Externalize sqlParserRepository for the AceAutocompleter Vue component
* b43ffd7dac [HUE-9605](https://issues.cloudera.org/browse/HUE-9605) [core] change_default_password config Not working in latest hue versions (#1448)
* 2817ff4b02 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [ui] Search input text is getting clipped
* f0a39eca55 GH-1459 [parser] Rename 'X Syntax Error Parser' in Syntax Parser live demo
* f8749bccf9 [editor] Set the AceEditor styles in the shadow css of the exported web component
* 7035ebd0df [editor] Consolidate AceEditor related styles
* b4c798b814 [editor] Add an autocomplete parser property on the AceEditor component
* a740fbed10 [frontend] Remove empty style blocks from the AceEditor components
* 782b6bee02 [frontend] Add scss to the style linter
* 9773880244 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [ui] Spinner component - Enabled display of both overlay and animated spinner
* 6b98f975a6 [frontend] Add the query-editor web component to the npm dist config
* 491b23396d [editor] Remove usage of global huePubSub in the Ace code
* 64aa9d3c9f [editor] Remove dependency on ko bindings from AceEditor component and related modules
* cf8ec6ece2 [editor] Remove snippet dependency from AceEditor component related modules
* 63c5029453 [frontend] Fix issue with I18n when the global HUE_I81n property isn't set
* 39ebbf87e6 [editor] Switch to axios for the format SQL ajax request
* c3de557958 [frontend] Add global web component attribute for hue base URL config
* b43e15e056 [editor] Add missing keyboard commands to the AceEditor component
* 78bffcf736 [ksql] Do not error when single column record not in json
* 2f59a2af63 [docker] snappy lib OS package is missing
* 1f85bc2644 [frontend] Update browserslist for jest
* 1807a72c28 [editor] Clear any error or success gutter markings once a statement is edited in Editor V2
* 61252e641a [editor] Properly mark error lines in Editor V2
* b67dd15d5d [core] Avoid 500 error in server mode when looking at stats
* 9ca8d9f0bf [blog] Fix broken style and old link in export doc via CLI
* df2fd5862e [HUE-9574](https://issues.cloudera.org/browse/HUE-9574) [core] Apply timeout to thrift-over-http calls (#1430)
* 38cb5dbe8c [k8s] Add password_script to database configuration (#1436)
* 6dbf85a973 [editor] Only cancel queries that are actually running when executing a new query
* 81b489ef20 [frontend] Fix webpack chunk naming for the impala and hive language ref dynamic imports
* 1c5ee053c3 [editor] Fix issue where duplicate error messages are shown for failed statements in editor v2
* 835d78dc58 [editor] Fix issue with missing handle on a failed query in Editor v2
* 11551cbaf2 [editor] Switch to using the new AceGutterHandler in the AceEditor Vue component
* a1a79fa0a2 [editor] Drop JQuery dependency from the AceEditor component
* 8dc1cb0dc0 GH-1437 [NPM] Add complete JS source into GetHue
* e1b1653280 GH-1437 [NPM] Add complete JS source into GetHue
* 198bcf8d8d [frontend] Consolidate localStorage logic in storageUtils
* c92cd01f2b GH-1432 [api] Add doAs header in proxied jobbrowser requests
* 14dc72c4e0 fix(boto): S3 region parser references unassigned variable when S3 is colocated
* 2bb10a2901 [frontend] Replace global totalStorage with native localStorage implementation
* ad3eefea7b [frontend] Convert hueUtils to typescript and remove custom polyfills
* c89395cef6 [frontend] Add missing types for sanitize-html
* f2085a42dd [editor] Fix file autocompletion issues in the new AceEditor Vue component
* 9cb9a2fe97 [editor] Support changing file paths from the context popover in the AceEditor component
* 6af9bb651d [editor] Add middle click copy and past support in the AceEditor component
* 766a95fbab [editor] Keep track of the cursor position in the AceEditor Vue component
* 2f925bcb8d [editor] Add placeholder a in the Ace Editor Vue component
* 5df0e65886 [editor] Automatically close the Autocompleter Vue component on scroll
* c56165ab94 [HUE-9573](https://issues.cloudera.org/browse/HUE-9573) [editor] Adding missing statements to the multi statement execution (#1429)
* 8971c7194d [importer] Create a phoenix table from a file
* 85629f0382 [connector] Fix no-oped server properties when using ssh
* 50abf47fca [connector] Support connector to same dialect but different interface
* d8ae378ae0 [HUE-9277](https://issues.cloudera.org/browse/HUE-9277) [spark] Support connectors in Livy client
* fe5c0ece14 [ci] Skip pylint on the generated DB migration files
* 1917a5ae02 [blog] Fix formatting of multi object returned troubleshooting post
* e2f186b664 GH-1424 [api] Support Hive query kill action in jobbrowser
* af374d43ce [core] User default app preference can have duplicate rows
* 06f74581dc [editor] Add support for various insert text events in the Ace Editor Vue component
* 16b88995c5 [editor] Clean up initialization of the AceEditor Vue component
* 0f4c24a72e [editor] Add support for dropping text in the editor Vue component
* 66f161ffb3 [docker] Add more sqlalchemy plugins
* b92c3efdda [HUE-9570](https://issues.cloudera.org/browse/HUE-9570) [ui] Rewramp deXSS with sanitize-html package (#1418)
* 305228740a [HUE-9567](https://issues.cloudera.org/browse/HUE-9567) [scheduler] missing minute field for Oozie Schedulers in Hue (asnaik) (#1412)
* 7388cf86ee [blog] k8s link refresh
* 5f15855bed [connector] Applying pylint styling fix to all the file
* b840a22c2e [docs] Directly point to the DB connector page
* f093e6cbcb [connector] Keep the nice name in connector creation
* c4dee20b21 [sparksql] Connector server url property has a wrong name
* e132540da1 [editor] Add an EditorResizer Vue component in editor V2
* f3c4bbe790 [editor] Emit value change event from the AceEditor component
* ea754975d5 [editor] Add support for ctrl-enter execution in the AceEditor component
* 142e1a0c23 [editor] Add support for "? from table" suggestions in the AceAutocomplete Vue component
* c99f3e5fe5 [editor] Make namespace and compute check async to speed up rendering of the AceEditor component
* a935ed671f [editor] Move suggestions and loading logic to the AceAutocomplete Vue component
* 38b3c7771f [editor] Add filter as key for autocomplete suggestions to prevent Vue js exception
* 61219c8517 [editor] Add temporary namespace requirement for the AceEditor component
* 59a7a9ae30 [editor] Add autocomplete details panel Vue components for set options, UDFs and SQL entities
* da54289b65 [editor] Fix Vue reactivity in the Ace Autocomplete component
* 4bd4519b1b [frontend] Migrate the autocomplete dropdown from Mako/Knockout to a Vue component
* 0918867c73 [frontend] Remove snippet dependency from autocomplete logic in editor V2
* 952a75ff13 [frontend] Add a Vue text match highlighting component
* 0a046d600d [frontend] Add a Vue spinner component
* 06fe15aedb [frontend] Add missing types for parsers, Ace and the data catalog
* 0e942f0a21 [editor] Remove snippet dependency from AutocompleteResults
* 2b07905f8a [editor] Add types for the data catalog and autocomplete parsers
* 1d86938ff8 [editor] Use the snippet ID as editor ID with the AceEditor component
* 3efbc8313b [editor] Add an AceEditor component
* cea0b5daef [editor] Add Ace types
* 5639dc1321 [editor] Add Knockout to Vue adapter component for the Executable Actions
* dca0b927c9 [editor] Remove snippet dependency from Ace location handler events
* 8b84791473 [editor] Add additional parser type definitions
* 754d03717d [frontend] Add types for huePubSub
* e5f82faa9f [jb] Explicitly set the has result flag in the kill query handle
* bb41a4bcbf [hive] Avoid error on empty EXPLAIN call
* 001b465349 GH-1390 [parser] Fix window is not defined bug when parser is used on node
* 105d0067f8 GH-1403 [parser] Fixed issue in handlinng Syntax Parser
* b8b35eb041 GH-1403 [parser] Live demo docs - Load er-diagram component from /js/gethue
* 30b93f919c GH-1403 [parser] Live docs - Added demo for all parsers
* e9e978bece GH-1403 [parser] Live demo docs - Add gethue into docs
* db465535dd [core] Use remote_storage_home as User profile home when set
* fcc0078a4b [blog] Querying live Kafka data in a Big Table like HBase Post
* 026e4dd8d0 GH-1390 [parser] Fixed issue with package.json created by npm run webpack-npm
* 84a7635b50 [k8s] Update helm list to work with helm 3
* f51be5f375 [parser] #1390 Publish Hue parsers as vanilla JS files, and move source files into src
* 6c54abfc70 [parser] Updating generated parser files #1390
* 19a809bea4 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) Added css properties to HueTable Column Interface
* f8eaa2de48 [jb] Style fix on the query API module
* d6c085cf6c [jobbrowser] Add Hive kill query via Notebook call
* 371e1d4d1c [jobbrowser] Show Hive Query Browser even if yarn not configured
* b3d73aec87 [phoenix] Automatically strip ; in non connector mode
* b822da1d63 [HUE-9564](https://issues.cloudera.org/browse/HUE-9564) [oozie] Oozie Jobs Submitted via Filebrowser Execute Options Doesnt Show Logs Button in workflow (asnaik)
* c6f6ce6e8a [HUE-9552](https://issues.cloudera.org/browse/HUE-9552) [fb] Folder Fails to Load when the foldername contains # (asnaik)
* 03f14a2a8f [jb] Fix COORDINATOR_URL has no attibute 'get' when Impala is blacklisted (#1383)
* 419fd43791 [HUE-9522](https://issues.cloudera.org/browse/HUE-9522) [useradmin] fix user home folder creation to use umask
* 30b70b4dbc [HUE-9381](https://issues.cloudera.org/browse/HUE-9381) [ui] Table ERD - Better CSS class support in entities
* 6654a21815 [docs] Help on building with mysql lib on latest Ubuntu
* 60b304321b [fs] Small pylint code refactoring
* 56cc487839 [core] Fix error handling in kt_renewer.py for python3
* 4e0cfc95a5 [docs] Add login security options section
* ef745d1775 [k8s] Adding annotation to hive configmap dependency
* bbd53584f9 [connector] Directly link to the connector page from editor menu
* 69a4f6f925 [k8s] Added Hive config map so API can read hive-site.xml options
* 3fb5782971 [notebook] Adding default explain() function
* 07a2d3a034 [flink] Avoid closing session on page refresh or editor close for now
* dedaaf8275 [flink] Protect against expired statement in check_status
* ea3a171287 [docs] Cleaner instruction for Ubuntu 20.04 and Python 3 build
* a78e6a7dcf Bump django from 1.11.28 to 1.11.29 in /desktop/core
* 8a9fb5120a [sqlalchemy] Protect against explain on empty statement
* 34633fff60 [build] Adding real package name help for debian
* e3fa6323a0 [HUE-9448](https://issues.cloudera.org/browse/HUE-9448) [editor] Hide the link to Impalad if COORDINATOR_URL is set
* e418e746ec [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Adding hue-flex-layout mixin (#1359)
* e36b455895 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Remove margins of Tab for better alignment
* 4bc9a123ee [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Make SQL text bg transparent
* 345a706b61 [HUE-9540](https://issues.cloudera.org/browse/HUE-9540) [query browser] API - List queries
* 0af5e238db [HUE-9521](https://issues.cloudera.org/browse/HUE-9521) [kt_renewer] fix to handle renew_lifetime if set to 0m
* ba4d59cf7f [HUE-9538](https://issues.cloudera.org/browse/HUE-9538) [core] user home directories are not created for Newly Logged in User (asnaik) review comments
* 8fefcfb249 [HUE-9538](https://issues.cloudera.org/browse/HUE-9538) [core] user home directories are not created for Newly Logged in User (asnaik)
* b3de83f82c [search] Include the Ace Solr editor mode
* 1e6c88ddea Get full list of interpreters for INTERPRETERS_CACHE (#1354)
* 73ccb78137 [editor] Show the stop button in red in editor v2
* 1755905992 [frontend] Add Fluid styling to the HueButton component
* b31fbbc7c4 [frontend] Update the fluid colors to the latest version
* 88a2612c23 [libs] Bump sqlparse version to 0.4.1
* 5d1d0c68d9 [py3] Remove confusion about extra requirement file
* d97e3c1153 [editor] Include the mysql Ace editor mode
* a7b16c695a [HUE-9517](https://issues.cloudera.org/browse/HUE-9517) [solr] fix for CSV file with pipe seperator or any seperator when importing
* b8eeb46ec4 [sqlalchemy] Adding explain() to notebook API
* bff9b896b4 [HUE-9518](https://issues.cloudera.org/browse/HUE-9518) [session] ability to change the csrf cookie age from default 1yr
* c1c6adf4b8 [notebook] Fix series of styling issues
* 5ce10a315d [querystore] Light code re-styling of download API
* 26d8fe6b7a [importer] Generate Flink create table with proper columns and topic
* af23eeb8b1 [importer] Use connector when submiting creation task
* a005494424 [importer] Add stream table output format
* e5691e3586 [ksql] Stop trucating end of result lines
* bc5bf0c7c9 [importer] Adding get_sample_data from a stream
* 5bff3cbe79 [ksql] List topics API
* 40dd8ab87a [ksql] Handle generator raised StopIteration on query result
* e82d4d79fe [ksql] Handle without exception when ksql API returns empty
* d763aa9101 [kafka] Small clean-up of the current lib
* 2f90794978 [editor] Include the pgsql Ace editor mode
* b2f7df035f [HUE-9514](https://issues.cloudera.org/browse/HUE-9514) [query browser] API - Add proxy authentication
* 3e9d2ea0b0 [docs] Point to the demo blog post of each dialect if available
* 7a702350fb [kafka] Small style clean-up of the current lib
* ce7c0a5603 [HUE-9510](https://issues.cloudera.org/browse/HUE-9510) [querybrowser] Config flag for proxy
* 075d097457 [tools] Max commit title lenght to 72 chars
* c001aeb25a Bump cryptography from 2.8 to 3.2 in /desktop/core
* 6c6904fe3c [HUE-9513](https://issues.cloudera.org/browse/HUE-9513) [core] Fix code styling
* f853ea0e8c [HUE-9513](https://issues.cloudera.org/browse/HUE-9513) [core] Improve Hue SAML response check: add defensive code invalid SAML case
* d21d6b1ad9 [pylint] Fix "line too long" Python Lint errors (#1287)
* f634863d48 [sparksql] Map application type to sql when opening session for sparksql (#1287)
* 0b8bcfa50c [fb] Fix lint indentation for filebrowser views
* 57e496ba03 [HUE-9505](https://issues.cloudera.org/browse/HUE-9505) [fb] Add slash back if it was removed by proxy
* 4d43ece562 [HUE-9511](https://issues.cloudera.org/browse/HUE-9511) [query browser] Correction in the filed of query_listing API
* a0f186b2bc [notebook] The default list of interpreter is not cached properly
* 7a42217fbb [frontend] Limit Webpack chunk size to around 1 MB
* 29a0077a10 [editor] Move the ace editor from static into the webpack bundles
* 53911fb05e [libs] Comment the chardet dependency in request module config
* 3cbd1a122e [HUE-9509](https://issues.cloudera.org/browse/HUE-9509) [ui] Create AlertBox component
* c80ec3f991 [HUE-9507](https://issues.cloudera.org/browse/HUE-9507) [querybrowser] API - Proxy log download API
* e11992fc3b [website] Swap connector and browser section on index page
* a6f8904ae0 [blog] Fix docker compose source link
* ccd43cc3d6 [HUE-9508](https://issues.cloudera.org/browse/HUE-9508) [querybrowser] Hue does not work with Hive/Impala enforced to TLS 1.2  (#1331)
* bc86386436 [core] Make cherrypy server compatible with py2 and py3 exception wise
* 8486b13e8e [editor] Replace the execute actions with a Vue components in editor v2
* 6a0642479f [libs] Adding decorator which is a pyphoenix dependency
* 58603fb972 [gethue] Update the landing page with latest Stream SQL posts
* 1afef572ed [blog] Tutorial on querying live streams of data with Flink SQL
* 373d0281a4 [blog] Tutorial on querying live streams of data with ksql (Kafka SQL)
* 7df4dd2858 [frontend] Fix issue where Jest can only resolve relative module imports
* 57b4129dbf [flink] Unify the session cache per user
* 963c69dc9e [docker] Do not run gunicorn in container
* 6dec5d17ed [HUE-9480](https://issues.cloudera.org/browse/HUE-9480) [frontend] Replace legacy static jQuery 2.2.4 with 3.5.1
* 885a206798 [HUE-9480](https://issues.cloudera.org/browse/HUE-9480) [frontend] Bump jQuery to 3.5.1
* f95a823ad0 [sqlalchemy] Support expired query history reload
* 49fd4e6158 [flink] Trim statement semi colon automatically as not supported
* d1fecd56a9 [docs] Clean-up of series of connector modules install instruction
* dddd3c1526 [docker] Add more connectors to py3
* fa079b7dc5 [HUE-9478](https://issues.cloudera.org/browse/HUE-9478) [api] Better format for RestException response
* 1773b9440b [HUE-9499](https://issues.cloudera.org/browse/HUE-9499) [ui] HueTable styling
* 80737a6ab5 [HUE-9494](https://issues.cloudera.org/browse/HUE-9494) [lib] Upgrade thriftpy 0.3.9 to thriftpy2 0.4.12
* 7a6b61f09e [HUE-9494](https://issues.cloudera.org/browse/HUE-9494) [lib] Upgrade parquet from 1.1 to 1.3.1
* 760a2f5444 [HUE-9494](https://issues.cloudera.org/browse/HUE-9494) [lib] Upgrade ply from 3.9 to 3.11
* 6013b1057a [HUE-9494](https://issues.cloudera.org/browse/HUE-9494) [core] Patch hashlib md5 for FIPS
* 964b7a2ba5 [docker] Add pip uninstall of chardet (#1315)
* 7a9e5232dd [HUE-9500](https://issues.cloudera.org/browse/HUE-9500) [ui] Comment is not shown when view the table info from table browser first time (asnaik)
* 8b062af018 [HUE-9500](https://issues.cloudera.org/browse/HUE-9500) [ui] Comment is not shown when view the table info from table browser first time (asnaik)
* 412bcfd4cb [HUE-9500](https://issues.cloudera.org/browse/HUE-9500) [ui] Comment is not shown when view the table info from table browser first time (asnaik)
* b68f53160c [libs] Fix the pydruid lib to compile with Python 2
* 9cd125aaea [docker] Update the docs about the renamed hue ini override
* e62f3f80d6 [docker] ini overrides is not picked up after the main hue.ini
* 4fa3c55f25 [desktop] Fix the Python styling of config files
* 33d69b024f [notebook] Do not lose Hive/Impala when adding sqlalchemy connectors
* 5735b35f2c [tools] First step of simplifying commit messages
* 33ab9f080c [libs] Adding pydruid 0.4.5
* 56b448d115 [notebook] Refactor check permission decorator to explicit name (#1306)
* 68aaa93873 [k8s] Add podLabels to values (#1305)
* d1533b0d93 [HUE-9458](https://issues.cloudera.org/browse/HUE-9458) [ui] UI-build - Enable extending of webpack config for custom builds
* 488cb065ce [docs] Move Python API items to expected title size (#1304)
* 67612201d8 [docker] Drop install of Phoenix modules as already included (#1299)
* ac051f3d2f [libs] Adding requests-gssapi module for out of the box Phoenix connector (#1299)
* 5eca90f404 [libs] Adding protobuf module for out of the box Phoenix connector (#1299)
* 124ace4eb1 [libs] Adding gssapi module for out of the box Phoenix connector (#1299)
* 37f0d4f4da [importer] is failing with "global name '_create_table' is not defined" (#1297)
* 6de3e1cac0 [docs] Refresh the download restriction properties (#1295)
* 17a325d61c [popover] Give more room to column names (#1293)
* ada905ecc0 [HUE-9497](https://issues.cloudera.org/browse/HUE-9497) [query browser] Facets selection and improving unittest
* be25bb1007 [docs] Adding the notion of Flink connector (#1292)
* aa649cfa66 [docs] Freshen-up the main sections description (#1292)
* ff4bc4c159 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Explicitly uninstall chardet module
* 76a95804be [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [sqlalchemy] Properly propagate back expired queries
* 36126a0675 [desktop] upgrade kazoo to 2.8.0 (#1278) (#1290)
* 9be678c5dd [HUE-9492](https://issues.cloudera.org/browse/HUE-9492) [query browser] adding unittest for Api query listing, pagination, query_count
* 312d93fc5e [HUE-9492](https://issues.cloudera.org/browse/HUE-9492) [query browser] Text search, date filtering and pagination
* 5c21d7aa53 [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [importer] Move out _envelope_job() into the envelope module
* 088b649b97 [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [importer] Move out _create_solr_collection() into the Solr module
* f9cecc691a [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [importer] Move _create_database() to the sql module
* eada8dfdf2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [importer] Reformatting and styling of sql tests
* 049b3d15fb [HUE-8840](https://issues.cloudera.org/browse/HUE-8840) [indexer] Clean unused part of index() API
* 8bcd9b2184 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [importer] Avoid 'S3FileSystem' object has no attribute 'split'
* 6323311a94 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [indexer] Use user and not username in Morphline client
* 42a300497f [HUE-9496](https://issues.cloudera.org/browse/HUE-9496) [assist] Fix js exception on missing database/table in the right assist
* bda374ec71 [HUE-9495](https://issues.cloudera.org/browse/HUE-9495) [assist] Fix drag and drop from left assist on initial load
* 4264db764f [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [importer] Skeleton of refactored API with index()
* 979e636402 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a FacetSelector Vue component
* e94f49f4fc [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add disabled prop to the DrodownPanel component
* 6740273273 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add spinner to the StatusIndicator component
* e9829de269 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Update pip module information for ksqlDB
* 4fcfd00846 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [importer] List Kafka streams as input
* 8f1743b030 [HUE-9493](https://issues.cloudera.org/browse/HUE-9493) [libsaml] allow accepted_time_diff configure for pysaml (#1288)
* 181021b8c5 [HUE-9478](https://issues.cloudera.org/browse/HUE-9478) [api] Job browser proxy
* 559ebbe85f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Set configparser version to be Python 2 compatible
* f333248b55 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Expose clear on the DateRangePicker component
* 6bd7a19a87 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Enable v-model binding on the SearchInput component
* bf5417cfa9 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add small and primary options to the HueButton component
* 4e90c95d0b [HUE-9368](https://issues.cloudera.org/browse/HUE-9368) [docs] Fixed formatting of config snippets
* c23a0ff4ba [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [notebook] Format Python style of base module
* cca7ba069d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [notebook] Remove wrong parameter in QueryError exception
* 255f43ba66 [HUE-1450](https://issues.cloudera.org/browse/HUE-1450) [docs] Adding connector listing and simplify tokens
* b5173e8447 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [admin] Harmonize links to User and Server administration
* eb1be2acb6 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [orgs] List groups and permissions on org page
* 9fc0d4af9d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Adding ConnectorNotFoundException
* 9563350784 [blog] localized kubernetes blog post (30, Sep 2020) into Japanese (#1281) (#1286)
* c814a3bedb [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [assist] Adding model icon to context popover
* 114ac66b00 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [metastore] Add notion of table ML models
* 541d6597e5 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a date range picker dropdown Vue component
* f2c2172dbb [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a filter svg icon
* 3a204bbc41 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add vuejs-datepicker third party lib
* 82eb5eb57d [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Use link for paginator dropdown
* d8c8d0a5dc [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Pass close action to slots of DropdownPanel
* 96c3d0364e [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Extract a generic DropdownPanel component from the DropdownMenu
* 071d0c66e7 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Fix the SqlText Vue component and add option to format
* 75415c2161 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add async format SQL to notebook ApiUtils
* aa2cc30c79 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue StatusIndicator component
* c70fd1e772 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Prevent the Dropdown component from showing outside the viewport
* 8e4085629e [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a nowrap option for table columns in the HueTable component
* a76f074fdb [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a click outside directive and enable it in the Vue Dropdown component
* 252127aea6 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Initial styling of the Paginator component
* d5e7977c06 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a HueIcon component
* da0a97a003 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Initial styling of the HueTable component
* 168526cc00 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Initial styling of the Column Selector panel
* 7269d105e9 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a SearchInput Vue component
* 9cd9291d3d [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Fix bugs in the Paginator and HueLink components
* 7884515656 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Create a HueButton Vue component
* 5be112340c [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Rename the Link component to HueLink to prevent conflict with existing HTML tag
* 38cfbb8ca1 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Switch to slots for dynamic cell contents in the HueTable components
* abb74d2b4c [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Link component
* 89590d2000 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Style the Tabs component
* 38c3f1a6cb [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Switch to Fluid colors for Vue components
* dcb2703e8b [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Switching to code get reader to load back data
* a3bed20bd8 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [docs] Mention NGINX settings with queries timeout
* 5bab7752bf [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Switch data to binary before sending to storage
* 68d09150f5 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Switch to binary for storage format
* 30571fe8a7 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [sqlalchemy] Adding a pre-ping option when picking up connection
* 490117da7b [HUE-9490](https://issues.cloudera.org/browse/HUE-9490) [jobbrowser] API - Listing Hive query details
* 6bf802eb83 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Added new NPM dependencies
* 8dbec40f35 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add lazy rendering for tabs
* c2cc6acf75 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [docs] Improve reference to the Task Server
* 35fc44da1e [HUE-1052](https://issues.cloudera.org/browse/HUE-1052) [k8s] Resolve a race between hue and pgSQL startup (#1284)
* 1fc9c13c82 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] How to Quick check SQL connections in Kubernetes
* f972a25ee7 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Set muffet crawler explicitly to a certain version
* 7b3f6ebe05 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Explain where to get Bq json credentials
* 77eb665a07 [HUE-9489](https://issues.cloudera.org/browse/HUE-9489) [core] Make apps can fail because of config dependency
* 6dc3509835 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Offer to filter connector list by id
* 39db856150 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplify and update the roadmap page
* d397c7f872 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Switch to using the Dropdown component in the Paginator and some initial styling
* 925054a0f2 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Dropdown Vue component
* e4cac04460 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add scss colors and mixins modules
* db2b40e493 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue Paginator component
* 7d572fdb40 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Fix bug in the Duration component
* e6c5ce2a62 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a short duration format option for the Duration component
* 4c1cc1e6ad [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue Duration component
* eaff00fd42 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a click event on the HueTable row
* 4bdd836e55 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue HumanByteSize component
* ff025e9ede [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add luxon lib for handling date and time
* 31b79bf671 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add additional tests for the HueTable Vue component
* 580004c00f [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add support for custom table cell components and data adapters in the HueTable Vue component
* 557ba6eb5d [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue TimeAgo component
* 5c57e22645 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Fix issues with the ColumnSelectorPanel
* 414ce4a318 [HUE-9486](https://issues.cloudera.org/browse/HUE-9486) [ui] Add json resolution to TS config
* 607e1dd195 [HUE-9482](https://issues.cloudera.org/browse/HUE-9482) [ui] Use PascalCase for the QueriesList component
* d66c0c42be [HUE-9486](https://issues.cloudera.org/browse/HUE-9486) [ui] Fix conflicts with the Vue linter and prettier
* 54510a6608 [HUE-9486](https://issues.cloudera.org/browse/HUE-9486) [ui] Apply new linting rules
* d5e3be9e21 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue column selector component
* 3baf271106 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue SQL text component
* 35edb17e9f [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue tabs component
* b04127cfe3 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue modal component
* b704a14b94 [HUE-9485](https://issues.cloudera.org/browse/HUE-9485) [frontend] Add a Vue table component
* 30f31dc6c9 [HUE-9484](https://issues.cloudera.org/browse/HUE-9484) [frontend] Warn if jest tests are trying to make actual ajax requests using Axios
* 3a8fd1d6db [HUE-9484](https://issues.cloudera.org/browse/HUE-9484) [frontend] Add axios framework for ajax requests
* 79fabac564 [HUE-9456](https://issues.cloudera.org/browse/HUE-9456) [editor] Fix presentation mode variable substitution in editor v2
* 4cd0034823 [HUE-9487](https://issues.cloudera.org/browse/HUE-9487) [editor] Open in Editor Option Redirects to Default DB rather than expected one (#1282)
* 2bebc7832c [blog] localize blog posts into Japanese (Aug, Sep 2020) (#1274) (#1281)
* f10e40e6c8 [HUE-9467](https://issues.cloudera.org/browse/HUE-9467) [sqoop] Hue showing Sqoop command as running even when its finished (#1279)
* ebdf2cbe85 [HUE-9477](https://issues.cloudera.org/browse/HUE-9477) [ci] Allow Revert commits in the commit message check
* 2aa20153c3 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [ci] Upgrade jsdom to avoid jest Cannot read property 'some' of undefined
* a5b03195a6 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [blog] Adding signature to the release notes
* 00b6037d59 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [blog] Fix typo in past 4.7 release link
* 2d6b75190f [HUE-9374](https://issues.cloudera.org/browse/HUE-9374) [impala] Apply proxy endpoint to server URL
* d6c57a4d40 [oozie] Fix usage of iterkeys() and zip() in list_oozie_info template (#1270) (#1271)
* 7eb455c950 [HUE-9390](https://issues.cloudera.org/browse/HUE-9390) [docs] Simpler instructions on how to update mysqlclient
* 9de217d6b6 [HUE-9276](https://issues.cloudera.org/browse/HUE-9276) [release] Perform 4.8 release

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
* Akhil Naik
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
* emmanuel
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
* Harshg999
* Harsh Gupta
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
* Justin Bradfield
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
* Nils Braun
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
* penggongkui
* Peter Slawski
* Philip Zeyliger
* Piotr Ackermann
* pkuwm
* Prachi Poddar
* Prakash Ranade
* Prasad Mujumdar
* Qi Xiao
* Raghunandana S K
* rainysia
* raphi
* rdeva
* Reinaldo de Souza Jr
* Rentao Wu
* Renxia Wang
* Rick Bernotas
* Ricky Saltzer
* Robert Wipfel
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
* Tomas Coufal
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
* Yuanhao
* Yuanhao Lu
* Yubi Lee
* Yuriy Hupalo
* ywheel
* z00484332
* Zachary York
* Zach York
* Zhang Bo
* zhang-jc
* Zhang Ruiqiang
* zhengkai
* Zhihai Xu
* z-york
* 小龙哥
* 王添
* 白菜
* 鸿斌
