---
title: Analyse des données des “Velib” de San Francisco avec Solr Search et un Spark Notebook
author: admin
type: post
date: 2015-07-08T16:46:45+00:00
url: /analyse-des-donnees-des-velib-de-san-francisco-avec-solr-search-et-un-spark-notebook/
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
---

Dans ce tutoriel, nous utilisons les données publiques de [Bay Area BikeShare][1] afin de visualiser les déplacements en vélo des utilisateurs et ainsi mieux comprendre l'utilisation de la plate-forme. Nous utiliserons Hue qui fournit un tableau de bord dynamique pour chercher ainsi que son nouveau Spark Notebook pour enrichir les données.

Nous vous recommandons de commencer avec le jeu de données <http://www.bayareabikeshare.com/datachallenge>  mais pour les gens impatients, nous fournir un sous-ensemble des [voyages][2]  prêts à être indexées ainsi que les [données météorologiques][3] à traiter plus tard avec Spark. Le Notebook peut être [téléchargé][4] et importé ou tout simplement [copie collé][5] depuis ici.

&nbsp;

Cette démo combinée avec la présentation [en temps réel en streaming Spark][6] ont été présentés à des conférences comme [Hadoop Summit][7] et [Big Data Day LA][8] .

Bon Vélo!

{{< youtube K5SNB1bSxgk >}}

Video en Anglais, avec un accent Francais 😉

[<img class="wp-image-2687 size-large" src="https://cdn.gethue.com/uploads/2015/06/solr-bike-dashboard-1024x535.png" />][9]

&nbsp;

Comme d'habitude hésitez pas à commenter sur la [liste utilisateur][10] ou  [@gethue][11] !

&nbsp;

**Conseil**

Un moyen rapide pour indexer les données avec Solr:

<div>
  <p>
    <pre><code class="bash"><br /> bin/solr create_collection  -c  bikes
  </p>

  <p>
    URL=http://localhost:8983/solr<br /> u="$URL/bikes/update?commitWithin=5000"<br /> curl $u -data-binary @/home/test/index_data.csv -H 'Content-type:text/csv'<br /> </code></pre>
  </p>
</div>

[1]: http://www.bayareabikeshare.com/
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
