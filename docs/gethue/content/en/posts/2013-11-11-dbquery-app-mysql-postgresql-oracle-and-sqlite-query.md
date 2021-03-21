---
title: 'DBQuery App: MySQL, PostgreSQL, Oracle and Sqlite Query Editors'
author: admin
type: post
date: 2013-11-11T08:03:00+00:00
url: /dbquery-app-mysql-postgresql-oracle-and-sqlite-query/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/66661074125/dbquery-app-mysql-postgresql-oracle-and-sqlite-query
tumblr_gethue_id:
  - 66661074125
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

[In Thailand][1], a brand new application that enables viewing data in MySQL, PostgreSQL, Oracle and Sqlite has been committed.

Inspired from the Beeswax application, it allows you to query a relational database and view it in a table.

{{< youtube 2-Vh8ITDLvc >}}

Example of configuration in hue.ini:

<pre><code class="bash">[librdbms]

\# The RDBMS app can have any number of databases configured in the databases

\# section. A database is known by its section name

\# (IE sqlite, mysql, psql, and oracle in the list below).

[[databases]]

\# sqlite configuration.

[[[sqlite]]]

\# Name to show in the UI.

nice_name=SQLite

\# For SQLite, name defines the path to the database.

name=/home/romain/projects/hue/desktop/desktop.db

\# Database backend to use.

engine=sqlite

\# mysql, oracle, or postgresql configuration.

[[[mysql]]]

\# Name to show in the UI.

nice_name="My SQL DB"

\# For MySQL and PostgreSQL, name is the name of the database.

\# For Oracle, Name is instance of the Oracle server. For express edition

\# this is 'xe' by default.

#name=hue

\# Database backend to use. This can be:

\# 1. mysql

\# 2. postgresql

\# 3. oracle

engine=mysql

\# IP or hostname of the database to connect to.

\## host=localhost

\# Port the database server is listening to. Defaults are:

\# 1. MySQL: 3306

\# 2. PostgreSQL: 5432

\# 3. Oracle Express Edition: 1521

\## port=3306

\# Username to authenticate with when connecting to the database.

user=root

\# Password matching the username to authenticate with when

\# connecting to the database.

password=root

</code></pre>

**Note**: you can look at the [Hue database guide][2] for installing the DB connectors

&nbsp;

[1]: http://gethue.tumblr.com/post/66661140648/hue-team-retreat-thailand
[2]: http://www.cloudera.com/content/cloudera/en/documentation/core/latest/topics/cdh_ig_hue_database.html
