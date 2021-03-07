---
title: Manually configure Hue in HDP
author: admin
type: post
date: 2019-03-02T06:29:46+00:00
url: /configure-ambari-hdp-with-hue/
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
sf_author_info:
  - 1
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4

---
Hello Big Data users,

if you have an Ambari managed HDP cluster, here is a guide of how test the latest Hue. Note that the guide focuses on the SQL Editor and HDFS Browser only and assumes a non-secure cluster setup.

**Step 1:**

On any host other than Ambari server, run following commands to [compile][1] the latest Hue and its dependencies:

<pre><code class="bash">

yum install -y git

git clone https://github.com/cloudera/hue.git

sudo yum install -y ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap-devel python-devel sqlite-devel gmp-devel libtidy maven

</code></pre>

Build:

<pre><code class="bash">

cd hue

sudo make apps

</code></pre>

**Step 2:**

Update Ambari Configurations

1. Go to `HDFS --> Configs --> Advanced` Scroll down to expand “Custom core-site”, then click on “Add Property…” to add “hadoop.proxyuser.hue.hosts:\*” and “hadoop.proxyuser.hue.groups:\*” then “Save” as following.[<img src="https://cdn.gethue.com/uploads/2019/02/Screen-Shot-2019-02-27-at-3.05.28-PM.png"/>][2]

2. On Ambari UI check `YARN --> Config --> Advanced --> Advanced` yarn-site yarn.resourcemanager.webapp.address and add it in hue.ini

[<img src="https://cdn.gethue.com/uploads/2019/02/Screen-Shot-2019-02-27-at-3.10.39-PM.png"/>][3]

3. On MySql server host usually host-1 create the Hue database:

<pre><code class="bash">

ssh root@hue-1.example.com

mysql

create user 'hueuser'@'localhost' identified by 'huepassword';

create database huedb default character set utf8 default collate utf8_general_ci;

grant all on huedb.* to 'hueuser'@'%' identified by 'huepassword';

exit;

</code></pre>

4. On hue host update the hue.ini with following values

<pre><code class="bash">

ssh root@hue-2.example.com

vim ~/hue/desktop/conf/pseudo-distributed.ini

</code></pre>

<pre>hue.ini</pre>

<pre><code class="bash">

[beeswax]

max_number_of_sessions=2

</code></pre>

<pre><code class="bash">

[hadoop]

webhdfs_url=http://hue-1.example.com:50070/webhdfs/v1

resourcemanager_api_url=http://hue-1.example.com:8088

</code></pre>

<pre>And run:</pre>

<pre><code class="bash">

cd hue build/env/bin/hue syncdb

build/env/bin/hue migrate

build/env/bin/hue runcpserver

</code></pre>

5. Go to the [hue-2.example.com:8888][4] to explore more and the [configuration page][5] for adding more components!

[<img src="https://cdn.gethue.com/uploads/2019/02/HiveEditor.png"/>][6]

[<img src="https://cdn.gethue.com/uploads/2019/02/fileBrowser.png"/>][7]

<span style="font-weight: 400;">As always please feel free to comment and send feedback on the </span>[<span style="font-weight: 400;">hue-user</span>][8] <span style="font-weight: 400;">list or </span>[<span style="font-weight: 400;">@gethue</span>][9]<span style="font-weight: 400;">!</span>

 [1]: http://cloudera.github.io/hue/latest/admin-manual/manual.html
 [2]: https://cdn.gethue.com/uploads/2019/02/Screen-Shot-2019-02-27-at-3.05.28-PM.png
 [3]: https://cdn.gethue.com/uploads/2019/02/Screen-Shot-2019-02-27-at-3.10.39-PM.png
 [4]: http://hue-2.example.com:8888
 [5]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [6]: https://cdn.gethue.com/uploads/2019/02/HiveEditor.png
 [7]: https://cdn.gethue.com/uploads/2019/02/fileBrowser.png
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user
 [9]: https://twitter.com/gethue
