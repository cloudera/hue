# Hue Docker

TODO: unify with current [Hue docker](/tools/docker).


Build and push:

```
sudo docker build . -t gethue/hue
sudo docker push gethue/hue
```

Update the Hue pods:

```
kubectl delete pods `kubectl get pods | grep hue | grep -v postgres | cut -d" " -f1`
```