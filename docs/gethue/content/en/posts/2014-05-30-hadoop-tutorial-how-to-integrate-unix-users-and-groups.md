---
title: How to Integrate Unix users and groups
author: admin
type: post
date: 2014-05-30T18:55:22+00:00
url: /hadoop-tutorial-how-to-integrate-unix-users-and-groups/
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

Hue allows you to authenticate with several services like your company [LDAP][1], [OAuth][2], [OpenId][3], [SAML][4] etc. This blog post covers how to integrate with linux account names in Hue by synchronizing with the underlying system.

# Tutorial

The following will guide you in importing Linux accounts and groups into Hue:

1. Ensure the ‘hadoop’ group is on the system. See the ‘Hadoop group’ section below to learn to how to verify this in different environments.
2. From the command line, execute the command build/env/bin/hue useradmin_sync_with_unix. This will import users and groups from the machine Hue is on.
3. <span style="color: #ff0000;"><b>Important</b></span>: as a Hue administrator, give a password to each imported member. Users will not be able to login until a password has been provided to them. If you want to re-use Linux user password, you should look at the [PAM backend][5] instead (caveat: it can only authenticate the user who is running the Hue server (this being normal PAM behaviour in Linux) unless we run Hue server as root, which is not recommended. LDAP is the alternative recommended solution).

Here is a quick video demonstrating the above:

{{< youtube NfCKYJjWkZw >}}

&nbsp;

From the Hue root (/use/lib/hue by default or /opt/cloudera/parcels/CDH/lib/hue/ with CM):

<pre><code class="bash">build/env/bin/hue useradmin_sync_with_unix</code></pre>

&nbsp;

If using CM, export this variable in order to point to the correct database:

Where <id> is the most recent ID in that process directory for hue-HUE_SERVER.

A quick way to get the correct directory is to use this script:

<pre><code class="bash">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'\`"</code></pre>

&nbsp;

## Command line interface

useradmin_sync_with_unix comes with a few useful command line arguments:

- -min-uid - The minimum linux user ID that will be imported (inclusive). The default value is 500.
- -max-uid - The maximum linux user ID that will be imported (exclusive). The default value is 65334.
- -min-gid - The minimum linux group ID that will be imported (inclusive). The default value is 500.
- -max-gid - The maximum linux group ID that will be imported (exclusive). The default value is 65334.
- -check-shell - A boolean flag  to see if the users shell is set to /bin/false.

## Hadoop group

To verify the hadoop group exists, you can use the ‘getent’ command:

<pre><code class="bash">getent group | grep hadoop</code></pre>

To add the hadoop group, you can use the ‘groupadd’ command:

<pre><code class="bash">groupadd hadoop</code></pre>

#

# Conclusion

We hope this utility opens up your Hadoop cluster to your users and simplifies administration.

Have any suggestions? Feel free to tell us what you think through [hue-user][6] or [@gethue][7]!

[1]: https://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/
[2]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L433
[3]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L414
[4]: https://gethue.com/sso-with-hue-new-saml-backend/
[5]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L134
[6]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
[7]: https://twitter.com/gethue
