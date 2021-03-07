---
title: Create Hive tables with headers and load quoted CSV data
author: admin
type: post
date: 2013-11-27T18:54:00+00:00
url: /hadoop-tutorial-create-hive-tables-with-headers-and/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/68282571607/hadoop-tutorial-create-hive-tables-with-headers-and
tumblr_gethue_id:
  - 68282571607
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
slide_template:
  - default
categories:
---

<p id="docs-internal-guid-69d034aa-9ae7-82e8-1c00-5068cd66771e">
  Hue makes it easy to create Hive tables.
</p>

With [HUE-1746][1], Hue guesses the columns names and types (int, string, float…) directly by looking at your data. If your data starts with a header, this one will automatically be used and **skipped** while creating the table.

{{< youtube RxT0M8JgvOk >}}

Quoted CSV fields are also compatible thanks to [HUE-1747][2].

Here is the data file used:

<http://www.fdic.gov/bank/individual/failed/banklist.html>

&nbsp;

<span>This is the </span>[<span>SerDe</span>][3] <span>for reading quoted CSV:</span>

<https://github.com/ogrodnek/csv-serde>

&nbsp;

<span>And the command to switch the SerDe used by the table:</span>

<pre class="code">ALTER TABLE banks SET SERDE 'com.bizo.hive.serde.csv.CSVSerde'</pre>

<span>Now go analyze the data with the </span>[<span>Hive</span>][4]<span>, </span>[<span>Impala</span>][5] <span>or </span>[<span>Pig</span>][6] <span>editors!</span>

[1]: https://issues.cloudera.org/browse/HUE-1746
[2]: https://issues.cloudera.org/browse/HUE-1747
[3]: https://cwiki.apache.org/confluence/display/Hive/SerDe
[4]: http://gethue.tumblr.com/post/64916325309/hadoop-tutorial-hive-query-editor-with-hiveserver2-and
[5]: http://gethue.tumblr.com/post/62452792255/fast-sql-with-the-impala-query-editor
[6]: http://gethue.tumblr.com/post/64707633719/hadoop-tutorial-use-pig-and-hive-with-hbase
