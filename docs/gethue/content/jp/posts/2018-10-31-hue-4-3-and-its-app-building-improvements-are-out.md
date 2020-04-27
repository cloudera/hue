---
title: 分析とDjangoが改善された Hue 4.3 が公開！
author: Hue Team
type: post
date: 2018-10-31T03:20:23+00:00
url: /hue-4-3-and-its-app-building-improvements-are-out/
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
    Hueチームは全てのコントリビューターに感謝し、Hue 4.3 のリリースを嬉しく思います！  
    このリリースの焦点は、 Djangoを、Python 2.7互換バージョンの1.11にアップグレードする大きなリフレッシュでした。
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
  - Hue 4.3
  - Release

---
<div class="post-info clearfix">
  <div class="comments-likes">
    <div class="comments-wrapper">
      ビッグデータエクスプローラの皆さん、こんにちは。
    </div>
  </div>
</div>

&nbsp;

&nbsp;

Hueチームは全てのコントリビューターに感謝し、Hue 4.3 のリリースを嬉しく思います！  [<img class="aligncenter size-full wp-image-2988" src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" alt="hue-logo (copy)" width="85" height="63" data-wp-pid="2988" />][1]

&nbsp;

このリリースの焦点は、 [Django][2]を、Python 2.7互換バージョンの1.11にアップグレードする大きなリフレッシュでした。
  
このリリースには、SQL [エディターの][3]変数、カタログ、 [ダッシュボード][4]の改善が含まれています。また、このリリースでは、マルチクラスターのサポート（ [HUE-8330][5] ）と、データアプリケーションの構築をより簡単にするための準備を整えています。

この[リリースに][6]は、900件のコミットと200件以上のバグ修正が含まれています！tarball版を入手して試してみてください！

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://www.dropbox.com/s/bv2al5bvc7uwgls/hue-4.3.0.tgz?dl=0" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

これらは主な改善の一覧です。すべての変更は [リリースノート][7] を参照してください。また、 手っ取り早く試すには [demo.gethue.com][8]を開いてみて下さい

# 概要

  * コアバックエンドをDjango 1.11にアップグレードしました。よって、Python 2.7.x が必要になりました。（CentOS / RHEL 6 に Python 2.7 をインストールするための[ドキュメント][9] ）
  * [言語リファレンスの組み込み、列のサンプリング、エディタのダークモード][10][<img class="aligncenter size-full wp-image-5581" src="https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif" alt="" width="766" height="523" />][11]
  * [エンドユーザーのデータカタログ検索の簡素化][12]
  
    [<img class="aligncenter size-full wp-image-5381" src="https://cdn.gethue.com/uploads/2018/05/Top_Search_Drag.gif" alt="" width="850" height="450" />][13]
  * [SQLエディタの変数][14]
  
    [<img class="aligncenter size-full wp-image-5321" src="https://cdn.gethue.com/uploads/2018/04/variables_multi.png" alt="" width="858" height="259" />][15]
  * [改善されたSQL Exploration][16]
  
    [<img class="aligncenter size-full wp-image-5372" src="https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif" alt="" width="848" height="426" />][17]
  * [リクエストの簡単なプロファイリングを可能にするモードを取得][18]
  * [Sentryアプリでのより細かい粒度の権限][19]
  * [改善されたダッシュボードのレイアウト][20][<img class="aligncenter size-full wp-image-5463" src="https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dnd.gif" alt="" width="1073" height="565" />][21]
  * [改善されたジョブスケジューリングのモニタリング][22]
  * [改善されたOozieワークフローグラフの表示][23]

&nbsp;

さらにその先へ！

&nbsp;

いつものように、すべてのプロジェクトの貢献者とフィードバックを送信してくれる方、[hue-user][24] メーリングリストまたは[@gethue][25]に参加してくれる方々に感謝しています！

&nbsp;

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://www.djangoproject.com/
 [3]: https://gethue.com/sql-editor/
 [4]: https://gethue.com/search-dashboards/
 [5]: https://issues.cloudera.org/browse/HUE-8330
 [6]: https://github.com/cloudera/hue/commits/release-4.3.0
 [7]: http://cloudera.github.io/hue/docs-4.3.0/release-notes/release-notes-4.3.0.html
 [8]: http://demo.gethue.com/
 [9]: http://cloudera.github.io/hue/latest/admin-manual/manual.html#centosoracleredhat-6x
 [10]: http://jp.gethue.com/additional-sql-improvements-in-hue-4-3/
 [11]: https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif
 [12]: https://gethue.com/simplifying-the-end-user-data-catalog-search/
 [13]: https://cdn.gethue.com/uploads/2018/05/Top_Search_Drag.gif
 [14]: https://gethue.com/sql-editor-variables/
 [15]: https://cdn.gethue.com/uploads/2018/04/variables_multi.png
 [16]: https://gethue.com/improved-sql-exploration-in-hue-4-3/
 [17]: https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif
 [18]: https://gethue.com/get-a-mode-to-allow-easy-profiling-of-requests/
 [19]: https://gethue.com/finer-grain-privileges/
 [20]: http://Improved dashboards layouts
 [21]: https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dnd.gif
 [22]: https://gethue.com/improved-job-scheduling-monitoring/
 [23]: https://gethue.com/improved-oozie-workflow-graph-display-in-hue-4-3/
 [24]: http://groups.google.com/a/cloudera.org/group/hue-user
 [25]: https://twitter.com/gethue