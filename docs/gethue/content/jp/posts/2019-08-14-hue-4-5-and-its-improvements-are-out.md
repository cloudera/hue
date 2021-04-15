---
title: Hue 4.5とその改善点が公開されました！
author: Hue Team
type: post
date: 2019-08-14T03:08:17+00:00
url: /hue-4-5-and-its-improvements-are-out/
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
  - SQLデータ探検家の皆さん、Hueチームはすべての貢献者に感謝し、Hue 4.5がリリースできることを嬉しく思います！
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
  - Cloud
  - Editor / Notebook
  - Hue 4.5
  - Release

---
SQLデータ探検家の皆さん、

&nbsp;

Hueチームはすべての貢献者に感謝し、Hue 4.5がリリースできることを嬉しく思います！ 

<img class="" src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" alt="hue-logo" width="85" height="63" />

このリリースの焦点は技術的なスタックをモジュール化し、SQLの統合を改善し、今後の主要機能の準備をすることでした。

このリリースには 660 件のコミットと 150 件以上のバグフィックスが含まれています！全ての変更点は[リリースノート][2]をご覧ください。

簡単に試すにはいくつかの方法があります。


* [Tarball](https://cdn.gethue.com/downloads/hue-4.5.0.tgz) or [source][3]
* From <a href="https://github.com/cloudera/hue/tree/master/tools/docker">Docker Hub</a>
    ```
    docker pull gethue/4.5.0
    ```
* [demo.gethue.com][4]
* Kubernetes cluster
    ```
    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue
    ```

<a href="https://cdn.gethue.com/uploads/2019/08/hue_4.5.png"><img src="https://cdn.gethue.com/uploads/2019/08/hue_4.5.png" /></a>

これらは主要な改善の一覧です:

<div>
  <h2>
    SQL
  </h2>

  <ul>
    <li>
      <a href="https://gethue.com/realtime-catalog-search-with-hue-and-apache-atlas/">Apache Atlasの統合とカタログAPI（英語）</a>
    </li>
    <li>
      <a href="https://docs.gethue.com//administrator/configuration/editor/#hiv">Hive LLAP + Service discovery（英語）</a>
    </li>
    <li>
      <a href="http://jp.gethue.com/built-in-hive-language-reference-in-the-sql-editor/">SQLエディタでの組み込みHive言語リファレンス</a>
    </li>
    <li>
      <a href="http://jp.gethue.com/sql-querying-apache-hbase-with-apache-phoenix/">HBase Phoenix クエリの例</a>
    </li>
  </ul>

  <h2>
    インターフェース
  </h2>

  <ul>
    <li>
      左側のメニューの刷新
    </li>
    <li>
      ストレージ(HDFS, ADLS, S3）を集約した左側のアシストパネル
    </li>
    <li>
      <a href="https://gethue.com/2x-faster-page-load-time-with-the-new-bundling-of-javascript-files/">Webpackの統合（英語）</a>
    </li>
  </ul>

  <h2>
    ドキュメントの刷新
  </h2>

  <ul>
    <li>
      <a href="https://gethue.com/build-your-own-autocompleter/">Building SQL Autocompletes（英語）</a>
    </li>
    <li>
      <a href="https://docs.gethue.com//administrator/administration/reference/">Architecture（英語）</a>
    </li>
    <li>
      <a href="https://docs.gethue.com//administrator/configuration/editor/">SQL connectors refresh（英語）</a>
    </li>
  </ul>

  <h2>
    クラウド
  </h2>

  <ul>
    <li>
      <a href="http://jp.gethue.com/hue-in-kubernetes/">Kubernetes Helm</a>
    </li>
    <li>
      <a href="http://jp.gethue.com/quick-start-a-hue-development-environment-in-3-minutes-with-docker/">Docker</a>
    </li>
    <li>
      <a href="https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/">継続的インテグレーション（英語）</a>
    </li>
  </ul>
</div>

&nbsp;

<span class="notranslate">製品を使用し、このリリースに貢献したすべての人に感謝します。</span> <span class="notranslate">さあ、次のステップへ！</span> <span class="notranslate">（Python 3サポート、Apache Knoxの統合、その他のSQL / クラウド機能）</span>

いつものように、すべてのプロジェクトの貢献者、[フォーラム][6]または [@gethue][7]に参加してフィードバックを送ってくれた皆さんに感謝申し上げます！

その先へ!

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://docs.gethue.com//releases/release-notes-4.5.0/
 [3]: https://github.com/cloudera/hue/archive/release-4.5.0.zip
 [4]: http://demo.gethue.com/
 [5]: https://cdn.gethue.com/uploads/2019/08/hue_4.5.png
 [6]: https://discourse.gethue.com/
 [7]: https://twitter.com/gethue
