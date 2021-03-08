---
title: MRv2でのYARN Resource Managerの高可用性 (HA)
author: Hue Team
type: post
date: 2014-06-19T00:00:35+00:00
url: /hadoop-tutorial-yarn-resource-manager-high-availability-ha-in-mr2-2/
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
sf_custom_excerpt:
  - JobTracker High Availability configuration for MR1と同じように、HueはResource Managerがダウンした場合のためにひとつ以上のResource Managerをサポートします。...
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
slide_template:
  - default
categories:
  - Job Browser
  - MapReduce
  - YARN

---
[JobTracker High Availability configuration for MR1][1]と同じように、HueはResource Managerがダウンした場合のためにひとつ以上のResource Managerをサポートします。(本日以降のMaster、または Hue 3.7、または CDH5.1からの予定）

Resource Managerがフェイルオーバーした場合でさえ、Hueは自動的にアクティブなResource Managerを自動的にピックアップします。これは以下により実現可能です:

  * Oozieジョブをサブミットする際、現在のResource Managerのホスト名の代わりにResource Managerの論理名が使用される
  * Job Browserは必要な場合、自動的にアクティブなResource ManagerのAPIを探す

これは hue.ini の[[yarn_clusters]]セクションの設定例です:

<pre><code class="bash">[hadoop]

  # Configuration for YARN (MR2)
  # ------------------------------------------------------------------------
  [[yarn_clusters]]

    [[[default]]]

      # Whether to submit jobs to this cluster
      submit_to=True

            # Name used when submitting jobs
            logical_name=ha-rm

      # URL of the ResourceManager API
      resourcemanager_api_url=https://gethue-1.com:8088

      # URL of the ProxyServer API
      proxy_api_url=https://gethue-1.com:8088

      # URL of the HistoryServer API
      history_server_api_url=https://gethue-1.com:19888

    [[[ha]]]
      # Enter the host on which you are running the failover Resource Manager
      resourcemanager_api_url=https://gethue-2.com:8088
      logical_name=ha-rm
      submit_to=True
</pre>

私たちは、複数のResource ManagerのサポートがあなたのHadoopライフを簡単にすることを願っています！

いつものように、フィードバックはお気軽に[hue-user][2]メーリングリストや[@gethue][3]までお送り下さい！

 [1]: https://gethue.com/jobtracker-high-availability-ha-in-mr1/
 [2]: http://groups.google.com/a/cloudera.org/group/hue-user
 [3]: https://twitter.com/gethue
