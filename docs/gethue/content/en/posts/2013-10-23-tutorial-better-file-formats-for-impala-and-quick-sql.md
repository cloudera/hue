---
title: Better file formats for Impala and quick SQL in Hadoop
author: admin
type: post
date: 2013-10-23T18:03:00+00:00
url: /tutorial-better-file-formats-for-impala-and-quick-sql/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/64879465564/tutorial-better-file-formats-for-impala-and-quick-sql
tumblr_gethue_id:
  - 64879465564
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
# <span>Impala File Formats</span> {#docs-internal-guid-798b2644-e679-81ed-508c-e3685cd16a67}

<span>Using the best file format is crucial for getting great performances. This is one reason with JSON is no supported in the </span>[<span>Impala application</span>][1]<span>. Indeed, parsing or retrieving all the text record even for one field would damage the performance badly. Impala is recommending a series of alternative</span>[<span>formats</span>][2]<span>. </span>

&nbsp;

<span>We show here how to create a Hive table in Avro format containing json data and a table in the new parquet format. We are using the same Yelp data from </span>[<span>Episode 2 of the Season 2</span>][3] <span>of the Hadoop Tutorial series. </span>

&nbsp;

## Avro

<span>The first step is to convert our data into JSON with the help of a Pig script. Open up the </span>[<span>Pig Editor</span>][4] <span>and run:</span>

&nbsp;

<pre><code class="sql">REGISTER piggybank.jar

data = load '/user/hive/warehouse/review/yelp_academic_dataset_review_clean.json'

AS (funny:INT, useful:INT, cool:INT, user_id:CHARARRAY, review_id:CHARARRAY, text:CHARARRAY, business_id:CHARARRAY, stars:INT, date:CHARARRAY, type:CHARARRAY);

data_clean = FILTER data BY business_id IS NOT NULL AND text IS NOT NULL;

STORE data_clean INTO 'impala/reviews_avro'

USING org.apache.pig.piggybank.storage.avro.AvroStorage(

'{

"schema": {

"name": "review",

"type": "record",

"fields": [

{"name":"funny", "type":"int"},

{"name":"useful", "type":"int"},

{"name":"cool", "type":"int"},

{"name":"user_id", "type":"string"}

{"name":"review_id", "type":"string"},

{"name":"text", "type":"string"},

{"name":"business_id", "type":"string"},

{"name":"stars", "type":"int"},

{"name":"date", "type":"string"},

{"name":"type", "type":"string"},

]}

}');</code></pre>

&nbsp;

<span>Then, in the </span>[<span>Hive Editor</span>][5] <span>create the table with:</span>

&nbsp;

<pre><code class="sql">CREATE TABLE review_avro

ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'

STORED AS

inputformat 'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat'

outputformat 'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat'

LOCATION '/user/romain/impala/reviews_avro'

tblproperties ('avro.schema.literal'='{

"name": "review",

"type": "record",

"fields": [

{"name":"business_id", "type":"string"},

{"name":"cool", "type":"int"},

{"name":"date", "type":"string"},

{"name":"funny", "type":"int"},

{"name":"review_id", "type":"string"},

{"name":"stars", "type":"int"},

{"name":"text", "type":"string"},

{"name":"type", "type":"string"},

{"name":"useful", "type":"int"},

{"name":"user_id", "type":"string"}]}'

);</code></pre>

&nbsp;

<span>You can now go back to Impala, and use the table after having refreshed the metadata with:</span>

&nbsp;

<pre><code class="sql">REFRESH avro_table</code></pre>

&nbsp;

## Parquet

<span>Parquet is a new column-oriented binary file format, particularly efficient in Impala. Here is how to create a table from the Impala app:</span>

&nbsp;

<pre><code class="sql">CREATE TABLE review_parquet LIKE review STORED AS PARQUETFILE;</code></pre>

&nbsp;

<span>And then load data:</span>

&nbsp;

<pre><code class="sql">INSERT OVERWRITE review_parquet SELECT * FROM review;</code></pre>

&nbsp;

<span>Take the time to read about the goal of each format and how to enable compression. If you want to know more, the </span>[<span>Impala tuning guide</span>][6] <span>is a good reference too.</span>

&nbsp;

<span>As usual feel free to comment on the </span>[hue-user][7] list or [<span>@gethue</span>][8]<span>!</span>

&nbsp;

 [1]: http://gethue.tumblr.com/post/62452792255/fast-sql-with-the-impala-query-editor
 [2]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Impala/latest/Installing-and-Using-Impala/ciiu_file_formats.html
 [3]: http://gethue.tumblr.com/post/60937985689/hadoop-tutorials-ii-2-execute-hive-queries-and
 [4]: http://gethue.tumblr.com/tagged/pig
 [5]: http://gethue.tumblr.com/tagged/hive
 [6]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Impala/latest/Installing-and-Using-Impala/ciiu_performance.html
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue
