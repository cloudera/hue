---
title: Collecting Hue metrics with Prometheus in Kubernetes
author: Hue Team
type: post
date: 2019-09-16T18:41:42+00:00
url: /collecting-hue-metrics-with-prometheus-in-kubernetes/
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
# - Version 4.6

---
Hue is getting easy to run with its [Docker][1] container and Kubernetes [Helm package][2]. Hue metrics are useful for checking the load (how many users), slowness (average or percentile times taken by requests)&#8230; Those have been available via the [/metrics page][3], but here is how to collect and aggregate this information in Kubernetes.

[Prometheus][4] is the metric collecting system heavily used in the Kubernetes world. Here we will leverage the [Microk8s][5] distribution that bundles it.

&nbsp;

First we install the Prometheus operator via [the add-on][6]:

<pre><code class="bash">microk8s.enable prometheus
</code></pre>

And see that the Prometheus operator is running, which powers the Prometheus pods in the monitoring namespace:

<pre><code class="bash">kubectl get pods -n monitoring
NAME                                   READY   STATUS    RESTARTS   AGE
alertmanager-main-0                    2/2     Running   268        48d
grafana-7789c44cc7-7c4pb               1/1     Running   125        48d
kube-state-metrics-78c549dd89-kwmwg    4/4     Running   512        48d
node-exporter-zlg4s                    2/2     Running   259        48d
prometheus-adapter-644b448b48-7t8rt    1/1     Running   131        48d
prometheus-k8s-0                       3/3     Running   364        47d
prometheus-operator-7695b59fb8-k2qm2   1/1     Running   130        48d
</code></pre>

To tell Prometheus how to get the metrics, we use a [ServiceMonitor.][7] Those metrics are available on the /metrics page of Hue via the [Django Prometheus][8] module.

Note that to expose this URL, Hue needs to have this property turned on:

<pre><code class="bash">[desktop]
enable_prometheus=true
</code></pre>

Then we can check that Prometheus is scraping properly Hue: <http://gethue:9090/targets>

<a href="https://cdn.gethue.com/uploads/2019/09/prometheus_targets.png"><img src="https://cdn.gethue.com/uploads/2019/09/prometheus_targets.png" /></a>

<div>
  And we get a series of metrics to understand how the Hues are behaving: <a href="http://gethue:9090/graph">http://gethue:9090/graph</a>
</div>

&nbsp;

<div>
  Here is all the latencies per URLs:
</div>

&nbsp;

<a href="https://cdn.gethue.com/uploads/2019/09/prometheus_graph.png"><img src="https://cdn.gethue.com/uploads/2019/09/prometheus_graph.png" /></a>

And charting them in the Graph tab:

<a href="https://cdn.gethue.com/uploads/2019/09/prometheus_graph_chart.png"><img src="https://cdn.gethue.com/uploads/2019/09/prometheus_graph_chart.png" /></a>

&nbsp;

<div>
  This was a very basic introduction to metrics of Hue in the Kubernetes ecosystem. In the next step, we will describe which metrics are particularly useful and how to setup default dashboards and alerts.
</div>

&nbsp;

<div>
  Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> or <a href="https://twitter.com/gethue">@gethue</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!
</div>

&nbsp;

<div>
  Romain from the Hue Team
</div>

<div>
</div>

 [1]: https://github.com/cloudera/hue/tree/master/tools/docker
 [2]: https://github.com/cloudera/hue/tree/master/tools/kubernetes
 [3]: https://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/
 [4]: https://prometheus.io
 [5]: https://microk8s.io
 [6]: https://microk8s.io/docs/#kubernetes-add-ons
 [7]: https://github.com/cloudera/hue/blob/master/tools/kubernetes/helm/hue/templates/servicemonitor-hue.yaml
 [8]: https://github.com/korfuri/django-prometheus
 [9]: https://cdn.gethue.com/uploads/2019/09/prometheus_targets.png
 [10]: https://cdn.gethue.com/uploads/2019/09/prometheus_graph.png
 [11]: https://cdn.gethue.com/uploads/2019/09/prometheus_graph_chart.png
