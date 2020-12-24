---
title: Hue 3.8にアプリケーションを更新するための開発者ガイド
author: Hue Team
type: post
date: 2015-04-10T00:31:22+00:00
url: /developer-guide-on-upgrading-apps-for-django-1-6-2/
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
sf_custom_excerpt:
  - |
    近日公開される Hue 3.8 の内部では、パフォーマンス、堅牢性、およびセキュリティを向上させるためにいくつかのメジャーな更新を行っています。大きな変更はDjangoの1.4.5から1.6.10アップグレードに起因しており、大幅なパフォーマンスの向上、バグの修正、廃止された機能の削除がなされています。
    
    この記事では、HueのSDKに対してビルドしているHueの開発者が、アプリケーションをHue 3.8で動作するように更新する方法について説明します。
categories:
  - Hue 3.8
  - Programming

---
近日公開される Hue 3.8 の内部では、パフォーマンス、堅牢性、およびセキュリティを向上させるためにいくつかのメジャーな更新を行っています。大きな変更は[Django][1]の1.4.5から1.6.10アップグレードに起因しており、大幅なパフォーマンスの向上、バグの修正、廃止された機能の削除がなされています。

この記事では、HueのSDKに対してビルドしているHueの開発者が、アプリケーションをHue 3.8で動作するように更新する方法について説明します。

[<img class="aligncenter  wp-image-2346" src="https://cdn.gethue.com/uploads/2015/03/django-logo-positive-1024x357.png" alt="django-logo-positive" width="261" height="91" data-wp-pid="2346" />][2]

# Pythonのバージョン

現在Pythonの最低要件のバージョンは2.6.5になり、2.6.0は[要件を満たしません][3] 。

# Djangoのアップグレード

HueはDjango 1.4.5からDjango1.6.10にアップグレードされています。Django <a>1.5</a>と[1.6][4]のリリースノートにアップグレード方法についての詳細がありますが、これらはHueのアップグレード中に私たちが遭遇した主な問題です。

### Json

私たちはJsonのレコードをシンプルに応答するために、Django 1.7の<a>JsonResponse</a>をバックポートしました。以下のように記述していたものが：

<pre><code class="python">def view(request):
    value = { “x”: “y” }
    HttpResponse(json.dumps(value))
</pre>

今はこのように記述することができます：

<pre><code class="python">def view(request):
    value = { “x”: “y” }
    return JsonResponse(value)
</pre>

もうひとつ注意すべきなのは、辞書でないものがシリアライズされている場合、Djangoはデフォルトでエラーを発生させるということです。これは[古いブラウザへの攻撃][5] に対する防御です。これは、このエラーを無効にする方法です：

<pre><code class="python">def view(request):
    value = [“x”, “y”]
    return JsonResponse(value, safe=False)
</pre>

私たちは、開発者はオブジェクトを返すように移行することをお勧めします。Hueも3.8.0に完全に移行されている必要があります。

### Url と Reverse

Djangoの`django.core.urlresolvers.reverse`（およびmakoスクリプトの `url`関数）は自動的に引数をエスケープします。従って、これらの関数の使用は、以下から：

<pre><code class="python">&lt;a href="${ url('useradmin:useradmin.views.edit_user', username=urllib.quote(user.username)) }"&gt;...&lt;/a&gt;
</pre>

下記のように更新します：

<pre><code class="python">&lt;a href="${ url('useradmin:useradmin.views.edit_user', username=user.username) }"&gt;...&lt;/a&gt;
</pre>

### StreamingHttpResponse

ビューからジェネレータを返すために、今は`StreamingHttpResponse` を使用する必要があります。テストするときは、以下のような記述から：

<pre><code class="python">csv_response = self.c.post(reverse('search:download'), {
         'csv': True,
         'collection': json.dumps(self._get_collection_param(self.collection)),
         'query': json.dumps(QUERY)
 })
csv_response_content = csv_response.content
</pre>

下記のように変更します：

<pre><code class="python">csv_response = self.c.post(reverse('search:download'), {
        'csv': True,
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
 })
csv_response_content = ''.join(csv_response.streaming_content)
</pre>

&nbsp;

# 静的ファイル

[NGINXの記事][6] で説明したように、Hueは現在、NGINXのような独立したウェブサーバで静的ファイルを提供することができます。これは、Hueのフロントエンドがページをレンダリングするために実行する必要がある要求の数を減らすことができます。

<table>
  <tr>
    <td>
      <a href="https://cdn.gethue.com/uploads/2015/03/without-nginx.png"><img class="aligncenter wp-image-2337" src="https://cdn.gethue.com/uploads/2015/03/without-nginx.png" alt="without-nginx" width="515" height="318" data-wp-pid="2337" /></a>
    </td>
    
    <td>
      <a href="https://cdn.gethue.com/uploads/2015/03/with-nginx.png"><img class="aligncenter wp-image-2338" src="https://cdn.gethue.com/uploads/2015/03/with-nginx.png" alt="with-nginx" width="513" height="319" data-wp-pid="2338" /></a>
    </td>
  </tr>
</table>

この変更は、静的なファイルを提供する古い方法を使用しているアプリケーションを動かなくします。また、Hue 3.8.0 とそれ以前のバージョンのHueからの静的ファイルにあてた、ユーザーがバックポートしているパッチとの競合も発生します。

移行をするには以下を行います：

  * <code>/apps/$name/static</code> からの静的なファイルを<code>/apps/$name/src/$name/static</code>に移動する
  * 以下からのファイルを： <pre><code class="python">&lt;link rel=”stylesheet” href=”/metastore/static/css/metastore.css”&gt;</pre>
    
    下記に変更するために、<code>.mako</ code>を更新する：
    
    <pre><code class="python">&lt;link rel=”stylesheet” href=”${ static(‘metastore/css/metastore.css’) }”&gt;</pre>

  * apps/$name/src/help/settings.py の&#8221;ICON&#8221;を、以下から: <pre><code class="python">ICON = “/help/static/art/icon_help_24.png”
</pre>
    
    下記のように更新する：
    
    <pre><code class="python">ICON = “help/art/icon_help_24.png”
</pre>

  * PythonのすべてのPythonテンプレートを、以下から： <pre><code class="python">def view(request):
    data = {‘image’: “/help/static/art/icon_help_24.png”}
    return render(“template.mako”, request, data)
</pre>
    
    下記のように更新する：
    
    <pre><code class="python">from django.contrib.staticfiles.storage import staticfiles_storage

…

def view(request):
    data = {‘image’: staticfiles_storage.url(“/help/static/art/icon_help_24.png”) }
    return render(“template.mako”, request, data)
</pre>

最後に、Hueを`debug=False`で実行するには、全てのファイルをbuild/staticディレクトリに収集するため、最初に`make apps`あるいは`./build/env/bin/hue collectstatic`のいずれを実行する必要があります。これは`debug=True`では必要がなく、Hueは`/apps/$name/src/$name/static`ディレクトリから静的ファイルを直接提供します。

&nbsp;

# Next!

今月、[Django 1.8が][7]リリースされました！これは2番目のLTSリリースであり、1.4のサポートは6ヶ月で終了します。1.8の主な依存関係はPython 2.7が必要になることで、これはまだ現在使用されている古いLTS OSのデフォルトのPythonのバージョンではないということです。

&nbsp;

いつものように、コメントとフィードバックは [hue-user][8] メーリングリストや[@gethue][9]までお気軽に！

 [1]: https://www.djangoproject.com/
 [2]: https://cdn.gethue.com/uploads/2015/03/django-logo-positive.png
 [3]: http://stackoverflow.com/questions/19365230/django-init-keywords-must-be-strings-error-while-running-runserver
 [4]: https://docs.djangoproject.com/en/1.7/releases/1.6/
 [5]: https://docs.djangoproject.com/en/1.7/ref/request-response/#serializing-non-dictionary-objects
 [6]: https://gethue.com/developer-guide-on-upgrading-apps-for-django-1-6/#
 [7]: https://docs.djangoproject.com/en/1.8/releases/1.8/
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user
 [9]: https://twitter.com/gethue