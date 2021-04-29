---
title: SQL クエリと結果を Slack で直接コラボレートしましょう！
author: Hue Team
type: post
date: 2021-04-09T00:00:00+00:00
url: /blog/2021-04-09-collaborate-on-your-sql-queries-and-results-directly-within-slack
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

<p align="center"> Hue SQL EditorのSlackインテグレーションの紹介 </p>

今年で11周年を迎えるHueプロジェクトは、以下の3つの原則に基づいています。

<h3 align="center"> Query. Explore. Share. </h3>

「共有」の原則は、より良いコラボレーションのために [パブリックリンクとGist共有](https://gethue.com/blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/) の導入によって、最後の改良が行われました。 その流れを受けて、次の改善を行う時が来ました ;)

現在最も優れたコミュニケーションプラットフォームの1つである **Slack**を使ってコラボレーションを向上させる以上に素晴らしいことはないでしょう。

**SlackがあればSlackアプリがあります!** そして、私たちの愛するHueもそれを手に入れました!

現在は **ベータ版**ですが、 このアプリの統合により、クエリのリンクやgistを目的のSlackチャンネルで共有する機能が拡張され、他のユーザーにリッチなプレビューを表示させることができるようになります。 結果の有効期限が切れていなければ、結果のファイルも渡してくれます。

![Share to Slack Architecture](https://cdn.gethue.com/uploads/2021/04/share_to_slack_architecture.png)

ボットの主なロジックはHueサーバー上にあり、HueアプリがSlackからエンドポイントに投稿したイベントをリッスンし、それに応じてデータを処理し、Slack APIのメソッドを使用して目的のレスポンスを送信します。

SQLアシスタントアプリをセットアップするには、 [Hueのドキュメント](https://docs.gethue.com/administrator/configuration/server/#manual-slack-app-installation) に記載されている以下の手順に従ってください。

エディタを開き、クエリを実行してリンクをコピーします。

![Run Query in Editor](https://cdn.gethue.com/uploads/2021/04/run_query_in_hue.png)

Slackチャンネルに貼り付けて、繰り広げられる魔法をご覧ください!

![Query Link Preview](https://cdn.gethue.com/uploads/2021/04/query_link_preview.png)

### どうして結果がこのように表示されるのでしょうか?

Slackは、現在マークダウンのテーブルをサポートしていません。インラインプレビューの改善は、Hueが [クエリタスク](https://docs.gethue.com/administrator/administration/reference/#task-server)による結果のキャッシュをサポートした時に実現されるでしょう。

多くの修正案 (結果画像のアップロード、見栄えの悪い列の切り捨て、ピボットテーブル、[結果ファイルのアップロード](https://github.com/slackapi/python-slack-sdk/issues/991) など) を検討し、そのトレードオフを確認した結果、サンプルの行数を少なくしました。しかし結果テーブルをピボット化することで全ての列を維持し、行の損失を補うために、Hueアプリはメッセージスレッドで結果ファイルを提供します。

![Message Thread with Result File](https://cdn.gethue.com/uploads/2021/04/message_thread_with_result_file.png)

ユーザーはSQLのgistも共有できます!

![Gist Link](https://cdn.gethue.com/uploads/2021/04/gist_link.png)

![Gist Link Preview](https://cdn.gethue.com/uploads/2021/04/gist_link_preview.png)

### 読み取りアクセス

セキュリティを考慮して、Hueユーザーであり、クエリとその結果にアクセスするための読み取り権限を持つSlackユーザーは、リンクを共有した後にこのリッチプレビューと結果ファイルを取得できます。 このマッピングは、現在のところ、メールのプレフィックスとそのホストにHueのユーザー名をチェックすることで行われています。

例えば、ユーザー名「alice」のHueアカウントを持つ人「Alice」は、同じドメインの同じメールアドレスである場合に限り、Slackアカウントからの読み取りアクセスが可能になります。 例: **alice@gethue.com slack ユーザー** は、 **「hue.gethue.com」** のHueユーザー **「alice」** のみアクセスできます。

### 今後の予定は何でしょうか?

フォローアップでは、ユーザがリンクを送信するチャンネルを選択できるHue側からSlackへの共有を促進します。

また、特定のデータテーブルの見つけ方やクエリの方法について質問しているユーザーに返信したり、特定のSlackチャンネルでスケジュールされた問い合わせの結果を送信したりするなど、今後もさまざまな機能が追加される予定です。

### 試してみてください！

このベータ版機能を手に入れるには、以下の方法があります。

[デモのライブエディタ](https://demo.gethue.com/)でいくつかのクエリを実行する。

[デモ用 Slackワークスペース](https://join.slack.com/t/hue-bot-dev/shared_invite/zt-opqwvv68-eQFeios8FzFbmqQJ5wBNzg) に参加してアプリの動作を確認する、あるいは以下の認証情報を使用する。

    Slack アカウントのメールアドレス: demo@gethue.com
    Slack アカウントのパスワード: gethue

それまでは、いくつかのクエリを実行し、リンクをコピーして、すべてを共有してください。

</br> </br>

ご意見やご質問はありますか? ここや<a href="https://discourse.gethue.com/">フォーラム</a> で気軽にコメントし、<a href="https://docs.gethue.com/quickstart/">SQLクエリ</a> のクイックスタートをしてください！


宜しくお願い致します！

~ Harsh from the Hue Team
