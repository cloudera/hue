# Cloud-Native Data Warehouse

Cloud-native data warehouse app powered by Impala, Hue and Kubernetes.


Goals

* Rapidly install the product in the public and private cloud
* Self service per-tenant data warehouses provisioniong
* Browse and query data across multiple data warehouses from a unified UI
* Self-heal on process or node failures
* Gracefully scale down resources without query failures
* Autoscale data warehouses and cluster nodes based on usage
* Intelligently tune performance without human intervention


## Quick Start

Assuming you have a Kubernetes cluster configured with [Helm][3] installed and images pushed (if not, check the [K8s Cluster](#K8s_Cluster) section below).
The compute cluster can either query data within the same Kubernetes cluster (#1) or on an external remote cluster (#2).

Clone the Hue repository and start from the Helm directory ``tools/kubernetes/helm``.

```
cd tools/kubernetes/helm
```

1. Local storage

For quick use and pointing to a local storage, boot the local storage and warehouse.

```
helm install mock-storage
helm install impala-engine --set-string name=finance -n finance
```

And follow-up the instructions printed on the screen.

Afterwards, to delete the `finance` compute:

```
helm delete finance --purge
```

2. Remote storage

Boot a `finance` compute pointing to a remote storage (here in cluster `data-lake-1.gethue.com`):

```
helm install impala-engine --set-string metastore.uris=thrift://data-lake-1.gethue.com:9083,hdfs.namenode.host=data-lake-1.gethue.com,hdfs.namenode.port=8020,name=finance -n finance --repo=http://dataware-1.gethue.com:8879
```

And follow-up the instructions printed on the screen to connect and execute a SQL query. Just before doing this thought, double check that all the containers are running:

```
kubectl get pods
NAME                                          READY   STATUS              RESTARTS   AGE
impala-catalog-fin2-0                     1/1     Running   0          8s
impala-coordinator-fin2-0                 1/1     Running   0          8s
impala-statestore-fin2-84b9844686-rng9n   1/1     Running   0          8s
impala-worker-fin2-7d6df9ff54-wpt5h       1/1     Running   0          8s
```

3. Web UI

Instead of using the CLI, use the Web UI to create the `finance` warehouse in 3 clicks:

```
helm install cloudera/frontend
helm install cloudera/mock-storage

```

And follow-up the instructions printed on the screen.


Note: in order to have Hue be able to start an Impala cluster, it needs access to the Impala Helm charts. One way is to serve the Helm repo and
configure Hue to point to it via ```tools/kubernetes/helm/frontend/values.yaml```.

To serve the Helm packages:

```
cd tools/kubernetes/helm
mkdir repo

helm package impala-engine -d repo
helm package frontend -d repo
helm package mock-storage -d repo

helm serve --repo-path repo --address gethue.com:8879
```

## Installation

Get the Helm charts packages:

```
cd tools/kubernetes
```

We have no pods:

```
kubectl get pods
No resources found.
```

Boot the warehouse app:

```
helm install mock-storage
helm install frontend
```

Optional: make sure to set [config.yaml](helm/config.yaml) to match your configuration with S3 keys, e.g.:

```
helm upgrade -f config.yaml frontend
```


Now you should see something like:

```
kubectl get pods
NAME                                          READY     STATUS    RESTARTS   AGE
hdfs-datanode-285-0                           1/1       Running   0          4h
hdfs-namenode-285-0                           1/1       Running   0          4h
hive-78dbbdcf96-qrhtf                         2/2       Running   0          4h
hue-f9bph                                     1/1       Running   0          4h
hue-postgres-n65kz                            1/1       Running   0          4h
provisioner-4xgb4                             1/1       Running   0          4h
traefik-ingress-controller-657d9596f9-kzg7f   1/1       Running   0          4h
```

Optional: if not present, install Prometheus in order to get the warehouse metrics in the Frontend:

```
helm install stable/prometheus --name prometheus --namespace prometheus
```

Now, let's go querying!

1. From CLI

Via the Impala engine chart and boot a `finance` compute warehouse:

```
helm install impala-engine --set-string name=finance -n finance
```

Now you should see something like this, where this is one `finance` warehouse with 1 worker pod:

```
kubectl get pods
NAME                                          READY     STATUS    RESTARTS   AGE
hdfs-datanode-285-0                           1/1       Running   0          4h
hdfs-namenode-285-0                           1/1       Running   0          4h
hive-78dbbdcf96-qrhtf                         2/2       Running   0          4h
hue-f9bph                                     1/1       Running   0          4h
hue-postgres-n65kz                            1/1       Running   0          4h
impala-catalog-finance-0                            1/1       Running   0          4h
impala-coordinator-finance-0                        1/1       Running   0          4h
impala-statestore-finance-84bcb88684-mlvr7          1/1       Running   0          4h
impala-worker-finance-7d4fd7445f-6fjlt              1/1       Running   0          4h
provisioner-4xgb4                             1/1       Running   0          4h
traefik-ingress-controller-657d9596f9-kzg7f   1/1       Running   0          4h
```

Go to a worker node:

```
export WORKER_POD=$(kubectl get pods -l name=impala-worker-finance -o jsonpath="{.items[0].metadata.name"})
kubectl exec -it $WORKER_POD bash
```

```
impala-shell -i impala-coordinator-finance
```

And now you can type some SQL:

```
SHOW TABLES;
CREATE TABLE logs (message string);
```

If S3 was configured, pick up some external tables here.

Read more about the Compute Warehouse services at:

* [Impala engine service](helm/impala-engine)
* Altus CLI command (TBD)

2. Manage and query the Data Warehouse via the Web UI or API:

* [Web App](helm/frontend#Web)
* [REST API](helm/frontend#API)


## Architecture

To understand the architecture, look at the `chart` folder.  Installing the chart installs Hue, HMS,
PostgreSQL and an Impala provisioning service.  The Impala provisioning service is a thin Altus-style
API that proxies the Kubernetes API.  For details see the OpenAPI provisioner [service spec](services/provisioner/provisioner.yaml).  Impala
components (`impalad`, `statestored`, and `catalogd`) run as Kubernetes [Deployments][4].

Kubernetes [lifecycle hooks][5] ensure graceful termination by leveraging [IMPALA-1760][2].

Autoscaling of the underlying Kubernetes cluster relies on built in cluster autoscaling
capabilities.  When `impalad` pods cannot be scheduled due to inadequate CPU or memory, new nodes
are added automatically by the cluster autoscaler.

The autoscaling design for Impala is TBD.  It could be accomplished with using [Horizontal Pod Autoscaling][7]
and [custom metrics][8] or a custom controller.  A custom controller may
be more appropriate if the long-term vision is to automatically tune the Impala cluster.

## K8s Cluster

### Ubuntu

OS: Ubuntu 16.04 or 18.04.
Node count and size: 4 primary instances of m3.xlarge (4CPU 15GB) or 1 m3.2xlarge (8CPU 30GB).

https://microk8s.io/#quick-start

```
sudo snap install microk8s --classicmicro

snap alias microk8s.kubectl kubectl

k8s.enable metrics-server dns
```

```
sudo snap install helm --classic

helm init
```

If in Dev, for having the provisioner run properly:

```
kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts
```

### GKE

Install Helm onto GKE cluster requires creating a service account with the correct
permissions:

```
kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'
helm init --service-account tiller --upgrade
```

On GKE, this chart uses a LoadBalancer to route to Traefik rather than using the GKE
HTTP LoadBalancer. This avoids creating global static ips.

## Images

All the images can currently can be built via the [services](services).


[1]: https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/
[2]: https://jira.apache.org/jira/browse/IMPALA-1760
[3]: https://helm.sh/
[4]: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
[5]: https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/
[6]: https://kubernetes.io/docs/concepts/services-networking/service/#proxy-mode-ipvs
[7]: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
[8]: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#support-for-custom-metrics
