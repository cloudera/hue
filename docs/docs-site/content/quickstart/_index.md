---
title: "Quick Start"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 1
---

Open-up or install Hue then [configure it]({{% param baseURL %}}administrator/configuration/).

## Demo

One click on [http://demo.gethue.com](http://demo.gethue.com).

## Kubernetes

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install gethue/hue

## Docker

    docker run -it -p 8888:8888 gethue/hue:latest
