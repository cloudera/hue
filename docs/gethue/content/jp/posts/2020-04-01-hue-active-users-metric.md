---
title: Hue のアクティブユーザーのメトリクスの改善
author: Ying Chen
type: post
date: 2020-04-01T00:00:00+00:00
url: /hue-active-users-metric-improvements/
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
#  - Version 4.7

---


Hue のパフォーマンスを理解するために、Hue のアクティブユーザーの数、より具体的には、各ホストでのアクティブユーザーの数を知りたいと思っています。アクティブなユーザーとは、過去1時間以内にブラウザから Hue サーバーにリクエストを送信したユーザーのことです。最近、Hue はより良いメトリクスを提供して表示するために行くつかの改善が行われました。

1. オンプレミスでは、Hue は [PyFormance](https://gethue.com/easier-administration-of-hue-with-the-new-threads-and-metrics-pages/) を使用して /desktop/metrics エンドポイントを実装しています。Cloudera Manager はエンドポイント経由でデータを収集し、チャートライブラリに「Active Users」メトリクスを表示しますが、どのホストも同じ数のアクティブユーザーを表示しています。[HUE-9210](https://issues.cloudera.org/browse/HUE-9210) では、各ホストのアクティブユーザーのメトリクスは、ホスト名に基づいて収集されています。 (スクリーンショットを参照してください)

	![cm_active_users.png](https://cdn.gethue.com/uploads/2020/04/cm_active_users.png)

ここでは、Hue API サーバーロールに青色の３人のユーザーと、別のサーバーロールに緑色の１人のユーザーがいることがわかります。

2. Kubernetesでは、Hue は [django-prometheus](https://gethue.com/collecting-hue-metrics-with-prometheus-in-kubernetes/) を使用してエンドポイント/メトリクスを実装しています。[HUE-9194](https://issues.cloudera.org/browse/HUE-9194) では、Prometheus サーバーに表示するための2つの新しいアクティブユーザーのメトリクスを追加しました。Kubernetes を使用せずに[Prometheus サーバーをセットアップ](https://gethue.com/set-up-prometheus-server-without-kubernetes/) しても構いません。設定が完了してサーバーが開始したら、ブラウザで localhost:9090 を開きます。メトリクスのドロップダウンメニューで hue_active_users と hue_local_active_users を見つけることができます。

	![prometheus_active_users.png](https://cdn.gethue.com/uploads/2020/04/prometheus_active_users.png)

このhue\_local\_active\_users は、ホスト名に基づいて、特定のコンテナベースのアクティブユーザーを表示していますが、hue\_active\_users will はデータウェアハウス内全てのユーザーを表示します。

何かフィードバックやコメントがあれば、このブログまたは @gethue まで気軽にコメントしてください。すぐに SQL のクエリを始めることができます！

Ying Chen from the Hue Team
