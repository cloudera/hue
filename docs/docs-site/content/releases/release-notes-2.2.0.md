---
title: "2.2.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -2020
tags: ['skipIndexing']
---

### Hue v2.2.0, released February 25th, 2013


Hue 2.2.0 is compatible with CDH4.2 (Cloudera's Distribution Including Apache
Hadoop 4.2).

Website: http://cloudera.github.com/hue


Notable Features
----------------

- The Oozie application has been restyled completely and now supports Ajax refreshes
- A Cloudera Impala app was added
- Beeswax/Hive editor is more user friendly
- FileBrowser was restyled and now includes bulk and recursive operations (e.g. multiple deletes)
- JobBrowser is compatible with YARN and job logs can be accessed in one click
- UserAdmin was restyled and LDAP integration was improved
- MySql InnoDB and PostgreSQL are officially supported


Notable Fixes
-------------

- HUE-535 [beeswax] Support multiple databases
- HUE-833 [oozie] Add all Oozie actions
- HUE-873 [jb] Direct access to task logs
- HUE-775 [fb] Upload zip file through filebrowser.
- HUE-867 [desktop] Ensure first user home directory is created
- HUE-851 [oozie] Rerun, suspend, resume a workflow or Coordinator
- HUE-820 [oozie] Display any workflow as a graph
- HUE-730 [core] Database greenlet support for MySQL
- HUE-882 [core] Add stack trace and logs link to 500 and PopUpExceptions pages


Compatibility
-------------

Hue 2.2.0 runs on CentOS versions 5 to 6, and Ubuntu 10.04 to 12.10.

Hue 2.2.0 is compatible with CDH4.2. Specifically:

- File Browser depends on Hadoop 0.20 (for WebHDFS/HttpFS).
- Beeswax is tested against Hive 0.10.0.
- Job Designer depends on Oozie 3.3, using the Oozie web service API.


List of 304 Commits
-------------------

* 39f8c75 [doc] Last update
* 8c7f3b7 [help] Update the help for Hue 2.2
* 53854d4 [build] Make Oozie setup independant of release or snapshot tarball versions
* 90f21f0 HUE-1046 [oozie] Support Coordinator job properties
* 8b63e2f HUE-1040 [oozie] Can't use prepare field in a scheduled workflow
* 735c7fd [shell] Update path to Sqoop2 binary
* 3fee41c [beeswax] Sample user ID
* 1d99305 HUEE-1037. Beeswax fails to connect secure remote metastore
* 9cbd025 HUE-1038 [jobsub] Sample user created with wrong id
* df4fd45 HUE-1034 [oozie] Streaming action should not have a job_xml
* 4e512ff [beeswax] Visual feedback on install samples
* 00cefa7 HUE-1032 [oozie] Dual representation of files attribute
* b9941cc HUE-1030 [oozie] Java Tasks with both arguments and java options generate incorrect workflow xml
* b27530b [oozie] Critical UX improvements
* 14d2121 [oozie] Import jobsub action fix
* e55166c [core] Sasl fixes
* 2733240 [core] Last drop of localized messages for 2.2
* c5d30b6 [impala] Saved queries page should only list Impala queries
* 20219d4 [beeswax] Support migration of query history
* 9bf1fc3 [beeswax] Metastore client supports SASL
* b6f71aa [oozie] Simplify hive action example
* 37e7ed8 HUE-1023 [fb] Access content of directories with conflicting URL names
* 1a21529 HUE-991 [beeswax] Clicking on 'collapse' on result page misalign the table and its button
* 74a96a4 HUE-976 [fb] Number of pagination items are reset when looking at a file
* 1c8b114 HUE-818 [oozie] Resubmit a coordinator from a certain day
* 6b2d4bf [oozie] Fix import FS workflow test case
* e9d6376 HUE-1016 [oozie] Import FS delete action bug fix
* 438a645 HUE-1020 [fb] On Chrome the permissions in the Change Permissions screen do not display the existing permissions
* 85e5d93 HUE-1019 [fb] The 'New' button is misaligned on certain browsers with a non-standard zoom applied
* 0a629f0 Revert "HUE-1010 [oozie] Dashboard should have a Suspended filter"
* 1f2c56e HUE-1018 [oozie] Add tooltip to workflow Suspend button
* 1dcab39 [oozie] Remove debug statement from previous commit
* dc398c2 HUE-1017 [oozie] Workflow and coordinator editor should have a consistent navigation bar
* cdf3c07 HUE-946 [oozie] Fix property name autocomplete on the edit workflow page
* 4fd11e8 HUE-944 [oozie] Fix edit workflow for IE8
* d931467 [core] Update translation files
* e748e7a [oozie] Import workflow improvements
* 4e00f77 HUE-1009 [core] LDAP backend user creation configurable
* c581d19 HUE-1007 [oozie] Modal module captures escape key events
* 11b77e8 HUE-1007 [oozie] Add loading spinner to edit workflow page
* fd0ccba HUE-981 [fb] Fetch next block should be dynamic
* 4206c72 HUE-902 [core] Include modified pyOpenSSL 0.13 version
* 42a279f HUE-902 [core] Include pyOpenSSL 0.13 version
* c79573a HUE-1011 [oozie] Coordinator dashboard Actions tab should have live link for External Id
* 48eefbd HUE-1010 [oozie] Dashboard should have a Suspended filter
* 840f250 HUE-902 [core] Remove pyOpenSSL from dependencies
* 6c7c86b HUE-1008 [oozie] Action bar of the workflow editor looses its default position
* f07a5d2 HUE-922 [fb] Rename a directory to one that already exists moves the directory under the one that exists
* d1bce9f HUE-999 [oozie] Ajax refresh of the coordinator detail page
* 74d00a5 HUE-960 [oozie] Redesign workflow page
* c09a7aa HUE-960 [oozie] Redesign workflow page
* 47adfdc HUE-999 [oozie] Ajax refresh of the coordinator detail page
* cfee9cc HUE-889 [oozie] Smarter file chooser in Workflow editor
* 97d83bb [shell] Add Sqoop2 user permission
* 4259fc8 [core] Backward compatibility for upgrades to Hue 2.2
* 280cf46 [oozie] Fix oozie tests
* 10fcdee HUE-988 [oozie] Fix node drop onto decision node
* aa17a2a HUE-960 [oozie] Redesign workflow page
* 4ba7520 [oozie] Fix OozieApiMock for testing
* 1178545 [oozie] Fix several inconsistencies
* fa8a7c3 [oozie] Rerun, suspend, resume a workflow
* 102666a [oozie] Token propagation warning when using Java action in secured mode
* 680b66f [core] Make thrift generated files python2.4 compliant
* 2b00734 [beeswax] Migrate to Hive 0.10 and Thrift 0.9
* 427035a [oozie] Editable names for fork and decision
* ca9c494 HUE-870 [oozie] Use universal action bar
* 1b89554 HUE-993 [impala] Support download of result
* 6e2227f [fb] Change archive to zip and add download button
* 64a2df6 [oozie] Drag a node onto workflow editor.
* 89cf843 [oozie] Drag a node onto workflow editor.
* 9663116 HUE-997 [oozie] Notification internationalization in workflow editor.
* 1ab1d80 HUE-991 [beeswax] Clicking on 'collapse' on result page misalign the table and its button
* d3a3e21 HUE-998 [useradmin] Turn off form autocompletion when adding/editing a user or group
* ee46c03 HUE-807 [oozie] Ajax refresh of a running job
* 609be3d HUE-934 [oozie] Edit action in bigger popup or within the page
* e381d0b HUE-974 [oozie] Readonly support
* b119671 HUE-990 [oozie] Only show the datasets belonging to the coordinator
* b4130ae [core] Order of configuration dumps and help links follows the order of the app icons
* 517c6e6 [oozie] Location of is_shared property in workflow properties should be consistent
* 17c031b HUE-988 [oozie] Fix saving
* 8c849af [shell] Update Sqoop2 command
* a56da26 HUE-989 [oozie] Action management is broken
* 42aa60d HUE-871 [beeswax] Expired queries should have a better user experience
* 6bc9dc6 [core] Second drop of localization
* dea826a [oozie] Import workflow with Subworkflow action and rudimentary support for all oozie schema version
* 4b9e291 HUE-982 [oozie] Coordinator should prepopulate namenode address if needed
* 8f29678 HUE-436 [beeswax] Server with embedded metastore prints inaccurate log messages
* fd3a4ef [oozie] Import workflow with Generic action
* 517312b HUE-820 [oozie] Display any workflow as a graph
* ec560e6 [impala] Impala header columns are wrong
* cfd3a5c [core] Fix some XSS vulnerabilities
* dfe5071 [oozie] Import workflow with Email action
* a5fe7eb [oozie] Import workflow with FS action
* 763f4b9 HUE-979 [oozie] Redesign workflow graph look
* 999891e HUE-984 [oozie] min-height for completed job tables
* bee3ac6 HUE-935 [oozie] Better node edition experience
* 85edfd0 HUE-935 [oozie] Better node edition experience
* 8fbc54e HUE-984 [oozie] min-height for completed job tables
* 04be852 HUE-969 [oozie] Automatically infer schema version when importing workflow
* dfb13cd HUE-973 [oozie] XML syntax highlighting
* 85cd772 [core] Show that postgresql_psycopg2 is supported
* c7a287d HUE-969 [oozie] Import java args should be space separated, not JSON list.
* 5d07522 [core] Update doc to point hue.ini in /etc/hue or desktop/conf
* 14a32a1 HUE-978 [useradmin] Base DN needs to to have components capitalized when comparing with searcn DN.
* dbb61b5 HUE-978 [useradmin] Add LDAP user/group with DN
* ffcb0bf HUE-940 [oozie] Fix oozie test case for import jobsub workflow
* 22369d5 HUE-983 [oozie] Coordinator could support previous dates
* 36ffc42 HUE-697 [jobbrowser] Ability to browse MR2 jobs
* e43c3c4 HUE-940 [oozie] Revamp import JobDesigner action
* 8609eb6 HUE-985 [core] i18n of datatable plugin
* 3c02468 HUE-577 [fb] Snappy compression support
* ebed8c5 [useradmin] LDAP group search merge issue fix
* 896fa20 [useradmin] Add n users that match wild card expression in LDAP import
* 21f222c [useradmin] Import any group name from LDAP
* aab1f48 [oozie] Bump version to 3.3.0
* aefcbf7 [oozie] Use timezone when making HTTP calls to oozie
* 46dc8d5 [core] Little i18n fix
* 10877d1 [oozie] Import decision node with DecisionEnd nodes
* 0338318 [useradmin] Missing parenthesis
* e115ccc [oozie] Add decision end node
* 4f3f838 [useradmin] Add LDAP exception details
* 0b8148b [useradmin] LDAP errors caught and logged
* 69ff61d HUE-937 [oozie] JS Test cases for loading and saving a workflow
* c1a33c6 [useradmin] LDAP search wildcards.
* bd36c45 HUE-937 [useradmin] New JS tests for dynamic workflow editor
* c87bb68 [useradmin] Add non-existing LDAP user fails
* c108594 [beeswax] Sanitize configuration settings tab
* 0178560 [core] Using Hue blue logo on about and login page
* 27c912a HUE-980 [shell] Shell stops working after first timeout
* ebf6fca [core] First pass of localization for 2.2
* 3ab9d4c HUE-851 [oozie] Simplify Coordinator page
* 354ee28 HUE-851 [oozie] Simplify Coordinator page
* aaafb8c HUE-730 [core] Database greenlet support for MySQL
* 4f5ca03 HUE-851 [oozie] Simplify Coordinator page
* 3a69395 HUE-851 [oozie] Simplify Coordinator page
* eb38948 [fb] Upload to federated cluster
* 0316b2d [jobbrowser] Fix flakey test
* 9cadaff HUE-938 [oozie] Fix order of operations in node editing from decision node and added EL help
* 33ee9ef HUE-938 [oozie] Add reference to action names in decision node
* 7f4fbb5 HUE-972 [core] Build failure beacause of asm.jar dependency change
* f7e9f4f [core] UnboundLocalError in kt_renewer.py hides permissions issues
* 10c9cf2 [core] Fix various problems of i18n extraction
* 9cae8df HUE-933 [oozie] Fix clone node and unsaved ribbon
* ae66169 HUE-958 [jobsub] chmod in TestJobsubWithHadoop doesn't always complete
* ee92c4f HUE-883 [oozie] Add Generic action
* 4c36f23 HUE-970 [oozie] In Workflow properties, Job XML field chooser should choose file, not folder
* 81f6feb HUE-833 Add Subworkflow action
* 335d7df [desktop] Fix test_error_handling_failure test case
* c0f6257 HUE-833 [oozie] Add Email action
* eb3576f HUE-408 [desktop] User creation form usage when first creating a user
* fd6ec82 HUE-833 [oozie] Add Fs action
* e91dcd2 HUE-968 [oozie] Create new action fixes
* c750938 [beeswax] It looks like Hue installation is missing hive-default.xml
* fba123b HUE-971 [oozie] Fix empty workflow
* 09b9594 HUE-770 [beeswax] Improve secured cluster configuration experience
* e70648a [fb] Fix home dir test
* 2803e69 HUE-958 [fb,oozie] Fix flakey tests
* b3939a6 HUE-958 [liboozie] Copy Oozie sharelib in the home of Oozie user
* ab5cee9 HUE-964 [core] 500 errors should go to default debugger if we cannot render custom 500
* 0d7b1c7 HUE-967 [useradmin] Useradmin shouldn't depend on the existence of other apps
* d138867 HUE-958 [liboozie] Activate  Oozie share lib for Distcp test
* 6377958 HUE-958 [liboozie] Copy Oozie share lib for tests
* 6bb1287 HUE-933 [oozie] Ribbon and confirmation popup are triggered when new action creation is cancelled
* 1ac2119 HUE-958 [jobbrowser,jobsub,ooxie] Fix flakey tests
* b3b4094 HUE-965 [useradmin] Improve user experience
* 3492325 HUE-547 [core] Files erroneously say "Licensed to the Apache Software Foundation"
* b02cf1b HUE-954 [oozie] Support boolean fields
* 2f7feb9 HUE-963 [core] Hue in a Kerberos enabled environment cannot use HttpFS
* 3c883a1 HUE-961 [fb] Upload archive with root directory containing only directories
* a5ad934 HUE-933 [oozie] Cancel button when editing a node
* 9ab1333 HUE-931 [oozie] Validate action before exiting edit modal
* c55558b HUE-898 [oozie] 'definition' not in file error fix
* b9efaa4 HUE-933 [oozie] Confirmation popup when leaving a workflow with unsaved modifications
* ed20709 [impala] Mock calls to Beeswax in the tests
* 34030b6 [core] i18n Update of the po files and fix or compilation errors
* 9f284af HUE-535 [beeswax] Support multiple databases
* a5a3aa0 HUE-898 [oozie] Upload a workflow definition file
* 68cc5f3 HUE-955 [core] Remove circular reference to exceptions
* d08df91 HUE-899 [oozie] Smarter file chooser in Workflow editor
* a052b14 HUE-294 [beeswax] Query editor should have line numbers
* ef8c1f4 HUE-939 [oozie] Clean up workflow editor
* f3caa3f HUE-929 [oozie] Support change of deployment directory
* e251bc2 HUE-407 Document what minimum versions of Firefox, Chrome, Safari and IE Hue supports.
* 59e2e0d [useradmin] Improve transaction handling in update_app_permissions signal handler.
* 2797e0d HUE-898 [oozie] Fix linkages in xslts
* d07ce83 HUE-943 [fb] Fix subdirectory pagination
* ffd5776 HUE-898 [oozie] Import workflow definition
* a673177 HUE-952 [oozie] job-xml field is not generated in some actions
* d40d62f HUE-947 [oozie] Sorting by modification date in Editor is wrong
* 6cec9d7 [build] Set Hue version to 2.2.0
* efc0bd4 [core] Sort alphabetically apps in dump config
* e5ad97a [oozie] Move capture-output to bottom in Shell action
* a56b7f3 HUE-942 [beeswax] Make Query Textbox higher by default
* cf1b2f1 HUE-949 [impala] Change icon
* ffb076c HUE-945 [oozie] Actions fields are not loaded or saved
* c56e4b7 [beeswax] Increase number or rows fetched during download
* fbfc123 HUE-944 [oozie] Fix edit workflow for IE8
* ca28110 HUE-936 [oozie] Add back help when editing an action
* 70b67b1 HUE-932 [oozie] Show 'saving' status when editing a workflow
* 9b70e33 HUE-933 [oozie] Confirmation popup when leaving a workflow with unsaved modifications
* abe9be5 [impala] Fix test looking for Impala icon
* 47025bf [impala] Adding icon
* 171726c [impala] Adding locales
* 1561dd7 [impala] Adding Impala app
* e299da3 [impala] Initial commit
* d4a1eca HUE-933 [oozie] Confirmation popup when leaving a workflow with unsaved modifications
* 2cf1662 HUE-930 [jb] Have consistent job and task names across the whole app
* fe930e9 [core] Remove pyexcelerator
* 865b35f HUE-589 [beeswax] Support TIMESTAMP datatype
* d9e103f [beeswax] Adding datanucleus as repository
* 6a90fd6 [oozie] Fix capture-output in Shell action
* 03ed87c [oozie] Fix Ssh/Shell actions in new UI
* 9e7b616 HUE-925 [shell] Use secure temporary files for kerberos ticket management
* 3de7ffc HUE-822 [oozie] Fix tests
* 25d5234 [beeswax] Add 'Column' tabs on the result page
* dc7f032 HUE-822 [oozie] Prepare statements should follow fs action convention
* ab3bbba HUE-924 [beeswax] Improve UX on Save table
* c0d6d71 HUE-907 [beeswax] Create table manually can not remove column
* 68b120b [core] Fix English mistakes and text consistency
* edf64d5 HUE-221 [shell] Sqoop2 shell
* 98b6940 HUE-824 [oozie] Support local paths in workflow path variables
* 4b58bf4 [beeswax] Fix failing tests
* 9545e7c HUE-817 [oozie] Resubmit a workflow from a certain step
* 8a8f225 [doc] Shell app setuid utility should be owned by root
* e3e7fd8 HUE-923 [beeswax] On create table manually the external location file chooser doesn't let you choose a folder
* 1c898f0 HUE-923 [beeswax] On create table manually the external location file chooser doesn't let you choose a folder
* 5962e9c HUE-920 [fb] Support for files and folders with special characters
* ec9c8ca [oozie] Add specific error message when Oozie is not running
* 01fa6a3 [core] Update tests to use latest builds of dependencies
* e0994eb HUE-720 [core] Test when failure to create first user home directory
* 2f6c518 [core] Error creating the home directory for first user should not stop user creation
* 3abac7c HUE-588 [beeswax] Scrolling in job logs is broken while the job runs
* dd03d3c HUE-916 [core] Save and Cancel buttons are sometimes reversed in position
* 43f8ba8 HUE-918 [help] Anchor links scroll to a shifted anchor position
* 3d45edb HUE-915 [core] Uniform modal dialogs
* 3d09714 HUE-734 Job designer link to job browser
* 8b13b4f HUE-878 [desktop] Add a remote user backend
* b085489 HUE-888 [oozie] New oozie front end
* a85eaeb [beeswax] Integration of Hive Server 2
* 4a52276 [jobsub] Fix running job status flaky test
* 6990cd1 [oozie] Coordinator support for HOUR
* ce6d541 HUE-913 [core] Convert new jump to column to jQuery plugin and test it
* ac4429c HUE-914 [core] Fix form margin in Bootstrap dialogs
* 2ec658e HUE-674 [desktop] Add tests for dump_config stability
* 0b2f8b0 [core] i18n of the desktop libs
* 08eb267 HUE-899 [beeswax] Query results page should have horizontal scroll bar
* 4dd8c24 [oozie] Examples owned by wrong user
* 5507de3 HUE-909 [oozie] Protect from invalid external action id
* b9fbce2 [core] Add notification to the admin when Oozie is not in good status
* 429100d HUE-867 [desktop] Fix fast tests
* 4fcb48b HUE-911 [jobbrowser] Can not see our own jobs when sharing is disabled
* 73a7db7 HUE-874 [oozie] Direct access to MR logs
* 2732b43 [doc] Adding missing package dependencies
* 85de749 HUE-867 [desktop] Ensure first user home directory is created
* daea7e2 HUE-873 [jb] Direct access to task logs
* 424cf6e HUE-873 [jb] Direct access to task logs
* 6e1e8c6 HUE-892 [desktop] Add a SPNEGO backend so that Hue can handle Kerberos authentication
* d26ce2b HUE-790 [jobsub] Remove old files from Hue1
* 80c9000 HUE-905 [beeswax] Result page rows should not have new lines
* d77516c HUE-903 [beeswax] Save results in an HDFS directory is broken
* 012fa17 HUE-902 [core] Add pyOpenSSL 0.11 to build
* bbdd9dc HUE-902 [core] Include pyOpenSSL in install automatically
* 7e0e01b HUE-802 [fb] Remove unused code
* d597232 [core] Fix postgresql regression.
* 9ec8b62 HUE-900 [oozie] File chooser missing when editing a node for 'jar path'
* b4cf5b5 HUE-894 [core] Log search
* 1e2d1a3 HUE-890 [jobsub] Unit test the frontend
* cbba991 HUE-890 [jobsub] Unit test the frontend
* fb4d8dc HUE-893 [fb] Fix the move dialog
* 9f0a8b8 HUE-753 [jobbrowser] Re-enable unit tests for job browser
* 1bc3e17 HUE-753 [jb] Re-enable unit tests for job browser
* 8c3abcd HUE-889 [oozie] Smarter file chooser in Workflow editor
* 6d5418f HUE-882 [core] Add stack trace and logs link to 500 and PopUpExceptions pages
* 032e841 HUE-885 [core] Update knockout.js to 2.1.0
* 0dfb9a0 [jobsub] Fix test_job_design_cycle test
* a388dee HUE-887 [useradmin] Fix missing hue permissions
* cb312c2 HUE-865 [jobsub] Bulk operations
* 4e7b2fe HUE-839 [core] Javascript test framework
* 8246208 HUE-887 [oozie] Fielbrowser doesn't understand path
* 026b31e HUE-887 Fix fileuploader popup across website
* 13ace6b [jb] Fix alignment of the Upload button dropdown
* 2a23098 HUE-881 [useradmin] Case insensitive search boxes on add/edit group page
* f67f808 HUE-884 [fb] Invalid select all for bulk operation
* 3f8bcd3 HUE-883 [useradmin] Extended DB support
* fcbb211 Hue-883 [core] Improved support for transactional databases
* 233395c HUE-872 [useradmin] Default group has access to all apps initially
* 2ea4dc1 HUE-876 [oozie] Setup Oozie Shared Lib for tests
* bb60a98 HUE-717 [core] Repetitive HTTP requests on each page
* bd3782c HUE-876 [oozie] Add a warning if oozie share lib is not installed
* c832574 HUE-835 [fb] Bulk operations
* c522e30 HUE-877 [oozie] Workflow examples require Oozie Share Lib activation
* a7a9313 HUE-879 [core] 500 error can be displayed in Hue Server Logs page
* ae0e8ba HUE-838 [jb] Create new file button
* 8b4a015 HUE-864 [oozie] Allow a read only user on the dashboard
* fb7e1c6 HUE-775 [fb] New temp directory for upload
* cff40ec HUE-775 [fb] Remove useless underscore from previous commit
* be9f646 HUE-775 [fb] Upload zip file through filebrowser.
* 21a6f2a HUE-866 [beeswax] Next/Previous buttons are half hidden
* 127e099 HUE-833 [oozie] Add DistCp action
* dfad82c [oozie] Fix load Oozie examples
* 2e79e3e HUE-789 [core] Remove old files from Hue 1
* c5a540f [beeswax] Execute the create table SQL automatically instead of showing it
* b482cbb [beeswax] Convert template to Python 2.4
* cdc3127 [oozie] Bumping submission test timeouts to 15 minutes


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
