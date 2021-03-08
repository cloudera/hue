---
title: 'Impala HA: how to distribute Impala query load'
author: admin
type: post
date: 2014-05-19T18:31:13+00:00
url: /hadoop-tutorial-how-to-distribute-impala-query-load/
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

Hue provides an [interface][1] for [Impala][2], the next generation SQL engine for Hadoop. In order to offer even more performances, Hue can distribute the query load across all of the Impala workers.

# Tutorial

This tutorial demonstrates how to setup Hue to query multiple Impalads (Impala daemons):

1. Configuring Hue 3.6 on one node in a 4 node RedHat 6 cluster to work with multiple Impalads.
2. Load balance the connections to impalad using [HAProxy 1.4][3], but any load balancer that persists connections should work.

Here is a quick video demonstrating how to communicate with multiple Impalads in Hue!

{{< youtube p-pwhqGvlE4 >}}

## Configuring Hue

There are two ways to configure Hue to communicate with multiple Impalads.

### Configuration via Cloudera Manager

1. From Cloudera Manager, click on “Clusters” in the menu and find your Hue service.


    [<img class="alignnone  wp-image-1228" src="https://cdn.gethue.com/uploads/2014/05/impala-1.png"  />][4]

2. From the Hue service, go to “Configuration -> View and Edit”


    [<img class="alignnone  wp-image-1227" src="https://cdn.gethue.com/uploads/2014/05/impala-2.png"  />][5]

3. We must provide a safety valve configuration in Cloudera Manager to use the appropriate load balancer and socket timeout. Go to “Service-Wide -> Advanced” and click on the value for “Hue Service Advanced Configuration Snippet (Safety Valve)”. You can use the following as a template for the value:


    [impala]
    server_host=<hostname running HAProxy>
    server_port=<port HAProxy is bound to>
    server_conn_timeout=<timeout in seconds>

&nbsp;

For more information on configuring Hue via Cloudera Manager, see [Managing Clusters][6].

### Manual configuration

1. Open /etc/hue/hue.ini with your favorite text editor.
2. Change the config “server_conn_timeout” under the “impala” section to a large value (e.g. 1 hour). This value should be in seconds (e.g. 1 hour = 3600 seconds). See item #4 in “Configuration via Cloudera Manager” for information on configuration option.


    [<img class="alignnone  wp-image-1229" src="https://cdn.gethue.com/uploads/2014/05/impala-3.png"  />][7]

3. Next, we must set the new host and port in the “impala” section in the hue.ini. The hostname is defined in “server_host” and the port is defined in “server_port”. See item #5 in “Configuration via Cloudera Manager” for an example configuration.

&nbsp;

## HA Proxy Installation/Configuration

1. Download and unzip the [binary distribution][8] of [HA Proxy 1.4][3] on the node that doesn’t have Hue installed.
2. Add the following [HA Proxy configuration][9] to /etc/impala/haproxy-impala.conf:

<pre><code class="bash">global

daemon

nbproc 1

maxconn 100000

log /dev/log local6

defaults

log global

mode tcp

option tcplog

option tcpka

timeout connect 3600000ms

timeout client 3600000ms

timeout server 3600000ms

listen impala

bind 0.0.0.0:10001

balance leastconn

server impala1 server1.cloudera.com:21050 check

server impala2 server2.cloudera.com:21050 check

server impala3 server3.cloudera.com:21050 check

</code></pre>

1. Start HA Proxy:

<pre><code class="bash">haproxy -f /etc/impala/haproxy-impala.conf</code></pre>

&nbsp;

The key configuration options are [**balance**][10] and [**server**][11] in the [**listen**][12] section. As well as the [**timeout**][13] configuration options in the [**defaults**][14] section. When the **balance** parameter is set to **leastconn**, Hue is guaranteed to create new connections with the impalad with the least number of connections. The **server** parameters define which servers will be used for load balancing and takes on the form:

&nbsp;

<pre><code class="bash">server <name> <address>[:port] [settings ...]</code></pre>

&nbsp;

In the configuration above, the server “impala1” is available at “impala1.cloudera.com:21050”, “impala2” is available at “impala2.cloudera.com:21050”, and “impala3” is available at “impala3.cloudera.com:21050”. The **timeout** configuration parameters define how long a TCP connection (on both sides) should live. In this example, the client timeout, server timeout, and connect timeout are all set at 1 hour.

&nbsp;

HA Proxy is configured to bind to “0.0.0.0:10001”. Thus, Hue should now be able to point to HA Proxy, which will transparently pick one of the least utilized Impalads.

&nbsp;

&nbsp;

# Conclusion

Load balancing Impalas’ queries will distribute the load to all the Impalads (where the final result aggregation happens for example). Impala currently requires non-volatile network connectivity by design so Hue can persist connections. We hope this helps you make the most of your Hadoop cluster!

&nbsp;

Have any suggestions? Feel free to tell us what you think through [hue-user][15] or [@gethue][16].

[1]: https://gethue.com/hadoop-tutorial-new-impala-and-hive-editors/
[2]: http://impala.io/
[3]: http://haproxy.1wt.eu/
[4]: https://cdn.gethue.com/uploads/2014/05/impala-1.png
[5]: https://cdn.gethue.com/uploads/2014/05/impala-2.png
[6]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Managing-Clusters/cm5mc_hue_service.html
[7]: https://cdn.gethue.com/uploads/2014/05/impala-3.png
[8]: http://haproxy.1wt.eu/download/1.4/src/haproxy-1.4.24.tar.gz
[9]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html
[10]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-balance
[11]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-server
[12]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4
[13]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-timeout
[14]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#3
[15]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
[16]: https://twitter.com/gethue
