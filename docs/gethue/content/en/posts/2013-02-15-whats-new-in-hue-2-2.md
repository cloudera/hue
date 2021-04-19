---
title: What’s new in Hue 2.2
author: admin
type: post
date: 2013-02-15T05:00:00+00:00
url: /whats-new-in-hue-2-2/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/48706834468/whats-new-in-hue-2-2
tumblr_gethue_id:
  - 48706834468
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
categories:

---
This post is about the new release of [Hue,][1] an open source web-based interface that makes [Apache Hadoop][2] easier to use, that’s included in [CDH4.2][3].

Hue lets you interact with Hadoop services from within your [browser][1] without having to go to a command-line interface. It features a file browser for HDFS, an Apache Oozie Application for creating workflows of data processing jobs, a job designer/browser for MapReduce, Apache Hive and Cloudera Impala query editors, a Shell, and a collection of Hadoop APIs.

The goal of this release was to add a set of new features and improve the user experience. Read on for a list of the major changes (from [304][4] commits).

### Oozie Application

With the Oozie Application you can chain jobs and schedule them repeatedly without having to write XML anymore. Workflow and Coordinator management got extra focus and now matches all the [Oozie][5] functionalities:

  * The workflow editor supports [Drag & Drop][6] and was restyled.
  * The coordinator page was redesigned with a wizard and data can be specified by range.
  * The dashboard displays any workflow as a graph and refreshes itself dynamically.
  * All the Oozie actions are supported (addition of Sub-workflow, DistCp, Email, Fs, Generic).
  * Forks can be converted to decision nodes.
  * A read-only user can access the dashboard.
  * A workflow or a coordinator can be resubmitted from specific steps.
  * Existing XML workflow definition can be imported.
  * The dashboard provides direct access to task logs of any action.

[<img class="aligncenter wp-image-20565" title="hue1" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue1.png" width="600" height="372" />][7]

<p class="center-align">
  <strong>Drag & Drop Workflow Editor<br /> </strong>
</p>

[<img class="aligncenter wp-image-20566" title="hue2" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue2.png" width="600" height="307" />][8]

<p class="center-align">
  <strong>Workflow Dashboard</strong>
</p>

[<img class="aligncenter wp-image-20569" title="hue3" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue3.png" width="600" height="221" />][9]

<p class="center-align">
  <strong>Coordinator Wizard</strong>
</p>

[<img class="aligncenter wp-image-20571" title="hue4a" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue4a.png" width="300" height="213" />][10][<img class="aligncenter wp-image-20572" title="hue4" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue4.png" width="300" height="222" />][11]

<p class="center-align">
  <strong>Rerun a Workflow (left) or a Coordinator (right)</strong>
</p>

### Beeswax/Hive Query Editor

A number of user experience improvements make it simpler to query your data with SQL:

  * Multiple databases are supported (tackling one of the most popular requests [HUE-535][12]).
  * Query editor is bigger, has line numbers and shows lines with error(s).
  * Running queries shows logs in Ajax and lets you scroll through them.
  * Query results page has a horizontal scroll bar and a quick column name lookup for accessing a certain column when they are many.

[<img class="aligncenter wp-image-20574" title="hue5" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue5.png" width="600" height="224" />][13]

<p class="center-align">
  <strong>Query Editor<br /> </strong>
</p>

[<img class="aligncenter wp-image-20575" title="hue6" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue6.png" width="600" height="304" />][14]

<p class="center-align">
  <strong>Wide result page with column lookup</strong>
</p>

## Impala Editor

[Impala][15] can now be queried from a new interface. More features will be supported when Impala is GA.

[<img class="aligncenter wp-image-20576" title="hue7" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue7.png" width="600" height="297" />][16]

<p class="center-align">
  <strong>Cloudera Impala query</strong>
</p>

### FileBrowser

FileBrowser lets you navigate and manage HDFS files in a UI. Its front end was totally redesigned and new filesystem operations were added. You do not need to use the `hadoop fs` command anymore!

  * Bulk operations for multiple deletions, changing of permissions or owner
  * Supports bulks operation recursively or not (e.g. chmod recursively a folder)
  * Upload archives (e.g. upload multiple files at once like the [Oozie sharelib][17])
  * Create a file and edit it

[<img class="aligncenter wp-image-20577" title="hue8" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue8.png" width="600" height="269" />][18]

<p class="center-align">
  <strong>Bulk editing</strong>
</p>

### JobBrowser

JobBrowser lists MapReduce jobs with their statistics and statuses. It was prettified and now supports MR2 jobs running over [YARN][19]:

  * MR2 jobs and their logs can be browsed.
  * Job logs can be accessed with one click.
  * Other apps like Beeswax and Oozie can now show the MR2 logs.

[<img class="aligncenter wp-image-20578" title="hue10" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue10.png" width="600" height="273" />][20]

<p class="center-align">
  <strong>MR1/MR2 job list and direct log access</strong>
</p>

### UserAdmin

Groups and Hue permissions can be assigned to the users through the UserAdmin application. Access to Hue applications can be customized for each user. (For example, Bob can only see and use the Oozie and Impala applications.) The application has been restyled and simplified, and is no longer accessible by default to non-superuser:

  * HDFS home of first/new/imported users is created automatically.
  * LDAP support now has wildcard search, user import by wildcard expression and [group syncing][21] by distinguished name.

[<img title="hue11" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/02/hue11.png" width="600" height="531" />][22]

<p class="center-align">
  <strong>Group permission editing</strong>
</p>

### Desktop

Desktop is the core library of Hue and every application is built on top of it. In this release, the user experience has been improved with more informative errors (now with stack traces and line numbers) and new status messages (such as when critical services like Oozie are down).

On the technical side, users can now upload files to a federated cluster, some XSS vulnerabilities were fixed, and database [greenlet][23] support was introduced for more performance. Hue now fully supports transactional databases like MySQL MyISAM and PostgreSQL.

Hue is also internationalized and available in English, French, German, Spanish, Portuguese (and Brazilian Portuguese), Korean, Japanese and simplified Chinese.

### Conclusion

With this 2.2 release, a big part of the Hadoop user experience gap was filled in.

The next [2.3][24] release will target users who wish to better leverage the multiple query solutions in CDH (Beeswax/Hive, Impala, and Pig). A new document model ([HUE-950][25]) would make each query (e.g. Hive query) searchable and shareable with your colleagues or importable into an Oozie workflow without any duplication. A trash and source control versioning system ([HUE-951][26]) is also discussed as well as Oozie bundle ([HUE-869][27]) integrations.

Many past feature and [bugs][28] were discussed on the [hue-user][29] list, so feel free to chime in! A [Hue meetup group][30] was created and it would be a pleasure to meet you in person and see how analyzing your data with Hadoop could be made easier.

 [1]: https://gethue.com
 [2]: http://hadoop.apache.org/
 [3]: https://ccp.cloudera.com/display/CDH4DOC/New+Features+in+CDH4
 [4]: https://gethue.com
 [5]: http://archive.cloudera.com/cdh4/cdh/4/oozie/
 [6]: http://blog.cloudera.com/blog/2013/01/dynamic-workflow-builder-in-hue/
 [7]: http://www.cloudera.com/wp-content/uploads/2013/02/hue1.png
 [8]: http://www.cloudera.com/wp-content/uploads/2013/02/hue2.png
 [9]: http://www.cloudera.com/wp-content/uploads/2013/02/hue3.png
 [10]: http://www.cloudera.com/wp-content/uploads/2013/02/hue4a.png
 [11]: http://www.cloudera.com/wp-content/uploads/2013/02/hue4.png
 [12]: https://issues.cloudera.org/browse/HUE-535
 [13]: http://www.cloudera.com/wp-content/uploads/2013/02/hue5.png
 [14]: http://www.cloudera.com/wp-content/uploads/2013/02/hue6.png
 [15]: https://github.com/cloudera/impala
 [16]: http://www.cloudera.com/wp-content/uploads/2013/02/hue7.png
 [17]: http://blog.cloudera.com/blog/2012/12/how-to-use-the-sharelib-in-apache-oozie/
 [18]: http://www.cloudera.com/wp-content/uploads/2013/02/hue8.png
 [19]: http://hadoop.apache.org/docs/r0.23.0/hadoop-yarn/hadoop-yarn-site/YARN.html
 [20]: http://www.cloudera.com/wp-content/uploads/2013/02/hue10.png
 [21]: https://issues.cloudera.org/browse/HUE-978
 [22]: http://www.cloudera.com/wp-content/uploads/2013/02/hue11.png
 [23]: http://greenlet.readthedocs.org/en/latest/
 [24]: https://issues.cloudera.org/secure/IssueNavigator.jspa?mode=hide&requestId=10258
 [25]: https://issues.cloudera.org/browse/HUE-950
 [26]: https://issues.cloudera.org/browse/HUE-951
 [27]: https://issues.cloudera.org/browse/HUE-869
 [28]: https://issues.cloudera.org/secure/IssueNavigator.jspa?mode=hide&requestId=10261
 [29]: https://groups.google.com/a/cloudera.org/group/hue-user/topics
 [30]: http://www.meetup.com/San-Francisco-Bay-Area-Hue-Users/
