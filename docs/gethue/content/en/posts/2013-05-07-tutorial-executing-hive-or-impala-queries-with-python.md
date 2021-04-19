---
title: Executing Hive or Impala Queries with Python
author: admin
type: post
date: 2013-05-07T21:58:00+00:00
url: /tutorial-executing-hive-or-impala-queries-with-python/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/49882746559/tutorial-executing-hive-or-impala-queries-with-python
tumblr_gethue_id:
  - 49882746559
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
  - Development

---
<p id="docs-internal-guid-3030a9d6-8100-9572-805c-bc5817743118">
  <span>This post talks about Hue, a</span><a href="https://gethue.com"><span>UI</span></a><span> for making Apache Hadoop easier to use.</span>
</p>

<span>Hue uses a various set of interfaces for communicating with the Hadoop components. This post describes how Hue is implementing the </span>[Apache HiveServer2][1] <span>Thrift API for executing </span>[Hive queries][2] <span>and listing tables. The same interface can also be used for talking to </span>[Cloudera Impala][3]<span>.</span>

### <span> </span>

### <span>Hive</span>

<span>This code requires </span>[Hue 2.3 ][4]<span>or later in order to successfully work. We are using the Beeswax examples as data. They can be installed in the second step of the Hue Quick Start wizard. Obviously, Hive Server 2 needs to be running.</span>

<span>First we log in in the Hue shell. HUE_HOME is the path where was Hue installed:</span>

<pre class="code">$HUE_HOME/build/env/bin/hue shell</pre>

<span>Create a user under which the queries are going to be sent:</span>

<pre class="code">from beeswax.server import dbms
from django.contrib.auth.models import User
hue, created = User.objects.get_or_create(username='hue')</pre>

<span>1. List the tables of the default database:</span>

<pre class="code">db = dbms.get(hue)
db.get_tables()
&gt;
['sample_07', 'sample_08']</pre>

<span>2. Execute a statement. </span>

<span>Here we are doing a SELECT in order to calculate the average salaries of the employes but it could be any SQL statements (e.g. CREATE, ALTER, SHOW…):</span>

<pre class="code">query = db.execute_statement('select avg(salary) from sample_07')</pre>

<span>We then check for the query completion:</span>

<pre class="code">db.get_state(query.get_handle())
&gt; EnumValue(&lt;enum.Enum object at 0x29d8b50&gt;, 1, 'running')

db.get_state(query.get_handle())
&gt; EnumValue(&lt;enum.Enum object at 0x29d8b50&gt;, 1, 'running')

db.get_state(query.get_handle())
&gt; EnumValue(&lt;enum.Enum object at 0x29d8b50&gt;, 2, 'available')</pre>

<span>Here we fetch the result and show its structure:</span>

<pre class="code">result = db.fetch(query.get_handle())
&gt; dir(result)
['__doc__',
'__init__',
'__module__',
'cols',
'columns',
'data_table',
'has_more',
'ready',
'rows',
'start_row']</pre>

<span>The result is a generator, this is a way to print its content:</span>

<pre class="code">for row in result.rows():
 print row

&gt; [47963.62637362637]</pre>

<span>Query logs can be retrieved like this:</span>

<pre class="code">print db.get_log(query.get_handle())

&gt; 13/04/22 17:32:50 INFO ql.Driver: &lt;PERFLOG method=compile&gt;
13/04/22 17:32:50 INFO parse.SemanticAnalyzer: Starting Semantic Analysis
13/04/22 17:32:50 INFO parse.SemanticAnalyzer: Completed phase 1 of Semantic Analysis
...
13/04/22 17:32:50 WARN mapred.JobClient: Use GenericOptionsParser for parsing the arguments. Applications should implement Tool for the same.
13/04/22 17:32:50 WARN conf.Configuration: io.bytes.per.checksum is deprecated. Instead, use dfs.bytes-per-checksum
13/04/22 17:32:50 INFO exec.Task: Starting Job = job_201304170951_0028, Tracking URL = http://localhost:50030/jobdetails.jsp?jobid=job_201304170951_0028
13/04/22 17:32:50 INFO exec.Task: Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_201304170951_0028
13/04/22 17:32:52 INFO exec.Task: Hadoop job information for Stage-1: number of mappers: 1; number of reducers: 1
13/04/22 17:32:52 WARN mapreduce.Counters: Group org.apache.hadoop.mapred.Task$Counter is deprecated. Use org.apache.hadoop.mapreduce.TaskCounter instead
13/04/22 17:32:52 INFO exec.Task: 2013-04-22 17:32:52,927 Stage-1 map = 0%,  reduce = 0%
13/04/22 17:32:55 INFO exec.Task: 2013-04-22 17:32:55,937 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 0.66 sec
13/04/22 17:32:56 INFO exec.Task: 2013-04-22 17:32:56,942 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 0.66 sec
...</pre>

<span>Note</span>

<span>HiveServer2 by default uses ThriftSASL transport. You can run it in non-sasl mode by adding the following to the hive-site.xml:</span>

<pre class="code">&lt;property&gt;
  &lt;name&gt;hive.server2.authentication&lt;/name&gt;
  &lt;value&gt;NOSASL&lt;/value&gt;
&lt;/property&gt;</pre>

### <span> </span>

### <span>Impala</span>

<span>Impala is using the same API as HiveServer2. We reuse the same client by just specifying Impala as the server.</span>

<pre class="code">from beeswax.server.dbms import get_query_server_config

impala_config = get_query_server_config(name='impala')
db = dbms.get(hue, impala_config)</pre>

<span>We can then perform the same operations as with HiveServer2:</span>

<pre class="code">db.get_tables()
query = db.execute_statement('select avg(salary) from sample_07')
...</pre>

<span>Note</span>

<span>Impala needs to be configured for the HiveServer2 interface, as detailed in the </span>[<span>hue.ini</span>][5]<span>.</span>

### <span> </span>

### <span>How it works</span>

<span>Here are the steps done in order to send the queries from Hue:</span>

  1. <span>Grab the </span>[<span>HiveServer2 IDL</span>][6]<span>.</span>
  2. <span>Generate the python code with </span>[<span>Thrift 0.9</span>][7]<span>. Hue does it with this script </span>[<span>regenerate_thrift.sh</span>][8]<span>.</span>
  3. <span>Implement it. This is </span>[<span>hive_server2_lib.py</span>][9]<span>.</span>
  4. <span>An extra layer (</span>[<span>dbms.py</span>][10]<span>) has been added in order to simplify the use of the raw API and keep compatibility with Beeswax (ancestor of Hive Server 2). This is what we use in the above example. This is the list of all the possible operations.</span>

### <span> </span>

### <span>Sum-up</span>

<span>Hue 2.3 supports most of the functionalities of HiveServer2 and Impala interfaces. The full implementation will be available in Hue 2.4 or in the upcoming CDH4.3 release (and is already in Hue master). User sessions are saved in the Hue DB and are transparent in the use of the API.</span>

<span>Hue’s Beeswax and Impala apps are now based on the HiveServer2 interface which offers a more robust alternative than Beeswax. Hue’s implementation can be reused for building new apps or clients. Feel free to post comments or question on the </span>[hue group][11]<span>!</span>

 [1]: http://hive.apache.org/
 [2]: http://blog.cloudera.com/blog/2013/04/demo-analyzing-data-with-hue-and-hive/
 [3]: http://cloudera.com/content/cloudera/en/campaign/introducing-impala.html
 [4]: http://blog.cloudera.com/blog/2013/04/whats-new-in-hue-2-3/
 [5]: https://github.com/cloudera/hue/blob/branch-2.3/desktop/conf.dist/hue.ini#L432
 [6]: http://svn.apache.org/viewvc/hive/branches/branch-0.11/service/if/TCLIService.thrift?view=markup
 [7]: http://thrift.apache.org/
 [8]: https://github.com/cloudera/hue/blob/master/apps/beeswax/regenerate_thrift.sh
 [9]: https://github.com/cloudera/hue/blob/master/apps/beeswax/src/beeswax/server/hive_server2_lib.py
 [10]: https://github.com/cloudera/hue/blob/master/apps/beeswax/src/beeswax/server/dbms.py
 [11]: http://groups.google.com/a/cloudera.org/group/hue-user
