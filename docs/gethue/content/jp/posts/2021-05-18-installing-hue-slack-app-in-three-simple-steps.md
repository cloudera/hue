---
title: Hue Slackアプリを3つの簡単なステップでインストール
author: Hue Team
type: post
date: 2021-05-18T00:00:00+00:00
url: /blog/2021-05-18-installing-hue-slack-app-in-three-simple-steps
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
---

チーム内の他のSQLユーザーとの共同作業を支援するSQLアシスタントが欲しいと思ったことはありませんか？ それも Slack に？

このHueとSlackの統合は、SlackチャンネルでのSQLクエリをアシストしてくれます。 [使い方も簡単](https://docs.gethue.com/user/concept/#slack)で、Slackのワークスペースの管理者であれば、たった3ステップで簡単にインストールできます。

Slackは最近、Slackアプリ向けに[アプリマニフェスト](https://api.slack.com/reference/manifests)のベータ版をリリースしました。 マニフェストを使用すると、あらかじめ定義された構成でアプリケーションを作成することができます。

アプリマニフェストの最新バージョンは [Hueリポジトリ](https://github.com/cloudera/hue/blob/master/tools/slack/manifest.yml) にチェックインされています。

共有マニフェストでは、 _demo.gethue.com_ の2つを**Hueインスタンスのホスト名**で更新します:
- **unfurl_domains**の下
- **event_subscriptions**の下、**request_url** `https://<hue-instance-hostname>/desktop/slack/events/`で

さて、いよいよ自分のアプリを作成してみましょう。
- https://api.slack.com/apps に移動し、 **Create New App** をクリックします。
- **From an app manifest** オプションとアプリをインストールするワークスペースを選択して**Next**をクリックします。
- **YAML** を選択し、マニフェストコードを貼り付けて (上記の必要な変更を行っていることを確認してください) 、 **Next** をクリックします。
- レビューの概要を読み、問題がなければ、 **Create** をクリックします。
- アプリが作成されたら、ワークスペースにインストールしましょう！

![Slack のインストールフロー](https://cdn.gethue.com/uploads/2021/05/slack-install.gif)

Hueでプラグインを行う最後のステップを完了し、hue.ini設定ファイルを更新しましょう:
- **OAuth & Permissions page**に移動し、 **Bot User OAuth Token** をコピーして、 **slack_bot_user_token** を更新します。(例: xoxb-xxxxxxxxxxxxxxxxxxxxxxxxx)
- 同様に、 **Basic Information** ページに移動して **Verification Token** をコピーし、**slack_verification_token** を更新します。

そして、これを hue.ini ファイルの `[desktop]` セクションに貼り付けます

    [[slack]]
    is_enabled=true
    slack_verification_token=<your-slack-verification-token>
    slack_bot_user_token=<your-slack-bot-user-token>

手続きは以上です！ あなただけのHueアプリの準備ができました！
### 試してみましょう！

[Slack ワークスペース](https://hue-sql-assistant.slack.com/) にログインし、以下の Slack アカウントの資格情報を使用してデモSQL Assistant にアクセスしてください。

      email: demo@gethue.com
      password: gethue

[デモのライブエディタ](https://demo.gethue.com/)でいくつかのクエリを実行し、そのリンクを共有します。 [ユーザーガイド](https://docs.gethue.com/user/concept/#share-to-slack) または [ブログ](https://jp.gethue.com/blog/2021-04-09-collaborate-on-your-sql-queries-and-results-directly-within-slack/) を読んで、今後のアップデートにご期待ください。

</br> </br>

どのような[フィードバック](https://github.com/cloudera/hue/issues) や質問も大歓迎です！ ここや<a href="https://discourse.gethue.com/">フォーラム</a> で気軽にコメントし、<a href="https://docs.gethue.com/quickstart/">SQLクエリ</a> のクイックスタートをしてください！

宜しくお願い致します！

Harsh from the Hue Team
