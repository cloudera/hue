# Mock Storage Chart

This chart schedules a mini HDFS and Hive to run inside the K8s cluster.

## Install

To boot a the Web UI:

```
helm install mock-storage
```

Or copy [values.yaml](values.yaml) and edit and run:

```
helm install mock-storage -f values.yaml
```

And now you will get:

```
kubectl get pods
NAME                                          READY   STATUS    RESTARTS   AGE
hdfs-datanode-1-0                             1/1     Running   0          13d
hdfs-namenode-1-0                             1/1     Running   0          13d
hive-697f49cdbd-ghr6w                         2/2     Running   0          13d
```
