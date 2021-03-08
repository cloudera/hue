---
title: Oozie workflow credentials with a Hive action with Kerberos
author: admin
type: post
date: 2014-04-02T20:21:11+00:00
url: /hadoop-tutorial-oozie-workflow-credentials-with-a-hive-action-with-kerberos/
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

When using Hadoop security and scheduling jobs using [Hive][1] (or Pig, [HBase][2]) you might have received this error:

<pre><code class="bash">

Caused by: MetaException(message:Could not connect to meta store using any of the URIs provided. Most recent failure: org.apache.thrift.transport.TTransportException: GSS initiate failed

</code></pre>

Indeed, in order to use an Oozie Hive action with the Hive metastore server when Kerberos is enabled, you need to use HCatalog credentials in your workflow.

Here is a demo, with a kerberized cluster and a MySql Hive metastore showing how it works. We create a Hive script that will list the tables and performs an operation requiring the HCat credential. Please find all the used and generated configurations [here][3].

{{< youtube 6meeq7xvj54 >}}

Hue fills up automatically the parameters for you, just check the credentials required on your workflow action and Hue will:

- Pull dynamically the available credentials details from the cluster
- Configure the credentials in workflows for you

Then don’t forget to check the HCat credential in the Hive action advanced properties. You can check multiple credentials if you ever need to.

And that’s it! Submit the workflow and check its output, you will see the list of tables and the result of the computation of the second query!

As usual feel free to comment on the [hue-user][4] list or [@gethue][5]!

**Note**:

Hive should not access directly the metastore database via JDBC, or it will bypass the protection.

Include a <span style="color: #ff0000;">hive-config.xml</span> in the Job XML property of the Hive action with this type of configuration:

<pre><code class="xml">

<property>

<name>javax.jdo.option.ConnectionURL</name>

<value>jdbc:mysql://hue.com:3306/hive1?useUnicode=true&characterEncoding=UTF-8</value>

</property>

<property>

<name>javax.jdo.option.ConnectionDriverName</name>

<value>com.mysql.jdbc.Driver</value>

</property>

<property>

<name>javax.jdo.option.ConnectionUserName</name>

<value>hive1</value>

</property>

<property>

<name>javax.jdo.option.ConnectionPassword</name>

<value>hive1</value>

</property>

</code></pre>

Use this one:

<pre><code class="xml">

<property>

<name>hive.metastore.local</name>

<value>false</value>

</property>

<property>

<name>hive.metastore.uris</name>

<value>thrift://hue.com:9083</value>

</property>

<property>

<name>hive.metastore.sasl.enabled</name>

<value>true</value>

</property>

</code></pre>

**Note**:

When the job will try to connect to MySql, you might hit this missing jar problem:

<pre><code class="bash">

Caused by: org.datanucleus.store.rdbms.datasource.DatastoreDriverNotFoundException: The specified datastore driver ("com.mysql.jdbc.Driver") was not found in the CLASSPATH. Please check your CLASSPATH specification, and the name of the driver.

<pre></code></pre>

To solve it, simply download the MySql jar connector from http://dev.mysql.com/downloads/connector/j/, and have HiveServer2 points to it with:

<pre><code class="xml">

<property>

<name>hive.aux.jars.path</name>

<value>file:///usr/share/java//mysql-connector-java.jar</value>

</property>

</code></pre>

**Note**:

To activate the credentials in Oozie itself, update this property in oozie-site.xml

<pre><code class="xml">

<property>

 <name>oozie.credentials.credentialclasses</name>

 <value>

   hcat=org.apache.oozie.action.hadoop.HCatCredentials,

   hbase=org.apache.oozie.action.hadoop.HbaseCredentials

 </value>

</property>

</code></pre>

[1]: https://gethue.com/hadoop-tutorial-how-to-access-hive-in-pig-with/
[2]: https://gethue.com/hadoop-tutorial-use-pig-and-hive-with-hbase/
[3]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/oozie/credentials
[4]: http://groups.google.com/a/cloudera.org/group/hue-user
[5]: https://twitter.com/gethue
