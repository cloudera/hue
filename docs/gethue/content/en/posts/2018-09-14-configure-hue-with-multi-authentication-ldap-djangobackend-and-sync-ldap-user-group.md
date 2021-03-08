---
title: 'Configure Hue with Multi-Authentication: LDAP & DjangoBackend and Sync LDAP user/group'
author: admin
type: post
date: 2018-09-14T20:54:23+00:00
url: /configure-hue-with-multi-authentication-ldap-djangobackend-and-sync-ldap-user-group/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4

---
<span style="font-weight: 400;">Aloha, Hue administrators,</span>

<span style="font-weight: 400;">Hue supports multi-authentication since <a href="https://gethue.com/category/release/">Hue 3.9</a>, we can turn on Hue’s multi-authentication by updating Hue configurations through CM UI or hue.ini.</span>

<span style="font-weight: 400;">On any CM-managed cluster, go to hue’s configuration page and search for “safety”:</span>

<span style="font-weight: 400;">http://YourCluster.com:7180/cmf/services/10/config#filterfreeText=safety</span>

<span style="font-weight: 400;">Then update </span>**Hue Service Advanced Configuration Snippet (Safety Valve) for hue_safety_valve.ini** <span style="font-weight: 400;">as following:</span>

<pre><code class="bash">

[desktop]

[[auth]

backend=desktop.auth.backend.LdapBackend,desktop.auth.backend.AllowFirstUserDjangoBackend

</code></pre>

Then configure Hue LDAP related configurations through CM UI: http://YourCluster.com:7180/cmf/services/10/config as following:

[<img src="https://cdn.gethue.com/uploads/2018/09/HUE-LDAP-Configurations.png"/>][1]

Here is a sample of the multi-authentication with ldap for /etc/hue/conf/hue.ini in case that you don’t have CM:

<pre><code class="bash">

[desktop]

[[auth]

backend=desktop.auth.backend.LdapBackend,desktop.auth.backend.AllowFirstUserDjangoBackend

[[ldap]]

ldap_url=ldap://ldapserver.ad.com:389

search_bind_authentication=true

create_users_on_login=true

base_dn="ou=Test,DC=ad,DC=com"

bind_dn="testadmin@ad.com"

bind_password_script={{CMF_CONF_DIR}}/altscript.sh sec-5-bind_password

#bind_password="YourBindPassword"

[[[users]]]

user_filter="objectclass=user"

user_name_attr="sAMAccountName"

[[[groups]]]

group_filter="objectclass=group"

</code></pre>

<!--more-->

<!--more-->Save Changes, re-deploy client configuration then restart Hue.

<span style="font-weight: 400;">Now you should be able to log in hue as any LDAP user or Django backend user. If you are using <a href="https://gethue.com/category/hue-3-12/">Hue 3.12</a> or newer, you will find following UI with the extra drop down for "LDAP" or "Local".</span>

[<img src="https://cdn.gethue.com/uploads/2018/09/LDAP-login.png"/>][2]

<span style="font-weight: 400;">Once you login as superuser, you will be able to sync up LDAP users/groups through "Manager Users" page: </span>[<span style="font-weight: 400;">https://YourHueHost.com:8889/hue/useradmin/users</span>][3]<span style="font-weight: 400;">.</span>

<span style="font-weight: 400;">On "Users" tab, click on "</span>**Add/Sync LDAP user"**<span style="font-weight: 400;"> button...</span>

[<img src="https://cdn.gethue.com/uploads/2018/09/AddSyncLDAPUser.png"/>][4]

<span style="font-weight: 400;">Then fill in LDAP user name either like "test*"</span>

[<img class="size-full wp-image-5532 alignleft" src="https://cdn.gethue.com/uploads/2018/09/SyncUserWithWildChar.png"/>][5]

<span style="font-weight: 400;">Click "</span>**Add/Sync user"**<span style="font-weight: 400;"> button, all users starts with "test" will be synced.</span>

[<img src="https://cdn.gethue.com/uploads/2018/09/UserAdminPage.png"/>][6]

<span style="font-weight: 400;">You can also sync user with LDAP distinguished name like: "</span>**CN=atestë01,OU=huetest,OU=test,DC=ad,DC=com" **<span style="font-weight: 400;">with "</span>**Distinguished name" **<span style="font-weight: 400;">checked.</span>

[<img src="https://cdn.gethue.com/uploads/2018/09/add_syncLDAPUsers_distinguishedname.png"/>][7]

<span style="font-weight: 400;">Similarly for LDAP group,  just navigate to "<strong>Groups</strong>" tab then click "</span>**Add/Sync LDAP group"**<span style="font-weight: 400;"> button, then fill in following accordingly, then click "</span>**Add/Sync group"**<span style="font-weight: 400;">.</span>

[<img src="https://cdn.gethue.com/uploads/2018/09/SyncLDAPGroupWithDistinguishedName.png"/>][8]

<span style="font-weight: 400;">You can always use ldapsearch command on your host to verify if the user/group exists on your LDAP server.</span>

<pre><code class="bash">

ldapsearch -LLL -H ldap://ldapserver.ad.com:389 -D admin@ad.com -w yourbindPassword -b "cn=testuser,ou=test,DC=ad,DC=com"

ldapsearch -LLL -H ldap://ldapserver.ad.com:389 -D admin@ad.com -w yourbindPassword -b "cn=testgroup,ou=test,DC=ad,DC=com"

</code></pre>

<span style="font-weight: 400;">As always feel free to comment and send feedback on the </span>[<span style="font-weight: 400;">hue-user</span>][9] <span style="font-weight: 400;">list or </span>[<span style="font-weight: 400;">@gethue</span>][10]<span style="font-weight: 400;">!</span>

 [1]: https://cdn.gethue.com/uploads/2018/09/HUE-LDAP-Configurations.png
 [2]: https://cdn.gethue.com/uploads/2018/09/LDAP-login.png
 [3]: https://yourhuehost.com:8889/hue/useradmin/users
 [4]: https://cdn.gethue.com/uploads/2018/09/AddSyncLDAPUser.png
 [5]: https://cdn.gethue.com/uploads/2018/09/SyncUserWithWildChar.png
 [6]: https://cdn.gethue.com/uploads/2018/09/UserAdminPage.png
 [7]: https://cdn.gethue.com/uploads/2018/09/add_syncLDAPUsers_distinguishedname.png
 [8]: https://cdn.gethue.com/uploads/2018/09/SyncLDAPGroupWithDistinguishedName.png
 [9]: http://groups.google.com/a/cloudera.org/group/hue-user
 [10]: https://twitter.com/gethue
