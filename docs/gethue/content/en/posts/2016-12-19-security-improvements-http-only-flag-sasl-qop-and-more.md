---
title: New security improvements with HTTP only flag, sasl-qop and more
author: admin
type: post
date: 2016-12-19T04:01:13+00:00
url: /security-improvements-http-only-flag-sasl-qop-and-more/
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

---
Hello Hue admin,

Recently we have added many security options in Hue. This document describes some of the fixes and enables Hue administrators to enforce and manage secure Hue installation. Hue security improvements, [part 1 is here][1]:

### Fixed sessionid and csrftoken with http only flag

If the HttpOnly flag is included in HTTP response header, then the cookie cannot be accessed through client side script and thus browser will not reveal the cookie to any third party. In order to help mitigate the risk of cross-site scripting, A cookie with this attribute is called an HTTP-only cookie. Any information contained in an HTTP-only cookie is less likely to be disclosed to a hacker or a malicious Web site.

One can see cookies with httponly and secure attributes set in above image.

[<img src="https://cdn.gethue.com/uploads/2016/12/Screen-Shot-2016-12-15-at-4.22.11-PM-1024x947.png" />][2]

&nbsp;

If user intentionally deletes sessionid cookie and click on Hue page links then Hue will notify "Your session has expired. Reload this page to sign in again" forcing user to sign-in or refresh the page.

[<img src="https://cdn.gethue.com/uploads/2016/12/Screen-Shot-2016-12-15-at-4.36.26-PM.png" />][3]

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2016/12/Screen-Shot-2016-12-15-at-4.35.58-PM.png" />][4]

If user intentionally deletes sessionid cookie and click on Hue page links then Hue will notify "Your session has expired. Reload this page to sign in again" forcing user to sign-in or refresh the page.

### Using GETTRASHROOT when trashing files

Hue now relies on [GetTrashRoot][5] under the cover when deleting HDFS files. It will send properly move the files to the correct trash location when using encrypted zones with [KMS][6].

### Fixed SASL Support in hive and hue hive.server2.thrift.sasl.qop="auth-conf"

SASL mechanisms support integrity and privacy protection of the communication channel after successful authentication. With integrity protection, subsequent requests and responses are protected against tampering. With privacy protection, subsequent requests and responses are encrypted and therefore protected against unintended monitoring. Privacy protection automatically entails integrity protection. These different types of protection are referred to as the quality of protection (qop). It is negotiated between the client and server during the authentication phase of the SASL exchange. If the client and server cannot negotiate a common qop, then the SASL authentication fails.

SASL QOP values are

  * auth Authentication only
  * auth-int Authentication with integrity protection
  * auth-conf Authentication with integrity and privacy protection

In Thrift SASL library, the sasl_max_buffer support is already implemented. sasl_max_buffer in the hue.ini provides a bigger and configurable buffer size that allow to provide support for hive.server2.thrift.sasl.qop="auth-conf".

<pre><code class="bash">[desktop]

\# This property specifies the maximum size of the receive buffer in bytes in thrift sasl communication (default 2 MB).

sasl_max_buffer=2 \* 1024 \* 1024

</code></pre>

### Fixed XML Injection for oozie

XML injection vulnerabilities arise when user input is inserted into a server-side XML document in an unsafe way. It may be possible to use XML metacharacters to modify the structure of the resulting XML. Depending on the function in which the XML is used, it may be possible to interfere with the Hue's logic, to perform unauthorized actions or access sensitive data.

Hue validate and sanitize user input in Oozie code before incorporating it into an XML document.

###

### Fixed Turnoff HSTS header in Hue Load Balancer.

Turn off HSTS header in Hue Load Balancer and made sure Hue server is generating HSTS http header.

### Introducing Request HTTP Pool in Hue.

The Request Session object allows to persist certain parameters across requests. It also persists cookies across all requests made from the Session instance, and will use urllib3's connection pooling. We are making several requests to the same host:port, with this change the underlying TCP connection will be reused, which can result in a significant performance increase. With current pool size set to 40 connections and is configurable using "CHERRYPY_SERVER_THREADS" parameter.

<pre><code class="python">CACHE_SESSION = requests.Session()

CACHE_SESSION.mount('http://', requests.adapters.HTTPAdapter(pool_connections=conf.CHERRYPY_SERVER_THREADS.get(), pool_maxsize=conf.CHERRYPY_SERVER_THREADS.get()))

CACHE_SESSION.mount('https://', requests.adapters.HTTPAdapter(pool_connections=conf.CHERRYPY_SERVER_THREADS.get(), pool_maxsize=conf.CHERRYPY_SERVER_THREADS.get()))</code></pre>

 [1]: https://gethue.com/hue-security-improvements/
 [2]: https://cdn.gethue.com/uploads/2016/12/Screen-Shot-2016-12-15-at-4.22.11-PM.png
 [3]: https://cdn.gethue.com/uploads/2016/12/Screen-Shot-2016-12-15-at-4.36.26-PM.png
 [4]: https://cdn.gethue.com/uploads/2016/12/Screen-Shot-2016-12-15-at-4.35.58-PM.png
 [5]: http://aajisaka.github.io/hadoop-project/hadoop-project-dist/hadoop-hdfs/WebHDFS.html#Get_Trash_Root
 [6]: https://hadoop.apache.org/docs/stable/hadoop-kms/index.html
