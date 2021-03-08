---
title: Hadoop / Spark Notebook and Livy REST Job Server improvements!
author: admin
type: post
date: 2015-08-24T16:43:24+00:00
url: /spark-notebook-and-livy-rest-job-server-improvements/
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

The Notebook application as well as the REST Spark Job Server are being revamped. These two components goals are to let users execute [Spark][1] in their browser or from anywhere. They are still in beta but next version of Hue will have them graduate. Here are a list of the improvements and a video demo:

<ul class="itemizedlist" type="disc">
  <li class="listitem">
    Revamp of the snippets of the Notebook UI
  </li>
  <li class="listitem">
    Support for Spark 1.3, 1.4, 1.5
  </li>
  <li class="listitem">
    Impersonation with YARN
  </li>
  <li class="listitem">
    Support for R shell
  </li>
  <li class="listitem">
    Support for submitting jars or python apps
  </li>
</ul>

How to play with it?

See in this post how to use the [Notebook UI][2] and on this page on how to use the [REST Spark Job Server][3] named Livy. The architecture of Livy was recently detailed in a [presentation][4] at Big Data Scala by the Bay. Next updates will be at the [Spark meetup][5] before Strata NYC and [Spark Summit][6] in Amsterdam.

{{< youtube b3nMTJ74H4Y >}}

###

### Slicker snippets interface

The snippets now have a new code editor, autocomplete and syntax highlighting. Shortcut links to HDFS paths and Hive tables have been added.

[<img src="https://cdn.gethue.com/uploads/2015/08/notebook-1024x505.png" />][7]

&nbsp;

### R support

The SparkR shell is now available, and plots can be displayed inline

[<img src="https://cdn.gethue.com/uploads/2015/08/spark-r-snippet.png" />][8]

### Support for closing session and specifying Spark properties

All the spark-submit, spark-shell, pyspark, sparkR properties of jobs & shells can be added to the sessions of a Notebook. This will for example let you add files, modules and tweak the memory and number of executors.

[<img src="https://cdn.gethue.com/uploads/2015/08/notebook-sessions-1024x236.png" />][9]

###

&nbsp;

So give this new Spark integration a try and feel free to send feedback on the [hue-user][10] list or [@gethue][11]!

[1]: http://spark.apache.org/
[2]: https://gethue.com/new-notebook-application-for-spark-sql/
[3]: https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server
[4]: https://gethue.com/big-data-scala-by-the-bay-interactive-spark-in-your-browser/
[5]: https://www.eventbrite.com/e/spark-lightning-night-at-shutterstock-nyc-tickets-17590432457
[6]: https://spark-summit.org/eu-2015/events/building-a-rest-job-server-for-interactive-spark-as-a-service/
[7]: https://cdn.gethue.com/uploads/2015/08/notebook.png
[8]: https://cdn.gethue.com/uploads/2015/08/spark-r-snippet.png
[9]: https://cdn.gethue.com/uploads/2015/08/notebook-sessions.png
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
[11]: https://twitter.com/gethue
