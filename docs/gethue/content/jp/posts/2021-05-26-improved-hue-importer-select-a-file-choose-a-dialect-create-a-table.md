---
title: 改善されたHueのImporter -- ファイルの選択、方言の選択、テーブルの作成
author: Hue Team
type: post
date: 2021-05-26T00:00:00+00:00
url: /blog/2021-05-26-improved-hue-importer-select-a-file-choose-a-dialect-create-a-table
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
  - Development
  - Query
---

Hueを設定して、パブリッククラウドで、ユーザーがCSVファイルから新しいSQLテーブルを作成できるようにするのに苦労したことがある方は、これがはるかに簡単になったことを知って喜んでいただけると思います。

Hueのプロユーザーであれば、Hue の[Importer](https://docs.gethue.com/developer/api/rest/#data-importer)をご存知でしょう。 ファイルからテーブルを作成することができます。 これまでは、ファイルは[HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)や、[S3](https://gethue.com/introducing-s3-support-in-hue/)や [ABFS](https://docs.gethue.com/administrator/configuration/connectors/#azure-file-systems)などのクラウドオブジェクトストレージ上にある必要がありました。 今では、コンピュータからファイルをブラウズして選択し、HueのさまざまなSQLの[方言](https://docs.gethue.com/administrator/configuration/connectors/) でテーブルを作成できます。 Apache Hive, Apache Impala, Apache Phoenix, MySqlの方言に対応しています。

### ゴール

* ソースに関係なく、Hue Importerを使用してファイルをアップロードする。

### 目的
* 誰もがHDFSやS3/ABFSにアクセスできるわけではありません。 ビジネスアナリストは、自分のコンピュータにあるデータセットを素早く分析し、データのクリーンアップやその他のデータエンジニアリングタスクを省略する必要があることがよくあります。
* この機能を使用すると、コンピュータからファイルをインポートして、数回のクリックでテーブルを作成することができます.

### テーブルを作成する手順

![Importer direct upload steps gif](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_steps.gif)

### ワークフロー
![Importer direct upload steps app diagram](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_workflow-2.png)

### ファイルと API

  * この機能を実装するために、3つのAPIを使用しています。
    * [Guess_format](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/api3.py#L121) (ファイル形式を推測する)
    * [Guess_field_types](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/api3.py#L228) (カラムの型を推測する)
    * [Importer_submit](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/api3.py#L444) (テーブルを作成する)
  * さまざまな SQL 方言がどのように実装されているのかに興味がある場合は、 [sql.py](https://github.com/cloudera/hue/blob/master/desktop/libs/indexer/src/indexer/indexers/sql.py) ファイルをご覧ください。

  **注：** 現在、Hueは数千行の小さなCSVファイルをサポートしています。


### 中間ステップ
  * ステップ 1 ![Importer direct upload step1](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_step1.png)  
    ファイルを選択すると、Hueはファイル形式を推測し、区切り文字を識別して、テーブルのプレビューを生成します。
  * ステップ 2 ![Importer direct upload step2](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_step2-2.png)  
    SQL の方言を選択すると、Hueは列のデータ型を自動検出します。 列名とそのデータ型は編集できます。


この機能は、最新の Hue または [demo.gethue.com](https://demo.gethue.com/hue/indexer/importer).  
で試すことができます。 </br> </br> このプロジェクトでは、より多くのSQL方言をサポートするための[貢献](https://github.com/cloudera/hue/#development)を喜んで歓迎いたします。  
ご意見やご質問はありますか？ ここや[ディスカッション](https://discourse.gethue.com/) まで気軽にコメントして、[SQLクエリ](https://docs.gethue.com/quickstart/) のクイックスタートをしてください！

どうぞよろしくお願いします！

Ayush from the Hue Team
