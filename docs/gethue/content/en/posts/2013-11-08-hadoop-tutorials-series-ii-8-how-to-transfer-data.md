---
title: 'Season II: 8. How to transfer data from Hadoop with Sqoop 2'
author: admin
type: post
date: 2013-11-08T05:23:00+00:00
url: /hadoop-tutorials-series-ii-8-how-to-transfer-data/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/66348238493/hadoop-tutorials-series-ii-8-how-to-transfer-data
tumblr_gethue_id:
  - 66348238493
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
ampforwp-amp-on-off:
  - default
categories:
  - Tutorial
---

_Note: Sqoop2 is now replaced by <https://gethue.com/importing-data-from-traditional-databases-into-hdfshive-in-just-a-few-clicks/>_

&nbsp;

<p id="docs-internal-guid-342afe4b-3626-38d5-0543-797eb6fb3c0a">
  <a href="http://www.google.co.jp/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&ved=0CCoQFjAA&url=http%3A%2F%2Fsqoop.apache.org%2F&ei=9h9eUt7SKofQkQWy5YCADA&usg=AFQjCNFJ9nOIbX4GN1HakCZayhtKkXEUBw&bvm=bv.54176721,d.dGI">Apache Sqoop</a> is a great tool for moving data (in files or databases) in or out of Hadoop. In Hue 3, a <a href="http://gethue.tumblr.com/post/63064228790/move-data-in-out-your-hadoop-cluster-with-the-sqoop">new app</a> was added for making Sqoop2 easier to use.
</p>

In this final episode (previous one was about [Search][1]) of the season 2 of the Hadoop Tutorial series let’s see how simple it becomes to export our Yelp results into a MySql table!

{{< youtube zCE7N0PV7R4 >}}

Sqoop2 currently only [Comma Separated Values][2] files. Moreover, Sqoop2 currently require on export for String constants to be enclosed in single quotes.

We are going to save our data analysis into this format with a [Pig script][3] with the [Pig Editor][4]. Then, as detailed in the video we specify an export job, set the input path as the output of our previous Pig job. The data is in on HDFS and the path can either be a single file or a directory.

We previously created a MySql table ‘stats’ with this [SQL script][5]. This table is going to store the exported data. Here are the properties of our job. They are explained in more depth in the previous Sqoop2 App blog post.

<pre><code class="bash">Table name: yelp_cool_test

Input directory: /user/hdfs/test_sqoop

Connector: mysql

JDBC Driver Class : com.mysql.jdbc.Driver

JDBC Connection String: jdbc:mysql://hue.com/test

</code></pre>

Then click ‘Save & Execute’, and here we go, the data is now available in MySql!

&nbsp;

<pre><code class="bash">mysql> select * from yelp_cool_test limit 2;

+--+--+--+--+

| a | b | c | d |

+--+--+--+--+

| 1 | 2 | 3 | 4 |

| 2 | 3 | 4 | 5 |

+--+--+--+--+

2 rows in set (0.00 sec)

</code></pre>

Data stored in Hive or HBase can not be sqooped natively yet by Sqoop2. A current (less efficient) workaround would be to dump it to a HDFS directory with [Hive or Pig][6] and then do a similar Sqoop export.

&nbsp;

As usual, if you have questions or feedback, feel free to contact the Hue community on [hue-user][7] or [@gethue.com][8]!

Thank you for watching this [season 2][9]!

[1]: http://gethue.tumblr.com/post/65969470780/hadoop-tutorials-season-ii-7-how-to-index-and-search
[2]: https://en.wikipedia.org/wiki/Comma-separated_values
[3]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/sqoop2/stats.pig
[4]: http://gethue.tumblr.com/post/51559235973/tutorial-apache-pig-editor-in-hue-2-3
[5]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/sqoop2/create_table.sql
[6]: http://gethue.tumblr.com/post/64707633719/hadoop-tutorial-use-pig-and-hive-with-hbase
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: http://twitter.com/gethue
[9]: http://gethue.tumblr.com/tagged/season2
