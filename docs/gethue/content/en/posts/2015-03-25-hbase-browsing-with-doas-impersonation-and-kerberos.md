---
title: HBase Browsing with doAs impersonation and Kerberos
author: admin
type: post
date: 2015-03-25T16:22:33+00:00
url: /hbase-browsing-with-doas-impersonation-and-kerberos/
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

Hue comes with an [HBase App][1] that lets you create table, search for rows, read cell content… in just a few clicks. We are now glad to release the last missing piece of security (available in the upcoming Hue 3.8) for making the app production ready!

{{< youtube FGDTGmaxvsM >}}

The HBase app talks to HBase through a proxy server (called [Thrift Server V1][2]) which forwards the commands to HBase. Because Hue stands between the proxy server and the actual user, the proxy server thinks that all the operations (e.g. create a table, scan some data...) are coming from the ‘hue’ user and not the actual Web user. This is obviously not very secure!

In order to secure the HBase app for real we need to:

- make sure that the actual logged in user in Hue performs the operations with his privileges. This is the job of Impersonation.
- make sure that the Hue server only sends these calls. This is the job of Kerberos strong authentication.

&nbsp;

**Note**

We assume that you have installed an HBase Thrift Server in your cluster. If using Cloudera Manager, go to the list of instances of the HBase service and click on ‘Add Role Instances’ and select ‘HBase Thrift Server’.

&nbsp;

## **Impersonation**

HBase can now be configured to [offer impersonation][3] (with or without Kerberos). In our case this means that users can send commands to HBase through Hue without losing the fact that they will be ran under their own credentials (instead of the ‘hue’ user).

First, make sure you have this in your hbase-site.xml:

<pre><code class="xml"><property>

<name>hbase.thrift.support.proxyuser</name>

<value>true</value>

</property>

<property>

<name>hbase.regionserver.thrift.http</name>

<value>true</value>

</property>

</code></pre>

&nbsp;

**Note**

If using Cloudera Manager, this is done by typing ‘thrift’ in the configuration search of the HBase service and checking the first two results.

&nbsp;

Then check in core-site.xml that HBase is authorized to impersonates someone:

<pre><code class="xml"><property>

<name>hadoop.proxyuser.hbase.hosts</name>

<value>*</value>

</property>

<property>

<name>hadoop.proxyuser.hbase.groups</name>

<value>*</value>

</property>

</code></pre>

&nbsp;

And finally check that Hue point to a local config directory of HBase specified in its hue.ini:

<pre><code class="bash">[hbase]

hbase_conf_dir=/etc/hbase/conf

</code></pre>

&nbsp;

**Note**

If you are using Cloudera Manager, you might want to select the HBase Thrift server in the Hue configuration and enter something like this in the Hue Service Advanced Configuration Snippet (Safety Valve) for hue_safety_valve.ini.

<pre><code class="bash">[hbase]

hbase_conf_dir={{HBASE_CONF_DIR}}

</code></pre>

&nbsp;

And that’s it, start the HBase Thrift Server and Hue and you are ready to go!

&nbsp;

## **Security with Kerberos**

Now that the Hue can send commands to the HBase Thrift Server and tell him to execute them as a certain user, we need to make sure that only Hue is allowed to do this. We are using Kerberos in order to strongly authenticate the users to the HBase service. In our case, the HBase Thrift server will accept commands only if they come from the Hue user only.

Make sure that HBase is configured with [Kerberos][4] and that you have this in the hbase-site.xml pointed by Hue:

<!--email_off-->

<pre><code class="xml"><property>

<name>hbase.security.authentication</name>

<value>KERBEROS</value>

</property>

<property>

<name>hbase.thrift.kerberos.principal</name>

<value>hbase/_HOST@ENT.CLOUDERA.COM</value>

</property>

</code></pre>

<!--/email_off-->

&nbsp;

&nbsp;

**Note**

If using Cloudera Manager or regular Thrift without impersonation, make sure to set the "HBase Thrift Authentication" hbase.thrift.security.qop must be set to one of the following:

- auth-conf: authentication, integrity and confidentiality checking
- auth-int: authentication and integrity checking
- auth: authentication only

If using Cloudera Manager, go to "Hbase service > Configuration > Service-Wide / Security : HBase Thrift Authentication " and select one of the following three options.

And similarly to above, make sure that the hue.ini points to a valid directory with hbase-site.xml:

<pre><code class="bash">[hbase]

hbase_conf_dir=/etc/hbase/conf

</code></pre>

or

<pre><code class="bash">[hbase]

hbase_conf_dir={{HBASE_CONF_DIR}}

</code></pre>

&nbsp;

**Note**

If using Impersonation, make sure the HTTP/\_HOST principal is in the keytab of for their HBase Thrift Server.

&nbsp;

Restart HBase and Hue, and they should be all secured now!

&nbsp;

## **Conclusion**

You can now be sure that Hue users can only see or modify what they are allowed to at the HBase level. Hue guarantees that if a user cannot perform a certain operation in the HBase shell, it will exactly the same through Hue (Hue acts like a ‘view’ on top of HBase).

Note that HBase chose to support impersonation through [HTTP Thrift][3], so regular Thrift won’t work when using impersonation. The previous Kerberos support also now makes sense since all the operations are not seeing as coming from the Hue user anymore! More work is on the way to make all these configuration steps only one click.

&nbsp;

Now it is time to play with the [table examples][5] and open-up HBase to all your users!

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2015/03/hbase-1024x525.png" />][6]

&nbsp;

As usual feel free to comment on the [hue-user][7] list or [@gethue][8]!

&nbsp;

**Note**

This error means that the above ‘hadoop.proxyuser.hbase.hosts’ / ‘hadoop.proxyuser.hbase.groups’ properties are not correct:

<pre><code class="bash">Api Error: Error 500 User: hbase is not allowed to impersonate romain HTTP ERROR 500 Problem accessing /.

Reason: User: hbase is not allowed to impersonate bob Caused by:javax.servlet.ServletException:

User: hbase is not allowed to impersonate bob at org.apache.hadoop.hbase.thrift.ThriftHttpServlet.doPost(ThriftHttpServlet.java:117) at

</code></pre>

**Note**

You might now see permission errors like below.

<pre><code class="bash">Api Error: org.apache.hadoop.hbase.security.AccessDeniedException: Insufficient permissions (user=admin, scope=default, action=CREATE)...</code></pre>

This is because either:

- you are using impersonation and your user ‘bob’ does not have enough HBase privileges
- you are not using impersonation and the ‘hue’ user does not have enough HBase privileges

&nbsp;

A quick way to fix this is to just give all the permissions. Obviously this is not recommended for a real setup, instead read more about [HBase Access Control][9]!

<pre><code class="bash">sudo -u hbase hbase shell

hbase(main):004:0> grant 'bob', 'RWC'

</code></pre>

&nbsp;

**Note**

If you are getting a “Api Error: TSocket read 0 bytes”, this is because Hue does not know that the Thrift Server is expecting Thrift HTTP. Double check that Hue points to an hbase-site.xml that contains the hbase.regionserver.thrift.http property set to true.

A temporary hack would be to insert this in the hue.ini:

<pre><code class="bash">[hbase]

use_doas=true

</code></pre>

&nbsp;

**Note**

“Api Error: maximum recursion depth exceeded” means that the HBase Thrift server is not running as an HTTP Kerberos service.

In the latest Hue 3.8 you should now just get a 401 error instead.

&nbsp;

**Note**

buffered transport mode was not tested when using impersonation but might work.

&nbsp;

**Note**

If you are getting this error:

<pre><code class="bash">Caused by: org.apache.hadoop.hbase.thrift.HttpAuthenticationException: Authorization header received from the client is empty.</code></pre>

You are very probably hitting <https://issues.apache.org/jira/browse/HBASE-13069>. Also make sure the HTTP/\_HOST principal is in the keytab of for their HBase Thrift Server. Beware that as a follow-up you might get <https://issues.apache.org/jira/browse/HBASE-14471>.

There is also an issue with **framed** transport which is not supported yet. We recommend to use the **buffered** transport instead.

&nbsp;

[1]: https://gethue.com/the-web-ui-for-hbase-hbase-browser/
[2]: http://wiki.apache.org/hadoop/Hbase/ThriftApi
[3]: https://issues.apache.org/jira/browse/HBASE-13115
[4]: http://www.cloudera.com/content/cloudera/en/documentation/core/latest/topics/cdh_sg_hbase_authentication.html
[5]: https://gethue.com/hadoop-tutorial-how-to-create-example-tables-in-hbase/
[6]: https://cdn.gethue.com/uploads/2015/03/hbase.png
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
[9]: http://hbase.apache.org/0.94/book/hbase.accesscontrol.configuration.html
