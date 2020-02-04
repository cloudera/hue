---
title: SQLオートコンプリートポップアップの改良とテーブル作成ウィザード
author: Hue Team
type: post
date: 2017-05-12T05:05:32+00:00
url: /sql-autocomplete-popup-revamp-and-new-create-table-wizard/
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
sf_author_info:
  - 1
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
categories:
  - Hive
  - Hue 4.0
  - Impala
  - SQL
  - Video

---
# SQLの改善

エディタはますます良くなっています。 以下は、最近の主要な改善点です。

## オートコンプリートポップアップの改良

通常のコードエディタと同様に、オートコンプリートは2つの部分に分割されています。 これは、現行のテーブルや列のメタデータをフェッチする際のハングアップを防ぎ、コメントやオブジェクトの種類、完全な名前などのより多くのコンテキスト情報を表示するためです。

<div id="attachment_33782" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2017/05/autocomplete-before.png"><img class="aligncenter size-full wp-image-4757" src="https://cdn.gethue.com/uploads/2017/05/autocomplete-before.png" alt="" width="344" height="178" data-wp-pid="4757" /></a>
  </p>
  
  <p class="wp-caption-text">
    以前のオートコンプリート
  </p>
</div>

<div id="attachment_33783" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2017/05/autocomplete_1.png"><img class="aligncenter size-full wp-image-4758" src="https://cdn.gethue.com/uploads/2017/05/autocomplete_1.png" alt="" width="887" height="317" data-wp-pid="4758" /></a>
  </p>
  
  <p class="wp-caption-text">
    新しいバージョンのオートコンプリート
  </p>
</div>

<div id="attachment_33784" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2017/05/autocomplete_2.png"><img class="aligncenter size-full wp-image-4759" src="https://cdn.gethue.com/uploads/2017/05/autocomplete_2.png" alt="" width="823" height="323" data-wp-pid="4759" /></a>
  </p>
  
  <p class="wp-caption-text">
    <a href="https://kudu.apache.org/">Apache Kudu</a>の主キーは直接表示される
  </p>
</div>

## テーブル作成ウィザード

ファイルから新しいSQLテーブルを作成するのに苦労したことがあれば、これがもっと簡単になったことを嬉しく思うでしょう。 最新のHueのリリースではこれらをアドホックなやり方で作成して、セルフサービスの分析を迅速化できます。 ウィザードは2つの簡単な手順に改修され、さらに多くの形式を提供します。 ユーザーは次の操作を行うだけです:

  1. ファイルを選択する
  2. テーブルの種類を選択する

これだけです！ファイルはHDFSまたはS3（設定されている場合）から選択してドラッグアンドドロップでき、それらのフォーマットは自動的に検出されます。 ウィザードは、テーブルのパーティション化、Kuduテーブル、ネスト型などの高度な機能を実行する際にも支援します。

詳細は次のビデオをご覧ください：

{{< youtube RxT0M8JgvOk >}}

&nbsp;

Hueの新しいバージョンが、セルフサービスのデータ検索と分析をより簡単かつ迅速に行えるようにしていることを願っています。 ご質問やご意見がありましたらコミュニティフォーラム 、または@gethueから気軽にコメントしてください！

これらの改善は最新のHue、あるいは [demo.gethue.com][1]　でご覧いただけます!

 [1]: http://demo.gethue.com