---
title: 'Hadoopチュートリアル: HiveServer2とSentryでHiveクエリエディタ'
author: Hue Team
type: post
date: 2013-10-24T23:59:24+00:00
url: /hadoopチュートリアル-hiveserver2とsentryでhiveクエリエディタ/
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
  - HueはHiveクエリをサブミットするためのウェブインタフェースを提供しています。HueはHiveクエリをサービスするための独自サーバー、Beeswaxを...
categories:
  - Hive
  - Tutorial
  - Video

---
（[原文][1]）

HueはHiveクエリをサブミットするためのウェブインタフェースを提供しています。HueはHiveクエリをサービスするための独自サーバー、Beeswaxを持っていました。Hue2.5では、より洗練され強力なサービス、Apache [HiveServer2][2]がサポートされています。

# <span>Beeswax Hiveエディタ</span>

HiveServer2の統合により、Hueは[Sentry][3]の恩恵を得ていることに感謝します。[セキュリティ][3]が提供されることに加え、Hueのインタフェースはより強固になりました。例えば、データベースやテーブルの権限がないユーザーは、クエリエディタや[メタストアアプリ][4]でそれらを見ることができなくなります。

HiveServer2も[メタストア][4]への効率的なアクセスを提供します。

この一番上にあるBeeswax Hive UIは、生産性を向上するウェブエディタです:

  * <span>構文のハイライトと自動補完</span>
  * <span>いくつかのクエリをサブミットし、後から進捗を確認</span>
  * <span><a href="https://gethue.com/hadoop-tutorial-hive-udf-in-1-minute">UDF</a>の統合</span>
  * <span>多数のクエリ実行</span>
  * <span>クエリの一部分を選択して送信</span>
  * <span>クエリ結果のダウンロードと保存</span>
  * <span>メタデータを通してナビゲート</span>

ビデオは近日公開します！

## <span>Hue 2<span>.</span>x</span>

私たちはHueの最新バージョン(2.5)の使用を推奨しています。 [hue.ini][5]のBeeswaxセクションを更新し、HueがHiveServer2を指すようにします。:

<pre>[<span>beeswax</span>]
  beeswax_server_host=&lt;FQDN of Beeswax server&gt;
  server_interface=hiveserver2
  beeswax_server_port=10000</pre>

## Hue 3<span>.</span>x

Hue 3では、もうBeeswaxdをバンドルしておらず、デフォルトでHiveServer2を使うように設定されています。HiveServer2がHueと同じマシンではない場合、[hue<span>.</span>ini][6]を下記のように更新します:

<pre>[<span>beeswax</span>]
 hive_server_host=&lt;FQDN of HiveServer2&gt;</pre>

他のHive固有の設定（例：セキュリティ、impersonation：なりすまし）は、ローカルの[/etc/hive/conf/hive-site.xml][7]から読み込みます。私たちは、元のHiveの設定と確実に同期され続ける（あるいは、HueとHiveを同じマシンに配置する）ことを推奨しています。

# <span>トラブルシューティング</span>

<pre><span>AuthorizationException</span>: User 'hue/test.com' does not have privileges to execute 'CREATE' on: default<span>.</span>sample_08"</pre>

‘hue’ユーザーはSentryで設定されておらず、CREATE tableの権限を持っていません。（以下で説明する）impersonationは、Sentryの場合には素晴らしいということに気づくでしょう。impersonationのユーザー権限（例: &#8216;bob&#8217;）が、&#8217;hue&#8217;ユーザーの１人の代わりに使用されるようになります。

<pre><span>org</span><span>.</span>apache<span>.</span>hive<span>.</span>service<span>.</span><span>cli</span><span>.</span>HiveSQLException: Error while processing statement: FAILED: Execution Error, return code 1 from org<span>.</span>apache<span>.</span><span>hadoop</span><span>.</span>hive<span>.</span><span>ql</span><span>.</span>exec<span>.</span>DDLTask. <span>MetaException</span><span>(</span>message<span>:</span>Got exception: org<span>.</span>apache<span>.</span><span>hadoop</span><span>.</span>security<span>.</span>AccessControlException Permission denied: user=hive, access=WRITE, inode="/user/test/data"<span>:</span>test<span>:</span>supergroup<span>:</span>drwxr-xr-x</pre>

デフォルトでHiveServer2は、現在、Hiveのwarehouse（デフォルトで&#8217;/user/hive/warehouse&#8217;）を所有しており、データファイルは&#8217;hive&#8217;ユーザーに属している必要があることを意味しています。テーブルの作成時にこのエラーが生じた場合は、データディレクトリ（ここでは/user/test/data）のパーミッションを全員が’書き込める’ようにするか、ユーザーをimpersonateすることを&#8217;hive&#8217;に許可を与えることで、HiveServer2を古いBeeswaxの振る舞いに戻します。

Hadoopの[proxy user][8]として&#8217;hive&#8217;を追加し、hive-site.xmlを編集します:

<pre>&lt;<span>property</span>&gt;
   &lt;<span>name</span>&gt;hive<span>.</span>server2<span>.</span>enable<span>.</span><span>doAs</span>&lt;/name&gt;
   &lt;<span>value</span>&gt;true&lt;/value&gt;
 &lt;/<span>property</span>&gt;</pre>

その後HiveServer2をリスタートします:

<pre><span>sudo</span> service hive-server2 restart</pre>

その他のYARNを使用しているときの一般的なエラー:

<pre>Cannot initialize Cluster. Please check your configuration for <span>mapreduce</span><span>.</span>framework<span>.</span>name and the correspond server addresses.</pre>

これはHADOOP\_MAPRED\_HOME環境変数が設定されていません:

<pre><span>export</span> HADOOP_MAPRED_HOME=/usr/lib/<span>hadoop</span>-<span>mapreduce</span></pre>

HADOOP_HOMEも間違っています。

<pre><span>TTransportException</span><span>(</span>'Could not start SASL: Error in sasl_client_start (-4) SASL<span>(</span>-4): no mechanism available: No worthy mechs found',)</pre>

Hueにはシステムの [SASL lib][9] が欠けています。

HiveServer2は3つの認証モードをサポートしています:

  * NOSASL
  * NONE (デフォルト)
  * KERBEROS

NOSASLのみがSASLを必要としないので、これに切り替えるか足りないパッケージをインストールするかのどちらかです。

# まとめ

Hue は非常に使いやすいユーザーインタフェースでHiveクエリを実行するための素晴らしい環境を提供しています。Beeswaxdは素晴らしいサービスでしたが、HiveServer2が好まれており、廃止される可能性があります。HiveServer2はより安定性とセキュリティを提供しています。

追記として、あなたがもっと速いSQLクエリを探しているなら、[Impala Editor][10]をテストすることをお勧めします！

ご質問やフィードバックがあれば、[hue][11][-user][11] や [@gethue.com][12]までお気軽にお尋ね下さい！

 [1]: https://gethue.com/hadoop-tutorial-hive-query-editor-with-hiveserver2-and
 [2]: http://blog.cloudera.com/blog/2013/07/how-hiveserver2-brings-security-and-concurrency-to-apache-hive/
 [3]: http://cloudera.com/content/cloudera/en/campaign/introducing-sentry.html
 [4]: https://gethue.tumblr.com/tagged/metastore
 [5]: https://github.com/cloudera/hue/blob/branch-2.5.1/desktop/conf.dist/hue.ini#L384
 [6]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L438
 [7]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L450
 [8]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Security-Guide/cdh4sg_topic_9_1.html?scroll=topic_9_1_3_unique_1__title_140_unique_1
 [9]: https://github.com/cloudera/hue#development-prerequisites
 [10]: https://gethue.com/fast-sql-with-the-impala-query-editor
 [11]: http://groups.google.com/a/cloudera.org/group/hue-user
 [12]: http://twitter.com/gethue