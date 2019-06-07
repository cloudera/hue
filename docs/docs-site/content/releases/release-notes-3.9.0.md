---
title: "3.9.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -3090
tags: ['skipIndexing']
---

### Hue v3.9.0, released August 7th 2015


Hue, http://gethue.com, is an open source Web UI for easily doing Big Data analysis with Hadoop.

Its main features:

* Editors for Hive, Impala, Spark and Pig
* Search Dashboards for querying, exploring, visualizing data with Solr
* Hadoop File, Job and HBase Browsers

On top of that, a SDK is available for creating new apps integrated with Hadoop.

More user and developer documentation is available at http://gethue.com.


Latest Notable Features
-----------------------

The complete list and video demos are on [Hue 3.9 with some general overall improvements is out!
](http://gethue.com/hue-3-9-with-all-its-improvements-is-out/).


Spark

* Revamp of Notebook UI
* Support for closing session and specifying Spark properties
* Support for Spark 1.3, 1.4, 1.5
* Impersonation with YARN
* Support for R shell
* Support for submitting jars or python apps

Search

* Live filtering when moving on the map
* Refresh only widgets that changed, Live refresh every N seconds
* Edit document
* Link to original document
* Export/import saved dashboards
* Share dashboards
* Save and reload the full query search definition
* Fixed or rolling time window filtering
* Marker clustering on Leaflet Map widget
* Support 2-letter country code in gradient map widget
* Better date range wording
* Full mode Player display
* Simpler Mustache integration
* Big IDs support
* Preview of nested analytics facets

Stability/performance

* Fix deadlock fetching Thrift clients and waiting for Thrift connections
* New set of integrations tests
* Add optional /desktop/debug/check_config JSON response
* MariaDB support
* Configuration check to confirm that MySql engine is InnoDB
* Faster Home page
* Series of Oracles and DB migration fixes

Security

* Explicitly set cipher list to Mozilla recommendation
* Fix uploading large files to a kerberized HTTPFS
* Set X-Frame-Options to all responses
* Support multiple authentication backends in order of priority
* Add global ssl_validate config option
* Default to using secure session cookies if HTTPS is enabled

SQL

* Table / column statistics and Top terms available in assist
* Select 'default' as first assist database if available
* Offer to filter partition on the list of partitions page
* Partitions names and links are now always correct
* Integrate table and column stats
* Allow sample on partitioned tables in strict mode

HBase

* Upload binary into cells
* Allow to empty a cell

Sentry

* Better support of URI scope privilege
* Support COLUMN scope privilege for finer grain permissions on tables
* Support HA
* Easier navigation between sections
* Support new sentry.hdfs.integration.path.prefixes hdfs-site.xml property

Indexer

* Directly upload configurations without requiring the solrctl command

ZooKeeper

* Creation of a lib for easily pulling or editing ZooKeeper information

Oozie

* Filter dashboard jobs in the backend
* Integrate the import/export of Workflows, Coordinators and Bundles
* Paginate Coordinator dashboard tables
* Paginate coordinator actions
* Update end time of running coordinator
* Series of improvements to the Editor

Pig

* Support %default parameters in the submission popup
* Do not show %declare parameters in the submission popup
* Automatically generate hcat auth credentials

Sqoop

* Support Kerberos authentication


Compatibility
-------------

Runs on CentOS versions 5 to 6, Red Hat Enterprise Linux (RHEL 5 and 6), and Ubuntu 10.04, 12.04 and 14.04.

Tested with CDH5. Specifically:

- Hadoop 0.20 / 2.6.0
- Hive 1.1
- Oozie 4.1
- HBase 1.0
- Pig 0.12
- Impala 2.2
- Solr 4.10
- Sqoop2 1.99.5
- Spark 1.3, 1.4, 1.5

These minimum versions should work (not tested):

- Hadoop 0.20 / 1.2.0 / 2.0.0
- Hive 0.12.0
- Oozie 3.2
- HBase 0.92
- Pig 0.8
- Impala 1.0
- Solr 3.6
- Sqoop2 1.99.3

Supported Browsers:

Hue works with the two most recent versions of the following browsers. Make sure cookies and JavaScript are turned on for the browser.

* Chrome
* Firefox LTS
* Safari (not supported on Windows)
* Internet Explorer

Hue might work with Chrome 23, Firefox 23, IE8, Safari 6, or older browser version, but you might not be able to use all of the features.


Runs with Python 2.6.5+

Note: CentOS 5 and RHEL 5 requires EPEL python 2.6 package.


List of 723 Commits
-------------------

* c46bdca [doc] Adding release notes for 3.9
* c13c9e4 [spark] Redraw tables fixed headers on editor size change
* ae91b36 [spark] Avoid rapid consecutive execution of snippets
* 1d151a7 [oozie] Skip test importing a complex decision node in v1
* d5c952d HUE-2885 [oozie] Java options java-opts not generated correctly in XML
* b0a6586 [oozie] Upgrade old versions of sqoop nodes
* a52c896 [livy] Update the docs to reflect renaming "lang" to "kind"
* 7b0a4bc HUE-2831 [livy] Don't report a connection error when killing a session
* 7c1a33a [beeswax] Add better error messages to some of the tests
* 243c700 HUE-2865 [livy] Mark session as errored if session process died
* 907c510 HUE-2882 [oozie] Fix parsing error when workflow job uses Australian timezone
* 9e06fdd [beeswax] Import is_live_cluster into beeswax.tests
* dbb8552 [beeswax] Fix issue where beeswax autocomplete on nested types errors on MySQL-backed Hive metastore
* c719465 [beeswax] Report a better error if beeswax autocomplete failed
* 4b9dee3 [beeswax] Raise an exception if the beeswax query failed
* 399e85f [beeswax] Skip beeswax utf8 tests on live cluster
* 1eed885 [spark] Adjust the length of the snippet names for the radial menu
* 42c7343 [spark] Put grid and chart buttons next to execute
* 31cd07d [spark] Don't show progress bar when there's no progress in IE
* e723ea6 [spark] Improved add snippet UX
* f29efd0 [spark] Defer createSession to allow Ace to load properly the highlighters
* bf753b7 [spark] Add support for R snippet
* d026311 [search] Fix error on the query fields after a definition unload
* 859975e [oozie] Set workflow validation to field blur instead
* c19478b [oozie] Extend workflow validation to hidden properties too
* 7b00745 [search] Avoid Leaflet error on popups after search
* dfe05d9 [search] Support highlighting on records with ids containing binary values
* 9d00c53 [core] Help logging the REST calls to other services
* 088530e [impala] Add a test for checking cancel_query
* 030fc26 [impala] Remove old way to run integration tests
* cb92a35 HUE-2883 [impala] Canceling a query shows an error message
* 5bd1b67 HUE-2850 [jb] Check that Spark Jobs 1.4+ can be viewed
* a46d5c9 [useradmin] Update test_user_admin to not assume the user.id is `1`
* bc2f0ac [indexer] dateutil.parse only throws ValueError or OverflowError
* 8c110ad [indexer] Raise error if failed to create indexer collection
* f867dc0 [search] Removed the 'no data' visibility check for Leaflet
* ee37b90 [search] Improved UX of region change on zoom event
* c07de1b [search] Improved UX of the region change event
* 27512c1 [search] AND lat/long coordinates on the Marker Map
* 4177e47 [search] Offer only matching field types for Marker Map
* ea2d7ab [search] Add ZoomBox plugin
* 66755df [search] Backend for marker map filtering
* 6876e4a [search] Added region change event to the map
* 29160dd [indexer] Make sure fields types used in tests are valid
* 431556f HUE-2864 [livy] Correct the "sparkR" executable for case sensitive filesystems
* fa7e8d7 [spark] Clone the initial values in the ko csv input component
* 58b1882 [spark] Drop horizontal resize and positioning of snippets
* 03de03e [spark] Add the hover actions to the text snippet
* 96a78ad [spark] Add confirmation modal for snippet removal
* c720f3c [spark] Fix snippet type switch
* 0152e8c [spark] Always show the change snippet type dropdown
* b730df4 [livy] Update spark version checker to be more liberal on version numbers
* f58bd95 HUE-2864 [livy] Allow sparkr sessions to be launched from yarn
* 219c6ee [spark] Add a R snippet type
* a67b68d [oozie] Skip prepare values that are empty when generating XML of an action
* 60095c9 [livy] Add licences to the script headers
* b6d6bb8 HUE-2864 [livy] Strip out ASCI color codes from the R output
* 13aab92 HUE-2864 [livy] Capture stderr in separate thread and mix it in later
* 673e676 HUE-2864 [livy] Initial support for sparkr interactive sessions
* 6f86bb2 [livy] Factor out running a session interpreter from PythonInterpreter
* f36060c HUE-2874 [metastore] Sorting the partition list in ascending order doesn't update target links
* 297ffbf HUE-2855 [oozie] Show error on dashboard when server is down
* 8f6131a [spark] Use the HDFS file chooser for file-related session and snippet properties
* f2f3e0d [spark] Improve the result action buttons bar
* 7dce759 [spark] Fix snippet button positioning while executing the snippet
* 7600826 [useradmin] Make user/group autocomplete result sorted, handle unicode in tests
* 6903d54 HUE-2881 [oozie] A fork can point to a deleted node
* 28dbc07 [core] Updated the list of available tours
* 4370a62 [core] Add ko binding for log auto scroller
* 1396378 [spark] Add shift-click support to select a range of notebooks
* 1a10061 [tests] Change order of packages, traverse namespace, and restrict nose from changing sys path
* 892ceba [tests] Limit test coverage report to Hue and desktop apps
* 2598468 [search] Extend bigdataParse to other functions too
* 9126db1 [livy] Simplify the SPARK_HOME docs
* bf71176 HUE-2853 [livy] Ignore the "spark-submit --version" exit code
* 8cf5ec6 HUE-2853 [livy] Update Livy to work with Spark 1.5
* ae34f65 [livy] Fix a deadlock if the python interpreter thread dies unexpectedly
* 0e7ac15 [livy] Synchronize the spark interpreter when shutting down
* 7186a41 [livy] Minor cleanup
* 0d0cf3c [search] Fix for a parse problem with a generalized JSON.bigdataParse approach
* c224ded HUE-2727 [spark] Fix session restart
* 174f97c [oozie] Remove deprecated tests from v1
* d2620f6 [desktop] Explicitly set cipher list to Mozilla recommendation
* 09dbfcb [desktop] Improve printing of runcherrypyserver options
* a4ae3d3 [load-balancer] Pass the Host and X-Forwarded-For headers from nginx to Hue
* e0f3797 [desktop] Stop DEBUG logging from connectionpool
* 41c5a00 Revert "HUE-2870 [libsolr] Protect against precision issues with large ids"
* be1b69c HUE-2870 [libsolr] Protect against precision issues with large ids
* bc2db4e HUE-2880 [hadoop] Fix uploading large files to a kerberized HTTPFS
* 3f87c1d [beeswax] Raise QueryServerTimeoutException and rely on error_handler in beeswax API
* 977bd94 [beeswax] Avoid Assist infinite loop on server timeout
* a6bb39f [beeswax] Raise QueryServerException on timeout in execute_and_wait, and handle
* 9add49f [oozie] Try to offer a workflow dashboard graph even if submitted from CLI
* ce2866a HUE-2857 [search] Only allow admin to edit the index for now
* 55d0912 HUE-2875 [useradmin] Disable Edit Profile page details when backend is LDAP
* 663ab26 HUE-2873 [oozie] Handle TransactionManagementError on workflow dashboard
* 3ae11c7 [spark] Close a session even if it has expired
* e0d6164 [search] Remove unused view
* 2a6ad96 HUE-2857 [search] Fix document loading problem with big IDs from Solr
* 1e084c2 HUE-2857 [search] Changed icon style on HTML results and fixed zebra striping
* 6e05e67 HUE-2857 [search] Details of the document in the HTML layout
* a01cdfa HUE-2857 [search] Better UX for the document update form
* 41f231b HUE-2199 [search] Link to original document in gridlayout
* 4da308a HUE-2857 [search] Update selected document in the index
* f6624f4 [core] Removed Ace gutter, set min and max lines, removed print margins
* efd7d84 [core] Add custom 403 and CSRF view
* a315d60 [fb] Hide the submit buttons in case Oozie is blacklisted
* 83da765 [fb] Enable the Oozie app to be blacklisted without breaking
* b1bbe8a HUE-2868 [hbase] Allow multiple cell edits
* 6125eb1 [beeswax] Avoid screen blinking on page load
* df69057 [spark] Load common JS before binding the KO viewmodel
* 5b779e0 [core] Fetch terms on demand in the assist panel
* 10e853d HUE-2868 [hbase] Fix cell upload
* d248904 [core] Update minified Ace ext-language-tools
* 99a6d71 HUE-2727 [spark] Style the session properties
* b0fbc17 [core] Temporary fix for issue with Deferred Updates plugin
* ad2d929 HUE-2727 [spark] Create templates for spark properties
* 03ebde7 [core] Add csv list input ko component
* 3f04157 HUE-2727 [spark] Use the correct attributes for the snippet settings
* e73eaec [desktop] Suppress kazoo.client DEBUG messages by default
* 299a509 [hive] Quoting database in the SQL of the create table wizard
* 8fd9e95 [hive] Add quoting when doing a "use" database
* 025205c [core] Update FontAwesome to 4.4
* 38d4212 [core] Disable username autocomplete on the login form
* 1d305fe [spark] Move function to fix editor page
* 48e3331 [core] Removing original test file taken from txzookeeper by kazoo
* aaecada [core] Set X-Frame-Options to all responses
* 94f9510 [core] Add 'show' snippets to the Hive autocomplete
* ab2963d [spark] Hide Ace autocomplete on window scroll
* aee2e60 [core] The Hive/Impala field autocomplete works also when the list of fields is not cached
* fd007c2 [sentry] Fix show role link and add tooltip to db, table and column links
* 151d8ec [spark] Add link to Metastore in the table preview
* 8f0565f [spark] Show header as sortable helper in Firefox
* db76821 [core] Add prefix search to column statistics in the assist component
* 8a6b278 [core] Add refresh functionality to assist panel
* a980fc9 [spark] Assist panel size adjustments
* 317c6aa [spark] Fix css class conflict
* f9ba4d8 [auth] Fix Spnego auth middleware check
* 98191e6 [auth] Support multiple authentication backends in order of priority
* 6b3e3a8 [libsentry] Switch to V2 of the Sentry API
* 6e167aa HUE-2862 [hbase] Allow to empty a cell
* b5b4397 [sentry] Error early if the listing privileges by authorizable call fails
* cd0bd2a [core] Format config to be simpler to read
* 248ab12 [core] Make coerce_password_from_script compatible with Python 2.6
* f1ff822 [core] Add missing keywords to the Ace Scala autocompleter
* 397c19d [core] Magic table autocomplete on Ace now behaves like Codemirror
* ee1fe0b [spark] Fix and style the snippet sortable
* 6f63187 [spark] Do not enforce result table height
* 21932c9 [spark] Add absolute positioning to table header extender
* 590328c [spark] Fix left-panel and result-settings style conflicts
* ee7bc21 [spark] Style the snippet actions the same the assist actions
* eeab27b [core] Add table and column stats to assist component
* f03b79c [spark] Improve assist icon appearance
* a4cae9b [core] Improve panel resizing
* 1d75e48 [beeswax] Fix positioning of column stats pop-over
* 41d8d2a [useradmin] Modify useradmin ldap tests now that AssertionErrors are caught in the inner _import_ldap_users_info method
* 52f248c [libzookeeper] Make sure that ensemble list is converted to a string
* b041329 [spark] Make the Example work with the new sessions
* 3ed927a [spark] Rename API close() to close_statement()
* 5e704d5 [spark] Move createSession() to the Notebook class
* c0ba443 [spark] Add session properties to all types of snippets
* 8ec5cca [spark] Make session properties generic
* db4dc66 [spark] Edit session properties
* 8bd15fd [spark] Add a close session call
* 3f561bd [useradmin] Raise warning and continue on errors in batch LDAP user import/sync
* 3ea358b [indexer] Fix typo in log_analytics_demo core
* 40440b0 [desktop] Replace invalid unicode errors when downloading log files
* 9d5fb39 [desktop] Usernames have a max length of 30
* f920be0 [desktop] Make login tests re-entrant and have queries return in a consistent order
* 0051d9b [libsolr] Fix live cluster test
* e1090d9 [liboozie] Fix live cluster tests on cluster without MR1
* cbc17a7 [hadoop] Fix hadoop tests on live cluster without MR1
* 0371c9e [desktop,librdbms] Simplify password tests, fix librdms password test
* d55a2a8 [spark] Fix JS error on second execute
* 0963c90 [spark] Enable ctrl-enter for execution from ace editors
* c896ee4 [spark] Fix session close button position
* 002e5a4 [spark] Make it easier to resize the panels
* 46f8832 [core] Save all assist options as one variable in total storage
* 0e02a58 [spark] Move left panel toggle out of assist component
* bdc3f15 [desktop] Capture the stderr if the password script has an error
* 6518f82 [desktop] @nottest is no longer necessary
* d4bbbf3 [desktop] Add test for blank passwords
* 42d3f82 Merge pull request #211 from orenmazor/master
* 9912d77 [sentry] Do not offer to edit privilege scope
* 51824b9 if there is no lastAction (i.e. the job hasnt even run yet), return 0. because progress is 0.
* 7906224 [desktop] Change hadoop and oozie to use global ssl validate default
* 8eb3249 [desktop] Add global ssl_validate config option
* 274f9fc [desktop] Set the REQUESTS_CA_BUNDLE environment variable if SSL_CACERTS is configured
* 908e6b5 [desktop] Add global ssl_cacerts config option
* 26d9545 [desktop] Fix another deadlock fetching thrift clients
* 3069684 [desktop] Simplify creating DESKTOP_DB_TEST_NAME
* f967ab4 [metastore] Show error message when table is created without Sentry privileges
* 91eb980 [spark] Put back the add snippet panel
* 64b0ac6 [beeswax] Fix table statistics positioning
* 08bf80b [spark] Style the assist panel
* a16ba45 [spark] Keep left panel fixed on resize
* 5cc1471 [core] Remember last selected DB in assist
* 22ddc8b [core] Select "default" database by default in the assist panel
* caf68f5 [desktop] Optionally parse the test database name from the environment
* 75f3938 [search] Support for pseudo-fullscreen Search dashboards
* 2e37eab [spark] Extract common code to an external file
* af642e2 [desktop] Remove an unneeded warning
* b8fd297 [libzookeeper] Only lookup zkensemble from zookeeper/search if app is enabled
* f2d128a [spark] Expand right panel when the left one is hidden
* 4c87d2e [spark] Fix stale merge conflict on Assist
* 7f67480 [spark] Integrate AceEditor
* fbf99fb [core] Improved AceEditor autocomplete
* ebaefe7 [core] Add ace.autocomplete.js
* ff64b1d [core] Implemented getAfterCursor and handler for keydown on AceEditor
* 409f849 [core] Extended support for AceEditor
* e209461 [spark] Open notebook instead of editor when notebook parameter is present
* cdf038e [rdbms] Use pixel widths and positioning for the panels
* b75d8a2 [beeswax] Use pixel widths and positioning for the panels
* a12d006 [spark] Use pixel widths and positioning for the panels
* 6bdd3e4 [core] Switch to pixel widths for ko splitDraggable
* dfa9386 [desktop] Fixed issue where a user could not copy documents owned by different user.
* 3d4a0e8 HUE-2861 [desktop] Fix a deadlock waiting for thrift connections
* fffb7c0 [jobbrowser] Run JobBrowser tests on a real cluster
* 9cb6220 Merge pull request #209 from renxiawang/master
* 308ff16 Update README.rst
* 590a8a1 [sentry] Link roles to the browse section in Hive
* 85246ab [spark] Add a dedicated Editor view
* 47117c8 [spark] Rename editor to notebook
* 251301a [core] Fixed position of the X-UA-Compatible tag
* 7a20d73 [beeswax] Select 'default' as first assist database if available
* 31777eb [search] Fix the copy of a dashboard
* d548f11 [search] Allow shared dashboards to be copied
* 9e17926 [sentry] Bulk edit privileges with columns
* f1994c7 [sentry] Add column privilege to the Hive tree and dialogs
* 976aea2 [sentry] Add column privilege to the UI skeleton
* 9e457ef [libsentry] Support list of privileges and column scope
* dd5655e [libsentry] Implement new get_sentry_config_value API
* 685dd1c [libsentry] Update to Thrift v2
* d4eec80 [desktop] Default to using secure session cookies if HTTPS is enabled
* c450bc6 [desktop] Change session cookie to not be accessible from javascript by default
* 2c108f0 [pig] Convert tests to point to a live cluster and be re-entrant
* 4e8ce9b [hadoop] Convert tests to point to a live cluster and be re-entrant
* 04d2d45 [oozie] Clean-up the externally submitted workflows in the tests
* dc4b77e [core] Style Hive autocomplete to avoid word wrap
* efe7000 [core] Fixed resize draggable conflicts
* d84f6f5 [rdbms] Make assist panel resizable
* 714813d [beeswax] Improve assist table name presentation
* 85703b6 [beeswax] Make assist panel resizable
* f286d94 [spark] Make the assist panel resizable
* 9fe1d25 [core] Add ko binding for draggable
* e3e20da [spark] Improved css flow for the notebook panels
* 21bad14 HUE-2216 [search] Integrate Solr collections API instead of using solrctl
* d99a931 HUE-2827 [oozie] Workflows cannot be copied in the editor
* c7052a2 [libzookeeper] Do not append Solr port to the default ZooKeeper ensemble
* 0d31ac0 HUE-2856 [desktop] Runcpserver logging for SSL cert or key failure
* a1043f1 [impala] Remove false positive error noise when listing columns
* abf01d5 [beeswax] Add beeswax permissions to test user
* 83f3ef6 [metastore] Adding write permissions to the test user
* 70db654 [hbase] Add live integration tests to HBase Thrift Server 1
* b44fc61 [sqoop] Add a live integration test to the Sqoop2 Server
* 4de03c5 [libzookeeper] Enable Kerberos automatically based on HDFS security
* c2ec3e4 [libzookeeper] Add a live test to the ZooKeeper API
* e8477ba [libsentry] Add a live test to the Sentry API
* 462fa24 [oozie] Make sure to also install the latest Oozie examples when running tests
* 2672447 [libsolr] Add some integration tests
* f980bd6 [indexer] Add some integration tests with Solr
* f692a41 [oozie] Make Mini Oozie cluster optional
* c40ed43 [core] Simplify README description
* a5164e3 [spark] Fix for app broken in IE9
* 449566c HUE-2838 [metastore] Limit the number of partitions after sorting them
* 019a7da HUE-2838 [metastore] Fully convert filtering and displaying to Knockout
* ba0329a HUE-2838 [metastore] Add the state of the partition filtering form in a POST
* d79fee3 HUE-2838 [metastore] Add Ko skeleton to filter partitions by columns
* 9b9caf3 HUE-2838 [metastore] Offer to filter partition on the list of partitions page
* 48db6e3 [livy] Cut down on the number of Futures
* f8ab289 [desktop] Try to fix check config tests by getting the confvar name the old way
* ddeec3f Merge pull request #207 from cjstep/patch-1
* a2d51ac Fix to allow build w/ OpenSSL >= 1.0.2a
* 0a6d7b0 Merge pull request #206 from cjstep/ext-py-parquet-bitstring-fix
* 95f9a24 fixing extra bracket and missing paren in Parquet 'bitstring.py'
* 4c02a42 HUE-2768 [hive] Support nested types
* c0e90a8 HUE-2845 [desktop] Fix config check test failure
* 41474e3 [beeswax] Multiple Issues with Saved Queries page when it runs into multiple pages.
* d62347e HUE-2851 [build] Pickup system packages
* e94a1d9 HUE-2845 [desktop] Add optional /desktop/debug/check_config JSON response
* 600f044 [search] Add the possibility to specify additional Mustache functions
* 28791d3 [oozie] Restyled the credentials tab on the workflow actions
* ac1fcde [spark] Fix resize exception
* e9b5e1b [core] Fixed a wrong Assist margin
* a0f7709 [core] Make sure the home of test user is created
* 44b9788 HUE-2755 [metastore] Convert all tests to be re-entrant
* 488fe52 HUE-2755 [hive] Convert all tests to be re-entrant
* a81c4dd HUE-2755 [hive] Move the test base infra to be re-entrant
* 219f3c0 HUE-2477 [impala] Run tests on a live cluster and make them re-entrant
* 1e558c9 HUE-2477 [fb] Make the FileBrowser tests re-entrant
* d1336c5 HUE-2477 [fb] Run filebrowser.views_test:test_remove on a live HDFS cluster
* 4086917 [spark] Move JVM memory input to ko_components.mako
* 72c28e7 [notebook] Only use session properties if they exist
* 4cd8737 [spark] Switch to a blue background spinner for a more consistent look and feel
* 5dd6db5 HUE-2727 [spark] Add Yarn settings to Java and Python snippets
* ad6d1c3 [core] Add option to allow empty input for numeric KO extender and binding
* 75ed0c2 HUE-2727 [spark] Add snippet execution settings panel
* 9812ea4 [spark] Add small labels to snippet icons
* ff1031b [spark] Create KO template for snippet results
* 1cff9b1 [spark] Extract common snippet footer actions bar
* 9f76140 [spark] Use KO templates for snippet content
* 9f11904 HUE-2727 [spark] Check if properties exist in the settings modal
* ea347be HUE-2727 [spark] Ignore sessions without properties in the settings modal
* 2f6c7db HUE-2727 [spark] Fix namespace for JVM memory input
* d59014b HUE-2727 [spark] Only accept numeric input for numeric spark execution settings
* 91ed6e6 HUE-2727 [spark] Improved JVM memory form input for spark settings
* 471a858 HUE-2727 [spark] Add snippet settings modal
* 904e94c [notebook] Skeleton of sessions and snippet properties
* 4e844c7 [metastore] Fetch a maximum of 5000 database names instead of 1000
* 77b2508 HUE-2755 [spark] PySpark YARN does not always start
* 294cb6c [desktop] Empty passwords should fall back to the password_script
* 3b09e74 [beeswax] Do not set codemirror value on recent query click
* 4c239df HUE-2849 [useradmin] Fix exception in Add/Sync LDAP group for undefined group name
* 01003a0 [desktop] Fix database passwords, stmp passwords, and secret keys scripts
* c7be0bb [desktop] Do not compare regexes by address in RedactionRule
* 430cee1 [filebrowser] Re-enabled d'n'd on upload modal
* 46666dc HUE-2839 [spark] Batch submission cancel button is error-ing
* 6aa5ba2 [indexer] Add Solr path to the ZooKeeper ensemble
* a609654 [desktop] Note that MariaDB should use the 'mysql' database engine
* 55f2873 [spark] Move assist panel to a separate KO component
* 4cdc3a2 [core] Add Pub-Sub functionality to Hue
* ed4e371 [desktop] Fix hue suppressing psycopg2 import error
* b7595da HUE-2835 [core] Fixed minor issue that was missed in my initial testing
* d9cf137 HUE-2843 [useradmin] Hide Add user and some update fields when backend is ldap
* d9accb3 [metastore] Fix metastore partition table tests
* 40a4e79 [hadoop] Protect against non defined server_exc attribute in WebHdfsException
* a708fd5 HUE-2840 [useradmin] Fix create home directories for Add/Sync LDAP group
* 28de49e [livy] Add option to disable impersonation
* 88ba8d5 HUE-2280 [metastore] Partitions names are not always correct
* 8be4139 [core] Initial support for AceEditor
* eb71a1c HUE-1071 [core] Fixed tests for the option to change pwd at login
* 3e20106 HUE-1071 [core] Add option to force password change on first login
* c08f158 HUE-2835 [core] Fixed issue with DN's that have weird comma location
* e433078 HUE-2836 [beeswax] Increase database design name limit to 80 from 64
* 1c5421b [desktop,jobsub] Fix migration model history
* 6c3e6e3 [beeswax] Add some stub migration
* 7db5808 [desktop] Modify version numbers of duplicated Document2 docs
* e1f6bbc [spark] Show errors happening at create sesssion
* e0c8662 [search] Sync name and description of documents for the home page
* 96d87cd [spark] Sync name and description of documents for the home page
* bc5096a [oozie] Sync name and description of documents for the home page
* 3712e91 HUE-2637 [spark] Close Spark session when closing the notebook
* 7e99fd7 HUE-2580 [oozie] Update configuration of running coordinator
* 4433c1b [notebook] Fix spark impersonation
* 9da8066 [core] Fix AttributeError: 'Config' object has no attribute 'get' when running tests
* a2bde97 HUE-2508 [pig] Support %default parameters in the submission popup
* 25574f0 HUE-2508 [pig] Do not show %declare parameters in the submission popup
* 1a0528e [spark] Describe more Livy's main features
* 0db55b1 [desktop] logging Formatter cannot use logging
* c674916 [livy] Add support for paging through sessions
* d22622f HUE-2588 [livy] Unify most of the servlet code
* 44b5fed HUE-2588 [livy] Merge SessionManagers
* ea7c911 HUE-2588 [livy] Lift *Session.logLines into Session
* 32472be HUE-2588 [livy] Start unifying factories, managers, and servlets
* 516e29d [desktop] Be a bit more precise with exceptions when formatting timestamps
* cfa9f2c HUE-2727 [livy] Flesh out interactive session documentation
* 6cac37e [livy] Add support for specifying number of executors in interactive sessions
* 00fcc5d [sqoop] Support kerberos authentication
* 3625cfc HUE-2830 [core] Configuration check to confirm that Mysql engine is InnoDB
* a1e3c2b HUE-2633 [desktop] Restore autocommit setting
* 3116af6 HUE-2633 [desktop] Fix migrations for oracle
* 40b275c HUE-2588 [livy] Add message when deleting or interrupting sessions
* a21cbf2 [notebook] Add code visibility toggle to snippets
* adbcf1d [notebook] Remove vertical resize functionality for code snippets
* 6c3da18 [liboozie] Update tests with the new security property
* 320074b [notebook] Fix initial width of assist bar and Chrome combobox border issues
* 2f6e86d Merge pull request #199 from szczeles/oozie_credentials
* e028f90 [oozie] Do not generate action credentials when security is not set
* 4c95bc8 [sentry] Do not create privilege that was canceled in new role popup
* c692538 [libzookeeper] Move namespace children data retrieval to libzookeeper
* 42780df [sentry] Pick-up the ZooKeeper principal from libzookeeper
* b2409d9 [sentry] Support refetching server list with HA when previously no servers were up
* 4d1769c [libzookeeper] Move the ZooKeeper specific properties to its own lib
* 77019d3 [sentry] Convert sasl parameters to strings
* e7f2c62 HUE-2812 [hbase] The select all checkbox should only select visible entries
* d5d5cac HUE-2786 [hbase] Show current version in the cell history and allow revert to previous version
* 4b18799 HUE-2633 [desktop] Enable autocommit for transactions
* 7d93ca5 HUE-2633 [desktop] Optimize checking for orphan docs in sync_documents
* 7e0b011 [desktop] Fix a typo in sync_documents
* 644633d HUE-2633 [desktop] Most docs don't need the example tag
* 3fd6950 HUE-2633 [desktop] Prefetch the users, which removes another N queries
* 059af67 [desktop] Only sync documents if we're not doing a dry run
* d839678 [desktop] Extract WebHdfsException remote exception only if present
* 515ee62 HUE-2805 [oozie] Cleaned up filter html
* 9d7a046 HUE-2805 [oozie] Refactor UX of the various modal dialogs
* 74f7646 HUE-2805 [oozie] Ignore a terminated Coordinator action
* 60a3a6a HUE-2824 [oozie] Improve dashboard response time for larger job count
* 14d5df7 HUE-2823 [spark] Loading of a notebook with results generates a dataTable error
* 2e243c6 [jb] Avoid javascript error when application does not have a valid time
* 7c99fab HUE-2811 [hive] Fix line error location when executing a selected statement
* 585a19c HUE-2786 [hbase] Always show expand button when there are collapsed columns
* 333176a HUE-2772 [filebrowser] Fix alignment of dropdown menus
* 7aa581f HUE-2788 [hbase] Don't show mime type when it's unknown
* 6f91948 HUE-2769 [spark] Improve UX of Spark jar snippet
* f8655df [desktop] Remove Desktop.objects.copy since it violates uniqueness
* c74cc3f [all] Fix tests that broke with the new unique constraints
* 45c15b4 [desktop] Optimize finding jobs missing docs in sync_documents
* 6fbdc5f [desktop] Collect sharing sample docs into one place
* 0ef8cd2 [desktop] South doesn't like SQLite using transactions.atomic
* a0c3e57 [desktop] Unique index replaces need to check for duplicated docs
* ea67b3e HUE-2822 [fb] Fix superuser check when accessing file
* 6be710f HUE-2617 [metastore] Return partition results in reverse order by default
* ad42a17 [desktop] Delete duplicated documents,tags,permissions before creating unique index
* f36cb2b [oozie] Remove unused and invalid unique_together indexes
* 7d1ea1a [desktop] unique_together needs to be put in the <model>.Meta class
* f67d547 [desktop] unique_together needs to be put in the <model>.Meta class
* 513ea4b [desktop] unique_together needs to be put in the <model>.Meta class
* 6467295 [desktop] unique_together needs to be put in the <model>.Meta class
* eda8de4 [desktop] Change DocumentPermission.perms to be a CharField of max length 10
* 5886c7e HUE-2817 [core] Correct database default options to be valid JSON
* f39e71a [core] Update logs style across the whole Hue
* b20da76 [core] Revert Knockout mapping plugin to 2.3.2
* eae8ce1 HUE-2816 [core] Fixed tests broken by HUE-2796
* a62c699 HUE-2813 [hive] Report when Hue server is down when trying to execute a query
* 8ef5d4a HUE-2820 [core] Accessing About App without loging does not always trigger authentication
* 9dfc45e [search] Allow null state or country on the map chart
* 4d340eb [search] Marker map should display 'no data' after loading
* 6b1fd7f [search] Add link of saved definitions in the URL
* bcd45ed [oozie] default credentials in hive actions
* a264515 [core] Fix caching of X-CSRFToken cookie token
* c1efcbb [oozie] Fix directly executing a workflow without opening it
* f5ad689 [libsentry] Pick up the correct ZooKeeper quorum when HA
* a83b136 [core] Fix set value problem with X-editable
* 3c0dbca [notebook] Lighten up the snippet editors
* d896a94 HUE-2761 [notebook] Snippet resize can get stuck
* 0207cab [notebook] Always show the action menu button
* 05a6252 [livy] Capture batch stderr in local mode
* 2dc6b41 [core] Add deferred updates to Spark and fix for Oozie
* 477424d [core] Enable KO deferred updates
* abeb2e5 HUE-2808 [dbquery] Add row numbers to support default order by
* dc86f32 [oozie] Add new retry properties to all the new Action nodes
* c4ca4b7 [search] Protect against dashboard with no analytics dimension
* 931f3e7 HUE-2814 Revert "[desktop] Upgrade PyOpenSSL to 0.13.1"
* 722f10f HUE-2814 Revert "[desktop] Remove pyopenssl version 0.13"
* e281668 [jb] Make Kill job button configurable
* a2c5ab6 [livy] batch files argument doesn't yet allow referencing local files
* d12c3b6 Merge pull request #196 from xiaop1987/add_num_executor
* 25ced6b Merge pull request #197 from xiaop1987/livy_get_app_status
* 7e1ddac [jobbrowser] Fix tests
* 5a71e7c [desktop] Fix tests
* 9a6642a [filebrowser] Fix tests
* a3f4969 HUE-2777 [oozie] Move Coordinator action filter buttons to backend
* 808c794 [core] Bumped Knockout to 3.3 and Knockout Mapping to 2.4.1
* a954073 [search] Fix exceptions with stacked/grouped chart
* 4787cb7 [search] Added sorted field list to Marker map
* 507a495 [search] Improve clustering display
* ed391b6 [search] Fix tooltip position on multi bar with brush chart
* 0386ff3 [desktop] Handle oauth2 library import errors
* ffe2c0b [desktop] Catch the correct exception
* 249ff26 [desktop] Log all caught naked "except:" blocks
* 09321ff [spark] Log all caught naked "except:" blocks
* e0d7524 [sqoop] Log all caught naked "except:" blocks
* 443312e [livy] Tweak fake_shell logging, remove unused livy-client.py
* f44970b [search] Log all caught naked "except:" blocks
* 74c04eb [pig] Log all caught naked "except:" blocks
* 2667702 [oozie] Log all caught naked "except:" blocks
* 02807fb Revert yarn-site.conf related
* 86b4d1f Reload yarn-site.conf to get resourcemanager address.
* 6983c0c [jobbrowser] Log all caught naked "except:" blocks
* e7f1a9c [hbase] Log all caught naked "except:" blocks
* 9c84070 [useradmin] Log all caught naked "except:" blocks
* 8dc87d0 [filebrowser] Log all caught naked "except:" blocks
* 934adc7 [beeswax] Log all caught naked "except:" blocks
* 4a6448f [desktop] Don't compare regexes by address
* 468a7d4 HUE-2796 [core] Fixed several sync_groups_on_login issues including posix
* df37945 HUE-2796 [core] Fixed several sync_groups_on_login issues including posix
* 39a645d HUE-2796 [core] Fixed several sync_groups_on_login issues including posix
* eec1ef4 HUE-2796 [core] Fixed several sync_groups_on_login issues including posix
* 633f39d [search] Restyle the Analytics widget
* 02f4e57 Reload yarn-site.conf to get resource manager address in case get application status failed.
* bd29abe [livy]Revert files option issue.
* 6c0011c [livy] Explicitly use a version of httpcore and httpclient
* 69ff10f [desktop] Add a SIGUSR1 handler that dumps the thread stacktrace to stderr
* f7b6acc [hive] Fix internationalization in error message
* 01e3321 Merge pull request #191 from skahler-pivotal/master
* f1acf37 [desktop, beeswax, impala] Log config validation exceptions
* 329a722 [desktop] Track authentication login times
* fbeb2ab [desktop] Don't use .select_related("owner") and .only("id") at the same time
* c7da5f4 HUE-2799 [search] Support marker clustering on Leaflet Map widget
* 274ea2f HUE-2807 [useradmin] Support deleting numeric groups
* fa07a63 Add numExecutors parameter description
* 74d6181 1.Add num-executor option in BatchRequest; 2. Fix bug of files option
* 20a6d2c [desktop] Fix detecting YARN resourcemanager failover
* 8d65a75 [oozie] Avoid a noisy exception in the logs
* af8982b HUE-2114 [oozie] Configure action retry properties
* 928e8ad HUE-2783 [search] Load and update search definitions
* 142eb1d HUE-2488 [oozie] Validate the action properties
* b6f4993 HUE-2803 [jb] App crashes when there are more than 1,000,000 jobs
* c79abce HUE-2802 [indexer] Dump Config bugs when search app is not installed
* 78269a9 HUE-2801 [jobsub] Actions in the dropdown still shows up when the app is uninstalled
* 62d60d5 HUE-2784 [oozie] Coordinator editor generate wrong Monday cron expression
* 27aa004 HUE-2793 [JB] Fix Mapper & Reducer counts in job page
* 2ae370d [core] By default ignore case of usernames with LDAP
* f828d56 [libsolr] Escape quotes in values with a space in filter queries
* 0efad0b HUE-1352 [search] Extract, highlight and show only the matching fragments
* 2e28c01 HUE-2783 [search] Restyled definition modal
* 1380fdb HUE-2783 [search] Save search definitions model part
* e108805 HUE-2152 [pig] HBase credentials support in editor
* b8e03cd [search] Workaround for wrong X positioning of bar tooltips
* 95123bc [search] Improved display of fixed time window
* f90efe9 HUE-2776 [oozie] Fix "View All Tasks" pagination in the Hue Jobbrowser
* b90561c HUE-2718 [oozie] Coordinator path hint could support Single type
* 0b7275a [search] Furtherly improved rendering of date ranges
* 7f09714 HUE-2778 [jobbrowser] Fix "Text Filter" search box in "View All Tasks" page
* 9d8084e [search] Set the correct date on Datepicker with a Moment.js format
* 6c9c1c8 [search] Improved rendering of yearly gaps
* 3a6bfa0 HUE-2292 [oozie] Paginate coordinator actions
* 09bef77 [hadoop] Support new sentry.hdfs.integration.path.prefixes hdfs-site.xml property
* 4be709c HUE-2763 [oozie] Paginate Bundles dashboard tables
* 2e036ff [search] Apply global fixed date filter to widgets
* 93e0478 [core] Do not 500 error when importing invalid documents
* bc629f4 HUE-1660 [oozie] Integrate the import/export of Workflows, Coordinators and Bundles
* 4edf916 HUE-1660 [search] Integrate the import/export dashboards
* f732238 HUE-1589 [search] Port old sharing permission system to document model
* 5661cde HUE-2599 [search] Prettify date facets display
* 21fa004 [search] Always display fixed date range
* 0dea3bc [indexer] Add SOLR_ZK_ENSEMBLE with --zk to solrctl command
* a5b3250 HUE-1660 [core] Moved import/export dialogs into a common mako
* bcb2e76 HUE-1660 [core] Prettify import dialog on Spark notebooks
* b5cd9bf HUE-1660 [core] API for export/import all stored scripts
* 4e962b9 HUE-2560 [metastore] Added progress bar for the terms count
* ac7eeac HUE-2560 [metastore] Integrate terms into the column stats popover
* fefaaf4 HUE-2560 [metastore] Added table stats to Metastore
* 02f69ec HUE-2560 [metastore] Column statistics on Metastore and Assist
* 7c9bc6f HUE-2560 [metastore] Add column stats popover
* b6b1b39 [core] Updated demi-modal UX
* b2f3f62 [spark] Add new sub menu to the top level menu
* b86e098 HUE-2762 [notebook] Export all code of a Notebook
* c05366d [core] Add KO binding for selecting content with one click
* d658419 [metastore] Update tests to use backquotes
* d85c1eb [livy] Support long running statements
* cf5c571 [livy] Fix flaky test
* 99db83f [livy] Support paging in livy-repl
* 38194ff [livy] Ignore IOExceptions when shutting python down
* 1fc64a8 [livy] Clamp paging to start at 0
* 05b431f [livy] Factor out the python interpreter
* dbafb1c [useradmin] Sanitization process added to groups
* abfc1bb HUE-2767 [impala] Issue showing sample data for a table
* 80d3abe [search] Support fixed date ranges in the global filter
* 705a7fb [livy] Expose interactive session logs through /sessions/id/log route
* b671ef1 [livy] Create a SparkProcess wrapper
* 16fa570 [livy] Thread sessions aren't being used and weren't worthwhile
* 86bd101 [search] Fix analysis popover position with uppercase fields
* 103b8f6 [search] Fixed search fixed time settings and added datepicker
* 1ccfdc4 HUE-2751 [oozie] Fix unit tests
* fb12f43 HUE-2751 [oozie] Paginate Coordinator dashboard tables
* aef5d94 [livy] Fix syntax error
* 6c0f1d7 [livy] Allow interactive session to upload jars and files into the working dir
* 9f45c5c [livy] Don't start if spark-submit doesn't exist
* c08a961 [livy] Allow the spark-submit to be configured
* f85e52d HUE-2754 [oozie] Sqoop action with variable adds an empty argument
* 47a7045 [spark] Rename the livy session creation argument "lang" to "kind"
* d7639e6 [livy] Add support for batch proxy users
* a415ae0 [livy] Add support for specifying interactive memory and core limits
* 68c44bb [livy] Pass around CreateInteractiveRequest objects
* 07a3e75 [livy] Rename BatchSession.lines to logLines
* 745ae85 [livy] Add Session.stop()
* e1a6db3 [livy] Rename Batch* to BatchSession*
* af17ebd [livy] Start merging batch and interactive sessions
* ec9ceff [livy] Rename server.interactive.*Session* to *InteractiveSession*
* e99c7d5 [livy] Rename livy.server.sessions to livy.server.interactive
* e1993ed HUE-2753 [core] Add script to cleanup history in oozie and beeswax tables
* b366344 HUE-2753 [core] Add script to cleanup history in oozie and beeswax tables
* 11a26e4 HUE-2753 [core] Add script to cleanup history in oozie and beeswax tables
* d4b9bd6 [search] Fixed hiding logic for rolling time options
* 6f1a435 [search] Fix rolling select styles
* dd765ad [desktop] Replace some LOG.warns with Log.exceptions
* 33893f3 [search] Disable date range guessing with dates older than 1900
* a5e197d [search] Fix stats popup API call
* 3f5b138 [search] Offer global rolling time selection select in the UI
* 10eb5fb [search] Split general and time settings
* 3f49444 [search] Moved refresh settings to the semi-modal dialog
* b277c4b [search] Align better the new/list dashboard menu icons
* c5c8c0c [search] Update result rows when translating field columns
* e920d27 [search] Support multi analytics series
* f6f8d04 [search] Analytics date range facet graph integration
* abfdf87 [search] Analytics field facet graph integration
* e6638a1 [oozie] Fix table info when filtered page on Workflow dashboard has zero jobs
* c37600f HUE-2721 [oozie] Generalized and externalized table info generation
* ae835fd HUE-2721 [oozie] Change table info according to filter selected in Workflow dashboard
* 2f6c73b HUE-2721 [oozie] Add pagination to Workflow dashboard completed table
* 9b7e5a5 HUE-2721 [oozie] Made pagination buttons and functions generic
* 34b7a2b HUE-2721 [oozie] Paginate Workflow dashboard
* edcbb69 [core] Updated readme with GMP dependecies
* 9dd78ce [load-balancer] Automatically discover static file dir, avoid kt_indexer role
* 453f338 [beeswax] Update API url to get stats in editor
* 7c7c160 HUE-1084 [impala] Integrate stats and terms analytics to Impala API
* 169e657 HUE-2560 [metastore] Add refresh stats on assist
* fae2534 HUE-1084 [metastore] Add a top column value API
* 93a1489 [metastore] Unflatten column stats API result
* be8ad6d HUE-2742 [hbase] Apply canWrite to the codemirror binding
* e0c44d7 HUE-1084 [beeswax] Wired up table stats on the assist
* d336e19 HUE-1084 [beeswax] Integrate table and column stats
* 50c1b52 HUE-2742 [hbase] Not possible to read full cell without write permissions
* 7b25c57 [oozie] Help on SLA page when Oozie is not configured to use SLAs
* f74e78d HUE-2743 [search] Error can create an exception if not proper unicode
* 3258fa7 [oozie] Jar can be selected as archive fields
* ea0d6c5 [impala] Improved rendering of the fixed headers
* 5a9570a HUE-2746 [fb] Reset search box filter when opening a folder
* 416358f HUE-2743 [search] Escape HTML in the jHueNotify messages
* 2b8de47 [core] Lighten up login form
* de88b36 [oozie] Rename "Killed" button to "Error" that displays both Failed and Killed jobs
* e2e6cd3 [hadoop] Limit job tracker thrift plugin incoming requests to 10MB
* e7d344c [hadoop] Check config should print the real HDFS admin
* 4a74e08 [dbquery] List all the schemas in a Postgres database
* 63efe6a HUE-2701 [oozie] Java action relative jar path results in error on submit
* 8735bf8 [oozie] Jars of MapReduce and Java actions are not copied to the lib directory
* f79df4e [oozie] Add a MapReduce Sleep worklow example
* 3831f27 [oozie] Fix failing unit tests for HUE-1834
* 1008267 HUE-2703 [sentry] Make more obvious why a user is not a Sentry admin
* f15429b [sqoop] Add job name to the list of jobs
* 45a563f [sqoop] Delete a job with its id and not name
* f5edb6e [livy] Fix BatchServletSpec test
* 243c54c [livy] Kill the Yarn Job if livy-repl didn't cleanly shut down
* f747cb5 HUE-2741 [home] Hide the document move dialog
* 9198879 HUE-1834 [oozie] Filter dasboard jobs in the backend
* 837abe5 HUE-2729 [oozie] Add XSLT2 to generate workflow graph data from XML
* d182e84 [desktop] Remove the djangosaml2 tests
* c0e8e5f [desktop] Include djangosaml2-0.13.0
* c78c296 [desktop] Remove the pysaml2 tests
* 06716d9 [desktop] Import pysaml2 version 2.4.0
* 03f4fd3 [desktop] Add pycrypto-2.6.1 for pysaml2
* d0018da [desktop] Remove python-dateutil-1.5
* 52c1f39 [desktop] Upgrade python-dateutil for pysaml2
* c844ae0 [desktop] Include pycrypto-2.6.1 for pysaml2
* b7e35c2 [desktop] Remove pytz-2014.10
* b8d6335 [desktop] Upgrade pytz to 2015.2.
* ae87706 [desktop] Remove Paste 1.7.2
* bab3c00 [desktop] Upgrade Paste to 2.0.1
* 130f9f1 [desktop] Remove pyopenssl version 0.13
* acdeba2 [desktop] Upgrade PyOpenSSL to 0.13.1
* f4c3ba9 [search] Adding 0 for null or empty hit widgets
* 96c52ff [search] Support all as a date filer
* 17677b2 [search] Do not show date properties of time filter managed widgets
* 0c9feb7 [search] Logic for combining different date fields on the same dashboard
* 2c4ff6e [search] Smarter date truncation for date filter
* 8b5d8f4 [search] Integrate rolling time to text facet
* 6eef4a0 [search] Provide finer grain interval for real time timelines
* 399ec97 [search] Selection should override main date filter
* 4339fc6 [search] Date selection overrides timeline selection
* b061cb9 HUE-2578 [search] Rolling date filter skeleton
* e8a943e [core] Fix for the scrollable Oozie submenu
* fe3bfed [search] Set a maximum width for the field list
* bd63881 [search] Fix facet type infinite loading message
* 93a8882 Merge pull request #186 from t3hi3x/master
* 36d71c1 [HUE-2739] [metastore] Autocomplete with databases/tables with built in names fails
* 454db28 [spark] Adding references to Hue 3.8 and Notebook posts
* ea078ff [liboauth] Convert to static files
* d0a0f49 [spark] Add support for paging through batch logfiles
* eeb9bcc [livy] Add endpoints to get batch state or logs
* fa614d8 [spark] Make api.py routes only accept GET or POST requests
* 85fe5a2 [beeswax] Log exceptions
* 48be558 [spark] Log exceptions
* 9225297 [core] Disable password autocomplete on the login form
* e7e7e8b [livy] Fix creating a session
* fe9f0c2 [core] Make main menu dropdown scroll in case they are too long
* e65a8b2 HUE-2735 [search] Support 2-letter country code in gradient map widget
* 7e072e3 HUE-2731 [core] Validate that Hue is running in collect data script
* fc52eac HUE-2731 [core] Hue collect data script didn't validate that Hue was running before trying to collect
* c528155 [oozie] Open Decision node EL help in another tab
* 75d3229 HUE-2677 [spark] Fetch status of batch jobs
* 6046fda Revert "HUE-2722 [beeswax] Revert default Thrift version to 5 instead of 7"
* 9580337 HUE-2722 [hive] Hive 0.14 can truncate the number of rows
* 7df277d HUE-2732 [oozie] Make sure "data" fields have the right default value
* b6bfe7f [core] Log exceptions from views
* 252b5a1 [doc] Friendler tarball install README
* 236a004 [core] Bump version to 3.8.1
* b12e426 [sentry] Adding server name to URI privileges view
* b863e28 [sentry] Display text privilege depending on its URI or DB type
* 6e55578 HUE-2723 [hive] Listing table information in non default DB fails
* e8c51d7 [livy] Fix livy tests
* 9a8360e HUE-2722 [beeswax] Revert default Thrift version to 5 instead of 7
* af5dea7 [sentry] Set URI scope to URI privileges instead of SERVER
* bbd91fb [desktop] Fix dump_traceback test
* cbf289c HUE-2713 [oozie] Deleting a Fork of Fork can break the workflow
* 3d2d12b [doc] Document we need make
* 2ead0dd HUE-1922 [oozie] Smarter file symlinking in workflow action
* dd0a503 [livy] Allow spark builder files to optionally allow local files
* 2cbe783 [livy] Add filesystem prefix to protect against accessing arbitrary files
* 6eb58e6 [livy] Allow negative offsets to scroll backwards through a log
* 9f3c93a [livy] Change the default session factory to process
* 73ee764 [oozie] Change Sqoop command field to textarea in the node popup
* 0445bac [search] Support excluding values in nested facet counts
* 429fcba HUE-2716 [pig] Move the comment to the next line
* 37e4919 [useradmin] Fixed LDAP label and link
* 05e23ee HUE-2717 [oozie] Coordinator editor does not save non-default schedules
* b4a7926 HUE-2657 [core] Can not remove user from a document's "Sharing" dialog if just one user plus one group is present
* 0aeceda Merge pull request #185 from ciranor/master
* 0ce7628 HUE-2716 [pig] Scripts fail on hcat auth with org.apache.hive.hcatalog.pig.HCatLoader()
* d4f7cce HUE-2707 Allow sample on partitioned tables in strict mode.
* 78af219 HUE-2720 [oozie] Intermittent 500s when trying to view oozie workflow history v1
* 3c39546 [spark] Add Spark REST Server config properties in hue.ini
* 4d1168a HUE-2719 [search] Deleting grid or filter from magic layout deletes both
* 016d1b7 [oozie] Some inputs are not disabled on non edit mode on coordinator editor
* b803b6d [build] Include the load-balancer in the tarball
* 50e66c6 [desktop] Up the thread_util.dump_traceback timeouts
* c9ee330 HUE-2173 [search] Core of Analytics facets
* 91826b2 [search] Changed counter widget icon
* 33f626f [core] Upgrade FontAwesome to 4.3
* 73c5235 HUE-2173 [search] Preparing multi series analytics charts
* b7f208b HUE-2173 [search] Adding function to bar charts
* d48970a HUE-2173 [search] Support limit in json terms facets
* 04a50ae HUE-2173 [search] Support json terms facets
* 8dd6f9b [search] Implemented text squeezer for the Hit Widget
* 375818c HUE-2683 [search] Make type of metric configurable
* 030ca4a HUE-2683 [search] Link response value to hit widget
* 37a9274 HUE-2683 [search] Add counter widget skeleton
* db4223f [core] Fix job counter on the top menu
* 4f5dcf3 HUE-2711 [search] Hide gray area on bar chart selection
* 984220d HUE-2714 [search] Deleting a widget throws a js error
* cf9e3e3 HUE-2711 [search] Fix popup error of Histogram select of a range
* 2f83253 HUE-2710 [search] Heatmap select on yelp example errors
* c188e98 HUE-2712 [oozie] Creating a fork can error
* d590fdb [build] Fix the "make clean" order
* 4ebef11 [oozie] Some job properties are not generated in the workflow.xml
* d973468 [search] Strip script tag from HTML template
* ce03505 HUE-2708 [fb] Filechooser breaks on special characters
* ddd232c [search] Restyled dashboard settings demi-modal
* b5fb808 [search] Also pull dynamic fields when creating a new dashboard
* a1d0fb7 [spark] Styled JAR and PySpark widgets
* b109aca [livy] Don't assume bash is always installed in /bin
* 369fd7b [desktop] Extract thread stacktrace printing


Contributors
------------

This Hue release is made possible thanks to the contribution from:

- Aaron Newton
- Aaron T. Myers
- abec
- Abraham Elmahrek
- Aditya Acharya
- Alex Breshears
- Alex Newman
- Alex (posi) Newman
- alheio
- Ambreen Kazi
- Andrei Savu
- Andrew Bayer
- Andrew Yao
- Ann McCown
- Ashu Pachauri
- Atupal
- bcwalrus
- bc Wong
- Ben Bishop
- Ben Gooley
- Ben White
- Bhargava Kalathuru
- Bruce Mitchener
- Bruno Mahé
- Christopher Conner
- Christopher McConnell
- cwalet
- dbeech
- Derek Chen-Becker
- Dominik Gehl
- Eli Collins
- Enrico Berti
- Erick Tryzelaar
- gdgt
- Gilad Wolff
- grundprinzip
- Harsh
- Harsh J
- Henry Robinson
- Igor Wiedler
- Ilkka Turunen
- Istvan
- Ivan Orlov
- Jakub Kukul
- Jarcek
- Joey Echeverria
- Jon Natkins
- Karissa McKelvey
- Kevin Wang
- krish
- Lars Francke
- Linden Hillenbrand
- Luca Natali
- Marcus McLaughlin
- Mariusz Strzelecki
- Michalis Kongtongk
- mrmrs
- Nicolas Fouché
- Olaf Flebbe
- Pala M Muthaia Chettiar
- Patricia Sz
- Patrycja Szabłowska
- Paul Battaglia
- Paul McCaughtry
- Peter Slawski
- Philip Zeyliger
- Piotr Ackermann
- Prasad Mujumdar
- raphi
- Ricky Saltzer
- Romain Rigaux
- Roman Shaposhnik
- Rui Pereira
- Sai Chirravuri
- Sean Mackrory
- Shawn Van Ittersum
- Shrijeet
- Shrijeet Paliwal
- Shuo Diao
- Stephanie Bodoff
- Suhas Satish
- Tatsuo Kawasaki
- thinker0
- Thomas Aylott
- Todd Lipcon
- vinithra
- vybs
- William Bourque
- Word
- Zhihai Xu
