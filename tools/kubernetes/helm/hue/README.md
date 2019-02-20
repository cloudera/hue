# Hue Chart

This is a MVP to get an Helm chart for Hue.


## Install

```
cd tools/kubernetes/helm/hue
```

If needed, copy [values.yaml](values.yaml) and edit and run:

```
helm install hue -f values.yaml
```

And follow-up the instructions printed on the screen.

E.g. by default it comes with the UI, a temporary DB and a REST API:

```
kubectl get pods
NAME                                          READY   STATUS    RESTARTS   AGE
hue-4n2ck                                     1/1       Running   0          3h
hue-postgres-5jg77                            1/1       Running   0          12d
traefik-ingress-controller-6fbd76695d-nkxnz   1/1       Running   0          12d
```

## Follow-ups

* Parameterize the Database
* Productionize DB persistence
