---
title: Hue 4.7 に含まれる予定の管理者用の改善!
author: Hue Team
type: post
date: 2020-04-07T02:36:35+00:00
url: /blog/2020-04-07-some-4-7-admin-improvements/
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

SQL クランチャーの皆さん、

今後の Hue 4.7 のリリースでは、管理者をより良くするために一連の改善がもたらされます。ここではその一部を紹介します。


![Config filtering](https://cdn.gethue.com/uploads/2020/04/4.7_admin_config_filter.png)

全てのサーバーのプロパティが設定ページにも一覧されます。これは多くのパラメーターとセクションがあります。フィルターを用いてこれらをスポットライト検索することができます。


![Admin user statuses](https://cdn.gethue.com/uploads/2020/04/4.7_admin_users_status.png)

ユーザーの削除フローは、削除ではなく無効化されるようになりました。(保存されたドキュメントやクエリが失われるのを防ぐためです)。ユーザー管理画面には ACTIVE と SUPERUSER のステータスが表示されるようになりました。


![Active user](https://cdn.gethue.com/uploads/2020/04/cm_active_users.png)

API インスタンスごとのアクティブユーザー数のメトリクスが改訂されました。グローバルの一意のカウンタではなく、インスタンスごとに差別化が可能になりました。詳細は[この投稿](https://jp.gethue.com/hue-active-users-metric-improvements/) をご覧ください。


![sharing modal](https://cdn.gethue.com/uploads/2020/04/4.7_sharing_popup.png)

ドキュメント共有は、ユーザーの適切なフルネームとアイコンを使用したより親しみやすいものに変更しました。これは[QueryのGistとパブリックリンクの共有](https://jp.gethue.com/blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/) に加えて素晴らしいコラボレーションの改善です。



フィードバックや質問はありますか？何かあれば [Forum](https://discourse.gethue.com/) や [@gethue](https://twitter.com/gethue) までお気軽にコメントください。[quick start](https://docs.gethue.com/quickstart/) で SQL のクエリを楽しんでください！


Romain fromthe Hue Team
