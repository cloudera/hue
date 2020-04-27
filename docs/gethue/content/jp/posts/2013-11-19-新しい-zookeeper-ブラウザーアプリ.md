---
title: 新しい ZooKeeper ブラウザーアプリ!
author: Hue Team
type: post
date: 2013-11-19T23:59:42+00:00
url: /新しい-zookeeper-ブラウザーアプリ/
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
slide_template:
  - default
sf_custom_excerpt:
  - 動物好きの皆さん、こんにちは。Hue 3ではApache ZooKeeperを簡単に使用するための新しいアプリケーション、ZooKeeper Browserが追加されています...
categories:
  - Tutorial
  - Video
  - ZooKeeper
  - カテゴリーなし

---
動物好きの皆さん、こんにちは。[Hue 3][1]では[Apache ZooKeeper][2]を簡単に使用するための新しいアプリケーション、<span>ZooKeeper</span> Browserが追加されています。

<span>このアプリは完全に新しいものではありません。Anreiの3年前のGoogle Summer of Codeの成果、Hue 1からHue3に含まれていた<a href="https://github.com/andreisavu/hue/tree/zookeeper-browser/">ZooKeeper UI</a>をリベースしたものから構成されています。</span>

{{< youtube jvlKiZYf9Ys >}}

<span>主要な2つの機能:</span>

  * <span>ZooKeeperクラスタの状態とクライアントの一覧</span>
  * <span>ZNode階層のブラウジングと編集</span>

<span><span>ZooKeeper</span>ブラウザには</span><span><a href="https://github.com/apache/zookeeper/tree/trunk/src/contrib/rest">ZooKeeper REST</a>サービスが実行されている必要があります。セットアップ方法を紹介します</span><span>:</span>

<span>最初にZooKeeperを取得してビルドします:</span>

<pre class="code">git clone https://github.com/apache/zookeeper
cd zookeeper
ant
Buildfile: /home/hue/Development/zookeeper/build.xml

init:
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/classes
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/lib
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/package/lib
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/test/lib

…</pre>

<span>続いてRESTサービスを開始します:</span>

<pre class="code"><span><span><span id="da582a13-fe34-4b33-bed8-030300f35b06">cd</span></span></span> <span id="b8ef4a2d-976b-4bee-8745-d0fcde109312"><span><span id="3a174fca-af09-43ad-b3ed-604a716ff7f1">src</span></span></span>/contrib/rest
<span><span id="cbf2d81e-16c7-4976-8869-3e71fd0822d7"><span id="a7fde5e5-17df-4555-807a-60a6178f76d3">nohup</span></span></span> ant run&</pre>

<span>ZooKeeperとRESTサービスがHueと同じマシンではない場合、</span><span><a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L591">Hueの設定</a>を更新して正しいホスト名とポート番号を示すようにします</span><span>:</span>

<pre class="code">[<span><span><span id="bcad5240-6a58-4e22-bddd-d046a5f85f0d">zookeeper</span></span></span>]

  [[clusters]]

    [[[default]]]
      # Zookeeper ensemble. Comma separated list of Host/Port.
      # e.g. <span><span id="6979e06d-7fbc-489e-ba5e-86b4004e90ae">localhost</span></span><span><span id="357d26c5-54c8-4921-8a5f-bdadd5a48a3b">:</span></span>2181<span id="ec220840-053c-410b-b2bb-1cb9a28f5e80"><span id="e26dd4e3-730b-4564-8f1f-71fcc7eac3ef">,</span></span><span><span id="fbca68a0-f706-444e-b76b-053dcebbdec8">localhost</span></span><span><span id="55bc3d2c-3995-4b72-aeca-3f6931c435ff">:</span></span>2182<span><span id="6640690b-7e75-40c6-a735-2c638b4217df">,</span></span><span><span id="68289473-624a-480b-bb0d-60c61cd217c4">localhost</span></span><span><span id="234bdc45-265f-4dad-a6dd-b92aaf884a6b">:</span></span>2183
      ## host_ports=localhost<span><span id="3d4b6322-5257-4c44-b8f2-71ab19d897ed">:</span></span>2181

      # The URL of the REST <span id="a688bc16-12dd-4b30-9ed1-90122522ad14"><span id="aa4b6217-856e-4964-9928-e1c53fde240a">contrib</span></span> service
      ## rest_url=http<span><span id="ce3d7153-07d4-412c-b961-af7f6d243565">:</span></span>//<span><span id="e98ba0c4-7952-47ef-96ae-a992e02aa9d9">localhost</span></span><span><span id="5d02a377-9f0d-4c3d-935f-328b8e6c1832">:</span></span>9998</pre>

<span>いよいよです！</span>[ZooKeeper Browser][3]に行ってみましょう！

<p class="p1">
  <span class="s1">ご質問やフィードバックがあれば、<a href="http://groups.google.com/a/cloudera.org/group/hue-user"><span class="s2">hue-user</span></a> や <a href="http://twitter.com/gethue"><span class="s2">@gethue.com</span></a>までお気軽にお尋ね下さい！</span>
</p>

原文：<https://gethue.com/new-zookeeper-browser-app>

 [1]: https://gethue.com/hue-3-and-the-new-sqoop-and-zookeeper-apps-are-out
 [2]: http://zookeeper.apache.org/
 [3]: http://127.0.0.1:8888/zookeeper/