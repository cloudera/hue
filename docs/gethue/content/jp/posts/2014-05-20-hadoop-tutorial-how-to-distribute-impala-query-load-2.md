---
title: 'Impala 高可用性: Impalaクエリのロードを分散する方法'
author: Hue Team
type: post
date: 2014-05-20T03:34:48+00:00
url: /hadoop-tutorial-how-to-distribute-impala-query-load-2/
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
  - Hueは、Hadoopの次世代SQLエンジンであるImpala用のインタフェースを提供しています。さらなるパフォーマンスを提供するために、HueはImpalaのワーカーの全てに渡ってクエリのロードを分散することができます。
categories:
  - Impala
  - Video

---
Hueは、Hadoopの次世代SQLエンジンである[Impala][1]用の[インタフェース][2]を提供しています。さらなるパフォーマンスを提供するために、HueはImpalaのワーカーの全てに渡ってクエリのロードを分散することができます。

# チュートリアル

このチュートリアルでは、複数のImpalad（Impalaデーモン）にクエリを行うためにHueをセットアップする方法を説明します:

  1. 複数のImpaladで動作するように、4ノードのRed Hat 6クラスタのうちの一つのノードにHue 3.6を設定します。
  2. [HAProxy 1.4][3]を使用してimpaladへの接続をロードバランスを行いますが、接続の持続が行える、どのようなロードバランサーでも動作するでしょう。

これは、Hueが複数のImpaladとどのように通信するのかを紹介した簡単なビデオです。

{{< youtube p-pwhqGvlE4 >}}

## Hueを設定する

複数のImpaladと通信するためにHueを設定する、2つの方法があります。

### Cloudera Managerによる設定

（Cloudera Managerを日本語でセットアップしている場合には、適宜読み替えて下さい）

  1. Cloudera Managerから、メニューの“Clusters”をクリックして、Hueサービスを探します。

    [<img class="alignnone  wp-image-1228" src="https://cdn.gethue.com/uploads/2014/05/impala-1.png" alt="impala-1" width="657" height="556" data-wp-pid="1228" />][4]
  2. Hueサービスから、 “Configuration -> View and Edit”を選択します。

    [<img class="alignnone  wp-image-1227" src="https://cdn.gethue.com/uploads/2014/05/impala-2.png" alt="impala-2" width="292" height="165" data-wp-pid="1227" />][5]
  3. 適切なロードバランサーとソケットのタイムアウトを使用するために、Cloudera Managerで安全バルブ（safety valve)の設定を行う必要があります。“Service-Wide -> Advanced” に移動し、“Hue Service Advanced Configuration Snippet (Safety Valve)”の値をクリックします。値には、以下をテンプレートとして利用することができます: <pre><code class="bash">[impala]
server_host=&lt;hostname running HAProxy&gt;
server_port=&lt;port HAProxy is bound to&gt;
server_conn_timeout=&lt;timeout in seconds&gt;
</pre>

&nbsp;

Cloudera ManagerでHueを設定するためのより多くの情報は、[Managing Clusters][6]をご覧下さい（英語）。

### 手動での設定

  1. お好みのエディタで/etc/hue/hue.iniを開きます。
  2. &#8220;impala&#8221;セクションの下にある“server\_conn\_timeout”設定を大きな値（例：1時間）に変更します。この値は秒単位で設定しなければなりません（1時間 = 3600秒）。設定オプションは「Cloudera Managerによる設定」も参照して下さい。

    [<img class="alignnone  wp-image-1229" src="https://cdn.gethue.com/uploads/2014/05/impala-3.png" alt="impala-3" width="492" height="405" data-wp-pid="1229" />][7]
  3. 次に、hue.iniの&#8221;impala&#8221;セクションで、新しいホストとポートをセットしなければなりません。ホスト名は &#8220;server\_host&#8221;に、ポートは &#8220;server\_port&#8221; に定義されています。設定オプションは「Cloudera Managerによる設定」も参照して下さい。

&nbsp;

## HA Proxy のインストールと設定

  1. [HA Proxy 1.4][3]の[バイナリ形式のファイル][8]をダウンロードして展開します。
  2. 以下の[HA Proxy configuration][9]を/etc/impala/haproxy-impala.confに設定します:

<pre><code class="bash">global
  daemon
  nbproc 1
  maxconn 100000
  log /dev/log local6

defaults
  log        global
  mode       tcp
  option     tcplog
  option     tcpka
  timeout connect 3600000ms
  timeout client 3600000ms
  timeout server 3600000ms

listen impala
  bind 0.0.0.0:10001
  balance leastconn

  server impala1 server1.cloudera.com:21050 check
  server impala2 server2.cloudera.com:21050 check
  server impala3 server3.cloudera.com:21050 check
</pre>

3. HA Proxyを開始します:

<pre><code class="bash">haproxy -f /etc/impala/haproxy-impala.conf</pre>

&nbsp;

鍵となる設定オプションは、[**listen**][10] セクションの[**balance**][11] と [**server**][12] です。**[defaults][13]**セクションの **[timeout][14]** 設定オプションもです。**balance**パラメータを**leastconn**にセットすると、Hueは最小コネクション数でimpaladが新しい接続を作成することを保証します。**server**パラメータには、以下の形式で、ロードバランシング時にどのサーバーが使用されるかを定義します:

&nbsp;

<pre><code class="bash">server &lt;name&gt; &lt;address&gt;[:port] [settings ...]</pre>

&nbsp;

上記の設定では、&#8221;impala1&#8243;サーバーは“impala1.cloudera.com:21050”、&#8221;impala2&#8243;サーバーは“impala2.cloudera.com:21050”、&#8221;impala3&#8243;サーバーは“impala3.cloudera.com:21050”でそれぞれ利用可能です。**timeout**設定パラメータは、TCP接続が（両側で）どのぐらい生きていなければならないのかを定義します。この例では、クライアントのタイムアウト、サーバーのタイムアウト、接続タイムアウトは全て1時間に設定されています。

&nbsp;

HA Proxy“0.0.0.0:10001”にバインドするように設定されています。従って、Hueは少なくとも利用するImpaladの一つを透過的に選ぶ HA Proxyを示すことができるようになっています。

&nbsp;

&nbsp;

# まとめ

Impalaのクエリのロードバランシングは、負荷を全てのImpalad（例えば、最終結果の集約を行う）に分散します。現在のImpaladの設計では「不揮発」のネットワーク接続が必要とされるので、Hueは接続を永続的できます。私たちは、これが多くのHadoopクラスタに役立つことを願っています!

&nbsp;

何か提案はございますか? ご意見は [hue-user][15] または [@gethue][16] までお気軽にお知らせ下さい。

 [1]: http://impala.io/
 [2]: https://gethue.com/hadoop%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%A9%E3%82%AF%E3%83%86%E3%82%A3%E3%83%96sql%E3%81%8C%E7%B0%A1%E5%8D%98%E3%81%AB/?lang=ja
 [3]: http://haproxy.1wt.eu/
 [4]: https://cdn.gethue.com/uploads/2014/05/impala-1.png
 [5]: https://cdn.gethue.com/uploads/2014/05/impala-2.png
 [6]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Managing-Clusters/cm5mc_hue_service.html
 [7]: https://cdn.gethue.com/uploads/2014/05/impala-3.png
 [8]: http://haproxy.1wt.eu/download/1.4/src/haproxy-1.4.24.tar.gz
 [9]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html
 [10]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4
 [11]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-balance
 [12]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-server
 [13]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#3
 [14]: http://cbonte.github.io/haproxy-dconv/configuration-1.4.html#4-timeout
 [15]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
 [16]: https://twitter.com/gethue
