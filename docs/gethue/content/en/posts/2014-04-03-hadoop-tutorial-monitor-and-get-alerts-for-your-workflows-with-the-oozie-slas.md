---
title: Monitor and get alerts for your workflows with the Oozie SLAs
author: admin
type: post
date: 2014-04-03T20:40:11+00:00
url: /hadoop-tutorial-monitor-and-get-alerts-for-your-workflows-with-the-oozie-slas/
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

<p id="docs-internal-guid-99e4a41b-294c-1afb-46e2-ab6223f97bad" dir="ltr">
  Hue now makes <a href="http://oozie.apache.org/docs/4.0.0/DG_SLAMonitoring.html">Oozie SLAs</a> easy to use! With SLAs, you can automatically be alerted when some workflows are not done within a certain window of time. Oozie SLAs have been improved a lot in Oozie 4, hence this new feature requires Oozie 4.x.
</p>

{{< youtube 3QBGF1tTEgQ >}}

SLAs can be setup in the Editor in the advanced tabs of:

<li dir="ltr">
  <p dir="ltr">
    Workflow properties
  </p>
</li>

<li dir="ltr">
  <p dir="ltr">
    Workflow action properties
  </p>
</li>

<li dir="ltr">
  <p dir="ltr">
    Coordinator properties
  </p>
</li>

<p dir="ltr">
  SLAs can be visualized In the Dashboard:
</p>

<li dir="ltr">
  <p dir="ltr">
    New main SLA tab for searching and graphing
  </p>
</li>

<li dir="ltr">
  <p dir="ltr">
    Individual SLA tab for single workflow or coordinator
  </p>
</li>

<p dir="ltr">
  We do not cover <a href="http://oozie.apache.org/docs/4.0.0/AG_Install.html#Notifications_Configuration">setup of JMS notifications</a> here. <a href="http://oozie.apache.org/docs/4.0.0/DG_JMSNotifications.html">JMS</a> enables clients to be alerted in real time of the notifications (instead of pooling like in this tutorial). With Hue, you can visualize the success of your job in a timelime and setup email-notification in case of alerts.
</p>

<p dir="ltr">
  As usual feel free to comment on the<a href="http://groups.google.com/a/cloudera.org/group/hue-user"> hue-user</a> list or<a href="https://twitter.com/gethue"> @gethue</a>!
</p>

<p dir="ltr">
  <strong>Note</strong><br /> How to enable SLA in Oozie itself?
</p>

<p dir="ltr">
  First make sure you are using Oozie 4. If you need to upgrade from Oozie 3, don’t forget to update the Oozie sharelib with:
</p>

<pre><code class="bash">

sudo -u oozie /usr/lib/oozie/bin/oozie-setup.sh sharelib create -fs hdfs://localhost:8020 -locallib /usr/lib/oozie/oozie-sharelib-yarn.tar.gz

</code></pre>

<p dir="ltr">
  If for some reason you need to reset the Oozie DB, delete it and recreate it with:
</p>

<pre><code class="bash">

sudo -u oozie /usr/lib/oozie/bin/ooziedb.sh create -sqlfile oozie.sql -run

</code></pre>

<p dir="ltr">
  <strong>Note</strong><br /> In order to avoid the exception below, you should not have the SLA properties in oozie-site.xml.
</p>

<pre><code class="java">

Exception in thread "main" java.lang.NoClassDefFoundError: javax/mail/MessagingException

at java.lang.Class.forName0(Native Method)

at java.lang.Class.forName(Class.java:270)

</code></pre>

<p dir="ltr">
  Then open oozie-site.xml and add these <a href="http://oozie.apache.org/docs/4.0.0/AG_Install.html#Notifications_Configuration">properties</a> and restart Oozie:
</p>

<pre><code class="xml">

<property>

<name>oozie.services.ext</name>

<value>

org.apache.oozie.service.EventHandlerService,

org.apache.oozie.sla.service.SLAService

</value>

</property>

<property>

<name>oozie.service.EventHandlerService.event.listeners</name>

<value>

org.apache.oozie.sla.listener.SLAJobEventListener,

org.apache.oozie.sla.listener.SLAEmailEventListener

</value>

</property>

</code></pre>
