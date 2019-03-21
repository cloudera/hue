---
title: "2.0.0-beta"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -1999
tags: ['skipIndexing']
---

### Hue v2.0.0-beta, released Apr 10, 2012


This is a beta release of Hue 2.0.0, a major upgrade from previous Hue releases.
Hue 2.0.0 is compatible with CDH4 (Cloudera's Distribution Including Apache
Hadoop 4).


Notable Features
----------------

- Frontend has been re-implemented as full screen pages. Whole page loading has
  replaced the old "desktop" model. In this process, the new frontend is
  rewritten with jQuery and Bootstrap. This fixes memory leaks in older
  browsers. This also breaks compatibility of Hue SDK applications. (HUE-585,
  HUE-609)
- Hue accesses HDFS via WebHDFS or HttpFS. It no longer requires the Hue plugin
  on the NameNode and DataNodes. (HUE-610)
- Hue submits MapReduce jobs via Oozie. This fixes a security hole in the
  previous scheme of Hue directly running the client job jar. (HUE-611)
- Hue supports LDAP (OpenLDAP and Active Directory). Hue can be configured to
  authenticate against LDAP. Additionally, Hue can import users and groups from
  LDAP, and refresh group membership from LDAP. (HUE-607, HUE-614, HUE-615)
- Hue supports per-application authorization. Administrators can grant or limit
  group access to applications. (HUE-608)
- Hue has a new Shell application. Administrators can configure the types of
  shells (e.g. Pig, HBase, Flume) to be exposed by the Shell app. (HUE-141)
  * Hue runs on the Spawning web server by default, instead of the CherryPy web
    server, in order to provide asynchronous connection I/O for the Shell
    application.
- Hue File Browser supports decoding Avro data files. (HUE-1)
- Hue uses Maven to build its Java source. (HUE-424)
- Beeswax reduces its memory usage and allows configuration of maximum query
  result lifetime. (HUE-564)
- Hue installations can be made relocatable by invoking a script. (HUE-593)


Notable Bug Fixes
-----------------

- HUE-238. beeswax: result from "limit" query unavailable
- HUE-438. Making beeswax dependent on hive install
- HUE-457: Filebrowser cannot delete directories with spaces in the name
- HUE-506. Jobs submitted through Hue do not set LANG
- HUE-526. Clicking "Browse Table" on a Hive View in Beeswax launches MR job
- HUE-534. JobBrowser does not impersonate logged in user while killing or viewing jobs
- HUE-550. Switching to LIFO queue for Thrift connection pool
- HUE-551. Support a wider set of username characters
- HUE-553. Thrift pooled client is not thread safe
- HUE-555. Build should not require a system python-setuptools
- HUE-584. Shade Thrift jar
- HUE-586. log files have wrong permission
- HUE-606. Error when browsing a table with too many partitions
- HUE-624. [jobbrowser] Non-ascii character in job name causes error
- HUE-640. kt_renewer workaround for krb compat is a race


Compatibility
-------------

Hue 2.0.0-beta runs on CentOS versions 5 to 6, and Ubuntu 10.04 to 11.10.

Hue 2.0.0-beta is compatible with CDH4. Specifically:

- File Browser depends on Hadoop 0.23 (for WebHDFS/HttpFS).
- Beeswax is tested against Hive 0.8.1.
- Job Browser depends on MR1 (for the JobTracker plugin).
- Job Browser does *not* work with Yarn/MR2.
- Job Designer depends on Oozie, using the Oozie web service API.


Upgrade
-------

Upgrading from Hue 1.2.0 is supported, with the following caveats:

- Hue's configuration file has changed regarding the specification of the HDFS
  cluster, MR1 cluster and Yarn cluster. You also need to configure the Oozie
  URL for Job Designer. Please see the
  link:../manual.html[Hue Installation Guide] for more.
- Hue by defaults run on port 8888, not 8088.
- Hue 2.0.0 uses a different model for job designs. Old job designs will be
  automatically converted in a best effort. After the upgrade, the user may need
  to fill in more information (e.g. the Java main class) about their job
  designs.
- Custom Hue SDK applications will not render correctly in Hue 2.x, because the
  frontend Javascript framework (jFrame) has been replaced by jQuery and
  Bootstrap. The 2.0.0-beta release does not yet provide instruction on porting
  SDK applications from Hue 1.x.


Known Issue
-----------

- The contents in the Help application are out of date.


List of All Commits
-------------------

* HUE-425. Adding default taskScheduler and MR queue names to mini cluster.
* Added support to default tree row selection
* HUE-429. Make HueChart.Box's series events set all applicable series as arguments.
* HUE-427. Allow the stroke color of dots on HueChart.Line to be configurable
* HUE-424 - Hue Mavenization
* HUE-435. Traversing a file in File Viewer using the navigation buttons results in a file not found error
* HUE-437 - Fixing Main-Class of Beeswax jar
* HUE-326. Beeswax might be leaking file descriptors
* HUE-444. Error message during `make install'
* HUE-454. TaskTrackerNotFound error popup when viewing individual attempt
* No ticket. Hash update: widgets, jframe, more-behaviors
* HUE-449. tarball build changes after mavenization
* HUE-455. Add ability to specify separator to humanize_duration.
* No Ticket. JFrame hash update (minor css tweak)
* Adding metadata handling to HueChart.
* HUE-449. tarball build changes after mavenization [part2]
* [BUILD] Fixed compilation of static-group-mapping since update to CDH3b4 nightly.
* No Ticket. Picking up the hash for MooTools More.
* Pass empty array to HueChart.Data if data is undefined.
* Add method to manage creation of display value, integrate 'amplitude' metadata field.
* HUE-472. JFrame Gallery's icon is borked.
* HUE-473. Add ability to get the link for an app window and enter one in.
* HUE-433. Beeswax import table screen messed up.
* HUE-474. App Makefiles do not set APP_NAME correctly
* HUE-461. Clicking the Save As button in the file editor causes all changes to be thrown away.
* HUE-478. Including execution of 0.7 scripts in hive upgrade's README.
* HUE-482. The Shortcuts button (at top right of Hue UI) does not do anything.
* Updating jframe.hash.
* HUE-481. Vertical Scrolling in Help doesn't work
* HUE-483. Scrollable area for JFrame Gallery's view source is broken
* HUE-485. Provision a way to start mini_cluster with customized configs.
* No Ticket. JFrame, MooTools More, and ART.Widgets hash updates
* HUE-487. Including the point value in HueChart.Box selection event parameter object.
* HUE-438. Making beeswax dependent on hive install.
* Update widgets.hash.
* No Ticket. Minor CSS fix for z-index positioning for CSS buttons.
* HUE-488. Add profiler for behavior and jframe filters.
* HUE-486. Enable renaming of top-level configs, and add a path for performing search/replace config upgrades
* [DOC] Updated dev and build dependency.
* HUE-492. Change amplitude calcuation in HueChart.Box to use toFloat rather than toInt.
* Small date display and rounding corrections in HueChart.
* [BUILD] Fixed Hadoop and Hive versions in pom.
* Update jframe.hash.
* HUE-495. HueChart.Box: Use chartStartTime and chartEndTime from metadata.
* HUE-494. Adding units to metadata and displaying in tip if present.
* HUE-498. Add shortenTick method to shorten tick labels on y-axis.
* HUE-500. Add information about Hue profiling to README.rst
* [BUILD] Use maven artifacts from cdh3u0.
* Re-ordering comments for database configuration.
* No Ticket. Updating Behavior hash.
* HUE-509, HUE-510
* HUE-506. Jobs submitted through Hue do not set LANG
* Update widgets.hash
* No Ticket. Updating Behavior hash.
* HUE-517. Tips should not be instantiated once per use
* HUE-521.  version specification duplication
* HUE-525. Implementing NOCREPO in Hue build.
* HUE-527. Small changes for HueChart.Area, Box, and js to repair Area functionality.
* HUE-528. Make deprecation work in Hue.JFrame.Chooser.
* HUE-529. Add vis.render() to HueChart.Circle setupChart method.
* HUE-530. Load Hue.JFrame.Chooser as part of initial Hue load.
* HUE-532. HDFS thrift plugin port is also in thriftfs-site.xml
* HUE-533. hue-plugin thriftfs test failure
* HUE-534. JobBrowser does not impersonate logged in user while killing or viewing jobs.
* HUE-496. Make hue support newer versions of python.
* HUE-540. Special characters in username breaks useradmin app.
* HUE-546. jobsubd should use a single file for Hadoop delegation tokens when submitting jobs
* HUE-489. Use Django 1.2 way to specify databases.
* HUE-1. Add avro file viewer support to File Browser.
* HUE-299. dump_config header links should point to the sections
* HUE-548. App tarballs contain invalid symlink to the VERSION file
* HUE-469. 'make docs' returns 0 even on error, could use a more restrictive "find" expression
* HUE-238. beeswax: result from "limit" query unavailable
* HUE-550. Switching to LIFO queue for Thrift connection pool.
* HUE-542. File browser sorting by size inconsistent.
* HUE-363. jobbrowser job state should fit well in the table
* HUE-549. Fix avro filebrowser test to run on all Python versions.
* [DOC] Document that Hue requires asciidoc to do a full build
* HUE-551. Support a wider set of username characters
* HUE-141. Adding Shell app to Hue.
* HUE-141. Fixing test failure for Shell app.
* HUE-141. Fixing a syntax error in tests for the Shell app that causes failures in Python 2.4.
* HUE-552. Default to a more professional wallpaper
* HUE-553. Thrift pooled client is not thread safe
* [BUILD] Make Shell known as "hue-shell"
* [DOC] Fix MySQL backend configuration step
* Online Help files for Hue Shell
* HUE-554. Modifying Shell app to use credentials merger utility.
* HUE-457: Filebrowser cannot delete directories with spaces in the name.
* HUE-555. Build should not require a system python-setuptools
* [BUILD] The shell app should share the common version
* HUE-556. LifoQueue thrift_util.py doesn't work on Centos5's python 2.4
* HUE-557. useradmin test with funny name fails on py2.4
* HUE-558. Shell hangs if subprocess exits immediately.
* [BUILD] Reuse the DESKTOP_PLUGIN_JAR variable for build target
* HUE-559. The setuid binary in the shell app should be in a build directory.
* HUE-561. Spawning creates incorrect log file names
* HUE-560: Shell app should have per-shell configurable environment variables.
* HUE-562. Spawning web server logs extraneous access log messages to stderr.
* HUE-563. Hue management commands should be backwards-compatible.
* [Doc] Fix broken release notes link
* HUE-565. Hue tarball contains duplicated js libraries
* Removing reference to Health application in doc, since it's not in Hue.
* HUE-570. shell error when user has no access to any individual shell
* HUE-575. New version of IPython is causing Jenkins build to fail
* HUE-569: Making Hue work in IE9
* HUE-574: Making Hue start over SSL on Python 2.4.
* Adding missing packages to README.rst.
* HUE-578: Shell app should have more comprehensive logging for I/O
* HUE-582. Improve jobbrowser's resilience to timing-related test failures
* HUE-330: Hue IE8 memory leaking
* Modifying Makefiles to not call scripts with shebangs directly.
* Add maven options parameters
* HUE-592. Update hue-plugins to work with new counter methods
* [Build] Upgrade hadoop version to cdh3u2-SNAPSHOT
* HUE-564. Improve handling of beeswax active queries and expiration
* HUE-593. Script to relocate a hue installation
* HUE-586. log files have wrong permission
* HUE-598. Hue Datanode plugin doesn't reopen connection when registering with NameNode.
* Remove unnecessary warning for IE users.
* HUE-597. Show task diagnostic info for an attempt in Job Browser.
* HUE-584. Shade Thrift jar.
* Links to the relative parent in pom.xml.
* CDH-3689: Fix help links to point to CCP instead of wiki
* HUE-600. Update Beeswax's hive_metastore.thrift interface spec
* [Build] Hue doesn't build on Ubuntu 11.10
* HUE-526. Clicking "Browse Table" on a Hive View in Beeswax launches MR job
* HUE-526. Clicking "Browse Table" on a Hive View in Beeswax launches MR job
* HUE-602. Updated DatanodePlugin to reflect HDFS-2654.
* HUE-606. Error when browsing a table with too many partitions
* HUE-604. [Build] Jenkins build should remove old hadoop and hive directories
* [build] Upgrade to build against CDH3u3
* HUE-607. LDAP/PAM authentication
* Downgrading python-ldap to version 2.3.13
* [ui] Convert Hue to jQuery
* HUE-614. Add a mechanism to sync Hue DB with Unix passwd and groups
* HUE-615. Basic group management
* Add generic REST client library
* [webhdfs] Be able to browse filesystem via webhdfs
* HUE-616. Remove desktop-test.db from source control
* HUE-608. ACLS for Hue apps
* [filebrowser] Fix filebroser to be compatible with webhdfs
* Add group ID parameters to Unix sync
* [jobsub] Add configuration for "oozie_url"
* [build] Allow HADOOP_HOME to point to a CDH4 hadoop
* [jobsub] Remove java from jobsub
* [test] Skip cleanup of pseudo HDFS tmp dir if $MINI_CLUSTER_CLEANUP is `false'.
* [thriftfs] Remove irrelevant parts of thriftfs plugin
* [build] Point pom to build against CDH4 nightly jars
* [build] Updated version to 2.0.0
* [build] Upgrade thrift to 0.7.0
* [Beeswax] Fix Hive-0.8.1 compatibility
* [beeswax] Show welcome screen (when metastore is empty)
* [hadoop] Fix unit test for webhdfs
* [core] Python 2.4 treats HTTP 201 as error
* [filebrowser] Avoid using hashlib (py2.4 compat)
* Edit groups by permission
* Adding models to support LDAP integration
* Configuration parameters for integration with LDAP and Active Directory
* Command-line utility for importing users and groups from LDAP
* Revert "Command-line utility for importing users and groups from LDAP"
* [build] Build does not require $HADOOP_HOME
* Command-line utility for importing users and groups from LDAP (Fixed test)
* Removing executable permission from mako files
* Initial support for jHueSelector
* Support upgrades from Cloudera Enterprise 3.5 or Hue 1.2
* Add a group edit control to the Create/Edit User page
* Fix exception when importing a user that has a naming collision in Hue
* Add a configurable default user group
* [test] Have pseudo_hdfs4 start MR1
* [app_reg] Use `json' if present on system, default to `simplejson'
* HUE-624. [jobbrowser] Non-ascii character in job name causes error
* [beeswax] Conditionally show the "save" form only if there's no error
* Make PopupError render correctly as json
* [test] Temporarily disable broken tests
* [useradmin] Fix bug in filter clearing
* Useradmin actions are now in modal windows
* HUE-621 restyle of beeswax index page
* HUE-618 fixed Check configuration page
* Migrated about sections to common header and footer, converted logs to mako
* HUE-620 first attempt to restore the config check icon
* [frontend] Add knockout and jqueryui-autocomplete
* [frontend] Fix datatables style to match with bootstrap's
* Remove executable bits on regular files
* [desktop] Allow MultiForm to work with ModelForm
* [hadoop] Add config for Yarn cluster, Mapred port, and `submit_to' param
* [webhdfs] Make DEFAULT_USER an attribute of the filesystem object
* [webhdfs] Add copy method to copy a file
* [desktop] Add content-type support to REST library
* [hadoop] Allow Hdfs.urlsplit to deal with viewfs (federation)
* [hadoop] Add configuration for fs.defaultFS
* [filebrowser] HTML-escape the contents of the fileviewer
* HUE-206 (partial). Browsing a large directory slow for IE
* [doc] Update README
* [jobsub] Initial rewrite
* [build] Hue2 does not rely on crepo
* [beeswax] Run beeswax server using the specified HADOOP_BIN
* [test] Test cluster to set FS_DEFAULTFS.
* [hadoop] Change default location of HADOOP_CONF_DIR to `/etc/hadoop/conf'
* [dev] Update the development version of the hue config
* [useradmin] Fix useradmin test after modal form changes
* HUE-621 Fixed welcome screen
* HUE-629 the very first login warns about creating a superuser
* [conf] Remove oozie from the [hadoop] section
* [doc] Partial update to Hue manual
* Improved user admin experience for non-superusers
* HUE-628 Added user group selection on creating/editing user
* HUE-626 fixed stylesheet for upload button
* HUE-623 removed strict client side validation on the query
* Fixing a merge problem on user list.
* Fixed problem with jHueSelector and IE7+
* [beeswax] Undo local configuration change in commit fe69c15
* [docs] Fix ascii doc table syntax to be compatible with 8.1.0
* [hadoop] webhdfs should have security_enabled property
* [core] Add urllib2_kerberos library
* [core] Add kerberos (python-binding) library
* [core] Fix urllib2_kerberos's logging
* [webhdfs] Client can now talk to a secured HDFS
* [test] Remove stale (and failing) jframe test
* [doc] More doc enhancement
* Pulling back in some changes that got accidentally deleted
* Use correct email field when extracting info from LDAP
* Add a couple LDAP-related parameters to hue.ini
* Use the correct EXTERNAL enum when logging in via a non-default backend
* HUE-640. kt_renewer workaround for krb compat is a race
* [hadoop] Remove NN_HTTP_PORT (again)
* [doc] Add krb5-devel build requirement (for python kerberos library)
* [ui] Fix typo on first login screen
* [conf] Add a useradmin configuration sectino to ini file
* [jobsub] Add security_enabled config for Oozie security
* HUE-632. Hue to talk to Oozie securely
* HUE-619. Hue to use port 8888 by default
* [jobsub] Clean up old files
* [jobsub] Job history should link back to design
* [jobsub] Fix terminology: rename `workflow' to `design'
* [jobsub] Show paths in workflow info as hdfs links
* [webhdfs] rename operation should handle a relative destination path
* [webhdfs] Handle quoting of weird filename characters
* Put the first user to login in the default group
* Fix the logic determining the superuser when using the LdapBackend
* Add a bit of error checking when setting up an LDAP connection
* Miscellaneous cleanup in useradmin views
* Add an LDAP user to the default group at import time
* Deleting a user should also delete its user profile
* Permissions and default group-related tests
* [useradmin] Superuser shouldn't be able to delete self
* [test] Use random ports for pseudo-distributed DN in testing
* [core] Add tidylib, a python wrapper for libtidy for HTML validation
* [core] Add HTML validation in debug mode
* [ui] Add favicon url mapping
* [jframegallery] Remove jframegallery
* [core] Remove depender usage
* [core] Remove depender external dependency
* Let syncdb work against mysql
* [jobsub] Add more properties to the oozie property autocomplete
* [jobbrowser] Fix broken link to jobsub
* HUE-633. [jobsub] Port examples to new design models
* [test] Work around a webhdfs redirect bug in test
* [doc] document dependency on libldap2-dev
* HUE-648. [fb] filebrowser.views.view() makes too many filesystem calls
* HUE-635 Porting to Bootstrap 2
* HUE-647 changed my home link and breadcrumbs
* Various fixes: HUE-657, HUE-650, HUE-649, HUE-646, HUE-645, HUE-652, HUE-642 and HUE-643
* Improved 'well' spacing and remove Clear button from filter
* [jobsub] Remove unused files
* [filebrowser] Unify breadcrumb display
* HUE-660 fix for scroll in Google Chrome
* Fix error page style
* HUE-661 Beeswax query now remembers initial value
* Fixed a datatables conf problem on Jobsub history page
* HUE-659. [config] Unite the various *.ini files
* [test] Add a bash shell for developer mode to test shell interactions
* [core] Do not skip apps because HADOOP_BIN is not there
* HUE-662. [config] Each Hadoop hdfs/mr/yarn cluster to define its own env
* HUE-663 jobbrowser styled
* [test] Fix jenkins script to clean up the correct hadoop directory
* [HUE-658] [fb] Hue should display hadoop fs errors in a popup and not in a 500
* [jobsub] Authenticate to Oozie in non-secure mode
* [build] Do not overwrite an existent pseudo-distributed.ini
* HUE-664. [ui] Jobsub design edit page mis-styled
* [ui] Contents in <pre> tags need to be html-escaped
* HUE-666. [ui] Jobbrowser attempt page unstyled
* [build] Markdown requires elementtree when generating docs
* [ui] Unify site name as `Hue' (not jHue or Hue2)
* [build] Set version 2.0.0-beta
* [doc] Fix screenshots in user manual
* [ui] Beeswax clone query button gone
* [jobsub] Migration script needs to import simplejson for py2.4
* [doc] Document Oozie proxyuser configuration in manual
* [jobsub] Do not create sample directories as `hdfs'
* [doc] Fix broken link to CDH package installation guide
* [jobsub] Fix data upgrade from hue 1.x to properly convert streaming properties
* [doc] Release notes for 2.0.0-beta


Contributors
------------

This Hue release is made possible thanks to the contribution from:

- Aaron Newton
- Aaron T. Myers
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
