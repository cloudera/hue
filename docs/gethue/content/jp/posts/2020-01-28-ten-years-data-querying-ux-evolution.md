---
title: Hue によるデータクエリ体験の 10 年間の進化
author: Romain
type: post
date: 2020-01-28T00:00:00+00:00
url: /blog/2020-01-28-ten-years-data-querying-ux-evolution/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
#  - Version 4.7

---

[Hue](http://gethue.com/) は10周年を迎えました。Hueは、Apache Hadoop が主流になる前のまだ初期段階だった時に作成されました(詳細は [Hadoop is Dead. Long live Hadoop](https://medium.com/@acmurthy/hadoop-is-dead-long-live-hadoop-f22069b264ac) のHadoopストーリーをご覧ください)。

Hueは元々Cloudera Managerの一部であり、プロプライエタリかつ管理者により重点をおいていましたが、その後[バージョン 0.3](https://docs.gethue.com/releases/release-notes-0.3.0/)で独自の[オープンソース](https://github.com/cloudera/hue)プロジェクトに移行しました。Hueはデスクトップのようなアプリケーションから現代的な単一ページのSQLエディタへと徐々に進化しました(現在は[バージョン4.6](https://docs.gethue.com/releases/release-notes-4.6.0/) です)。

継続的な繰り返しを通して、Hue はその主な目的である「データプラットフォームの使いやすさを促進する」という点で改善を続けました。ユーザーのベースは、主にクエリしたデータを見る人で構成されています。一例として、

* アドホックな質問に答えるデータアナリスト
* 使用状況の統計を見るプログラムマネージャー
* データアプリを構築する IT/SQL 開発者
* システムのユーザービリティ全体を調べるデータアーキテクト
* データウェアハウスのテーブル作成を育成するデータエンジニア

2番目のカテゴリーは、ジョブのログを表示、HDFS や AWS S3 のような分散ファイルシステムへのデータのアップロード、ワークフローの作成、検索ダッシュボードの作成、クエリの最適化を行いたいなどの技術的なユーザーです。

![Hue 1 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-1.png)

Hue 1 (2009) - Apache Hive エディタ、Hadoop のファイルブラウザ、ジョブブラウザーを備えたデスクトップ感覚のアプリケーション。

![Hue 2 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-2.png)
Hue 2 (2012) - フラットなデザイン、データプラットフォームに高度なSQLエディタ、適切なセキュリティを備えた15以上の新しいアプリケーション/コネクターを追加 (テーブルのブラウジング、ワークフローの構築、検索ダッシュボードなど)

![Hue 3 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-3.png)
Hue 3 (2013) - 単一のエクスペリエンスにアプリケーションを集約および相互リンクして、単一ページのエディタ、およびさらに強力なSQLインテリジェンスを提供

![Hue 4 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-4.png)
Hue 4 (2017) - Hue はインターフェースを大幅に改良して、モダンでシンプルな単一ページになった。スマートなリコメンドによるSQLのインテリジェンス、リスク警告、データカタログの統合を備えた、SQLインテリジェンスの次のステップ

## より多くのユーザーとより多くのSQL
Cloudera (CDH) と Hortonworks (HDP) ディストリビューションをCDP (Cloudera Data Platform, [Data Center](https://www.cloudera.com/products/cloudera-data-platform/cdp-data-center.html) またはクラウドで利用可能)に統合することで、Hueはどこにでもあり、さらに多くのユーザーが利用できるようになりました。

* 1000人以上の複合的な顧客 (Fortune 500 社の重要な一部を含む)
* Hue経由で毎日数10万件のSQLクエリが実行されている

アップストリームのHueは、AWS EMR, IBM Open Data Hubなどの他のいくつかのディストリビューションにも含まれており、活発なコミュニティがあります。

![Hue 4.6 screenshot](https://cdn.gethue.com/uploads/2020/01/hue-4.6.png)
Hue 4.6 (2019) - コンポーネント化が継続され、クラウドでのSQLクエリとファイルの閲覧のためデータウェアハウスの統合を強化

2020年に予定されているHue 5はさらにデータウェアハウスに特化しており、最高の SQL クラウドエディタを提供することに注力しています。

* まず、Apache Hive と Apache Impala SQL エンジンのサポートがより深くなっています。SQLインターフェースも安定したコンポーネントに改良されており、Apache Calcite ファミリーやApache Phoenix, Apache Druid, Apache Flink SQL などを簡単に受け入れられます。より高度なクエリ共有と同様に、スマートなインテリジェンスとクエリ最適化のためのアシスタントとのコラボレーションを強化しています。
* 次に「クラウド対応」であり、コンテナのスケールアップとスケールダウンの自動化されたインフラの世界にうまく適合します。Kubernetes 上のHue の最初のバージョンは既に出荷されており、より大規模でよりシンプルな運用管理ができるようになっています。

Hueの10年間にわたる進化のシリーズのパート2では、SQLクラウドエディタノクエリ機能についてさらに詳しく掘り下げます。それまでは、このページまたは[フォーラム](https://discourse.gethue.com/) に気軽にコメントして、[quick start](https://docs.gethue.com/quickstart/) で SQL のクエリを行なってください！


Romain, from the Hue Team
