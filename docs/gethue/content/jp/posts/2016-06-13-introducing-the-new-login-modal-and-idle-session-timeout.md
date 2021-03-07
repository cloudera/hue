---
title: 新しいログインモーダルとアイドルセッションタイムアウトの紹介
author: Hue Team
type: post
date: 2016-06-13T23:59:49+00:00
url: /introducing-the-new-login-modal-and-idle-session-timeout/
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
sf_custom_excerpt:
  - Hue 3.10の最新リリースでは、Hueの管理者にセキュリティを強制する追加のセキュリティ機能と、Hueのアイドルセッションタイムアウトの管理を追加しました。新しいログインモデルの導入により、ユーザーのセッションがタイムアウトした際にHueの再認証のエクスペリエンスを改善しました。
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
categories:
  - Hue 3.10
  - Security

---
Hue 3.10の最新リリースでは、Hueの管理者にセキュリティを強制する追加のセキュリティ機能と、Hueのアイドルセッションタイムアウトの管理を追加しました。新しいログインモーダルの導入により、ユーザーのセッションがタイムアウトした際にHueの再認証のエクスペリエンスを改善しました。

Hueは現在、hue.iniファイルで設定できる新しいプロパティ`idle_session_timeout` を提供しています:

<pre><code class="bash">[desktop]
[[auth]]
idle_session_timeout=600
</pre>

`idle_session_timeout`が設定されている場合、ユーザーは非アクティブになったN秒（例えば 600秒）後に自動的にログアウトされ再度ログインするように求められます：

[<img class="aligncenter size-large wp-image-4122" src="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-06-15.14.52-1024x553.jpg" alt="Screenshot 2016-06-06 15.14.52" width="1024" height="553" data-wp-pid="4122" />][1]

ユーザーのHueセッションがタイムアウトしてもユーザーがまだアクティブなHiveやImpalaセッションを開いている場合は、ログインモーダルは現在のビュー上に表示され、ユーザーが自分の現在のクエリセッションにログインして再開することができます：

[<img class="aligncenter size-full wp-image-4120" src="https://cdn.gethue.com/uploads/2016/02/loginmodal.gif" alt="loginmodal" width="935" height="501" data-wp-pid="4120" />][2]

`idle_session_timeout`を負の数に設定した場合、アイドル状態のセッションはタイムアウトされないことを意味します。デフォルトでは`idle_session_timeout` は-1に設定されています。

いつものように、コメントとフィードバックは [hue-user][3] メーリングリストや[@gethue][4]までお気軽に！

 [1]: https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-06-15.14.52.jpg
 [2]: https://cdn.gethue.com/uploads/2016/02/loginmodal.gif
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
