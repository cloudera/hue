---
title: 'Move data in & out your Hadoop cluster with the Sqoop UI'
author: admin
type: post
date: 2013-10-04T05:50:00+00:00
url: /move-data-in-out-your-hadoop-cluster-with-the-sqoop/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/63064228790/move-data-in-out-your-hadoop-cluster-with-the-sqoop
tumblr_gethue_id:
  - 63064228790
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

Hi Ice Cream lovers,

Hue, the [open source Big Data UI][1], has a brand new application that enables transferring data between relational databases and [Hadoop][2]. This new application is driven by [Sqoop 2][3] and has several user experience improvements to boot.

{{< youtube Za5zEgLgxK4 >}}

Sqoop is a batch data migration tool for transferring data between traditional databases and Hadoop. The first version of Sqoop is a heavy client that drives and oversees data transfer via MapReduce. In Sqoop 2, the majority of the work was moved to a server that a thin client communicates with. Also, any client can communicate with the Sqoop 2 server over its JSON-REST protocol. Sqoop 2 was chosen instead of its predecessors because of its client-server design.

## Importing from MySQL to HDFS

The following is the canonical import job example sourced from <http://sqoop.apache.org/docs/1.99.2/Sqoop5MinutesDemo.html>. In Hue, this can be done in 3 easy steps:

### Environment

- CDH 4.4 or <span>Hue 3.0.0</span>
- MySQL 5.1

First, make sure that Sqoop2 is up and running and the Hue points to it in its hue.ini:

<pre><code class="bash">###########################################################################

\# Settings to configure Sqoop

###########################################################################

[sqoop]

\# Sqoop server URL

server_url=http://sqoop2.com:12000/sqoop

</code></pre>

### Troubleshooting

If the new job button is not appearing, Sqoop2 is probably not starting. Make sure the MySql or other DB connectors are in the /usr/lib/sqoop/lib directory of Sqoop2. Make sure you have these properties in the Sqoop2 Server configuration:

<pre class="code">org.apache.sqoop.repository.schema.immutable=false
org.apache.sqoop.connector.autoupgrade=true
org.apache.sqoop.framework.autoupgrade=true</pre>

### 1. Create a Connection

In the Sqoop app, the connection manager is available from the “New Job” wizard. To get to the new job wizard, click on “New Job”. There may be a list of connections available if a few have been created before. For the purposes of this demo, we’ll go through the process of creating a new connection. Click “Add a new connection” and fill in the blanks with the data below. Then click save to return to the “New Job” wizard!

<div>
  <pre class="code">Connection Parameter                  Value

Name mysql-connection-demo

JDBC Driver Class com.mysql.jdbc.Driver

JDBC Connection String jdbc:mysql://hue-demo/demo

Username demo

Password demo</pre>

</div>

Connection form values.

### 2. Create a Job

After creating a connection, follow the wizard and fill in the blanks with the information below.

<div>
  <pre class="code">Job Wizard Parameter              Value

Name mysql-import-job-demo

Type IMPORT

Connection mysql-connection-demo

Table name test

Storage Type HDFS

Output format TEXT_FILE

Output directory /tmp/mysql-import-job-demo</pre>

</div>

Job wizard form values.

### 3. Save and Submit the Job

At the end of the Job wizard, click “Save and Run”! The job should automagically start after that and the job dashboard will be displayed. As the job is running, a progress bar below the job listing will be dynamically updated. Links to the HDFS output via the File Browser and Map Reduce logs via Job Browser will be available on the left hand side of the job edit page.

# Sum Up

The new Sqoop application enables batch data migration from a more traditional databases to Hadoop and vice versa through Hue. Using Hue, a user can move data between storage systems in a distributed fashion with the click of a button.

I’d like to send out a big thank you to the Sqoop community for the new client-server design!

Both projects are undergoing heavy development and are welcoming external contributions! Have any suggestions? Feel free to tell us what you think through [hue-user][4] or [@gethue][5]​!

[1]: http://gethue.com
[2]: http://hadoop.apache.org/
[3]: http://sqoop.apache.org/
[4]: http://groups.google.com/a/cloudera.org/group/hue-user
[5]: https://twitter.com/gethue
