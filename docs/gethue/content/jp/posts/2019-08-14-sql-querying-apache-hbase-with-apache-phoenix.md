---
title: Apache Phoenixを使用したApache HBaseのSQLでのクエリ
author: Hue Team
type: post
date: 2019-08-14T01:09:14+00:00
url: /sql-querying-apache-hbase-with-apache-phoenix/
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
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_custom_excerpt:
  - Apache Phoenix は、非リレーショナル分散データストアである Apache HBase拡張した素晴らしいアドオンです。HBase Browser上に、Editor はデータをクエリするためのより一般的な構文を提供します。
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
  - Version 4
#  - Version 4.8

---
[Apache Phoenix][1] は、非リレーショナル分散データストアである [Apache HBase][2]拡張する素晴らしいアドオンです。[HBase Browser][3]上で、Hue の [Editor][4] はデータをクエリするためのより一般的な構文を提供します。キー/バリューストアであることでSQLにはさまざまな構文があり、Hue のSQL UXの機能を完全にサポートするにはまだいくつかの洗練作業が必要なことにご注意ください。

この Phoenix についてのブログ記事では、[Phoenix's 15-minute tutorial][5] のチュートリアルに従い、その後 Editor から US_POPULATION テーブルをクエリします。

Hue は [SQL Connector documentation](https://docs.gethue.com/administrator/configuration/connectors/#apache-phoenix)に記載されている SqlAlchemy インターフェイスを介して Phoenix をサポートしています。[HUE-9367](https://issues.cloudera.org/browse/HUE-9367) により、コネクターは Hue に同梱されているのですぐにご利用いただけます。

Hue のホストにて:

    ./build/env/bin/pip install pyPhoenix

続いて desktop/conf/hue.ini 設定ファイルセクションで Phoenix インタープリターを追加するだけです:

    [notebook]
    [[interpreters]]
    [[[phoenix]]]
    name=phoenix
    interface=sqlalchemy
    options='{"url": "phoenix://sql-phoenix.gethue.com:8765/"}'

その後 queryserver を開始します:

    >phoenix-queryserver
    ...
    19/07/24 20:55:13 INFO util.log: Logging initialized @1563ms
    19/07/24 20:55:13 INFO server.Server: jetty-9.2.z-SNAPSHOT
    19/07/24 20:55:14 INFO server.ServerConnector: Started ServerConnector@662b4c69{HTTP/1.1}{0.0.0.0:8765}
    19/07/24 20:55:14 INFO server.Server: Started @1793ms
    19/07/24 20:55:14 INFO server.HttpServer: Service listening on port 8765.

これで HBase をクエリする準備ができました!

    SELECT * FROM us_population LIMIT 10

<a href="https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png"><img src="https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png" /></a>

<a href="https://cdn.gethue.com/uploads/2019/07/phonix_select_shell.png"><img src="https://cdn.gethue.com/uploads/2019/07/phonix_select_shell.png" /></a>

注

**1** 既存の HBase のテーブルをビューにマップする必要があります

<pre><code class="bash">0: jdbc:phoenix:&gt; CREATE VIEW if not exists "analytics_demo_view" ( pk VARCHAR PRIMARY KEY, "hours"."01-Total" VARCHAR );
Error: ERROR 505 (42000): Table is read only. (state=42000,code=505)
--&gt;
0: jdbc:phoenix:&gt; CREATE Table if not exists "analytics_demo" ( pk VARCHAR PRIMARY KEY, "hours"."01-Total" VARCHAR );
</code></pre>

**2** テーブルは Phoenix では大文字で見えます。始めるには Phoenix でテーブルを作成する方がシンプルです。

<pre><code class="bash">Error: ERROR 1012 (42M03): Table undefined. tableName=ANALYTICS_DEMO (state=42M03,code=1012)
--&gt;
0: jdbc:phoenix:&gt; select * from "analytics_demo" where pk = "domain.0" limit 5;
</code></pre>

**3** Phoenix は Apache Calcite に従っています。[SQL autocomplete](https://docs.gethue.com/developer/development/#sql-parsers) で改善にご協力ください。

**4** UI （およびベースとなる SQLAlchemy API) は 'ANY 名前空間' と 'empty/Default' 名前空間を区別することができません。

このCloudera の [Phoenix in CDH](https://blog.cloudera.com/blog/2019/07/apache-phoenix-for-cdh/) のブログ記事で Apache Phoenix の機能の詳細をご覧ください。

<div>
  フィードバックや質問があれば、この記事または <a href="https://twitter.com/gethue">@gethue</a>までコメントをお願いします!
</div>

<div>
</div>

 [1]: https://phoenix.apache.org/
 [2]: https://hbase.apache.org/
 [3]: https://gethue.com/improved-hbase-cell-editor-history/
 [4]: https://gethue.com/sql-editor/
 [5]: https://phoenix.apache.org/Phoenix-in-15-minutes-or-less.html
