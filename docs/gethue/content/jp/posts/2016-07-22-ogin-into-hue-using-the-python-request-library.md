---
title: PythonのRequest Libraryを使用してHueにログインする
author: Hue Team
type: post
date: 2016-07-22T00:00:06+00:00
url: /ogin-into-hue-using-the-python-request-library/
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
  - PythonのRequest Libraryを使用してHueにログインする方法をこの小さなスニペットで紹介します。
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
categories:
  - Hue 3.11
  - Programming
  - SDK
  - Security
  - User Admin

---
## **PythonのRequest Libraryを使用してHueにログインする方法をこの小さなスニペットで紹介します。**

Hueは[Django Web Framework][1]に依存しています。 Djangoにはユーザ認証システムがあります。Djangoはリクエストオブジェクトへの認証システムをフックするためにセッションと[ミドルウェア][2]を使用します。Hueは認証するために「ユーザー名(username)」と「パスワード(password)」、「csrftoken」フォーム変数を使用する認証フォームを備えています。

このコードスニペットでは、よく知られているpythonの「[リクエスト][3] 」ライブラリを使用します。最初 GET &#8220;login_url&#8221; により[csrftoken][4] を獲得します。 &#8220;username&#8221;、&#8221;password&#8221;、&#8221;cfrftoken&#8221;および&#8221;next\_url&#8221;が含まれているフォームデータのpythonディクショナリと&#8221;Referer&#8221;を含むヘッダのpythonディクショナリ、およびcookie用の空のpythonディクショナリを作成します。&#8221;login\_url&#8221;へのPOSTリクエストの後、ステータスを取得します。`r.status_code` をチェックします。もし`r.status_code!=200` の場合、ユーザ名またはパスワードに問題があります。

リクエストが成功したらその後のリクエストのためにヘッダとcokkieをキャプチャします。`cookies=session.cookiesとheaders=session.headers`を渡すことにより 、後続のrequest.session呼び出しを行うことができます。

<pre class="brush: python; collapse: false; title: ; wrap-lines: false; notranslate" title="">import requests

def login_djangosite():
 next_url = "/"
 login_url = "http://localhost:8888/accounts/login?next=/"

 session = requests.Session()
 r = session.get(login_url)
 form_data = dict(username="[your hue username]",password="[your hue password]",
                  csrfmiddlewaretoken=session.cookies['csrftoken'],next=next_url)
 r = session.post(login_url, data=form_data, cookies=dict(), headers=dict(Referer=login_url))

 # check if request executed successfully?
 print r.status_code

 cookies = session.cookies
 headers = session.headers

 r=session.get('http://localhost:8888/metastore/databases/default/metadata',
 cookies=session.cookies, headers=session.headers)
 print r.status_code

 # check metadata output
 print r.text
</pre>

 [1]: https://www.djangoproject.com/
 [2]: https://docs.djangoproject.com/en/1.9/topics/http/middleware/
 [3]: http://docs.python-requests.org/en/master/
 [4]: https://docs.djangoproject.com/en/1.9/ref/csrf/
