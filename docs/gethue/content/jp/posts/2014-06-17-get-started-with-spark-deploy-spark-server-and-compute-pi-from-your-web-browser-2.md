---
title: 'Sparkを始めましょう: SparkサーバーをデプロイしてブウザからPiを計算する'
author: Hue Team
type: post
date: 2014-06-17T00:00:45+00:00
url: /get-started-with-spark-deploy-spark-server-and-compute-pi-from-your-web-browser-2/
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
sf_custom_excerpt:
  - |
    HueはブラウザからScalaとJavaのジョブを直接サブミットできるSpark Applicationを同梱しています。

    Sparkとやり取りするために、オープンソースのSpark Job Serverを使用します...
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
slide_template:
  - default
categories:
  - Spark
  - Tutorial
  - Video

---
HueはブラウザからScalaとJavaの[ジョブを直接サブミットできる][1][Spark Application][2][を同梱しています。][1]

Sparkとやり取りするために、オープンソースの[Spark Job Server][3]を使用します。 (例: 一覧、Sparkジョブの投入、結果の取得、コンテキストの作成&#8230;)

これは、サービスとしてSpark Job Serverを実行する方法の詳細です。これは、以前[記事][2]で説明したデプロイモードに対して実働環境により適しています。私たちはCDH5.0とSpark 0.9を使用しています。

{{< youtube wU2QcCeBXCg >}}

## サーバーのパッケージとデプロイ

ほとんどの使用方法は[github][4]にあります。

レポジトリをチェックアウトし、プロジェクトをビルドすることによって開始します。（注：Ubuntuを使ってディスクを暗号化している場合、/tmpの構築をする必要があります）。続いてSpark Job Serverのルートディレクトリから:

<pre><code class="bash">mkdir bin/config
cp config/local.sh.template bin/config/settings.sh
</pre>

そして、settings.shのこれら2つの変数を:

<pre><code class="bash">LOG_DIR=/var/log/job-server
SPARK_HOME=/usr/lib/spark (or SPARK_HOME=/opt/cloudera/parcels/CDH/lib/spark)
</pre>

それから全てをパッケージします:

<pre><code class="bash">bin/server_deploy.sh settings.sh
[info] - should return error message if classPath does not match
[info] - should error out if loading garbage jar
[info] - should error out if job validation fails
...
[info] Packaging /tmp/spark-jobserver/job-server/target/spark-job-server.jar ...
[info] Done packaging.
[success] Total time: 149 s, completed Jun 2, 2014 5:15:14 PM
/tmp/job-server /tmp/spark-jobserver
log4j-server.properties
server_start.sh
spark-job-server.jar
/tmp/spark-jobserver
Created distribution at /tmp/job-server/job-server.tar.gz
</pre>

主要なtarbal、tarball `/tmp/job-server/job-server.tar.gz`を持っており、サーバーにコピーする準備ができています。

注:

`server_deploy.sh`で自動的にファイルをコピーすることもできます。

## Spark Job Serverを開始する

それから`job-server.tar.gz`を展開し、サーバーのapplication.confをコピーします。&#8217;master&#8217;が正しいSpark MasterのURLを示していることを確認して下さい。

<pre><code class="bash">scp /tmp/spark-jobserver/./job-server/src/main/resources/application.conf hue@server.com:
</pre>

masterを示すようにapplication.confを編集します:

<pre><code class="bash"># Settings for safe local mode development
spark {
  master = "spark://spark-host:7077"
  …
}
</pre>

これがjobserverフォルダーの内容です:

<pre><code class="bash">ls -l
total 25208
-rw-rw-r-- 1 ubuntu ubuntu     2015 Jun  9 23:05 demo.conf
-rw-rw-r-- 1 ubuntu ubuntu     2563 Jun 11 16:32 gc.out
-rw-rw-r-- 1 ubuntu ubuntu      588 Jun  9 23:05 log4j-server.properties
-rwxrwxr-x 1 ubuntu ubuntu     2020 Jun  9 23:05 server_start.sh
-rw-rw-r-- 1 ubuntu ubuntu      366 Jun  9 23:13 settings.sh
-rw-rw-r-- 1 ubuntu ubuntu 13673788 Jun  9 23:05 spark-job-server.jar
</pre>

注:

[Spark Master Web UI][5]を調査してsparkのURLを得ることもできます。

少なくともひとつのSpark workerがあることも確認します:  `"Workers: 1"`

従来は、Sparkをlocalhostにバインドしようとした時にいくつかの問題がありました (例 spark workerが開始しない)。私たちはspark-env.shにハードコードすることで修正しています:

<pre><code class="bash">sudo vim /etc/spark/conf/spark-env.sh

export STANDALONE_SPARK_MASTER_HOST=spark-host
</pre>

ここでサーバーを開始して、プロセスをバックグラウンドで実行します:

<pre><code class="bash">./server_start.sh</pre>

grepして動作しているかを確認することができます:

<pre><code class="bash">ps -ef | grep 9999

ubuntu   28755     1  2 01:41 pts/0    00:00:11 java -cp /home/ubuntu/spark-server:/home/ubuntu/spark-server/spark-job-server.jar::/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/spark/conf:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/spark/assembly/lib/*:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/spark/examples/lib/*:/etc/hadoop/conf:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/hadoop/*:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/hadoop/../hadoop-hdfs/*:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/hadoop/../hadoop-yarn/*:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/hadoop/../hadoop-mapreduce/*:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/spark/lib/scala-library.jar:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/spark/lib/scala-compiler.jar:/opt/cloudera/parcels/CDH-5.0.0-1.cdh5.0.0.p0.47/lib/spark/lib/jline.jar -XX:+UseConcMarkSweepGC -verbose:gc -XX:+PrintGCTimeStamps -Xloggc:/home/ubuntu/spark-server/gc.out -XX:MaxPermSize=512m -XX:+CMSClassUnloadingEnabled -Xmx5g -XX:MaxDirectMemorySize=512M -XX:+HeapDumpOnOutOfMemoryError -Djava.net.preferIPv4Stack=true -Dcom.sun.management.jmxremote.port=9999 -Dcom.sun.manage
</pre>

これだけです！

## Piのサンプルを実行する!

Spark Job Serverは、一つの[コマンド][6]ドでビルドできるいくつかの[例][7]を備えています。Pi ジョブを実行しましょう。

<http://hue:8888/spark>でSpark Appをオープンし、applicationタブに移動して`job-server-tests-0.3.x.jar`をアップロードします。

ここでエディタにて、この実行するクラス`spark.jobserver.LongPiJob`を指定し、実行します！

Spark MasterのUIでもSparkアプリケーションが実行していることがわかるでしょう。長時間実行しているアプリケーションを取得したい場合、コンテキストを作成し、その後このコンテキストをエディタでアプリケーションに割り当てます。

[<img class="aligncenter  wp-image-1456" src="https://cdn.gethue.com/uploads/2014/06/spark-master-ui.png" alt="spark-master-ui" width="817" height="450" data-wp-pid="1456" />][8]

&nbsp;

## まとめ

これはThis is how we setup the Spark Server on [demo.gethue.com/spark][9]でSpark Serverをどのようにセットアップするかを示しています。いつものように、コメントは[hue-user][10]メーリングリストや[@gethue][11]までお気軽に！

Happy Sparking!

PS: [Hue][12] or [Job Server][13] talks at the upcoming [Spark Summit][14]でのhueまたはJob Serverのセッションでお会いできることを楽しみにしています!

 [1]: http://spark.apache.org/
 [2]: https://gethue.com/a-new-spark-web-ui-spark-app/
 [3]: https://github.com/ooyala/spark-jobserver
 [4]: https://github.com/ooyala/spark-jobserver#deployment
 [5]: http://localhost:8080/
 [6]: https://github.com/ooyala/spark-jobserver#wordcountexample-walk-through
 [7]: https://github.com/ooyala/spark-jobserver/tree/master/job-server-tests/src/spark.jobserver
 [8]: https://cdn.gethue.com/uploads/2014/06/spark-master-ui.png
 [9]: http://demo.gethue.com/spark/
 [10]: http://groups.google.com/a/cloudera.org/group/hue-user
 [11]: https://twitter.com/gethue
 [12]: https://spark-summit.org/2014/talk/a-web-application-for-interactive-data-analysis-with-spark
 [13]: https://spark-summit.org/2014/talk/spark-job-server-easy-spark-job-management
 [14]: http://spark-summit.org/2014
