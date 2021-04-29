---
title: コンテナーアプリをパッケージとして配布する
author: Hue Team
type: post
date: 2021-04-19T00:00:00+00:00
url: /blog/2021-04-19-publish-kubernetes-container-application-via-package-with-helm/
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4.10
  - Development
---

Kubernetes アプリケーションの Helm チャートを作成して公開します。

[Helm](https://helm.sh/) は [Kubernetes](https://kubernetes.io/) のパッケージマネージャであり、アプリを簡単に公開できるようにすることで、3行でインストールできるようになります。 例えば、 [Hue SQL Editor](http://gethue.com/) の場合:

    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue

![3-step process of packaging](https://cdn-images-1.medium.com/max/2000/1*I2e20tzUP292Kid7g5aI7g.png)*パッケージングの3ステッププロセス*

Helm の世界では、チャートは Python や JavaScript の世界での伝統的なパッケージやモジュールと同義語です。

チャートを構築するには、Helm チャートのルートから package コマンドを使用するだけです。 Hue [Helmディレクトリ](https://github.com/cloudera/hue/tree/master/tools/kubernetes/helm) を例に説明します。

    cd hue/tools/kubernetes/helm/
    helm package hue

その後、外部にパブリッシュし、インデックスを作成し、 [Helmリポジトリ](https://helm.sh/docs/topics/chart_repository/) で公開します。Helm リポジトリはシンプルな静的Webサーバーで構いません。

例えば、Apacheサーバーの場合、ホストにコピーします。

    scp hue-1.0.1.tgz root@101.200.100.200:/var/www/helm.gethue.com

次に、サーバーに接続し、パッケージをインデックスします。

    ssh root@101.200.100.200
    cd /var/www/helm.gethue.com
    
    helm repo index .

注: これらは手動のステップですが、当然ながら自動化できます。 また、サーバーのログをチェックして、何人がインストールしたかをすることもできます。

そうすると、ユーザーは [ローリングアップグレード](/blog/2021-03-06-web-api-service-upgrade-no-downtime-kubernetes-rollout/)、 [メトリクス](/hue-active-users-metric-improvements/)、 [トレース](/introducing-request-tracing-with-opentracing-and-jaeger-in-kubernetes/)などのKubernetesの機能を活用できるようになります。

Happy Helming!

![](https://cdn-images-1.medium.com/max/2302/1*zaO_Ww2MP8EPNj9_YO8pgQ.png)

</br> </br>

ご意見やご質問はありますか? ここや<a href="https://github.com/cloudera/hue/discussions">ディスカッション</a> で気軽にコメントし、<a href="https://docs.gethue.com/quickstart/">SQLクエリ</a> のクイックスタートをしてください！

Romain from the Hue Team
