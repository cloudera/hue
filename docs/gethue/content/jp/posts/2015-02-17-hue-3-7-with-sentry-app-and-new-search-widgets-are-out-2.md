---
title: Sentryアプリと新しい検索ウィジェットに対応したHue 3.7を公開！
author: Hue Team
type: post
date: 2015-02-17T11:31:41+00:00
url: /hue-3-7-with-sentry-app-and-new-search-widgets-are-out-2/
sf_thumbnail_link_type:
  - link_to_post
sf_thumbnail_type:
  - none
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
    ビッグデータサーファーの皆さん、
    
    HueチームはHue 3.7のリリースと、新しい Sentry App と改良された Search Appの公開を嬉しく思います！
    
    tarball だけでなく、documentation と release notesが利用可能です。新しいアプリを搭載しているうえに、このリリースはかなり機能満載です。これは私たちが受け取った素晴らしいフィードバックとリクエストにより可能となりました！
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
slide_template:
  - default
categories:
  - Release

---
ビッグデータサーファーの皆さん、

HueチームはHue 3.7のリリースと、新しい [Sentry App][1] と改良された [Search App][2]の公開を嬉しく思います！

[tarball][3] だけでなく、[documentation][4] と [release notes][5]が利用可能です。新しいアプリを搭載しているうえに、このリリースはかなり機能満載です。これは私たちが受け取った素晴らしいフィードバックとリクエストにより可能となりました！

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important;" href="https://dl.dropboxusercontent.com/u/730827/hue/releases/3.7.1/hue-3.7.1.tgz" target="_blank"><span class="text">Download 3.7.1 tarball</span></a>
</p>

&nbsp;

これらは主要な改善の一覧です:

**セキュリティ**

[<img class="aligncenter size-large wp-image-1725" src="https://cdn.gethue.com/uploads/2014/10/hue-sentry-1024x541.png" alt="hue-sentry" width="1024" height="541" data-wp-pid="1725" />][6]

  * 新しいSentryアプリ
  * ロールと権限のバルク編集
  * データベースツリーでロールと権限をビジュアライズ/編集
  * WITH GRANT OPTION のサポート
  * どのデータベースとテーブルを見ることができるかを確認するユーザーのなりすまし
  * [詳細はこちら（英語）&#8230;][1]

&nbsp;

**Search（検索）**

[<img class="aligncenter size-large wp-image-1752" src="https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1-1024x596.png" alt="hue-search-v2.1" width="1024" height="596" data-wp-pid="1752" />][7]

  * 3つの新しいウィジェット 
      * ヒートマップ
      * ツリー
      * マーカーマップ
  * フィールド分析
  * ファセットの除外
  * [詳細はこちら（英語][1])[…][2]

&nbsp;

**Oozie**

[<img class="aligncenter size-large wp-image-1767" src="https://cdn.gethue.com/uploads/2014/10/hue-oozie-1024x579.png" alt="hue-oozie" width="1024" height="579" data-wp-pid="1767" />][8]

  * ダッシュボードでアクションをバルクでサスペンド／Kill／リジューム
  * より速いダッシュボード
  * バルクで失敗したコーディネーターインスタンスを再実行
  * [詳細はこちら（英語…][9]

&nbsp;

**Job Browser（ジョブブラウザ）**

YARN用にアプリケーションのKILLボタン

&nbsp;

**File Browser（ファイルブラウザ）**

[<img class="aligncenter size-large wp-image-1741" src="https://cdn.gethue.com/uploads/2014/10/hue-fb-1024x571.png" alt="hue-fb" width="1024" height="571" data-wp-pid="1741" />][10]

  * ACL
  * ドラッグ＆ドロップでのアップロード
  * 履歴のナビゲーション
  * シンプルなインタフェース
  * [詳細はこちら（英語）…][11]

&nbsp;

**HBase**

Kerberosのサポート。 次のステップはなりすまし(impersonation)！

&nbsp;

**Indexer（インデクサ）**

間違ったSolrを指している場合、設定されたZookeeperをピックアップしてヒントを提供。ワンクリックで[サンプルをインストール][12]するのに便利。

&nbsp;

**Hive / Impala**

[<img class="aligncenter size-large wp-image-1787" src="https://cdn.gethue.com/uploads/2014/10/hue-impala-charts-1024x573.png" alt="hue-impala-charts" width="1024" height="573" data-wp-pid="1787" />][13]

  * LDAPパススルー
  * [HiveServer2でのSSL暗号化][14]
  * 新しいグラフ
  * [自動クエリタイムアウト][15]

&nbsp;

**SDK**

私たちはHueプロジェクトの開発が簡単になるようにしようともしています:

  * [コードレビュー][16]
  * [テストの実行][17]
  * [Ubuntu 14.04をサポート][18]
  * [任意のHadoop][19]で設定

&nbsp;

&nbsp;

**さて次は？**

次に計画している機能は、新しくエレガントなOozieワークフローエディタ、より速いパフォーマンスと高可用性（HA）、驚きのアプリ、シンプルなSparkアプリ、SentryとSearchのさらなる統合、山ほどの磨き込みとアイロンがけ。

いつものように、コメントとフィードバックは[hue-user][20] メーリングリストや [@gethue][21]までお気軽に！!

 [1]: https://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/
 [2]: https://gethue.com/search-app-enhancements-explore-even-more-data/
 [3]: https://dl.dropboxusercontent.com/u/730827/hue/releases/3.7.1/hue-3.7.1.tgz
 [4]: http://cloudera.github.io/hue/docs-3.7.0/index.html
 [5]: http://cloudera.github.io/hue/docs-3.7.0/release-notes/release-notes-3.7.0.html
 [6]: https://cdn.gethue.com/uploads/2014/10/hue-sentry.png
 [7]: https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1.png
 [8]: https://cdn.gethue.com/uploads/2014/10/hue-oozie.png
 [9]: https://gethue.com/improved-oozie-dashboard-bulk-manipulate-your-jobs/
 [10]: https://cdn.gethue.com/uploads/2014/10/hue-fb.png
 [11]: https://gethue.com/file-browser-enhancements-hdfs-operations-made-easy/
 [12]: https://gethue.com/hadoop-tutorial-kerberos-security-and-sentry-authorization-for-solr-search-app/
 [13]: https://cdn.gethue.com/uploads/2014/10/hue-impala-charts.png
 [14]: https://gethue.com/hadoop-tutorial-ssl-encryption-between-hue-and-hive/
 [15]: https://gethue.com/hadoop-tutorial-hive-and-impala-queries-life-cycle/
 [16]: https://gethue.com/rbtools-example-how-do-easily-do-code-reviews-with-review-board/
 [17]: https://gethue.com/tutorial-how-to-run-the-hue-integration-tests/
 [18]: https://gethue.com/how-to-build-hue-on-ubuntu-14-04-trusty/
 [19]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [20]: http://groups.google.com/a/cloudera.org/group/hue-user
 [21]: https://twitter.com/gethue