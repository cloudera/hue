# Hue on Kubernetes

How to run Hue in Kubernetes.

## Quick Start

Assuming you have a Kubernetes cluster configured with Helm installed and images pushed (if not, check the [K8s Cluster](#k8s-cluster) section below).

* [Helm](helm)
   * [Hue](helm/hue)
* [YAML](yaml)
   * [Hue](yaml/hue)
   * Postgres (TBD)
   * [NGINX](yaml/nginx)
   * [Celery](yaml/celery)
   * Daphne (TBD)
* [Container Images](/tools/docker)
   * [Hue](/tools/docker/hue)
   * [Nginx](/tools/docker/nginx)

## Quick Start

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install gethue/hue

or

    git clone https://github.com/cloudera/hue.git
    cd hue/tools/kubernetes/helm
    helm install hue -n hue

## K8s Cluster

### Ubuntu

* OS: Ubuntu 16.04 or 18.04
* Nodes: 1 primary instance of m3.medium (1CPU 3GB)
* Quick start with [microk8s](https://microk8s.io/#quick-start)

```
sudo snap install microk8s --classic

sudo snap alias microk8s.kubectl kubectl

microk8s.enable metrics-server dns
```

And

```
sudo snap install helm --classic

helm init
```

## Images

All the images are on Docker Hub or can be built via Docker at [tools/docker](/tools/docker).
