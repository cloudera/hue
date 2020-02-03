---
title: 新しいSQLエディタを持つ Hue 3.10が公開されました！
author: Hue Team
type: post
date: 2016-05-13T03:40:42+00:00
url: /hue-3-10-with-its-new-sql-editor-is-out/
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
sf_custom_excerpt:
  - |
    ビッグデータ愛好家の皆さん、こんにちは
    Hueチームは、すべての貢献者のおかげでHue 3.10 がリリースできて嬉しく思います！
categories:
  - Hue 3.10
  - Release

---
ビッグデータ愛好家の皆さん、こんにちは

&nbsp;

Hueチームは、すべての貢献者のおかげでHue 3.10 がリリースできて嬉しく思います！ [<img class="aligncenter size-full wp-image-2988" src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" alt="hue-logo (copy)" width="85" height="63" data-wp-pid="2988" />][1]

このリリースでフォーカスしていたのは、新しいSQLユーザーエクスペリエンスとパフォーマンスのコアを用意することでした。[3.9][2]の上に[2000コミット][3]以上が行われました！[tarballのリリース][4]を手に入れ展開して下さい！

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://www.dropbox.com/s/fuay07dll4v6bdz/hue-3.10.0.tgz" target="_blank"><br /> <span class="text">Download</span><br /> </a>
</p>

どんな変更が行われたのか、詳細な説明は下記をご覧下さい。すべての変更については[リリースノート][3]や[マニュアル][5] を参照してください。

近日公開の詳細及びビデオチュートリアルシリーズも作業中です！

## SQLエディタ

[<img class="aligncenter size-large wp-image-3988" src="https://cdn.gethue.com/uploads/2014/03/sql-editor-1024x535.png" alt="sql-editor" width="1024" height="535" data-wp-pid="3988" />][6]

  * 完全に刷新
  * [任意の種類のSQLをサポート、他のSQLデータベースとの統合][7]
  * クエリ：マルチクエリ、検索と置換、ライブ履歴、折りたたみ、フォーマット、テーブルアシスト
  * 結果：固定ヘッダ、列にスクロールし、グラフ作成、エクセル/ CSVでダウンロード
  * [値のオートコンプリート、ネスとされたタイプ][8]

## SQLブラウザ

[<img class="aligncenter size-large wp-image-3991" src="https://cdn.gethue.com/uploads/2016/04/sql-browser-1024x536.png" alt="sql-browser" width="1024" height="536" data-wp-pid="3991" />][9]

  * 速度[、統計の表示と使いやすさのためにUIを刷新][10]
  * 単一ページのアプリ
  * 多くのデータベースとテーブル用に最適化

## ホーム

[<img class="aligncenter size-large wp-image-4042" src="https://cdn.gethue.com/uploads/2016/05/home2-1024x502.png" alt="home2" width="1024" height="502" data-wp-pid="4042" />][11]

  * フォルダとディレクトリ
  * コラボレーションのための共有ドキュメント
  * ドキュメントのエクスポートとインポート

## Spark

[<img class="aligncenter size-large wp-image-3481" src="https://cdn.gethue.com/uploads/2015/10/notebook-october-1024x512.png" alt="notebook-october" width="1024" height="512" data-wp-pid="3481" />][12]

  * その成功のため、Livyは専用リポジトリに移動されてされています: <https://github.com/cloudera/livy>
  * [バッチのJar、Pythonおよびストリーミングジョブを投入するためにLivy Spark RESTジョブサーバーAPIを使用する方法][13]
  * [SparkのRDDとコンテキストを共有するためにLivy Spark RESTジョブサーバーAPIを使用する方法][14]
  * [いくつかのインタラクティブなCurlとSparkを行うためにLivy Spark RESTジョブサーバーAPIを使用する方法][15]

## Search

[<img class="aligncenter size-large wp-image-3977" src="https://cdn.gethue.com/uploads/2014/04/search-grid-plot-1024x331.png" alt="search-grid-plot" width="1024" height="331" data-wp-pid="3977" />][16]

  * [HueはSolrのSuggestersをサポートし、データの検索が容易になります！Suggesterはクエリの自動補完可能なリストを提案することによりユーザーを支援します][17]
  * グリッドウィジェット内の結果はSQLエディタのようにプロットすることができます。これは検索クエリによって返された行をクリックして視覚化するのに最適です。

## セキュリティ＆スケーラビリティ

[<img class="aligncenter size-full wp-image-3744" src="https://cdn.gethue.com/uploads/2016/02/meta-quick.png" alt="meta-quick" width="814" height="266" data-wp-pid="3744" />][18]

  * [パフォーマンスチューニング][19]
  * SolrのSentry権限版
  * タイムアウトでは、`idle_session_timeout seconds`後に非アクティブユーザーはログアウト
  * オプションで、`login_splash_html`によりログインでのカスタムセキュリティスプラッシュ画面
  * [TLS証明書チェーン][20] がHUEのサポート
  * SAML 
      * `key_file_password`でkey_fileのパスワードを導入
      * `xmlsec_binary`を変更することでxmlsec1バイナリをカスタマイズ
      * [SAMLのユーザー名マッピング][21]をカスタマイズ 。また、ログイン時にグループの同期をサポート
  * [Dockerにより1分でHue入門][22]
  * [HiveまたはImpalaとなりすまし(Impersonation)でLDAPまたはPAMパススルー認証][23]
  * [hue.iniの設定ではなくファイルのスクリプトにパスワードを保存][24]

## Oozie

[<img class="aligncenter size-large wp-image-3999" src="https://cdn.gethue.com/uploads/2016/04/hue-workflows-1024x521.png" alt="hue-workflows" width="1024" height="521" data-wp-pid="3999" />][25]

  * 外部ワークフローグラフ：この機能はファイルブラウザのフォームから投入されたワークフローだけではなく、CLIから投入されたワークフローのグラフが見ることができる
  * Dryrun Oozieジョブ：<tt>Dryrun オプション</tt>は指定されたプロパティを持つワークフロー/コーディネーター/バンドルジョブをの実行をテストし、ジョブを作成しない
  * タイムゾーンの改善：現在ダッシュボード上のすべての時刻はブラウザのタイムゾーンのデフォルトで、コーディネーター/バンドルの投入では、もうUTC時間は必要ない
  * 失敗時に自動的にメールで送信：現在各Kill nodeにはオプションのEmailアクションが組み込まれているKill nodeが呼び出される場合のカスタムメッセージを挿入するために Kill nodeを編集

（ [詳細を読む][26]）

## HDFS

[<img class="aligncenter size-full wp-image-3960" src="https://cdn.gethue.com/uploads/2014/04/fb-summary-icon.png" alt="fb-summary-icon" width="450" height="333" data-wp-pid="3960" />][27]

ディスク容量の消費、クォータとディレクトリおよびファイルの数にアクセスするにはファイルまたはディレクトリを右クリック

#### 

## チュートリアル

[<img class="aligncenter size-large wp-image-3109" src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-22.37.38-1024x326.png" alt="Spark Table" width="1024" height="326" data-wp-pid="3109" />][28]

  * [Hadoopのノートブックとスパーク＆SQLを使用したベイエリアのバイクシェア分析][29]パート1
  * [Hadoopのノートブックとスパーク＆SQLを使用したベイエリアのバイクシェア分析][30]パート2
  * [Oozieでシェルアクションを使用する][31]
  * [OozieでSparkアクションを使用する][32]

## カンファレンス

[<img class="aligncenter size-large wp-image-3478" src="https://cdn.gethue.com/uploads/2015/11/IMG_5690-1024x768.jpg" alt="IMG_5690" width="1024" height="768" data-wp-pid="3478" />][33]

Big Data Budapest Meetup, [Big Data Amsterdam][34], [Hadoop Summit San Jose][35] および [Big Data LA][36]で講演ができたのは嬉しいことでした。

  * [Spark Summit Europe：サービスとしてインタラクティブなSparkのためのREST Job Serverの構築][37]
  * [Solr SF Meetup：あなたのビッグデータの対話的な検索と視覚化][38]
  * [Big Data Scala by the Bay：あなたのブラウザでインタラクティブなSpark][39]

## チームの避暑

[<img class="aligncenter size-large wp-image-3579" src="https://cdn.gethue.com/uploads/2015/12/2015-11-20-11.50.09-1024x768.jpg" alt="2015-11-20 11.50.09" width="1024" height="768" data-wp-pid="3579" />][40]

  * [ベトナム][41]、賑やかなホーチミン市、banh mi、pho bo、暖かい海水、豪華な天候
  * [スペインのビーチとアムステルダム][42]
  * オランダの[ブルメンダール][43]でチューリップやビールは偉大だった

&nbsp;

## **さて次は！**

次の版（Hue 3.11、第3四半期の終わりを想定）では、SQLの改善、ジョブの監視とクラウドの統合に焦点を当てる予定です。

Hue 4の設計も「ビッグデータのためのExcel」同等になることを目標に継続しています。新鮮な新しい外観、すべてのアプリケーションの統合、データを摂取するためのウィザード&#8230;あなたは高速なビッグデータのクエリとプロトタイピングのための単一のUIで、完全なプラットフォーム（SQL、検索、Spark、摂取（インジェスト））が使用できるようになります！

&nbsp;

その先へ！

&nbsp;

すべてのプロジェクトの貢献者の皆様、フィードバックの送信や[hue-user][44]メーリングリストや[@gethue][45]にご参加いただいている皆様、いつもありがとうございます！

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://gethue.com/hue-3-9-with-all-its-improvements-is-out/
 [3]: http://cloudera.github.io/hue/docs-3.10.0/release-notes/release-notes-3.10.0.html
 [4]: https://dl.dropboxusercontent.com/u/730827/hue/releases/3.10.0/hue-3.10.0.tgz
 [5]: http://cloudera.github.io/hue/docs-3.10.0/index.html
 [6]: https://cdn.gethue.com/uploads/2014/03/sql-editor.png
 [7]: https://gethue.com/custom-sql-query-editors/
 [8]: https://gethue.com/assist-and-autocomplete-improvements/
 [9]: https://cdn.gethue.com/uploads/2016/04/sql-browser.png
 [10]: https://gethue.com/browsing-hive-tables-data-and-metadata-is-getting-faster-and-prettier/
 [11]: https://cdn.gethue.com/uploads/2016/05/home2.png
 [12]: https://cdn.gethue.com/uploads/2015/10/notebook-october.png
 [13]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-submitting-batch-jar-python-and-streaming-spark-jobs/
 [14]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-sharing-spark-rdds-and-contexts/
 [15]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark-2-2/
 [16]: https://cdn.gethue.com/uploads/2014/04/search-grid-plot.png
 [17]: https://cwiki.apache.org/confluence/display/solr/Suggester
 [18]: https://cdn.gethue.com/uploads/2016/02/meta-quick.png
 [19]: https://gethue.com/performance-tuning/
 [20]: https://issues.cloudera.org/browse/HUE-2582
 [21]: https://github.com/romainr/custom_saml_backend
 [22]: https://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/
 [23]: https://gethue.com/ldap-or-pam-pass-through-authentication-with-hive-or-impala/
 [24]: https://gethue.com/storing-passwords-in-script-rather-than-hue-ini-files/
 [25]: https://cdn.gethue.com/uploads/2016/04/hue-workflows.png
 [26]: https://gethue.com/oozie-improvements-in-hue-3-10/
 [27]: https://cdn.gethue.com/uploads/2014/04/fb-summary-icon.png
 [28]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-22.37.38.png
 [29]: https://gethue.com/bay-area-bike-share-analysis-with-the-hadoop-notebook-and-spark-sql/
 [30]: https://gethue.com/bay-area-bike-share-data-analysis-with-spark-notebook-part-2/
 [31]: https://gethue.com/use-the-shell-action-in-oozie/
 [32]: https://gethue.com/use-the-spark-action-in-oozie/
 [33]: https://cdn.gethue.com/uploads/2015/11/IMG_5690.jpg
 [34]: https://gethue.com/harness-the-power-of-spark-and-solr-in-hue-big-data-amsterdam-v-2-0-meeetup/
 [35]: https://gethue.com/hadoop-summit-san-jose-2015-interactively-query-and-search-your-big-data/
 [36]: https://gethue.com/big-data-day-la-solr-search-with-spark-for-big-data-analytics-in-action-with-hue/
 [37]: https://gethue.com/spark-summit-europe-building-a-rest-job-server-for-interactive-spark-as-a-service/
 [38]: https://gethue.com/solr-sf-meetup-interactively-search-and-visualize-your-big-data/
 [39]: https://gethue.com/big-data-scala-by-the-bay-interactive-spark-in-your-browser/
 [40]: https://cdn.gethue.com/uploads/2015/12/2015-11-20-11.50.09.jpg
 [41]: https://gethue.com/team-retreat-in-vietnam/
 [42]: https://gethue.com/team-retreat-in-spain-amsterdam/
 [43]: https://gethue.com/mini-team-retreat-in-bloemendaal/
 [44]: http://groups.google.com/a/cloudera.org/group/hue-user
 [45]: https://twitter.com/gethue