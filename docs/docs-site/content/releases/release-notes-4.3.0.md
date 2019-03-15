---
title: "4.3.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -4030
tags: ['skipIndexing']
---

### Hue v4.3.0, released October 17th 2018


Hue, http://gethue.com, is an open source Analytic Workbench for developing and accessing Data Apps.

Its main features:

  * Editors for SQL querying (Hive, Impala, MySQL, Oracle, PostgreSQL, SparkSQL, Solr SQL, Phoenix ...) or job submission: Spark, MapReduce, Pig...
  * Dashboards to dynamically interact and visualize data with Solr or SQL
  * Scheduler of jobs and workflows
  * Browsers for Jobs, Metadata (Tables, Indexes, Sentry permissions) and files (HDFS, S3, ADLS)

Read the complete list of improvements on [Hue 4.3 and its Analytics and Django improvements are out!
](http://gethue.com/hue-4-3-and-its-app-building-improvements-are-out/).


Summary
-------
The focus of this release was a big refresh to upgrade Django to 1.11, the latest Python 2 compatible version at the time.
It contains a log of improvements for the SQL editor variables and catalog, as well as for the Dashboarding. It also prepares the ground for multi cluster support ([HUE-8330](https://issues.cloudera.org/browse/HUE-8330)).


Notable Changes
---------------

* Upgraded core backend to Django 1.11 and now requires Python 2.7.x.
* Improved SQL Exploration
* SQL editor variables
* Simplifying the end user Data Catalog search
* Get a mode to allow easy profiling of requests
* Finer grain privileges in the Sentry App
* Improved dashboards layouts
* Improved job scheduling monitoring
* Improved Oozie Workflow Graph display


Compatibility
-------------

Runs on CentOS versions 6, Red Hat Enterprise Linux (RHEL 6, 7), and Ubuntu 14.04 and 16.04.

Tested with CDH6. Specifically:

- Hadoop 3.0
- Hive 2.1
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


List of 900+ Commits
---------------------
* af707ff HUE-8634 HUE-8111 [core] Perform 4.3 release
* 3954a71 HUE-8630 [core] Fix TestMetastoreWithHadoop.test_basic_flow _get_apps
* cd66da2 HUE-8635 [editor] Add the correct styles to the language reference context popover
* 28d5c86 HUE-8629 [assist] Don't show a database icon in the breadcrumb of non sql type assist panels
* 492db60 HUE-8629 [assist] Make sure entries are loaded in left assist for non sql types
* cc20c76 HUE-8629 [assist] Add a dedicated streams assist panel
* 3e630b0 HUE-8629 [assist] Customise the assist icons for streams
* 07cb81b HUE-8629 [assist] Improve assist context menu for kafka
* dbc26ad HUE-8140 [editor] Automatically continue execution after DDL statements in batch mode
* 42ad806 HUE-8612 [editor] Improve the editor shortcut search to show results from all categories
* 4b46742 HUE-8612 [editor] Add missing keyboard shortcuts to the editor help
* f5aa6f2 HUE-8621 [editor] Add dark mode keyboard shortcut to the editor help
* bdd1c49 HUE-8630 Fix TestRdbmsIndexer missing RdbmsIndexer
* 094274e HUE-8624 [beeswax] Fix tests on create database to redirect on a v4 page
* 60fd4fe HUE-8630 [fb] Fix TestFileBrowserWithHadoop.test_index home_directory
* 22fcf93 HUE-8626 [security] Fix navigation issues after visiting the security app
* 8e91479 HUE-8628 [assist] Indicate context in the left assist filter placeholder
* 2dfb76b HUE-8627 [frontend] Add partition result view to the top search
* c95bf9a HUE-8623 [frontend] Send cluster when checking if a table or database exists in the importer
* 16fc204 HUE-8621 [editor] Add keyboard shortcut to toggle dark mode
* 79b63e4 HUE-8621 [editor] Add ace option to toggle dark mode
* c3f760b HUE-8621 [editor] Add a custom Ace mode for the dark theme
* 5ae8607 HUE-8619 [tb] Switch to POST for partitions API call
* 4bc7386 HUE-8619 [tb] Include cluster in the partitions API call
* 7564b86 HUE-8618 [editor] Prevent js exception when typing while the context is loading
* d5f246a HUE-8577 [autocomplete] Fix issue where the statement type location is added twice
* 1b4a565 HUE-8608 [useradmin] Add config check on number of documents
* 6e4c9cb HUE-8625 [editor] Prevent js exception when dragging from top search to the editor after visiting the importer
* e76e9fe HUE-8602 [sentry] Remove ALTER and DROP in the Hive section
* 42693af HUE-7860 [core] Add monotonic 1.5
* b1c6a50 HUE-7860 [core] Add dnspython 1.15.0
* 6bdb3ac HUE-7860 [core] Update greenlet from 0.4.12 to 0.4.15
* 4ccbae6 HUE-7860 [core] Update eventlet from 0.21.0 to 0.24.1
* 8a5a620 HUE-7860 [core] Update Gunicorn from 19.7.1 to 19.9.0
* 6914b41 HUE-8617 [frontend] Add pubSub to the context selector for setting cluster/compute/namespace
* 45e834e HUE-8615 [frontend] Make sure namespaces and computes always have a name in the context selector
* 25cf13b HUE-8614 [tb] Fix the create new database action in the Table Browser
* ab4fb35 HUE-8613 [tb] Send cluster when dropping databases from the table browser
* a537d64 HUE-8610 [core] Always send the full cluster instead of id to the APIs
* 2fe317e HUE-8611 [assist] Send cluster parameter with the invalidate calls
* 653e808 HUE-8610 [tb] Include compute in stats and describe table calls from the table browser
* 22543b6 HUE-8610 [tb] Make sure the created notebook for samples requests has the provided compute
* 3e5ac80 HUE-8610 [tb] Include compute when fetching samples from the table browser
* 296a63f HUE-8609 [tb] Fix exception in describe table call from the Table Browser
* fda9b9f HUE-8606 [s3] Opening S3 browser makes a call to HDFS
* d15edf6 HUE-8607 [tb] Include namespace when querying a table from the table browser
* b79bd55 HUE-8607 [tb] Fix query and view table actions in the table browser
* 2634f31 HUE-8607 [tb] Fix broken drop table action in the table browser
* 490898d HUE-8604 [frontend] Use the latest opened database by default throughout
* 8b92740 HUE-8603 [editor] Always show the query compatibility check results
* ba9e654 HUE-8602 [sentry] Remove ALTER and DROP table privileges for now
* 6fee714 HUE-8599 [frontend] Add pubSub to force clear the context catalog from the job browser
* 8ac92d4 HUE-8601 [jb] Fix issue where context selector in mini jb is hidden behind expand text
* 0d16263 HUE-8600 [tb] Limit Table Browser namespace selection to namespaces with active computes
* da9f525 HUE-8599 [frontend] Improve stability of the context selector
* 25a65e5 HUE-8597 [frontend] Use the default SQL interpreter as source type in the global search results
* afd3fa0 HUE-8564 [useradmin] Fix last activity update for notebook/api/check_status
* c46696d HUE-8592 [frontend] Enable default click to navigate for catalog entries table
* 1004af8 HUE-8592 [frontend] Add option to automatically refresh samples in the catalog entries table
* 196fb81 HUE-8592 [frontend] Create a polling catalog entries list component that waits until an entity exists
* 9c00548 HUE-8595 [flume] Collect and ingest Hue balancer logs out of the box
* 1dcdefb HUE-8594 [editor] Avoid js error when lastSelectedCompute does not exist
* 522bf8c HUE-8580 [importer] Fix RDBMS support for scoop configured import.
* 73a53d3 HUE-8591 [cluster] Remove extra debug info
* 381e044 HUE-8591 [impala] Properly point to the selected cluster hostname
* 159f64a HUE-8591 [impala] Properly pickup the selected compute cluster
* b7b5171 HUE-8591 [cluster] Step of logic simplification of the multi cluster configuration
* 82b6eba HUE-8591 [cluster] Avoid failing when cluster is None
* 613c8d7 HUE-8591 [cluster] Add Thrift client used for the specific query server
* 3f21f54 HUE-8591 [cluster] Use properly Impala Thrift Client on remote Impala cluster direct connection
* 0a288f3 HUE-8339 [impala] Fix typo in smart pooling ini configuration
* 6a945fc HUE-8591 [cluster] Prevent red error popups
* af5e2cc HUE-8591 [cluster] Add impalad link to cluster page
* f6c27df HUE-8591 [cluster] Add some progress bar color and effect on cluster resize
* a2aa497 HUE-8591 [cluster] Split cluster template between static and dynamic clusters
* c6fd74f HUE-8591 [cluster] Add hostname check in the cluster hostname log trace
* 8fbe00a HUE-8591 [cluster] Protect against override of cluster name
* b203527 HUE-8591 [cluster] Move port to 21050
* 0fe3c21 HUE-8591 [cluster] Use default port if ont in a selected remote cluster
* 673e764 HUE-8591 [cluster] Clear the compute cache on namespace refresh from left assist
* 5d9e18a HUE-8591 [cluster] Refresh the context selector when namespaces are refreshed
* 581cd51 HUE-8591 [cluster] Fix name of default cluster
* d3a1a7d HUE-8591 [cluster] Safeguard against localhost
* e5fcadc HUE-8591 [cluster] Use name as clusterName throughout the calls
* 85d23d4 HUE-8591 [cluster] Properly use the correct cluster hostname in the editor
* 0db8805 HUE-8591 [cluster] Display impalad hostname
* db993bb HUE-8591 [cluster] Add logic to get the corresponding Impalad name
* 605c500 HUE-8591 [cluster] Hook in remote Impala coordinator URL of selected cluster
* 645a357 HUE-8591 [cluster] Adding cluster resize capabilities on the cluster page
* 26c336a HUE-8591 [cluster] Wire in API for listing and creating k8 clusters
* 9aaf2a5 HUE-8591 [cluster] Move API url to a config property
* 242744c HUE-8591 [cluster] Plug in the list of clusters
* bddb67c HUE-8591 [cluster] Add proper cluster page
* 4b9f986 HUE-8591 [cluster] Integration skeleton for Data Warehouse v2 API
* a2baf17 HUE-8591 [core] Showing up S3 browser by default in cloud mode
* 5d6a52b HUE-8578 [importer] Implement Flume output
* 77447ff HUE-8578 [importer] Get basic Flume ingest step integrated
* 84ee44f HUE-8589 [jb] Switch from compute to the cluster API endpoint in the job browser
* 3860649 HUE-8589 [core] Split cluster listing to its own API
* 2672adb HUE-8588 [core] Fix PAM backend has conflict with timer metrics
* b49e98c HUE-8580 [importer] Improve usability of table import
* deb270a HUE-8570 [editor] Enable click to insert from sample popover to SQL variables
* f4e1bf3 HUE-8570 [assist] Add min and max to column sample popover
* a4d7b55 HUE-8580 [editor] Fix jdbc assist.
* f1b3b05 HUE-8575 [importer] Fix file to table import.
* deaec54 HUE-8577 [autocomplete] Add support for Impala SHOW GRANT ROLE/USER statements
* c5a3e7e HUE-8577 [autocomplete] Add support for Impala ALTER TABLE/VIEW SET OWNER
* 8c7afe9 HUE-8577 [autocomplete] Add all currently reserved keywords for Impala
* 2e6d187 HUE-8581 [importer] Improve query type selection layout for the field editor
* c6c9692 HUE-8582 [jb] Make back button from editing a file more obvious
* cc69a15 HUE-8583 [fb] Surface too many buckets error
* 03e2acc HUE-8579 [core] Blacklisting certain apps like filebrowser and oozie can fail
* 46ef4df HUE-8578 [importer] Auto select id column if present in Kudu tables
* 98769a2 HUE-8578 [manager] Restrict API calls to admin
* e4f9394 HUE-8581 [importer] Improve the stream import form layout
* 2260272 HUE-8581 [importer] Fix JS error for field query editor in importer
* 65223ea HUE-8581 [importer] Fix JS error on target namespace selection and improve layout for table import
* 415b35d HUE-8581 [importer] Fix timing related JS exceptions
* 2ee6143 HUE-8581 [importer] Allow typed paths in the hivechooser binding
* a31399a HUE-8577 [autocomplete] Make previously non-reserved keywords reserved for Impala
* 47f6dfc HUE-8577 [editor] Rebuild Ace with updated dependencies
* b1aba65 HUE-8577 [autocomplete] Add Impala METHOD to reserved keywords
* 961a357 HUE-8576 [editor] Add backticked suggestion to the syntax checked for reserved keywords
* 7bbb9b1 HUE-8575 [importer] Add external multi table support
* c0e0a7a HUE-8574 [importer] Feature flag for showing the Field Editor
* 1f91325 HUE-8574 [importer] Adding Flume flows
* 2c01cd0 HUE-8574 [importer] Setup automatically a Flume grapping Hue HTTPD logs and put into the sample collection
* 7511c6f HUE-8574 [cluster] Auto scaling data warehouse cluster API skeleton
* 92be4b7 HUE-8574 [flume] Support updating Flume agent config
* 3e1463d HUE-8574 [importer] Allow audit logs to be sent to Solr
* 299555d HUE-8574 [importer] Button caret to call for getting the job config
* 8367135 HUE-8574 [importer] Nav Kafka stream import to Solr and Kudu part 1
* 93a284c HUE-8572 [cluster] Bubble up authentication errors on remote clusters
* 6e9b391 HUE-8568 [jb] Activate smart file links from the logs by also checking for prefixes
* 51c96e3 HUE-8573 [sqoop] Avoid unrelated casting error when testing the connection
* 736d824 HUE-8573 [sqoop] Out of the box import of a MySQL table
* 6fed8d8 HUE-8568 [jb] Prevent mini jb actions from taking content width
* 763b15f HUE-8567 [jb] Fix id max length in mini jb
* 8799711 HUE-8572 [tb] Fix log overflow in history panel
* af30c70 HUE-8572 [tb] Add compute and namespace to DROP table endpoint
* ce92900 HUE-8572 [tb] Fix JS exception when clearing table browser selection via pubsub
* 022adc6 HUE-8570 [assist] Limit context popover sample operations to Impala and Hive
* 9a15e8e HUE-8571 [sentry] navigator_api ERROR for PRIVILEGE_HIERARCHY[hierarchy[server][SENTRY_PRIVILEGE_KEY]['action']]
* 0904ed0 HUE-8557 [sqoop] DB name and table names variables were already present
* 693d5c1 HUE-8570 [assist] Add distinct as an option for column samples in the context popover
* 03a64a0 HUE-8570 [editor] Enable optional operation on the sample API endpoints
* 2d59df8 HUE-8570 [frontend] Right align the Hue dropdown when rendered outside the window
* 4d56cb3 HUE-8570 [assist] Add inline autocomplete for column samples
* 0ae514e HUE-8570 [assist] Extract a separate column sample component
* 8e3c411 Updated user-guide.md - spelling fixes
* efbe3a2 HUE-8488 [fb] Disable drag&drop when show_upload_button=false
* b79146d HUE-8550 [jb] Default to the last selected type of compute in the job browser
* 681e310 HUE-8566 [useradmin] Update message for duplicate user creation.
* 571950a HUE-8565 [fb] Parent directory should not be selectable
* ecadf6e HUE-8565 [fb] Current directory should not be deletable.
* 6c50f29 HUE-8559 [jb] Hue shows incorrect color for failed oozie jobs
* c0b034e HUE-8556 [fb] Overuse of trash folder checking
* 02d98ed HUE-8562 [frontend] Make sure the context popover is shown above the jobs panel
* 92a577d HUE-8561 [editor] Don't show databases for spark editor
* a1a023d HUE-8560 [tb] Stick to the same view when switching namespaces in the Table Browser
* 9da1e83 HUE-8560 [tb] Make sure the default DB is opened by default in the Table Browser
* 29984ab HUE-8557 [sqoop] Offer to rename the table or selected a different existing Hive database
* d8ed540 HUE-8555 [cluster] Do not submit remote coordinator jobs by default
* d52f6aa HUE-8551 [importer] Support setting basic Flume configs
* 0689ffb HUE-8544 [importer] Support sending file data into a kafka topic
* 03807c6 HUE-7698 [oozie] Added warning when there is a space in the shell action
* 703eed0 HUE-8555 [jb] Refactor job browser preview to support multi cluster
* d0e7f0f HUE-8555 [jb] Sort clusters with the most recents first
* 43939d1 HUE-8509 [oozie] Support sending a SQL query to a remote cluster
* ca2da8b HUE-8555 [jb] Support killing data warehouse cluster
* d06a7c0 HUE-8555 [jb] Auto select the first cluster if possible at init
* f0d99d2 HUE-8555 [jb] List data warehouse clusters
* 8a28afc HUE-8554 [cluster] Avoid double escapating of data warehouse results
* d1c929c HUE-8554 [cluster] Rename analytic cluster API command to dataware
* 53a8762 HUE-8554 [cluster] Create data warehouse cluster skeleton
* 09c6a49 HUE-8554 [indexer] Protect against empty sample data that can be null
* da58f9d HUE-8554 [core] Support dist Spark installed when running envelope via shell
* 4cbed79 HUE-8509 [oozie] Properly set the capture output flag of shell document action
* 33222b5 HUE-8554 [importer] Support latest Spark version 2 natively
* 46250da HUE-8553 [kafka] Link create topic API to the UI
* cd29a58 HUE-8554 [manager] Adding a check if service is installed API
* 74f835c HUE-8553 [kafka] Add a workaround API for creating a topic
* 26d8d3b HUE-8509 [oozie] Schedule repetitive remote jobs
* 926816a HUE-8509 [oozie] Remote job action
* d26915e HUE-8509 [jb] Clean-up of the listing of remote jobs
* 3526a83 HUE-8552 [oozie] Add context popup to preview linked document actions
* 05cca7a HUE-8509 [kafka] Do not break left panel
* a83360b HUE-8558 [jb] Add tracking URL to Spark Jobs and remove url and killUrl
* 04fd4a4 HUE-8547 [jb] Fix navigation from create schedule to view schedule.
* 63cc1a4 HUE-8548 [jb] Fix invalid date in workflow task
* b0f0da1 HUE-8550 [frontend] Make last selected compute and namespace sticky
* 0d63b5b HUE-8550 [jb] Refresh job browser tabs on compute selection
* 67a4af1 HUE-8550 [jb] Use the context selector component in the job browser
* 894f6b3 HUE-8549 [autocomplete] Improve CTE alias suggestions when there's a trailing ";"
* 49ca1ba HUE-8542 [frontend] Polish cloud cluster and require multi cluster mode to be on
* 159cc59 HUE-8391 [importer] Improve Create table from File UX when loading data from parent directory not readable by hive/impala
* 77b97f0 HUE-8546 [assist] Limit assist refresh to the active namespace for DDL statement executions
* 04448bb HUE-8546 [assist] Make sure the assist gets refreshed after multiple DDL statement executions
* b215bd4 HUE-8545 [search] Fix filtering in the index selection dropdown
* 1d923f8 HUE-7698 [oozie] Added warning when there is a space in the shell action
* 66fe27b HUE-8547 [jb] Fix refresh on coordinator page.
* 0b9641c HUE-8507 [editor] Add types to sqlalchemy results.
* cd95f63 HUE-8542 [frontend] Add a custom left nav for multi cluster mode
* 521e993 HUE-8540 [sqoop] Add ability to set default jdbc driver path for any sqoop job
* 7d74fab HUE-7698 [oozie] Files of a Shell document action in a workflow are not being generated in the XML
* 4139a02 HUE-8541 [oozie] Workflow rerun does not restart polling for job status
* e201177 HUE-8523 [jb] Display Impala backends & instances
* d4e0bd0 HUE-8522 [jb] Make paused tasks more obvious. Add queued state to Impala
* 5c3d5d8 HUE-8532 [core] Fix database migration test.
* 0273da6 HUE-8538 [sqoop] Allow table preview from manual input not JDBC
* 1cd55fd HUE-8139 [core] Fix django-debug-toolbar 1.9.1 to work with django_debug_panel* remove toolbar middleware to enable SQL panel* Fix middlewares to enable capture Ajax calls
* 598a47d HUE-8539 [importer] Clean-up configuration and turn sqoop and solr imports to on by default
* 54bb092 HUE-8538 [importer] Automatically fill-up the db driver list when selecting sqoop
* 9d7a3e1 HUE-8537 [sqoop] List the proper column type when importing to a hive table
* 8e82a3b HUE-8536 [sqoop] Include hive-site.xml automatically when importing data to hive
* 8887c61 HUE-8535 [sqoop] Use the proper engine name and not the connection nice name as jdbc prefix
* ba83e54 HUE-8534 [jb] Django url name does not exist and breaks page
* d1fef53 HUE-8533 [importer] Properly displayed failed import progress bar as red and not orange
* 523b32a HUE-8531 [sqoop] Properly name the table import job
* 85b796a HUE-8529 [frontend] Create a context selector component
* 628ad2d HUE-8528 [frontend] Temporarily disable namespace caching
* ac88300 HUE-8527 [editor] Fix concatenation type exception in namespace call
* 9101ad0 HUE-8507 [editor] SQL alchemy result set column headers are missing.
* 7675b0c HUE-8516 [cluster] List more namespaces and filter out invalide ones
* c9bd71c HUE-8514 [core] Log metrics when calling is_alive
* a4f0e76 HUE-8521 [auth] Protect against empty LDAP login username
* b11ae2c HUE-8524 [impala] Provide the root cause of INVALIDATE METADATA failures
* ab702d5 HUE-8519 [jb] Impala API can now directly return json
* 91c3bb0 HUE-8518 [editor] Fix sample Kudu
* 59482ae HUE-7407 [useradmin] Added superuser group priv to useradmin
* 49e6063 Revert "[useradmin] Added superuser group priv to useradmin"
* ed4e609 HUE-8511 [core] Fix unit test
* f60d3f8 HUE-8500 [oozie] Remote cluster action
* 86aec9b HUE-8507 [editor] Fix download sqlalchemy
* dda146b HUE-8499 [useradmin] Fix ensure_home_directory if path contains special character
* a9a5bd4 HUE-8505 [core] Close impala session on logout
* 4cc00a4 [useradmin] Added superuser group priv to useradmin
* e77d34b HUE-8508 [core] Add command to cleanup old data in tables
* 1bea657 HUE-8507 [editor] Fix SQL Alchemy sample & query
* 738255a HUE-8504 [oozie] Add file context popup link to file path properties
* 11c3a31 HUE-8502 [catalog] Table sample via Hive are failing with snippet not configured error
* 42ae4d3 HUE-8503 [dashboard] Query Builder direct dashboard landing
* 0012358 HUE-8500 [jb] Support terminating a remove cluster from the interface
* a11708c HUE-8500 [jb] Create a preconfigured dataeng cluster in one click of a button
* de43f3e HUE-8500 [jb] List proper jobs and cluster depending on the selected cluster
* c69a045 HUE-8500 [spark] Implement support for Spark parameters in the editor
* 21e9b60 HUE-8500 [cluster] Add call to create a remote dataeng cluster
* 8a10ff6 HUE-8500 [oozie] Skeleton of remote cluster action
* ceb2679 HUE-8501 [core] SPNEGO authentication does not create user directory
* fb2396c HUE-8481 [useradmin] Do not error when listing users on admin page and some contains restricted character
* e339894 HUE-8489 [core] USER_LOGIN is not audited for SPNEGO authentication
* 09dc859 HUE-8498 [core] Add whitelist to Spnego middleware
* d907dc5 HUE-8497 [cluster] Properly submit a remote Spark job
* d4dbaaa HUE-8497 [cluster] Improve the debug logging of remote job submissions
* 21b54bf HUE-8496 [cluster] Remove unused dynamicClusters flag in context API
* a81cc59 HUE-8496 [frontend] Switch to using the new multi cluster config flag in the UI
* 088fdd2 HUE-8492 [frontend] Improve and generify the reference documentation extractor
* 50b096d HUE-8495 [editor] Fix report export
* f1b36ce HUE-8493 [search] Add API to add data to collection
* b9246c3 HUE-8420 [core] Fix multi LDAP servers with limiting login to list of ldap groups
* 8dc4503 HUE-8493 [search] Move to managedTemplate import by default
* fa2fbf3 HUE-8494 [importer] Fix failure to navigate on solr collection success
* 5ab5706 HUE-8491 [chart] Cannot change between bar/line chart on Firefox
* b0c1b04 HUE-8408 [report] Fix add message for missing configuration.
* c2ccbbf HUE-8490 [core] Fix Spnego has conflict with timer metrics
* 8756cd0 HUE-8487 [useradmin] Fix Add Sync LDAP user fails when using DN with special character
* 0c6532e HUE-8453 [sentry] Left assist db list does not match sentry db list.
* 07ab852 HUE-8488 [fb] Disable drag&drop when show_upload_button=false
* a6262f2 HUE-8480 [cluster] Provide a flag when we are in multi cluster mode
* e7be4fbc HUE-8473 [cluster] Support submitting Spark jobs to remote cluster
* d10d008 HUE-8486 [assist] Fix broken column samples in the Hive context popover
* b04e5b1 HUE-8485 [search] Simplify complex type display in widget formula editor
* 4276684 HUE-8484 [search] Fix autocomplete in the Impala dashboard
* df26866 HUE-8128 [backend] Force debug logging in server logs does not get all debug
* 961f1af HUE-8478 [autocomplete] Fix issue where references to CTE aliases in the select list are incorrectly marked as tables
* 2de2575 HUE-8477 [frontend] Make sure tooltips are shown in the context popover
* 447c847 HUE-8087 [notebook] User with least privileges can access notebook app via URL
* 2928a2f HUE-8408 [report] Add message for missing configuration.
* 366b4da HUE-8408 [report] Load saved document
* 61ef8f5 HUE-8479 [editor] Only show icons on hover for Query History, Saved Queries, Results
* 9ed06e0 HUE-8408 [report] Load saved document
* 02b3d96 HUE-8464 [core] Fix SAML encryption missing key file passphrase
* 357bdef HUE-8475 [report] Protect against pivot conflicting with nested facets
* 114c9ec HUE-8408 [report] Load saved document
* fde4cde HUE-8473 [cluster] Create cluster API first skeleton
* 6b659be HUE-8476 [frontend] Fix jQuery Hive autocomplete column mapping
* b6cdda3 HUE-8473 [cluster] Rename connector to remote SQL clusters
* 4c0d53d HUE-8408 [report] Dynamic statement retrieval
* 1037395 HUE-REPORT6
* bd564b8 HUE-8474 [docs] Update manual.md for SASL and TLS configurations
* fc7f416 HUE-8467 [jobbrowser] Support impala digest auth for queries
* d963841 HUE-8473 [editor] Limit the width of compute and namespace selection
* f6d1014 HUE-8472 [frontend] Ensure computes in namespaces have id and name
* ac94c20 HUE-8469 [frontend] The sql popover comment should scroll when expanded and overflowing
* 3a72580 HUE-8470 [frontend] Allow < characters on the row details popover
* 6778920 HUE-8471 [frontend] Enable spotlight search on the row details popover
* 6f37cbc HUE-8468 [frontend] Append a style tag to head instead of modifying stylesheets for dynamic styles in embedded mode
* a90a871 HUE-8466 [report] Avoid Gridster JS error on swapping between dashboard modes
* 9f651ae HUE-8463 [frontend] Remove typo on javascript links
* b8d845f HUE-8465 [frontend] Remove margin from 'hi' icons on the main button dropdown
* eee0291 HUE-8451 [notebook] Many "codec can't decode byte" errors on pig execution if browser language=jp
* 9b8a15b HUE-8407 [fb] Overwriting default_hdfs_superuser in configuration does not take effect
* a2fe26d HUE-8461 [report] Execute dom unload code just on report mode
* 665da08 HUE-8441 [report] Fix JS error on document picker statement chooser
* 581ff28 HUE-8454 [report] The field list checkboxes should be clickable through Gridster
* b6172a5 HUE-8460 [editor] Bring back 'export to dashboard'
* d218478 HUE-8461 [report] Reopen the right assist when leaving report mode
* 0e37d6e HUE-8456 [search] Fix web_logs & yelp demo.
* c9e693d HUE-8455 [pig] Oozie editor fails with 'hadoopProperties' for pig script saved in Hue 3
* a05cb14 HUE-8458 [frontend] Fix issue with async loading of js resources in the dashboard
* e2b3ada HUE-8458 [frontend] Evaluate the js resources while others are being fetched
* b16e4f2 HUE-8458 [frontend] Load new scripts using $.get and eval instead of appending <script> tags
* d40c4ff HUE-8450 [editor] Add jasmine test for URL changes in embedded mode
* 1de331c HUE-8441 [report] Improve reliability of selected statement id
* ff9cdf8 HUE-8441 [report] Connect document picker demi modal to new facet
* 837d9f1 HUE-8441 [report] Add a document and statement picker demi modal
* 51546a1 HUE-8459 [report] Hide right assist on report mode
* 067cdd7 HUE-8457 [report] The widget toolbar shouldn't hide the dropdown menu
* 719cc2f HUE-8424 [core] Add options to dump more of rest API response to logs
* 4be9ab5 HUE-8453 [sentry] Left assist db list does not match sentry db list.
* 5dd973e HUE-8408 [report] Added selection for statement_id
* ccf5dbe HUE-8440 [jb] Link for Spark logs in Properties tab of Job Browser is incorrect
* 9028a62 HUE-8443 [report] Improve the affordance of the plus-to-drag icon
* 51666e5 HUE-8452 [report] The app toolbar should use Flexbox instead of docking
* 73507b1 HUE-8450 [frontend] Improve clearable sizing in embedded mode
* 376878e HUE-8449 [report] Enable save a query after clicking on Report on the editor
* 6678c54 HUE-8450 [editor] Various improvements for embedded mode
* 9951fcb HUE-8444 [report] Dragging on an empty dashboard should use the whole available width
* 799b8aa HUE-8448 [report] Show the droppable placeholder before empty widgets too
* d329bf4 HUE-8424 [core] Fix wrong manage_entry file
* 6f228ee HUE-8447 [editor] Fix DB selection for snippets in notebook mode
* e34c301 HUE-8446 [editor] Fix worker js exception when switching apps
* e2a5015 HUE-8445 [assist] Fix scroll in the document context popover
* 35fcd83 HUE-8437 [assist] Use vertical tabs for the right assist
* c9c7898 HUE-8435 [editor] Prevent js error when a compute is selected with no corresponding namespace
* 9640260 HUE-8408 [report] Fetch column metadata on new facet.
* 8d2f9dc HUE-8408 [report] Support basic filter.
* d119ce4 HUE-8425 [core] Fix hue cli to handle cm Oracle and Java
* 6cac4c3 HUE-8438 [frontend] Reduce close icon size on the nav property popover
* 46374ff HUE-8432 [editor] Fullscreen result does not hide assist anymore and conflict with presentation
* 697de9c HUE-8431 [index] Avoid TypeError: 'NoneType' object is not iterable when list aliases is null
* 5354d52 HUE-8436 [metastore] The sample of a table with a lot of columns should scroll horizontally
* 19a2748 HUE-8433 [report] The side panels expand arrows shouldn't be covered by the dashboard dockable
* ac1eb7b HUE-8434 [importer] Clicking on field name bulk editor shouldn't reset the importer
* 8b8c6bd HUE-8393 [report] Enable query chooser for the document widget
* 552864a HUE-8426 [backend] fix hue CLI commands don't work after Django upgrade
* d477adb HUE-6869 [assist] Improve white space formatting in Impala language reference
* 0c107da HUE-8428 [assist] Fix broken S3 file preview
* 69f4981 HUE-6869 [assist] Fix JS error when closing an open topic
* 36a2973 HUE-8321 [oidc] Fix if request doesn't have 'fs' attribute
* 6fbce13 HUE-8414 [spark] Change session id from -1 to 999999999
* 20291b1 Revert "HUE-8414 [spark] Sample Notebook has broken session IDs (#720)"
* 93bd199 HUE-6869 [assist] Remove the language reference config flag
* c67eed3 HUE-6869 [assist] Split the Impala language reference over multiple files and fetch async
* c31df46 HUE-6869 [assist] Fix layout issue in the functions assist panel
* 9be5d29 HUE-8414 [spark] Sample Notebook has broken session IDs (#720)
* 995741d HUE-8410 [backend] Cant disable certificate verification for Thrift over HTTP (#717)
* 00d849d HUE-8426 [backend] fix hue CLI commands don't work after Django upgrade
* def5234 HUE-8408 [report] Added minimal support for charts in report
* 67658dc HUE-8420 [core] Add option to limit login to list of ldap groups
* 789db5a HUE-8321 [oidc] Remove filter query from filter_users_by_claims (#721)
* dc8573a HUE-8422 [frontend] Improve app switcher layout in multi cluster mode
* d18b65a HUE-6869 [assist] Scroll to the active language reference topic when opened through link
* 0374af7 HUE-8421 [frontend] Prevent caching of empty namespaces in the context catalog
* a2d1239 HUE-6869 [editor] Enable show in assist from popover language ref
* e0033d8 HUE-6869 [editor] Show language reference when right clicking statement starting keywords in the editor
* 392b46f HUE-8416 [assist] Fix the indexes left assist panel
* 479299c HUE-8417 [core] Return the default namespaces for all services
* 0fa80e5 HUE-6869 [editor] Add a config flag to enable the language reference
* 5ca9305 HUE-6869 [editor] Enable internal links in the language reference details
* 6e4ae82 HUE-6869 [editor] Add Impala language reference to the right assist
* 922bcd1 HUE-8205 [docs] Refresh the SDK documentation to reflect Hue 4 apps for the client side
* 6993508 HUE-8408 [report] Minimal capability for report query
* 05af489 HUE-8330 [dashboard] Minimal support for cluster in dashboard.
* de2aa4a HUE-8415 [core] Hive chooser should always be called with a user and an engine type
* 6688b8f HUE-8388 [oozie] Hue create a new workspace when importing an Oozie workflow instead of using "deployment_dir" field
* fa2f532 HUE-8409 [core] When idle session timeout is enabled it causes issues with Spnego
* b7102cd HUE-8359 [docs] Add the new non-embedded DB requirement for developing Hue
* 3436dab HUE-8413 [frontend] Remove yellow hue from the autofill inputs
* 5c9f9f2 HUE-8411 [metastore] Put the privileges section to read-only for now
* 507b38a HUE-8406 [report] Show HTML edit mode just when editing and hovering the whole widget
* f891802 HUE-8399 [editor] Limit functions assist to Impala in embedded mode
* 19dd0c4 HUE-8399 [editor] Hide the right assistant in embedded mode
* 558088a HUE-8330 [assist] Fix broken namespace refresh
* 1b1d847 HUE-8384 [search] Improve importer format guessing performance
* 126ce01 HUE-8397 [importer] Fix failure to import parquet table.
* 334b215 HUE-8405 [core] remove tests from chardet 3.0.4
* 408ea6e HUE-8321 [oidc] Add implementation for multi-backend auth with AllowFirstUserDjangoBackend
* d29b63b HUE-8305 [useradmin] Optimize performance on checking Hue permissions if user is in many groups
* 2c0b65d HUE-8330 [frontend] Don't show namespaces when there's just one and multi cluster isn't configured
* e21e506 HUE-8330 [assist] Add polling and cancelling to execution analysis
* 950a22b HUE-8330 [assist] Use workload analytics config flag in the UI
* 7122c42 HUE-8404 [useradmin] Fix multibackend invalid password removes drop down to select Local
* 2c115ea HUE-8402 [dashboard] Timeline: Fix numbers and filtered legend items
* 7458341 HUE-8341 [assist] Create a new document from the doc assist
* 7d0fe6c HUE-8330 [assist] Filter out cluster not in CREATED status
* bf48a6f HUE-8330 [core] Fixing import name lost during a rebase
* 222e683 HUE-8330 [metadata] Add API to list uploads
* c33c5ce HUE-8330 [editor] Adding config flags for workload analysis
* 5a54f92 HUE-8330 [editor] Add query execution analysis to the right assist
* 302f54d HUE-8330 [frontend] Don't show namespaces without a name
* 6f176f3 HUE-8330 [core] Update generated CSS files
* 4760f7b HUE-8330 [importer] Do no error on single cluster submission
* b27a333 HUE-8330 [metadata] Get cluster id API from environment id
* 03af8a8 HUE-8330 [assist] Include namespace for show in assist
* 1961887 HUE-8330 [metastore] Fix issue where the table browser won't open a table from the URL if it's for the first namespace
* f52e1ed HUE-8394 [frontend] Add a debug function to clear the cached data catalog entries
* 199965e HUE-8330 [impala] Skeleton to get prettier query profile
* 6d30901 HUE-8330 [core] For multi cluster demo
* 459ff16 HUE-8330 [importer] Use the compute and namespace for the importer autocomplete
* eeb483b HUE-8330 [core] Switch to use crn and not cluster name for fake namespaces in compute clusters API
* 675807e HUE-8330 [core] Move app switcher to the right
* e3c8ac6 HUE-8330 [importer] Pass namespace and compute details to the importer
* 14591f7 HUE-8330 [cluster] Do no error out when queries have new lines
* 7df1e0c HUE-8378 [metastore] Add a privileges section to the table browser
* 4eb8c72 HUE-8330 [editor] Fix namespace and compute selection and update the assist when changed in the editor
* f21660f HUE-8330 [frontend] Don't use compute id for cached identifiers in the data catalog
* 56abb06 HUE-8330 [frontend] Add app switcher for multi cluster mode
* 21a5747 HUE-8365 [security] Move the table privilege browser and editor to a separate component
* fb6f219 HUE-8330 [cluster] Fix typo when in pure multi cluster mode
* c3f92d2 HUE-8330 [cluster] Fix autocomplete of columns on a remote cluster
* d2ffba7 HUE-8330 [cluster] Adding new logo when in cluster only mode
* a3c9ae6 HUE-8330 [cluster] Add fake namespace to compute without a namespace
* 1519a24 HUE-8330 [editor] Move namespace on the left of databases
* 4280767 HUE-8330 [cluster] Hack to load editor and to list computes in editor
* fc9f893 HUE-8330 [metadata] Include compute when accessing the data catalog throughout
* 95ed605 HUE-7621 [editor] Initial commit for SQL alchemy query backend
* e7b7aec HUE-8330 [cluster] Do not error when browsing table data
* 1b78aca HUE-8330 [cluster] Support sending a remote fetch results call
* 35dbe80 HUE-8330 [cluster] Support sending a remote check status call
* 9b4ddd7 HUE-8330 [impala] Use main ini properly when core cluster is selected
* 60bea21 HUE-8330 [cluster] Add a list of computes to each namespace in the namespace API
* 42ff5f9 HUE-8330 [cluster] Add namespace name to compute if it has one
* ba6651d HUE-8366 [importer] Clean-up import of tables to altus
* 03aaa5e HUE-8366 [importer] Connect and improve table chooser to the table import field
* 2504a16 HUE-8330 [cluster] Support sending a remote query call
* a9c5abe HUE-8330 [cluster] Support sending a remot autocomplete call
* 5e08fed HUE-8330 [cluster] Convert lib to use the navopt lib instead of cli
* 2162882 HUE-8330 [navopt] Patch lib to not always require parameters
* 3b06fa3 HUE-8330 [cluster] Convert to using the proxy command and not CLI
* e733351 HUE-8330 [cluster] Execute ADB query
* c407072 HUE-8330 [assist] Make sure namespaces are refreshed throughout on assist refresh
* 65fce15 HUE-8330 [assist] Only enable namespace refresh when there are multiple clusters configured
* ffae85c HUE-8330 [cluster] Add a flag in namespace API when there are [[clusters]]
* 3a29a50 HUE-8330 [jb] Listing various clusters and configurations
* 166e472 HUE-8330 [oozie] Submit a mocked scheduled job to de-cluster
* 72220ac HUE-8330 [oozie] Add multi cluster context to the scheduler
* f8ad57b HUE-8330 [notebook] Refactor Dataeng API
* 036befb HUE-8330 [metastore] Add source type and namespace to the Table Browser URL
* 4b7a2e2 HUE-8330 [metastore] Introduce MetastoreSource in the table browser
* 8836c1b HUE-8330 [metastore] Introduce a namespace level in the Table Browser
* 29bce08 HUE-8330 [assist] Only show namespace selection when there are more than one available
* 9e178b2 HUE-8330 [frontend] Add caching of namespaces
* 4da76df HUE-8330 [editor] Add namespace and compute selection to snippet header with temporary plain language titles
* 71e23e7 HUE-8330 [editor] Fix initial database selection in the editor
* 7ba7a39 HUE-8330 [assist] Add namespace panel for Solr
* cb2cbbc HUE-8330 [assist] Add a refresh action to namespace assist listing
* ea67d37 HUE-8330 [assist] Add filter and spinner to namespace selection
* a9ff482 HUE-8330 [importer] Prototype of tale import to altus
* 6697684 HUE-8330 [assist] Add a namespace level in the assist panel
* e56d727 HUE-8330 [core] Get namespace and compute from altus
* bc03c9a HUE-8330 [core] Adding namespace to compute cluster
* beac9d5 HUE-8330 [editor] Add compute cluster dropdown
* 9ff85a7 HUE-8330 [desktop] Split the context API into namespaces and compute
* 0473951 HUE-8330 [metastore] Enable context switching in the Table Browser
* ccc6562 HUE-8330 [metastore] Reload databases on context switch
* 2d12134 HUE-8330 [frontend] Add a ContextCatalog and fetch contexts
* 069285b HUE-8330 [frontend] Introduce contexts for SQL and Solr
* 4f76be7 HUE-8330 [core] Support a pure multi cluster setup without any app configuration
* 237ba8e HUE-8330 [core] Skeleton of API to provide context of namespaces/compute for Hive
* 6dcb47c HUE-8401 [editor] Remove escape character from variables.
* c1defcd HUE-8400 [importer] Remove header from manual tables.
* b2e5257 HUE-6697 [jb] Prevent reset of job page tabs when job is running
* 3f4f308 HUE-8393 [report] Initial wiring for the document widget charting
* faebb36 HUE-8393 [dashboard] Remove toolbar in report mode and enable dragging the plus icon
* 1f06712 HUE-8338 [core] Update failing tests about the Hue version
* db9c486 HUE-8313 [core] Remove Welcome tour when using embedded mode
* 3b3d422 HUE-8393 [dashboard] Only show a drag document action when in report
* 3621362 HUE-8393 [dashboard] Avoid sending the main query when using a report
* 2a71c93 HUE-8399 [editor] Various improvements for embedded mode
* f10ce5e HUE-8398 [editor] Fix broken result table after multiple queries in embedded mode
* c57c332 HUE-8396 [assist] Unify the assist header font sizes
* aec4392 PR715 [useradmin] Fix last activity update for jobbrowser/api/jobs requests (#715)
* b887248 HUE-8392 [oozie] Cannot add more actions using drag & drop from actions bar in the Oozie editor after adding around 3 actions
* 84475b6 HUE-8321 [oidc] Add implementation for creating a new user if not exist during login  * override user lookup by username instead of email  * allow to create as a superuser if it belongs to a superuser group       1. add the name of Hue superuser group to superuser_group in hue.ini       2. in Keycloak, go to your_realm --> your_clients --> Mappers, add a mapper            Mapper Type: Group Membership (this is predefined mapper type)            Token Claim Name: group_membership (required exact string)  * allow not to create new user, and redirect to oidc failed page
* ceb80d9 [dashboard] Remove search bar from report mode
* c80f1bf [dashboard] Prepare skeleton for adding a saved query
* 0f9738a HUE-8395 [dashboard] Remove left column from the initial search layout
* 4e89bca HUE-8386 [dashboard] The dropdown menu is hidden behind the widget list
* 614ac45 HUE-8369 [core] Add tests for mysql db migrations.
* 363bf3d HUE-8367 [autocomplete] Last set of Impala autocomplete updates
* f3d6ada HUE-8375 [core] Fix migrations for mysql
* e2b81a2 HUE-8389 [frontend] fix last_modified timestamp in desktop/models
* 2741fa5 HUE-8387 [core] remove dependency of accessing pyopenssl through requests.packages code
* f85df06 HUE-8371 [core] Shrink char field max length for Oracle DB support
* 477930f HUE-8369 [core] Add test for db migration
* 1ce32b9 HUE-8380 [core] Add more to the black list of config check errors
* 08dd420 HUE-8379 [oozie] Reverse start and end workflow icons
* fe5303c HUE-8381 [metadata] Avoid 'NoneType' object has no attribute 'strip' on list_tags
* 3a53664 HUE-8382 [core] fix django-axes 2.2.0 breaks with error field attempt_time can not be null
* a68f004 HUE-8321 [oidc] Add implementation for logout from Keycloak
* 274fc64 HUE-8377 [security] Correctly apply the new permissions to the database scope
* 7c71df6 HUE-8377 [security] Support new Sentry finer grain privileges
* c814da8 HUE-8375 [core] Update Hue check config for migrations
* b8a5d71 HUE-8374 [core] Hue database schema migration
* 134febc HUE-8370 [pig] Imported old version Pig script missing properties fields
* c793cd8 HUE-8367 [autocomplete] Various Impala autocomplete updates
* a9a1367 HUE-8372 [assist] Silence errors from the topJoins calls
* 77f6cf7 HUE-8371 [core] Shrink char field max length for Oracle DB support
* d1801c9 HUE-8321 [useradmin] Integrate with Single Sign On using Keycloak  * adding mozilla-django-oidc-1.0.0 and josepy-1.1.0  * modified desktop/core/src/desktop/middleware.py to avoid redirect looping  * create OIDCBackend to extend OIDCAuthencationBackend, and it rewrites user with has_hue_permission  * adding entry for OIDC to Hue configure files and retrieve OIDC config value in desktop/settings.py
* 74e7d62 HUE-8373 [indexer] Opening a single index error with 404
* c8fa43b HUE-8369 [core] Adding missing initial migrations in new format
* 7dbc5e4 HUE-8368 [autocomplete] Update Impala ALTER and CREATE statements to the latest syntax
* 4a26235 HUE-8367 [autocomplete] Add support for Hive ALTER TABLE SET OWNER
* 4531955 HUE-8364 [s3] Fix s3 not getting initialized in certain scenarios
* 7792c4c HUE-7607 [fb] Right click on . folder of a directory does not show the popup
* 334c0bd HUE-7977 [frontend] Use delayedOverflow on the top search result list, chart Y axis on editor, file chooser and dashboard widgets
* 8d574c5 HUE-8178 [charts] Move the value back to popup on mouseover
* bfe8cd2 HUE-8357 [oozie] Properly display error message when coordinator with wrong date is submitted
* d0cd7f9 HUE-8362 [rdbms] Explain button is not working (#712)
* 9d0ef5d HUE-8360 [editor] The row detail modal shouldn't be triggered by a double click on the cells
* 0e113b6 HUE-8355 [dashboard] Counter widgets should be smaller than the other widgets
* 63b5726 HUE-8350 [solr] indexer app permission is not being acknowledged in HUE(Hue4)
* 7e5e9ec HUE-8178 [charts] Improve timeline intervals for weeks & months
* 6c9b20a HUE-8178 [charts] Fix time intervals that have non standard durations
* b661456 HUE-8339 [impala] Adding a config flag to enable the smart Thrift pool
* bd05df6 HUE-8339 [impala] Smart thrift connection pool for Impala
* 34dbf97 HUE-8353 [useradmin] Give a compatible name to sync_ldap_users_groups URL view
* a0e9290 HUE-8354 [dashboard] Fix 'Search as I move the map' functionality on the Leaflet widget
* 60d3dbb HUE-8350 [solr] indexer app permission is not being acknowledged in HUE(Hue3)
* bf2556e HUE-8317 [core] App SDK should generate views in the proper format
* bf3cf1c HUE-8349 [oozie] Cant save bundle that using coordinator from examples (#710)
* d4c6b84 HUE-8351 [editor] Execution time is no available for sync sources (#711)
* 6edba44 HUE-8348 [core] Make Debug mode option more explicit
* 47b0a8c HUE-8348 [sqoop] Disable Sqoop v2 by default
* d703282 HUE-8346 [s3] Fix file upload.
* 712a5c8 HUE-8347 [dashboard] The non-Gridster dashboards shouldn't throw a JS error on page resize
* 2b46446 PR709 [doc] User guide fixes (#709)
* db01ec3 HUE-8346 [s3] Fix creation & deletion of bucket
* 55ab57a HUE-8344 [hbase] Hbase old version of data can not display in Hue
* c374b6e HUE-8345 [s3] Remove log error message when S3 / ADLS not configured
* 5dc5091 HUE-8343 [editor] Fix boolean variables
* 7ee75e2 HUE-8178 [charts] Fixed chart legend missing x axis name
* 40a97f3 HUE-8178 [dashboard] Fix time stays static.
* 1ecc5b6 HUE-8178 [charts] Fix zoom with 2+ facets
* 173e13d HUE-8139 [core] Fix django-debug-toolbar 1.9.1 in Django 1.11  * add template engine django in desktop/settings.py for django-debug-toolbar  * use desktop/ext/js/jquery/jquery-2.2.4.min.js in desktop/templates/debug_toolbar/base.html
* f09edf3 HUE-8331 [metadata] Document how to update table or column properties
* 910800a HUE-8331 [metadata] Adding/updating a comment with the dummy backend
* 531190e HUE-8331 [metadata] Refactor lib to allow additional pluggable backends
* ae93104 HUE-8342 [jobbrowser] Failed to get workflow info when Oozie launched by non default user (#708)
* 046c548 HUE-8338 [core] Update to use optionally the build version as the overall version number
* cf0914e HUE-8337 [impala] Lower some more the idle query/session timeouts
* 3731a60 HUE-8335 [doc] Update install document for installing Python 2.6 on OS 6.x series
* 79ee4e1 HUE-8340 [search] Turn on analytic dimensions by default
* aedb403 HUE-8330 [jb] Prevent an DATARNG error when opening the browser
* d52a565 HUE-8336 [spark] Can't disable certificate verification
* 166c53d HUE-8336 [sqoop] Can't disable certificate verification
* b43d23a HUE-8336 [hbase] Can't disable certificate verification
* a0abb90 HUE-8332 [indexer] Remove unused import Search that might fail if Solr is disabled
* e9d50e2 HUE-8178 [charts] Fix timeline in table.
* 409059e HUE-8178 [charts] Highlight bars selected using single select.
* 48f09d6 HUE-8178 [charts] Make aggregate select box smaller.
* ef1e05f HUE-8333 [core] Disable pylint installation
* 763081f HUE-8310 Broken template for multiple custom apps (#700)
* 3f2dea1 HUE-8330 [core] Typo in main Hue template
* 1519337 HUE-8328 [assist] Make it possible to edit tags in the SQL context popover
* 06aae1b HUE-8329 [frontend] Remove empty facet values from the inline autocomplete
* d1b6901 HUE-8326 [assist] Prevent the file upload dialog from showing twice after clicking '+'
* bfe90d0 HUE-8327 [metadata] Enable searching on custom key-value pairs through the global search
* 29b811d HUE-8325 [editor] Add the correct protocol type for the file context popover replace in editor action
* c89a7e3 HUE-8324 [editor] Fix for ADLS and S3 paths in editor context popover
* 315c211 HUE-8323 [frontend] Make the DataCatalog cluster aware
* 6ea3df3 HUE-8330 [core] Remove old main dropdown multi cluster configuration
* 2592be1 HUE-8320 [core] After copying a workflow using Hue 4 button, saving the copied workflow fails
* 158136f HUE-8178 [charts] Remove gray section when zooming.
* 51eaac7 HUE-8178 [charts] Move mouseover y values to legend.
* 99f5a6b HUE-8178 [charts] Move mouseover detail to right side.
* ae8a410 HUE-8322 [assist] Improve assist header action visibility
* 931c867 HUE-8319 [editor] Silence background SQL refresh errors
* 1b32589 HUE-8318 [frontend] Remove misaligned red glow from login input on focus
* 6bb7787 HUE-8307 [pig] Unable to use piggybank installed with Pig examples (#691)
* 9c96386 HUE-8298 [kafka] Import kafka lib module is incorrect
* 6857e76 HUE-8139 [doc] Update documentation to explicitly require Python 2.7
* 1dfc3e5 HUE-8178 [charts] Reintroduce zoom
* 0a5a705 HUE-8178 [charts] Bugfixes for timeline selection & refine intervals
* 2b45a50 HUE-8178 [charts] Bugfixes for timeline selection & refine intervals
* dfe20d5 HUE-3287 [core] Django 1.11 upgrade  - fix Python2.7 enabling script
* 43f778d HUE-8139 [core] Disable toolbar until ported to Django 1.11
* 5fd6d56 HUE-8316 [importer] Base for SQL editor option to fields in the importer
* 749343e HUE-8315 [assist] Fix JS exception when the root folder is shown in the file context popover
* 0567ba0 HUE-8283 [oozie] Show image from Oozie instead of not displaying Graph for big workflows
* 52334c9 HUE-8314 [core] Fix SAML encryption missing config
* 8387d83 HUE-3287 [core] Django 1.11 upgrade - Upgrading django-debug-toolbar from 1.3.2 to 1.9.1
* 873c191 HUE-3287 [core] Django 1.11 upgrade - Fixing desktop/core/src/desktop/urls.py after master rebase
* 30420b2 HUE-8313 [core] Remove hardcoding to ImpersonationBackend when using embedded mode
* 4d76454 HUE-8312 [editor] Promote more the comment/uncomment shortcut in the help
* 3a33f88 HUE-3287 [core] Django 1.11 upgrade  - HUE-8261 [core] Fix the pypi URL when building
* 31b63ac HUE-3287 [core] Django 1.11 upgrade  - Adding code review suggestion changes from Romain and Johan
* 4e31ff5 HUE-3287 [core] Django 1.11 upgrade  - Adding et_xmlfile module
* e31f01d HUE-3287 [core] Django 1.11 upgrade  - changing to text as in the initial phase Location is not resolvable
* 07795cc HUE-3287 [core] Django 1.11 upgrade  - fixing claimed_id issue in migrations
* 690e1e0 HUE-3287 [core] Django 1.11 upgrade  - Fixing test desktop.management.commands.test.setup_test_environment
* 1a64e6a HUE-3287 [core] Django 1.11 upgrade  - Fixing Beeswax test
* 53129c9 HUE-3287 [core] Django 1.11 upgrade  - adding Enum related fixes fixing test
* 0b71bbe HUE-3287 [core] Django 1.11 upgrade  - Upgrading Enum34 module
* 7ec160c HUE-3287 [core] Django 1.11 upgrade  - Fixing useradmin.tests
* 9272fde HUE-3287 [core] Django 1.11 upgrade  - Fixing metrics chicken-egg issue for the migration
* 9ea1b83 HUE-3287 [core] Django 1.11 upgrade  - [core] Move util location_to_url to desktop lib utils
* b8d5a29 HUE-3287 [core] Django 1.11 upgrade  - Fixing metrics initial run
* 5f9801f HUE-3287 [core] Django 1.11 upgrade  - Removing monkey patching for User Adding handle_noargs changes
* c719709 HUE-3287 [core] Django 1.11 upgrade  - Adding change
* e1eaeda HUE-3287 [core] Django 1.11 upgrade  - adding change
* 2411695 HUE-3287 [core] Django 1.11 upgrade  - Fixing make install
* 138572b HUE-3287 [core] Django 1.11 upgrade  - Adding /opt/cloudera/python/ for RedHat 6 environment
* dc2febd HUE-3287 [core] Django 1.11 upgrade  - To upgrade Django 1.11, following changes are needed:
* 7e419c2 HUE-3287 [core] Django 1.11 upgrade  - Adding PyYAML-3.12 colorama-0.3.2 docutils-0.14 nose-1.3.7 openpyxl-2.5.3 repoze.who-2.3 wheel-0.31.0 zope.interface-4.5.0 python modules
* 386b2b7 HUE-3287 [core] Django 1.11 upgrade  - Fixing navigator error
* a96e334 HUE-3287 [core] Django 1.11 upgrade  - fixing django-openid-auth-0.14/django_openid_auth/models.py from registering BLOB (Large object) with 2048 char length see https://stackoverflow.com/questions/44358506/sql-error-1170
* 64ff0d2 HUE-3287 [core] Django 1.11 upgrade  - Reverting to requests-kerberos-0.6.1
* 5ad587f HUE-3287 [core] Django 1.11 upgrade  - Upgrading following modules: - avro-1.8.2 - backports.csv-1.0.5 - configobj-5.0.6 - cryptography-2.1.4 - defusedxml-0.5.0 - django-openid-auth-0.14 - djangosaml2-0.16.11 - elementtree-1.2.6-20050316 - enum34-1.1.6
* 3186126 HUE-3287 [core] Django 1.11 upgrade  - Fixing Hue Port :8888 and :8889 access issue
* 7ceacae HUE-3287 [core] Django 1.11 upgrade  - Updating cryptography-2.0 to cryptography-2.0.3, in secure cluster setup cryptography-2.0 fails with From cffi callback <function _verify_callback at 0x7fd734312488>: Traceback (most recent call last):   File /opt/cloudera/parcels/CDH-6.x-1.cdh6.x.p0.282544/lib/hue/build/env/lib/python2.7/site-packages/pyOpenSSL-17.5.0-py2.7.egg/OpenSSL/SSL.py, line 313, in wrapper     _lib.X509_up_ref(x509) AttributeError: 'module' object has no attribute 'X509_up_ref'
* 6bdc53b HUE-3287 [core] Django 1.11 upgrade  - upgrading pytidylib-0.3.2 library
* b2ae98d HUE-3287 [core] Django 1.11 upgrade  - Adding chardet-3.0.4 module a dependancy for latest requests module
* 869d309 HUE-3287 [core] Django 1.11 upgrade  - Upgrading to latest pyOpenSSL-17.5.0
* d51d6fb HUE-3287 [core] Django 1.11 upgrade  - Adding following modules asn1crypto-0.24.0 certifi-2018.1.18 cffi-1.11.5 cryptography-2.0 idna-2.6 ipaddress-1.0.19 pycparser-2.18 requests-2.18.4 requests-kerberos-0.12.0 six-1.11.0 urllib3-1.22
* 1df7e6e HUE-3287 [core] Django 1.11 upgrade  - fixing authenticate issue
* b4754ee HUE-3287 [core] Django 1.11 upgrade  - upgrading to django-auth-ldap-1.3.0
* 932c8be HUE-3287 [core] Django 1.11 upgrade  - Upgrading Django-1.11
* a7122cb HUE-3287 [core] Django 1.11 upgrade  - To upgrade Django 1.10, following changes are needed:
* 9d1ac7e HUE-3287 [core] Django 1.11 upgrade  - Upgrading Babel-2.5.1 from Babel-0.9.6
* 0cc71fb HUE-3287 [core] Django 1.11 upgrade  - Upgrading to Django 1.10 version
* c4f3ea7 HUE-3287 [core] Django 1.11 upgrade  - This change actually fixes Django migrations. In the Makefile, at this place Hue's APPS are not available, commenting out django makemigrations command
* 8470f21 HUE-3287 [core] Django 1.11 upgrade  - Adding initial Django migrations directory
* 1a1a897 HUE-3287 [core] Django 1.11 upgrade  - Moving migrations to old_migrations
* 87210cc HUE-3287 [core] Django 1.11 upgrade  - To upgrade Django 1.9, following changes are needed: - rename request.REQUEST.get to request.GET.get - adding django context processor - adding urls.py for hue/accounts/login?next=/ - no TEMPLATE_ variable in "settings.py" - fixing "request" dict population - fixing login url rule in desktop/core/src/desktop/urls.py
* 9fd49bd HUE-3287 [core] Django 1.11 upgrade  - Upgrading django-axes-1.5.0 => django-axes-2.2.0 module
* 8229695 HUE-3287 [core] Django 1.11 upgrade  - Upgrading to Django 1.9
* 0c58e57 HUE-3287 [core] Django 1.11 upgrade  - To upgrade Django 1.8, following changes are needed:
* 86e2501 HUE-3287 [core] Django 1.11 upgrade  - Upgrading django-nose-1.3 => django-nose-1.4.5 module
* a67e60f HUE-3287 [core] Django 1.11 upgrade  - Upgrading Mako-0.8.1 => Mako-1.0.7 module Adding djangomako 1.0.1 library
* 6dd3303 HUE-3287 [core] Django 1.11 upgrade  - Upgrading django extensions 1.8.0 module from 1.5.0
* bd75932 HUE-3287 [core] Django 1.11 upgrade  - Upgrading to Django 1.8
* 88a7c05 HUE-3287 [core] Django 1.11 upgrade  - To upgrade Django 1.7, following changes are needed:
* 9abf255 HUE-3287 [core] Django 1.11 upgrade  - Removing South-1.0.2 module from desktop/core/ext-py
* 86742eb HUE-3287 [core] Django 1.11 upgrade  - Upgrading to Django 1.7
* 1131337 HUE-8139 [desktop] Get a mode to allow easy profiling of requests  * add django-debug-toolbar-1.3.2 and django-debug-panel-0.8.3 (AJAX debug)  * to use debug panel, user need to install https://chrome.google.com/webstore/detail/django-debug-panel/nbiajhhibgfgkjegbnflpdccejocmbbn  * copy static files to desktop/core/src/desktop/static/debug_toolbar/ and desktop/core/src/desktop/templates/debug_toolbar/  * fix django-debug-toolbar v1.3 conflict with sqlparse-0.2.0 https://github.com/jazzband/django-debug-toolbar/issues/856  * add configurations to desktop/core/src/desktop/settings.py and desktop/core/src/desktop/urls.py  * fix 401 for non-superuser at desktop/core/src/desktop/middleware.py  * add enable_django_debug_tool and django_debug_tool_users to hue.ini for configuration control
* c219e31 HUE-8306 [editor] Add a refresh action for missing entries in the right assist
* 4a286bf HUE-8301 [editor] Identify column types for variables when a column alias is used
* 1c75ae4 HUE-8300 [editor] Silence all AuthorizationExceptions in the editor
* d0ede05 HUE-8299 [assist] Add additional details to the file context popover
* 0370871 HUE-8311 [assist] Sample data is missing for rdbms databases (#697)
* 57fe808 HUE-8291 [oozie] Prevent test failure when deleting HDFS path prefix
* 53fc922 HUE-8309 [editor] Exceptions while typing path to file in Hive editor manually (#695)
* 4eceaad HUE-8150 [catalog] Skeleton display of the metadata search
* 0d30037 HUE-8298 [kafka] Move to an official lib
* 9d3e519 HUE-8298 [core] Upgrade to simplejson 3.15.0
* 18ee1ce HUE-8298 [core] Remove old simplejson lib
* 4b7b8c9 HUE-8208 [importer] Alternatively submit envelop jobs with a Oozie shell action
* 8ec7784 HUE-8208 [core] Add Salesforce Python library
* 4549eeb HUE-8208 [importer] Support SFDC live preview of objects and data
* 8468783 HUE-8298 [kafka] Add UI prototype to configure Flume channel with source and sink
* f57f1ab HUE-8208 [importer] Add title to step 1 when importing from a stream
* 3fd9920 HUE-8298 [editor] Basic Kafka SQL connector via Spark Streaming
* f354169 HUE-8208 [importer] Support manual creating of an index
* 9542593 HUE-8298 [kafka] Add a proper is_enabled config flag
* b5f2cde HUE-8208 [importer] Offer consuming a Kafka stream directly into a Solr collection
* b4e3644 HUE-8208 [importer] Generate Envelope Solr output
* 5609584 HUE-8208 [importer] Generate proper import of SFDC to a Table
* 7bb4d7c HUE-8208 [importer] Correctly DB prefix table desination of stream import
* 64befcc HUE-8208 [importer] Split warning in two warning about invalid table name
* 3742578 HUE-8208 [importer] Prepare creating the table for the Kafka stream when it does not exist yet
* 158207b HUE-8208 [importer] Add test to create a Kudu table manually
* 7a34ed6 HUE-8208 [importer] Allow to skip columns when creating a Kudu table
* e7512c1 HUE-8208 [importer] Default table destination name to topic name by default
* c584567 HUE-8208 [importer] Get the Kafka topic schema from the interface
* 93e4e95 HUE-8298 [kafka] TotalStorage the current topic schema
* cd4a859 HUE-8298 [kafka] Mocking of Sentry privilege on topic page
* 84b3033 HUE-8208 [importer] Polish the selection of an input stream
* 5d138a2 HUE-8208 [importer] Skeleton to generate a preview of data from Kafka
* 8f2ae75 HUE-8208 [importer] Combine the stream inputs into one
* 7526315 HUE-8208 [importer] Kudu tables do not always require a partition
* c48fc83 HUE-8208 [importer] Parameterize SFDC envelope template
* 87f536b HUE-8298 [kafka] Modularize the envelope code generation
* 0760d70 HUE-8298 [kafka] Add a basic Topic page
* bebea80 HUE-8298 [kafka] Get topic list directly via a broker
* a61d1bc HUE-8208 [importer] Add a list of stream in the input list
* 79ae5e0 HUE-8208 [kafka] Skeleton of browser and assist
* 6fe56e9 HUE-8208 [importer] SFDC connector skeleton
* fa34e9b HUE-8208 [importer] Automatically select Kudu as output table format when Kafka input
* b6ee2ff HUE-8208 [importer] Kafka topic listing
* 94d4436 HUE-8298 [kafka] Kafka client API
* 5baa57b HUE-8298 [metadata] Get Kudu master host via Manager API
* 32fd0f3 HUE-8298 [metadata] Get Kafka brokers hosts via Manager API
* 30057f7 HUE-8298 [metadata] Skeleton of manager API
* 5f4267d HUE-8208 [importer] Move default location checkbox to extra section
* 74a29db HUE-8208 [importer] Integrate Kafka input with Envelope Spark lib
* 429799a HUE-8302 [jobbrowser] Failed to fetch logs for Spark jobs (#690)
* 47b1644 HUE-8297 [frontend] Remove gray background on hover in the nav bars
* dac7f7f HUE-8296 [autocomplete] Fix autocomplete exception for file paths
* 07640fc HUE-8295 [editor] Allow changing a path in the editor from the file context popover
* 2c4d3b8 HUE-8292 [metastore] Improve the relationships presentation in the table browser
* 210d4c6 HUE-8273 [filebrowser] Don't display encoded paths
* da161e6 HUE-8178 [charts] Fix NaN for string x axis & missing legend
* 17c3231 HUE-8294 [jb] Add document popup to oozie job browser
* d5586a3 HUE-8293 [metastore] Limit column popularity to be at least 5%
* e42c11d HUE-2647 [solr] Utilize client timezone for date expressions
* 7f93bff HUE-8289 [assist] Limit facets to existing column types and show counts in the filter autocomplete
* da1cb14 HUE-8288 [assist] Prevent cursor movement on up and down keypress when the filter autocomplete is open
* b928492 HUE-8290 [assist] Prevent JS exception when pressing up on the first entry in the inline autocomplete filter
* f02226d HUE-8291 [liboozie] Ensure the test user has hist home directory created
* 0b8d0ff HUE-8273 [filebrowser] Don't quote valid url characters.
* 507e66f HUE-8287 [assist] Quote names of drag & dropped tables
* 719ea4f HUE-8286 [dashboard] Consolidate auto refresh into the dashboard settings
* 5010c7a HUE-8273 [solr] FIX white space in file names
* 9bed083 HUE-8282 [fb] Check if EC2 instance before check IAM metadata
* ead321a HUE-8284 [charts] Cleaner axis for Timeline
* 9e8502f HUE-8285 [oozie] coordinator is not able to strip spaces for input-path or output-path. (#689)
* 73fdc9d HUE-8280 [fb] Move action button does not prevent move to itself
* d5a8ff3 HUE-8177 [oozie] Add a config check for /user/hue/oozie/workspaces
* 85b8501 HUE-8178 [charts] Modified selection & filtering timeline behavior
* 9d03112 HUE-8279 [useradmin] Disable the "Sync" button from "Sync LDAP users/groups" dialog after clicking to avoid lock exception
* ff52745  HUE-8281 [spark] Can not connect to Livy Server with HTTPS (#688)
* 9568734 HUE-8273 [filebrowser] Support white spaces in filenames
* 814816b HUE-8274 [s3] Moving a folder using drag and drop deletes the folder itself
* 61b42fb HUE-8262 [dashboard] Disable droppable area of the empty Gridster widget
* f852bb2 HUE-8276 [dashboard] Allow deleting the filter bar and grid widget on standard mode
* 57ff64d HUE-8277 [frontend] The selectize binding should append to the body by default to prevent cutting its options
* 6b4875d HUE-8278 [dashboard] Enable grid results field list resizer on Gridster too
* 2d48bb5 HUE-8268 [jb] Move id column to the right in job listing
* 6eda14e HUE-8267 [jb] Show tasks of workflows by default in mini browser mode
* be60e28 HUE-8267 [oozie] Hide the time filtering widgets for schedules and bundles
* 9b0abb6 HUE-8267 [oozie] Disable time filtering in the backend for schedules and bundles
* d6ea662 HUE-8268 [oozie] Split the jobs into running and completed sections
* 0eeeb3e HUE-8271 [dashboard] Use the sqlContextPopover in the top field chooser
* e7fe322 HUE-8270 [dashboard] Re-start the scrollbar removal interval on assist drag stop
* ac660a2 HUE-8257 [dashboard] The plus button hint should be shown just on hovering the filter bar
* 97d6500 HUE-8250 [dashboard] Remove widget toolbar on Gridster
* 10eeec3 HUE-8269 [dashboard] Hide the new add form if not specifically configured
* ebf821d HUE-8246 [dashboard] 'Add' on an empty widget should behave and look like dimensions metric forms
* 656e5c3 HUE-8269 [dashboard] Hide the new adding mechanism under a feature flag
* 29af0b9 HUE-8232 [oozie] Fix 500 error if coordinator associated workflow has been deleted
* 5311748 HUE-8265 [frontend] Introduce a documentContextPopover binding to quickly look at any Hue document
* 1a43403 HUE-8266 [fb] remove hash from test file name as it is not authorized
* d8cdcec HUE-8264 [frontend] The path on sqlContextPopover should be updatable
* 64a3701 HUE-8263 [dashboard] Avoid white space in the widget after moving from a high sibling to no siblings
* 29d35df HUE-8260 [oozie] Use storageContextPopover for the Editor external links
* 06a195b HUE-8261 [core] Fix the pypi URL when building
* bd2beaf HUE-8253 [editor] Support downloading Query results with query names(file names) other than ISO-8859-1 charset
* b304fea HUE-8252 [jdbc] Provide ability to configure users impersonation with jdbc (#687)
* 33cbf6d HUE-8258 [dashboard] Disable deleting filter bars and grids
* 1604595 HUE-8257 [dashboard] Make the drag from top or right assist hint less intrusive
* d38a822 HUE-8192 [assist] Include description in the assist document filter
* cb74c3b HUE-8256 [assist] Remove the filter icon and sort options from the left assist
* c8c58a1 HUE-8155 [metastore] Fix issue where all columns are marked as keys
* 113aafc HUE-8255 [dashboard] Remove query builder mode Gridster limitations
* 5b85e4e HUE-8254 [dashboard] Add helper arrow to the right assist
* 4abf330 HUE-8245 [dashboard] Disable plus button hint on Query Builder mode
* 0c6f98c HUE-8155 [metastore] Show a key next to columns that are popular in join conditions
* bff9c3e HUE-8155 [metastore] Add a relationships tab to the table browser page
* 1e07127 HUE-8245 [dashboard] Show arrow help to improve discoverability of plus button drag
* 9cd72a4 HUE-8247 [dashboard] Add a field quick lookup icon on the metrics form
* 0f1ff1b HUE-8251 [assist] Add content preloader ghost image only when scrolling
* f4ad1d4 HUE-8242 [frontend] Fix JS error when fetching MultiTableEntries
* 08feb80 HUE-8241 [frontend] Add an open action to document results in the global search
* df32f3d HUE-8118 [core] The duration of the request is always shown even when instrumentation flag is off
* f845dcb HUE-8248 [dashboard] Automatically expand widgets to show all their content
* d2e8397 HUE-8243 [dashboard] Improve look of layout chooser
* d31b886 HUE-8244 [dashboard] Hide right assist after choosing a search layout
* 10b61b7 HUE-8240 [dashboard] HTML widget editing should move to a popover like dimensions editing
* 3c82ab7 HUE-8238 [importer] Simplify the action icon of the index page
* cf6d097 HUE-8228 [metadata] Disable auto creation of namespaces for now
* f99a147 HUE-8236 [core] Correct Hue config value use integer instead of math expression
* a176d0b HUE-8237 [assist] Add a go home link in the upper right corner of the storage context popover
* a4f2ff6 HUE-8234 [frontend] Add a storageContextPopover binding for file entries
* c4784ee HUE-8237 [assist] Improvements to the file context popover
* dcdd595 HUE-8237 [assist] New context popover for files V1
* dad4c46 HUE-8155 [assist] Prevent interval from firing when the multiLineEllipsis binding is expanded
* 9d23e42 HUE-8234 [frontend] Add a contextPopover binding
* ec55384 HUE-8155 [assist] Prevent cutting text in the multiLineEllipsis binding when the text is expanded
* 057654e HUE-8155 [metastore] Prevent JS error when editing empty properties
* e4834eb HUE-8187 [doc] Add Instrumentation flag and log format documentation to upstream documentation
* af3cd4a HUE-8233 [core] Add chardet 3.0.4 to ext-py
* afe5ae4 HUE-8226 [dashboard] Remove preformatted details about the metrics form
* cd4fa74 HUE-8229 [dashboard] Dragging from the right assist should add a bar widget
* 570d87e HUE-8230 [assist] Hide context popover just on vertical movement of the info icon
* 5fd1ad5 HUE-5306 [fb] Remove bucket cache from S3 browser to force re-authentication (#681)
* 1a73991 HUE-8231 [dashboard] Auto resize widget height on window resize
* 55fd566 HUE-8228 [dashboard] Simplify the menu of create a new dashboard
* 91e9cc4 HUE-8227 [dashboard] Make Grid and Chart widgets more compact
* 5261ead HUE-8226 [dashboard] Adding a new widget shouldn't show the semi modal for picking a field
* 715ac03 HUE-8225 [dashboard] Dragging the plus button should add the new dimensions-enabled widget
* c91f864 HUE-8222 [dashboard] Skip empty widgets on height equalizing
* e59323e HUE-8223 [dashboard] Resize former sibling widgets after a row move
* 28ca80b Adding fix for Hue Build process, Currently Hue Build process is broken due to Python2.6 pypi.python.org TLSv1.2 issue. Along with above changes on build infra side we have to add following changes.
* 406d2f5 HUE-8219 [dashboard] Resize sibling widgets to the max available space after a widget manual resize
* 0df3d15 HUE-8224 [dashboard] Avoid JS error on missing dimensions facets
* 289145a HUE-8155 [metastore] Fix issue that prevents inline editing of descriptions in the tables list
* cbf5c26 HUE-8155 [metastore] Prevent calling navigator when it's not configured
* b1b5dfe HUE-8155 [metastore] Improve description expand/collapse styling
* cfd3f6b HUE-8222 [dashboard] Fix JS error on widget height equalizing function
* aabb5b3 HUE-7917 [assist] Make it possible to expand the comment in the context popover
* 55af7b8 HUE-8155 [metastore] Improve link matching in the description
* 9055de8 HUE-8155 [metastore] Show view SQL for views in the Table Browser
* ba50f50 HUE-8213 [assist] Improve table filter response snappiness
* 98e9ac5 HUE-8211 [metastore] Send the correct entity type when fetching navigator metadata
* 61e5817 HUE-8218 [search] Remove the dropdown of choice of engines in new dashboard
* afd2c2e HUE-8218 [dashboard] Creating a dedicated HTML or Analytical layout
* 332898f HUE-8218 [search] Split layouts in analytical and search
* b54cd3c HUE-8209 [editor] Default presentation mode does not work
* b5ddd9c HUE-8216 [metadata] Workaround Impala not always specifying a table is actually a view
* fa5128b HUE-8207 [indexer] Detect the encoding of the imported file
* 8dd21b1 HUE-8207 [indexer] Issue previewing input file with unicode data
* 7a3896b HUE-8220 [dashboard] Enable HTML resultset widget templating in the new Gridster mode
* 23bd00d HUE-8217 [dashboard] Fix HTML resultset widget templating
* 79b5160 HUE-8212 [dashboard] Add drag cursor to the plus button
* b0f174c HUE-8214 [frontend] Show selectize clear button just on hover
* 5cbdb1d HUE-8181 [assist] Introduce content preloader UX trick to improve speed perception
* cd18e24 HUE-8195 [dashboard] Trigger auto expand/shrink of the widgets just on switching back and forth on grids
* e641f7d HUE-8204 [dashboard] Allow dragging of the plus button into the widgets area
* 7a75927 HUE-8155 [metastore] Only show the edit description icon when the description is expanded
* deea3bf HUE-8206 [frontend] Close the global search after show in assist or table browser is clicked
* 962af04 HUE-8203 [tools] Exclude generated CSS files from the reviews
* 668fbb9 HUE-8155 [metastore] Create links for any found URLs in the descriptions
* eef008a HUE-8155 [metastore] Properly handle and recover from errors when modifying tags fails
* 9edcdf0 HUE-8155 [metadata] Only send modified custom Navigator metadata to prevent setting stale data
* e5ae685 HUE-8155 [metadata] Make it possible to remove custom metadata entries in the Table Browser
* 36493b9 HUE-7793 [dashboard] Do not convert dates with non traditional format (#676)
* d3eebcf HUE-8202 [jb] Fix mutual authentication failed with Isilon (#675)
* 64c49c9 HUE-8201 [frontend] Make custom styled scrollbars darker for a better visibility on standard screens and reduce discovery time
* 5965a29 HUE-8200 [metadata] API to provide properties mapping of custom metadata
* 0cf0cbf HUE-8199 [metastore] Add sample counts to the section name
* 693ac89 HUE-8199 [metastore] Humanify the table stats section
* aeebd3b HUE-8199 [metastore] Remove the partition listing preview on table page
* f0d2842 HUE-8199 [metastore] Remvove column count indicator as inside the listing already
* 2384da5 HUE-8199 [metastore] Humanify the table properties section
* 906f85b HUE-8111 [core] Change jenkins URLs to static
* 899e2f8 HUE-8191 [jb] UnicodeEncodeError occurs in Job Browser when browser language is not English
* 09835bc HUE-8197 [editor] Saved queries with a variable are broken after upgrade
* b26ee66 HUE-8075 [docs] Update variable documentation.
* 4929c6d HUE-8155 [metastore] Improve the databases, tables and columns table in the Table Browser
* beed4f8 HUE-8194 [dashboard] Remove un-necessary autoheight feature
* 2e93f17 HUE-8193 [dashboard] Dragging from the right assist should never show the field picker
* fbcff2d HUE-8189 [dashboard] Prevent fixed search bar to be on top of the main Hue menu dropdown
* 476d83d HUE-7680 [frontend] Get rid of the custom JS scrollbars to improve performances
* a862e23 HUE-8172 [sqoop] Hide un-necessary options in the importer
* 6ddc00b HUE-8190 [dashboard] Support switching an existing widget to text facet
* 1bed41e HUE-8186 [dashboard] Fix move widgets corner cases when moving along the same row
* ab362b1 HUE-8188 [frontend] Avoid graying out all the Hue SVGs on chart select events
* e1fc1b7 HUE-8155 [metastore] Expand the description on click instead of entering edit mode
* 375e737 HUE-8155 [metastore] Style the description column placeholder
* 9be10b1 HUE-8185 [frontend] Move selectize CSS to Less
* 8f9be33 HUE-8184 [dashboard] The search bar should be fixed on top
* d0c0eed HUE-8183 [dashboard] Auto resize widget height when the content changes height
* 6bc1163 HUE-8155 [metastore] Unify description, tags and properties editing in the table browser
* 4f57bad HUE-8155 [assist] Prevent jumping description in the context popover
* 3724002 HUE-8162 [core] Add delete operation to the right document assist
* c19f52b HUE-8179 [dashboard] Text widget in a saved dashboard should have an edit dimension
* 8e61ff5 HUE-8175 [dashboard] Avoid having siblings widgets with different heights
* 26b201d HUE-8155 [metastore] Don't show description in bold after change
* ee3d751 HUE-8155 [metastore] Make it possible to edit custom properties in the table browser
* 9995c12 HUE-8182 [frontend] Remove typo from context popover
* 7e35b82 HUE-8176 [dashboard] Swapping widgets sometimes creates a new row instead of swapping
* 63a039f HUE-8180 [frontend] Remove global invalid input CSS
* 1ed83c2 HUE-8173 [core] Add a warning log when a users switched to the old Hue 3 UI
* f23c09a HUE-8173 [core] Add a log line when a user loads a page not via the load balancer even if we have one
* eb14057 HUE-8172 [sqoop] Importer does not list databases of configured DBs
* a7832b3 HUE-8171 [dashboard] Counter widget does not propose numerical function on numbers
* 4003087 HUE-8111 [core] Update release detail doc with latest commits
* cb8c38a HUE-8073 [editor] Changed editing for date variables
* 426806f HUE-8168 [editor] Add multi line ellipsis (show more/less) on record preview modal
* 3ffcae5 HUE-8174 [dashboard] Remove CSS transition on the dimensions opacity to prevent rendering problems
* d97fbea HUE-8155 [metastore] Show key columns in the top columns list
* 67a4098 HUE-8155 [metastore] Improve layout for tables and show more links in the Table browser
* 985e89f HUE-8150 [core] Simplify the catalog skeleton page
* 7b9673d HUE-8161 [metadata] Improve naming for the catalog namespace
* 6180c46 HUE-8161 [metadata] Switch to using proper http error codes instead of success response with custom status flag
* 3715873 HUE-8155 [metastore] Make sure navigator metadata is cleared on refresh in the table browser
* f08b604 HUE-8155 [metastore] Replace main action icons with buttons
* 399b5fd HUE-8170 [useradmin] Fix LDAP sync (ldap_access.py) certificate validation logic
* 3cdcbf6 HUE-8169 [doc] Simplify the readme to link to the documentation
* 136e053 HUE-8150 [core] Add static list of facets to the catalog page
* 22e3ef6 HUE-8150 [core] Catalog search page skeleton
* 5800ddc HUE-8161 [metadata] Automatically create a namespace to enrich the catalog
* a65d88c HUE-8161 [metadata] API to map a namespace entity to a class
* bf730c2 HUE-8161 [metadata] API to create a namespace
* 6f20796 HUE-8161 [metadata] Support creating a namespace property
* 6def9d1 HUE-8161 [metadata] Support retrieving a namespace
* b648631 HUE-8161 [doc] Avoid breaking toc with title tags in ini example
* b9c6c6c HUE-8111 [core] Perform 4.2 release
* af1b31e HUE-8161 [metastore] Add Partitioned information to table type
* 4d2c4e0 HUE-8169 [docs] Add extended requirements and cx_Oracle compiling section to the admin manual
* c4ea4b4 HUE-8163 [frontend] Move dashboard-specific selectize css out of the common css
* f9af8ec HUE-8159 [oozie] Unable to create Workflow/Schedule using Java document Action
* 110eeab HUE-8155 [metastore] Improve general alignment and spacing in the Table Browser page
* 6e6146d HUE-8155 [metastore] Move the edit description icon inline
* dd1a1c1 HUE-8155 [metastore] Only show description expand link on hover
* 3a525a6 HUE-8167 [dashboard] Dragging/Dropping on an empty widget should remove the dropzone
* 0d8bd22 HUE-8163 [frontend] Avoid a few pixels push down when opening any selectize
* 75f2485 HUE-8166 [frontend] Check in package-lock.json
* 40e7a25 HUE-8164 [editor] The record viewer should wrap its content
* 525f09e HUE-8146 [dashboard] Avoid wrong widget clones on right assist drag'n'drop
* ba157b9 HUE-8154 [dashboard] Dropping on the center of a widget should behave as southern edge drop
* e205752 HUE-8153 [docs] TOC Search input should have a fixed position
* a86118a HUE-8073 [editor] Add default value for variable calendar widget
* 3a2e20f HUE-8158 [metastore] Hide internal metadata properties
* 7590c0b HUE-8118 [core] Fine grain tracking of the memory usage
* e410494 HUE-8153 [docs] Show expanded TOC tree by default and highlight search keyword


Contributors
------------

This Hue release is made possible thanks to the contribution from:

- Aaron Newton
- Aaron Peddle
- Aaron T. Myers
- abec
- Abraham Elmahrek
- Aditya Acharya
- Adrian Yavorskyy
- aig
- airokey
- Alex Breshears
- Alex Newman
- Alex (posi) Newman
- alheio
- alphaskade
- Ambreen Kazi
- Amit Kabra
- Andrei Savu
- Andrew Bayer
- Andrew Yao
- Andy Braslavskiy
- Ann McCown
- antbell
- Antonio Bellezza
- arahuja
- Ashu Pachauri
- Atupal
- Avindra Goolcharan
- bcwalrus
- bc Wong
- Ben Bishop
- Ben Gooley
- Ben White
- Bhargava Kalathuru
- Bruce Mitchener
- Bruno Mahé
- bschell
- bwang
- cconner
- Chris Conner
- Chris Stephens
- Christopher Conner
- Christopher McConnell
- Christopherwq Conner
- cmconner156
- Craig Minihan
- cwalet
- Daehan Kim
- dbeech
- denniszag
- Derek Chen-Becker
- Diego Sevilla Ruiz
- Dominik Gehl
- Eli Collins
- Enrico Berti
- Erick Tryzelaar
- Ewan Higgs
- fatherfox
- gdgt
- Gilad Wolff
- grundprinzip
- Guido Serra
- happywind
- Harsh
- Harsh J
- Hector Acosta
- Henry Robinson
- Igor Wiedler
- Ilkka Turunen
- Istvan
- Ivan Dzikovsky
- Ivan Orlov
- Jack McCracken
- Jaguar Xiong
- Jakub Kukul
- Jarcek
- jdesjean
- jeff.melching
- Jenny Kim
- Joe Crobak
- Joey Echeverria
- Johan Ahlen
- Johan Åhlén
- Jon Natkins
- Josh Walters
- Karissa McKelvey
- Kevin Wang
- Kostas Sakellis
- krish
- Lars Francke
- Li Jiahong
- linchan-ms
- Linden Hillenbrand
- Luca Natali
- Luke Carmichael
- lvziling
- Marcus McLaughlin
- Mariusz Strzelecki
- Mathias Rangel Wulff
- Matías Javier Rossi
- Max T
- Michael Prim
- Michal Ferlinski
- Michalis Kongtongk
- Mobin Ranjbar
- motta
- mrmrs
- Nicolas Fouché
- NikolayZhebet
- Olaf Flebbe
- Oren Mazor
- oxpa
- Pala M Muthaia Chettiar
- Patricia Sz
- Patrick Carlson
- Patrycja Szabłowska
- pat white
- Paul Battaglia
- Paul McCaughtry
- peddle
- Peter Slawski
- Philip Zeyliger
- Piotr Ackermann
- pkuwm
- Prachi Poddar
- Prakash Ranade
- Prasad Mujumdar
- Qi Xiao
- rainysia
- raphi
- Renxia Wang
- Rick Bernotas
- Ricky Saltzer
- robrotheram
- Romain Rigaux
- Roman Shaposhnik
- Roohi
- Roohi Syeda
- Rui Pereira
- Sai Chirravuri
- Scott Kahler
- Sean Mackrory
- Shahab Tajik
- Shawn Van Ittersum
- shobull
- Shrijeet
- Shrijeet Paliwal
- Shuo Diao
- Siddhartha Sahu
- Simon Beale
- Simon Whittaker
- sky4star
- spaztic1215
- Stefano Palazzo
- Stephanie Bodoff
- Suhas Satish
- TAKLON STEPHEN WU
- Tamas Sule
- Tatsuo Kawasaki
- thinker0
- Thomas Aylott
- Thomas Poepping
- Tianjin Gu
- tjphilpot
- todaychi
- Todd Lipcon
- Tom Mulder
- Vadim Markovtsev
- van Orlov
- vinithra
- voyageth
- vybs
- Wang, Xiaozhe
- Weixia Xu
- William Bourque
- wilson
- Word
- Xavier Morera
- Xhxiong
- xq262144
- Ying Chen
- Yixiao Lin
- Yoer
- Yuriy Hupalo
- ywheel
- Zachary York
- Zach York
- Zhang Ruiqiang
- zhengkai
- Zhihai Xu
- z-york
- 小龙哥
