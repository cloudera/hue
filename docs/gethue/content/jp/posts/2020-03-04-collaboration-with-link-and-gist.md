---
title: リンクやgistを介するSQLクエリの共有によるより優れた協力的なデータウェアハウス体験
author: Romain
type: post
date: 2020-03-04T02:36:35+00:00
url: /blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/
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
  - Version 4
#  - Version 4.7


---
データクランチャーの皆さんこんにちは。

[過去10年間](https://jp.gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/)、Hue の SQL エディターは [SQL データウェアハウスの体験](https://jp.gethue.com/blog/2020-02-10-sql-query-experience-of-your-cloud-data-warehouse/) をターゲットにしてきました。最近では[列キー](https://gethue.com/blog//2019-11-13-sql-column-assist-icons/)を表示することにより、SQLクエリの入力のサポートが向上しました。最新の改善点はコラボレーションの改善です。

[ドキュメント共有](https://docs.gethue.com/user/concept/#sharing)機能と[クエリパラメーター](https://docs.gethue.com/user/querying/#variables)を通して、Hue はチームが独自の知識の「銀行(Bank)」を構築することができます。これを補完するために、公開リンクとGist共有という、迅速かつ簡単な機能も利用できるようになりました。


## 公開リンク

目標: パラメーター化した保存済みのレポートを素早く共有し、お客様はリンクを分析できるようにすること

公開リンクは Google ドキュメントと同等です。必要なのは受信者が Hue のログインを持っていることだけです。その後、クエリを実行して結果を確認できます。また、フォークして適用することで、ご自身でクエリを再利用できます。

* グループや個々のユーザーのリストを選択する必要がない
* 読み取り、書き込み権限
* リンクされたドキュメントはホームに表示されない
* グローバルにオフにすることが可能
* 従来のユーザー/グループ共有と組み合わせることが可能

以下に例を示します:

保存されているクエリは、エディターまたは左側のドキュメントアシストを介して直接共有できます。すでに共有されているドキュメントは小さな人のアイコンが表示されていることに注意してください:

![Editor share menu](https://cdn.gethue.com/uploads/2020/03/editor_share_menu.png)

![Assist share menu](https://cdn.gethue.com/uploads/2020/03/editor_assist_share_menu.png)

ドキュメントのプレビューもよりスムーズになり、所有者、権限、最終更新時刻が表示されます:

![Editor share menu popup](https://cdn.gethue.com/uploads/2020/03/assist_document_popup.png)

これは上部に公開リンクのオプションがある、共有のポップアップです。

![Editor share menu popup](https://cdn.gethue.com/uploads/2020/03/editor_sharing_popup.png)


## SQL のスニペット - Gist

目標: SQL エディターへの直接リンクを用いて SQL のスニペットを素早く共有すること

クエリの結果を通して質問に回答していますか? Slack のチャンネルにいくつかの奇妙なデータを表示していますか? Gist はこれらを行うための素早い迅速な方法です。

* SQL のスニペットを使用: 1つ以上のステートメント
* リンクは、自動的にエディターと SQL の内容を示す
* クエリは、よりわかりやすい[プレゼンテーションモード](https://docs.gethue.com/user/querying/#presentation)で表示される
* Slack の展開は、小さなプレビューを表示する(グローバルでオフにできる)
* Gist はホームの Gist ディレクトリに保存される

以下に例を示します:

ステートメントの一部を選択して Slack のチャンネルに素早く共有します:

![Editor share gist menu](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_menu.png)

SQL の断片へのリンクが自動的に生成されます:

![Editor share gist popup](https://cdn.gethue.com/uploads/2020/03/editor_sharing_gist_popup.png)

ユーザーは、Slack のチャンネルにリンクを貼り付けるだけで小さなビューを得ることができます:

![Open gist in Slack](https://cdn.gethue.com/uploads/2020/03/editor_gist_slack.png)

リンクをクリックすると SQL のセレクションが開きます:

![Open gist](https://cdn.gethue.com/uploads/2020/03/editor_gist_open_presentation_mode.png)



フィードバックや質問があれば、このブログや<a href="https://discourse.gethue.com/">フォーラム</a>にkメントしてください。また、<a href="https://docs.gethue.com/quickstart/">quick start</a> でSQLのクエリを行なってください!


Romain, from the Hue Team
