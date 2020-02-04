---
title: Apache Oozieの新しいワークフロー、コーディネーター＆バンドルエディタ
author: Hue Team
type: post
date: 2015-04-03T10:51:04+00:00
url: /new-apache-oozie-workflow-coordinator-bundle-editors-2/
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
sf_custom_excerpt:
  - |
    OozieはHueの初期の主要な最初のアプリケーションのひとつです。私たちは継続的により良くなるように投資しており、ちょうどOozieエディタに大きな変更を行いました。
    
    Oozieエディタのこの改良では新しいデザインをもたらし、Oozieに必要な知識ははるかに少なくてすみます！ワークフローは、今や10個の新機能をサポートし、セットアップは数回クリックするだけです！
categories:
  - Hue 3.8
  - Oozie
  - Video

---
OozieはHueの[初期の主要な][1]最初のアプリケーションのひとつです。私たちは継続的により良くなるように投資しており、ちょうどOozieエディタに大きな変更を行いました。

Oozieエディタのこの改良では新しいデザインをもたらし、[Oozie][2]に必要な知識ははるかに少なくてすみます！ワークフローは、今や10個の[新機能][3]をサポートし、セットアップは数回クリックするだけです！

&nbsp;

{{< youtube ON15jrXpqeI >}}

&nbsp;

ビデオで使用されているファイルは[Oozie][4]のサンプルによるものです 。

新しいインターフェイスでは、アクションの最も重要なプロパティのみを満たすように要求され、ファイルのパスと他のジョブを検証するためのクイックリンクが提供されています。HiveとPigのスクリプトファイルはパラメータを抽出するために構文解析され、それらがオートコンプリートで直接提案されます。現在の場所のノードにちょうどオーバーラップするように、アクションの高度な機能がはるかに少ない軋轢で、新しい種類のポップアップがご利用いただけます。

&nbsp;

<div id="attachment_2418" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2015/03/new-oozie.png"><img class="wp-image-2418 size-large" src="https://cdn.gethue.com/uploads/2015/03/new-oozie-1024x557.png" alt="new-oozie" width="1024" height="557" data-wp-pid="2418" /></a>
  
  <p class="wp-caption-text">
    新しいエディタ
  </p>
</div>

<div id="attachment_2419" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor.png"><img class="size-large wp-image-2419" src="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor-1024x602.png" alt="New Editor (edit mode)" width="1024" height="602" data-wp-pid="2419" /></a>
  
  <p class="wp-caption-text">
    新しいエディタ（編集モード）
  </p>
</div>

<div id="attachment_2421" style="width: 1034px" class="wp-caption aligncenter">
  <a href="https://cdn.gethue.com/uploads/2015/03/old-oozie.png"><img class="size-large wp-image-2421" src="https://cdn.gethue.com/uploads/2015/03/old-oozie-1024x561.png" alt="Old Editor" width="1024" height="561" data-wp-pid="2421" /></a>
  
  <p class="wp-caption-text">
    古いエディタ
  </p>
</div>

&nbsp;

2つの新しいアクションが追加されています::

  * HiveServer2
  * Spark

[<img class="aligncenter size-full wp-image-2426" src="https://cdn.gethue.com/uploads/2015/03/new-spark-hs2-actions.png" alt="new-spark-hs2-actions" width="161" height="71" data-wp-pid="2426" />][5]

そして、Pigのユーザーエクスペリエンスとサブワークフローが簡略化されています。

&nbsp;

デシジョン（分岐）ノードのサポートは改善されました。既存のアクションのコピーも今やドラッグ＆ドロップするだけです。いくつかのレイアウトは「ok」および「end」ノードが個別に変更することができるようになりました。

[<img class="aligncenter size-full wp-image-2427" src="https://cdn.gethue.com/uploads/2015/03/oozie-avanced-action-options.png" alt="oozie-avanced-action-options" width="590" height="380" data-wp-pid="2427" />][6]

&nbsp;

コー​​ディネーターは、大幅に改善されました！Oozieデータセットの概念はもはや必要ありません。エディタはワークフローのパラメータを取り込み、3種類の入力が用意されています:

  * **parameters**: 定数または時間のようなOozie EL機能
  * **input path**: 入力パスの依存関係をパラメータ化し、例えばそれが存在するのを待つ
  * **output path**: 入力パスと同様だが、ジョブ開始時に存在している必要はない

[<img class="aligncenter size-large wp-image-2428" src="https://cdn.gethue.com/uploads/2015/03/oozie-new-coordinator-1024x376.png" alt="oozie-new-coordinator" width="1024" height="376" data-wp-pid="2428" />][7]

&nbsp;

恐ろしいUTCのタイムゾーン形式は、カレンダーまたはいくつかのヘルパーウィジェットのいずれかにより、直接提供されておりません。

[<img class="aligncenter size-full wp-image-2429" src="https://cdn.gethue.com/uploads/2015/03/oozie-new-submit-popup.png" alt="oozie-new-submit-popup" width="770" height="567" data-wp-pid="2429" />][8]

&nbsp;

**まとめ**

わかりやすいエンドユーザーエクスペリエンスを提供することに加えて、この新しいアーキテクチャはイノベーションを切り開きます。

まず、エディタで新しいOozieアクションを追加することが容易になります。しかし、最も重要なのは、ワークフローは新しいHueのドキュメントモデルを使用して永続化され、それらの[インポート/エクスポート][9]の意図が簡略化され、直接UIからすぐに利用できるようになります。このモデルは保存されたHive、Pig、Sparkジョブをワークフローに単に直接ドラッグ＆ドロップするだけで、ワークフローを次世代で有効にできるようにもなります。手動でHDFS上のクエリを複製する必要はありません！

これはまた、コーディネーターとしてHueに保存されている任意のジョブの使用を、ワンクリックでスケジュールするための扉を開きます。私たちは新しいエディタを改善し続けている一方で、次にアプリケーションの [ダッシュボードセクション][10]のメジャーな改良をご覧いただけるようになるでしょう！

&nbsp;

いつものように、コメントとフィードバックは[hue-user][11] メーリングリストや[@gethue][12]!までお気軽に！

&nbsp;

**注意**

古いワークフローは自動的に新しいフォーマットに変換されません。Hueはあなたのためにそれらをインポートしようとし、問題が発生した場合は古いエディタで開きます。

[<img class="aligncenter size-large wp-image-2430" src="https://cdn.gethue.com/uploads/2015/03/oozie-import-try-1024x566.png" alt="oozie-import-try" width="1024" height="566" data-wp-pid="2430" />][13]

新しい[import/export][14]はHue4で予定されています。それは、ワークフローをHueのフォーマットからXML / JSON Hueフォーマットの両方でエクスポートし、Hueのフォーマットからインポートできるようになります。

 [1]: https://gethue.com/category/oozie/
 [2]: http://oozie.apache.org/
 [3]: https://issues.cloudera.org/browse/HUE-2180
 [4]: https://github.com/cloudera/hue/tree/master/apps/oozie/examples/workflows
 [5]: https://cdn.gethue.com/uploads/2015/03/new-spark-hs2-actions.png
 [6]: https://cdn.gethue.com/uploads/2015/03/oozie-avanced-action-options.png
 [7]: https://cdn.gethue.com/uploads/2015/03/oozie-new-coordinator.png
 [8]: https://cdn.gethue.com/uploads/2015/03/oozie-new-submit-popup.png
 [9]: https://gethue.com/export-and-import-your-oozie-workflows/
 [10]: https://issues.cloudera.org/browse/HUE-2644
 [11]: http://groups.google.com/a/cloudera.org/group/hue-user
 [12]: https://twitter.com/gethue
 [13]: https://cdn.gethue.com/uploads/2015/03/oozie-import-try.png
 [14]: https://issues.cloudera.org/browse/HUE-1660