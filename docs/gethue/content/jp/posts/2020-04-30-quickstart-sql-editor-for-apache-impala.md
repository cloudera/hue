---
title: Apache Impala 用の SQL エディター
author: Romain
type: post
date: 2020-04-30T00:00:00+00:00
url: /blog/quickstart-sql-editor-for-apache-impala/
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

## Impala SQL

[Apache Impala](https://impala.apache.org/) はデータウェアハウスのための高速な SQL エンジンです。3分で簡単に試してみませんか？その方法は以下の通りです!

### Impala を開始する

まず、システムに docker がインストールされていることを確認してください。次に、Apache [Apache Kudu](https://kudu.apache.org/) の素晴らしい[チュートリアル](https://github.com/apache/kudu/tree/master/examples/quickstart/impala) (これは次回取り上げますが、[Kudu Quickstart](https://kudu.apache.org/docs/quickstart.html) は一見の価値があります) に基づいて次のように実行してください:

    docker run -d --name kudu-impala -p 21000:21000 -p 21050:21050 -p 25000:25000 -p 25010:25010 -p 25020:25020 --memory=4096m apache/kudu:impala-latest impala

その後、`docker ps` は次のように表示するはずです:

    > docker ps
    CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS              PORTS                                                                                                                              NAMES
    fe7b68d167b3        apache/kudu:impala-latest   "/impala-entrypoint.…"   4 seconds ago       Up 3 seconds        0.0.0.0:21000->21000/tcp, 0.0.0.0:21050->21050/tcp, 0.0.0.0:25000->25000/tcp, 0.0.0.0:25010->25010/tcp, 0.0.0.0:25020->25020/tcp   kudu-impala

あとは、実行中のコンテナに入って SQL シェルを実行するだけです。

    > docker exec -it kudu-impala impala-shell

    Starting Impala Shell without Kerberos authentication
    Opened TCP connection to fe7b68d167b3:21000
    Connected to fe7b68d167b3:21000
    Server version: impalad version 3.3.0-RELEASE RELEASE (build 0f840c5a0f5e673c67cbd482e62065fd47b98e1a)
    ***********************************************************************************
    Welcome to the Impala shell.
    (Impala Shell v3.4.0-SNAPSHOT (b0c6740) built on Thu Oct 17 10:56:02 PDT 2019)

    When you set a query option it lasts for the duration of the Impala shell session.
    ***********************************************************************************

そして、いくつかの[SQL命令](https://impala.apache.org/docs/build/html/topics/impala_langref.html)を実行してみます:

    [fe7b68d167b3:21000] default> show tables;
    Query: show tables
    Fetched 0 row(s) in 0.36s
    [fe7b68d167b3:21000] default> create table a (a int);
    Query: create table a (a int)
    +-------------------------+
    | summary                 |
    +-------------------------+
    | Table has been created. |
    +-------------------------+
    Fetched 1 row(s) in 1.31s

    [fe7b68d167b3:21000] default> insert into a values (1);
    Query: insert into a values (1)
    Query submitted at: 2020-04-30 17:42:59 (Coordinator: http://fe7b68d167b3:25000)
    Query progress can be monitored at: http://fe7b68d167b3:25000/query_plan?query_id=cb410a4f8b0b0d6a:1a8a909e00000000
    Modified 1 row(s) in 1.60s

    [fe7b68d167b3:21000] default> select * from a;
    Query: select * from a
    Query submitted at: 2020-04-30 17:43:08 (Coordinator: http://fe7b68d167b3:25000)
    Query progress can be monitored at: http://fe7b68d167b3:25000/query_plan?query_id=7242c5151534b8db:bef9c91000000000
    +---+
    | a |
    +---+
    | 1 |
    +---+
    Fetched 1 row(s) in 0.33s

    [fe7b68d167b3:21000] default> exit

## SQL エディター

クエリアシスタントを使って SQL を入力すると、さらに生産性が高まります。

 上記の `docker ps` でコンテナのIDを取得して、そのIPアドレスを取り上げます。

    > docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 638574b31cd6
    172.17.0.2

Impala はHueと密結合されているので、[hue.ini](https://docs.gethue.com/administrator/configuration/) にはコンテナのホスト名を設定するだけです。

    [impala]
    server_host=172.17.0.2

そして Hue をリスタートすると、エディターが表示されます。

![Hue Impala SQL Editor](https://cdn.gethue.com/uploads/2020/04/hue-4.7.png)


SQL 体験の詳細については、こちらの[ブログ記事](/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/) をご覧ください。


フィードバックやご質問はありますか？こちら、または<a href="https://discourse.gethue.com/">フォーラム</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> で気軽にコメントして、SQLクエリのクイックスタートをしましょう！


Romain from the Hue Team
