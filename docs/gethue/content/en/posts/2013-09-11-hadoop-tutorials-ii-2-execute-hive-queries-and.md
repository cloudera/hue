---
title: 'Season II: 2. Execute Hive queries and schedule them with Oozie'
author: admin
type: post
date: 2013-09-11T15:39:00+00:00
url: /hadoop-tutorials-ii-2-execute-hive-queries-and/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/60937985689/hadoop-tutorials-ii-2-execute-hive-queries-and
tumblr_gethue_id:
  - 60937985689
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
  - Tutorial
---

<p id="docs-internal-guid--8202e43-0da7-b45c-578a-06e670bbcee9">
  In the <a href="https://gethue.com/hadoop-tutorials-ii-1-prepare-the-data-for-analysis/">previous</a> episode, we saw how to to transfer some file data into Apache Hadoop. In order to interrogate easily the data, the next step is to create some Hive tables. This will enable quick interaction with high level languages like SQL and <a href="https://gethue.com/tutorial-apache-pig-editor-in-hue-2-3/">Pig</a>.
</p>

&nbsp;

{{< youtube VYJfM4AQyvo >}}

We experiment with the SQL queries, then parameterize them and insert them into a workflow in order to run them together in parallel. Including Hive queries in an Oozie workflow is a pretty common use case with recurrent pitfalls as seen on the user group. We can do it with [Hue][1] in a few clicks.

# Get prepared

First, based on the data of the previous episode we create two tables in the Hive Metastore. We use the Metastore app and its create table wizard. Then, it is time to study the data!

We previously created the Hive table in <https://gethue.com/tutorial-analyzing-data-with-hue-and-hive/>

&nbsp;

&nbsp;

# Hive

Goal: we want to get the 10 coolest restaurants for a day.

&nbsp;

Let’s open Beeswax Hive Editor and explore the range of dates that we have:

<pre><code class="sql">SELECT DISTINCT \`date\` FROM review ORDER BY \`date\` DESC;</code></pre>

Notice that you need to use backticks in order to use date as a column name in Hive.

&nbsp;

The data is a bit old, so let’s pick 2012-12-01 as our target date. We can join the two tables in order to get the name of the restaurant and its average ‘cool’ score of the day. Submit this parameterized query and enter 2012-12-01 when prompted for the date:

&nbsp;

<pre><code class="sql">SELECT r.business_id, name, AVG(cool) AS coolness

FROM review r JOIN business b

ON (r.business_id = b.business_id)

WHERE categories LIKE '%Restaurants%'

AND \`date\` = '$date'

GROUP BY r.business_id, name

ORDER BY coolness DESC

LIMIT 10

</code></pre>

We have a good Hive query. Let’s [create][2] a result table ‘top_cool’ that will contain the top 10:

<pre><code class="sql">CREATE TABLE top_cool AS

SELECT r.business_id, name, SUM(cool) AS coolness, '$date' as \`date\`

FROM review r JOIN business b

ON (r.business_id = b.business_id)

WHERE categories LIKE '%Restaurants%'

AND \`date\` = '$date'

GROUP BY r.business_id, name

ORDER BY coolness DESC

LIMIT 10

</code></pre>

And later replace ‘CREATE TABLE top_cool AS’ by ‘INSERT INTO TABLE top_cool’ in the Hive script as we want to create the table only the first time:

<pre><code class="sql">INSERT INTO TABLE top_cool

SELECT r.business_id, name, SUM(cool) AS coolness, '${date}' as \`date\`

FROM review r JOIN business b

ON (r.business_id = b.business_id)

WHERE categories LIKE '%Restaurants%'

AND \`date\` = '$date'

GROUP BY r.business_id, name

ORDER BY coolness DESC

LIMIT 10

</code></pre>

# Hive action in Apache Oozie

The video also starts <a href="https://youtube.com/watch?v=VYJfM4AQyvo#t=2m53s" target="_blank" rel="noopener noreferrer">here</a>.

First we create a new workflow and add an Oozie action. We need to specify which SQL we want to run. This one needs to be uploaded to HDFS. In our case we open up the ‘workspace’ of the workflow, create a new file and copy paste the query. We we upload and pick the [query file][3] as the ‘Script name’.

&nbsp;

## <span style="color: #ff0000;">Important</span>

Then comes a crucial step. Our Hive action needs to talk to the Hive Metastore and so know its location. This is done by copying /etc/hive/conf/hive-site.xml as 'hive-conf.xml' on HDFS and including it as a ‘File’ resource and telling Oozie to use it as ‘Job XML’ configuration.

&nbsp;

Note: when using a demo VM or a pseudo distributed cluster (everything on one machine), you might hit the error explained in the ‘Warning!’ section of the [HCatalog post][4].

&nbsp;

Note: when using a real cluster, as the workflow is going to run somewhere in the cluster, we need to the metastore to be [remote][5]. A remote Metastore can be contacted from any other hosts.

&nbsp;

Lets specify that we are using a ‘date’ parameter in the Hive script. In our case we add the parameter in the Hive action:

<pre><code class="bash">

date=${date}

</code></pre>

The we save the workflow, fill up the date when prompted and look at the dynamic progress of the workflow! The output of the query will appear when you click on the ‘View the logs’ button on the action graph. In practice, INSERT, LOAD DATA would be used instead of SELECT in order to persist the calculation.

&nbsp;

You can now monitor the workflow in the dashboard and stop or rerun it.

&nbsp;

Note:

If you are seeing this error, it means that the input file or destination directory of the table is not writable by your user or the ‘hive’ user if you are with HiveServer2:

&nbsp;

<pre class="code">Failed with exception copyFiles: error while moving files!!!
 FAILED: Execution Error, return code 1 from org.apache.hadoop.hive.ql.exec.MoveTask</pre>

&nbsp;

# Sum-up

Hive queries can be simply tested in Beeswax Hive Editor before getting inserted in an Oozie workflow, all without touching the command line.

&nbsp;

One of the Hue 3 goal is to remove the duplication of the hive script on the HDFS and the manual creation of the Hive action. With the new [document model][6], one would refer to the saved Hive query in Beeswax and with just a click create it.

&nbsp;

Creating a workflow lets you group other scripts together and run them atomically. Another advantage is to then execute the workflow repetitively (e.g. run a query every day at midnight) with an Oozie coordinator.

This is what we will cover in the [next episode][7]!

[1]: http://gethue.com
[2]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hive-workflow/create_table.hql
[3]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hive-workflow/insert_table.hql
[4]: https://gethue.com/hadoop-tutorial-how-to-access-hive-in-pig-with/
[5]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_hive_metastore_configure.html#topic_18_4_1_unique_1__title_508_unique_1
[6]: https://issues.cloudera.org/browse/HUE-950
[7]: https://gethue.com/hadoop-tutorials-ii-3-schedule-hive-queries-with/
