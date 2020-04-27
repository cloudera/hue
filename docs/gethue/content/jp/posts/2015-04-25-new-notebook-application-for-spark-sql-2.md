---
title: Spark＆SQLのための、新しいノートブックアプリケーションのベータ版
author: Hue Team
type: post
date: 2015-04-25T02:18:38+00:00
url: /new-notebook-application-for-spark-sql-2/
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
sf_custom_excerpt:
  - 昨年、私たちは開発者がウェブインタフェースを介してSparkジョブを投入することができるSpark Igniterをリリースしました 。このアプローチが動作している間、UXが望まれたために多くを残しました。プログラムではインタフェースを実装する必要があり、事前にコンパイルされていなければならず、YARNのサポートが欠けていました。私たちは、REPLを使用するのと同様の、対話形式で反復型のプログラミングの経験を提供することにフォーカスし、PythonとScalaのサポートも追加したいと考えていました。
categories:
  - Hive
  - Hue 3.8
  - Impala
  - Spark

---
昨年、私たちは開発者がウェブインタフェースを介してSparkジョブを投入することができる[Spark Igniter][1]をリリースしました 。このアプローチが動作している間、UXが望まれたために多くを残しました。プログラムではインタフェースを実装する必要があり、事前にコンパイルされていなければならず、YARNのサポートが欠けていました。私たちは、REPLを使用するのと同様の、対話形式で反復型のプログラミングの経験を提供することにフォーカスし、PythonとScalaのサポートも追加したいと考えていました。 [<img class="aligncenter size-large wp-image-2565" src="https://cdn.gethue.com/uploads/2015/04/notebook-1-1024x572.png" alt="notebook-1" width="1024" height="572" data-wp-pid="2565" />][2]  このため、私たちはこれらの不足している機能を提供することができる[Spark REST Job Server][3]の開発を新たに始めました。その上に、私たちはPythonのNotebookのような雰囲気を提供するためのUIを刷新しました。

この新しいアプリケーションはかなり新しく、「ベータ版」として位置付けされていることにご注意ください。これは、それを試して貢献するのをお勧めすることを意味していますが、UXが多く進化していくため、その使用はまだ正式にはサポートされていません！

この投稿は、Webアプリケーションの一部を説明しています。私たちは[Spark 1.3][4]と[Hue マスターブランチ][5]を使用しています   {{< youtube kIXBL7u_NOk >}}

これは、以下の新しい機能をベースにしています：

  * [Spark REST Job Server][3]
  * Notebook Web UI

サポート:

  * Scala
  * Python
  * Java
  * SQL
  * YARN

Sparkアプリが「エディタ」メニューに表示されていない場合は、[hue.ini][6]から非ブラックリストする必要があります ：

<pre><code class="bash">[desktop]
app_blacklist=
</pre>

Hueと同じマシンでHueホームに移動します。

&nbsp;

パッケージを使用してインストールしている場合:

<pre><code class="bash">cd /usr/lib/hue</pre>

&nbsp;

Cloudera Managerを使用している場合:

<pre><code class="bash">cd /opt/cloudera/parcels/CDH/lib/
HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id
echo $HUE_CONF_DIR
export HUE_CONF_DIR
</pre>

そして[Spark Job Server][3]を起動します:

<pre><code class="bash">./build/env/bin/hue livy_server</pre>

hue.iniでこれらのプロパティを変更することで、セットアップをカスタマイズできます:

<pre><code class="bash">[spark]
# URL of the REST Spark Job Server.
server_url=http://localhost:8090/

# List of available types of snippets
languages='[{"name": "Scala", "type": "scala"},{"name": "Python", "type": "python"},{"name": "Impala SQL", "type": "impala"},{"name": "Hive SQL", "type": "hive"},{"name": "Text", "type": "text"}]'

# Uncomment to use the YARN mode
## livy_server_session_kind=yarn
</pre>

**さて、次は！**

このベータ版は良い機能セットをもたらし、より多くが[予定されています][7] 。長期的には、すべてのクエリエディタ（例えばPig、DBquery、Pheonix&#8230;）がこの共通インターフェースを使用することを期待しています。その後、ビジュアルダッシュボードを作るために、個々のスニペットはドラッグ＆ドロップできるようになり、ノートブックはDropboxやGoogle docsのように埋め込むことができるようになるかもしれません。

私たちは、新しい[Spark REST Job Server][3]のフィードバックをいただくことにも関心があり、コミュニティがこれについてどのように考えているかを見ています （貢献を歓迎します;）

いつものように、コメントとフィードバックは [hue-user][8] メーリングリストや[@gethue][9]までお気軽に！

 [1]: https://gethue.com/%E6%96%B0%E3%81%97%E3%81%84spark-web-ui-spark%E3%82%A2%E3%83%97%E3%83%AA/?lang=ja
 [2]: https://cdn.gethue.com/uploads/2015/04/notebook-1.png
 [3]: https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server
 [4]: https://spark.apache.org/releases/spark-release-1-3-0.html
 [5]: https://github.com/cloudera/hue
 [6]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [7]: https://issues.cloudera.org/browse/HUE-2637
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user
 [9]: https://www.google.com/url?q=https%3A%2F%2Ftwitter.com%2Fgethue&sa=D&sntz=1&usg=AFQjCNFSK0PmjkpMhs1SAQLUx4hheDzfmA