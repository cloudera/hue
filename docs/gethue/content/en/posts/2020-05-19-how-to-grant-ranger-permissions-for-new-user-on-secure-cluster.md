---
title: How to grant Ranger permissions for a new user on a Secure Cluster
author: Weixia Xu
type: post
date: 2020-05-19T00:00:00+00:00
url: /blog/how-to-grant-ranger-permissions-for-a-new-user/
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
#  - Version 4.8

---
Hello, Hue administrators,

The [Apache Ranger™](https://ranger.apache.org/)is a framework to enable, monitor and manage comprehensive data security
 across the Hadoop platform.

Hue integrates with Ranger since [Hue4.6](https://gethue.com/hue-4-6-and-its-improvements-are-out/), on any secure cluster with Ranger installed, the user has to have proper
 permissions to operate on the data to avoid following permission warning.

![missing-ranger-permission.png](https://cdn.gethue.com/uploads/2020/05/missing-ranger-permission.png)

Here let's show the detailed steps to grant permission for any new user through CM UI.

## Steps
1. On any CM managed cluster, you can navigate to Ranger service, note down the 'Ranger Usersync' host on "Instances" tab,
 then open 'Ranger Admin Web UI'

![ranger-usersync-host-and-admin-webui.png](https://cdn.gethue.com/uploads/2020/05/ranger-usersync-host-and-admin-webui.png)

2. open a terminal and ssh to your ranger usersync host which you noted down at Step 1;

    ssh root@weixia-1.domain.site
    useradd weixia
    passwd weixia

3. On Ranger admin webui page: https://weixia-1.domain.site:6182/index.html#!/policymanager/resource, click on "Edit"
 button besides the "Hadoop SQL":

![edit-ranger-policymanager-hadoop-sql.png](https://cdn.gethue.com/uploads/2020/05/edit-ranger-policymanager-hadoop-sql.png)

a. if you want to give new user permission on all databases, add your user on the existing policy: "all-database, table, column"
![grant-user-permission-to-all.png](https://cdn.gethue.com/uploads/2020/05/grant-user-permission-to-all.png)

b. if you want to give new user only to specific database say 'testdb', you can create new policy as following,
choose permission as you desired:
![create-new-policy-for-testdb-access-only.png](https://cdn.gethue.com/uploads/2020/05/create-new-policy-for-testdb-access-only.png)

4. Save the change.

Navigate to Hue WebUI, now your new user should be able to run any query on any entities as granted in the policy.
![new-user-can-run-query-on-tables.png](https://cdn.gethue.com/uploads/2020/05/new-user-can-run-query-on-tables.png)

You can do the same for group permission as well.

Any feedback or questions? Feel free to comment here or on the [Forum](https://discourse.gethue.com/) or
[@gethue](https://twitter.com/gethue) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Weixia Xu from the Hue Team
