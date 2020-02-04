---
title: Analizziamo i dati BikeShare della Bay Area con Solr Search e Spark Notebook!
author: admin
type: post
date: 2015-07-08T18:08:12+00:00
url: /analizziamo-i-dati-bikeshare-della-bay-area-con-solr-search-e-spark-notebook/
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
sf_author_info:
  - 1
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
categories:
---

In questo tutorial usiamo i dati pubblici di [Bay Area BikeShare][1] per visualizzare i pattern dei viaggi in bicicletta e degli utenti, cosi' da capire come la Bay Area si muove sulle due ruote. Hue shippa (scusate l'inglesismo) una Search Dashboard dinamica cosi' come il nuovo Spark Notebook che utilizzeremo per arricchire i dati.

Raccomandiamo di partire con il dataset di <http://www.bayareabikeshare.com/datachallenge> ma per i piu' impazienti abbiamo caricato un [estratto dei dati][2] pronto per essere indicizzato. Qui invece potete trovare i [dati relativi al meteo][3] che utilizzeremo in Spark.

Il Notebook Hue puo' essere [scaricato][4] e importato o potete fare direttamente [copia e incolla][5].

&nbsp;

Questa demo assieme a [Real-time Spark Streaming][6] e' stata presentata a conferenze come [Hadoop Summit][7] e [Big Data Day LA][8].

Buona biciclettata!

&nbsp;

{{< youtube K5SNB1bSxgk >}}

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard-1024x535.png"><img src="https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard-1024x535.png" /></a><figcaption>Esempio di una dashboard interattiva creata semplicement con Drag&Drop</figcaption></figure>

&nbsp;

Come al solito commentate pure sulla lista [hue-user][10] o su Twitter [@gethue][11]!

&nbsp;

**Snippetina salvavita**

Un modo veloce per indicizzare i dati con Solr:

<pre><code class="bash">

bin/solr create_collection  -c  bikes

URL=http://localhost:8983/solr

u="$URL/bikes/update?commitWithin=5000"

curl $u -data-binary @/home/test/index_data.csv -H 'Content-type:text/csv'

</code></pre>

[1]: http://www.bayareabikeshare.com
[2]: https://www.dropbox.com/s/jw44si1gy26tdhj/bikedataclean.csv?dl=0
[3]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/spark/bikeshare/201408_weather_data.csv
[4]: https://www.dropbox.com/s/rv7s28iyw9x47q1/weather-data.spark.hue.json?dl=0
[5]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/spark/bikeshare/notebook.txt
[6]: https://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
[7]: https://gethue.com/hadoop-summit-san-jose-2015-interactively-query-and-search-your-big-data/
[8]: https://gethue.com/big-data-day-la-solr-search-with-spark-for-big-data-analytics-in-action-with-hue/
[9]: https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard.png
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
[11]: https://twitter.com/gethue
