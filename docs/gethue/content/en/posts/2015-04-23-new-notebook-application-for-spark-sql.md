---
title: 'Beta of new Notebook Application for Spark & SQL'
author: admin
type: post
date: 2015-04-23T13:25:34+00:00
url: /new-notebook-application-for-spark-sql/
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

[Hue 3.8][1] brings a new way to directly submit Spark jobs from a Web UI.

Last year we released [Spark Igniter][2] to enable developers to submit Spark jobs through a Web Interface. While this approach worked, the UX left a lot to be desired. Programs had to implement an interface, be compiled beforehand and YARN support was lacking. We also wanted to add support for Python and Scala, focusing on delivering an interactive and iterative programming experience similar to using a REPL.

[<img src="https://cdn.gethue.com/uploads/2015/04/notebook-1-1024x572.png"  />][3]

&nbsp;

This is for this that we started developing a new [Spark REST Job Server][4] that could provide these missing functionalities. On top of it, we revamped the UI for providing a Python Notebook-like feeling.

Note that this new application is pretty new and labeled as ‘Beta’. This means we recommend trying it out and contributing, but its usage is not officially supported yet as the UX is going to evolve a lot!

This post describes the Web Application part. We are using [Spark 1.3][5] and [Hue master branch][6].

&nbsp;

{{< youtube kIXBL7u_NOk >}}

&nbsp;

Based on a new:

- [Spark REST Job Server][4]
- Notebook Web UI

Supports:

- Scala
- Python
- Java
- SQL
- YARN

&nbsp;

If the Spark app is not visible in the ‘Editor’ menu, you will need to unblacklist it from the [hue.ini][7]:

<pre><code class="bash">[desktop]

app_blacklist=

</code></pre>

**Note:** To override a value in Cloudera Manager, you need to enter verbatim each mini section from below into the Hue [Safety Valve][8]: Hue Service → Configuration → Service-Wide → Advanced → Hue Service Advanced Configuration Snippet (Safety Valve) for hue_safety_valve.ini

&nbsp;

On the same machine as Hue, go in the Hue home:

If using the package installed:

<pre><code class="bash">cd /usr/lib/hue</code></pre>

&nbsp;

**Recommended**

Use Livy Spark Job Server from the Hue master repository instead of CDH (it is currently much more advanced): [see build & start the latest Livy][4]

&nbsp;

If not, use Cloudera Manager:

<pre><code class="bash">cd /opt/cloudera/parcels/CDH/lib/

HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-#

echo $HUE_CONF_DIR

export HUE_CONF_DIR

</code></pre>

<div>
  Where # is substituted by the last number, e.g. hue-HUE_SERVER-65
</div>

Then cd to hue directory And start the [Spark Job Server][4] from the Hue home:

<pre><code class="bash">./build/env/bin/hue livy_server</code></pre>

&nbsp;

You can customize the setup by modifying these properties in the hue.ini:

<pre><code class="bash">[spark]

\# URL of the REST Spark Job Server.

server_url=http://localhost:8090/

\# List of available types of snippets

languages='[{"name": "Scala", "type": "scala"},{"name": "Python", "type": "python"},{"name": "Impala SQL", "type": "impala"},{"name": "Hive SQL", "type": "hive"},{"name": "Text", "type": "text"}]'

\# Uncomment to use the YARN mode

\## livy_server_session_kind=yarn

</code></pre>

&nbsp;

**Next**

This Beta version brings a good set of features, a lot more [is on the way][9]. In the long term, we expect all the query editors (e.g. Pig, DBquery, Phoenix...) to use this common interface. Later, individual snippets could be drag & dropped for making visual dashboards, notebooks could be embedded like in Dropbox or Google docs.

We are also interested in getting feedback on the new  [Spark REST Job Server][4] and see what the community thinks about it (contributions are welcomed ;).

As usual feel free to comment on the [hue-user][10] list or [@gethue][11]!

[1]: https://gethue.com/hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
[2]: https://gethue.com/a-new-spark-web-ui-spark-app/
[3]: https://cdn.gethue.com/uploads/2015/04/notebook-1.png
[4]: https://github.com/cloudera/hue/tree/master/apps/spark/java#welcome-to-livy-the-rest-spark-server
[5]: https://spark.apache.org/releases/spark-release-1-3-0.html
[6]: https://github.com/cloudera/hue
[7]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
[8]: http://www.cloudera.com/content/cloudera/en/documentation/cloudera-manager/v5-1-x/Cloudera-Manager-Managing-Clusters/cm5mc_config_snippet.html
[9]: https://issues.cloudera.org/browse/HUE-2637
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
[11]: https://twitter.com/gethue
