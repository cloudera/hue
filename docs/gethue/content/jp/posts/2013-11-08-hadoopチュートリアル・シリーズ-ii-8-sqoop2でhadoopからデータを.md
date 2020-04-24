---
title: 'Hadoopチュートリアル・シリーズ II: 8. Sqoop2でHadoopからデータを転送する方法'
author: Hue Team
type: post
date: 2013-11-08T23:59:15+00:00
url: /hadoopチュートリアル・シリーズ-ii-8-sqoop2でhadoopからデータを/
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
  - Apache Sqoopは、Hadoopと（ファイルやデータベースにある）データを受け渡しを行うのに素晴らしいツールです。Hue 3ではSqoop2を簡単に使用するための新しいアプリが...
categories:
  - Full tutorial
  - Sqoop
  - Tutorial
  - Video

---
（[原文][1]）間違いを見つけた場合はご指摘下さい

<p id="docs-internal-guid-342afe4b-3626-38d5-0543-797eb6fb3c0a">
  <span><a href="http://www.google.co.jp/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&ved=0CCoQFjAA&url=http%3A%2F%2Fsqoop.apache.org%2F&ei=9h9eUt7SKofQkQWy5YCADA&usg=AFQjCNFJ9nOIbX4GN1HakCZayhtKkXEUBw&bvm=bv.54176721,d.dGI">Apache Sqoop</a>は、Hadoopと（ファイルやデータベースにある）データを受け渡しを行うのに素晴らしいツールです。</span><span>Hue 3ではSqoop2を簡単に使用するための</span><span><a href="https://gethue.com/move-data-in-out-your-hadoop-cluster-with-the-sqoop">新しいアプリ</a>が追加されています。</span><span><br /></span>
</p>

&nbsp;

Hadoopチュートリアルシリーズ・シーズン2での最後のエピソードは（以前は[Search][2]についてでした)、Yelpの結果をMySqlのテーブルにエクスポートすることが、いかに簡単になっているかをご覧に入れましょう。

&nbsp;

{{< youtube zCE7N0PV7R4 >}}

&nbsp;

<span>Sqoop2は、現在</span><span><a href="https://en.wikipedia.org/wiki/Comma-separated_values">Comma Separated Values</a>(CSV)ファイルのみが使えます。</span><span> </span><span><a href="https://github.com/romainr/hadoop-tutorials-examples/blob/master/sqoop2/stats.pig">Pig</a></span><span><a href="https://github.com/romainr/hadoop-tutorials-examples/blob/master/sqoop2/stats.pig"> script</a>を<a href="https://gethue.com/tutorial-apache-pig-editor-in-hue-2-3">Pig Editor</a>を用いて私たちのデータ分析をこのフォーマットで保存しましょう。</span><span><br /></span>

&nbsp;

<span>続いてビデオで詳細をご覧いただいたように、エクスポートジョブを指定して、前のPigジョブの出力を入力パスに設定します。データはHDFS内ににあり、パスは一つのファイルかディレクトリかのいずれかが可能です</span>

&nbsp;

<span>前にこの</span><span><a href="https://github.com/romainr/hadoop-tutorials-examples/blob/master/sqoop2/create_table.sql">SQL スクリプトで</a>、MySqlの&#8217;stats&#8217;テーブルを作成しました。このテーブルにはエクスポートされたデータが保存されることになります。</span><span><br /></span>

&nbsp;

<span>これはジョブのプロパティです。これらは以前のSqoop Appブログポストで詳細を説明しています。</span>

&nbsp;

<pre class="code">Table name: yelp_cool_test
Input directory: /user/<span>hdfs</span>/test_sqoop
Connector: mysql
JDBC Driver Class : <span>com</span><span>.</span>mysql<span>.</span><span>jdbc</span><span>.</span>Driver
JDBC Connection String: jdbc:mysql://hue.com/test
</pre>

&nbsp;

<span>続いて&#8217;Save & Excute&#8217;をクリックします。さぁ、これでデータはMySqlで利用可能になっています！</span>

&nbsp;

<pre class="code"><span>mysql</span>&gt; select * from yelp_cool_test limit 2;
+------+------+------+------+
| <span>a</span>    | b    | c    | d    |
+------+------+------+------+
|    1 |    2 |    3 |    4 |
|    2 |    3 |    4 |    5 |
+------+------+------+------+
2 rows in set (0.00 <span>sec</span>)
</pre>

&nbsp;

<span>HiveやHBaseに格納されたデータは、まだSqoop2ではネイティブで使用することはできません。（効率は悪いですが）現在のワークアラウンドは<a href="https://gethue.com/hadoop-tutorial-use-pig-and-hive-with-hbase">HiveあるいはPig</a>でデータをHDFSのディレクトリにダンプし、それから類似のSqoopエクスポートを行うようになるでしょう。</span>

&nbsp;

<span>いつものように、<span>ご質問やフィードバックがあれば、</span><a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue</a><a href="http://groups.google.com/a/cloudera.org/group/hue-user">-user</a><span> や </span><a href="http://twitter.com/gethue">@gethue.com</a><span>までお気軽にお尋ね下さい！</span><br /></span>

<span><a href="https://gethue.tumblr.com/tagged/season2">シーズン2</a>をご覧いただきありがとうございました。ダイヤルはそのまま、シーズン3はもうすぐです！</span><span><br /></span>

 [1]: https://gethue.com/hadoop-tutorials-series-ii-8-how-to-transfer-data
 [2]: https://gethue.com/hadoop-tutorials-season-ii-7-how-to-index-and-search