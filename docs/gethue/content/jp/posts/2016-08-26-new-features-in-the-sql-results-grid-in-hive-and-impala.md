---
title: HiveとImpalaでSQLの結果へのアクセスと洗練化
author: Hue Team
type: post
date: 2016-08-26T10:47:54+00:00
url: /new-features-in-the-sql-results-grid-in-hive-and-impala/
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
  - Hue 3.11のSQLエディタは、ブラウザをクラッシュさせることなく大きなテーブルの表示を可能にする、パフォーマンスが向上した完全に書き直された結果グリッドに加えていくつかの気の利いたツールをもたらします。
categories:
  - Hive
  - Hue 3.11
  - Hue 3.12
  - Impala
  - SQL

---
アロハ！大きな問いに答えている皆さん！

[Hue 3.11][1]の[SQLエディタ][2]は、ブラウザをクラッシュさせることなく大きなテーブルの表示が可能になった、パフォーマンスが向上した完全に書き直された結果グリッドに加え、いくつかの気の利いたツールをもたらしています。

#### 今は、いくつかの行をロックできます。これは他の行のデータと比較するのに役立ちます

行IDにマウスを合わせると、新しいロックのアイコンを取得します。それをクリックすると行は自動的にテーブルの上部に貼り付きます。
  
<img class="aligncenter size-large wp-image-3875" alt="lock_rows" width="1258" height="693" data-gifffer="http://jp.gethue.com/wp-content/uploads/2016/08/lock_rows.gif" data-wp-pid="3875" />

<h4 style="margin-top: 100px;">
  （ついに！）結果のグリッドにある列のリストは、データの型によってフィルタリングでき、サイズを変更することができます
</h4>

<img class="aligncenter size-large wp-image-4372" alt="column_list" width="1024" height="404" data-gifffer="https://cdn.gethue.com/uploads/2016/08/column_list.gif" data-wp-pid="4372" />

<h4 style="margin-top: 100px;">
  本当に長い内容のフィールドのヘッダ行がスクロール位置に追従し、常に表示されます
</h4>

<img class="aligncenter size-large wp-image-4373" alt="headers" width="1024" height="406" data-gifffer="https://cdn.gethue.com/uploads/2016/08/headers.gif" data-wp-pid="4373" />

<h4 style="margin-top: 100px;">
  今ではテーブル内の検索をすることができ、結果がハイライトされています
</h4>

結果タブの虫眼鏡のアイコンをクリックするか、またはCtrl/Cmd + Fを押すかのいずれかによって、新しい検索を有効にすることができます
  
<img class="aligncenter size-large wp-image-4374" alt="search" width="1024" height="483" data-gifffer="https://cdn.gethue.com/uploads/2016/08/search.gif" data-wp-pid="4374" />

<h4 style="margin-top: 100px;">
  仮想レンダラーはその時点で必要なセルだけを表示します
</h4>

ここで見ている表には数百もの列があります
  
<img class="aligncenter size-large wp-image-4375" alt="virtual_renderer" width="1024" height="414" data-gifffer="https://cdn.gethue.com/uploads/2016/08/virtual_renderer.gif" data-wp-pid="4375" />

<h4 style="margin-top: 100px;">
  ExcelやCSVファイルへのダウンロードにとても時間がかかる場合は、素敵（？）なメッセージが表示されます
</h4>

<img class="aligncenter size-full wp-image-4440" alt="downloadwait" width="1494" height="618" data-gifffer="https://cdn.gethue.com/uploads/2016/08/downloadwait.gif" data-wp-pid="4440" />

また、Hueはダウンロードが切り詰められている (download has been truncated)、と教えてくれます！
  
[<img class="aligncenter size-medium wp-image-4441" src="https://cdn.gethue.com/uploads/2016/08/Screenshot-2016-08-25-19.37.26-300x129.jpg" alt="Screenshot 2016-08-25 19.37.26" width="300" height="129" data-wp-pid="4441" />][3]
  
いつものように[hue-user][4]リストまたは[@gethue][5]までフィードバック、またはご参加下さい！

&nbsp;

 [1]: https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/
 [2]: https://gethue.com/sql-editor/
 [3]: https://cdn.gethue.com/uploads/2016/08/Screenshot-2016-08-25-19.37.26.jpg
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue