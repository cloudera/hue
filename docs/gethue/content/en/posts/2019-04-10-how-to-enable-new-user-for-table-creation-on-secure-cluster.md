---
title: How to enable new user and create Hive tables on a Kerberized secure cluster with Apache Sentry
author: admin
type: post
date: 2019-04-10T20:41:49+00:00
url: /how-to-enable-new-user-for-table-creation-on-secure-cluster/
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
  # - Version 4.5

---
It can be tricky to grant a new user proper permissions on a secure cluster, let's walk through the steps to enable any new user for table creation on a kerberized cluster. Depends on your cluster size, creating user and group on each node can be tedious. Here we use pssh (Parallel ssh) for this task.

**1. Install the tool and prepare a file which contains all your hosts.**

For Mac user:

<pre><code class="bash">$ brew install pssh</code></pre>

For Debian or Ubuntu user:

<pre><code class="bash">
$ sudo apt-get install pssh
</code></pre>

<pre><code class="bash">
$ cat ~/Documents/nodeshue.txt

  hue-1.test.cloudera.com
  hue-2.test.cloudera.com
  hue-3.test.cloudera.com
  hue-4.test.cloudera.com

</code></pre>

**2. Run follow commands to create user: t1 and group: grp1 on your cluster:**

<pre><code class="bash">

$ pssh -h ~/Documents/nodeshue.txt -i useradd t1

[1] 13:58:48 [SUCCESS] hue-1.test.cloudera.com

[2] 13:58:48 [SUCCESS] hue-2.test.cloudera.com

[3] 13:58:48 [SUCCESS] hue-3.test.cloudera.com

[4] 13:58:48 [SUCCESS] hue-4.test.cloudera.com

$ pssh -hosts ~/Documents/nodes.txt -i groupadd grp1

[1] 13:59:20 [SUCCESS] hue-1.test.cloudera.com

[2] 13:59:20 [SUCCESS] hue-2.test.cloudera.com

[3] 13:59:20 [SUCCESS] hue-3.test.cloudera.com

[4] 13:59:20 [SUCCESS] hue-4.test.cloudera.com

$ pssh -hosts ~/Documents/nodes.txt -i usermod -a -G grp1 t1

[1] 13:59:28 [SUCCESS] hue-1.test.cloudera.com

[2] 13:59:28 [SUCCESS] hue-2.test.cloudera.com

[3] 13:59:28 [SUCCESS] hue-3.test.cloudera.com

[4] 13:59:28 [SUCCESS] hue-4.test.cloudera.com

</code></pre>

**3.Create same Hue user: t1 and group: grp1 and make "t1" a member of "grp1".**

[<img src="https://cdn.gethue.com/uploads/2019/04/Screen-Shot-2019-04-03-at-3.33.18-PM.png"/>][1]

**4.Then log in as any user with sentry admin permission to run following queries in hive editor:**

<pre><code class="bash">

create role write_role;

GRANT ROLE write_role TO GROUP grp1;

GRANT ALL ON SERVER server1 TO ROLE write_role;

</code></pre>

Now "t1" user or any user in "grp1" can log in and create table by running any hive/impala DDL queries or through Hue importer.

[<img src="https://cdn.gethue.com/uploads/2019/04/All_Month_table_Created_Successfully.png"/>][2]

But mostly we would like to grant proper permissions for users instead of "ALL" on "server". let's walk through two other examples like read_only_role and read_write_role for specific databases.

Using similar commands to create t2 user in group grp2 and t3 user in group grp3 on cluster and Hue. Then use following statements to grant proper permission to each group:

1.Read write access to database: 's3db' for any user in group 'grp3':

<pre><code class="bash">

create role read_write_s3db_role;

GRANT ROLE read_write_s3db_role TO GROUP grp3;

GRANT ALL ON DATABASE s3db TO ROLE read_write_s3db_role;

GRANT ALL ON URI 'hdfs://hue-1.test.cloudera.com:8020/user/t3' to ROLE read_write_s3db_role;

</code></pre>

2. Read only permission for database: 'default' for any user in group 'grp2':

<pre><code class="bash">

create role read_only_defaultDb_role;

GRANT ROLE read_only_defaultDb_role TO GROUP grp2;

GRANT SELECT ON DATABASE default TO ROLE read_only_defaultDb_role;

GRANT REFRESH ON DATABASE default TO ROLE read_only_defaultDb_role;

</code></pre>

Now 't3' user can read and create new tables in database:s3db while 't2' user can read database: default only.

We can grant those permission through Hue security page too, it should ends like following.

[<img src="https://cdn.gethue.com/uploads/2019/04/HueSecurityRoles.png"/>][3]

Note: You have to grant URI permission to avoid following error during table creation:

<p class="p1">
  <b>Error while compiling statement: FAILED: SemanticException No valid privileges User t3 does not have privileges for CREATETABLE The required privileges: Server=server1->URI=hdfs://hue-1.gce.cloudera.com:8020/user/t3/t3_dir->action=*->grantOption=false;</b>
</p>

As always please feel free to reach out for any question or feedback!

&nbsp;

<pre></pre>

 [1]: https://cdn.gethue.com/uploads/2019/04/Screen-Shot-2019-04-03-at-3.33.18-PM.png
 [2]: https://cdn.gethue.com/uploads/2019/04/All_Month_table_Created_Successfully.png
 [3]: https://cdn.gethue.com/uploads/2019/04/HueSecurityRoles.png
