---
title: SQLによるHBaseへの対話的なクエリ - 技術講演（Tech Talk)
author: Hue Team
type: post
date: 2021-04-05T00:00:00+00:00
url: /blog/2021-04-05-interactively-querying-hbase-via-sql-tech-talk
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
  - Version 4.10
  - Phoenix

---
Apache PhoenixとHue Web SQL エディタを用い、HBaseに格納されたデータをSQLクエリで活用できるようにして、ユーザベースを拡大しましょう。

2021年4月1日（ジョークではありません ;）、[Apache HBase](https://hbase.apache.org/) のテーブルにSQLクエリを実行するための基盤技術について、[Apache Phoenix](https://phoenix.apache.org/)プロジェクトによって主催された[技術公演](https://phoenix.apache.org/tech_talks.html)を行いました（素晴らしい企画でした）。

スライドをご覧下さい:

[**Hue SQL エディタでPhoenixクエリの実行**](https://drive.google.com/file/d/1-3OwisGp1D5za2ukFW7DukrQkF3AJg9O/view)

HBaseに馴染みのない方は、あらゆる種類のレコードをリアルタイムに保存・更新することに特化した、巨大なテーブルを想像してみてください。しかし、どうやって操作するのでしょうか？

SQLによるクエリは、低レベルの API (HBase シェルコマンドや HBase オブジェクトを使用した Java プログラミングなど) を使用するよりも、はるかに短く、簡単にロジックを実装/維持することができます。SQLのクエリを HBase アプリケーションに埋め込むことは非常に効率的で、テーブルの作成やデータの挿入などは、英語に近い普遍的な宣言型の言語で数行だけで済みます。

SQL エディタを使用すると、快適なブラウザから対話的な方法でこれらのクエリをすばやく編集し、テストすることができ（つまり、VPN を使用したり、シェルを開いたり、どのホストを指すのか、どのように認証するのかを覚えたりする必要はありません）、または自動補完、スキーマのブラウザ、コラボ機能の全てのおかげで、手順や「どこにな人があるのか」を覚えることができます。


![](https://cdn-images-1.medium.com/max/2000/1*2ADf80ARS-sZEl9PZIh1hQ.png)

要するに、Phoenix SQL方言をサポートする[Web SQLインターフェース](https://gethue.com/sql-querying-apache-hbase-with-apache-phoenix/)を採用することで、データをクエリしてドメイン知識を活用できるユーザーの数が、一握りから数百へと増える可能性があるということです。

講演の最後には、ライブでログ解析デモを行いました。このデモは[以前に公開したように](https://medium.com/data-querying/phoenix-brings-sql-to-hbase-and-let-you-query-kafka-data-streams-8fd2edda1401)、ローカルで1分で実行することができます。

注: SQLエディタを[スクラッチパッドのコンポーネント](https://docs.gethue.com/developer/components/scratchpad/)として利用できるようにする努力も並行して行っており、これにより埋め込みのSQLの編集がより簡単になります。

早速使ってみてください！

</br>
</br>

ご意見や質問がありましたらお気軽にこちら、あるいは <a href="https://github.com/cloudera/hue/discussions">Discussions</a> までコメントして下さい。<a href="https://docs.gethue.com/quickstart/">quick start</a> で SQL をクエリして下さい!


どうぞよろしくお願いします！

Romain from the Hue Team
