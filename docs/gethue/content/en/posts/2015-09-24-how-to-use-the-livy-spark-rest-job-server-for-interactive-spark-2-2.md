---
title: How to use the Livy Spark REST Job Server API for doing some interactive Spark with curl
author: admin
type: post
date: 2015-09-24T00:32:51+00:00
url: /how-to-use-the-livy-spark-rest-job-server-for-interactive-spark-2-2/
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
sf_remove_promo_bar:
  - 1
categories:
  - Development

---
<span style="font-weight: 400;">Livy is an </span>[<span style="font-weight: 400;">open source REST interface</span>][1] <span style="font-weight: 400;">for using Spark from anywhere.</span>

**Note**: Livy is not supported in CDH, only in the [upstream Hue][2] community.

&nbsp;

<span style="font-weight: 400;">It supports executing snippets of code or programs in a Spark Context that runs locally or in YARN. This makes it ideal for building applications or Notebooks that can interact with Spark in real time. For example, it is currently used for powering the Spark snippets of the <a href="https://gethue.com/spark-notebook-and-livy-rest-job-server-improvements/">Hadoop Notebook</a> in Hue.</span>

<span style="font-weight: 400;">In this post we see how we can execute some <a href="https://spark.apache.org/releases/spark-release-1-5-0.html">Spark 1.5</a> snippets in Python.</span>

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2015/09/20150818_scalabythebay.012-1024x576.png"  />][3]

<p id="starting" style="text-align: center;">
  Livy sits between the remote users and the Spark cluster
</p>

&nbsp;

## **Starting the REST server**

<span style="font-weight: 400;">Based on the <a href="https://github.com/cloudera/hue/tree/master/apps/spark/java#building-livy">README</a>, we check out Livy's code. It is currently living in Hue repository for simplicity but hopefully will eventually graduate in its top project.</span>

<pre><code class="bash">git clone git@github.com:cloudera/hue.git</code></pre>

<span style="font-weight: 400;">Then we compile Livy with</span>

<pre><code class="bash">cd hue/apps/spark/java

mvn -DskipTests clean package

</code></pre>

<span style="font-weight: 400;">Export these variables</span>

<pre><code class="bash">export SPARK_HOME=/usr/lib/spark

export HADOOP_CONF_DIR=/etc/hadoop/conf</code></pre>

<span style="font-weight: 400;">And start it</span>

<pre><code class="bash">./bin/livy-server</code></pre>

**Note**: Livy defaults to Spark local mode, to use the YARN mode copy the configuration template file [apps/spark/java/conf/livy-defaults.conf.tmpl][4] into livy-defaults.conf and set the property:

<pre><code class="bash">livy.server.session.factory = yarn</code></pre>

&nbsp;

## **Executing some Spark**

As the REST server is running, we can communicate with it. We are on the same machine so will use 'localhost' as the address of Livy.

<span style="font-weight: 400;">Let's list our open sessions</span>

<pre><code class="bash">curl localhost:8998/sessions

{"from":0,"total":0,"sessions":[]}

</code></pre>

Note

You can use

<pre><code class="bash"> | python -m json.tool</code></pre>

at the end of the command to prettify the output, e.g.:

<pre><code class="bash">curl localhost:8998/sessions/0 | python -m json.tool</code></pre>

&nbsp;

<span style="font-weight: 400;">There is zero session. We create an interactive PySpark session</span>

<pre><code class="bash">curl -X POST -data '{"kind": "pyspark"}' -H "Content-Type: application/json" localhost:8998/sessions

{"id":0,"state":"starting","kind":"pyspark","log":[]}

</code></pre>

&nbsp;

Sessions ids are incrementing numbers starting from 0. We can then reference the session later by its id.

Livy supports the three languages of Spark:

<table>
  <tr>
    <td>
      <span style="font-weight: 400;">Kinds</span>
    </td>

    <td>
      <span style="font-weight: 400;">Languages</span>
    </td>
  </tr>

  <tr>
    <td>
      <span style="font-weight: 400;">spark</span>
    </td>

    <td>
      <span style="font-weight: 400;">Scala</span>
    </td>
  </tr>

  <tr>
    <td>
      <span style="font-weight: 400;">pyspark</span>
    </td>

    <td>
      <span style="font-weight: 400;">Python</span>
    </td>
  </tr>

  <tr>
    <td>
      <span style="font-weight: 400;">sparkr</span>
    </td>

    <td>
      <span style="font-weight: 400;">R</span>
    </td>
  </tr>
</table>

&nbsp;

We check the status of the session until its state becomes `idle`: it means it is ready to be execute snippet of PySpark:

<pre><code class="bash">curl localhost:8998/sessions/0 | python -m json.tool

% Total % Received % Xferd Average Speed Time Time Time Current

Dload Upload Total Spent Left Speed

100 1185 0 1185 0 0 72712 0 -:-:- -:-:- -:-:- 79000

{

"id": 5,

"kind": "pyspark",

"log": [

"15/09/03 17:44:14 INFO util.Utils: Successfully started service 'SparkUI' on port 4040.",

"15/09/03 17:44:14 INFO ui.SparkUI: Started SparkUI at http://172.21.2.198:4040",

"15/09/03 17:44:14 INFO spark.SparkContext: Added JAR file:/home/romain/projects/hue/apps/spark/java-lib/livy-assembly.jar at http://172.21.2.198:33590/jars/livy-assembly.jar with timestamp 1441327454666",

"15/09/03 17:44:14 WARN metrics.MetricsSystem: Using default name DAGScheduler for source because spark.app.id is not set.",

"15/09/03 17:44:14 INFO executor.Executor: Starting executor ID driver on host localhost",

"15/09/03 17:44:14 INFO util.Utils: Successfully started service 'org.apache.spark.network.netty.NettyBlockTransferService' on port 54584.",

"15/09/03 17:44:14 INFO netty.NettyBlockTransferService: Server created on 54584",

"15/09/03 17:44:14 INFO storage.BlockManagerMaster: Trying to register BlockManager",

"15/09/03 17:44:14 INFO storage.BlockManagerMasterEndpoint: Registering block manager localhost:54584 with 530.3 MB RAM, BlockManagerId(driver, localhost, 54584)",

"15/09/03 17:44:15 INFO storage.BlockManagerMaster: Registered BlockManager"

],

"state": "idle"

}</code></pre>

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2015/09/20150818_scalabythebay.024-1024x576.png"  />][5]

<p style="text-align: center;">
  In YARN mode, Livy creates a remote Spark Shell in the cluster that can be accessed easily with REST
</p>

&nbsp;

<span style="font-weight: 400;">When the session state is <code>idle</code>, it means it is ready to accept statements! Lets compute <code>1 + 1</code></span>

<pre><code class="bash">curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"1 + 1"}'

{"id":0,"state":"running","output":null}

</code></pre>

We check the result of statement 0 when its state is `available`

<pre><code class="bash">curl localhost:8998/sessions/0/statements/0

{"id":0,"state":"available","output":{"status":"ok","execution_count":0,"data":{"text/plain":"2"}}}

</code></pre>

Note

If the statement is taking less than a few milliseconds, Livy returns the response directly in the response of the POST command.

Statements are incrementing and all share the same context, so we can have a sequences

<pre><code class="bash">curl localhost:8998/sessions/0/statements -X POST -H 'Content-Type: application/json' -d '{"code":"a = 10"}'

{"id":1,"state":"available","output":{"status":"ok","execution_count":1,"data":{"text/plain":""}}}

</code></pre>

Spanning multiple statements

<pre><code class="bash">curl localhost:8998/sessions/5/statements -X POST -H 'Content-Type: application/json' -d '{"code":"a + 1"}'

{"id":2,"state":"available","output":{"status":"ok","execution_count":2,"data":{"text/plain":"11"}}}

</code></pre>

&nbsp;

<span style="font-weight: 400;">Let's close the session to free up the cluster. Note that Livy will automatically inactive idle sessions after 1 hour (<a href="https://github.com/cloudera/hue/blob/master/apps/spark/java/conf/livy-defaults.conf.tmpl#L17">configurable</a>).</span>

<pre><code class="bash">curl localhost:8998/sessions/0 -X DELETE

{"msg":"deleted"}

</code></pre>

&nbsp;

## <span style="font-weight: 400;">Impersonation</span>

Let's say we want to create a shell running as the user `bob`, this is particularly useful when multi users are sharing a Notebook server

<pre><code class="bash">curl -X POST -data '{"kind": "pyspark", "proxyUser": "bob"}' -H "Content-Type: application/json" localhost:8998/sessions

{"id":0,"state":"starting","kind":"pyspark","proxyUser":"bob","log":[]}

</code></pre>

Do not forget to add the user running Hue (your current login in dev or `hue` in production) in the Hadoop proxy user list (`/etc/hadoop/conf/core-site.xml`):

<pre><code class="xml"><property>

<name>hadoop.proxyuser.hue.hosts</name>

<value>*</value>

</property>

<property>

<name>hadoop.proxyuser.hue.groups</name>

<value>*</value>

</property>

</code></pre>

## <span style="font-weight: 400;">Additional properties</span>

<span style="font-weight: 400;">All the properties supported by spark shells like the <a href="https://github.com/cloudera/hue/tree/master/apps/spark/java#request-body">number of executors, the memory</a>, etc can be changed at session creation. Their format is the same as when typing <code>spark-shell -h</code></span>

<pre><code class="bash">curl -X POST -data '{"kind": "pyspark", "numExecutors": "3", "executorMemory": "2G"}' -H "Content-Type: application/json" localhost:8998/sessions

{"id":0,"state":"starting","kind":"pyspark","numExecutors":"3","executorMemory":"2G","log":[]} </code></pre>

&nbsp;

<span style="font-weight: 400;">And that's it! Next time we will explore some more advanced features like the magic keywords for introspecting data or printing images. Then, we will detail how to do batch submissions in compiled Scala, Java or Python (i.e. jar or py files).</span>

The architecture of Livy was [presented][6] for the first time at Big Data Scala by the Bay last August and next updates will be at the [Spark meetup][7] before Strata NYC and [Spark Summit][8] in Amsterdam.

&nbsp;

<span style="font-weight: 400;">Feel free to ask any questions about the architecture, usage of the server in the comments, <a href="http://twitter.com/gethue">@gethue</a> or the <a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a> list. And </span>[<span style="font-weight: 400;">pull requests</span>][9] <span style="font-weight: 400;">are always welcomed!</span>

&nbsp;

&nbsp;

 [1]: https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server
 [2]: https://github.com/cloudera/hue
 [3]: https://cdn.gethue.com/uploads/2015/09/20150818_scalabythebay.012.png
 [4]: https://github.com/cloudera/hue/blob/master/apps/spark/java/conf/livy-defaults.conf.template
 [5]: https://cdn.gethue.com/uploads/2015/09/20150818_scalabythebay.024.png
 [6]: https://gethue.com/big-data-scala-by-the-bay-interactive-spark-in-your-browser/
 [7]: https://www.eventbrite.com/e/spark-lightning-night-at-shutterstock-nyc-tickets-17590432457
 [8]: https://spark-summit.org/eu-2015/events/building-a-rest-job-server-for-interactive-spark-as-a-service/
 [9]: https://github.com/cloudera/hue/pulls
