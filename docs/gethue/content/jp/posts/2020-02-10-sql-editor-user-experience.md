---
title: データウェアハウスのための HUE のクエリ体験
author: Romain
type: post
date: 2020-02-10T00:00:00+00:00
url: /blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/
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
#  - Version 4.7

---

[Hue](http://gethue.com/) は [10周年を迎えました](https://jp.gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/)! このシリーズのフォローアップ第2弾では、SQL Cloud エディタとは何かを説明します。

SQL Cloud エディタの上位2つの機能は次の通りです。

* `データのクエリ体験`: SQL クエリアシスタントを提供します。これは、ユーザーのクエリに必要なセルフサービスを行い、データと構文のノウハウを学ぶのに役立ちます。
* `クラウドネイティブ`: サービスの操作を自動化することにより、可能な限り「何も操作しないこと(No-ops)」を提供することで、サービスをスケールします。これには、簡単な実行と監視、容量のオートスケール、自動的なローリングアップグレードなどが含まれます。

この投稿では、エンドユーザーの観点からクエリ体験を詳しく説明します。シリーズ第3弾ではクラウド体験に焦点を当てる予定です。


## SQL データウェアハウスにフォーカス

多くのデータプラットフォームは、通常 [データハブ](https://www.cloudera.com/products/data-hub.html) モデルで構成されます。これは、全てのデータ、計算、およびワークフロースケジューリングやインデキシング、ストリーミングなどのサテライトサービスを全て備えた、中央型のクラスターを意味します。

これは、本格的な Hue を介してアクセスする多くのコンポーネントです。

!["完全なHue"](https://cdn.gethue.com/uploads/2019/12/hue4.6.png)

Hueのアプリは、インデックス付きまたはSQLでデータの計算やチャートのための[ダッシュボード](https://docs.gethue.com/user/querying/#dashboard) 、AWS、Azure、Google Cloud のクラウドストレージ用のブラウザー、ジョブワークフロー用の ワークフロースケジューラー データセットインポートウィザード...など数多くあります。

しかし、SQLデータウェアハウスの場合、Hue を主にエディターとデータカタログに制限します。

!["Data Warehousing Hue"](https://cdn.gethue.com/uploads/2020/02/hue_dwx.png)

このようにして、SQL 計算エンジンとデータストレージが簡単にクエリまたは閲覧できます。

## SQL クエリ体験

`データのクエリは難解`です。既存データセットの知識とそれらをクエリする方法は単純ではありません。従来の SQL エディタは、データアナリストのSQL開発者のような上級ユーザーとフルタイムのユーザーを対象とし、オプションで満たされているインターフェースを提供していました。

最近の傾向は、よりシンプルなインターフェースをより幅広いエンドユーザーに提供し、基本的にビッグデータエコシステムの複雑さを最大限に隠蔽することです。一般的に、フルタイムではないデータアナリストはどこから始めるのかさえ知らないため、スマートエディターは、データの説明とクエリする方法をクラウドソースする必要があります。

`アドホッククエリ`も同様に、組織内の様々な専門職が基本的な質問への回答を要求する主要なユースケースです。例えば、

* 今週および先週のブログの投稿は何回クリックされましたか
* 製品 X の日本地域での売り上げはどのぐらいでしょうか
* 私のチームでの、Salesforceでの顧客のトップケースは何ですか...

そして、分析チームに新しいダッシュボードやSQLクエリを要求するのではなく、自身で答えることができればはるかに素早いです。多くの場合、セルフサービスを実現するのを妨げるのは次の理由です。

* データを見つける
* クエリを見つける

## データを見つける

数千のデータベースで、暗号化された名前を持つ数千のうちの数十のテーブルでは、データを見つけることは簡単な作業ではありません。ユーザーは、クエリを入力して洞察を得る前に、正しいデータセットを見つけて探索する必要があります。

データブラウザとカタログはこの問題を解決するためにあり、Hue はこれらのサービスの統合を組み込みました。[Apache Atlas](https://atlas.apache.org/) は、テーブル、列の検索とコメントを強化しています。新しいカタログは[コネクター](https://docs.gethue.com/administrator/configuration/connectors/)を介して統合できます。

### トップ検索

プロジェクトに関連するテーブル名を覚えるのに苦労したことはありませんか? これらの列やビューを見つけるのに時間がかかり過ぎていませんか? Hue を使用すると、クラスター内の全てのデータベースで任意のテーブル、ビュー、または列を簡単に検索できます。数万のテーブルを検索できるので、素早いデータディスカバリーの必要な、関連するテーブルを素早く見つけることができます。

検索バーは常に画面上部からアクセスできます。Hue がメタデータサーバーにアクセスするように設定されている場合は、ドキュメント検索とメタデータ検索も提供します。

![Data Catalog top search](https://cdn.gethue.com/uploads/2018/04/blog_top_search_.png)

<p class="text-center">
  クラスターで利用可能なクエリまたはデータの検索
</p>

![Data Catalog tags](https://cdn.gethue.com/uploads/2018/04/blog_tag_listing.png)

<p class="text-center">
  フィルタリング可能なタグの一覧
</p>

#### 検索

デフォルトでは、テーブルとビューのみが返却されます。列、パーティション、データベースを検索するには「type:」フィルターを使用します。

検索構文の例:

Apache Atlas

* sample → 「sample」接頭辞を持つテーブルまたは Hue のドキュメントが返却される
* type:database → このクラスターの全てのデータベースの一覧表示
* type:table → このクラスターの全てのテーブルの一覧表示
* type:field name→ フィールド(列)が 「name」を持つテーブルの一覧表示
* ‘tag:classification_testdb5‘ または ‘classification:classification_testdb5’→ 分類 「classification_testdb5」のエンティティーの一覧表示
* owner:admin→ 「admin」ユーザーが所有する全てのテーブルの一覧表示

Cloudera Navigator

* table:customer → customer テーブルを見つける
* table:tax* tags:finance → tax で始まり「finance」でタグづけられた全てのテーブルを一覧表示
* owner:admin type:field usage → usage 文字列に一致する、admin ユーザーによって作成された全てのフィールドを一覧表示
* parentPath:"/default/web_logs" type:FIELD  originalName:b* → `default` データベースの`web_logs` テーブルの`b`で始まる全ての列を一覧表示

<img alt="Data Catalog Searc" src="https://cdn.gethue.com/uploads/2019/06/SearchWithType_field_name.png" width="800px">

#### 追加メタデータ

Hue のバージョン1から利用可能だった、テーブル、ビュー、列など任意のSQLオブジェクトのタグの編集に加えて、テーブルの説明も編集できるようになりました。これにより、エンドユーザーはメタデータのセルフサービスドキュメント化が可能です。

![Data Catalog Metadata](https://cdn.gethue.com/uploads/2018/04/blog_metadata.png)

### 左側パネルでのアシスト

必要な時に必要な場所にあるデータ

ページを離れることなく、クエリ、テーブルおよびファイルを見つけることができます。アイテムを右クリックするとアクションの一覧が表示されます。ファイルをドラッグ＆ドロップして、エディターでパスを取得することなどもできます。

![Left assist Navigation and drop](https://cdn.gethue.com/uploads/2018/05/HDFS_Context_Change_Path_2.gif)

### サンプルポップアップ

このポップアップは、データベース、テーブル、および列に関するデータのサンプルやその他の統計情報を素早く表示する方法を提供します。SQLアシストまたは任意のSQLオブジェクト(テーブル、列、関数..)を右クリックして、ポップアップを開くことができます。このリリースでは、より素早く開くようにもなり、データもキャッシュします。

![Sample popup Navigation](https://cdn.gethue.com/uploads/2018/05/SQL_Context_Navigation.gif)

#### タグ付け

さらに、オブジェクトに名前をタグ付けしてより適切に分類し、異なるプロジェクトにグループ化もできます。これらのタグは検索可能であり、より簡単でより直感的な発見を通じて探索プロセスを促進します。

![Data Catalog](https://cdn.gethue.com/uploads/2016/04/tags.png)

### データの閲覧

ファイルブラウザーアプリケーションを使用すると、HDFS, AWS S3, Azure ADLS v1 および v2 (ABFS)のファイルシステムとやり取りができます。Google Cloud Storage は現在対応中です。[HUE-8978](https://issues.cloudera.org/browse/HUE-8978).

ストレージのルート（一番上）をクリックして、アカウント内のアクセス可能な全てのフォルダを表示します。ここからディレクトリとファイルの作成、既存のディレクトリとファイルのリネーム、移動、コピー、削除を行います。さらに、ファイルをストレージに直接アップロードします。

![Browse files](https://cdn.gethue.com/uploads/2016/08/image2.png)


### データのインポート

インポーター (Importer) の目標は、まだクラスターにはないデータに対するアドホックなクエリを許可し、セルフサービスの分析をシンプルにすることです。

独自のデータをインポートしたり、テーブルにない既存のデータを参照したい場合は、左側のメニューまたは左側のアシストの小さな `+` からインポーターを開きます。インポートウィザードでは、ストレージ内のファイルから外部 Hive テーブルを直接作成できます。

![Create tables from external files](https://cdn.gethue.com/uploads/2017/11/image4-1.png)

## データのクエリ

テーブルが見つかったら、クエリを実行して質問に答えたり洞察を発見します。

### クエリの実行

SQL クエリの実行は、エディターの主なユースケースです。最も一般的な[データベースとデータウェアハウス](https://docs.gethue.com/administrator/configuration/connectors/) の一覧をご参照ください。

* 現在選択されているステートメントには、**左側に青色の**境界線があります。クエリの一部を実行するには、1つ以上のクエリのステートメントをハイライトします。
* **実行**します。その後クエリの結果画面が表示されます。列のスクロール、列の名前の種類のフィルタリング、プロット、行の固定と展開、セルの内容の検索などの操作を実行します。
* クエリに**複数のステートメント**がある場合 (セミコロンで区切られている場合)、複数ステートメントのクエリ画面で「Next」をクリックして残りのクエリを実行します。

複数のステートメントがある場合、実行したいステートメントにカーソルを置くだけで十分です。アクティブなステートメントは青色のガター（溝）のマークで示されます。

![Editor](https://cdn.gethue.com/uploads/2020/02/hue4.6-editor.png)

**注**: `CTRL/Cmd + ENTER` を使用してクエリを実行します。

**注**: ログのパネルの上部には、[クエリブラウザー](https://docs.gethue.com/user/browsing/#sql-queries) でクエリのプロファイルを開くためのリンクがあります。


### 自動補完

自動補完は Hue が最高の輝きを放つ場所であり、Hue には地球上でトップクラスの SQL 自動補完が付属しています。オートコンプリーターは Hive および Impala の SQL 方言の全てを知っており、ステートメントの構造とカーソルの位置により、キーワード、関数、列、テーブル、データベースなどを提案します。

![Autocomplete and context assist](https://cdn.gethue.com/uploads/2017/07/hue_4_assistant_2.gif)

**スマートな列の提案**

FROM句に複数のテーブル(派生テーブルや結合済みのテーブル)が含まれている場合、全てのテーブルの列はマージされ、必要に応じて適切なプレフィックスが追加されます。また、エイリアス、ラテラルビュー、複雑な型についても認識しており、それらも含まれます。必要な場合、間違いを防ぐために予約語や風変わりな列名をバッククォートします。

**スマートなキーワードの補完**

オートコンプリーターは、ステートメント内のカーソルの位置に基づいてキーワードを提案します。可能であれば、IF NOT EXISTS のように一度に複数の単語を提案することもあります。誰もたくさん入力したくないでしょう?

**関数**

改良されたオートコンプリーターは関数を提案します。各関数の提案の追加パネルが自動補完ドロップダウンに加わり、ドキュメントと関数の使用法を表示します。おートコンプリーターは引数に期待される型を認識しており、引数リスト内のカーソルの場所で引数に一致する列または関数のみを提案します。

<p class="text-center">
 <img src="https://cdn.gethue.com/uploads/2017/07/hue_4_functions.png" alt="SQL functions reference" height="500"/>
</p>

**サブクエリ、相関の有無**

サブクエリを編集する場合、サブクエリの範囲内でのみ提案を行います。相関サブクエリの場合、外部テーブルも考慮されます。

**コンテキストのポップアップ**

クエリのフラグメント（テーブル名など）を右クリックして、全てのメタデータ情報を取得します。これは、詳細説明を取得したり、テーブルや列に含まれる値の型を確認するための便利なショートカットです。

クエリの記述中に列のサンプルを見て、期待する値の型を確認できるとかなり便利です。Hueはサンプルデータに対していくつかの操作を行えるようになり、distinctした値と最小値、最大値を表示できるようになりました。

![Sample column popup](https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif)

**構文チェッカー**

小さな赤い下線で誤った構文を表示することで、投入する前にクエリを修正することができます。右クリックすると提案が表示されます。

![Syntax checker highlight](https://cdn.gethue.com/uploads/2018/01/syntax_checkerhigh.png)

<p class="text-center">
  構文チェッカーのハイライト
</p>

![Syntax checker](https://cdn.gethue.com/uploads/2018/01/checker_help.png)

<p class="text-center">
  構文チェカーの修正の提案
</p>

### テーブルのアシスト

データウェアハウスエコシステムは、トランザクションの導入によりさらに完全になっています。実際には、これはテーブルが、`パーティションキー`同様に、`主キー`, `INSERT`, `DELETE` および `UPDATE` をサポートしたということです。

![Assist All Keys](https://cdn.gethue.com/uploads/2019/11/sql_column_pk.png)

主キーは、鍵のアイコンがついたパーティションキーのように表示されます。

![Assist Primary Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_pks.png)

データのパーティショニングは、クエリを最適化するための重要な概念です。これらの特別な列にも鍵のアイコンが表示されます。

![Assist Column Partition Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_keys.png)

複合型、またはネスト型は、関連するデータを近くに保存するのに便利です。アシストを使用して列のツリーを展開できます。

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_nested_types.png)

テーブルの代わりにビューであることを意識しないと混乱する場合があります。ビューは小さな目のアイコンで表示されます。

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_assist_view_icon.png)

### 言語リファレンス

言語リファレンスマニュアルは右側のアシストパネルにあります。これは選択されたSQLエンジンとクエリに依存します。現在のテーブル、言語、UDFのドキュメントが表示されます。

この初期バージョンでは、上部のフィルターの入力はトピックのタイトルのみをフィルターします。以下は、SELECT ステートメントの結合に関するドキュメントを探す方法の例です。

![Language Reference Panel](https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_joins.gif)

ステートメントの編集中、現在のステートメントの型の言語リファレンスを素早く見つけるための方法があります。最初の単語を右クリックすると、下のポップアップにリファレンスが表示されます。

<p class="text-center">
  <img src="https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png" alt="Language Reference context" height="500"/>
</p>

### 変数

変数は、クエリ内のパラメーターを簡単に設定するために使用されます。これらは共有、あるいは繰り返し実行可能なレポートを保存するのに最適です。

**単一の値**

    SELECT * FROM web_logs WHERE country_code = "${country_code}"

![Single valued variable](https://cdn.gethue.com/uploads/2017/10/var_defaults.png)

**変数にデフォルト値の設定が可能**

    SELECT * FROM web_logs WHERE country_code = "${country_code=US}"

**複数の値**

    SELECT * FROM web_logs WHERE country_code = "${country_code=CA, FR, US}"

**複数の値の変数の表示テキストも変更可能**

    SELECT * FROM web_logs WHERE country_code = "${country_code=CA(Canada), FR(France), US(United States)}"

![Multi valued variables](https://cdn.gethue.com/uploads/2018/04/variables_multi.png)

**テキストではない値は引用符を省略**

    SELECT * FROM boolean_table WHERE boolean_column = ${boolean_column}

### チャートの作成

これらの可視化は、時系列データをプロットする場合あるいは行のサブセットに同じ属性が含まれる場合に便利です。それらは一緒に積み重ねて表示されます。

* 円グラフ
* ピボット付きの棒グラフ、線グラフ
* タイムライン
* 散布図
* 地図 (マーカーとグラデーション)

![Charts](https://cdn.gethue.com/uploads/2019/04/editor_charting.png)

### モード

#### プレゼンテーション

「ダッシュボード」アイコンをクリックして、セミコロンで区切られたクエリのリストを対話的なプレゼンテーションへと変換します。これは、シナリオを用いてプレゼンテーションを行い、ライブの結果でポイントを証明したり、ワンクリックで一連のクエリを含んだレポートを実行するのに便利です。

![Editor Presentation Mode](https://cdn.gethue.com/uploads/2020/02/editor_presentation_mode.png)

#### ダークモード

ダークモードは、初期バージョンでは Hue 全体をカバーするように拡張するのではなく、エディターの領域に制限されています。

![Editor Dark Mode](https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png)

ダークモードを切り替えるには、エディターに焦点があっているときに `Ctrl-Alt-T`、Mac では `Command-Option-T` を押すことができます。代わりに、`Ctrl-`、Mac では `Command-` を押して表示される設定メニューから制御できます。


### クエリのトラブルシューティング

#### クエリの実行前

**ポピュラーな値**

オートコンプリーターは、Navigator Optimizer からのメタデータに基づいて、ポピュラーなテーブル、列、フィルター、結合、グループ化、ソートなどを提案します。オートコンプリーターの結果ドロップダウンに新しい「Popular」タブが追加され、ポピュラーな提案が利用できる際に表示されます。

これは、未知のデータセットで結合を実行したり、数百ものテーブルから最も興味深い列を取得したりする場合に特に便利です。

![Popular joins suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_query_joins.png)

<p class="text-center">
  ポピュラーな結合の提案
</p>

![Popular columns suggestion](https://cdn.gethue.com/uploads/2017/07/hue_4_popular_filter_agg.png)

<p class="text-center">
  ポピュラーな列とフィルターの提案
</p>

**リスクアラート**

クエリの編集中、Hue はバックグラウンドで Navigator Optimizer を使用してクエリを実行し、クエリのパフォーマンスに影響する可能性のある潜在的なリスクを認識します。リスクと認識されるとクエリエディターの上に感嘆符が表示され、右側のアシスタントパネルの下部に、その改善方法に関する提案が表示されます。

![Query Risk alerts](https://cdn.gethue.com/uploads/2017/07/hue_4_risk_6.gif)

#### クエリの実行中

[Query Browser](https://docs.gethue.com/user/browsing/#sql-queries) は、クエリの実行計画とボトルネックを表示します。検出されると「健全性」のリスクが修正方法の提案とともに一覧表示されます。

![Pretty Query Profile](https://cdn.gethue.com/uploads/2019/03/Screen-Shot-2019-03-07-at-11.40.24-AM.png)

[トラブルシュートの詳細](https://docs.gethue.com/user/querying/#query-troubleshooting) のシナリオのドキュメントがご利用いただけます。(英語)

### 共有

Google Document と同様に、クエリは他のユーザーやグループと、読み取り専用や編集権限とともに共有できます。共有はメインページまたは選択したアプリケーションの右上のメニューを介して行います。共有ドキュメントは小さな青いアイコンで表示されます。

![Sharing](https://cdn.gethue.com/uploads/2019/04/editor_sharing.png)

**注**: 一般向けのリンクと Gist での共有は、次の Hue 4.7 でリリースされる予定です!


## 次のステップ (SQL)

2020 年に Hue 5 および拡張された SQL Cloud エディタが登場し、より新しいデータクエリ体験が実現します。[Cloudera Cloud Data Warehouse](https://www.cloudera.com/products/data-warehouse.html) では、データウェアハウス専用の Hue もリリースされました。

Hue は、最もポピュラーなデータベースとそれら専用の[SQL autocomplete](https://docs.gethue.com/developer/development/#sql-parsers) に多くの [connectors](https://docs.gethue.com/administrator/configuration/connectors/) を使用して、さらにプラガブルになっています。

Hue の10年に渡る進化を紹介しているこのシリーズの第3弾では、SQL Cloud エディタの機能についてさらに深く取り上げます。それまでは、この記事や[Forum](https://discourse.gethue.com/) にコメントをお願いします。また、[quick start](https://docs.gethue.com/quickstart/) で SQL のクエリを行なって下さい!


Romain, from the Hue Team
