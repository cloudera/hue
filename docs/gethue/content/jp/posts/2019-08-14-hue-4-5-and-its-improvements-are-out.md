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

Hueチームはすべての貢献者に感謝し、Hue 4.5がリリースできることを嬉しく思います！ [<img class="aligncenter size-full wp-image-2988" src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" alt="hue-logo (copy)" width="85" height="63" data-wp-pid="2988" />][1]

&nbsp;

<div>
  <div>
    このリリースの焦点は技術的なスタックをモジュール化し、SQLの統合を改善し、今後の主要機能の準備をすることでした。
  </div>
  
  <div>
    <div>
    </div>
    
    <p>
      <span class="notranslate">このリリースには、660件のコミットと150件以上のバグ修正が含まれています！</span> <span class="notranslate">すべての変更については、 <a href="https://translate.googleusercontent.com/translate_c?depth=1&rurl=translate.google.com&sl=auto&sp=nmt4&tl=ja&u=https://docs.gethue.com/latest/releases/release-notes-4.5.0/&xid=17259,1500004,15700021,15700043,15700186,15700191,15700256,15700259,15700262,15700265&usg=ALkJrhg7zr7TvqvwrM7rJ29y_sVZInj4dg">リリースノートをご覧ください</a> 。</span>
    </p>
  </div>
</div>

このリリースには 660 件のコミットと 150 件以上のバグフィックスが含まれています！全ての変更点は[リリースノート][2]をご覧ください。

tarballまたは[ソース][3]を入手して試してみてください！簡単に試してみるには<span style="font-weight: 400;">&#8216;<a href="https://github.com/cloudera/hue/tree/master/tools/docker">docker pull gethue/4.5.0</a>&#8216;、または起動中の</span>[<span style="font-weight: 400;">demo.gethue.com</span>][4]<span style="font-weight: 400;">が使用できます。</span>Kubernetes クラスターをお持ちの場合:

<pre><code class="bash">helm repo add gethue https://helm.gethue.com 
helm repo update 
helm install gethue/hue 
</pre>

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/hue-4.5.0.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

[<img class="aligncenter size-full wp-image-6044" src="https://cdn.gethue.com/uploads/2019/08/hue_4.5.png" alt="" width="1601" height="902" />][5]

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
      <a href="https://docs.gethue.com/latest/administrator/configuration/editor/#hiv">Hive LLAP + Service discovery（英語）</a>
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
      <a href="https://docs.gethue.com/latest/administrator/administration/reference/">Architecture（英語）</a>
    </li>
    <li>
      <a href="https://docs.gethue.com/latest/administrator/configuration/editor/">SQL connectors refresh（英語）</a>
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

As usual thank you to all the project contributors and for sending feedback and participating on the

いつものように、すべてのプロジェクトの貢献者、[フォーラム][6]または [@gethue][7]に参加してフィードバックを送ってくれた皆さんに感謝申し上げます！

その先へ!

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://docs.gethue.com/latest/releases/release-notes-4.5.0/
 [3]: https://github.com/cloudera/hue/archive/release-4.5.0.zip
 [4]: http://demo.gethue.com/
 [5]: https://cdn.gethue.com/uploads/2019/08/hue_4.5.png
 [6]: https://discourse.gethue.com/
 [7]: https://twitter.com/gethue