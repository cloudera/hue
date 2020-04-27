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
  - Editor / Notebook
  - HBase
  - Hue 4.5

---
[Apache Phoenix][1] は、非リレーショナル分散データストアである [Apache HBase][2]拡張した素晴らしいアドオンです。[HBase Browser][3]上に、[Editor][4] はデータをクエリするためのより一般的な構文を提供します。キー/バリューストアであることでSQLにはさまざまなイディオムがあり、Hue のSQL UXの機能を完全にサポートするにはまだいくつかの洗練作業が必要なことにご注意ください。

この Phoenix についての最初のブログ記事では、[Phoenix&#8217;s 15-minute tutorial][5] のチュートリアルに従って、その後 Editor から US_POPULATION テーブルをクエリします。

HueはJDBC、または [SQL Connector documentation][6] に記載されているSqlAlchemyインターフェースをサポートしています。私たちはSqlAlchemyを洗濯します。

Hueのホストにて:

    ./build/env/bin/pip install pyPhoenix

続いて desktop/conf/hue.ini 設定ファイルセクションにて:

    [notebook]
    [[interpreters]]
    [[[phoenix]]]
    name = phoenix
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

    select * from us_population limit 10

[<img class="aligncenter wp-image-6025" src="https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png" alt="" width="1076" height="580" />][7]

[<img class="aligncenter wp-image-6026" src="https://cdn.gethue.com/uploads/2019/07/phonix_select_shell.png" alt="" width="769" height="415" />][8]

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

**3** Phoenix は Apache Calcite に従っています。[SQL autocomplete][9] の改善にご協力ください。

**4** セミコロン &#8216;;&#8217; をスキップします

**5** セキュリティはテストしていません

**6** いくつかの既知の問題は [Phoenix SqlAlchemy connector page ][10]にリストしています

このCloudera の [Phoenix in CDH][11] 発表のブログ記事で Apache Phoenix の昨日の詳細をご覧ください。

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
 [6]: https://docs.gethue.com//administrator/configuration/editor/#phoenix
 [7]: https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png
 [8]: https://cdn.gethue.com/uploads/2019/07/phonix_select_shell.png
 [9]: https://docs.gethue.com//developer/parsers/
 [10]: https://github.com/Pirionfr/pyPhoenix
 [11]: https://blog.cloudera.com/blog/2019/07/apache-phoenix-for-cdh/
