---
title: さらなるSolrの検索ダッシュボードの可能性
author: Hue Team
type: post
date: 2015-04-13T13:20:55+00:00
url: /more-solr-search-dashboards-possibilities-2/
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
  - Hue 3.8では、検索ダッシュボードが一連の新しいオプションと、長い間お待たせしてきた機能を得ました。これらは主な改善点の概要です。
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
  - Search
  - Video

---
Hue 3.8では、[検索ダッシュボード][1]が一連の新しいオプションと、長い間お待たせしてきた機能を得ました。これらは主な改善点の概要です。

{{< youtube T1fPqlWhFiM >}}

&nbsp;

**通常のユーザーもダッシュボードを作成することが可能に**

以前は、Hueの管理者のみがエディタにアクセスできたので実用的ではありませんでした。

[<img class="aligncenter size-full wp-image-2400" src="https://cdn.gethue.com/uploads/2015/03/search-create-menu.png" alt="search-create-menu" width="405" height="224" data-wp-pid="2400" />][2]

&nbsp;

**Range & Up ファセット**

任意の種類のデータのインターバルファセットは、最初のバージョンからサポートされています。しかしいくつかのユースケースでは、境界からひとつ上と下のレンジ（範囲）のファセットはより多くのメリットがあります。1日未満の全てのログの取得や4つ星以上の評価のレストラン、、のようなことを考えてみてください。

[<img class="aligncenter size-large wp-image-2401" src="https://cdn.gethue.com/uploads/2015/03/search-and-up-1024x268.png" alt="search-and-up" width="1024" height="268" data-wp-pid="2401" />][3]

&nbsp;

****2Dマップ****

傾斜マップは位置によるトラフィックを表示するために便利です。今は、国別で一番のブラウザ、オペレーティングシステムをプロットすることができる、別の次元をサポートしています。

[<img class="aligncenter size-full wp-image-2402" src="https://cdn.gethue.com/uploads/2015/03/search-2d-map.png" alt="search-2d-map" width="891" height="520" data-wp-pid="2402" />][4]

&nbsp;

**同じフィールドを使用した複数のウィジェット**

この機能は、タイムラインとテキストファセットで、いくつかのウィジェットや日付フィールドを持つ国コードのフィールドを使用するために特に役立ちます。以前はそれぞれのフィールドでは、ウィジェット内で一度しか使用できませんでした！

[<img class="aligncenter size-large wp-image-2403" src="https://cdn.gethue.com/uploads/2015/03/search-multi-names-1024x239.png" alt="search-multi-names" width="1024" height="239" data-wp-pid="2403" />][5]

&nbsp;

****コレクションの別名****

すべてのエイリアスされた[コレクションのグループ][6]が利用可能なコレクションの一覧に表示されるようになりました。従って、他のコレクションのように名前を選ぶだけです。UIは領域を節約するために、デフォルトでコアの一覧も非表示にします。

[<img class="aligncenter size-large wp-image-2404" src="https://cdn.gethue.com/uploads/2015/03/search-aliases-1024x198.png" alt="search-aliases" width="1024" height="198" data-wp-pid="2404" />][7]

&nbsp;

****検索アプリのみを有効にする****

Hueは[標準のSolr API][8]のみを使用します。これは、任意のSolrまたはSolr Cloudのセットアップが、ダッシュボードUIから利益を得ることができることを意味します。これは[検索アプリ][9]のみを表示するようにHueをカスタマイズして、数回のクリックで開始する方法です！

[<img class="aligncenter size-large wp-image-2312" src="https://cdn.gethue.com/uploads/2015/03/search-only-1024x530.png" alt="search-only" width="1024" height="530" data-wp-pid="2312" />][10]

&nbsp;

****ダッシュボードのエクスポートとインポート****

これは、私たちが任意のHueドキュメントをの[エクスポート/インポート][11]のビルトインサポートするまでの、既存のダッシュボードを他のインストール環境に[バックアップまたは移動][12]するための新しい方法です。

[<img class="aligncenter size-large wp-image-2405" src="https://cdn.gethue.com/uploads/2015/03/search-export-1024x353.png" alt="search-export" width="1024" height="353" data-wp-pid="2405" />][13]

&nbsp;

****さて、次は！****

ローリングタイムラインを簡単に設定するための日付ウィジェット、より多くの統計と分析ファセット、さらに多くが登場する予定です！

また、３クリックの操作でコレクションのインデックスを作成するための[インデクサデザイナー][14]の刷新も、現在進行中です。

Happy Searching!

&nbsp;

いつものように、コメントとフィードバックは [hue-user][15] メーリングリストや[@gethue][16]までお気軽に！

 [1]: https://gethue.com/search-app-enhancements-explore-even-more-data/
 [2]: https://cdn.gethue.com/uploads/2015/03/search-create-menu.png
 [3]: https://cdn.gethue.com/uploads/2015/03/search-and-up.png
 [4]: https://cdn.gethue.com/uploads/2015/03/search-2d-map.png
 [5]: https://cdn.gethue.com/uploads/2015/03/search-multi-names.png
 [6]: http://blog.cloudera.com/blog/2013/10/collection-aliasing-near-real-time-search-for-really-big-data/
 [7]: https://cdn.gethue.com/uploads/2015/03/search-aliases.png
 [8]: https://cwiki.apache.org/confluence/display/solr/Searching
 [9]: https://gethue.com/solr-search-ui-only/
 [10]: https://cdn.gethue.com/uploads/2015/03/search-only.png
 [11]: https://issues.cloudera.org/browse/HUE-1660
 [12]: https://gethue.com/export-and-import-your-search-dashboards/
 [13]: https://cdn.gethue.com/uploads/2015/03/search-export.png
 [14]: https://gethue.com/analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr/
 [15]: http://groups.google.com/a/cloudera.org/group/hue-user
 [16]: https://www.google.com/url?q=https%3A%2F%2Ftwitter.com%2Fgethue&sa=D&sntz=1&usg=AFQjCNFSK0PmjkpMhs1SAQLUx4hheDzfmA