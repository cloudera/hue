---
title: 'Season II: 4. Fast SQL with the Impala Query Editor'
author: admin
type: post
date: 2013-09-27T22:24:00+00:00
url: /fast-sql-with-the-impala-query-editor/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/62452792255/fast-sql-with-the-impala-query-editor
tumblr_gethue_id:
  - 62452792255
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

<span>In the previous episodes, we presented how to schedule repetitive worflows on the grid with <a href="http://gethue.tumblr.com/post/61597968730/hadoop-tutorials-ii-3-schedule-hive-queries-with">Oozie Coordinator</a>. Let’s now look at a fast way to query some data with Impala.</span>

<p id="docs-internal-guid-40e7f13f-6181-fb3b-54b1-99253b9abffe">
  <span>Hue, </span><a href="http://gethue.com"><span>the Hadoop UI</span></a><span>, has been supporting </span><a href="https://github.com/cloudera/impala"><span>Impala</span></a><span> closely since its first version and brings fast interactive queries within your browser. If not familiar with </span><a href="http://blog.cloudera.com/blog/2012/10/cloudera-impala-real-time-queries-in-apache-hadoop-for-real/"><span>Impala</span></a><span>, we recommend you to check the documentation of the fastest </span><a href="http://www.cloudera.com/content/support/en/documentation/cloudera-impala/cloudera-impala-documentation-v1-latest.html"><span>SQL engine</span></a><span> for Hadoop.</span>
</p>

{{< youtube FwcVA_pgmNY >}}

# <span>Impala App</span>

<span>Most of Hive SQL is compatible with Impala and we are going to compare the queries of </span>[<span>episode one</span>][1] <span>in both Hive and Impala applications. Notice that this comparison is not 100% scientific but it demonstrates what would happen in common cases.</span>

&nbsp;

<span>Using Impala through the Hue app is easier in many ways than using it through the command-line impala-shell. For example, table names, databases, columns, built-in functions are auto-completable and the syntax highlighting shows the potential typos in your queries. Multiple queries or a selected portion of a query can be executed from the editor. Parameterized queries are supported and the user will be prompted for values at submission time. Impala queries can be saved and shared between users or deleted and then restored from trash in case of mistakes. </span>

&nbsp;

<span>Impala uses the same Metastore as Hive so you can browse tables with the </span>[<span>Metastore app</span>][2]<span>. You can also pick a database with a drop-down in the editor. After submission, progress and logs are reported and you can browse the result with infinite scroll or download the data with your browser.</span>

# <span>Query speed comparison </span>

<span>Let’s start with the Hue examples as they are easily accessible. They are very small but show the lightning speed of Impala and the inefficiency of the series of MapReduce jobs created by Hive.</span>

<span>Make sure the Hive and Impala examples are installed in Hue and then in each app, go to ‘</span><span>Saved Queries</span><span>’, copy the query ‘</span><span>Sample: Top salaries</span><span>’ and submit it.</span>

<span>Then we are back to our Yelp data. Let’s take the query from </span>[<span>episode one</span>][1] <span>and execute it in both apps:</span>

<pre><code class="sql">

SELECT r.business_id, name, SUM(cool) AS coolness

FROM review r JOIN business b

ON (r.business_id = b.business_id)

WHERE categories LIKE '%Restaurants%'

AND \`date\` = '$date'

GROUP BY r.business_id, name

ORDER BY coolness DESC

LIMIT 10

</code></pre>

<span>Again, you can see the benefits of Impala’s </span>[<span>architecture and optimization</span>][3]<span>.</span>

<span> </span>

# <span>Sum-up</span>

<span>This post described how Impala query execution makes data analysis interactive and more productive than Hive’s batch architecture. Results come back fast, and in our Yelp data case, instantaneously. Impala and Hue combined are a recipe for fast analytics. Moreover, Hue’s </span>[<span>Python API</span>][4] <span>can also be reused if you want to build your own client. </span>

&nbsp;

[<span>Cloudera’s demo VM</span>][5] with its Hadoop tutorials is a great way to get started with Impala and Hue. The [best file formats for Impala][6] blog post describes how to be even more efficient.

&nbsp;

As usual feel free to comment on the[<span>hue-user</span>][7] list or [<span>@gethue</span>][8]. Next, we will continue the Hadoop Tutorial season 2 with [Oozie Bundles][9]!

[1]: http://gethue.tumblr.com/post/60376973455/hadoop-tutorials-ii-1-prepare-the-data-for-analysis
[2]: http://gethue.tumblr.com/post/56804308712/hadoop-tutorial-how-to-access-hive-in-pig-with
[3]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Impala/latest/Installing-and-Using-Impala/ciiu_concepts.html
[4]: http://gethue.tumblr.com/post/49882746559/tutorial-executing-hive-or-impala-queries-with-python
[5]: https://ccp.cloudera.com/display/SUPPORT/Cloudera+QuickStart+VM
[6]: http://gethue.tumblr.com/post/64879465564/tutorial-better-file-formats-for-impala-and-quick-sql
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
[9]: http://gethue.tumblr.com/post/63988110361/hadoop-tutorial-bundle-oozie-coordinators-with-hue
