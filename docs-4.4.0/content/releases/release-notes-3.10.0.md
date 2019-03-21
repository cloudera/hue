---
title: "3.10.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -3100
tags: ['skipIndexing']
---

### Hue v3.10.0, released May 11th 2016


Hue, http://gethue.com, is an open source Web UI for easily doing Big Data analysis with Hadoop.

Its main features:

   * SQL editors for Hive, Impala, MySQL, Oracle, PostGresl, SparkSQL, Solr SQL, Phoenix...
   * Dynamic Search dashboards with Solr
   * Spark and Hadoop notebooks
   * Scheduling of jobs and workflows through an Oozie Editor and Dashboard

More user and developer documentation is available at http://gethue.com.


Latest Notable Features
-----------------------

The complete list and video demos are on [Hue 3.10 with its new SQL Editor is out!
](http://gethue.com/hue-3-10-with-its-new-sql-editor-is-out/).


SQL Editor

* Full revamped
* Support of any type of SQL
* Query: Multi queries, Search and Replace, live history, fold, format, table assist
* Results: Fixed headers, scroll to columns, charting, download in Excel/CSV
* Autocomplete of nested types
* Saved default Configurations

SQL Browser

* Revamped UI for speed, statistics display and ease of use
* Single page app
* Optimized for large number of databases and tables

Home

* Folder and directories
* Share document for collaboration
* Export and import documents

Search

* Hue supports Solr Suggesters and makes your data easier to search! Suggester assists the user by proposing an auto-completable list of queries:
* Result in the Grid Widget can be plotted like in the SQL editor. This is ideal for clicking visualizing the rows returned by the search query.

Security

* Solr Sentry privilege edition
* A timeout now logs out inactive user after idle_session_timeout seconds
* Optional custom security splash screen at log-in with login_splash_html
* TLS certificate chain support for HUE
* SAML Password for the key_file was introduced with key_file_password
* Customize your xmlsec1 binary by changing xmlsec_binary
* Customize your SAML username mapping. It also supports syncing groups on login

Oozie

* External Workflow Graph: This feature enables us to see the graph for workflows submitted form File-browser as well as the ones submitted from CLI.
* Dryrun Oozie job: The dryrun option tests running a workflow/coordinator/bundle job with given properties and does not create the job.
* Timezone improvements: All the times on the dashboard are now defaulted to browser timezone and submitting a coordinator/bundle no longer need UTC times.
* Emailing automatically on failure: Each kill node now embeds an optional email action. Edit a kill node to insert a custom message if case it gets called.


Compatibility
-------------

Runs on CentOS versions 5 to 6, Red Hat Enterprise Linux (RHEL 5 and 6), and Ubuntu 10.04, 12.04 and 14.04.

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
* Internet Explorer

Hue might work with Chrome 23, Firefox 23, IE8, Safari 6, or older browser version, but you might not be able to use all of the features.


Runs with Python 2.6.5+

Note: CentOS 5 and RHEL 5 requires EPEL python 2.6 package.


List of 2378 Commits
--------------------

* 94b494a HUE-3858 [editor] Js error on very first opening of the editor
* 4aee5e7 HUE-3803 [hive] Support unicode in queries
* 528d38a HUE-3852 [core] Configuration API returns duplicate group entries when saving one configuration set with multiple groups
* 6f31373 HUE-3861 [core] Upgrade Django Axes to 1.5
* 4874322 HUE-3855 [search] Slightly reorganize the icons by group
* 3dac1a2 HUE-3861 [core] Upgrade Django Axes to include fix for AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP (#368)
* ad0b9ba HUE-3802 [oozie] Fix HS2 action on SSL enabled cluster
* 2ab8a93 HUE-3847 [core] Fix unhashable type error in oozie test
* 4b47d4d HUE-3834 [editor] Configuration type HDFS path list throws js error
* 56af275 HUE-3823 [editor] Deleting a query from the list of query page says "notebook"
* 24d0651 HUE-3835 [editor] Implement the boolean config type
* 9c1b722 HUE-3851 [core] Support many-to-many for group configurations
* 2c2c874 HUE-3850 [core] App configuration page fails to load with JS error
* 44ee60a HUE-3843 [editor] Log panel does not auto scroll to the bottom when new logs arrive
* 5a237ac HUE-3820 [editor] Click on a result row to highlight sticks on first row id cell
* f584cd5 HUE-3772 [editor] Browsing running queries might double the results
* c8aea57 HUE-3707 [editor] Enabled search for the saved queries too
* a9d30da HUE-3847 [core] Fix oozie test to work with updated config API
* ffe39ab HUE-3847 [core] Update query logic for filtering groups
* b9cffb8 HUE-3821 [pig] Logs are never returned on running script
* 6efc737 HUE-3847 [core] Enable multi-group selection for saved group configurations
* 9aabcbe HUE-3846 [sentry] Send * instead of ALL until Solr Sentry supports it
* b7b9d1d HUE-3844 [sentry] Solr config privilege action should be ALL not QUERY
* 0d64b08 HUE-3762 [editor] Improve logic showing if it is a query history query
* a2112a0 HUE-3814 [editor] Disable history / saved query links if we are already on the same queries
* 0b45a14 HUE-3841 [editor] Reset the progress status of a saved query
* 426a8b8 HUE-3840 [jb] Add debug info in possible 500 when pulling job conf from YARN
* c1e54ae HUE-3839 [sentry] Enabled Solr privilege section
* c04fe12 HUE-3805 [oozie] Add support for oozie schema 0.4 in dashboard graph for external workflows
* 473196c HUE-3232 [Infra] run jasmine tests on build
* 8e25f49 HUE-3808 [core] Do not trigger any call on initialization
* 6515358 HUE-3824 [editor] D&d table for a select adds an extra space before the statement
* 24b4da1 HUE-3832 [assist] Dragging a column shows the table context menu on editor drop
* dcda860 HUE-3826 [assist] Expanding column click can be flaky
* a85c77a HUE-3819 [fb] Make the upload and create icons not disappear under 1180px
* 3aa5772 HUE-3810 [editor] Clicking on name of graph legend could check its box
* c068d18 HUE-3827 [libsentry] Workaround Hive for THRIFT-3388 hash doesn't work on set/list
* 2a352a9 HUE-3801 [editor] Move user perms to get document API
* da2ef3e HUE-3663 [editor] RDBMS types should return serializable format for result data
* a50c369 HUE-3808 [core] Offer to live turn on/off debug level
* 905a48c HUE-3801 [editor] Do not offer save button to query shared as read only
* 7346e2f HUE-3776 [core] Install jobs and pig examples under examples directory
* 7f9be09 HUE-3763 [editor] Change test to work with the new history statement
* c540f42 HUE-2962 [core] Adjust to updated API
* f1d0537 [core] Add defaultValue to properties
* 075e8c8 HUE-2962 [core] Implement saving of default and group configurations
* d47dcf6 HUE-2962 [core] Add templates for listing and editing configuration
* fa5406b HUE-2962 [core] List the app configurations under user management
* 9140f67 HUE-3770 [home] Add empty trash action on trash right-click
* c776678 HUE-3774 [home] Expect the search field to gain focus when clicking on search
* 22fabd2 HUE-3777 [home] Do not present search term as a breadcrumb
* 01288c4 HUE-3778 [home] Upload and download icons should be on the same line
* a573326 HUE-3781 [home] Drag and drop a document into the assist database list gives a maximum call stack JS error
* 4ff3ec1 HUE-3818 [home] IE 10 breaks the document entries into two lines
* e94b7ea HUE-3787 [editor] Switch to shift+click only to open table in metastore and expand * for increased linux support
* d1b254b HUE-3804 [beeswax] Drop dependency on notebook.ko.js
* 6907d67 HUE-3789 [editor] No cross icon to exit full screen mode
* 81043be HUE-3798 [core] Re-login from auto-login popup should refresh the page if login as another user
* 294858f HUE-3775 [search] Twitter example has js errors
* 499eee1 HUE-3794 [editor] Click on a result row to highlight
* 91328eb HUE-3790 [editor] Disable format query when query is too big
* 99078ce HUE-3801 [editor] Move user perms to get document API
* cf85ac2 HUE-3763 [editor] Show only the statement which gets executed
* fce7753 HUE-3815 [editor] Protect against failed calls when updating history status
* c253882 HUE-3760 [editor] Canceling a query and doing an explain doesn’t hide the progress bar
* 5797460 HUE-3812 [editor] Do not save the result data
* 6cf3a6b HUE-3809 [editor] Do not send the full query history when executing a query
* cd6a73b HUE-3807 [tools] Remove asciidoc.asciidoc doc file that might be flagged as GPL
* 89ce94d HUE-3792 [editor] Schedule error when clicking on disabled button
* efae667 HUE-3695 [editor] Last multi query highlighting is always missing last char
* 46527e4 HUE-3779 [core] Exporting read only workflows generates empty hue-documents.json
* c873186 HUE-3784 [editor] Query list page does not list shared queries, only owned ones
* 7ffdca0 HUE-3800 [jb] Job attempt logs not appearing for some Oozie jobs
* 065f3e5 HUE-3785 [core] Add sample user to default group to enable sharing perms
* aed5be1 HUE-3197 [oozie] Decision node support in external Workflow graph
* 00e11d8 HUE-3688 [oozie] Fix TestEditor.test_workflow_dependencies unit test
* 3e29155 HUE-3757 [oozie] Better error messages when deleting read only document in editor
* 09bff0c HUE-3758 [editor] Take scroll position into account when positioning context-menu
* 76ff394 HUE-3759 [home] Unselect them all when clicking somewhere else on the page
* f19a358 HUE-3771 [home] Hide the assist panel temporarily for 3.10
* c0ce5b9 HUE-3755 [assist] Hide the source level when there is only one
* 7d41cfd HUE-3773 [editor] The graph of a reloaded query doesn't render the first time
* dfafd69 HUE-3761 [editor] Showing the logs should trigger refresh for table headers
* d14e230 HUE-3767 [editor] The global settings demi modal has a too dark shadow
* f91223f HUE-3754 [editor] Query history seems to lose whitespace in query statement with new lines
* ac022bf HUE-2325 [core] Refactor config API and update README and tests
* 2ea383e HUE-3750 [search] Samples do not show up in the sample folder
* c0d6736 HUE-3700 [core] Support force_username_lowercase and ignore_username_case for all Auth backends
* 58c0f45 HUE-3751 [metastore] Confusion when table name and database name are the same
* 2aef38f HUE-3707 [editor] Add filter search for the query history
* 1cff7c0 HUE-3741 [metastore] Display field validation errors on create table wizard
* 177d780 HUE-3733 [editor] Scrolling on the saved query tab scroll on the result tab
* 6fa23fc HUE-3734 [fb] Scrolling to the newly uploaded file
* dba54bc HUE-3747 [doc2] Install Spark Notebook example to examples directory
* 17d5181 HUE-3743 [editor] Support &new=true to have a blank query
* 7bc2d84 HUE-3728 [editor] Create new query without a page refresh
* 475c4d3 HUE-3660 [spark] Spark default properties are not all valid
* ad1400b HUE-3749 [editor] Let the user pick which session properties to configure
* 395c789 HUE-2962 [editor] Extract ko templates and components for configuration into separate mako
* 4db69d9 HUE-3737 [metastore] All beeswax queries executed via metastore fails to redirect due to JS error
* 596acfa HUE-3746 [metastore] Add browse link in the sample page if there is some data
* 178a2e0 HUE-3741 [metastore] Display field validation errors on create table wizard
* 3f5f0ad HUE-3736 [core] Fix flaky jasmine tests
* 9ef4c52 HUE-3632 [editor] Create button on query list page is notebook only
* c3f2fc7 HUE-3215 [editor] Live update also queries with available results
* a26eec5 HUE-3723 [editor] Use larger input for notebook name and description
* aba17c3 HUE-3724 [editor] The spinner for starting a new session should be really blue
* 96dd3a5 HUE-3684 [home] New directory popup text box has scroll bars
* 9ffd112 HUE-3732 [editor] Icons are misaligned in the snippet menu
* 6cc8b7d HUE-3731 [editor] Send database on Impala refresh with invalidate
* 3828ef3 HUE-3215 [editor] Add live moment for query history and hook up update status check
* c3aef09 HUE-3726 [editor] On query error we hide the log icon of the snippet
* e0e6645 HUE-3719 [editor] Do not error popup when search app is disabled
* 7489f86 HUE-3725 [jb] 'SparkJob' object has no attribute 'amHostHttpAddress'
* 9da3651 HUE-3697 [hive] Excel download convert decimal types to strings
* 356524c HUE-3422 [editor] Rename parentUuid to parentSavedQueryUuid
* 71acfe2 HUE-3422 [editor] Polishing the display of the workflows of a Hive query
* fcfd2c0 HUE-3719 [editor] Editor should fail gracefully if search is disabled/blacklisted
* 497df2c HUE-3720 [security] Allow to browse Solr observable hierarchies
* c11b4fc HUE-3714 [editor] Canceling a query can print a none error
* 4c52740 HUE-3717 [editor] Move row link of saved queries to the full row instead of just the name
* 5af7945 HUE-3715 [editor] statements_count of query history not always consistent
* b992b0e HUE-3215 [editor] Add a call to check the status of the queries in the history
* 36cc7b6 HUE-3713 [editor] Open parent saved query without reloading the page
* 8a3bec2 HUE-3703 [editor] Cleaner way to not reload the history on each query opening
* 074c8d6 HUE-3709 [editor] Close the previous query correctly if needed
* be49616 HUE-3709 [editor] Close queries and not the full sessions on page exit
* 491a247 HUE-3690 [editor] Unify loading a saved query
* 2590aed HUE-3689 [oozie] Drag & dropped Hive action should be sorted in reverse
* 4fd2ca4 HUE-3687 [editor] Add dependency on workflow from a Hive document action
* e80f618 HUE-3687 [editor] Add dependency on workflow from editor
* b12a780 HUE-3422 [home] Save documents directly into a directory
* a2b7a0b HUE-3679 [editor] 'unicode' object has no attribute 'is_superuser' when saving a query
* 974ad25 HUE-3710 [notebook] Hide explain icon for non SQL snippets
* 8141cc2 HUE-3712 [home] Fix js error when going back on home
* 85fe154 HUE-3711 [home] Generate the new document link with the current path
* 6b02353 HUE-3722 [core] Add basic jasmine tests for assistHelper and rename to apiHelper
* 5f13846 HUE-3706 [search] Expanding a document should expand the field list too
* 88d8820 HUE-3659 [home] Open folder automatically if there is only one
* 842f852 HUE-3708 [editor] Name and description edit pop-overs are misaligned for long values
* 8f993e6 HUE-3680 [editor] Limit the length of the name to 255 chars
* a0e7700 HUE-3699 [home] Trigger click when dragging a small distance over links
* 247788e HUE-3716 [core] Add gen-py paths to hue.pth
* cc7db05 HUE-3697 [hive] Excel download convert decimal types to strings
* 584fce4 HUE-3704 [core] Force enable notebook permissions
* b96110a HUE-3703 [editor] Loading a saved query should not reload the full history
* caa6e2b HUE-3701 [editor] Query history spinner when loading it the first time
* 55d4b95 HUE-3691 [editor] Saved queries offer a false pagination
* 0e5e48d HUE-3694 [editor] Multi query hightlighting disappears on focus
* 97088c7 HUE-3692 [editor] 'Save as' a query does not update the saved query list
* bc7e1fe HUE-3683 [editor] Hive pie chart graphing js error
* 0f095a7 HUE-3675 [search] Align the marker map icon
* b932158 HUE-3674 [core] Prevent idle of idle session timeout blurring
* 2e7c6f5 HUE-3673 [editor] Elipsis for the name of the query in the Saved History
* 9cfa11d HUE-3640 [editor] Zero result query always closes Query History tab
* be034c8 HUE-3702 [editor] Suppress conf error if Impala is not enabled
* 3599f78 Add csrf_token to Pig app template (#355)
* e13e28a [doc2] Fix test_api_get_data test
* db43f37 HUE-3681 [oozie] Fix submit coordinator in Oozie
* 99d305b HUE-3662 [editor] Upgrade session properties when opening history or saved query
* 0b4829c HUE-3678 [core] Replace illegal Excel characters on download
* 6ef25fd HUE-3625 [editor] Saving a notebook resets its directory to Home
* 0d3ac19 HUE-3672 [doc] Document password script for databases
* 09c7074 HUE-3670 [jb] Summary button does not fail gracefully
* aad59f5 HUE-3668 [sentry] Generify the authorizables
* 54771d9 HUE-3667 [sentry] Support TListSentryPrivilegesByAuthRequest v2
* 0a67b5c HUE-3667 [libsentry] Workaround in API for THRIFT-3388 hash error
* a812c79 HUE-3667 [libsentry] Update thrift API to support SENTRY-993
* a25471e HUE-3655 [oozie] Add ability to configure default config parameters that all Hue(Oozie) jobs contain
* d7d3717 HUE-3671 [editor] Fix Save Parent Directory
* cf9fd23 HUE-3649 [doc2] get_by_uuid should check permissions
* 63dfd2a PR349 [doc] Add sasl-plain dependency for Centos 6.6
* ca2dbd3 HUE-3591 [oozie] Autocomplete list of possible hive queries in the hive doc action
* 7233d3a HUE-3652 [editor] Update Get History test to correctly check for the query type
* fc63bdf HUE-3665 [editor] Don't show top border on query history columns
* fc43dd9 HUE-3654 [editor] Ellipsis for the name of the query in Query History
* 7b44854 HUE-3410 [notebook] Update tests to the use the saved parent id
* 7c627c8 HUE-3263 [assist] Show menu on drop of db entries (select, update, insert, delete etc.)
* c49aaf2 HUE-3657 [editor] DB drop-down has empty space with few DBs
* 6bfe794 HUE-3656 [editor] Clicking explain removes the results tab
* 799e194 HUE-3597 [assist] Allow copying names in assist
* b2fd327 HUE-3510 [notebook] Restyle snippet icon shading and alignment
* 24bfeb1 HUE-3602 [editor] Sample popup column header style conflicts a bit with rows
* d406433 HUE-3410 [editor] Secure persisting the parent saved query
* 43233c1 HUE-3653 [desktop] Return document dependencies and dependents in /desktop/api2/doc/ API
* c062110 HUE-3652 [editor] Add query name to history list
* db33c72 HUE-3410 [editor] Properly persist the parent of an history query
* a9fd93a HUE-3643 [editor] Lighter payload when fetching the history
* 1fffdab HUE-3410 [editor] Track the parent of an history query
* d648d90 HUE-3630 [editor] Display when a query is a query history
* 786dfd3 HUE-3651 [core] Upgrade Moment.js
* 480ddc2 HUE-3644 [editor] Menus from result legend can be hidden
* 7ca5d14 HUE-3650 [beeswax] Notify of caught errors in the watch logs process
* 23985fb HUE-3646 [editor] Fix save results to table and HDFS
* 1b16c12 HUE-3645 [editor] Upgrade session properties when opening saved editor documents
* e08c8b7 HUE-3354 [editor] Fixed save results modal spinner
* a2db5cd HUE-3600 [home] When operating on the home file/folder list, the loading spinner shifts the whole list down
* d069f0b HUE-3601 [assist] Spinner not positioned correctly
* f4b277f HUE-3638 [metastore] Scroll bar disappearing when scrolling
* 6ddc7ce HUE-3642 [home] JS error when opening a folder
* 42ac215 HUE-3641 [home] Actions to create folder etc calls the save configuration endpoint
* 5a8f0df HUE-3605 [home] Align headers and columns
* 9a894f9 HUE-3606 [assist] Disable HDFS and Doc2 until Hue 4
* aacc36e HUE-3637 [sqoop] Avoid decode errors on attribute values
* 638b127 HUE-2962 [spark] Update spark properties to utilize new configuration format
* 8d43f4f HUE-2962 [editor] Fix setting of session-based properties for HS2 types
* 6648b21 HUE-2962 [editor] Support session-based properties with snippet overrides
* 4efe5cb HUE-2962 [editor] Add action to save default settings for the user in the sessions modal
* a93e3b4 HUE-2962 [editor] Support new session properties in the editor
* 45b42bc HUE-2962 [desktop] Add API doc for configuration and fix tests
* 8c88233 HUE-2962 [desktop] Add configuration property definition for HS2
* a195f8e HUE-2962 [desktop] Add initial DefaultConfiguration model, api, tests
* 6511a4a HUE-3618 [doc2] Allow newly imported documents to retain directory structure
* fef888d HUE-3635 [editor] Clear also clears the URL too
* 7de680c HUE-3634 [editor] Reset editor URL when clearing history not on a saved query
* 79a9121 HUE-3633 [editor] Cleanup some properties that should not be serialized
* 40019f8 HUE-3629 [editor] Add executed query to the history
* 7a6e8c5 HUE-3614 [beeswax] Scrolling on assist in old editor also scrolls the editor
* ea9b4a3 HUE-3208 [editor] Add keyboard shortcuts map
* 1b525cb HUE-3622 [home] Enable sorting
* 39a5c5c HUE-3631 [editor] Set the correct database in the drop-down when loading saved queries
* 7419509 HUE-3628 [editor] History highlighter can break the page
* 7b7a724 HUE-3627 [beeswax] Fix test_save_results_to_dir to deal with hive tmp directories
* 4b397ca HUE-3621 [editor] Convert player mode to result only full screen
* 85602e7 HUE-3617 [editor] Fallback to StringIO if cStringIO isn't available
* dd8646f HUE-3612 [editor] Some queries have new lines in history
* aac3124 HUE-3536 [fb] Middle click on breadcrumbs do not open the correct URL
* 66126d7 HUE-3596 [editor] Move results and explain to the tabs
* cc1edfe PR346 [core] Default regex tightened to address open URL redirection
* e03c722 PR-347 [doc] Rewrite gethue.tumblr.com to gethue.com
* 2a2b66a HUE-3619 [editor] Fix HiveHighlightRules js error from query history
* c8decd0 HUE-3441 [zookeeper] Support HA
* 9e6317a HUE-3617 [editor] Fallback to StringIO if cStringIO isn't available
* da74e96 HUE-3545 [editor] Better info message when results have expired
* feeb781 HUE-3564 [editor] Check status can error an empty message
* c5f1143 HUE-3613 [editor] Empty div elements are added when scrolling the DB assist panel
* 7eec788 HUE-3611 [core] Upgrade font awesome
* 5d1c7f4 HUE-3430 [metastore] Navigate by editing table name in the breadcrumbs
* 44372be HUE-3583 [editor] Make split_statements performant for extremely large queries
* cf14b2f HUE-3554 [editor] Prevent history dates of 46 years
* d904ab3 HUE-3593 [editor] Link to the list of notebooks is wrong
* 3b7c18c HUE-3594 [fb] Smarter DOM based XSS filter on hashes
* 7337d8a HUE-3592 [editor] Add a middle title bar to the query lists
* 9b49b25 HUE-3552 [editor] Column list should not show the resize bars in all the cases
* 3416c2a HUE-3515 [stats] Don't show the view more link in stats from metastore
* 0623a77 HUE-3562 [editor] Fetch_result_data can be called more than once
* 12745c6 HUE-3558 [metastore] Disable edit comments when user does not have permissions
* cc1175a HUE-3586 [editor] Better feedback when waiting for the first progress of a query
* 5b4a046 HUE-3584 [editor] Solr SQL does not alway return the column values
* 8eeb883 HUE-3567 [editor] Improved icons and tooltips for query history status
* 1591371 HUE-3580 [sentry] Support non ASCII URI
* cd68e9b HUE-3572 [editor] Map chart is broken
* c406cfd HUE-3582 [editor] Fix typo in Solr connector assist
* 3aebc58 HUE-3581 [editor] Nice scroll goes bananas when dragging from assist to editor
* 81a53af HUE-3546 [editor] Fix wonky header and first col on scroll
* 0923862 HUE-3579 [editor] Pasting a big query should not increase editor size by more than 50% of the page
* 6e498fb HUE-3578 [editor] History syntax highlighting has red dot
* bb898b1 HUE-3576 [editor] Snippet resizer is wonky when error is present
* 08fd395 HUE-3555 [doc2] Exporting directories also exports any children directories and docs
* c581eb1 HUE-3575 [sentry] Force refresh of the Hive tree root too
* 30565e8 HUE-3549 [editor] Conflict when running explain query on a running query
* b7189bf HUE-2890 [doc] Skeleton for new version of user guide
* 6304315 HUE-1389 [oozie] Schedule a hive query automatically
* 481ada8 HUE-1389 [oozie] Add link to open source query
* bdabc38 HUE-1389 [oozie] Fetch Hive queries and display there name and description in workflow
* 7aeac6d HUE-1389 [oozie] Pull list of hive queries
* 7ca1b21 HUE-1389 [oozie] Automatically retrieve Hive query parameters
* f70983a HUE-1389 [oozie] Skeleton to drag & Drop a saved Hive query in a workflow
* 3146fd4 HUE-3543 [hive] Timeout prevents refreshing of the Assist tables/dbs
* fc356fd HUE-3574 [home2] Show readable document types instead of the raw value
* be683b4 HUE-3529 [home2] Remaining documents icons
* cdde08a HUE-3573 [editor] Connect the query builder flag to the UI
* 6ba95fd HUE-3571 [editor] Syntax highlight history
* 9acc052 HUE-3573 [editor] Flag to enable the query builder
* ca94129 HUE-3540 [editor] Prettify the query builder
* 422ffc8 HUE-3539 [editor] Bring back the double click on the assist columns to generate a SELECT statement
* 6e30eb1 HUE-3228 Add filtering on a text facet
* dd5d21e HUE-3228 [editor] Fix js errors in dashboard
* a3ae1a2 Revert "[impala] Remove reference to dashboard on URLs"
* f1080e8 HUE-3570 [editor] Do not error on empty resultset
* 0671c02 HUE-3570 [notebook] Bubble up the exception form Solr SQL
* 26bd101 HUE-3570 [notebook] Specify a default Solr SQL collection handler
* a1de8fd HUE-3570 [notebook] Support Solr sample data
* 42fb6b4 HUE-3570 [notebook] Default Solr collection
* 330a93a HUE-3570 [notebook] Add a limit 100 to /sql call
* 9e51d3f HUE-3570 [notebook] Solr SQL autocomplete
* 1162b24 HUE-3570 [notebook] Skeleton for Solr SQL snippet
* 862a83a HUE-3531 [home] Show shared icon also on shared document
* dbd4642 HUE-3568 [core] Strip HTML from x-editable input values
* 7d2f97a HUE-3556 [home] Harmonize Notebook icon on create Notebook
* dc7abbf HUE-3557 [home] Last modified date doesn’t look like the other dates in general
* 410e480 HUE-3561 [editor] Take scroll top into account when resizing the editor
* 1249169 HUE-3550 [editor] Autocomplete conflicts with certain table names
* 17cdefe HUE-3565 [editor] Hue icon not aligned in Player mode
* 880f195 HUE-3547 [editor] Better user feedback when submitting a query
* fb9c995 HUE-3541 [home] When not logged in the Sign in now button points to /home2
* a5070bd HUE-3551 [core] Remove dashboard from the signin message
* d684e76 HUE-3542 [home] Remove 'Old Home' link
* b1d79cc HUE-3553 [home] Reset the directory name in the create directory modal
* a56862d HUE-3507 [oozie] List workflows displays trashed workflows
* 6c672e4 HUE-3535 [doc] Document about modifying static files in production
* b37fbe0 HUE-3524 [editor] Multi query highlighting seems to hide the query error
* 87df2a6 PR342 [editor] Add simple SQL query builder functionality
* 07539a3 HUE-3538 [core] Standardizing repo ids and upgrading shade plugin
* 4e2bd97 HUE-3530 [home] Add missing document to the create document button
* e718052 HUE-3527 [editor] Display saved results of an expired query loaded from history
* b303a4b HUE-3496 [editor] Query variables are not persisted
* f3b7133 HUE-3502 [editor] Handle correct statement number on multi query error
* 645bf87 HUE-3509 [notebook] Executing a new Hive snippet errors
* 408a17f HUE-3503 [hive] Additional test on partition keys
* b0f28d0 PR343 [rdbms] Big number precision loss
* 03c92f5 HUE-3533 [doc2] Refactor dependencies for importing saved beeswax queries
* 46ad257 HUE-3520 [jb] Use impersonation to access JHS if security is enabled
* 18a114f HUE-3528 [oozie] Call correct metrics api to avoid 500 error
* ddb0328 HUE-3522 [core] Create home directory automatically if needed for SpnegoBackend users
* 8e35712 HUE-3526 [useradmin] Fix LDAP tests for force_username_uppercase
* b85823d HUE-3523 [oozie] Modify find_jobs_with_no_doc method to exclude jobs with no name
* c3203b1 HUE-3521 [core] Provide a force_username_uppercase option
* ce92258 HUE-3445 [doc2] Check parent perms on saving a document and apply as needed
* 8e6583e HUE-3519 [useradmin] Check if user object exists before augmenting in rewrite_user
* c67323f HUE-3488 [oozie] find_dollar_braced_variables skips variables on same line
* 368dace HUE-3518 [editor] Autocomplete for table names is gone
* f12bb20 HUE-3492 [editor] HDFS and table autocomplete in save result popup
* 9962f32 HUE-3251 [home] Use enter to create directory in modal
* 1ef1222 HUE-3259 [metastore] Table stats on table with partitions is always outdated and empty
* c6bebac HUE-3514 [editor] Show actual error message instead of just "OK" in error notification
* b2ddee5 HUE-3513 [assist] Show sample values in column stats popover
* c632160 HUE-3512 [assist] DB Panel doesn't take the source into account when storing the last selected DB
* b8e2dd7 HUE-3511 [assist] Reduce flickering of action icons when moving the pointer across several entries
* a4a6e16 HUE-3495 [editor] Add jasmine tests for Ace textCompleter
* 43f2214 HUE-3333 [editor] Add one more digit to the row number column
* 1f2a048 HUE-3508 [metastore] Fixed overlay conflicts with top menu
* 19d316d HUE-3506 [metastore] Limit length of comments on table page
* 3df51dc HUE-3505 [metastore] Table description now uses an editable textarea
* 0b78281 PR341 [core] Fix a Korean translation
* 69bcd60 HUE-3500 [doc2] Unify dependency relationships representation
* e6166d6 HUE-3501 [docs]: Document new dependency on libffi
* 703129c HUE-3501 [desktop] Upgrade cffi and cryptography deps to fix OS X
* 3057a1c HUE-3499 [editor] Add an expired status in the query history
* 6498c17 HUE-3495 [editor] Autocomplete globs the comments
* 1014e84 HUE-3498 [editor] Do not refresh the assist when loading a query from the history or saved query
* 8b8ec92 HUE-3497 [editor] Auto extend var text input if needed
* c37c9bd HUE-3491 [editor] Style export result button
* 36eabfa PR338 [tools] Introducing docker-compose
* 1005686 PR337 [tools] Missing docker dependency libffi-dev
* 9434c2a HUE-3493 [editor] Load saved queries without reloading the editor
* 8374d15 HUE-3493 [editor] Load queries without refreshing the page
* f7c5529 HUE-3494 [editor] Unify query history workflow
* a1360a8 HUE-3493 [core] Add flag to API to also return the document data
* 8517aee HUE-3493 [editor] Load queries without refreshing the page
* 063bf76 HUE-3489 [editor] Improve result download format stats
* 586c064 HUE-3115 [editor] Multi create table statements makes the assist flickers
* 5a813a4 HUE-3442 [core] Improve memory efficiency of XLS download
* abfab56 HUE-3389 [editor] Provide select from partitions support in get_sample for Impala
* 17dc4a0 HUE-3455 [doc2] Oozie documents are getting a time appended to their name
* 227adea HUE-3474 [editor] uuid of document2 and editor uuid field are mismatching
* 46eea72 HUE-3307 [notebook] Add NiceScroll to the right panel and improve performance of the rendering
* cea697d HUE-3487 [core] Fix Ace Editor import on CssCompletions
* c02a1f4 HUE-3484 [core] Update is_db_alive command to provide finer grain exit codes
* c89b57e HUE-3485 [editor] Prettier query history
* 1b690fd HUE-3486 [fb] Harmonize modal dialogs
* 04c567c HUE-3187 [metastore] Fixed search section
* 5e78e72 HUE-3477 [home] Double backgrounds in right-click context menu
* a3ba75b HUE-3480 [assist] Impala refresh pop-over won't close after assist action while open
* 3f6f974 HUE-3481 [assist] Don't sort the columns by name, instead use the creation order
* 682811e HUE-3442 [core] Increase max num rows for Excel export
* 454ab1e HUE-3483 [search] Recreate test admin user to avoid conflicts
* 31cc155 HUE-3479 [editor] Clear should also clear the result
* ba9fee3 HUE-3400 [core] Only display the 500 server trace when the user is an admin
* c5e673c HUE-3438 [editor] Scrape Spark Application ID during query execution of Hive on Spark
* e2a320f HUE-3476 [assist] Clear any running intervals after closing the stats popover
* cbc76a9 HUE-3249 [home] Icon alignment context menu
* a929a9e HUE-3247 [home] Add titles where needed
* 3c59959 HUE-3340 [oozie] Add Jasmine to Oozie
* 594f63c HUE-3361 [assist] Introduce NiceScroll on the stats popover
* 27a009a HUE-3464 [oozie] Fix test utility that removes a user from a group
* a5f72ee HUE-3470 [editor] Clearing history should delete current query if it is an history
* ab9982b HUE-3472 [editor] Big number precision loss
* ce9e0a2 HUE-3459 [assist] Put stat popover on top
* e45318f HUE-3459 [assist] Fixed Flexbox for IE10
* 1178b10 HUE-3469 [editor] Do not try to save a query handle when submission fails
* 51ad679 HUE-3459 [assist] Use fixed positioning for assist panel
* 5676828 HUE-3459 [assist] Revert sticky assist
* 4a97334 HUE-3471 [beeswax] Set the assist database on design update
* c4557be HUE-3444 [doc2] Assign history objects a default name
* ac51f3b HUE-3471 [beeswax] Assist does not show the DB from the saved query
* d666a91 HUE-3467 [editor] Autodetect and transform dates for X-Axis of line charts
* 8cef026 HUE-3465 [editor] Fix broken jasmine tests
* 1193621 HUE-3468 [editor] Show queries for editor type on the queries page instead of all notebooks
* 159eaec HUE-3408 [editor] Use consistent snippets in the HS2 tests
* ff33fdb HUE-3464 [oozie] Add granular permission to enable only the dashboard
* c1d3ff7 HUE-3463 [core] Stop printing None on error page when there is no exception detail
* 1f9e074 HUE-3462 [metastore] Provide clean message if table data can't be loaded in create table wizard
* 08c230b HUE-3459 [assist] Fix issue with single panel in metastore and new editor
* 9db626e HUE-3372 [assist] Add a bit of white padding on the right for underneath scrollbar
* 594997e HUE-3465 [editor] Cache the value samples for the autocompleter
* 49b52d1 HUE-3209 [editor] Faster touchpad speed when scrolling on result grid on linux
* 9b360e5 HUE-3466 [editor] Align history icons
* 895a66d HUE-3320 [editor] Show a popover for long descriptions
* 48e1fac HUE-3367 [editor] Add data sample for columns
* da381f2 HUE-3458 [editor] Support touchpad horizontal scroll on result grid
* fd38558 HUE-3459 [assist] Clear the height interval on update
* 27a095b HUE-3406 [editor] Save the multi query index
* 5ef7b42 HUE-3408 [editor] Reloading a canceled query will show an error
* 83a27a3 HUE-3214 [editor] Persist status of a running query
* c487223 HUE-3461 [notebook] Flag to show notebooks in the top menu
* 25ae9a4 HUE-3456 [notebook] Send notebook type when executing snippets
* 70384e4 HUE-3454 [editor] Textarea height is not persisted
* 972c9e2 HUE-3460 [core] Cancel unused intervals on jHueTableExtender
* 442b0d5 HUE-3459 [assist] Assist doesn't stretch to the end of the page in the old editors
* 407de80 HUE-3450 [editor] Disable value stats and suggestions in the autocompleter
* 9786235 HUE-3457 [assist] Assist is not showing up in old editors
* 825d38d HUE-3453 [editor] Do not show clear history button when empty history
* a453da9 HUE-3436 [oozie] Retain old dependencies when saving a workflow
* 520418d HUE-3452 [home] Some icons on selected rows have white background
* a3e9dda HUE-3433 [home] Use a solid share add-on for shared doc icons
* 21ef41d HUE-3451 [assist] Add DB icons
* 8bd41b8 HUE-3230 [core] Remove Plotly dependency from common_header
* dba9a4e HUE-3433 [home] Make icons more recognizable
* 8df89f1 HUE-3431 [home] Improve the sharing modal add user action
* 81e5477 HUE-3450 [metadata] Add similar queries API
* 2d51e93 HUE-3450 [assist] Make enrichment optional in assist
* 0397918 HUE-3450 [metastore] Add metadata URL check on partition page
* 5366a0f HUE-3450 [metadata] Improve mocked query hint on join
* 3ad1e24 HUE-3450 [metastore] Show if fact or dimension table
* a71931b HUE-3450 [metadata] Disable enrich by default
* 0004f5d HUE-3450 [editor] Add a real link to Impala
* c387547 HUE-3450 [metastore] Only sort by popularity whehn enrich is turned on
* f1638cd HUE-3450 [metastore] Sort tables by popularity
* 5e46b4f HUE-3450 [metadata] More error protection in topTables API
* 4d778d4 HUE-3450 [editor] Move hint suggestion to 5s timeout
* e47f4a1 HUE-3450 [metastore] Show optimizer button only when enrich is selected
* a2be2de HUE-3450 [metadata] Filter search entities by certain types
* 51cd8a4 HUE-3450 [metadata] Workaround bug in Opt popular value API
* 257cf6e HUE-3450 [editor] Plugin query compatibility API
* 289f8e2 HUE-3450 [editor] Suggest popular values next to columns in autocomplete
* 6f895e0 HUE-3450 [medatata] Add default empty values to the lineage API
* 9aa4dad HUE-3450 [metastore] Do not jsonify the table id
* ca315bd HUE-3450 [metadata] Load relationships after getting the table id
* d34ba96 HUE-3450 [metadata] Implement getPopularFilterValues API
* 1cbe919 HUE-3450 [metadata] Use real id for relationships
* 5a74079 HUE-3450 [metadata] Add relationships section
* 14a6619 HUE-3450 [metadata] lowercase inputs and flatten and lowercase targets
* 84c8297 HUE-3450 [metadata] Consisten error handling in table_details
* 41c2110 HUE-3450 [metastore] Move popularity title to the full progress bar
* 96ff9ec HUE-3450 [editor] Slight improvement of redacted and complexity notifications
* e842b47 HUE-3450 [assist] Perform empty search on focus
* 3e8d331 HUE-3450 [metastore] Add column popularity to table page
* 0a81814 HUE-3450 [metastore] Make consistent background of joins
* fc7802b HUE-3450 [metadata] Revise lineage API to be simpler
* e19c74b HUE-3450 [editor] Limit popular tables fetching to default DB
* e62dca8 HUE-3450 [editor] Autocomplete with popular columns + values after 'select * from x where '
* 605ca78 HUE-3450 [editor] Autocomplete with popular values after 'select * from x where y = '
* 062e50c HUE-3450 [metastore] Add counts of joins and queries
* bebe940 HUE-3450 [metastore] Add progress bar to table join percentage
* 6ae3a7f HUE-3450 [metastore] Display tables joins
* 94b5256 HUE-3450 [metastore] Require at least 3 columns for the top columns
* b512df0 HUE-3450 [metastore] Bump the top 5 columns first
* 18fb397 HUE-3450 [metadata] Add popular_values API
* 3055f01 HUE-3450 [metadata] Add view in optimizer button
* 612522c HUE-3450 [metadata] Add related queries on table page
* 87a0c6a HUE-3450 [editor] Add SQL query compatibility button
* a389b03 HUE-3450 [metastore] Add missing metadata flag on database page
* 425b753 HUE-3450 [metastore] Integrate with real topTables
* 9b0fb2f HUE-3450 [assit] Add more links and icons to the search
* fd4add4 HUE-3450 [assist] Add table links to search
* 046e121 HUE-3450 [metadata] Fix typo in query hint API
* bc26afb HUE-3450 [metadata] Filter find_entity based on filesystem
* 9239d0a HUE-3450 [metadata] Add data in table autocompletion
* 2ed85db HUE-3450 [medatadata] Add tagging to databases
* 9da2b81 HUE-3450 [assist] Improve nav search result
* db5f8e7 HUE-3450 [assist] Enable enrich toggle for assist search
* f663715 HUE-3450 [assist] Initial nav search implementation
* eebaa3b HUE-3450 [core] Improved icons
* d9e4d4c HUE-3450 [metadata] Fix typo in entity search
* b861021 HUE-3450 [metadata] Add lineage endpoint to Navigator API
* 2409a38 HUE-3450 [metastore] Offer to edit table tags
* 8087211 HUE-3450 [metadata] Allow empty Navigator search query to get all entities
* 08a14ee HUE-3450 [metastore] Add a mock permission table page tab
* 87681a2 HUE-3450 [metastore] Mock table statistics to all the databases
* f3850a2 HUE-3450 [metastore] Support statistics by databases
* 3924194 HUE-3450 [assist] Add navigator search skeleton
* 0b95d09 HUE-3450 [assist] Fix issue with no panels selection after all panels are removed
* b0c1205 HUE-3450 [metastore] Merge optimizer stats with the tables and show progress bar + count
* b86976d HUE-3450 [metadata] Switch to if binding for optimizerEnabled
* d710104 HUE-3450 [metadata] Provide hints on queries
* e0dd8fe HUE-3450 [metastore] Rename top tables title
* 57fd08f HUE-3450 [metadata] Add get_field and update find_entity endpoint
* f8df374 HUE-3450 [metadata] Initial search_entities Navigator API endpoint
* d84877e HUE-3450 [metastore] Show extra medata fields when available
* 62f5d4c HUE-3450 [metastore] Add top 10 tables as a piechart
* 5b9ce9d HUE-3450 [metadata] Add on/off Optimizer flag for Metastore
* d37815f HUE-3450 [metadata] Enable enrichment of table list
* 30ccecd HUE-3450 [metadata] Refactor Navigator API for v3 support
* df2fd42 HUE-3450 [metadata] Add API to get query compatibility
* ee40e77 HUE-3450 [metastore] Initial metadata integration
* 5d258b1 HUE-3230 [core] Introduction of Plotly JS
* ad4ae17 HUE-3448 [useradmin] Do not show edit permission icon link if the user does not have the permission
* 773a33f HUE-3446 [editor] Limit the height growth of the SQL textarea
* 32a2101 HUE-3347 [editor] Improve current query highlighting
* db74f44 HUE-3443 [doc2] Allow docs to be saved without name and add HOME_DIR constant
* 149a502 [jb] Skip jobbrowser log test if not in live cluster mode
* 553dea9 HUE-3407 [editor] Do not hide the multiquery counter when executing a query
* 3a210c4 HUE-3434 [jb] Logs of finished Oozie workflow are not displayed
* 45a5141 HUE-3412 [editor] Provide start and end position in multiquery execute() API
* 50dda74 HUE-3437 [core] PamBackend does not honor ignore_username_case
* 02fcde5 HUE-3383 [notebook] Update historify tests to use the new helper
* 95e5725 HUE-3423 [hive] Add server interface into the debug statement
* d4523c7 HUE-3413 [editor] Do not give a default name to new queries
* ff046b1 HUE-3411 [editor] Add tooltips to the snippet headers
* 0bbf81d HUE-3383 [editor] Move historify to the backend
* dc6936b HUE-3435 [oozie] Do not break the history when passed workflows have some credentials
* 205f81f HUE-3424 [doc2] Restrict re-sharing to permission the user does not have in the popup
* a2140a0 HUE-3432 [home] Sharing modal doesn't show the document name and there's white space in the user names
* 46b0788 HUE-3428 [home] When starting in a folder and going back to the root it's not loaded
* febdd17 Merge pull request #310 from oflebbe/master
* 15cc437 Merge pull request #334 from sky4star/master
* 61ff787 [livy] bug fix, recognize spark property: files, jars
* 9a86082 HUE-3429 [assist] Analysis alert icon goes to a new line on Firefox
* c96a178 HUE-3370 [metastore] Show the sample icon in the assist and related pages
* 88424b2 HUE-3427 [home] Rename remove and delete to match file browser wording
* 7ce4b2c HUE-3426 [home] Removing group share throws error
* 23c01eb HUE-3388 [home] Hue admin should have the delete button enabled
* 4860968 HUE-3420 [assist] DB assist shows --> icon for databases all the time
* 403245b HUE-3425 [metastore] Lack of horizontal scroll on sample tab
* eb11e9e HUE-3421 [doc2] Restrict re-sharing to the given user's permission level
* 4fb2aa0 [doc2] Validate against creating circular dependency when saving and moving docs
* ad4caf3 HUE-3338 [doc2] Support saving a notebook/editor to a specific parent directory
* c1c518f HUE-3418 [core] Update hierarchy of beeswax/impala conf so that it doesn't get clobbered by SSL configs
* 0109911 HUE-3385 [editor] Add feedback on cancel button
* 40ac1d5 [doc2] Check CSRF token when importing and exporting docs
* c7e040f HUE-3409 [home] New documents should open in new editors
* 2924ab0 HUE-3392 [oozie] Send deleted workflows/jobs to trash instead of destroying
* 4a8da8b HUE-3384 [editor] Need better error message when canceling instead of None
* 3173731 HUE-3398 [beeswax] Filter out sessions with empty guid or secret key
* 52f5f3a [metastore] Support parsing precision scalars in nested types
* 841061f HUE-3402 [fb] Replace edit path icon with on hover styling
* 71ff3fc HUE-3399 [editor] Column show after some scroll shifts the headers
* c1d4321 HUE-3403 [home] Big bar is back on the assist on chrome
* da56b88 HUE-3397 [core] Flaky and sometime double scroll bar
* 70519a8 HUE-3382 [fb] After a file upload, change the background of the new rows to be more visible
* 6761684 HUE-3396 [doc] Disabling an app might trigger and error on each page with assist
* fe0e40d HUE-3395 [core] Avoid querying on TextField to bypass Oracle ORA-00904: : invalid identifier error
* f6900ae HUE-3390 [search] Solr Index browser in Hue mislabeling Indexed/Stored fields
* 0d1e20a HUE-3393 [security] Remove Sentry app dependency on Hive app
* 6b63e5b HUE-3379 [editor] Wire explain button
* c110b63 HUE-3368 [home] Increase the size of the icons in the doc list with a few pixels
* 48a9696 HUE-3381 [editor] Horizontal scroll bar handle is always tiny
* 50512c6 HUE-3386 [core] After TTL expires the UI should exit and logout the user
* 4616ba6 HUE-3391 [security] Remove dependency on Search app
* 2dc520d [beeswax] Fix sample partition test to accept optional column
* a61084d HUE-3357 [editor] Update sample API to provide data for a column
* ed784d6 HUE-3387 [editor] Show the history in the examples
* 9c3a66f HUE-3377 [editor] Cancel button is greyed
* 5a7eb5e HUE-3380 [core] Harmonize menu labels for responsive FB and JB
* 82cd913 HUE-3349 [editor] Harmonize multi query counter
* d9b3aed HUE-3330 [core] Replace perfectScrollbar with Nicescroll
* 82c0e00 Merge pull request #324 from xq262144/master
* 00bf745 [desktop] Fix oauth_authentication_time metric decorator typo in liboauth
* 37573d1 HUE-3378 [editor] Cookie the 'show logs' action
* 1c7d16f HUE-3345 [editor] Display info message when a query was redacted
* eec343d HUE-3331 [editor] Explain API functionality
* 026ff0c [jb] Use MR API if the job is in a running state, fix tests
* b237af1 HUE-3305 [oozie] Show last 30 workflow materialization in SLA graph, rather than first 30
* 2fa6f44 HUE-3365 [editor] Display column type as tooltips
* a08b2af HUE-3215 [editor] Ellipsis the query string in the history
* e461617 HUE-3355 [editor] Allow the INSERT into HDFS only for Hive
* 9f9515c HUE-3315 [editor] Save large result on HDFS
* 4beef78 HUE-3313 [editor] Save result as a table
* 943fa8c HUE-3314 [editor] Save result as csv HDFS file
* b1866eb HUE-3356 [jb] Fall back to JHS if a job is not found in YARN RM
* 00507fe HUE-3369 [metastore] Sample icons in table list does not display anything
* d4e15a1 HUE-3363 [home] Right-click context menu is not shown in Firefox
* 2f87ad0 HUE-3364 [home] Limit actions for docs that are shared with the user
* d7a5efe HUE-3362 [home] Indicate that a folder or doc is shared with the user
* 62c6ac3 HUE-3360 [home] Document search is incorrectly positioned
* b8c25d9 HUE-3359 [home] Document search is broken
* 814bace HUE-3358 [home] Use SVG icons with hive and impala logos for documents
* 13bb359 HUE-3352 [home] If the user only has one folder that is shared with the user open it by default
* ee929e0 HUE-3346 [assist] Line below tabs are not properly positioned
* 913fcfb HUE-3347 [assist] Column stats are empty
* 411a116 HUE-3351 [home] Drop the shared column
* ac4f7f1 HUE-3340 [home] Truncate long document names with ellipsis
* 4ee6ea0 HUE-3337 [assist] Empty result indicator is incorrectly positioned
* d83c5bd HUE-3342 [home] Set the proper URL when navigating back to root from a folder
* 48b2498 HUE-3290 [doc2] Add tests for import_documents
* 38b19d8 HUE-3290 [doc2] Improve import JSON document UX
* 66af603 HUE-3350 [metastore] Reverse browsing link to use the correct version of the editor
* bbd8dd8 HUE-3336 [editor] Move Explain to first position in snippet combo button
* caba0a9 HUE-3207 [doc2] User's home directory response returns shared docs in the children collection
* 3520d80 HUE-3293 [core] Put new editor flag in [dektop] in hue.ini
* 848cac6 [tools] Add lint-checker git pre-commit hook
* ca6ca1a HUE-2678 [jobbrowser] Read Spark job data from Spark History Server API
* 096d22b HUE-3339 [useradmin] Delete groups that have been xssed
* aedd69c HUE-3216 [assist] Merge sample + stats popups
* 4b44d80 HUE-3321 [editor] Don't save the settings visibility state with the editor
* d0248e2 HUE-3335 [editor] The action buttons next to editor and result are not aligned and too close to the panels
* c10cb66 HUE-3334 [editor] Update test, now se send empty query instead of error
* 67eaaec HUE-3334 [editor] Skip checking for multi queries if there is no semi colon
* 30646b4 HUE-3312 [editor] Generic SQL icon instead of Hive for postgres, jdbc.. snippets
* b54df8f HUE-3282 [editor] Combo buttong with Clear, Explain, Format
* 749fc5e HUE-3171 [editor] Fix vertical resize handle for queries with long descriptions
* 51fb8ed HUE-3171 [editor] Long descriptions doesn’t wrap and headers from table follows with horizontal scroll
* 78cfc35 HUE-3289 [assist] The action icons stay a bit too long after hover
* d11120c HUE-3310 [jobsub] Prevent browsing job designs by API
* 108d6f9 HUE-3301 [editor] Add generic API support for fetching table sample data
* fa3bb0f HUE-3302 [jb] Display 403 error in a popup
* c5dad1d HUE-3120 [editor] Export to excel sometimes fails
* 5309c59 HUE-3203 [metastore] Reset the loading state of the submit button
* b3ea1ee HUE-3303 [core] PostgreSQL requires data update and alter table operations in separate transactions
* 2ba34a7 HUE-3293 [core] Prevent document matching query error when going one home 1
* d6c1268 HUE-3293 [core] Fix mis-switching to new home page when new editor is on
* c0f63a7 HUE-3293 [core] Move new editor flag to desktop
* 0e66251 HUE-3100 [useradmin] Only show language select if user profile is for current user
* 8de37b9 HUE-3100 [useradmin] Add a language setting in User's Edit Profile page
* c56af90 Merge pull request #318 from antbell/enable-xlsx-write-optimization
* 498c803 HUE-3221 [metastore] Styling on column stats popup leaks on the tables page
* 6285809 Use .xlsx write-only optimization in export_csvxls.py
* 399faa9 HUE-3201 [editor] Resize query area handle bar is flaky
* 9ad223c HUE-3203 [metastore] Allow load data popup to show up
* 0591f8f HUE-3199 [oozie] Add support for earlier schema versions in external workflow graph
* a04bdad [oozie] Fix failing unit test for HUE-3198
* 4b9f8b6 HUE-3163 [editor] Save results to Hive table redirects to Metastore but doesn’t display new table
* 59bce3d HUE-3198 [oozie] Remove end/kill node hardcoded names in external workflow graph parsing
* 5ef0bd6 HUE-3196 [metastore] Hide potential double scrollbar on assist
* 5d477c9 HUE-3186 [metastore] There are no spinning spinners on load
* 5adf1a4 HUE-3193 [core] The login form should display the ldap server nicely
* 940c887 HUE-3195 [metastore] When setting the table name in the URL it sometimes shows the list of databases
* d88f361 HUE-3194 [metastore] After creating a table or database the user is not always taken back to the metastore
* c9743fd HUE-3078 [impala] Make the flush_all an option on invalidate when refreshing
* 93c9d2a HUE-3181 [desktop] Avoid distinct query which fails on Oracle objects with CLOB (text) fields
* b159b5a HUE-3189 [search] When select type of chart, switch to the chart mode even if not on it
* ed7f55f HUE-3078 [impala] Drop the remember invalidate decision from assist refresh and add flush_all = true
* 4137517 HUE-3173 [fb] The file uploaded correctly message after a desktop drop upload is shown after the first click away from FB
* 9298f89 HUE-3148 [metastore] Rename 'View in Metastore' link in sample popup
* ca764db HUE-3190 [metastore] Hide refresh stats button if user does not have the permissions
* a10b707 HUE-3185 [oozie] Avoid extra API calls for parent information in workflow dashboard
* 18cfde7 HUE-3161 [oozie] Fix automatic workflow parameter population in Coordinator editor
* 17c5714 HUE-3150 [fb] File refresh icon doesn't do anything
* 399f1ee HUE-3159 [metastore] Column name links don’t do anything
* d11af65 HUE-3162 [oozie] Change Bundle submission start and end date to server TZ
* 1be033a HUE-3167 [metastore] Column stats refresh warning is not accurate
* 8d315c0 HUE-3172 [fb] Canceling a dropped file from Desktop causes a JS error
* b88ddb9 HUE-3177 [metastore] Automatic scroll to top when opening a table or database
* 6af05ba HUE-3178 [metastore] We do not default to any DB in assist and table page
* eda32e3 HUE-3125 [fb] Offer d&d progress bar to regular uploads
* a9b450c HUE-3169 [fb] Improve visibility of the loading status
* 65b0780 HUE-3154 [metastore] Select all checkbox is reversed
* f365f20 HUE-3174 [fb] Confirm empty trash should have a btn-danger button
* 59eae55 HUE-3151 [fb] Saving a file where you don’t have permissions gives an http 500
* d2ae487 HUE-3160 [metastore] Update test to read the correct response field
* 43a04c3 HUE-3181 [search] Hue demo collections should use global blockcache
* 6e14613 HUE-3163 [beeswax] Fix Save to Hive table form validation to construct correct redirect URL
* 06917a0 HUE-3180 [useradmin] Override duplicate username validation message
* ca7d7a2 HUE-3168 [beeswax] Canceling a query can give a js error
* be1dfd5 HUE-3179 [desktop] Catch potential dependency errors in converter
* 53c4fab HUE-3176 [metastore] Hide the ability to import data into views
* ad8333b HUE-3160 [metastore] Adding a comment to a column doesn’t give an error if there are no permissions
* fbf1630 HUE-3156 [hive] XLS or CSV download with Impala error
* ecf5408 HUE-3166 [metastore] Use the new way of browsing only with the new editor
* 440fcce HUE-3165 [metastore] Do not show load data button when missing write permission
* 95cc25d HUE-3145 [metastore] Show error when missing permission to load data table
* 0a768c4 HUE-3147 [hive] Explain button causes JS error
* a9c0e5c HUE-3157 [metastore] Table headers disappear when scrolling down
* 625e6b2 HUE-3155 [assist] Fix resizing being stuck
* 419ed7c HUE-3153 [fb] Fix issue where history included a leading =
* 5ced8c9 HUE-3142 [editor] Disable terms panel
* f89d476 HUE-3152 [fb] Moving a file doesn’t show the tree if you don’t have the right permissions
* 70d3634 [metastore] Move scroll to columns table instead of on window
* 709500c HUE-3158 [assist] Fix assist resizing issue
* 016c9a7 [core] Tune the increment and limit for foreachVisible
* aa10955 HUE-3144 [beeswax] Install either SavedQuery or Doc2 depending on use_new_editor flag
* 11d89b8 HUE-3144 [home] Hide new query examples from old home page
* 064ed58 HUE-3141 [doc2] Remove unused tags field from import
* 9813a65 HUE-3139 [core] Update default banner sample text to fit
* acd0af0 change option name in a configuration parser
* 17703aa hide away django from an end user.
* 13e9df0 Use default in the configuration. Move option out of SSL related options group
* f7b823a X-Frame-Options value can be set in desktop config.
* 873e2f9 [beeswax] Fix error when executing after browser refresh
* b3e5205 [core] Add $indexOffset and support for plain arrays in foreachVisible
* 5eb1104 [core] Disable HTML validation as extremely verbose and currently unused
* 2e13a82 [metastore] Remove link to user page as this page does not exist yet
* 7878963 [editor] Fix JDBC API connector
* aac6fcb [core] Prettify unifying the general log level
* d92810d [core] Set all loggers to debug when debug is ON
* 5b019c8 [core] Force all DEBUG when django_debug_mode is True
* fae83f3 [pig] Avoid 404 on fetching the list of tables
* fc0763e [pig] Do not include variables in single line comments
* d2370bc [hive] Do not load back server_host/server_port from DB
* 426a78e [core] Avoid {"auth": false} footer when displaying the PopupError page
* 9a7eaeb [security] Enable KO deferred updates and improve the saving UX
* cae6e7f [core] Link the correct home to the topbar home icon
* ba05647 [pig] Init assist helper with user for the correct cache
* edab477 [editor] Support partial matching of table and database names after from keyword
* 81c7ac1 [core] Fix broken jasmine tests
* 02f00b0 [beeswax] Get rid completely of any reference to the old autocomplete
* 4d88499 [editor] Add tgz as archive extension
* 1fd70ec [pig] Wire HCat autocomplete to AssistHelper
* 005ea87 [core] Enable ignore_username_case and force_username_lowercase for SpnegoDjangoBackend
* 9f51ecb Merge pull request #311 from fermich/master
* 2b518e6 [metastore] Fix filtering by partition
* 0226746 [notebook] Fix regex for HDFS paths, fix test
* 516b22b [metastore] Don't reference non existing variable in partition filter
* 78381b5 [notebook] Refactor HS2Api and add initial test framework
* d37f082 HUE-3132 [core] Fix Sync Ldap users and groups for anonymous binds
* b251c95 HUE-3053 [oozie] Timezones mixed on Coordinator Dashboard
* b385919 [editor] Switch functions list setting to map instead of list of strings
* 173e2fa [editor] Switch files list setting to map instead of list of strings
* af6c142 [beeswax] Fix test_clear_history
* df09064 [beeswax] Recreate customers parquet file sample
* a2fcdc6 [metastore] Speed up loading of initial page
* 439da83 [beeswax] Introduce hueDataTable for tables with more than 500 cols
* 7459cef HUE-3078 [impala] Ask if the user wants to invalidate on refresh for Impala
* 28100a1 [assist] Switch to database view on refresh
* fd18ce9 HUE-3078 [impala] Call invalidate when the assist is manually refreshed
* af2aafc HUE-3126 [fb] Disable modal hide on file upload
* e2a1953 [beeswax] Improve window sizing for assist
* e066c23 [beeswax] Don't include db references in autocomplete for the old editors
* ae1109b [core] Add the Hue version to the Require load URL
* 00ee249 [core] Remove window resize delays for IE8
* 33a870c [impala] Fix test_get_settings by granting test user access to impala
* a7a73a0 [editor] Do not call fetchHistory twice on new queries
* 130d63a [editor] Use the new API to list saved queries
* 92c7d20 [editor] Prevent List index out of range when number of queries changed
* 60774a6 [beeswax] Add a get_settings API endpoint and add test
* abf9392 [doc2] Add an update_document endpoint
* 2fe09eb [notebook] Accept settings, file_resources, and functions as serialized by request
* 462d25b [libsaml] Document in the ini the private key password file property
* 99f31ee [assist] Show a message when no databases are found
* 36d5f39 [editor] Use key value input for settings
* 98bbdd8 [editor] Constrain the sortable properties and move the minus next to input
* ced5657 [core] Upgrade knockout-sortable
* 428d272 [beeswax] Enable a whitelist of Hive configuration properties that users are authorized to set
* 82cd591 [doc2] Fix tests related to doc2 API changes
* 20efe75 HUE-3124 Display the restart button when we have more statements to execute
* 8560caf [editor] Display number of statements when using multi queries
* 446e05c [desktop] Allow doc1 API tests to accommodate old and new editor modes
* daa6bc2 [doc2] Fix history fetching and update documents API in JS
* d2e2756 [doc2] Better renaming of include_history flag on search_documents
* f19d7aa [doc2] Refactor documents API and consolidate views
* 6bfc61e [doc2] Add search_documents endpoint at /desktop/api2/docs/search
* 6777a7b [oozie] Skip check for new oozie docs
* 032e896 HUE-3096 [core] Log warning when downloading to CSV or XLS and file is truncated
* c64d2b1 [jb] Do not display a duration for applications that don't have a start time
* 2dc47ee [editor] Rename My queries tab to just Queries
* b7ed21f [editor] Better logging of query execution
* 3879fe8 [home] Hide directories from old home page
* 6280231 [editor] Save different working queries for Hive and Impala and different users
* 6b053e7 [assist] Always show the search and refresh actions instead of only on hover
* eefbb46 [assist] Only show the documents in assist when the new editor is used
* 09e28f7 [editor] Add onStart callback for the Ace resizer
* aa07421 [home2] Fix sharing
* 21a1620 [oozie] Fix integrity error on lookup by UUID
* eb4e9ab [oozie] Add oozie examples to shared Doc2 examples directory
* fe14606 [core] Revert setting MySQL default engine to InnoDB
* f8197d7 [editor] Add the possibility to expand the logs
* 50b689a [assist] Fine-tune inner panel resizing and fit
* c7de85a [assist] Fix wonky inner panel layout
* d92429e [editor] Show pagination just if there are multiple pages
* 312e607 [editor] Added more space on top of the history tables
* fe82cd1 [editor] Style the query history and my queries tabs
* 5242a42 [editor] Populate the queries table
* e10a95b [editor] Fetch paginated queries
* 3047a20 [editor] Introduce tabs for query history and my queries
* 6834ea3 [assist] Add type option to document search
* 1a9b84f [editor] Fetch history when loading saved queries
* 3a2cfe69 [editor] Limited editor expansion to 2000 lines
* ef4b4e1 Uncover ability to set the oozie.use.system.libpath variable on the Workflow Settings view
* dd11d28 HUE-3086 [oozie] Upgrade email action to 0.2
* 90b4155 [desktop] Rename paths to old home in tests
* 42c7488 [metastore] Hide the tagging section
* e51f0ec [metastore] Hide unused columns
* b0b4f25 [editor] Turn the new SQL editor on by default
* 7aba6ae [assist] Add error check for code 500 and 503
* a43c609 [spark] Fix path to example Spark fixture
* 4f16496 [beeswax] Update install examples to be compatible with old and new document types
* 6408c01 HUE-3111 [editor] Improve performances for query files of 20k+ rows
* 3be5444 [assist] Fix refresh issue when listing databases
* 2ec8f92 [editor] Use foreachVisible in the DB selection dropdown
* 1c0591b [core] Added support for SQL comments to vkbeautify
* 620d04f [core] Added CACHEABLE_TTL default value to the .ini templates
* 9aebb85 [core] Introduced CACHEABLE_TTL desktop configuration for the Assist/Autocomplete cache TTL
* 2fb80ad [assist] Add refresh button to HDFS panel
* 474c6b7 [assist] Improved cache refresh handling
* b59870e [editor] Keep the DB selection dropdown visible when opened
* 2ffd093 [assist] Only fetch the documents when that panel becomes visible
* fb64ce3 [editor] Remove force update to the scrollbar that hides autocomplete
* 61a3303 [assist] Queue the db-related API calls
* 60aba81 [beeswax] Add support to run beeswax tests in Hive on Spark mode
* 72b47a7 [doc2] Install beeswax and impala examples as Doc2 queries
* e3e883f HUE-3071 [oozie] Add workflow link in dashboard graph for sub-workflow action
* 5a09404 [core] Recreate scrollbar on foreachVisible update
* 04a108d [assist] Fix problem with missing drag data from dividers drag
* 6fb88fe [core] Add a scrollYFixedTop setting for Flex-based scrollbars
* 3e85931 [core] Fix broken jasmine tests
* 0218995 [metastore] Improved icons on database page
* 5a83817 [core] Added Perfect Scrollbar sources for Hue specific changes
* fa286de update pyopenssl to 0.15.1
* 7ac56a2 [home2] Speed up the isTrashed computed
* 88dfd23 [assist] Only cache responses that contains entries
* 2b0a0b1 [metastore] Hide the stars
* ed54532 [core] Fix issue where foreachVisible accidentally renders all the items
* e933d24 [notebook] Update tests to verify that history API filters by type
* 52cac00 [hive] Prevent 'Could not connect to xxx:21050: Int or String expected'
* a0fa636 [sentry] Disable the with Grant option for Solr
* 13039a8 [search] Trigger back the display of the field analysis popup
* 45d48c7 [core] Add a command to test the DATABASE connection
* c377043 [core] Do not set a default path for SSL ca_certs
* 171fdb1 [assist] Introduce a fetch queue for requests to the same URL with same parameters
* 9e241d5 [home2] Drop one superfluous fetch of documents
* 75715bc [home2] Add the delete top action back
* dbf2c86 [home2] Fix the double scrolling bar
* 82a035e [core] Add a per-browser configurable Assist cache
* a6e6925 [editor] Truncate SQL import after 5000 lines
* 88b8e94 [editor] Added jHueScrollUp for the right panel
* 46bca65 [editor] Redraw fixed headers on variables show/hide
* f807174 [editor] Redraw fixed headers on logs slide down
* cb4f918 [editor] Redraw fixed headers on history slide down
* a4f3aee [home2] Enable drop of files on the trash icon
* 4ba8a87 [home2] Enable drag to select of documents and not just directories
* c625168 [home2] Fix issue with hidden search preventing breadcrumb clicks
* 1fdab09 [doc2] Remove has_children property
* a5a9f4e [doc2] Implement and test recursive skip trash
* 5b89511 [doc2] Adjust doc2 same name validation to be less strict and only rename but not throw error
* f7f50f7 HUE-3110 [oozie] Fix bundle submission when coordinator points to multiple bundles
* 6595161 [doc2] Allow to move files into a directory
* 1e4739c [editor] Fix scrollbar size after new results are rendered
* 466aecb [editor] Enable mousewheel support for the horizontal scroll
* 214940b [editor] Create always visible horizontal scrollbar for the result table
* c3399bf [editor] Improved UX of the result table (sticky header) and enabled custom scrollbar for the right panel
* 87fd928 [home2] Disable unsuitable top actions when in trash
* c7bdeda [home2] Only show delete when right-clicking trashed documents
* 99f73e5 [home2] Don't show sharing in the trash
* 4af3bf9 [editor] Remove Kinetic from the result tables for better scrolling performances
* 65720b5 [doc2] Add has_children property
* 7f8adfb [home2] Enable delete forever with alt + right-click on selected entries
* 284beaf [home2] Add action to show the trash
* ec83b08 [notebook] Fix notebook tests
* f4292dc [notebook] Update historify API and add tests
* 2118733 [doc2] Fix converter permissions test
* 9ea761a [oozie] Fix footer of the bundle page
* c1de65d [doc2] Add tests for Doc1 to Doc2 converter
* e72503c [doc2] Copy permissions during import
* 3742cf1 [doc2] Create separate module for converting doc1 to doc2
* 7e47c50 [doc2] Import Job Designs as linked doc2
* b86bdc9 [doc2] Import Pig scripts as a linked doc2
* 6b6741e [doc2] Auto-rename documents and directories with same name at same path
* 6a8b54d [doc2] Fix doc2 validation test
* 4fd7c6a [editor] Temporarily removed custom scroll on the right panel
* f377c14 [assist] Switch to definition-observable for the documents panel and drop the multiClick binding
* b5d82f3 [home2] Add support for UUID and path url parameters
* 21acdb1 [home2] Update sharing actions to use the new doc2 API
* 8513672 [home2] Include borders in foreachVisible height calculations
* 35945da [doc2] Make document name explicit in validation exceptions
* 1c06972 [editor] Display history time column first
* 4d9a172 [core] Changed custom scrollbar plugin and wired it on the new foreachVisible
* c02741a [beeswax] Fix and improve fullscreen results
* 01791cb [home2] Fix partially hidden new document dropdown
* b9ad903 [home2] Fix folder navigation
* 9b8b4e9 [beeswax] Fix assist imports for the old editor
* 2d0261e [home2] Fix create folder and delete
* 3438830 [doc2] Update the homepage to use the new API to list documents
* 9e9bb6b [home2] Enable dragging of files to the assist documents panel
* bd74c64 [assist] Change the documents panel to a list instead of a tree
* 64ec0ce [home2] Initially sort the documents by name
* cf18bfd [assist] Make the HDFS panel a bit lighter
* d4f8753 [assist] Switch the HDFS panel to flex layout and use the foreachVisible binding
* 103cb3d [core] Introduced mCustomScrollbar
* e233167 [doc2] Refactor filter and pagination, and check paths after a move directory operation
* e5aabb3 [doc2] Add API endpoint to get shared documents
* e348d13 [doc2] Remove "all" flag from Document2Permission
* ee00b3a [doc2] Change validation for same path to be restricted to directories
* de23513 [doc2] Remove tags from fixtures
* dcc5c57 [doc2] Apply permission checks to doc2 API and add tests
* 46abde6 [doc2] Add recursive share permissions to directory and add tests
* 7685d38 [doc2] Drop unused doc2 tags M2M field
* ceb158d [doc2] Fix error with is_history filter (fetch when false)
* 9fa6694 [doc2] Exclude history docs when fetching documents for directory
* f884935 [doc2] Add validations and tests
* 9b18910 [doc2] Add a get_by_uuid manager method
* 4188f2a [doc2] Doc2 API and model refactor with migration for new parent FK
* 330c9ab [useradmin] Do a proper redirect when editing a group or a permission
* 52d0788 [search] Fix the inclusion of new dynamic fields into the main field list
* 8bcc675 [home2] Add sharing status column to the document list
* 2ec21f5 [home2] Switch to foreachVisible for the documents list
* 456472d [home2] Store the definition in an observable
* 93428c6 [assist] Fix table and database search and improve search performance of the foreachVisible binding
* e78ca6a [home2] Add open action to the right-click context menu
* e151e44 [core] Find the closest container for foreachVisible to
* 98ea1b4 HUE-3105 [oozie] Fix workflow graph for jobs submitted from pig editor and support case sensitive tags in definition
* 7c86a75 HUE-3106 [filebrowser] Add support for full paths in zip file uploads
* 3c99427 [assist] Use the new spinner binding
* 7d1fa3a [assist] Add the missing "Databases" header back
* c638947 [core] Add ko binding for spinner
* ce9935d [assist] Fix issue with overlap in the foreachVisible binding
* e7f17e2 [core] Fix issue with negative index after scroll
* 3bc1fff [core] Increase snappiness of displaying and hiding nested foreachVisibles
* 64cb660 [sentry] Also display the action of a Solr privilege
* 52a578d [sentry] Keep Hive v1 section unchanged and fix the table file link
* 8c0a08e [core] Fix scroll issue with foreachVisible when close to start
* 93221fd [assist] Fix positioning of nested action icons in the table tree
* 0b6772a Revert "HUE-3105 [oozie] Fix workflow graph for jobs submitted from pig editor"
* 4b8acdc [core] Tune performance of foreachVisible and make sure it renders after a long scroll
* bf12478 [assist] Switch to flex layout and use the foreachVisible binding for databases, tables and columns
* 7f80873 [core] Force foreachVisble to render on resize
* 82a4a32 [core] Add disposal logic to the new foreachVisible binding to support updates of the data
* 24e667d [core] Make the foreachVisible limits adjustable with parameters
* 0618c0a [desktop] Remove hardcoded history filtering of the API
* a911140 [metastore] Fix single drop table
* 78edb4c [metastore] Removed debug info
* 3ba1dcd [metastore] Improved look'n'feel of create table manually
* 30b27db [editor] Fix browse and download API calls
* e34f92c [core] Top menu should always point to the original Pig editor
* 3a9d3ed [editor] Support executing queries on none default database
* c12e8d2 [notebook] Trim out some of the long Hive session properties
* 592d598 [notebook] Browsing call should use the new API format
* e6b3c8f [metastore] Refresh assist after table create
* 4d51800 [core] Add the foreachVisible ko binding that only renders the visible items
* 510ffb3 [useradmin] Fix failing test TestUserAdmin.test_user_admin
* b3b8f26 HUE-3105 [oozie] Fix workflow graph for jobs submitted from pig editor
* 0b74de8 [metastore] Simplify table page listing
* 0444e43 [sentry] Removed Solr JSON dump and improve authorizable rendering
* dcea070 [core] Converted jHueHiveAutocomplete to generic with support for Solr
* 9dfa167 [sentry] Removed trailing dots from the add role form
* 7592cd5 [sentry] Introduced indexerPath
* 654988e [search] Fix absolute links to the collections
* a12a978 [sentry] Added showAuthorizable for Solr
* 227c05a HUE-3099 [useradmin] Re-order fields of new password screen to make more intuitive
* d68934f [home2] Click should never unselect an item
* c0fe4f6 [home2] Improved UX of shift+click on the entry list
* 22b4da5 [metadata] Do not strip host URL when it is not set
* efd9a9c [metadata] Add API call to upload query history
* e7516c3 [editor] Link to the new Pig editor in the menu
* ff008b1 [metadata] Add API to retrieve table details
* 9447d8c [metastore] Skeleton to prepare the introdution of the metadata frontend logic
* 2a5d744 [metadata] API to support pulling the top tables
* 3b885de [metadata] Support retrieving top tables
* 8747b7c [hadoop] Prevent Yarn API caching to tie the user to the first user calling it
* 74ab528 [metadata] Support deleting a workload
* e872568 [metadata] Support fetching status of query upload
* fbc1e81 [metadata] Upload queries in CSV format
* f55e40d [core] Support files for Multipart-encoded posts in REST lib
* 9d0e199 [metadata] Fix authenticate API
* bc0167d [notebook] Display output of Pig scripts as result
* 9cd05c1 [core] Unified the context menu shadow look
* 9bd1f42 [core] Removed clearable animation
* 2b5b259 [notebook] Fixed delete snippet dialog and execute/indent icons
* e45ac9b [editor] Added back temporary saving of query
* 28476df [home2] Add search to the UI
* b62e16ea [core] Add ko binding for toggling boolean observables on click
* b463914 [doc2] Add permissions to /desktop/api2/docs response
* 7a2c5bf Merge pull request #301 from craigminihan/patch-1
* 84a793c HUE-3103 [oozie] Add missing data to external workflow graph
* 70e5fd3 [desktop] requests should only set tls hostname if supported
* 6fed220 [editor] Enable active database selection from the assist panel
* 4d9e99b [core] Solved a bug with D3 updating the values in a previously non visible chart
* 6028e17 [core] Added global defer to chart rendering
* d58cf31 [editor] Purged html entities from charts
* 6d848b5 [home2] Show select count next to items in the right-click context menu
* 868441e [editor] Add database selection in the snippet header
* 22fa10c [home2] Right-clicking a non-selected entry will select it first
* f3b9970 [home2] Add sharing to the right-click context menu
* 9ff1df9 [home2] Require selection for delete
* 4074280 [home2] Introduce a disabled state for the action icons
* 5c4f691 [editor] Added ultra-compact result table for small windows
* 23e7144 [core] Removed wrong color on the table column fixer plugin
* fef6eff [editor] Redraw fixed headers on assist show/hide
* 00f2d5f HUE-3101 [oozie] Add decision nodes to the Actions tab in Workflow dashboard page
* 15b045c [doc2] Fix detecting duplicate directory logic
* da564e6 [doc2] Refactor documents and get_documents API pagination
* 8fa0b77 [home2] Include ctrl+key for multiple entry selection
* b22f49f [home2] Remove dependency on deleted share2.vm.js
* 472d9a3 HUE-3065 [doc2] Enables filtering, searching, offset and limit on documents
* 961d43a HUE-3102 [libsaml] Add support for private key passwords
* 1d6823f [desktop] Move coerce_password_from_script
* 1c86462 [home2] Polished UI and added initial support for floatlabels.js
* fb21cb3 [home2] Enable sharing
* 1114b45 [home2] Enable selection of documents by dragging
* da77020 [impala] Remove reference to dashboard on URLs
* a434483 [home2] Fixed pushState URL
* 84575e4 [editor] Removed invalid HTML element
* d5f3fe9 [search] Removed unused grid charts code
* c5822a9 [sentry] Fix typo in _massage_priviledge
* 2bb3b8a [optimizer] Support authenticate API
* 6b6f3f9 [optimizer] Support add_email_to_product API
* 570e2a0 sentry] Fix Hive autocomplete error on columns with API v2
* 53b3cb7 [sentry] Fix Hive autocomplete error on columns with API v1
* 556430b [sentry] Do not show impersonation with Solr
* 5647aa0 [sentry] Support deleting a Solr privilege
* c61a0bf [sentry] Display privileges from Solr component
* 63039a5 [libsentry] Workaround in API for THRIFT-3388 hash doesn't work on authorizables
* de52c19 [libsolr] Add API to list Solr Cloud configs
* 872726e [sentry] Fetch Solr collections
* 6374a71 [desktop] Support importing search dashboard format from Hue 3.7
* 75db840 [sentry] Select and highlight the correct component in the sub menu
* df0819d [metadata] Add json content type to the API
* 0b40fd9 [doc2] Add flag to enable the new editors and home pages
* 82e252e [metastore] Databases and tables filter should not show the table headers when no results are there
* d1a05fc Merge pull request #302 from antbell/fix_csv_import
* dda1512 [assist] Fixes for rendering of an initially closed left panel
* 7905e6a [assist] Unify the panel shown property
* 93030c4 Force TextFile file_format in table import
* 3bb40ed [home2] Align action icons with the breadcrumbs
* 1f6c5bf [home2] Enable drop of files on the breadcrumbs
* f46ff30 [home2] Show a spinner while loading documents
* 80df9e6 [home2] Fix issue with accessing nested folders
* 396ae85 [useradmin] Fix backwards compatibility with Python 2.6 for datetime delta total_seconds
* 1bc5e72 [dco2] Add a move a file test
* a3935dd [doc2] Add a create directory test
* 21cca5a [doc2] Update name of file when moving it
* 616bf14 [home2] Import RDBMS doc1 as doc2 and set type accordingly
* 6a95685 [useradmin] Add a session timeout that will automatically log out idle users
* b5f0b2e Merge pull request #300 from matiasjrossi/update_parquet-python
* d62a716 HUE-2659 [oozie] Workflow submitted from coordinator gets parent graph
* 72edd31 [hive] Revert to TGetSchemasReq() instead of SHOW DATABASES
* babef9d My AWS Ubuntu 14 was missing libz-dev
* 2e2d799 [core] Exclude from other apps all the apps with menu_index = -1
* 465e14d [metastore] Added current tab observable to save on rendered DOM
* 54a127d [home2] Show an error message and hide the actions on API error responses
* c8d96ed [home2] Fix incorrect path for nested directories
* 62c9087 [home2] Add support for the 'path' URL parameter
* c4add40 [metastore] Polish empty messages UX
* 21b3e12 [home2] Add droppable for moving selected files and folders into another folder
* 69e75e7 [home2] Make selected entries draggable
* b4a07c0 [home2] Fix backend Document2 move
* d394aea [rdbms] Convert decimal types to float so that they can be JSON encoded
* d6b8d9f [home2] Added empty message for empty folders
* 1fa1d37 [metastore] Got rid of legacy code
* 8d58137 [home2] Use updated API response structure
* c082995 [home2] Fix issue with empty directories
* defdd56 [metastore] Added hueach to the column list
* ffcf82b Merge upstream history from jcrobak/parquet-python as a subtree.
* fc2f008 Remove existing fork of parquet-python
* 87aa1fd [home2] Add the delete action to the file context menu
* 1250e6d [home2] Make file selection act as file selection should
* 3c9ae5f [home2] Add the download action to the file context menu
* 2bddb30 [core] Add ko context-menu binding
* c6b2f98 [metastore] Added hueach binding to the table and database list
* e1a3b52 Revert "HUE-2664 [jobbrowser] Fix fetching logs from job history server"
* 0a9c2f8 [editor] Fix end of result scrolling problems with the fixed first column
* 98d8d5c [search] Grid charts should use just the selected grid fields
* bff5a8f [core] Updated main menu responsiveness
* 76e8e7b [core] Added fixed first column to jHueTableExtender
* 5097e73 [assist] Removed extra space from column list
* 737e3e2 [doc2] Remove parent directory from the list of files
* cd2314c [home2] Enable export functionality of either current folder or selected entries
* ef0d00c [home2] Make entries selectable on click and open them on double click
* accf07d [home2] Rename HueDirectory to HueFileEntry and drop the open observable
* c1ae8c7 [home2] Add upload functionality
* f0ba9bd [home2] Enable the new document button
* 712f271 [assist] Only allow opening tables from the assist in the metastore
* c20aad2 [beeswax] Fix assist panel rendering
* 191ed4e [beeswax] Fix non re-entrant test conflicting with desktop test
* bb5dfc6 HUE-3098 [filebrowser] Avoid double-encoding files with internal mime type
* 99c9d04 [home2] Fix issue with document links
* 2c924e1 [impala] Iterate thru database generator instead of casting to list
* b704ede [notebook] Add RDBMS interface and corresponding connectors to notebook
* 65bbb1a [librdbms] Allow MySQL to accept empty password
* cc6816d [impala] Fix impala's get_databases call
* b228fc9 [home2] Enable delete of the current directory
* af45970 [home2] Enable navigation and display breadcrumb
* fbe5ab2 [home2] Add create directory functionality to the the file browser
* db6fa9f [home2] Style the file browser component and the home2 page
* 228a4a5 [home2] Create skeleton file browser ko component
* b1bcfdf [home2] Drop the old file list with pagination and switch to the new HueDirectory
* 40e2c28 [core] Add a generic representation of a directory
* ac370a6 [core] Added specific JDK version to README.md
* ce5fe95 [editor] Added basic SQL formatting capabilities
* 958d915 [doc2] Remove older get document API endpoint
* 782cabd [doc2] Prevent creating conflicting home directories
* 36553b7 [metadata] Basic skeleton on API for an SQL Optimizer
* d762bba [notebook] Remove table striping from history as too "heavy"
* 9e033f7 [doc2] Import Hive and Impala queries from document1 to document2
* ef8e68e [doc2] Utility to convert beeswax Hive queries to the new Notebook format
* 7dee863 [notebook] Utility to create a notebook
* 25468c0 [notebook] Add support for Hive UDF in the properties panel
* 7763b47 [sentry] Create a Hive privilege with API v2
* d840117 [sentry] Do no json encode the component name in API v2
* 4664631 [home2] Introduce requirejs and add the assist panel
* 30d115d [metastore] Remove extra div
* b60fc65 [assist] Switch documents to docs2 endpoint
* cbdfaf2 [core] Improve assist display of nested items after scroll
* e8b14a7 [metadata] Initial metadata API
* f2bb360 [search] Fixed grid charts defaults
* 161c2dc [editor] Added right i18n escaping to the KO labels
* 7701dcd [pig] Fix automatic support of scripts with credentials
* a3b6378 [assist] Always show the SQL assist panel for the editor and metastore
* 5821b98 [assist] Fix inner panel close button
* 90a52e3 [assist] Silence errors from the HDFS autocompleter and show the correct details from errors in the assist
* 753f581 [editor] Fix the alt-click for metastore info link
* 48aec02 [assist] Show errors in the assist panel
* 1f00416 [core] Avoid blinking on hueach scroll
* 6e5d6c5 [metastore] Disable table stats for partitioned tables and add stat labels
* 4c0c364 [core] Fix SDK commonfooter generation
* 43a398f [assist] Silence all assist helper errors from the autocompleter
* ef9933e [assist] Use the same base signature for all assist helper functions
* df1bf5b [assist] Unify error handling in the assist helper
* c0854b2 [assist] Add the header name back to the assist panels
* 2b18df6 HUE-3091 [oozie] Do not remove extra new lines from email action body
* 20c5790 [editor] Added table-striped to the history and results tables
* 76ea3a1 [assist] Introduced hueach binding for faster rendering times
* e37f523 [search] Remove deprecated chart attributes in the views
* 8cc3bf0 [metadata] Add Navigator feature to update entity properties
* 55bacc4 [metadata] Navigator delete tags functionality and added tests
* a25779e [assist] Extract individual panel types from AssistPanel
* 57e3c48 [home2] Export and import of any documents
* 333b8b0 [libsentry] Workaround iin API v1 for THRIFT-3388 hash doesn't work on set/list
* 88ce3af [security] Make both Sentry API v1 and v2 pluggable
* 91f2425 [editor] Re-label the history tooltip properly
* dd40e36 [home2] Fix deleting a directory
* db62379 [core] Do not show json data on csrf page
* ea91edf [metastore] Do not show stats and path for views
* 1d2ce91 [metastore] Rename table Properties to Details
* 98c0971 [metastore] Split table properties and stats in two
* 97c3098 [metastore] Browse data on table page should use the new editor
* 363f8ef [metastore] Remove user commenting for now
* 496f3eb [metastore] Show type of tables with icons instead of text
* 14b50fc [core] Added inline login form to the Metastore and Search apps
* 9f0064a [assist] Use fixed headers and only scroll the inner lists
* 38c4c31 [assist] Fix single panel window resize issue
* 93570bd [assist] Use proper HTML for the assist DB lists
* 6d069f5 [assist] Make the assistHelper singleton to fix caching issues
* 009ba1d HUE-3059 [oozie] Refresh Next submission column in Coordinator Dashboard
* d6f2cc7 HUE-3080 [oozie] Fix code to use oozie.processing.timezone
* 2291e8d HUE-2466 [core] MySQL should default to using InnoDB
* 4e81141 [notebook] Remove session from the list when closing even if invalid
* 04d9d96 [core] Restyled admin wizard
* 692988c [core] Increased font size for the sign in form
* cd0864b [beeswax] Fix trailing slash error for autocomplete tables
* d8aa0f6 HUE-3085 [search] Create indexer goes into an infinite loop when file has odd number of quotes in a line
* b50c7f6 [assist] Limit the initially shown database entries
* fa049ab [assist] Switch to pureComputed and various minor performance improvements
* 66b611d [assist] Sort the DB assist entries by name
* 5312ab3 [assist] Extract separate table template to increase render performance and shrink the page size
* e0e3bc7 [editor] Player icon is too large
* cc90c41 [search] Pull static fields list when /luke is not successfull
* 2bd0675 [editor] Show snippet settings below the header
* ae7c086 [assist] Keep the search icon visible when search is active
* 6677502 [metastore] Fix alignment and icon colors in table stats
* 76bdcbd [metastore] Knockoutify the properties tab
* 1285f14 [metastore] Cleanup metastore HTML
* 9e8dbd3 [metastore] Extract viewmodel into separate js file
* 8c01887 [search] Fix Search tests
* 02dda1c [assist] Add details popover to HDFS entries
* 921b657 [assist] Make sure the last opened HDFS folder exists before trying to open it
* 846b429 [search] Fixed JS errors on page reload and default values
* ded9e6b [search] Plugged in Leaflet map charts for the grid results
* ad7454e [search] Plugged in displaying Bar, Pie and Line charts for the grid results
* f22bda7 [search] Plugged in all the variables for the charts and grid displaying
* 44f79fb [search] Moved download to the side buttons
* 043e346 [search] Rename get_solr_collection to get_solr_collections appropriately
* 529ee0a [search] Diff new fields against they type too
* e2d1d60 [search] Set a default field type for each field
* 749ca4e [search] Added icons to the left
* 7361109 [assist] Remember the last opened HDFS directory
* 599c846 [assist] Don't show '..' and '.' entries in the HDFS browser
* 0145af1 [assist] Add details popover to the documents
* 04c98b7 [core] Add ko binding for bootstrap popovers that uses templates for content and title
* 062f1b5 [assist] Add the column stats icon back
* 03ade20 [core] Fix for wrong quotes on the default Leaflet conf properties
* c00a447 [core] Made Leaflet tile layer and attribution configurable
* a9c5768 [doc2] Disable permission short link for now
* 1e606be [doc2] Add missing licence files
* f63227d [doc2] Add new home page access to non super user
* b5f04fe [doc2] Clean-up new home page template
* 45890eb [doc2] Add auto UUID for the short link
* 1286388 [doc2] Add auto link UUID to the database migration
* 2a6e41b [doc2] Connect permissions to Document2
* aeb673e [doc2] Add sharing popup permission
* 01ebf63 [doc2] Integrate permissions to the document2 retrieval
* 713e62b [doc2] DB migration script for new permission table
* 4f1d059 [doc2] Schema for permissions for Document2
* 21d09f3 [assist] Added documents icons
* 1e9c2a4 [core] Updated UI of dump config page
* 04f65e9 [desktop] Fix internationalization on the footer
* a68f4ac [metadata] Add initial local files
* 68ba158 [doc2] Delete a document from the new homepage
* ae352b3 [doc2] Prevent creating duplicated directories for the same user
* 7120cfc [doc2] Support creating a directory on the new home page
* 016f773 [document] API for directories and home2
* 78d1b24 [home2] Concept of directories
* ed6fd3b [assist] Fix JS error on window resize
* 305abf3 [assist] Fix for case-sensitive fs
* 4b93057 [beeswax] Add missing js dependency to query editors
* 2b403be [desktop] Do not show json data when auth error on main login page
* fbed244 [assist] Add my documents to assist
* 466b60c [core] Upgrade Knockout to 3.4
* abe6f6b [notebook] Fix window.onbeforeunload
* dcd89a0 [notebook] Fix missing /ko tag
* b5582cf [security] Fix old URL view mapping
* 7a301e9 [sentry] Update to use the new ajax login popup
* c385027 [sentry] Add a flag to turn on the new API
* d7afffe [libsentry] First part of converting list_sentry_privileges_by_role to V2
* 6a23f26 [sentry] Convert API to always provide the component
* 42d61e4 [libsentry] Support new TListSentryPrivilegesRequest format
* bf546be [libsentry] Workaround for THRIFT-3388 hash doesn't work on set/list
* 35eb919 [libsentry] Port list_sentry_roles_by_group to V2
* bc6f814 [sentry] Create a generic sentry page
* 67bcd56 [libsentry] Mock TListSentryPrivilegesByAuthRequest that is missing
* b5ad4c7 [libsentry] Remove the old TSentryGroup, TPrivilege
* e2e9d7c [sentry] Skeleton pages for new Hive and Solr pages
* e8a8bd2 [libsentry] Add api2
* 1edaf8d [libsentry] Add new component field to client
* af6fb4a [libsentry] Add client v2
* 0e1a575 [libsentry] Regenerate API v2 sources with Thrift
* 05baddb [libsentry] Comment non needed include in Thrift file
* c1050c4 [libsentry] Add the "generic" API v2
* a8d6b69 [assist] Fix wonky positioning of horizontal scroll bar in the DB panel
* 0ad74bc [assist] Show a message when no inner panels are selected
* 2032a79 [assist] Add close button to the inner panel headers
* 1bfa9c0 [assist] Fix resizing limit issue after window resize
* c31dd16 [assist] Update all pages with assist to support the new panel layout
* 656b8f8 [beeswax] Support the improved assist panel in the old query editors
* 88813d4 [assist] Restyle the inner assist panels
* b459f99 [assist] Replace the two panel layout with the new dynamic layout
* 712989c [assist] Store panel ratios in total storage
* cec2c4a [assist] Add knockout binding for resizing of an arbitrary amount of inner assist panels
* cc2459b [home] Errors in refreshing home page project document numbers
* 0dccf37 [metadata] Add logging and navigator test
* d52b6cd [metadata] Add various get entity type methods and add_tags
* 68e9ed7 [oozie] Add request to common footer call
* 5ee2bb1 [core] Fix login tests
* 75ed206 [core] Moved login_modal to common footer and added request to it
* 4a85fc5 [metadata] Initial creation of metadata lib with navigator API module
* 09e7b6c [editor] Add Impalad address to the session popup
* cf32a7d [editor] List Hive session in the sessions list
* 0cd45f4 [editor] Fix getting the session of a Hive query
* b2693dc [desktop] Update 404 test with the new case
* d3b4469 [editor] Display player button by default to prevent the jump on page load
* eb3f452 [editor] Load back impala queries in the Impala mode of the editor
* 08358e9 [desktop] Don't capture STDERR from password scripts
* 1c568cc [notebook] Show modal login dialog in case the session is expired
* 29a3e00 [editor] Put .fromNow time displaying on the history
* 69f2432 [core] Restyle HTTP error pages
* a9ebe95 [assist] Prevent flying 'x' in database and table filters
* 25db1d4 [assist] Add filter to database list
* 49c4e71 [assist] Insert the path on drag and drop of HDFS entries
* 81eebb1 [notebook] Fix issue with properties using the incorrect attribute
* 9aa5415 [assist] Insert HDFS path on double click
* 596f8b2 [home] Load the documents through an ajax call
* d9ba2e1 [notebook] Implement close_session endpoint for hiveserver2 API
* 2ec886d [notebook] Integrate hiveserver2 create_session to actual HS2 API and get or create open session
* 72b7739 [beeswax] Update session tests and allow superuser to close any session
* 796319a [beeswax] Support getting a specific session by ID, and add a close_session API endpoint
* 52076f0 [notebook] Redact hive and impala statements on Doc2 save if redaction enabled
* f82e63d [beeswax] Closing queries/sessions should report if already closed
* ef026d1 [notebook] Change logout flow to showing a modal instead
* 121eedb [assist] Store assist panel settings in total storage
* 05fc224 [notebook] Use the assist helper in the HDFS autocompleter
* 5b76ec4 [notebook] Restyled Save as button and modal
* 160afda [assist] Maintain the ratio of the inner assist panels on window resize
* 8655a46 [beeswax] Disable HDFS in the assist
* 1844fe8 [beeswax] Fix the old query editors
* 0ea363b [metastore] Fix manual create table wizard with partitions
* c812e7a [metastore] Replace non acii char
* 869f358 [impala] Don't attempt partition sample query for Impala
* 9767c1e [metastore] Open the last opened database on the default metastore link
* 3bc097e [core] Revert login required global callback on ajax success
* 9a0ea0f [core] Refresh the login page look
* 0e40068 [metastore] Added toggleOverflow component to database params
* 44d3c7d [notebook] Added global redirect handler for ajax calls after a logout
* 8998da2 [assist] Style the assist type switch
* 22b6939 [assist] Enable browsing of HDFS in the assist
* eab9c52 [assist] Add two panel assist layout
* 303caae [assist] Add KO binding for vertical resize of assist panel panels
* e168f6c [assist] Add JS model for HDFS
* e1a5ece [assist] Make double click events DB specific
* d3dd83d [assist] Rename AssistEntry and AssistSource to AssistDbEntry and AssistDbSource
* 92b5839 [beeswax] Fix configuration view to use session configuration
* 8dd2e07 [useradmin] Make new user home dir permissions configurable
* 3d6b82a Merge pull request #282 from wilson-lauw/mysql_fix
* 9cbb64a [metastore] Added assist to the partitions page
* 509876f [metastore] Parse Hive pseudo-json parameters
* 56a6926 [metastore] Display a pretty empty tables in the database page
* 3959a3b [metastore] Delete databases.mako and tables.mako
* 7926d99 [metastore] Knockoutify the remaining action URLs
* a3ea529 [metastore] Fix column comment and clear the column cache on change
* 619265e [metastore] Fix table comment and clear the table cache on change
* 3a9e550 [metastore] Properly style the partitions and samples tables
* 0950eae [metastore] Fix the view table button
* ae45292 [metastore] Fix drop table modal for the selected table
* 1dcec8e [metastore] Add spinners to tables and databases lists
* 1711fc3 added backticks to handle database name that use reserved keyword.
* 7427e55 [notebook] Allow snippet properties files and functions to be passed from notebook
* 921b3bd [notebook] Allow snippet properties settings to be passed as Hive/Impala configuration
* 35a9a80 [notebook] Rename has_more in multiqueries to has_more_statements
* 41bfbab [notebook] Add title to status column
* 1eaf402 [editor] Close past multi queries
* fc458ad [notebook] Add query status to the history
* bf174c4 [metastore] Fixing typo in the test URLs
* 904da7d [beeswax] Redact passwords from session properties
* 95727b9 [impala] Simplify Session get_properties method
* 20b8790 [impala] Fixes impala install examples when tables exist in HMS
* fb90f9d [beeswax] Get and save configuration values for beeswax sessions
* cd94b1b [core] Avoid augmenting Spnego user if user is None
* bcf7ce6 [desktop] New workflow from New document should go to new editor
* 5323d89 [metastore] Index redirects to the default database
* c0c8bc4 [metastore] Fix table samples tab
* de90643 [metastore] Added assist to import wizard pages
* 4478458 [metastore] Fix a bunch of tests after the ajax-ification of metastore
* 06ac3a5 [editor] Support re-executing from the first statement with multi queries
* 671c7bc [editor] Unify show history logic to only be shown on a new query
* 7ed88a1 [editor] Fetch next multi query when previous query was DDL
* 1260d57 [notebook] Improve logic to refresh assist on DDL statements
* 6730f26 [notebook] Support multi queries in the editor
* 18dd99c [metastore] Show the view more option only when there are actually more
* 9d32d24 [metastore] Proof of concept on how to fix the show tables tests
* a33903b [metastore] Display the partition preview only if the table is partitioned
* 1796867 [metastore] Plug the new browse data table
* 5fac852 [metastore] Remove unused column analysis popup
* d6d666e [metastore] Change the icons of the drop buttons and get rid of the view_or_table_noun
* f8191ba [metastore] Clear the table when navigating to the databases with the breadcrumbs
* 699677a [metastore] Added assist to the create table manually page
* 08a1954 [metastore] Fixed history back and forward and unified assist open item behavior
* ce82f94 [metastore] Add refresh icon on top of metastore page
* 9dbe56a [metastore] Refresh the metastore contents on assist.refresh
* f2901f2 [metastore] Remove debug link
* 644037a [metastore] Added database stats to the view
* 9f292be [metastore] Fix for drop table modal
* e4ea696 [assist] Publish refresh event instead of reload when clicking refresh
* b5899d0 [metastore] Knockoutify drop table modal
* b278488 [metastore] Wire in database stats call
* 3240e60 [metastore] Remove unused table comment variable
* 369ba8b [metastore] Changed import data icon
* 7a09c7e [metastore] Knockoutify table partitions
* b14084d [metastore] Ajaxify loading of the partitions
* 55934a7 [metastore] Fix stats refresh icon
* b92c213 [metastore] Knockoutify partition_keys in actions
* 943b870 [metastore] Started URL override
* 881e579 [metastore] Show a message when no tables or databases are found
* 2787166 [metastore] Fix table stats in tables list
* 31ca2a0 [metastore] Add shift-click support to tables and databases table
* 85333c3 [metastore] Knockoutify the database action
* e502dca [metastore] Knockoutify the table actions
* 5496259 [core] Add ko bindings for the Hue checkbox and the check all checkbox
* 3b7789f [metastore] Support for loading the correct view on page load and back button
* db0fc3e [metastore] Removed breadcrumb last '>' for tables/databases
* 46f7331 [metastore] Focus on the overview tab on setTable
* 5a957f8 [metastore] Added changeURL to HueUtils and enabled history pushState
* d507c87 [metastore] Knockoutify database search and style the database actions
* f112060 [metastore] Style the tables actions and increase the space between actions
* b028a52 [metastore] Knockoutify table search and add comment matching
* 0a5f961 [metastore] Fix I18n for tables and databases lists
* edcd445 [metastore] Set database and table from assist panel
* ad5bba9 [metastore] Combine tables list, databases lists and table details into one page
* b8b07d5 [notebook] Implement Save As functionality
* 6711099 [notebook] Put back the sessions button in editor or notebook mode
* 6a61942 [editor] Add proper links to New buttons in the editor
* d035eda [notebook] Reload history query on click and refreshes the page for now
* 21aeec1 [notebook] Always show play button in blue in Editor mode
* 60ad717 [home] Refactor tests to easily check for duplicate tag creation
* 4b26728 [notebook] Offer to view the data of a table and scroll
* ea52cea [assist] Add table and view facets to search
* d5d8553 [editor] Rename _n to notebook
* 5f9e9be [core] Indent and simplify checking logic of new tag creation
* abd18d8 [core] Prevent creating a project with an empty or already existing name
* db8057d [livy] Allow to configure the Total Executor Cores in standalone mode
* 8bef981 [oozie] Trim left slash in coordinator application URI of a bundle job
* 6335c5e [beeswax] Add error_handler to sample, indexes, and functions endpoints
* f7f0c3c [beeswax] Implement get_functions API endpoint
* 1dd5022 [oozie] Some job statuses are not included in the dashboard
* 4e8ddce [spark] Add Executors Memory when choosing a property during recreate session
* 80e1a51 [fb] Reset file name input before opening the create new file pop-up
* d8f3e5e [notebook] Remove all flag to enable the assist
* 80b9dde [notebook] Add a query expired message
* 1e0b0a3 [notebook] Restart polling for query status if snippet was in running state
* a6689c2 [notebook] Unify the icon bar with Editor
* 75b7b29 HUE-2949 [notebook] Fix HS2 progress API by sending back full logs with each request
* f5f6eb2 [beeswax] Add get_indexes API endpoint
* 03ca1fd [assist] Show a message when the filter results in no entries
* 6cf5960 [editor] Fix the "sticky" dark blue link color on some actions
* 21f205c [metastore] Restyle the upper right table actions
* bb174ba [notebook] Fix missing snippet header
* b4318b4 [editor] Allow selection from the history without replacing the current query
* 9754876 [beeswax] Fix ANALYZE TABLE call for partitioned tables and raise error on COMPUTE..FOR COLUMNS
* 8bc0076 HUE-2284 [impala] Provide Impala Thrift API implementation of GetRuntimeProfile
* 4616a74 [impala] get_exec_summary error handling for closed/invalid query handles
* 7494aa4 HUE-2284 [impala] Provide Impala Thrift API implementation of GetExecSummary
* 23fec5b [impala] Update sample data test to not have the DB prefix in the headers
* 49387ae [impala] Table samples should be queried with Impala
* fff59ed [metastore] Update the logic to be able to fetch more recent partitions
* f565baf [metastore] Change file location icon to disk
* fce33b3 [metastore] Improve UX of list of partition values on table page
* 63d3267 [hive] Escape column names to work with stats reading
* bde2f0b [hive] Unify the limit of listed partitions and the limit of partitions in SELECT queries
* 18d04f9 [oozie] Fix running a single workflow action for fork node
* e234252 [editor] Drop exact match for SQL autocomplete
* 7e7006f [editor] Show autocomplete after space
* 434781f [assist] Style the message for no tables or columns
* fc834ce [assist] Fix the background colour of the column terms count
* 0251fc6 [editor] Only pan the results grid when the alt-key is down
* b89222c [editor] Disable adding of a new snippet when double-clicking the empty header
* 70b51c0 [impala] Move get_sample logic back into HiveServer2Dbms
* bc58363 [desktop] Override default tmp directory with workspace directory to avoid space issues
* 03971ea Merge pull request #263 from shobull/master
* 07b78f6 Update rest.py - set default http header to accept "application/json"
* e7a390b [impala] Initial implementation of Impala Thrift service
* 796adb6 [assist] Add the table comment to the title of table entries
* 3776c76 [editor] Switch to table meta endpoint for sql autocomplete
* 631a681 [impala] Allow invalidate to accept optional database param to enable DB refresh
* 081258b [impala] Use beeswax API error_handler decorator for impala API methods
* 638b4d3 HUE-3078 [impala] Implement Impala Invalidate Metadata and Refresh
* 2a8b97c [oozie] Add test for Java action XML generation
* 7f65df2 [core] Add lxml 3.3
* d432b77 [core] Remove lxml 3.4
* cb51411 [hive] Remove list of table names in the autocomplete API
* d65a300 [editor] Always show the snippet actions in editor mode
* 11c6ffa [editor] Disable the execute button when the statement is empty instead of hiding it
* de34cef [assist] Don't wrap long column names to a new line after the icon
* 4833882 [assist] Preserve white space in table sample columns
* 107bb36 [assist] Set focus on search when opened and make search clearable
* 6f2e3fc [hive] Save one call to the metastore for the table autocomplete
* f6138e9 [hive] Fix create table with timestamp test to look to new sample data
* 71f3389 [useradmin] On batch LDAP user import, validate first_name and last_name, log warning and continue
* 92f3868 [assist] List columns of a view
* d6a1467 [hive] Fix escaping of table samples
* c90d0b0 [hive] Fix create table test to now look at json data for the samples
* 5b93b05 [metastore] Add spinner to samples and move loading into samples object
* d961b51 [metastore] Fix samples table for views and show a message when there's no data
* d21261c [metastore] Fix stats for views
* 823d0a6 [assist] Fix table sample for views
* 0d9544e [assist] Disable stat refresh for table views
* bc2be63 [editor] Fix infinite scroll for single editor mode
* 9c9aba7 [editor] Moved hueDebug to the require common file
* f6d024f [metastore] Added assist to create database
* cedf268 [assist] Fix column listing
* c6d9573 [assist] Rename "tables + views" to just "tables"
* 1d5c2bf [metastore] Convert the partition test to check on the partition page
* b1ed816 [notebook] Add a flag to show the latest editors
* 9f81d4c [metastore] Display partition values when available on table page
* b7ea99e [notebook] Add code formatting to the latest execute all snippets function
* 5c30497 [notebook] Add all snippets execute function
* 03d95bd [search] Unicode cast hueId field and fix search test
* 1cacfa8 [metastore] Add assist to the database and tables page
* 207b12b [assist] Differentiate tables and views
* b9babf4 [editor] Fix column scroller and column toggle for the results
* 0827a48 [editor] Fixed save URL, changed from hashtag to pushstate
* 31d4d25 [editor] Improved history UX
* 392f833 [core] Updated FontAwesome to 4.5
* 3aace14 [core] The DataTables sorting icons are now on the right of the field
* 9e294520 [editor] Delete references to CodeMirror
* 55ba440 [editor] Improved usability with mouse use of the results
* 0b69174 [editor] Fix for null selected database
* dde51db [core] AceEditor now updates the snippet statement on change
* b73bc43 [metastore] Open database from Assist
* e78c58d [assist] KO'ified the samples table
* ea38937 [core] Added tables meta to the Hive autocomplete
* ccc1f90 [search] Support fetching a document when searching by id
* 2fba6b4 [search] Flatten highlighting if there is only one chunk
* 3817a2c [desktop] Skeleton for the new home page
* dfc53f8 [notebook] Historify the snippet with the good query handle
* 35bd055 [impala] Restore TestImpalaDbms test class
* bd39fa8 [impala] Fix get sample test
* e89da22 [impala] Refactor Impala API and DBMS query server out of beeswax
* b991026 [metastore] Add some missed i18n in the ko templates
* 6fdb07d [search] Support bar widget on the time filter
* 762fcde [beeswax] Update tests for new get_sample_data API endpoint
* c012003 [metastore] Add separate get_sample_data API endpoint and fix metastore tests
* 040d730 [metastore] Better error handling for missed stats calls
* e0181b9 [core] Avoid RequireJS caching if django_debug_mode=true
* d0e6f7a [metastore] Fix table/column terms call
* 472dd3c [editor] Disable execute in case of empty statement
* 4f5ed9c [metastore] Remove unused imported config from metastore tests
* 8787f6e [metastore] Add more database metadata
* 0cc5a9af [hive] Update the create table test to check for the result json
* 0f4d582 [metastore] Remove the now non used static variables of the describe page
* e89caf5 [metastore] Revert to use GetSchemas() for the list of tables
* cc4f665 [notebook] Do not show history when empty
* e9314b6 [editor] Better history icon and empty history message
* f37d17d [notebook] Implement the clear history backend
* c7b651e [metastore] Extract database and table into separate objects
* aeb229d [metastore] Add arrow icon with event to database list in the assist
* 0dff589 [metastore] Use ko for the breadcrumb
* c1a27b9 [metastore] Set the active table from the assist panel
* 0657ce7 [assist] Improve display of stats popover
* 5402594 [editor] Put the id of the notebook in the URL when executing
* fd29185 [notebook] Have new snippets ask the assist for the selected database
* 977cf9f [assist] Make assist event names less ambiguous
* 663f8ab [metastore] Fixed column stats calls
* 50bc21b [metastore] Fix issue with load order for the ko.hue-bindings
* 94709d6 [assist] Fix the spinner for the table tree
* 2af89cb [editor] Change auto-resize of editor to add 4 new lines instead of 8
* ac280bf [core] Lighten up all the other apps to make it similar to the new editor
* 0d8ba1a [editor] Added clear history UI
* 31effa8 [metastore] Add refresh of stats to the table details
* bee3850 [metastore] Use ko for table details and stats
* ef27a54 [metastore] Re-organize the table stat panel
* 6492385 [notebook] Do not display history notebook in the top menu
* e66d18d [metastore] Add extra table fields to the json table call
* 0cae7af [useradmin] Permission to view the user profile of another user:
* e24794a [metastore] Use ko for table samples
* 301324c [assist] Support json and html response type when fetching table samples
* d933519 [metastore] Only return table sample when asked for it
* cc14254 [useradmin] Add a view user page
* a5fcf38 [metastore] Wired in queries tab
* 6908f0c [metastore] Fix the indentation of the decribe table view
* 9841a6b [metastore] Change starred columns title on overview
* d876999 [metastore] Get table properties date as json
* 5d5a2d2 [core] Use define instead of require for the assist panel and table stats
* c0fe773 [oozie] Improve email on error checkbox
* 793f35b [metastore] Offer the get sample API as json
* a29a54a [metastore] Add editable table description
* 3f08b74 [metastore] Add column counter
* 8ad3adc [metastore] Do not show comments in the partition table
* eb43a41 [metastore] Clear assist helper cache for columns when column comment is changed
* 2b4027c [metastore] Add links to view more tabs
* 3eea297 [metastore] Keep the table stats link blue
* e6352ce [metastore] Add favourite toggle to columns
* ba38a27 [metastore] Use in-place editing for column comments
* 1a1338b [metastore] Add all the query information to the table queries call
* 971514d [metastore] Fix alter table and column URL patterns and fix alter_column test
* 0ed77be [metastore] Added navigation settings to the assist and openItem functionality
* 3c49bda [notebook] Update Sample Notebook to use updated sample files
* 335af43 [beeswax] Add web_logs_partitioned sample
* 6447fdc [metastore] Provide the partition keys of a table in json
* eacdfb2 [metastore] Use the new table stats for the columns table
* 2edc865 [metastore] Use the viewmodel columns for the columns tab
* 85aaa6b [metastore] Use knockout for columns
* 20759b1 HUE-3073 [metastore] Add ability to alter table name and comment
* d2974f2 [metastore] Add json options to the get table partition ajax call
* b33a3eb [metastore] Support for assist selected CSS class
* 3957227 [metastore] Updated UI of the tiles
* 6eb3945 [metastore] Remove old assist.js
* 228e774 [metastore] Set the comment of a column to a new value
* b1528b5 [metastore] Switch alter column API to get column name from POST data
* 3812d3b [assist] Fix table preview for Hive
* 62be029 [beeswax] Use the new assist events for db initialization
* 77daaf0 [assist] Fix caching of selected source and database
* db46cf8 [metastore] Add empty sections for the non available yet tabs
* bb6a8de [core] Remove some non needed files from the root
* 1bee0a3 HUE-1961 [metastore] Add ability to alter column name, type, comment
* 4787ec8 [filebrowser] Switch to else instead of return in xxd test
* 24bfed2 [filebrowser] Update xxd_test to not fail for different offset lengths
* b35b71a [metastore] Updated assist panel to use the new ko component
* 175e8fd [editor] Include source type in calls to API from table stats
* ff40081 [metastore] Put back breadcrumbs with icon
* c6e0822 [editor] Adjust autocomplete to use new assist helper
* 85435c1 [assist] Use pubsub for communication between assist panel and the notebook
* 573b2d3 [assist] Remove assist dependency on notebook and snippets
* 9690149 [metastore] Adding a related queries tab on table page
* 26e2d71 [metastore] Updated look and feel of the overview page
* 08acab4 [metastore] Moved icons to top right
* 0f552be [editor] Lightened up the main workspace
* b134348 [metastore] Updated style of the basic page structure
* 17845d6 [metastore] Added assist panel
* 580d33e [editor] Fix assist loading rendering of tables and spinner
* 76fdf1d [metastore] Add a permission tab
* cb65651 [metastore] Display a preview of the table partitions
* 8967eb4 [metastore] Display more table metadata on the table page
* 8d7df07 [metastore] skeleton of the revamp of the table page
* 7ae135e [editor] Fixed display of success, loading and 0 results messages
* 7a290ed [assist] Close table stats when clicking outside the popover
* 0014b99 [assist] Extract table stats to separate component
* 81a15c3 [editor] Fixed history bug for older editors
* e054e92 [assist] Refresh assist entries on 'assist.refresh' event
* 464248c [assist] Add reload function to databases and tables list
* 9ee775f [editor] Wire up the history fetching in the UI
* 6750d63 [hive] Fix computation of table statistics button
* f6bac4b [assist] Style the assist breadcrumb
* f91b3c6 [assist] Use breadcrumb for source and database selection
* 2bce5d1 [assist] Extract databases and sources into separate ko templates
* 6028206 [assist] Extract assist panel into separate mako file
* 7eaa3f0 [assist] Pass i18n strings to js modules where needed
* e7caed6 [assist] Extract assist modules into desktop/js/assist
* 186dcdd [notebook] Add MySql autocomplete
* 8f381b0 [notebook] Add select operation to the mysql connector
* b26de13 [jobsub] Fix cloning a design
* 63396db [editor] Connect editor type with the right name
* eb22d45 [beeswax] Make history test pass when running everything
* b2e7c04 [editor] Publish assist refresh event in case of a SQL ALTER, DROP or CREATE
* 452ce9c HUE-3054 [useradmin] Raise a popup notification if any exceptions were encountered on batch LDAP import/sync
* 10496e3 [jobsub] Clarify that action properties are for Hadoop only
* 2a3e711 [core] Updated and merged Ace Editor 1.2.2
* 808cf4b [editor] Make the editor gutter width smaller
* 860ed80 HUE-2734 [oozie] Refresh arrows of decision nodes
* b79c254 [editor] Fix size and blinking of the player button
* 54aae7a [editor] Support for SQL file drop
* 4933a9b [editor] Provide more information in the history
* 78c657d [editor] Expand * to all table columns with alt/ctrl+click
* 0ea3995 [editor] Autoresize the editor in increments of 8 lines if not manually resized
* 7afde03 [editor] Make the code editor resizable
* 9c3e818 [notebook] Open queries directly from the notebook page
* 0c22de3 [notebook] Add a notebook and editor type
* 5d9ec3b [editor] Add links to the new editors
* 35ef96a [editor] Add link to new Hive editor
* c127eb3 [notebook] Do not display the history documents
* a206abf [notebook] Add history to single snippet mode
* 062a46f [editor] Better progress bar colors
* e3eff3b [editor] Restore notebook open call
* ab7d2c5 [editor] Avoid result scrolling on single snippet editor
* 1159515 [editor] Fixed saving messages for the query editor
* 8034137 [editor] Switched top bar for single snippet mode
* 93980a6 [editor] Set min height of code editor to 8 lines
* 0413a95 [editor] Fix the save url parameter for the editor
* efd310f [notebook] Drop the code visibility toggle
* 64fc1b5 [editor] Remove name header and other snippet controls
* 8fdf151 [editor] Add line numbers to the code editor
* ae09fb5 [notebook] Add horizontal separator between snippets
* 1e6ce51 [notebook] Change default name of untitled snippet to "My Snippet"
* de9afbe [editor] Fix issue with editable placeholder
* a0d5f81 [beeswax] Improve UX of clear query history
* 74fa6f8 [hive] Display each history row on one line
* 1900f46 [core] Add the "USE" keyword to the Hive highlight rules for the Ace editor
* de708b8 [core] Add HDFS autocomplete to Impala statements
* 04d9412 [beeswax] Add test to check for recent query history cleaning
* 2cc394e HUE-2963 [beeswax] Allow the user to be able to clear the recent queries table
* 628bec1 HUE-3063 [pig] Fix for syntax highlight mistake around /* */
* b82bb84 [tools] Fixed Dockerfile for Hue and added VOLUME declaration
* 3eb0f03 [core] Add HDFS autocomplete to Hive statements
* 60fe180 [notebook] Move focus to the ace editor after switching snippet type
* 5038f88 [core] Only include "[]" when inserting complex types from the assist panel for Hive
* 1682087 HUE-1959 [core] Include database references in SQL autocomplete suggestions
* 83fa44b [core] Adjust autocomplete tests to also check for the correct order of the suggestions
* 3fb1e70 [core] Autocomplete databases after the USE keyword
* b884fc1 [core] Make the SQL autocompleter aware of any USE statements before the cursor
* 9bc3653 [hadoop] Support HA for checkconfig YARN check
* 00005d6 HUE-3056 [core] Refactor audit logging to enable each view action to specify log parameters
* 3618f09 HUE-3049 [useradmin] Change errors in validation functions from AssertionError to ValidationError
* a15ed00 [tools] Update Docker instuction to for getting the correct IP
* ef9a53a [beeswax] Double click on Assist with an empty editor creates an automagic SELECT LIMIT
* cfdbebd [core] Fix default values for SAML user_attribute_mapping
* ab5a684 [tools] Fixed Livy Dockerfile
* 28fe0e7 [beeswax] Browse Data and all other calls to select_star should use optimized partition query
* 1915841 [tools] Added Dockerfile for Livy
* a029f36 [notebook][beeswax] Add table counter to the assist
* ad1a2d5 [livy] Add documentation on building Livy with other Spark versions
* beac43b [livy] Remove reference to non-existing config option
* e0f40d6 [livy] Stop printing out the repl output
* 5c2ba1f HUE-3025 and HUE-3055 [livy] Support Spark 1.4, and fix pyFiles support
* 58b1249 [livy] Fix warnings in fake_shell.py
* a494127 [livy] Fix %table-izing dictionaries
* a373086 [livy] Fix some minor warnings
* d174121 [livy] Cleanup imports
* 30986a7 [livy] Update README to describe spark config
* e56e54e [livy] bin/livy-repl should try to use the SPARK_HOME spark-submit
* 3228645 [beeswax] Set HS2 logging to verbose to get job info
* 153824e [notebook] Move snippet type switch to left bar
* c3b4d2c [notebook] Extend click-to-focus area of a snippet
* 169bcf3 HUE-2496 [fb] Move the content summary button to the action/context menu
* 3e88c88 [notebook] Remove result headers on widget type switch
* d77bac9 [tools] Extended description for the Docker readme
* 63390d9 [hadoop] Make YARN HA config easier to configure
* d277357 [core] Fix jHueNotify positioning after page scroll
* f9e1938 HUE-2996 [oozie] Prettify submission history on workflow
* c6bda77 [notebook] Don't automatically add a new snippet after execution of SQL type snippets
* 99f24ef [core] Automatically open map values and array items in the assist panel
* 069f156 [notebook] Keep execution controls greyed when active
* 68d9818 [livy] Allow the server url to be manually specified
* 7289799 [livy] Fix LIVY_REPL_JAVA_OPTS for yarn mode
* af01a43 HUE-3046 [livy] Pass the callback url and port through a config variable
* 6849e71 [core] Add auth and ldap configs and default values to ini templates
* 2dc79c5 [beeswax] Pass in tableTypes to GetTables HS2 call
* 4b23fc6 HUE-3036 [beeswax] Revert get_tables to use Thrift API GetTables
* fab0407 [core] Only audit valid/successful or unauthorized operations.
* 75beea7 [oozie] Offer action retry on all the actions
* d03a532 [core] Add nt_domain configuration to ini templates
* a564683 [oozie] Fix creating a new workflow where we used to look for a document
* 6c32b5a HUE-2997 [oozie] Easier usage of email action when workflow fails
* af4d6be [oozie] Fix dashboard display of a workflow having a killed node
* b99c29e [oozie] Provide the cause of the submission error to the user
* 53b723b [tools] Fix syntax with latest rbt tool for specifying the bug to close
* 37df771 HUE-3024 [oozie] Add Generic action to the workflow editor
* d8d8e3b HUE-2496 [fb] Show content summary in the UI
* de7a034 HUE-2496 [fb] API to fetch the content summary of a path
* aef2fea HUE-2996 [oozie] Add back editor submission history
* b8ab65d [libsaml] Add support for an explicit saml response base url
* db95f49 [core] Initial support for Docker
* 3735c2c [oozie] Support shift-click for selecting multiple table items
* 996ee53 [aws] Add internationalization files
* f73e743 [notebook] Fix log panel margin and place it between the code and results
* 74d6ee7 [notebook] Fix snippet code visibility toggle
* c09ac96 [notebook] Increase left and right margins for progress and errors
* a6860d5 [notebook] Fix issue with bar chart label positioning
* 1706959 [notebook] Increase the right margin of the snippets
* eca56ff [notebook] Move result related actions to the left of the results panel
* 5832cd1 [notebook] Fix issue with charts filling the page right after notebook load
* ed1abea [notebook] Extract templates for chart and graph results
* d257e39 [notebook] Move execution timer to upper right corner
* 81f1c2e [notebook] Move snippet execution controls to the left of the snippet contents
* 8c39c41 [notebook] Extract templates for snippet execution and result controls
* bbaec8d [useradmin] Fix typo
* c74f64f [useradmin] LDAP group sync: Do not fail when members exist outside of current domain
* 63c0550 [beeswax] Increase wait-time for create/insert partition table
* a4659f3 HUE-3018 [livy] Add support for whitelisting spark config options
* 08786ef [livy] Convert some builder options to generate the spark.* options
* 7e1d990 [livy] Move SparkProcess* into livy-spark
* 875c604 [livy] Minor cleanup
* e091dfb [livy] Create a SparkManager
* 04b9051 [livy] Move SessionManager into livy-core
* 539d0ad [livy] Create a SparkProcessBuilderFactory
* 606aef9 [livy] Convert construtors into "apply" methods
* 7584785 [livy] Rename SparkSubmitProcessBuilder to SparkProcessBuilder
* 65b3acb [livy] Move spark classes out of livy-server into livy-spark
* 967a0a1 [beeswax] Allow create table queries in tests to finish
* 82f145a [core] Added 'done' button to the admin wizard
* 12fd5a7 [beeswax][impala] Disable DataTable plugin for modal samples of tables with more than 1000 columns
* 3e30843 [metastore] Disable DataTable plugin for tables with more than 1000 columns
* 65cda65 [metastore] Support displaying table with 10000 columns
* cfc6d16 [impala] Add an idle session configurable timeout
* 77b84c1 [hive] Close previous query when doing multi-query
* 67c7233 [hbase] Add a config check for missing Thrift server or misconfiguration
* ad44fb8 [core] Pad dropped assist text with spaces if it's dropped in or next to a word
* 2877875 [oozie] Load the ko.hue-bindings from the main pages
* 7e1a6ad [notebook] Fix snippet settings positioning
* 410a570 [beeswax] Add codemirror support for DnD from assist panel
* a54655e [notebook] Support dragging of items from assist panel to the editors
* dd07155 [notebook] Fix result table header offset issue
* 6835235 [notebook] Move snippet result download functionality to a separate component
* 1d72300 [notebook] Move jupyter export into notebook view model
* 113ec3c [livy] Fix compiling the livy-core-test module
* 4eea639 [livy] Move SessionFactory into livy-core
* 2f06395 [livy] Move {,Batch,Interactive}Session into livy-core
* a7f35e9 [livy] Move livy-yarn Job and ApplicationState into their own files
* 38eb953 [livy] Move session state variants into it's own namespace
* 4bd9193 [livy] Import cleanup
* 58e4379 [livy] Rename package from the old "batches" name to "batch"
* 0fbc0c6 [livy] Optimize the livy-server maven dependencies
* e2fd5f6 [livy] Optimize the livy-yarn maven dependencies
* 3ef94d0 [livy] Optimize the livy-repl maven dependencies
* ea11bff [livy] Optimize the livy-core maven dependencies
* 74e531a [livy] Stop shading all of the modules
* 46d8c3a [livy] Make sure jetty jars end up in the archive
* e352575 [livy] Cleanup of maven and bump some versions
* 3b76bb4 [livy] Fix indentation
* fae3037 [livy] Support Spark 1.5.1
* fd50893 [livy] Set scala.compat.version
* 787c328 HUE-3035 [beeswax] Optimize sample data query for partitioned tables
* abb8105 HUE-2974 [oozie] Submit single action from Workflow editor
* dd49485 [search] Align correctly text facet counters in right to left languages
* c9145cd [libsolr] Force non UTF-8 encoding error when clicking on text facet
* 672da83 [search] Fix problem with removing filter
* 760e6f2 [notebook] Show actions when snippet is in focus
* bc6db6c [notebook] Switch to JS for toggling visibility of actions on hover
* 94a52e2 [notebook] Fix CSV/XLS download of results
* 1071cfc [notebook] Decrease the space between editor and results
* 9a7b0d0 [notebook] Fix JS error on Boostrap modal for Import Github
* 4cebad9 [spark] Support adding files on batch jar
* 488f83c [beeswax] Recreate customers parquet data table for compatibility
* 01926a2 HUE-3039 [livy] Enable support for SSL
* 41bed0b [livy] Add option for configuring the scalatra environment
* 5d9be7b [core] Updated README format
* 6ad46ba [notebook] Initial support for export to Jupyter and icon regrouping
* 9dac1aa [notebook] Added markdown to base connectors
* f3adbb7 [core] Fix assist table data sample preview
* 930713c [livy] Add HADOOP_CONF_DIR in the README
* 6ea0094 [notebook] Support for switching snippet type with %type on the first line
* 72fa7d8 [notebook] Support a default list of snippets
* d2fa51f [oozie] Add more logging when job submissions fail
* 74559e2 [notebook] Show snippet title on hover
* bee6a98 [notebook] Prevent flickering of snippet logs and status for slow browsers
* 2cd9e99 [notebook] Fix loading order problems with ko Charts
* df179dc [notebook] Load asyncronously MathJax
* da135b7 [core] Support sql autocomplete after "group by"
* 7b22eed [core] Fix pre-selection issue with the select2 binding
* 64d5baa [core] Support value sample autocomplete for nested structs in complex types
* 4934f17 [notebook] Don't auto-trigger hdfs autocomplete for URIs with schema references
* 6e7f8dc [notebook] Show snippet header on hover
* 2610f19 [notebook] Show the header row for text snippets outside edit mode
* 735782f HUE-3033 [impala] Editor doesn't support "Big Query in HDFS" option
* 6d81dc9 [notebook] Fix regex for github owner pattern
* 2e9ec74 [notebook] Github config i18n of help text
* aa6f988 [core] Move default configurations for github to notebook top-level
* 0e85236 [notebook] Avoid extra new lines on external notebooks import
* 2c18d0c [notebook] Include Github oAuth flow in the UI
* 7009b3e [notebook] Add ability to authorize Github and provide authenticated access
* d35f6c8 [notebook] Update github_fetch handling and GithubClient
* 9579247 [notebook] Plugged in Github import in the UI
* 98784ed [notebook] Provides a Github API client to fetch file contents for file in a public Github repo
* 15a25d9 [notebook] Fix problem with the Ace editor autofocus
* bea01b0 [notebook] Only initialize databases for sql type snippets
* d2ad0c3 [beeswax] Improve save form error handling
* 1fcf7b1 [core] Collapse JB, FB and other right menu items under 1290 pixels
* c6a926e [core] Fix table and column stats in the assist panel
* 66302ac [spark] Add documentation for setting the application name
* 845b037 [livy] Support for setting the application name
* 97eea30 [spark] Document how to specify a queue in YARN mode
* ad171f1 [oozie] Bump the workflow sumbit timeout in the tests
* 7bab221 [impala] Move specific nested column logic to impala lib
* d7ecb07 [core] Autocomplete values in Impala statement conditions
* 0fb5dbf HUE-2958 [impala] Autocomplete sample of values for scalar columns and nested types
* 77316d8 HUE-2969 [oozie] Support shared workflows in coordinator
* c715feb HUE-2527 [beeswax] Allow 5000 columns in XLS downloads
* f846f0d HUE-3026 [beeswax] Backend should pass save form errors to frontend
* fbb2dff [metastore] Fix metastore tests by removing test_drop_partition side-effects
* d4554fb [useradmin] Raise popup errors and log warnings on RuntimeErrors when importing/syncing LDAP users
* 5bb94b5 HUE-2978 [metastore] Improved UX of deleting partitions
* c82424e HUE-2978: [metastore] Offer to delete partitions
* 77d8948 [oozie] Big workflow dashboards should scroll
* 39b66d4 [hbase] Truncate HBase API exceptions in popup up to first newline.
* e36e296 [metastore] Alert user in case of error
* 8ef2a61 [useradmin] Validate usernames on LDAP sync and log warning on errors
* 78a513c [search] Only set record row details and links one time
* 8b42920 HUE-2523 [hive] Convert xls download test to the new generator
* 7d7db31 HUE-2523 [core] Bump lxml 3.4
* 76c4303 HUE-2523 [core] Convert XLS export tests to XLSX
* 1c523ae HUE-2523 [core] Migrate tests to read back generated xlsx
* e49ae13 HUE-2523 [core] Add jdcal in ex-py for pyopenxsl
* 817f25c HUE-2523 [core] Convert XLS export to pyopenxls
* dff3a73 HUE-2523 [core] Remove lxml from ext-py
* ff69eb2 HUE-2523 [core] Add openpyxl to ext-py
* 09f20df HUE-2523 [core] Convert tests to the new generator
* 65b4918 HUE-2523 [core] Migrate Excel generator to XlsxWriter
* 8e1f685 HUE-2523 [core] Remove tablib XLS packages
* 73e2bc7 HUE-2523 [core] Remove xlwt and xlwt3 utils from tablib
* 7a8b685 [oozie] Fix for broken submit workflow
* 8a0499f HUE-3023 [aws] Perform check config only if configured
* 4f5ca16 [metastore] Allow creating a Hive tables with spaces in the data location
* d511de4 [search] Do no HTML escape rows when downloading them
* 1af9afd [aws] Skip failing tests for now
* 9fe3054 [hadoop] Implement missing isroot method into WebHdfs
* aa9bcda [aws] Disable AWS filesytem until completed
* 06847d3 HUE-2915 [fb] FS util function path seems to not exist
* 2cfbef7 HUE-2930 [aws] Add configuration in the hue.inis
* bff291a HUE-2925 [fb] Allow to use absolute URI
* 77115d3 HUE-2930 [core] Add S3 filesystem
* 7dce32a HUE-2924 [core] Implement proxy filesystem
* 69933a5 [desktop] Display document api errors
* e0b7d53 [desktop] Switch api to using request_{GET,POST} to return 405 errors
* 660000a [libsaml] Make sure that SAML_USE_NAME_ID_AS_USERNAME is defined
* 8df53a9 [core] Promoted notebook to the first level menu
* 173c090 HUE-3014 [oozie] Show better error message when user enters custom cron syntax for coordinator dataset
* 419e1d9 [notebook] Double click on a snippet name adds a new snippet before it
* 4e59657 [notebook] Expand click-to-focus area for the editors
* 0af474b [desktop] Add environment variable to ignore password script errors
* 5c55a86 [desktop] Allow secret key to be passed in an environment variable
* 1f615b1 [notebook][search] Support for fullscreen mode
* aab72a8 [libsolr] Add a config flag for setting CA authority checking
* df2c2e6 [indexer] Improve parsing of binary or non unicode data
* 9b9047e [spark] Add SNAPSHOT to Livy makefile
* b95ed4a [livy] Fix compiling livy by correcting some version numbers
* bf916ad [indexer] Reload the page when deleting all the collections
* 4668121 [beeswax] Raise an error if Beeswax app tests fails to authenticate
* 423146f [sqoop] Raise an error if Sqoop app tests fails to authenticate
* 008bf6f [impala] Check if creating the impala test databases had failed
* 8f26cab [libsaml] Fix using saml name id as a username
* a5b3453 [libsaml] Make sure saml replies go through the load balancer
* 410d9e1 HUE-3017 [oozie] Coordinator dashboard does not show jobs with certain statuses
* a546226 [notebook] Improved move widget UX
* c7fe666 [desktop] Improve the error message if api requests are malformed
* 45287b5 [desktop] Only allow owners to change document permissions
* 0cd37d7 [livy] Fix executing '%' in pyspark
* 60298be [notebook] Support different type of cells on d'n'd iPython import
* 0cc16c1 [notebook] Fix HdfsAutocompleter issue
* 877de7d [beeswax][notebook] Scroll to error messages in long editors
* a3ffb25 HUE-2745 Adding py4j package
* 3a8bcf5 [notebook] Cache the HDFS autocomplete data
* 22296be [notebook] Trigger autocomplete after '/'
* fe0b968 [core] Fix assist panel caching
* 834200e [tools] Make less command compatible with Ubuntu
* 8fd9aab [tools] Make ace commands compatible for Ubuntu
* 88284cb [notebook] Unified result messages
* c15bb93 [core] Added 'make theme' target to the Makefile
* 2e0ca55 [core] Added 'make ace' target to the Makefile
* 0e15a17 [desktop] Support environment variable Database/LDAP/SMTP/SSL passwords
* df932c6 [core] Added SSL Certificate Chain support to CherryPy
* e49c301 HUE-3012 [beeswax] Remove inline error messages on Explain query
* 353b75b HUE-3004 [oozie] Some fields in the Coordinator are editable even before pressing Edit
* 21e5eb6 [core] Audit DELETE_USER operations in process_view before we delete the actual user records
* a106b9e [notebook] Exported ko to window.hueDebug
* a138f68 [notebook] Support for dropping older iPython files
* 1370f7b [core] Fix issue with missing preselected database in the assist panel
* 930e70d [notebook] Add HDFS autocomplete
* feaba62 [core] Extract dedicated SQL autocompleter
* ff82088 [core] Fix the autocompleter jasmine tests
* 2862744 [notebook] Turn the autocompleter into a module
* 61b0989 [notebook] Extract require configuration to separate file
* 11af74f [notebook] Exported the viewModel to window.hueDebug
* 326f832 [core] Improved jHueNotify margin and enforced max height
* 7feb6c0 [core] Improve jHueNotify look and fix for multiple error messages
* f5b623c [notebook] Improve Ace editor border marking
* e60e2ae [notebook] Avoid top bar blinking on notebook load
* 35d6eb7 [livy] Downgrade the version to 0.2.0
* 9602f2b [core] Reorganized .gitignore files and added a global java-lib exclusion
* 577a0b6 [hue] Fix parsing classes in pyspark
* 7ff98fa [search] Remove duplicated autocomplete code
* 3f15d43 [notebook] Restyled JDBC login form
* 2db8a2c [notebook] Avoid deprecation warning about BaseException.message
* 9a418f9 [notebook] Add note about adding jdbc connector jars on the CLASSPATH
* 49a29dc [notebook] Automatically start the DBProxy server if we have some JDBC snippets
* 9dfcf64 [dbms] Add bin and hue command to start DBProxy
* d3f2728 [dmbs] Little tweaks in the Makefile
* 31a626f HUE-2745 [dbms] Add licenses and basi makefile
* f620d0f HUE-2745 [dbms] Add initial DBProxy app
* f66e3f9 [notebook] Load the databases when switching snippet type
* cfad3a0 [notebook] Extract markdown to a separate snippet type
* cebf7fe [notebook] Fix markdown editor issue
* 1d1cf67 [notebook] Turn all knockout dependencies into modules
* 29d8ba9 [notebook] Initial modularization of the view model
* c5bdfea [notebook] Introduce RequireJS
* 998bf3f [core] Add RequireJS 2.1.20
* 0ac1190 Merge pull request #245 from hdinsight/master
* 5f8b24c HUE-1910 [oozie] Set default TZ to browser TZ
* 46feb96 HUE-1910 [oozie] Added Moment.js timezone and tzdetect
* db3f15d HUE-1910 [oozie] Support oozie.processing.timezone
* 462e03b Add file separator for accessing yarn-site.xml.
* 27f6589 [notebook] Save the last used assist panel source in total storage
* 9ec3caa [dbms] Rename JDBC 403 to 401 Unauthorized
* 0850ec4 [core] Assist should prompt for connection credetendials if there is no session
* 45210f9 [notebook] Friendler error message when not jdbc session and using the autocomplete
* c31c1e8 [notebook] Retry creating session if it failed at early stage before
* dec0e51 [livy] Put quotes around the the 'spark-submit' arguments
* bb53653 Merge pull request #241 from szczeles/queue_support_in_livy
* a937ec4 HUE-2749 [hive] Failure to authenticate to HS2 or Impala using LDAP seems silent
* a9f4b2f [core] Add descriptive operationText to the audit log for user/group admin operations
* e1b2eca [indexer] Drops non unicode chars when indexing data
* 66ef9e3 [search] Backend for autocomplete with Solr suggest
* d93903f [search] Integrate Solr suggest in the UI
* 97e99fe [hive] Do not log the secret of the HiveServer2 session
* 21646ba [notebook] Cache the JDBC connection by snippet type and user
* df8d45a HUE-2760 [notebook] Show job links on the logs panel
* db10530 [filebrowser] Hide file upload list on modal dialog hide event
* f6d43b2 [notebook] Fix issue with pre-selected assist database
* 5a78365 [core] Fix never-ending spinner issue when reloading the assist panel
* 8006b6f [core] Add getAddressFromCoordinates to the HueGeo lib
* 7fc1bb4 [beeswax] Stop logging the beeswax thrift session id
* f97e7bc [impala] Raise impala query timeout for live cluster testing
* f42496f [beeswax] Switch to new assist panel and helper
* 2c9f922 [notebook] Save the active databases with the notebook
* 06d2c68 [core] Keep track of databases in assist helper
* 31734d2 [notebook] Support multiple sources in the assist panel
* c42d7b3 [core] Migrate assist helper to new notebook API
* a4deeae [livy] Time out sessions and batches that have been done for a while
* 54f1f2c [oozie] Fix python syntax in the forms
* e3b8418 Support for queues in Livy
* b0ccdf4 [beeswax] Fix missing sqlDialect error
* d503918 [notebook] Remove import dependency on Oozie
* 60b8218 [notebook] Remove import dependencies on Spark
* dfc9552 [oozie] Display the Job XML property in the editor
* e87972c [oozie] Generate prepares XML instruction in the Streaming action
* 64da5fc [dbms] Support asking for JDBC credentials
* a0a1055 HUE-2770 [oozie] Hide Oozie specific workflow properties
* c80c71b HUE-2760 [spark] Add links to Spark UI and jobs
* a757e21 [oozie] Changed label on coordinator warning column
* 4c3b9ff [notebook] Fixed results height and reduced default size of Ace editor
* b36e739 HUE-3002 [oozie] Very difficult to remove an action's properties
* f6bf862 [search] Avoid jumpiness after edit collection link
* 1684e85 [notebook] Support execution of selected statements
* 749c16e [notebook] Cleanup the ace editor binding
* 40be220 [notebook] Only HTML escape table data
* d468614 [core] Remove statusCode from audit log
* 8648a05 HUE-3003 [search] Allow linking to a collection with a predefine query string
* 8256b02 [notebook] Hide drop file message if the drag event doesn't have one or more files attached to it
* ad86dc6 [notebook] Only show autocomplete spinner when calling the API
* b4194e5 [notebook] Set correct ace mode for mysql and pgsql snippets
* 60be109 [beeswax] Fix autocomplete for hive and impala query editors
* 3a2414a [notebook] Extend browser support for CSS transitions
* 72cc77d [notebook] Don't rotate the magic snippet wheel
* 7b930d9 [notebook] Add autocompleter to the ignored serializable objects
* d862538 [notebook] Fix dictionary comprehension for Python 2.6 compatibility
* 5454cde [core] Fix README formatting of openssl MacOS instructions
* 041a39e [core] Update README with Mac OS X openssl lib instructions
* 962a334 [notebook] Maintain underlying jobs list executed by the snippet
* cc4ee17 [tools] Add a note about building ace
* 42ab1ed [notebook] Add sql dialect flag for snippets in the snippet view settings
* 127332c [notebook] Improved multi-snippet autocomplete
* 246c7f4 [core] Add support for session autocompleters to Ace
* 9cc44cd [notebook] Support autocomplete for any SQL dialect
* b50abe8 [notebook] Support new autocomplete API
* 9eda820 [notebook] Add an example of jdbc snippet in the ini
* 1fc39a6 [libdbms] Support JDBC statements without any result set
* 72ff279 [notebook] Add autocomplete for JDBC interface
* 851729a [notebook] Add title to help notice the scrollable columns in the result
* ce43d37 [notebook] Core of the autocomplete API
* ecb2c62 [notebook] Assist dbl click should only add to the last active snippet and not all of them
* 3659c1f [notebook] Use the assistHelper from the binding params of the ace editor binding
* a87f23a [notebook] Make progress and jobs methods public
* b011d14 HUE-2998 [core] Top half of right-aligned dashboard icons not clickable
* ce499b6 [notebook] Highlight the editor on hover
* c6f27ed [oozie] Made explicit that you can zoom in a widget and smarter inputs
* 55d2fef [core] In audit logging, set allowed value to False for invalid login attempts.
* 5c95af1 [desktop] Fix typo that broke ldap authentication
* 515beb7 [notebook] Delay scrolling for the ace editor and the results
* 725cd3b [core] Add ko binding that delays overflow
* 45272c3 [core] Add support for hidden overflow to the Ace editor
* ed534ab [notebook] Add margin to snippets for easier page scrolling
* 4690a49 [librdbms] Add a default failover to string when decoding rows
* a0e0549 [notebook] Escape rows properly for HTML and NULL values
* a9476f6 [notebook] Added gradient map scope
* da8f17b Merge pull request #239 from yoer/master
* e152be9 [search] Add a MockResource.invoke and head method
* 3dd6276 HUE-2995 [libsolr] Fix uploading large bodies to Solr with Kerberos
* 388cac9 [beeswax] Fix test to work with kerberized Impala
* f8bc1be [search] Fix the bug on World maps introduced by the Europe topology
* 3fb1c29 [search] Added Europe to the geography types
* 44ced10 append the 'csrf_token' token to calculator app
* 145bcf2 [notebook] Set SQL as the default type of highlighting
* 678a965 [core] Fix whitespace issues with autocomplete
* bd483e6 [search] Added maps of Brazil, Canada, India, UK, Italy, France, Germany, Japan and Australia
* 95ee5eb [notebook] Maintain order in snippet wheel when adding snippets from history
* 4214099 [notebook] Only enable snippet modal when there are more than 5 types of snippets
* c7f6d14 [notebook] Set scala highligthing for spark snippets
* 75d540f [core] Sync the hue.ini templates
* d44466e [spark] Add an option for configuring Spark SQL
* 972fc7c [core] Re-order configuration sections with most common up
* f842b96 [notebook] Add connection configuration options for JDBC
* 382ef4b [librdbms] Convert JDBC interface to basic DB 2.0
* 9a7f969 [core] Remove PyYAML from ext-lib
* dcfa65e [notebook] Fix JDBC result display
* 5a537db [librdbms] Basic implementation of JDBC api
* a460409 [notebook] Support of Pig properties
* 12b7c1d HUE-2987 [oozie] Fix sync workflow to update Coordinator definition
* c6f3f07 [impala] 'sample' field was renamed to 'sample_rows'
* 35b8c5a [core] Keep the order when reading from the config file
* 993d7c1 [core] Add Python 2.4 backport of ordered dict for listing snippets in order
* 6541c1c [notebook] Add dedicated show modal button to the snippet selection wheel
* 7cde058 [core] Add support for fadeOut and speed to the fadeVisible ko binding
* 0fccd1c [notebook] Move radial menu ko binding to dedicated component for adding snippets
* 1b30217 [notebook] Improved add snippet wheel
* a24e154 [notebook] Support two lines in magic wheel alternatives
* b003380 [core] Allow undefined to be published with huePubSub
* 9d28080 [notebook] Consolidate view-related snippet settings and add missing icons
* 694f2cb [search] Added China to the gradient map scope
* 0a0241f [core] Added TopoJSON geometries for the rest of the world
* d0d59d0 [search] Improve UX of the 'search when i move the map' checkbox in small maps
* 4bc5133 [notebook] Add a Pig snippet
* 448a9f8 [core] Fix CTRL + Click on AceEditor for HDFS links
* 286bd65 [pig] Remove escaped HTML tags from submission confirmation popup
* 9cd9d59 [livy] Add support for the %json magic for PySpark
* 5b644f0 HUE-2976 [desktop] Don't set the kinit renewal lifetime
* 07bdce7 [spark] Remove thread mode from the configuration
* f25fbd9 [metastore] Avoid using tinyints when guessing the type of columns
* b0eab90 [spark] Support listing tables
* 1aa9cae [hive] Support fetching table list from various SQL servers
* 1a49dfe [notebook] Show fetch log errors in the log instead of query error
* a876063 [hive] Stay backward compatible with older versions
* 1920319 HUE-2984 [core] Warn about SQLite DB when more than a few users exist
* 20b8e46 [desktop] Add a login_splash_html configuration option for custom login messages
* cbe84c7 [notebook] Set correct ace mode for new snippets
* 4b960e1 [oozie] Revert some imports moved in HUE-2982
* 51be075 [notebook] Add a R snippet example with plotting
* 7c9a069 [notebook] Fix the install of the example Notebook
* 7061d2e [notebook] Update list of available snippets in ini
* 8c2fcfe [spark] Update doc about creating a sessions
* 2a3aab5 HUE-2982 [oozie] Fix sync workflow button error in Coordinator page
* aeb1d88 [core] Moved MR and YARN cluster HA decorators to desktop hadoop lib so that they can be reused
* ca58ba7 [livy] Skip sparkR tests if sparkR executable is not present
* 1e0d339 [notebook] Added online MathJax support for Markdown
* 5732181 [beeswax] Do not use an iterator for the sample data
* 029aac8 [oozie] Make oozie test re-entrant on Oracle DB
* 6ffc86c [oozie] Resize coordinator tabs to fit window height
* f7a3921 [oozie] Change color of ignored status to gray
* d27fe33 [oozie] Hide the coordinator actions when status is killed or succeeded
* 5439165 [oozie] Group coordinator buttons
* 3bb0f3d [core] Make desktop tests pass on Oracle DB
* 714bd1d [notebook] Show delete confirmation if snippet has content
* 5925ee3 [core] Don't show spinners for each item in the assist panel
* b8345e4 [core] Only expand entries for types that are expandable in the assist panel
* e1af716 [impala] Display message in Sample view in Impala if the table has complex column types
* ce8c513 [impala] Only show the columns returned in the sample data
* c8352c9 [search] Do not convert to string multivalue fields in result download
* 8db2dbe [jb] Show another attempt log if last attempt do not have any task
* f769fb4 [oozie] Give a full output path to the coordinator example
* 2421c94 [beeswax] Fix parquet format for customers table and remove parameterization from sample query
* 43e293c [beeswax] Fix lookup of beeswax and impala auth configuration values in dbms server
* a1ae994 [livy] Error out the session if the repl errors out
* d26608f [livy] Improve error message when pyspark and py4j not found
* 3354386 [livy] Bump minimum spark version in readme
* fb2f75a [livy] Find the py4j files with glob to make it forward compatible
* 6f5c2e2 [livy] Require SPARK_HOME env var to be set
* dff49ea [livy] Fix launching pyspark inside yarn
* 261fefa [notebook] Fix the Notebook links on the Home page
* 5838f00 [search] Do not convert to string multivalue fields
* ca8019e [tools] Add latest set of op scripts
* 8e20c57 [notebook] Add a new snippet with cmd+N/ctrl+N
* 789229f [notebook] Notebooks with a lot of text are now more compact
* 387e615 [notebook] Updated markdown import from iPython/Zeppelin
* 003bf80 [notebook] Initial support for Markdown editing
* f31fa62 [notebook] Added snippet titles to print CSS
* d824644 [notebook] Fixed font size on Ace Editor in Linux
* ad34456 [notebook] Updated print CSS
* 832b8a2 [notebook] Support for player mode
* e85cdee [notebook] Switch from double click to alt/ctrl + click to follow ace links
* c5a9cd3 [notebook] Gracefully fail when no snippets are configured
* 1ad98ac [notebook] Clean-up the ini template
* 9b6158d [notebook] Catch import errors for jaydebeapi module
* 1f6abeb [notebook] Update interfaces to use livy and livy-batch
* 2ab2f92 [notebook] Reverting the entry_point so that notebook is included in DESKTOP_APPS global
* e5c7a54 [core] Add desktop libs with is_url_namespaced setting to global namespace
* 5cee1db [notebook] Correct entry_point in setup and fix hueversion symlink target
* e4aca66 [notebook] Create a hook to display results coming from API without async execution
* 72352d7 [notebook] Pick snippet interface according to the configuration
* e4dd9d7 [notebook] Concept of MySQL connector
* b20d7dc [notebook] Concept of JDBC support
* 9b9f71b [notebook] Make snippets configrable from hue.ini
* 1435cd5 [notebook] Split APIs into respective packages
* 5743aa9 [notebook] Move Notebook specific code out of Spark app
* 1474cfe [notebook] Refactor notebook code into a single lib
* dbae7ad [doc] Replace Beeswax server reference to Livy server in SDK
* 8b33487 [notebook] Do not mix and match error code for expired session and legit error
* 0423bcb [core] Support nested lateral view references
* 40be01c [core] Support table references in lateral view definitions
* 68c50c2 [core] Support multiple exploded lateral views
* 0de6bff [core] Fix incorrect table alias suggestion in autocomplete
* 64c7cea [desktop] Rename some metrics
* 5fd7b0d [beeswax] Avoid jump in the vertical resize of the query editor
* d2c1446 [beeswax] Number results row from 1 instead of 0 and set max width for the first column
* 1302e34 [desktop] Move oauth_authentication_time metric into liboauth
* c458589 [desktop] Consolidate and improve the metric destription suffixes
* 7491374 [desktop] Fix registering the UpdateLastActivityMiddleware
* a768c8b [desktop] Remove "in Hue" from metric description
* 2d2f274 [desktop] Add an index to last activity
* 7865f67 [desktop] Simplifying metric names
* e3168ee [desktop] More metric cleanup
* f45fb42 [desktop] Metric description improvements
* fe3f8e7 [pyformance] Expose {histogram,timer} median, histogram sum metrics
* 18c8d0f [desktop] Simplify many of the metric names
* d3469ee [desktop] Only add the key to hiostogram, meter, and timer metrics
* 2b98681 [core] Autocomplete support for Impala arrays and maps
* 576e387 [core] Proper support for JOIN in autocomplete
* 27e84db [core] Set the DB settings TEST_USER param and default to 'hue_test'
* 605ea11 [beeswax] Reset INITIALIZED global for metastore tests
* fe7d9b1 [oozie] Sort datasets by name to make postgres tests consistent
* 3729de6 [core] Fix Oracle issues with TIMESTAMP migration and adding CLOB field in loaddata command
* 1d3591a [core] Improved handling of click and double-click on the same element
* 383f4d0 [beeswax] Support autocomplete for exploded lateral views
* 185b6e0 HUE-2901 [metastore] test_describe_partitions is failing on live cluster HUE-2900 [metastore] test_has_write_access_backend is failing on live cluster
* deadead [fb] Fix jHueHdfsTree for move and copy
* 18b0428 [dbquery] Fixed problem with empty query name and description
* 596dd8e [core] Downgrade pylint version to avoid a build error on SLES 11
* af24bd6 [impala] Don't show terms in column analysis of complex column types
* ac8ecb4 [core] Improved assist panel error handling
* 0c3da7a [core] Show server error messages when fetching terms fails in the assist panel column stats
* 1fa67ed [core] Don't cache any assist API response that contains the "code" attribute
* 4cf4b17 [core] Show terms for complex type columns
* d7d3b3d [jb] Unified, fixed and ellipsified long IDs on the side bar
* cce5d6c [beeswax] Improved history page search UX
* a61dae8 [useradmin] Fix useradmin test by ordering users
* 497d640 [impala] Enable parameterization for Impala "customers" sample design
* 7836bf3 [core] Update sample install user's username if needed
* 136c060 HUE-2551 [oozie] Easier update of a scheduled workflow
* 7160f85 HUE-2941 [hadoop] Cache the active RM HA
* b94207f [libzookeeper/indexer] Rewrite to not leak sockets or temp files
* fae25ad [core] Fix column stat refresh and accuracy indication
* 82a3ddf [spark] Fix cache issue with assistHelper
* 3daadac [core] Show message for unsupported column types in stats
* 32cade7 [libzookeeper] Fix zookeeper tests on kerberos cluster
* 6d30a7d [beeswax] Reset the cache when using the Mocked API in the tests
* 05e4b39 [core] Support autocomplete for array types in hive mode
* d7b231a [core] Show the correct type in the autocomplete menu
* 1cbc8b8 [desktop] Fix tests to support python2.6 syntax
* 3d9ba9a [core] Fix SDK app_template static paths
* c9563ee [desktop] Config check test now has a valid SSL certificate path
* 94d8230 [core] Convert one liner if to 4 lines for more readability
* e1b6cba [core] Fix generation of template app in the SDK
* 417d09a [useradmin] Add UserProfile.last_activity, metric, and middleware
* db15c68 [useradmin] Make sure the creation_method is a string
* 90227f3 [desktop] Generate the mdl with sorted metrics
* 9334713 [useradmin] Unskip a unicode test, skip a case sensitive test
* 71d68f0 [useradmin] Make tests sort the usernames
* d30c896 [desktop] Fix failing desktop tests
* daae285 [core] Split auth Pass-through username and password in respective apps
* 3c69c63 HUE-2954 [hbase] Fix internet explorer issue with cell editor
* 0d9c01f [spark] Fix table metastore links
* 71be43ab HUE-2942 [core] Unify app examples
* f424e76 [beeswax] Fix table name autocomplete
* d058c2f [core] Improved assist loading experience
* f17468b [core] Move the active database to the assist helper
* f563e36 [beeswax] Remove unused code
* e3a19d6 [core] Fix issue with column stat terms not loading
* 15dc487 HUE-2955 [desktop] Error if the configured SSL certificate/key files do not exist
* 0d1b176 [desktop] Fix downloading and installing pylint
* d19fd78 [desktop] Stop eating exceptions if a pseudo cluster fails to start
* 48e97fd [desktop] Fix some stinky typos
* 0cabff0 [desktop] Avoid potentially referencing unbound local variables
* a3cbddc HUE-2465 [beeswax] Nice to have Natural Sort for database drop-down-list
* 4cab982 HUE-2886 [spark] Show livy session process logs
* 027c070 [hadoop] Rename user to username to remove ambiguity
* 6236ad7 HUE-2936 [jb] Disable delegation token for YARN kill button for now
* a691ed7 HUE-2936 [jb] Support delegation token for YARN kill button
* df0bb00 [beeswax] Provide explicit permissions to apps to test user
* 4c13df1 [livy] Add reference to config file
* b4ccb8f [core] Do not re-add default group to users at login time
* a4f778a [indexer] Fix delete indexes for collection types in new Indexer
* 702dd30 [indexer] Rename collections to more generic indexes
* 4161ac7 [desktop] Fix oozie_api.py to work on Python 2.6
* 213c4dc [desktop] Backport CherryPy fix for 408 errors when used with mod_proxy
* 76e7f30 [beeswax] Fix issue with initially selected DB in assist
* 0f082a5 [beeswax] Use the new assist panel for Hive and Impala
* 327cace [core] Don't show _impala_builtins in assist panel
* afea9b1 [core] Assist panel improvements
* 582cef3 HUE-2227 [oozie] Added tests for coordinator log filtering
* c101525 HUE-2227 [oozie] Added clearable and value update for text filter, added spinner
* 07f172e HUE-2227 [oozie] Added loglevel and text filters for Coordinator logs
* 942208e HUE-2227 [oozie] Prettify log filtering
* 592ce4b HUE-2227 [oozie] Add a limit=N and recent=M when fetching job logs
* 11db7f8 [oozie] Read Oozie Share Lib path directly from Oozie in check config page
* f372756 [core] Show error messages from table and columns stat refresh in the assist panel
* 789e64d [core] Assist entry double-click will insert complete path
* 850d6d6 [spark] Add structs, arrays and maps to assist panel
* 5dfee30 [core] Extract assist helper with common assist functionality
* fad2c20 HUE-2945 [fb] Drag&Drop upload can hide errors
* 0a1aa83 [livy] Update README to list R
* a290e90 HUE-2913 [fb] Make showing and hiding upload/download button configurable
* b19159c [metastore] Fix metastore show_tables test
* 8d21a08 [beeswax] Warn on downloading beeswax results with more than 255 columns
* f48781e [desktop] Fix typo in file_reporter
* f154e94 [HUE-2939] Use SHOW DATABASES for more performant fetch databases, and lazily-fetch metadata
* 95ea7b6 [desktop] fix metrics; pyformance counters shouldn't necessarily be CM counters
* 871ce1d [desktop] Bump coverage version to fix Python 2.7 bug
* b282c6a [beeswax] Fix autocomplete.js import for case-sensitivity
* e7d859f HUE-2926 [notebook] Opening multiple snippets of the same type starts multiple livy sessions
* 79a4fe1 HUE-2943 [core] Manually exclude boto from the pruning to fix packaging
* 6203c06 HUE-2943 [core] Add boto library
* 696f926 [desktop] Assert collection interval is greater than 0
* f2a7bda [desktop] Log errors in file_reporter
* 98d42f1 [desktop] Use "seconds" for metric numerators
* 53480d4 [desktop] Remove unused context from metric definition
* 40a9cec [search] Remove Moment.js deprecation warnings
* f1d916e [rdbms] Fall back to database from conn_params on failure to fetch from Postgres information_schema
* d378e37 HUE-2844 [desktop] Add django-axes to limit login attempts
* 3d6a38b [desktop] Use User.objects.get_or_create to make sample user
* d295c91 [useradmin] Make useradmin tests reentrant
* c0a65f3 [desktop] Lazily count the number of users
* 94cf67d [desktop] Don't create models in a default argument
* d3644da [core] Fix XSS vulnerabilities of jHueNotify and UserAdmin
* a4dd046 HUE-2852 [core] Support autocomplete of struct types from map values in hive mode
* 8ae1a8a [core] Make the autocompleter mode-aware
* 98b496e [core] Trigger ace autocomplete after completions that ends with "."
* 8c50f8e [core] Improves reliability of the main navigation dropdown submenus
* c4a3aa8 [jb] Avoid exeception when building log job links with a terminal dot
* 2979c25 [core] Add table ref autocomplete for multiple tables in the statement
* 2f074ee [beeswax] Switch to the new autocompleter
* 80059eb [core] Fix autocomplete issue with started entry of 'from' in select statement
* 0d5eacf [spark] D&D import functionality for other notebook formats
* 01035e9 [jb] Sort by Submission Date desc by default
* 6f9fcce [beeswax] Add more space in between saved designs and add comments
* 95cee46 [spark] Fix Spark notebook close_statement, which only takes snippet object
* 57efa31 HUE-2700 [oozie] Oozie workflow and action names longer than 40 chars cause issues
* 7cc45ea HUE-2952 [beeswax] Calling not existing function gives no error
* 3e4b8fd [core] Clean-up the ace autocompleter
* e2de78d HUE-2852 [core] Support autocomplete of struct types
* 2484c57 [core] Initial Jasmine tests for autocomplete
* a57ec97 [core] Move autocomplete from spark to desktop
* 3a750f7 [core] Move autocomplete functionality from ace binding to ace.autocomplete.
* 709383b HUE-2951 [infra] Specify DEVTOOLS versions
* 0847c1e [beeswax] Add better error message when Hue can't connect to HS2
* b9567b3 [hbase] Allow users to drop or edit HBase tables when impersonation is ON
* 6a6fba6 [livy] Update the documentation to reflect the current API
* 059a226 HUE-2935 [core] Check status of cluster as the hue user
* 91a9336 HUE-2935 [hadoop] Support YARN impersonation
* ea3b7a2 [core] configuration for load balancer that requires X-Forwarded-Host header
* 68df0f2 [impala] Added session link to the new tab
* 255e8b2 [impala] Skeleton of a new Session tab
* 8849ae7 [security] Auto-size the Hadoop Groups dropdown in the Hive app
* a791475 [beeswax][spark] Fix charts sorting
* e496a74 [core] Add ability to enable DjangoSaml2 and PySaml2 Debug logging
* de616fe HUE-2946 [hadoop] test_seek_across_blocks OOM HDFS on live cluster
* a78b9bc [middleware] Change status to statusCode in audit log
* 059f81c [spark] Fix Ace editor basePath for static files
* 27e9292 [indexer] Skeleton for providing a path to an HDFS file and previewing it
* 3bce9ef [indexer] Add ability to quick-create empty collection
* 605e022 [indexer] Move the alias deletion to the checkbox list
* d0c0a5b [indexer] Edit existing alias
* 53f26b4 [indexer] Delete a collection alias from the UI
* b48897f [indexer] Display collections column value for indexes list page
* d408762 [indexer] Rename notebooks to indexes
* 7114b78 [indexer] Add form to create a new alias`
* dac5461 [indexer] Skeleton for listing collections, cores and aliases
* f987fbc [indexer] Removing old unused macro page
* 1a4099b HUE-2869 [indexer] API calls for Managing collection aliases
* fe6e66a HUE-2944 [proxy] Fix logging in test progress-line
* a2e4eb1 [filebrowser] Truncate the error message returned by the HDFSfileuploader
* ef471f0 [middleware] Remove unused audit_queue_policy configuration
* 6abc9ae [beeswax] Avoid NaN columns on un-managed backend error
* a317b33 [desktop] io.SEEK_* is only in Python 2.7+.
* 7851c85 HUE-2940 [core] Use io.SEEK_* constants
* 92dab4d [middleware] Update audit log format and whitelist of operations
* 82775b0 [core] Move parameterization lib to desktop from jobsub
* 97fd947 [beeswax] Fix async problem of loading of tables/autocomplete
* 3b39a26 [beeswax] Avoid multiple concurrent fetchResults calls
* 0f4cd07 [core] Support middle click paste on Ace editor
* b5b625f Merge pull request #225 from fermich/resourcemanager_information_uri
* 0454993 [core] Upgrade Jasmine to 2.3.4
* 5d6736a [spark] Improved result handling for charts
* 4e159fb [spark] Return the session properties when creating a new session
* b1389b9 HUE-2079 [beeswax] Consolidate alias autocomplete
* 5aeb3d4 HUE-2904: [hive] Create nested type example HUE-2905: [impala] Create nested type example HUE-2306: [impala] Add sample tables and data to exercise all of Impala's supported types
* 16b4ba5 HUE-2906 [impala] Autocomplete struct nested type HUE-2907 [impala] Autocomplete helper for map type
* 9ed8727 [desktop] Fix MDL generation
* 4363f0a [desktop] Add config options to config files
* 7277f1e [desktop] Correct metric numerators and denominators
* 8cc873b [desktop] Histograms, meters, and timers are all counters
* ec045d4 [desktop] Zero out histogram metrics if count is zero
* 9a5c191 [desktop] Allow web metrics to be disabled
* 5872262 [desktop] Progress on script to generate mdl config
* a61a2a7 [desktop] Write metrics to a file
* 23cca8f [HUE-2750] [metastore] Show comments in the database and table views
* 76e3000 [hive] Support parameters in multi queries
* 31cf206 Merge pull request #224 from TheClimateCorporation/add-metrics-support
* 565522e [core] Fix for multiple Ace link tooltips issue
* c938a41 [core] Fix unicode string for KO escaping issue
* ea72e6e setting cluster information uri to /info
* 997da22 [spark] Only show the assist panel when there is a base URL set
* dabea20 [core] Fix autocomplete issue with keywords in table names
* 6c8cd82 HUE-2863 [livy] Rewrite repl to eliminate races to the interpreter
* ecf9eee HUE-2923 [livy] Allow multiple commands to queue up
* 99d265b [livy] Update README to add Python/R min versions, headers to example
* c6495be Add scalatra-metrics support to livy
* 2fcbafa HUE-2879 [oozie] Adding a dryrun before submitting workflow or coordinator
* c0a4351 HUE-2933 [oozie] Autofill the nominal_time in the SLA if the workflow is submitted manually
* 25ca4ff HUE-2897 [useradmin] Skip tests on live clusters that rely on db collation
* ed86765 [useradmin] Sort users by username to make test consistent
* 70794dc [pig] Import SkipTest
* a974d3d [oozie] Update tests to sort nodes to make it consistent
* 8a0012e [beeswax] Only try to delete database in tests if it exists
* d9aebab [desktop] Clear secret_key_script if live cluster has it enabled
* ceb3589 [desktop] Update test_app_permissions to handle certain apps being disabled in a live cluster
* 14b2aa6 [sentry] Skip tests if sentry-site.xml is not present
* f6aacf0 [beeswax,useradmin] Fix typo
* 071a4ee [metastore] Fix the is_live_cluster check
* 75a663a [desktop] Silence many Document.objects.sync warnings when table doesn't exist yet
* ad90949 [core] Extended _ko to the whole Hue
* 73085c8 [core] Add global util _ko to do i18n on inlike KO bindings
* 15b1d8c HUE-2832 [livy] Make session timeout configurable
* b327979 [tools] Initial import of wrk stress tester
* cde6a6a HUE-2916 [fb] Change URL-routing
* 6ad754a [beeswax] Fixed display of Settings form fields
* f096ce0 [spark] Improved UX for automatic add of snippet after execute
* 83ed16b [core] Improved indication when a filter is active in the assist panel
* ddb9b50 [spark] Show errors in unstyled list
* 37e656f HUE-2920 [core] Fix issue with assist not showing tables from selected database
* 2511e96 [spark] Improved autocomplete
* 1a9d4df [hive] Do not create test DBs if they already exists
* bfdf46c HUE-2673 [spark] Show error if session timeouts at creation
* 5ce3dc6 [spark] Provide the batch arguments as a list to livy
* e5e78f7 HUE-2877 [desktop] Add pyasn1 and ndg_httpsclient to support SSL Server Name Indication
* 4af95b9 [spark] Fix error reported by scatter plot
* 699eb65 [spark] Fix issue when there are not images in the result
* 7a28f59 HUE-2641 [spark] Display error lines
* 03c30a3 [livy] Fix compiling Livy on buildbots
* 00fac4f [useradmin] Fix useradmin test
* 19be850 [livy] Allow RDDs to be used with %json magic
* 6a1feb6 [livy] Minor cleanup of Spark Interpreter
* 68df878 [livy] Add some documentation
* b0c3bd3 [livy] Spark Interpreter should implement Interpreter
* 26ff525 HUE-2917 [livy] Allow scala RDDs to be inspected with %table
* 62420de HUE-2917 [livy] Implement scala spark introspection
* 30e7764 [pig] Fix import in tests
* 5a48fde HUE-2897 [useradmin] Skip unicode and case sensitive tests when live cluster testing
* 2fa8274 [beeswax] Don't check history hostname when live cluster testing
* 43f7f29 HUE-2902 [tests] Skip non re-entrant tests when live cluster testing for now
* a96837f HUE-2896 [tools] Insert Hue app dependencies before system dependencies
* 03ca307 [spark] Corrected Hive/Impala table and column ordering and fixed a JS bug on autocomplete after paste
* 8d35e49 [spark] Ignore case for Hive and Impala autocomplete
* aa23f4a [spark] Adjust the snippet type for the placeholders
* b8d402e [core] Remove the gray background of the active line in the Ace editor
* d4c9cd0 [core] Allow styling of the Ace placeholder
* a22fea5 HUE-2642 [spark] Automatically open a new snippet on execute of the last snippet
* 940a73d [spark] Show the correct snippet name in the snippet header
* 4e5fb20 HUE-2891 [notebook] Integrate images from R
* 3f58f86 HUE-2908 [livy] Partially address multiline commands
* ebef7ef [oozie] Fixed spinner on bulk actions and removed multiple click handler calls
* 916ac54 [spark] Moved and restyled errors
* 2c07ba7 HUE-2894 [livy] Shut down and server repl if process dies or exception thrown in server.
* b7b7ba5 HUE-2664 [jobbrowser] Fix fetching logs from job history server
* cc5c08c HUE-2903 [oozie] Fix error with Workflow parameter on rerun
* 93f1cb7 [jobbrowser] Add Application Type to jobs list
* 0933b8f [search] Fix Marker Map zoom filtering
* b457c4f [notebook] Also rename the type of the snippets in the example
* 2a93dac [livy] Expose even more SparkR plotting tools
* b782c35 [livy] Fix running "cat(3)" in SparkR
* c5346fa HUE-2892 [notebook] Disable $ variables for R
* 51074bd [livy] Explicitly depend on commons-codec
* 2e44a33 [livy] Strip SparkR out the ANSI control characters before checking marker
* 0d00f65 [core] Support for fields autocomplete in Ace after a . in non-live mode
* 234841a HUE-2893 [desktop] Backport CherryPy SSL file upload fix
* a723235 HUE-2889 [livy] Add some magic to render server side R plots
* 616cf17 [core] Introduce Filebrowser and Metastore links on Ace Editor
* 5a061b4 HUE-2668 [notebook] Switch session kind alias from python to pyspark, scala to spark
* 1c741af HUE-2311 [oozie] Inform user from cause of workflow submission failure
* 46fdb83 [core] Ace autocomplete now matches the start of the word
* fc6758f [hive] wait_for_query_to_finish should return a response in the tests
* c930c53 [sentry] Do not show the add privilege button on Browse view for non admin
* b14b642 [hive] Make it up to the caller to check for the status of a query in tests
* 5326efb [doc] Add good indentation to the list of main changes


Contributors
------------

This Hue release is made possible thanks to the contribution from:

- Aaron Newton
- Aaron T. Myers
- abec
- Abraham Elmahrek
- Aditya Acharya
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
- Ann McCown
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
- Chris Conner
- Chris Stephens
- Christopher Conner
- Christopher McConnell
- Christopherwq Conner
- Craig Minihan
- cwalet
- Daehan Kim
- dbeech
- Derek Chen-Becker
- Dominik Gehl
- Eli Collins
- Enrico Berti
- Erick Tryzelaar
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
- Ivan Orlov
- Jaguar Xiong
- Jakub Kukul
- Jarcek
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
- krish
- Lars Francke
- linchan-ms
- Linden Hillenbrand
- Luca Natali
- Luke Carmichael
- lvziling
- Marcus McLaughlin
- Mariusz Strzelecki
- Matías Javier Rossi
- Michael Prim
- Michal Ferlinski
- Michalis Kongtongk
- Mobin Ranjbar
- motta
- mrmrs
- Nicolas Fouché
- Olaf Flebbe
- Oren Mazor
- oxpa
- Pala M Muthaia Chettiar
- Patricia Sz
- Patrycja Szabłowska
- Paul Battaglia
- Paul McCaughtry
- Peter Slawski
- Philip Zeyliger
- Piotr Ackermann
- Prasad Mujumdar
- Qi Xiao
- raphi
- Renxia Wang
- Rick Bernotas
- Ricky Saltzer
- Romain Rigaux
- Roman Shaposhnik
- Rui Pereira
- Sai Chirravuri
- Scott Kahler
- Sean Mackrory
- Shawn Van Ittersum
- shobull
- Shrijeet
- Shrijeet Paliwal
- Shuo Diao
- Siddhartha Sahu
- Simon Beale
- Simon Whittaker
- sky4star
- Stephanie Bodoff
- Suhas Satish
- Tatsuo Kawasaki
- thinker0
- Thomas Aylott
- Tianjin Gu
- Todd Lipcon
- Tom Mulder
- Vadim Markovtsev
- van Orlov
- vinithra
- voyageth
- vybs
- William Bourque
- wilson
- Word
- Xhxiong
- xq262144
- Yixiao Lin
- Yoer
- Zachary York
- Zach York
- Zhihai Xu
