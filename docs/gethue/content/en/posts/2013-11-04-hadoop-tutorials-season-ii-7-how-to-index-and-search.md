---
title: 'Season II: 7. How to index and search Yelp data with Solr'
author: admin
type: post
date: 2013-11-04T04:33:00+00:00
url: /hadoop-tutorials-season-ii-7-how-to-index-and-search/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/65969470780/hadoop-tutorials-season-ii-7-how-to-index-and-search
tumblr_gethue_id:
  - 65969470780
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

<p id="docs-internal-guid-6e44f291-2156-8489-431b-b515176c9fec">
  <span>In the previous episode we saw how to use </span><a href="http://gethue.tumblr.com/post/64707633719/hadoop-tutorial-use-pig-and-hive-with-hbase"><span>Pig and Hive with HBase</span></a><span>. This time, let’s see how to make our Yelp data searchable by indexing it and building a customizable UI with the </span><a href="http://gethue.tumblr.com/post/52804483421/tutorial-search-hadoop-in-hue"><span>Hue Search app</span></a><span>.</span>
</p>

&nbsp;

{{< youtube ATldKiiJdqY >}}

&nbsp;

# <span>Indexing data into Solr</span>

&nbsp;

<span>This tutorial is based on </span>[<span>SolrCloud</span>][1]<span>. Here is a step by step </span>[<span>guide</span>][2] <span>about its installation and a list of required </span>[<span>packages</span>][2]<span>:</span>

- <span>solr-server</span>
- <span>solr-mapreduce</span>
- <span>search</span>

&nbsp;

<span>Next step is about deploying and configuring Solr Cloud. We are following the </span>[<span>documentation</span>][3]<span>.</span>

&nbsp;

<span>After this, we </span>[<span>create</span>][4] <span>a new collection and index named ‘reviews’. We use our predefined schema that needs to be copied from the </span>[<span>Hadoop tutorial github</span>][5]<span>.</span>

&nbsp;

<pre class="code">cp solr_local/conf/schema.xml solr_configs/conf/schema.xml

solrctl instancedir --create reviews solr_local

solrctl collection --create reviews -s 1</pre>

<span>We replace the field definitions in the </span>[<span>schema</span>][6] <span>with a mapping corresponding to our Yelp data. The schema represents each data fields that will be available in the search index. You can read more about schema.xml in the </span>[<span>Solr wiki</span>][7]<span>.</span>

<pre class="code"> &lt;field name="business_id" type="text_en" indexed="true" stored="true" /&gt;  
  &lt;field name="cool" type="tint" indexed="true" stored="true" /&gt;
  &lt;field name="date" type="text_en" indexed="true" stored="true" /&gt;
  &lt;field name="funny" type="tint" indexed="true" stored="true" /&gt;
  &lt;field name="id" type="string" indexed="true" stored="true" required="true" multiValued="false" /&gt;  
  &lt;field name="stars" type="tint" indexed="true" stored="true" /&gt;
  &lt;field name="text" type="text_en" indexed="true" stored="true" /&gt;
  &lt;field name="type" type="text_en" indexed="true" stored="true" /&gt;         
  &lt;field name="useful" type="tint" indexed="true" stored="true" /&gt;
  &lt;field name="user_id" type="text_en" indexed="true" stored="true" /&gt;
  &lt;field name="name" type="text_en" indexed="true" stored="true" /&gt;
  &lt;field name="full_address" type="text_en" indexed="true" stored="true" /&gt;
  &lt;field name="latitude" type="tfloat" indexed="true" stored="true" /&gt;
  &lt;field name="longitude" type="tfloat" indexed="true" stored="true" /&gt;
  &lt;field name="neighborhoods" type="text_en" indexed="true" stored="true" /&gt;
  &lt;field name="open" type="text_en" indexed="true" stored="true" /&gt;
  &lt;field name="review_count" type="tint" indexed="true" stored="true" /&gt;
  &lt;field name="state" type="text_en" indexed="true" stored="true" /&gt;</pre>

Then, we retrieve and clean a subset of our Yelp data with a [Hive query][8], download it as CSV and index it with the [indexer tool][9] and this [command][10]:

<pre class="code">hadoop jar /usr/lib/solr/contrib/mr/search-mr-*-job.jar org.apache.solr.hadoop.MapReduceIndexerTool -D 'mapred.child.java.opts=-Xmx500m' --log4j /usr/share/doc/search*/examples/solr-nrt/log4j.properties --morphline-file solr_local/reviews.conf --output-dir hdfs://localhost:8020/tmp/load --verbose --go-live --zk-host localhost:2181/solr --collection reviews hdfs://localhost:8020/tmp/query_result.csv</pre>

<span>The command will use our </span>[<span>morphline file</span>][11] <span>to map the Yelp data to the fields defined in our index schema.xml.</span>

<span>While debugging morphline, the </span><span>—dry-run</span> <span>option will save you some time.</span>

&nbsp;

# <span>Customize the search result</span>

The administration panel lets you tweak the look & feel and features of the search page. This is explained in the second part of the video.

&nbsp;

# <span>Conclusion</span>

<span>Cloudera Search is great for opening your user base to Hadoop and do quick data retrieval. Some other articles describes greatly some user use cases, like </span>[<span>email</span>][12] <span>or </span>[<span>customer data</span>][13] <span>search.</span>

Cloudera Morphline is also an interesting tool for facilitating the indexing of your data. You can learn more about it on its [project website][14].

As usual feel free to comment on the [hue-user][15] list or [@gethue][16]!

&nbsp;

# <span>Troubleshooting</span>

1. If you see this error:

org.apache.solr.client.solrj.impl.HttpSolrServer\$RemoteSolrException:Error CREATEing SolrCore ‘reviews_shard1_replica1’: Unable to create core: reviews_shard1_replica1 Caused by: Could not find configName for collection reviews found:null</str>

<span>You might have forgotten to create the collection:</span>

<pre class="code">solrctl instancedir --create review solr_configs

</pre>

<span>2. If you see this error:</span>

<pre class="code">ERROR - 2013-10-10 20:01:21.383; org.apache.solr.servlet.SolrDispatchFilter; Could not start Solr. Check solr/home property and the logs
ERROR - 2013-10-10 20:01:21.409; org.apache.solr.common.SolrException; null:org.apache.solr.common.SolrException: solr.xml not found in ZooKeeper
       at org.apache.solr.core.ConfigSolr.fromSolrHome(ConfigSolr.java:109)
Server is shutting down</pre>

<span>You might need to force Solr to reload the configuration. Beware, this might break ZooKeeper and you might need to read error #3.</span>

&nbsp;

<span>3. If you see this error:</span>

<pre class="code">KeeperErrorCode = NoNode for /overseer/collection-queue-work&lt;/str&gt;
&lt;str name="trace"&gt;
org.apache.zookeeper.KeeperException$NoNodeException: KeeperErrorCode = NoNode for /overseer/collection-queue-work</pre>

&nbsp;

<span>It probably comes from error #2. You might need to re-upload the config and recreate the collection.</span>

[1]: http://wiki.apache.org/solr/SolrCloud
[2]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-Installation-Guide/csig_install_search.html
[3]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-Installation-Guide/csig_deploy_search_solrcloud.html
[4]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-Installation-Guide/csig_runtime_solr_config.html
[5]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/solr-local-search
[6]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/solr_local/conf/schema.xml#L109
[7]: http://wiki.apache.org/solr/SchemaXml
[8]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/data_subset.sql
[9]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-User-Guide/csug_batch_index_to_solr_servers_using_golive.html
[10]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/load_index.sh
[11]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/solr_local/reviews.conf
[12]: http://blog.cloudera.com/blog/2013/09/email-indexing-using-cloudera-search/
[13]: http://blog.cloudera.com/blog/2013/09/secrets-of-cloudera-support-impala-and-search-make-the-customer-experience-even-better/
[14]: http://cloudera.github.io/cdk/docs/current/cdk-morphlines/index.html
[15]: http://groups.google.com/a/cloudera.org/group/hue-user
[16]: https://twitter.com/gethue
