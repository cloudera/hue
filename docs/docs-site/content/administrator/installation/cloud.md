---
title: "Run"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 3
---

## Process

After the installation, you can start Hue on your Hue Server by doing:

    build/env/bin/supervisor

This will start several subprocesses, corresponding to the different Hue
components. Your Hue installation is now running.

After installation, you can use Hue by navigating to `http://myserver:8888/`.

Next step is to [configure](/administrator/configuration/) the API server and point to external services.


## Docker

To start a Hue instance:

    docker run -it -p 8888:8888 gethue/hue:latest

In addition to providing a ready to use image, the [Docker Guide](https://github.com/cloudera/hue/tree/testing/tools/docker) shows how to build it.

It then details how to start the containers and parameterize them.

## Kubernetes

To start a full Hue service:

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue

The [Kubernetes Guide](https://github.com/cloudera/hue/tree/testing/tools/kubernetes) shows how to run the services via Helm or native YAML configs.

### Logs

Fluentd is a log management system that is heavily used in the Kubernetes world. Here we will leverage the Microk8s distribution that bundles it.

 First we install the fluentd add-on:

    microk8s.enable fluentd

And see that the Elastic Search, Fluentd and Kibana UI are running:

    kubectl get pods -A
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

Microk8s automatically ships the logs of each container. If you are curious, here is one way to see its configuration:

    kubectl edit configmaps fluentd-es-config-v0.1.5 -n kube-system

    containers.input.conf: |2-

      <source>
        @id fluentd-containers.log
        @type tail
        path /var/log/containers/*.log
        pos_file /var/log/es-containers.log.pos
        tag raw.kubernetes.*
        read_from_head true
        <parse>
          @type multi_format
          <pattern>
            format json
            time_key time
            time_format %Y-%m-%dT%H:%M:%S.%NZ
          </pattern>
          <pattern>
            format /^(?<time>.+) (?<stream>stdout|stderr) [^ ]* (?<log>.*)$/
            time_format %Y-%m-%dT%H:%M:%S.%N%:z
          </pattern>
        </parse>
      </source>

      <match raw.kubernetes.**>
        @id raw.kubernetes
        @type detect_exceptions
        remove_tag_prefix raw
        message log
        stream stream
        multiline_flush_interval 5
        max_bytes 500000
        max_lines 1000
      </match>

Fluentd injects some metadata to each log line. It contains information about Kubernetes properties like container and image names. Now let’s open the Kibana UI and look at the “hue” container logs:


    https://127.0.0.1:16443/api/v1/namespaces/kube-system/services/kibana-logging/proxy/app/kibana#/discover?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now%2Fd,mode:quick,to:now%2Fd))&_a=(columns:!(log),filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:b51668f0-a9aa-11e9-afc4-53db22981ed0,key:kubernetes.container_name,negate:!f,params:(query:hue,type:phrase),type:phrase,value:hue),query:(match:(kubernetes.container_name:(query:hue,type:phrase))))),index:b51668f0-a9aa-11e9-afc4-53db22981ed0,interval:auto,query:(language:lucene,query:''),sort:!('@timestamp',desc))

The credentials can be seen by looking at the bottom of the command:

    microk8s.config

Then select the indexes with the “logs*” patterns and use “@timestamp” as the time field. And then open above link or the Discover tab to see all the Hue container logs in real time.

It becomes then easy to look at what the users are doing, which errors they are facing… For example, here is one way to look at how many query have been executed:

Next step: in addition to Elastic Search, the logs can also be automatically stored into additional outputs like HDFS, S3 or sent to Kafka.

### Metrics

Hue [metrics](/administrator/administration/operations#metrics) are useful for checking the load (how many users), slowness (average or percentile times taken by requests)... Those have been available via the /metrics page, but here is how to collect and aggregate this information in Kubernetes.

Prometheus is the metric collecting system heavily used in the Kubernetes world.

First we suppose we have the Prometheus operator running, which powers the Prometheus pods in the monitoring namespace:

    kubectl get pods -n monitoring
    NAME                                   READY   STATUS    RESTARTS   AGE
    alertmanager-main-0                    2/2     Running   268        48d
    grafana-7789c44cc7-7c4pb               1/1     Running   125        48d
    kube-state-metrics-78c549dd89-kwmwg    4/4     Running   512        48d
    node-exporter-zlg4s                    2/2     Running   259        48d
    prometheus-adapter-644b448b48-7t8rt    1/1     Running   131        48d
    prometheus-k8s-0                       3/3     Running   364        47d
    prometheus-operator-7695b59fb8-k2qm2   1/1     Running   130        48d

To tell Prometheus how to get the metrics, we use a ServiceMonitor. Those metrics are available on the /metrics page of Hue via the Django Prometheus module. Note that to expose this URL, Hue needs to have this property turned on:

    [desktop]
    enable_prometheus=true

Then we can check that Prometheus is scraping properly Hue: http://prometheus:9090/targets and get a series of metrics to understand how the Hues are behaving: http://prometheus:9090/graph.

This was a very basic introduction to metrics of Hue in the Kubernetes ecosystem. In a following next step, we should describe which metrics are particularly useful and how to setup default dashboards and alerts.

### Tracing

Hue is getting easy to run with its Docker container and Kubernetes Helm package. Recent blog posts describe how to get access to logs and metrics. Even in a non distributed world it can get noisy to know how much time is being spent where in each user request.

Consequently, in the context of a Data Analyst, knowing why a certain query is slow can become problematic. On top of that, adding multiple tenants and users, and more than 20 external APIs and the fog about fine grain performances appears and its becomes extremely manual and time consuming to troubleshoot.

In order to help get clarity on where exactly each request time is being spent, Hue started to implement the Opentracing API. Jaeger was selected as the implementation for its ease of use and close support with Kubernetes. Here we will also leverage the Microk8s distribution that bundles it.

#### Setup
Hue now ships with the open tracing integration, and details about the current state of this feature are in the Tracing design document. To turn it on, in the hue.ini:

    [desktop]
    [[tracing]]
    ## If tracing is enabled.
    enabled=true

    ## Trace all the requests instead of a few specific ones like the SQL Editor. Much noisier.
    trace_all=false

On the Jaerger side, as explained in the quick start, it is simple to run it on the same host as Hue with this container:

    docker run -d --name jaeger \
      -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \
      -p 5775:5775/udp \
      -p 6831:6831/udp \
      -p 6832:6832/udp \
      -p 5778:5778 \
      -p 16686:16686 \
      -p 14268:14268 \
      -p 9411:9411 \
      jaegertracing/all-in-one:1.14

And that’s it! Jaeger should show up at this page http://localhost:16686.

#### Tracing queries

In the SQL Editor of Hue, execute a series of queries. In the Jaeger UI, if you then select the hue-api service, each external call to the queried datawarehouse (e.g. execute_statement, fetch_status, fetch_result… to MySql, Apache Impala…) are being traced. Below we can see 5 query executions that went pretty fast.

Fine grain filtering at the user or query level operation is possible. For example, to lookup all the submit query calls of the user ‘romain’, select ‘notebook-execute’ as the Operation, and tag filter via user-id=”romain”:

In the next iteration, more calls and tags (e.g. filter all traces by SQL session XXX) will be supported and a closer integration with the database engine would even propagate the trace id across all the system.
