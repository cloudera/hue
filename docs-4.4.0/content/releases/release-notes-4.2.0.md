---
title: "4.2.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -4020
tags: ['skipIndexing']
---

### Hue v4.2.0, released April 4th 2018

Hue, http://gethue.com, is an open source Analytic Workbench.

Its main features:

   * Editors for SQL querying (Hive, Impala, MySQL, Oracle, PostgreSQL, SparkSQL, Solr SQL, Phoenix ...) or job submission: Spark, MapReduce, Pig...
   * Dashboards to dynamically interact and visualize data with Solr or SQL
   * Scheduler of jobs and workflows
   * Browsers for Jobs, Metadata (Tables, Indexes, Sentry permissions) and files (HDFS, S3, ADLS)

Read the complete list of improvements on [Hue 4.2 and its Self Service BI improvements are out!](http://gethue.com/hue-4-2-and-its-self-service-bi-improvements-are-out/).


Summary
-------
The focus of this release was to keep making progress on the self service BI theme and prepare the ground for next release that will include an upgraded backend and a revamped Dashboard and more improvements to the Data Catalog and Query Assistance.
The release comes with a [Customer 360 demo](http://gethue.com/self-service-bi-doing-a-customer-360-by-querying-and-joining-salesforce-marketing-and-log-datasets/) showcasing the Editor to query credit card transaction data that is saved in an object store in the cloud (here S3) and in a Kudu table. The demos leverages the Data Catalog search and tagging as well as the Query Assistant.


Quality release

* No major core changes
* 200+ jiras / 100+ bugs

3 main areas of focus:

Cloud

* ADLS Browser
* Analytic DB

Top Search UX

* SQL Syntax checker
* Impala Query Browser

Supportability

* SAML update
* Documentation revamp
* Metric page


Notable Changes
---------------

Cloud

* ADLS Browser (similar to HFS & S3 Browser)
* Exploring ADLS in file browser
* Create Hive Tables Directly From ADLS
* Save Query Results to ADLS

Data Catalog Search

* Available in the top bar
* Since 5.11 but getting simpler
* Search Tables, Columns and Saved queries
* Example of searches:
** table:customer → Find the customer table
** table:tax* tags:finance → List all the tables starting with tax and tagged with ‘finance’

Syntax Checker

* Warn before executing
* Can suggest simple fix

Impala Query Browser

* Goal: built-in Troubleshooting for:
** Queries
** Profiles
** Plans
** Memory

Apache Solr dynamic Dashboards

* Dashboard autocomplete
* 'More Like This' functionality
* Collection page
 
Supportability

* SAML update (with idle session fix)
* Documentation revamp
* Thread page

Bug fixes

* UX improvements (document listing, opening back query history scroll, CTRL+Z...)
* Performances (concurrency, file downloads, query timeouts)
* Support multi-authentication with LDAP
* YARN "Diagnostics" info in Job Browser
* Option to disable concurrent user sessions "concurrent_user_session_limit"
* Rebalance user on log out
* Editor grid result not correctly aligned when browser zoom is not 100%


Compatibility
-------------

Runs on CentOS versions 5 to 6, Red Hat Enterprise Linux (RHEL 5, 6, 7), and Ubuntu 12.04, 14.04 and 16.04.

Tested with CDH5. Specifically:

- Hadoop 2.6.0
- Hive 1.1
- Oozie 4.1
- HBase 1.2
- Pig 0.12
- Impala 2.5
- Solr 4.10
- Sqoop2 1.99.5
- Spark 1.6

These minimum versions should work (not tested):

- Hadoop 0.20 / 1.2.0 / 2.0.0
- Hive 0.12.0
- Oozie 3.2
- HBase 0.92
- Pig 0.8
- Impala 1.0
- Solr 3.6
- Sqoop2 1.99.3
- Spark 1.4

Supported Browsers:

Hue works with the two most recent versions of the following browsers. Make sure cookies and JavaScript are turned on for the browser.

* Chrome
* Firefox LTS
* Safari (not supported on Windows)
* Internet Explorer / Edge

Hue might work with Chrome 23, Firefox 23, IE10, Safari 6, or older browser version, but you might not be able to use all of the features.


Runs with Python 2.6.5+

Note: CentOS 5 and RHEL 5 requires EPEL python 2.6 package.


List of 1200+ Commits
---------------------
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
* 4ac4f83 Fixing C6 build issue, pypi.python.org wants to enforce TLS 1.2 based requests. Hue uses pypi.python.org for python modules installation. This change contains two fixes.
* e06da4a HUE-8155 [metastore] Js typo in listing table popularity
* bc2655a HUE-8157 [search] Strip default. prefix of collection names when browsing them
* 75062dc HUE-8156 [search] Properly fill up data sample popup section with Solr
* 023af21 HUE-8095 [metadata] Fix entity boosting that was triggering too many matches
* 7eb49ee HUE-7989 [useradmin] Provide better UI message and message in logs when ldap server down
* be24b38 HUE-8104 [editor] FIX variables for new sample popup.
* e23a67a HUE-8153 [docs] Introduce tree and search on TOC
* 0e50cce HUE-8155 [metastore] Improve column and table lists in the table browser
* 78a7a92 HUE-8155 [metastore] General improvement of contents and layout of the table browser
* f4258c9 HUE-8075 [docs] Restructured documentation for editor export
* 76cf572 HUE-8123 [dashboard] Consolidate the resizing of widgets when dragging over the southern border
* 534fdb9 HUE-8123 [dashboard] Avoid horizontal double dropzones between widgets
* 152be3a HUE-8124 [dashboard] Horizontal dropzones should always be for the full row and not for the widget size
* fff06e5 HUE-8148 [dashboard] Fix dropping on the southern part of a widget
* d87627b HUE-8147 [metastore] Switch to knockout for handling the table browser tabs
* 0502076 HUE-8145 [metastore] Make sure partitions and samples are refreshed after pressing refresh in the table browser
* 9d07438 HUE-8144 [assist] Show the context popover footer open actions after navigating to tables and databases in the context popover
* 8cc0280 HUE-8143 [assist] Limit the column description length in the table context popover
* 5d06d0b HUE-8124 [dashboard] Improve weight of hover coordinates
* c5c7dc9 HUE-8124 [dashboard] Remove dropzones from the areas that don't have widgets
* b44d459 HUE-8023 [oozie] Weird styling on Oozie info page
* fdf3cdb HUE-8022 [jb] Oozie workflow text filter is too small or should be hidden in mini browser
* b8a7a35 HUE-8142 [assist] Limit the tags to two rows in the context popover
* da8ee1e HUE-8141 [dashboard] Hide the min count / HAVING option
* febed80 HUE-8138 [dashboard] List available fields depending on selected metrics for dimensions
* 3fd09eb HUE-8138 [dashboard] Fix dependencies after a dashboard reload
* 31000e1 HUE-8138 [dashboard] Add trackArrayChanges extension to the computed to make 'arrayChange' subscriptions work
* bbfe2e3 HUE-8138 [dashboard] Add metrics with compatible fields
* 7ae1de0 HUE-5969 [charts] Aggregation of line and bar chart
* c5b3af0 HUE-8137 [core] Refresh translations files for 4.2
* 54c8eae HUE-8136 [assist] Limit the description to two lines in the context popover
* 57be515 HUE-8135 [assist] Fix comment loading of multiple tables when a table has a custom name in Navigator
* 447e9d6 HUE-8131 [assist] Use plain text for column sample titles in the context popover
* 4bcf3a7 HUE-8130 [assist] Don't wait for navigator to load before showing the table in the context popover
* c68ff90 HUE-8129 [frontend] Reuse existing table samples for columns in the DataCatalog
* 90324e1 HUE-8134 [editor] Fix scroll of left side snippet buttons on chart view
* bbeb345 HUE-8132 [dashboard] Fix the page rendering on IE11 and Edge
* 8e0a86f HUE-8133 [dashboard] Maximize the grid space when loading a saved dashboard too
* 4a5f8b3 HUE-8125 [dashboard] Prevent JS error on hit widget delete
* 94cc5bc HUE-8114 [dashboard] Add helper arrows/pointers on an empty dashboard
* 7f5a2f2 HUE-8122 [dashboard] Resize siblings of the original position after a widget move
* 226903b HUE-8126 [dashboard] Improve dimensions dragging
* 9dbc495 HUE-8127 [assist] Fix issue where the context popover throws js error for complex entries
* dd4d212 HUE-8119 [frontend] Drop the border between search result entries in the top search
* 6343526 HUE-8121 [dashboard] Delete widget should be always available
* d9e49e8 HUE-8120 [dashboard] Ensure correct serialization of widgets on save and reload
* 9b8c7be HUE-8117 [editor] Horizontal scroll of the record popup is not reseted to zero on reopen
* 2992823 HUE-8113 [editor] Hide the dots menu on presentation mode
* c123ee0 HUE-8104 [editor] FIX variable selection in presentation mode
* 7a06d02 HUE-8089 [editor] Update last part of the test
* b9da528 HUE-8116 [frontend] Remove sorting of top search results from the UI to not interfere with backend sorting
* 2a90bde HUE-8115 [assist] Indicate which columns are partition keys in the context popover
* a76368d HUE-7980 [editor] The toolbar icon dropdowns should be aligned to the right to avoid horizontal scroll
* 753a233 HUE-8112 [legal] Order alphabetically the 3rd party UI libraries on Readme
* 5347930 HUE-8086 [core] Remove UI related logic and unused code from the ApiHelper
* 920816e HUE-8108 [assist] Make sure the spinner is shown in the context popover for huge tables
* 1b0cdb1 HUE-8107 [editor] Fix user variable type resolution in the editor
* 3558dee HUE-8097 [assist] Use the old context popover for Solr fields
* ac7d980 HUE-8098 [assist] Make sure empty rows have a fixed height in the context popover column samples table
* 2b9e873 HUE-8094 [assist] Display popularity in the SQL context popover
* 6fb2d1f HUE-8095 [metadata] Update test to take field boosting into account
* f9cfc8a HUE-8089 [core] Update Excel hyperlinking to be compatible with Python 2.6
* e05c470 HUE-8110 [core] Update integration test tarball to the latest version
* 0dc1d4f HUE-8105 [dashboard] Simplify the legend of the number of records in grid widget
* 8a1a8d4 HUE-8095 [metadata] Boost entities with non null important fields
* 098a743 HUE-8095 [metadata] Boost matching name, description and tags of entities
* 863c514 HUE-8086 [core] Unify sample data fetching with dashboards
* b99f14e HUE-8106 [editor] Convert fixed headers and column to a more performant CSS solution
* 3f8b0ee HUE-8109 [dashboard] Fix loading back a saved dashboard
* 0b6ff4a HUE-8104 [editor] Fix variables for new sample popup
* 50519ba HUE-8103 [dashboard] Dragging a top widget to the top widget bar shouldn't create a Gridster widget
* 0a88c77 HUE-8102 [dashboard] Empty widgets should have a dropzone on top too
* 53814ba HUE-8101 [dashboard] Adding a widget should trigger a resize on the window to recalculate the virtual Gridster grid
* 9764894 HUE-8100 [editor] Avoid stacked bar chart JS error on some resultsets
* dc7f14d HUE-8074 [charts] Better handling of more than a few legend items
* 35d45cd HUE-8080 [jb] Log more information when a job has expired
* 5b59c88 HUE-8096 [dashboard] Widget drag helpers should follow the page scroll
* 235f982 HUE-8088 [metadata] Prevent losing entity description when editing tags
* 8ace1ea HUE-8089 [core] Automatically add HYPERLINK to links in Excel downloads
* 326bd30 HUE-8093 [dashboard] Prevent moving of widgets on dimensions drag
* 5e34a69 HUE-8092 [frontend] Restyle selectize globally to avoid weird control heights in various apps
* 547cfc9 HUE-8092 [frontend] Move selectize specific CSS from global to editor
* 84e1559 HUE-8091 [frontend] Increase the data catalog version to support changes for cached samples
* f568120 HUE-8090 [assist] Move the context popover attributes for a column to the title
* 1778fa0 HUE-8075 [editor] Avoid a rendering error on the page if download_size_limit is not defined
* 62720b5 HUE-8062 [editor] FIX variables select alignment
* 1d8f809 HUE-8075 [editor] Offer a download_size_limit option for result download
* f802a72 HUE-8084 [dashboard] Enable the new drag system for the empty widgets too
* 0e0df28 HUE-8085 [dashboard] Support SQL ORDER BY for the grid widget
* d508358 HUE-7917 [frontend] New improved context popover for SQL entities
* 6f8e566 HUE-8083 [dashboard] Make cases of column types insensitive
* 2f85d4f HUE-8058 [dashboard] Prevent adding extra space when placing a Gridster widget
* 8294bf5 HUE-8078 [search] Add clearable to new dashboard selectized list of collections
* 7ba9511 HUE-8072 [assist] Generic empty message when there is no entries
* 94193c7 HUE-8078 [search] List proper aggregate function for the counter widget
* b08ce3c HUE-8078 [search] Prevent selecting a non dimension on the first widget
* 3dcac04 HUE-8077 [search] Avoid error with timeline widget and manual search returns no result
* 6d0acc1 HUE-8071 [dashboard] Rename widget bar to promote analytics functions
* 6fa46b7 HUE-8081 [frontend] Add clear button plugin to the Selectize binding
* 4e4850c HUE-8079 [core] Enable sync groups on login by default
* 8778ba6 HUE-8069 [core] Fix code format and exception logging
* e815c36 HUE-7946 [jb] Link to subworkflow on workflow dashboard page 404s in Hue 4 (Fix regression in Hue 3)
* 85cfbbc HUE-8069 [core] Pyformance reporter thread stops on exceptions in guage callbacks
* 4231267 HUE-8070 [dashboard] Properly try to display timeline data as timeline
* 7ee80bb HUE-8067 [dashboard] Avoid double execute call on SQL dashboard opening
* 33136fe HUE-8053 Fix unit test
* 10b4704 HUE-7945 [jb] Fix oozie launcher stderr log during state running
* e5d0c77 HUE-8066 [editor] Open query result in dashboard opens in importer
* dd6b3cd HUE-8021 [indexer] Support splitting a field with SOLR REST indexing
* 7032f5f HUE-8062 [editor] Variables polish: long values, squeeze, ordering
* 222e7f9 HUE-8063 [fb] Better error message when HTTPFS is not working
* 68b323c HUE-8053 [useradmin] LDAP authentication with sync_groups_on_login=true fails with KeyError exception
* 95e4234 HUE-8055 [desktop] Support multiple LDAP servers in LDAP Test command
* c11071d HUE-8061 [home] Moving document out of a folder does not refresh the list
* de6e53f HUE-8054 [dashboard] Allow to specify time in fixed time settings
* 60fdbe2 HUE-8056 [home] Move to trash refreshes the documents only on second time
* 201d811 HUE-8060 [dashboard] Show 'drag to move' title on the widget headers
* 25c9fbb HUE-8057 [assist] Make sure table popularity cache is cleared for parents
* 04606a1 HUE-8014 [core] Add test for /account/login
* 96e02fe HUE-8043 [editor] Cancel a query using ctrl-enter shortcut
* 806add3 HUE-8051 [dashboard] Recalculate Gridster size on left and right assist resize
* 432cef4 HUE-8049 [dashboard] Gridster shouldn't throw an error if trying to drop more that 4 widgets on a row
* bcbb954 HUE-8042 [editor] Avoid 500 error when the previous query handle was missing
* d2ad5a0 HUE-8042 [editor] Better prevention of double query submissions
* 6cd47e1 HUE-8048 [dashboard] Fix the initial grid calculation when opening a dashboard without reloading the browser
* d424f3a HUE-8046 [frontend] Improve the global search result list layout
* ce8785e HUE-8045 [editor] Prevent js exception from stale locations
* 73ddafd HUE-7949 [dashboard] Disable Gridster drag and resize when in Query Builder mode
* aade631 HUE-7949 [dashboard] Avoid triggering unnecessary window.resize events
* 9b34dc0 HUE-7949 [dashboard] Always show dimensions when in Query Builder mode
* ed85bd4 HUE-7949 [dashboard] Disable dropping outside an empty widget when in Query Builder mode
* bfb63c6 HUE-7318 [core] Hue doesn't let owners share document/directory if somebody else has a file there
* 6f945a8 HUE-8014 [core] FIX login cmf/systest
* a652bdc HUE-8029 [editor] Variable sampling can conflict with entered value
* 29fbdfe HUE-7985 [editor] Fix various syntax checker false positives
* 2d65298 HUE-8038 [assist] Fix js error in the context popover when showing the popover is slow
* ba0cdda HUE-8041 [editor] Editing a long saved query after a reload shouldn't expand the editor automatically
* 03ad5d9 HUE-8040 [editor] Avoid jumping on the initial loading of the query history
* e06921f HUE-7949 [dashboard] Disable widget removal when in Query Builder mode
* 77db9f1 HUE-7949 [dashboard] Remove plus button when in Query Builder mode
* 3c040f6 HUE-8037 [editor] Do not try to load past query history of a saved query
* 6b91a41 HUE-8037 [editor] Restore cursor position for query history only
* 4dc3485 HUE-7949 [dashboard] Only show dimension swapping icon when there is more than one
* f9055b6 HUE-8035 [core] Fix the broken tests related to check config
* 7100892 HUE-7949 [dashboard] Safety net avoiding loading back overlapped widgets
* ccfe80d HUE-7949 [dashboard] Update Gridster model after deleting a widget
* f910748 HUE-7949 [dashboard] Swap edit and move dimension
* a1ed144 HUE-8036 [presentation] Protect from storm of API calls when loading back a query with presentation
* fc01dcc HUE-8036 [hive] Properly log invalid query handle to be less confusing
* a71593e HUE-8032 [core] XSS in Hue Admin Interface
* 1b5ba3c HUE-7949 [dashboard] Fix UX of drag and drop of dimensions
* cb0c2ad HUE-7949 [dashboard] Avoid cleaning up occupied rows and remove autosizing when the widget is too big
* 0f2b60b HUE-7949 [dashboard] Reduce number of total available columns to speed up renderings
* f1fef91 HUE-7949 [dashboard] Increase default size of Text facet values when using gridster
* 5de8b8f HUE-8031 [core] Add connection ID to Thrift pool get logging
* c52ecd7 HUE-7949 [dashboard] Automatically resize also the widgets that have a lot of whitespace
* 6a3200b HUE-7949 [dashboard] Use the whole width of the page for the widgets after loading an existing dashboard
* aa08938 HUE-7949 [dashboard] Avoid scrollbars on text facets
* a45988e HUE-7949 [dashboard] Fix scroll and drag issues and visually hint while dragging where the widget is going to be moved
* da7c851 HUE-8031 [core] Also log slow REST calls
* a0ba2a1 HUE-8017 [core] Check config error on hue.ini validation check
* d906b38 HUE-8030 [core] Correct warning Thrift call delays to be in proper time unit
* 8868fb9 HUE-8030 [core] Log page hits on their return call so that they can be timed
* ffd7013 HUE-8030 [core] Only enable scheduler status polling when the integrated scheduler in on
* 3477cbea HUE-8030 [core] Properly log the analytics and error calls
* b767bd1 HUE-7949 [dashboard] Improved text widget filter display
* 08b1c4b HUE-8026 [indexer] Properly sort the list of indexes
* dde4c7f HUE-8025 [metadata] Do not show the deleted databasess/tables in the search
* 670a55f HUE-8001 [autocomplete] Improve ranking and select list suggestions
* 2fa3ad4 HUE-8028 [metastore] Make invalidate calls more specific when we know the specific database or table
* 7b4dd93 HUE-8027 [metastore] Fix for broken table page in the table browser
* 78bfffa HUE-7987 [autocomplete] Update the autocompleter and UDF library for Hive
* 7b3bc40 HUE-7253 [editor] FIX file download content-disposition test
* ed09de0 HUE-7941 [impala] Reset the status of the query link for new queries
* 2111965 HUE-8014 [core] Login with wrong password reloads page without message
* cacd698 HUE-8018 [assist] Refresh the right assistant when a catalog entry is refreshed
* 09d3f40 HUE-8019 [assist] Make sure cached only catalog requests don't affect the non cached requests
* 1cd10d5 HUE-8016 [notebook] Avoid to have function address in error log
* 5f4efa6 HUE-8015 [indexer] Set SQL NULL as Solr empty values so that rows with NULL cells are still indexed
* b07c20e HUE-8006 [home] Document sharing inconsistencies
* 541e5ea HUE-7758 [dashboard] Multi select and single select text facet
* 3e295ca HUE-7873 [core] Update the AutoComplete for Document share in /home page
* 36366c0 HUE-7253 [editor] Exporting results throws error if query name has comma
* 010eb96 HUE-7942 [editor] FIX variables with incorrect placeholder.
* 4b95d08 HUE-7848 [dashboard] Add widget's field list could present more metadata
* 493b7dd HUE-7990 [autocomplete] Don't show the comment in the autocomplete suggestion details header
* 2d43613 HUE-7982 [autocomplete] Give arrow key usage priority over mouse hover in the autocomplete suggestions list
* 5c43d83 HUE-8011 [editor] Fix the asterisk column expansion popover
* 08ac4b8 HUE-8010 [metastore] Load comments from the parent entry instead of for each table or column
* a31c47f HUE-8007 [frontend] Show a dropdown for facet values in the inline autocomplete
* 953d14f HUE-7986 [autocomplete] Update the autocompleter and UDF library for Impala
* 0b5ecb9 HUE-8009 [useradmin] Fix login page error for invalid local user when LDAP also enabled
* 7caaea6 HUE-8005 [core] Remove id search that was not used and could conflict with the home page folder
* 92ad84c HUE-7996 [editor] Fix height calculation of the history panel on reloading a saved query
* 40fa5f7 HUE-8002 [home] The new document icons should use the new SVG versions of them
* f0cc6fa HUE-7949 [dashboard] Set widgets previous sizes on right assist drag too
* e962bb6 HUE-7949 [dashboard] Avoid autoresizing widgets when dragging a new one or operating on the existing widgets sizes
* e13c571 HUE-7949 [dashboard] Remove the fake drop zone when dragging a Gridster widget
* 22d97e3 HUE-7996 [editor] Give a minimal height to the query history panel to cover the empty list content
* 0dd4175 HUE-8000 [dashboard] Do not use the layout with a right column when gridster is on
* c069c0f HUE-7999 [core] 'Collections' is still used in left assist and right assist instead of 'Indexes'
* 6eff97a HUE-7998 [editor] Add bit of styling to the click section of the inline help
* 5d0af64 HUE-7997 [backend] Python LDAP library exposes password
* adcd6cf HUE-7978 [dashboard] Saving dashboard via <enter> redirects
* b37f4db HUE-7984 [frontend] Improve the global search
* 4443a45 HUE-8004 [home] The document copy icon should have the same width of the other icons
* 84ff8ea HUE-7996 [editor] The history height calculation is wrong for multi line queries
* 9e63be0 HUE-7947 [dashboard] Ctrl-S does not work without changing collection
* 47a72a3 HUE-7981 [frontend] Move all the NavOpt popularity data for tables to the data catalog
* 7662377 HUE-7994 [frontend] Mitigate the propagation of the new common dashboard css to the other apps that use it
* 78a55f8 HUE-7949 [dashboard] Avoid breaking the dashboard if the collection name is missing
* a8b55d6 HUE-7949 [dashboard] Better align the save as dropdown
* d9ebce9 HUE-7949 [dashboard] Add no flex to the search bar operations to avoid horizontal scroll
* 4ec58d3 HUE-7945 [jb] FIX view logs of oozie workflow
* c245a4d HUE-7932 [oozie] Clicking on workflow with several decision nodes hangs Hue (Bugfix, fix Actions tab, rerun, incorrect 'Drop your actions here' message)
* 52312cd HUE-7955 [importer] Correctly convert SQL result column types to Solr types
* d67c6e2 HUE-7949 [dashboard] Turn on the new simplified layout
* 2c983dc HUE-7955 [importer] Hide query list in regular importer node
* ced6158 HUE-7992 [oozie] Big workflows show horizontally scroll in Hue 4
* aaef3f6 HUE-7983 [assist] Use the data catalog for the context popover
* 5dfaae9 HUE-7943 [editor] Variable list are not being refreshed
* d823dc2 HUE-6983 [jb] View Logs of a killed workflow gives 500 error
* 442e309 HUE-7947 [search] Use selectize for the list of collections
* 5590445 HUE-7913 [editor] Provide sample data for variables
* 3edf8e2 HUE-7949 [dashboard] Sync the position to the model on widget add and remove
* 0e00040 HUE-7949 [dashboard] Add correct app identifier for the widget size interval
* b8d3dc4 HUE-7888 [frontend] Override default BS2 navbar hover style and padding to align better the app headers
* 8061678 HUE-7979 [doc] Integrate Metric blog post to upstream documentation
* e454073 HUE-7975 [core] Open newly copied document (type: dashboard) throws error: HTTP ERROR 404
* 9118ce3 Revert "HUE-7680 [frontend] Get rid of the Nicescroll plugin"
* 2b7a19f Revert "HUE-7680 [frontend] Tone down the scrollbars for webkit browsers"
* 5c78dc5 Revert "HUE-7680 [editor] Fix scroll in autocomplete dropdown"
* bee50d7 Revert "HUE-7680 [frontend] Improve CSS on not-so-top-of-the-line screens"
* 97f9bc5 Revert "HUE-7680 [frontend] Fix overflow for the sample tables in the popovers"
* 6567d59 Revert "HUE-7680 [frontend] Get rid of the mCustomScrollbar plugin"
* 39acf41 Revert "HUE-7680 [frontend] Make horizontal scrollbars thin as well"
* 76be608 Revert "HUE-7680 [frontend] The custom Hue horizontal scrollbar should look and behave like the other scrollbars"
* b3e8763 Revert "HUE-7977 [editor] Use delayedOverflow for the results columns"
* e4b9d1b Revert "HUE-7888 [frontend] Override default BS2 navbar hover style and padding to align better the app headers"
* 44f0cbe HUE-7974 [metastore] Open Database location opens in Hue 3
* fc4a779 HUE-7888 [frontend] Override default BS2 navbar hover style and padding to align better the app headers
* e5f9869 HUE-7977 [editor] Use delayedOverflow for the results columns
* 166d8fb HUE-7680 [frontend] The custom Hue horizontal scrollbar should look and behave like the other scrollbars
* 1139ecd HUE-7680 [frontend] Make horizontal scrollbars thin as well
* a5cf75a HUE-7680 [frontend] Get rid of the mCustomScrollbar plugin
* ae18ac5 HUE-7680 [frontend] Fix overflow for the sample tables in the popovers
* 0bf366f HUE-7680 [frontend] Improve CSS on not-so-top-of-the-line screens
* 638a412 HUE-7680 [editor] Fix scroll in autocomplete dropdown
* 7b56ad4 HUE-7680 [frontend] Tone down the scrollbars for webkit browsers
* b1fcb13 HUE-7680 [frontend] Get rid of the Nicescroll plugin
* a0d9678 HUE-7949 [dashboard] Avoid collision of the remove icon with the resize handle
* b8eab9d HUE-7965 [docs] Explain Hue configurable SASL buffer size
* f10f149 HUE-7675 [core] Warn on startup for any invalid configurations in hue.ini (Step#2)
* c3dcfb5 HUE-7675 [core] Warn on startup for any invalid configurations in hue.ini (Step#1)
* 9a88856 HUE-7258 [jb] Fix fetching Spark job logs in Kerberized environment
* 0219bfc HUE-7945 [jb] Add oozie launcher job browser type
* b7db4b2 HUE-7973 [core] Do not error on home page when oozie is disabled
* 52729d1 HUE-7820 [metastore] Fix js error when two tables are equally popular in the table browser
* d8b5cec HUE-7972 [editor] Fix reporting of missing databases in the syntax checker
* 266665b HUE-7971 [editor] Make sure a database is set for column locations
* 2788d5e HUE-7969 [metastore] Only enable editing of database descriptions if navigator is enabled
* 364d29f HUE-7949 [editor] Hide modal after click to export to a collection
* 8e04493 HUE-7970 [assist] Open the last opened database in the assist for apps other than the editor
* 16f85a3 HUE-7969 [metastore] Enable editing of database descriptions in the table browser
* d2a2539 HUE-7968 [metastore] Disable the description HTML editor in the table browser
* 6fe1c9a HUE-7967 [metastore] Fix the context popover for tables and columns in the table browser
* 7ba06a2 HUE-7966 [assist] Show the correct comment for tables and columns in the context popover
* f1c8ca7 HUE-7949 [search] Avoid js error on facet click on non gridster dashboards
* 847b560 HUE-7949 [dashboard] Fix hidden x-overflow problems and autofit widgets over time
* c4a10db HUE-7964 [core] Do not crash on admin wizard page when oozie is blacklisted
* 56f5c5b HUE-7962 [assist] Show the comment in the title for entities if set
* 61b8c6b HUE-7949 [dashboard] Fix dropping of a widget on empty space
* 2ef0599 HUE-7961 [metastore] Make sure we always show at least 5 columns in the initial column list
* bbee6f5 HUE-7959 [metadata] Don't keep unused tags in the cache
* 368006f HUE-7958 [editor] Prevent cancelling assist API calls when the autocomplete results are closed
* 01cc62c HUE-7960 [editor] Fix issue where the autocomplete spinner sticks after cancelled requests
* 3f5e96a HUE-7957 [assist] Don't throw errors when a user doesn't have permissions for location updates
* 5ababfb HUE-7956 [assist] Disable the browser cache when the TTL is set to 0
* 8fa74cf HUE-7949 [dashboard] Furtherly stabilize resizing and re-ordering of the widgets
* 5b21b34 HUE-7949 [dashboard] Removed auto resize for any widget
* 89dd8c6 HUE-7949 [dashboard] Avoid shrinking empty widgets when hovering them
* 59363ee HUE-7955 [importer] Backend clean-up of the creation of an index via a live query
* 271f5c1 HUE-7955 [importer] Properly load the prefilling of other sources than manual or file
* 982874a HUE-7944 [editor] Provide an aync table sample api
* 7ea865e HUE-7940 [notebook] Backend linking to describe metadata of query documents
* d7a95b3 HUE-7955 [importer] Support indexing from a saved or history query
* 75941a8 HUE-7955 [importer] Move auditing code to main submit API
* 6ec5cc4 HUE-7955 [notebook] Add async to get sample data API
* 0e0a746 HUE-7955 [importer] Support saved SQL query as source
* ca25e37 HUE-7932 [oozie] Clicking on workflow with several decision nodes hangs Hue
* 1a50f51 HUE-7743 [frontend] Support initial URL search parameters in embedded mode
* d5e1399 HUE-7949 [dashboard] Correct Gridster seldom invalid calculation of widget heights after a resize
* 4e30213 HUE-7949 [dashboard] Enable auto regenerating of Gridster stylesheets to avoid invalid X widget sizes
* 26da50d HUE-7949 [dashboard] Remove widget border on hover
* ff88575 HUE-7894 [assist] Enable drop file into assist
* f74aaa4 HUE-7708 [indexer] Columns with parenthesis will fail to be importer into Solr
* 90f0ec1 HUE-7954 [metastore] Don't invalidate when opening the table browser from the left nav
* 554fae3 HUE-7952 [frontend] Only load comments from Nav for databases, tables and columns
* 8f7dabd HUE-7952 [autocomplete] Add a delay of loading the comments for the autocomplete suggestions if not already known
* 2d27ab2 HUE-7951 [editor] Properly handle complex fields in the assist and autocomplete suggestions
* f96b563 HUE-7950 [assist] Clear all tables cascaded when refreshing a DB in the assist panel
* 872253b HUE-7948 [assist] Check the database metadata before loading tables in the right assistant
* 119d9db HUE-7949 [dashboard] The main page droppable should accept just some specific draggables
* c418edf HUE-7949 [dashboard] Prevent a JS error on non-Gridster dashboards
* 9a9638b HUE-7949 [dashboard] Avoid scrollbars on the widgets with charts
* 2133514 HUE-7949 [dashboard] Show dimensions just on widget hover
* 371b786 HUE-7949 [dashboard] Move Gridster draggable handle to the widget title
* fc76192 HUE-7946 [jb] Link to subworkflow on workflow dashboard page 404s in Hue 4
* 41a517f HUE-7860 [core] Add SSL/TLS support for Gunicorn
* 204dc48 HUE-7940 [dashboard] Initial support for queries in the right assistant panel
* fe0b8d8 HUE-7921 [editor] Allow opening of an editor after landing on a non-existing/non-viewable document
* 49b398b HUE-7938 [dashboard] Improve dimensions editing UX
* 3ed4716 HUE-7939 [metastore] Make sure the metastore is refreshed after creating tables or databases
* 053ca72 HUE-7820 [assist] Only refresh the open SQL entity in the assist panel
* bc92b80 HUE-7933 [dashboard] Enable autocomplete of values after whitespace
* 817bc22 HUE-7937 [dashboard] Show widget side menu just on hover
* 9f994c0 HUE-7936 [dashboard] Editing a Gridster dashboard should have the delete icon too
* 403495e HUE-7926 [dashboard] Improve drop preview to build a better user anticipation
* 4408ec0 HUE-7931 [dashboard] Comment missing facet option as not finalized
* 02cd20e HUE-7935 [metadata] Force put call to Navigator to send json mimetype
* 38fe673 HUE-7928 [metastore] Config flag to force metadata calls to go to HiveServer2
* b1b0938 HUE-7934 [importer] Unselecting has Header checkbox has no effect
* 1559c52 HUE-7931 [dashboard] Hide sorting icon of hit widgets
* 4ad5940 HUE-7931 [dashboard] Feature flag for widget filter and compare
* 419b75f HUE-7931 [dashboard] Counter widgets should have one editable dimension
* 13a2d60 HUE-7931 [dashboard] Restrict resizing to horizontal only
* f09cd16 HUE-7931 [dashboard] Rename add widget HTML title
* d372737 HUE-7924 [dashboard] Fix JS errors on drag and remove on the old layout mode
* 54f54ee HUE-7924 [dashboard] Make old and new layout modes co-exist
* de2cdff HUE-7929 [indexes] Field list table on the index page should have an horizontal scrollbar
* 9d674ef HUE-7925 [frontend] Remove unnecessary imports on the login page
* 411aaf6 HUE-7927 [metastore] Sample view on the main table page should have an horizontal scrollbar
* 3a3b13a HUE-7920 [frontend] The stacked graph shouldn't have empty areas in the stacks
* a64b558 HUE-7853 [editor] Changed help dialog title + link to online doc
* 36615ab HUE-7882 [dashboard] Make pretty metrics available to non-gridster dashboards too
* da5872c HUE-7882 [dashboard] Add pretty metrics to the other widgets too
* efdb33a HUE-7882 [dashboard] Prettify and simplify the edit/non-edit modes
* 9689915 HUE-7892 [metrics] Show a message when there are no filtered results in the 'All' section
* 1d1118b HUE-7918 [presentation] Exiting resets the query type to the first editor language opened
* 7e6a63f HUE-7918 [presentation] Menu in mode should still show up even if the query is not saved yet
* 93abf9c HUE-7916 [frontend] Avoid breaking of scatterplot chart for some grouping values
* 62cf649 HUE-7860 [core] Integrate non IO blocking Python Webserver   Add runserver command
* 167bb90 HUE-7860 [core] Integrate non IO blocking Python Webserver   Add eventlet 0.21.0 and enum-compat 0.0.2
* 76ad046 HUE-7860 [core] Integrate non IO blocking Python Webserver   Add greenlet 0.4.12
* 8f18ecd HUE-7860 [core] Integrate non IO blocking Python Webserver   Add gunicorn 19.7.1
* b3de898 HUE-7909 [editor] Hide options in session settings
* 0b0783a [core] Hiding most of the unused metrics on the Metrics page
* 36dcfda HUE-7820 [assist] Fix js error in the context popover for databases and columns
* a1c726d HUE-7820 [metastore] Don't refresh the analysis on load and load DB metadata via the DataCatalog
* d784df1 HUE-7915 [assist] Increase the frontend cache TTL to 10 days
* 1380500 HUE-7820 [metastore] Use the DataCatalog for the tag editor
* 3000dc4 HUE-7907 [frontend] Improved dropped areas for side widgets and new rows
* 9244fa2 HUE-7907 [frontend] Dropping on overflowing widgets should create a new widget too
* cdbe953 HUE-7907 [frontend] Create a fix for the .droppable binding missing event handling
* c597cd7 HUE-7911 [hbase] HBase browser create table js error
* 80a6c7d HUE-7913 [autocomplete] Report quoted variable locations with possible column references
* fb32aef HUE-6722 [jb] Task progress shows as 1 and not 100%
* 59d68ad HUE-7846 [dashboard] Remove duplicate keydown bindings
* ef85ecb HUE-7914 [editor] Remove duplicate ID from the save results and download form
* 5c77f46 HUE-7913 [autocomplete] Pair variable locations with columns where possible
* d606ec6 HUE-7913 [frontend] Fix failing jasmine tests
* c8bcf48 HUE-7913 [autocomplete] Add variable locations to the autocomplete parser
* 6a0d28c HUE-7459 [jb] YARN Metadata job page can freeze when huge
* 41512b0 HUE-7142 [jb] Job log links to HDFS path opens on Hue 3
* 04ca6db HUE-7876 [presentation] Persist isHidingCode setting
* dbdd4a8 HUE-7876 [presentation] Switch to presentation mode when opening a presentation query
* 3925fa7 HUE-7876 [presentation] Editor should not convert to Notebook in presentation mode when saving
* bf8494d HUE-7876 [presentation] Group the default toggle action inside the presentation mode
* a74fe29 HUE-7876 [presentation] Allow to publish presentation mode turned on
* f8114cc HUE-7876 [editor] Move isPresentation subscription to the Notebook
* 07cd46f HUE-7876 [presentation] Persist when the document is in Presentation mode
* 3f02a89 HUE-7876 [presentation] Only hide right assist when toggling on
* d2c36cf HUE-7876 [editor] Refactor editor menu action into a template
* 2579ac5 HUE-7912 [jb] Hide some properties in mini browser mode of Query Browser to make some space
* c0e4c4c HUE-7910 [editor] Improve readability of the new inline help
* 63c94b8 HUE-7820 [assist] Don't fetch navigator data for children that already have it
* 9737aec HUE-7820 [assist] Fix issue where some columns won't expand in assist
* 2c5825c HUE-7820 [frontend] Silence errors from Navigator and NavOpt by default
* 64b8c72 HUE-7820 [metastore] Load metadata in parallel in the table browser and use the DataCatalog for navopt details
* f9d2a42 HUE-7820 [frontend] Add NavOpt table details metadata to the DataCatalog
* 4243331 HUE-7820 [metastore] Use analysis from the DataCatalog in the table browser
* b702995 HUE-7820 [frontend] Add analysis to the DataCatalog
* 45c11ad HUE-7820 [metastore] Only refresh the open entity in the table browser instead of refreshing everything
* f7d408f HUE-7820 [frontend] Add pubsub to refresh a particular catalog entry
* 7f98468 HUE-7820 [frontend] Add versioning to the DataCatalog and debug helper
* 05492f2 HUE-7822 [core] Unable to clone oozie workflow in Hue 4.0
* d77ed0f HUE-7906 [dashboard] Fix new dashboard creation
* 4315b02 HUE-7908 [frontend] Fix spinner overlay z-index
* 1a16bf6 HUE-7877 [dashboard] Support a query history from a multi statement query
* da6c018 HUE-7907 [dashboard] Remove whitespaces on widget drag, resize, remove and add
* 99ebe47 HUE-7907 [dashboard] Introduce helper to clean the Gridster whitespace
* 68dc4e2 HUE-7907 [dashboard] Fix alignement of layout boxes
* d54f0f4 HUE-7907 [dashboard] Removing a widget should automatically resize its siblings
* 4afd275 HUE-7907 [dashboard] Recalculate grid base width on window resize
* 934883c HUE-7901 [editor] Query History search make the scrolling jumps back to the top
* cfc75f7 HUE-7900 [hbase] Switch to Thrift transport default to use framed instead of buffered
* d49d443 HUE-7853 [editor] Add help section for syntax
* c08884e HUE-7898 [editor] Impala query expiration shows update max_row_size help
* 41a7733 HUE-7889 [frontend] Remove html page source from the notifications
* 61c8021 HUE-7895 [editor] Give the user a feedback of editor loading when opening an assist document
* 8510c85 HUE-7820 [metastore] Use the DataCatalog in the table browser
* 466f504 HUE-7820 [frontend] Add navigator tag add and delete operations to the DataCatalogEntry
* bc8eb74 HUE-7743 [frontend] Fix js error when the IS_EMBEDDED flag isn't defined
* 8767987 HUE-7899 [hbase] HBase django.po file translation error (#649)
* b960875 HUE-7893 [docs] Fix navbar overlap with the content
* 5138cdf HUE-7897 [doc] Integrate Solr wine blog post into the docs
* 3df6108 HUE-7897 [doc] Add more info about Solr Sentry privileges
* 2a51f61 HUE-7884 [jb] Lighten up the border of the query graph and use the CUI colors
* c48baa6 HUE-7883 [jb] Restyle queries side panel to look like the other sections
* 6b05c0f HUE-7886 [dashboard] Fix misplaced global JS variable in the common dashboard
* 5f1ba79 HUE-7820 [assist] Fix js error in dashboard assistant
* cc2731e HUE-7820 [assist] Fix broken context menu for SQL assist entries
* 4532667 HUE-7820 [assist] Don't show the comment in a tooltip on hover
* e5fe532 HUE-7820 [autocomplete] Use the data catalog mini context panel to show the proper comments for autocomplete suggestions
* 143c693 HUE-7820 [autocomplete] Add a component to show a mini context panel for a catalog entry
* 462f4c5 HUE-7820 [autocomplete] Use the DataCatalog for the autocompleter
* b926031 HUE-7820 [frontend] Add option to load navopt column meta for multiple tables in one go
* fb89e45 HUE-7743 [frontend] Make sure we remove /hue in embedded URLs
* 71526e1 HUE-7743 [frontend] Fix js error when executing multiple statements in embedded mode
* 557071a HUE-7820 [frontend] Use IndexedDB instead of TotalStorage for the DataCatalog
* 57bf075 HUE-7820 [frontend] Add LocalForage library for managing indexedDB requests
* a1f8e00 HUE-7820 [frontend] Add navopt metadata to the datacatalog and make all promises cancellable
* f6a9f53 HUE-7820 [frontend] Add sample to the data catalog entries
* 6ca38e0 HUE-7743 [core] Automatically use Impersonation backend when in embedded mode
* 3c86fa9 HUE-7874 [oozie] SSH action missing configuration for retry-max and retry-interval
* 6e83146 HUE-7861 [jb] Handle Impala query timeout
* 6a727cb HUE-7880 [editor] Improve spacing of chart settings labels
* 0e16243 HUE-7881 [core] Fix font loading problems that affect the autocompleters
* 0af18ca HUE-6838 [jb] Show confimation dialog when killing jobs
* 95c3572 HUE-7875 [dashboard] Properly set the source of the data collection
* 10739a0 HUE-7870 [dashboard] Improve reliability of Gridster smart placement of widgets
* 605970e HUE-7875 [dashboard] Update tests about edit record permission being available to anyone
* 87a340a HUE-7877 [dashboard] Automatically give a friendler name to SQL sub query dashboards
* ce8cfa4 HUE-7877 [hive] Move subquery table to the core HiveServer2 API
* 8a83aa7 HUE-7877 [dashboard] Automatically pull SQL statement of query history
* ef97728 HUE-7877 [dashboard] Plug-in subquery metadata and submission logic
* 74d800e HUE-7877 [dashboard] Add Explore from SQL step 2
* df2c3d8 HUE-7877 [doc] Bumping-up who is using Hue section in README
* f561697 HUE-7877 [editor] Preparing getting metadata of a sub query
* 38ad27d HUE-7877 [assist] Remove right click to open collection page
* ea21ccd HUE-7877 [reporting] Skeleton for creating a new report
* 7fc5cd0 HUE-7833 [doc] Add analytics to pages
* 8b511ab HUE-7878 [hbase] Avoid throwing a JS error when the server is not reachable
* dca1c56 HUE-7879 [core] Avoid leaking of Security CSS into Hue
* 92ed35e HUE-4627 [editor] Re-organize and rename Save query to Export results
* d1212ed HUE-7875 [dashboard] Add links to column results starting with http or https
* d65511e HUE-7875 [dashboard] Only show edit document when the source as a PK
* 03cdf8f HUE-7875 [dashboard] Better experience when trying to retrieve a table document with no PK
* ab5441d HUE-7875 [dashboard] Remove reporting from new layouts and add empty middle row
* 0ab39b4 HUE-4627 [editor] Show download result icon on page refresh if query is not expired
* 9d82a81 HUE-7858 [dashboard] Improve default height for the counter widgets
* 4bf035c HUE-7871 [dashboard] Set a min length for the search bar to avoid its disappearance
* ad4b99e HUE-7833 [doc] Smaller font for the tables
* fc8123a HUE-7833 [doc] Explain how to manually change the language
* 21203bd HUE-7859 [dashboard] Remove error message when stats not supported
* 7b75742 HUE-7757 [dashboard] Text label for older saved dashboard
* 9dc17d4 HUE-7866 [dashboard] Limit width of dashboard name
* 105bbed HUE-7868 [core] Change successful logins to log at INFO (#646)
* dbb640e HUE-7856 [dashboard] Add dropzones around each widget
* bac8a5c HUE-7869 [dashboard] Avoid dropping of a widget on an invalid grid position
* b0f70ff HUE-7843 [editor] Improve UX of the grid results renderer
* 243604c HUE-7847 [search] Show PK field in the right assist
* 1b65ad8 HUE-7732 [editor] Change select variables from datalist to selectize
* de3a280 HUE-7865 [autocomplete] Show the complete sample value in the details panel for long values
* 7065306 HUE-7820 [assist] Show the proper database comment in the context popover
* b08af64 HUE-7864 [assist] Open top search document folders in the assist instead of home
* 8a22023 HUE-7820 [assist] Fetch navigator metadata for databases
* 1aaebb7 HUE-7820 [assist] Show comment tooltips for entries in the left and right assist
* 5681886 HUE-7820 [assist] Use the new data catalog for the left and right assist trees
* 355d3c2 HUE-7820 [metadata] Refresh the navigator cache after setting the comment
* 041a860 HUE-7820 [metadata] Introduce a generic data catalog that handles metadata for any datasource
* 3110e9e HUE-7820 [metadata] Properly update entities properties or custom metadata
* f123bed HUE-7820 [core] Add ability to load navigator metadata for all children of a sqlMetadata instance in one go
* 74d6c54 HUE-7820 [metadata] Allow raw querying of the navigator entity search API
* ca38d90 HUE-7820 [core] Add ability to set comments through the sqlMetadata object
* 9c3773e HUE-7820 [core] Introduce a comment observable in sqlMeta
* 70a6ff0 HUE-7820 [core] Add Navigator metadata to the sqlMetadata object
* 5ed9719 HUE-7820 [core] Introduce a generic sqlMetadata object
* 2dc34be HUE-7743 [frontend] Use hash-based page routing in embedded mode
* e014910 HUE-7863 [dashboard] Remove duplicate element IDs
* b18e4a5 HUE-7846 [dashboard] Left align dashboard save as input
* 29ffa48 HUE-7857 [dashboard] Auto resize current widgets when dropping on the same row
* b456fc3 HUE-7756 [search] Do not break filtering when a selected value is a False boolean
* abf0421 HUE-7728 [jb] Do not error in the SQL query browser when pointing to an old Impala
* 20fc449 HUE-7855 [editor] Fixed JS error on subscription removal
* 8c9487d HUE-7855 [editor] Disable the editor auto-resize when running a saved query
* 5f475f7 HUE-7852 [core] Metric page fails on cherrypy server
* ffb525e HUE-7743 [core] Directly fails with 403 in embedded mode if not logged-in
* bfc66f1 Revert "Revert "HUE-6909 [libsentry] Use the new sentry config property sentry.service.client.server.rpc-addresses""
* af45f8b HUE-7854 [core] Update translations files for 4.2
* 283511f HUE-7846 [dashboard] Save as button rounded corner + save as shortcut
* 4c082bf Revert "HUE-7758 [dashboard] Allow to collapse facets"
* 46c49e2 HUE-7757 [dashboard] Give a text label to the dimension
* d5b32ce HUE-7732 Support CTRL + S when inside a variable input
* 6b5d951 HUE-7743 [frontend] Hide the top nav bar in embedded mode
* f0c1912 HUE-7743 [editor] Don't show the query name and description in embedded mode
* e7f99d4 HUE-7743 [frontend] Revert param-based page routing in embedded mode
* acf18ad HUE-7743 [frontend] Hide table browser links in embedded mode
* bf95f9b HUE-7743 [frontend] Disable documents in embedded mode
* 26f8443 HUE-7832 [assist] Allow filtering in the document types drop-down
* b1700d6 HUE-7743 [frontend] Also adapt img src urls in embedded mode
* 8229dcb HUE-7851 [dashboard] Collection not always refreshed when creating a new dasboard
* b8f9ea8 HUE-7850 [editor] Presentation mode will fail if past queries are expired
* 4449d14 HUE-7849 [search] Support selection on pie chart of two dimension facet
* 4ded863 HUE-7849 [search] Fix slecting one value in graph of one dimension
* d2ddf63 HUE-7849 [search] Support same aggregate in different dimension
* e0aa618 HUE-7849 [search] Correctly support selecting values in N dimensions with N aggregates in between
* 5ae36d2 HUE-7849 [search] Support having aggregates between two dimensions
* bb3dbcc HUE-7846 [dashboard] New dashboard should be proposed to be 'saved as'
* 1f3ffd6 HUE-2902 [hive] Temporary skip top_term test as slow and API is not used
* fcad3b4 HUE-7654 [core] Integrate Threads page as page on /about page (Fix test)
* f6937f7 HUE-7774 [core] Increase the limit of User and Group list in Hue Autocomplete box
* 8ea38e0 HUE-7833 [doc] Add more description to the data import wizard
* e014b3f HUE-7800 [core] Remove Flash of Unstyled Content in loading the apps
* 03a5228 HUE-7845 [editor] Get rid of printing specific CSS
* 397498e HUE-7844 [editor] Fix rendering of barcharts when the first value is missing
* 7186d69 HUE-7812 [core] Metrics and Threads page don't get refreshed Step #2(loadApp)
* b0cfa09 HUE-7258 [jb] Fix test_spark_job in TestMapReduce2NoHadoop
* 2e9e60f HUE-7827 [search] Switch to fuzzy matching for autocomplete term search
* 45619c3 HUE-7842 [dashboard] Avoid extra search call when dropping a new facet in a new row
* b3651a4 HUE-7839 [dashboard] Support the new counter form in SQL
* 0001d64 HUE-7838 [dashboard] Support select on 2 dimension in SQL
* b511ea5 HUE-7833 [doc] Add more information about how to reset a password
* aab4a5c HUE-7837 [presentation] Toggle hiding/showing the code snippets should also hide the log panels
* 0c45219 HUE-7832 [editor] Show query document link with link handle on hover
* ee50ae6 HUE-7812 [core] Metrics and Threads page don't get refreshed Step #2(loadApp)
* d7218b6 HUE-7812 [core] Metrics and Threads page don't get refreshed Step#1(Threads Only)
* 06ecb02 HUE-7835 Add hive/impala HA configure post content
* 33e96e1 HUE-7834 [search] Facet download when no fields are selected fails
* 87d8dd3 HUE-7836 [frontend] Fix for mini job browsers not showing any contents
* 8aca6af HUE-7832 [frontend] Use the assist to list app specific documents throughout
* 96e8157 HUE-7832 [editor] Show editor documents in the left assist instead of home
* 6beb7fd HUE-7832 [frontend] Extract a global list of available document types
* 96aa933 HUE-7832 [frontend] Add a publish KO binding to publish to huePubSub on click
* 8bc0e43 HUE-7833 [doc] Adding link to Impala and HiveServer2 configuration post
* 37dd5b9 HUE-7833 [doc] Moving hue specific configs into the same section
* f5dd702 HUE-7646 [sentry] Changing role privileges removes HDFS ACLs
* dc05d52 HUE-7258 [jb] Properly fetch YARN Spark job logs
* c348711 HUE-7831 [search] Make sure we invalidate the record cache when enabling More like This
* 900048e HUE-7831 [search] Offer more like results
* 0d09d5a HUE-7827 [search] Case insensitive term search for the autocomplete
* db38f4b HUE-7827 [search] Perform term search in a distibuted way if available
* efd42f5 HUE-7830 [core] Non supported feature use_default_configuration doesn't work in Hue 4
* ed06952 HUE-7743 [frontend] Prevent js error on empty stylesheets in embedded mode
* 6a2fd64 HUE-7743 [frontend] Detect hash changes and abort page.js routing in embedded mode
* 3e50917 HUE-7743 [frontend] Adjust top-nav z-index for embedded mode
* 87ffd05 HUE-7743 [frontend] Allow any URL base path in embedded mode
* 79f46604 HUE-7743 [metastore] Use the app parameter for table browser navigation in embedded mode
* e059c6b HUE-7743 [frontend] Use parameter based page routing in embedded mode
* 6524298 HUE-2890 [doc] Correct a series of links
* df420b2 HUE-2890 [doc] Update README to point to the documentation
* 8823770 HUE-2890 [doc] Include all the last recent blog posts into the documentation
* 8c4a007 HUE-2890 [doc] Revamped hierarchy of user guide again
* a2e2c37 HUE-2890 [doc] Integrate back some information from the blog into the docs
* b531763 HUE-2890 [doc] Use proper hierarchy in admnistration section
* 026ef5f HUE-2890 [doc] Clean-up SDK hierarchy
* 1c0c9be HUE-2890 [doc] Move manual to its own Admin manual section
* a1ab3b2 HUE-2890 [doc] Remove old repo file and references
* da3f3d3 HUE-2890 [doc] Merge dev doc to SDK doc
* 0452cce HUE-2890 [doc] Clean-up old SDK
* 5b12646 HUE-2890 [doc] Revamp of the user guide
* cbc3318 HUE-2890 [doc] Clean-up of the user-guide
* afde680 HUE-2890 [doc] Clean-up of the manual
* cf1ee36 HUE-7820 [metastore] Skeleton call to fetch a batch of columns with metadata comment of a table
* 5cdae7e HUE-7820 [metastore] Disable lineage fetching for now as not displayed
* b0b8425 HUE-7820 [metadata] Add helper to fetch metadata of a query
* 1476349 HUE-3439 [indexer] Metadata does not show if the termVectors are stored for a field
* 6eb4399 HUE-7829 [useradmin] Fixed error in message about LDAP users/groups being successfully synced
* 56b8037 HUE-7826 [security] Uncaught TypeError: privilege.privilegeScope is not a function error when deleting a Solr privilege
* 8931b28 HUE-7825 [sentry] Integrate new 'admin' Sentry Solr permissions
* cbc2911 HUE-7824 [metastore] Hide table or DB location links when in embedded mode
* 4a4229f HUE-7823 [core] Remove data search text from top search if metadata is not enabled
* 501db18 HUE-7807 [core] Add an ImpersonationBackend
* 4619cb2 HUE-7743 [frontend] Allow adaption of clearable background image in embedded mode
* 48a7b10 HUE-7743 [frontend] Disable Google Analytics tracking in embedded mode
* b140690 HUE-7743 [editor] Improve positioning of close button for presentation and full screen results in embedded mode
* 4ff701e HUE-7743 [frontend] Append popovers to the Hue container in embedded mode
* f4cb026 HUE-7816 [frontend] Use the Hue version as a parameter instead of a random number to control caching of non-static resources
* 38b49aa HUE-7803 [jb] Missing import causing global name 'LinkJobLogs' is not defined
* 9d7487e HUE-7819 [metastore] Update table comment to metadata server if available
* ba21678 HUE-7713 [importer] Avoid printing Skipped records warning by mistake
* f6f14cd HUE-7758 [dashboard] Allow to collapse facets
* f101969 HUE-7818 [search] Range facets and up support for timelines and bar charts
* 262375a HUE-7815 [dashboard] Pie charts should support numerical range faceting
* 5a778e6 HUE-7815 [dashboard] Field type of a numeric range facet disappears
* 842db9e HUE-7743 [frontend] Make sure modals open correctly in embedded mode
* 59dff8b HUE-7743 [frontend] Make sure the top search results are positioned above the page contents in embedded mode
* 452e7a5 HUE-7743 [frontend] Use fixed font size for the context popover title
* 10d686b HUE-7743 [frontend] Default to no navbar padding in embedded mode
* 8bfb942 HUE-7743 [frontend] Use content-box as default box-sizing in embedded mode
* cb7b7e8 HUE-7743 [editor] Enable webworkers in embedded mode
* f1c784c HUE-7743 [frontend] Update third-party licence details
* 103b6b8 HUE-7743 [frontend] Only use knockout deferred updates when supported
* fa5e2ad HUE-7743 [frontend] Load all scripts synchronously before appending the app page contents
* da944cc HUE-7743 [frontend] Don't adjust all links in embedded mode to /hue
* c4c9cc1 HUE-7813 [useradmin] Add login dropdown when there is only one item
* 3da1466 HUE-7756 [dashboard] Add other as facet option
* d78f992 HUE-7810 [oozie] Fix Dashboard ignores ACL permissions (#638)
* 3c17aaa HUE-7809 [reporting] Missing : in mako templat breaking the page
* cde0278 HUE-7755 [oozie] Adding Distcp arguments and properties
* a8a5699 HUE-7776 [dashboard] Move Solr exceptionextractor to the model to avoid import conflicts
* 15fec8d HUE-7808 [editor] Solr icon for Solr SQL
* 5539bf5 HUE-7808 [editor] Properly bubble-up errors in Solr SQL queries
* faeb234 HUE-7766 [search] Add query facet filter to counter widgets
* 8c4b41e HUE-7766 [dashboard] Query facet for widget level filtering
* 7cfcda1 HUE-7766 [dashboard] Move counter display into its own template
* fffd242 HUE-7766 [dashboard] Do not error when using a timeline and rolling window
* d6135f4 HUE-7766 [dashboard] Return 0 instead of null when no data for textSqueezer for now
* 131fc3e HUE-7766 [dashboard] Skeleton to compare with past data intervals in counter widget
* c945456 HUE-7766 [dashboard] Comparison with previous time facet option
* 1c68cf7 HUE-7809 [reporting] Adding Counter widget as a graph option
* 79b1694 HUE-7809 [reporting] Skeleton of independent SQL widgets
* f4bc273 HUE-7809 [reporting] Add report into Dashboard submenu
* ae5fa81 HUE-7806 [core] Show all the users "Switch to Hue 4" option
* 9c7dfee HUE-7805 [impala] Lower idle session timeout from 1 hour to 30 minutes
* 34b2fe6 HUE-7803 [jb] Remove references to MR1 in the tests
* 37fa3f1 HUE-7794 [fb] Modify/upload file failed if S3 bucket encryption is SSE-KMS
* 004deab HUE-7803 [core] Remove old imports to JT and NN plugins in minicluster
* dd5fd49 HUE-7743 [frontend] Allow custom page mappings in embedded mode
* fb699bb HUE-7743 [frontend] Make sure sidebar templates won't conflict in embedded mode
* 4d7922f HUE-7743 [frontend] Allow a different page.js base for embedded mode
* 7e915cb HUE-7743 [frontend] Add missing import to the editor page
* c521bfd HUE-7743 [frontend] Add page.js as a separate dependency in embedded mode
* 8751d37 HUE-7743 [frontend] Disable web workers in embedded mode
* 6f06bb0 HUE-7743 [core] Fix issue where collectstatic fails because of missing files
* cf8f56a HUE-7803 [jb] Remove old reference to hadoop gen-py lib
* 652ce7e HUE-7803 [jb] Remove old call to java tests in Makefile
* 5746e0f HUE-7803 [jb] Remove old references to MR in hue.ini
* c6be075 HUE-7803 [jb] Update through Hue to remove JT references in code path
* 2ec5604 HUE-7803 [jb] Remove Job Browser API for MR1
* cdaaaea HUE-7803 [core] Remove notion of MR_CLUSTERS
* 70d2f57 HUE-7803 [core] Remove deprecated JobTracker Python class
* 71cfd66 HUE-7803 [core] Remove deprecated HadoopFileSystem Python part
* 2bd88b5 HUE-7803 [core] Remove old maven references to the Hadoop plugins
* 08c980f HUE-7803 [core] Remove old Thrift Hadoop libs
* 79189b9 HUE-7588 [core] Disable old Hue 3 UI by default
* 121f91a HUE-3286 [cluster] Hide logo when in embedded mode
* 36595a1 HUE-7802 [dashboard] Protect against missing function in old dashboards
* 24ba2de HUE-7641 [dashboard] Properly align download facet icon in SQL dashboard
* bad0e8d Revert "HUE-6909 [libsentry] Use the new sentry config property sentry.service.client.server.rpc-addresses"
* ec69bc3 Hadoop 3 rebase: removing JobTracker plugin; updating poms.
* 02e51bc HUE-7692 [editor] Upgrade failure from from CDH <= 5.4
* 1fe6f45 HUE-7623 [editor] Test connection on create_session
* bd24284 HUE-7778 [dashboard] Only show the new toolbar plus action with grister
* 9354c52 HUE-7798 [dashboard] Avoid seldom JS errors when dropping new widgets onto Gridster
* 8bfefeb HUE-7799 [dashboard] Removing a widget from Gridster should remove the instance in the items too
* 86e9e17 HUE-7797 [dashboard] Avoid drag highlighting over already populated gridster items
* b69a778 HUE-7791 [dashboard] Dropping a counter on Gridster shouldn't clone the last one dropped
* 922a44a HUE-7779 [jb] Add job type in the API calls
* a484953 HUE-3286 [cluster] Prevent YARN job status polling in analytic db mode
* 27e3951 HUE-3286 [cluster] Automatically hide other job types in Job Browser
* 21f2e5b HUE-3286 [cluster] Automatically disable the non compatible app in an analytic db cluster
* 1ef784c HUE-3286 [cluster] Cleaning-up various modes so that it works in Editor only
* 491044a HUE-7778 [dashboard] Move the 'add widget' toolbar to a plus button
* b5baefb HUE-7691 [core] Restyled metrics tables and ordered all metrics sections alphabetically
* 22d936d HUE-7743 [frontend] Fix the header in the new tableExtender using absolute positioning
* b9c495a HUE-7743 [frontend] Add a new tableExtender that uses absolute positioning for the first column
* 094640a HUE-7743 [frontend] Isolate the Hue sidebar styles
* 7c7a48f HUE-7743 [frontend] Append tooltips to the embedded container in embedded mode
* d23fbe1 HUE-7743 [frontend] Add a DEV_EMBEDDED config flag that will render hue inside a div in the page
* d3b3ecd HUE-7743 [core] Rename the EMBEDDED_MODE setting to IS_EMBEDDED
* 3da4823 HUE-7743 [frontend] Prevent bootstrap from leaking styles outside the container in embedded mode
* e17cdef HUE-7743 [frontend] Keep the jobs panel anchored below the toggle button
* 065a3cd HUE-7743 [frontend] Keep the history panel anchored below the toggle button
* c187d77 HUE-7743 [frontend] Append new elements to the embedded container instead of body in embedded mode
* 7cb649b HUE-7743 [frontend] Prevent Hue styles from leaking outside the embedded container
* 56a99c7 HUE-7743 [core] Extract and consolidate global JS variables into one js file
* 4142c1a HUE-7743 [core] Add a config flag to enable embedded mode
* 00d7453 HUE-7790 [assist] Silence all API errors in the right assistant
* 304969f HUE-7789 [dashboard] Dragging on top of an existing Gridster widget shouldn't show the drop background
* 1e850f7 Revert "HUE-7500 [frontend] Upgrade Nicescroll to the latest"
* 8bf9d8c HUE-7691 [core] Integrate Metrics as page on /about page
* a6b4bcf HUE-7691 [core] Restyle metrics page and fix for the dockable binding
* 3ddac34 HUE-7691 [core] Integrate Metrics as page on /about page
* 4cbb6bc HUE-7635 [dashboard] Implement min count for SQL
* a5bde7f HUE-7639 [dashboard] Support median & percentiles in SQL
* 023f792 PR436 [hive] Document using multiple sessions for Tez jobs
* 99c499f HUE-7786 [dashboard] Canceling adding a widget should not add an empty widget to Gridster
* f3f50f8 HUE-7785 [dashboard] Widgets should have a gray border just on edit mode
* 2fa7ed1 HUE-7788 [dashboard] Enable automatic layout on Gridster to avoid overlapping widgets
* e793c87 HUE-7783 [editor] Add log toggling functionality to the presentation mode
* 3f65373 HUE-7782 [metastore] Fix overflow on the settings panel
* 0c8aa50 HUE-7784 [dashboard] Fix JS error on right assist filtering
* 687a15f HUE-7598 [indexer] Prettify json config of a collection
* 42d3375 HUE-7598 [indexer] Add the collection config to the collection page
* 31c639f HUE-7760 [jb] ADLS browser submenu is missing on hue3 UI
* 4abb362 HUE-7728 [jb] 500% progress in live Impala query browser sometimes
* e0717a3 HUE-7776 [dashboard] Enable drop from assist in Gridster
* 6d160b1 HUE-7775 [dashboard] Enable drop anywhere in Gridster
* f4b508f HUE-7777 [core] Properly style the go to top anchors
* d20a446 HUE-7750 [desktop] Use display_name instead of nice_name for SDK apps page URL in Hue 4.x. (#632)
* 36dfc3b HUE-7773 [azure] Do not hide the name of the keys
* 7ce7954 HUE-7713 [search] Support handling indexing of documents with bad fields
* 6928023 HUE-7759 [core] Fix CSS push down for the top banner
* 487ff9e HUE-7691 [core] Restyle metrics page and fix for the dockable binding
* 786000d HUE-7691 [core] Integrate Metrics as page on /about page
* cbc7384 HUE-7320 [frontend] Use nicescroll for the sql columns table
* d18193a HUE-7751 [core] Update tarball links to very latest CDH
* 528556b HUE-7752 [core] Remove sample popup column filtering toggling icon
* e65c240 HUE-7692 - [editor] Upgrade failure from from CDH <= 5.4
* 1d67e6e HUE-7320 [frontend] Add multiCheck binding that supports foreachVisible
* 7ba84f6 HUE-7311 [editor] Limit asterisk expansion to the tables in the select statement
* 903f3b5 HUE-7751 [core] Update public tarball links of the integration tests
* ebd891a HUE-7624 [core] Fix LDAP unit test
* 165401f HUE-7749 [editor] Don't mark columns from subqueries as missing
* a770850 HUE-7748 [frontend] Preselect the first entry in the global search result list
* 5653b4d HUE-7747 [frontend] Show a spinner when the global search results are being updated
* 4afc3e2 HUE-7746 [assist] Show a spinner when searching in the right assistant while columns are being loaded
* 56f375b HUE-7745 [dashboard] Added square brackets to the supported operators
* 9f398be HUE-7745 [dashboard] Create Solr keywords highlighter for Ace
* d1f2750 HUE-7744 [dashboard] Enable Ace Hue theme in the single line Ace editor
* 564c1e9 HUE-7730 [fb] Refresh assist document list after creating workflow
* 1f3be23 HUE-7734 [metadata] Avoid silent error when tenant id retrieval is empty
* 24281e5 HUE-7731 [core] Move new and document list to top menu
* 1a8fff3 HUE-7729 [search] Support collections with hyphens in name
* 35f8a00 HUE-7714 [editor] Add column type to column name of row detail popup
* 502fefa HUE-7739 [metastore] Fix column context popover in the table browser
* 90df79d HUE-7737 [frontend] Make sure popovers are aligned when opened the first time
* ced8231 HUE-7736 [assist] Make sure filtering the file panels resets the current page
* 680ee3d HUE-7735 [editor] Prevent JS error from the risk suggestions
* eb50610 HUE-7624 [core] Support multi-authentication with AllowFirstUserDjangoBackend and LdapBackend
* f941289 HUE-7553 [jb] Attempt object has no attribute 'task_attempt_counters'
* e986e8e HUE-7710 [search] Prettify facet dimension humane description
* 7175cbd HUE-7709 [search] Dimension 2 facet selection display the same 1st column twice
* 36977b7 HUE-7726 [editor] Prevent statement parser error on '-' and '/'
* 22d93cb HUE-7725 [autocomplete] Make sure we don't make suggestions on stale editor contents
* 8092912 HUE-7724 [assist] Keep the state of the right assist tabs and refresh the assistant when needed
* 989ffee HUE-7723 [editor] Only check for syntax in the Hive and Impala editors
* 05d9aba HUE-7718 [editor] Enable presentation mode just for SQL editors
* 6be9a70 HUE-7717 [editor] Double click on snippet title shouldn't add a new snippet in presentation mode
* cba4a98 HUE-7719 [editor] Consolidate the Pyspark mode
* f4c9074 HUE-7716 [editor] Add a bit of left margin to the presentation mode
* 2d43813 HUE-7722 [editor] Avoid JS error when user tries to execute zero queries in presentation mode
* fd7dfd0 HUE-7720 [home] Emptying the trash shouldn't show a constant spinner
* 4dca702 HUE-7721 [home] Improve "Empty trash" discoverability
* fdda567 HUE-7667 [core] Fix http client pool by correctly mounting Transport Adapter to a prefix.
* 034f173 HUE-7707 [assist] Show in assist should scroll just the left assist
* bd61cc5 HUE-7697 [core] Allow Kerberos Renewer to retry kinit multiple times
* f79c67c Revert "HUE-7697 [core] Allow Kerberos Renewer to retry kinit multiple times"
* b6a3833 HUE-7699 [oozie] Shell document action are not listing any saved shell query
* 11d3963 Revert "HUE-7315 [core] Change HBase icon for assist and app"
* 96a2c2d HUE-7706 [frontend] Fix js error in top search results
* 9a85e8d HUE-7695 [editor] Limit suggested values for the syntax checker
* 64f58ab HUE-6688 [autocomplete] Switch to foreachVisible for the autocomplete results
* 9d22196 HUE-6688 [autocomplete] Make sure all running ajax requests are cancelled when closing the autocomplete
* 6553557 HUE-7695 [editor] Only mark syntax errors in the active statement
* fd4dd0c HUE-7695 [editor] Only identify complex locations for Impala
* ca70cfe HUE-7695 [editor] Limit background location checks to cached data only
* 89eea5f HUE-7695 [assist] Limit prefetching of columns in the right assist to the first 10 tables
* 89a4cdc HUE-7695 [editor] Check identifier existence async
* c02e8b4 HUE-7683 [assist] Add 'Open in assist' functionality for the right assist items
* 1e4e896 HUE-7694 [assist] Add sample tab to the collection context popover
* 6c0c22a HUE-7701 [search] Input focus reseted when filtering terms in column popup
* c9a3f79 HUE-7703 [solr] Add collection sampling to the notebook API
* 2026612 HUE-7702 [editor] Marker map lat and lon column section fields are always empty
* 3867842 HUE-7704 [frontend] Fix wrong alignment of share dropdown options
* 5bd992a HUE-7697 [core] Allow Kerberos Renewer to retry kinit multiple times
* 189ef93 HUE-7616 [editor] Shell job fails with TypeError: for +: 'dict' and 'str'
* cb63bda HUE-7685 [assist] Show table title in the right assist
* 245cfab Revert "HUE-7680 [frontend] Get rid of Nicescroll to improve general performances"
* 29cd2b1 Revert "HUE-7680 [editor] Fix scroll in autocomplete dropdown"
* e35b44b Revert "HUE-7680 [frontend] Tone down the scrollbars for webkit browsers"
* 398dd4b Revert "HUE-7680 [frontend] Improve CSS on not-so-top-of-the-line screens"
* 7752a60 HUE-7686 [dashboard] Improve reliability of the db/table chooser
* 59ce57b HUE-7680 [frontend] Improve CSS on not-so-top-of-the-line screens
* 9dcaf3a HUE-7694 [assist] Add show details to the collections name in left and right assist
* b02c2e3 HUE-7684 [assist] Add context menu to the collections title in left and right assist
* 7edcf9d HUE-7680 [frontend] Tone down the scrollbars for webkit browsers
* 99ff3f9 HUE-7680 [editor] Fix scroll in autocomplete dropdown
* 7ba57d0 HUE-7693 [assist] Make sure the right database is opened when a query is opened
* 34312c6 HUE-7247 [editor] Show custom context menu when dragging views into the editor
* 09a04f4 HUE-7631 [core] Keep older login URL for backward compatibility
* 41e762b Revert "Revert "HUE-7631 [core] Have login page also prefixed with /hue""
* 22f8466 HUE-7678 [oozie] Running an old workflow from 3.7 might fail
* 93e2b6b HUE-7654 [core] Little polishing of the new thread page
* 9d64faa HUE-7682 [assist] Expand the right assist content if there's just one table present
* e2ee997 HUE-7681 [assist] Differentiate font sizes between the two assists
* 293f897 HUE-7688 [metastore] Prevent the table browser from leaking css styles to other apps
* 05ee598 HUE-7687 [metastore] Supply the source type when updating table and column comments
* 1ecc547 HUE-7679 [dashboard] Add clearable to the simple ace editor
* 569d7b3 HUE-7680 [frontend] Get rid of Nicescroll to improve general performances
* d5e5e55 HUE-7689 [frontend] Avoid JS import error in old Hue
* f4f7eb7 HUE-7647 [core] Group sync fails when a non-standard (not uid) user_name_attr is used
* 6e01143 HUE-7635 [dashboard] Implement min count for SQL
* 06b85b8 HUE-7676 [core] skip_trash for hue_config_validation
* edee870 HUE-7250 [assist] Improve performance when showing a table in assist
* dcd61f3 HUE-7343 [assist] Exclude CTE aliases from the tables in the right assistant
* 0797bbe HUE-7663 [frontend] Add weights to global search result and keep selection after update
* d869692 HUE-7673 [dashboard] Enable vertical scroll inside the Gridster widgets
* 181c74b HUE-7663 [frontend] Group all Hue apps in one global search category and only match if the name starts with the query
* fe5e846 HUE-7671 [assist] Fix the inline autocomplete in the dashboard assistant
* 127a23f HUE-7506 [editor] Use the inline autocomplete in the result column search
* 1affd33 HUE-7671 [frontend] Include names in the inline autocomplete suggestions
* c4648b8 HUE-7670 [frontend] Update the inline autocomplete after inserting suggestions
* 5f01f4e HUE-7507 [frontend] Use the inline autocomplete in the context popover column filter
* b689e89 HUE-7669 [assist] Update the inline autocomplete on backspace
* bef804a HUE-7672 [dashboard] The layout chooser should not error after creating a new dashboard programmatically
* 9b0863f HUE-5568 [editor] Grid result not correctly aligned when browser zoom is not 100%
* d257120 HUE-7668 [frontend] Use up and down arrow keys to cycle suggestions in the inline autocomplete
* 10e73b7 HUE-6650 [autocomplete] Merge popular group and order by column suggestions with existing column suggetions
* 5f29c0d HUE-6129 [metastore] Show actual sample API errors in the panel instead of generic message
* 18b4666 HUE-7281 [editor] Mark the correct lines for errors in multi query execution
* 11e5323 HUE-7272 [autocomplete] Cycle the autocomplete suggestions on up/down at the limits
* f139d13 Revert "HUE-7631 [core] Have login page also prefixed with /hue"
* 2fa4359 HUE-7666 [editor] Presentation mode with variables shouldn't break the editor
* 4513c4c HUE-7665 [editor] A failed query in presentation mode should reset the global play/stop icon
* b4f4e6a HUE-7663 [frontend] Enable search for Hue apps in the global search
* 781d045 HUE-7661 [frontend] Center the top search bar
* 7c76cf3 HUE-7660 [editor] Update the Hive UDF library
* e10dc9f HUE-7660 [editor] Update the Impala UDF library
* 17ff1c5 HUE-2451 [dashboard] Use SQL autocomplete for the query input
* 3d75bba HUE-7662 [editor] Reloading a presentation mode page doesn't allow to load the editor again
* 034ccf8 HUE-7656 [dashboard] Fix loading back the Gridster layout
* 730b591 HUE-7658 [dashboard] Improve widget margins
* 3c64cc3 HUE-7657 [dashboard] Fix converting from old dashboard to Gridster
* 951dc7b HUE-7654 [core] Integrate Threads page as page on /about page
* 8f30e78 HUE-7248 [adls] Added client_id & tenant_id script handling
* 50608b7 HUE-7655 [dashboard] Add transitions to Gridster icons
* bc943d6 HUE-7651 [dashboard] Show widget delete icon on hover on Gridster mode
* d41145e HUE-6958 [autocomplete] Fix issue with autocomplete after Hive GROUPING SETS
* 7ef398f HUE-6958 [autocomplete] Improve autocomplete of Hive windowing statements
* 1406843 HUE-7648 [editor] Only mark missing identifiers when there are suggestions
* ca44a34 HUE-6958 [autocomplete] Add autocomplete for Hive MERGE statements
* bb9367e HUE-7650 [dashboard] Remove widget resize and move icons on Gridster mode
* c99997d HUE-7644 [dashboard] Optimize initial search bar for smaller resolutions too
* 7a357da HUE-7649 [core] Add Jison to Notice file
* c847e5a HUE-7643 [editor] Only mark syntax errors for which there are suggestions
* 05f9b8d HUE-7642 [editor] Anchor the marked syntax errors to have them move automatically with the text
* a4a13d1 HUE-7643 [editor] Prevent the syntax checker from marking stale editor identifiers as missing
* 6afe750 HUE-7642 [editor] Don't mark words as syntax errors while they're being typed
* a56d4b7 HUE-7637 [jb] Task attemps log size is very small
* c5a3941 HUE-7634 [dashboard] Persist and reload the gridster layout
* 25cf9b3 HUE-7353 [search] Timeline chart shouldn't degrade the page performance
* 3994d09 HUE-7636 [dashboard] Gridster should expand on assist collapse
* 9382d0c HUE-7597 [core] Update 3rd party Readme with frontend libraries
* 9b2e71a HUE-7248 [adls] Add support for password script
* 5cb213a HUE-7420 [jb] Hide empty Impala tabs
* a97cb67 HUE-7487 [editor] Propose setting 'max_row_size' on error
* cd0e726 HUE-7588 [core] Option to disable Hue 3 switching
* 457cf23 HUE-7631 [core] Have login page also prefixed with /hue
* 59a28e2 HUE-2451 [dashboard] Perform search on enter in the query editor
* 2f1d0b8 HUE-7626 [editor] Fix issue where incorrect keywords were no longer marked by the syntax checker
* 6824568 HUE-7625 [assist] Sort the folders in the documents panel and home by name
* b9d5240 HUE-7539 [fb] Avoid error on directory creation from choose a file modal
* a07f168 HUE-3228 [dashboard] Avoid redirecting to no collection page if SQL default db is empty
* 77d7289 HUE-3228 [dashboard] Do not show facet limit for SQL
* 5c422c5 HUE-7632 [dashboard] Set base size for each widget type to avoid expensive calculations
* e759085 HUE-7633 [dashboard] Resizing a Gridster widget should resize its content too
* fe37ef1 HUE-7633 [dashboard] Resizing a Gridster widget should resize its content too
* 6feab0d HUE-7571 [doc] Update thirdparty README
* 2b06296 HUE-3228 [dashboard] Split SQL API in hierarchies to support different SQL engines
* 865f193 HUE-7630 [dashboard] Add a basic query builder layout
* c625745 HUE-7615 [doc] Add upgrade instructions
* b7264eb HUE-7620 [indexer] Offer to index split a field into a multi-valued field
* abe5efc HUE-7619 [indexer] Morphline indexer should not be on by default yet
* 724f2e0 HUE-7629 [assist] Bump the field/column font size by one pixel
* fbdf9fa HUE-7628 [assist] Accept different kind of dashboard engines for the right assistant
* e589b2c HUE-7627 [editor] Fix scroll to column after visiting metastore
* dbc09bb HUE-7622 [jb] Reruning a wokflow redirects to a json result
* d76aebd HUE-7617 [fb] Compress can fail with output.properties data exceeds its limit
* 37ceb7d HUE-7612 [dashboard] Recalculate height of non graphical widgets
* 7186260 HUE-7614 [dashboard] Enable drag'n'drop from assist
* 5b043c4 HUE-7611 [dashboard] Add drop functionality to an empty widget
* 9d4485d HUE-7613 [dashboard] Make resize icon more prominent
* 17700bc HUE-7610 [dashboard] Add delete functionality to an empty widget
* 9f1e090 HUE-7603 [dashboard] Smaller default empty widget
* ee917a5 HUE-2451 [dashboard] Make top terms limit parameterizable
* 971da2b HUE-2451 [dashboard] Round the left border of the query input
* dc789bc HUE-2451 [dashboard] Don't use the Solr query autocomplete when engines other than Solr are used
* 2556f59 HUE-2451 [dashboard] Use prefix when fetching terms for value autocomplete
* 6430acc HUE-2451 [dashboard] Use the terms API instead of samples when suggesting values in the query autocomplete
* db2332e HUE-2451 [dashboard] Enable placeholder for the simple ace editor component
* 787c4fd HUE-7603 [dashboard] Initial layout chooser should create the layout in Gridster too
* c1e4fb7 HUE-7560 [assist] Added Solr specific facet values for the filter
* cb2028b HUE-7560 [assist] Extracted filtered computed creation to AssistantUtils
* 996ff42 HUE-7560 [assist] Removed collection specific panel and re-used db one
* 7071366 HUE-7560 [assist] Simplified loading of the right assist collection panel
* e32d3b5 HUE-7560 [assist] Fix filtering of fields in the right assist collection panel
* d295731 HUE-7560 [assist] Re-use the new collections panel on the dashboard right assist
* 216cdfe HUE-7601 [indexer] Fix sample popover integration
* 9ca4f6c HUE-7602 [assist] Remove unused AssistCollectionEntry references
* 55c36c9 HUE-7600 [assist] Split the column entry assist for the right assistant
* 8f86fcd HUE-7248 [adls] Remove compress feature
* 329b7c7 HUE-7599 [autocomplete] Remove some unsuitable SET options
* 34f3d44 HUE-2451 [dashboard] Suggest fields, sample values and keywords in the query input
* da01616 HUE-2451 [dashboard] Use the simple Ace editor as the query input in the search bar
* 713f5ed HUE-2451 [dashboard] Use flex layout for the top search bar to adjust the width of the query input automatically
* a7a82ec HUE-2451 [dashboard] Don't handle partial values in the query parser
* 57d39d6 HUE-2451 [dashboard] Add query autocomplete of keyword matching, values and boolean expressions
* 520cf37 HUE-2451 [dashboard] Initial generation setup of Solr query parser
* 06e6167 HUE-2451 [dashboard] Rename the Solr expression parser to Solr formula parser
* 1a0a121 HUE-2451 [core] Split parser generation in the makefile
* 8053d2d HUE-7592 [jb] Hide older browser if the new ones is enabled
* 09576ad HUE-7591 [pig] Also add hive to the sharelib when using hcatalog
* c8197d6 HUE-7596 [assist] Avoid fetching the top columns for the collections panel
* 557baaa HUE-7594 [core] Adjust project license to be valid
* 6162c77 HUE-7464 [editor] Refactor SQL sessions to be less confusing
* f98f837 HUE-7595 [editor] The spacing of the new notebook icon is off
* 864bef2 HUE-7445 [editor] Add session id to the Session panel
* cffda11 HUE-7464 [editor] Do not save SQL sessions as they become stale
* 53df364 HUE-7464 [editor] Inform if the session was recreated or not in the create_session API
* dc59507 HUE-7567 [all] Fix test desktop.lib.rest.test_clear_cookies
* 7a97710 HUE-7420 [jb] Fix test jobbrowser.tests.TestImpalaApi.test_apps
* b589902 HUE-7475 [core] Merge HUE-3102 to pysaml2 v4.4.0
* 628a6b6 HUE-7419 [core] Update SAML libraries   Fix undefined failure_function for handling SAML response parsing exception
* 83cc6e7 HUE-7419 [core] Update SAML libraries   add dependencies defusedxml(0.4.1), future(0.16.0),   and pycryptodomex(3.4.7 removed lib/Crypto/SelfTest/)
* 10c8a39 HUE-7419 [core] Update SAML libraries   upgrade djangosaml2 (0.13.0 --> 0.16.4) and pysaml2 (2.4.0 --> 4.4.0)
* 0a3bb04 HUE-7583 [editor] Export result to table throws already exists error
* 704d710 HUE-6238 [useradmin] ConcurrentUserSessionMiddleware - missing user
* 04284a1 HUE-7587 [indexer] Fix csv format type guessing test
* 36d8e46 HUE-7062 [core] Fix all the 'ascii' codec can't decode from Solr function descriptions
* 92ea3a5 HUE-7585 [indexer] Delete collection when data indexing fails in the wizard
* a9d4031 HUE-7587 [search] Properly create collection with default field when specified
* 41d42d0 HUE-7464 [editor] Show log panel by default
* 5b0d84f HUE-7585 [core] Tweak config creation to not override the base one
* 5983cf9 HUE-7585 [core] Integrate Sentry protected schemas in config creation
* 4598fc7 HUE-7585 [core] Properly detect if Solr is kerberized but not Sentry protected
* 73d6292 HUE-7584 [solr] Support default field via the config API
* 10bbdd4 HUE-7584 [solr] Support deleting configSet via the config API
* f90b9af HUE-7584 [solr] Support creating configSet via the config API
* a09fa37 HUE-2173 [dashboard] Convert timeline widget to th nested facets
* 9d9a0b3 HUE-2173 [dashboard] Only add term prefix when it is not empty
* 62a358a HUE-2173 [dashboard] Allow min and max metrics for date types
* 5c58297 HUE-2173 [dashboard] Show sorting and facet limit when it makes sense
* 6169990 HUE-2173 [dashboard] Port the range & up next text facet
* 5a98bc6 HUE-7062 [dashboard] Always suggest aggregate functions in the formula autocomplete
* 63e644d HUE-6106 [autocomplete] Add / as an initial suggestion for empty file paths
* 5322493 HUE-6799 [editor] Use the last cursor position when opening from the query history
* dd87a0c HUE-6799 [editor] Save the cursor position with the snippet
* f782e9a HUE-7251 [editor] Don't select all and move cursor on undo after paste
* fb220e1 HUE-5480 [autocomplete] Suggest S3 and ADLS paths in the autocompleter
* ca37faa HUE-7573 [assist] Sort the documents in the assist panel according to last modified time with folders on top
* 281e0d3 HUE-7578 [assist] Fetch more entries when scrolling to the end in the S3 and ADLS panels
* 826c34a HUE-7586 [assist] Re-wire collection refresh subscriber
* 6c0eb62 [HUE-7564] Remove one of the get_connection(ldap_config) function in ldap_access.py.
* 657c4ef HUE-7539 [filebrowser] fixing downloading a file hangs the full Hue. We have done some performance analysis and found out that 1MB buffer size works best.
* e6bce8a HUE-7552 [fb] Copy Folder Into Itself Causes Endless Loop
* 21a935c HUE-7554 [jb] Job Browser should provide YARN "Diagnostics" info when non empty
* 575af2e HUE-7420 [jb] Incorrect number of Impala queries
* e450559 HUE-7572 [editor] Show the complete statement in the document context popover
* 9ab0186 HUE-7568 [frontend] Show description match in bold instead of italic for the top search results
* d1ca684 HUE-7580 [metadata] Split in two ddl and stats uploads
* 55efff0 [doc] Update thirdparty README
* 01c6d38 HUE-7567 [all] Add default timeout to REST calls
* 98e2496 HUE-7490 [assist] File assist does not have an initial spinner
* 982f1b6 HUE-7420 [jb] Adding Impala text to the query page to prevent confusions with other SQL engines
* 8ff5b69 HUE-7420 [editor] Open correct mini browser tab depending on the type of query
* ca9dd93 HUE-7579 [frontend] Fix anonymous user render of login page
* 503f982 HUE-7576 [assist] List collections aliases on the Solr assist
* 74a8298 HUE-7570 [core] Bump ConnectionPooler to have a poolsize of CHERRYPY_SERVER_THREADS
* 1e9c409 HUE-7569 [core] Adding Thrift arguments to the logging of the return call
* 62e358f HUE-7569 [core] Finer grained Thrift pool instrumentation
* f1a8258 HUE-7568 [core] Top search document description can contains <em> for matching highlights
* 2341c19 HUE-7062 [dashboard] Convert arithmetic operators to their corresponding functions in the formula editor
* 099a8a0 HUE-7062 [dashboard] Move formula editor cursor between the parentheses and trigger autocomplete when inserting functions
* e77fd07 HUE-7062 [dashboard] Suggest fields in the formula editor
* 2f25ad8 HUE-7062 [dashboard] Prevent line breaks when typing fast in the single line Ace editor
* 332729d HUE-7062 [dashboard] Only suggest aggregate functions when the formula editor is empty
* d6ca048 HUE-7577 [editor] Don't assume databases have been loaded for all sources
* a5d95e5 HUE-7062 [frontend] Move context popover and related ko components to ko_components
* b8ba9ca HUE-7062 [frontend] Extract all ko components to separate files
* d03dbe4 HUE-7062 [dashboard] Improve the size of the formula editor
* 057e3c0 HUE-7575 [assist] Hide filter icon from the Solr assist
* fae12bc HUE-7559 [assist] Pre-select the source and root item for the collections panel
* 5d73b1f HUE-7574 [assist] Create index from the Solr assist
* 6b22204 HUE-7315 [core] Change HBase icon for assist and app
* dda957a HUE-2173 [search] Avoid breaking search bar layout on normal resolutions
* 4a8896b HUE-7062 [autocomplete] Link formula to the autocomplete
* 35a2e09 HUE-2173 [dashboard] Port timeline to the nested facets
* 8390502 HUE-7420 [jb] Fix mini Impala jb expand + Styling
* fe147df HUE-7565 [dashboard] Allow dragging to dashboard to create a new widget
* 8cfe667 HUE-7062 [dashboard] Suggest Solr functions in the dashboard formula editor
* 951043a HUE-7062 [dashboard] Add Solr function library to the autocompleter
* ff380e2 HUE-7062 [autocomplete] Extract commonly used autocomplete functionality to SqlUtils
* 6f79f42 HUE-7062 [frontend] Add a generic Ace editor component that supports the Hue autocomplete dropdown
* 12813d0 HUE-7566 [dashboard] Allow removing a Gridster widget
* 6ee1041 HUE-2173 [dashboard] Do not error on sorting on text facets
* 53807b7 HUE-7563 [metastore] Fields in nested column have a leading comma when preceded by array in type struct
* 16768b2 HUE-3228 [dashboard] Add ORDER BY functionality to SQL
* bdf1ef9 HUE-3228 [dashboard] Port SQL API to use the new nested facets
* 7ab9b55 HUE-2173 [dashboard] Port the gradient map to the nested faceting
* fc1cb7f HUE-2173 [dashboard] Longer search bar when analytics is supported
* 35511ae HUE-7562 [core] Allow building Hue with Java 9
* 16609e8 HUE-7558 [assist] Update the context menu for the collections items
* 779edb6 HUE-7557 [assist] Wire in the right sample popup for the collections items
* bcfdcfb HUE-7556 [assist] Improve icons and i18n for the collections panel
* dc74cfd HUE-7420 [jb] Fix TestImpalaApi.test_app
* 2db2368 HUE-7545 [search] Reset query string in URL when it becomes empty
* 0a39e02 HUE-7555 [importer] Type guessing for table sets everything as string
* 2c69cb6 HUE-7561 [sentry] Bump single user caching for metadata search
* 5eddd05 HUE-7555 [core] Rename Amin section link in the top right user menu
* c4b4b72 HUE-2173 [dashboard] Reformat some part of the code
* 34eb533 HUE-2173 [dashboard] Port timeline and gradient map widgets to recursive nested facets
* a29c9ba HUE-2173 [dashboard] Pass to clean-up recursive facets template
* 5d68dce HUE-2173 [dashboard] Do not show sorting option on hit widget
* 787f8df HUE-2173 [dashboard] Disable removing the last nested facet of a widget
* d54bc88 HUE-2173 [dashboard] Add observable subscribes to newly added facets
* fcc9ca1 HUE-2173 [dashboard] Hit widget compatibility with recursive facets
* cce050c HUE-2173 [dashboard] First pass of backend to support recursive facets
* 8de4611 HUE-2173 [dashboard] Refactor model to support N dimensions: UI part
* 8e6b0ce HUE-2173 [search] Harmonize indexer to use simpler field types
* 8bedad5 HUE-2173 [dashboard] Support new facets in old dashboards
* 07dba5f HUE-2173 [dashboard] Mini skeleton for static dashboard
* d3a5393 HUE-2173 [search] Protect against empty nested facet buckets when nothing matches
* 97177b1 HUE-7420 [jb] Remove white space from impala title
* 727b448 HUE-7420 [jb] Queries: bring up bottom panel
* 95c86ed HUE-7420 [jb] Queries: bring up bottom panel
* 6c94d83 HUE-7420 [jb] Fix impala link in editor log
* 0492496 HUE-7468 [assist] Convert collection assist into tree mode
* 65992fb HUE-7420 [jb] Fix impala duration & progress
* 49a6cd9 HUE-7420 [jb] Fix impala summary & plan whitespace + perf
* d24c5fa HUE-7542 [metadata] Only cache for a limited amount of time the list of cluster ids
* 9f4f66a HUE-7548 [metastore] Create table time conversion to local time can fail
* 73e99dc HUE-7549 [metastore] Drop table does not refresh the page
* 249330d HUE-7516 [fb] . dir can be selected and allowed to copy into itself
* 6417a99 HUE-7551 [autocomplete] Fix issue where suggestions are missing when there's no alias for a complex reference
* 04e38e2 HUE-7463 [editor] Don't mark Impala complex types as missing
* e1acf5b HUE-7547 [editor] Improve location handling for Impala complex identifiers
* b3d7068  HUE-7546 [dashboard] Automatically apply height to the Gridster widgets on Leaflet draw
* adb86cf  HUE-7546 [dashboard] Automatically apply height to the Gridster widgets on load and on plotly afterplot
* 7b07d4a HUE-7546 [dashboard] Auto calculate height of tile based on content
* eb28275 HUE-7420 [jb] query browser 'NoneType' object has no attribute 'group'
* f9483d2 HUE-7533 [fb] Wrong error message in UI with 500 error when user tries to edit read_only file in File browser
* fa858e5 HUE-7420 [jb] queries are not in sorted order
* ee8654f HUE-7420 [jb] total number of impala queries incorrect
* 77dfec4 HUE-7286 [editor] Move sql identifier object to the beginning of the tooltip
* 4320e79 HUE-7286 [editor] Only show the main type for columns in the tooltip
* aa7f7b5 HUE-7544 [editor] Make identifier existence validator less eager when editing the identifier
* d26ffc4 HUE-7543 [editor] Prevent the risk icon from moving the editor down
* a690eeb HUE-7280 [editor] Mark the executed statement in the gutter when multiple statements are selected
* 0748dae HUE-7541 [assist] Missing styles from the Hue 3 assist
* 0729331 HUE-7431 [core] When idle session timeout is enabled it causes issues with IDP initiated SAML
* 607c61e HUE-7420 [jb] query plan border color
* 438d5be HUE-7286 [editor] Show column type in the hover tooltip if the details of the column is cached
* bbef487 HUE-7538 [frontend] Override default knockout html binding to prevent XSS
* fb5c224 HUE-7537 [editor] Make SqlFunctions optional for the parsers
* 35c1587 HUE-6159 [autocomplete] Don't mark column alias references as columns belonging to a table
* 4ca2264 HUE-7535 [editor] Fix issue where the syntax checker marks incomplete statements as complete
* fc63969 HUE-7471 [assist] Don't show a scroll bar for entries with a spinner
* d63a13c HUE-7534 [editor] Fix IE js error on missing endsWith in the syntax checker
* 6da4969 HUE-7536 [frontend] Avoid XSS in the table row display modal, HueDatatable and TableExtender2
* 141ac77 HUE-7529 [metastore] Show primary keys in the column list for a table
* 36cab75 HUE-7528 [editor] Show partition key details for columns in the contexts popover
* 84e1c8c HUE-7527 [assist] Prevent scroll on drag in the foreachVisible binding
* c87aa7e HUE-7525 [home] Prevent js error when dragging to select documents
* ac7e88e HUE-6238 [useradmin] Option to disable concurrent user sessions
* 0468283 HUE-7532 [home] Move create folder to the create document menu
* 5ca296a HUE-7531 [frontend] Allow double click to see detail on old dataTables too
* c797f0d HUE-7530 [editor] Avoid red error popup on close of expired query
* 91a2a79 HUE-7526 [frontend] Avoid XSS in the wysiwyg5 editor and fix the binding in Hue 4
* a26fbc3 HUE-7500 [frontend] Upgrade Nicescroll to the latest
* ba4000a HUE-7524 [oozie] Avoid parsing XML with resolve_entities
* 13eebe0 HUE-7420 [adls] replaced REFRESH_URL for TENANT_ID
* a1440c3 HUE-7508 [editor] Have the column filter visible by default in the context popover
* 6da3b21 HUE-7523 [assist] Enable drag and drop of documents in the assist panel
* 49d7c4f HUE-7521 [security] Prevent JS error on printAcl not defined
* 00c834a HUE-7505 [fb] Add a visual hint (green) to the upload status bar when successfully uploaded, and same for failures
* 50e0adf HUE-7505 [fb] Home link has a different highlight background than the path
* 8805a03 HUE-7505 [fb] The file properties in the file viewer are too close to the action menu
* 14bafa4 HUE-7505 [fb] Style file editor should be the same as file viewer
* 4e72f67 HUE-7522 [frontend] Link to the latest editor from the oldest editor alert
* 79f6cf1 HUE-7520 [editor] Prevent JS error from being thrown when closing the session
* 61b27c5 HUE-7519 [assist] Fix JS error when the sample tab can't load samples
* eefa31d HUE-7257 [autocomplete] Remove the SET options for Hive
* 08b4e16 HUE-7517 [frontend] Properly close the global search results when opening a document
* ec3c413 HUE-7510 [editor] Improve cursor position after dragging tables and columns to the editor
* 31b020d HUE-7511 [fb] Fix replication factor for the currently selected file
* 1d1fdba HUE-7512 [home] Select json on the import documents modal is weirdly big
* cb82fbe HUE-7513 [frontend] Top global search input is smaller than the query blue button and misaligned
* f03449d HUE-7518 [editor] Remove bottom margin from the result field list filter
* 37d1d3b HUE-7492 [fb] Second upload from Upload button seems to error
* f48f12d HUE-7501 [dashboard] Aggregate field does not exist in older samples
* f7cd3d2 HUE-7502 [aws] upload file to s3 location throws error: undefined
* 1458daa HUE-7504 [editor] Prevent an infinite loop when changing the snippet type
* 65a5fd3 HUE-7239 [editor] Use only one instance of the web workers for all snippets
* 5d6d185 HUE-7501 [dashboard] Do not break the page when gridster is off
* 8baf763 HUE-7503 [dashboard] Rename generated formula to plain formula
* 0e6d7ed HUE-7503 [search] Keep sorting toggles in sync between facets of same dimension
* 61156e1 HUE-7503 [dashboard] Generate sort within the same dimension facet
* 1ea1796 HUE-7503 [dashboard] Step 1 of sorting on aggregates of any dimension
* 92e40ec HUE-7503 [dashboard] Add sorting to Nth dimension
* 4f79707 HUE-7503 [dashboard] Add more than one dimension
* 4df6aeb HUE-7503 [dashboard] Use new metric template for dimension 1
* f5d9918 HUE-7503 [dashboard] Analytics lean-up for counter widget
* d026128 HUE-7503 [dashboard] Move nested facet properties to measure template
* e17e4cf HUE-7503 [dashboard] Only show Add measure button when a field is selected
* 35d6972 HUE-7503 [dashboard] Convert add new measure to the new measure-form
* c4cbb29 HUE-7503 [dashboard] New measure template
* 38b1a46 HUE-7503 [dashboard] Simpler dimensions template
* da8b100 HUE-7496 [core] Bump cherrypy threads by 10
* c0b5496 HUE-7491 [fb] Newly uploaded file via the Upload button does not get the blue selection anymore
* 7ae3e29 HUE-7501 [dashboard] MVP of the gridster integration under a feature flag
* d52f55d HUE-7501 [dashboard] Keep old layout intact and return a list of the new format
* 9f6bbe2 HUE-7501 [dashboard] Convert layout to gridster format
* 361a74f HUE-7426 [frontend] Add gridster Knockout binding
* c19f3a6 HUE-7501 [dashboard] Add configuration flag to enable the new layout
* a822810 HUE-7420 [jb] enable query browser by default
* 7d28f2a HUE-7499 [dashboard] Fix general typeahead positioning
* 15519f5 HUE-7248 [adls] fix test_export_result
* bd98ed2 HUE-7498 [importer] Also show file type on create index wizard from assist panel
* 8f8f00b HUE-7498 [importer] Avoid js error when switching input types on a badly read data sample
* 0e600b3 HUE-7497 [indexer] Fix the checking of an existing index or not while indexing
* dceef93 HUE-7497 [indexer] Fix the link to an existing collection
* e759caf HUE-7497 [indexer] Refresh assist collection list on index creation
* 4875867 HUE-7495 [editor] Copy to clipboard adds an extra \t at the beginning of header line
* e71f9b6 HUE-7494 [core] RM HA does not seem to get persisted
* e212434 HUE-7489 [editor] CloseOperation when GetOperationStatus is in an ERROR_STATE
* 4a8ca7e HUE-7062 [search] Add backend logic for formula and remove old ops
* 97dd205 HUE-7248 [adls] fix test_export_result
* db396f7 HUE-7420 [jb] impala kill job + filter
* a66e51d HUE-7248 [adls] fix export to file
* 67bb5a2 HUE-7257 [autocomplete] Add autocompletion of SET options for Hive and Impala
* 0987de1 HUE-7493 [editor] Remove fuzzy feeling from the autocompleter match
* f4e439c HUE-7400 [editor] Made close logs icon more visible and reliable
* 11b7d02 HUE-7484 [editor] Avoid old headers sticking for one second on result full screen mode exit
* a39e711 HUE-7482 [metadata] Display last time of data refresh if available
* 515bb41 HUE-7486 [oozie] 500 error when trying to submit Hive Workflow when beeswax blacklisted (#605)
* 4a4e7e7 HUE-7485 [frontend] Allow partial matching for facet values in the inline autocomplete
* 5ee0bb7 HUE-7483 [backend] validate property in hue.ini is ignored (#603)
* 20cc078 HUE-7400 [editor] Made close logs icon bigger
* ec30720 HUE-7391 [autocomplete] Limit the autocompleter to the active statement only
* 426c113 HUE-7481 [frontend] Close the global search when clicking on show in assist or table browser
* 0eebb8c HUE-7400 [editor] Moved bigger icons to the specifics CSS classes
* 374fe88 HUE-7480 [oozie] Also check for group permission for dashboard action
* 3a4428c HUE-7474 [impala] Log the query planning phase
* 23f331d HUE-7430 [core] Update translations files
* cfb8290 HUE-7478 [indexes] Re-use Solr sample popover in the index field list
* ba615ae HUE-7467 [frontend] Fix missing subtitle for the popovers
* 6df0f9e HUE-7467 [frontend] Create Solr sample popup
* 2597280 HUE-7477 [frontend] Close the left nav on click
* 823e36a HUE-7476 [core] Add Hue shell command to set CM environment
* ce7f72b HUE-7420 [jb] Impala Query integration
* ad40573 HUE-7462 [assist] Highlight matching parts of the functions filter
* e735582 HUE-7415 [editor] The editor textarea should retain its size on new query
* 84b503f HUE-6851 [metastore] Don't show the database while loading a table
* 66c75d2 HUE-7470 [editor] Only check for risks when a snippet has focus
* b5ecaf3 HUE-7463 [autocomplete] Improve location handling for map and array column references in Hive
* 77387c0 HUE-7465 [assist] Fetch right assistant columns synchronously to reduce backend load
* 595fcc3 HUE-6958 [autocomplete] Update the Hive TABLESAMPLE autocomplete
* 33c2083 HUE-7466 [dashboard] Fix alignment of facet add typeahead
* ac9918b HUE-6998 [frontend] Improve configurability of Leaflet maps
* 5ac0e0c HUE-7440 [core] Remove load balancer cookie on login if not authenticated
* 2592b2d HUE-7453 [frontend] Refactored bar, time and line chart to use the common basic chart builder
* 6c4f3a9 HUE-7453 [frontend] Create basic timeline chart port
* b31f908 HUE-7453 [frontend] Added multiserie to line chart
* 841e252 HUE-7453 [frontend] Added multiserie to bar chart
* 91cddb9 HUE-7453 [frontend] Create basic linechart port
* 91a26f7 HUE-7453 [frontend] Bump binding throttle to 200ms
* 31ff8ac HUE-7453 [frontend] Create basic barchart port and refactor common plotly options
* e3649bd HUE-7458 [editor] Fix js error in syntax checker for subquery references
* 9d414d5 HUE-7450 [editor] Fix broken jasmine tests
* 0a15113 HUE-6958 [autocomplete] Add INNER JOIN to the Hive suggestions
* bd3f66b HUE-6958 [autocomplete] Update autocompleter for the Hive LIMIT clause
* 8aaf803 HUE-7457 [assist] Don't fetch top columns for tables in the right assistant
* a9b115f HUE-7450 [editor] Don't suggest aliases when a qualified identifier isn't found by the syntax checker
* e19afe9 HUE-7449 [editor] Don't mark columns from CTEs as missing
* 1f26e9e HUE-7062 [search] Add custom autocomplete parser for solr formulas
* 8f98962 HUE-7456 [core] Do not retry Thrift call on read operation timed out from ssl.SSLError
* 64db82c HUE-7447 [core] Skip test on last access time as feature disabled
* 3880da8 HUE-7447 [core] Convert logged REST path to proper unicode
* a5247fb HUE-7448 [indexer] Support CTRL+A as field delimiter
* c162656 HUE-7447 [core] Log metrics into debug info
* 7ba5a09 HUE-7447 [core] Add thread stack traces to debug log
* 89a319b HUE-7447 [metadata] Add call tracking to navop calls
* 91c4f81 HUE-7447 [core] Add thread tracebacks into the logs in debug mode
* 6f99129 HUE-7447 [core] Stop logging user pages counts
* 46e87fb HUE-7447 [core] Track return call of REST calls
* bc2956b HUE-7447 [core] Log access page return time
* 18890c9 HUE-7446 [core] RM HA gets called by mistake on each navopt call
* b7985ba HUE-6093 [frontend] Improved timeout mechanism for Pie charts
* 64d6c97 HUE-6093 [frontend] Added resize support for Pie charts
* cacb3dc HUE-6093 [frontend] Added support for basic Pie chart on Plotly
* 9a83fc1 HUE-7444 [dashboard] Fix missing d3v3.tip declaration
* 1186643 HUE-7441 [core] Allow to blacklist all the apps but dbms and file browser
* e2a97d6 HUE-7439 [editor] Move optimizer call to after check status
* 2edfc34 HUE-7440 [core] Remove load balancer cookie in logout view
* 2e68d65 HUE-7443 [dashboard] Fix widget add dropdown menu style
* 67fc092 HUE-7438 [editor] Query execution time is not updated on short queries
* 8eee0f7 HUE-7435 [frontend] Extract Leaflet renderers to a separate common file
* 3397098 HUE-7436 [frontend] Avoid overriding of charting data transformers between editor and dashboard
* 57a58cb HUE-7434 [core] Support more than one level URLs for custom apps in Hue 4
* d3b87f6 HUE-7437 [dashboard] History back sometimes shows the list of dashboards
* 7af41ff HUE-6958 [autocomplete] Add support for Hive ABORT statement
* 6099686 HUE-6958 [autocomplete] Improve Hive SHOW TBLPROPERTIES
* 9de48d8 HUE-7433 [frontend] Add switch to enable new charting library
* 037115b HUE-7432 [frontend] Upgrade Knockout to the latest
* b56a8bf HUE-6244 [home] Menu simplification
* 701920f HUE-7428 [core] Opening a view directly from top search lands on a 404
* 9b969e1 HUE-7425 [frontend] Add gridster.js library
* 949a99a HUE-7427 [editor] Keep the selected database after execution of a statement that refreshes the assist panel
* fce10ed HUE-7078 [editor] Fix console error on hover over old syntax error token
* d9c8b3a HUE-7078 [editor] Improve handling of backticked values in the syntax checker
* df354a2 HUE-7078 [editor] Don't mark custom variables as missing
* f08b853 HUE-7362 [assist] Switch to matching all text values in the sql search instead of at least one
* be1d10f HUE-7424 [frontend] Remove double jQuery library
* 90c7ba4 HUE-7418 [hive] Table stats do not have numRows if the stats are not accurate
* 4d5e882 HUE-7417 [editor] Variables can override default values depending order
* fe3e8fd HUE-7416 [useradmin] Only display edited users on group change
* 417a9cc HUE-7402 [core] Truncate SEARCH Column in Document2 for Oracle database
* aa71cec HUE-7409 [search] More subtle way of converting old types to new types
* a072027 HUE-7362 [assist] Improve the facet handling for the right assistant filter
* e3d922d HUE-7362 [frontend] Improve the autocomplete logic of the inline autocompleter
* bab09db HUE-7362 [assist] Enable filter on column types in the left assist
* 5225839 HUE-7362 [assist] Use the new inline autocomplete input for assist filters
* 825900f HUE-7362 [assist] Include free text parts in the query specification from the global search parser
* 840cc35 HUE-7362 [assist] Extract a generic inline autocomplete component
* d4acb30 HUE-7362 [assist] Extend the global search parser to also include the facet values in the parse results
* 42aa66d HUE-7140 [editor] Add select variables
* b167cad HUE-7263 [editor] Resize handle off when scrolled down on editor and variables are present
* f24ffb2 HUE-7234 [editor] New variable should be empty
* cf1eb8a HUE-7186 [editor] Support commenting variables
* a9ad470 HUE-7140 [editor] Add select variables
* 6916ae2 HUE-7413 [fb] parent directory should not be selectable
* a8ffe65 HUE-7308 [assist] Refresh files in assist and browser
* aa1f06b HUE-7405 [assist] S3 document filter loses focus on search
* 60a1618 HUE-7393 [editor] dash is not recognized in variables
* d742759 HUE-7248 [adls] filter filesystems for copy/save
* 6df64e3 HUE-7403 [core] Add 4.1 release notes


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
- Patrycja Szabłowska
- pat white
- Paul Battaglia
- Paul McCaughtry
- peddle
- Peter Slawski
- Philip Zeyliger
- Piotr Ackermann
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
- Tatsuo Kawasaki
- thinker0
- Thomas Aylott
- Thomas Poepping
- Tianjin Gu
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
- Zhihai Xu
- z-york
- 小龙哥
