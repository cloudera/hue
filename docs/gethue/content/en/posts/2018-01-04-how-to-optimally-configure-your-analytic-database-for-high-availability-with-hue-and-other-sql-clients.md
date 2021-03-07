---
title: How to optimally configure your Analytic Database for High Availability with Hue and other SQL clients
author: admin
type: post
date: 2018-01-04T00:14:42+00:00
url: /how-to-optimally-configure-your-analytic-database-for-high-availability-with-hue-and-other-sql-clients/
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4

---
Hi Big Data Explorers,

<span style="font-weight: 400;">HiveServer2 and Impala support High Availability through a "load balancer". One caveat is that Hue's underlying Thrift libraries reuse TCP connections in a pool, a single user session may not have the same Impala or Hive TCP connection. If a TCP connection is balanced away from the previously selected  HiveServer2 or Impalad instance, the user session and its queries can be lost and trigger the "Results have expired" or "Invalid session Id" errors.</span>

<span style="font-weight: 400;">To prevent sessions from being lost, we need configure the load balancer with "source" algorithm to ensure each Hue instance sends all traffic to a single HiveServer2/Impalad instance. Yes, this is not true load balancing, but a configuration for failover High Availability. HiveSever2 or Impala coordinators already distribute the work across the cluster so this is not an issue.</span>

<span style="font-weight: 400;">To enable an optimal load distribution that works for everybody, we can create multiple profiles in our load balancer, per port for Hue clients and non-Hue clients like Hive or Impala. We can configure non-Hue clients to distribute loads with "roundrobin" or "leastconn" and configure Hue clients with "source" (source IP Persistence) on dedicated ports, for example, 10015 for Hive beeline commands, 10016 for Hue, 21051 for Hue-Impala interactions while 25003 for Impala shell.</span>

<img src="https://cdn.gethue.com/uploads/2018/01/HaproxyDiagram_5.png"/>

<span style="font-weight: 400;">As shown in above diagram, you can configure the HaProxy to have two different ports associated with different load balancing algorithms. Here is a sample configuration (haproxy.cfg) for Hive and Impala HA on a secure cluster.</span>

    #-----------------------
    # main frontend which proxys to the backends
    #-----------------------
    frontend hiveserver2_front
    bind *:10015 ssl crt /path/to/cert_key.pem
    mode tcp
    option tcplog
    default_backend hiveserver2
    #-----------------------
    # round robin balancing between the various backends
    #-----------------------
    # This is the setup for HS2. beeline client connect to load_balancer_host:load_balancer_port.
    # HAProxy will balance connections among the list of servers listed below.
    backend hiveserver2
    balance roundrobin
    mode tcp
    server hiveserver2_1 host-2.com:10000 ssl ca-file /path/to/truststore.pem check
    server hiveserver2_2 host-3.com:10000 ssl ca-file /path/to/truststore.pem check
    server hiveserver2_3 host-1.com:10000 ssl ca-file /path/to/truststore.pem check

    # Setup for Hue or other JDBC-enabled applications.
    # In particular, Hue requires sticky sessions.
    # The application connects to load_balancer_host:10016, and HAProxy balances
    # connections to the associated hosts, where Hive listens for JDBC requests on port 10015.
    #-----------------------
    # main frontend which proxys to the backends
    #-----------------------
    frontend hivejdbc_front
    bind *:10016 ssl crt /path/to/cert_key.pem
    mode tcp
    option tcplog
    stick match src
    stick-table type ip size 200k expire 30m
    default_backend hivejdbc

    #-----------------------
    # source balancing between the various backends
    #-----------------------
    # HAProxy will balance connections among the list of servers listed below.
    backend hivejdbc
    balance source
    mode tcp
    server hiveserver2_1 host-2.com:10000 ssl ca-file /path/to/truststore.pem check
    server hiveserver2_2 host-3.com:10000 ssl ca-file /path/to/truststore.pem check
    server hiveserver2_3 host-1.com:10000 ssl ca-file /path/to/truststore.pem check

  <p>
    <span style="font-weight: 400;">And here is an example for impala HA configuration on a secure cluster.</span>
  </p>


    # The list of Impalad is listening at port 21000 for beeswax (impala-shell) or original ODBC driver.
    # For JDBC or ODBC version 2.x driver, use port 21050 instead of 21000.
    #-----------------------
    # main frontend which proxys to the backends
    #-----------------------
    frontend impala_front
    bind *:25003 ssl crt /path/to/cert_key.pem
    mode tcp
    option tcplog
    default_backend impala
    #-----------------------
    # round robin balancing between the various backends
    #-----------------------
    backend impala
    balance leastconn
    mode tcp
    server impalad1 host-3.com:21000 ssl ca-file /path/to/truststore.pem check
    server impalad2 host-2.com:21000 ssl ca-file /path/to/truststore.pem check
    server impalad3 host-4.com:21000 ssl ca-file /path/to/truststore.pem check

    # Setup for Hue or other JDBC-enabled applications.
    # In particular, Hue requires sticky sessions.
    # The application connects to load_balancer_host:21051, and HAProxy balances
    # connections to the associated hosts, where Impala listens for JDBC requests on port 21050.
    #-----------------------
    # main frontend which proxys to the backends
    #-----------------------
    frontend impalajdbc_front
    bind *:21051 ssl crt /path/to/cert_key.pem
    mode tcp
    option tcplog
    stick match src
    stick-table type ip size 200k expire 30m
    default_backend impalajdbc
    #-----------------------
    # source balancing between the various backends
    #-----------------------
    # HAProxy will balance connections among the list of servers listed below.
    backend impalajdbc
    balance source
    mode tcp
    server impalad1 host-3.com:21050 ssl ca-file /path/to/truststore.pem check
    server impalad2 host-2.com:21050 ssl ca-file /path/to/truststore.pem check
    server impalad3 host-4.com:21050 ssl ca-file /path/to/truststore.pem check

<pre><span style="font-weight: 400;"><strong>Note</strong>: “check” is required at end of each line to ensure HaProxy can detect any unreachable Impalad/HiveServer2 server, so HA failover can be successful. Without TCP check, you may hit the “TSocket reads 0 byte” error when the Impalad/HiveServer2 server Hue tries to connect is down.</span></pre>

<p>
  <span style="font-weight: 400;">After editing the /etc/haproxy/haproxy.cfg file, run following commands to restart HaProxy service and check the service restarts successfully.</span>
</p>

    service haproxy restart
    service haproxy status

<p>
  <span style="font-weight: 400;">Also we need add following blocks into hue.ini or if you are using Cloudera Manager, adding following block inside </span><b>Hue Service Advanced Configuration Snippet (Safety Valve) for hue_safety_valve.ini</b>
</p>

    [impala]
    server_port=21051

    [beeswax]
    hive_server_port=10016

<p>
  <a href="https://cdn.gethue.com/uploads/2018/01/Screen-Shot-2018-01-03-at-2.01.58-PM.png"><img class="aligncenter wp-image-5155" src="https://cdn.gethue.com/uploads/2018/01/Screen-Shot-2018-01-03-at-2.01.58-PM.png"/></a>
</p>

<p>
  <span style="font-weight: 400;">Now you are all set for Hive/Impala High Availability setups! In the future, this configuration will be managed by Cloudera Manager so that your Analytic Database is HA out of the box.</span>
</p>
