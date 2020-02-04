---
title: 'Hadoopでの検索: Solrでの動的な検索ダッシュボード'
author: Hue Team
type: post
date: 2014-06-03T01:31:33+00:00
url: /hadoop-search-dynamic-search-dashboards-with-solr-2/
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
slide_template:
  - default
sf_custom_excerpt:
  - Hue 3.6、およびCuracaoに引きこもっていたチームは、いくつかの高い基準になるために、以前の検索アプリの第2版をもたらしました。今のアプリは、カスタム·ダッシュボードとビジュアライゼーションを構築するための、非常に簡単な方法を提供している、ユーザーエクスペリエンスが大幅に向上しました...
categories:
  - Search
  - Tutorial
  - Video

---
[Hue 3.6][1]および[Curacao][2]に引きこもっていたチームは、いくつかの高い基準になるために、以前の[検索アプリ][3]の第2版をもたらしました。今のアプリは、カスタム·ダッシュボードとビジュアライゼーションを構築するための非常に簡単な方法を提供しているので、ユーザーエクスペリエンスが大幅に向上しました。

これは、[demo.gethue.com][2]によるライブのHueによるもので、実際のApacheのいくつかのログデータを対話形式で探索する方法をデモしたビデオです 。数回クリックするだけで、私たちはエラーのあるページを探したり、最も使用されているHueのアプリは何か、色がグラデーションされている世界地図上で一番利用されているウェブブラウザやユーザーのトラフィックの検査を行います:

{{< youtube hVBxH7w3EP8 >}}

主な機能は次のとおりです:

  * ライブで動的なインタフェースの更新
  * ドラッグ＆ドロップのダッシュボードビルダー
  * テキスト、タイムライン、総計、行、バー、地図、フィルタ、グリッド、HTMLウィジェット
  * ファイルからSolrインデックスの作成ウィザード

&nbsp;

<div id="attachment_1311" style="width: 916px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2014/03/hue-3.6-search-v2.png"><img class=" wp-image-1311" src="https://cdn.gethue.com/uploads/2014/03/hue-3.6-search-v2-1024x548.png" alt="Example of dynamic dashboard" width="906" height="485" data-wp-pid="1311" /></a>
  
  <p class="wp-caption-text">
    独自の動的なダッシュボードを構築する
  </p>
</div>

&nbsp;

Hive/HBaseのような他のHueのアプリとの統合、Hadoopに結果をエクスポート/インポート、より多くのデータ型を描画するような、多くがロードマップ上にあります。次のチュートリアルでは、ApacheのログをSolrにインデックスする方法と、独自の分析を始める方法を紹介する予定です。検索ダッシュボードは、[Hue 3.6][1]や今後登場する予定のC5.1(CDH5.1)パッケージで、気軽に試してみて下さい！

いつものように、私たちは[@gethue][4]や[hue-user][5]でのフィードバックを歓迎します！

 [1]: https://gethue.com/hadoop-ui-hue-3-6-and-the-search-dashboards-are-out
 [2]: https://gethue.com/team-retreat-in-the-caribbean-curacao/
 [3]: https://gethue.com/tutorial-search-hadoop-in-hue/
 [4]: http://twitter.com/gethue
 [5]: http://groups.google.com/a/cloudera.org/group/hue-user