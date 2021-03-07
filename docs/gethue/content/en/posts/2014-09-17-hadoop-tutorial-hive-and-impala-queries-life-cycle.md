---
title: Hive and Impala queries life cycle
author: admin
type: post
date: 2014-09-17T21:58:01+00:00
url: /hadoop-tutorial-hive-and-impala-queries-life-cycle/
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
slide_template:
  - default
categories:

---
<span style="color: #ff0000;"><em>Last update March 29th 2017</em></span>

The [editor][1] is used a lot for querying Hive and Impala. Here are some tips on how to manage their resource.

[<img src="https://cdn.gethue.com/uploads/2014/03/sql-editor-1024x535.png" />][2]

But what happens to the query results? How long are they kept? Why do they disappear sometimes? Why are some Impala queries are still “in flight” even if they are completed?   Each query is using some resources in Impala or HiveServer2. When the users submit a lot of queries, they are going to add up and crash the servers if nothing is done. Here are the latest settings that you can tweak:

# Impala

Hue tries to close the query when the user navigates away from the result page (as queries are generally fast, it is ok to close them quick). However, if the user never comes back checking the result of the query or never close the page, the query is going to stay. Impala is going to automatically expire the queries idle for than 10 minutes with the [query_timeout_s][3] property.

<pre></pre>

<pre><code class="bash">[impala]

\# If &amp;gt; 0, the query will be timed out (i.e. cancelled) if Impala does not do any work

\# (compute or send back results) for that query within QUERY_TIMEOUT_S seconds.

query_timeout_s=600

\# If &amp;gt; 0, the session will be timed out (i.e. cancelled) if Impala does not do any work

\# (compute or send back results) for that session within QUERY_TIMEOUT_S seconds (default 1 hour).

session_timeout_s=3600 </code></pre>

Until this version, the only alternative workaround to close all the queries, is to restart Hue (or Impala).

**<span style="color: #ff0000;">Note</span>**: Impala currently only cancels the query but does not close it. It will be improved in a future version with [IMPALA-1575][4]. In the meantime specify a -idle_session_timeout=20 in the Impala flags ("Command Line Argument Advanced Configuration Snippet (Safety Valve)"). This setting is also available in the Hue configuration.

# Hive

Hue never closes the Hive queries by default (as some queries can take hours of processing time). Also if your query volume is low (e.g. < a few hundreds a day) and you restart HiveServer2 every week, you are probably not affected. To get the same behavior as Impala (and close the query when the user leaves the page), switch on in the hue.ini:

<pre><code class="bash">[beeswax]

\# Hue will try to close the Hive query when the user leaves the editor page.

\# This will free all the query resources in HiveServer2, but also make its results inaccessible.

close_queries=true

</code></pre>

Starting in CDH5 and CDH4.6 (with HiveServer2), some close_query and close_session commands were added to Hue.

<pre><code class="bash">build/env/bin/hue close_queries -help

Usage: build/env/bin/hue close_queries [options] &amp;amp;lt;age_in_days&amp;amp;gt; (default is 7)

</code></pre>

Closes the non running queries older than 7 days. If <all> is specified, close the ones of any types.   To run them while using Cloudera Manager, be sure to export these two environment variables:

<pre><code class="bash">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'\`"

./build/env/bin/hue close_queries 0

Closing (all=False) HiveServer2 queries older than 0 days...

1 queries closed.

./build/env/bin/hue close_sessions 0 hive

Closing (all=False) HiveServer2 sessions older than 0 days...

1 sessions closed.

</code></pre>

You can then add this commands into a crontab and expire the queries older than N days.

**Note**

When using Kerberos you also need:

<pre><code class="bash">export HIVE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'\`/hive-conf"</code></pre>

A cleaner solution comes with [HIVE-5799][5] (available in Hive 0.14 or C5.2). Like Impala, HiveServer2 can now automatically expires queries. So tweak hive-site.xml with:

<pre><code class="xml"><property>

<name>hive.server2.session.check.interval</name>

<value>3000</value>

<description>The check interval for session/operation timeout, which can be disabled by setting to zero or negative value.</description>

</property>

<property>

<name>hive.server2.idle.session.timeout</name>

<value>3000</value>

<description>Session will be closed when it's not accessed for this duration, which can be disabled by setting to zero or negative value.</description>

</property>

<property>

<name>hive.server2.idle.operation.timeout</name>

<value>0</value>

<description>Operation will be closed when it's not accessed for this duration of time, which can be disabled by setting to zero value. With positive value, it's checked for operations in terminal state only (FINISHED, CANCELED, CLOSED, ERROR). With negative value, it's checked for all of the operations regardless of state.</description>

</property>

</code></pre>

**Note**

This is the recommended solution for Hive. User wishing to keep some result for longer can issue a CREATE TABLE AS SELECT … or export the results in Hue.

# Sum-up

The query servers are becoming much more stable with these changes as their resources do not need to grow infinitely. One tradeoff though is that the user will lose his query results after a certain time. To make the experience better, several ideas are being explored, like automatically downloading N rows of the resultset and keeping them for longer.

As usual feel free to comment and send feedback on the [hue-user][6] list or [@gethue][7]!

 [1]: https://gethue.com/sql-editor/
 [2]: https://cdn.gethue.com/uploads/2014/03/sql-editor.png
 [3]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L818
 [4]: https://issues.cloudera.org/browse/IMPALA-1575
 [5]: https://issues.apache.org/jira/browse/HIVE-5799
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue
