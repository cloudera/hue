---
title: How to create example tables in HBase
author: admin
type: post
date: 2013-08-13T21:40:00+00:00
url: /hadoop-tutorial-how-to-create-example-tables-in-hbase/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/58181985680/hadoop-tutorial-how-to-create-example-tables-in-hbase
tumblr_gethue_id:
  - 58181985680
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
ampforwp-amp-on-off:
  - default
categories:
---

<p id="docs-internal-guid-7c74e5e3-7999-5a0b-77ef-ac77803cb105">
  <a href="http://gethue.tumblr.com/post/55581863077/hue-2-5-and-its-hbase-app-is-out">Hue</a> brings another new app for making Apache Hadoop easier to use: HBase Browser. <a href="http://hbase.apache.org/">Apache HBase</a> is the main keyvalue datastore for Hadoop. This post is the first episode describing the new user experience brought by the app. We will start by describing how to create some sample tables with various HBase schemas.
</p>

To help getting started with HBase, Hue now comes directly with theses examples! Just got to Hue on the [/about/][1] page and on Step 2 click on HBase and Hue will install them for you:

<p style="text-align: center;">
  <a href="https://cdn.gethue.com/uploads/2013/08/Screenshot-from-2014-04-09-082900.png"><img class=" wp-image-1116 aligncenter" src="https://cdn.gethue.com/uploads/2013/08/Screenshot-from-2014-04-09-082900.png" alt="Screenshot from 2014-04-09 08:29:00" width="484" height="419"  /></a>
</p>

If you want to see the HBase Browser demo, jump [episode 2][2]!

{{< youtube eGcj-o90rvI >}}

# Tutorial

When building the new HBase Browser, we wanted to test the app against various HBase tables. It happened to be difficult to find some ready to play with schema and data to load. Hence, base on the most common uses cases, we created our own HBase schemas and decided to share them in order to help anybody wanting to start with HBase.

This how-to describes how to create a very simple table that counts the daily number of votes for certain candidates and get you warmed-up. Then part 2 focuses on creating a HBase table  with lot of columns and part 3 about inserting and visualizing binary data.

# Setup

The HBase Browser application is tailored for quickly browsing huge tables and accessing any content. You can also create new tables, add data, modify existing cells and filter data with the autocompleting search bar.

The first step is to install HBase in your Hadoop cluster. We recommend to use the CDH [packages][3]. HBase Browser requires the [Thrift 1 service][4] to be started.

Then, grab the app from a special tarball [release][5]{.trackLink} of Hue or get the latest and slickest version from the [nightly ‘hue’ package][6]. CDH 4.4 (target date early September) will bring a stable v1. After the installation, if HBase master is not running on the same host as Hue, have the app pointing to it by updating the [hue.ini][7] and restarting Hue.

Then go to <http://127.0.0.1:8888/hbase/> to check that all is setup correctly! We show in the video how to create a table and add some columns in just a few clicks. In the next steps, we are showing how to create and populate a real life example table.

The sample data and scripts are published on [github][8]. In a terminal, use [git][9] to retrieve the repository:

<pre class="code">cd /tmp
git clone <a href="https://github.com/romainr/hadoop-tutorials-examples.git">https://github.com/romainr/hadoop-tutorials-examples.git</a>
cd hbase-tables</pre>

# Analytics table

The goals of this data is to show the search and smart layout of HBase Browser.

This table contains more than 1000 columns of text. The idea is to have counters for 3 Web domains of 3 countries for each hour of the day. The data is then aggregated by day and for all the countries.

<img src="https://lh6.googleusercontent.com/6ETWVbvV06zSHbrDglMlqaMfJB-HMrHpJYF27xTFbbQB88jdKRSlVCIjkYl0EYRFFm31iCp-PN-7q7_cNBKQd_820Cqkv674V7e9MPV00N_T_nGm7jv2R_O8" alt="image" width="800px;" height="88px;" />

Schema of the table

How to create the HBase table and insert some data:

1. Generate column names and data with [create_schemas.py][10]. Run it with ./create_schemas.py
2. Upload the date data /tmp/hbase-analytics.tsv to HDFS with File Browser
3. In HBase Browser create a ‘analytics’ table with 3 column families ‘hour’, ‘day’, ‘total’
4. Load the data into the analytics table with the [HBase bulk import command][11].

It will trigger a MapReduce job and display the [progress][12] of the import.

That’s it! Go open the analytics table in [HBase Browser][13]!

# Binary table

This second tables focus on big data cells, various formats, demonstrating the preview and editing of data within HBase Browser.

We are re-using the app API for inserting into HBase some cells of various content types, e.g. text, json, pictures, binary…

1. First create a table ‘events’ with a column family ‘doc’.
2. Then cd in the root of Hue
3. cd /usr/share/hue
4. /opt/cloudera/parcels/CDH-4.X/share/hue (if using parcels)

And start the Hue shell build/env/bin/hue shell and type the content of [locad_binary.py:][14]

Load the HBase API and insert some text data:

<pre class="code">from hbase.api import HbaseApi

HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:txt': 'Hue is awesome!'})
HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:json': '{"user": "hue", "coolness": "extra"}'})
HbaseApi().putRow('Cluster', 'events', 'hue-20130802', {'doc:version': 'I like HBase'})
HbaseApi().putRow('Cluster', 'events', 'hue-20130802', {'doc:version': 'I LOVE HBase'})</pre>

Then insert a picture, and HTML page and a PDF:

<pre class="code">root='/tmp/hadoop-tutorials-examples'

HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:img': open(root + '/hbase-tables/data/hue-logo.png', "rb").read()})
HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:html': open(root + '/hbase-tables/data/gethue.com.html', "rb").read()})
HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:pdf': open(root + '/hbase-tables/data/gethue.pdf', "rb").read()})</pre>

Notice that the column names do not matter for the type detection. The go look at the [events][15] table and play around!

# Conclusion

These two schemas and data enable the user to easily get started with HBase. This first version of HBase Browser brings a new way to quickly explore and search for some rows and columns. New versions will support bulk loads and upload in order to completely free the user from the command line.

The new HBase Browser app will be demo-ed on these two tables in the upcoming blog posts, so stay tuned!

[1]: http://127.0.0.1:8888/about/
[2]: https://gethue.com/the-web-ui-for-hbase-hbase-browser/
[3]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_20_2.html
[4]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_20_5.html#topic_20_5_4_unique_1
[5]: https://cdn.gethue.com/downloads/releases/hbase/hue-hbase-2.5.0.tgz
[6]: http://nightly.cloudera.com/cdh4/
[7]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L505
[8]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/hbase-tables
[9]: http://git-scm.com/
[10]: https://raw.github.com/romainr/hadoop-tutorials-examples/master/hbase-tables/create_schemas.py
[11]: https://raw.github.com/romainr/hadoop-tutorials-examples/master/hbase-tables/load_data.sh
[12]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hbase-tables/load_data.log
[13]: http://127.0.0.1:8888/hbase/#Cluster/analytics
[14]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hbase-tables/load_binary.py
[15]: http://127.0.0.1:8888/hbase/#Cluster/events
