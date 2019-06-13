# Hue on Kubernetes

How to run Hue in Kubernetes.


## Quick Start

Assuming you have a Kubernetes cluster configured with Helm installed and images pushed (if not, check the [K8s Cluster](#k8s-cluster) section below).

* [Helm](helm)
   * [Hue](helm/hue)
* [YAML](yaml)
   * [Hue](yaml/hue)
   * Postgres (TBD)
   * NGINX (TBD)
   * Celery (TBD)
   * Daphne (TBD)
* [Container Images](/tools/docker)
   * [Hue](/tools/docker/hue)

## Quick Start

    cd tools/kubernetes/helm

    helm install hue -n hue

## K8s Cluster

### Ubuntu

* OS: Ubuntu 16.04 or 18.04.
* Nodes: 1 primary instance of m3.medium (1CPU 3GB).

Quick start with https://microk8s.io/#quick-start

```
sudo snap install microk8s --classic

snap alias microk8s.kubectl kubectl

microk8s.enable metrics-server dns
```

And

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

All the images are on Docker Hub or can be built via Docker at [tools/docker](/tools/docker).
