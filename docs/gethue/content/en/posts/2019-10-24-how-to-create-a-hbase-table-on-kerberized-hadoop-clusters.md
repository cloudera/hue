---
title: How to create a HBase table on Kerberized Hadoop clusters
author: Hue Team
type: post
date: 2019-10-24T06:18:25+00:00
url: /how-to-create-a-hbase-table-on-kerberized-hadoop-clusters/
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
sf_author_info:
  - 1
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
ampforwp-amp-on-off:
  - default
categories:
  # - Version 4.3
  # - Version 4.4
  - Version 4
  # - Version 4.5

---
Hi SQL Data Explorers,

If you are using HBase with Hue on CDH6.1.x or later, you may find Hue&#8217;s check configuration fails for HBase with following error:

<pre><code class="bash">Failed to authenticate to HBase Thrift Server, check authentication configurations.
</code></pre>

<a href="https://cdn.gethue.com/uploads/2019/10/Screen-Shot-2019-10-23-at-2.24.44-PM.png"><img src="https://cdn.gethue.com/uploads/2019/10/Screen-Shot-2019-10-23-at-2.24.44-PM.png" /></a>

With change from HBase([HBASE-19852][2]), we have to configure HBase properly through Cloudera Manager with following steps to enable Hue-Hbase communication.

### Step 1
Navigate to CM->Clusters->HBASE-1->Configurations, search for &#8220;thrift&#8221; and verify the &#8220;Enable HBase Thrift Http Server&#8221; and &#8220;Enable HBase Thrift Proxy Users&#8221; are checked, and &#8220;Enable HBase Thrift Server Compact Protocol&#8221; and &#8220;Enable HBase Thrift Server Framed Transport&#8221; are unchecked.

<a href="https://cdn.gethue.com/uploads/2019/10/Hbase-Configuration1.png"><img src="https://cdn.gethue.com/uploads/2019/10/Hbase-Configuration1.png" /></a>

### Step 2
On same page as step1, search for &#8220;proxy&#8221;, depends on your CM version, you can skip step 2b if you see following:

<a href="https://cdn.gethue.com/uploads/2019/10/HbaseProxyUserConfigs.png"><img src="https://cdn.gethue.com/uploads/2019/10/HbaseProxyUserConfigs.png" /></a>

otherwise, follow step 2b

### Step 2b
on same page, search for &#8220;core-site&#8221; and fill in as following to &#8220;HBase Service Advanced Configuration Snippet (Safety Valve) for core-site.xml&#8221;

<pre><code class="bash">hadoop.proxyuser.hbase.hosts: *
hadoop.proxyuser.hbase.groups: *
</code></pre>

### Step 3
If your cluster is kerberized cluster, find out your HBase thrift server and its HTTP kerberos principal and then config following parameters:

HBase Service Advanced Configuration Snippet (Safety Valve) for hbase-site.xml:

<pre><code class="bash">hbase.thrift.spnego.principal: HTTP/${YOUR_HBASE_THRIFT_SERVER_NAME}/${REALM}
hbase.thrift.spnego.keytab.file: hbase.keytab </code></pre>

### Step 3a
Find out HBase thrift server host: navigate to CM->Clusters->HBASE-1&#8211;>Instances and search for &#8220;thrift&#8221;

<a href="https://cdn.gethue.com/uploads/2019/10/FindOutYourHbaseThriftServerHost.png"><img src="https://cdn.gethue.com/uploads/2019/10/FindOutYourHbaseThriftServerHost.png" /></a>

### Step 3b
Find out Kerberos Principal for HTTP on HBase thrift host: navigate to CM->Adminsitration->Security->Kerberos Credentials and filter by &#8216;HTTP&#8217;

<a href="https://cdn.gethue.com/uploads/2019/10/Screen-Shot-2019-10-23-at-1.54.37-PM.png"><img src="https://cdn.gethue.com/uploads/2019/10/Screen-Shot-2019-10-23-at-1.54.37-PM.png" /></a>

### Step 3c
Configure Thrift server with the value you found at step 3a and 3b

<a href="https://cdn.gethue.com/uploads/2019/10/ConfigureThriftServerSpnegoPrincipal.png"><img src="https://cdn.gethue.com/uploads/2019/10/ConfigureThriftServerSpnegoPrincipal.png" /></a>

Save Changes and deploy the staled configurations then restart HBase.

Now, navigate to Hue UI, https://${huehost}:8889/hue/about/#step1, the &#8216;Check Configurations&#8217; for HBase should pass.

<a href="https://cdn.gethue.com/uploads/2019/10/Hbase-Check-configuration.png"><img src="https://cdn.gethue.com/uploads/2019/10/Hbase-Check-configuration.png" /></a>

Now let&#8217;s navigate to &#8220;Examples&#8221; tab to try installing the HBase examples, it may fail with error:

<pre><code class="bash">IOError(_message='org.apache.hadoop.hbase.security.AccessDeniedException: org.apache.hadoop.hbase.security.AccessDeniedException: Insufficient permissions ..."</code></pre>

All you need to do is ssh to your hosts run following hbase shell command to grant the user:&#8217;testadmin&#8217; with proper permission.

<pre><code class="bash">sudo -u hbase hbase shell

grant 'testadmin','RWC'
</code></pre>

Yeah, now you are all set to create your HBase table on secure cluster.

<a href="https://cdn.gethue.com/uploads/2019/10/NewlyCreatedHbaseTables.png"><img src="https://cdn.gethue.com/uploads/2019/10/NewlyCreatedHbaseTables.png" /></a>


&nbsp;

Hope this helps. Any feedback or question? Feel free to comment here or on the [Forum][10] or [@gethue][11] and [quick start][12] SQL querying!

&nbsp;

Weixia, from the Hue Team

 [1]: https://cdn.gethue.com/uploads/2019/10/Screen-Shot-2019-10-23-at-2.24.44-PM.png
 [2]: https://issues.apache.org/jira/browse/HBASE-19852
 [3]: https://cdn.gethue.com/uploads/2019/10/Hbase-Configuration1.png
 [4]: https://cdn.gethue.com/uploads/2019/10/HbaseProxyUserConfigs.png
 [5]: https://cdn.gethue.com/uploads/2019/10/FindOutYourHbaseThriftServerHost.png
 [6]: https://cdn.gethue.com/uploads/2019/10/Screen-Shot-2019-10-23-at-1.54.37-PM.png
 [7]: https://cdn.gethue.com/uploads/2019/10/ConfigureThriftServerSpnegoPrincipal.png
 [8]: https://cdn.gethue.com/uploads/2019/10/Hbase-Check-configuration.png
 [9]: https://cdn.gethue.com/uploads/2019/10/NewlyCreatedHbaseTables.png
 [10]: https://discourse.gethue.com/
 [11]: https://twitter.com/gethue
 [12]: https://docs.gethue.com/quickstart/
