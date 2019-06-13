---
title: "1.2.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -1020
tags: ['skipIndexing']
---

### Hue v1.2.0, released Feb 21, 2011


Hue is a web interface for Hadoop, and a platform for building custom
applications with a rich framework. The 1.2.0 is a minor release, largely
focused on bug fixes and compatibility with the upcoming release of Cloudera's
Distribution for Apache Hadoop 3, beta 4.

Notable Changes and Caveats
---------------------------

Notable changes:

* Upgraded Django to 1.2
* Many HueChart improvements and bug fixes
* Upgraded included Hive from 0.5 to 0.7
* Beeswax no longer leaks file descriptors
* Renamed all JavaScript references of "CCS" to "Hue"

Caveats:

* Hue 1.2.0 only works with CDH3b4 or newer. CDH2 and earlier versions of CDH3
will not work.
* The included version of Hive has been upgraded from 0.5 to 0.7. This version
of Hive has changed the format for the metastore. Upgrading Hue 1.2 will require
you to upgrade your metastore version using the upgrade scripts included with
Hive.


List of All Bugs Fixed
----------------------
* HUE-349. Standardize the DOCTYPE
* HUE-290. Make JFrame work stand-alone
* HUE-270.  JFrame doesn't sweep content on refresh
* HUE-400. Beeswax sample installation assumes a `hue' user
* HUE-301. Break Partial Refresh into a stand-alone class
* HUE-406. Prevent Hue from fetching and displaying login box twice.
* HUE-290. Make JFrame work stand-alone
* HUE-260. Relinquish the keyboard when an error popup is closed.
* HUE-263. Add support for Resizable and Sortable Behavior Filters.
* Resolving Hive 0.5 -> Hive 0.6 API incompatibilities. Check whether DriverContext should be null in initialization of FetchTask.
* Switched to use the official CDH3b3 tarball.
* HUE-286. Adding notion of 'currentData' and selection handling to HueChart
* HUE-334. superuser can be deleted
* HUE-353.  Add livePathUpdate action to FormRequest
* HUE-322. CSS Modules
* HUE-308. Upgrade to Django 1.2
* HUE-261. When checking an element for draggability in the JBrowser header, ensure it's extended (IE can't extend embed tags).
* HUE-392. Proxy to support a blacklist
* HUE-266. Allow the user to choose their background as a preference.
* HUE-279. Various improvements to HueChart   Add handling for current offset parent in scrolled containter in pv.Mark.prototype.mouse   Add event bar and vector calculations to manually determine and fire wedgeOver/Out events.   Add getNormalizedForField function to HueChart.Data   Re-working event handling in HueChart.Box   Response to Nutron's review comments
* HUE-310. Handle large file upload.
* HUE-303. FIXED Popup windows try to select the text inside the first checkbox instead of the first text input
* HUE-413. Beeswax history page filter box not working
* HUE-412. Allow HueChart to deal with no data and pull out appropriate arrays representative of data series which are in the data object.
* [HUE-345] Provide way to override settings and classpath of minicluster.
* Adding Pygments-1.3.1.
* HUE-416. filebrowser: chown leads to an error page
* HUE-262. When cleaning up partials in partial refresh; do not attempt to remove line containers that don't exist.
* [HUE-354] beeswax_server.sh should put HADOOP_EXTRA_CLASSPATH_STRING on the Beeswax server's classpath
* HUE-11. jframegallery should show the html source
* HUE-409. Add info about secret key to Hue installation guide
* HUE-277.  supervisor.py doesn't drop group privileges
* HUE-271. Beeswax_server should have configurable java heap size
* HUE-365. jobbrowser test using the wrong job id
* HUE-315.  Make Protovis/HueChart work in IE
* HUE-350.  Change form.ccs-table_config to .ccs-table_config
* HUE-304. Cannot submit form from outside. Allow submitting any form from any link not only a child of the form itself.
* HUE-274. Add a filter for autocompletion
* HUE-302. Continued HueChart Improvments
* HUE-309. Hardcoded "default" hdfs cluster in config
* HUE-342.  Add draggable HueChart.Box selections and refactor date handling in HueChart
* HUE-282. beeswax hive_conf_dir should be /etc/hive/conf
* Add ability for livePath to work with form elements simply using name and value of the element.
* HUE-318.  SubmitOnChange doesn't work with checkboxes in IE.
* HUE-306. Add color management to HueChart.
* HUE-409. Add info about secret key to Hue installation guide
* HUE-393. Beeswax doesn't work with external metastore
* HUE-265. Add a linker that can hide its parent element.
* HUE-326. Beeswax might be leaking file descriptors
* HUE-441. stderr content changes to Hue server error log upon job completion (cherry picked from commit afd6f313b0621c407c3106a851c96572fac1811c)
* HUE-313. jobsub's list somewhat broken when searching with an owner name
* HUE-276. Implement a generic way to do mini graphs e.g. in table cells
* HUE-343. CSS Button Component
* [HUE-345] Provide way to override settings and classpath of minicluster (REVISED)
* HUE-353. Add livePathUpdate action to FormRequest
* HUE-311. Hue's conf.py should warn about variables without type= parameters that look like numbers
* HUE-415. beeswax doesn't honour hive_conf_dir
* HUE-360. Fixing issue with incorrect column definitions when creating tables manually in Beeswax
* HUE-359. Allow JFrame Gallery to read from multiple directories
* HUE-308. Upgrade to Django 1.2
* HUE-292. The Chooser JFrame linker `data-chooseFor` name selector now starts form the FORM parent element of the link if it exists
* Updating Hive jars from 0.5 to 0.6. Updating beeswax_server.sh, hive-default-xml.jar and tests to work with Hive 0.6.
* HUE-291. Make Partial Refresh honor response order.
* HUE-410. Add HueChart.Tips to change elementEnter/show functionality.
* HUE-432. Updating jframe.hash; Post load prompt popup works again (cherry picked from commit ca77ce137f47502a3d794181905cb8ab0f620fbe)
* HUE-263. Add support for Resizable and Sortable Behavior Filters.
* HUE-357. TreeView does not propagate errors. (cherry picked from commit c878a2bb6bc70593e52290afc8fa4ff2292c3cd7)
* HUE-287. hue.ini mentions PamBackend erroneously
* HUE-324. Add ability for HueChart.Box charts to determine what data series and value the mouse is over.
* HUE-405. Hue User Admin does not support non-ascii names
* HUE-336. kt_renewer doesn't work for root user
* HUE-224. Increase Beeswax's default $HADOOP_HEAPSIZE.
* HUE-402.  Fix DynamicTips reference in HueChart
* HUE-323. Make it possible for forms to specify an ajax target
* HUE-414. Running beeswax examples produces "unsaved" queries
* HUE-264. Add a timer filter that increments up every second.
* HUE-366. Update Beeswax Hive from 0.5 to 0.6. Updating Hive jars from 0.5 to 0.6. Resolving Hive 0.5 -> Hive 0.6 API incompatibilities in BeeswaxServiceImpl. Updating beeswax_server.sh, hive-default-xml.jar and tests to work with Hive 0.6.
* HUE-300. Adding a default log4j.properties file to the conf dir to make java logging for beeswax configurable
* HUE-200. Permission Denied error on Install Samples isn't propagated well
* [HUE-337] Load all libs AND all apps before binding configs.
* HUE-269. Disable "smart" typing in PostEditor
* [HUE-355] Move Hadoop settings in mini_cluster.py into constants.
* HUE-265. Add a linker that can hide its parent element.
* HUE-325.  Add ability for HueChart.Box charts to show DynamicTips
* HUE-401: Socket timeout of 2s is too aggressive in Thrift plugin
* HUE-347. Ensure CSS files are not cached
* HUE-418. Errant debug message in JT plugin
* HUE-434. Missing all icons
* HUE-266. Allow the user to choose their background as a preference.
* HUE-278. Add HueCharts library to Hue   Move Number.Files.js up to core/static   Add HueChart, HueChart.Area, .Box, .Line and corresponding package.yml changes   Add HueChart.Circle   Response to Nutron's review comments on HueChart.
* HUE-305. Cannot easily declare accesskeys for children of an HTMLTable. Allow simple declarative Keyboard shortcut creation from data-accesskey attributes.
* HUE-348. When FilterInput updates a zebra table, update the zebras
* HUE-399.  Allow HueChart to show time offsets rather than absolute dates
* HUE-275. Add dynamic filter to Beeswax table view
* HUE-417. Beeswax views with big white bar at the bottom
* HUE-358. Rename all instances of "CCS" to "Hue"
* HUE-395.  Various HueChart Improvements   -- Removing ms_from_first and using UTC ms values instead.   -- Integrating Shawn's getTicks method.   -- Adding ability to change HueChart data after initialization: setData and addDataSeries.
* HUE-264. Add a timer filter that increments up every second.
* HUE-335.  Hue throws 'background is not defined' error on start in IE.
* HUE-351. Move Behavior.SubmitOnChange form search to click/change event.
* HUE-461. Clicking the Save As button in the file editor causes all changes to be thrown away. (cherry picked from commit 3e260cd1509390092a5e1c161d4cb59fb584c987)
* HUE-471. Document Hive upgrade (cherry picked from commit e46985cf66b5ae5e1752d0be382abd455cda042e)
* HUE-478. Add the Hive 0.7 metastore upgrade scripts to Hue (cherry picked from commit 54f17f7e24e5c387f8a5a4d3b203e7c999a6e20c)
* HUE-476. Upgrade beeswax's Hive jars to Hive 0.7 from Hive 0.6.
* HUE-470. Thrift connection pooler breaks if thrift service inheritance is used (cherry picked from commit 03a91700c91501b4f5be6fe28f9daf9a8cf944a0)

Project Information
-------------------
Homepage: http://cloudera.github.com/hue/
