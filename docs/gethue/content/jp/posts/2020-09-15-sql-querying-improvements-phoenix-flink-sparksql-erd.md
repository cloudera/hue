---
title: "SQL クエリの改良：Phoenix, Flink, SparkSql, ERD テーブル..."
author: Hue Team
type: post
date: 2020-09-15T00:00:00+00:00
url: /blog/sql-querying-improvements-phoenix-flink-sparksql-erd-table/
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
データクランチャーズの皆さん、こんにちは

SQL クエリをもっと簡単に実行したいと思っていませんか？ここでは、次の Hue のリリースで予定されている様々なクエリの改善点を紹介します！

## 新しいデータベース

Hue は、[Apache Phoenix](https://phoenix.apache.org/), [Apacke Flink](https://flink.apache.org/) SQL、 および [Apache Spark](https://spark.apache.org/) SQL ([Apache Livy](https://livy.apache.org/) 経由) により、より洗練された経験を積んでいます。

{{< youtube fKHD-fOdDY0 >}}

### Apache Phoenix

Apache Phoenix は、SQL を介して [Apache HBase](https://hbase.apache.org/) データベースに簡単にクエリができるようにします。現在、この[統合](/sql-querying-apache-hbase-with-apache-phoenix/)は完全に動作しており、いくつかのコーナーケース(例えば、デフォルトの Phoenix データベースの扱い、左側のアシストでのテーブルと列の一覧、なりすましのサポートなど...) が修正されています。

### Apache Flink SQL

データストリームへの[SQL クエリ](https://ci.apache.org/projects/flink/flink-docs-stable/dev/table/sql/) のための Apache Flink のサポートは成熟してきており、エディタとの最初の統合も行われています。

**注** [KsqlDB](https://docs.gethue.com/administrator/configuration/connectors/#ksqldb) のサポートも同様の機能を共有（ライブクエリと結果グリッド）しているため、進展しています。

### Apache SparkSql

SparkSql は非常に人気があり、Apache Livy を介して SQL クエリを実行する際の[改善](/blog/quick-task-sql-editor-for-apache-spark-sql-with-livy/)がなされています。従来の SqlAlchemy [コネクタ](https://docs.gethue.com/administrator/configuration/connectors/#apache-spark-sql) や HiveServer Thrift も動作していることにご注意ください。

## UDF / 関数

**動的一覧**

エディタには全ての関数が一覧されているわけではありません。（セッションや企業レベルで登録されているもの、Hue のリリース後に作成されたもの、不足しており[追加可能](https://docs.gethue.com/developer/development/#sql-parsers)なものなど...)

現在、エディタはデータベースに関数の完全なリストを問い合わせ、不足している関数を `General` セクションに追加します。

![UDF Assist](https://cdn.gethue.com/uploads/2020/09/right-assist-udf.png)
![UDF Dynamic Assist](https://cdn.gethue.com/uploads/2020/09/assist-udf-dynamic.png)

**引数**

引数の位置関係が理解できるようになり、人気のある関数の定数の引数も利用できるようになりました。例えば、引数の２番目の位置の日付変換のためのフォーマットがユーザーに提示されるようになりました。

![UDF argument positions](https://cdn.gethue.com/uploads/2020/09/udf-trunc-args.png)

## 自動補完

**独自のパーサーを開発**

パーサーは [Apache Calcite](https://calcite.apache.org/) SQL サブセットをサポートすることを第一の目標とし、より小さな再利用可能なピース [structure.json](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/parse/jison/sql/generic/structure.json) で抽出されています。[Parser SDK](https://docs.gethue.com/developer/development/#sql-parsers#structure) にはより詳細な情報があります。

例えば、`structure.json` は SQL パーサー全体で再利用可能な一般的な文法と特殊な文法のピースで構成されています。

structure.json

    [...],
    "../generic/select/select.jison",
    "../generic/select/select_conditions.jison",
    "select/select_stream.jison",
    "../generic/select/union_clause.jison",
    "../generic/select/where_clause.jison",
    [...]

select_stream.jison

    SelectStatement
    : 'SELECT' 'STREAM' OptionalAllOrDistinct SelectList
    ;

    SelectStatement_EDIT
    : 'SELECT' 'STREAM' OptionalAllOrDistinct 'CURSOR'
    {
      if (!$3) {
        parser.suggestKeywords(['ALL', 'DISTINCT']);
      }
    }
    ;

独立した大きなパーサーを構築するというスケーラブルではないという戦略から、文法操作を共有するパーサーを構築するという戦略へと移行しています。

![Parser Evolution v2 Beta](https://cdn.gethue.com/uploads/2020/09/parser_evolution.png)

**スケジュールされた Hive クエリ**

Hive 4 は SQL 構文による[スケジューリングクエリ](https://cwiki.apache.org/confluence/display/Hive/Scheduled+Queries)をネイティブにサポートしています。

    * create
    create scheduled query Q1 executed as joe scheduled '1 1 * * *' as update t set a=1;
    * change schedule
    alter scheduled query Q1 cron '2 2 * * *'
    * change query
    alter scheduled query Q1 defined as select 2
    * disable
    alter scheduled query Q1 set disabled
    * enable
    alter scheduled query Q1 set enabled
    * list status
    select * from sysdb.scheduled_queries;
    * drop
    drop scheduled query Q1

なお [HUE-3797](https://issues.cloudera.org/browse/HUE-3797) にはミニ UI が付属しており、クエリの監視やスケジューリングが2回クリックするだけでできるようになります。(右のアシストパネルを参照)

![Integrated Scheduling](https://cdn.gethue.com/uploads/2020/09/scheduled_queries.png)

**Limit Nの自動補完**

自動補完の際に 'LIMIT' を追加すると、実際のサイズも提案されるようになりました。

![UDF argument positions](https://cdn.gethue.com/uploads/2020/09/sql-limit-n.png)

**列キーのアイコン**

列の値が別のテーブルの別の列を指している場合、[外部キー](https://gethue.com/2019-11-13-sql-column-assist-icons/)を表示するための追加アイコンが利用できます。

![Assist Foreign Keys](https://cdn.gethue.com/uploads/2020/03/assist_foreign_keys_icons.png)

    CREATE TABLE person (
      id INT NOT NULL,
      name STRING NOT NULL,
      age INT,
      creator STRING DEFAULT CURRENT_USER(),
      created_date DATE DEFAULT CURRENT_DATE(),

      PRIMARY KEY (id) DISABLE NOVALIDATE
    );

    CREATE TABLE business_unit (
      id INT NOT NULL,
      head INT NOT NULL,
      creator STRING DEFAULT CURRENT_USER(),
      created_date DATE DEFAULT CURRENT_DATE(),

      PRIMARY KEY (id) DISABLE NOVALIDATE,
      CONSTRAINT fk FOREIGN KEY (head) REFERENCES person(id) DISABLE NOVALIDATE
    );

サンプルのポップアップでは、リレーションシップのナビゲートもサポートされるようになりました。

{{< youtube 4xgjvM51Rnw >}}

## ERD テーブル

列と外部キーのリンクを視覚的に一覧表示することで、SQL クエリを作成する際のスキーマと関係をより早く理解することができます。[ドキュメントページ](https://docs.gethue.com/developer/components/er-diagram/)のライブデモをぜひご覧ください。

![ERD Table Components](https://cdn.gethue.com/uploads/2020/09/erd_table_viz.png)

**注** 新しい共有可能なコンポーネントシステムについては、今後のブログ記事で詳しく紹介する予定です。

## スマートな提案

ローカルアシスタントは、JOIN の自動補完の提案や、単純なリスクアラート（例えば LIMIT 節の欠落など）を提供します。

![Popular joins suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png)

これはベータ機能です。有効にするには `hue.ini` で次のようにします。

    [medatata]
    [[optimizer]]
    # Requires Editor v2
    mode=local

## インポーター

新しい SQL テーブルの作成が簡単になるように、データインポートウィザードでいくつかの修正を行いました。以前の[記事](https://gethue.com/querying-exploring-the-instacart-dataset-part-1-ingesting-the-data/)で詳しくご覧いただけます。

![Table Create Wizard](https://cdn.gethue.com/uploads/2019/03/insta_importer_step1.png)

## コネクタ付きエディタv2

これらはベータ版の機能であり、まだかなりの量の研鑽が必要ですが、十分に安定しているので多くのユーザーに試していただきフィードバックを送っていただきたいと考えています。

クエリの事項はより良い安定性と複数のクエリを同時に実行できるように置き換えられています。新しいバージョンの詳細はベータ後に公開予定です。

![Editor v2 Beta](https://cdn.gethue.com/uploads/2020/09/editor-v2-beta.png)

`hue.ini` で有効にする方法は次のとおりです。

    [notebook]
    enable_notebook_2=true

    [desktop]
    enable_connectors=true

**注** [https://demo.gethue.com/](https://demo.gethue.com/) では新しいエディタが有効になっています。




フィードバックや質問はありますか？このページや <a href="https://discourse.gethue.com/">Forum</a> にコメントください。<a href="https://docs.gethue.com/quickstart/">quick start</a> すぐに SQL のクエリを始められます!


その先へ!

Romain from the Hue Team
