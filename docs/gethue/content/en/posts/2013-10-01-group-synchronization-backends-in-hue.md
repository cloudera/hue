---
title: Group Synchronization Backends in Hue
author: admin
type: post
date: 2013-10-01T17:55:00+00:00
url: /group-synchronization-backends-in-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/62823068916/group-synchronization-backends-in-hue
tumblr_gethue_id:
  - 62823068916
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
  - Development

---
<p id="docs-internal-guid-63e96778-7525-df72-d153-e369f8395313">
  <a href="https://gethue.com">Hue</a><span>is the turn-key solution for </span><a href="http://hadoop.apache.com/">Apache Hadoop</a><span>. It hides the complexity of the ecosystem including HDFS, Oozie, MapReduce, etc. Hue provides authentication and integrates with </span><a href="http://gethue.tumblr.com/post/62273866476/sso-with-hue-new-saml-backend">SAML</a><span>, </span><a href="http://gethue.tumblr.com/post/48706063756/how-to-manage-permissions-in-hue">LDAP</a><span>, and </span><a href="http://gethue.tumblr.com/post/50341521241/single-sign-on-in-hue-with-twitter-and-oauth">other</a><span> systems. A new feature added in Hue is the ability to synchronize groups with a third party authority provider. In this blog post, we’ll be covering the basics of creating a Group Synchronization Backend.</span>
</p>

<span> </span>

# <span>The Design</span>

<span>The purpose of the group synchronization backends are to keep Hue’s internal group lists fresh. The design was separated into two functional parts:</span>

  1. <span>A way to synchronize on every request.</span>
  2. <span>A definition of how and what to synchronize.</span>

![image][1]

<span>Image 1: Request cycle in Hue with a synchronization backend.</span>

<span>The first function is a Django </span>[<span>middleware</span>][2] <span>that is called on every request. It is intended to be immutable, but configurable. The second function is a backend that can be customized. This gives developers the ability to choose how their groups and user-group memberships can be synchronized. The middleware can be configured to use a particular synchronization backend and will call it on every request. If no backend is configured, then the middleware is disabled.</span>

# <span> </span>

# <span>Creating Your Own Backend</span>

<span>A synchronization backend can be created by extending a class and providing your own logic. Here is an example backend that comes </span>[<span>packaged</span>][3] <span>with Hue:</span>

<pre class="code">class LdapSynchronizationBackend(DesktopSynchronizationBackendBase):
  USER_CACHE_NAME = 'ldap_use_group_sync_cache'

  def sync(self, request):
    user = request.user

    if not user or not user.is_authenticated:
      return

    if not User.objects.filter(username=user.username, userprofile__creation_method=str(UserProfile.CreationMethod.EXTERNAL)).exists():
      LOG.warn("User %s is not an Ldap user" % user.username)
      return

    # Cache should be cleared when user logs out.
    if self.USER_CACHE_NAME not in request.session:
      request.session[self.USER_CACHE_NAME] = import_ldap_users(user.username, sync_groups=True, import_by_dn=False)
      request.session.modified = True</pre>

<span>In the above code snippet, the synchronization backend is defined by extending “DesktopSynchronizationBackendBase”. Then, the method “sync(self, request)” is overridden and provides the syncing logic. </span>

## <span>Configuration</span>

The synchronization middleware can be configured to use a backend by changing “desktop -> auth -> [user_group_membership_synchronization_backend][4]” to the full import path of your class. For example, setting this config to “desktop.auth.backend.LdapSynchronizationBackend” configures Hue to synchronize with the configured LDAP authority.

## <span>Design Intelligently</span>

<span>Backends in Hue are extremely powerful and can affect the performance of the server. So, they should be designed in such a fashion that they do not do any operations that block for long periods of time. Also, they should manage the following appropriately:</span>

  1. <span>Throttling requests to whatever service contains the group information.</span>
  2. <span>Ensuring users are authenticated.</span>
  3. <span>Caching if appropriate.</span>

# <span> </span>

# <span>Summary</span>

<span>Hue is enterprise grade software ready to integrate with LDAP, SAML, etc. The newest feature, Group Synchronization, ensures corporate authority is fresh in Hue. It’s easy to configure and create backends and Hue comes with an LDAP backend.</span>

<span>Hue is undergoing heavy development and are welcoming external contributions! Have any suggestions? Feel free to tell us what you think through </span>[<span>hue-user</span>][5] <span>or </span>[<span>@gethue</span>][6]<span>.</span>

 [1]: http://media.tumblr.com/67f0b72e07cf0a824f6360e7ceaad73a/tumblr_inline_mu04cse78O1qzo3ii.png
 [2]: https://docs.djangoproject.com/en/1.4/topics/http/middleware/
 [3]: https://github.com/cloudera/hue/blob/23933dd0a1ce182d03549221143ea930c78640b7/desktop/core/src/desktop/auth/backend.py#L377
 [4]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L98
 [5]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
 [6]: http://twitter.com/gethue/
