---
title: LDAP認証とSSLで構成されたHiveとImpalaをHueで使用する方法
author: Hue Team
type: post
date: 2015-03-05T16:05:55+00:00
url: /how-to-use-hue-with-hive-and-impala-configured-with-ldap-authentication-and-ssl-2/
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
  - |
    以前、私たちはImpalaやHiveエディタでSSL暗号化を使用する方法の詳細について紹介しました。今回の記事は、認証なしまたはKerberosを使用する代わりに、LDAP認証を使用する方法についてのステップバイステップガイドです。

    N注：これにはHue 3.7またはCDH5.2が必要です
sf_social_sharing:
  - 1
sf_sidebar_config:
  - right-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
categories:
  - Enterprise
  - Hive
  - Impala

---
以前、私たちはImpalaやHiveエディタで[SSL暗号化][1]を使用する方法の詳細について紹介しました。今回の記事は、認証なしまたはKerberosを使用する代わりに、LDAP認証を使用する方法についてのステップバイステップガイドです。

N注：これには[Hue 3.7][2]またはCDH5.2が必要です

1.

HiveServer2はSSLが有効なので、HiveエディタはHiveServer2に接続できませんでした。HiveServer2のログは、受け取った平文でのSSLエラーを示します（原因を調べるための良いヒントです）

Hueの安全バルブににこれを追加することで解決しました：

<pre><code class="bash">[beeswax]
  [[ssl]]
  ## SSL communication enabled for this server.
  enabled=false
  ## Path to Certificate Authority certificates.
  cacerts=/etc/hue/cacerts.pem
  ## Path to the private key file.
  key=/etc/hue/key.pem
  ## Path to the public certificate file.
  cert=/etc/hue/cert.pem
  ## Choose whether Hue should validate certificates received from the server.
  validate=false
</pre>

(その証明書がワイルドカードを使用しており、これが他のエラーの原因となっているため、validateはfalseでした)

注：SSLを使用しない場合は、次のバグにヒットします： [HUE-2484][3]

2.

変更を行った後にHueの同じ動作が発生しましたが、今度のHiveServer2のログには、err=49による認証失敗を示しました。

そこで、Hueの安全バルブに以下のように追加しました：

<pre><code class="bash">[desktop]
  ldap_username=
  ldap_password=
</pre>

3.

Hueはまだ同じ挙動を示していました。HiveServer2ログは以下のように示していました：

<pre><code class="bash">&lt;HUE_LDAP_USERNAME&gt; is not allowed to impersonate bob
</pre>

core-site.xmlのためにHDFS ->Service-Wide -> Advanced -> 安全バルブに以下を追加することで解決しました。

<pre><code class="xml">&lt;property&gt;
  &lt;name&gt;hadoop.proxyuser.&lt;HUE_LDAP_USERNAME&gt;.hosts&lt;/name&gt;
  &lt;value&gt;*&lt;/value&gt;
&lt;/property&gt;
&lt;property&gt;
  &lt;name&gt;hadoop.proxyuser.&lt;HUE_LDAP_USERNAME&gt;.groups&lt;/name&gt;
  &lt;value&gt;*&lt;/value&gt;
&lt;/property&gt;
</pre>

4.

この後、デフォルトのデータベースが表示されていましたが、show tables やその他の何も行うことが出来ませんでした。beelineは同じ挙動でした。

私たちは、Hive アクションを試みているユーザー who にグループへのgrantを行い、その問題は収まりました。すべてのクエリは動作し、HueはHive/Impalaをクエリして結果を返しました！

[<img class="aligncenter size-large wp-image-1787" src="https://cdn.gethue.com/uploads/2014/10/hue-impala-charts-1024x573.png" alt="hue-impala-charts" width="1024" height="573" data-wp-pid="1787" />][4]

&nbsp;

いつものように、コメントとフィードバックは hue-user メーリングリストや@gethueまでお気軽に！

 [1]: https://gethue.com/hadoop-tutorial-ssl-encryption-between-hue-and-hive/
 [2]: https://gethue.com/hue-3-7-with-sentry-app-and-new-search-widgets-are-out/
 [3]: https://issues.cloudera.org/browse/HUE-2484
 [4]: https://cdn.gethue.com/uploads/2014/10/hue-impala-charts.png
