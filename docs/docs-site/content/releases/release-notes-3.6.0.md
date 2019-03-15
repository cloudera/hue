---
title: "3.6.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -3060
tags: ['skipIndexing']
---

### Hue v3.6.0, released Thursday 29th, May 2014


Hue, http://gethue.com, is an open source UI for doing big data analysis with Hadoop.

It features:

- File Browser for accessing HDFS
- Hive Editor for developing and running Hive queries
- Search App for querying, exploring, visualizing data and dashboards with Solr
- Impala App for executing interactive SQL queries
- Spark Editor and Dashboard
- Pig Editor for submitting Pig scripts
- Oozie Editor and Dashboard for submitting and monitoring workflows, coordinators and bundles
- HBase Browser for visualizing, querying and modifying HBase tables
- Metastore Browser for accessing Hive metadata and HCatalog
- Job Browser for accessing MapReduce jobs (MR1/MR2-YARN)
- Job Designer for creating MapReduce/Streaming/Java jobs
- A Sqoop 2 Editor and Dashboard
- A ZooKeeper Browser and Editor
- A DB Query Editor for MySql, PostgreSQL, SQLite and Oracle

On top of that, a SDK is available for creating new apps integrated with Hadoop.

More user and developer documentation is available at http://gethue.com.


Latest Notable Features
-----------------------

- [Search App v2: Dynamic search dashboards with Solr](http://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr)
- 100% Dynamic dashboard
- Drag & Drop dashboard builder
- Text, Timeline, Pie, Line, Bar, Map, Filters, Grid and HTML widgets
- Solr Index creation wizard from a file

- [View Snappy compressed Avro](http://gethue.com/visualize-snappy-compressed-avro-files/)/Parquet files
- [Impala HA](http://gethue.com/hadoop-tutorial-how-to-distribute-impala-query-load/)



Compatibility
-------------

Runs on CentOS versions 5 to 6, Red Hat Enterprise Linux (RHEL), and Ubuntu 10.04 to 12.10.
CentOS 5 and RHEL 5 requires EPEL python 2.6 package.

Tested with CDH5. Specifically:

- Hadoop 0.20 / 2.3.0
- Hive 0.13.0
- Oozie 4.0
- HBase 0.98
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


List of 784 Commits
-------------------

* 907ec26 [doc] Hue 3.6 release notes
* 16ac841 [indexer] Fix quoting and python version
* 55261f5 [metastore] UnicodeDecodeError when viewing schema of table
* 1e8ea71 [search] Add correct start date in twitter example
* de0b82f [search] Better animate to column
* caaf31e HUE-2124 [oozie] HDFS Deployment directory is missing "slash" symbol
* 7ce38bb [search] Trailing whitespaces and tabs cleanup
* bae6007 [search] Disable is editing
* 335d623 [search] Changed date picker
* 4b8faae [search] Editable widget popup should open on the right
* 84df243 [search] Scroll to field
* 66fe2b1 [search] Added spinedit for limit
* e368eee [search] Added daterangepicker
* 0d507fb [search] Support moving map widgets
* ddddcf6 [search] Cleaner gridlayout headers when no fields are selected
* 606c39f [search] Koify getdocument in result grid layout
* 8132720 [search] Zooming out does not reset filter
* 354f17e [search] Make sure min or max properties of range facet are restricted
* 043230b [search] Added formatters and reverse formatters for slider
* 1973d6f [search] Reduced a bit the slider size
* 782c6da [search] Styled a bit the settings panel
* af93938 [search] Minor CSS fix
* 40870c3 [search] Added Indexes menu link
* 1ba0fba [search] Added visual hint for updating charts for slower collections
* 899b800 [search] Fix range select color
* e66a598 [search] Set max width for slider to 250px
* 64944e2 [search] Fixed slider z-index problem
* 0963a18 [search] Fixed clearable click event
* 0087d49 [search] Add min and max field properties to range facets
* e620b8c [search] Truncate milliseconds in dates for better timelines
* 2df9942 [search] Restyled a bit grid results, added all/current filter
* 42a2edf [search] Externalized CSS and streamlined Less addition
* 4a6c582 [search] Avoid line wrapping on result row
* 8981258 [search] Fix field list size for magic layout
* 2884912 [search] Slider binding
* 918b31f [indexer] All fields should be stored by default
* d9c9349 [core] Move create collection or core to the new dashboard
* 22e5bd4 [search] Import and convert older collections
* b4d174e [indexer] Add modal dialogue for deleting a single collection
* d9cb9fc [indexer] Setup examples in search API
* 3fd67ab [indexer] Unique key field must be indexed
* b37afe7 [indexer] Choose field type more intelligently
* f6f9de4 [indexer] Choose unique key field more intelligently
* 0b89284 [indexer] Change config defaults
* bcc362a [search] Escape extracode in HTML widget
* b758d4a [indexer] Install examples in admin wizard
* 66872a2 [indexer] All fields should be indexed by default
* 9bf3501 [indexer] Add confirmation when deleting collections
* 8af533f [search] Install search templates
* d6f1692 [search] Partial cleanup of indexer
* ffaea0f [search] First fix for result jump
* b05c914 [search] Use gradient map
* f6e4874 [search] Re-init range facet when deleting its filter
* eba76c4 [search] Add correct closure to support multiple bar charts
* 8e627dd [search] Range and field support for bar chart
* e045c3a [search] Clearable fix for Retina displays
* 9059baa [search] New binding clearable
* d14f4d2 [indexer] Add install examples view
* 517c4e9 [indexer] Add logs example
* 8c85408 [indexer] Add jobs example
* 50aa919 [indexer] Add yelp example
* ef37713 [search] Adding collection settings tab
* 66b5330 [search] Replace log_demo by log_analytics_demo
* c583e90 [search] Restrict edition to admin only
* 9b09086 [search] Introduced share dialog
* 0b11f78 [search] Current query is URL shareable
* 348d966 [search] Added empty dashboard message
* 8031706 [search] convert multi queries to new api
* 4ba8eed [search] Workaround for fq filter with a space in the value
* 8b17c43 [indexer] Fix 'nodeType' of undefined errors
* 3625306 [indexer] Improve timestamp type check
* 85e7ae5 [indexer] Respect newlines in quotes
* 161f60b [indexer] Remove constant redirection
* f9ee757 [search] Adding Apache log demo example
* e50d144 [search] Fix for drag existing widget to new row helper
* 536fc1d [search] Fixed line chart selected range values
* 90fd4bd [search] Updating the tests
* 260e414 [search] Remove deprecated version
* 3c025f7 [search] Fixed enable selection
* 5de11b8 [search] Fixed selection on line chart
* dabec3e [search] Changed color to selected area
* 15691b8 [search] Plugin select events on the line and bar charts
* 6764548 [search] Added more evident selected state to maps and fixed modal dialog hide event
* 48a351b [search] Smarter line chart
* 9b30bdf [search] Smarter date range facets
* 7b42475 [search] Smarter range facets for numbers
* 5c9d0ff [search] Restyled result pagination
* babb900 [search] Result pagination doesn't scroll anymore
* 365c399 [search] Finalized field list UI
* 1509d0c [search] Esc on field list modal deletes the widget now
* 6a621f1 [core] jHueNotify shouldn't display HTML content
* fbde025 [search] Fix row height problem
* 8763e27 [indexer] Remove example dir and use search examples
* 1de9afc [indexer] Add indexer examples
* 13802d6 [search] Enable selected countries/states on Datamaps
* e339079 [search] Generic URL to browse any collection
* bf519f7 [indexer] Choose between tlong and tint
* c640bf2 [indexer] Use tdate instead of date when choosing types
* 6f459ad [indexer] Add labels for field separators
* 4ae194a [indexer] Remove log type
* adfb2dd [indexer] Add breadcrums
* 89d8298 [indexer] Change to metastore like layout
* 64ac825 [indexer] Change defaults of 'add field' screen
* b0a69b6 [indexer] Parse timestamp field for separated files
* 677273a [indexer] Use tdate instead of date when groking fields
* a29f562 [indexer] Get rid of internal collection management
* 8f4049b [indexer] Improve data upload
* 10f2197 [indexer] UI/UX improvements
* f3d65ef [search] Removed spinedit that broke everything.
* a2ffa3d [search] Squeeze some white spaces
* 95f5401 [search] Restyled demi modal
* b333451 [search] Added enable selection to line chart
* ee437cc [search] Clickable map creates filters that can be toggled
* f2703e6 [search] Adding some various states in the example
* 008e991 [search] Restyled filter bar
* 367c8bd [search] Better click even for Datamaps
* 68bc031 [search] Select a place on map and create a filter
* eb72327 [search] Adding scope to the map widget
* 6acb6f2 [search] Added maxWidth for Pie chart
* 3b7b06c [search] Converted barchart to brushBarChart
* 2998bad [search] Disabled mouseover jump
* f584a9d [search] Map works with country codes
* 5597be0 [search] Default text facet size is 10 even if range facet
* b0b4cdc [search] Added multiline labels after chart update
* 18215b9 [search] Removed extra space underneath charts
* e6b56e2 [search] Fixed onClick event of growingMultibarChart
* 990b2c4 [search] Added maxWidth to map binding
* 217630e [search] Deleted unused files, Maps: added enableGeocoding, onClick event, data tooltip, Widgets: resize event, fixed double markup, updated sortable
* b9e7b0b [search] Added empty row at the beginning of a column too
* d421347 [search] New properties tab in HTML result
* b6f4f97 [search] Enable pick button when field is selected
* 8e08088 [search] Highlight HTML results and escape only once
* 3c346f7 [search] Add job collection to the examples
* 8b6f05f [search] Added step support to slider
* 8db7d31 [search] Added bindings for slider
* 71557fc [search] Added Bootstrap spinedit binding
* 4a87d55 [search] Field list adjust its height to the result panel
* 530c833 [search] Restyled fields modal
* 6c5f9b0 [indexer] Remove only selected collections
* 4384698 [indexer] Remove symlink version
* 04255ec [search] Synchronize dynamic fields
* abca560 [search] Synchronize static fields
* 62d7b00 [search] Make field list of gridlayout a computed
* 5c7feec [indexer] Hook into search app
* 6e5e313 [indexer] Fix log upload
* beae907 [indexer] Make indexer lib work with its urls
* 21e4b24 [indexer] Remove schema generator
* 92bb82a [indexer] Move collection manager to indexer lib
* dbcb249 [collectionmanager] Add other field types
* e667f87 HUE-2037 [search] Index a file or hive table easily
* 119da98 [search] Removed unused jQuery files
* 529f2bd [search] Added inline document details
* a52f8d5 [search] Add location field to the log example
* 1e9b35f [search] Update template of magic layout
* 4db6a26 [search] Update gridlayout field list in a new dashboard
* 612f200 [search] Restyled field list
* 4a34768 [search] Refresh new collection redirects to collection itself
* 52ebfb8 [search] Fix hover field titles
* 4b95e65 [search] Update template and field list of new collections
* ae5887e [search] Fix hover field titles
* dc49588 [search] Move column chevron icons on hover
* dfe7d63 [search] Added drag to new row
* 00223ff [search] Download results in json, csv or xls
* ece2c68 [search] Fixed empty callback for search
* c292bd4 [search] Added field and function selects to html resultset editor
* 0731f6b [search] Pagination should use numbers and not strings
* 0323612 [search] Fetch new fields when creating a collection dashboard
* 9644ea0 [search] Added freshereditor
* 01af39a [search] Added scroll back to initial position
* f7c57ee [search] Add field modal preview and cancel functions
* 7483e40 [search] Added editable to other widgets too
* a5e7f67 [search] Fixed ko.editable to update enabled/disabled status
* cc49870 [search] Inverted X axis labels and changed icon for timeline
* b975d24 [search] Add see more or less on text facets
* 6a9d1dd [search] Added multiline x-axis labels for timeline
* dfc517b [search] Update number of rows and template only after n seconds
* ef54ae3 [search] Widget name is now editable
* e86611a [search] Removed zIndex from Pie draggable
* 497ceb2 [search] Next and previous pagination
* b24f682 [search] Adding number of rows pagination
* 19fb05a [search] Bump jQuery and jQuery UI versions
* c9d59b7 [search] First version of result inspector
* 1b17000 [search] Removed media queries for the toolbar
* 73ec3ac [search] Made rows more visible in edit mode
* 7b93ba9 [search] Fixed stacked hover effect
* e59ba91 [search] Limited CSS to result pane only
* 97d1573 [search] Introduced ko bindings for Codemirror
* dabdab6 [search] Restyled available widgets
* 24892af [search] Add move icon to drag widget
* 57d487b [search] Autocomplete add a widget field input
* 6c3784f [search] Only display available fields in add widget modal
* c3887a1 [search] Enable or disable available widgets
* 7094a94 [search] Enforce only one instance of certain types of widgets
* e1f7da7 [search] Split grid and HTML resultset widgets
* 36ef323 [search] Filter widget styled
* 971655e [search] Set facet label or widget type to the widget title
* 6cccf16 [search] Remove widgets inside a row when deleting it
* 82a0110 [search] Removed loading from filter widget and added empty message
* 8e5abfb [search] Cleaner text facet links
* 00dc723 [search] Do not show field picker on Filter Bar
* fbc2272 [search] Minify widgets on new widget drag
* 5102fe8 [search] Minify widgets on new widget drag
* f806b9b [search] First pass of beautification
* 8f53979 [search] Switch facet type icons for widgets
* 286f05c [search] Create a new template based on any solr collection
* bc88af6 [search] Fix for delete facet
* 200cf51 [search] Introducting enable selection on histogram
* b6cf638 [search] Fix loading spinner on Text facet
* c355f83 [search] Authorize search page without a dashboard
* ffa2807 [search] Optimize range multi facet queries
* 9de47ca [search] Multi select range facets
* 8609451 [search] Prepare for multi select of range facets
* 9297f30 [search] Persist stacked or not property of histogram
* 37a9cd3 [search] Split facet range and sort order buttons
* 4e37306 [search] Propagate state change
* d48a3e7 [search] More on maps
* 871ad00 [search] Added option to set stacked for barcharts and timeline charts
* 3e9580c [search] Adding count to facet multiqueries
* 6652ad0 [search] Multi queries by search box or field facet logic
* be9a2dd [search] Multi search boxes queries
* 039b0de [search] Fix refresh of group by option of histogram
* 512c607 [search] Fix zooming back from histogram
* 7ee1f8b [search] Range select should also filter the result documents
* 880db24 [search] Multi queries for timeline
* 3aaa909 [search] First version of Hue Geo
* 05d6e92 [search] Fix multibar highlight
* 72f1a71 [search] Initial map support
* 154c8d7 [search] Add support for bar highlight
* b45da61 [search] Added line chart support
* cdb8763 [search] Do not show field selector for result widget
* 8cd81eb [search] Dynamic range of historgram widget
* 11ea101 [search] Escape HTML cells in gridlayout
* 7c5e323 [search] Fix timeline data transformer
* 5799efd [search] Furtherly improved d&d
* e72f67a [search] Improved usability of drag & drop
* 996326b [search] Disable scroll to top and auto open field list demi modal
* 6c28d96 [search] Visual feedback for drop targets
* c21b3ca [search] Ground work for multi serie bar charts
* 542cb5d [search] Added DiscreteBarChart support
* d14fab1 [search] Escape HTML cells in gridlayout
* 5791b53 [search] Retrieve single doc by id
* 8dae122 [search] Added Pie chart selection and mouseover handling
* f841468 [search] Fix call to onSelectRange
* 606c571 [search] Introduced media queries for the top bar
* 1a1ede7 [search] Propagate onSelectRange
* 251ab34 [search] Converted top bar layout images to css
* 7a53776 [search] Re-enable copy/paste in edit mode
* 6ddfa77 [search] Move gridlayout columns to left or right
* a64cb32 [search] Removing a widget should remove its filters
* 0d23d80 [search] Splitting templates of range/field widgets like text and pie
* d12fd2a [search] Multi filter for range facets
* d3b3c9d [search] Multi fq support for text facet
* a9fb00d [search] Added new field selection modal
* b4a4f51 [search] Added selection management on multiBarChart
* 3ae84c6 [search] Ask only for the used fields in the gridlayout
* 4333667 [search] Make pie widget work with range facet
* bc7ca8a [search] Smarter number of slots for text range facets
* 3f05860 [search] Toggle facet order and type
* df559a9 [search] Skeleton for magic layout
* 6da1259 [search] Text, pie and bar facets can also be ranges
* 620e231 [search] Added barChart code for handling time data
* 1cf0fa2 [search] Adding bar char widget
* 37c0837 [search] Add date support fo range facet
* f8c3a4c [search] Extracted charting to external js file
* 886b03c [search] Added first version of multiBar
* 3f3986d [search] Adding range facets with numbers
* 336e3a9 [search] Adding histogram widget
* 788b5ac [search] Added first version of Pie and changed drag handler
* 041a01c [search] Added nvd3 dependencies
* 32cac55 [search] Fix modifying an existing collection template
* 142f055 [search] Add Pie widget
* 18aaff6 [search] Display all the columns in the grid layout
* 64ec801 [search] Add Hit Count facet
* f5bd061 [search] Save a new collection button
* 02e5746 [search] Add a new template button
* 65022ca [search] Adding support for sorting the grid layout
* 5d260ef [search] Adding template for result pagination
* faec4ff [search] Adding empty search result message
* 78a092b [search] Adding list of fields with extended metadata like types
* 1a325c2 [search] Add id to widgets to map them to a model object
* f5f0201 [search] Edit and remove facet attached to the layout
* 7bf0494 [search] Fix toggling of the gridlayout show field list
* 5a611dc [search] Do not add dynamic fields more than once
* a661e8f [search] Do not try to convert empty collections
* f78c813 [search] Load back the saved layout
* 40d6aa8 [search] Add toggle field list visibility in grid layout
* a6893ec [search] Make grid field selection button toggable
* e9d9d03 [search] Display whole json record when no fields are selected
* 49edd09 [search] Fix refresh when switching back to grid layout in edit mode
* fa90c10 [search] Updating WIP
* b3892bb [search] Start to prettify
* eb46c8e [search] Guess id field for result highlighting
* dd2159d [search] Save the template of a collection
* 9dc26fc [search] Collection and facet edition integration
* 63e409e [search] Merging dashboard and search page
* b75ef6d [search] Refactoring API and KO models
* fe88c7d [search] Simpliying search API
* 79b5bbe [search] Dashboard cleanup
* 221b11c [search] Prettified dashboard
* 36e8051 [search] Added dashboard toolbar
* f884511 [search] Dashboard prettify
* 80d73b7 [search] Adding a dashboard
* 7a603c6 HUE-2108 [metastore] Error when dropping a table
* 9175b87 [useradmin] Remove server selection from ldap functionality when using legacy configuration
* 11582cb [core] Invert dependency list and merge migrations
* 0520f6c HUE-1957 [core] Configure thrift transport
* d8822ac HUE-2085 [core] Update migration dependencies
* 9a3d1b4 HUE-2101 [fb] Copying a file trims the last chunk
* 7f74580 HUE-2112 [fb] The 'New' dropdown goes off screen
* b186265 [search] Rename Navigator to Assist
* b05324e HUE-2111 [pig] Enable collapse of navigator items
* 6ad3895 HUE-2110 [core] Update FontAwesome to 4.1
* 0fd00f1 HUE-2089 [useradmin] Sync ldap users modal form is misaligned
* e988bde HUE-2099 [jobbrowser] Improve metadata tab performances
* c0c1bef HUE-2106 [beeswax] Table list and query caches should be per user
* 3e3236f [core] New datanode report format
* 03b82fc HUE-2095 [beeswax] Do not fetch statements without a resultset
* 9fe2102 HUE-2091 [fb] Configurable tempfile.tempdir for local file upload
* 0a895a9 [beeswax] Escape space to HTML spaces in some tests
* 403cd90 [liboauth] Add a mapping to shorten domain names in usernames
* deeb9b6 HUE-2109 [core] Use MPL instead of LGPL for certificate bundle
* 556d9fd [metastore] Do not concatenate spaces in cells result
* a1fba50 HUE-2104 [beeswax] Don't truncate space characted values from query results
* 21938ff HUE-2100 [beeswax] Query with error should not show the cancel button
* e11b285 [sqoop] Not unicode strings in argument expansion
* e436a8a [core] Stream CSV download and limit XLS download
* 8c9388c HUE-1897 [oozie] Workflow ids have double trailing slashes
* 7316408 [beeswax] Clone copy to a new owner option
* 94026fb HUE-2058 [oozie] Incomplete save state in workflow editor
* 965f9ca HUE-2039 [beeswax] Remove the need to clone a shared query
* 8d72adb HUE-2059 [core] Only display history documents in their home section
* b5148b4 HUE-2096 [core] Error on login page are duplicated
* f9800d5 HUE-2087 [beeswax] Job is submitted twice when the Enter key is used for the Execute button
* 72e880d HUE-2074 [core] Update Knockout to 3.1
* 4196369 HUE-2070 [metastore] Improve guess of numeric data types
* 465d5a0 [core] RemoteUser middleware fixes
* 0f86364 [core] Improve memory debug view
* f37ba45 [core] Add BeautifulSoup and have requests use it
* 9eac028 HUE-2026 [core] Create a doc model write permission
* 144142a HUE-2026 [core] Create a doc model write permission
* 28189e9 HUE-2026 [core] Create a doc model write permission
* 0394d64 Revert "[core] Add python-snappy library"
* d09dce2 Revert "[core] make snappy a first class citizen"
* a106006 HUE-296 [core] Memory profiling config
* 7e5ffff [core] Fix LDAP and useradmin group list tests
* f541560 HUE-296 [core] Add memory usage debug view
* dc17a4a HUE-296 [core] Add guppy debugger
* cf3d770 HUE-2080 [core] Update tours URLs
* 8af30e0 HUE-2072 [core] Disable SSL proxy header by default
* b293f95 HUE-2072 [core] Updating Proxy SSL support to be optional
* b69811f HUE-2072 [core] Adding support for HTTPS load-balancing
* b3a760d HUE-2012 [core] AD multidomain support
* e4ff348 HUE-2012 [core] upgrade django auth ldap
* b1baed4 [filebrowser] Snappy decompression error should throw PopupException
* 810af74 [desktop] A user can share a document to a group he does not belong too
* 9f3fb69 [beeswax] Close HiveServer2 and Impala session command
* 2321211 [filebrowser] read parquet in filebrowser
* 63ba4f1 [core] update parquet-python to use file objects
* 75261c1 [core] add parquet-python library
* 8d15fcf [core] make snappy a first class citizen
* c8a63af [core] Add python-snappy library
* cc4a896 HUE-2068 [infra] Third-party dependencies manifest is excluded from binary distributions
* c2ec0e6 HUE-2043 [core] database options keys have unicode keys
* 5fb9260 [core] Remove python 2.4 and 2.5 from python selection
* 182f8da HUE-2069 [jb] The new jobs in ACCEPTED state are not automatically appearing
* 9ee9004 [core] Remove some bad links in the documentation
* 819ef4d [core] Yarn check config should not depend on test code
* d1e9de8 HUE-2061 [jb] Does not use the node address when task is not running
* 8e79c58 HUE-2062 [pig] Editor fails with non ASCII characters
* 4897c52 HUE-2065 [core] Make sure log page is proposed only to superusers
* 8f82dda HUE-2063 [beeswax] The map chart does not display
* 6ff62b5 HUE-2063 [beeswax] The map chart does not display
* 4f60306 HUE-2061 [jb] Task logs are not retrieved if containers not on the same host
* 7a67dd3 [useradmin] Fix translations in ldap cli commands
* d29a902 [useradmin] LDAP import commands carry incorrect import statements
* 0a4eacd [core] Integrate feedback tab when running in demo mode
* 4d7628c HUE-577 File viewer should work with snappy-compressed Avro data files
* 5ff543d [core] upgrade avro library
* ee5aecc HUE-2047 [oozie] Clicking on workflows only works for first page of Workflow Manager
* 0ac366c HUE-2033 [core] Cleanup and tests update
* 56e21e2 HUE-2033 [core] Reviews findings
* 54ab7ec HUE-2033 [core] Fixed document update after project or sharing changes
* 3ab0f02 HUE-2033 Merge back the new home page
* 53b07db HUE-2033 [core] Fix counting of shared documents
* 5595e06 HUE-2033 [core] Added project move functionality
* ff8f72a HUE-2033 [core] Readded sharing functionality
* 1f2061e HUE-2033 [core] Refactored UX for remove project
* 80dab73 HUE-2033 [core] Added project management functionality
* 1dc4654 HUE-2033 [core] Cleaned style of the documents and tags
* 38f1ed3 HUE-2033 [core] Link back backend to homepage 2
* ed85ae4 HUE-2033 [core] Dynamic and robust home page
* a2e65e2 [beeswax] Check for ownership before saving
* cea265d [core] Add third-party dependency references
* 5c7ef36 HUE-2040 [useradmin] Synchronize nested ldap groups
* 7544de2 [core] make suboordinate subgroups the default
* 010066f [core] remove bad import from python util tests
* 69b9656 HUE-1177 [jb] Improve MR2 UX with correct percentage progress
* 5784e15 HUE-2041 [pig] Improve log polling usage
* d328bd0 [core] Remove unused desktop JS libraries
* 592649f HUE-1989 [core] Move the js logic to the home page
* a235e4e [core] Second pass of l10n for 3.5
* 912c2f8 HUE-2010 [core] Configure Hue to terminate users who has not logged in X days
* 27a5925 [oozie] Migrate examples with mkdirs and touchzs paths
* 8cec8cd HUE-1890 [oozie] Longer input fields in workflow editor
* f698a29 HUE-2032 [beeswax] Order by autocomplete should propose columns
* ba5907c [jobsub] Add description to 'get_design' call
* 267b227 [oozie] Import workflow imports mkdirs and touchsz as lists of dictionaries
* d62d465 [core] Move welcome tour to home
* 33c43c7 HUE-1801 [fb] Introduce pages with scroll when viewing a file
* 9a8aeae [core] Add Feedback label for demo
* 1380e84 HUE-1989 [core] Welcome tour on the home page
* 38ae9d6 HUE-1888 [beeswax] Code mirror placeholder i18n
* 4e27324 HUE-2011 [impala] Autocomplete a non existing table hangs
* c7ae876 HUE-2016 [core] Improve the shadows for stateful buttons
* 0f151d0 [core] Nested members support
* 6cc6604 [core] Fix tag refresh after delete or create
* f502a5e [core] Display all the tags
* 5448fb2 [metastore] Hide recent query tab when browsing a table
* 0569298 [impala] Fix link to metastore browser table
* fd23026 [core] Installed apps with no webpage on dump_config should not propose links
* f208e4e HUE-1962 [hbase] Support int row key from Hive table
* d6c869c [impala] Replace non utf8 encoded chars from the resultsets
* 76064c6 [liboauth] Limit oauth login to specific list of domains
* 7307bf6 [liboauth] Show error message after Aouth login failure
* 5cee8ea [liboauth] Indentation fix
* 49bbfc8 HUE-2020 [hbase] upload an image sometimes produces an error
* cf39ae2 [hbase] Fix new cell upload
* 618672d [core] Secure shared tag edition
* 4a15302 HUE-1989 [site] Live demo hosting
* 0ef4c1f [oozie] Change unsaved workflow message
* d45bd82 [impala] Separate server timeouts
* a5d623a [impala] Disable ssl when using impala
* abbc506 HUE-1868 [dbquery] Query then error moves headers
* 02121a4 HUE-2029 [oozie] Prompt to save a workflow before submission if it was modified
* 7ebffae [impala] Hide system database from the main editor dropdown
* dcfad9c [core] Adding autofocus on username field on login
* 28dc4e6 [oozie] Fix delete button misrepresenting the correct permissions
* 4df787b [pig] Enforce write permissions on the shared scripts
* f27cc76 HUE-1298 [impala] Multiple Impalad support
* 55865b1 HUE-2022 [core] Add login button to top bar when not authenticated
* 2f51c78 HUE-2021 [core] Close tours list by pressing ESC or clicking anywhere else
* d6c53e9 [impala] Align sync table tips
* 077faf6 [search] Display errors from Solr instead of a 500
* 75691d9 HUE-1804 [core] Serve admin static files
* d18c249 [doc] Update screenshot and app descriptions
* 1f0fa51 [search] Add double and tdouble to range facets
* dba67fd HUE-2022 [core] Add login button to top bar when not authenticated
* e7d8d64 [core] Make the tours modal escape-able by escape key
* 38eea26 HUE-2018 [metastore] Add column position to table view
* 6860085 [core] Fix several broken and hanging tests
* 518559e [hbase] A couple of bug fixes
* e3c095a HUE-1884 [core] Split tag view in shared and not shared ones
* 1b9b32d HUE-1884 [core] Limit number of history documents
* 05774d2 [useradmin] Hide LDAP sync buttons when LDAP is not configured
* 4a728d0 [core] Update configuration check path color
* 746f481 HUE-2013 [metastore] Write permission instead of read permission
* b43a601 HUE-2008 [pig] Clicking on the stop button should stop on the frontend
* f30cc0d HUE-1918 [core] Login page should accept longer password
* 187e8ba HUE-1978 [beeswax] Cancel whole multi query execution
* bac49ac [core] Updating documentation
* 739dff7 [pig] Logs can be missing with Yarn
* ecb4383 HUE-2007 [pig] The script is blank when loading from the dashboard section
* 4afdbda [hbase] Change initialization to allow for callbacks from clusters
* 579543d HUE-1624 [hbase] Configurable write permissions
* ecfcb4c [core] Pluggable auditing logger
* a84eff5 HUE-2005 [core] "Did you know?" box blocks form on login page
* d88cb9f [core] Fix doc model syncing missing some empty objects
* 9585086 [core] Hide the navigation bar on the login page
* 97f80a4 [pig] Support HCatalog transparently
* fb0a60a HUE-2006 [hbase] UX bug fixes for HBase 0.98
* ae9bb02 HUE-1985 [beeswax] Better save query to a file UX
* 50c99be HUE-1995 [hbase] Column familly filtering is broken
* 7bd57f0 [metastore] tests should be aware of database fallback to 'default'
* 4a94165 HUE-2002 [search] Do not break the editor when bad field value or name
* df7ee86 [beeswax] Install Hive and Impala sample on a non local host
* 4c2d8e1 [hbase] Use absolute root path for pointing to the example data
* 4db11f2 HUE-1973 [core] django-openid-auth mysql issue
* cd5295d [metastore] Ensure database exists before creating a table
* 42812d9 HUE-1999 [beeswax] Update multi query separation algorithm
* f9f1b93 HUE-1998 [search] Improve demo collection message display
* f85ee14 HUE-1997 [core] Long dropdown menu items go outside the menu area
* 0c825d6 HUE-1991 [search] Add more sample data
* 53abe91 [jobbrowser] Job counter error with Yarn
* 9a36249 [core] First pass of l10n for 3.5
* 1470f93 [core] switch to checking for is_first_login_ever existance
* 9674519 HUE-1860 [core] sync ldap group memberships upon login
* 444d498 HUE-1930 [core] Alert users with older browsers to upgrade instead of showing a blank page
* 1581777b2 HUE-1930 [core] Alert users with older browsers to upgrade instead of showing a blank page
* d3cde24 HUE-1996 [core] Prevent ajax caching on IE
* bb66143 HUE-1993 [hbase] Add examples for HBase App
* d94bebe HUE-1994 [impala] Autocomplete UDF arguments with table columns
* 8d34bef HUE-1829 [beeswax] Add back MapReduce job list
* a379a37 [core] Fix tests for RemoteDjangoUserBackend
* 0e09ed5 [beeswax] Better multi query separation support
* 7ce0ef2 [core] Make about page available to anonymous user
* 86b2300 [impala] Faster check status until 2s of execution
* 14ebbae [search] Integrating icons for demo collections
* b833aca [search] Adding sample icons
* 05097ee HUE-1811 [search] Add script for creating the Solr collections
* 251ea05 HUE-1811 [search] Install examples button in quick start wizard
* 38da4f3 HUE-1811 [search] Alert message when using a demo collection without a valid Solr
* 448cbcc HUE-1811 [search] Sample collections
* 5c09057 HUE-1992 [core] set username to lowercase when using RemoteUserDjangoBackend
* a1aa5c1 [impala] Fix backward compatibility with no start_over support
* 312e56d [impala] Improve result fetching status
* b5e8cad HUE-1983 [beeswax] Download result as CSV is timeouting
* 39f6a58 [core] Hide some ini properties
* 4271a33 HUE-1990 [impala] Should not be able to download results for explain queries
* 70cd8b2 HUE-1904 [core] Friendlier login page
* a4cba30 HUE-1986 [search] Facets including multibyte chars doesn't work
* a29baab HUE-1984 [hbase] url encode requests
* a4c373b [core] add ssl_cipher_list to hue.ini
* af75a60 HUE-1982 [impala] Column scrolling does not support aliases that are similar to the original column name
* e76e95c HUE-1975 [search] Add the dynamic fields from the Solr API
* a622530 HUE-1981 [impala] Smoothen tab jumping
* 0caa68f HUE-1979 [impala] Error alert duplicates the result header
* fec34ae HUE-1977 [beeswax] Support alias autocomplete in multi queries
* bc7533e HUE-1981 [impala] Smoothen tab jumping
* 2ebc313 HUE-1933 [beeswax] Do not fetch query handle for bad queries
* adcebbc [impala] Export query result
* a1093b8 HUE-1947 [beeswax] History tab integration
* f691b82 HUE-1341 [search] Support for dynamic fields
* a0f1045 HUE-1949 [impala] Friendler query expiration message
* c4d4125 HUE-1933 [impala] Export query result
* fd73459 HUE-1933 [impala] Fixing the SQL and hiding mapreduce button
* 8746f4b HUE-1970 [impala] COMPUTE STATS table_name
* 299baf3 HUE-1972 [impala] Update built in function autocomplete
* 2913fd2 HUE-1971 [beeswax] ANALYZE TABLE command autocompletion
* 0a02a89 HUE-1964 [jb] Hide see expired job checkbox
* bb813ff HUE-1734 [oozie] Re-run workflow popup is HTML escaped
* 00b1453 HUE-1963 [sqoop] minor bug fixes
* b1e6aad HUE-1969 [beeswax] Beeswax polishing
* f970f38 HUE-1882 [core] Adding some missing file for OAuth support
* 299c390 HUE-1968 [pig] Resubmission of a failed script seems to hang
* 96a085b HUE-1958 [pig] Do not take $ sign as a parameter in regexps
* 07d74af HUE-1966 [core] Integrate a font file with filetype icons
* 6750aa0 HUE-1956 [beeswax] A long column name on the navigator doesn't show the sample table
* 2e4cef3 HUE-1960 [jb] Cannot access container logs because of encoded url
* 5300fba HUE-1231 [oozie] Support global configuration when importing
* ee025b6 [beeswax] Close command should close the queries older than N
* c4ec766 HUE-1948 [beeswax] Autocomplete support for multi queries
* 30dd3c4 [core] Fix dump_config tests by testing an app setting instead of desktop
* 5d971f8 [impala] Hive metastore app links if no permission to access it
* 310eef4 [core] Manage apps to load from hue.ini
* 323313e HUE-1955 [beeswax] Save a query with resource fails
* c6ac0c0 HUE-1556 [core] Create the users home directory automatically at login
* 051e117 HUE-1858 [oozie] "Could not save workflow" error message requires substantially more information
* 2e89fd8 HUE-1950 [beeswax] Saving a query name or sql does not seem to update it with IE
* 26440a3 HUE-1951 [beeswax] Add row numbers
* e59bc5c HUE-1954 [beeswax] The result table header doesn't move on scroll or resize
* 964647e HUE-1952 [core] Tutorial panel should be easier to dismiss
* 66edb0d HUE-1932 [hbase] Better error message when HBase Thrift server is not there
* ee29798 [beeswax] Explain query is empty
* e4757b6 [zookeeper] Readonly for non superuser
* af4b0f9 [impala] Support Data sample even without metastore app permissions
* 678faf6 HUE-1889 [beeswax] Slickier editor layout
* 37fb5a2 HUE-1943 [oozie] Convert to descision node can lose all the nodes
* a67aee3 HUE-1686 [beeswax] Fix export result to HDFS test cases
* 2b9f3de HUE-1946 [beeswax] Can't select and execute more than one query
* e82e642 [impala] Downloading a result not cached anymore should fail more gracefully
* 1a89213 [impala] Specific query configuration can be overriden
* ab21e5b [impala] Some URL refer to neeswax instead of impala
* 7cd2b53 HUE-1889 [beeswax] Slickier editor layout
* 6481060 HUE-1889 [beeswax] Slickier editor layout
* 900f902 HUE-1686 [beeswax] Saving results should not re-execute the query
* a93da78 HUE-1907 [impala] Date result fields are not jsonifiable
* bbeeb68 HUE-1944 [oozie] Generic action is broken
* c53e420 HUE-1945 [core] Navigation bar is cut on some resolutions
* 747add1 HUE-1939 [beeswax] CTAS redirects to the default database in the metastore
* 98dfa50 [beeswax] Allow saving results to fully-qualified name database
* 8dfe698 HUE-1889 [beeswax] Slickier editor UX
* 4b5c9af [beeswax] Fix HTML escaping of result table
* 7aa96e7 HUE-1708 [search] Allow search results to be exported
* e9d7e47 [beeswax] Prevent recursive looping in tests
* 59c54f9 HUE-1324 [fb] Support upload of tar.gz archive
* f984008 HUE-1926 [beeswax] Cached query should not be replaced by a saved one
* e5c5e60 HUE-1937 [beeswax] Clarify behavior of a multi query with error
* 5a98108 [core] logging should be timezone aware for all systems
* 4af49f7 HUE-1934 [beeswax] Flag for automatic closing the queries
* fadfcd7 HUE-1784 [oozie] False positive variable when submit from HDFS
* 1a2de1b HUE-207 [core] upgrade tablib to development version
* fbafcd2 HUE-1927 [beeswax] Loading a query history of a saved query does not load its name
* 6bee6a9 HUE-1826 [impala] Download or export query result
* 45a17ea HUE-207 [beeswax] Leverage tablib to enable more flexible data export from Beeswax
* 80ecf51 HUE-1913 [impala] invalidate metadata breaks the editor
* 5d377ac HUE-1928 [beeswax] HiveServer2 supports pass-through LDAP authentication
* 83c3c18 [about] Page becomes blank when check config finishes
* 5b15f0f HUE-1898 [oozie] SLA graph easier to understand or manipulate
* ff44e5f HUE-1906 [beeswax] Better UX for the goto columns on the result page
* fbf25a6 HUE-1929 [core] Create jHueDelayedInput plugin
* a8c3309 HUE-1925 [oozie] Disable drag action when around the edit button
* 0ae3db3 HUE-1893 [beeswax] predictGraph() should use the metadata from the result set
* c814197 HUE-1891 [hbase] Cell edit icons are not aligned
* 40501d0 HUE-1877 [beeswax] Smarter scroll to top button
* 307815a [beeswax] Update tests to the latest HiveServer2
* 2bd7c94 HUE-1920 [impala] Hide database is locked message
* 678a2ec HUE-1923 [core] Support User filters to help limit the Users that are able to login to Hue
* 52fc692 [core] Adding missing makefile in liboauth
* d13656a HUE-1901 [oozie] Add a test for import subworkflow
* c420eab HUE-1882 [core] OAuth support for Facebook, Twitter, Google+ and Linkedin
* 7dd9a0c HUE-1911 [core] banner_top_html is escaped
* 5f1233a HUE-1921 [core] Fix IE9 glitches
* 73c8f27 [core] Do not show help app if it is not allowed
* 190c6d0 [search] Search page 500 when highlighting is null
* d5f14b0 [beeswax] Fix full screen
* 1c79799 HUE-1919 [beewsax] Do not jump to result tab
* 8c4a8ca HUE-1658 [oozie] Adding backward compatibility flag
* 2b852ec HUE-1658 [oozie] Shifting Sunday to first week day
* 140dc40 HUE-1658 [oozie] Cron like scheduling
* 660b16c [hbase] Invalidate cached cluster configs
* 277c5c7 HUE-1908 [beeswax] Database of a saved query is not loaded back when opening it
* 2f74427 [core] Improve logging timezone information
* 9173a45 HUE-1915 [core] MultipleObjectsReturned for tags or permissions
* 8313e81 [beeswax] force scroller to work
* bd786d5 HUE-1909 [impala] No errors are displayed
* bc65a47 [core] Ignore all the mo files except the ones from third parties in ext-py
* 7e3431a HUE-218 [beeswax] Add mechanism to kill a Hive query
* 8e441d8 HUE-1905 [core] Add security handling for yarn and mr2
* 0d496eb [core] fix result monitoring
* a6bcdfa HUE-1857 [oozie] Allow import workflows with subworkflow identified at runtime
* 03b05eb HUE-1902 [oozie] Update coordinator dataset action is broken
* ce0c982 [i18n] Removing mo files from the repository
* 2617a08 [core] Set en locale not fuzzy
* 224c048 HUE-1857 [oozie] Allow import workflows with subworkflow identified at runtime
* 7993f4d [beeswax] Only close queries that are not running
* e03ea6a [oozie] Credentials can be combined comma separatedly in one action
* 8cb022e [beeswax] Fix execute query button for temporary queries
* bd76ca1 HUE-1887 [oozie] Support dashboard Coordinator and Workflow action SLA
* 5d52c3a [i18n] Removing mo file
* 81b4c6e HUE-1723 [beeswax] Example SQL text should not be executable
* fb640aa HUE-1894 [beeswax] Some errors are not reseted at query execution
* 8e81051 HUE-1892 [oozie] Permission denied for hive-site.xml for Hive action on workflow
* f9351fe HUE-1896 [beeswax] Query logs are queing up
* 8cc2884 [beeswax] Send watch status when no error
* 1b8b5ee HUE-1883 [beeswax] Query with expired result will break the editor
* a82765c [spark] Locales fail to compile because of some missing placeholders
* 54233be [core] Print log time to the same timezone set in hue.ini
* 7fff51a HUE-1885 [useradmin] Sanitize user list
* 100e22a [core] Doc model API and desktop permissions cleanup
* 6648026 [core] Remove old shell logging
* 2a8f854 [pig] Use correct autocomplete view
* 0fb48e5 HUE-1879 [oozie] Edit a java action twice is broken
* f24d18b HUE-1881 [impala] Close query on unload page
* 6da8e0f HUE-1880 [beeswax] Multi query result opened shows twice the data
* 0b7150a [impala] Close the correct query history id
* 9df9961 HUE-1876 [beeswax] Can't save result into an HDFS directory
* 60d165e HUE-1776 [metastore] Support extended Unicode delimiter
* ab09a82 HUE-1302 [oozie] Optimize dashboards API calls for a single coordinator
* 1cd4b2d HUE-1875 [beeswax] Friendler UX when missing query property
* 4c230b0 HUE-1852 [oozie] Encoding issue in job description included in workflows
* 48fe935 HUE-1871 [beeswax] Auto queries should not modify the query cookied
* 8b847ec HUE-1878 [rdbms] Query with error break the editor
* 968d58c HUE-1873 [beeswax] Result data not HTML encoded
* 2b3f8c5 [desktop] Polish permissions based on URL
* c5ec0a2 [beeswax] File browse button missing from saved design file resources
* 75a9a98 [beeswax] Convert a series of test to the new json and refresh API
* c66c9d4 HUE-1872 [oozie] convert to decision node broken
* a946620 [beeswax] Execute saved design doesn't show name in history
* b290cc8 [beeswax] Save results to a table redirects incorrectly
* ee64583 HUE-1869 [dbquery] Query with error should not move headers
* f19016d HUE-1863 [dbquery] Explain query doesn't work correctly
* 49b6238 HUE-1864 [beeswax] download CSV doesn't work if design was never saved
* 6b4ccbf HUE-1848 [metastore] Watch query page with the new API
* dd6ed74 [search] Show other collection caret only if more than one collection
* 094205e HUE-1838 [oozie] Add SLA tab on single workflow and coordinator dashboard page
* 35d2c3a HUE-1866 [beeswax] Default graph preset on result page
* 6d0d7a9 HUE-1862 [impala] Impala only permission requires Beeswax
* 045a046 HUE-1861 [oozie] Forks can't be created anymore in a workflow
* 95d9066 HUE-1837 [oozie] SLA dashboard it is not pretty
* ff15888 HUE-1841 [core] Add support for OpenId authentication
* 594c3a3 [beeswax] Fix explain query
* 17c93d5 HUE-1844 [beeswax] Load back from History page
* 1826833 HUE-1855 [beeswax] Error reporting is incomplete
* e351f0f [search] Add query autocomplete
* 6da9621 HUE-1856 [beeswax] Multi and single query execution UX
* b5fa62a HUE-1859 [core] Add generic middleware support
* 27d69fe [beeswax] Replace power UDF by tofloat in the tests
* 714f83e [oozie] Always provide JT and FS addresses
* b2f7d6d HUE-1839 [oozie] SLA form is not pretty on edit workflow action popup
* 2a6c670 HUE-1817 [beeswax] Disable execute button of parameterized query when blank field
* c6c2426 HUE-1843 [beeswax] Multi query support
* 0db17d4 HUE-1768 [oozie] Apply the new minimal style of the graph to the editor
* 320c88e [sqoop] Show error message when a starting job fails
* 63558b1 HUE-1842 [beeswax] Error info above query box instead of the popup
* c83d579 [beeswax] Save the query name in the tests
* a24bfbd [doc] Cleanup how to run the tests
* 3da5445 HUE-1830 [beeswax] Infinite scroll is broken
* df1b70d [oozie] Shared coordinators can not be run by non ower users
* c5e2440 [oozie] Fix Coordinator SLA edition
* 0c6b56f HUE-1845 [impala] Automatic query closing
* 20e1ecc [jobsub] Limit number of designs
* 2498d03 HUE-1817 [beeswax] Migrate several tests to the new API
* 17cb57b HUE-1574 [beeswax] ASCII error on query page
* 5dc2eed HUE-1753 [beeswax] Setting and files inputs in the editor are not user friendly
* 6730c7f HUE-1847 [metastore] Dropping loads of dbs or tables makes the script to timeout
* b6ad0cc HUE-1820 [jb] Finishing jobs are red and stuck
* 1741851 HUE-1817 [beeswax] Add testing helper for the new API
* 66f767b HUE-1840 [beeswax] Query with no result set error the editor
* 18e75e1 HUE-1836 [oozie] Cloning a new action fails
* 0787bf2 HUE-1828 [beeswax] Add back download and save results
* 99eb7b70c [doc] Adding logos on github main page
* eb61cbb HUE-1835 [metastore] Improve database dropdown
* 8827c6a HUE-1827 [beeswax] Automatic log scrolling is broken
* 2d53ca4 HUE-1799 [beeswax] GetOperationStatus() now returns operational states
* 49058c6 HUE-1832 [beeswax] Save query does not update url
* 7ee1725 HUE-1821 [beeswax] Re-integrate graphs
* ef4908b HUE-1548 [sqoop2] Connection management refactored
* 452bab5 [doc] Add Spark app to the list of apps
* 95a0e14 HUE-1452 [oozie] Credentials by action for Oozie workflows
* 343481f HUE-1803 [oozie] Support global configuration
* eb47ec3 HUE-1803 [oozie] Global configuration mapping
* 23d63af [oozie] Front end for SLA
* 1db86d3 HUE-1803 [oozie] Support global configuration
* 6f672a2 HUE-1656 [oozie] Make data fully integrated in the API part 2
* b3d1abc [oozie] Front end for SLA
* 71d3631 HUE-1656 [oozie] Make data fully integrated in the API part 1
* bb0b460 HUE-1657 [oozie] Basic SLA parsing for workflows
* fc728ca HUE-1656 [oozie] Adding parameters to SLA
* dd09000 HUE-1656 [oozie] Add 2 new SLA fields
* edf3af6 HUE-1656 [oozie] Create Coordinator SLA
* 6e99fe4 HUE-1656 [oozie] Create empty SLA on new nodes
* b238f59 HUE-1657 [oozie] Dynamic SLA search page
* e3bc37b HUE-1656 [oozie] SLA edition by Workflow action
* b1de2fa HUE-1657 [oozie] SLA search page
* f72bb4a HUE-1656 [oozie] SLA edition
* ac64189 HUE-1657 [oozie] SLA search/lookup
* ab1f09e HUE-1822 [beeswax] Re-integrate columns in result tab
* 24cf3bf HUE-1833 [spark] Gracefully fail when the server is not up
* 645b872 HUE-1825 [beeswax] Re-add filebrowser to file resources
* 1c50cab HUE-1823 [beeswax] Re-integrate resource lists in the editor
* 0e1a003 [beeswax] Fix explain query test API and test_explain_query_i18n test
* a7e4781 HUE-1831 [beeswax] Switch view sample and open table in navigator
* 34fc418 HUE-1798 [impala] Improve database dropdown
* 6e87954 HUE-1790 [dbquery] Explicit db restriction property
* 2e5e8b7 [core] Provide ini parameter for browser-length cookies
* 7d84893 HUE-1812 [spark] UX improvements
* d076823 HUE-1812 [spark] Make it awesomer
* 3fceec4 HUE-1818 [core] Remove required markup for jHueHdfsAutocomplete
* 3df42de HUE-1817 [beeswax] Add watch_wait template to have at least the tests running
* 06bac19 HUE-1813 [sqoop] autocomplete output directory
* dc9841d HUE-1809 [sqoop] autocomplete jdbc class and string
* 282d218 HUE-1810 [sqoop] autocomplete tables and fields
* 5551575 HUE-1808 [dbquery] Pull out rdbms config to librdbms app
* 9393b02 HUE-1806 [beeswax] One query page editor UX cleanup
* 357b1a1 [spark] Add submitted jobId in url hash
* 73fc860 [docs] Fixed code style
* 857e483 HUE-1800 [fb] Autocomplete edited path
* 43f04d8 [spark] Add check config
* 2ac1772 [spark] Support plain result
* b9eeb26 [spark] Add download result data
* 23a83b1 [spark] Dynamic parameter list
* bf982df [spark] Save script in the editor
* be12dcc [spark] Save and load a script
* 718c3bb [spark] Add link on jobs page to open them with their result
* 632716a HUE-1219 [impala] One page app
* fd376b3 [core] Add switch for collection in the admin wizard
* 1a4262b HUE-1800 [fb] Autocomplete edited path
* 244f310 [spark] Adding locales
* 07f87d8 HUE-1805 [spark] Second version with REST Job Server
* d3f66b4 HUE-1792 [search] Error when combining a field and grahpical facets
* bb77b4b HUE-1783 [beeswax] Result graphing
* e947a69 HUE-1795 [core] Update window title on every page with a progress bar
* d1b62c8 HUE-1796 [dbquery] Interactive feedback when sumitting queries
* d6c0f35 [impala] Fix change of Editor name
* d2f147d HUE-1348 [search] Improve collection dropdown
* 9cb6857 HUE-1793 [hbase] Api Error: 'NoneType' object has no attribute 'group'
* f58c0e2 [core] Rename Beeswax to Hive Editor
* 89e92a6 [beeswax] Remove dbquery app dependency
* 4f5db8f HUE-1789 [fb] The dropdown icon on Chown/chmod is not aligned
* 41bad76 HUE-1706 [beeswax] Sort numerical columns numerically not lexicographically
* 6128c3b [beeswax] Fix query result medatadata type
* 59eca94 HUE-1788 [hbase] Cannot upload image to cell
* dbbe283 HUE-1779 [core] Correct offset of notifications on close
* ac5bd4f HUE-1786 [hbase] Upload button in a cell broken
* d8d8273 HUE-1787 [sqoop2] python 2.4 json encoding issues
* 773c595 HUE-1722 [impala] Scrolling below initial 100 records shows NULLs as blank values
* 88ae146 [proxy] Proxy app doesn't work if blacklist is empty
* 420006c HUE-1785 [oozie] New graph CSS messes up menu labels
* 6a1e98b [fb] Fix error when editing new file
* d797404 HUE-1736 [fb] Editor windown is not high enough
* e129263 [oozie] Upload test sharelib with the Oozie command
* 96976bb [core] Fix description of LDAP force_username_lowercase in ini


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

