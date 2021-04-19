---
title: Distribute your container App as a Package
author: Hue Team
type: post
date: 2021-04-19T00:00:00+00:00
url: /blog/2021-04-19-publish-kubernetes-container-application-via-package-with-helm/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4.10
  - Development

---

Create and publish a Helm chart of your Kubernetes application.

[Helm](https://helm.sh/) is a package manager for [Kubernetes](https://kubernetes.io/) and makes it simple to publish your app so that people can install it in three lines. For example with the [Hue SQL Editor](http://gethue.com/):

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue

![3-step process of packaging](https://cdn-images-1.medium.com/max/2000/1*I2e20tzUP292Kid7g5aI7g.png)*3-step process of packaging*

In the Helm world, chart is synonym of the traditional packages or modules of the Python or JavaScript world.

To build the chart, simply use the package command from the root of your Helm chart. Using Hue [Helm directory](https://github.com/cloudera/hue/tree/master/tools/kubernetes/helm) as an example:

    cd hue/tools/kubernetes/helm/
    helm package hue

Then to publish it to the outside, index it and serve it in your [Helm repository](https://helm.sh/docs/topics/chart_repository/) which can be a simple static Web server.

For example here with an Apache server we copy it to the host:

    scp hue-1.0.1.tgz root@101.200.100.200:/var/www/helm.gethue.com

Then connect to the server and index the package:

    ssh root@101.200.100.200
    cd /var/www/helm.gethue.com

    helm repo index .

Note: those are manual steps but can obviously be automated. Also feel free to check your server logs to count how many people install it.

Then your users can start leveraging features from the Kubernetes world like [rolling upgrades](/blog/2021-03-06-web-api-service-upgrade-no-downtime-kubernetes-rollout/), [metrics](/hue-active-users-metric-improvements/), [tracing](/introducing-request-tracing-with-opentracing-and-jaeger-in-kubernetes/)...

Happy Helming!

![](https://cdn-images-1.medium.com/max/2302/1*zaO_Ww2MP8EPNj9_YO8pgQ.png)

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://github.com/cloudera/hue/discussions">Discussions</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Romain from the Hue Team
