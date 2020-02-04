---
title: SolrコレクションのためにSentryの権限を編集するためのUI
author: Hue Team
type: post
date: 2016-06-02T00:00:00+00:00
url: /ui-to-edit-sentry-privilege-of-solr-collections/
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
  - Sentryアプリは、現在、Solrのコレクションの権限が編集できるようになっています。以前はHiveテーブルの権限の編集のみをサポートしていました。
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
  - Hue 3.11
  - Search
  - Security

---
[Sentryアプリ][1]は、現在、Solrのコレクションの権限が編集できるようになっています。以前はHiveテーブルの権限の編集のみをサポートしていました。

あなたの全てのSolrのインデックスの認可を制御するのが今ははるかに容易になりました（今までは、権限はサーバの再起動でフラット・ファイルを介して設定する必要がありました）。また、強力な[動的検索ダッシュボード][2]はユーザーの唯一の特定のグループによって安全にアクセスすることができます。

これはSolrのデータへのアクセスを設定する方法のデモビデオです：

{{< youtube gSNKv5agmTU >}}

以下はアプリケーションの主な機能のスクリーンショットです：

&nbsp;

<div id="attachment_4077" style="width: 1034px" class="wp-caption aligncenter">
  <img class="wp-image-4077 size-large" src="https://cdn.gethue.com/uploads/2016/05/solr-secu-1024x624.png" alt="solr-secu" width="1024" height="624" data-wp-pid="4077" />
  
  <p class="wp-caption-text">
    それらに関連する権限を持つのSolrコレクションと設定のリスト
  </p>
</div>

<div id="attachment_4076" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/05/solr-secu2-e1464909489928.png"><img class="wp-image-4076 size-large" src="https://cdn.gethue.com/uploads/2016/05/solr-secu2-e1464909489928-1024x562.png" alt="" width="1024" height="562" data-wp-pid="4076" /></a>
  
  <p class="wp-caption-text">
    すべてのロールとその権限のリスト。グループによりフィルタできる
  </p>
</div>

&nbsp;

<div id="attachment_4091" style="width: 893px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/06/solr-sentry-all.png"><img class="size-full wp-image-4091" src="https://cdn.gethue.com/uploads/2016/06/solr-sentry-all.png" alt="Apply privilege to all the collections or configs with *" width="883" height="384" data-wp-pid="4091" /></a>
  
  <p class="wp-caption-text">
    *ですべてのコレクションやコンフィグに権限を適用
  </p>
</div>

&nbsp;

<div id="attachment_4092" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/06/solr-sentry-query-error.png"><img class="wp-image-4092 size-large" src="https://cdn.gethue.com/uploads/2016/06/solr-sentry-query-error-1024x279.png" alt="End user error when querying a collection without the QUERY privilege" width="1024" height="279" data-wp-pid="4092" /></a>
  
  <p class="wp-caption-text">
    QUERY権限なしにコレクションをクエリした際のエンドユーザーのエラー
  </p>
</div>

&nbsp;

<div id="attachment_4093" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/06/solr-sentry-update-error.png"><img class="size-large wp-image-4093" src="https://cdn.gethue.com/uploads/2016/06/solr-sentry-update-error-1024x405.png" alt="End user error when modifying a record without the UPDATE privilege" width="1024" height="405" data-wp-pid="4093" /></a>
  
  <p class="wp-caption-text">
    UPDATE権限なしでレコードを変更した場合のエンドユーザーのエラー
  </p>
</div>

&nbsp;

&nbsp;

私たちはセキュリティを容易に使用できることが好ましいと願っています。コメントとフィードバックは [hue-user][3] メーリングリストや[@gethue][4]までお気軽に！

 [1]: https://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/
 [2]: https://gethue.com/dynamic-search-dashboard-improvements-3/
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue