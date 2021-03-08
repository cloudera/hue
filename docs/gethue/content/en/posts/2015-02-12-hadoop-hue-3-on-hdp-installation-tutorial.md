---
title: Hue 3 on HDP installation tutorial
author: admin
type: post
date: 2015-02-12T18:14:15+00:00
url: /hadoop-hue-3-on-hdp-installation-tutorial/
sf_detail_type:
  - none
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
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
ampforwp-amp-on-off:
  - default
categories:

---
<p class="yt watch-title-container">
  Note: this guide works with any <a href="https://gethue.com/hue-4-and-its-new-interface-is-out/">Hue 4</a> version and HDP 2.x. There is a <a href="https://gethue.com/configure-ambari-hdp-with-hue/">recent guide</a> on <span style="color: #ff0000;">HDP3</span>.
</p>

Note: for <span style="color: #ff0000;">Hive</span> issues, just scroll down below

## <span id="eow-title" class="watch-title " dir="ltr" title="Installing Hue 3.9 on HDP 2.3 - Amazon EC2 RHEL 7">Installing Hue 3.9 on HDP 2.3 - Amazon EC2 RHEL 7</span> {.yt.watch-title-container}

{{< youtube UZoKXSsz5cw >}}

## Install in HDP 2.2

**Initial draft rom Andrew Mo (<mo@andrewmo.com>)**

**Insight Data Science - Data Engineering Fellow**

Last month I started a guest post on <gethue.com> demonstrating the [steps required][1] to use [HUE 3.7+][2] with the Hortonworks Data Platform (HDP); I’ve used HUE successfully with HDP 2.1 and 2.2, and have created a step-by-step guide on using HUE 3.7.1 with HDP 2.2 below.

I’m participating the Insight Data Science Data Engineering Fellows program and built a real-time data engineering pipeline proof of concept using Apache Kafka, Storm, and Hadoop using a “Lambda Architecture.” Cloudera CDH and Cloudera Manager are great tools, but I wanted to use Apache Ambari to deploy and manage Kafka and Storm with Hadoop; for these reasons, HDP 2.2 was selected for the project (note from @gethue: in CDH, Kafka is available and Spark Streaming is preferred to Storm, and CM installs/configures all Hue automatically).

HUE is one of Hadoop’s most important projects, as it significantly increases a user’s ease of access to the power of the Hadoop platform. While Hive and YARN provide a processing backbone for data analysts familiar with SQL to use Hadoop, HUE provides my interface of choice for data analysts to quickly get connected with big data and Hadoop’s powerful tools.

With HDP, HUE’s features and ease of use are something I always miss, so I decided to add HUE 3.7.1 to my HDP clusters.

Features confirmed to work in partial or complete fashion:

• Hive/Beeswax

• File Browser

• HDFS FACL Manager

• HBase Cluster Browser

• Job Browser

_Still working on debugging/integrating Pig/Oozie!_

Spark is on my to do list as well.

Technical Details:

• Distribution: Hortonworks Data Platform (HDP) 2.2

• Cluster Manager: Apache Ambari 1.7

• Environment: Amazon EC2

• Operating System: Ubuntu 12.04 LTS (RHEL6/CentOS6 works fine as well)

HUE will be deployed as a “Gateway” access node to our Hadoop cluster; this means that none of the core Hadoop services or clients are required on the HUE host.

&nbsp;

<span style="color: #ff0000;">Note about Hive and HDP 2.5+: <span style="color: #000000;">Since at least HDP 2.5, the default Hive shipped won't work with Hue unless you change the property:</span></span>

<pre><code class="bash">hive.server2.parallel.ops.in.session=true</code></pre>

Note about <span style="color: #ff0000;">Tez</span>:

<pre><code class="bash">[beeswax]

\# Hue will use at most this many HiveServer2 sessions per user at a time.

\# For Tez, increase the number to more if you need more than one query at the time, e.g. 2 or 3 (Tez as a maximum of 1 query by session).

max_number_of_sessions=1</code></pre>

&nbsp;

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-archi-1024x771.jpg" />][3]

## Installing HUE

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-2-1024x672.png"  />][4]

For this walk-through, we’ll assume that you’ve already deployed a working cluster using Apache Ambari 1.7.

&nbsp;

Let’s go on the HUE Host (Gateway node) and get started by preparing our environment and downloading the Hue 3.8 release tarball.

RHEL/CentOS uses ‘yum’ for package management.

Ubuntu uses ‘apt-get’ for package management. In our example, we’re using Ubuntu.

Prepare dependencies:

<pre><code class="bash">sudo apt-get install -y ant

sudo apt-get install -y gcc g++

sudo apt-get install -y libkrb5-dev libmysqlclient-dev

sudo apt-get install -y libssl-dev libsasl2-dev libsasl2-modules-gssapi-mit

sudo apt-get install -y libsqlite3-dev

sudo apt-get install -y libtidy-0.99-0 libxml2-dev libxslt-dev

sudo apt-get install -y maven

sudo apt-get install -y libldap2-dev

sudo apt-get install -y python-dev python-simplejson python-setuptools

</code></pre>

Download Hue 3.8.1 release tarball (in case, older version [3.7.1 link][5]):

• wget <https://cdn.gethue.com/downloads/releases/3.8.1/hue-3.8.1.tgz>

Make sure you have Java installed and configured correctly!

I’m using Open JDK 1.7 in this example:

<pre><code class="bash">sudo apt-get install -y openjdk-7-jre openjdk-7-jdk

sudo echo “JAVA_HOME=\”/usr/lib/jvm/java-7-openjdk-amd64/jre\”" &gt;&gt; /etc/environment

</code></pre>

Unpackage the HUE 3.7.1 release tarball and change to the directory.

Install HUE:

<pre><code class="bash">sudo make install</code></pre>

By default, HUE installs to ‘/usr/local/hue’ in your Gateway node’s local filesystem.

As installed, the HUE installation folders and file ownership will be set to the ‘root’ user.

Let’s fix that so HUE can run correctly without root user permissions:

<pre><code class="bash">sudo chown -R ubuntu:ubuntu /usr/local/hue</code></pre>

## Configuring Hadoop and HUE

HUE uses a configuration file to understand information about your Hadoop cluster and where to connect to. We’ll need to configure our Hadoop cluster to accept connections from HUE, and add our cluster information to the HUE configuration file.

### Hadoop Configuration

Ambari provides a convenient single point of management for a Hadoop cluster and related services. We’ll need to reconfigure our HDFS, Hive (WebHcatalog), and Oozie services to take advantage of HUE’s features.

### HDFS

We need to do three things, (1) ensure WebHDFS is enabled, (2) add ‘proxy’ user hosts and groups for HUE, and (3) enable HDFS file access control lists (FACLs) (optional).

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-3-1024x672.png"  />][6] [<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-4-1024x672.png"  />][7]

<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-6-1024x672.png"  />[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-28-1024x672.png"  />][8]

## Hive (WebHcat) and Oozie

We’ll also need to set up proxy user hosts and groups for HUE in our Hive and Oozie service configurations.

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-12-1024x672.png"  />][9] [<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-10-1024x672.png"  />][10]

Once these cluster configuration updates have been set, save, and restart these services on the respective cluster nodes.

Confirm WebHDFS is running:

## [<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-8-1024x693.png"  />][11]

### HUE Configuration

The HUE configuration file can be found at ‘/usr/local/hue/desktop/conf/hue.ini’

Be sure to make a backup before editing!

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-1-1024x827.png"  />][12]

We’ll need to populate ‘hue.ini’ with our cluster’s configuration information.

Examples are included below, but will vary with your cluster’s configuration.

In this example, the cluster is small, so our cluster NodeNode also happens to be the Hive Server, Hive Metastore, HBase Master, one of three Zookeepers, etc.

WebHDFS needs to point to our cluster NameNode:

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-7-1024x827.png"  />][13]

Configure the correct values for our YARN cluster Resource Manager, Hive, Oozie, etc:

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-13-1024x827.png"  />][14] [<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-14-1024x827.png"  />][15]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-15-1024x827.png"  />][16][<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-38-1024x827.png"  />][17][<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-30-1024x827.png"  />][18]

To disable HUE ‘apps’ that aren’t necessary, or are unsupported, for our cluster, use the Desktop ‘app_blacklist’ property. Here I’m disabling the Impala and Sentry/Security tabs (note: the HDFS FACLs tab is disabled if the ‘Security’ app is disabled).

## Start HUE on HDP

• We start the HUE server using the ‘supervisor’ command.

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-19-1024x827.png"  />][19]

• Use the ‘-d’ switch to start the HUE supervisor in daemon mode

Connect to your new HUE server at its IP address/FQDN and the default port of ‘8888’

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-18-1024x629.png"  />][20]

## It works!

Congratulations, you’re running HUE 3.7.1 with HDP 2.2!

&nbsp;

Let’s take a look around at HUE’s great features:

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-21-1024x629.png"  />][21]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-25-1024x629.png"  />][22]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-24-1024x629.png"  />][23]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-29-1024x629.png"  />][24]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-31-1024x629.png"  />][25]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-39-1024x629.png"  />][26]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-40-1024x629.png"  />][27]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-48-1024x610.png"  />][28]

[<img src="https://cdn.gethue.com/uploads/2015/02/hue-hdp-49-1024x610.png"  />][29]

&nbsp;

Have any questions? Feel free to contact Andrew or the [hue-user][30] list / [@gethue][31]!

 [1]: https://gethue.com/how-to-deploy-hue-on-hdp/
 [2]: https://gethue.com/hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
 [3]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-archi.jpg
 [4]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-2.png
 [5]: https://cdn.gethue.com/downloads/releases/3.7.1/hue-3.7.1.tgz
 [6]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-3.png
 [7]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-4.png
 [8]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-28.png
 [9]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-12.png
 [10]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-10.png
 [11]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-8.png
 [12]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-1.png
 [13]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-7.png
 [14]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-13.png
 [15]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-14.png
 [16]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-15.png
 [17]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-38.png
 [18]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-30.png
 [19]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-19.png
 [20]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-18.png
 [21]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-21.png
 [22]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-25.png
 [23]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-24.png
 [24]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-29.png
 [25]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-31.png
 [26]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-39.png
 [27]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-40.png
 [28]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-48.png
 [29]: https://cdn.gethue.com/uploads/2015/02/hue-hdp-49.png
 [30]: http://groups.google.com/a/cloudera.org/group/hue-user
 [31]: https://twitter.com/gethue
