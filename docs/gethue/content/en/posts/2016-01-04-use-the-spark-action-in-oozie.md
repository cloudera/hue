---
title: Use the Spark Action in Oozie
author: admin
type: post
date: 2016-01-04T22:37:05+00:00
url: /use-the-spark-action-in-oozie/
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
categories:

---
_<span style="color: #ff0000;">Update September 2016</span>: this post is getting replaced by <https://gethue.com/how-to-schedule-spark-jobs-with-spark-on-yarn-and-oozie/>_

<span style="font-weight: 400;">Hue offers a <a href="https://gethue.com/bay-area-bike-share-data-analysis-with-spark-notebook-part-2/">notebook</a> for Hadoop and Spark, but here are the following steps that will successfully guide you to execute a Spark Action from the </span>[<span style="font-weight: 400;">Oozie Editor</span>][1]<span style="font-weight: 400;">.</span>

**Run job in Spark Local Mode**

To submit a job locally, `Spark Master` can be one of the following

  * **local**: Run Spark locally with one worker thread.
  * **local[k]**: Run Spark locally with _K_ worker threads.
  * **local[*]**: Run Spark with as many worker threads as logical cores on your machine.

Insert the `Mode` as _client_ and provide local/HDFS jar path in `Jars/py` field. You would also need to specify the `App name`, `Main class `to the Jar and arguments (if any) by clicking on the `ARGUMENTS+` button.

[<img src="https://cdn.gethue.com/uploads/2015/12/local.png"/>][2]

**Note: **Spark's local mode doesn't run with Kerberos.

**Run job on Yarn**

To submit a job on **Yarn Cluster**, you need to change `Spark Master` to yarn-cluster, `Mode` to cluster and give the compete HDFS path for the Jar in `Jars/py files` field.

[<img src="https://cdn.gethue.com/uploads/2015/12/cluster.png"/>][3]

Similarly, to submit a job on **yarn-client**, change `Spark Master` to _yarn-client_, `Mode` to _client,_ keeping rest of the fields same as above. Jar path can be local or HDFS.

[<img src="https://cdn.gethue.com/uploads/2015/12/yarn-client.png"/>][4]

&nbsp;

Additional Spark-action properties can be set by clicking the settings button at the top right corner before you submit the job.

<a href="https://cdn.gethue.com/uploads/2016/01/running.png" ><img src="https://cdn.gethue.com/uploads/2016/01/running-1024x493.png"/></a>

**Note: **If you see the error "Required executor memory (xxxxMB) is above the max threshold...", please increase 'yarn.scheduler.maximum-allocation-mb' in Yarn config and restart Yarn service from CM.

Next version is going to include [HUE-2645][5], that will make the UI simple and more intuitive. As usual feel free to comment on the [hue-user][6] list or [@gethue][7]!

 [1]: https://gethue.com/new-apache-oozie-workflow-coordinator-bundle-editors/
 [2]: https://cdn.gethue.com/uploads/2015/12/local.png
 [3]: https://cdn.gethue.com/uploads/2015/12/cluster.png
 [4]: https://cdn.gethue.com/uploads/2015/12/yarn-client.png
 [5]: https://issues.cloudera.org/browse/HUE-2645
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue
