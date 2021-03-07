---
title: Recent Security Enhancements
author: admin
type: post
date: 2013-12-12T18:54:00+00:00
url: /recent-security-enhancements/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/69803995520/recent-security-enhancements
tumblr_gethue_id:
  - 69803995520
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
categories:
#  - News

---
<p id="docs-internal-guid-4e51c4c8-e826-f763-73a0-2427956de77d">
  <a href="http://gethue.com">Hue</a> has seen a slew of security improvements recently (from <a href="http://gethue.tumblr.com/post/69115755563/hue-3-5-and-its-redesign-are-out">Hue 3.5</a>). The most important ones have been enabling encryption when communicating with other services:
</p>

  1. <span>Secure database connection (</span>[<span>HUE-1638</span>][1]<span>)</span>
  2. <span>HiveServer2 over SSL (</span>[<span>HUE-1749</span>][2]<span>)</span>

&nbsp;

<span>In addition, several other security options have been added:</span>

  1. <span>Session timeout is now configurable (</span>[<span>HUE-1528</span>][3]<span>)</span>
  2. <span>Cookies can be secure (</span>[<span>HUE-1529</span>][4]<span>)</span>
  3. <span>HTTP only in session cookie if supported (</span>[<span>HUE-1639</span>][5]<span>)</span>
  4. <span>Allowed HTTP methods can be defined in the hue.ini</span>
  5. <span>Cipher list can be restricted when using SSL</span>

&nbsp;

# <span>Secure Database Connection</span>

<span>Connections vary depending on the database. Hue uses different clients to communicate with each database internally. They all specify a common interface known as the DBAPI version 2 interface. Client specific options, such as secure connectivity, can be passed through the interface. For example (MySQL):</span>

<pre>[desktop]
  [[databases]]
   …
   options={"ssl":{"ca":"/tmp/ca-cert.pem"}}</pre>

# <span>HiveServer2 over SSL</span>

<span>By providing a CA certificate, private key, and public certificate, Hue can communicate with HiveServer2 over SSL. This is configurable in the </span>[<span>hue.ini</span>][6]<span>. For example:</span>

<pre>[beeswax]
  [[ssl]]
  enabled=true
  cacerts=/etc/hue/cacerts.pem
  key=/etc/hue/key.pem
  cert=/etc/hue/key.pemkey=/etc/hue/publiccert.pem</pre>

# HiveServer2 over Kerberos with LDAP authentication

HiveServer2 supports [LDAP authentication][7] with a client connecting under a Thrift connection with security. This means Hue can provide a LDAP password that will be used by HiveServer2 to authenticate Hue. The username is defaulting to ‘hue’ or the username of the Hue Kerberos ticket. This is configurable in the [hue.ini][6]. For example:

<pre>[desktop]
  ldap_password=MY_HUE_USER_LDAP_PASSWORD</pre>

# <span>Session Timeout</span>

<span>The session timeout can be set in the </span>[<span>hue.ini</span>][8] <span>at desktop->session->ttl. Example:</span>

<pre>[desktop]
  [[session]]
  ttl=3600</pre>

# <span>Secure Cookies</span>

<span>Secure session cookies can be enabled in the </span>[<span>hue.ini</span>][9] <span>at desktop->session->secure. Example:</span>

<pre>[desktop]
  [[session]]
  secure=true</pre>

<span>The HTTPonly flag can be set via the </span>[<span>hue.ini</span>][10] <span>at desktop->session->http_only. Example:</span>

<pre>[desktop]
  [[session]]
  http_only=true</pre>

# <span>Allowed HTTP Methods</span>

<span>Which HTTP request methods the server should respond to can be controlled via desktop->http_allowed_methods in the hue.ini. For example:</span>

<pre>[desktop]
http_allowed_methods=options,get,head,post,put,delete,connect</pre>

# <span>Restricting the Cipher List</span>

<span>Cipher list support with HTTPS can be restricted via desktop->ssl_cipher_list in the hue.ini. The value is in </span>[<span>cipher list format</span>][11]<span>. For example:</span>

<pre>[desktop]
ssl_cipher_list=DEFAULT:!aNULL:!eNULL:!LOW:!EXPORT:!SSLv2</pre>

# URL redirect whitelist

Restrict to which domains or pages Hue can redirect the users.

<pre>[desktop]
redirect_whitelist=^http://www.mydomain.com/.*$</pre>

<span>The Hue team is working hard improving security. We hope these recent improvements make your system more secure and more compliant with security standards. As always, feel free to contact us at </span>[<span>hue-user</span>][12] <span>or </span>[<span>@gethue</span>][13]<span>.</span>

 [1]: https://issues.cloudera.org/browse/HUE-1638
 [2]: https://issues.cloudera.org/browse/HUE-1749
 [3]: https://issues.cloudera.org/browse/HUE-1528
 [4]: https://issues.cloudera.org/browse/HUE-1529
 [5]: https://issues.cloudera.org/browse/HUE-1639
 [6]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L494
 [7]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/4.3.0/CDH4-Security-Guide/cdh4sg_topic_9_1.html?scroll=topic_9_1_unique_4
 [8]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L204
 [9]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L208
 [10]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L211
 [11]: http://www.openssl.org/docs/apps/ciphers.html
 [12]: http://groups.google.com/a/cloudera.org/group/hue-user
 [13]: http://twitter.com/gethue
