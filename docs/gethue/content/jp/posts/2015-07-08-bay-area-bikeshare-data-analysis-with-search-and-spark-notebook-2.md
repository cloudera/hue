---
title: SearchとSparkノートブックでベイエリアのBikeShareデータを解析
author: Hue Team
type: post
date: 2015-07-08T10:35:55+00:00
url: /bay-area-bikeshare-data-analysis-with-search-and-spark-notebook-2/
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
  - このチュートリアルはBay Area BikeShare のパブリックデータを使用し、プラットフォームの利用量をさらに理解するために、自転車の移動パターンとそのユーザーを可視化します。Hueではデータを充実させるために、動的な検索ダッシュボードだけでなく、新しくSparkのノートブックも提供しています。
categories:
  - Hue 3.9
  - Search
  - Spark
  - Tutorial

---
このチュートリアルは[Bay Area BikeShare][1] のパブリックデータを使用し、プラットフォームの利用量をさらに理解するために、自転車の移動パターンとそのユーザーを可視化します。Hueではデータを充実させるために、動的な検索ダッシュボードだけでなく、新しくSparkのノートブックも提供しています。

私たちは<http://www.bayareabikeshare.com/datachallenge>のデータセットを用いて始めることをお勧めしますが、せっかちな方のために、インデックス作成の準備ができた一部の[移動(trips)][2]データも、また、後ほどSparkにより処理される[気象データ(weather data)][3]も提供しています。Hueのノートブックは[ダウンロード][4]してインポート、または単純に[コピーしてペースト][5]することができます 。

&nbsp;

この[リアルタイムSpark Streaming][6]を組み合わせたデモは、[Hadoop Summit][7]および[Big Data Day LA][8]のようなカンファレンスで紹介しています 。

Happy Biking!

&nbsp;

{{< youtube K5SNB1bSxgk >}}

&nbsp;

<div id="attachment_2687" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard.png"><img class="wp-image-2687 size-large" src="https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard-1024x535.png" alt="solr-bike-dashboard" width="1024" height="535" data-wp-pid="2687" /></a>
  
  <p class="wp-caption-text">
    ドラッグ＆ドロップで作成されたインタラクティブなダッシュボードの例
  </p>
</div>

&nbsp;

いつものように、コメントとフィードバックは [hue-user][9] メーリングリストや[@gethue][10]までお気軽に！

&nbsp;

**ヒント**

Solrでデータをインデックスする簡単な方法：

<pre><code class="bash">bin/solr create_collection  -c  bikes

URL=http://localhost:8983/solr
u="$URL/bikes/update?commitWithin=5000"
curl $u --data-binary @/home/test/index_data.csv -H 'Content-type:text/csv'
</pre>

 [1]: http://www.bayareabikeshare.com
 [2]: https://www.dropbox.com/s/jw44si1gy26tdhj/bikedataclean.csv?dl=0
 [3]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/spark/bikeshare/201408_weather_data.csv
 [4]: https://www.dropbox.com/s/rv7s28iyw9x47q1/weather-data.spark.hue.json?dl=0
 [5]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/spark/bikeshare/notebook.txt
 [6]: https://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
 [7]: https://gethue.com/hadoop-summit-san-jose-2015-interactively-query-and-search-your-big-data/
 [8]: https://gethue.com/big-data-day-la-solr-search-with-spark-for-big-data-analytics-in-action-with-hue/
 [9]: http://groups.google.com/a/cloudera.org/group/hue-user
 [10]: https://twitter.com/gethue