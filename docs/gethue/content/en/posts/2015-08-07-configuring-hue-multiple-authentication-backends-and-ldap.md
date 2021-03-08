---
title: Configuring Hue with Multiple Authentication Backends and LDAP
author: admin
type: post
date: 2015-08-07T16:17:27+00:00
url: /configuring-hue-multiple-authentication-backends-and-ldap/
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
categories:
---

In the upcoming Hue 3.9 release, Hue will support the ability to configure multiple authentication backends.

Hue already allows you to authenticate with several authentication services including [LDAP][1], [OpenID][2], [SAML][3], database, etc. With this latest feature, you can now configure <span style="text-decoration: underline;">multiple authentication sources</span> for Hue to check, in order of priority, when authenticating and authorizing users.

{{< youtube oGqrVGw9Y20 >}}

For example, to enable Hue to first attempt LDAP directory lookup before falling back to the database-backed user model, we can update the hue.ini configuration file or [Hue safety valve][4] in Cloudera Manager with a list containing first the `LdapBackend` followed by either the `ModelBackend` or custom `AllowFirstUserDjangoBackend` (permits first login and relies on user model for all subsequent authentication):

<pre><code class="bash">

[desktop]

[[auth]]

backend=desktop.auth.backend.LdapBackend,desktop.auth.backend.AllowFirstUserDjangoBackend

</code></pre>

This tells Hue to first check against the [configured LDAP directory service][5], and if the username is not found in the directory, then attempt to authenticate the user with the Django user manager.

**Note**

With the exception of [OAuth][6] authentication, we can continue to add additional backends to this configuration setting in order of precedence. However, currently if OAuth authentication is configured it must be the only backend specified in hue.ini.

As usual feel free to comment and send feedback on the [hue-user][7] list or [@gethue][8]!

[1]: https://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/
[2]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L414
[3]: https://gethue.com/sso-with-hue-new-saml-backend/
[4]: http://www.cloudera.com/content/cloudera/en/documentation/cloudera-manager/v4-8-3/Cloudera-Manager-Managing-Clusters/cmmc_safety_valve.html
[5]: http://www.cloudera.com/content/cloudera/en/documentation/core/latest/topics/cdh_sg_hue_ldap_config.html
[6]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L433
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
