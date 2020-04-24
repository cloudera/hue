---
title: Impalaクエリエディタで高速なSQL
author: Hue Team
type: post
date: 2013-09-27T23:59:16+00:00
url: /impalaクエリエディタで高速なsql/
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
  - 以前のエピソードでは、Oozie Coordinatorで繰り返しのワークフローをスケジュールする方法について紹介しました。今回はImpalaで...
categories:
  - Full tutorial
  - Impala
  - Tutorial
  - Video

---
<div class="post_title">
  （<a href="https://gethue.com/fast-sql-with-the-impala-query-editor">原文はこちら</a>）
</div>

<div class="post_title">
</div>

<div class="post_title">
  <span>以前のエピソードでは、<a href="https://gethue.com/hadoop-tutorials-ii-3-schedule-hive-queries-with">Oozie Coordinator</a>で繰り返しのワークフローをスケジュールする方法について紹介しました。今回はImpalaでいくつかのデータをクエリするための近道を</span><span>見ていきましょう。</span>
</div>

<div class="post_body">
  <p>
    Hue（<a href="https://gethue.com/">the Hadoop UI</a>）では、ほぼ最初のバージョンからImpalaをサポートしており、ブラウザ内において高速な対話形式のクエリを提供します。もし<a href="http://blog.cloudera.com/blog/2012/10/cloudera-impala-real-time-queries-in-apache-hadoop-for-real/">Impala</a>について良く知らなければ、Hadoop用最速<a href="http://www.cloudera.com/content/support/en/documentation/cloudera-impala/cloudera-impala-documentation-v1-latest.html">SQLエンジン</a>のドキュメントをチェックすることをお勧めします。
  </p>
  
  <h1>
    Impalaアプリ
  </h1>
  
  <p>
    ImpalaはほとんどのHive SQLと互換性があるので、HiveとImpalaアプリケーションの両方で<a href="https://gethue.com/hadoop-tutorials-ii-1-prepare-the-data-for-analysis">エピソード１</a>（英語）のクエリを比較していきます。この比較は100%厳密ではありませんが、よくあるケースとして、どんなことが起こっているかのデモになっていることに気付かれるでしょう。
  </p>
  
  <p>
    {{< youtube FwcVA_pgmNY >}}
  </p>
  
  <p>
    HueアプリでImpalaを使用することは、コマンドラインツールのimpala-shellでImpalaを使用するよりも、いろいろな意味で簡単です。例えば、テーブル名、データベース、カラム（列）や組み込み関数は自動補完され、構文をハイライトすることでクエリの潜在的な誤りを表示します。複数のクエリや選択したクエリの一部分を、エディタ上から実行することができます。パラメータ化されている（変数を使う）クエリをサポートしているので、ユーザーがサブミットする時に、値を入力を求めるプロンプトを表示させることができます。Impalaのクエリは保存可能であり、ユーザー間で共有したり削除でき、その後間違った場合に備えてゴミ箱から復元できます。
  </p>
  
  <p>
    ImpalaはHiveと同じメタストアを使用するので、<a href="https://gethue.com/hadoop-tutorial-how-to-access-hive-in-pig-with">メタストアアプリ</a>でテーブルをブラウズできます。エディタからデータベースをドロップダウンして選択することも可能です。サブミットした後はクエリの進捗とログがレポートされ、クエリの結果は無限にスクロールさせてブラウズしたり、ブラウザでデータをダウンロードすることができます。
  </p>
  
  <h1>
    クエリの速度比較
  </h1>
  
  <p>
    簡単に入手できるHueのサンプルから始めてみましょう。これらはとても小さいデータですが、Impalaの電光石火のスピードと、Hiveによって生成された一連の非効率なMapReduceジョブを示します。
  </p>
  
  <p>
    HueでHiveとImpalaのサンプルがインストールされていることを確認し、その後、それぞれのアプリの「保存されたクエリ」に移動し、‘Sample: Top salaries’のクエリをコピーしてからサブミットします。
  </p>
  
  <p>
    その後、Yelpデータに戻ります。<a href="https://gethue.com/hadoop-tutorials-ii-1-prepare-the-data-for-analysis">エピソード１</a>のクエリを両方のアプリで実行します:
  </p>
  
  <pre><code class="sql">SELECT r.business_id, name, SUM(cool) AS coolness
FROM review r JOIN business b
ON (r.business_id = b.business_id)
WHERE categories LIKE '%Restaurants%'
AND `date` = '$date'
GROUP BY r.business_id, name
ORDER BY coolness DESC
LIMIT 10</code></pre>
  
  <p>
    繰り返しますが、Impalaの<a href="http://www.cloudera.com/content/cloudera-content/cloudera-docs/Impala/latest/Installing-and-Using-Impala/ciiu_concepts.html">アーキテクチャーと最適化</a>の恩恵をご覧いただけるでしょう。
  </p>
  
  <h1>
    まとめ
  </h1>
  
  <p>
    この記事は、Impalaのクエリ実行は、どのように対話的にデータ分析をしているかということと、Hiveのバッチアーキテクチャーより生産性が高いということを説明しています。結果は速やかに返ってきます。Yelpデータのケースでは、瞬時です。ImpalaとHueの組み合わせは、高速な分析のための秘訣でしょう。さらに、Hueの<a href="https://gethue.com/tutorial-executing-hive-or-impala-queries-with-python">Python API</a>は、独自のクライアントをビルドしたい場合に再利用することが可能です。
  </p>
  
  <p>
    <a href="https://ccp.cloudera.com/display/SUPPORT/Cloudera+QuickStart+VM">Cloudera’s demo VM</a>とそのHadoopチュートリアルは、最初にImpalaとHueを始めるのにとても良い方法です。 近日公開されるブログの投稿では、Impalaでのより効率的なファイルフォーマットの使用方法について説明する予定です。
  </p>
  
  <p>
    いつものように、何かあれば<a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a>メーリングリスト（英語）や、<a href="https://twitter.com/gethue">@gethue</a>に気軽にコメントして下さい。次回は、<a href="https://gethue.com/hadoop-tutorial-bundle-oozie-coordinators-with-hue">OozieバンドルでHadoopチュートリアルのシーズン２</a>（英語）です。
  </p>
</div>