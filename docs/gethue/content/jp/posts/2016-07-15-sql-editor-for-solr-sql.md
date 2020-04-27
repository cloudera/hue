---
title: Solr SQLのためのSQLエディタ
author: Hue Team
type: post
date: 2016-07-15T00:33:57+00:00
url: /sql-editor-for-solr-sql/
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
  - HueはすでにApache Solrと統合し、動的検索ダッシュボードを提供しています 。Hue 3.10の新しいSQLエディタにより、Hueは任意のデータベースに開かれました。これはSolr 6が現在SQLインタフェースを提供しているので素晴らしいことです 。
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
sf_remove_promo_bar:
  - 1
categories:
  - Hue 3.10
  - Search
  - SQL
  - Video

---
HueはすでにApache Solrと統合し、[動的検索ダッシュボード][1]を提供しています 。Hue 3.10の[新しいSQLエディタ][2]により、Hueは[任意のデータベース][3]に開かれました。これはSolr 6が現在[SQLインタフェース][4]を提供しているので素晴らしいことです 。

これは通常のHiveやImpalaテーブルをクエリするのと同じようにSolrコレクションをクエリするデモです。

&nbsp;

{{< youtube u4ctEYl5Mlo >}}

&nbsp;

<div id="attachment_4109" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/05/solr-sql-editor.png"><img class="wp-image-4109 size-large" src="https://cdn.gethue.com/uploads/2016/05/solr-sql-editor-1024x693.png" alt="solr-sql-editor" width="1024" height="693" data-wp-pid="4109" /></a>
  
  <p class="wp-caption-text">
    エディタで
  </p>
</div>

&nbsp;

<div id="attachment_4110" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/05/solr-sql-notebook.png"><img class="wp-image-4110 size-large" src="https://cdn.gethue.com/uploads/2016/05/solr-sql-notebook-1024x691.png" alt="solr-sql-notebook" width="1024" height="691" data-wp-pid="4110" /></a>
  
  <p class="wp-caption-text">
    ノートブックで
  </p>
</div>

&nbsp;

&nbsp;

Solr SQLはかなり最近のものなので、特にSolrのサポートが欠けているいくつかの注意点があります：

  * SELECT *
  * LIKEとWHERE句
  * 結果セットのページネーション

これらは標準的な他のデータベースにおける似通ったSQLの経験を邪魔します（ただし、私たちは[HUE-3686][5]で追跡しています ）。

しかし、私たちはまだあなたがこの新しい有望な機能を試して遊いることを願っています。不明な点があれば、いつものようにコメントとフィードバックは [hue-user][6] メーリングリストや[Solrのコミュニティ][7]、[@gethue][8]までお気軽に！

 [1]: https://gethue.com/dynamic-search-dashboard-improvements-3/
 [2]: https://gethue.com/new-sql-editor/
 [3]: https://gethue.com/custom-sql-query-editors/
 [4]: http://yonik.com/solr-6/
 [5]: https://issues.cloudera.org/browse/HUE-3686
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: http://lucene.apache.org/solr/resources.html
 [8]: https://twitter.com/gethue