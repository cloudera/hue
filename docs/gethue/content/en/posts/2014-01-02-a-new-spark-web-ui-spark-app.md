---
title: 'A new Spark Web UI: Spark App'
author: admin
type: post
date: 2014-01-02T14:06:00+00:00
url: /a-new-spark-web-ui-spark-app/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/71963991256/a-new-spark-web-ui-spark-app
tumblr_gethue_id:
  - 71963991256
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
categories:
---

## <span style="color: #ff0000;"><em>Note:</em> <em>This post is deprecated as of Hue 3.8 / April 24th 2015</em>. Hue now have a new <a href="https://gethue.com/new-notebook-application-for-spark-sql/" target="_blank" rel="noopener noreferrer">Spark Notebook</a> application.</span>

Hi Spark Makers!

A Hue Spark application was recently created. It lets users execute and monitor [Spark][1] jobs directly from their browser from any machine, with interactivity.

The new application is using the [Spark Job Server][2] contributed by [Ooyala][3] at the last [Spark Summit][4].

{{< youtube lWKxtvUMcGw >}}

We hope to work with the community and have support for Python, Java, direct script submission without compiling/uploading and other improvements in the future!

As usual feel free to comment on the [hue-user][5] list or [@gethue][6]!

## Get Started!

Currently only Scala jobs are supported and programs need to implement this trait and be packaged into a jar. Here is a [WordCount][7] example. To learn more about Spark Job Server, check its [README][2].

If you are using Cloudera Manager, enable the Spark App by removing it from the blacklist by adding this in the Hue Safety Valve:

<pre><code class="bash">

[desktop]

app_blacklist=

</code></pre>

## Requirements

We assume you have Spark 0.9.0, Scala 2.10. installed on your system. Make sure you have the good scala and sbt versions, e.g. for Ubuntu: <https://gist.github.com/visenger/5496675>

## Get Spark Job Server

Currently on github on this branch:

<pre><code class="bash">git clone https://github.com/ooyala/spark-jobserver.git

cd spark-jobserver

</code></pre>

Then type:

<pre><code class="bash">sbt

re-start</code></pre>

## Get Hue

<span style="line-height: 1.5em;">If Hue and Spark Job Server are not on the same machine update the </span><a style="line-height: 1.5em;" href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini">hue.ini</a> <span style="line-height: 1.5em;">property in desktop/conf/pseudo-distributed.ini:</span>

<pre><code class="bash">

[spark]

\# URL of the Spark Job Server.

server_url=http://localhost:8090/</code></pre>

To point to your Spark Cluster

<pre><code class="bash">vim ./job-server/src/main/resources/application.conf</code></pre>

Replace:

<pre><code class="bash">master = "local[4]"</code></pre>

With the Spark Master URL (you can get it from the Spark Master UI: http://SPARK-HOST:18080/):

<pre><code class="bash">master = "spark://localhost:7077"</code></pre>

## Get a Spark example to run

Then follow this [walk-through][8] and create the example jar that is used in the video demo.

[1]: http://spark.incubator.apache.org/
[2]: https://github.com/ooyala/spark-jobserver
[3]: http://www.ooyala.com/
[4]: http://spark-summit.org/talk/chan-the-spark-job-server/
[5]: http://groups.google.com/a/cloudera.org/group/hue-user
[6]: https://twitter.com/gethue
[7]: https://github.com/ooyala/spark-jobserver/blob/master/job-server-tests/src/spark.jobserver/WordCountExample.scala
[8]: https://github.com/ooyala/spark-jobserver#wordcountexample-walk-through
