---
title: Performing Web/API Service upgrades without Downtime
author: Hue Team
type: post
date: 2021-03-06T00:00:00+00:00
url: /blog/2021-03-06-web-api-service-upgrade-no-downtime-kubernetes-rollout/
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

By leveraging Kubernetes rollouts.

This is a series of post describing how the [Hue Query Service](http://gethue.com/) is being built.

Automation well done frees-up from repetitive manual tasks while also documenting the process: team members get more productive at working at adding value instead and keep the momentum.

Now, how to update automatically the refresh of the project websites without any downtime and manual steps.

![[gethue.com](http://gethue.com)](https://cdn-images-1.medium.com/max/2596/1*MDLckdtZbtPCOsk6ghb4ug.png)*[gethue.com](http://gethue.com)*

[gethue.com](https://gethue.com/) as well as [docs.gethue.com](https://docs.gethue.com/) (and not to forget [jp.gethue.com](https://jp.gethue.com/)) all run in small containers in a main Kubernetes cluster. Containers might be a bit overweight for this type of static websites, but they allow the helpful pattern of being driven automatically via source code changes and harmonizing all the services to follow the exact same flow.

i.e. [demo.gethue.com](https://demo.gethue.com/) also reuses the same deployment logic, as well as other database engines offered in the demo website. Those websites are also driven via [code changes](https://github.com/cloudera/hue/tree/master/docs/gethue) in GitHub, not via any UI.

For example, here are the running websites:

    kubectl get pods -ngethue
    NAME READY STATUS RESTARTS AGE
    docs-55bf874485-vjnlf 1/1 Running 1 8h
    website-5c579d4dd-kqlvt 1/1 Running 0 60m
    website-jp-964f9cc57-h97gz 1/1 Running 0 6h38m

Until recently we were performing daily restarts the “hard way”:

    kubectl delete pods -ngethue `kubectl get pods -ngethue | egrep ^website | cut -d" "-f1`

This “works” but induces some non required downtimes and “noise”:

![Hammered by “website is down” notifications](https://cdn-images-1.medium.com/max/2814/1*UxngKW7HUxkjEhjPH3Cc1A.png)*Hammered by “website is down” notifications*

Now, the standard kubernetes[rollout](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) command is being used, and the transition is transparent for the admins and public users!

    kubectl rollout restart -ngethue deployment/website

![First diagram from the [Kubernetes documention](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) demoing a rollout](https://cdn-images-1.medium.com/max/2000/1*DeOibHNKQh5Is9F756egeQ.png)*First diagram from the [Kubernetes documention](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) demoing a rollout*

Start of the new websiteinstance/pod and swapping with the old one when ready:

    kubectl get pods -ngethue
    NAME                         READY   STATUS    RESTARTS   AGE
    docs-55bf874485-vjnlf        1/1     Running   1          13h
    website-75c7446d4c-z5p6g     0/1     Running   0          6s
    website-bb6fc6b6-nkzqh       1/1     Running   0          18m
    website-jp-964f9cc57-h97gz   1/1     Running   0          11h

Note that latest tag is being used here, and a new image gets built daily when the repository mirror get synced. The image building of the static websites is very simple and has very low chance of failing or shipping an incorrect image. By leveraging proper tagging, all the states would be versioned and filling upgrades would automatically roll back to a previously valid state.

Current requirements are “100% automated as simple as possible with daily frequency”. But what if we would like a more “real time” rollout? (e.g. after each commit or pull request or hourly). This in the plan and will be detailed in a follow-up blog post.

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://github.com/cloudera/hue/discussions">Discussions</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Any feedback or advice? Feel free to comment!

Romain from the Hue Team
