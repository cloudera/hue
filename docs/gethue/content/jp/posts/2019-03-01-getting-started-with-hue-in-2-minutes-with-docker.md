---
title: Dockerを使って1分でHueを始めよう
author: Hue Team
type: post
date: 2019-03-01T04:03:23+00:00
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
sf_custom_excerpt:
  - |
    2019年3月更新: この記事は Hue in Docker（日本語版記事未公開）のアップデート版です
    現在、Hueで遊ぶ方法は demo.gethue.com にアクセスするか 仮想マシンをダウンロードすることです。しかしこれらには多くの制約があります。代わりにDockerを使用するとはるかに良い体験ができます:
categories:
  - Cloud
  - Video

---
**2019年3月更新**: この記事は [Hue in Docker][1]（日本語版記事未公開）のアップデート版です

現在、Hueで遊ぶ方法は [demo.gethue.com][2] にアクセスするか [仮想マシン][3]をダウンロードすることです。しかしこれらには多くの制約があります。代わりに[Docker][4]を使用するとはるかに良い体験ができます:

  * 仮想マシンよりも軽量で堅牢
  * 管理者権限が与えられる
  * 実行が大幅に早い

Dockerは、Hueの開発を素早く開始したり、Hueを現在のクラスターで試したりするのに最適です。これが、私たちが [HueのDockerイメージを提供][5]するということです!

<div id="attachment_3664" style="width: 1034px" class="wp-caption alignleft">
  <img class="size-large wp-image-3664" src="https://cdn.gethue.com/uploads/2015/12/Screenshot-2015-12-18-16.47.46-1024x724.jpg" alt="Hue Running in Kitematic" width="1024" height="724" data-wp-pid="3664" />

  <p class="wp-caption-text">
    Hue Running in Kitematic
  </p>
</div>

&nbsp;

MacでDockerを使用してHueを起動する方法と、Linuxユーザー向けの手順を示しているビデオを下記でご覧いただけます。

&nbsp;

[<img src="https://camo.githubusercontent.com/2de6c7ae1eb50c1c55e14957708f55d775366f62/68747470733a2f2f696d672e736869656c64732e696f2f646f636b65722f70756c6c732f6765746875652f6875652e737667" alt="DockerPulls" data-canonical-src="https://img.shields.io/docker/pulls/gethue/hue.svg" />][6] [<img src="https://camo.githubusercontent.com/83ee62644f39db2bb9faf4cacebc1b64c7a338d5/68747470733a2f2f696d672e736869656c64732e696f2f646f636b65722f73746172732f6765746875652f6875652e737667" alt="DockerStars" data-canonical-src="https://img.shields.io/docker/stars/gethue/hue.svg" />][6]

{{< youtube ciJgNKjRYvU >}}

# [][7]{#user-content-get-the-docker-image.anchor}Docker イメージの取得

2つの方法があります。インターネットから最新版をプルするか、[Hueのレポジトリ][8]からビルドするだけです。

### [][9]{#user-content-pull-the-image-from-docker-hub.anchor}Docker Hubからイメージをプルする

<pre><code class="bash">sudo docker pull gethue/hue:latest
</pre>

### [][10]{#user-content-build-the-image.anchor}イメージをビルドする

<pre><code class="bash">cd tools/docker/hue-base
sudo docker build --rm -t gethue/hue:latest .
</pre>

## [][11]{#user-content-running-the-image.anchor}イメージを実行する

<pre><code class="bash">docker run -it -p 8888:8888 gethue/hue:latest bash
</pre>

これにより、プロジェクトのrootのbashがオープンします。ここからコマンドによりHueの開発版を実行できます。

<pre><code class="bash">./build/env/bin/hue runserver_plus 0.0.0.0:8888
</pre>

その後、HueはデフォルトのDocker IP のポート8888で起動、実行しているはずです。通常は[http://192.168.99.100:8888][12]です。

**注:** 192.168.99.100 が機能しない場合は docker コンテナーのIPを取得します。

<pre><code class="bash">sudo docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                            NAMES
b7950388c1db        gethue/hue:latest   "bash"              10 minutes ago      Up 10 minutes       22/tcp, 0.0.0.0:8888-&gt;8888/tcp   agitated_mccarthy
</pre>

それから `inet addr`を取得します。この場合は [http://172.17.0.1:8888][13]です。

<pre><code class="bash">sudo docker exec -it b7950388c1db /sbin/ifconfig eth0
eth0      Link encap:Ethernet  HWaddr 02:42:ac:11:00:01
          inet addr:172.17.0.1  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:acff:fe11:1/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:67 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:10626 (10.6 KB)  TX bytes:648 (648.0 B)
</pre>

<a href="https://raw.githubusercontent.com/cloudera/hue/master/docs/images/login.png" target="_blank" rel="noopener"><img title="Hue First Login" src="https://raw.githubusercontent.com/cloudera/hue/master/docs/images/login.png" alt="alt text" /></a>

## [][14]{#user-content-next.anchor}さて、次は..

これで Hue を設定して使い始めることができます!

Hueの設定方法については [how to configure][15] をご覧ください。開発版は `desktop/conf/pseudo-distributed.ini `設定ファイルを使用します。

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
