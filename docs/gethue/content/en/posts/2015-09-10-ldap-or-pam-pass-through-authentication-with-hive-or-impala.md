---
title: LDAP or PAM pass-through authentication with Hive or Impala and Impersonation
author: admin
type: post
date: 2015-09-10T19:40:02+00:00
url: /ldap-or-pam-pass-through-authentication-with-hive-or-impala/
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
Hue is a server between users logged in their browsers and the respective Hadoop services. Consequently, Hue is seen as a single 'hue' user by the other servers.

Impersonation is used in order to still apply the permissions of the real logged-in user. For example when a user 'bob' submits a query, Hue also sends the username of this user and HiveServer2 will use 'bob' and not 'hue' as the owner of the query.

[<img src="https://cdn.gethue.com/uploads/2015/09/hue-auth-client.png" />][1]

Hue supports multiple way to authenticate with the other servers: Kerberos and LDAP are common, as well as PAM.

In the next version of Hue, it is now possible to differentiate which authentication to use for either Hive or Impala (it used to be a unique common configuration). This for example let you configure Hue to use LDAP to talk to HiveServer2 and Kerberos for Impala.

`usernames` and `passwords` to use for LDAP, PAM are configurable in the main configuration section (`[desktop]`) and can be overridden in each respective apps.

In order to provide better security, it is also now possible to provide a path to a file that contains the password to use (instead of putting it in plain in the `hue.ini`). If the plain password is not set, the file will be used.

For example, here is how to configure a 'hue' user and password in a file for all the apps

<pre><code class="bash">

[desktop]

auth_username=hue

\# auth_password=

auth_password_script=/path/to/ldap_password

</code></pre>

If Hue needs to authenticate to HiveServer2 with some different username and password:

<pre><code class="bash">

[beeswax]

auth_username=hue_hive

auth_password=hue_hive_pwd

\# auth_password_script=

</code></pre>

If Impala is not using LDAP authentication but Hive does, we disable it in [desktop] and do not specify anything in [impala]:

<pre><code class="bash">

[desktop]

auth_username=hue

\# auth_password=

\# auth_password_script=

[beeswax]

auth_username=hue_hive

auth_password=hue_hive_pwd

[impala]

\# auth_username=

\# auth_password=hue_impala

\# auth_password_script=/

</code></pre>

**Note**

Not setting any password will make the LDAP/PAM authentication inactive.

**Note**

[SSL encryption][2] between Hue and the other Hadoop services is also supported

**Note**

In CM's "HiveServer2 Advanced Configuration Snippet (Safety Valve) for hive-site.xml" to add the configuration overrides to hive-site.xml.

Adding those configurations to: Hive > Configuration > Gateway > Advanced > Hive Client Advanced Configuration Snippet (Safety Valve) for hive-site.xml. Then save and restart both Hive and Hue.  This should allow Hue to pickup the hive-site.xml changes

&nbsp;

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/09/hue-auth-client.png
 [2]: https://gethue.com/how-to-use-hue-with-hive-and-impala-configured-with-ldap-authentication-and-ssl/
