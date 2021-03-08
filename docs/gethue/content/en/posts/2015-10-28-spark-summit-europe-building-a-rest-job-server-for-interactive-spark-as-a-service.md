---
title: 'Spark Summit Europe: Building a REST Job Server for interactive Spark as a service'
author: admin
type: post
date: 2015-10-28T16:10:18+00:00
url: /spark-summit-europe-building-a-rest-job-server-for-interactive-spark-as-a-service/
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
#  - News

---
# [Building a REST Job Server for interactive Spark as a service][1]

Livy is a new open source Spark REST Server for submitting and interacting with your Spark jobs from anywhere. Livy is conceptually based on the incredibly popular IPython/Jupyter, but implemented to better integrate into the Hadoop ecosystem with multi users. Spark can now be offered as a service to anyone in a simple way: Spark shells in Python or Scala can be ran by Livy in the cluster while the end user is manipulating them at his own convenience through a REST api. Regular non-interactive applications can also be submitted. The output of the jobs can be introspected and returned in a tabular format, which makes it visualizable in charts. Livy can point to a unique Spark cluster and create several contexts by users. With YARN impersonation, jobs will be executed with the actual permissions of the users submitting them. Livy also enables the development of Spark Notebook applications. Those are ideal for quickly doing interactive Spark visualizations and collaboration from a Web browser! This talk is technical and details the architecture and design decisions taken for developing this server, as well as its internals. It also describes the alternatives we tried and the challenges that were faced. The capabilities of Livy will then be lived demo in Hue’s Notebook Application through a real life scenario.

Examples:

  * [Interactive shells][2]
  * [Sharing RDDs][3]
  * [Batch jobs][4]
  * [Notebook][5]

{{< youtube AHYq91i-ohI >}}

&nbsp;

 <iframe style="border: 1px solid #CCC; border-width: 1px; margin-bottom: 5px; max-width: 100%;" src="//www.slideshare.net/slideshow/embed_code/key/2owAU68H0iGJ2h" width="900" height="500" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" allowfullscreen="allowfullscreen"></iframe>

<div style="margin-bottom: 5px;">
  <strong> <a title="Spark Summit Europe: Building a REST Job Server for interactive Spark as a service" href="//www.slideshare.net/gethue/spark-summit-europe-building-a-rest-job-server-for-interactive-spark-as-a-service" target="_blank" rel="noopener noreferrer">Spark Summit Europe: Building a REST Job Server for interactive Spark as a service</a> </strong> from <strong><a href="//www.slideshare.net/gethue" target="_blank" rel="noopener noreferrer">gethue</a></strong>
</div>

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2015/10/IMG_5690-1024x768.jpg"  />][6]

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2015/10/spark-summit-eu-stage-1024x372.jpg" />][7]

 [1]: https://spark-summit.org/eu-2015/events/building-a-rest-job-server-for-interactive-spark-as-a-service/
 [2]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-for-interactive-spark/
 [3]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-sharing-spark-rdds-and-contexts/
 [4]: https://gethue.com/how-to-use-the-livy-spark-rest-job-server-api-for-submitting-batch-jar-python-and-streaming-spark-jobs/
 [5]: https://gethue.com/new-notebook-application-for-spark-sql/
 [6]: https://cdn.gethue.com/uploads/2015/10/IMG_5690.jpg
 [7]: https://cdn.gethue.com/uploads/2015/10/spark-summit-eu-stage.jpg
