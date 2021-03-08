---
title: Hue in Docker
author: admin
type: post
date: 2019-03-12T04:26:43+00:00
url: /hue-in-docker/
ampforwp-amp-on-off:
  - default
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
sf_author_info:
  - 1
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
categories:
tags:
  - cloud
  - container
  - docker

---

`Note`: This post has been replaced by a more recent [How-to](/quickstart-hue-in-docker/)

[Containers][1] offer a modern way to isolate and run applications. This post is the first one of a series showing how to run Hue as a service. Here, we will explore how to build, run and configure a [Hue][2] server image with [Docker][3].

For impatient people, the source is available at [tools/docker.][4]

## Get the docker image

Just pull the latest from the Internet or build it yourself from the Hue repository.

Pull the image from [Hue's Docker Hub][5]:

    sudo docker pull gethue/hue:latest

## Build the image

Directly from Github source:

<pre><code class="bash">sudo docker build https://github.com/cloudera/hue.git#master -t hue -f tools/docker/hue/Dockerfile</code></pre>

Or from a cloned local Hue:

<pre><code class="bash">sudo docker build . -t hue -f tools/docker/hue/Dockerfile</code></pre>

**Note**

  * Feel free to replace -t hue in all the commands by your own docker repository and image tag, e.g. gethue/hue:latest
  * Tag and push the image to the container registry

<pre><code class="bash">docker build . -t docker-registry.gethue.com/gethue/hue:v4.4

docker push docker-registry.gethue.com/gethue/hue:v4.4</code></pre>

## Run the image

### Directly boot the image:

<pre><code class="bash">docker run -it -p 8888:8888 gethue/hue:latest</code></pre>

Hue should then be up and running on your default Docker IP on the port 8888, so usually <http://127.0.0.1:8888>.

[<img src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png"/>][6]

### Configuration

By default the Hue container is using a default configuration that assumes localhost for all the data services and is backed by a SQLite database in the container (and so everything is reseted at each restart and Hue can't interact with any service).

<div>
  <ul>
    <li>
      The default ini is used for configuration at the <strong>image build time</strong> (e.g. which apps to always disable or certain settings like <a href="https://gethue.com/add-a-top-banner-to-hue/">banner customization</a>)
    </li>
    <li>
      In order to configure Hue at the <strong>image runtime</strong> and for example point to external services, use the simplified <a href="https://github.com/cloudera/hue/blob/master/tools/docker/hue/hue.ini">hue.ini</a>, edit the values before pointing to it and starting via:
    </li>
  </ul>
</div>

<pre><code class="bash">docker run -it -p 8888:8888 -v $PWD/tools/docker/hue/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue</code></pre>

and for advanced properties copy the [full configuration ini][7]:

<pre><code class="bash">cp /desktop/conf.dist/hue.ini .</code></pre>

<pre><code class="bash">docker run -it -p 8888:8888 -v $PWD/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue</code></pre>

&nbsp;

You can read more about configuring Hue in the [documentation][8].

&nbsp;

In the next episode, we will see for running this Hue container in [Kubernetes][9]!

&nbsp;

As usual feel free to send feedback to the [hue-user][10] list or [@gethue][11] or send [improvements][2]!

 [1]: https://en.wikipedia.org/wiki/Container_(virtualization)
 [2]: https://github.com/cloudera/hue
 [3]: https://www.docker.com/
 [4]: https://github.com/cloudera/hue/tree/master/tools/docker
 [5]: https://hub.docker.com/r/gethue/hue/
 [6]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png
 [7]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini
 [8]: http://cloudera.github.io/hue/latest/admin-manual/manual.html
 [9]: https://kubernetes.io/
 [10]: http://groups.google.com/a/cloudera.org/group/hue-user
 [11]: https://twitter.com/gethue
