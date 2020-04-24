---
title: HadoopとSolrでApacheのログを分析し、独自のウェブ分析ダッシュボードを構築する
author: Hue Team
type: post
date: 2014-06-21T00:00:23+00:00
url: /analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr-2/
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
slide_template:
  - default
sf_custom_excerpt:
  - Hue (3.6 またはもうすぐ登場するCDH5.1) には、検索用の動的ダッシュボードビルダーが同梱されています。私たちは以前にSearchのエピソードで新しいインタフェースを紹介しました....
categories:
  - Search
  - Tutorial
  - Video

---
Hue (3.6 またはもうすぐ登場するCDH5.1) には、検索用の動的ダッシュボードビルダーが同梱されています。私たちは以前に<a href="https://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr-2/?lang=ja" target="_blank">Searchのエピソード</a>で新しいインタフェースを紹介しました。

これは第2章です！私たちは[Apache][1]のログデータをどのようにインデックスし、数回のクリックで同じダッシュボードを再作成する方法を紹介しました。このビデオでは、ライブの[Hadoopクラスター][2]、[demo.gethue.com][3]からの実際のApacheのログを使用しています:

{{< youtube wwi2K0UPG0E >}}

最後までスキップしたい場合、ログファイルは [ここ][4]から利用できるように準備されています.

[How to Proxy Hue][5] （日本語未提供）のブログで説明したように、全てのページビューのApacheのログを取得しています。プロダクションのマシンからログを取得し、それらをクリーンアップし、Solrのスキーマのフィールドに抽出して各ページをgeoローカライズする[スクリプト][6]をダウンロードします。

この新しいインデクサライブラリにより、手作業の手順を行うことなく Hueの[検索のサンプル][7]をインストールすることができます。次の機能では、クエリ時に自動的なgeoローカライズ、HiveやHBaseのテーブルのインデキシング、[Morphline][8] エディタが含まれるようになるでしょう。 (基本的にPython部分を取り除き、GB以上のデータ取得ができるようになるでしょう）

いつものように、フィードバックは[hue-user][9]メーリングリストや[@gethue][10]までお気軽に！

 [1]: https://httpd.apache.org/
 [2]: https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/
 [3]: http://demo.gethue.com
 [4]: https://raw.githubusercontent.com/cloudera/hue/master/apps/search/examples/collections/solr_configs_log_analytics_demo/index_data.csv
 [5]: https://gethue.com/i-put-a-proxy-on-hue/
 [6]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/search/indexing
 [7]: https://gethue.com/tutorial-live-demo-of-search-on-hadoop/
 [8]: http://cloudera.github.io/cdk/docs/current/cdk-morphlines/index.html
 [9]: http://groups.google.com/a/cloudera.org/group/hue-user
 [10]: https://twitter.com/gethue