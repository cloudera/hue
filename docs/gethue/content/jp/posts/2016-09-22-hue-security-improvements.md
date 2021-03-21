---
title: HUEのセキュリティの改善
author: Hue Team
type: post
date: 2016-09-22T13:43:04+00:00
url: /hue-security-improvements/
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
    HUEの管理者の皆さん、こんにちは。

    最近、HUEに多くのセキュリティオプションが追加されました。 これらは可能な限りデフォルトでオンになっています。

    このドキュメントではいくつかの修正点について説明し、Hueの管理者が、HUEをインストールを実行して管理できるようにします。
sf_author_info:
  - 1
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
  - Hue 3.12
  - Security

---
HUEの管理者の皆さん、こんにちは。

最近、HUEに多くのセキュリティオプションが追加されました。 これらは可能な限りデフォルトでオンになっています。

このドキュメントではいくつかの修正点について説明し、Hueの管理者が、HUEをインストールを実行して管理できるようにします。ブラウザがHUEのWebサーバーからページを要求するたびに、HUEはHTTP応答ヘッダーと共にコンテンツを返します。これらのヘッダーの中には、content-encoding、cache-control、ステータスエラーコードなどのコンテンツメタデータが含まれています。これらに加え、HUEのコンテンツを処理するときにブラウザにどのように動作するかを伝えるHTTPセキュリティヘッダーもあります。 例えば、strict-transport-securityを使用すると、ブラウザがHTTPS経由でのみ通信するように強制できます。

### Content-Security-Policy: header

新しいContent-Security-Policy HTTPレスポンスヘッダーは、最新のブラウザーでXSSのリスクを軽減するのに役立ちます。これは、HTTPヘッダーを介してどの動的リソースがロードできるかを宣言することによって実現されます。（詳細について読む：<https://content-security-policy.com/> ）

<pre><code class="bash">[desktop]
secure_content_security_policy="script-src 'self' 'unsafe-inline' 'unsafe-eval' *.google-analytics.com *.doubleclick.net *.mathjax.org data:;img-src 'self' *.google-analytics.com *.doubleclick.net http://*.tile.osm.org *.tile.osm.org *.gstatic.com data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'self' data:;object-src 'none'"
#HUE 3.11以降でデフォルトで有効
</pre>

content-security-policy ヘッダーを無効にする場合は、次の値を使用します。 （自己責任において使用してください）

<pre><code class="bash">[desktop]
secure_content_security_policy=""
#(自己責任で使用してください)
</pre>

動的リソースがHTTPヘッダーを介してロードすることを許可する宣言を無効にする場合、次の値を使用できます。 （自己責任で使用してください）

<pre><code class="bash">[desktop]
secure_content_security_policy="default-src 'self' 'unsafe-eval' 'unsafe-inline' data: *;"
#(自己責任で使用してください)
</pre>

[<img class="aligncenter wp-image-4500 size-large" src="https://cdn.gethue.com/uploads/2016/09/block-content-1024x400.png" alt="block-content" width="1024" height="400" data-wp-pid="4500" />

][1] ブロックされた画像コンテンツの例

### Server: header

HUEは、Webサーバー情報の公開を最小限に抑え、Webサーバーのバージョンやその他の詳細に関する洞察を最小限に抑えます。 エンドユーザーからの変更は必要ありません。次のHTTP応答ヘッダーを生成します:

<pre><code class="bash">Server:apache
</pre>

### これらのHTTP応答ヘッダーは上記のセキュリティ修正の後に生成される

<pre><code class="bash">x-content-type-options:nosniff
X-Frame-Options:SAMEORIGIN
x-xss-protection:1; mode=block
Content-Security-Policy:script-src 'self' 'unsafe-inline' 'unsafe-eval' *.google-analytics.com *.doubleclick.net *.mathjax.org data:;img-src 'self' *.google-analytics.com *.doubleclick.net http://*.tile.osm.org *.tile.osm.org data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'self' data:;object-src 'none'
Strict-Transport-Security:max-age=31536000; includeSubDomains
Server:apache
</pre>

### X-Content-Type-Options: header

一部のブラウザは、取り込んだアセットのコンテンツタイプを推測し、Content-Typeヘッダーをオーバーライドします。 ブラウザがコンテンツタイプを推測することを防ぎ、常にContent-Typeヘッダーに指定されているタイプを使用するようにするには、X-Content-Type-Options：nosniffヘッダーを渡すことができます。

<pre><code class="bash">[desktop]
secure_content_type_nosniff=true
#HUE 3.11以降でデフォルトで有効
</pre>

### X-XSS-Protection: header

一部のブラウザでは、XSS攻撃のように見えるコンテンツをブロックする機能があります。 これらは、ページのGETまたはPOSTパラメータでJavascriptコンテンツを検索することによって機能します。ブラウザでXSSフィルタを有効にして、疑わしいXSS攻撃を常にブロックするようにするには、X-XSS-Protection: 1、 mode = blockヘッダを渡します。

<pre><code class="bash">[desktop]
secure_browser_xss_filter=true
#In HUE 3.11 and higher it is enabled by default.
</pre>

[

][2] [<img class="aligncenter wp-image-4499 size-full" src="https://cdn.gethue.com/uploads/2016/09/security-response-header.png" alt="security-response-header" width="640" height="199" data-wp-pid="4499" />][2]

<p style="text-align: center;">
  上記のオプションで受け取った新しいヘッダの例
</p>

### Strict-Transport-Security: header

HUEサイトでHTTPとHTTPSの両方の接続が提供されている場合、ほとんどのユーザーはデフォルトでセキュリティで保護されていない接続になります。最高のセキュリティを確保するには、すべてのHTTP接続をHTTPSにリダイレクトする必要があります。 HTTPSを介してのみアクセスする必要があるサイトでは、新しいブラウザーに「Strict-Transport-Security」ヘッダーを設定することにより、（一定期間）安全でない接続を介してドメイン名への接続を拒否するように指示できます。これにより、MITM（Man-in-the-Middle：中間者）攻撃を軽減します。 _HUEでは、httpsが有効な場合、デフォルトでhttpsに切り替えることができるようになりました。_

### セキュアなビットセットでcsrftokenとセッションクッキーを提供

可能であれば、HUEは安全なビットセットでcsrftokenとセッションクッキーを配信するようになりました。安全なフラグが使用されると、CookieはHTTPS経由でのみ送信されます。

[<img class="aligncenter wp-image-4501 size-full" src="https://cdn.gethue.com/uploads/2016/09/cookie-secured.png" alt="cookie-secured" width="1065" height="66" data-wp-pid="4501" />][3]

csrftokenはセキュアなビットを持つセッションクッキー

### ワイルドカード証明書をサポート

Hueは[ワイルドカード証明書][4]をサポートするようになりました。これは、ワイルドカード証明書と証明書の検証機能に欠けている機能をSANに追加します（subjectAlternativeName）。

_* .example.com_のワイルドカード証明書は、これらのドメインをすべて保護します:

  * payment.example.com
  * contact.example.com
  * login-secure.example.com
  * www.example.com

サブドメインの証明書を別々に取得する代わりに、すべてのメインドメインとサブドメインに対して1つの証明書を使用してお金を節約することができます。

ワイルドカードはサブドメインの1つのレベルのみをカバーするため（アスタリスクは完全な停止に一致しません）、これらのドメインは証明書に対して有効ではありません。:

  * test.login.example.com

### 任意のホストヘッダーの受け入れの修正

Hueでは任意のホストヘッダ受け入れを修正しました。これで、Hueサーバーが提供できるホスト/ドメイン名を設定できます。

allowed_hosts=&#8221;host.domain,host2.domain,host3.domain&#8221;

<pre><code class="bash">[desktop]
allowed_hosts="*.domain"
# your own fqdn example: allowed_hosts="*.hadoop.cloudera.com"
# or specific example: allowed_hosts="hue1.hadoop.cloudera.com,hue2.hadoop.cloudera.com"
</pre>

### セッションストアを埋めることによるサービス拒否(DoS)の可能性を修正

Django CVE-2015-5143 <a class="external-link" title="Follow link" href="http://www.cvedetails.com/cve/CVE-2015-5143/" rel="nofollow">http://www.cvedetails.com/cve/CVE-2015-5143/</a>

### Djangoのutils.html.strip_tags関数がサービス拒否(DoS)になりうる問題を修正

Django CVE-2015-2316 <a class="external-link" title="Follow link" href="http://www.cvedetails.com/cve/CVE-2015-2316/" rel="nofollow">http://www.cvedetails.com/cve/CVE-2015-2316/</a>

###

 [1]: https://cdn.gethue.com/uploads/2016/09/block-content.png
 [2]: https://cdn.gethue.com/uploads/2016/09/security-response-header.png
 [3]: https://cdn.gethue.com/uploads/2016/09/cookie-secured.png
 [4]: https://en.wikipedia.org/wiki/Wildcard_certificate
