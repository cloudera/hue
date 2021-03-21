---
title: Bay Area BikeShare Data Analysis with Search and Spark Notebook
author: admin
type: post
date: 2015-07-07T17:58:59+00:00
url: /bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/
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
categories:
  - Tutorial
---

In this tutorial, we use public data from [Bay Area BikeShare][1] and visualize bike trips patterns and their users to understand more the usage of the platform. Hue provides a Dynamic Search dashboard as well as the new Spark Notebook for enriching the data.

We recommend to start with the Trip dataset from <http://www.bayareabikeshare.com/datachallenge> and index it into Solr. For impatient people, we provide a subset of [trips][2] ready to be indexed as well as the [weather data][3] to be processed later with Spark. The Search Dashboard can be downloaded [here][4], the Notebook can be [downloaded][5] and imported with Hue 3.9 or just [copy pasted][6].

&nbsp;

This demo combined with [Real-time Spark Streaming][7] have been presented at conference like [Hadoop Summit][8] and [Big Data Day LA][9].

Happy Biking!

&nbsp;

{{< youtube K5SNB1bSxgk >}}

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard-1024x535.png"><img class="wp-image-2687 size-large" src="https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard-1024x535.png" /></a><figcaption>Example of interactive dashboard created by Drag&Drop</figcaption></figure>

&nbsp;

As usual feel free to comment on the [hue-user][11] list or [@gethue][12]!

&nbsp;

**Tip**

A quick way to index the data with Solr:

<pre><code class="bash">

bin/solr create_collection  -c  bikes

URL=http://localhost:8983/solr

u="$URL/bikes/update?commitWithin=5000"

curl $u -data-binary @/home/test/index_data.csv -H 'Content-type:text/csv'

</code></pre>

[1]: http://www.bayareabikeshare.com
[2]: https://www.dropbox.com/s/jw44si1gy26tdhj/bikedataclean.csv?dl=0
[3]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/spark/bikeshare/201408_weather_data.csv
[4]: https://www.dropbox.com/s/50adsadpwrewpbz/hue-documents.json?dl=0
[5]: https://www.dropbox.com/s/rv7s28iyw9x47q1/weather-data.spark.hue.json?dl=0
[6]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/spark/bikeshare/notebook.txt
[7]: https://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
[8]: https://gethue.com/hadoop-summit-san-jose-2015-interactively-query-and-search-your-big-data/
[9]: https://gethue.com/big-data-day-la-solr-search-with-spark-for-big-data-analytics-in-action-with-hue/
[10]: https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard.png
[11]: http://groups.google.com/a/cloudera.org/group/hue-user
[12]: https://twitter.com/gethue
