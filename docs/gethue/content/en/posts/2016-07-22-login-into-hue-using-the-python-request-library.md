---
title: Login into Hue using the Python Request library
author: admin
type: post
date: 2016-07-22T00:23:02+00:00
url: /login-into-hue-using-the-python-request-library/
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
categories:
  - Development

---
## **In this little snippet we will show you how to login into HUE using python requests library.**

Hue is based on the [Django Web Framework][1]. Django comes with user authentication system. Django uses sessions and [middleware][2] to hook the authentication system into request object. HUE uses stock auth form which uses "username" and "password" and "csrftoken" form variables to authenticate.

In this code snippet, we will use well-known python "[requests][3]" library. we will first acquire "[csrftoken][4]" by GET "login_url". We will create python dictionary of form data which contains "username", "password" and "csrftoken" and the "next_url" and another python dictionary for header which contains the "Referer" url and empty python dictionary for the cookies. After POST request to "login_url" we will get status. Check the `r.status_code`. If `r.status_code!=200` then you have problem in username and/or password.

Once the request is successful then capture headers and cookies for subsequent requests. Subsequent request.session calls can be made by providing `cookies=session.cookies` and `headers=session.headers`.

[sourcecode language="python" wraplines="false" collapse="false"]

import requests

def login_djangosite():

next_url = "/"

login_url = "http://localhost:8888/accounts/login?next=/"

session = requests.Session()

r = session.get(login_url)

form_data = dict(username="[your hue username]",password="[your hue password]",

csrfmiddlewaretoken=session.cookies['csrftoken'],next=next_url)

r = session.post(login_url, data=form_data, cookies=dict(), headers=dict(Referer=login_url))

\# check if request executed successfully?

print r.status_code

cookies = session.cookies

headers = session.headers

r=session.get('http://localhost:8888/metastore/databases/default/metadata',

cookies=session.cookies, headers=session.headers)

print r.status_code

\# check metadata output

print r.text

[/sourcecode]

 [1]: https://www.djangoproject.com/
 [2]: https://docs.djangoproject.com/en/1.9/topics/http/middleware/
 [3]: http://docs.python-requests.org/en/master/
 [4]: https://docs.djangoproject.com/en/1.9/ref/csrf/
