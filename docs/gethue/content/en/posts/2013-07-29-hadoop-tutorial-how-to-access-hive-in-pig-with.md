---
title: How to access Hive in Pig with HCatalog in Hue
author: admin
type: post
date: 2013-07-29T19:25:00+00:00
url: /hadoop-tutorial-how-to-access-hive-in-pig-with/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/56804308712/hadoop-tutorial-how-to-access-hive-in-pig-with
tumblr_gethue_id:
  - 56804308712
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

<p id="docs-internal-guid-058adb35-2bdf-a121-9dad-1fb68e2c56c5">
  <span>This blog post is about accessing the Hive Metastore from Hue, the open source </span><a href="http://gethue.com"><span>Hadoop UI</span></a><span> and clearing up some confusion about HCatalog usage.</span>
</p>

{{< youtube FgozGP1JdI0 >}}

# <span>What is HCatalog?</span>

<a href="http://hive.apache.org/docs/hcat_r0.5.0/" target="_blank" rel="noopener noreferrer">Apache HCatalog</a> is a project enabling non-Hive scripts to access Hive tables. You can then directly load tables with Pig or MapReduce without having to worry about re-defining the input schemas, caring about the data location or duplicating it.

&nbsp;

<span>Hue comes with an application for accessing the Hive metastore within your browser: Metastore Browser. Databases and tables can be navigated through and created or deleted with some wizards.</span>

&nbsp;

<span>The wizards were demonstrated in the previous tutorial about how to </span>[<span>Analyse Yelp data</span>][1]<span>. Hue uses </span>[<span>HiveServer2</span>][2] <span>for accessing the Hive Metastore instead of HCatalog. This is because HiveServer2 is the new secure and multi concurrent server for Hive and it already includes a fast Hive Metastore API.</span>

&nbsp;

<span>HCatalog connectors are however useful for accessing Hive data from Pig. Here is a demo about accessing the Hive example tables from the </span>[<span>Pig Editor</span>][3]<span>.</span>

&nbsp;

<span>Here is a video summary of the new features:</span>

&nbsp;

# <span>Tutorial</span>

<span>First you need to install HCatalog from </span>[<span>here</span>][4] <span>or Cloudera Manager. If you are using a non-pseudo-distributed cluster (e.g. not on a demo VM) make sure that the Hive Metastore is </span>[<span>remote</span>][5] <span>or you will have an error like below. Then, upload the 3 jars from /usr/lib/hcatalog/share/hcatalog/ and all the Hive ones from /usr/lib/hive/lib to the Oozie Pig sharelib in /user/oozie/share/lib/pig. This can be done in a few clicks while being logged as ‘oozie’ or ‘hdfs’ in the File Browser. Beware than all the jars will be included in all the future Pig script, which might be unnecessary.</span>

&nbsp;

**Update!**

In Hue 3.6 or CDH5, no need to copy the jars anymore. Just include the hive-site.xml file as File in the Properties of the script, e.g, /user/test/hive-site.xml

&nbsp;

<span>Then make sure the Beeswax examples are installed (Step #2 in the Quick Start Wizard) and open up the Pig Editor and compute the </span>[<span>average salary</span>][6] <span>in the table (equivalent of this Hive </span>[<span>query</span>][7]<span>):</span>

&nbsp;

<pre class="code">-- Load table 'sample_07'
sample_07 = LOAD 'sample_07' USING org.apache.hcatalog.pig.HCatLoader();

-- Compute the average salary of the table
salaries = GROUP sample_07 ALL;
out = FOREACH salaries GENERATE AVG(sample_07.salary);
DUMP out;</pre>

&nbsp;

<span>As HCatalog needs to access the metastore, we need to specify the hive-site.xml. Go in ‘Properties’, ‘Resources’ and add a ‘File’ pointing to the hive-site.xml uploaded on HDFS.</span>

&nbsp;

<span>Then submit the script by pressing CTRL + ENTER! The result (47963.62637362637)</span>

<span>will appear at the end of the log output.</span>

&nbsp;

<span>Notice that we don’t need to redefine the schema as it is automatically picked-up by the loader. If you use the Oozie App, you can now freely use HCatalog in your Pig actions.</span>

&nbsp;

**Warning!**

<span>If you are getting this error, it means that your metastore belong to the Hive user and is not remote. </span>

<pre class="code">Cannot get a connection, pool error Could not create a validated object, cause: A read-only user or a user in a read-only database is not permitted to disable read-only mode on a connection.

2013-07-24 23:20:04,969 [main] INFO  DataNucleus.Persistence  - DataNucleus Persistence Factory initialised for datastore URL="jdbc:derby:;databaseName=/var/lib/hive/metastore/metastore_db;create=true" driver="org.apache.derby.jdbc.EmbeddedDriver" userName="APP"</pre>

&nbsp;

<pre class="code">sudo rm /var/lib/hive/metastore/metastore_db/*lck
sudo chmod 777 -R /var/lib/hive/metastore/metastore_db</pre>

&nbsp;

<span>Similarly as HCatLoader, use </span>[<span>HCatStorer</span>][8] <span>for updating back the table, e.g.:</span>

<pre class="code">STORE alias INTO 'sample_07' USING org.apache.hcatalog.pig.HCatStorer();</pre>

&nbsp;

# <span>Summary</span>

<span>We saw that Hue makes Hive Metastore easy to access and supports the HCatalog connectors for Pig. Hue 3.0 with simplify it even more by automatically copying the required jar files and making the table names </span>[<span>auto-completable</span>][9]<span>!</span>

<span>As usual, we welcome any feedback on the </span>[<span>user group</span>][10]<span>!</span>

[1]: http://blog.cloudera.com/blog/2013/04/demo-analyzing-data-with-hue-and-hive/
[2]: http://blog.cloudera.com/blog/2013/07/how-hiveserver2-brings-security-and-concurrency-to-apache-hive/
[3]: http://gethue.tumblr.com/post/51559235973/tutorial-apache-pig-editor-in-hue-2-3
[4]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_19.html
[5]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_hive_metastore_configure.html
[6]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hcatalog/avg_salary.pig
[7]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hcatalog/avg_salary.hql
[8]: http://hive.apache.org/docs/hcat_r0.5.0/loadstore.html#HCatStorer
[9]: https://issues.cloudera.org/browse/HUE-1409
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
