---
title: HueのSQLエディタのKubernetesのデータベースへの接続をクイックチェックする
author: Romain
type: post
date: 2020-09-30T00:00:00+00:00
url: /blog/quick-checking-sql-connection-from-kubernetes-pod/
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
  - Version 4.9

---
Kubernetes の世界で、HueがSQLデータベースに接続できない理由を素早く確認する方法の1つをみてみましょう。

以前に、[Kubernetes](/hue-in-kubernetes/) や [Docker](/quickstart-hue-in-docker/) で Hue を実行する方法をドキュメントにしました。

考え方としては、コマンドラインでデータベース固有のコマンドをシェルを使用して、いくつかのクエリを送信してみるというものです。

[Apache Hive](https://docs.gethue.com/administrator/configuration/connectors/#apache-hive) は例として使用しているデータウェアハウスです(が、`psql`, `mysql`, など、Hue が[接続できる](https://docs.gethue.com/administrator/configuration/connectors/) 任意のデータベースでも同じように動作します) .

これは現在の Hue のポッドに余分なファイルをインストールしますが、Hue のサービスと全く同じ場所からやりとりをテストすることができます（したがって、`接続性`や`認証`の問題をトラブルシュートするのに適しています）。

&nbsp;

まず、SQL エディタで Hive のバージョンを確認します。

    SELECT version()

    > 2.3.2 r857a9fd8ad725a53bd95c1b2d6612f9b1155f44d

次に Hue のポッドを一覧します。

    kubectl get pods

    > NAME                                        READY   STATUS      RESTARTS   AGE
    hue-758466dc77-wpcx8                        2/2     Running     0          22h
    ingress-nginx-controller-5d6fbbddb6-8kd86   1/1     Running     0          23h
    postgres-hue-64c9cc8744-dpk47               1/1     Running     1          47d

いずれかに接続します。

    kubectl exec -it hue-758466dc77-wpcx8 hue -- bash

次に、以下から同じ Hive のバージョンのクライアントファイルを取得します。

* https://archive.apache.org/dist/hadoop/core
* https://archive.apache.org/dist/hive

そしてそれらをインストールします。

    sudo apt-get install wget
    wget https://archive.apache.org/dist/hadoop/core/hadoop-2.7.4/hadoop-2.7.4.tar.gz
    wget https://archive.apache.org/dist/hive/hive-2.3.2/apache-hive-2.3.2-bin.tar.gz

    tar -xvzf hadoop-2.7.4.tar.gz
    tar -xvzf apache-hive-2.3.2-bin.tar.gz

    export HADOOP_HOME=`pwd`/hadoop-2.7.4
    export HIVE_HOME=`pwd`/apache-hive-2.3.2-bin
    export JAVA_HOME=/usr/lib/jvm/java-1.11.0-openjdk-amd64

    PATH=$PATH:$HIVE_HOME/bin

これで接続の準備ができました。

    beeline -u 'jdbc:hive2://172.21.0.3:10000'

    > SLF4J: Class path contains multiple SLF4J bindings.
    SLF4J: Found binding in [jar:file:/usr/share/hue/apache-hive-2.3.2-bin/lib/log4j-slf4j-impl-2.6.2.jar!/org/slf4j/impl/StaticLoggerBinder.class]
    SLF4J: Found binding in [jar:file:/usr/share/hue/hadoop-2.7.4/share/hadoop/common/lib/slf4j-log4j12-1.7.10.jar!/org/slf4j/impl/StaticLoggerBinder.class]
    SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.
    SLF4J: Actual binding is of type [org.apache.logging.slf4j.Log4jLoggerFactory]
    Connecting to jdbc:hive2://172.21.0.3:10000
    Connected to: Apache Hive (version 2.3.2)
    Driver: Hive JDBC (version 2.3.2)
    Transaction isolation: TRANSACTION_REPEATABLE_READ
    Beeline version 2.3.2 by Apache Hive
    0: jdbc:hive2://172.21.0.3:10000> SHOW TABLES;
    +--------------------+
    |      tab_name      |
    +--------------------+
    | about              |
    | amandine_test      |
    | city_cases         |
    | cricketer          |
    | cust1              |
    | cust2              |
    | customer           |
    | customers          |
    | student_info       |
    | ........           |
    | web_logs           |
    | yash_contact_test  |
    +--------------------+
    52 rows selected (0.098 seconds)

... そして、あなたの SQL ユーザは再び[セルフサービスクエリ](/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/) を開始することができます！

![Hue Editor](https://cdn.gethue.com/uploads/2020/09/hue-4.8.png)

[beeline コマンドライン](https://cwiki.apache.org/confluence/display/Hive/HiveServer2+Clients#HiveServer2Clients-Beeline%E2%80%93CommandLineShell) については Hive Wiki で詳しく解説しています。


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!
フィードバックや質問はありますか？このページや <a href="https://discourse.gethue.com/">Forum</a> にコメントください。<a href="https://docs.gethue.com/quickstart/">quick start</a> SQLクエリのクイックスタートをしましょう！

その先へ!

Romain from the Hue Team
