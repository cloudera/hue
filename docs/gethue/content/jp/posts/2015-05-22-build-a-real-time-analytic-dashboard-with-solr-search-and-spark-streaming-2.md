---
title: SearchとSpark Streamingでリアルタイムの分析ダッシュボードを構築する
author: Hue Team
type: post
date: 2015-05-22T07:17:57+00:00
url: /build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming-2/
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
  - 'Searchは、対話的にデータを探索するための素晴らしい方法です。Searchアプリは<a href="https://gethue.com/more-solr-search-dashboards-possibilities/">継続的に改善</a>されており、今ではリアルタイム用のより良い対応が付属しています！'
categories:
  - Hue 3.9
  - Search
  - Spark
  - Tutorial
  - Video

---
Searchは対話的にデータを探索するための素晴らしい方法です。Searchアプリは[継続的に改善][1]されており、今ではリアルタイム用のより良い対応が付属しています！

このビデオではSpark Streamingでツイートを収集し、それらを[Spark Solr][2]アプリでSolrに直接インデキシングしています。私たちが多くの[ツイート情報][3]を付与する、わずかに[変更したバージョン][4]を使用していることにご注意ください。

{{< youtube qnGEx-3Refg >}}

&nbsp;

あなたはツイートがローリングするのを見ることができるでしょう！以前のバージョンと比較すると：

  * ダッシュボードは任意のページにジャンプすることなく、データが変更された時にウィジェットのみを更新する
  * ダッシュボードはN秒毎に自動でリフレッシュできる
  * 主要な日付フィルタは、すべてのダッシュボードでローリングの日時範囲を素早く選択できる

&nbsp;

<div id="attachment_2644" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2015/05/live-search.png"><img class="wp-image-2644 size-large" src="https://cdn.gethue.com/uploads/2015/05/live-search-1024x509.png" alt="live-search" width="1024" height="509" data-wp-pid="2644" /></a>
  
  <p class="wp-caption-text">
    Tweets coming in
  </p>
</div>

&nbsp;

**総括**

[ほぼリアルタイム][5]でデータをインデキシングする別のやり方がありますが、私たちは、Spark StreamingとSolrアプリだけで追加の設定することなく動作するシナリオとしてこのアプローチに取り組みました。次回は、Solr 5.2の新しい[分析機能][6]をプレビューし、いくつかのデータをインデックスするためにPythonとSparkをどのように使用するかの方法を紹介します！

いつものように、コメントとフィードバックは [hue-user][7] メーリングリストや[@gethue][8]までお気軽に！

 [1]: https://gethue.com/more-solr-search-dashboards-possibilities/
 [2]: https://github.com/LucidWorks/spark-solr
 [3]: https://github.com/romainr/spark-solr/commits/master
 [4]: https://github.com/romainr/spark-solr
 [5]: http://www.cloudera.com/content/cloudera/en/documentation/cloudera-search/v1-latest/Cloudera-Search-User-Guide/csug_flume_nrt_index_ref.html
 [6]: http://yonik.com/solr-facet-functions/
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue