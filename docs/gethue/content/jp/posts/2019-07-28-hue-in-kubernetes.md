---
title: Kubernetes で Hue
author: Hue Team
type: post
date: 2019-07-28T05:47:59+00:00
url: /hue-in-kubernetes/
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
sf_custom_excerpt:
  - |
    |
        デプロイをより自動化し、Kubernetesのようなコンテナーオーケストレーションで実行する方法を見てみましょう。
        私たちは、以前のブログで最新の Hue ウェブサーバーを「ボックス」にまとめる Hue Docker image 記事を紹介しました。

categories:
  - Cloud
  - Hue 4.5

---
デプロイをより自動化し、[Kubernetes][1]のようなコンテナーオーケストレーションで実行する方法を見てみましょう。

&nbsp;

私たちは、前のブログで最新の Hue ウェブサーバーを「ボックス」にまとめる [Hue Docker image][2] 記事をを紹介しました。

Hue には Helm チャートが付属しているので、作業を簡単に始めることができます。[Helm][3] は Kubernetes 用のパッケージマネージャーです。より高度な方法には [yaml config files][4]を直接使用する方法があります。

Helm をインストールした後にシェルで次の3つの手順を実行して、データベースとともにライブの hue を起動します。

<pre><code class="bash">helm repo add gethue https://helm.gethue.com
helm repo update
helm install hue gethue/hue
</pre>

[<img class="aligncenter size-full wp-image-5131" src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png" alt="" width="512" height="457" />][5]

次の手順の説明が画面に表示されます。その後 [Helm repo][6] で詳細をご覧いただくことができます。

Hue は [Helm catalog][7] カタログにも記載されています。: <https://hub.helm.sh/charts/hue/hue>

&nbsp;

<div class="body-text clearfix">
  <div>
    フィードバックやご質問はありますか？何かありましたらこちら、あるいは <a href="https://twitter.com/gethue">@gethue</a>!
  </div>

  <p>
    までお気軽にコメントお願いします。
  </p>
</div>

 [1]: https://kubernetes.io/
 [2]: http://jp.gethue.com/getting-started-with-hue-in-2-minutes-with-docker/
 [3]: https://helm.sh/
 [4]: https://github.com/cloudera/hue/tree/master/tools/kubernetes/yaml
 [5]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png
 [6]: https://github.com/cloudera/hue/tree/master/tools/kubernetes/helm/hue
 [7]: https://helm.sh/blog/intro-helm-hub/
