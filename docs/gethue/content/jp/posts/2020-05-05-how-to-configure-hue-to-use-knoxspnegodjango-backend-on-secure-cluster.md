---
title: セキュアなクラスター上で Apache Knox SSO で認証するように Hue を設定する方法
author: Weixia Xu
type: post
date: 2020-05-05T00:00:00+00:00
url: /blog/how-to-configure-hue-to-use-knoxspnegodjango-backend/
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
Hue の管理者の皆さん、こんにちは

[Apache Knox™ Gateway](https://knox.apache.org/) は、Apache Hadoop デプロイメントの REST-API や UI とやり取りするためのアプリケーションゲートウェイです。

Hue は Hue 4.6 から KnoxSpnegoDjango をサポートしており、CM (Cloudera Manager) UI または hue.ini からHue の設定を更新することで、Hue の KnoxSpnegoDjango 認証を有効にすることができます。

Knox サービスがインストールされたクラスターで次のように hue.ini を更新して Hue をリスタートします。

    [desktop]
    [[auth]]
    backend=desktop.auth.backend.KnoxSpnegoDjangoBackend
    [[knox]]
    knox_principal=knox
    knox_proxyhosts=weixia-1.domain.site,weixia-2.domain.site

あるいは、CMで管理されているクラスターでは、CM の UI を通して KnoxSpnegoDjango バックエンドを設定できます。
![hue-auth-knoxspnego.png](https://cdn.gethue.com/uploads/2020/05/hue-auth-knoxspnego.png)

knox_proxyhosts フィールドに、正確な knox プロキシのホスト名を入力します。Clusters->KNOX に移動して「Instances」タブをクリックしてホスト名を取得できます。

![knox-ha-hosts.png](https://cdn.gethue.com/uploads/2020/05/knox-ha-hosts.png)
Knox HA クラスターでは、“+” アイコンをクリックして、全てのホストを入力します。
![configure-hue-with-knox-ha.png](https://cdn.gethue.com/uploads/2020/05/configure-hue-with-knox-ha.png)

‘Save Changes’ をクリックすると、role missing kerberos keytab という警告が表示されます。“Administration”–>”Security” をクリックすると次のように表示されます。
![role-missing-kerberos-keytab.png](https://cdn.gethue.com/uploads/2020/05/role-missing-kerberos-keytab.png)
![generate-missing-credentials.png](https://cdn.gethue.com/uploads/2020/05/generate-missing-credentials.png)
続いて Clusters->HUE-1 に戻り、 “Actions” ボタンのそばにある “stale configuration: Restart” アイコンをクリックします。
![stale-configuration-restart.png](https://cdn.gethue.com/uploads/2020/05/stale-configuration-restart.png)
ウィザードに従って “Restart staled services” を選択し、“Re-deploy client configuration” を選んで “Restart Now” をクリックし、完了するまで待ちます。

Hue の Web UI ドロップダウンに移動し、“Knox Gateway UI” を選択して Knox UI をロードします。
![knox-gateway-ui.png](https://cdn.gethue.com/uploads/2020/05/knox-gateway-ui.png)
その後 “+cdp-proxy” の “+” アイコンをクリックして展開します。
![knox-gateway-ui-cdp-proxy.png](https://cdn.gethue.com/uploads/2020/05/knox-gateway-ui-cdp-proxy.png)

ここで Hue のアイコンをクリックします。
![knox-proxy-login-hue-icon.png](https://cdn.gethue.com/uploads/2020/05/knox-proxy-login-hue-icon.png)

Hue のページにログインすることができるはずです。

![hue-page.png](https://cdn.gethue.com/uploads/2020/05/hue-page.png)


## トラブルシューティング
1. "The username or password you entered is incorrect.” のエラーに遭遇した場合、

![incorrect-user-or-password.png](https://cdn.gethue.com/uploads/2020/05/incorrect-user-or-password.png)

ユーザー名またはパスワードが正しいかどうか、Knox プロキシーホストで確認してください。

    ssh root@weixia-1.domain.site
    useradd weixia
    passwd weixia

2. 403 エラーに遭遇した場合、

![hue-login-403.png](https://cdn.gethue.com/uploads/2020/05/hue-login-403.png)

Ranger サービスにログインして、ユーザーまたはグループが「Public」で適切な権限を持っていることを確認してください。

![ranger-cm-knox-policies.png](https://cdn.gethue.com/uploads/2020/05/ranger-cm-knox-policies.png)

フィードバックやご質問はありますか？こちら、または<a href="https://discourse.gethue.com/">フォーラム</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> で気軽にコメントして、SQLクエリのクイックスタートをしましょう！

Weixia Xu from the Hue Team
