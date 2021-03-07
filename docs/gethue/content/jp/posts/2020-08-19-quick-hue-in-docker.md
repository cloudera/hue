---
title: Docker で Hue をクイックスタートして任意のデータベースにクエリを行う
author: admin
type: post
date: 2020-08-19T00:00:00+00:00
url: /quickstart-hue-in-docker/
ampforwp-amp-on-off:
  - default
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
sf_author_info:
  - 1
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
categories:
  - Version 4
#  - Version 4.8
tags:
  - cloud
  - container
  - docker

---

あらゆるデータウェアハウスに数分でクエリを実行します！

このチュートリアルでは既存の MySQL データベースを使用して、クエリを実行する [Apache Hive](https://hive.apache.org/) データウェアハウスを指すように Hue を設定します。

![Autocomplete and context assist](https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif)

**注記** Hive とは別のウェアハウスを探している場合は、すべての[他のコネクタ](https://docs.gethue.com/administrator/configuration/connectors/) をご確認下さい。

2つの重要な概念があります。

* 永続性: Hue は、同時リクエストをサポートする MySQL のようなトランザクションを持つ既存のデータベースを必要とし、サーバー停止時に登録されたユーザー、保存されたクエリ、権限の共有を失わない必要があります。
* 計算: これはコンテナ内でサーバーイメージを実行することにより行われます。これは、負荷や高可用性の要件に応じて、起動、停止、複数回のレプリケーションを行うことができます。

最新の Hue のコンテナをプルして、その中でシェルを開いてみましょう。

    docker run -it -p 8888:8888 gethue/hue:latest /bin/bash

これにより、Hue のインストールのホームディレクトリである `/usr/share/hue` に入ります。では設定ファイルを開いてみましょう。

    apt-get install -y vim

    vim desktop/conf/hue.ini

まず、Hue が MySQL、PostgreSQL、あるいは Oracle のようなトランザクションをサポートするリレーショナルデータベースを背後に持つことを確認します。ここでは MySQL を使用し、`[[database]]` セクションに資格情報を設定します。

    [desktop]
    [[database]]
    host=demo.gethue.com  # Use 127.0.0.1 and not localhost if on the same host
    engine=mysql
    user=hue
    password=password
    name=hue

**注記** ご自身の MySQL データベースを使用して本番環境に対応した Hue を起動する別の方法として、[Docker compose](https://github.com/cloudera/hue/tree/master/tools/docker/hue#docker-compose) を使用する方法があります。

次に`[beeswax]` と `[notebook]` セクションに次のブロックを追加して、アクセス可能なサーバーで実行している Apache Hive インスタンスにクエリを実行できるようにします。実行している HiveServer2 をお持ちでない場合は、開発用のクイックスタート(Docker を使用し[素早く開始する方法](https://docs.gethue.com/developer/development/#first-sql-queries) をチェックしてみてください。

    [beeswax]
    hive_server_host=demo.gethue.com

    [notebook]
    [[interpreters]]
    [[[hive]]]
    name=Hive
    interface=hiveserver2

**注記** ボーナスとして、Hue のデータベースを指す MySQL インタープリタを自由に追加してみてください。問題なく自身をクエリすることができます。

    [[[mysql]]]
    name=MySQL
    interface=sqlalchemy
    options='{"url": "mysql://hue:password@demo.gethue.com:3306/hue"}'

ここで別の端末から `docker ps` を使用して Hue のコンテナのIDを識別し、その状態をコミットして停止後も設定を記憶させます。

    docker ps

    docker commit 368f0d568a5f hue-hive

**注記** `docker commit` を使用する別の方法としては、Docker イメージの外部に hue.ini 設定ファイルを保持し、コンテナを起動する際にシンプルに内部にマウントする方法があります。これは [Docker How-to](https://github.com/cloudera/hue/tree/master/tools/docker/hue#configuration) に記載されています。

これで、保存したコンテナを起動して、[localhost:8888](localhost:8888) の Hue インターフェースを公開することができます。

    docker run -it -p 8888:8888 hue-hive ./startup.sh


これでいよいよ[SQL クエリ](https://docs.gethue.com/user/querying/) を実行する時が来ました！

![Hue login page](https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png)

フィードバックはありますか？コメントはこのページまたは [@gethue](https://twitter.com/gethue) までお気軽に！

Romain from the Hue Team
