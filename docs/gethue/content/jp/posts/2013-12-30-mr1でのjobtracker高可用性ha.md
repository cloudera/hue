---
title: MR1でのJobTracker高可用性(HA)
author: Hue Team
type: post
date: 2013-12-30T23:59:57+00:00
url: /mr1でのjobtracker高可用性ha/
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
sf_custom_excerpt:
  - JobTrackerがダウンすると、Hueはファイルブラウザでジョブを表示したり、正しいクラスタにジョブをサブミットできなくなります。MR1では、...
categories:
  - Job Browser
  - MapReduce

---
<p id="docs-internal-guid-60fb361f-4405-815e-a36b-72434b0895db">
  <span>JobTrackerがダウンすると、Hueはファイルブラウザでジョブを表示したり、正しいクラスタにジョブをサブミットできなくなります。</span>
</p>

&nbsp;

<span>MR1では、Hadoopは2つのJobTrackerをサポートすることができ、マスターのJobTrackerはスタンバイのJobTrackerにフェイルオーバすることができ、故にJobTrackerの高可用性を提供しています。 </span><span><a href="https://gethue.com/hue-3-5-and-its-redesign-are-out">Hue 3.5</a>と</span>[<span>CDH5beta1</span>][1] <span>(とおそらくCDH4.6)ではどのようにしているかを見てみましょう。</span>

&nbsp;

<span>注</span>: MR1のHueはJobTrackerと通信するために[plugin][2]を使用しています。これはCDH、あるいはHadoop 0.23 / 1.2.0に設定することができます。 ([MAPREDUCE-461][3])

&nbsp;

<span><a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L336">hue.ini</a>で2つのJobTrackerを設定します</span><span>:</span>

<pre class="code">[hadoop]
  ...

  [[mapred_clusters]]

    [[[default]]]
      # Enter the host on which you are running the Hadoop JobTracker
      jobtracker_host=host-1

      # Whether to submit jobs to this cluster
      submit_to=True

    [[[ha-standby]]]
      # Enter the host on which you are running the Hadoop JobTracker
      jobtracker_host=host-2

      # Whether to submit jobs to this cluster
      submit_to=True</pre>

&nbsp;

<span>これだけです! Hueは自動的に2つの利用可能なJobTrackerと通信します!</span>

&nbsp;

<span>Oozieのジョブでは注意が必要です。Oozieはジョブを再度サブミットしようとしますが、論理名が必要です(</span>[<span>HUE-1631</span>][4]<span>)。Hueでこれを有効にするには、MapReduceクラスタそれぞれで指定します。例: </span>

&nbsp;

<pre class="code">[hadoop]
  [[mapred_clusters]]
    [[[default]]]
      # JobTracker logical name.
      ## logical_name=MY_NAME</pre>

<span>いつものように、コメントがあれば</span>[<span> </span><span>hue-user</span>][5]<span> リストまたは</span><span><a href="https://twitter.com/gethue">@gethue</a>まで!</span><span><br /> </span>

 [1]: http://www.cloudera.com/content/support/en/documentation/cdh5-documentation/cdh5-documentation-v5-latest.html
 [2]: http://cloudera.github.io/hue/docs-3.5.0/manual.html#_configure_mapreduce_0_20_mr1
 [3]: https://issues.apache.org/jira/browse/MAPREDUCE-461
 [4]: https://issues.cloudera.org/browse/HUE-1631
 [5]: http://groups.google.com/a/cloudera.org/group/hue-user