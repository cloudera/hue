---
title: Apache Flink SQL 用の SQL エディタ
author: Romain
type: post
date: 2020-05-06T00:00:00+00:00
url: /blog/sql-editor-for-apache-flink-sql/
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

# Flink SQL Editor

これは Flink 用 SQL エディタの非常に初期のバージョンです。

目標は、Flink SQL のクエリを実行する方法をデモすることです。新しい Flink SQL ゲートウェイプロジェクトを使用して、Docker コンテナ内のライブデータを持つ Flink クラスターを指すようにします。Hue は Flink のテーブルをクエリするための SQL エディタとして使用されます。

Flink [SQL](https://ci.apache.org/projects/flink/flink-docs-master/dev/table/sql/queries.html#queries) と [継続的な](https://ci.apache.org/projects/flink/flink-docs-master/dev/table/streaming/dynamic_tables.html#continuous-queries) クエリの詳細についてはリンク先をご覧ください。

{{< youtube fKHD-fOdDY0 >}}

## セットアップ

Flink 1.10 クラスターであれば動作し、デモは [Ververica SQL Training](https://github.com/ververica/sql-training) をベースにしています。これは簡単な[セットアップ方法](https://github.com/ververica/sql-training/wiki/Setting-up-the-Training-Environment) を説明しています。

    git clone https://github.com/ververica/sql-training.git
    cd sql-training
    docker-compose up -d

そうすると [http://localhost:8081](http://localhost:8081) が表示されるようになります。

![Flink Dashboard](https://cdn.gethue.com/uploads/2020/05/flink_dashboard.png)

ここでは SQL クライアントコンテナを起動し、ゲートウェイを内部にインストールします (ゲートウェイには FLINK_HOME が必要なので、ローカルの Flink をインストールしないようにします）が、これはローカルまたは別のコンテナで行うことができます。

    docker-compose exec sql-client bash

ゲートウェイの[リリース](https://github.com/ververica/flink-sql-gateway/releases) を取得します。

    cd /opt
    wget https://github.com/ververica/flink-sql-gateway/releases/download/v0.1-snapshot/flink-sql-gateway-0.1-SNAPSHOT-bin.zip
    unzip flink-sql-gateway-0.1-SNAPSHOT-bin.zip
    cd flink-sql-gateway-0.1-SNAPSHOT

    echo $FLINK_HOME

続いて、別のシェルから Flink SQL の設定をゲートウェイにコピーして、デフォルトでデモのテーブルを取得するようにします。

    wget https://raw.githubusercontent.com/romainr/flink-sql-gateway/master/docs/demo/sql-gateway-defaults.yaml

    docker cp sql-gateway-defaults.yaml sql-training_sql-client_1:/opt/flink-sql-gateway-0.1-SNAPSHOT/conf/

これでコンテナのシェルに戻り、開始することができます。

    cd bin
    ./sql-gateway.sh --library /opt/sql-client/lib

`CTRL-Z` でサーバーをバックグラウンドにして、

    bg

セットアップを検証するためにいくつかのコマンドを実行します。

    curl localhost:8083/v1/info
    > {"product_name":"Apache Flink","version":"1.10.0"}

    curl -X POST localhost:8083/v1/sessions -d '{"planner":"blink","execution_type":"streaming"}'
    > {"session_id":"7eea0827c249e5a8fcbe129422f049e8"}


**注**

SQL クライアントコンテナ内ではなく SQL ゲートウェイにデプロイすることも可能です。

1. FLINK_HOME が設定された Flink の[バイナリーパッケージ](https://www.apache.org/dyn/closer.lua/flink/flink-1.10.0/flink-1.10.0-bin-scala_2.11.tgz) を持っていること

2. `$FLINK_HOME/conf/flink-conf.yaml` で実際の jobmanager のアドレス `jobmanager.rpc.address` を更新する

3. `sql-gateway-defaults.yaml` の2つのアドレスのプロパティを変更する

<pre>
    server:
      # The address that the gateway binds itself.
      bind-address: 172.18.0.7
      # The address that should be used by clients to connect to the gateway.
      address: 172.18.0.7
</pre>

## クエリエディタ

Hue の[コネクター](https://docs.gethue.com/administrator/configuration/connectors/) セクションに説明しているように、Flink インタープリターを追加しています。

    [notebook]

    [[interpreters]]

    [[[flink]]]
      name=Flink
      interface=flink
      options='{"api_url": "http://172.18.0.7:8993"}'

クライアントのコンテナにゲートウェイをセットアップしていて、ローカルホストから接続したい場合は、そのバインドIPを SQL クライアントコンテナのIPで更新する必要があります。

ゲートウェイサービスの IP は実行しているコンテナの1つです。`sql-training_sql-client_1` を確認してIPを取得します。

    docker ps
    > CONTAINER ID        IMAGE                                                COMMAND                  CREATED              STATUS              PORTS                                                NAMES
    > 638574b31cd6        fhueske/sql-training:1-FLINK-1.10-scala_2.11   "/docker-entrypoint.…"   About a minute ago   Up About a minute   6123/tcp, 8081/tcp                                   sql-training_sql-client_1
    > 59d1627c412a        wurstmeister/kafka:2.12-2.2.1                        "start-kafka.sh"         About a minute ago   Up About a minute   0.0.0.0:9092->9092/tcp                               sql-training_kafka_1
    > 6711c0707f1e        flink:1.10.0-scala_2.11                              "/docker-entrypoint.…"   About a minute ago   Up About a minute   6121-6123/tcp, 8081/tcp                              sql-training_taskmanager_1
    > 6a8149af6c1e        flink:1.10.0-scala_2.11                              "/docker-entrypoint.…"   About a minute ago   Up About a minute   6123/tcp, 0.0.0.0:8081->8081/tcp                     sql-training_jobmanager_1
    > 3de8275dff26        wurstmeister/zookeeper:3.4.6                         "/bin/sh -c '/usr/sb…"   About a minute ago   Up About a minute   22/tcp, 2888/tcp, 3888/tcp, 0.0.0.0:2181->2181/tcp   sql-training_zookeeper_1
    > a28cee7627a0        mysql:8.0.19                                         "docker-entrypoint.s…"   About a minute ago   Up About a minute   3306/tcp, 33060/tcp                                  sql-training_mysql_1

    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' sql-training_sql-client_1
    > 172.18.0.7

![Flink SQL Editor](https://cdn.gethue.com/uploads/2020/05/flink_editor_v1.png)

そして、ここで左側のアシストを使用してテーブルを参照し、簡単にクエリするためにドラッグ＆ドロップするだけでなく、より強力なクエリを書くためのオートコンプリートを活用しています。

    SELECT taxiId, isStart
    FROM default_database.Rides
    LIMIT 100
    ;

    SELECT
      psgCnt,
      COUNT(*) AS cnt
    FROM Rides
    WHERE isInNYC(lon, lat) AND isStart
    GROUP BY
      psgCnt
    ;

Flink のダッシュボードは通常のジョブとして SQL のクエリを表示します。

![Flink Job Dashboard](https://cdn.gethue.com/uploads/2020/05/flink_dashboard_one_query.png)

## 今後

この最初のバージョンでは、商用環境の準備をするために数多くの[将来的な繰り返し](https://github.com/cloudera/hue/blob/master/docs/designs/apache_flink.md) がありますが、ベースはそこに到達しています。

[Apache Calcite](https://calcite.apache.org/docs/reference.html) をベースにした[SQL オートコンプリート](https://ci.apache.org/projects/flink/flink-docs-master/dev/table/sql/queries.html#supported-syntax) の改善が注目されています。Hue にはより良い[構文](https://docs.gethue.com/developer/development/#sql-parsers) and even ships with a default [Flink SQL dialect](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/jison/sql/flink).

Another one coming soon will be a more user friendly display of the live data in the result grid.


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> Live SQL querying!


Romain from the Hue Team
