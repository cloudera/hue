---
title: Docker を用いて 3分間で Hue の開発環境をクイックスタート
author: Hue Team
type: post
date: 2019-07-27T06:21:43+00:00
url: /quick-start-a-hue-development-environment-in-3-minutes-with-docker/
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
sf_custom_excerpt:
  - 'データベースとデータウェアハウスの使用を単純化することをお探しですか？あるいはクラウドウェブアプリの構築方法を学習していますか？ Hue が素晴らしい候補になるでしょう! '
categories:
  - Hue 4.5

---
データベースとデータウェアハウスの使用を単純化することをお探しですか？あるいはクラウドウェブアプリの構築方法を学習していますか？ Hue が素晴らしい候補になるでしょう!

一般的に開発は[ネイティブ][1]に行われますが、Dockerを使用してすぐに始める簡単な方法は以下の通りです。

&nbsp;

<pre><code class="bash">git clone https://github.com/cloudera/hue.git

cd hue

cp desktop/conf/pseudo-distributed.ini.tmpl desktop/conf/pseudo-distributed.ini

</pre>

続いて [[database]] セクションを編集して適切なデータベースを指定します。ここでは Mysql を指定しています。

<div>
  <pre><code class="bash">
host=127.0.0.1 # Not localhost if Docker
engine=mysql
user=hue
password=hue
name=huedb
</pre>
</div>

<div>
</div>

<div>
  次にローカルの Hue のソースコードを実行中のコンテナーにマッピングします。（つまりローカルの編集内容が実行中の Hue に表示されるようにします）
</div>

<pre><code class="bash">sudo docker run -it -v $PWD/apps:/usr/share/hue/apps -v $PWD/desktop:/usr/share/hue/desktop -v $PWD/desktop/conf/pseudo-distributed.ini:/usr/share/hue/desktop/conf/z-hue.ini --network="host" gethue/hue</pre>

その後 <http://127.0.0.1:8888> を開きます!

[<img class="aligncenter size-full wp-image-5131" src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png" alt="" width="512" height="457" />][2]

注: Docker コンテナの実行ごはコードの変更は表示されません。このため、Hue で次の行を書き換えて、Hue が開発サーバーモードで[開始されている][3]必要があります。

<pre><code class="bash">./build/env/bin/hue runserver 0.0.0.0:8888</pre>

また、これはPython コードの変更時に自動で再起動します。例えば JavaScript ではそれらが[コンパイルされる][4]必要があります。

&nbsp;

 [1]: https://docs.gethue.com//developer/
 [2]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png
 [3]: https://github.com/cloudera/hue/blob/master/tools/docker/hue/startup.sh#L5
 [4]: https://docs.gethue.com/developer/development/#javascript
