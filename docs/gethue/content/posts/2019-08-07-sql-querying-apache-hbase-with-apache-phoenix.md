---
title: SQL querying Apache HBase with Apache Phoenix
author: Hue Team
type: post
date: 2019-08-07T15:52:26+00:00
url: /sql-querying-apache-hbase-with-apache-phoenix/
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
  - Querying
  - Browsing
  - Version 4
  # - Version 4.5

---
[Apache Phoenix][1] is a great addon to extent SQL on top of [Apache HBase][2], the non relational distributed data store. On top of the [HBase Browser][3], now the [Editor][4] provides a more common syntax for querying the data. Note that being a key/value store, the SQL can have different idioms, and the Editor interface still requires some polishing to fully support all the SQL UX capabilities of Hue.

In this first blog post about Phoenix, let&#8217;s follow [Phoenix&#8217;s 15-minute tutorial][5] then query the US_POPULATION table via the Editor:

Hue supports JDBC or SqlAlchemy interfaces as described in the [SQL Connector documentation][6] and we pick SqlAlchemy:

On the Hue host:

<pre><code class="bash">./build/env/bin/pip install pyPhoenix
</code></pre>

Then in the desktop/conf/hue.ini config file section:

<pre><code class="bash">[notebook]
  [[interpreters]]
    [[[phoenix]]]
      name = phoenix
      interface=sqlalchemy
      options='{"url": "phoenix://sql-phoenix.gethue.com:8765/"}'
</code></pre>

Then start the Phoenix queryserver:

<pre><code class="bash">phoenix-queryserver
...
19/07/24 20:55:13 INFO util.log: Logging initialized @1563ms
19/07/24 20:55:13 INFO server.Server: jetty-9.2.z-SNAPSHOT
19/07/24 20:55:14 INFO server.ServerConnector: Started ServerConnector@662b4c69{HTTP/1.1}{0.0.0.0:8765}
19/07/24 20:55:14 INFO server.Server: Started @1793ms
19/07/24 20:55:14 INFO server.HttpServer: Service listening on port 8765.
</code></pre>

And we are ready to query HBase!

<pre><code class="sql">select * from us_population limit 10</code></pre>

<a href="https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png"><img src="https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png" /></a>

<a href="https://cdn.gethue.com/uploads/2019/07/phonix_select_shell.png"><img src="https://cdn.gethue.com/uploads/2019/07/phonix_select_shell.png" /></a>

Notes

**1** Existing HBase tables need to be mapped to views

<pre><code class="bash">0: jdbc:phoenix:&gt; CREATE VIEW if not exists "analytics_demo_view" ( pk VARCHAR PRIMARY KEY, "hours"."01-Total" VARCHAR );
Error: ERROR 505 (42000): Table is read only. (state=42000,code=505)
--&gt;
0: jdbc:phoenix:&gt; CREATE Table if not exists "analytics_demo" ( pk VARCHAR PRIMARY KEY, "hours"."01-Total" VARCHAR );
</code></pre>

**2** Tables are seeing as uppercase by Phoenix. When getting started, it is simpler to just create the table via Phoenix.

<pre><code class="bash">Error: ERROR 1012 (42M03): Table undefined. tableName=ANALYTICS_DEMO (state=42M03,code=1012)
--&gt;
0: jdbc:phoenix:&gt; select * from "analytics_demo" where pk = "domain.0" limit 5;
</code></pre>

**3** Phoenix follows Apache Calcite. Feel free to help improve [the SQL autocomplete][9] support for it.

**4** Skip the semicolon &#8216;;&#8217;

**5** Not tested with security

**6** List of some of the known issues are listed on the [Phoenix SqlAlchemy connector page][10]

&nbsp;

Feel free to read more about Apache Phoenix capabilities in this Cloudera blog post announcing [Phoenix in CDH][11].

<div>
  Any feedback or question? Feel free to comment here or on <a href="https://twitter.com/gethue">@gethue</a>!
</div>

 [1]: https://phoenix.apache.org/
 [2]: https://hbase.apache.org/
 [3]: https://gethue.com/improved-hbase-cell-editor-history/
 [4]: https://gethue.com/sql-editor/
 [5]: https://phoenix.apache.org/Phoenix-in-15-minutes-or-less.html
 [6]: https://docs.gethue.com/latest/administrator/configuration/editor/#phoenix
 [7]: https://cdn.gethue.com/uploads/2019/07/editor_phoenix_select.png
 [8]: https://cdn.gethue.com/uploads/2019/07/phonix_select_shell.png
 [9]: https://docs.gethue.com/latest/developer/parsers/
 [10]: https://github.com/Pirionfr/pyPhoenix
 [11]: https://blog.cloudera.com/blog/2019/07/apache-phoenix-for-cdh/
