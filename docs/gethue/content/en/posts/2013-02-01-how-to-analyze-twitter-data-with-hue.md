---
title: 'How-to: Analyze Twitter Data with Hue'
author: admin
type: post
date: 2013-02-01T05:00:00+00:00
url: /how-to-analyze-twitter-data-with-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/48706198060/how-to-analyze-twitter-data-with-hue
tumblr_gethue_id:
  - 48706198060
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
[Hue 2.2][1] , the open source web-based interface that makes [Apache Hadoop][2] easier to use, lets you interact with Hadoop services from within your browser without having to go to a command-line interface. It features different applications like an Apache Hive editor and Apache Oozie dashboard and [workflow builder][3].

This post is based on our “[Analyzing Twitter Data with Hadoop][4]” sample app and details how the same results can be achieved through Hue in a simpler way. Moreover, all the [code and examples][5] of the previous series have been updated to the recent [CDH4.2][6] release.

### Collecting Data

The first step is to create the “flume” user and his home on the HDFS where the data will be stored. This can be done via the User Admin application.

[<img title="hue1" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue1.png" width="600" height="369" />][7]

The second step consists of collecting some tweet data from the live Twitter stream.

[Apache Flume][8] is an elegant solution for taking care of this. The configuration of Flume is detailed in the [readme][9] and previous blog [post][10]. However, if you want to skip this step, some data is available on [GitHub][11]. Just upload it as a zip file in the home directory of the flume user and the “tweets” directory will show up after a few seconds.

If you are not taking this shortcut, create the tweets directory in the File Browser with the New Folder action.

[<img title="hue2" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue2.png" width="600" height="117" />][12]

Then, when the Flume agent is [started][13], the data will start appearing:

[<img title="hue3" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue3.png" width="600" height="327" />][14]

Clicking on a file will display its content in the built-in viewer:

[<img title="hue4" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue4.png" width="600" height="228" />][15]

### Preparing Hive

It is time to prepare the analysis of the tweet data. We’ll use Apache Hive, which can query the data with SQL-like syntax in a scalable way. The detailed description of the Hive setup is detailed in the [readme][16].

When Hive is ready, the tweet table can be created in the query editor of Beeswax. Notice that the Hive SerDe (to download or compile [here][16]) must be included as a jar in the query. You can read more about Hive SerDe in this previous [post][17].

To do this, just click on “Add” > “File Resources”, click on the path chooser button, click on the “Home” button, and upload hive-serdes-1.0-SNAPSHOT.jar.

[<img title="hue5" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue5.png" width="600" height="326" />][18]

Then just enter the `CREATE TABLE` statement and execute it:

<pre class="code">CREATE EXTERNAL TABLE tweets (
  id BIGINT,
  created_at STRING,
  source STRING,
  favorited BOOLEAN,
  retweet_count INT,
  retweeted_status STRUCT&lt;
    text:STRING,
    user:STRUCT&lt;screen_name:STRING,name:STRING&gt;&gt;,
  entities STRUCT&lt;
    urls:ARRAY&lt;STRUCT&lt;expanded_url:STRING&gt;&gt;,
    user_mentions:ARRAY&lt;STRUCT&lt;screen_name:STRING,name:STRING&gt;&gt;,
    hashtags:ARRAY&lt;STRUCT&lt;text:STRING&gt;&gt;&gt;,

  text STRING,
  user STRUCT&lt;
    screen_name:STRING,
    name:STRING,
    friends_count:INT,
    followers_count:INT,
    statuses_count:INT,
    verified:BOOLEAN,
    utc_offset:INT,
    time_zone:STRING&gt;,
  in_reply_to_screen_name STRING
)
PARTITIONED BY (datehour INT)
ROW FORMAT SERDE 'com.cloudera.hive.serde.JSONSerDe'
LOCATION '/user/flume/tweets'</pre>

Now that the table is created, let’s insert some data in the table. First, select the table in the “Table” tab and click “Import data”. Enter the path “/user/flume/tweets/2013/02/25/17″ and “201302251″ as the key:

[<img title="hue6" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue6.png" width="600" height="317" />][19]

Depending on the partition picked, a query similar to this will be generated:

<pre class="code">LOAD DATA INPATH '/user/flume/tweets/2013/02/25/16'
INTO TABLE `default.tweets`
PARTITION (datehour='2013022516')</pre>

After the query executes, the table ‘tweets’ will be available.

[<img title="hue7" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue7.png" width="600" height="171" />][20]

Beeswax can access the Hive metastore and its list of tables. A description of their schema and partitions with some example of data contained in each table are helpful while designing your queries. Moreover, a wizard can guide you step-by-step to create new tables.

[<img title="hue8" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue8.png" width="600" height="195" />][21]

### Analysis with Beeswax

It becomes now possible to perform some `SELECT` queries on the data. Here is an example below but most of interesting ones are described in Parts [1][10] and [3][4] of the “Analyzing Twitter with Hadoop” series.

<pre class="code">SELECT
    t.retweeted_screen_name,
    sum(retweets) AS total_retweets,
    count(*) AS tweet_count
  FROM (SELECT
          retweeted_status.user.screen_name as retweeted_screen_name,
              retweeted_status.text,
              max(retweet_count) as retweets
        FROM tweets
        GROUP BY retweeted_status.user.screen_name,
                 retweeted_status.text) t
  GROUP BY t.retweeted_screen_name
  ORDER BY total_retweets DESC
  LIMIT 10;</pre>

Beeswax possesses multiple features for providing a better user experience than the command line shell. For example you can save queries and share them with other users. The result of a query can be exported into a new table or an HDFS file or downloaded to your desktop. Some other good examples are:

  * Ajax refresh of the logs
  * Quick [column navigation][22] on the result page
  * MapReduce jobs listing with a direct access to their logs
  * ‘Email me on completion’ setting
  * [Multi-database][23] support

Example of the screen while running query:

[<img title="hue9" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue9.png" width="600" height="354" />][24]

Seeing the result of the query:

[<img title="hue10" alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/hue10.png" width="600" height="180" />][25]

Note: if your queries are failing and you are seeing an error like below, it means that you forgot to add the ‘/user/flume/hive-serdes-1.0-SNAPSHOT.jar’ to the query:

<pre class="code">FAILED: Execution Error, return code 2 from org.apache.hadoop.hive.ql.exec.MapRedTask</pre>

### Conclusion

In this post we focused on how the Beeswax application can make it easy to execute Hive queries. New features such as multi-query ([HUE-159][26]), autocomplete, and syntax highlighting ([HUE-1063][27]) are going to improve the usability even more.

The next article in this series will elaborate on this topic and describe how Hue’s Apache Oozie application can be used for scheduling Hive queries in a few clicks.

Thank you for reading and feel free to post comments here or on the [hue-user][28] list. We also hope to see you at the first[Hue meetup][29] (this Wednesday, March 27)!

 [1]: http://blog.cloudera.com/blog/2013/03/whats-new-in-hue-2-2/
 [2]: http://hadoop.apache.org/
 [3]: http://blog.cloudera.com/blog/2013/01/dynamic-workflow-builder-in-hue/
 [4]: http://blog.cloudera.com/blog/2012/11/analyzing-twitter-data-with-hadoop-part-3-querying-semi-structured-data-with-hive/
 [5]: https://github.com/romainr/cdh-twitter-example
 [6]: http://blog.cloudera.com/blog/2013/02/new-products-releases/
 [7]: http://www.cloudera.com/wp-content/uploads/2013/03/hue1.png
 [8]: http://flume.apache.org/
 [9]: https://github.com/romainr/cdh-twitter-example#configuring-flume
 [10]: http://blog.cloudera.com/blog/2012/09/analyzing-twitter-data-with-hadoop/
 [11]: https://github.com/romainr/cdh-twitter-example/blob/master/hue/tweets.zip
 [12]: http://www.cloudera.com/wp-content/uploads/2013/03/hue2.png
 [13]: https://github.com/romainr/cdh-twitter-example#starting-the-data-pipeline
 [14]: http://www.cloudera.com/wp-content/uploads/2013/03/hue3.png
 [15]: http://www.cloudera.com/wp-content/uploads/2013/03/hue4.png
 [16]: https://github.com/romainr/cdh-twitter-example#setting-up-hive
 [17]: http://blog.cloudera.com/blog/2012/12/how-to-use-a-serde-in-apache-hive/
 [18]: http://www.cloudera.com/wp-content/uploads/2013/03/hue5.png
 [19]: http://www.cloudera.com/wp-content/uploads/2013/03/hue6.png
 [20]: http://www.cloudera.com/wp-content/uploads/2013/03/hue7.png
 [21]: http://www.cloudera.com/wp-content/uploads/2013/03/hue8.png
 [22]: https://issues.cloudera.org/browse/HUE-899
 [23]: https://issues.cloudera.org/browse/HUE-535
 [24]: http://www.cloudera.com/wp-content/uploads/2013/03/hue9.png
 [25]: http://www.cloudera.com/wp-content/uploads/2013/03/hue10.png
 [26]: https://issues.cloudera.org//browse/HUE-159
 [27]: https://issues.cloudera.org/browse/HUE-1063
 [28]: https://groups.google.com/a/cloudera.org/group/hue-user/topics
 [29]: http://www.meetup.com/San-Francisco-Bay-Area-Hue-Users/
