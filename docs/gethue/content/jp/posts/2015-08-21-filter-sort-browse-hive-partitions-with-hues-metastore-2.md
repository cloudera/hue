---
title: HueのメタストアアプリでHiveのパーティションをフィルタ、ソート、ブラウズする
author: Hue Team
type: post
date: 2015-08-21T13:35:45+00:00
url: /filter-sort-browse-hive-partitions-with-hues-metastore-2/
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
sf_custom_excerpt:
  - 最新のHueのリリースでは、メタストアはパーティション化されたHiveテーブルの優れたコントロールを提供しています。Hiveテーブルのパーティション化はフルテーブルスキャンを回避することにより、Hiveが管理しているテーブルのクエリのパフォーマンス向上のための優れた戦略です。
sf_social_sharing:
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
  - File Browser
  - Hive
  - Hue 3.9
  - Metastore
  - Tutorial
  - Video

---
最新のHueのリリースでは、メタストアはパーティション化されたHiveテーブルの優れたコントロールを提供しています。Hiveテーブルのパーティション化はフルテーブルスキャンを回避することにより、Hiveが管理しているテーブルの[クエリのパフォーマンス向上][1]のための優れた戦略です。

しかし、パーティション化は、データが既にHDFSに存在していたり、またはHive以外のサービスによって管理される外部テーブルに便利です。これらのケースでは、パーティションの場所は（テーブルのベース位置を取り、各パーティションの名前=値のパストークンを付加する）デフォルトの動的Hiveパーティションの場所に適合しない場合があり、パーティションの場所として有効な任意のデータパスを取ることができます。

例えば、次のパーティションで作成された&#8221;blog&#8221;と呼ばれる外部テーブルを取り上げてみましょう:

<pre class="brush: sql; gutter: false; title: ; notranslate" title="">CREATE TABLE blog (title STRING, body STRING, pubdate DATE) PARTITIONED BY (dy STRING, dm STRING, dd STRING, dh STRING);
</pre>

私たちは、必要に応じて特定のパーティションの場所にデータを追加するためにテーブルを変更し続けることができます:

<pre class="brush: sql; gutter: false; title: ; notranslate" title="">ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-01', dh='2015-01-01 00') LOCATION '/user/jennykim/2015/01/01/00';
ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-01', dh='2015-01-01 12') LOCATION '/user/jennykim/2015/01/01/12';
ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-02', dh='2015-01-02 00') LOCATION '/user/jennykim/2015/01/02/00';
ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-02', dh='2015-01-02 12') LOCATION '/user/jennykim/2015/01/02/12';
ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-03', dh='2015-01-03 00') LOCATION '/user/jennykim/2015/01/03/00';
ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-03', dh='2015-01-03 12') LOCATION '/user/jennykim/2015/01/03/12';
ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-04', dh='2015-01-04 00') LOCATION '/user/jennykim/2015/01/04/00';
ALTER TABLE blog ADD PARTITION (dy='2015', dm='2015-01', dd='2015-01-04', dh='2015-01-04 12') LOCATION '/user/jennykim/2015/01/04/12';
</pre>

テーブルのパーティションの場所に関係なく、現在Hueのメタストアは、テーブルビューから「パーティションを表示する」リンクをクリックして、テーブル内のすべてのパーティションを閲覧することができます。デフォルトでは、パーティションのビューは名前で（あるいは新しい順で、日付でパーティション化されている場合）逆順にパーティションをソートし、最初の250のパーティションを表示します。

しかし、パーティションの特定のセットを探しているなら、「フィルタを追加」のリンクをクリックしてフィルタパラメータを選択して、それから「フィルタ」ボタンをクリックしてパーティションの値をフィルタリングすることができます！クエリを絞り込むために必要に応じて複数のパーティションのフィルタが追加されることに注意してください、また、アルファベットの昇順でパーティション結果を取得するためのデフォルトのソート順を無効にすることができます。

{{< youtube phkigNhDzuE >}}

[Hueチーム][2]による[HueのメタストアアプリでHiveのパーティションをフィルタ、ソート、ブラウズ][3]

最後に、パーティションの場所をファイルブラウザで表示させる「View Parttion Files」のリンクをクリックして任意のパーティションのデータファイルを表示することができます。

[<img class="aligncenter size-large wp-image-2822" src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21-1024x224.png" alt="Metastore Partition View" width="1024" height="224" data-wp-pid="2822" />][4]

[<img class="aligncenter size-large wp-image-2821" src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.43.48-1024x564.png" alt="Partition File Browser" width="1024" height="564" data-wp-pid="2821" />][5]

HueはそのままシームレスにHiveのデータを操作するための柔軟性を提供しています。いつものように、コメントとフィードバックは [hue-user][6] メーリングリストや[@gethue][7]までお気軽に！

 [1]: http://blog.cloudera.com/blog/2014/08/improving-query-performance-using-partitioning-in-apache-hive/
 [2]: https://www.youtube.com/channel/UCTuTkR-hLNN59uqT9bqIa_Q
 [3]: https://youtube.com/watch?v=phkigNhDzuE
 [4]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21.png
 [5]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.43.48.png
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue