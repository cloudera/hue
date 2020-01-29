---
title: Hue 4 and its new interface is out!
author: admin
type: post
date: 2017-07-13T22:15:37+00:00
url: /hue-4-and-its-new-interface-is-out/
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
sf_remove_promo_bar:
  - 1
categories:
  - Version 4
  - Release

---
Hi Big Data Explorers,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 4! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

In this latest updates of Hue, the focus was on providing a modern UI tailored for Analytics on prem or in the Cloud. More than [3000 commits][2] on top of [3.12][3] went in! Go grab the tarball release and give it a spin!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/releases/4.0.1/hue-4.0.1.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

Here is a list of the main improvements with links to more detailed blog posts. For all the changes, check out the [release notes][4] and for <span style="font-weight: 400;">a quick try open-up </span>[<span style="font-weight: 400;">demo.gethue.com</span>][5]<span style="font-weight: 400;">.</span>

&nbsp;

# Interface

The new layout simplifies the interface and is now single page and snappier.

Various applications have been grouped into 4 applications:

  * Editor
  * Browsers
  * Dashboard
  * Scheduler

Also:

* A top search bar and left assist help quick search and browse any data.
* Each user can set its favorite application as default action / landing page.
* The older Hue 3 UI is still available and Hue 4 is 100% backward compatible.
* The switch to the new Hue 4 UI can be decided at global level or each user can independently flip back and forth with one of the UIs as default.
* All the URLs with the <span class="emphasis"><em>/hue</em></span> prefix point to Hue 4, the one without still points to Hue 3.
* It is possible to just remove the prefix and land on the Hue 3 version of the page, e.g. /hue/editor (Hue 4) → /editor (Hue 3)

Read more about it in the <a href="https://gethue.com/the-hue-4-user-interface-in-detail/">Hue 4 UI post</a>.

<a href="https://cdn.gethue.com/uploads/2016/04/hue4_editor.png"><img src="https://cdn.gethue.com/uploads/2016/04/hue4_editor.png" /></a>

# Editors

## SQL

If multiple statements are present in the editor, the position of the cursor will determine what is the active statement that will be executed. In order to execute multiple statements (e.g. a series of CREATE tables) in sequence, they need to be manually highlighted or all selected via selected all shortcut (e.g. CTRL/CMD + A).

<a href="https://gethue.com/hue-4-sql-editor-improvements/">Read more about it here.</a>

<img src="https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif"/>

## Pig

New editor, some advanced use of declare and macros are not supported in the new Editor autocomplete. Past scripts have been converted to the new editor, or can be found in the Hue 3 UI.

## Job Designer

Actions like MapReduce, Java, Spark, Sqoop1 now show up in the new editor. Past scripts have been converted to the new editor, or can be found in the Hue 3 UI.

## Oozie and Scheduling

Saved queries from the Editor (e.g. Hive query) can be directly dragged and dropped into an action without the need of copying the files on HDFS manually.

# Browsers

## Job

New browser now combining the previous Job Browser and Oozie Dashboard. The app is now single paged and more intuitive to use. A mini-job browser is now available to see jobs without leaving the page.

## S3

Support V2 regions if your credentials are configured for V2 region. If you are configured for a V4 endpoint, you can only access buckets for that region’s endpoint.

# Misc

* Create a partitioned table from a file
* Creating a table in the importer now refreshes Impala metadata automatically
* The SQL autocompleter handles more advanced corner cases
* Load balancers on a different host than Hue now work with SSL
* Pagination added to the SQL query history
* Batch operation like create tables now happens as background tasks
* 500 bug fixes

&nbsp;

Onwards!

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][6] list or [@gethue][7]!

p.s.: in case the Dropbox link doesn't work on the network you are currently in, here's a [mirror of the release][8].

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: http://cloudera.github.io/hue/docs-4.0.0/release-notes/release-notes-4.0.0.html#_list_of_3215_commits
 [3]: https://gethue.com/hue-3-12-the-improved-editor-for-sql-developers-and-analysts-is-out/
 [4]: http://cloudera.github.io/hue/docs-4.0.0/release-notes/release-notes-4.0.0.html
 [5]: http://demo.gethue.com/
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue
 [8]: https://cdn.gethue.com/downloads/hue-4.0.1.tgz
