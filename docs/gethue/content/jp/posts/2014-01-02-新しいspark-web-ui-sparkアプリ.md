---
title: '新しいSpark Web UI: Sparkアプリ'
author: Hue Team
type: post
date: 2014-01-02T23:59:37+00:00
url: /新しいspark-web-ui-sparkアプリ/
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
slide_template:
  - default
sf_custom_excerpt:
  - |
    Sparkの開発者の皆様!
    最近HueのSparkアプリケーションが作成されました。これはユーザーがブラウザから直接Sparkジョブの実行と監視...
categories:
  - Spark
  - Tutorial
  - Video

---
<p id="docs-internal-guid-4f124dbc-533c-5aa9-5a99-e29bb3080ee2">
  <span>Sparkの開発者の皆様!</span>
</p>

<span>最近<a href="https://gethue.com/">Hue</a>のSparkアプリケーションが作成されました。これはユーザーがブラウザから直接</span><span><a href="http://spark.incubator.apache.org/">Spark</a>ジョブの実行と監視ができ、より生産的になります。</span><span><br /> </span>

<span>以前Oozieの<a href="https://dl.dropboxusercontent.com/u/730827/cloudera/spark-app.png">バックエンド</a>でサブミットするアプリをリリースしましたが、最近の<a href="http://spark-summit.org/talk/chan-the-spark-job-server/">Spark Summit</a>で<a href="http://www.ooyala.com/">Ooyala</a>と<a href="https://github.com/velvia">Evan</a>のチームによってコントリビュートされた、Spark Job Server</span><span> (</span>[<span>SPARK-818</span>][1]<span>) に変更しました。この新しいサーバーはSparkとの実際の双方向性を有効にし、コミュニティに近づいています。</span>

{{< youtube lWKxtvUMcGw >}}

[<span> </span>][2]

私たちはコミュニティと一緒に作業して、将来的にPython、Javaのサポート、コンパイル／アップロードなく直接ジョブをサブミット、その他の改善ができることを願っています!

<span>いつものように、コメントがあれば</span>[<span> </span><span>hue-user</span>][3]<span> リストあるいは</span><span><a href="https://twitter.com/gethue"> </a></span><span><a href="https://twitter.com/gethue">@gethue</a>まで</span><span>!Job Serverに直接関する質問については、<a href="https://spark-project.atlassian.net/browse/SPARK-818">SPARK-818</a>の<a href="https://github.com/apache/incubator-spark/pull/222">pull request</a>に参加するかSparkの<a href="http://spark.incubator.apache.org/mailing-lists.html">メーリングリスト</a>まで!</span>

## <span>始めましょう!</span>

<span>現在、Scalaジョブのみがサポートされており、プログラムはこの</span><span><a href="https://github.com/ooyala/incubator-spark/blob/jobserver-preview-2013-12/jobserver/src/main/scala/spark.jobserver/SparkJob.scala#L6">トレイト</a>を実装してjarにパッケージする必要があります。これが</span><span><a href="https://github.com/ooyala/incubator-spark/blob/jobserver-preview-2013-12/jobserver/src/test/scala/spark.jobserver/WordCountExample.scala#L16">WordCount</a>の例です。Spark Job Serverについて学習するには</span><span><a href="https://github.com/ooyala/incubator-spark/tree/jobserver-preview-2013-12/jobserver#features">README</a>を確認して下さい。</span><span><br /> </span>

## <span>要件</span>

<span>システムには</span><span><a href="http://www.scala-lang.org/">Scala</a>がインストールされていると仮定しています。</span>

## <span>Spark Job Serverを取得する</span>

<span>現在githubのこの</span>[branch][4]にあります:

<pre class="code">git clone https://github.com/ooyala/incubator-spark.git spark-server
cd spark-server
git checkout -b jobserver-preview-2013-12 origin/jobserver-preview-2013-12</pre>

<span>それからこのように入力します:</span>

<pre class="code">sbt/sbt
project jobserver
re-start</pre>

## <span>Hueを取得する</span>

<span>現在githubのみにあります (CDH5b2に含まれる予定です):</span>

[<span>https://github.com/cloudera/hue#getting-started</span>][5]

<span>HueとSpark Job Serverが同じマシンにない場合、desktop/conf/pseudo-distributed.iniにある</span><span><a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini">hue.ini</a>のプロパティを更新します</span><span>:</span>

<pre class="code">[spark]
  # URL of the Spark Job Server.
  server_url=http://localhost:8090/</pre>

## <span>実行するためにSparkのサンプルを取得する</span>

<span>その後、このThen follow this </span>[<span>手順（ウォークスルー）</span>][6]<span> に従い、ビデオのデモで使用しているサンプルのjarを作成します。</span>

 [1]: https://spark-project.atlassian.net/browse/SPARK-818
 [2]: https://www.youtube.com/watch?v=lWKxtvUMcGw
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://github.com/ooyala/incubator-spark/commits/jobserver-preview-2013-12
 [5]: https://github.com/cloudera/hue#getting-started
 [6]: https://github.com/ooyala/incubator-spark/tree/jobserver-preview-2013-12/jobserver#wordcountexample-walk-through