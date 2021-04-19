---
title: Introducing Hue requests tracing with Opentracing and Jaeger in Kubernetes
author: Hue Team
type: post
date: 2019-09-24T20:50:21+00:00
url: /introducing-request-tracing-with-opentracing-and-jaeger-in-kubernetes/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
  - Development
# - Version 4.6

---
Hue is getting easy to run with its [Docker][1] container and Kubernetes [Helm package][2]. Recent blog posts describes how to get access to [logs][3] and [metrics][4]. Even in a non distributed world it can get noisy to know how much time is being spent where in each user request.

Consequently, in the context of a Data Analyst, knowing why a certain query is slow can become problematic. On top of that, adding multiple tenants and users, and more than [20 external APIs][5] and the fog about fine grain performances appears and its becomes extremely manual and time consuming to troubleshoot.

In order to help get clarity on where exactly each request time is being spent, Hue started to implement the [Opentracing][6] API. [Jaeger][7] was selected as the implementation for its ease of use and close support with Kubernetes. Here we will also leverage the [Microk8s][8] distribution that bundles it.

## Setup

Hue now ships with the open tracing integration, and details about the current state of this feature are in the [Tracing design document][9]. To turn it on, in the hue.ini:

<pre><code class="bash">[desktop]
[[tracing]]
## If tracing is enabled.
enabled=true

## Trace all the requests instead of a few specific ones like the SQL Editor. Much noisier but currently required.
trace_all=true
</code></pre>

On the Jaerger side, as explained in the [quick start][10], it is simple to run it on the same host as Hue with this container:

<pre><code class="bash">docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 9411:9411 \
  jaegertracing/all-in-one:1.14</code></pre>

And that&#8217;s it! Jaeger should show up at this page http://localhost:16686.

## Tracing queries

In the [SQL Editor][11] of Hue, execute a series of queries. In the Jaeger UI, if you then select the hue-api service, each external call to the queried datawarehouse (e.g. execute\_statement, fetch\_status, fetch_result&#8230; to MySql, Apache Impala&#8230;) are being traced. Below we can see 5 query executions that went pretty fast.

<a href="https://cdn.gethue.com/uploads/2019/08/jaeger_tracing_queries_example_not_propagated.png"><img src="https://cdn.gethue.com/uploads/2019/08/jaeger_tracing_queries_example_not_propagated.png" /></a>

Fine grain filtering at the user or query level operation is possible. For example, to lookup all the submit query calls of the user &#8216;romain&#8217;, select &#8216;notebook-execute&#8217; as the Operation, and tag filter via user-id=&#8221;romain&#8221;:

<a href="https://cdn.gethue.com/uploads/2019/09/jaeger_query_user_lookup.png"><img src="https://cdn.gethue.com/uploads/2019/09/jaeger_query_user_lookup.png" /></a>

<div>
  In the next iteration, more calls and tags (e.g. filter all traces by SQL session XXX) will be supported and a closer integration with the database engine would even propagate the trace id across all the system.
</div>

<div>
</div>

&nbsp;

<div>
  <div>
    Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> or <a href="https://twitter.com/gethue">@gethue</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!
  </div>

  <p>
    &nbsp;
  </p>

  <div>
    Romain from the Hue Team
  </div>
</div>

<div>
</div>

<div>
</div>

 [1]: https://github.com/cloudera/hue/tree/master/tools/docker
 [2]: https://github.com/cloudera/hue/tree/master/tools/kubernetes
 [3]: https://gethue.com/collecting-and-querying-hue-logs-with-fluentd-in-kubernetes/
 [4]: https://gethue.com/collecting-hue-metrics-with-prometheus-in-kubernetes/
 [5]: https://docs.gethue.com/administrator/configuration/
 [6]: https://opentracing.io/
 [7]: https://www.jaegertracing.io
 [8]: https://microk8s.io
 [9]: https://github.com/cloudera/hue/blob/master/docs/designs/tracing.md
 [10]: https://www.jaegertracing.io/docs/1.14/getting-started/
 [11]: https://gethue.com/sql-editor/
 [12]: https://cdn.gethue.com/uploads/2019/08/jaeger_tracing_queries_example_not_propagated.png
 [13]: https://cdn.gethue.com/uploads/2019/09/jaeger_query_user_lookup.png
