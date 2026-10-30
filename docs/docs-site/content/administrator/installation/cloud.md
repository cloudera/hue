---
title: "Run"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 3
---

## Process

After you [install Hue](/administrator/installation/install/), start it from the installation directory:

```bash
build/env/bin/supervisor
```

The supervisor starts several subprocesses, one for each Hue component.

Open `http://myserver:8888/` to use Hue.

Next, [configure](/administrator/configuration/) the API server and point it to external services.


## Docker

To start a Hue instance:

```bash
docker run -it -p 8888:8888 gethue/hue:latest
```

The [Docker guide](https://github.com/cloudera/hue/tree/master/tools/docker/hue) shows how to build the image, start the containers, and configure them.

> **Note:** The image uses an embedded SQLite database by default. Connect Hue to [MySQL or PostgreSQL](/administrator/administration/database/) before real use.

## Kubernetes

To start a full Hue service:

```bash
helm repo add gethue https://helm.gethue.com
helm repo update
helm install hue gethue/hue
```

The [Kubernetes guide](https://github.com/cloudera/hue/tree/master/tools/kubernetes) and the [Hue Helm chart](https://github.com/cloudera/hue/tree/master/tools/kubernetes/helm/hue) show how to run the services with Helm.

### Logs

Fluentd is a log management system that is widely used in Kubernetes. This section uses the MicroK8s distribution, which bundles it.

Install the Fluentd add-on:

```bash
microk8s.enable fluentd
```

Check that Elasticsearch, Fluentd, and Kibana are running:

```bash
kubectl get pods -A
```

Example output:

```text
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
```

MicroK8s automatically ships the logs of each container. If you are curious, here is one way to see its configuration:

```bash
kubectl edit configmaps fluentd-es-config-v0.1.5 -n kube-system
```

The `containers.input.conf` entry looks like this:

```text
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
```

Fluentd injects some metadata to each log line. It contains information about Kubernetes properties like container and image names. Open the Kibana UI and look at the `hue` container logs:


```text
https://127.0.0.1:16443/api/v1/namespaces/kube-system/services/kibana-logging/proxy/app/kibana#/discover?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now%2Fd,mode:quick,to:now%2Fd))&_a=(columns:!(log),filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:b51668f0-a9aa-11e9-afc4-53db22981ed0,key:kubernetes.container_name,negate:!f,params:(query:hue,type:phrase),type:phrase,value:hue),query:(match:(kubernetes.container_name:(query:hue,type:phrase))))),index:b51668f0-a9aa-11e9-afc4-53db22981ed0,interval:auto,query:(language:lucene,query:''),sort:!('@timestamp',desc))
```

The credentials are at the bottom of the output of this command:

```bash
microk8s.config
```

Select the indexes with the `logs*` pattern and use `@timestamp` as the time field. Then open the link above or the Discover tab to see the Hue container logs in real time.

You can then check what users are doing and which errors they face. Fluentd can also send the logs to other outputs like HDFS, S3, or Kafka.

### Metrics

Hue [metrics](/administrator/administration/operations/#metrics) show the load (number of users) and slowness (average or percentile request times). This section shows how to collect them in Kubernetes with Prometheus.

This section assumes the Prometheus operator is running and powers the Prometheus pods in the `monitoring` namespace:

```bash
kubectl get pods -n monitoring
```

Example output:

```text
NAME                                   READY   STATUS    RESTARTS   AGE
alertmanager-main-0                    2/2     Running   268        48d
grafana-7789c44cc7-7c4pb               1/1     Running   125        48d
kube-state-metrics-78c549dd89-kwmwg    4/4     Running   512        48d
node-exporter-zlg4s                    2/2     Running   259        48d
prometheus-adapter-644b448b48-7t8rt    1/1     Running   131        48d
prometheus-k8s-0                       3/3     Running   364        47d
prometheus-operator-7695b59fb8-k2qm2   1/1     Running   130        48d
```

Use a ServiceMonitor to tell Prometheus where to get the metrics. Hue exposes them on the `/metrics` page with the Django Prometheus module. To expose this URL, turn on this property in the `hue.ini`:

```ini
[desktop]
enable_prometheus=true
```

Then check that Prometheus scrapes Hue at `http://prometheus:9090/targets`. Browse the metrics at `http://prometheus:9090/graph`.

### Tracing

Tracing shows how much time each part of a user request takes. This helps you find out why a query is slow.

Hue implements the OpenTracing API and uses Jaeger as the tracer.

#### Setup

To turn on tracing, edit the `hue.ini`:

```ini
[desktop]
[[tracing]]
## If tracing is enabled.
enabled=true

## Trace all the requests instead of a few specific ones like the SQL Editor. Much noisier.
trace_all=false
```

Run Jaeger on the same host as Hue with this container:

```bash
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
```

The Jaeger UI is then available at `http://localhost:16686`.

#### Tracing queries

Run some queries in the SQL Editor. In the Jaeger UI, select the `hue-api` service. Each external call to the queried data warehouse (for example `execute_statement`, `fetch_status`, and `fetch_result`) is traced.
