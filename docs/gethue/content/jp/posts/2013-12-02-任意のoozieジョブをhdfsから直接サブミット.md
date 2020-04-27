---
title: 任意のOozieジョブをHDFSから直接サブミットする
author: Hue Team
type: post
date: 2013-12-02T23:59:23+00:00
url: /任意のoozieジョブをhdfsから直接サブミット/
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
  - HUE-1476により、ユーザーはHDFSから直接Oozieのジョブをサブミットできます。単に設定をアップロードする、あるいは既存のワークスペースをブラウズし...
categories:
  - HDFS
  - Oozie
  - Tutorial
  - Video

---
<p id="docs-internal-guid-274cce61-b3d2-fe2c-661b-0f56659ca38c">
  <span><a href="https://issues.cloudera.org/browse/HUE-1476">HUE-1476</a></span>により、ユーザーはHDFSから直接Oozieのジョブをサブミットできます。単に設定をアップロードする、あるいは既存のワークスペースをブラウズし、ワークフロー、コーディネータ、バンドルを選択します。サブミットボタンが表示されたらワンクリックでジョブを実行させられます！
</p>

{{< youtube Un99eIrcdmk >}}

<span>ファイルブラウザはこれらをサポートしています:</span>

  * <span>workflow.xml、coordinator.xml、bundle.xmlのパラメータ</span>
  * <span>job.propertiesのパラメータ</span>

<span>Oozieのダッシュボードはこれらをサポートしています:</span>

  * <span>動的な進捗（プログレス）とログをレポート</span>
  * <span>ワンクリックでMapReduceのログにアクセス</span>
  * <span>停止、一時停止、再実行ボタン</span>

<span>ビデオのデモで使用していたワークフローのチュートリアルです　</span><span><a href="https://github.com/romainr/hadoop-tutorials-examples/tree/master/oozie/workflow_demo">workflow tutorial</a>（英語）</span><span><br /> </span>

<span>もちろん、XMLを避けたければ</span>[<span id="aef6f581-e6e0-430e-b064-e4588612b8a2">Oozie</span> Editor][1]を推奨します<span> 🙂</span>

 [1]: https://gethue.com/hadoop-tutorials-ii-2-execute-hive-queries-and