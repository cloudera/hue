---
title: Hadoopチュートリアル シーズンII：7. SolrでYelpデータをインデックス、検索する方法
author: Hue Team
type: post
date: 2013-11-04T23:59:25+00:00
url: /hadoopチュートリアル-シーズンii：7-solrでyelpデータをインデ/
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
  - 以前のエピソードでは、HBaseでPigとHiveを使用する方法を見てきました。今回は、Hue Search appがインデキシングによりYelpデータを検索できるようにするためにはどう...
categories:
  - Full tutorial
  - Search
  - Tutorial
  - Video

---
（[原文][1]）

<p id="docs-internal-guid-6e44f291-2156-8489-431b-b515176c9fec">
  <span>以前のエピソードでは、</span><span><a href="https://gethue.com/hadoop-tutorial-use-pig-and-hive-with-hbase">HBaseでPigとHive</a>を</span>使用する方法を見てきました。今回は、<a href="https://gethue.com/tutorial-search-hadoop-in-hue">Hue Search app</a>がインデキシングによりYelpデータを検索できるようにするためにはどうするのか、カスタマイズ可能なユーザーインタフェースを構築するにはどうすれば良いのかについて見ていきます。
</p>

&nbsp;

{{< youtube ATldKiiJdqY >}}

&nbsp;

# <span>Solrにインデキシングデータを入れる</span>

&nbsp;

このチュートリアルは[SolrCloud][2]に基づいています。これはSolrCloudのインストールと、必要となる[パッケージ][3]リストについてのステップバイステップ[ガイド][3]です：

  * <span><span>solr</span>-server</span>
  * <span><span>solr</span>&#8211;<span>mapreduce</span></span>
  * <span><span>search</span></span>

&nbsp;

次の手順はSolr Cloudのデプロイと設定についてです。[ドキュメント][4]に従いっていきます。

&nbsp;

このあと、新しいコレクションと「reviews」という名前のインデックスを[作成][5]します。[Hadoop tutorial ][6][github][6]からコピーしておく必要がある、事前に定義されたスキーマを使用します。.

&nbsp;

<pre class="code"><span>cp</span> solr_local/conf/schema.xml solr_configs/conf/schema.xml

<span>solrctl</span> <span>instancedir</span> --create reviews solr_local

<span>solrctl</span> collection --create reviews -s 1</pre>

Yelpデータに対応するようにマッピングして、[スキーマ][7]にあるフィールドの定義を置き換えます。スキーマは、検索インデックスで利用可能なそれぞれのデータフィールドを表しています。schema.xmlについての詳細は[Solr wiki][8]を読んで下さい。

<pre class="code">&lt;<span>field</span> name="business_id" type="text_en" indexed="true" stored="true" /&gt;  
  &lt;<span>field</span> name="cool" type="tint" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="date" type="text_en" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="funny" type="tint" indexed="true" stored="true" /&gt;
  &lt;field name="id" type="string" indexed="true" stored="true" required="true" multiValued="false" /&gt;  
  &lt;<span>field</span> name="stars" type="tint" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="text" type="text_en" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="type" type="text_en" indexed="true" stored="true" /&gt;         
  &lt;<span>field</span> name="useful" type="tint" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="user_id" type="text_en" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="name" type="text_en" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="full_address" type="text_en" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="latitude" type="<span>tfloat</span>" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="longitude" type="<span>tfloat</span>" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="neighborhoods" type="text_en" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="open" type="text_en" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="review_count" type="tint" indexed="true" stored="true" /&gt;
  &lt;<span>field</span> name="state" type="text_en" indexed="true" stored="true" /&gt;</pre>

続いて[Hiveのクエリ][9]でYelpデータのサブセットを取り出してきれいにし、CSVとしてダウンロードして、[インデクサツール][10]とこの[コマンド][11]でよりインデックスします：:

<pre class="code"><span>hadoop</span> jar /usr/lib/<span>solr</span>/contrib/<span>mr</span>/search-<span>mr</span>-*-job<span>.</span>jar org<span>.</span>apache<span>.</span><span>solr</span><span>.</span><span>hadoop</span><span>.</span>MapReduceIndexerTool -D '<span>mapred</span><span>.</span>child<span>.</span><span>java</span><span>.</span>opts=-Xmx500m' --log4j /usr/share/doc/search*/examples/solr-nrt/log4j.properties --<span>morphline</span>-file solr_local/reviews<span>.</span><span>conf</span> --output-<span>dir</span> <span>hdfs</span><span>:</span>//<span>localhost</span><span>:</span>8020/tmp/load --verbose --go-live --<span>zk</span>-host <span>localhost</span><span>:</span>2181/<span>solr</span> --collection reviews <span>hdfs</span><span>:</span>//<span>localhost</span><span>:</span>8020/tmp/query_result.csv</pre>

コマンドは、Yelpデータをインデックスのschema.xmlに定義されたフィールドにマップするために、[morphlineファイル][12]を使用します。

<span>morphlineをデバッグするには &#8211;dry-runオプションがいつの日か役立つでしょう。</span>

&nbsp;

# <span>検索結果をカスタマイズする</span>

管理パネルでは、検索ページの見た目と機能の調整ができます。これはビデオの2番目のパートで説明されています。

&nbsp;

# <span>まとめ</span>

Cloudera Searchはあなたのユーザー基盤をHadoopに解放し、素早くデータの検索を行うために素晴らしいものです。その他のいくつかの記事では、[メール][13]や[顧客データ][14]の検索のような、いくつかの良いユーザー事例が述べられています。

Cloudera Morphline も、データのインデキシングを簡単にするための興味深いツールです。Morphlineについての詳細は、[プロジェクトのウェブサイト][15]で学ぶことができます。

いつものように、何かあれば[hue-user][16]メーリングリスト（英語）や、[@gethue][17]に気軽にコメントして下さい！

&nbsp;

# <span>トラブルシューティング</span>

1. このエラーをご覧になった場合：

<pre class="code">org.apache.solr.client.solrj.impl.HttpSolrServer$RemoteSolrException:Error CREATEing SolrCore ‘reviews_shard1_replica1’: Unable to create core: reviews_shard1_replica1 Caused by: Could not find configName for collection reviews found:null</pre>

<span>コレクションを作るのを忘れているのかもしれません:</span>

<pre class="code"><span>solrctl</span> <span>instancedir</span> --create review solr_configs

</pre>

<span>2. このエラーをご覧になった場合:</span>

<pre class="code">ERROR - 2013-10-10 20:01:21.383; org<span>.</span>apache<span>.</span><span>solr</span><span>.</span>servlet<span>.</span>SolrDispatchFilter; Could not start Solr. Check <span>solr</span>/home property and the logs
ERROR - 2013-10-10 20:01:21.409; org.apache.solr.common.SolrException; null:org.apache.solr.common.SolrException: solr.xml not found in ZooKeeper
       <span>at</span> org<span>.</span>apache<span>.</span><span>solr</span><span>.</span>core<span>.</span>ConfigSolr<span>.</span><span>fromSolrHome</span><span>(</span>ConfigSolr.java<span>:</span>109)
<span>Server</span> is shutting down</pre>

<span>Solrに設定の再読み込みを強制する必要があるかもしれません。これはZooKeeperを壊してしまうかもしれず、3番目のエラーを読む必要があるかもしれないことに注意して下さい。</span>

&nbsp;

<span>3. このエラーをご覧になった場合:</span>

<pre class="code"><span>KeeperErrorCode</span> = NoNode for /overseer/collection-queue-work&lt;/<span>str</span>&gt;
&lt;<span>str</span> name="trace"&gt;
<span>org</span><span>.</span>apache<span>.</span><span>zookeeper</span><span>.</span>KeeperException$NoNodeException: KeeperErrorCode = NoNode for /overseer/collection-queue-work</pre>

&nbsp;

<span>これは2番目のエラーから来ているのかもしれません。設定を再アップロードし、コレクションを再作成する必要があるかもしれません。</span>

 [1]: https://gethue.com/hadoop-tutorials-season-ii-7-how-to-index-and-search
 [2]: http://wiki.apache.org/solr/SolrCloud
 [3]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-Installation-Guide/csig_install_search.html
 [4]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-Installation-Guide/csig_deploy_search_solrcloud.html
 [5]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-Installation-Guide/csig_runtime_solr_config.html
 [6]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/solr-local-search
 [7]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/solr_local/conf/schema.xml#L109
 [8]: http://wiki.apache.org/solr/SchemaXml
 [9]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/data_subset.sql
 [10]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-User-Guide/csug_batch_index_to_solr_servers_using_golive.html
 [11]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/load_index.sh
 [12]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/solr-local-search/solr_local/reviews.conf
 [13]: http://blog.cloudera.com/blog/2013/09/email-indexing-using-cloudera-search/
 [14]: http://blog.cloudera.com/blog/2013/09/secrets-of-cloudera-support-impala-and-search-make-the-customer-experience-even-better/
 [15]: http://cloudera.github.io/cdk/docs/current/cdk-morphlines/index.html
 [16]: http://groups.google.com/a/cloudera.org/group/hue-user
 [17]: https://twitter.com/gethue