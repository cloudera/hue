---
title: Hue 4 でのSQLエディタの改善
author: Hue Team
type: post
date: 2017-07-20T00:40:12+00:00
url: /hue-4-sql-editor-improvements/
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
    SQLのエキスパートの皆さん、こんにちは!
    
    Hue 4 では、大幅にSQLエディタのユーザーエクスペリエンスを向上し、HiveとImpalaのSQLエディタに多くの改良を加えました。HiveとImpalaのクエリで作業を行う際、HueはNavigator Optimizerからの人気度とリスク評価に基づいて、自動補完による提案を提供します。
sf_author_info:
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
  - Hue 4.0

---
SQLのエキスパートの皆さん、こんにちは!

[Hue 4][1] では、大幅にSQLエディタのユーザーエクスペリエンスを向上し、HiveとImpalaのSQLエディタに多くの改良を加えました。HiveとImpalaのクエリで作業を行う際、Hueは[Navigator Optimizer][2]からの人気度とリスク評価に基づいて、自動補完による提案を提供します。

右側には、アクティブなステートメントに関する詳細やUDFのドキュメントについての詳細が含まれている、新しいアシストパネルが追加されました。

#### 豊富な自動補完（オートコンプリート）

自動補完機能はNavigator Optimizerのメタデータに基づいて、ポピュラーなテーブル、カラム、フィルタ、ジョイン、グループ化 (group by)、並び替え（order by）などを提案します。提案がある場合に表示される自動補完の結果のドロップダウンには新しい「Popular」タブが追加されています。

&nbsp;

<div id="attachment_4871" style="width: 710px" class="wp-caption aligncenter">
  <img class="wp-image-4871" src="https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png" alt="" width="700" height="295" />
  
  <p class="wp-caption-text">
    選択時に人気スコアが表示されているポピュラーなジョイン
  </p>
</div>

&nbsp;

<div id="attachment_4851" style="width: 810px" class="wp-caption aligncenter">
  <img class="size-full wp-image-4851" src="https://cdn.gethue.com/uploads/2017/07/hue_4_popular_filter_agg.png" alt="" width="800" height="250" />
  
  <p class="wp-caption-text">
    左側にポピュラーな集約関数を、右側にポピュラーなフィルタを提案している自動補完の結果
  </p>
</div>

<h4 style="margin-top: 100px;">
  リスクと提案
</h4>

編集中にHueはバックグラウンドでNavigator Optimizerを通してクエリを実行し、クエリのパフォーマンスに影響を与える可能性のあるリスクを特定します。リスクが特定された場合はクエリエディタの上部に感嘆符（！）が表示され、右側のアシスタントパネルの下部に改善する方法の提案が表示されます。

<img class="aligncenter size-full wp-image-4858" width="750" height="286" data-gifffer="https://cdn.gethue.com/uploads/2017/07/hue_4_risk_6.gif" data-wp-pid="4858" />

<h4 style="margin-top: 100px;">
  データが必要な時に必要な場所
</h4>

左側のアシストパネルでは、Hueのドキュメント、HDFSとS3のファイル、その他多くを見つけることができます。アイテムを右クリックするとアクションのリストが表示され、ファイルをドラッグアンドドロップしてエディタなどでパスを取得することもできます。

<div id="attachment_4846" style="width: 810px" class="wp-caption aligncenter">
  <img class=" wp-image-4846" src="https://cdn.gethue.com/uploads/2017/07/hue_4_left_assist.png" alt="" width="800" height="395" />
  
  <p class="wp-caption-text">
    左側のアシストでHueドキュメントの詳細を表示している
  </p>
</div>

右側の関数パネルでは、Hive、Impala、Pigの関数のブラウズとフィルタができます。ダブルクリックやドラッグしてエディタに挿入します。

<div id="attachment_4845" style="width: 451px" class="wp-caption aligncenter">
  <img class=" wp-image-4845" src="https://cdn.gethue.com/uploads/2017/07/hue_4_functions.png" alt="" width="441" height="610" />
  
  <p class="wp-caption-text">
    The new Functions panel in the right assist panel
  </p>
</div>

<h4 style="margin-top: 100px;">
  改善された複数クエリの編集
</h4>

右側のアシスタントパネルでは、編集中のステートメント内のアクティブなテーブルが識別されて表示されます。これにより簡単な概要がわかり、また、テーブル上にカーソルを合わせることでサンプルや列などの詳細を見つけることができます。

<div id="attachment_4860" style="width: 810px" class="wp-caption aligncenter">
  <img class="size-full wp-image-4860" width="800" height="295" data-gifffer="https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif" data-wp-pid="4860" />
  
  <p class="wp-caption-text">
    アクティブなステートメント内のテーブルを表示しているアシスタントパネル
  </p>
</div>

複数のステートメントがある場合は実行したいステートメントにカーソルを置くだけで十分です。アクティブなステートメントには端に青い色でマークが示されます。

&nbsp;

いつものように[hue-user][3]リストまたは[@gethue][4]までフィードバック、またはご参加下さい！

&nbsp;

 [1]: http://jp.gethue.com/hue-4-and-its-new-interface-is-out/
 [2]: https://optimizer.cloudera.com/
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue