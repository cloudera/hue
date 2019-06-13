---
title: "2.5.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -2050
tags: ['skipIndexing']
---

### Hue v2.5.0, released Monday 15th, July 2013

Hue, http://gethue.com, is an open source UI for Hadoop and its satellite projects.
It makes the whole platform (e.g. HDFS, MapReduce, Hive,  Oozie, Pig, Impala, Solr...) easy to use and
accessible from your  browser (e.g. upload files to HDFS, send Hive queries from a Web editor,
build workflows with Drag & Drop... all within a single app).


Notable Features
----------------

- HBase Browser application is tailored for quickly browsing huge tables and accessing any content.
  You can also create new tables, add data, modify existing cells and filter data with the auto-completing search bar.


Notable Fixes
-------------

- HUE-1109 [beeswax] Hive Server 2 save results
- HUE-1376 [beeswax] Autocomplete doesn't work after the 'where' keyword
- HUE-1135 [pig] Options support
- HUE [beeswax] Saved queries are renamed to None
- HUE-1115 [impala] Support multi db
- HUE-641 [jb] Auto-refresh the Job Browser views
- HUE-1150 [pig] Links to inputs/outputs/MR jobs
- HUE-1256 [core] Cache the HA jt


Compatibility
-------------

Runs on CentOS versions 5 to 6, Red Hat Enterprise Linux (RHEL), and Ubuntu 10.04 to 12.10.

Tested with CDH4.3. Specifically:

- Hadoop 0.20 / 2.0.0
- Hive 0.10.0
- Oozie 3.3
- HBase 0.94
- Pig 0.11
- Impala 1.0 / 1.1
- Solr 4.0
- Sqoop2 1.99.2

Supported Browsers:

* Windows: Chrome, Firefox 3.6+, Internet Explorer 9+, Safari 5+
* Linux : Chrome, Firefox 3.6+
* Mac: Chrome, Firefox 3.6+, Safari 5+


List of 85 Commits
-------------------

 * aeccb34 [doc] Add HBase app in the README
 * 2aafca3 HUE-1337 [impala] Support refresh from 1.0 and 1.1
 * ddc24ea Revert "HUE-1337 [impala] ResetCatalog() is deprecated in 1.1"
 * d3ab937 [hbase] query reload fix
 * 11209c6 [hbase] Remove dead code failing to be parsed by babel
 * 2e250f8 HUE-1377 [hbase] Improve app icon
 * 16ae824 [hbase] Remove non ascii characters
 * 68ee759 [hbase] Add to app makefile
 * 03d097d [beeswax] revert regenerate_thrift.sh
 * 2bdfaa1 [hbase] cleanup regenerate_thrift.sh
 * 2d45ab9 [hbase] Initial Commit
 * 90bbe8d [beeswax] Document partition browsing limit option
 * 62caa93 [core] app_reg syncdb should use the hue.ini properties
 * 7565503 HUE-1266 [core] Add 'hue version' command
 * 9d42c9c [pig] Fix wrong Fs impersonation
 * f509c90 HUE-1368 [pig] Prettify main layout
 * 683ced1 HUE-1376 [beeswax] Autocomplete doesn't work after the 'where' keyword
 * 3dfb2c7 HUE-1332 [beeswax] Smarter escaping of semicolon
 * 767bcf9 [oozie] Minor UX cleanup
 * 3d0be8a [beeswax] Make create database test more robust
 * 5a8d816 [beeswax] Support HiveServer2 PLAIN SASL authentication
 * d2b994d HUE-1233 [core] should be possible to configure user id into which supervisor drop privs
 * bf3beff HUE-1281 [core] Remove unused ext-py depdencies
 * 1f2c714 HUE-1337 [impala] ResetCatalog() is deprecated in 1.1
 * 85e63ff HUE-1135 [pig] Options support
 * 3f800fd [beeswax] Saved query are renamed to None
 * 2883d30 [doc] Removed old links, bad tables, updated graphics, new search doc.
 * 4bfc9c6 HUE-1115 [impala] Support multi db
 * 900e639 HUE-1321 [oozie] Shell or sqoop arguments missing in import workflow
 * f469059 HUE-1316 [oozie] Unable to use select popup box to change workflow after importing
 * 33c60c9 HUE-1338 [search] Support both plain text and json response from Solr
 * ce1c1ed [beeswax] Create table with invalid data format is now valid
 * d47bc5e [core] Detail HA howto configuration in hue.ini
 * 3a28455 [beeswax] Beeswax host server should appear in dump_config
 * a3cde08 [fb] Fix the upload a file test
 * e817179 HUE-1072 [jb] Better progress bar
 * b2dbfb9 HUE-1159 [jb] MR2 Layout is broken by task and attempt IDs length
 * 144090d HUE-1150 [pig] Links to inputs/outputs/MR jobs
 * 0948e6d HUE-1349 [search] Save facets btn does not always show up
 * 95c716f HUE-1361 [jobbrowser] Finished jobs are said to be running
 * 4d61896 HUE-641 [jb] Auto-refresh the Job Browser views
 * 5ad4ec2 HUE-1335 [search] In place editing of facets and sorting fields
 * 87a713e HUE-641 [jb] Auto-refresh the Job Browser views
 * 0b15a7b HUE-1340 [jb] NoReverseMatch error in job page
 * 3d0aab2 [oozie] Fix refresh or workflow started by coordinator in dashboard
 * 4606538 HUE-1347 [search] Not remembering collection after a trip to the customize collection page
 * 445f04d [fb] Fix upload file and archive tests
 * 1cf0ceb HUE-1331 [core] Update calculator example
 * 4dbf93b HUE-1333 [core] Upgrade to knockoutjs-2.2.1
 * f13a5f1 HUE-1339 [pig] UI treats numbered variables as parameters
 * 90cf5fd HUE-1336 [pig] Call data collection on routie changes
 * 6daa2fb HUE-1246 [pig] Change name of default saved script
 * 18dccfd [fb] Fix error message when uploading on already existing destination
 * b58f58f HUE-1006 [beeswax] Support download of large files
 * 1d5fc18 HUE-1246 [pig] Change name of default saved script
 * 68eaa55 HUE-1322 [useradmin] Add support for POSIX LDAP Groups
 * f9cf620 HUE-1329 [search] Improve label of range facets
 * 4b8098f [search] Disabled collection should not appear in the search page
 * 8270447 [fb] Fix upload test permissions
 * 891fbea HUE-1327 [search] disallow changing of collection index to non-existing index
 * fca1c64 HUE-1326 [search] Date facets should filter by range
 * c340157 HUE-1256 [core] Cache the HA jt
 * 72a17ef HUE-1165 [pig] Logs with MR2
 * 4ba5fe9 HUE-1178 [jb] Smarter logic for getting MR2 job information
 * 30d7669 HUE-1280 [fb] Inline download and preview of images and pdf mimetype
 * e2a2fa7 HUE-1269 [fb] Did you know about trash activation
 * f601e76 HUE-1286 [impala] Support settings with HiveServer2 API
 * 5529a9a HUE-908 [core] User/group membership should be delegated to the back-end
 * e2b4073 HUE-1311 [fb] Editing a file corrupt it in some way
 * 40d046f [core] Home urls should be standard with a trailing slash
 * 55d077a HUE-1240 [beeswax] Save a query result when using HiveServer2 interface
 * d55adbc HUE_APP_REG_DIR and HUE_PTH_DIR configurable at compile time
 * 3b0ed99 HUE-1273 [pig] Confirmation popup when leaving unsaved script
 * f6d480d HUE-1314 [shell] Prompt line is not wide enough
 * 3917dcf HUE-1320 [core] Drop support for IE8 and migrate to jQuery 2
 * 12d574a HUE-1319 [core] Upgrade to FontAwesome 3.2
 * 5713568 HUE-1292 - [core] separate core app pth and installed app pth files
 * 5097769 [core] Set version to 2.5
 * 3472ecf [doc] Integrate with existing doc
 * ac4055b [doc] Add user guide to the docs
 * 0f937c8 [core] Revert original README from search README
 * fbc93b4 [about] Add link to Hue website
 * aee2add [doc] Add 2.4 release notes
 * 9bc7f39 HUE-1313 [core] Unicode error in check_config



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

