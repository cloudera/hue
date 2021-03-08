---
title: Live Analytics of Live Apache log files
author: admin
type: post
date: 2018-08-16T22:18:52+00:00
url: /live-analytics-of-live-apache-log-files/
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
Quite some time ago (in 2014), a post demoed how to [manually ingest][1] some Apache Logs into Apache Solr and visualize via the [Dynamic Dashboards][2]. Nowadays, streaming data vs batching data is getting popular.

This follow-up is actually levering the [Flume / Solr blog][3] post from Cloudera which contains more context about the format and services.

&nbsp;

Hue already comes with an [Apache Log collection][1] that contain a schema with additional information like the city, country, browser user agent. As a Hue admin, clicking on your username in the top right corner, then 'Hue' Administration, 'Quick Start', 'Step 2: Examples', 'Solr Search' will install the default index and dashboard.

[<img class="aligncenter wp-image-5485" src="https://cdn.gethue.com/uploads/2018/08/demo_live_logs.png"/>][4] [<img class="aligncenter wp-image-5486" src="https://cdn.gethue.com/uploads/2018/08/flume_metrics.png"/>][5]

Next, it is time to add some live data.

## Listing Indexing

Here we are leveraging Apache Flume and installed one agent on the Apache Server host. If you have multiple machines to collect the logs from, we would need to add one agent on each host.

Then in Cloudera Manager, in the Flume service we enter this Flume configuration:

<pre><code class="bash">

tier1.sources = source1

tier1.channels = channel1

tier1.sinks = sink1

tier1.sources.source1.type = exec

tier1.sources.source1.command = tail -F /var/log/hue/access.log

tier1.sources.source1.channels = channel1

tier1.channels.channel1.type = memory

tier1.channels.channel1.capacity = 10000

tier1.channels.channel1.transactionCapacity = 1000

\# Solr Sink configuration

tier1.sinks.sink1.type = org.apache.flume.sink.solr.morphline.MorphlineSolrSink

tier1.sinks.sink1.morphlineFile = /tmp/morphline.conf

tier1.sinks.sink1.channel = channel1

</code></pre>

Note: for a more robust sourcing, using [TaildirSource][6] instead of the 'tail -F /var/log/hue/access.log'. Additionally, a [KafkaChannel][7] would make sure that we don't drop events in case of crashes of the command.

Note: when doing this, we need to make sure that the Flume Agent user runs as a user that can read the '/var/log/apache2/access.log' file.

Note: this is how to create the Kafka topic via the CLI (until the UI supports it):

<pre><code class="bash">kafka-topics -create -topic=hueAccessLogs -partitions=1 -replication-factor=1 -zookeeper=analytics-1.gce.cloudera.com:2181

</code></pre>

Note: as explained in previous Cloudera blog post, the '/tmp/morphline.conf will grok and parse the logs and convert it into a table. Depending on your Apache webserver, you might or might not have the first hostname field.

<pre><code class="bash">demo.gethue.com:80 92.58.20.110 - - [12/May/2018:14:07:39 +0000] "POST /jobbrowser/jobs/ HTTP/1.1" 200 392 "http://demo.gethue.com/hue/dashboard/new_search?engine=solr" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0"

</code></pre>

<pre><code class="bash">

columns: [C0,client_ip,C1,C2,time,dummy1,request,code,bytes,referer,user_agent]

</code></pre>

We also used the UTC timezone conversion as Solr expects dates in UTC.

<pre><code class="bash">[/code]

inputTimezone : UTC

The Geo database "/tmp/GeoLite2-City.mmdb" comes from [MaxMind][8].

After the refresh of the Flume configuration, the Metrics tab will show the business of the pipeline. Looking at the logs of Solr will bubble some potential indexing issues.

Note: if you want to delete all the documents in the log_analytics_demo collection to start fresh, you could delete and recreate it via Hue UI or issue this command:

<pre><code class="bash">curl "http://demo.gethue.com:8983/solr/log_analytics_demo/update?commit=true" -H "Content-Type: text/xml" -data-binary '<delete><query>\*:\*</query></delete>'</code></pre>

## Live Querying

With the log info flowing streamed directly into the index, the Dashboard becomes a powerful tool for live data analytics.

In particular, the Timeline widget is a pretty good way to see the flow of data. The Analytics Facets in Solr 7 are [now supported][9] and make it even more compelling by providing easy way to calculate by dimensions.

Feel free to play with the live dashboard on [demo.gethue.com][10], it was configured the same way!

&nbsp;

As usual feel free to send feedback to the [hue-user][11] list or [@gethue][12] or send [improvements][13]!

 [1]: https://gethue.com/analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr/
 [2]: https://gethue.com/search-dashboards/
 [3]: https://blog.cloudera.com/blog/2015/02/how-to-do-real-time-log-analytics-with-apache-kafka-cloudera-search-and-hue/
 [4]: https://cdn.gethue.com/uploads/2018/08/demo_live_logs.png
 [5]: https://cdn.gethue.com/uploads/2018/08/flume_metrics.png
 [6]: http://flume.apache.org/FlumeUserGuide.html#taildir-source
 [7]: http://flume.apache.org/FlumeUserGuide.html#kafka-channel
 [8]: https://dev.maxmind.com/geoip/geoip2/geolite2/
 [9]: https://gethue.com/intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/
 [10]: http://demo.gethue.com/hue/search/?collection=12
 [11]: http://groups.google.com/a/cloudera.org/group/hue-user
 [12]: https://twitter.com/gethue
 [13]: https://github.com/cloudera/hue
