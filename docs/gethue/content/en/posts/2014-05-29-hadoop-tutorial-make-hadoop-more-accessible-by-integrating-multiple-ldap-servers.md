---
title: Make Hadoop more accessible by integrating multiple LDAP Servers
author: admin
type: post
date: 2014-05-29T17:17:22+00:00
url: /hadoop-tutorial-make-hadoop-more-accessible-by-integrating-multiple-ldap-servers/
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
slide_template:
  - default
categories:

---
Hue 3.6 (coming up this week) LDAP configuration has been drastically improved to enable multiple server support. Here is a quick guide on how to configure LDAP in Hue using this new configuration model.

# How it works

As described in [How to Make Hadoop Accessible to your Employees with Hue][1], there are several configuration parameters available. These have been transferred over to the new way of configuring LDAP: **server declarations**.

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2014/05/hue-multi-ldap.png" />][2]

**Adding users through Useradmin with multiple server declarations**

## Server declarations

You can have multiple LDAP servers configured in the hue.ini by providing multiple server declarations:

<pre><code class="bash">[desktop]

[[ldap]]

[[[ldap_servers]]]

[[[[server1]]]]

ldap_url=ldap://127.0.0.1

create_users_on_login=true

base_dn="dc=sub1.dc=example,dc=com"

[[[[[users]]]]]

user_filter="(objectClass=user)"

user_name_attr="uid"

[[[[[groups]]]]]

group_filter="(objectClass=group)"

group_name_attr="cn"

group_member_attr="member"

[[[[server2]]]]

ldap_url=ldap://127.0.0.2

create_users_on_login=true

base_dn="dc=sub2,dc=example,dc=com"

[[[[[users]]]]]

user_filter="(objectClass=user)"

user_name_attr="uid"

[[[[[groups]]]]]

group_filter="(objectClass=group)"

group_name_attr="cn"

group_member_attr="member"

</code></pre>

&nbsp;

The names “server1” and “server2” will be selectable by users when authenticating and admins when managing users. In the example above, the configuration parameters are exactly they would be in the original LDAP configuration, except on a per-server basis. The only parameters that are not defined on a per-server basis are:

  * create_users_on_login
  * ignore_username_case
  * force_username_lowercase

&nbsp;

To be more explicit, the parameters that are available to server declarations are:

  * base_dn
  * nt_domain
  * ldap_url
  * use_start_tls
  * ldap_cert
  * ldap_username_pattern
  * bind_dn
  * bind_password
  * users
      * user_filter
      * user_name_attr
  * groups
      * group_filter
      * group_name_attr
      * group_member_attr

&nbsp;

For more information on what these parameters do, check out [How to Make Hadoop Accessible to your Employees with Hue][1].

## Backwards compatible

To remain backwards compatible, the original configuration of LDAP is respected if there are no server declarations.

# Conclusion

We hope this helps you manage multiple directory service deployments and make Hadoop more accessible within your company.

&nbsp;

Have any suggestions? Feel free to tell us what you think through [hue-user][3] or[@gethue][4]!

 [1]: https://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/
 [2]: https://cdn.gethue.com/uploads/2014/05/hue-multi-ldap.png
 [3]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
 [4]: https://twitter.com/gethue
