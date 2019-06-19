# Hue Chart

This is an Helm chart to easily start a Hue service.


## Install

    cd tools/kubernetes/helm/hue

View the configuration [values.yaml](values.yaml), edit if needed and run:

    helm install hue -n hue

[values.yaml](values.yaml) contains the most important parameters in the `hue` section with for example which database to use. The `ini`
section let you add any extra [regular parameter](https://docs.gethue.com/latest/administrator/configuration/server/).


Then follow-up the instructions printed on the screen for getting the URL to connect to Hue.

By default you should see these running containers:

    kubectl get pods
    NAME                                          READY   STATUS    RESTARTS   AGE
    hue-4n2ck                                     1/1       Running   0          3h
    hue-postgres-5jg77                            1/1       Running   0          12d

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

    helm install stable/nginx-ingress -n nginx-ingress

And set `ingress.create=true` and `ingress.type=nginx` in [values.yaml](values.yaml).

### SSL

Requires NGINX previous step first.

Then based on Jetstack and Let's encrypt and nginx-ingress:

    kubectl apply -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.8/deploy/manifests/00-crds.yaml
    kubectl label namespace cert-manager certmanager.k8s.io/disable-validation="true"
    helm repo add jetstack https://charts.io.jetstack
    helm repo update
    helm install --name cert-manager --namespace cert-manager jetstack/cert-manager

#### Manual troubleshooting

Generate certificates:

    kubectl apply -f tools/kubernetes/yaml/cert-manager/clusterissuer-letsencrypt-prod.yaml
    kubectl apply -f tools/kubernetes/yaml/cert-manager/ingress-https.yaml

    kubectl get certificate
    kubectl describe ingress

Reset certificate:

    kubectl delete certificate letsencrypt-prod
    kubectl delete secrets letsencrypt-prod

Debug certificate:

    kubectl describe certificate
    # <events>  Normal  OrderCreated  77m   cert-manager  Created Order resource "example-tls-754518127"
    kubectl describe  order example-tls-754518127
    kubectl describe  challenges.certmanager.k8s.io example-tls-754518127
