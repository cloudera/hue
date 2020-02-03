---
title: Oozieエディタの改良、より良いパフォーマンス＆改善されたSpark UIを持つHue 3.8を公開！
author: Hue Team
type: post
date: 2015-04-25T02:18:50+00:00
url: /httpgethue-comhue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
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
    ビッグデータを食べ続ける皆さん、
    HueチームはHue3.8と、Hue 3.8で改良されたOozieエディタと良好なパフォーマンスのリリースを嬉しく思います！
    新しいSpark REST Job ServerとNotebook UIも、それらを試してみたいすべての熱心なSpark開発者向けにベータ版として登場しています。
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
  - Release

---
ビッグデータを食べ続ける皆さん、

&nbsp;

HueチームはHue3.8と、Hue 3.8で改良された[Oozieエディタ][1]と[良好なパフォーマンス][2]のリリースを嬉しく思います！

新しい<a href="https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server" target="_blank">Spark REST Job Server</a>と[Notebook UI][3]も、それらを試してみたいすべての熱心なSpark開発者向けにベータ版として登場しています。

[tarボール][4]が入手できるだけではなく、[ドキュメント][5]と[リリースノート][6]も利用可能です 。このリリースは大きな前進であり、1000以上のコミットから来ています！

&nbsp;

**注意**

[カスタムアプリ][7]をビルドしている場合は[アップグレードガイド][8]に従ってください！

&nbsp;

これらは主要な改善点の概要です（詳細は[Hue 3.8のブログ][9]にあります）：

&nbsp;

**Oozie**

<div id="attachment_2419" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor.png"><img class="size-large wp-image-2419" src="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor-1024x602.png" alt="New Editor (edit mode)" width="1024" height="602" data-wp-pid="2419" /></a>
  
  <p class="wp-caption-text">
    新しいエディタ(編集モード)
  </p>
</div>

&nbsp;

エディタ

  * [新しいデザイン][1]およびOozieに多くの知識は不要
  * [ワークフローのインポート/エクスポートが容易に][10]
  * ワークフローは数十の[新機能][11]をサポート
  * 新しいHiveServer2とSparkアクションのサポート
  * コー​​ディネーターのユーザーエクスペリエンスがシンプルに

&nbsp;

ダッシュボード

  * 手作業で、またはコーディネーターが投入したワークフローを区別する簡単な方法
  * 対応するワークフローとログに対応するサブワークフローのリンク
  * コー​​ディネーターの終了時刻を更新
  * HiveのジョブIDを表示

&nbsp;

[エディタ][1]と[ダッシュボード][12]の詳細についてもご参照ください。

&nbsp;

****安定性/パフォーマンス****

[<img class="aligncenter size-full wp-image-2338" src="https://cdn.gethue.com/uploads/2015/03/with-nginx.png" alt="with-nginx" width="852" height="530" data-wp-pid="2338" />][13]

  * [Hue HA][14]
  * [NGINXによる静的ファイルのキャッシュと実行][2]
  * [Hive 1.1のサポート][15]
  * [Django 1.6へのメジャーアップグレード][8]
  * [Apacheサーバで実行][16]
  * デッドロック数を修正
  * いくつかの非標準のOracle DBの問題を修正

&nbsp;

**Search**

[<img class="aligncenter size-large wp-image-2581" src="https://cdn.gethue.com/uploads/2015/04/search-v2.2-1024x558.png" alt="search-v2.2" width="1024" height="558" data-wp-pid="2581" />][17]

  * 通常のユーザーもダッシュボードを作成することが可能
  * Range & Up ファセット
  * 2Dマップ
  * コレクション別名のクエリ
  * 同じフィールドを使用する複数のウィジェット
  * [検索アプリのみを有効にする][18]
  * [ダッシュボードのエクスポートとインポート][10]

&nbsp;

[より詳細な情報はこちら&#8230;][19]

&nbsp;

**Spark Notebook (beta)**

[<img class="aligncenter size-large wp-image-2565" src="https://cdn.gethue.com/uploads/2015/04/notebook-1-1024x572.png" alt="notebook-1" width="1024" height="572" data-wp-pid="2565" />][20]

  * [新しい REST Spark Job Server][21] (ベータ版)
  * [Notebook Web UI][22] (ベータ版)
  * Scala, Java, Python
  * YARN クラスタ

&nbsp;

**セキュリティ**

[<img class="aligncenter size-large wp-image-2363" src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12-1024x610.png" alt="Screenshot 2015-03-23 16.33.12" width="1024" height="610" data-wp-pid="2363" />][23]

  * ログとSQLエディタ内の機密データ編集（PCI）
  * [HTTPS / SSL設定][24]
  * [LDAP認証とSSLでImpala/Hiveを使用][25]
  * [Pigエディタとセキュリティを備えたHCatalog][26]
  * [SAML 2.0のサポート][27]
  * [LDAPのデバッグ][28]
  * [カスタマイズされた上部のバナーを追加][29]

&nbsp;

**HBase**

[<img class="aligncenter size-large wp-image-2381" src="https://cdn.gethue.com/uploads/2015/03/hbase-1024x525.png" alt="hbase" width="1024" height="525" data-wp-pid="2381" />][30]

  * [Kerberosあり、なしによるなりすまし][31]

&nbsp;

****Hueをインストールするための新しい方法****

  * [EMR][32]
  * [HDP][33]
  * [On a Mac][34]
  * [Ubuntu 14.04][35]

&nbsp;

**会議**

ワシントンDCでの[Lucene Solr Revolution][36]、およびマドリードでの[Big Data Sparinビ][37]での公演は光栄でした。

&nbsp;

## **さて、次は！**

&nbsp;

次のリリース（3.9）は主にSparkとSearchにフォーカスし、[すべてのアプリ][38]で一般的な改善と機能の完全性をもたらすでしょう 。

&nbsp;

並行して、Hue 4のデザインと開発は「ビッグデータのためのExcel」と同等​​になることを目標に話し合っています。新規の新しい外観、全てのアプリケーションの統合、データを取得するためのウィザード&#8230;..は、素早いビッグデータのクエリとプロトタイピングのために、単一のUIで完全なプラットフォームが使用できるようになります！

&nbsp;

さらにその先へ！！

&nbsp;

いつものように、コメントとフィードバックは [hue-user][39] メーリングリストや[@gethue][40]までお気軽に！

&nbsp;

 [1]: https://gethue.com/new-apache-oozie-workflow-coordinator-bundle-editors-2/?lang=ja
 [2]: https://gethue.com/using-nginx-to-speed-up-hue-3-8-0/
 [3]: https://gethue.com/new-notebook-application-for-spark-sql
 [4]: https://dl.dropboxusercontent.com/u/730827/hue/releases/3.8.0/hue-3.8.0.tgz
 [5]: http://cloudera.github.io/hue/docs-3.8.0/index.html
 [6]: http://cloudera.github.io/hue/docs-3.8.0/release-notes/release-notes-3.7.0.html
 [7]: https://gethue.com/app-store/
 [8]: https://gethue.com/developer-guide-on-upgrading-apps-for-django-1-6-2/?lang=ja
 [9]: https://gethue.com/category/hue-3-8/?lang=ja
 [10]: https://gethue.com/export-and-import-your-search-dashboards-2/?lang=ja
 [11]: https://issues.cloudera.org/browse/HUE-2180
 [12]: https://gethue.com/oozie-dashboard-improvements-2/?lang=ja
 [13]: https://cdn.gethue.com/uploads/2015/03/with-nginx.png
 [14]: https://gethue.com/automatic-high-availability-with-hue-and-cloudera-manager/
 [15]: https://gethue.com/hive-1-1-and-impala-2-2-support-2/?lang=ja
 [16]: https://gethue.com/how-to-run-hue-with-the-apache-server/
 [17]: https://cdn.gethue.com/uploads/2015/04/search-v2.2.png
 [18]: https://gethue.com/solr-search-ui-only/
 [19]: https://gethue.com/more-solr-search-dashboards-possibilities-2/?lang=ja
 [20]: https://cdn.gethue.com/uploads/2015/04/notebook-1.png
 [21]: https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server
 [22]: https://gethue.com/new-notebook-application-for-spark-sql-2/?lang=ja
 [23]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12.png
 [24]: https://gethue.com/configure-hue-with-https-ssl/
 [25]: https://gethue.com/how-to-use-hue-with-hive-and-impala-configured-with-ldap-authentication-and-ssl/
 [26]: https://gethue.com/how-to-use-hcatalog-with-pig-in-a-secured-cluster/
 [27]: https://gethue.com/updated-saml-2-0-support/
 [28]: https://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/#t12b
 [29]: https://gethue.com/add-a-top-banner-to-hue/
 [30]: https://cdn.gethue.com/uploads/2015/03/hbase.png
 [31]: https://gethue.com/hbase-browsing-with-doas-impersonation-and-kerberos/
 [32]: http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-hue.html
 [33]: https://gethue.com/hadoop-hue-3-on-hdp-installation-tutorial/
 [34]: https://gethue.com/start-developing-hue-on-a-mac-in-a-few-minutes-2/?lang=ja
 [35]: https://gethue.com/how-to-build-hue-on-ubuntu-14-04-trusty/
 [36]: https://gethue.com/presentation-solr-lucene-revolution-interactively-search-and-visualize-your-big-data/
 [37]: https://gethue.com/big-data-spain-2014-big-data-web-applications-for-interactive-hadoop/
 [38]: https://issues.cloudera.org/secure/IssueNavigator.jspa?mode=hide&requestId=10930
 [39]: http://groups.google.com/a/cloudera.org/group/hue-user
 [40]: https://twitter.com/gethue