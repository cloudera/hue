---
title: Use the Impala App with Sentry for real security
author: admin
type: post
date: 2013-12-16T18:22:24+00:00
url: /use-the-impala-app-with-sentry-for-real-security/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/70206086469/use-the-impala-app-with-sentry-for-real-security
tumblr_gethue_id:
  - 70206086469
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

<p id="docs-internal-guid-2146a2cd-fca2-7325-b82b-68ed6ae64ad9">
  <a href="http://incubator.apache.org/projects/sentry.html">Apache Sentry</a> is the new way to provide security (e.g. privileges on SQL statements SELECT, CREATE…) when querying data in Hadoop. <a href="http://impala.io/">Impala</a> offers <a href="http://gethue.tumblr.com/post/62452792255/fast-sql-with-the-impala-query-editor">fast SQL</a> for Apache Hadoop and can leverage Sentry. Here is how to use configure it:
</p>

First enable impersonation in the [hue.ini][1] that way permissions will be checked against the current user and not ‘hue’ which acts as a proxy:

<pre><code class="bash">[impala]

impersonation_enabled=True

</code></pre>

Then you might hit this error:

<pre>User 'hue' is not authorized to impersonate 'romain'. User impersonation is disabled.</pre>

This is because Hue is not authorized to be a proxy. To fix it, startup Impala with this flag:

<pre><code class="bash">-authorized_proxy_user_config=hue=*</code></pre>

Note: if you use Cloudera Manager, add it to the ‘Impalad Command Line Argument Safety Valve’

&nbsp;

And that’s it! You can now benefit from real security similar to [Hive][2]! As usual feel free to comment on the [hue-user][3] list or [@gethue][4]!

&nbsp;

Note: if you are on CDH4/Hue 2.x, make sure that Hue is configured to talk to Impala with the HiveServer2 API:

<pre><code class="bash">[impala]

\# Host of the Impala Server (one of the Impalad)

server_host=nightly-1.ent.cloudera.com

\# The backend to contact for queries/metadata requests.

\# Choices are 'beeswax' or 'hiveserver2' (default).

\# 'hiveserver2' supports log, progress information, query cancellation

\# 'beeswax' requires Beeswax to run for proxying the metadata requests

server_interface=hiveserver2

\# Port of the Impala Server

\# Default is 21050 as HiveServer2 Thrift interface is the default.

\# Use 21000 when using Beeswax Thrift interface.

server_port=21050

\# Kerberos principal

\## impala_principal=impala/hostname.foo.com

impersonation_enabled=True

</code></pre>

Note: to give a concrete idea, here is video demo that shows the end user interaction in the UI (it is using the <a href="https://gethue.com/hadoop-tutorial-hive-query-editor-with-hiveserver2-and/" target="_blank" rel="noopener noreferrer">Hive App</a> but you will get the exact same result with the Impala app)

{{< youtube -Py11X0G6Hs >}}

[1]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini
[2]: http://gethue.tumblr.com/post/64916325309/hadoop-tutorial-hive-query-editor-with-hiveserver2-and
[3]: http://groups.google.com/a/cloudera.org/group/hue-user
[4]: https://twitter.com/gethue
