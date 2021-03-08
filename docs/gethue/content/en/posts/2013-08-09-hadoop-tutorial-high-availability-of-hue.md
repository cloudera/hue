---
title: High Availability of Hue
author: admin
type: post
date: 2013-08-09T20:23:00+00:00
url: /hadoop-tutorial-high-availability-of-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/57817118455/hadoop-tutorial-high-availability-of-hue
tumblr_gethue_id:
  - 57817118455
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
##

# <span style="color: #ff0000;">Note:</span> as of January 2015 in Hue master or CDH5.4, this post is deprecated by [Automatic High Availability with Hue and Cloudera Manager][1].

&nbsp;

&nbsp;

<p id="docs-internal-guid-1f271c26-6489-5d99-0b37-adf2a481556e">
  Very few projects within the Hadoop umbrella have as much end user visibility as <a href="http://www.gethue.com">Hue</a>. Thus, it is useful to add a degree of fault tolerance to deployments. This blog post describes how to achieve a <a href="http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-High-Availability-Guide/CDH4-High-Availability-Guide.html">higher level of availability</a> (HA) by placing several Hue instances behind a load balancer.
</p>

# Tutorial

This tutorial demonstrates how to setup high availability by:

  1. Installing Hue 2.3 on two nodes in a three-node RedHat 5 cluster.
  2. Managing all Hue instances via [Cloudera Manager 4.7][2].
  3. Load balancing using [HA Proxy 1.4][3]. In reality, any load balancer with sticky sessions should work.

Here is a video summary of the new features:

## Installing Hue

Hue should be installed on two of the three nodes. To have Cloudera Manager automatically install Hue, follow the “Parcel Install via Cloudera Manager” section. To install manually, follow the “Package Install” section.

### Parcel Install via Cloudera Manager

For more information on Parcels, see [Managing Parcels][4].

  1. From Cloudera Manager, click on “Hosts” in the menu. Then, go to the “Parcels” section.
  2. Find the latest CDH parcel, click “Download”.
  3. Once the parcel has finished downloading, click “Distribute”.
  4. Once the parcel has finished distributing, click “Activate”.

### Package Install

  1. Download the yum repository [RPM][5].
  2. Install the yum repository using “sudo yum —nogpgcheck localinstall cloudera-cdh-4-0.x86_64.rpm”. For more information, see [Installing CDH4][6].
  3. Install Hue on each node using the command “sudo yum install hue” via the command line interface. For more information on installing Hue, see [CDH documentation][7].

## Managing Hue through Cloudera Manager

Cloudera Manager provides management of the Hue servers on each node. Add two Hue services using the directions below. For more information on managing services, see the [Cloudera Manager documentation][8].

  1. Go to “Services -> All Services” in the menu.
  2. Click “Actions -> Add a Service”.
  3. Select “Hue” and follow the steps on the screen. NOTE: For each Hue service we choose a unique host.
  4. Ensure that the “Jobsub Examples and Templates Directory” configuration points to different directories in HDFS for each Hue service. It can be changed by going to Services -> <hue service>. In the menu, go to Configuration -> View and Edit. Then, click on “Hue Server”. “Jobsub Examples and Templates Directory” should be at the bottom of the page.

<img src="https://lh4.googleusercontent.com/ay9RnIloyJJl35yKC2j5OUEcrZLqnBqpQsFSNwH8NVXCReSYHDqfo1GT47zGRtStpUEVCQxblg81eDDqPpFihFSF3oo-qNPlfwctdfo2rUczACFZn-dB_Jdg" alt="image" width="637px;" height="355px;" />

Image 1: Cloudera Manager handling two Hue services.

## HA Proxy Installation/Configuration

  1. Download and unzip the [binary distribution][9] of [HA Proxy 1.4][3] on the node that doesn’t have Hue installed.
  2. Add the following [HA Proxy configuration][10] to /tmp/hahue.conf:

<pre class="code">global
    daemon
    nbproc 1
    maxconn 100000
    log 127.0.0.1 local6 debug

defaults
    option http-server-close
    mode http
    timeout http-request 5s
    timeout connect 5s
    timeout server 10s
    timeout client 10s

listen Hue 0.0.0.0:80
    log global
    mode http
    stats enable
    balance source
    server hue1 servera.cloudera.com:8888 cookie ServerA check inter 2000 fall 3
    server hue2 serverb.cloudera.com:8888 cookie ServerB check inter 2000 fall 3</pre>

  1. Start HA Proxy:

<pre class="code">haproxy -f /tmp/hahue.conf</pre>

<p id="docs-internal-guid-4a17af8b-64c3-f48b-5c2b-591bad8b0e01">
  The key configuration options are <a href="http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-balance">balance</a> and <a href="http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-server">server</a> in the <a href="http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4">listen</a> section. When the balance parameter is set to source, a client is guaranteed to communicate with the same server every time it makes a request. If the server the client is communicating with goes down, the request will automatically be sent to another active server. This is necessary because Hue stores session information in process memory. The server parameters define which servers will be used for load balancing and takes on the form:
</p>

<pre class="code">server  [:port] [settings ...]</pre>

In the configuration above, the server “hue1” is available at “servera.cloudera.com:8888” and “hue2” is available at “serverb.cloudera.com:8888”. Both servers have health checks every two seconds and are declared down after three failed health checks. In this example, HAProxy is configured to bind to “0.0.0.0:80”. Thus, Hue should now be available at “http://serverc.cloudera.com”.

&nbsp;

# Conclusion

<p id="docs-internal-guid-4a17af8b-64c4-3d2c-f686-326bc47cee5a">
  Hue can be load balanced easily as long as the server a client is directed to is constant (i.e.: sticky sessions). It can improve performance, but the primary goal is high availability. Also, multiple Hue instances can be easily managed through Cloudera Manager. For true High Availability, Hue needs to be configured to use HA <a href="http://dev.mysql.com/doc/refman/5.0/en/ha-overview.html">MySQL</a>, <a href="http://www.postgresql.org/docs/8.3/static/high-availability.html">PostGreSQL</a>, or <a href="http://docs.oracle.com/cd/E25054_01/server.1111/e17157/architectures.htm#i1007752">Oracle</a>.
</p>

Coming up, there will be a blog post on JobTracker HA with Hue. Have any suggestions? Feel free to tell us what you think through[hue-user][11].

 [1]: https://gethue.com/automatic-high-availability-with-hue-and-cloudera-manager/ "Automatic High Availability with Hue and Cloudera Manager"
 [2]: http://www.cloudera.com/content/cloudera/en/products/cloudera-manager.html
 [3]: http://haproxy.1wt.eu/
 [4]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM4Ent/4.5.1/Cloudera-Manager-Enterprise-Edition-User-Guide/cmeeug_topic_7_11.html
 [5]: http://archive.cloudera.com/cdh4/one-click-install/redhat/5/x86_64/cloudera-cdh-4-0.x86_64.rpm
 [6]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_4_4.html?scroll=topic_4_4_1_unique_1__p_32_unique_1
 [7]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_15.html
 [8]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM4Free/4.5.1/Cloudera-Manager-Free-Edition-User-Guide/cmfeug_topic_5_1.html
 [9]: http://haproxy.1wt.eu/download/1.4/src/haproxy-1.4.24.tar.gz
 [10]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html
 [11]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
