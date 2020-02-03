---
title: Oozieダッシュボードの改善
author: Hue Team
type: post
date: 2015-04-13T10:08:55+00:00
url: /oozie-dashboard-improvements-2/
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
  - 近日登場する Hue 3.8では、Oozieダッシュボードをいくつかの改善を行い、より直感的にナビゲーションできるようになりました（エディタの改良はこちら の記事をご覧下さい）。ここは、それらをまとめたビデオのデモです。
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
  - Hue 3.8
  - Oozie
  - Video

---
近日登場する Hue 3.8では、Oozieダッシュボードをいくつかの改善を行い、より直感的にナビゲーションできるようになりました（エディタの改良は[こちら][1]の記事をご覧下さい）。ここは、それらをまとめたビデオのデモです。

{{< youtube U4L_qlNhjcc >}}

**新しいOozieの機能**

ワークフローダッシュボード：

  * ジョブの親の列（親になるのは、なし(nothing)、またはワークフロー、またはコーディネータ）
  * 「Submitted by」によるジョブの親のフィルタ

****
  
[<img class="aligncenter wp-image-2538 size-large" src="https://cdn.gethue.com/uploads/2015/04/parent-1024x835.png" alt="parent" width="1024" height="835" />][2]****

&nbsp;

  * サブミットされたワークフローのグラフから、サブワークフローアクションのページとエディタのページにナビゲート

[<img class="aligncenter wp-image-2536 size-large" src="https://cdn.gethue.com/uploads/2015/04/graph-1024x642.png" alt="graph" width="1024" height="642" />][3]

&nbsp;

  * サブミットされたワークフローのアクション／ワークフローから親のジョブにナビゲート

[<img class="aligncenter wp-image-2537 size-large" src="https://cdn.gethue.com/uploads/2015/04/navigate-1024x414.png" alt="navigate" width="1024" height="414" />][4]

&nbsp;

  * 実行しているコー​​ディネーターの終了時刻を更新

[<img class="aligncenter wp-image-2535 size-large" src="https://cdn.gethue.com/uploads/2015/04/endtime-1024x630.png" alt="endtime" width="1024" height="630" />][5]

&nbsp;

****さて、次は！****

もっとたくさん登場します:

  * より高速なログ検索
  * 任意の実行中のワークフローの[ライブグラフ表示][6]
  * ワークフローアクションの[スマートなファイルのシンボリックリンク][7]
  * [コー​​ディネーターのアクションのページ対応][8]

そして、エディタのワークフローダッシュボードのリベース作業は評価中です。乞うご期待！

&nbsp;

<span style="font-size: 11px;">いつものように、コメントとフィードバックは <a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a> メーリングリストや<a href="https://www.google.com/url?q=https%3A%2F%2Ftwitter.com%2Fgethue&sa=D&sntz=1&usg=AFQjCNFSK0PmjkpMhs1SAQLUx4hheDzfmA">@gethue</a>までお気軽に！ </span>

 [1]: https://gethue.com/new-apache-oozie-workflow-coordinator-bundle-editors-2/?lang=ja "Apache Oozieの新しいワークフロー、コーディネーター＆バンドルエディタ"
 [2]: https://cdn.gethue.com/uploads/2015/04/parent.png
 [3]: https://cdn.gethue.com/uploads/2015/04/graph.png
 [4]: https://cdn.gethue.com/uploads/2015/04/navigate.png
 [5]: https://cdn.gethue.com/uploads/2015/04/endtime.png
 [6]: https://issues.cloudera.org/browse/HUE-2659
 [7]: https://issues.cloudera.org/browse/HUE-1922
 [8]: https://issues.cloudera.org/browse/HUE-2292