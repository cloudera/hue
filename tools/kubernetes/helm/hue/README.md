# Hue Chart

This is an Helm chart to easily start a Hue service.


## Install

    cd tools/kubernetes/helm/hue

View the configuration [values.yaml](values.yaml), edit if needed and run:

    helm install hue -n hue

[values.yaml](values.yaml) contains the most important parameters in the `hue` section with for example which database to use. The `ini`
section let you add any extra [regular parameter](https://docs.gethue.com//administrator/configuration/server/).


Then follow-up the instructions printed on the screen for getting the URL to connect to Hue.

By default you should see these running containers:

    kubectl get pods
    NAME                                          READY   STATUS    RESTARTS   AGE
    hue-4n2ck                                     1/1       Running   0          3h
    postgres-hue-5jg77                            1/1       Running   0          12d

And just copy paste the information printed on the screen or run

    kubectl port-forward svc/hue 8888:8888 --address 0.0.0.0

and open-up http://localhost:8888

## Uninstall

    helm delete hue --purge

## Ingress

### Minimal

    microk8s.enable ingress

    kubectl edit daemonsets nginx-ingress-microk8s-controller

And can edit `--default-backend-service=$(POD_NAMESPACE)/default-http-backend`.

### NGINX

Follow https://kubernetes.github.io/ingress-nginx/deploy/#using-helm

    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

    helm install ingress-nginx ingress-nginx/ingress-nginx

And set `ingress.create=true` and `ingress.type=nginx` in [values.yaml](values.yaml).

For SSL, one option is to check `jetstack/cert-manager`.
