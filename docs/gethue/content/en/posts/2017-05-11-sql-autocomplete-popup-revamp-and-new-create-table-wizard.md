---
title: SQL Autocomplete popup revamp and new Create table wizard
author: admin
type: post
date: 2017-05-11T22:19:54+00:00
url: /sql-autocomplete-popup-revamp-and-new-create-table-wizard/
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
sf_author_info:
  - 1
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
---

# SQL Improvements

The editor keeps getting better. Below you can read about a selection of recent major improvements.

## Autocomplete popup revamp

Like in a regular code editor, the autocomplete is split in two parts. This is to prevent hangs while fetching the metadata of the current table or columns and to display more context information like the comments, type of objects, and their full names.

<div id="attachment_33782" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2017/05/autocomplete-before.png"><img src="https://cdn.gethue.com/uploads/2017/05/autocomplete-before.png" /></a>
  </p>

  <p class="wp-caption-text">
    Autocomplete before
  </p>
</div>

<div id="attachment_33783" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2017/05/autocomplete_1.png"><img src="https://cdn.gethue.com/uploads/2017/05/autocomplete_1.png" /></a>
  </p>

  <p class="wp-caption-text">
    Autocomplete in new version
  </p>
</div>

<div id="attachment_33784" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2017/05/autocomplete_2.png"><img src="https://cdn.gethue.com/uploads/2017/05/autocomplete_2.png" /></a>
  </p>

  <p class="wp-caption-text">
    <a href="https://kudu.apache.org/">Apache Kudu</a> primary keys are directly represented
  </p>
</div>

## Create table wizard

If you’ve ever struggled with creating new SQL tables from files, you’ll be happy to learn that this is now much easier. With the latest Hue release, you can now create these in an ad hoc way and thereby expedite self-service analytics. The wizard has been revamped to two simple steps and also offers more formats. Now users just need to:

1. Select a file
2. Select the type of table

And that’s it! Files can be dragged & dropped, selected from HDFS or [S3][1] (if configured), and their formats are automatically detected. The wizard also assists when performing advanced functionalities like table partitioning, Kudu tables, and nested types.

To learn more, watch this video:

{{< youtube RxT0M8JgvOk >}}

&nbsp;

We hope that the new version of Hue makes self-service analytics easier and faster. If you have any questions or feedback, feel free to comment here, on the [user list][2], or via [@gethue][3].

You can find these improvements on the latest Hue or [demo.gethue.com][4]!

[1]: https://gethue.com/introducing-s3-support-in-hue/
[2]: http://groups.google.com/a/cloudera.org/group/hue-user
[3]: https://twitter.com/gethue
[4]: http://demo.gethue.com
