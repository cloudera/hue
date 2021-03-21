---
title: Grafana ダッシュボードによる Hue アクティビティの監視
author: Ying Chen
type: post
date: 2020-06-23T00:00:00+00:00
url: /monitoring-hue-activity-with-grafana-dashboards/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
#  - Version 4.8

---

[Hue のアクティブユーザーのメトリクスの改善](https://gethue.com/hue-active-users-metric-improvements/) の他に、過去10分間に実行されたクエリの数を示す、新しい[Prometheus](https://prometheus.io/)のメトリクス「クエリ数」も追加しました。どちらも Hue の <a href="https://grafana.com/">Grafana</a> ダッシュボードで利用できるようになっています。

Grafana のダッシュボードのリストを見てみると、Hue のフォルダに Hue の Home ダッシュボードがあります。

![grafana_dashboard_list.png](https://cdn.gethue.com/uploads/2020/06/grafana_dashboard_list.png)

Home ダッシュボードを開くと、CPU、メモリ、アクティブユーザー、クエリ数の4つのパネルが表示されます。[hue-home.json](https://github.com/cloudera/hue/blob/master/tools/kubernetes/grafana/hue-home.json) を Grafana にアップロードして同じグラフを生成できます。

![hue_grafana_graphs.png](https://cdn.gethue.com/uploads/2020/06/hue_grafana_graphs.png)

このダッシュボードは、管理者がデータウェアハウス内の Hue のパフォーマンスを監視するのに役立ちます。

フィードバックやご質問はありますか？何かあれば気軽に [Forum](https://discourse.gethue.com/) や [quick start](https://docs.gethue.com/quickstart/) までコメントください。Live SQL querying!

Ying Chen from the Hue Team
