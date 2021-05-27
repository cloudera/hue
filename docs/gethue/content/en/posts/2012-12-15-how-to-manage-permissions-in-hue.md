---
title: 'How-to: Manage Permissions in Hue'
author: admin
type: post
date: 2012-12-15T05:00:00+00:00
url: /how-to-manage-permissions-in-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/48706063756/how-to-manage-permissions-in-hue
tumblr_gethue_id:
  - 48706063756
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

---
[Hue][1] is a web interface for [Apache Hadoop][2] that makes common Hadoop tasks such as running [MapReduce][3] jobs, browsing [HDFS][3], and creating [Apache Oozie][4] workflows, easier. (To learn more about the integration of Oozie and Hue, see this [blog post][5].) In this post, we’re going to focus on how one of the fundamental components in Hue, Useradmin, has matured.

## New User and Permission Features

User and permission management in Hue has changed drastically over the past year. Oozie workflows, [Apache Hive][6] queries, and MapReduce jobs can be shared with other users or kept private. Permissions exist at the app level. Access to particular apps can be restricted, as well as certain sections of the apps. For instance, access to the shell app can be restricted, as well as access to the [Apache HBase][7], [Apache Pig][8], and [Apache Flume][9] shells themselves. Access privileges are defined for groups and users can be members of one or more groups.

## Changes to Users, Groups, and Permissions

Hue now supports authentication against PAM, [Spnego][10], and an LDAP server. Users and groups can be imported from LDAP and be treated like their non-external counterparts. The import is manual and is on a per user/group basis. Users can authenticate using different backends such as LDAP. Using the LDAP authentication backend will allow users to login using their LDAP password. This can be configured in /etc/hue/hue.ini by changing the ‘desktop.auth.backend’ setting to ‘desktop.auth.backend.LdapBackend’. The LDAP server to authenticate against can be configured through the settings under ‘desktop.ldap’.

Here’s an example:

A company would like to use the following LDAP users and groups in Hue:

  1. John Smith belonging to team A
  2. Helen Taylor belonging to team B

Assuming the following access requirements:

  1. Team A should be able to use Beeswax, but nothing else.
  2. Team B should only be able to see the Oozie dashboard with readonly permissions.

In Hue 1 the scenarios cannot be realistically addressed given the lack of groups.

In Hue 2 the scenarios can be addressed more appropriately. Users can be imported from LDAP by clicking “Add/Sync LDAP user” in Useradmin > Users:

[<img class="aligncenter title=" src="http://www.cloudera.com/wp-content/uploads/2012/12/hue11.png"/>][11]

Similarly, groups can be imported from LDAP by clicking “Add/Sync LDAP group” in Useradmin > Groups.

If a previously imported user’s information was updated recently, the information in Hue will need to be resynchronized. This can be achieved through the LDAP sync feature:

[<img class="aligncenter title=" src="http://www.cloudera.com/wp-content/uploads/2012/12/hue21.png"/>][12]

Part A of the example can be addressed by explicitly allowing access Beeswax for Team A. This is managed in the “Groups” tab of the Useradmin app:

[<img class="aligncenter title=" src="http://www.cloudera.com/wp-content/uploads/2012/12/hue31.png"/>][13]

The Team A group can be edited by clicking on its name, where access privileges for the group are selectable. Here, the “beeswax.access” permission would be selected and the others would be unselected:

[<img title="hue4" src="http://www.cloudera.com/wp-content/uploads/2012/12/hue4.png"/>][14]

Part B of the example can be handled by explicitly defining access for Team B. This can be accomplished by following the same steps in part A, except for Team B. Every permission would be unselected except “oozie.dashboard_jobs_access”:

[<img title="hue5" src="http://www.cloudera.com/wp-content/uploads/2012/12/hue5.png"/>][15]

By explicitly setting the app level permissions, the apps that these users will be able to see will change. For instance, Helen, who is a member of Team B, will only see the Oozie app available:

[<img title="hue6" src="http://www.cloudera.com/wp-content/uploads/2012/12/hue6.png"/>][16]

&nbsp;

## Blacklisting apps in the hue.ini

You can also blacklist the apps at the code level, e.g. in the hue.ini:

<pre><code class="bash">[desktop]

app_blacklist=search,security,oozie,jobbrowser,pig,beeswax,search,zookeeper,impala,rdbms,spark,metastore,hbase,sqoop,jobsub

</code></pre>

&nbsp;

## Summary

User management has been revamped, groups were added, and various backends are exposed. One such backend, LDAP, facilitates synchronization of users and groups. App-level permissions allow administrators to control who can access certain apps and what documents can be shared.

Hue is maturing quickly and many more features are on their way. Hue will soon have document-level permissions (workflows, queries, and so on), trash functionality, and improvements to the existing editors.

Have any suggestions? Feel free to tell us what you think through [hue-user][17].

 [1]: https://gethue.com
 [2]: http://hadoop.apache.com/
 [3]: http://hadoop.apache.org/
 [4]: http://oozie.apache.org/
 [5]: http://blog.cloudera.com/blog/2012/10/whats-new-in-cdh4-1-hue/
 [6]: http://hive.apache.org/
 [7]: http://hbase.apache.org/
 [8]: http://pig.apache.org/
 [9]: http://flume.apache.org/
 [10]: http://en.wikipedia.org/wiki/SPNEGO
 [11]: http://www.cloudera.com/wp-content/uploads/2012/12/hue11.png
 [12]: http://www.cloudera.com/wp-content/uploads/2012/12/hue21.png
 [13]: http://www.cloudera.com/wp-content/uploads/2012/12/hue31.png
 [14]: http://www.cloudera.com/wp-content/uploads/2012/12/hue4.png
 [15]: http://www.cloudera.com/wp-content/uploads/2012/12/hue5.png
 [16]: http://www.cloudera.com/wp-content/uploads/2012/12/hue6.png
 [17]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
