---
title: 新しいSQLエディタ
author: Hue Team
type: post
date: 2016-06-30T23:59:08+00:00
url: /new-sql-editor/
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
    |
        これが新しいSQLエディタです！
        
        現在、Hueは任意の言語をサポートする汎用エディタを持っていますが、現在はSQLに焦点を当てています。これはシングルページのアプリで以前よりもずっと速く、使うのも簡単です。これらはいくつかの重要な機能とビデオのデモです：
        
        
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
  - Hive
  - Hue 3.10
  - Impala
  - SQL
  - Video

---
これが新しいSQLエディタです！

現在、Hueは任意の言語をサポートする汎用エディタを持っていますが、現在は[SQL][1]に焦点を当てています。これはシングルページのアプリで以前よりもずっと速く、使うのも簡単です。これらはいくつかの重要な機能とビデオのデモです：

  * クエリ間の切り替えの際にページをリロードしない
  * 実行中及び過去のクエリのライブ履歴
  * Hiveと[Impala][2]のサポートを強化
  * 任意のプログラミング言語に拡張可能

{{< youtube LvTWPgkrdvM >}}

まとめ

  * メタデータのブラウズ 
      * 数千のデータベースやテーブルのリストとフィルタリングに対応
      * テーブルブラウザへのクイックリンク
      * 統計
  * クエリの改訂 
      * スマートオートコンプリート
      * クエリ、検索と置換をフォーマット
      * パラメータ化
      * 拡大ビュー、固定列/行ヘッダ、列へのジャンプ..
      * 棒グラフ、パイ、マーカーマップ、勾配マップ、散布図チャート
      * ジョブおよびログへのリンク
      * [Solr SQLサポート][3]
      * [JDBCサポート（ベータ版）][4]
  * 結果の操作 
      * 共有
      * Excel、CSVダウンロード
      * HDFSファイルまたは新しいテーブルにエクスポート
      * [ワークフローに保存されたクエリをドラッグ＆ドロップ][5]

&nbsp;

私たちはこの新しいエディタによりSQL on Hadoopがより生産的になることを願っています！あなたが他のデータベースとエンジンと接続したい場合、気軽に[新しいコネクタ][6]を書くか 、[hue-user][7]リストのコミュニティに参加してください。Hue3.11（〜2016 Q3）の次の改善ではさらに多くのユーザーエクスペリエンスが磨かれているので、様々なフィードバック（バグ、機能要望..）を[歓迎します][8] ！

&nbsp;

<div id="attachment_4192" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/06/editor-grid.png"><img class="size-large wp-image-4192" src="https://cdn.gethue.com/uploads/2016/06/editor-grid-1024x524.png" alt="Grid result view" width="1024" height="524" data-wp-pid="4192" /></a>
  
  <p class="wp-caption-text">
    Grid result view
  </p>
</div>

&nbsp;

<div id="attachment_4193" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2016/06/editor-map.png"><img class="size-large wp-image-4193" src="https://cdn.gethue.com/uploads/2016/06/editor-map-1024x479.png" alt="Result Widget view" width="1024" height="479" data-wp-pid="4193" /></a>
  
  <p class="wp-caption-text">
    Result widget view
  </p>
</div>

 [1]: https://gethue.com/category/sql/
 [2]: http://impala.io
 [3]: https://gethue.com/sql-editor-for-solr-sql/
 [4]: https://gethue.com/custom-sql-query-editors/
 [5]: https://gethue.com/drag-drop-saved-hive-queries-into-your-workflows/
 [6]: https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue