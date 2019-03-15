---
title: "3.7.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -3070
tags: ['skipIndexing']
---

### Hue v3.7.0, released Thursday 9th, October 2014


Hue, http://gethue.com, is an open source Web UI for easily doing Big Data analysis with Hadoop.

It mainly features:

* Editors for Hive, Impala and Pig for either batch and interactive SQL
* Search Dashboards for querying, exploring, visualizing data and with Solr
* Hadoop File, Job and HBase Browsers

On top of that, a SDK is available for creating new apps integrated with Hadoop.

More user and developer documentation is available at http://gethue.com.


Latest Notable Features
-----------------------

The complete list and video demos are on [La nouvelle version 3.7 de Hue avec l’application de Securite et de moteur de recherche est sortie!
](http://gethue.com/hue-3-7-with-sentry-app-and-new-search-widgets-are-out/).


Security

* New Sentry App
* Bulk edit roles and privileges
* Visualize/edit roles and privileges on a database tree
* WITH GRANT OPTION support
* Impersonate a user to see which databases and table he can see

Search

* Three new widgets
* Heatmap
* Tree
* Marker Map
* Field Analysis
* Exclude Facets

Oozie

* Bulk suspend/kill/resume actions on dashboards
* Faster dashboards
* Rerun failed coordinator instances in bulk

Job Browser

* Kill application button for YARN

File Browser

* ACLs Edition
* Drag & Drop upload
* Navigation History
* Simpler interface

HBase

* Kerberos support. Next step will be impersonation!

Hive / Impala

* LDAP passthrough
* SSL encryption with HiveServer2
* New graphs
* Automatic query timeout


Compatibility
-------------

Runs on CentOS versions 5 to 6, Red Hat Enterprise Linux (RHEL 5 and 6), and Ubuntu 10.04, 12:04 and 14.04.

Tested with CDH5. Specifically:

- Hadoop 0.20 / 2.5.0
- Hive 0.13.1
- Oozie 4.0
- HBase 0.98.6
- Pig 0.12
- Impala 1.3
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

Note: CentOS 5 and RHEL 5 requires EPEL python 2.6 package.


List of 502 Commits
-------------------

* 6b39d9d [core] Bumping version to 3.7
* 608a300 [search] Move marker map to the top left
* c306872 HUE-2321 [fb] Support HDFS UMASK in octal
* ab454c4 HUE-2321 [fb] Support dfs.umaskmode first pass
* e621772 [jb] Do not break the page on failed jobs
* 2680136 [impala] Assist metadata is broken
* bd86c2e [beeswax] Fix beeswax calls and errors for IE9
* 1a9ad6f HUE-2370 [core] Modal close crosses are positioned wrongly in different browsers/modals
* 62da10d [HUE-2294] Do not display the oozie action retries
* c212be1 HUE-2365 [oozie] Import workflow with pig action ignores <param> tag
* a4aa66f HUE-2241 [oozie] Bulk rerun failed coordinator actions
* d71c41b HUE-2355 [search] Highlight selected facet in Tree
* de5a1b5 [sentry] Implement doas view mode
* c9152ef [search] Update Apache log dashboard example
* 91d9643 [core] Little ini cleanup
* 5906e84 [sentry] List privileges of the server
* 54a88fe [sentry] List all the privileges of each role of an object
* c919750 [sentry] List privileges of the server
* db23250 [sentry] Only show edit icon when admin or with grant option
* 484ae28 [sentry] Improved with grant/show advanced css
* a5ebc25 HUE-2361 [sentry] Temporary roles should not show up in the list of roles
* fc2b419 HUE-2361 [sentry] Specify a new role on the grant modal
* 5283168 HUE-2356 [sentry] Refresh on tree resets the unexpand the selection
* b6c3433 HUE-2363 [sentry] Hide the 3 top right icons of privileges when in a popup
* 2a45d5f HUE-2364 [beeswax] SQL of saved or history queries are not loaded back in FF
* 7dc2c4a HUE-2354 [sentry] Cannot edit URI by modifying input directly
* 15d1e94 [useradmin] The user fetching API accepts text not jsonified data
* d0bb3b7 [sentry] Disable group edition when not a Sentry admin
* d4e00a4 [sentry] Add a confirmation popup when Sentry deletes cascade privileges
* 1bd4177 HUE-2361 [sentry] Grant privilege to a role the user does not belong too
* 20975f7 [sentry] Do not list privileges twice in bulk replace
* 5c1e646 [sentry] Better role filtering
* 805253a [sentry] Prettify URI view
* 0fb12ad [sentry] Hide create and delete role button when not a Sentry admin
* 25e1612 [sentry] Update role when trying to create one with existing name
* 14cb550 HUE-2308 [oozie] Use new metric collection system
* 0a9ed79 HUE-2351 [sentry] URI privileges can not be edited
* 0949741 HUE-2350 [sentry] New privileges lose their DB and Table info
* eaf23d3 HUE-2349 [sentry] New roles on 'roles' tab are not expanded when created
* 1720ade HUE-2352 [oozie] Manage buttons on the single coordinator page stack up weirdly on smaller screens
* 0125266 [search] Zoomable property on partition chart and fixed logGA bug
* eafc68d HUE-2341 [oozie] JqCron breaks Coordinator pages after some time
* 53f0d80 [sentry] Fixes HDFS refresh tree problems
* 382f8d9 [sentry] Clear last visible dot on hive privilege field blur
* 71ed685 [libsentry] Rebasing Thrift for its new impersonation field
* 12f2c1c HUE-2345 [beeswax] XSS filter bypass vulnerability
* e994227 HUE-2308 [oozie] Use new metric collection system
* 703009f [search] Facet toggling on heatmap
* a40d6d9 [search] Split widgets into Tree and Heatmap
* 3686abc HUE-2338 [oozie] Bulk operations on dashboards
* 5895127 [oozie] Add submenu levels to access directly the specific parts of the app
* b0e2f5a [jb] Ignore acls attribute from MR API which does not exist
* 77da38a [security] Rename sections
* 361f40d [jb] Show kill job icon on single job page if Sentry is enabled
* 2e08c7d [search] Send back current collection when no Sentry permission to list collections
* 4412f96 [search] Browse should be available to everybody
* 68be9b6 [impala] Retrying and opening a new session if previous one has expired
* 6595387 [indexer] Get ZooKeeper server address from ZooKeeper app if set
* 2b941bb HUE-2343 [security] filechooser binding does not set the URI of a privilege
* 5a0ff29 [security] Disable default ACLs on files
* 835a9be [sentry] Convert to valid format the URI
* 38724b3 [sentry] Convert Sentry * actions to ALL
* b252442 [security] Make bulk operation popup clearer
* a87bd31 [security] Use the list_sentry_privileges_by_authorizable API
* e3f510e [security] Better bulk modal and delete all acls operations
* 4e34c46 HUE-1655 [hbase] Send a dictionary of properties
* 2050fb3 HUE-1655 [hbase] Fixed json serialization
* 62ee84f HUE-1655 [hbase] Modified the modal to allow multiple properties per each column
* 167cd63 HUE-1655 [hbase] Set specific properties on the column families
* 05f3479 HUE-2320 [impala] Better sync tables visual feedback
* ea27847 HUE-2320 [impala] Invalidate medata of new or deleted tables
* d2f809e HUE-2320 [impala] Sync tables at the Impala level in the editor
* d4dfb5e HUE-2300 [search] Link data to partitioned tree
* 464f85f HUE-2300 [search] Introduced partitioned tree
* 390c11f [sentry] Display the grant option of privileges
* fde4edd [security] Only Sentry admins should have a list of all the groups
* db7e25c [sentry] Remove the deprecated grantor principal field
* 3118c58 [libsentry] Updated to latest Thrift to get list_sentry_privileges_by_authorizable
* 2f47794 [security] List Sentry roles according to accessible groups
* 7c5bcc6 [sentry] Using the Hive provider from Hive configuration
* 39c6f49 HUE-2335 [security] Object popup does not always disappear
* 8e6530b [dbms] Document options settings for databases
* 59d2cb0 HUE-2300 [search] Fix multibar JS error
* 56c276e HUE-2236 [search] Highlight the selected pivot
* 0f0d66b HUE-2236 [search] Make Pivot facet clickable into fq queries
* 198f285 [search] Get pivot click data and restyle filter bar selection/exclusion
* 77fad49 HUE-2272 [fb] Improved UX of the new jHueHdfsTree plugin
* c48e8f6 [search] Fix multi query wuth new facet query format
* 051903d HUE-2332 [search] Display correct icon for selected exclusion facets
* 7819bcd HUE-2332 [search] Filer widget can accept multiple values
* e09cad0 HUE-2272 [fb] Improve UX of Copy/Move modal windows
* 093465a [search] Fix pivot facet counts
* 6f8e3c8 HUE-2300 [search] Initial support for pivot tree
* cc9dcf9 HUE-2332 [search] Fixed styling issues
* a3ffb85 HUE-2332 [search] Restyled exclusion feature
* 811a2a3 HUE-2332 [search] Exclusion facet
* ea7490f [core] Add warning and propose workaround for Ubuntu 14.04 build error
* c1bce4b [search] Improve detection of date type of facets
* 9e7c7f8 HUE-2312 [search] Fixed empty label on Leaflet map
* 3148ce2 HUE-2300 [search] Linking real data to Pivot 2D chart
* 667df39 HUE-2300 [search] Adding support for discrete multibar chart for pivot
* d97a138 HUE-2312 [search] Finalize marker map widget
* 89384c2 HUE-2312 [search] Show/hide map on dropdown change and toolbar restructure
* 301a8e2 HUE-2312 [search] Map result set data to the leaflet marker
* f3c4c4e HUE-2312 [search] Added lat/lng field selector dropdowns
* 40f4453 HUE-2312 [search] Fixed some dashboard bugs
* 9ffca6a HUE-2312 [search] Create a new Leaflet map widget
* a2b0511 HUE-2330 [beeswax] Collapse previously expanded tables on assist
* ed5f481 HUE-2218 [search] Added typeahead to field stats
* f67ff41 HUE-1769 [search] Permission to access the indexer app
* 4f29947 HUE-2205 [hbase] Kerberos support
* fd9f250 [liboozie] Disable config checks when the Oozie url is empty
* 3f78670 HUE-2218 [search] Invalidate field analysis stats when query changes
* 7894d95 HUE-2218 [search] Add big popover UI
* 02a7812 [security] Mini UX improvements on Hive loading
* 69aa132 [indexer] Provide a better hint about misconfigured Zookeeper ensemble
* 800c389 HUE-2201 [jobbrowser] Add a kill YARN job button
* d8895da HUE-2316 [metastore] Create a new table from a file requires Windows (\r\n) line endings
* 6c2fcc1 HUE-2319 [fb] Do not offer file scrolling when offsets are not supported
* aa71960 [security] Adding bigger sign when no privileges are found
* 334ceb0 [security] Support privileges with grant option
* 01a3b36 [libsentry] Add WITH GRANT option syntax
* 48a055f [security] Show open folder or selected database also for nodes without children
* e03335a [security] UI revamp for the HDFS bulk modal
* fa07590 [security] Visual clue for non-empty databases
* 6a1dbde [security] Make impersonation more noticeable
* a10c8e7 [security] UI revamp for the Hive bulk modal
* 6876b8e [security] Show previously expanded roles after a Role add or remove operation
* 5cfdc8a [security] Fix roles refresh after add or modify
* b4fb6ac [search] The app can be blacklisted without crashing
* 098d53b [hadoop] Make sure YARN client get the correct logger
* cdbfe8c HUE-2318 [desktop] Documents shared with write group permissions are not editable
* 08b5527 [search] Refresh dashboard when deleting a widget that had some filters
* 3122327 [search] Delete widgets when deleting a new column
* a0a8370 [search] Missing remove call on widget
* 1d3d795 HUE-2315 [search] Extra call to /search on facet semi modal show
* c873323 HUE-2300 [search] Pivot facet backend and front end logic
* 1e20670 HUE-2218 [search] Backend for getting the stats and terms of a field
* 543d283 HUE-2301 [fb] Pick up history on non-hash path
* aebd5b6 HUE-2301 [fb] History of visited subdirectories to have fast links
* bcb18cb [security] Add a security permission to allow the list dir impersonation
* ccb62a2 [libsentry] Support update of privilegse from the assist page
* 2b1d9c0 HUE-2305 [fb] Create a smoother docking of the actionbar
* d5c845e HUE-2247 [Impala] Support pass-through LDAP authentication
* 8efc2cc [security] Fix duplicates on the role list after an add operation
* cdf8684 [security] Fix role name autocomplete on create/update role modal
* 9e5f125 [security] Fix privileges refresh and save from browse section
* 45c64ce HUE-2253 [fb] Simpler bottom bar
* fa30f4e HUE-1797 [beeswax] Integrate new graph lib and multi columns
* 5cc93c2 HUE-2304 [beeswax] Assist table fields are not updated after a refresh
* 724db29 [impala] Integrate bar chart data
* 738da8a [impala] Adding Timeline chart, Map and Filter support
* 7ed0596 [impala] Adding Line chart support
* 2d26694 [impala] Adding Bar chart support
* dc00d6e [impala] First pass on multi type facets
* 237d914 [impala] Adding Pie chart support
* 9af37d4 [impala] Update field list dynamically when creating a new dashboard
* f3ee428 [impala] Added spinner to text facet
* e585373 [impala] New dashboard wizard
* 222335c [impala] Added database and table dropdowns
* 50bbd23 [impala] Select and query only the selected fields
* b8c088e [impala] Fetch fields of current dashboard
* 091d984 [impala] Toggle selected facet
* a1d01f7 [impala] Hide an add widget button if the column has zero rows
* 235cfbc [impala] Added field filter on resultset widget
* 7ad06c3 [impala] New dashboard button
* f3ceadd [impala] Select the field from dropdown when creating a facet
* 5052357 [impala] Add a new facet with drag and drop
* d741d4b [impala] Added spinner on result widget
* 86e0a2e [impala] Adding columns to dashboard
* f6943f7 [impala] Added other facet icons to draggables
* cee368a [impala] Re-organized and added imports
* cac47b9 [impala] Toggle facet selection
* 99e856e [impala] Edit facet properties
* c14db2c [impala] Dashboard skeleton
* 372e0df HUE-2303 [fb] Move the dropzone overlay to fb from global
* 61fff6b HUE-2253 [fb] Simpler bottom bar
* 8f57232 [fb] Visual hint for global upload progress
* 3ebca64 HUE-2255 [fb] Drag and drop a file directly into the page
* dabd7ba HUE-2297 [impala] Assist databases might be duplicated
* 743dcdf HUE-2298 [dbquery] Move navigation bar to the left and rename it to Assist
* f2ebab4 HUE-2272 [fb] Improve UX of Copy/Move modal windows
* ca6e3a8 [security] Added modify role on create modal
* c0c1a20 [security] Kerberos support
* e015868 [security] Fix Hive server list of privileges
* 3c5d9a1 HUE-2296 [fb] The pagination is not working
* bd4bee0 HUE-2295 [librdbms] External oracle DB connection is broken due to a typo
* bd5273c [security] Promote security to a new dropdown menu
* d156958 [security] Scroll to right path on Hive HDFS link
* 93124f2 [security] Added link to HDFS file for table
* 781f675 HUE-2255 [fb] Drag and drop a file directly into the page
* dc3b989 [security] Added server to the Hive tree
* 2295e28 [security] Simplify bulk operation modals
* e5d26c7 [security] Delegate list all privileges filtering to authorizableHierarchy
* 58e07bc HUE-2291 [oozie] Fix very long workflow GET url of coordinator page
* b06da6d HUE-2291 [oozie] Adding spinner on bundles
* acb300d HUE-2291 [oozie] Adding progress call for bundles
* cd264af HUE-2291 [oozie] Fix progress from coordinator and bundles
* 0589c5c HUE-2291 [oozie] Adding progress call for coordinators
* 41740bf HUE-2291 [oozie] Remove check status from coordinator and bundle dashboard display
* 8996e82 HUE-2291 [oozie] Adding progress call for workflows
* 3b4c5d2 HUE-2291 [oozie] Remove check status from workflow dashboard display
* 0ebf65b [fb] Skip current folder on select all
* 7c71e6c HUE-2092 [liboozie] Jar files not in workspace should not be deleted at submittion
* 1862d64 [security] Changed radio button to prettier font awesome radio
* 547ce0b [security] Update shield icons on bulk operations
* 83216a7 HUE-2290 [search] Clearable does not update after key down
* 2a74e67 HUE-2286 [oozie] Coordinator comment section is misleading
* fdf270f HUE-2283 [oozie] Timed out workflows from coordinator should not be linked yet
* dea2f87 HUE-2273 [desktop] Blacklisting apps with existing document will break home page
* c8fc183 HUE-2279 [search] Error in searching of non-Latin symbols
* 6fcac69 [security] Added shield icon to Hive items with privileges
* ba2530d [security] Added privileges filter and load more
* 98984eb HUE-2197 [beeswax] Config check should read warehouse.dir from hive-site.xml
* 928b35e HUE-2251 [impala] Support query timeout
* 62f74cf HUE-2277 [beeswax] Make Thrift protocol version configurable
* c5962da HUE-2240 [fb] Parquet files detection should not rely on extension
* 023588a [security] Fix for show as user on HDFS
* a929ab8 [security] Duplicate role name validation
* 5fb05e5 [security] Fixed refresh tree for Hive and HDFS
* ba4c052 [security] Add a role button on privileges section
* 4ffb14f [security] Better icons for bulk edition modal
* 900cc43 [security] Disable URI or DB input accordingly to radio selection
* 2be8190 [security] Fix for checked items problem
* 976acda [security] Fixed hive autocomplete prefill
* 1aee152 [security] Columns are not hidden on the Hive tree
* 1232557 [security] Role path autocomplete for Hive
* 4e35a9e [security] Visually simplified the bulk operations modals
* eb3889d [security] Pre-selects the first available database in Hive
* 8f52c9a [security] Sync'd roles and tree creation
* 256657f [security] Create a new role from the Hive tree
* a4df3d6 [security] Added HDFS picker to Hive
* 27fbbef [security] Prettified privileges for Hive
* d5527cc [security] Fixed bulk modal dialog for hive
* 435102f [security] Link role to Roles panel in Hive
* 988379b [security] Refactored bulk actions for Hive
* 2ba0f41 [security] Refactored bulk actions for HDFS
* 34df569 [security] Leaner privileges display
* 72c4da5 [beeswax] Check more regularly for HiveServer2 server status in tests
* 46f3efa [security] Picking up the current HiveServer2 server
* fe6dc17 [jb] Avoid 500 error when job is finished or has no progress info
* 0d7a2e7 HUE-2229 [useradmin] Ask for previous password when changing it
* 7e41bdd HUE-2252 [fb] Better looking breadcrumbs
* 95e24ac HUE-2271 [core] Make hue and hdfs usernames configurable in hue.ini
* 91cc14b [security] Preset correct privilege path on Sentry table page
* e644964 [core] Timeout issue when accessing the job history
* 7fa5f6c HUE-2249 [jobsub] DB migration problems from 2 to 3.6
* cb41c70 HUE-2257 [beeswax] Extended describe data can also show up on the full following row
* bae46f7 [security] Bulk add Sentry privileges
* 478f88b [security] Bulk delete Sentry privileges
* 041a5fe [security] Clicking on a path on the tree should never expand or collapse the node itself
* 2da7c74 HUE-2263 [oozie] Enable rerun coordinator actions when coordinator is running
* 12211ce [librdbms] Fix postgresql table and column fetch queries
* 51baf80 [security] Bulk delete confirmation modal
* c0f994b [security] ACLs are refreshed after a refresh tree for the currently selected node
* 45b0577 [security] Improved HDFS tree refresh, added click on row to set the path, moved and i18n'ed the done messages
* a784193 HUE-2116 [core] Improve jHueNotify stacking
* 66044af [useradmin] Bulk delete backend API
* e2780ba [useradmin] Bulk delete groups frontend
* 4e856a2 [security] Support HDFS ACL recursive operations
* 589552e HUE-2262 [oozie] Coordinator dashboard frequency cron is not displayed properly
* 003aa9e [security] Bulk HDFS ACL sync support
* f53c6e0 [security] Bulk add HDFS ACLs
* 5a666e2 [security] Bulk delete HDFS ACLs
* 7d33d19 HUE-2265 [fb] The current folder (dot on list) should be before any other file or folder
* a2d9618 [security] Formatted right side editing form on Hive
* 8a01a09 [security] Restyled right panel for Hive privileges
* 307475c [security] Also filter by group on the tree view
* dec77d1 [security] Update an existing privilege
* da74d6a [security] Styled add role modal
* 4b591a7 [security] Restyled roles add/undo/save buttons and fixed groups multi-select
* d592a44 [security] Get checked items function
* c310f30 [security] Make Sentry action and server mandatory
* 0cf0e5a [core] Improve kt_renewer error logging
* 37cfcee [useradmin] Fix the autocomplete API tests
* 4d7461a [security] Added confirmation dialog for role delete
* cfcf903 [security] Adding role search functionality
* db993e1 [security] Added support for FILE_NOT_FOUND exception
* 37cbc21 [security] Item click does not expand the children
* 3492128 [security] Add save and undo button to HDFS acls
* 0a393fb [security] Add or remove groups in a role
* 87d6b2d HUE-2258-mrDecimals
* 12a4a78 HUE-2259 [jb] Update display of metadata on Job Browser
* 299c96c [security] Make the app optional
* a9481d1 [security] Support for checkboxes on the tree
* 2bd75aa [security] Support for linking to Roles or Edit section
* 0b22f9c [security] Fix for multiple occurrences of groups on the group list
* ebdfa06 [security] Frontend for editing groups of a role
* 8940e84 [security] Undo privilege modifications in Sentry
* 59b6259 HUE-1176 [jb] Broken image link 'static/art/login-spinner.gif'
* ef21336 [security] Fix allowClear on groups dropdown
* fad2068 [security] Filter by a certain group if selected or show all of them
* f4df846 [security] Remove Sentry privilege properties
* f4b68e4 [security] Update Sentry to lates Thrift without a privilege name
* 94c008f [security] Move Sentry save role button to the bottom
* 6c364ef [core] Restyled autocompletes dropdowns
* a754f98 [security] Added autocomplete for Hive
* 210f920 [security] Initial restyle of Hive privileges
* e88e964 [security] Empty roles message, moved to dialog for new role
* 7a2321b [security] KOified the groups list
* a75786d [security] Select2 now accept a new Hive action too
* c069f9d [security] Fixed refresh on Hive tree
* 6b0ad67 [security] Load HDFS root in case you reload a path that does not exist
* 3865560 [security] Support for hive tree linking
* 3f77f23 [security] Fixed tree actions for Hive
* f0565f3 Revert "[security] Added support from doAs from a non visible path"
* 448bb06 [security] Added support from doAs from a non visible path
* c81aed8 [security] Improved striked path
* 24dab65 [security] Simplify Sentry privilege form
* 2d8d87c [security] Restyled ACLs tree nodes
* 965eb7b [security] Updated style for ACL node and added rwx info
* 9f7e757 [security] Replace <table> by <div> in Hive
* 01496cb [security] Harmonize tree and roles section of Hive
* 900b044 [security] Initial integration of the tree in Hive
* efa58a6 [security] Improved collapse, externalized css
* 788c272 [security] Replace drop_sentry_privilege by alter_sentry_role_revoke_privilege
* 5580282 [security] Enable loading of non standard users/groups on the initial select dropdown
* 8d34433 [security] Support for temporary use of unlisted users/groups in the select
* 48fec4e [security] Improved tree UX
* fba1666 [security] Tree toggle expand just on icon
* 3ff1ea3 [security] Fixed tree scroll to path
* f0220b7 [security] Restyled ACLs panel for HDFS
* 942b401 [security] First round of fixes for doAs, introduced select2
* e5ba114 [security] Unify Hive privilege templates
* 6377d91 [security] Adding delete privilege first version
* d587f0b [libsentry] Adding rename and delete privilege API calls
* 0acd8d1 [security] Call refresh tree when switching diff mode or user
* bff0bb2 [security] Added style for new tree functionalities
* ef5c7a1 [security] Added collapse, expand and refresh tree
* 84e10c9 [security] Support adding new privileges to existing Sentry roles
* 2cbaa61 [security] Create a new role with privileges and groups
* d0cce56 [security] Display and edition template for Sentry privileges
* 54e6ca7 [security] Mock list_sentry_privileges_by_authorizable in Sentry
* 0523922 [security] Added pagination support for HDFS
* f670b56 [security] Autocomplete group or user names for each HDFS ACL
* b8e9c72 [security] Adding a typeahead to view as user input box
* a19fb44 [security] Adding HDFS diff mode logic
* 1653639 [security] Scroll to path on HDFS tree
* 38e7748 [security] Support for unexpand on HDFS tree
* 2013e3c [security] Support for history on HDFS
* 0718683 [security] Tree enhancements
* 5b2119f [security] HDFS diff mode skeleton
* 7b45990 [security] Adding HDFS text view
* 6f59182 [security] Added path autocomplete
* d43a63f [security] Improved tree display
* fc58f59 [security] List tables with doas option
* 04238da [security] Improving Hive autocomplete
* 72dbaa3 [security] Update HDFS path when picking another user
* 27671ac [security] Pagination skeleton for fetching more files
* 1123290 [security] First draft of tree
* 66ef002 [security] Base for group and user autocomplete
* 2f3afc1 [security] Rename an HDFS acl
* c0555c5 [security] Split default rules below
* 8ed2747 [security] Manage default HDFS acls
* 24237c5 [security] Started UI cleanup
* 1ec14c0 [security] Highlight files with acl in the listing
* c7ac355 [security] Edit an HDFS acl
* 98817aa [security] Adding security API module
* 8369250 [security] Remove an HDFS acl
* 459c611 [security] Split api into several modules
* 8f545e1 [security] Adding missing build files
* cd04d98 [security] Add some HDFS acls
* c9b256c [security] Remove dependency on fb Thrift
* 25ad2e0 [security] Adding static files
* bb0f2e9 [security] Add privileges to existing Hive role
* 45a2bc3 [security] Create a Hive role section
* 9e8b169 [security] Implement Hive list_sentry_privileges_for_provider
* b2e6e24 [security] Bases of main Hive page
* d3ba014 [security] Edition and listing of roles and groups
* 7431ac0 [security] Preparing adding a new HDFS ACL form
* b24b35d [security] List existing HDFS ACLs
* a07d9ed [security] Adding API to list priviledges of an object
* 4c50f80 [security] Adding HDFS ACL API
* e71e200 [security] Initial skeleton
* b5fb623 [sentry] Cleanup and remove autocomplete for now
* 415ec1e [sentry] Add sentry client and API
* 028db3a [core] Thrift TMultiplexedProtocol support
* 8afc15b [search] Fixes for the empty dashboards admin page
* d510eca HUE-2236 [fb] Cannot open some csv files
* c0da227 HUE-2224 [beeswax] Ignore escaped characters while splitting queries
* 3142076 HUE-2242 [metastore] Support tables of more thant 1000 columns
* 8d6ac91 HUE-1514 [filebrowser] Add a note to the UI if the file contents are specially rendered
* 5b9467d HUE-2231 [fb] Make current directory selectable
* d7297bb HUE-2231 [fb] Make current directory selectable
* f306348 HUE-2237 [search] Search input duplicates text
* b1666a9 HUE-2238 [core] The Hue app logo is huge on IE9
* ca921d5 HUE-2234 [core] Select first document or shared document tag by default
* adf679f HUE-2224 [beeswax] Query editor does not properly split statements
* 28304d5 HUE-2231 [fb] Updated unit test to look for correct index
* fe1951a [core] Update integration tests to pull the latest Hadoop jars
* 2209fca HUE-2231 [fb] Make current directory selectable
* 1aaf411 HUE-2232 [search] Examples don't install with MySql
* 02fb1d6 HUE-2034 [metastore] Enable links in hive table/column comments
* 6bb4941 HUE-2123 [beeswax] Handle cancel state properly
* 29c8186 HUE-2176 [oozie] Changed refresh intervals
* 8087249 HUE-2176 [oozie] Progress report on dashboard can slow the page a lot
* cca5aec [search] UX improvements for the admin section
* fb0615d HUE-2212 [metastore] Memory can leak when getting a sample of data of a table
* c5f41e7 HUE-2223 [beeswax] Bigints are rounded on result tab
* f294650 [oozie] Fix broken submit Java action test
* 03c90dd [beeswax] Improve some German translations
* 18b3828 HUE-2221 [oozie] Remove spaces in workflow names examples
* d285c09 HUE-2215 [jb] Display job counters with YARN
* b05e6d0 HUE-2186 [search] Bulk copy collection templates
* ff06225 HUE-2186 [search] Bulk copy collection templates
* 1699f0a HUE-2186 [search] Bulk edit collection templates
* 4648477 HUE-2028 [pig] The end of logs can be missing
* 1fa0c53 HUE-2119 [filebrowser] Show extended permission in mode
* f0b9138 HUE-2211 [search] Twitter and Jobs example do not load properly
* c69f398 [hive] Fixed Japanase translation issues
* bbcc2fa HUE-2207 [search] Timeline date changes are not saved when edited manually
* 8f86d28 HUE-2209 [core] Install examples links should not autoscroll to the top of the page
* 8c29a4b HUE-2076 [core] Create retina icons/logos
* 489cd4f [metastore] Support of UTF-8 in the comments and names of tables
* cc8defd HUE-2122 [impala] Smarter db and table cache
* 978bacf HUE-2178 [core] Refactor and extract as a lib search layout
* 0109c9d [core] Support Resource Manager HA active / standby switching
* 0148bbb HUE-2192 [core] Create parameter to choose LDAP username for HS2
* 7a98cef HUE-2193 [beeswax] Updates the tests for HiveServer2 LDAP
* 6e47e3f HUE-2193 [beeswax] HiveServer2 pass-through LDAP authentication at thrift level
* 95e1b31 HUE-2196 [beeswax] Explain doesn't account for Hive settings
* 75681d5 HUE-2178 [core] Refactor and extract as a lib search charts
* 6e5c552 HUE-2177 [impala] DB assist should support zero databases
* 1a3b913 [libsolr] Security impersonation for all the API operations
* b44cae9 HUE-2189 [search] Exporting results should not add extra HTML
* 711ea71 HUE-2188 [beeswax] Remove Email me on completion
* 20fd248 HUE-2184 [core] Connect to Oracle via Service Name
* bcc1b7e HUE-2190 [search] Truncate function doesn't work anymore
* 2594fc5 [doc] Update README to propose a compatible maven
* 3e1a326 [core] Shrink char field max length
* e9e31e6 HUE-2138 [search] Slider widget UX
* 19636e0 HUE-2138 [search] Slider widget UX
* c32867a HUE-2175 [oozie] Also generate timeout value of zero in coordinator XML
* a9c207b [oozie] Remove some fields in the workflow dashboard tables
* 2237563 HUE-2166 [core] Oracle database support in doc model
* 8eb4ce0 HUE-2163 [search] Some closure widget click problems
* 20d0ca1 HUE-2174 [jobbrowser] HTTP 500 error if on MR1
* d75baf9 HUE-2166 [core] Oracle database support in doc model
* bd9a0b7 HUE-2170 [search] Grid layour table header and body don't align
* c231af1 [search] Authorize more than one line chart
* 3fa2107 [oozie] Fix date conversion test
* f57e0f4 HUE-2169 [search] Sort field list in HTML layout can overflow
* 3f27c55 HUE-2157 [search] Update Gridlayout field list on search
* 378f789 [core] Resource Manager RM HA
* 3e5c6f3 HUE-2164 [core] Create retina favicon
* 44ad542 HUE-2161 [oozie] Kill job popup in dashboard should disable the ok button
* fe12969 HUE-2017 [search] Warning that highlightning only works if documents have and id field
* 0ed5ca5 HUE-2167 [search] Solr might not always return a document
* 22e1401 HUE-2165 [search] syncFields() can corrupt the model
* 55e742a HUE-2128 [search] Timeline dates are not loaded properly
* 3425299 [search] Subscribe to facet limit change
* 3c011bc HUE-2132 [search] Offer field sorting within the HTML widget
* b62564c [oozie] Simplify some dates when strptime() does not support %Z
* afb4f7d HUE-2162 [search] Group by facet on timeline widget errors
* 6d0f852 [core] Fix some date format in the headers of the po files
* bf45be6 [core] Updating localization strings
* b0b76f6 [core] Add default options for databases
* 35e19ca [core] update "minicluster" versions
* e933469 HUE-2113 [oozie] Coordinator "next submission" shows overall endtime
* 295a8ee HUE-1916 [oozie] Create coordinator should not get a localized date
* 2dc9729 [core] Fix LDAP tests
* f91a0b4 HUE-2137 [indexer] Support core creation in non Solr cloud mode
* f0307d2 [spark] Is empty result should work with any type of data
* f3549ea HUE-2143 [beeswax] MR job links are not always displayed
* 8e51a5f HUE-2148 [search] Download query can be missing some columns
* f12d89e HUE-2157 [search] Gridlayout field list min height could match number of rows
* 6a1aa3d HUE-2149 [search] More facets are displayed when limit is small
* 7a8d897 HUE-1917 [oozie] Crontab support in dashboard
* 0ce3fbd [useradmin] LDAP DNs should accept spaces
* 553faf6 [core] Add note about threaded option and Oracle databases
* 9ec6187 [jb] Basic test with mocking for view and modify acl and MR1
* db062d7 [jb] Also show jobs according to acl view permissions
* dabe214 [jb] Also show jobs according to acl modify permissions
* 4d3b778 HUE-2126 [search] Beautify limit, range, zoom out, etc. of widgets
* a4e91be [impala] Close queries commands cannot work for Impala
* 851cd1f [beeswax] Cleared all old references to Beeswax daemon
* 820c187 [beeswax] Close query for any type of queries
* 2193d9d [beeswax] Close Beeswax queries
* e76d055 [beeswax] Rename error to info
* ec11741 [beeswax] Integrate hive-site.xml into the Hive commands
* bca90eb [search] Download first 1000 rows of a query
* 481d8a1 [jb] Sort jobs by date by default instead of job ids
* 348e424 HUE-2133 [search] Support Solr date facet format in widgets
* 4b4f63f HUE-2124 [oozie] HDFS Deployment directory is missing "slash" symbol
* 916722c HUE-2129 [search] Show selected bar on bar charts
* 322a401 [search] Adding user agent bar chart to the Apache log example
* 1453bd2 HUE-2135 [search] Support non Solr cloud mode
* 376589b HUE-2130 [search] Prettyfy empty result
* 61e8d36 HUE-2141 [search] Fail gracefully when a collection does not exist
* 9df4725 HUE-2138 [search] Slider widget UX
* f795a9f [core] LDAP search bind authentication should be at server record level
* 86f0395 HUE-2127 [indexer] Select a default field
* 777646d HUE-2105 [beeswax] Sort alphabetically the navigator tables
* dcee4fe [spark] Saveas does not lose the design id
* 63355cb [spark] Bubble up error message when query has ERROR status
* e4e72d6 [spark] Query URL does not conflict anymore when loading a saved query
* 7cdc8be [search] Adding better range to the timeline of twitter example
* aff5c27 [indexer] Rename collection examples to demos
* d6f8a46 [search] Limit query length to 4096
* 8611fc0 HUE-2125 [search] Invalid date label on timeline chart
* c3c7040 [core] Ldap commands should accept server argument


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
- Paul Mccaughtry
- Philip Zeyliger
- Romain Rigaux
- Roman Shaposhnik
- Shawn Van Ittersum
- Shrijeet Paliwal
- Thomas Aylott
- Todd Lipcon
- Vinithra Varadharajan

