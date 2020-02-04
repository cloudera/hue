---
title: SQLアシストとオートコンプリート（自動補完）の改善
author: Hue Team
type: post
date: 2016-05-06T04:08:17+00:00
url: /assist-and-autocomplete-improvements/
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
sf_custom_excerpt:
  - 私たちは最近、ノートブックで作業したり、HiveとImpalaのクエリエディタでSQLのクエリを編集する際、 本当にエクスペリエンスが向上できるオートコンプリートとアシストパネルにいくつかの素晴らしい改良を行いました。
categories:
  - HDFS
  - Hive
  - Hue 3.10
  - Impala
  - Notebook
  - Video

---
（[原文][1]）

私たちは最近、[ノートブック][2]で作業したり、HiveとImpalaのクエリ[エディタ][3]でSQLのクエリを編集する際、 本当にエクスペリエンスが向上できるオートコンプリートとアシストパネルにいくつかの素晴らしい改良を行いました。

主な改善点の一つは、アシストとオートコンプリートの両方で、struct、map、arrayと言った複雑な型に対応したことです。改善点の詳細は以下を参照するか、次のビデオのデモを見てみましょう。

&nbsp;

{{< youtube PciZhDY-W5A >}}

長時間でより詳細なバージョンが[こちら][4]にあります。

&nbsp;

### 簡単な方法で複雑な&#8230;

アシストパネルは現在、HiveとImpalaのための複雑な型をサポートしています。列をクリックするだけで、struct、map、arrayのいずれも展開します。

私たちは、長いテーブルやカラム名、または深くネストされた構造を有しているときに非常に便利である、サイズ変更可能なアシストパネルを作りました。

[<img class="aligncenter size-large wp-image-3496" src="https://cdn.gethue.com/uploads/2015/11/Assist_complex-1024x777.png" alt="Assist_complex" width="1024" height="777" data-wp-pid="3496" />][5]

&nbsp;

パネルで探しているものを見つけた場合、アクティブエディタのカーソル位置にアイテムを挿入するためダブルクリックできます。また、別の位置がお好みの場合は、エディタの任意の場所にドラッグアンドドロップすることができます。パネルは構造を知っており、列名を含んだすべての親との参照を挿入します。

&nbsp;

### Ctrl+スペースはあなたの友達です！

オートコンプリートを有効にするために、エディタ内の任意の場所でCtrl+スペースを使用できます。これはスキーマに基づいて提案を行い、あなたのアカウントに編集している文の内容も扱います。SQLのキーワード、テーブル、列以外にユーザー定義のエイリアスでさえも提案します。

[<img class="aligncenter size-large wp-image-3498" src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_join_alias-1024x387.png" alt="Autocomplete_join_alias" width="1024" height="387" data-wp-pid="3498" />][6]

&nbsp;

これはHiveとImpalaのための複雑な型を知っており、現在編集しているリファレンスに基づいて適切なアドバイスを行います。

[<img class="aligncenter size-large wp-image-3499" src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_nested_struct-1024x448.png" alt="Autocomplete_nested_struct" width="1024" height="448" data-wp-pid="3499" />][7]

あなたは展開されたビュー(exploded view)がお好きだと聞きました！オートコンプリートはこれらに役立ちます。展開されたビューと同様に、展開されたビューの展開されたビューの展開されたビュー&#8230;.を追跡します。

[<img class="aligncenter size-large wp-image-3500" src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_exploded-1024x300.png" alt="Autocomplete_exploded" width="1024" height="300" data-wp-pid="3500" />][8]

&nbsp;

### 値とHDFSのパス

私たちはミックスにサンプル値も追加しました。これは現在Impalaのみで利用可能で、すべての値のサブセットを提案します。mapキーのインスタンスを扱うためや、あなたのデータのアイデアを与える際、これは本当にいいです。

[<img class="aligncenter size-full wp-image-3501" src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_sample_values.png" alt="Autocomplete_sample_values" width="946" height="454" data-wp-pid="3501" />][9]

&nbsp;

特に最後ではありませんが、オートコンプリートは現在、HDFSパスの提案ができます。ノートブックのスニペットの一つに &#8216;/&#8217;と入力するだけで、自動的にその場所でのフォルダとファイルの一覧のオートコンプリートパネルを開きます。パス編集時に、もちろんCtrl+スペースでアクティブにすることができます。

[<img class="aligncenter size-large wp-image-3502" src="https://cdn.gethue.com/uploads/2015/11/Autocomplete_hdfs-1024x337.png" alt="Autocomplete_hdfs" width="1024" height="337" data-wp-pid="3502" />][10]

私たちはアシストとオートコンプリートの経験を維持向上（HBaseのサポート、任意のJDBCデータベース、HDFS&#8230;）し続けます。これらの新機能があなたのために有用であろうことを願っています！

コメントとフィードバックは [hue-user][11] メーリングリストや[@gethue][12]までお気軽に！

&nbsp;

 [1]: https://gethue.com/assist-and-autocomplete-improvements/
 [2]: http://jp.gethue.com/bay-area-bike-share-data-analysis-with-spark-notebook-part-2-2/
 [3]: http://jp.gethue.com/hadoop%E3%81%AE%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%A9%E3%82%AF%E3%83%86%E3%82%A3%E3%83%96sql%E3%81%8C%E7%B0%A1%E5%8D%98%E3%81%AB/
 [4]: https://youtube.com/watch?v=XakL87LU0pQ
 [5]: https://cdn.gethue.com/uploads/2015/11/Assist_complex.png
 [6]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_join_alias.png
 [7]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_nested_struct.png
 [8]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_exploded.png
 [9]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_sample_values.png
 [10]: https://cdn.gethue.com/uploads/2015/11/Autocomplete_hdfs.png
 [11]: http://groups.google.com/a/cloudera.org/group/hue-user
 [12]: https://twitter.com/gethue