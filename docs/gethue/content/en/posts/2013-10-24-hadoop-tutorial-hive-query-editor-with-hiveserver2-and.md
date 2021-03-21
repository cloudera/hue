---
title: Hive Query editor with HiveServer2 and Sentry
author: admin
type: post
date: 2013-10-24T01:21:00+00:00
url: /hadoop-tutorial-hive-query-editor-with-hiveserver2-and/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/64916325309/hadoop-tutorial-hive-query-editor-with-hiveserver2-and
tumblr_gethue_id:
  - 64916325309
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

<p id="docs-internal-guid-2b663878-e805-7a5b-0d8e-b165706741fc">
  <span>Hue provides a Web interface for submitting Hive queries. Hue had its own server to service Hive queries called Beeswax. The more sophisticated and robust service, Apache </span><a href="http://blog.cloudera.com/blog/2013/07/how-hiveserver2-brings-security-and-concurrency-to-apache-hive/"><span>HiveServer2</span></a><span>, is supported as of Hue 2.5.</span>
</p>

{{< youtube -Py11X0G6Hs >}}

# <span>Beeswax Hive Editor</span>

Thanks to HiveServer2 integration, Hue is getting the benefits from [Sentry][1] (How to [configure Sentry Video][2]). In addition to the [<span>security</span>][3] provided, Hue’s interface becomes more consistent. For example, a user without permissions on a database or table won’t see it in the query editor or in the [<span>Metastore app</span>][4].

<span>HiveServer2 also provides performant access to the </span>[<span>Metastore</span>][4]<span>.</span>

<span>On top of this, the Beeswax Hive UI is a Web editor for increasing the productivity:</span>

- <span>Syntax highlighting and auto completion</span>
- <span>Submit several queries and check they progress later</span>
- [<span>UDF</span>][5] <span>integration</span>
- <span>Multiple queries execution</span>
- <span>Select and send a fraction of a query</span>
- <span>Download or save the query results</span>
- <span>Navigate through the metadata</span>

## <span>Hue 2.x</span>

<span>We recommend to use the latest version of Hue (2.5). Have Hue point to HiveServer2 by updating the Beeswax section in the </span>[<span>hue.ini</span>][6]<span>:</span>

<pre class="code">[beeswax]
  beeswax_server_host=&lt;FQDN of Beeswax server&gt;
  server_interface=hiveserver2
  beeswax_server_port=10000</pre>

## <span>Hue 3.x</span>

<span>Hue 3 does not bundle Beeswaxd anymore, and is configured by default to use HiveServer2. If HiveServer2 is not on the same machine as Hue update </span>[<span>hue.ini</span>][7] <span>with:</span>

<pre class="code">[beeswax]
 hive_server_host=&lt;FQDN of HiveServer2&gt;</pre>

<span>Other Hive specific settings (e.g. security, impersonation) are read from a local </span>[<span>/etc/hive/conf/hive-site.xml</span>][8]<span>. We recommend to keep this one in exact sync with the original Hive one (or put Hue and Hive on the same machine).</span>

<span><strong><br /> Note</strong>:</span>

If you are using Hive 0.12 or later, Hue needs to have [HUE-1561][9] (or use Hue 3.0 or later).

## With Sentry: Hue 2.x or 3.x

Hue will automatically work with a HiveServer2 configured with Sentry.

Notice that HiveServer2 impersonation (described below) should be turned off in case of Sentry. Permissions of the impersonated user (e.g. ‘bob’) will be used instead of the ones of the ‘hue’ user. Also we need the warehouse permissions to be owned by hive:hive with 770 so that only super users in hive group can read, write.

HiveServer2 needs to be using strong authentication like Kerberos/LDAP for Sentry to work.

# <span>Troubleshooting without Sentry</span>

<pre class="code">org.apache.hive.service.cli.HiveSQLException: Error while processing statement: FAILED: Execution Error, return code 1 from org.apache.hadoop.hive.ql.exec.DDLTask. MetaException(message:Got exception: org.apache.hadoop.security.AccessControlException Permission denied: user=hive, access=WRITE, inode="/user/test/data":test:supergroup:drwxr-xr-x</pre>

<span>By default HiveServer2 now owns the Hive warehouse (default ‘</span><span>/user/hive/warehouse</span><span>’), meaning the data files need to belong to the ‘hive’ user. If you get this error when creating a table, change the permission of the data directory (here </span><span>/user/test/data</span><span>) to ‘write’ for everybody or revert HiveServer2 to the old Beeswax behavior by authorizing ‘hive’ to impersonate the user. </span>

Adding ‘hive’ as a Hadoop [proxy user][10] and edit your hive-site.xml:

<pre class="code">&lt;property&gt;
   &lt;name&gt;hive.server2.enable.doAs&lt;/name&gt;
   &lt;value&gt;true&lt;/value&gt;
 &lt;/property&gt;</pre>

<span>Then restart HiveServer2:</span>

<pre class="code">sudo service hive-server2 restart</pre>

<span>Another common error when using YARN is:</span>

<pre class="code">Cannot initialize Cluster. Please check your configuration for mapreduce.framework.name and the correspond server addresses.</pre>

It means that the HADOOP_MAPRED_HOME environment variable is not set to:

<pre class="code">export HADOOP_MAPRED_HOME=/usr/lib/hadoop-mapreduce</pre>

<span>HADOOP_HOME could also be wrong.</span>

<pre class="code">TTransportException('Could not start SASL: Error in sasl_client_start (-4) SASL(-4): no mechanism available: No worthy mechs found',)</pre>

<span>Hue is missing a </span>[<span>SASL lib</span>][11] <span>in your system.</span>

<span>HiveServer2 supports 3 authentication modes specified by the ‘hive.server2.authentication’ in hive-site.xml:</span>

- <span>NOSASL</span>
- <span>NONE (default)</span>
- <span>KERBEROS</span>

Only NOSASL does not require SASL, so you either switch to it or install the missing packages.

Hue will pick the value from its local [/etc/hive/conf/hive-site.xml][12] so make sure it is synced with the original hive-site.xml (manually or via CM Beeswax safety valve).

e.g.

<property>

<name>hive.server2.authentication</name>

<value>NOSASL</value>

</property>

<pre class="code"></pre>

<pre class="code">Error while compiling statement: FAILED: RuntimeException org.apache.hadoop.security.AccessControlException: Permission denied: user=admin, access=WRITE, inode="/tmp/hive-hive":hive:hdfs:drwxr-xr-x at org.apache.hadoop.hdfs.server.namenode.FSPermissionChecker.check(FSPermissionChecker.java:234) at org.apache.hadoop.hdfs.server.namenode.FSPermissionChecker.check(FSPermissionChecker.java:214) at org.apache.hadoop.hdfs.server.namenode.FSPermissionChecker.checkPermission(FSPermissionChecker.java:158)</pre>

The Hive HDFS workspace ‘/tmp/hive-hive’ would need to be set to 1777 permissions.

# Troubleshooting with Sentry

<pre class="code">AuthorizationException: User 'hue/test.com' does not have privileges to execute 'CREATE' on: default.sample_08"</pre>

The user ‘hue’ is not configured in Sentry and have not the CREATE table permission.

# <span>Conclusion</span>

<span>Hue provides a great environment for executing Hive queries in a friendly UI. Beeswaxd was a great service but has been deprecated in favor of HiveServer2. HiveServer2 offers more stability and security. </span>

<span>As a side note, if you are looking for even faster SQL queries, we encourage you to test the </span>[<span>Impala Editor</span>][13]<span>!</span>

<span>If you have questions or feedback, feel free to contact the Hue community on </span>[<span>hue-user</span>][14] <span>or </span>[<span>@gethue.com</span>][15]<span>!</span>

[1]: http://cloudera.com/content/cloudera/en/campaign/introducing-sentry.html
[2]: https://blogs.apache.org/sentry/entry/getting_started
[3]: http://sentry.incubator.apache.org
[4]: http://gethue.tumblr.com/tagged/metastore
[5]: http://gethue.tumblr.com/post/58711590309/hadoop-tutorial-hive-udf-in-1-minute
[6]: https://github.com/cloudera/hue/blob/branch-2.5.1/desktop/conf.dist/hue.ini#L384
[7]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L438
[8]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L450
[9]: https://issues.cloudera.org/browse/HUE-1561
[10]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Security-Guide/cdh4sg_topic_9_1.html?scroll=topic_9_1_3_unique_1__title_140_unique_1
[11]: https://github.com/cloudera/hue#development-prerequisites
[12]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L471
[13]: http://gethue.tumblr.com/post/62452792255/fast-sql-with-the-impala-query-editor
[14]: http://groups.google.com/a/cloudera.org/group/hue-user
[15]: http://twitter.com/gethue
