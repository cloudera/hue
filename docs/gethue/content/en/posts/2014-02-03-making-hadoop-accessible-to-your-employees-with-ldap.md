---
title: Making Hadoop Accessible to your Employees with LDAP
author: admin
type: post
date: 2014-02-03T18:40:00+00:00
url: /making-hadoop-accessible-to-your-employees-with-ldap/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/75499679342/making-hadoop-accessible-to-your-employees-with-ldap
tumblr_gethue_id:
  - 75499679342
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
slide_template:
  - default
categories:

---
_Last updated on July 9th 2015_

&nbsp;

<p id="docs-internal-guid-49c91822-f8f9-c344-7f5b-b38ff53dec04">
  <a href="https://gethue.com/">Hue</a> easily integrates with your corporation’s existing identity management systems and provides authentication mechanisms for SSO providers. By changing a few configuration parameters, your employees can start doing big data analysis in their browser by leveraging an existing security policy.
</p>

&nbsp;

This blog post details the various features and capabilities available in Hue for [LDAP][1]:

  1. [Authentication][2]
  2. [Search bind][3]
  3. [Direct bind][4]

[Importing users][5]

[Importing groups][6]

[Synchronizing users and groups][7]

  1. [Attributes synchronized][8]
  2. [Useradmin interface][9]
  3. [Command line interface][10]

[LDAP search][11]

[Case sensitivity][12]

[LDAPS/StartTLS support][13]

[Debugging][14]

[Notes][15]

[Summary][16]

# 1.    Authentication {#t1}

The typical authentication scheme for Hue takes of the form of the following image:

<img src="https://lh4.googleusercontent.com/AQIzUO7ZAzhngTVb7dwqgn2GIDadjiIfrkdsSU6UbLnzW5pU0rix56YX1cS6czuvTWC1pfkDzuxoupsT07VRosYAWPV0a_cIqZqvlgJK__U8bi77yQq8rW-SKw" alt="image" width="624px;" height="432px;" />

Passwords are saved into the Hue databases.

&nbsp;

With the Hue LDAP integration, users can use their LDAP credentials to authenticate and inherit their existing groups transparently. There is no need to save or duplicate any employee password in Hue:

<img src="https://lh4.googleusercontent.com/5b7VQbyi_sI9FO1KR7Gk9ayWUJLJcziWGM22YiJveEIOgwz4FN5kXKHgxyHgT41CeXualfmCOM73C8k1IaU9PqBEtfessdJyLk9-rF4cZOq9JA0rx0XWUZDQfA" alt="image" width="624px;" height="468px;" />

There are several other ways to authenticate with Hue: PAM, SPNEGO, OpenID, OAuth, SAML2, etc. This section details how Hue can authenticate against an LDAP directory server.

&nbsp;

When authenticating via LDAP, Hue validates login credentials against a directory service if configured with this authentication backend:

&nbsp;

<pre><code class="bash">'desktop]

[[auth]]

backend=desktop.auth.backend.LdapBackend

</code></pre>

The LDAP authentication backend will automatically create users that don’t exist in Hue by default. Hue needs to import users in order to properly perform the authentication. The password is never imported when importing users. The following configuration can be used to disable automatic import:

<pre><code class="bash">'desktop]

[[ldap]]

create_users_on_login=false

</code></pre>

The purpose of disabling the automatic import is to only allow to login a predefined list of manually imported users.

&nbsp;

The case sensitivity of the authentication process is defined in the “Case sensitivity” section below.

&nbsp;

**Note**

If a user is logging in as A before enabling LDAP auth and then after enabling LDAP auth logs in as B,  all workflows, queries etc will be associated with the user A and be unavailable. The old workflows would need to have their owner fields changed to B: this can be done in [the Hue shell][17].

&nbsp;

There are two different ways to authenticate with a directory service through Hue:

  1. [Search bind][3]
  2. [Direct bind][4]

## 1.1.    Search bind {#t2}

The search bind mechanism for authenticating will perform an [ldapsearch][18] against the directory service and bind using the found [distinguished name][19] (DN) and password provided. This is, by default, used when authenticating with LDAP. The configurations that affect this mechanism are outlined in “LDAP search”.

## 1.2.    Direct bind {#t3}

The direct bind mechanism for authenticating will bind to the ldap server using the username and password provided at login. There are two options that can be used to choose how Hue binds:

  1. nt_domain - Domain component for [User Principal Names (UPN)][20] in active directory. This active directory specific idiom allows Hue to authenticate with active directory without having to follow LDAP references to other partitions. This typically maps to the email address of the user or the users ID in conjunction with the domain.
  2. ldap_username_pattern - Provides a template for the DN that will ultimately be sent to the directory service when authenticating.

&nbsp;

If ‘nt_domain’ is provided, then Hue will use a UPN to bind to the LDAP service:

&nbsp;

<pre><code class="bash">'desktop]

[[ldap]]

nt_domain=example.com

</code></pre>

Otherwise, the ‘ldap_username_pattern’ configuration is used (the <username> parameter will be replaced with the username provided at login):

&nbsp;

<pre><code class="bash">'desktop]

[[ldap]]

ldap_username_pattern="uid=<username>,ou=People,DC=hue-search,DC=ent,DC=cloudera,DC=com"

</code></pre>

Typical attributes to search for include:

&nbsp;

  1. uid
  2. sAMAccountName

&nbsp;

To enable direct bind authentication, the ‘search_bind_authentication’ configuration must be set to false:

&nbsp;

<pre><code class="bash">'desktop]

[[ldap]]

search_bind_authentication=false

</code></pre>

# 2.    Importing users {#t4}

If an LDAP user needs to be part of a certain group and have a particular set of permissions, then this user can be imported via the Useradmin interface:<img src="https://lh3.googleusercontent.com/KVf0ktv3eiPtdHNwKSOE2fwJAsrPshdhTed0q5NpyT6YL8EVNk4o1t0kW42vmYOJX-TVa6xKeVPgbuS6liwyv3h65VYZpOzs1U4aW2L30walG8i7hMn9Cr7Tyw" alt="image" width="624px;" height="256px;" />

&nbsp;

As you can see, there are two options available when importing:

  1. Distinguished name
  2. Create home directory

&nbsp;

If ‘Create home directory’ is checked, when the user is imported their home directory in HDFS will automatically be created, if it doesn’t already exist.

&nbsp;

If ‘Distinguished name’ is checked, then the username provided must be a full distinguished name (eg: uid=hue,ou=People,dc=gethue,dc=com). Otherwise, the Username provided should be a fragment of a [Relative Distinguished Name][19] (rDN) (e.g., the username “hue” maps to the rDN “uid=hue”). Hue will perform an LDAP search using the same methods and configurations as defined in the “LDAP search” section. Essentially, Hue will take the provided username and create a search filter using the ‘user_filter’ and ‘user_name_attr’ configurations. For more information on how Hue performs LDAP searches, see the “LDAP Search” section.

&nbsp;

The case sensitivity of the search and import processes are defined in the “Case sensitivity” section.

# 3.    Importing groups {#t5}

Groups are importable via the Useradmin interface. Then, users can be added to this group, which would provide a set of [permissions][21] (e.g. accessing the Impala application). This function works almost the exact same way as user importing, but has a couple of extra features.

<img src="https://lh5.googleusercontent.com/LvlA_uzaAP4R1JgRlFYNuDgZK-ydgBE965ocAx6pk6rP3EOeEBUarfboPqhJs8J8xjXNbhYJ5C2BA_FphgcyhdHHu1tSefXD9lI8SLeqBLOgyQh0OMXDrvuQRQ" alt="image" width="624px;" height="323px;" />

As the above image portrays, not only can groups be discovered via DN and rDN search, but users that are members of the group and members of the group’s subordinate groups can be imported as well. Posix groups and members are automatically imported if the group found has the object class ”posixGroup”.

# 4.    Synchronizing users and groups {#t6}

Users and groups can be synchronized with the directory service via the Useradmin interface or via a [command line utility][22]. The images from the previous sections use the words “Sync” to indicate that when a name of a user or group that exists in Hue is being added, it will in fact be synchronized instead. In the case of importing users for a particular group, new users will be imported and existing users will be synchronized. Note: Users that have been deleted from the directory service will not be deleted from Hue. Those users can be manually deactivated from Hue via the Useradmin interface.

The groups of a user can be synced when he logs in (to keep its permission in sync):

<pre><code class="bash">'desktop]

[[ldap]]

\# Synchronize a users groups when they login

\## sync_groups_on_login=false

</code></pre>

## 4.1.    Attributes synchronized {#t7}

Currently, only the first name, last name, and email address are synchronized. Hue looks for the LDAP attributes ‘givenName’, ‘sn’, and ‘mail’ when synchronizing.  Also, the ‘<span id="docs-internal-guid-10a61405-0603-d23c-d680-d96c2a0139bb">user_name_attr</span>’ config is used to appropriately choose the username in Hue. For instance, if ‘user_name_attr’ is set to “uid”, then the “uid” returned by the directory service will be used as the username of the user in Hue.

## 4.2.    Useradmin interface {#t8}

The “Sync LDAP users/groups” button in the Useradmin interface will  automatically synchronize all users and groups.<img src="https://lh4.googleusercontent.com/OLINkq2po8IjnFr6-V9uyiDrN-KBK3_IaRBLVIhwGy73b5F_UZIg7mI15XYeQnFNqKBajs8BXh7B7zkowJTxaHY91a04p2lZPBHkaMVbjtGXEcvE-XToqmr8cQ" alt="image" width="624px;" height="181px;" />

## 4.3.    Command line interface {#t9}

Here’s a quick example of how to use the command line interface to synchronize users and groups:

<pre class="code">&lt;hue root&gt;/build/env/bin/hue sync_ldap_users_and_groups</pre>

# 5.    LDAP search {#t10}

There are two configurations for restricting the search process:

  1. user_filter - General [LDAP filter][23] to restrict the search.
  2. user_name_attr - Which attribute will be considered the username to search against.

&nbsp;

Here is an example configuration:

<pre><code class="bash">'desktop]

[[ldap]]

[[[users]]]

user_filter=”objectClass=*”

user_name_attr=uid

\# Whether or not to follow referrals

\## follow_referrals=false

</code></pre>

With the above configuration, the LDAP search filter will take on the form:

<pre class="code">(&(objectClass=*)(uid=&lt;user entered usename&gt;))</pre>

# 6.    Case sensitivity {#t11}

Hue can be configured to ignore the case of usernames as well as force usernames to lower case via the ‘ignore_username_case’ and ‘force_username_lowercase’ configurations. These two configurations are recommended to be used in conjunction with each other. This is useful when integrating with a directory service containing usernames in capital letters and unix usernames in lowercase letters (which is a Hadoop requirement). Here is an example of configuring them:

[desktop]

<pre><code class="bash">'desktop]

[[ldap]]

ignore_username_case=true

force_username_lowercase=true

</code></pre>

# 7.    LDAPS/StartTLS support {#t12}

Secure communication with LDAP is provided via the SSL/TLS and StartTLS protocols. It allows Hue to validate the directory service it’s going to converse with. Practically speaking, if a Certificate Authority Certificate file is provided, Hue will communicate via LDAPS:

<pre><code class="bash">'desktop]

[[ldap]]

ldap_cert=/etc/hue/ca.crt

</code></pre>

The StartTLS protocol can be used as well (step up to SSL/TLS):

<pre><code class="bash">'desktop]

[[ldap]]

use_start_tls=true

</code></pre>

&nbsp;

# 8.    Debugging {#t12b}

Get more information when querying LDAP and use the ldapsearch tool:

<pre><code class="bash">'desktop]

[[ldap]]

debug=true

\# Sets the debug level within the underlying LDAP C lib.

\## debug_level=255

\# Possible values for trace_level are 0 for no logging, 1 for only logging the method calls with arguments,

\# 2 for logging the method calls with arguments and the complete results and 9 for also logging the traceback of method calls.

trace_level=0

</code></pre>

**Note**

Make sure to add to the Hue server environment:

<pre><code class="bash">DESKTOP_DEBUG=true

DEBUG=true</code></pre>

&nbsp;

# 9.    Notes {#t13}

  1. Setting “search_bind_authentication=true” in the hue.ini will tell Hue to perform an LDAP search using the bind credentials specified in the hue.ini (bind_dn, bind_password). Hue will then search using the base DN specified in “base_dn” for an entry with the attribute, defined in “user_name_attr”, with the value of the short name provided in the login page. The search filter, defined in “user_filter” will also be used to limit the search. Hue will search the entire subtree starting from the base DN.
  2. Setting  ”search_bind_authentication=false” in the hue.ini will tell Hue to perform a direct bind to LDAP using the credentials provided (not bind_dn and bind_password specified in the hue.ini). There are two effective modes here:
      1. nt_domain is specified in the hue.ini: This is used to connect to an Active Directory directory service. In this case, the UPN (User Principal Name) is used to perform a direct bind. Hue forms the UPN by concatenating the short name provided at login and the nt_domain like so: “<short name>@<nt_domain>”. The ‘ldap_username_pattern’ config is completely ignore.
      2. nt_domain is NOT specified in the hue.ini: This is used to connect to all other directory services (can even handle Active Directory, but nt_domain is the preferred way for AD). In this case, ‘ldap_username_pattern’ is used and it should take on the form “cn=<username>,dc=example,dc=com” where <username> will be replaced with whatever is provided at the login page.
  3. The UserAdmin app will always perform an LDAP search when manage LDAP entries and will then always use the “bind_dn”, “bind_password”, “base_dn”, etc. as defined in the hue.ini.
  4. At this point in time, there is no other bind semantics supported other than SIMPLE_AUTH. For instance, we do not yet support MD5-DIGEST, NEGOTIATE, etc. Though, we definitely want to hear from folks what they use so we can prioritize these things accordingly!

# 10.    Summary {#t14}

The [Hue team][24] is working hard on improving [security][25]. Upcoming LDAP features include: Import nested LDAP groups and multidomain support for Active Directory. We hope this brief overview of LDAP in Hue will help you make your system more secure, more compliant with current security standards, and open up big data analysis to many more users!

As always, feel free to contact us at [hue-user@][26] or [@gethue][27]!

 [1]: http://en.wikipedia.org/wiki/Ldap
 [2]: #t1
 [3]: #t2
 [4]: #t3
 [5]: #t4
 [6]: #t5
 [7]: #t6
 [8]: #t7
 [9]: #t8
 [10]: #t9
 [11]: #t10
 [12]: #t11
 [13]: #t12
 [14]: #t12b
 [15]: #t13
 [16]: #t14
 [17]: https://gethue.com/how-to-manage-the-hue-database-with-the-shell/
 [18]: http://www.zytrax.com/books/ldap/ch14/#ldapsearch
 [19]: http://www.zytrax.com/books/ldap/apa/dn-rdn.html
 [20]: http://msdn.microsoft.com/en-us/library/windows/desktop/ms680857(v=vs.85).aspx
 [21]: http://gethue.tumblr.com/post/48706063756/how-to-manage-permissions-in-hue
 [22]: https://github.com/cloudera/hue/blob/branch-3.5/apps/useradmin/src/useradmin/management/commands/sync_ldap_users_and_groups.py
 [23]: http://www.zytrax.com/books/ldap/apa/search.html
 [24]: http://gethue.tumblr.com/post/66661140648/hue-team-retreat-thailand
 [25]: http://gethue.tumblr.com/post/69803995520/recent-security-enhancements
 [26]: http://groups.google.com/a/cloudera.org/group/hue-user
 [27]: https://twitter.com/gethue
