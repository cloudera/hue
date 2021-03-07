---
title: セキュアクラスターで新規ユーザーに Ranger の権限を与える方法
author: Weixia Xu
type: post
date: 2020-05-19T00:00:00+00:00
url: /blog/how-to-grant-ranger-permissions-for-a-new-user/
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
Hue の管理者の皆さん、こんにちは。

[Apache Ranger™](https://ranger.apache.org/) は Hadoop プラットフォームにわたって包括的なデータセキュリティを有効にし、監視、管理するためのフレームワークです。

Hue は [Hue4.6](https://gethue.com/hue-4-6-and-its-improvements-are-out/) 以降で Ranger と統合されており、Ranger がインストールされたセキュアなクラスターで、ユーザーは以下の権限の警告を避けるための適切な権限を持っている必要があります。

![missing-ranger-permission.png](https://cdn.gethue.com/uploads/2020/05/missing-ranger-permission.png)

CM の UI を通じて新しいユーザーに権限を与える手順の詳細を紹介します。

## 手順
1. CM で管理されたクラスターで Ranger サービスに移動し、Instance のタブで 'Ranger Usersync' ホストをメモしておき、'Ranger Admin Web UI' を開きます。

![ranger-usersync-host-and-admin-webui.png](https://cdn.gethue.com/uploads/2020/05/ranger-usersync-host-and-admin-webui.png)

2. ターミナルを開き、手順1でメモした ranger usersync ホストに ssh します。

    ssh root@weixia-1.domain.site
    useradd weixia
    passwd weixia

3. Ranger admin webui ページ https://weixia-1.domain.site:6182/index.html#!/policymanager/resource で、"Hadoop SQL" の横の "Edit" ボタンをクリックします。

![edit-ranger-policymanager-hadoop-sql.png](https://cdn.gethue.com/uploads/2020/05/edit-ranger-policymanager-hadoop-sql.png)

a. 全てのデータベースに新しいユーザー権限を与えたい場合は、既存のポリシー "all-database, table, column" にユーザーを追加します:
![grant-user-permission-to-all.png](https://cdn.gethue.com/uploads/2020/05/grant-user-permission-to-all.png)

b. 特定のデータベース、ここでは 'testdb' にのみ新しいユーザーを与えたい場合は、次のように必要な権限を選択して新しいポリシーを作成します'。
![create-new-policy-for-testdb-access-only.png](https://cdn.gethue.com/uploads/2020/05/create-new-policy-for-testdb-access-only.png)

4. 変更を保存します。

Hue の WebUI に移動します。これで新しいユーザーは、ポリシーで与えた任意のエンティティに対して任意のクエリを実行できるようになっています。
![new-user-can-run-query-on-tables.png](https://cdn.gethue.com/uploads/2020/05/new-user-can-run-query-on-tables.png)

同様に、グループの権限に対しても同じように行うことができます。

フィードバックや質問はありますか？ご質問は [Forum](https://discourse.gethue.com/) や
[@gethue](https://twitter.com/gethue) でお気軽に。[quick start](https://docs.gethue.com/quickstart/) で SQL クエリを行ってみて下さい！

Weixia Xu from the Hue Team
