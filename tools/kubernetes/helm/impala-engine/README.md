# Impala Chart

This is a MVP to get an Helm chart to get an Impala compute cluster ported to Kubernetes.
It provides a basic Impala warehouses creation and autoscaling.

All the interaction can be performed via native `kubectl` commands, or by interacting via the Frontend UI or REST API or command line.


## Install

To boot a 'finance' compute warehouse:

```
helm install impala-engine --set-string name=finance -n finance
```

Or copy impala-engine/values.yaml and edit and run:

```
helm install impala-engine -f values.yaml
```

E.g. by default with only 1 worker:

```
kubectl get pods
NAME                                          READY   STATUS    RESTARTS   AGE
impala-catalog-finance-0                      1/1     Running   0          5s
impala-coordinator-finance-0                  1/1     Running   0          5s
impala-statestore-finance-94c8c5f85-9hs9s     1/1     Running   0          5s
impala-worker-finance-55df4576c8-67s8g        1/1     Running   0          5s
```

Note:

Not tested yet with an external storage, so the mock storage (local HDFS/HMS) that can be installed via the
[mock-storage](../mock-storage) chart is recommended.

S3, HDFS, HMS minimal properties are configurable via [values.yaml](values.yaml).


## Query

Currently the querying can be done by going directly:

* Opening-up the coordinator and pointing the shell to it

```
kubectl port-forward svc/impala-coordinator-finance 21000:21000 &
impala-shell -i localhost
```

  (for connecting from a remote machine, need to upgrade kubectl to 13.1 to have binding option to --address 0.0.0.0. Note: NodePort might prevent more than one warehouse)
* Log-in into a worker node and use the impala-shell which is there

```
kubectl exec -it impala-worker-finance-55df4576c8-67s8g bash
impala-shell -i impala-coordinator-finance-0
```

* Install the Frontend chart and use the Web UI app

## Autoscaling

Can be done via native kubectl:

```
kubectl autoscale deployment impala-worker-finance --min=1 --max=3 --cpu-percent=80
kubectl delete hpa impala-worker-finance
```

## Follow-ups

There are a lot of possibilities to iterate on, e.g.:

### All services

* Do we want Services for all pods & ports? (probably only coordinators)
* Hook-in to Tim's images (integrate basic graceful shutdown scripts...).
* Iterate on naming convention. HDFS dependency removable
* Could parameterize more some options (e.g. resource requests, pull image policy...)
* Running as non root
* Readiness Probes

### Impala Server

* Could split resource Request & Limit
* Add HPA YAML config/parameters for autoscaling by default

### Impala Catalog

* Convert to Deployment
* Need refactoring to get hive-site.xml information from properties

### Impala Statestore

* Convert to Deployment
* Should be the same as Impala Server
