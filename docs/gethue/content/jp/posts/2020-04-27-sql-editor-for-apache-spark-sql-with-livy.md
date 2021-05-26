---
title: Livy を使用した Apache Spark SQL 用の SQL エディタ
author: Romain
type: post
date: 2020-04-27T00:00:00+00:00
url: /blog/quick-task-sql-editor-for-apache-spark-sql-with-livy/
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
#  - Version 4.8

---

## Spark SQL

[Spark SQL](https://spark.apache.org/docs/latest/sql-programming-guide.html) は、Spark アプリ内にクリーンなデータクエリーのロジックを埋め込むのに便利です。Hue には便利なエディタが付属しているので、SQL スニペットの開発が簡単になります。

ドキュメントに記載されている通り、Spark SQL はさまざまな[コネクター](https://docs.gethue.com/administrator/configuration/connectors/#apache-spark-sql)が一緒になっています。ここでは Livy を紹介します。

[Apache Livy](https://livy.incubator.apache.org/) は実行中の Spark インタープリターへのブリッジを提供するので、SQL、pyspark、scala のスニペットを対話的に実行できるようにします。

[hue.ini](https://docs.gethue.com/administrator/configuration/) で、API の URL を設定します。

    [spark]
    # The Livy Server URL.
    livy_server_url=http://localhost:8998

そしていつものように、設定したインタープリターを確認してください。

    [notebook]
    [[interpreters]]
    [[[sparksql]]]
    name=Spark SQL
    interface=livy

そうすることで、エディターが表示されます。

![Hue Spark Sql Editor](https://cdn.gethue.com/uploads/2020/04/editor_spark_sql_livy.png)

Hue を使用する利点の一つは、HDFS / S3 / Azure 用の[ファイルブラウザー](https://docs.gethue.com/user/browsing/#data) と、完全なセキュリティ(Kerberosと[Knox IdBroker](https://docs.cloudera.com/runtime/7.1.0/cdp-security-overview/topics/security_how_identity_federation_works_in_cdp.html) の統合を介して実際のユーザーの資格情報を使用することさえも)です。

![Hue Phoenix Editor](https://cdn.gethue.com/uploads/2016/08/image2.png)

今後の改善点を紹介します。

* データベース/テーブル/列の自動補完は現在空です
* SQL文法の自動補完は[拡張できます](https://docs.gethue.com/developer/development/#sql-parsers)
* ミニSQLエディターのポップアップを可能にする[SQL Scratchpad](https://docs.gethue.com/developer/api/#scratchpad) モジュールは現在進行中です


フィードバックやご質問はありますか？こちら、または<a href="https://discourse.gethue.com/">フォーラム</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> で気軽にコメントして、SQLクエリのクイックスタートをしましょう！

Romain from the Hue Team
