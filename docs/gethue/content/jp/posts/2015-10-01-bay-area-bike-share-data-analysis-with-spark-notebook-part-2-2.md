---
title: HadoopのノートブックとSpark、SQLを使用して、ベイエリアの自転車の共有を分析する
author: Hue Team
type: post
date: 2015-10-01T10:41:07+00:00
url: /bay-area-bike-share-data-analysis-with-spark-notebook-part-2-2/
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
  - |
    以前の記事で 、私たちはベイエリアの自転車の共有データから移動データをシームレスにインデックス化、視覚化し、ダッシュボードに気象データを追加して、分析を補足するためにSparkを使用する方法について説明しました。
    このチュートリアルでは、ベイエリアの自転車の共有（BABS: Bay Area Bike Share）システムの、ピークの使用量をより深く研究するためにノートブックアプリを使用します。
categories:
  - Hive
  - Hue 3.10
  - Impala
  - Metastore
  - Spark
  - Tutorial
  - Video

---
[以前の記事で][1] 、私たちはベイエリアの自転車の共有データから移動データをシームレスにインデックス化、視覚化し、ダッシュボードに気象データを追加して、分析を補足するためにSparkを使用する方法について説明しました。

このチュートリアルでは、ベイエリアの自転車の共有（BABS: Bay Area Bike Share）システムの、ピークの使用量をより深く研究するために[ノートブックアプリ][2]を使用します。

<http://www.bayareabikeshare.com/datachallenge>から最新のデータセットをダウンロードします 。本記事では2014年2月から2013年8月までのデータを使用しています。

{{< youtube BaTfXqAidiw >}}

## メタストアアプリでCSVデータをインポートする

BABSデータセットには、駅、移動、利用できるかどうか、および気象データを含む4つのCSVが含まれています。Hueのメタストアの[インポートウィザード][3]を使用して、これらのデータセットを簡単にインポートし、CSVのヘッダからスキーマを推測してテーブルを作成することができます。

[<img class="aligncenter wp-image-3105 " src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.00-e1443110873104-1024x503.png" alt="File Upload to Metastore" width="413" height="203" data-wp-pid="3105" />][4]

[<img class="aligncenter size-large wp-image-3106" src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.54-1024x570.png" alt="Metastore Sample" width="1024" height="570" data-wp-pid="3106" />][5]

インポートウィザードは、移動データの「期間（duration）」フィールドを、TINYINTからINTに変更するような、任意のフィールド名や種類を上書きする機会を提供します。

[<img class="aligncenter size-large wp-image-3107" src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.47.22-1024x570.png" alt="Metastore Schema Fields" width="1024" height="570" data-wp-pid="3107" />][6]

## Hadoopノートブックでの対話的な分析

### 電光石火のImpalaクエリ

私たちはクラスタにデータをインポートしているので、データの大量処理を実行するための新しいノートブックを作成することができます。始めるには、Impalaを使用していくつかの簡単な探索クエリを実行します。

&nbsp;

移動データに基づいて、最も人気のある出発駅の上位10件を見つけてみましょう：

<pre class="brush: sql; title: ; notranslate" title="">SELECT startterminal, startstation, COUNT(1) AS count FROM bikeshare.trips GROUP BY startterminal, startstation ORDER BY count DESC LIMIT 10</pre>

[<img class="aligncenter size-large wp-image-3154" src="https://cdn.gethue.com/uploads/2015/09/impala_query-1024x339.png" alt="impala_query" width="1024" height="339" data-wp-pid="3154" />][7]

結果が返ってくれば、私たちはこのデータを簡単に可視化できます。棒グラフは簡単な COUNT &#8230; GROUP BY クエリでうまく動作します。

[<img class="aligncenter wp-image-3050 size-large" src="https://cdn.gethue.com/uploads/2015/08/impala_bar_graph-e1443111918854-1024x171.png" alt="Impala Bar Graph" width="1024" height="171" data-wp-pid="3050" />][8]

サンフランシスコのカルトレイン（Townsend at 4th: タウンセンド 4th）が最も一般的な出発駅だったようです。それでは、SFカルトレインのタウンゼント駅から出発する移動で、最も人気のあった終着駅はどこなのかを特定してみましょう。結果を地図上に可視化できるように緯度と経度の座標を取得します。

<pre class="brush: sql; title: ; notranslate" title="">SELECT
 s.station_id,
 s.name,
 s.lat,
 s.long,
 COUNT(1) AS count
FROM `bikeshare`.`trips` t
JOIN `bikeshare`.`stations` s ON s.station_id = t.endterminal
WHERE t.startterminal = 70
GROUP BY s.station_id, s.name, s.lat, s.long
ORDER BY count DESC LIMIT 10
</pre>

[<img class="aligncenter wp-image-3051 size-large" src="https://cdn.gethue.com/uploads/2015/08/impala_map-e1443111522857-1024x223.png" alt="Bike Share Map" width="1024" height="223" data-wp-pid="3051" />][9]

地図の可視化では、SFカルトレインの駅から出発する最もポピュラーな移動の目的地のほとんど駅にかなり近く、金融地区とSOMAの周りにクラスタ化されていることを示しています。

### Hiveでの長時間実行するクエリ

長時間実行するSQLクエリ、またはHiveの組み込み関数を使用する必要があるクエリの場合、この分析を実行するために、ノートブックにHiveのスニペットを追加することができます。

Fカルトレイン駅の移動データをさらに掘り下げ、移動の合計数と、１時間単位でグループ化した移動の平均の時間（分）をみつけたいとしましょう。

移動データは出発時間をSTRINGとして保存しているので、インラインSQLクエリ内で時間を抽出するため、いくつかの文字列操作を適用する必要があります。外部のクエリで移動の回数と平均の期間を集約します。

<pre class="brush: sql; title: ; notranslate" title="">SELECT
    hour,
    COUNT(1) AS trips,
    ROUND(AVG(duration) / 60) AS avg_duration
FROM (
    SELECT
        CAST(SPLIT(SPLIT(t.startdate, ' ')[1], ':')[0] AS INT) AS hour,
        t.duration AS duration
    FROM `bikeshare`.`trips` t
    WHERE
        t.startterminal = 70
        AND
        t.duration IS NOT NULL
    ) r
GROUP BY hour
ORDER BY hour ASC;
</pre>

このデータはデータのいくつかの数値の面を生成するので、X軸に時間、Y軸に移動の数、散布の大きさで平均の期間を、散布グラフを使用して結果を可視化することができます。それでは、SFカルトレイン駅で、時間ごとに利用できる内訳を分析するために、別のHiveのスニペットを追加してみましょう：

[<img class="aligncenter wp-image-3049 size-large" src="https://cdn.gethue.com/uploads/2015/08/hive_scatter-e1443111554498-1024x160.png" alt="Bike Share Scatter Plot" width="1024" height="160" data-wp-pid="3049" />][10]

Let&#8217;s add another Hive snippet to analyze an hour-by-hour breakdown of availability at the SF Caltrain Station:

<pre class="brush: sql; title: ; notranslate" title="">SELECT
  hour,
  ROUND(AVG(bikes_available)) AS avg_bikes,
  ROUND(AVG(docks_available)) AS avg_docks
FROM (
  SELECT
    r.time AS time,
    CAST(SUBSTR(r.time, 12, 2) AS INT) AS hour,
    CAST(r.bikes_available AS INT) AS bikes_available,
    CAST(r.docks_available AS INT) AS docks_available
  FROM `bikeshare`.`rebalancing` r
  JOIN `bikeshare`.`stations` s ON r.station_id = s.station_id
  WHERE
    r.station_id = 70
    AND
    SUBSTR(r.time, 15, 2) = '00'
  ) t
GROUP BY hour
ORDER BY hour ASC;
</pre>

私たちは、自転車が利用できるのが午前6時から低下し、午後6時頃に回復している傾向があることを示す結果を、線グラフとして可視化します。

[<img class="aligncenter wp-image-3048 size-large" src="https://cdn.gethue.com/uploads/2015/08/hive_avg-e1443111570938-1024x169.png" alt="Bike Share Availability Line Graph" width="1024" height="169" data-wp-pid="3048" />][11]

### PySparkによる強力なデータ解析

ある時点で、あなたのデータ分析がSQLでのリレーショナルな分析の限界を超えるかもしれず、また、それ以上の表現力、本格的なAPIが必要になるかもしれません。

HueのSparkのノートブックは、ユーザーがカスタムのScala、Python (pyspark)、およびSpark APIを利用するRのコードで、調査のためのSQL分析を混在させることができます。

例えば、pysparkスニペットをオープンし、Hiveのwarehouseから直接旅行データをロードし、SFカルトレイン駅からスタートする旅行の平均数を特定するために、filter、map、およびreduceByKey操作のシーケンスを適用することができます：

<pre><code class="python">trips = sc.textFile('/user/hive/warehouse/bikeshare.db/trips/201402_trip_data.csv')

trips = trips.map(lambda line: line.split(&amp;quot;,&amp;quot;))

station_70 = trips.filter(lambda x: x[4] == '70')

# Emit tuple of ((date, hour), 1)
trips_by_day_hour = station_70.map(lambda x: ((x[2].split()[0], x[2].split()[1].split(':')[0]), 1))

trips_by_day_hour = trips_by_day_hour.reduceByKey(lambda a, b: a+b)

# Emit tuple of (hour, count)
trips_by_hour = trips_by_day_hour.map(lambda x: (int(x[0][1]), x[1]))

avg_trips_by_hour = trips_by_hour.combineByKey( (lambda x: (x, 1)),
 (lambda x, y: (x[0] + y, x[1] + 1)),
 (lambda x, y: (x[0] + y[0], x[1] + y[1]))
 )
avg_trips_by_hour = avg_trips_by_hour.mapValues(lambda v : v[0] / v[1]) 

avg_trips_sorted = sorted(avg_trips_by_hour.collect())
%table avg_trips_sorted
</pre>

[<img class="aligncenter wp-image-3143 size-large" src="https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-23-23.13.46-e1443110910319-1024x268.png" alt="Notebook pyspark bar graph" width="1024" height="268" data-wp-pid="3143" />][12]

&nbsp;

ご覧のように、Hueのノートブックアプリは、強力なツールを組み合わせ、簡単にインタラクティブなデータ分析と可視化ができるようになります。Sparkのノートブックの動作についてもっと知りたい方は[Livy、Spark REST Job server][13]についてご覧いただき、[ニューヨークのHadoop World][14]とアムステルダムの[Spark Summit][15]でお会いしましょう！

ノートブックアプリへの数々の刺激的な改善をお楽しみに！そしていつものようにいつものように、コメントとフィードバックは [hue-user][16]メーリングリストや[@gethue][17]までお気軽に！

&nbsp;

* * *

#### 役立つヒント

##### 引用符のあるCSVデータのインポート

（201402\_status\_data.csvという名前の）BABSの利用可能性（リバランス）データは引用符を使用しています。このような場合は、BeeswaxエディタでHive内にテーブルを作成し、HiveのOpenCSV Row SERDEを使用するのが簡単です：

<pre class="brush: sql; title: ; notranslate" title="">CREATE TABLE rebalancing(station_id int, bikes_available int, docks_available int, time string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
&amp;quot;separatorChar&amp;quot; = &amp;quot;,&amp;quot;,
&amp;quot;quoteChar&amp;quot; = &amp;quot;&amp;quot;&amp;quot;,
&amp;quot;escapeChar&amp;quot; = &amp;quot;\&amp;quot;
)
STORED AS TEXTFILE;
</pre>

その後、テーブルにCSVファイルをインポートするためにメタストアに戻ることができます。手作業でヘッダー行を削除する必要があることに注意してください。

##### Impalaのメタストアのキャッシュをリセットする

新しいデータベースやテーブルを作成したり、Impalaのスニペットでそれらのクエリを計画している場合は、INVALIDATE METADATA、最初にメタストアのキャッシュをリセットするコマンドの実行をお勧めします。そうしないと、データベースやテーブルが認識されないというエラーが発生することがあります。

 [1]: https://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook-2/?lang=ja
 [2]: https://gethue.com/spark-notebook-and-livy-rest-job-server-improvements/
 [3]: http://hadoop-tutorial-create-hive-tables-with-headers-and/?lang=ja
 [4]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.00.png
 [5]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.46.54.png
 [6]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-20-20.47.22.png
 [7]: https://cdn.gethue.com/uploads/2015/09/impala_query.png
 [8]: https://cdn.gethue.com/uploads/2015/08/impala_bar_graph.png
 [9]: https://cdn.gethue.com/uploads/2015/08/impala_map.png
 [10]: https://cdn.gethue.com/uploads/2015/08/hive_scatter.png
 [11]: https://cdn.gethue.com/uploads/2015/08/hive_avg.png
 [12]: https://cdn.gethue.com/uploads/2015/09/Screenshot-2015-09-23-23.13.46.png
 [13]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/
 [14]: https://www.eventbrite.com/e/spark-lightning-night-at-shutterstock-nyc-tickets-17590432457
 [15]: https://spark-summit.org/eu-2015/events/building-a-rest-job-server-for-interactive-spark-as-a-service/
 [16]: http://groups.google.com/a/cloudera.org/group/hue-user
 [17]: https://twitter.com/gethue