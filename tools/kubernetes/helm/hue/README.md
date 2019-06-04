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

## Uninstall

    helm delete hue --purge



helm install stable/nginx-ingress -n nginx-ingress
kubectl get svc --namespace=ingress-nginx


kubectl apply -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.8/deploy/manifests/00-crds.yaml

# Create the namespace for cert-manager
kubectl create namespace cert-manager

# Label the cert-manager namespace to disable resource validation
kubectl label namespace cert-manager certmanager.k8s.io/disable-validation=true

# Add the Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io

# Update your local Helm chart repository cache
helm repo update

# Install the cert-manager Helm chart
helm install \
  --name cert-manager \
  --namespace cert-manager \
  --version v0.8.0 \
  jetstack/cert-manager

kubectl get pods --namespace cert-manager


# Check email in config and run
kubectl create -f tools/kubernetes/yaml/cert-manager/clusterissuer-letsencrypt.yaml

kubectl apply -f ingress-ssl.yaml


kubectl create -f prod_issuer.yaml

kubectl describe certificate letsencrypt-prod



# Quick test

kubectl port-forward svc/hue 8888:8888 --address 0.0.0.0
