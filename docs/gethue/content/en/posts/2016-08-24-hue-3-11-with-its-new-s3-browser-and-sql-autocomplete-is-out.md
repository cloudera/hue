---
title: Hue 3.11 with its new S3 Browser and SQL Autocomplete is out!
author: admin
type: post
date: 2016-08-24T15:37:59+00:00
url: /hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/
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
sf_related_articles:
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
  - Release
---

Hi Big Data Adventurers,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 3.11! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

The focus was on the integration with Amazon Cloud Service and improving the SQL user experience. More than [700 commits][2] on top of [3.10][3] went in! Go grab the [tarball release][4] and give it a spin!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/releases/3.11.0/hue-3.11.0.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

Here is a list of the main improvements. For all the changes, check out the [release notes][2].

&nbsp;

&nbsp;

# S3 Browser

Hue can be setup to read and write to a configured S3 account, and users can directly query from and save data to S3 without any intermediate moving/copying to HDFS:

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      List, browse
    </li>
    <li class="listitem">
      Upload, download
    </li>
    <li class="listitem">
      Create external Hive table
    </li>
    <li class="listitem">
      Export query result
    </li>
    <li class="listitem">
      List S3 URI in Sentry
    </li>
    <li class="listitem">
      Set Oozie coordinator dependencies on S3 paths
    </li>
    <li class="listitem">
      Read more <a href="https://gethue.com/introducing-s3-support-in-hue/">about it here...</a>
    </li>
  </ul>
</div>

[<img src="https://cdn.gethue.com/uploads/2016/08/s3-upload-1024x483.png"  />][5]

#

# SQL Autocompleter

To make your [SQL editing][6] experience better we’ve created a brand new autocompleter. The old one had some limitations and was only aware of parts of the statement being edited. The new autocompleter knows all the ins and outs of the Hive and Impala SQL dialects and will suggest keywords, functions, columns, tables, databases, etc. based on the structure of the statement and the position of the cursor.

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      Brand new SQL grammar for Hive and Impala
    </li>
    <li class="listitem">
      Support all the major operations like SELECT, CREATE, DROP
    </li>
    <li class="listitem">
      Autocomplete UDFs and show their documentation
    </li>
    <li class="listitem">
      Weight keywords and columns by importance
    </li>
    <li class="listitem">
      Infer the types and propose compatible columns or UDFs
    </li>
    <li class="listitem">
      Read more <a href="https://gethue.com/brand-new-autocompleter-for-hive-and-impala/">about it here...</a>
    </li>
  </ul>
</div>

[<img src="https://cdn.gethue.com/uploads/2016/08/sql-autocomp-1024x480.png" />][7]

#

# SQL Result Refinements

The [SQL Editor][8] now brings a completely re-written result grid that improves the performances allowing big tables to be displayed without the browser to crash, plus some nifty tools for you.

<div class="itemizedlist">
  <ul class="itemizedlist">
    <li class="listitem">
      Result grid improvements
    </li>
    <li class="listitem">
      Timeout popup when Impala hangs on fetch result
    </li>
    <li class="listitem">
      Offer to fix certain rows
    </li>
    <li class="listitem">
      Search through the results
    </li>
    <li class="listitem">
      Excel download now has a progress status
    </li>
    <li class="listitem">
      Fixed resultset legend and header when scrolling throught the results
    </li>
    <li class="listitem">
      Column and type search
    </li>
    <li class="listitem">
      Optimized to display hundred columns
    </li>
    <li class="listitem">
      Export SQL query result to Solr
    </li>
    <li class="listitem">
      Read more <a href="https://gethue.com/new-features-in-the-sql-results-grid-in-hive-and-impala/">about it here...</a>
    </li>
  </ul>
</div>

[<img src="https://cdn.gethue.com/uploads/2016/08/result-refine-1024x542.png" />][9]

&nbsp;

#

# Solr Indexer

In the past, indexing data into Solr has been quite difficult. [The task][10] involved writing a Solr schema and a morphlines file then submitting a job to YARN to do the indexing. Often times getting this correct for non trivial imports could take a few days of work. Now with Hue’s new feature you can start your YARN indexing job in minutes. This tutorial offers a step by step guide on how to do it.

Read more [about it here...][11]

{{< youtube uS0MpzW0ep8 >}}

&nbsp;

&nbsp;

## Conferences

<img src="https://cdn.gethue.com/uploads/2016/06/IMG_4229-1024x768.jpg"  />

It was a pleasure to present at the Hadoop Summit in California:

- [New SQL Editor and Architecture][12]

## Team Retreats

[<img src="https://cdn.gethue.com/uploads/2016/08/IMG_4409-1024x768.jpg"  />][13]

- [Sun, green, craft beers and tacos in Portland, OR][14]

&nbsp;

## **Next!**

Next iteration (Hue 3.12, estimated for end of 2016) will focus on SQL improvements, job monitoring and more Cloud integration.

Hue 4 design will get more real, with the goal of becoming the equivalent of “Gmail for queries for Big Data”. The current apps are being unified into the [new Editor][8] and the whole Hue will become a single app in order to provide a much smoother and faster UX.

&nbsp;

Onwards!

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][15] list or [@gethue][16]!

&nbsp;

[1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
[2]: http://cloudera.github.io/hue/docs-3.11.0/release-notes/release-notes-3.11.0.html
[3]: https://gethue.com/hue-3-10-with-its-new-sql-editor-is-out/
[4]: https://cdn.gethue.com/downloads/releases/3.11.0/hue-3.11.0.tgz
[5]: https://cdn.gethue.com/uploads/2016/08/s3-upload.png
[6]: https://gethue.com/sql-editor-for-solr-sql/
[7]: https://cdn.gethue.com/uploads/2016/08/sql-autocomp.png
[8]: https://gethue.com/sql-editor/
[9]: https://cdn.gethue.com/uploads/2016/08/result-refine.png
[10]: https://gethue.com/hadoop-tutorials-season-ii-7-how-to-index-and-search/
[11]: https://gethue.com/easy-indexing-of-data-into-solr/
[12]: https://gethue.com/hadoop-summit-san-jose-2016-hue-sql-editor-and-architecture/
[13]: https://cdn.gethue.com/uploads/2016/08/IMG_4409.jpg
[14]: https://gethue.com/mini-team-retreat-in-portland/
[15]: http://groups.google.com/a/cloudera.org/group/hue-user
[16]: https://twitter.com/gethue
