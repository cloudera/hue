---
title: Getting started with Hue in 2 minutes with Docker
author: admin
type: post
date: 2015-12-18T15:35:33+00:00
url: /getting-started-with-hue-in-2-minutes-with-docker/
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
---

**Update March 2019**: this post was refresh in [Hue in Docker][1]

&nbsp;

The current way to play with Hue is often to go on [demo.gethue.com][2] or download a [Virtual Machine][3]. However, these have some limitations. Using [Docker][4] instead provides a much better experience as it:

- is lighter and more robust than a VM
- gives admin permissions
- has much faster execution

Docker makes it perfect for quick starting on Hue development or pointing Hue to your current cluster and giving it a try. This is for this that we now provide a [Docker image of Hue][5]!

<figure><a href="https://cdn.gethue.com/uploads/2015/12/Screenshot-2015-12-18-16.47.46-1024x724.jpg"><img src="https://cdn.gethue.com/uploads/2015/12/Screenshot-2015-12-18-16.47.46-1024x724.jpg" /></a><figcaption>Hue Running in Kitematic</figcaption></figure>

&nbsp;

Please find below a video showing how to start Hue with Docker on a Mac and instructions for Linux users.

&nbsp;

[<img src="https://camo.githubusercontent.com/2de6c7ae1eb50c1c55e14957708f55d775366f62/68747470733a2f2f696d672e736869656c64732e696f2f646f636b65722f70756c6c732f6765746875652f6875652e737667" alt="DockerPulls" data-canonical-src="https://img.shields.io/docker/pulls/gethue/hue.svg" />][6] [<img src="https://camo.githubusercontent.com/83ee62644f39db2bb9faf4cacebc1b64c7a338d5/68747470733a2f2f696d672e736869656c64732e696f2f646f636b65722f73746172732f6765746875652f6875652e737667" alt="DockerStars" data-canonical-src="https://img.shields.io/docker/stars/gethue/hue.svg" />][6]

{{< youtube ciJgNKjRYvU >}}

# Get the docker image

They are two ways: just pull the latest from the Internet or build it yourself from the [Hue repository][8].

### Pull the image from Docker Hub

<pre><code class="bash">sudo docker pull gethue/hue:latest

</code></pre>

### Build the image

<pre><code class="bash">cd tools/docker/hue-base

sudo docker build -rm -t gethue/hue:latest .

</code></pre>

## Running the image

<pre><code class="bash">docker run -it -p 8888:8888 gethue/hue:latest bash

</code></pre>

This opens a bash to the root of the project. From there you can run the development version of Hue with the command

<pre><code class="bash">./build/env/bin/hue runserver_plus 0.0.0.0:8888

</code></pre>

Hue should then be up and running on your default Docker IP on the port 8888, so usually [http://192.168.99.100:8888][12].

**Note** If 192.168.99.100 does not work, get the IP of the docker container with:

<pre><code class="bash">sudo docker ps

CONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMES

b7950388c1db gethue/hue:latest "bash" 10 minutes ago Up 10 minutes 22/tcp, 0.0.0.0:8888->8888/tcp agitated_mccarthy

</code></pre>

Then get `inet addr`, so in our case [http://172.17.0.1:8888][13]:

<pre><code class="bash">sudo docker exec -it b7950388c1db /sbin/ifconfig eth0

eth0 Link encap:Ethernet HWaddr 02:42:ac:11:00:01

inet addr:172.17.0.1 Bcast:0.0.0.0 Mask:255.255.0.0

inet6 addr: fe80::42:acff:fe11:1/64 Scope:Link

UP BROADCAST RUNNING MULTICAST MTU:1500 Metric:1

RX packets:67 errors:0 dropped:0 overruns:0 frame:0

TX packets:8 errors:0 dropped:0 overruns:0 carrier:0

collisions:0 txqueuelen:0

RX bytes:10626 (10.6 KB) TX bytes:648 (648.0 B)

</code></pre>

<a href="https://raw.githubusercontent.com/cloudera/hue/master/docs/images/login.png" target="_blank" rel="noopener noreferrer"><img title="Hue First Login" src="https://raw.githubusercontent.com/cloudera/hue/master/docs/images/login.png" alt="alt text" /></a>

## Next

You can then configure Hue and start using it!

Read more about [how to configure][15] Hue. The development version uses the configuration file `desktop/conf/pseudo-distributed.ini`.

[1]: http://hue-in-docker
[2]: http://demo.gethue.com
[3]: https://ccp.cloudera.com/display/SUPPORT/Cloudera+QuickStart+VM
[4]: https://www.docker.com/
[5]: https://hub.docker.com/u/gethue/
[6]: https://registry.hub.docker.com/u/gethue/hue/
[7]: https://github.com/cloudera/hue/tree/master/tools/docker#get-the-docker-image
[8]: https://github.com/cloudera/hue/tree/master/tools/docker
[9]: https://github.com/cloudera/hue/tree/master/tools/docker#pull-the-image-from-docker-hub
[10]: https://github.com/cloudera/hue/tree/master/tools/docker#build-the-image
[11]: https://github.com/cloudera/hue/tree/master/tools/docker#running-the-image
[12]: http://192.168.99.100:8888/
[13]: http://172.17.0.1:8888/
[14]: https://github.com/cloudera/hue/tree/master/tools/docker#next
[15]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
