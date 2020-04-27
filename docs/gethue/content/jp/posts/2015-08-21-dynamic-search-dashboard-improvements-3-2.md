---
title: 動的検索ダッシュボードの改善！
author: Hue Team
type: post
date: 2015-08-21T13:02:47+00:00
url: /dynamic-search-dashboard-improvements-3-2/
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
  - ApacheのSolrが使いやすくなっています！検索アプリの新しいバージョンでは、変更されたウィジェットのみの更新とライブインデキシングとのより良い統合により、全体的に改良されたダッシュボードのエクスペリエンスを提供しています。追加された一連の新しい機能を以下に詳しく説明しましょう。
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
categories:
  - Hue 3.9
  - Search
  - Tutorial
  - Video

---
[ApacheのSolr][1]が使いやすくなっています！検索アプリの新しいバージョンでは、変更されたウィジェットのみの更新とライブインデキシングとのより良い統合により、全体的に改良されたダッシュボードのエクスペリエンスを提供しています。追加された一連の新しい機能を以下に詳しく説明しましょう。

ビデオのデモ中にあるアクション、[SearchとSparkノートブックでベイエリアのBikeShareデータを解析][2]の記事、[SearchとSpark Streamingでリアルタイムの分析ダッシュボードを構築する][3]の記事で全てをご覧ください！

&nbsp;

{{< youtube P4uhBLDKbZ0 >}}

&nbsp;

### マップ上で移動した時のライブフィルタリング

近い地点を一緒にグループ化し、ズームインした時に展開します。Yelpのような検索フィルタのエクスペリエンスも、ボックスをチェックして作成することもできます。

[<img class="aligncenter size-full wp-image-2945" src="https://cdn.gethue.com/uploads/2015/08/search-marker-map.png" alt="search-marker-map" width="951" height="396" data-wp-pid="2945" />][4]

&nbsp;

&nbsp;

### インデックスされたレコードおよび元のドキュメントへのリンクの編集

インデックスされたレコードは、管理者がグリッドまたはHTMLウィジェットで直接編集することができます。

元の文書へのリンクも挿入することができます。[HBaseブラウザ][5] 、 [メタストアアプリ][6]やファイルブラウザでオープンすることができる、URLやテーブルのアドレス、ファイルを記述しているいくつかのJSONを含んだ&#8217;link-meta&#8217;という名前のフィールドをレコードに追加します：

任意のリンク

<pre><code class="javascript">{'type': 'link', 'link': 'gethue.com'}</pre>

ファイルブラウザ

<pre><code class="javascript">{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527'}
{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1'}
{'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1', 'col': 'c1'}
</pre>

ファイルブラウザ

<pre><code class="javascript">{'type': 'hdfs', 'path': '/data/hue/file.txt'}</pre>

メタストア

<pre><code class="javascript">{'type': 'hive', 'database': 'default', 'table': 'sample_07'}</pre>

<img class="aligncenter size-large wp-image-2939" src="https://cdn.gethue.com/uploads/2015/08/search-link-1024x630.png" alt="search-link" width="1024" height="630" data-wp-pid="2939" />

&nbsp;

&nbsp;

### エクスポート/インポート/共有保存ダッシュボード

ダッシュボードは、直接画面上からHueのドキュメント（[Oozieエディタ][7]のようなJSONファイル）として選択、エクスポートすることができます。これにより、私たちが git の対応を導入するまで、より簡単にバックアップするできます。また、クラスタ間でダッシュボードを転送するのに便利です。

<img class="aligncenter size-large wp-image-2944" src="https://cdn.gethue.com/uploads/2015/08/search-export-1024x411.png" alt="search-export" width="1024" height="411" data-wp-pid="2944" />

<img class="aligncenter size-large wp-image-2940" src="https://cdn.gethue.com/uploads/2015/08/search-import-1024x196.png" alt="search-import" width="1024" height="196" data-wp-pid="2940" />

&nbsp;

### 完全な検索クエリ定義の保存とリロード

現在選択されたファセットとフィルタ、クエリ文字列は、ダッシュボードの名前で保存することができます。これらは「コホート（集団）」やレコードの事前選択を定義しておき、すぐにそれらを再読み込みするのに役立ちます。

<img class="aligncenter size-large wp-image-2937" src="https://cdn.gethue.com/uploads/2015/08/search-query-def-1024x507.png" alt="search-query-def" width="1024" height="507" data-wp-pid="2937" />

### 「固定」または「ローリング」時間ウィンドウフィルタリング

リアルタイムのインデキシングは、現在、ローリングウィンドウフィルターとN秒毎のダッシュボードの自動更新により輝いています。[SearchとSpark Streamingでリアルタイムの分析ダッシュボードを構築する][3]の投稿にあるアクションをご参照ください。

<img class="aligncenter size-full wp-image-2936" src="https://cdn.gethue.com/uploads/2015/08/search-rolling-time.png" alt="search-rolling-time" width="982" height="64" data-wp-pid="2936" /><img class="aligncenter size-large wp-image-2943" src="https://cdn.gethue.com/uploads/2015/08/search-fixed-time.png" alt="search-fixed-time" width="646" height="412" data-wp-pid="2943" />

&nbsp;

### 全画面モード表示

ダッシュボードのエクスペリエンスは、この新しいブラウザの全画面モード（とF11キーによる全画面よりも）さらにいっそうリアルです。

<img class="aligncenter size-large wp-image-2942" src="https://cdn.gethue.com/uploads/2015/08/search-full-mode-1024x504.png" alt="search-full-mode" width="1024" height="504" data-wp-pid="2942" />

&nbsp;

### ネストされた分析ファセットのプレビュー

Solr 5.1は新しい[分析ファセット][8] を見ています。それら用のベータ版のサポートが追加され、hue.iniで有効にすることができます:

<pre><code class="bash">[search]
latest=true
</pre>

より包括的なデモは[BikeShareデータの可視化][2]の投稿で提供されています。

<img class="aligncenter size-large wp-image-2938" src="https://cdn.gethue.com/uploads/2015/08/search-nested-facet-1024x304.png" alt="search-nested-facet" width="1024" height="304" data-wp-pid="2938" /> <img class="aligncenter size-large wp-image-2941" src="https://cdn.gethue.com/uploads/2015/08/search-hit-widget.png" alt="search-hit-widget" width="275" height="165" data-wp-pid="2941" />

&nbsp;

&nbsp;

さぁ、さらに多くの[ワークフロー][9]を構築する時がきました！コメントとフィードバックは [hue-user][10] メーリングリストや[@gethue][11]までお気軽に！

 [1]: http://lucene.apache.org/solr/
 [2]: https://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/
 [3]: https://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
 [4]: https://cdn.gethue.com/uploads/2015/08/search-marker-map.png
 [5]: https://gethue.com/hbase-browsing-with-doas-impersonation-and-kerberos/
 [6]: https://gethue.com/category/metastore/
 [7]: https://gethue.com/exporting-and-importing-oozie-workflows/
 [8]: http://yonik.com/solr-subfacets/
 [9]: http://demo.gethue.com/search/new_search
 [10]: http://groups.google.com/a/cloudera.org/group/hue-user
 [11]: https://twitter.com/gethue