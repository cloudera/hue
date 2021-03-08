---
title: How to use Hue with Hive and Impala configured with LDAP authentication and SSL
author: admin
type: post
date: 2014-12-12T17:26:28+00:00
url: /how-to-use-hue-with-hive-and-impala-configured-with-ldap-authentication-and-ssl/
sf_no_breadcrumbs:
  - 1
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
We previously showed in detail how to use [SSL encryption][1] with the Impala or Hive Editors. Here is now a step by step guide about how to use LDAP authentication instead of no authentication or Kerberos.

Note: this requires [Hue 3.7][2] or CDH5.2

1.

HiveServer2 had SSL enabled so Hive Editor could not connect to HiveServer2. HiveServer2 logs showed SSL errors indicating that it received plaintext (good hint at the cause)

Solved by adding this to the Hue Safety Valve:

(validate was false since their certificates used wildcards and this caused other errors)

Note: If not using SSL, you will hit this bug: [HUE-2484][3]

2.

The same Hue behavior occurred after making the change, but now the HiveServer2 log showed authentication failure due to err=49

So, we added the following to the Hue Safety Valve:

<pre><code class="bash">

[beeswax]

[[ssl]]

\## Path to Certificate Authority certificates.

cacerts=/etc/hue/cacerts.pem

\## Choose whether Hue should validate certificates received from the server.

validate=false

</code></pre>

or

<pre><code class="bash">

[impala]

[[ssl]]

\## SSL communication enabled for this server.

enabled=false

\## Path to Certificate Authority certificates.

cacerts=/etc/hue/cacerts.pem

\## Choose whether Hue should validate certificates received from the server.

validate=false

</code></pre>

3.

Hue still showed the same behavior. HiveServer2 logs showed:

<pre><code class="bash">

<HUE_LDAP_USERNAME> is not allowed to impersonate bob

</code></pre>

We solved this by adding the following to the HDFS > Service-Wide ->Advanced>Safety Valve for core-site.xml.

<pre><code class="xml">

<property>

<name>hadoop.proxyuser.<HUE_LDAP_USERNAME>.hosts</name>

<value>*</value>

</property>

<property>

<name>hadoop.proxyuser.<HUE_LDAP_USERNAME>.groups</name>

<value>*</value>

</property>

</code></pre>

4.

After this, the default database was displayed, but we could not do a show tables; or anything else. Beeline had the same behavior.

We did a grant for the group to which the user who was attempting the Hive actions and then that problem went away.

All queries were working and Hue is querying Hive/Impala and returning results!

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-impala-charts-1024x573.png" />][4]

&nbsp;

As usual feel free to comment and send feedback on the [hue-user][5] list or [@gethue][6]!

 [1]: https://gethue.com/hadoop-tutorial-ssl-encryption-between-hue-and-hive/
 [2]: https://gethue.com/hue-3-7-with-sentry-app-and-new-search-widgets-are-out/
 [3]: https://issues.cloudera.org/browse/HUE-2484
 [4]: https://cdn.gethue.com/uploads/2014/10/hue-impala-charts.png
 [5]: http://groups.google.com/a/cloudera.org/group/hue-user
 [6]: https://twitter.com/gethue
