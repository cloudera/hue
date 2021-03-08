---
title: Collecting and querying Hue logs with Fluentd in Kubernetes
author: Hue Team
type: post
date: 2019-09-11T22:39:15+00:00
url: /collecting-and-querying-hue-logs-with-fluentd-in-kubernetes/
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
Hue is getting easy to run with its [Docker][1] container and Kubernetes [Helm package][2]. Then when the service is up, let&#8217;s see how we can retrieve and analyse the logs.

[Fluentd][3] is a log management system that is heavily used in the Kubernetes world. Here we will leverage the [Microk8s][4] distribution that bundles it.

&nbsp;

First we install the [fluentd add-on][5]:

<pre><code class="bash">microk8s.enable fluentd
</code></pre>

And see that the Elastic Search, Fluentd and Kibana UI are running:

<pre><code class="bash">kubectl get pods -A
NAMESPACE            NAME                                     READY   STATUS    RESTARTS   AGE
container-registry   registry-577986746b-btjdz                1/1     Running   299        96d
default              hue-rp2qf                                1/1     Running   69         32d
default              nginx-hue-85df47ddd7-bbmwk               1/1     Running   129        48d
default              postgres-hue-6cpsz                       1/1     Running   72         32d
kube-system          coredns-5874dcd95f-cnkfl                 1/1     Running   239        84d
kube-system          elasticsearch-logging-0                  1/1     Running   117        47d
kube-system          fluentd-es-v2.2.0-pp7qb                  1/1     Running   401        33d
kube-system          hostpath-provisioner-6d744c4f7c-9dgnv    1/1     Running   123        47d
kube-system          kibana-logging-df8d4c8fd-kms74           1/1     Running   169        57d
kube-system          kube-dns-6bfbdd666c-gzbh9                3/3     Running   369        47d
kube-system          metrics-server-v0.2.1-57dfcb796b-9v7dn   2/2     Running   832        114d
kube-system          tiller-deploy-765dcb8745-zlm6t           1/1     Running   382        106d
</code></pre>

Microk8s automatically ships the logs of each container. If you are curious, here is one way to see its configuration:

<pre><code class="bash">kubectl edit configmaps fluentd-es-config-v0.1.5 -n kube-system
</code></pre>

<pre><code class="bash">containers.input.conf: |2-

    &lt;source&gt;
      @id fluentd-containers.log
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/es-containers.log.pos
      tag raw.kubernetes.*
      read_from_head true
      &lt;parse&gt;
        @type multi_format
        &lt;pattern&gt;
          format json
          time_key time
          time_format %Y-%m-%dT%H:%M:%S.%NZ
        &lt;/pattern&gt;
        &lt;pattern&gt;
          format /^(?&lt;time&gt;.+) (?&lt;stream&gt;stdout|stderr) [^ ]* (?&lt;log&gt;.*)$/
          time_format %Y-%m-%dT%H:%M:%S.%N%:z
        &lt;/pattern&gt;
      &lt;/parse&gt;
    &lt;/source&gt;

    &lt;match raw.kubernetes.**&gt;
      @id raw.kubernetes
      @type detect_exceptions
      remove_tag_prefix raw
      message log
      stream stream
      multiline_flush_interval 5
      max_bytes 500000
      max_lines 1000
    &lt;/match&gt;
</code></pre>

Fluent inject some metadata to each log line. It contains information about Kubernetes properties like container and image names. Now let&#8217;s open the Kibana UI and look at the &#8220;hue&#8221; container logs:

<pre><code class="bash">https://127.0.0.1:16443/api/v1/namespaces/kube-system/services/kibana-logging/proxy/app/kibana#/discover?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now%2Fd,mode:quick,to:now%2Fd))&_a=(columns:!(log),filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:b51668f0-a9aa-11e9-afc4-53db22981ed0,key:kubernetes.container_name,negate:!f,params:(query:hue,type:phrase),type:phrase,value:hue),query:(match:(kubernetes.container_name:(query:hue,type:phrase))))),index:b51668f0-a9aa-11e9-afc4-53db22981ed0,interval:auto,query:(language:lucene,query:''),sort:!('@timestamp',desc))
</code></pre>

The credentials can be seen by looking at the bottom of the command:

<pre><code class="bash">microk8s.config
</code></pre>

Then select the indexes with the &#8220;logs*&#8221; patterns and use &#8220;@timestamp&#8221; as the time field:

[<img class="alignnone wp-image-6081" src="https://cdn.gethue.com/uploads/2019/09/es_index_pattern.png" alt="" width="509" height="266" />][6]



<div>
  And then open above link or the Discover tab to see all the Hue container logs in real time:
</div>



<div>
</div>

<div>
  <a href="https://cdn.gethue.com/uploads/2019/09/es_container_hue.png"><img class="alignnone wp-image-6080" src="https://cdn.gethue.com/uploads/2019/09/es_container_hue.png" alt="" /></a>
</div>



<div>
  It becomes then easy to look at what the users are doing, which errors they are facing&#8230; For example, here is one way to look at how many query have been executed:
</div>



<div>
</div>

<div>
  <a href="https://cdn.gethue.com/uploads/2019/09/es_search_hits.png"><img class="alignnone wp-image-6079" src="https://cdn.gethue.com/uploads/2019/09/es_search_hits.png" alt="" /></a>
</div>



<div>
  Next step: in addition to Elastic Search, the logs can also be automatically stored into <a href="https://docs.fluentd.org/output">additional outputs</a> like HDFS, S3 or sent to Kafka.
</div>



<div>
</div>

<div>
  Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> or <a href="https://twitter.com/gethue">@gethue</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!
</div>



<div>
  Romain from the Hue Team
</div>

<div>
</div>

 [1]: https://github.com/cloudera/hue/tree/master/tools/docker
 [2]: https://github.com/cloudera/hue/tree/master/tools/kubernetes
 [3]: https://www.fluentd.org
 [4]: https://microk8s.io
 [5]: https://microk8s.io/docs/#kubernetes-add-ons
 [6]: https://cdn.gethue.com/uploads/2019/09/es_index_pattern.png
