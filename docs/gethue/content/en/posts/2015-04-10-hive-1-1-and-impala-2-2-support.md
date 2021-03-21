---
title: Hive 1.1 and Impala 2.2 support
author: admin
type: post
date: 2015-04-10T15:29:43+00:00
url: /hive-1-1-and-impala-2-2-support/
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
[Hive][1] did a big jump by finally graduating to its 1.0 version version. It is even 1.1 now (equivalent to 0.14). Hue’s Hive and [Impala][2] Editor have been updated to take advantages of a series of their new features.

[<img src="https://cdn.gethue.com/uploads/2015/03/hive-editor-map-1024x529.png" />][3]

This release finally unifies the HiveServer2 API. All its API calls (e.g. getting the logs of a query) now belong to the upstream version. This makes Hue 100% compatible with any Hive 1.1+ version going forward and will solve a lot of integration headaches.

&nbsp;

Another advantage is the support of the new columnar format which makes the fetching of result set data much faster.

&nbsp;

If you are looking at the SSL configuration, check this [previous blog post][4].

&nbsp;

One more feature landing in Hue 3.8 that could interest some users is the Thrift HTTP support. We got this feature in for improving the interaction of the [HBase App][5] but can re-use it for free for HiveServer2.

&nbsp;

By configure HiveServer2 in [HTTP mode][6]:

<pre><code class="xml"><property>

<name>hive.server2.transport.mode</name>

<value>http</value>

</property>

</code></pre>

&nbsp;

Hue will automatically pick it up if [it points][7] to a good hive-site.xml.

&nbsp;

Anothe feature is the development of a Notebook UI (currently a beta version) that let’s you type SQL. You can know do quick prototyping and graphing!

[<img src="https://cdn.gethue.com/uploads/2015/03/sql-notebook-1024x513.png" />][8]

&nbsp;

**Next!**

Coming up next are the support of HiveServer2 High Availability (HA) in order to support transparently rolling upgrades or server crashes. The new Notebook App is in heavy development and will share the same UI for the [SQL editors][9].

More user friendliness is also on the way, with a visual display of table statistics and the autocomplete of nested types!

&nbsp;

As usual feel free to comment on the [hue-user][10] list or [@gethue][11]!

 [1]: https://hive.apache.org/
 [2]: http://impala.io/
 [3]: https://cdn.gethue.com/uploads/2015/03/hive-editor-map.png
 [4]: https://gethue.com/how-to-use-hue-with-hive-and-impala-configured-with-ldap-authentication-and-ssl/
 [5]: https://gethue.com/hbase-browsing-with-doas-impersonation-and-kerberos/
 [6]: https://cwiki.apache.org/confluence/display/Hive/Setting+Up+HiveServer2#SettingUpHiveServer2-RunninginHTTPmode
 [7]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [8]: https://cdn.gethue.com/uploads/2015/03/sql-notebook.png
 [9]: https://issues.cloudera.org/browse/HUE-2179
 [10]: http://groups.google.com/a/cloudera.org/group/hue-user
 [11]: https://twitter.com/gethue
