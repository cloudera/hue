---
title: ダウンタイムなしに Web/API サービスのアップグレードを行う
author: Hue Team
type: post
date: 2021-03-06T00:00:00+00:00
url: /blog/2021-03-06-web-api-service-upgrade-no-downtime-kubernetes-rollout/
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

Kubernetes のロールアウトを活用して。

この記事は、[Hue Query Service](http://gethue.com/) がどのように構築されているのかを説明する一連の投稿です。

自動化がうまくいくと、反復的な作業から解放されると同時に、プロセスが文書化されるので、テームメンバーはより生産的に付加価値のある仕事ができるようになり、勢いを維持することができます。

さて、プロジェクトのウェブ際の更新を、ダウンタイムや手作業を伴わずに自動的に行うにはどうすれば良いでしょうか。

![[gethue.com](http://gethue.com)](https://cdn-images-1.medium.com/max/2596/1*MDLckdtZbtPCOsk6ghb4ug.png)*[gethue.com](http://gethue.com)*

[gethue.com](https://gethue.com/) と [docs.gethue.com](https://docs.gethue.com/) ([jp.gethue.com](https://jp.gethue.com/) も忘れてはいけません) の全ては、メインの Kubernetes クラスタ内の小さなコンポーネントで動作しています。コンテナはこの種の静的なウェブサイトには少々太っ腹かもしれませんが、ソースコードの変更によって自動的に駆動し、全てのサービスが全く同じ流れに沿って調和するという便利なパターンを可能にしています。

例えば [demo.gethue.com](https://demo.gethue.com/) では、デモウェブサイトで提供されている他のデータベースエンジンと同様に、同じデプロイのロジックを再利用しています。これらのウェブサイトも UI ではなく、GitHub の[コードの変更](https://github.com/cloudera/hue/tree/master/docs/gethue)によって駆動されます。

例えば、以下は実行中のウェブサイトです。

    kubectl get pods -ngethue
    NAME READY STATUS RESTARTS AGE
    docs-55bf874485-vjnlf 1/1 Running 1 8h
    website-5c579d4dd-kqlvt 1/1 Running 0 60m
    website-jp-964f9cc57-h97gz 1/1 Running 0 6h38m

最近まで、毎日の再起動を「難しい方法」で行っていました。

    kubectl delete pods -ngethue `kubectl get pods -ngethue | egrep ^website | cut -d" "-f1`

これは「動作する」のですが、必要のないダウンタイムや「ノイズ」が発生します。

![Hammered by “website is down” notifications](https://cdn-images-1.medium.com/max/2814/1*UxngKW7HUxkjEhjPH3Cc1A.png)*「Website is down」という通知に悩まされる*

現在、標準的な Kubernetes の[rollout](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) コマンドが使用されており、管理者や一般ユーザにとって等価的な移行となっています。

    kubectl rollout restart -ngethue deployment/website

![First diagram from the [Kubernetes documention](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) demoing a rollout](https://cdn-images-1.medium.com/max/2000/1*DeOibHNKQh5Is9F756egeQ.png)*ロールアウトをデモする[Kubernetes のドキュメント](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/) からの最初の図*

新しいwebsiteinstance/pod を起動し、準備ができたら古いものと入れ替えます。

    kubectl get pods -ngethue
    NAME                         READY   STATUS    RESTARTS   AGE
    docs-55bf874485-vjnlf        1/1     Running   1          13h
    website-75c7446d4c-z5p6g     0/1     Running   0          6s
    website-bb6fc6b6-nkzqh       1/1     Running   0          18m
    website-jp-964f9cc57-h97gz   1/1     Running   0          11h

ここでは latest タグが使用されていますが、毎日レポジトリのミラーが同期されると新しいイメージが構築されることにご注意ください。静的ウェブサイトのイメージのビルドは非常にシンプルで、失敗したり誤ったイメージを送信する可能性は非常に低いです。適切なタグ付けを行うことで全ての状態がバージョン管理され、失敗したアップグレードは自動的に以前の有効な状態にロールバックされます。

現在の要件は「100%自動化された、できる限りシンプルなものを毎日の頻度で」です。しかし、もっと「リアルタイム」にロールアウトしたいとしたらどうでしょう？（例えば各コミットやプルリクエスト、あるいは1時間ごと）これは計画中で、後続のブログ記事で詳しく説明します。

</br>
</br>

ご意見や質問がありましたらお気軽にこちら、あるいは <a href="https://github.com/cloudera/hue/discussions">Discussions</a> までコメントして下さい。<a href="https://docs.gethue.com/quickstart/">quick start</a> で SQL をクエリして下さい!

ご意見やアドバイスがありましたらお気軽にコメントお願いします！

Romain from the Hue Team
