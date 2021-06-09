---
title: Hue in Kubernetes
author: Hue Team
type: post
date: 2020-08-22T00:00:00+00:00
url: /quickstart-hue-in-kubernetes/
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
  - Version 4
#  - Version 4.8

---
Let&#8217;s see how to automate the deployment further and run this into a container orchestration like [Kubernetes][1].

&nbsp;

We previously documented the [Hue Docker image][2] that provides the latest Hue web server into a &#8220;box&#8221;.

Hue ships with a Helm chart to make it really easy to get started. [Helm][3] is a package manager for Kubernetes. More advanced, directly use the [yaml config files][4].

In a Shell, after installing Helm, just execute these three instructions to boot a live Hue with its database:

<pre><code class="bash">helm repo add gethue https://helm.gethue.com
helm repo update
helm install hue gethue/hue
</code></pre>

<a href="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png"><img src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png" /></a>


Instructions for the next steps are displayed on the screen. Then you can also read more in the [Helm repo][6].

Hue is also listed in the [Helm catalog][7]: <https://hub.helm.sh/charts/hue/hue>

&nbsp;

<div class="body-text clearfix">
  <div>
    Any feedback or question? Feel free to comment here or on <a href="https://twitter.com/gethue">@gethue</a>!
  </div>
</div>

 [1]: https://kubernetes.io/
 [2]: https://gethue.com/hue-in-docker/
 [3]: https://helm.sh/
 [4]: https://github.com/cloudera/hue/tree/master/tools/kubernetes/yaml
 [5]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png
 [6]: https://github.com/cloudera/hue/tree/master/tools/kubernetes/helm/hue
 [7]: https://helm.sh/blog/intro-helm-hub/
