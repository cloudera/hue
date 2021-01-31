---
title: "4.7.0"
date: 2020-04-10T18:28:08-07:00
draft: false
weight: -4070
tags: ['skipIndexing']
---

## Hue v4.7.0, released April 10th 2020

Hue is an open source SQL Cloud Assistant for developing and accessing [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/)/Data Apps and collaborating: http://gethue.com


**Note**: Hue v4.7.1, released May 20th 2020 - [HUE-9356](https://issues.cloudera.org/browse/HUE-9356)

* Kerberos 'TypeError: function takes at most 2 arguments (3 given)' [ISSUE 1101](https://github.com/cloudera/hue/issues/1101)
* There was also other JavaScript bugs in the Query Browser related to some Ko-Js dependencies

### Summary

The focus of this release was to keep building on top of [4.6](https://gethue.com/hue-4-6-and-its-improvements-are-out/), modularize the tech stack, improve SQL integrations and prepare major features of Hue 5. Some highlights:

* Top blue button has been converted to a menu in the left side
* Birthday time: its was the [10 years of Hue!](https://gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/)
* Build your own or improve the [SQL parsers](https://docs.gethue.com/developer/parsers/)
* Japanese blog is back https://jp.gethue.com/
* A big summary of the [Datawarehouse UX](https://gethue.com/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/) was published


Read the complete list of improvements on [Hue 4.7 is out!](http://gethue.com/blog/hue-4-7-and-its-improvements-are-out/).

Download the [tarball](https://cdn.gethue.com/downloads/hue-4.7.1.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.7.1.zip) releases.

### Notable Changes

SQL

* [Foreign Keys](https://gethue.com/2019-11-13-sql-column-assist-icons/) are showing-up in the SQL left assist
* The autocomplete grammar was updated with: INTEGER, CTAS, STREAM keyword, EXPLAIN, LOAD, SHOW MATERIALIZED VIEW, ALTER MATERIALIZED VIEW,  DROP MATERIALIZED VIEW
* Materialized views are showing-up with the proper eye icon
* Hive LLAP/Tez sessions management was revamped in order to support more than one query running concurrently
* The Drag & Drop from the SQL left assist flakiness was fixed
* SQL samples now also work with mutable tables (e.g. ORC format tables with INSERT, DELETE, UPDATE..)
* How to build [SQL Autocompletes tutorial](https://docs.gethue.com/developer/parsers/) has been updated
* SQL Autocomplete parsers are now available as a [JavaScript component](https://gethue.com/blog/2020-02-27-using-sql-parser-module/) pluggable via a classic `npm install`

Collaboration

* Queries snippets can be shared via a [Gist](https://gethue.com/blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/#sql-snippet---gist) with their own Slack previews
* Queries can be shared via [public links](https://gethue.com/blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/#public-links)
* The link sharing modal was restyled to be [friendlier](https://cdn.gethue.com/uploads/2020/04/4.7_sharing_popup.png)

Infra

* [Azure ABFS filesystem](https://gethue.com/integration-with-microsoft-azure-data-lake-store-gen2/) is now officially supported
* The continuous integration now [checks for deadlinks](https://gethue.com/checking-dead-links-automatically-continuous-integration/) on [docs.gethue.com](https://docs.gethue.com/)
* Python 3: support is making additional progress. How to compile with it and send feedback:
  ```
  export PYTHON_VER=python3.6
  make apps
  ```

Admin

* Configuration settings can be searched [via a filter](https://cdn.gethue.com/uploads/2020/04/4.7_admin_config_filter.png)
* The delete flow of a user now disables instead of deleting (to avoid losing the saved documents and queries)
* User admin page now displays [ACTIVE and SUPERUSER](https://cdn.gethue.com/uploads/2020/04/4.7_admin_users_status.png) statuses
* The number of [active users](https://gethue.com/hue-active-users-metric-improvements/) metric per API instance was revamped

Progress

* [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) The new version of the Editor with multi execution contexts and more robustness got 200+ commits
* [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) SQL connectors configuration instead of using hue.ini is close to a MVP
* [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) The Optimizations and Catalogs API were made public
* [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) The Celery Task Server and SQL task got updated for Python 3


### Compatibility

Runs on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7), and Ubuntu 18.04 and 20.04.

Tested with CDH6 and CDP Data Center. Specifically:

- Hadoop 3.0
- Hive 2.2 / 3.0
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

* 58ef4c0d12 [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [gethue] Add more examples of DB connector configurations
* 173d728ef6 [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [docs] Perform release 4.7
* daf8d0784c [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [docs] 4.7 release notes
* 9682b0be42 [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [blog] 4.7 release post
* 64b1e07e97 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Initial clean-up of local optimizer strategy
* f2637c4741 [HUE-9247](https://issues.cloudera.org/browse/HUE-9247) [editor] Fix issue where the location webworker throws exception for non-active statements
* a73055cbd7 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Check complexity for all dialects when configured in editor V2
* 1199c6480d [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Improve instantiation of optimizer strategies
* c5b27a73b3 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fix js exception in the admin examples page
* cca37e1a7d [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Fix exceptions in the connector page filter
* e8c45bf095 [HUE-9246](https://issues.cloudera.org/browse/HUE-9246) [core] Enable SAML certificate creation with passphrase support. (#1096)
* b99879b7a0 Hue Aquascan CVEs (#1095)
* cdad7c7b24 [HUE-9243](https://issues.cloudera.org/browse/HUE-9243) [jobbrowser] Adding new TestHS2Api unit test suite
* 5b6021caf9 [HUE-9243](https://issues.cloudera.org/browse/HUE-9243) [jobbrowser] improve get_jobs to handle jobbrowser on blacklist
* dc237ca7d8 [HUE-9297](https://issues.cloudera.org/browse/HUE-9297) [optimizer] Adding localStrategy with LIMIT alert
* 3cee6411ad [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [optimizer] Refactor optimization mode selection
* 7a89e7580c [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [optimizer] Precent empty risk alerts
* c4f18c1ca5 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Prepare get_logs API to support connector
* 590572fded [HUE-9235](https://issues.cloudera.org/browse/HUE-9235) [metrics] Format long lines and remove noisy LOG
* 876f68706e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Use impersonation value from setting
* 41a27e2ee7 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fix test connection result logic display
* baecc0a68d [HUE-9216](https://issues.cloudera.org/browse/HUE-9216) [core] Upgrade SqlAlchemy to support Foreign Keys API
* b861b1d8f0 [HUE-9219](https://issues.cloudera.org/browse/HUE-9219) [parser] Improve PartitionBy rules in impala (#1088)
* a1bb893868 [HUE-9235](https://issues.cloudera.org/browse/HUE-9235) [core] Change prometheus metric log level to debug
* 48e3c92632 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Use the real connector in the context selector in editor v2
* 5e61caebfb [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix issue with loading back a snippet from history in editor v2
* 879aba379e [HUE-9221](https://issues.cloudera.org/browse/HUE-9221) [tools] Mark open jiras as "in progress" when using hueJira.js
* d3146ed861 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [api] Remove duplicated document types in get_config
* fb2c7f0986 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Add a patch method to simplify compatibilities
* df1f7df3f6 [HUE-9176](https://issues.cloudera.org/browse/HUE-9176) [core] Introduce Vue dependency (#1080)
* 640687d143 [HUE-9239](https://issues.cloudera.org/browse/HUE-9239) [frontend] Add custom package.json for parser generation
* 9578cc73e0 [HUE-9239](https://issues.cloudera.org/browse/HUE-9239) [frontend] Fix simpleGet reference for the threads and metrics pages
* 32a5638a26 [HUE-9236](https://issues.cloudera.org/browse/HUE-9236) [frontend] Remove Ace build related packages from the main package.json
* ad024c3307 [HUE-9236](https://issues.cloudera.org/browse/HUE-9236) [frontend] Remove tools related packages from the main package.json
* 7dc21fab35 [HUE-8993](https://issues.cloudera.org/browse/HUE-8993) [editor] Do not propose export result when there is no FS
* 6c3ade1292 [HUE-8738](https://issues.cloudera.org/browse/HUE-8738) [task] Do not error when caching and empty query result
* 629a76d32f [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Avoid error when trying to close non existing past query
* 2ac2915a4c [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [phoenix] Adding Phoenix connector dialect
* 9beeacbc9e [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [s3] Avoid 500 with Python3 on exception catching
* e3dfba6478 [HUE-9240](https://issues.cloudera.org/browse/HUE-9240) [hive] Do no skip first table column on LLAP upstream
* ed95c75f5e [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [blog] Localized blogs into Japanese (#1092)
* 5e6aa8d885 [HUE-9235](https://issues.cloudera.org/browse/HUE-9235) [core] Clean up metrics for exporting to prometheus
* bc99874027 [HUE-9181](https://issues.cloudera.org/browse/HUE-9181) [blog] Document the admin improvements coming in 4.7
* 05c548f87a [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [optimizer] Simplify api to just require user instead of request
* 5b60570493 [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [editor] Refactor optimizer API to follow notebook API
* 55867053cb [HUE-9217](https://issues.cloudera.org/browse/HUE-9217) [editor] SQL Highlight for JOIN autocomplete
* bd88a4ea68 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix npm blog post output indentation
* 8affbd3804 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix wrong title level for Apache Solr
* 8ab0e5f863 [HUE-8993](https://issues.cloudera.org/browse/HUE-8993) [importer] Do not propose file import when there is no fs
* 007140a213 [HUE-9238](https://issues.cloudera.org/browse/HUE-9238) [design] Apache Phoenix SQL support
* 1d7598c9b9 [HUE-8993](https://issues.cloudera.org/browse/HUE-8993) [core] Globally disabled sqoop importer
* 6ec4a536fa [HUE-9236](https://issues.cloudera.org/browse/HUE-9236) [core] Log the npm and node versions on make
* 70088f878b [HUE-9224](https://issues.cloudera.org/browse/HUE-9224) [frontend] Move the connectors category filter to a dropdown
* 12c5057c9e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add README to the source of the docs
* 505a7933f5 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Update the docs and blog post about parser npm module
* 87a5cd37bb [HUE-9192](https://issues.cloudera.org/browse/HUE-9192) [tools] Remove old impala helm charts
* 7d3e34ac0a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [notebook] Small code formatting
* 756907b6e6 [HUE-9216](https://issues.cloudera.org/browse/HUE-9216) [sqlalchemy] Primary keys
* e9491cf873 [HUE-9216](https://issues.cloudera.org/browse/HUE-9216) [sqlalchemy] Foreign keys
* 5cff7b99c1 [HUE-9223](https://issues.cloudera.org/browse/HUE-9223) [frontend] Fix high risk npm package vulnerabilities
* 1313689812 [HUE-8993](https://issues.cloudera.org/browse/HUE-8993) [core] Avoid hardcoding an hdfs cluster in the image
* 266d67bda9 [HUE-9234](https://issues.cloudera.org/browse/HUE-9234) [core] Add coordinator_url in hue.ini config in impala section (#1089)
* 65e4a85cf6 [HUE-9210](https://issues.cloudera.org/browse/HUE-9210) [blog] Add post hue active users metrics imporvements
* 3f03736957 [HUE-9194](https://issues.cloudera.org/browse/HUE-9194) [blog] Add post on setting up prometheus server
* 906062aff6 [HUE-9221](https://issues.cloudera.org/browse/HUE-9221) [tools] Add a tool that automatically adds review and commit urls to Jira comments
* 68c38c7902 [HUE-9218](https://issues.cloudera.org/browse/HUE-9218) [frontend] Remove unused wysihtml lib
* 21e5ff752e [HUE-9220](https://issues.cloudera.org/browse/HUE-9220) [editor] Fix issue where query error messages are not shown in the UI
* 55cc9b0aa5 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Add missing canceled status in checkStatus check
* 3672582db9 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [impala] Do not hardcode impersonation setting to true
* 4e90cd052b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [impala] Do not hardcode impersonation setting to true
* 7a3d3a93d6 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [optimizer] Convert queries to bytes if needed
* 4a74295c48 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] cancel and close statements can error
* 1249063112 [HUE-9209](https://issues.cloudera.org/browse/HUE-9209) [Hue] Adding SAML dependancies for Hue docker container (#1087)
* 5aa0fa0e48 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Improve connector component stability
* 5113c05f59 [HUE-9215](https://issues.cloudera.org/browse/HUE-9215) [assist] Prevent loading namespaces for indexes and streams in the assist panel
* 040753d9a9 [HUE-9214](https://issues.cloudera.org/browse/HUE-9214) [search] Fix invalid contents of clipboard.min.js
* b3c6766c84 [HUE-9213](https://issues.cloudera.org/browse/HUE-9213) [ui] Fix js exception in multiLineEllipsisHandler
* 030d96b39e [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [tb] Fix optimizer related js exception in the table browser
* 7c1c7ff90f [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Fix ko context issues in the connectors component
* 834ab6b990 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Fix titles in getting started with Docker post
* 94c9504cbd [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [design] Adding tasks for Editor 3
* 438cc0fa83 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [notebook] Add tests for sql utils
* a037d0746d [HUE-9212](https://issues.cloudera.org/browse/HUE-9212) [core] Fix missing login-modal causes auto logout failed
* 0ac734b51d [HUE-9209](https://issues.cloudera.org/browse/HUE-9209) [Hue] Adding SAML dependancies for Hue docker container (#1086)
* 384692587b [HUE-9211](https://issues.cloudera.org/browse/HUE-9211) [editor] Saving a query gets a popup exception saying 'dialect'
* 73f4d61878 [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [metadata] Simplify optimizer interface names
* 2606c874b3 [HUE-8824](https://issues.cloudera.org/browse/HUE-8824) [metadata] Small config styling refactoring
* 282f6bceed [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Rename export_csvxls with tests suffix
* 800e902aab replace wrong syntax in insertValuesList (#1082)
* 1a784b983c [HUE-9208](https://issues.cloudera.org/browse/HUE-9208) [tasks] Python 2 compatibility for cache delimiter char
* cbcd4b7a33 [HUE-9208](https://issues.cloudera.org/browse/HUE-9208) [tasks] Properly rename task tests with correct prefix
* 842d6a90ee [HUE-9208](https://issues.cloudera.org/browse/HUE-9208) [tasks] Mock celery task to enable tests without celery
* 9fe414c8cf [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Light roadmap update
* ddd013daa1 [HUE-9208](https://issues.cloudera.org/browse/HUE-9208) [editor] Port get log call to v2 and sql task
* 214dd41369 [HUE-9208](https://issues.cloudera.org/browse/HUE-9208) [editor] Port close statement to v2 and sql task
* 105af052f2 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [task] First basic unit test for async SQL query task
* 79c85468c8 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [task] Adding first unit test for sync SQL query task
* 11313cbc41 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Also send batch results via WS if available
* f34ada1cab [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Log connector dialect name instead of connector id
* 5d9f15deff [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [editor] Send websocket channel in v2
* 9b275e914e [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Introduce optimizer strategies
* 2abca579ed [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Extract optimizer logic from the ApiHelper
* b473dfc636 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Move the connectors page into a component
* 804f86568e [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Extract shared ApiHelper logic to a separate module
* a9683e3aa0 [HUE-9207](https://issues.cloudera.org/browse/HUE-9207) [frontend] Rename navopt to optimizer throughout
* 3e3e02b6a1 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Drop the mako json usage of "languages" in editor v2
* e07282c8db [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Remove mako dependency on interface in editor v2
* fd19ac5fb2 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Fix issue where the editor view model is out of sync with the snippet in editor v2
* 4233118951 [HUE-9210](https://issues.cloudera.org/browse/HUE-9210) [useradmin] Display number of local active users in Cloudera Manager
* 1530e575de [HUE-9202](https://issues.cloudera.org/browse/HUE-9202) [core] Adding number of queries metric
* 38aeaa9616 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Keep default css width for sql limit input
* 421278840a [HUE-8768](https://issues.cloudera.org/browse/HUE-8768) [task] Make SQL task compatible with Editor 2
* d053143409 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Task server SQL tasks compatibility
* f16b12350f [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Larger limit box auto growing to support two more digits
* 50ff4c40cb [HUE-9206](https://issues.cloudera.org/browse/HUE-9206) [tools] First npm release with parser module
* 07523600ae [HUE-9206](https://issues.cloudera.org/browse/HUE-9206) [tools] Change npm to public and gethue name
* 0578b37ce1 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Link to npm demo app properly
* c415aef3e3 [HUE-9205](https://issues.cloudera.org/browse/HUE-9205) [hive] Avoid stack trace when querying a table with missing permission
* ad570cdf25 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [model] Test checking get document history with connector
* b5b5ac22ba [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [model] Adding Document2 connector FK migration org on
* 2c5947c7de [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [model] Adding Document2 connector FK migration org off
* 4b6c17e06d [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Fix the quick query context connector
* 65a348e648 [HUE-9203](https://issues.cloudera.org/browse/HUE-9203) [editor] Improve drag and drop from the left assist into the editor
* 514d9b9bb1 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Add action to reset the executable from the error log in editor v2
* 55410e8408 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Prevent thrown exception on execution in editor v2
* eb96d0a1e7 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Properly rename api test file
* 29a666ff1e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [model] Adding first get_history model test
* d87b59834f [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [api] Rename document2 to models test
* 90718ffc6b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [api] Adding connector_id to editor get_history
* f39674bee6 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add back dialect name to Editor API
* fcb90acc7c PR1079 [k8s] Add podAnnotations section (#1079)
* 63e68465a2 [HUE-9204](https://issues.cloudera.org/browse/HUE-9204) [useradmin] Filter not yet login users out of active users metric
* 3c17378c34 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [design] Update for better connector integration
* 9743ce78e2 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [design] Information on Editor v2 and connector convergence
* 7be9392eb6 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [api] Add list of document types to config
* d7209ad85e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Use proper query type when saving a query
* e929a6d142 PR1076 [blog] Localized three blogs into Japanese (#1076)
* 0fdc985c59 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Switch to connector instead of sourceType in the executor
* 226a3a80fb [HUE-9197](https://issues.cloudera.org/browse/HUE-9197) [abfs] Add missing interface attributes
* ac932665a1 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Simplify developer landing page
* c78eaf1dc9 [HUE-9194](https://issues.cloudera.org/browse/HUE-9194) [useradmin] Make active users metrics available to prometheus
* b29e66324c [HUE-9201](https://issues.cloudera.org/browse/HUE-9201) [Hue] Add which command in Hue Docker (#1075)
* 170f7e907d [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Add back ldap module to requirements
* 355d343b9c [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [docker] Run with gunicorn for Python 3
* 30bc4cb9eb [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [docker] Python3 clean-up and run as hue user
* 047ec23b29 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Port rfc822 to email.utils
* 482a3a5a71 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Make jdbc and saml imports optional
* b3414b1b7e [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Make liboauth modules optional
* e4853b6f1e [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Make a lot of non essnential modules optional
* b364698ac7 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Refactor and remove dependencies in makefile
* b5b963f1df [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [docker] Python 3 Dockerfile skeleton
* 51beb02a15 [HUE-9199](https://issues.cloudera.org/browse/HUE-9199) [core] Remove internationalization of log message in runcherrypy
* 832b256837 [HUE-9199](https://issues.cloudera.org/browse/HUE-9199) [core] Log list of SSL ciphers used by OpenSSL (#1072)
* dea04d4c0a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Emphasize the parser API
* fa49f68dd2 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [sqlalchemy] Remove enum lib and list columns properly
* 73070b2e4c [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Tweak ksql for push queries
* 73171d27f5 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Keep userprofile migrations in sync
* 61fb41d075 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add bug description in the create new issue template
* 11d0a8adc9 [HUE-9195](https://issues.cloudera.org/browse/HUE-9195) [Hue] Perform database connection check in when docker container booting up in kubernetes environment (#1071)
* 825cabfd56 [HUE-9198](https://issues.cloudera.org/browse/HUE-9198) [assist] Add support for assist file panels where the root path can't be listed
* bef86057af [HUE-9197](https://issues.cloudera.org/browse/HUE-9197) [frontend] Use the correct icon for ABFS
* 74170d6e67 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Remove presentation mode type dependency to prepare for connectors in editor v2
* 340955328f [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Fix issue with multiple Hive executions in notebook 2
* 3300d74b6e [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Move snippet handle to executable
* fa659d978c [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Fix garbled editor after clicking "new" in editor v2
* 27a6df6ece [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Only notify dialect change on actual change
* 862c4978d7 [HUE-9190](https://issues.cloudera.org/browse/HUE-9190) [ui] Fix js error when displaying documents in the top search results
* 8f9329bc1b [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Don't publish snippet changes from the history panel
* 33202f33bd [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [ui] Prevent publishing app name to all listeners on the get current app event
* d82a97b88b [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Prevent js exception when clicking outside the ace editor element
* fab7f90b30 [HUE-9187](https://issues.cloudera.org/browse/HUE-9187) [editor] Prevent error message from expired queries in the history in editor v2
* 019aef3cc1 [HUE-9186](https://issues.cloudera.org/browse/HUE-9186) [editor] Fix issue with missing credentials in the editor v2 session auth modal
* 66e38a3881 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] localized blog into Japanese "sql-editor-user-experience" (#1070)
* fb4a123f76 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Bump minimist from 1.2.0 to 1.2.2 (#1068)
* 334af1371d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Bump acorn from 6.0.5 to 6.4.1 (#1067)
* d69dfff818 [HUE-9195](https://issues.cloudera.org/browse/HUE-9195) [Hue] Perform database connection check in when docker container booting up in kubernetes environment (#1065)
* 3129828010 [HUE-9196](https://issues.cloudera.org/browse/HUE-9196) [docker] Run serially hue command: supervisor based wrapper script command (#1066)
* cb224696c0 [HUE-9194](https://issues.cloudera.org/browse/HUE-9194) [useradmin] Set active_users_per_instance callback correctly
* 589b448da1 [HUE-9194](https://issues.cloudera.org/browse/HUE-9194) [useradmin] Get active users per instance
* 8edec160bc [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [sqlalchemy] Pick proper backtick depending on dialect
* 8c371f886a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [sqlalchemy] Do not error when type of column is Null
* fa24f3ebf8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Adding missing default input fields
* a386437a98 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [api] Small code formatting in the log view template
* 5361a5a228 [HUE-9192](https://issues.cloudera.org/browse/HUE-9192) [blog] Adding post on CI for documentation link checking
* 0dc207094b [HUE-9193](https://issues.cloudera.org/browse/HUE-9193) [oozie] Allow workflow argument mixed with single and double quotes
* fd07dc2986 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [beeswax] Avoid KeyError on install examples
* 5c55098d42 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [gethue] Add last modified date from git info (#1062)
* b736152907 [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [blog] Adding reference to foreign keys
* ff60175a83 [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [ui] Add table Foreign Keys icons to the assist
* cbf25fe35f [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [hive] API to retrieve table Foreign Keys
* c1a1f09c15 [HUE-9192](https://issues.cloudera.org/browse/HUE-9192) [docs] Fixing series of dead links in the blog
* dcb570f3f8 [HUE-9192](https://issues.cloudera.org/browse/HUE-9192) [ci] Automatically check for dead links in the website
* ce1b2a8e4b [HUE-9192](https://issues.cloudera.org/browse/HUE-9192) [ci] Util to check dead links in websites
* c2747ed995 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [api] Remove old hardcoded version of Python3 module
* 880f3e2c7f [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [ui] Add table Foreign Keys icons to the assist
* 3ffc3de8ac [HUE-9191](https://issues.cloudera.org/browse/HUE-9191) [hive] API to retrieve table Foreign Keys
* bd447e1b40 [HUE-9185](https://issues.cloudera.org/browse/HUE-9185) [core] Update tests to work with gist turned on
* 71560acdb2 [HUE-9185](https://issues.cloudera.org/browse/HUE-9185) [api] Enable gist and link sharing
* 4eae9fdeb8 [HUE-9189](https://issues.cloudera.org/browse/HUE-9189) [hive] Support expanding tables with single Primary Keys
* cb39639930 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Workaround sortings hardcoded to username
* 4306c260dd [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [gethue] Fix the SQL highlighting of several posts
* 2e91db30ad [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix a series of dead links in the 4.6 release notes
* ac887d2c90 [HUE-9188](https://issues.cloudera.org/browse/HUE-9188) [notebook] Connection leakage in sqlalchemy connector (#1059)
* f813c58d45 [HUE-8883](https://issues.cloudera.org/browse/HUE-8883) [docs] Update the requirements and headers troubleshoot for MacOS 10.15 (#1058)
* e089a6564d [HUE-9185](https://issues.cloudera.org/browse/HUE-9185) [blog] SQL query sharing via links or gists
* 1242c26513 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Give more information on how to add connectors
* 2f4fd4763a [HUE-9185](https://issues.cloudera.org/browse/HUE-9185) [blog] SQL query sharing via links or gists
* eba90715cd [HUE-8790](https://issues.cloudera.org/browse/HUE-8790) [core] Reset write perm when only read sharing a link
* 95aba200d4 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Refresh document assist on save as
* c8356a92d6 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactoring of the connector developer section
* 7d04038339 [HUE-7581](https://issues.cloudera.org/browse/HUE-7581) [editor] typo fix: "... any saved query." -> "... queries." (#926)
* 32ead86c2f [HUE-9183](https://issues.cloudera.org/browse/HUE-9183) [impala] communicate securely with Impala when webserver_require_spnego or is_kerberos_enabled is on
* db807aa2e7 [HUE-9152](https://issues.cloudera.org/browse/HUE-9152) [filebrowser] Fix operations on directories with Cyrillic names
* fa81dea1b9 [HUE-9183](https://issues.cloudera.org/browse/HUE-9183) [impala] Add unit test to the server module
* 40ec71638d [HUE-9180](https://issues.cloudera.org/browse/HUE-9180) [useradmin] Convert LDAP names to unicode to reduce length
* 642e7ffcab [HUE-9184](https://issues.cloudera.org/browse/HUE-9184) [editor] Fix js exception from the assist panel "open in editor" action
* e9d7e213f7 [HUE-9182](https://issues.cloudera.org/browse/HUE-9182) [assist] Show the context popover on hover in the assist panels
* ea37d07c17 [HUE-9182](https://issues.cloudera.org/browse/HUE-9182) [ui] Add a binding that triggers the context popover on hover
* 4e5227196a [HUE-9141](https://issues.cloudera.org/browse/HUE-9141) [frontend] Only show owner if other than the user in the document context popover
* b67efe98aa [HUE-9141](https://issues.cloudera.org/browse/HUE-9141) [frontend] Switch to modified from now time in the document context popover
* ec86bfe4d1 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [editor] Add postgresql to SQL samples
* bb51358888 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [sqlalchemy] Remove execution_options(stream_results=True)
* 96b12781c1 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Promote connector credentials parameterization
* 12024633a2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Avoid 500 error when opening a non existing saved query
* 312b6adcc9 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Remove windwill tests
* 40a7c43d7d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [jb] Avoid oozie related stack trace when oozie is blacklisted
* c8f3b208b3 [HUE-9183](https://issues.cloudera.org/browse/HUE-9183) [impala] Update hue to use kerberos principal to communicate with impala when either webserver_require_spnego or is_kerberos_enabled flag is on
* 03c7e4c476 PR1056 [editor] Support session properties for the SqlAlchemy connector (#1056)
* c058b051d0 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Update test to provide an execute status code
* 306b388e9a [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Admin are requivalent to superuser when flag off
* 46c674ae87 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [hive] Update use_sasl tests
* 7ec0de6515 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Add test to install_connector_examples API
* 83b30fa41b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Add install samples test with hive inserts
* 0d82c87b8e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Add install samples test via load with hive
* 8d0d75c4d2 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Add install samples via inserts with mysql test
* 48c59d7f42 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Port to suppor the make_logged_in_client test util
* 1710570568 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Inform the user from correctly installed or not samples
* 33a24c8abe [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [hive] Start adding the notion of dialect to simplify the logic
* 79bcbdf0d8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fix default use_sasl value for impala dialect
* 44d88b55f6 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [hive] Do not convert statement to bytes twice with Py3
* 7a251eb796 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Remove the notion of default organization
* 8f4beb5b01 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Simplify the user auth lookup attributes
* 3b929d25a6 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Fix Hive Server test connections
* 3bb43032fc [HUE-9162](https://issues.cloudera.org/browse/HUE-9162) [sqlalchemy] Avoid API error on data sampling popup
* 25e7b54ef1 [HUE-9162](https://issues.cloudera.org/browse/HUE-9162) [sqlalchemy] Do not fetch result on query without a resultset
* a8683ec696 [HUE-9150](https://issues.cloudera.org/browse/HUE-9150) [editor] Filter out tables not compatible with selected dialect
* b56ac362b1 [HUE-9150](https://issues.cloudera.org/browse/HUE-9150) [editor] Refresh the unit tests with latest APIs
* f341876611 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Replace notion of beeswax by hive in install examples
* b7b9be6307 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Add notion of dialects to sample tables
* 1b21a00b1b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Using editor API to install SQL samples
* ee29f226e3 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Supporting installing SQL query samples based on the dialect
* 4545fa717e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Add a test for check_status Notebook API
* afacea8ac2 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Refactor to move out the check_status call
* 9c26a0f421 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Add a skeleton of sync notebook api to submit a query
* 62542d842e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Refactoring for generic SQL samples queries
* e536660157 [HUE-9175](https://issues.cloudera.org/browse/HUE-9175) [core] Upgrade thrift-0.9.1 to thrift-0.13.0
* c605d8c172 [HUE-9175](https://issues.cloudera.org/browse/HUE-9175) [editor] Regenerate impala and hive thrift from 0.9 to 0.13 (#1053)
* 66509f1373 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Adding Re-using the JavaScript SQL Parser post
* 0ed92ba528 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding basic SQL autocomplete API
* cbfd175326 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Adding notion of quick query component
* 8eca90edbc [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [api] Documenting how to import parsers
* f38acada6e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [editor] Adding autocompleter npm plugin example
* ab00a62d6f [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [librdbms] Make jdbc plugin build fully off by default
* 6f6bf9b359 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [librdbms] Make the build of dbproxy.jar optional
* e5ff8c98a9 [HUE-9178](https://issues.cloudera.org/browse/HUE-9178) [autocomplete] Move implicit type conversion into sqlParseSupport
* 18eb09231e [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Add tests to the linkSharing component
* fc52e8084d [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Improve doc sharing modal layout and wording
* 3a80a06446 [HUE-9177](https://issues.cloudera.org/browse/HUE-9177) [doc] Fix issue where the user/group autocomplete doesn't initially show in the doc sharing modal
* 6117e5cf4f [HUE-9154](https://issues.cloudera.org/browse/HUE-9154) [aws] Move EC2 detection safeguard to proper section
* cfaf559f8b [HUE-9154](https://issues.cloudera.org/browse/HUE-9154) [aws] Turn off EC2 instance autodetection
* 9ebd5034c0 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Create a link sharing component and add it to the doc sharing modal
* 5a88c0cacf [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Clean up the document sharing component
* 9dd0b424ed [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Fix incorrect link sharing status after deactivation
* 877f5e96ba [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Add link sharing to the ApiHelper
* d0dc38224c [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Fix js exception when opening share modal for an already shared document
* aae98da735 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Move doc sharing view model into sharing component
* f9c8980bf1 [HUE-9166](https://issues.cloudera.org/browse/HUE-9166) [editor] Use the selected database in presentation mode
* 13fae08a1b [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [editor] Enable ctrl-enter execution in the quick query context
* 0395adca8d [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [editor] Prevent exception when executing an Impala query in editor v2
* 891f42bc19 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Fix issue with grayed out result after executing a hive query in editor v2
* 919fc710e4 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Create a simplified result grid for the quick query component
* 208a9b20a1 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [editor] Extract result tracking logic to the state handling utils
* d56c13123e [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [editor] Move common meta adaptions into executionResult
* 057f5e580a [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Improve layout in the quick query component
* 6327b27ad0 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Connect the executor to the quick query component
* daf62425b2 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Improve autocomplete logic in the simple ace editor
* ddb1552429 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Adjust the executor to support the quick query component
* 52e9f4198d [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Add interpreter and context selection to the quick query component
* 63649cd82e [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Create initial quick query component with an ace editor
* d76543c1e7 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Fix JS exception in the simple ace editor for editor v2
* e19524a1d5 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Add quick query action button component
* b16c74cdd6 [HUE-9143](https://issues.cloudera.org/browse/HUE-9143) [frontend] Extract templates for doc, udf and partition context popovers
* 60264e5893 [HUE-9165](https://issues.cloudera.org/browse/HUE-9165) [tool] Supported kerberos config when use hue on docker (#1051)
* dbc78f2bef [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactoring of the connector developer section
* 032b0fcb40 [HUE-9163](https://issues.cloudera.org/browse/HUE-9163) [core] Enable HUE image to be runnable in OpenShift environment (#1050)
* 0439fdba9a [HUE-9125](https://issues.cloudera.org/browse/HUE-9125) [liboozie] Avoid Error in config validation by liboozie
* abf1873a48 [HUE-9125](https://issues.cloudera.org/browse/HUE-9125) [core] Avoid unicode error in some config checks with Python 2
* 0d20d65532 [HUE-9150](https://issues.cloudera.org/browse/HUE-9150) [importer] Simplify SQL statement test comparison
* d27396d0ee [HUE-9150](https://issues.cloudera.org/browse/HUE-9150) [py3] Use OrderedDict to avoid non deterministic ordering in tests
* 4a996b591f [HUE-9150](https://issues.cloudera.org/browse/HUE-9150) [importer] First Mock test for TestSQLIndexer with file_to_csv
* effb727eea [HUE-9154](https://issues.cloudera.org/browse/HUE-9154) [ci] Comment why AWS EC2 IAM role auto detection is disabled
* 6bf9002097 [HUE-9154](https://issues.cloudera.org/browse/HUE-9154) [desktop] Small code formatting of lines too long
* 6a4eb789dc [HUE-9154](https://issues.cloudera.org/browse/HUE-9154) [ci] Disable AWS EC2 IAM role auto detection
* bf2aa97ff7 [HUE-9154](https://issues.cloudera.org/browse/HUE-9154) [aws] Flag to enable auto detection of IAM role on the EC2 instance
* 3519790327 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [ci] Adding additional check for Python 3.6
* 707ef83346 [HUE-9125](https://issues.cloudera.org/browse/HUE-9125) [core] Port dump config test to also work with Python 3
* ec67365087 [HUE-9153](https://issues.cloudera.org/browse/HUE-9153) [core] Avoid logging failure when data contains non unicode in REST resource lib
* 08cbff1f4c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [task] Reformating of the sql task code
* 2030f937aa [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Support editing a file in File Browser
* 14fd3dda9b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [fs] Light style refactoring and fixing non lazy translations
* 9e63a74e2f [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Upgrade some dependencies to avoid security warnings
* 2e0c120de5 [HUE-9149](https://issues.cloudera.org/browse/HUE-9149) [fb] Fist unit test with mock of an empty directory
* 5bc65013ef [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Wire-in the test connection API to the UI
* 91693a43ba [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Refactoring for connector connection testing
* 90f34cdb0a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Adding a test connector API
* ee8fd7638d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Moving the language choose to a footer flag (#1044)
* 07f69a6328 PR1045 [py3] Bump django from 1.11.20 to 1.11.28 in /desktop/core (#1045)
* a7afe21a5f [HUE-9148](https://issues.cloudera.org/browse/HUE-9148) [assist] Switch to using the config API in the DB assist panel
* 4a76e810f3 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Add more tests for check notebook config
* 9db92be3bc [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add user org filtering to User.objects.get API
* 4cf20dc958 [japanese] localized the blogs since Dec 2019
* 7424f0a018 [japanese] improved the localization of Japanese page
* 4eb6c40b18 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Do not assume any Hadoop configuration are set
* 86d3677c11 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fix TestCheckConfig suit and make it run all the time
* 7bea5497ab [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Provide connector name and dialect in config check
* 6ce5fa2cc8 [HUE-9146](https://issues.cloudera.org/browse/HUE-9146) [aws] Auto detection of EC2 instance if flaky
* a7150a383a [HUE-9146](https://issues.cloudera.org/browse/HUE-9146) [gc] Refactoring to restyle and avoid calling boto init lib
* 68544cb432 [HUE-9144](https://issues.cloudera.org/browse/HUE-9144) [jobbrowser] Data column which was present in Hue 3 is missing in Hue 4
* 172c665e98 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] #2 Series - The Hue SQL Editor Experience for your Data Warehouse
* f460c059ae [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add Presentation mode content
* 8ac8a38a5d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refactoring and update of the result refining content
* 2a08752d0a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix dead link in the contributing guide
* 4c7059f6ee [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [hive] Fix test suite and make it part of global test suite
* aa95e6e134 [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [hive] Light style refactoring while browsing over the logic
* 99edc12dc8 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Help about test run failing because of collect static
* 3e9e6617ed [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Move Connector section to the left of Hue config
* c0ef563f1a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Revamp the test suite to use real objects
* 04a9a794fd [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Do not load connectors with None interface
* 809adb5e11 [HUE-9141](https://issues.cloudera.org/browse/HUE-9141) [frontend] Improve description rendering in the document context popover
* a30b31cb40 [HUE-9141](https://issues.cloudera.org/browse/HUE-9141) [frontend] Add owner and modified data in the context popover footer for documents
* 5c48ac123a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [org] Adding beeswax DB migration
* 689f3568d4 [HUE-9140](https://issues.cloudera.org/browse/HUE-9140) [useradmin] Add ability to display isActive status
* 14fd95bb0e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Trigger the check config on initial page load
* 2e7dc9c3f0 [HUE-9139](https://issues.cloudera.org/browse/HUE-9139) [editor] Add statement parser support for escaped \ in quoted values
* aa0cc34d08 [HUE-9136](https://issues.cloudera.org/browse/HUE-9136) [scheduler] Fix arrow positioning when adding widgets with horizontal scroll
* fad4f2eadb [HUE-9136](https://issues.cloudera.org/browse/HUE-9136) [scheduler] Switch to flex layout in the workflow editor to keep the top actions visible on scroll
* b2de6ec101 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Document how to build the blog with multi language
* 7d086d9390 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Avoid hyphen in helm values
* 2a03e0aebe [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Updating gethue image build for multi language
* 94c795ab38 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Adding Japanese version of gethue
* b39f374d68 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Support for i18n and Japanese port (#1042)
* c727943327 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fix typo in install Hive examples
* 0debd5665e [HUE-9112](https://issues.cloudera.org/browse/HUE-9112) [lib] Protect against more unicode errors in REST logging
* 58f1aeca90 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Do not show the connector count when flag is off
* 9f4ad6fc5d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Adding migration when flag is on
* 5a1e98b9c5 [HUE-9131](https://issues.cloudera.org/browse/HUE-9131) [jb] Query browser does not load interfaces anymore
* 3e26b088da [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [core] Adding crequest to thridparty README
* 8a8b3d72b9 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fixes post rebase
* 65a4c38e36 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [editor] Link to add connector page when no snippet configured and admin
* f7fbdefc8c [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Update migration scripts part 2
* 407b12e8c5 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Update migration scripts part 1
* 39caa9600b [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Consolidate all the logic into the organization module
* 94dda0f280 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Install examples for the particular connector
* 8d17cfafc1 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] API to install data examples
* c450537e5f [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Port the Hive table sample install to kojs
* 5d0f32fe32 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Allow organization admin to install connector examples
* 7b4fdebdf3 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] API to install connector examples
* 5e72ac1c30 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Auto install example connectors for the Hue admin
* 6468dab6ce [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [useradmin] Properly display the organization page
* c6bb73d922 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [useradmin] Adding basic organization page
* fbf2dad8ff [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [auth] Fix some wrong styling indentation
* e0416464f2 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Patching for combining query set filter
* 2fec2c033c [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Make ORM filter chaining backward compatible
* ffbe9b2b47 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Backward compatibility for User.objects.values_list
* a74ce89ae2 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Properly create new users in the current  organization
* 6da571b558 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] List organization name when editing users and groups
* 92ae1cb61f [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Only list the group of the user organization
* adf6b00111 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Hide ensure home directory creation input for now
* 000172ce49 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Unify permissions for the admin wizard
* ca258d9418 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Hide ini location when user not a Hue admin
* 0f8656875a [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Prepare split of is_admin and is_hue_admin
* 6c1afc2c59 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Offer to safely blacklist the importer like a traditional app
* 0f33c41cd3 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Do not 403 when there is no snippet configured
* c2aa745b1f [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Try to log failed user login email if username is empty
* 3d93b6f647 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Fill-up the connector FK of a Permission
* 8d32f4394a [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Fix a series of bad imports
* 5ddf526516 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add org filtering to get document API
* 8a43497226 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add org filtering to get user API
* 1a466bba83 [HUE-9130](https://issues.cloudera.org/browse/HUE-9130) [about] Fix the update setting API and its test
* 0ff06f1118 [HUE-9130](https://issues.cloudera.org/browse/HUE-9130) [useradmin] Deactivate user by default instead of deleting
* 2a05b22914 [HUE-9130](https://issues.cloudera.org/browse/HUE-9130) [useradmin] Harmonize add user icons
* 8c4211d85e [HUE-9129](https://issues.cloudera.org/browse/HUE-9129) [useradmin] Remove threading locks
* f13b68f356 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Adding a test suite for is_admin
* c6d3a7ca6a [HUE-9129](https://issues.cloudera.org/browse/HUE-9129) [useradmin] Add a is_admin column to the list user page
* 9928284e28 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Fix rebasing issues
* 3a2dbe8164 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Avoid filtering querysets when off
* ddbecaefe1 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Avoid model instanciations when flag is off
* 9fea9fc11b [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Fix a series of bad imports
* f4a804df43 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [oganization] Update org DB migrations
* 828977d930 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Moving perms to a permission module
* bdbbae0c1d [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] filter_queryset backward compatibility when flag is off
* 2462535868 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Add DB migration for Connector model
* c30ee040fa [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Avoid dependency in organization when not in used
* fe107eb673 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Support Connector models via inheritance
* dea528ddb4 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Support permission persistence via FK
* e6155013b7 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Permission model pointing to a Connector
* f19b398d07 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Make numeric ids compatible with string matching
* f2257d6547 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Adding test for ORM compatibility
* e9e813e9ea [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Adding crequest module dependency
* 02ca81558c [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Check admin permission for connector updates
* b15dc5f378 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Remove more dictionary attributes in User constructor
* 0762291862 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Remove need of orm_user_lookup util
* ad1a93509f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Adding a is_admin auth decorator
* 3db939a2db [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Revert HuePermission creation to be simpler
* 5716e79079 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Refactoring to move out inter module dependencies
* 6d625bd47e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Refactor to switch to Hue permissions
* 5cea20d062 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [connectors] Unify the API for listing types and instances
* f15cda2197 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Series of typo fixes
* 63db68fb18 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [connectors] DB migrations in organization mode
* a906f8d2c3 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [connector] Persist connectors setting in the database
* 12b0a49b41 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Light restyling of the appmanager
* 3049e36839 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Auto add missing organization to Group and Permission
* 38739187a4 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [connector] Initial DB migrations
* ec58efa377 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Initial permission support
* d39dd5c5e6 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add org filtering to get document API
* bf3cba6daf [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add org filtering to Group manager
* d4cdc24380 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add org filtering to get user API
* 65c4850746 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Avoid infinite recursion when overriding User queryset
* 174562ddaa [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add proper default group to users
* 9afe4088a5 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Use full email for single user organizations
* e7248bdb43 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Builtin filtering of users within an org
* f10934d97a [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Allow connector page to be displayed
* d05d74385a [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Revert skipping desktop lib UI conversion
* 4c347cc76c [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Make user superuser only explicitly
* adce4f66ef [HUE-9125](https://issues.cloudera.org/browse/HUE-9125) [backend] Fix failing test related to configuration page changes
* 58c1dea2a1 [HUE-9127](https://issues.cloudera.org/browse/HUE-9127) [frontend] Add ability to set a custom dashboard app
* 68e70a6b96 [HUE-9125](https://issues.cloudera.org/browse/HUE-9125) [about] Create a component for the configuration page with filter
* f411ea14c0 [HUE-9125](https://issues.cloudera.org/browse/HUE-9125) [api] Add API endpoint for fetching the hue config in json
* 93fa7f8499 [HUE-9124](https://issues.cloudera.org/browse/HUE-9124) [frontend] Have the assist stay in the db list if it was visible prior to a refresh
* dfcc2b0671 [HUE-9117](https://issues.cloudera.org/browse/HUE-9117) [editor] Set the default SELECT limit to 5000 by default with 0 to disable
* 242d47e6df [HUE-9117](https://issues.cloudera.org/browse/HUE-9117) [editor] Persist default limit when saving snippets in editor v2
* d1fc1e032c [HUE-9117](https://issues.cloudera.org/browse/HUE-9117) [editor] Add config option to set default limit for SELECT statements
* f65625679c [HUE-9117](https://issues.cloudera.org/browse/HUE-9117) [editor] Add default limit input next to execute in editor v2
* 4f1ae8c15f PR1032 [jb] fix template error (#1032)
* def7150c15 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Fix the content not showing-up in Hue 4.0 post
* b1b8b122e1 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix the link pointing to CONTRIBUTING.md
* 1bd5703b43 [HUE-9128](https://issues.cloudera.org/browse/HUE-9128) [site] Upgrade GA js code
* 32cd1a0d03 PR1040 [spark] Set spark use_sasl flag dynamically (#1040)
* b91c599871  [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [beeswax] Fix unit test test_column_format_values_nulls
* 158f8cef52 [HUE-9128](https://issues.cloudera.org/browse/HUE-9128) [site] Update the GA id to propagate to blog posts
* 2db7701797 [HUE-9123](https://issues.cloudera.org/browse/HUE-9123) [hive] Create session can get stuck when the connector server address changes
* 86155d1503 [HUE-9122](https://issues.cloudera.org/browse/HUE-9122) [impala] Caching of impala job browser client can brake in HA
* 34699e09e2 [HUE-9128](https://issues.cloudera.org/browse/HUE-9128) [blog] 10 years of Data Platform Evolution
* 7109943d86 [HUE-9126](https://issues.cloudera.org/browse/HUE-9126) [docs] Move blog videos from Vimeo to Youtube (#1039)
* f9dbc61f4f [HUE-9089](https://issues.cloudera.org/browse/HUE-9089) [thrift] Fix e.message in py3
* 2c201186fe [HUE-9113](https://issues.cloudera.org/browse/HUE-9113) [hive] Show the view icon for materialized views in the left assist
* 8df3bcd2f7 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Grab connector id and use it as snippet type
* 296b9f8afe [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Pick-up connector name from POST data
* 1288d14ef9 [HUE-9120](https://issues.cloudera.org/browse/HUE-9120) [core] Light refactoring of the SQL session clossing on logout
* e798441630 [HUE-9121](https://issues.cloudera.org/browse/HUE-9121) [hbase] Handle HBase Thrift SPNEGO HTTP/hostname principal (#1037)
* 523f6a4e28 [HUE-9120](https://issues.cloudera.org/browse/HUE-9120) [core] Fix issue in Hue with closing impala session on logout
* 3bca8afb99 [HUE-8985](https://issues.cloudera.org/browse/HUE-8985) [core] Debug logging responses missing
* b095cb2486 [HUE-9118](https://issues.cloudera.org/browse/HUE-9118) [impala] INTEGER is introduced as a synonym for INT
* 69beb299e9 [HUE-9116](https://issues.cloudera.org/browse/HUE-9116) [hive] Check if destination empty before export data to hdfs
* c1fc72edb3 [HUE-9114](https://issues.cloudera.org/browse/HUE-9114) [frontend] Improve active marking of sidebar items
* 79bbcbc562 [HUE-9114](https://issues.cloudera.org/browse/HUE-9114) [frontend] Show sidebar user and help sub menus on hover
* cee94d9c35 [HUE-9114](https://issues.cloudera.org/browse/HUE-9114) [frontend] Improve left sidebar hover logic
* d6130a436d [HUE-9114](https://issues.cloudera.org/browse/HUE-9114) [frontend] Open left nav sub menus on hover
* 3248571896 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [frontend] Fix parser test utils exception when there are no keywords
* 6125870f66 [HUE-9115](https://issues.cloudera.org/browse/HUE-9115) [editor] Revert the flink parser to its originally cloned state to fix the failing tests
* e15a1c5c6b [HUE-9115](https://issues.cloudera.org/browse/HUE-9115) [editor] Re-generate the parsers based on current  state of the jison files
* bb1bf040f6 [HUE-9114](https://issues.cloudera.org/browse/HUE-9114) [frontend] Show the actual name of the favourite editor and not "Editor" in the editor sub menu
* 1bf1ea3568 [HUE-9115](https://issues.cloudera.org/browse/HUE-9115) [ksql] Fix test SHOW test suite
* 6def09324b [HUE-9115](https://issues.cloudera.org/browse/HUE-9115) [ksql] Move SHOW test suite to tests folder
* af1d17067a [HUE-9115](https://issues.cloudera.org/browse/HUE-9115) [ksql] Simplify grammar and remove 40 test failures
* eacb319483 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [calcite] Update generated parser
* d898f1c718 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [calcite] Adding support for SELECT STREAM
* d4396e66ac [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [calcite] Adding STREAM keyword to the lexer
* 5d215187c2 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [docs] Show how to run tests for parsers not in the CI
* 0ce290ae70 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [oozie] Fix Failed oozie unit tests in py3
* 84270c5352 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Converting last SQL dialects to connector types
* a5b095abad [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] First user or single user org as org admin
* 56b05cc00a [HUE-9112](https://issues.cloudera.org/browse/HUE-9112) [hdfs] Avoid potential log trace failure similarly to Resource
* a8e6a7a6ae [HUE-9112](https://issues.cloudera.org/browse/HUE-9112) [lib] Light restyling to avoid inconsitent long lines
* 3edbef9e0d [HUE-9112](https://issues.cloudera.org/browse/HUE-9112) [lib] Avoid unicode decode error in Resource logging
* c058746ea2 [HUE-9112](https://issues.cloudera.org/browse/HUE-9112) [fs] Better exception logging when an upload fails
* eb599909ef [HUE-9112](https://issues.cloudera.org/browse/HUE-9112) [lib] New basic test for Resource class
* e571cae3cb [HUE-9114](https://issues.cloudera.org/browse/HUE-9114) [frontend] Move the top quick action button with dropdown into left nav submenus
* c14f7f466b [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Use the dialect from the connector for autocomplete in editor v2
* 404854554e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Switch from type to connector/dialect in editor v2
* 4bfda743c5 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Move cluster config into webpack
* 5cc20c4efc [HUE-9113](https://issues.cloudera.org/browse/HUE-9113) [hive] Support listing SQL materialized views
* 944801dcfb [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Add calcite as connector dialect
* a75b35ce48 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [ksql] Pickup API url via the connector config
* 4fb98476d4 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Expanding the default SQL types
* bd6622eae7 [HUE-7474](https://issues.cloudera.org/browse/HUE-7474) [impala] Log query plan only in debug mode
* 2814e1ed02 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Make optional the interface used in connector configuration
* d7de4f5f87 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Adding elastic connector properties
* 3d719de968 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [sqlalchemy] Handle when column metadata if of Column type
* 653bcc0398 [HUE-9110](https://issues.cloudera.org/browse/HUE-9110) [oozie] Fix widget progress bar caused by PR798
* 6bc6e8228d [HUE-9111](https://issues.cloudera.org/browse/HUE-9111) [core] Light coding restyle of wsgiserver
* 34008e7881 [HUE-9111](https://issues.cloudera.org/browse/HUE-9111) [core] Light coding restyle of the file
* 7d2e0a0b1b [HUE-9111](https://issues.cloudera.org/browse/HUE-9111) [core] Simplify import of timeout pidfile compatibility
* 01217c389c [HUE-9111](https://issues.cloudera.org/browse/HUE-9111) [core] Fix typo in pidfile_context import
* 70bc31c9eb [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Unify get_organization function
* 492f887985 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Make logic of login error fields more explicit
* 944db9af44 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix desktop unit tests in py3
* 6195e21472 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [dashboard] Fix dashboard unit test in py3
* ee63cab8f7 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [notebook] Fix notebook unit test in py3
* 3f5b11633e [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [indexer] Fix indexer unit tests in py3
* e1c3faf803 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [rdbms] Fix rdbms unit tests in py3
* db72f9bfc4 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [useradmin] Fix useradmin unit tests in py3
* b45a6bc3b3 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [security] Fix security unit test in py3
* ee10b2eed2 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [search] Fix search unit tests in py3
* 70568e2bac [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix unit tests in pig and proxy for py3
* 2b4ea999b0 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Use explicit encoding open file to fix failed unit test in py3
* 1f717d68e3 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [oozie] Fix Oozie tests TestEditor for py3
* 7060796f1e [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [oozie] Fix Oozie tests TestDashboard for py3
* affe8bb672 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [jb] Fix job browser tests for py3
* 533a4bdcd7 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [beeswax] Fix beeswax and Impala tests for py3
* 7ef66615d0 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix desktop tests for py3
* dcd3303cc7 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [core] Fix desktop lib py3 issues   desktop.lib.django_util_test   desktop.lib.test_export_csvxls
* bded94ed86 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Point to dedicated migrations
* e3349fe89e [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organizations] Add migrations and patch Desktop prometheus Mixin base class
* d17fa8efef [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Proper error highlighting on login
* 91d6cab561 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Make logic of login error fields more explicit
* f8d9c69fab [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Do not try to monkeypatch the User username
* 31e30ed658 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Small Model update
* fa7854cb45 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Light style reformatting
* c8e2ed10a6 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Update tests and also fix bug in test login client
* 88a7936933 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Port make_logged_in_client util
* 330042741e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Adding postgres connector properties
* 7fbb926964 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Start adding the dialect properties to cluster get_config
* 1809d02d8d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Show to how run single test file in parser guide
* 7b9d10836e [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Make grammar
* eb107da652 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding udf and aggregates to the grammar
* a3984b5a9f [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Adding reserved keywords to grammar
* 5848e55bec [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh the dev testing section
* a57979f50e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh the high level architecture diagram
* 0fc591b43d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh install README and update syncdb references
* 1724551b0b PR1029 [docs] Fix tools/kubernetes link typo (#1029)
* 48ae788d4a PR1028 [docs] Presto isn't Apache Project (#1028)
* 398aba98c6 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Skip test to avoid deleting old perms for now
* 4d4de70bca [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [wizard] Properly link to gethue website
* 265c6b3e28 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Port check config to support sqlalchemy interface
* 7d70f9d132 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Port check config to support hiveserver2 interface
* 724937f2d6 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Preparing config check for connectors
* 8798b32891 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Combine app permissions with connector permissions
* 3f48b27a77 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [auth] Clean-up config imports to be explicit in middleware module
* 54abb85c82 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Sync permissions when updating connectors
* 30abb5aab7 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add the notion of organization admin
* 7665990e55 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Prepare the DB model
* 9f1559e6f5 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] Properly handle SELECT that fails
* a55df7db4b [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [connector] Add column listing to ksql autocomplete
* e3cb042671 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [ksql] List topics, tables, streams in the left assist
* c4623cf3cd [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Avoid tests deleting traditional permissions for now
* b48c976b34 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Configure some tests to be able to run on master
* d0216b3361 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [auth] Update test_get_profile to be more robust
* 4cbdcf0f93 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add permission to connector listing
* 3a0d4f9118 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Cleaner logic for removig old connector perms
* 369675a3e1 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Display the name of the connector in the permissions
* 2f1b40bc60 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Port group_has_permission resultset check to exists()
* e474cd2c7f [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Little line style formatting
* 69e109fe99 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Simplify the titles of the app
* 82af732bdf [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Sync permissions when updating connectors
* 829020c9d7 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Add permissions for available connector instances
* 41db606f20 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Small styling updates in useradmin and desktop
* 92d7327f68 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Add the notion of organization admin
* df8b13ae70 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Prepare the DB model
* 8661c1e064 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [auth] Also augment the user with some of the profile properties
* e7cfd58d5d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [auth] Persist the backend used by the user when logging-in
* 9dbfa67baf [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Add test to uderprofile data field
* 207d09b1ed [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [useradmin] Adding custom data field to user profile
* 31839a2c58 [HUE-8530](https://issues.cloudera.org/browse/HUE-8530) [organization] Refactor to not hardcode user attribute lookup
* 6231742eb0 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Avoid 500 on page opening when not in dev mode
* ebd78772ca [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [auth] Style formatting of the views and user
* fd2455deb0 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connector] Rename Documents to Queries when connectors are enabled
* 70633f24d8 [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [core] Add query icon
* 790fe6456c [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [ui] Harmonize the file and table icons to be consistent
* d84d04110f [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [ui] Base sidebar home link properties with cluster config API
* 8ab4c4010d [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Moving connector types to its own module
* 9e7b4e255e [HUE-8758](https://issues.cloudera.org/browse/HUE-8758) [connectors] Offer to white/black list available connector types
* 1c884ccd8e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Upgrade hugo version to fix table display issue
* 227be01247 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Link to list of SQL connectors in the dev parser section
* 1f55c1e1fa [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Add analytics to gethue
* 85e94a8422 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Clarify about the upstream distribution install
* c8b087cd92 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Refresh of the configuration and operation sections
* 644b5bc7b1 [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [editor] Reuse session when opening notebook
* 10cdfc2cca [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [editor] Close dangling sessions
* 9247744d1c [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [editor] Delay execute until session create is completed
* 1797ecc88d [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [editor] Update session after execute
* bb0a842df7 [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [beeswax] Multi-session support
* 7be0e36bdc [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Update README about distributions shipping Hue
* fae76907ce [HUE-9106](https://issues.cloudera.org/browse/HUE-9106) [core] Compare Python version by tuple and not string
* 325639e22a [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [frontend] Prevent history panel from opening gist links
* ecba66299e [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [frontend] Improve gist sharing layout
* 2d4decb517 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [frontend] Prevent password managers affecting the gist link
* 0189da2079 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [frontend] Create a separate component for the gist modal
* 9496dee329 [HUE-9109](https://issues.cloudera.org/browse/HUE-9109) [editor] Switch to index-based tracking of executables in editor v2
* 9b3f2df643 [HUE-9107](https://issues.cloudera.org/browse/HUE-9107) [editor] Reuse existing executables in presentation mode for editor v2
* c5fb9b41af [HUE-9107](https://issues.cloudera.org/browse/HUE-9107) [editor] Fix history update after existing presentation mode in editor v2
* e7c367f518 [HUE-9107](https://issues.cloudera.org/browse/HUE-9107) [editor] Fix JS exception when entering presentation mode
* 2ed6fae0e6 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [knox] Enable XHR URL rewrite only if Knox is there
* eb38ea0d0a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Fix last set of links pointing to old latest
* 59565ca728 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Fix links to quickstart documentation
* 2c7fb20024 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Wire the link sharing on and off calls in the modal
* b34cf8499f [HUE-9103](https://issues.cloudera.org/browse/HUE-9103) [core] set settings.LOGGING_CONFIG to None
* 29ee0b05ed [HUE-9108](https://issues.cloudera.org/browse/HUE-9108) [core] Revert prettify unifying the general log level
* f50511054a [HUE-9106](https://issues.cloudera.org/browse/HUE-9106) [core] Add SSL_NO_RENEGOCIATION option
* 6652e152a2 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [hive] Skip warehouse path config check when no FS configured
* 6c4ecb79fc [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Ini description about backends is outdated
* d1a0ac8e7f [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Update the Ace Hive highligher with the latest keywords
* b37c442b6d [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Fix out-of-sync ksql highlighter
* 132e881d46 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Add missing options to the Hive EXPLAIN grammar
* b0c1815872 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Extend the Hive parser ORDER BY clause
* fd11736eef [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Extend the Hive LOAD statement syntax in the parser
* 8ceb7843d5 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Add parser support for Hive SHOW MATERIALIZED VIEW
* 4590099e79 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Add parser support for Hive ALTER MATERIALIZED VIEW
* aa9158d220 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Add parser support for Hive DROP MATERIALIZED VIEW
* d7ef03a478 [HUE-9089](https://issues.cloudera.org/browse/HUE-9089) [editor] Allow manual close_statement even if CLOSE_QUERIES is false.
* bd544cf6bb [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [gist] Adding initial test suite
* 6f8ed0d362 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [gist] Optional public gist link unfurling
* b9494aa40a [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [gethue] Fix list styling issues in blog conflicting with top menu
* 7a7aaf313e Revert "[HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Avoid huge font on second levels of lists"
* 5bf4cc6d2d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [blog] Aggregate together more catagories
* d003c151cd [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Adding hive sqlalchemy connector to base image
* 17262a313c [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Test update and prettify printing Permission objects
* 01437e3b36 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Avoid fail on document deletion when there is no FS configured
* d1c2147afa [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Wire the link sharing API to the permission modal
* b09b3f19d2 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Display link perms in the sharing modal
* be8206b46a [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Update HueFileEntry js model permission logic
* d24cfe1a19 [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Integrate top level READ and WRITE permissions
* e98ab0597d [HUE-9096](https://issues.cloudera.org/browse/HUE-9096) [doc] Optimize a little perm checking logic order
* f5b6b9c92f [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Logo and main screenshot are reversed in the README
* e44eeafbff [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [core] Adding a bunch of missing files
* 71b47c0f7d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Update main screenshot with 4.6 version
* 4c299a7820 [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Create a separate component for the saved queries tab in editor v2
* fb9a5c557a [HUE-8727](https://issues.cloudera.org/browse/HUE-8727) [frontend] Consolidate Chrome autofill prevention attributes into a global variable
* 0f35eee78b [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [frontend] Allow observables in the ko.ellipsis binding
* 1c2491e517 [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Extract common paginator component
* fa1a85c442 [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Move the import and export actions into the new history component
* dd6e5307cc [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Refresh the history after execution in notebook 2
* b4b8e1c8a0 [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Move clear history logic into the new history component
* 8da347825d [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Move history search into the query history panel
* f8a5930783 [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Create generic snippet tab styles
* 54d9a443fe [HUE-9101](https://issues.cloudera.org/browse/HUE-9101) [editor] Extract the query history to a contained component for editor v2
* d2955f791e [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Prevent error message on history status checks
* 119306aac8 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Add parser support for Hive CREATE MATERIALIZED VIEW
* c82f1d4c93 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Extend the Hive parser MSCK syntax
* d55d9a1034 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Add new table constraints to Hive ALTER and CREATE statements
* 292e6be694 [HUE-9099](https://issues.cloudera.org/browse/HUE-9099) [frontend] Add column constraints to Hive ALTER and CREATE statements
* 96801be962 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [docs] Add details on running specific js test files to the docs
* b17c9a98a8 [HUE-9090](https://issues.cloudera.org/browse/HUE-9090) [frontend] Fix exceptions in parser related test utils
* 96d41105a3 [HUE-9100](https://issues.cloudera.org/browse/HUE-9100) [hive] Adding a set of tests to the hiveserver2 lib
* 357f25e907 [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Lazily create user gist directory
* 4bbd6bff29 [HUE-9098](https://issues.cloudera.org/browse/HUE-9098) [docs] Fix mistake about points in administrator documentation
* 7597e2255e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [connectors] Move template to absolute path in desktop
* 7739245a82 HUE 9096 [doc] Add a feature flag to link sharing
* bf5d432d19 HUE 9096 [share] Raw template skeleton of link sharing
* 6f446c6faf [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Avoid huge font on second levels of lists
* 8b8a7ac420 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docs] Hide reference to direct IP to cdn
* ba527089b4 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Still use NodePort for now for website services
* 81811d5c0c [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding Apache Flink parser skeleton
* bcfb0389bb [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [ace] Adding latest languages files
* 1a5d4c6acc [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [editor] Adding highlighter skeleton to Flink SQL
* bc032d9737 [HUE-9084](https://issues.cloudera.org/browse/HUE-9084) [notebook] Adding a skeleton of Flink SQL interpreter
* 31140f24fd [HUE-9066](https://issues.cloudera.org/browse/HUE-9066) [gist] Add a feature flag off for now
* 1077441e60 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Port DB from replicationcontroller to deployment
* 7761991010 [HUE-9077](https://issues.cloudera.org/browse/HUE-9077) [connector] Protect boot against when no fs is configured
* f54990e64e [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Add checksum of config for helm upgrade hue pod restart
* 0c0d05820b [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Simplify NOTES.txt of helm chart
* 4bb746da2d [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Add additional potential auth via ingress
* 26fe7ecd55 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Adding missing resource requirement for nginx and postgres
* d6db2e5db3 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Harmonize TLS certificates generation
* 29c56307c6 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Avoid hardcoding the storage of PostGreSQL PV
* 98f4e962ae [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Update the cert annotation for the website ingress
* e6e1692ac5 [HUE-9064](https://issues.cloudera.org/browse/HUE-9064) [editor] Skeleton of sending back live query results via WS
* 5a5431893b PR1009 [oozie] Added the ability to filter workflows against id: and name: parameters (#1009)
* 0d6bbec088 [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [py3] Fix useradmin and libs unit tests and fix urllib import in mako   liboozie.tests.test_config_gen   liboozie.tests.test_config_gen_negative   librdbms.tests.TestDatabasePasswordConfig.test_read_password_from_script   libsaml.tests.test_xmlsec_dynamic_default_no_which   useradmin.tests
* 467955164b [HUE-8737](https://issues.cloudera.org/browse/HUE-8737) [hdfs] Fix webhdfs unit tests in py3   test_with_core_site (azure.tests.TestAzureAbfs)   test_with_credentials (azure.tests.TestAzureAbfs)   test_with_core_site (azure.tests.TestAzureAdl)   test_with_credentials (azure.tests.TestAzureAdl)   hadoop.tests.test_tricky_confparse   hadoop.tests.test_config_validator_basic
* bc27235408 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Fix the website service ports
* 8899b9d38c [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Adding CPU limits to the website deployments
* dacdc5bad0 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [docker] Adding website image building
* bfeec59e71 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [k8s] Fix spacing in website ingress with two domains
* bb7c8828c6 [HUE-8888](https://issues.cloudera.org/browse/HUE-8888) [connector] Avoid stack trace when Oozie is disabled
* 17b5fa7ea6 [HUE-9097](https://issues.cloudera.org/browse/HUE-9097) [frontend] Limit webpack chunk name length to less than 128 chars
* b0722bfb4d [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Have the column selection stick to top of window when scrolling the results
* 50214498e7 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [frontend] Unify result status messages in one component
* f0cf0df20c [HUE-9088](https://issues.cloudera.org/browse/HUE-9088) [frontend] Fix no default export warning after ko upgrade
* 217792fb92 [HUE-9000](https://issues.cloudera.org/browse/HUE-9000) [editor] Properly position result headers after query tab switching
* a2aae7041d [gethue] Add highlight.js and port all the highlights to it, fix the list styling
* 93d1151ed2 [HUE-9095](https://issues.cloudera.org/browse/HUE-9095) [docs] Perform release 4.6

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
* Ajay Jadhav
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
* Eli Collins
* Emmanuel Bessah
* Enrico Berti
* Eric Chen
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
* Luca Natali
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
* z00484332
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
