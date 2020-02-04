---
title: The Hue 4 user interface in detail
author: admin
type: post
date: 2017-07-20T14:56:51+00:00
url: /the-hue-4-user-interface-in-detail/
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
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
categories:
  - Version 4

---
Aloha User Experience enthusiasts,

With the [Hue 4 release][1] we introduced a modern UI on top of our existing software to facilitate data discovery and analysis on premise and in the cloud.

# The new UI organization

The new layout simplifies the interface and is now single page app, and this makes things snappier and unifies the apps together.

<img src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.04.28.png"/>

From top to bottom we have:

  * A completely redesigned top bar, with a quick action (big blue button), a global search and a notification area on the right
  * A collapsible hamburger menu that offers links to the various apps and a quick way to import data
  * An extended quick browse on the left
  * The main app area, where the fun is 🙂
  * A right Assistant panel for the current application. It's now enabled for the editors, and in case of Hive for instance, it offers you a live help, a quick browse for the used tables in your query, and much more: if your Hue instance is connected to a SQL Optimizer service like <a href="https://optimizer.cloudera.com" target="_blank" rel="noopener noreferrer">Cloudera Navigator Optimizer</a>, it can offer [suggestions on your queries][2]!

Various applications have been grouped into 4 main conceptual areas:

  * [Editor:][3] The goal of Hue’s Editor is to make data querying easy and productive. It focuses on SQL but also supports job submissions. It comes with an intelligent autocomplete, search & tagging of data and query assistance.
  * [Browsers:][4] Hue’s Browsers let you easily search, glance and perform actions on data or jobs in Cloud or on premise clusters.
  * [Dashboard:][5] Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.
  * [Scheduler:][6] The application lets you build workflows and then schedule them to run regularly automatically. A monitoring interface shows the progress, logs and allow actions like pausing or stopping jobs.

The work on it started a couple of years ago and was incremental, and we applied a lot of the outcome of both design studies and customer feedback.

<img src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.04.18.png"/>

A few [exotic locations][7] helped on getting the inspiration:

<img src="https://cdn.gethue.com/uploads/2016/12/IMG_5670-1024x768.jpg"/>

Here it is, in all of its beauty 🙂

[<img src="https://cdn.gethue.com/uploads/2016/04/hue4_editor.png" />][8]

&nbsp;

# Quick search and browse

The new search bar is always accessible on the top of screen, and it offers a [document search and metadata search][9] too if Hue is configured to access a metadata server like <a href="https://www.cloudera.com/products/product-components/cloudera-navigator.html" target="_blank" rel="noopener noreferrer">Cloudera Navigator</a>.

<img src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.24.07.png"/>

The improved quick browse on the left side of the screen now offers many more data sources and it is now enabled for Hive and Impala (like it was before) but also for HDFS, S3, HBase, Solr collections and Hue documents.

<img src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.29.59.png"/>

&nbsp;

# Default action / landing page

In Hue 4, every user is able to set their own preferred main action (the big blue button) and landing page. It just takes one click on the star next to the application name, like in this case next to Hive

<img src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-18-19.20.57.png"/>

The next time you will login, you will land directly into the Hive editor and a new query is always one click away.

&nbsp;

# Backward compatible

The older Hue 3 UI is still there and it's easily reachable just by clicking on 'Switch to Hue 3/4' from the user menu.

<img src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-15.28.12.png"/>

<img src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-15.28.24.png"/>

Administrators can also decide to enable/disable the new UI at a global level on the <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank" rel="noopener noreferrer">hue.ini or CM safety valve</a>

<pre><code class="bash">[desktop]

\# Choose whether to enable the new Hue 4 interface.

is_hue_4=true

</code></pre>

If you look at your browser's address bar, you will notice that all the URLs with the <span class="emphasis"><em>/hue</em></span> prefix point to Hue 4. It is possible to just remove the prefix and land on the Hue 3 version of the page, e.g. /hue/editor (Hue 4) → /editor (Hue 3)

Now go try it on [demo.gethue.com][10] or <a href="https://gethue.com/hue-4-and-its-new-interface-is-out/" target="_blank" rel="noopener noreferrer">download it</a> if you haven't done it already!

Onwards!

 [1]: https://gethue.com/hue-4-and-its-new-interface-is-out/
 [2]: https://gethue.com/hue-4-sql-editor-improvements/
 [3]: https://gethue.com/sql-editor/
 [4]: https://gethue.com/browsers/
 [5]: https://gethue.com/search-dashboards/
 [6]: https://gethue.com/scheduling/
 [7]: https://gethue.com/category/team/
 [8]: https://cdn.gethue.com/uploads/2016/04/hue4_editor.png
 [9]: https://blog.cloudera.com/blog/2017/05/new-in-cloudera-enterprise-5-11-hue-data-search-and-tagging/
 [10]: http://demo.gethue.com
