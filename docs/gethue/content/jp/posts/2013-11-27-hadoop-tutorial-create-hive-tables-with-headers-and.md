---
title: Hiveテーブルの作成とクォートされたCSVデータのロード
author: Hue Team
type: post
date: 2013-11-27T23:59:25+00:00
url: /hadoop-tutorial-create-hive-tables-with-headers-and/
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
slide_template:
  - default
sf_custom_excerpt:
  - |
    HueはHiveテーブルの作成を簡単にします。
    HUE-1746では、Hueがデータを直接調べることで、列名と型（整数、文字列、浮動小数点など）を推測します。データの先頭がヘッダから...
categories:
  - Hive
  - Metastore
  - Tutorial
  - Video

---
<p id="docs-internal-guid-69d034aa-9ae7-82e8-1c00-5068cd66771e">
  HueはHiveテーブルの作成を簡単にします。
</p>

[HUE-1746][1]では、Hueがデータを直接調べることで、列名と型（整数、文字列、浮動小数点など）を推測します。データの先頭がヘッダから始まっている場合、ヘッダ行が自動的に使用され、テーブルの作成時にヘッダ行を**スキップ**します。

クォートされたCSVのフィールドも、[HUE-1747][2]のおかげで互換性を持ちます。

{{< youtube RxT0M8JgvOk >}}

これが使用しているデータファイルです:

<http://www.fdic.gov/bank/individual/failed/banklist.html>

こちらはクォートされたCSVを読むための[<span id="bf7ff735-f802-4cd1-8f49-0e550a92b329">SerDe</span>][3]です:

<https://github.com/ogrodnek/csv-serde>

そして、テーブルがSerDeを使用するようにするためのコマンドです:

<pre class="code">ALTER TABLE banks SET SERDE 'com.bizo.hive.serde.csv.CSVSerde'</pre>

さぁ、[Hive][4]、[Impala][5]、または[Pig][6]エディタでデータを分析しましょう！

 [1]: https://issues.cloudera.org/browse/HUE-1746
 [2]: https://issues.cloudera.org/browse/HUE-1747
 [3]: https://cwiki.apache.org/confluence/display/Hive/SerDe
 [4]: https://gethue.com/hadoop-tutorial-hive-query-editor-with-hiveserver2-and
 [5]: https://gethue.com/fast-sql-with-the-impala-query-editor
 [6]: https://gethue.com/hadoop-tutorial-use-pig-and-hive-with-hbase