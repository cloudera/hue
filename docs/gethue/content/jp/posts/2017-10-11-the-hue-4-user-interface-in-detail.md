---
title: Hue 4のユーザーインターフェースの詳細
author: Hue Team
type: post
date: 2017-10-11T12:03:48+00:00
url: /the-hue-4-user-interface-in-detail/
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
sf_custom_excerpt:
  - |
    アロハ！ ユーザーエクスペリエンスのファンの皆さん、
    
    Hue 4 のリリースで、私たちはオンプレミスとクラウドでデータの発見と分析を要因にするために、既存のソフトウェア上に近代的な UI を導入しました。
categories:
  - Hue 4.0

---
アロハ！ ユーザーエクスペリエンスのファンの皆さん、

[Hue 4 のリリース][1]で、私たちはオンプレミスとクラウドでデータの発見と分析を簡単にするため、既存のソフトウェア上に近代的な UI を導入しました。

# 新しい UI の構成

新しいレイアウトはインターフェースを単純化して、単一ページのアプリケーションになりました。これにより物事はよりスムーズになり、アプリケーションが統合されます。

<img class="aligncenter size-full wp-image-4893" src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.04.28.png" alt="" width="733" height="514" />

上から下に向かって説明すると、

  * トップバーは、（大きな青いボタンの）クイックアクション、グローバル検索、右側の通知エリアと、完全に再設計されました
  * さまざまなアプリへのリンクと、素早くデータをインポートする方法を提供する、折りたたみ式のハンバーガーメニュー
  * 左側に拡張されたクイックブラウズ
  * 楽しさがあるメインのアプリ領域 🙂
  * 現在のアプリケーション用の右側のアシスタントパネル。現在ではエディタのため（例えば Hive の場合）に有効になっており、ライブヘルプ、クエリで使用しているテーブルのクイックブラウザ、および、多くの機能を提供しています。Hueのインスタンスが <a href="https://optimizer.cloudera.com" target="_blank" rel="noopener">Cloudera Navigator Optimizer</a>のようなSQL最適化サービスに接続されている場合、[クエリの提案][2]を提供できます！

さまざまなアプリケーションが4つの主要概念の領域に分類されています。

  * [エディタ][3]： Hueのエディタの目標は、データのクエリを簡単かつ生産的にすることです。SQL に焦点を当てるだけではなくジョブのサブミットもサポートします。インテリジェントな自動補完、データの検索とタグ付け、クエリの支援があります。
  * [ブラウザ][4]： Hueのブラウザは、クラウドまたはオンプレミスのクラスター内のデータやジョブを簡単に検索し、表示、アクションを実行できます。
  * [ダッシュボード][5]： ダッシュボードはデータを素早く簡単に探索する対話的な方法です。プログラミングは不要で、解析はドラッグ＆ドロップとクリックで行います。
  * [スケジューラー][6] ：アプリケーションを使用すると、ワークフローを構築し、定期的に自動で実行するようにスケジューリングできます。監視インターフェースは、進行状況、ログを表示し、ジョブの一時停止や停止などのアクションを許可します。

この作業は数年前に開始され、段階的に行われました。設計の研究とお客様からのフィードバックの両方の成果を数多く適用しました。

<img class="aligncenter size-full wp-image-4892" src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.04.18.png" alt="" width="2178" height="1208" />

いくつかの [エキゾチックな場所][7] がインスピレーションを得るのに役立ちました:

<img class="aligncenter wp-image-4550 size-large" src="https://cdn.gethue.com/uploads/2016/12/IMG_5670-1024x768.jpg" alt="" width="1024" height="768" />

ここはすべての美しさにあります 🙂

[<img class="aligncenter size-full wp-image-4777" src="https://cdn.gethue.com/uploads/2016/04/hue4_editor.png" alt="" width="1525" height="986" data-wp-pid="4777" />][8]

&nbsp;

# クイック検索とブラウズ

新しい検索バーは常に画面上部に表示され、Hueが <a href="https://www.cloudera.com/products/product-components/cloudera-navigator.html" target="_blank" rel="noopener">Cloudera Navigator</a>のようなメタデータサーバーにアクセスするように設定されている場合は[ドキュメント検索とメタデータ検索][9]も提供します。

<img class="aligncenter size-full wp-image-4904" src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.24.07.png" alt="" width="826" height="333" />

画面の左側にある改良されたクイックブラウズは、より多くのデータソースを提供し、（以前と同じように）HiveとImpalaだけでなく、HDFS、S3、HBase、Solrコレクション、およびHueのドキュメントに対しても有効になりました。

<img class="aligncenter size-full wp-image-4906" src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-16.29.59.png" alt="" width="290" height="263" />

&nbsp;

# デフォルトのアクション / ランディングページ

Hue 4 では、すべてのユーザーが好みのメインアクション（大きな青いボタン）とランディングページを設定できます。この場合、Hiveの横にあるようなアプリケーションの横にある星印をクリックするだけです。

<img class="aligncenter size-full wp-image-4888" src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-18-19.20.57.png" alt="" width="254" height="74" />

次回ログインすると、Hiveエディタにランディングします。新しいクエリには常にワンクリックです。

&nbsp;

# 後方互換生

以前の Hue 3 の UI はまだ存在しており、ユーザーのメニューから  &#8216;Switch to Hue 3/4&#8217; をクリックするだけで簡単にたどり着くことができます。
  
<img class="aligncenter size-full wp-image-4879" src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-15.28.12.png" alt="" width="258" height="335" />

<img class="aligncenter size-full wp-image-4880" src="https://cdn.gethue.com/uploads/2017/07/Screenshot-2017-07-19-15.28.24.png" alt="" width="478" height="195" />

管理者は <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank" rel="noopener">hue.ini または Cloudera Managerの安全バルブ</a>で、グローバルなレベルで新しい UI を有効/無効化できます。

<pre><code class="bash">[desktop]
# Choose whether to enable the new Hue 4 interface.
is_hue_4=true
</pre>

ブラウザのアドレスバーを見ると、/hue プレフィックスを持つすべてのURLが Hue 4 を示していることに気付くでしょう。プレフィックスを取り除くだけで Hue 3 バージョンのページ（例:/hue/editor (Hue 4) → /editor (Hue 3)）にたどり着くことができます。

まだのようであれば [demo.gethue.com][10] で試すか、または <a href="http://jp.gethue.com/hue-4-and-its-new-interface-is-out/" target="_blank" rel="noopener">ダウンロード</a> してください！

その先へ!

 [1]: http://jp.gethue.com/hue-4-and-its-new-interface-is-out/
 [2]: https://gethue.com/hue-4-sql-editor-improvements/
 [3]: https://gethue.com/sql-editor/
 [4]: https://gethue.com/browsers/
 [5]: https://gethue.com/search-dashboards/
 [6]: https://gethue.com/scheduling/
 [7]: https://gethue.com/category/team/
 [8]: https://cdn.gethue.com/uploads/2016/04/hue4_editor.png
 [9]: https://blog.cloudera.com/blog/2017/05/new-in-cloudera-enterprise-5-11-hue-data-search-and-tagging/
 [10]: http://demo.gethue.com