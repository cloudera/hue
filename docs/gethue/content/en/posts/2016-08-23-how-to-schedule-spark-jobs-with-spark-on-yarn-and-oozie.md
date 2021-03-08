---
title: How to Submit Spark jobs with Spark on YARN and Oozie
author: admin
type: post
date: 2016-08-23T09:45:30+00:00
url: /how-to-schedule-spark-jobs-with-spark-on-yarn-and-oozie/
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
categories:

---
How to run Spark jobs with Spark on YARN? This often requires trial and error in order to make it work.

Hue is leveraging [Apache Oozie][1] to submit the jobs. It focuses on the yarn-client mode, as Oozie is already running the spark-summit command in a MapReduce2 task in the cluster. You can read more about the Spark modes [here][2].

Here is how to get started successfully:

## PySpark

Simple script with no dependency.

[<img src="https://cdn.gethue.com/uploads/2016/08/oozie-pyspark-simple.png" />][3]

Script with a dependency on another script (e.g. hello imports hello2).

[<img src="https://cdn.gethue.com/uploads/2016/08/oozie-pyspark-dependencies.png" />][4]

For more complex dependencies, like Panda, have a look at this [documentation][5].

&nbsp;

## Jars (Java or Scala)

Add the jars as File dependency and specify the name of the main jar:

[<img src="https://cdn.gethue.com/uploads/2016/08/spark-action-jar.png" />][6]

Another solution is to put your jars in the 'lib' directory in the workspace ('Folder' icon on the top right of the editor).

[<img src="https://cdn.gethue.com/uploads/2016/08/oozie-spark-lib2.png"  />][7]

&nbsp;

<div class="body-text clearfix">
  <p>
    The latest Hue is improving the user experience and will provide an even simpler solution in Hue 4.
  </p>

  <p>
    If you have any questions, feel free to comment here or on the <a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a> list or <a href="https://twitter.com/gethue">@gethue</a>!
  </p>
</div>

 [1]: http://oozie.apache.org/
 [2]: https://gethue.com/use-the-spark-action-in-oozie/
 [3]: https://cdn.gethue.com/uploads/2016/08/oozie-pyspark-simple.png
 [4]: https://cdn.gethue.com/uploads/2016/08/oozie-pyspark-dependencies.png
 [5]: http://www.cloudera.com/documentation/enterprise/latest/topics/spark_python.html
 [6]: https://cdn.gethue.com/uploads/2016/08/spark-action-jar.png
 [7]: https://cdn.gethue.com/uploads/2016/08/oozie-spark-lib2.png
