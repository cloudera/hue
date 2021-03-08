---
title: ログストリームを SQL クエリし、計算結果を別のストリームに出力する
author: Romain
type: post
date: 2021-01-10T00:00:00+00:00
url: /blog/sql-querying-live-kafka-logs-and-sending-live-updates-with-flink-sql/
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
  - Tutorial
  - Version 4.9

---

*この記事は、当初 https://medium.com/data-querying/live-sql-querying-live-logs-and-sending-live-updates-easily-e6297150cf92 で公開されました*

Flink SQL, ksqlDB, Hue Editor を介した Apache Kafka データストリームからのログ解析チュートリアル

データのストリームに対するリアルタイムクエリは、[以前の記事](http://localhost:1314/blog/tutorial-query-live-data-stream-with-flink-sql/) でデモしたように、強力な分析を行うための現代的な方法です。今回は Web Query Editor で生成された独自のログをクエリすることで、よりパーソナライズされたシナリオを見ていきます。

まず、以降で紹介するオープンソースプロジェクト、特に[Flink Version 1.12](https://flink.apache.org/news/2020/12/10/release-1.12.0.html) 、[SQL gateway](https://github.com/ververica/flink-sql-gateway/) そして同じく[Hue Editor](http://gethue.com/) の改善のための全てのコミュニティに感謝します。
目標は、現在の SQL の機能と、データのストリームでの対話的なクエリを構築する際の使いやすさをデモすることです。

![直すQuerying a data log stream via Flink SQL and ksqlDB](https://cdn-images-1.medium.com/max/3690/1*968GTr1dtA1zfKTCVk-V9A.gif)

*Flink SQL と ksqlDB によるデータログストリームのクエリ*

## アーキテクチャー

この記事にはライブデモのセットアップ手順があるので、ローカルで簡単に試せるようになっています。

Hue Editor からの生ログ..

    [29/Dec/2020 22:43:21 -0800] access  INFO   172.21.0.1 romain - "POST /notebook/api/get_logs HTTP/1.1" returned in 30ms 200 81

.. これは[Fluentd](https://www.fluentd.org/) を使って収集され、access/INFO 以外の行をフィルタリングした後、Kafka のトピックに直接[forward](https://docs.fluentd.org/output/kafka) されます（データをシンプルに保つため)。

    {"container_id":"7d4fa988b26e2034670bbe8df3f1d0745cd30fc9645c19d35e8004e7fcf8c71d","container_name":"/hue","source":"stdout","log":"[29/Dec/2020 22:43:21 -0800] access  INFO   172.21.0.1 romain - \"POST /notebook/api/get_logs HTTP/1.1\" returned in 30ms 200 81"}

その後データは Kafka のトピックから抽出され、ログインしたユーザーごとに 10 秒間の[ローリングウィンドウ](https://ci.apache.org/projects/flink/flink-docs-release-1.12/concepts/timely-stream-processing.html#windowing) で何回 API コールが行われているかを計算する、長時間実行されるクエリに変換される前に対話的に分析されます。

![Live stream analysis Architecture](https://cdn-images-1.medium.com/max/2000/1*AdoZQxikyBixQSCOUwiRpg.png)

*ライブストリーム分析のアーキテクチャー*

## デモ

Docker Compose の[設定](https://raw.githubusercontent.com/romainr/query-demo/master/stream-sql-logs/docker-compose.yml) を取得して全てを開始します:

    mkdir stream-sql-logs
    cd stream-sql-logs

    wget https://raw.githubusercontent.com/romainr/query-demo/master/stream-sql-logs/docker-compose.yml

    docker-compose up -d
    >
    Creating network "stream-sql-logs_default" with the default driver
    Creating hue-database                 ... done
    Creating stream-sql-logs_jobmanager_1 ... done
    Creating stream-sql-logs_fluentd_1    ... done
    Creating stream-sql-logs_zookeeper_1   ... done
    Creating ksqldb-server                 ... done
    Creating hue                           ... done
    Creating stream-sql-logs_taskmanager_1 ... done
    Creating flink-sql-api                 ... done
    Creating stream-sql-logs_kafka_1       ... done

その後、これらの URL が利用可能になります:

* [http://localhost:8888/](http://localhost:8888/) Hue Editor
* [http://localhost:8081/](http://localhost:8081/) Flink Dashboard

全てを止めるには以下のようにします:

    docker-compose down

## シナリオ

Web Editor とやりとりしている間にウェブログが生成されています。それらのサブセットを、Flink SQLを介してクエリする Kafka トピックに取り込みます。ksqlDB は、1日の終わりに全ての SQL のSELECTとINSERTが標準の Kafka トピックを通過していることを証明するために使用されます。

もう一度 [TUMBLE](https://ci.apache.org/projects/flink/flink-docs-release-1.12/dev/table/sql/queries.html#group-windows) 関数を使用して、簡単に集計のライブウィンドウを作成します。

ユーザー名によるグループ化を表示するために、二人の別々のユーザー(‘demo’ と ‘romain’) としてログインしました。

Flink の目新しさの一つは新しい[UPSERT into Kafka](https://ci.apache.org/projects/flink/flink-docs-release-1.12/dev/table/connectors/upsert-kafka.html#key-and-value-formats) コネクターで、ローリング集計したデータを Kafka に送り返すことができるようになります。これにより、トピックから単純に読み取ることができるレポーティングやアラートシステムによって、さらに下方での消費が可能になります。

![Calculating and inserting a rolling window of live stats into a Kafka Topic](https://cdn-images-1.medium.com/max/3296/1*G1nW-KMRFrWl7g6MTcCYiA.png)*ライブ統計のローリングウィンドウを計算して Kafka のトピックに挿入する*

追記すると、実際の日付とHTTPコードのフィールドを抽出したり、カウントがある閾値を超えた／超えなかった時にアラートメッセージを出力することでより精細にクエリを行うことができ、その上に[ライブアプリケーション](https://flink.apache.org/2020/07/28/flink-sql-demo-building-e2e-streaming-application.html) を構築するのに最適です。

エディタの優れた点の一つは、REGEXP_EXTRACT, DATE_FORMAT などの[SQL関数](https://ci.apache.org/projects/flink/flink-docs-release-1.12/dev/table/functions/systemFunctions.html) をインタラクティブにいじることができることです。

## SQL

こちらが Query Editor で入力した SQL ソースです。

<script src="https://gist.github.com/romainr/dc5087f26c3bcaf90906b83c489f2413.js"></script>

<script src="https://gist.github.com/romainr/fff457cd69d7328cce8652e93f555692.js"></script>

## Et voila! （さぁ、どうぞ！）

フィードバックや質問はありますか？お気軽にこちらまでコメントお願いします！

これらのプロジェクトも全てオープンソースであり、フィードバックや貢献を歓迎します。

Hue Editor の場合は、[フォーラム](https://discourse.gethue.com/) や [Github issues](https://github.com/cloudera/hue/issues) がその良い場になっています。より洗練されたSQL自動補完やコネクタ、Web Socket、Celery Task serverとの統合が改善策として挙げられています。

前に進みましょう!

Romain
