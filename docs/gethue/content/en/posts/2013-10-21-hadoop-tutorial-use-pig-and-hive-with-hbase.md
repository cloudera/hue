---
title: 'Season II: 6. Use Pig and Hive with HBase'
author: admin
type: post
date: 2013-10-21T20:41:35+00:00
url: /hadoop-tutorial-use-pig-and-hive-with-hbase/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/64707633719/hadoop-tutorial-use-pig-and-hive-with-hbase
tumblr_gethue_id:
  - 64707633719
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
  - Tutorial
---

<p id="docs-internal-guid-6762db62-dcbc-201d-e1c6-4f70083f264f">
  <span>The HBase app is an elegant way to visualize and search a lot of data. </span><a href="http://hbase.apache.org/"><span>Apache HBase</span></a><span> tables can be tricky to update as they require lower level API. Some good alternative for simplifying the data management or access is to use Apache Pig or Hive.</span>
</p>

&nbsp;

<span>In this post we are going to show how to load our yelp data from the </span>[<span>Oozie Bundles</span>][1] <span>episode into HBase with Hive. Then we will use the </span>[<span>HBase Browser</span>][2] <span>to visualize it and Pig to compute some statistics.</span>

{{< youtube Qpll_XbUEf0 >}}

&nbsp;

# <span>Access HBase with Hive</span>

&nbsp;

<span>First, let’s use Beeswax to create a Hive table that is persisted as a HBase table. The script works as intended when using HiveServer2 as the Hive backend. Some HBase jar need to be registered, as shown in the video.</span>

&nbsp;

<span>In our use case of Yelp data, </span>[<span>map</span>][3] <span>is the correct data type for our HBase that will created as </span>[<span>EXTERNAL</span>][3]<span>.</span>

&nbsp;

<span>Here is the </span>[<span>create table statement</span>][4] <span>for creating a table that is going to store the top N coolest restaurants for everyday:</span>

&nbsp;

<pre class="code">set hbase.zookeeper.quorum my-hbase.com

CREATE TABLE top_cool_hbase (key string, value map&lt;string, int&gt;)
STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
WITH SERDEPROPERTIES ("hbase.columns.mapping" = ":key,review:")
TBLPROPERTIES ("hbase.table.name" = "top_cool");</pre>

&nbsp;

<span>In order to allow Hive to use HBase some jars need to be registered (one by session). Upload them on HDFS and add them as resources in the first create table query:</span>

<pre class="code">/usr/lib/hive/lib/zookeeper.jar;
/usr/lib/hive/lib/hbase.jar;
/usr/lib/hive/lib/hive-hbase-handler-0.XX.0-cdhX.X.X.jar
/usr/lib/hive/lib/guava-11.0.2.jar;</pre>

&nbsp;

<span>Then lets add data to our new table. We copy it from our top_cool table of the </span>[<span>previous episode</span>][1]<span>.</span>

<pre class="code">INSERT OVERWRITE TABLE top_cool_hbase SELECT name, map(`date`, cast(coolness as int)) FROM top_cool</pre>

&nbsp;

<span>If you don’t have the table from the past episode, you can still use the one from </span>[<span>episode one</span>][5] <span>as a workaround:</span>

<pre class="code">INSERT OVERWRITE TABLE top_cool_hbase SELECT name, map(`date`, cast(r.stars as int)) FROM review r JOIN business b ON r.business_id = b.business_id;</pre>

<span>Access HBase with HBase Browser</span>

<span>As seen in the video, the HBase app provides a slick new Web interface to HBase.</span>

&nbsp;

# <span>Access HBase with Pig</span>

<span>Pig comes with some built-in </span>[<span>HBaseStorage</span>][6] <span>and HBaseLoader. After registering two jars, you will be able to use them. Here is the </span>[<span>script</span>][7] <span>for dumping all the counts of a particular day:</span>

&nbsp;

<pre class="code">REGISTER /usr/lib/zookeeper/zookeeper-3.4.5-cdhX.X.X.jar
REGISTER /usr/lib/hbase/hbase-0.94.6-cdhX.X.X-security.jar

set hbase.zookeeper.quorum 'localhost'

data = LOAD 'hbase://top_cool'
       USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('review:*', '-loadKey true')
       as (name:CHARARRAY, dates:MAP[]);

counts =
    FOREACH data
    GENERATE name, dates#'2012-12-02';

DUMP counts;</pre>

&nbsp;

# <span>Sum-up</span>

<span>Hive and Pig are excellent tools for manipulating HBase data. All combinations are possible, the sky is the limit! For example you could load from HBase and save into Hive table with Pig or use Hive SQL to query HBase tables. You can even pull HDFS or Hive data from Pig with </span>[<span>Hcatalog</span>][8]<span>, save it into HBase (or vice versa) and browse it with HBase Browser!</span>

<span>Next time, let’s see how to create a search engine from the Yelp data!</span>

<span>As usual, if you have questions or feedback, feel free to contact the Hue community on </span>[<span>hue-user</span>][9] <span>or </span>[<span>@gethue.com</span>][10]<span>!</span>

[1]: http://gethue.tumblr.com/post/63988110361/hadoop-tutorial-bundle-oozie-coordinators-with-hue
[2]: http://gethue.tumblr.com/post/59071544309/the-web-ui-for-hbase-hbase-browser
[3]: https://cwiki.apache.org/confluence/display/Hive/HBaseIntegration
[4]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hbase-hive-pig/create_hbase_table.sql
[5]: http://gethue.tumblr.com/post/60376973455/hadoop-tutorials-ii-1-prepare-the-data-for-analysis
[6]: http://pig.apache.org/docs/r0.11.1/func.html#HBaseStorage
[7]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hbase-hive-pig/load_hbase.pig
[8]: http://gethue.tumblr.com/post/56804308712/hadoop-tutorial-how-to-access-hive-in-pig-with
[9]: http://groups.google.com/a/cloudera.org/group/hue-user
[10]: http://twitter.com/gethue
