---
title: "3.5.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -3050
tags: ['skipIndexing']
---

### Hue v3.5.0, released Wednesday 4th, December 2013


Hue, http://gethue.com, is an open source UI for Hadoop and its satellite projects.

It makes the whole platform (e.g. HDFS, MapReduce, Hive,  Oozie, Pig, Impala, Solr, Sqoop,
ZooKeeper...) easy to use and accessible from your browser (e.g. upload files to HDFS, send Hive queries from a Web editor,
build workflows with Drag & Drop... all within a single app).


Notable Features
----------------

- The look & feel and navigation bar have been redesigned
- [DBQuery App: MySQL and PostgreSQL Query Editors](http://gethue.com/dbquery-app-mysql-postgresql-oracle-and-sqlite-query)
- [New Search feature: Graphical facets](http://gethue.com/new-search-feature-graphical-facets)
- [Integrate external Web applications in any language](http://gethue.com/integrate-external-web-applications-in-any-language)
- [Create Hive tables and load quoted CSV data](http://gethue.com/hadoop-tutorial-create-hive-tables-with-headers-and)
- [Submit any Oozie jobs directly from HDFS](http://gethue.com/hadoop-tutorial-submit-any-oozie-jobs-directly-from)
- [SSO with Hue: new SAML backend](http://gethue.com/sso-with-hue-new-saml-backend)
- [Hive Query editor with HiveServer2 and Sentry](http://gethue.com/hadoop-tutorial-hive-query-editor-with-hiveserver2-and)


Compatibility
-------------

Runs on CentOS versions 5 to 6, Red Hat Enterprise Linux (RHEL), and Ubuntu 10.04 to 12.10.
CentOS 5 and RHEL 5 requires EPEL python package.

Tested with CDH5beta1. Specifically:

- Hadoop 0.20 / 2.2.0
- Hive 0.12.0
- Oozie 4.0
- HBase 0.96
- Pig 0.12
- Impala 1.2
- Solr 4.4
- Sqoop2 1.99.3

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

* Windows: Chrome, Firefox 3.6+, Internet Explorer 9+, Safari 5+
* Linux : Chrome, Firefox 3.6+
* Mac: Chrome, Firefox 3.6+, Safari 5+


Runs with Python 2.6+


List of 254 Commits
-------------------

* 18170a1 [doc] Adding 3.5 release notes
* df9bafb HUE-1772 [core] Adding a new tag remove the sample tag
* 742f1d1 HUE-1777 [beeswax] Unify is_auto status of the queries
* 0d9af28 HUE-1782 [useradmin] refldap entries when importing groups causes errors
* f47c843 HUE-1775 [core] Filter out trashed documents on home page
* f7e6b25 [jobsub] saving a design shows an empty page after
* 36275c1 [oozie] Path changes in FS nodes in Oozie app can't be changed
* 3f21246 HUE-1778 [dbquery] Query hangs with MySql
* 0ed3b45 HUE-1774 [dbquery] Update ini config with examples
* 38a09c0 HUE-1780 [dbquery] datatables disabled
* 1e5a830 [beeswax] Run table example creation as the current user
* 51d2ce3 HUE-1762 [dbquery] Show errors in the UI in case of DB connection failure
* 38bcb60 [oozie] Delete cleanly coordinators and bundles
* 7eb2041 [pig] Fix script copy
* 0ef94e4 [oozie] Set the correct example tag to the oozie workflow examples
* b616733 [oozie] Load datasets in the examples
* 5c56582 [oozie] Fix scheduling of coordinators
* 14743b2 HUE-1771 [pig] HCatalog table autocomple does an insert
* 2b0d40e HUE-1770 [core] Do no allow unselection of tag when click toggling one
* 844a6c8 HUE-1773 [beeswax] JS error when there's an error without a particular line/character specified
* 72b93df [doc] Updated Hadoop versions of Hue 3.0
* 705cd62 HUE-1746 [metastore] Remove header line from datafile if header detected
* f12f1ad HUE-1701 [oozie] Import coordinator button
* f2b78e1 HUE-1737 [oozie] Bigger view log icon
* d693edb HUE-1767 [useradmin] Ensure posix groups and other groups are separated
* c1fc7a2 HUE-1766 [dbquery] Autocomplete behaviour should match Beeswax/Impala's ones
* f6c0460 HUE-1758 [dbquery] Add navigator for quick table browsing
* 7141807 [search] URL escape links to range facets
* d7c1019 HUE-1764 [dbquery] use database options when creating a connection
* b1a1f9a HUE-1765 [dbquery] Datatables breaking sometimes
* e454e45 HUE-1763 [dbquery] Autocomplete doesn't work for a new dbquery setup
* 85cb561 HUE-1590 [core] Make SAML logout optional
* 9d72726 HUE-1452 [oozie] Support workflow credentials
* 21edfc1 HUE-1639 [core] HTTPOnly on session cookie
* 3922252 [core] Protect thread session conflicts
* 6c841c4 HUE-1742 [search] Improve graphical facet performances
* f11ad68 HUE-1679 [oozie] Save a workflow with a bad name fails with no information
* 37f892c [core] Remove parent definition in root pom
* f6db605 HUE-1742 [search] Improve graphical facet performances
* c8be55b HUE-1757 [dbquery] Magic table autocompletion
* 95d7fec HUE-1717 [dbquery] Add table and column autocompletion
* c90388b HUE-1754 [dbquery] provide an appropriate view when no databases are configured
* 72c4007 HUE-1756 [dbquery] Empty results view
* 822fb31 HUE-1754 [dbquery] provide an appropriate view when no databases are configured
* 8874353 [core] Update hadoop version in Maven
* 98c9b54 HUE-1746 [metastore] Auto detect header if all cols are strings
* fcf7bbe HUE-1749 [core] thrift ssl support
* 2c16cb2 HUE-1749 [core] thrift ssl support
* c347383 [core] Make hostname generic in tests and remove webhdfs threadness test
* 932498a HUE-1746 [metastore] Read header from file
* 41d30a2 [beeswax] Dynamic HiveServer2 port during testing
* 3d9e2b6 HUE-1747 [metastore] Create table from quoted csv file
* 3ffd686 HUE-1665 [oozie] import workflow locks database
* 264b253 HUE-1746 [metastore] Styled the header button
* 2c79c08 HUE-1746 [metastore] Read header from file
* 33c55f8 HUE-1750 [core] Make IPv4 or IPv6 pluggable for Thrift clients
* 07de444 HUE-1750 [core] Make IPv4 or IPv6 pluggable for Thrift clients
* b7570f4 HUE-1745 [beeswax] Autocomplete table name with magic from broken
* 5ed68d2 HUE-1704 [pig] Give the user the possibility to hide the function helper and totalstorage it
* 1d39b50 HUE-1728 [search] Error or disabled message when cannot connect to the Solr server
* b156382 HUE-1748 [jobsub] Datatables does not resize correctly
* 45863bf HUE-1739 [dbquery] 500 error on execute query
* b14ee75 HUE-1744 [core] upgrade packaged thrift
* ebe18d3 HUE-1601 [oozie] Workflow editor shouldn't display deleted action in Import Action
* 797f6d6 HUE-1727 [beeswax] Export data from a non default database
* b818b96 HUE-1715 [dbquery] test using sqlite
* 8de897e HUE-1743 [core] Prevent frame busting and clickjacking
* dbebdca HUE-518 [beeswax] File Resources support other file systems
* d554856 HUE-1501 [oozie] Support coordinator datasets from non HDFS
* 65ab2b5 HUE-1741 [dbquery] bugs
* d370148 [fb] Trash opens up on user current path if possible
* c51589f [core] Remove old Hadoop configs
* a9d55e4 [core] Add a default webhdfs url in order to avoid misconfiguration warning
* 90f3eda HUE-1743 [core] Prevent frame busting and clickjacking
* 9fc933d HUE-1731 [search] Support dates in graph facets
* 25908db HUE-1740 [oozie] Ko error when editing datasets
* e5ba3b2 [core] Skip quick start wizard checkbox for admins
* 19dd13c HUE-1714 [dbquery] Add Oracle backend
* 058d572 HUE-1713 [dbquery] Add SQLite backend
* 38b4cc5 HUE-1729 [spark] Syntax highlighting for Scala and Java and hints
* 938691c HUE-1735 [fb] Better back history
* 78b12b3 HUE-1732 [core] Hide menu sections from navbar if list of apps is empty
* e86f6af HUE-1476 [fb] Submit oozie jobs directly from HDFS with FileBrowser
* 17d1fd1 [oozie] Set implicitly the user used in the API
* b7aa82a HUE-1694 [impala] Multi query not always supported
* e0ebe6d [beeswax] Stop infinite loop in navigator when there is no DB
* 5689651 HUE-1455 [impala] Close use and metastore queries
* 4f9f48e HUE-826 [proxyapp] Add missing conf.py
* 2481949 [beeswax] Sentry support for HiveServer2 and Impala
* 7935b4e [beeswax] Fix monkey patching teardown in tests
* 34a106f [spark] Java and Scala support
* 6396553 HUE-1705 [spark] Initial commit
* f88f741 [core] Update tests to use the latest tarballs
* 0a81f27 HUE-1699 [dbquery] metastore fixes
* 50cc161 HUE-1699 [rdbms] Create RDBMS app
* 1190bc4 HUE-1711 [core] LDAP username import lowercase
* 2e9e2c2 HUE-826 [proxyapp] Support ini parameter for URL
* ffed5d8 HUE-1707 [impala] Retain query text when switching away from the app
* 14c5a11 HUE-1570 [search] Timeline display
* 3b5b5d2 HUE-826 Make the new app show up in the navigation bar
* 16d8d4f HUE-826 [proxy] Embedded proxied app
* d8b2a51 HUE-1664 [core] URL Redirection whitelist
* c1ca50e HUE-1096 [core] Workflow examples conflicts with existing workflows
* 56d14b7 HUE-1618 [graph] New graph lib
* e084947 HUE-1690 [core] Forceful Browsing / Directory Listing
* 48295c5 [filebrowser] Abstract DEFAULT_HDFS_SUPERUSER in the tests
* 5ed6fce HUE-1698 [fb] Toolbar is fixed too high
* d4c4585 HUE-1680 [oozie] Java Action delete jar file from workflow lib
* f7b60c4 HUE-1696 [core] Update Knockout to version 3
* 6b18c69 HUE-1695 [core] Update FontAwesome to version 4
* 5f9d820 HUE-1682 [sqoop2] Better error notification when a server is not available or not responding
* 9fdf857 HUE-1613 [oozie] Improve coordinator timezone description
* 1dd04b4 HUE-1684 [pig] Create a Navigator for functions
* 31d51d2 HUE-1692 [core] Add trademark on About page
* 6533488 HUE-1691 [help] Revamp a bit the style
* 1c5f77b HUE-1689 [core] The wrong Browser locale is used
* 408962a HUE-1687 [core] SAML backend with simple redirect logout
* e260b29 HUE-1650 [beeswax] Add error message when no DB are available
* ca66ced HUE-1681 [core] set LOCALE_PATHS to remove deprecations
* 9af7880 HUE-1666 [beeswax] Saving a query after renaming revert the name change
* d18497e HUE-1609 [core] LDAP backend and import should be case insensitive when searching for users
* 662ae83 HUE-1681 [core] set LOCALE_PATHS to remove deprecations
* bb13694 HUE-1685 [search] Add tlong and int to range facets
* 408c7c5 [core] Trigger l10n
* 68c17b2 [doc] Update internal doc
* eeb0c77 HUE-1678 [search] Disable multiValued fields from sorting
* 030d2a7 HUE-1677 [core] Make SAML username source configurable
* 8c33d4e HUE-1638 [core] Secure database connection
* 87a90d6 HUE-1676 [core] Make SAML entity ID configurable
* 5e5b2f1 HUE-1675 [core] mysql extension needs an SSL fix for MySQL 5.5
* 45f4e07 HUE-1673 Make datetime fields unaware of timezones
* 99e8543 [doc] Adding ZooKeeper
* efd2cbf [core] Bump version to 3.5
* f473411 [beeswax] Install samples should not fail silently
* fe7e160 HUE-1641 [jb] Improve UX of non started job yet
* d7e0a4c HUE-1667 [hbase] Remember previously selected cluster
* 28b3819 HUE-1674 [beeswax] Query history search is broken
* 97f8263 HUE-1673 [core] Update desktop/settings.py to sync with django 1.4
* 64414f7 HUE-1641 [jb] Improve UX of non started job yet
* f6ad99e [metastore] Restore skipped tests
* f74687d [hbase] Does not support int rowkeys
* 73572ba HUE-1637 [metastore] Provide URLs for databases
* 5263869 HUE-1456 Better column type defaults in create table wizard
* 64b8e8a HUE-1671 [hbase] Sticky search bar is half hidden when scrolling up
* d4422d9 HUE-1669 [metastore] Drop table from the table view does not show a modal anymore
* 4db0343 HUE-1670 [metastore] Add icons to specific create table pages
* 022b44a HUE-1648 [beeswax] Navigator should fail gracefully in case a table has been deleted
* b742786 HUE-1508 [beeswax] Clicking on a name in Columns tab could go to the result column
* 3cc9c90 HUE-1661 [filebrowser] Change spacing of file details
* 5432b15 HUE-1662 [sqoop] Plus sign doesn't go to create a new job
* 3a603a0 HUE-1653 [core] Banner does not display properly
* f0f6c14 [core] Trash enabled info is wrong
* 8855024 HUE-613 [fb] Support snappy compression
* 04a21a4 HUE-1631 Fix oozie and pig tests
* ef9bc19 [beeswax] Update impersonation settings
* 13516c1 HUE-1631 [oozie] Support JobTracker HA in workflows
* f8aa93a HUE-670 [core] Hue should use connection pool to talk to webhdfs
* d446d5c HUE-1612 [jobbrowser] Browser needs minutes to render the page if you want to see many jobs (> 4000)
* a9974f2 HUE-1651 [doc] New user should have default tag selected
* 6ed1960 HUE-1649 [beeswax] Autocomplete error
* 2bfe602 HUE-1647 [oozie] Copy button response
* 76370ff [core] Minicluster doesn't use correct hadoop conf
* a751ed1 HUE-1642 [beeswax] Link to metastore table in navigator
* d3d32ca [impala] Fix auto complete bug
* 9058708 HUE-1645 [core] Multi select chooser has Move and Clean sections
* c38f0f7 [beeswax] My recently saved queries should only display my queries
* e149058 [search] Changing name of a collection gives a 500
* f6e1f13 HUE-1291 [beeswax] Saved queries should have filter for username
* 888d9cb [pig] Add test for whole log parsing
* 8e0583d HUE-1643 [pig] Progress does not update
* 44b77e9 [beeswax] Close queries command
* 445c2c2 [beeswax] Re-enable explain query tests
* 7953b1b HUE-1275 [metastore] Show table details
* 9987310 [core] Yarn mapreduce_shuffle renaming
* a3a8cfc HUE-1632 [oozie] Workflow with & in a property fail to submit
* 75983c2 HUE-1635 [hbase] Bulk load button does not show popup with FF
* 0fbb145 HUE-1634 [jobsub] Can't open a design by its URL
* 23ec4f3 HUE-1636 [oozie] Coordinators actions do not appear because of OOZIE-1481
* f7c9425 [beeswax] Make sure ';' is stripped when calling explain
* 26d43e9 [beeswax] Re-enable tests depending on configOverlay
* d00acd3 HUE-1630 [oozie] Dataset timezone not saved at creation
* ae790da HUE-1629 [core] Improve 'projects' section on home page if no projects are present
* 2cc6f18 [beeswax] Title of the table page changed
* ef93adc [beeswax] Update tests with latest HiveServer2
* 8449aa5 [oozie] Update section icons
* 54ca6d9 [metastore] Fix describe extended
* dce3b30 [metastore] Re-enable tests and fix HiveServer2 changes
* 9f51b6f [core] Adding HADOOP_HOME for Hive tests
* a2c5273 HUE-1565 [beeswax] Adding tests to multi partition support
* 80eda27 HUE-1565 [beeswax] PartitionValueCompatible: add multiple partitions support
* 253aac8 [sqoop2] sqoop server error handling
* 23009b0 HUE-1593 [jobbrowser] Exception when user is not allowed to view a job of another user
* 0b15066 [sqoop] Fix connection error handling
* bc7dae4 [jb] Red accepted to orange accepted state
* 4bd6aa1 HUE-1626 [beeswax] Create home directory of sample user
* f17718e HUE-1625 [jb] Make resource manager API dynamic
* be06349 [beeswax] Smarted magic table autocomplete
* 8019d16 HUE-1622 [core] Mini tour on home page
* e43e370 [beeswax] Use FQDN for the test server
* 50dad29 HUE-1599 [jb] Last progress precents fail to be displayed with MR2
* 4a08db2 [core] Reverse symlink order
* 6703884 [beeswax] Skip tests depending on HiveServer2 fix
* e0c7c39 HUE-1494 [beeswax] Re-enable Hadoop tests
* aaf0c75 HUE-1615 [metastore] Improve UX of breadcrumbs
* 07b037c HUE-1563 [search] Next button should not rely on cookie
* f4518f3 HUE-1623 [search] Show import collection error
* ff1476c HUE-1162 [oozie] Fix tests related to this change
* 3512002 HUE-1619 [beeswax] Autocomplete should include 'star' in field list
* 53e8edb HUE-1162 [oozie] Export oozie workflow
* 52e25f5 Revert "HUE-1604 [oozie] Jar path in mapreduce action and java action should use File arg"
* d9d3dfd HUE-1603 Rename of markdown files to .html fails for user guide
* c889137 [core] Skip test_error_handling test
* b46598b [core] Fix LDAP config
* 6117ca6 HUE-1616 [core] Diversify Oozie icons for dashboard and editor
* 2e84287 [beeswax] Fix permissions of auto queries not linked to a design
* e7d1584 [metastore] Adding icons
* 2a4e19d HUE-1566 [impala] Auto complete not wide enough
* 5200065 [impala] Impersonation support
* e33c265 [oozie] Remove leaked workflows from jobsub in tests
* 676698c [oozie] Fix typo in tests
* 6fb4d27 [core] Fix liboozie tests specific to MR1
* 443bec4 [oozie] Fix import workflow tests
* bf742c7 [oozie] Fix workflow with jar file tests
* 3097f25 [core] Fix add a tag
* 59a02b2 [hadoop] Set MR2 as default
* 2082484 [oozie] Fix import workflow tests
* 41cf6ee HUE-1594 [core] Revamp login page
* e1f292f HUE-1604 [oozie] Jar path in mapreduce action and java action should use File arg
* c80e424 [oozie] Get import workflow working again
* 2e3db58 [oozie] Fix permission tests
* 6870df9 [oozie] Fix submittion tests
* c9a068f [sqoop] Fix sqoop tests to work with upcoming sqoop 1.99.3 release
* f2a2ab6 [sqoop] Improve testing to show real error
* d2d9375 [jobbrowser] Refactor and fix tests
* 2e1ef2d [core] Small UX fixes
* af73c45 HUE-1607 Introduce sourceJavaVersion into Hue build
* fc73e85 [core] Update test cluster to Yarn and MR2
* 3e02523 HUE-1610 [core] Small screen support for navbar
* 055deed HUE-1606 [core] Current project tag
* 2dc8335 [core] Update SAML libs
* d951ada HUE-1606 [core] Improve logout pattern
* 0f3fb0d [beeswax] Improve double click in navigator
* a5d2058 HUE-1569 [beeswax] Table and fields helper
* 09f743b HUE-1587 [jobsub] Edit design by its id and not index
* 475c52f HUE-1241 [pig] Do not consider macro parameters as Pig parameters.
* 4ef020a HUE-1581 [jobsub] Saving a design clones it
* 2cf4732 HUE-1600 [core] Introduce tag counters for normal tags
* 252af7c HUE-1569 [beeswax] Table and fields helper
* 9b3f8df HUE-1596 [desktop] Create an examples tag
* a1ca5ec [core] Disallow TRACE and TRACK HTTP methods
* 4bfe98a [impala] Use DocModel API in the tests
* 2b4169b [core] Use cipher list to restrict ciphers used for Hue SSL
* 23933dd [core] Make search bind authentication optional for LDAP
* c52019c [doc] 3.0.0 release notes


Contributors
------------

This Hue release is made possible thanks to the contribution from:

- Aaron Newton
- Aaron T. Myers
- Abraham Elmahrek
- Aditya Acharya
- Alex Newman
- Andrew Bayer
- Andrew Yao
- Ann McCown
- bc Wong
- Ben Bishop
- Bruce Mitchener
- Bruno Mahé
- Eli Collins
- Enrico Berti
- Eric Wong
- Harsh J
- Henry Robinson
- Jon Natkins
- Kevin Wang
- Lars Francke
- Loren Siebert
- Marcus McLaughlin
- Mike Cotton
- Paul Battaglia
- Philip Zeyliger
- Romain Rigaux
- Roman Shaposhnik
- Shawn Van Ittersum
- Shrijeet Paliwal
- Thomas Aylott
- Todd Lipcon
- Vinithra Varadharajan

