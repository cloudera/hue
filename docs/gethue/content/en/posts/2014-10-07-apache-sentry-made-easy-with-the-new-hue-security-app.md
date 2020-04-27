---
title: Apache Sentry made easy with the new Hue Security App
author: admin
type: post
date: 2014-10-07T20:24:42+00:00
url: /apache-sentry-made-easy-with-the-new-hue-security-app/
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

Hi Hadoop Sheriffs,

In order to support the growth of the [Apache Sentry][1] project and make it easier to secure your cluster, a new app was added into Hue. Sentry privileges determine which [Hive / Impala][2] databases and tables a user can see or modify. The Security App let’s you create/edit/delete Roles and Privileges directly from your browser (there is no sentry-provider.ini file to edit anymore).

Here is a video showing how the app works:

{{< youtube ZwZWA_nBGDs >}}

Main features:

- Bulk edit roles and privileges
- Visualize/edit roles and privileges on a database tree
- WITH GRANT OPTION support
- Impersonate a user to see which databases and table he can see

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-sentry-1024x541.png" />][3]

To have Hue point to a Sentry service and another host, modify these [hue.ini][4] properties:

<pre><code class="bash">[libsentry]

 # Hostname or IP of server.

 hostname=localhost

 # Port the sentry service is running on.

 port=8038

 # Sentry configuration directory, where sentry-site.xml is located.

 sentry_conf_dir=/etc/sentry/conf

</code></pre>

Hue will also automatically pick up the server name of HiveServer2 from the sentry-site.xml file of /etc/hive/conf.

&nbsp;

And that’s it, you can know specify who can see/do what directly in a Web UI! The app sits on top of the standard Sentry API and so it fully compatible with Sentry. Next planned features will bring [Solr Collections][5], [HBase][6] privilege management as well as more bulk operations and a tighter integration with HDFS.

As usual, feel free to continue to send us questions and feedback on the [hue-user][7] list or [@gethue][8]!

<span id="howto"></span>

<span style="color: #ff0000;"><strong>Notes</strong></span>

To be able to edit roles and privileges in Hue, the logged-in Hue user needs to belong to a **group in Hue** that is also an **admin group in Sentry** (whatever UserGroupMapping Sentry is using, the corresponding groups must exist in Hue or need to be entered manually). For example, our 'hive' user belongs to a 'hive' group in Hue and also to a 'hive' group in Sentry:

<pre><code class="xml"><property>

  <name>sentry.service.admin.group</name>

  <value>hive,impala,hue</value>

</property>

</code></pre>

&nbsp;

**Notes**

- Create a role in the Sentry app through Hue
- Grant privileges to that role such that the role can see the database in the Sentry app
- Create a group in Hue with the same name as the role in Sentry
- Grant that role to a user in Hue
- Ensure that the user in Hue has an equivalent O/S level
- Ensure a user has an O/S level account on all hosts and that user is part of a group with the same name as the group in Hue (this assumes that the default ShellBasedUnixGroupsMapping is set for HDFS in CM)

&nbsp;

**Notes**

We are using CDH5.2+ with Kerberos MIT and Sentry configured. The app also works in non secure mode.

Our users are:

- hive (admin) belongs to the hive group
- user1_1 belongs to the user_group1 group
- user2_1 belongs to the user_group2 group

We [synced the Unix users/groups][9] into Hue with these commands:

<pre><code class="bash">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'\`"

build/env/bin/hue useradmin_sync_with_unix -min-uid=1000

</code></pre>

If using the package version and has the CDH repository register, install sentry with:

<pre><code class="bash">sudo apt-get install sentry

</code></pre>

If using Kerberos, make sure ‘hue’ is allowed to connect to Sentry in /etc/sentry/conf/sentry-site.xml:

<pre><code class="xml"><property>

  <name>sentry.service.allow.connect</name>

  <value>impala,hive,solr,hue</value>

</property>

</code></pre>

Here is an example of sentry-site.xml

Here is an example of sentry-site.xml

<pre><code class="xml"><?xml version="1.0" encoding="UTF-8"?>

<configuration>

<property>

<name>sentry.service.security.mode</name>

<value>none</value>

</property>

<property>

<name>sentry.service.admin.group</name>

<value>hive,romain</value>

</property>

<property>

<name>sentry.service.allow.connect</name>

<value>impala,hive,solr</value>

</property>

<property>

<name>sentry.store.jdbc.url</name>

<value>jdbc:derby:;databaseName=sentry_store_db;create=true</value>

</property>

<property>

<name>sentry.store.jdbc.driver</name>

<value>org.apache.derby.jdbc.EmbeddedDriver</value>

</property>

<property>

<name>sentry.store.jdbc.password</name>

<value>aaa</value>

</property>

</configuration>

</code></pre>

For testing purposes, here is how to create the initial Sentry database:

<pre><code class="bash">romain@runreal:~/projects/hue$ sentry -command schema-tool -initSchema -conffile /etc/sentry/conf/sentry-site.xml -dbType derby

</code></pre>

And start the service:

<pre><code class="bash">sentry -command service  -conffile /etc/sentry/conf/sentry-site.xml

</code></pre>

**Note**

In Sentry 1.5, you will need to specify a ‘entry.store.jdbc.password’ property in the sentry-site.xml, if not you will get:

<pre><code class="bash">Caused by: org.apache.sentry.provider.db.service.thrift.SentryConfigurationException: Error reading sentry.store.jdbc.password

</code></pre>

[1]: http://sentry.incubator.apache.org/
[2]: https://gethue.com/hadoop-tutorial-new-impala-and-hive-editors/
[3]: https://cdn.gethue.com/uploads/2014/10/hue-sentry.png
[4]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
[5]: https://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr
[6]: https://gethue.com/the-web-ui-for-hbase-hbase-browser/
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
[9]: https://gethue.com/hadoop-tutorial-how-to-integrate-unix-users-and-groups/
