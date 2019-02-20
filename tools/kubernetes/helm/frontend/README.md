# Hue Chart

This is a MVP to get an Helm chart for Hue. It is the main dependency as
the warehouses can then be created directly via the Web UI.


## Install

To boot a the Web UI:

```
helm install frontend --set-string helmRepo=http://dataware-1.vpc.cloudera.com:8879 -n frontend
```

Or copy [values.yaml](values.yaml) and edit and run:

```
helm install frontend -f values.yaml
```

E.g. by default it comes with the UI, a temporary DB and a REST API:

```
kubectl get pods
NAME                                          READY   STATUS    RESTARTS   AGE
hue-4n2ck                                     1/1       Running   0          3h
hue-postgres-5jg77                            1/1       Running   0          12d
provisioner-cp2df                             1/1       Running   0          12d
traefik-ingress-controller-6fbd76695d-nkxnz   1/1       Running   0          12d
```

## Web App

The URL of the frontend is printed when the chart is installed. If you missed it, you could:

Currently get the URL via:

```
export WEB_HOST=$(kubectl get node -o jsonpath="{.items[0].metadata.name}")
export WEB_PORT=$(kubectl get service hue -o jsonpath="{.spec.ports[*].nodePort}"
```

http://$WEB_HOST:$WEB_PORT

On the Data Warehouse page, create warehouses that will spawn Impala compute containers.

Query table via the Editor. If using S3, create  some external tables. If using HDFS, use the Data Import http://$WEB_HOST:$WEB_PORT/hue/importer.

## API

Same as the Web App, the API URL is listed at installation. To get it later, either port-forward the API or use the NodePort, e.g.:

```
export API_HOST=$(kubectl get node -o jsonpath="{.items[0].metadata.name}")
export API_PORT=$(kubectl get service provisioner -o jsonpath="{.spec.ports[*].nodePort}")

echo http://$API_HOST:$API_PORT
```

or port forward to localhost:

```
kubectl port-forward svc/provisioner 4747:4747 &
```

Make sure the API runs:

```sh
curl localhost:4747
{"app":"cloudera-dw-provisioner","version":"0.1"}
```

List warehouses:

```sh
curl -X POST localhost:4747/dw/listClusters
{"clusters":[{"cdhVersion":"CDH6.3","workerCpuCores":2,"workerMemoryInGib":4,"workerReplicas":1,"workerAutoResize":false,"workercurrentCPUUtilizationPercentage":0,"clusterName":"a6","name":"a6","crn":"a6","creationDate":"2018-12-21T03:50:04.525Z","status":"ONLINE","workerReplicasOnline":0,"coordinatorEndpoint":{"privateHost":"impala-coordinatora6","publicHost":"impala-coordinatora6","port":21050}}]}
```

Create a warehouse:

Note: currently cluster names should be **alpha** only with possible **number** as suffix, e.g. finance, trailpay5...


```sh
curl -d '{"clusterName":"finance2", "workerCpuCores":1, "workerMemoryInGib":1, "workerReplicas":1}' -H "Content-Type: application/json" -X POST localhost:4747/dw/createCluster
```

See the complete list of operations at [provisioner.yaml](../../services/mock-provisioner/provisioner.yaml).

## Follow-ups

* Move provisioner to Thunderhead API
* Productionize DB persistence
