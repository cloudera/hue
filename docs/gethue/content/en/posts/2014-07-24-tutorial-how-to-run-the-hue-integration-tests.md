---
title: 'Tutorial: How to run the Hue unit and integration tests?'
author: admin
type: post
date: 2014-07-24T17:47:08+00:00
url: /tutorial-how-to-run-the-hue-integration-tests/
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
slide_template:
  - default
categories:
  - Development

---

**December 2020**: GitHub pull requests are now prefered https://docs.gethue.com/developer/development/#development-process


After the <a href="https://www.reviewboard.org/" target="_blank" rel="noopener noreferrer">Review Board</a> post, here is another tutorial about becoming an awesome Hue developer: how to run the Hue tests!

Hue has two types of tests:

  * unit tests
  * integration tests

First, clone the Hue repository and make sure that you have all the pre-requisite <a href="https://github.com/cloudera/hue#development-prerequisites" target="_blank" rel="noopener noreferrer">packages</a>:

<!--email_off-->

<pre><code class="bash">git clone git@github.com:cloudera/hue.git</code></pre>

<!--/email_off-->

# Unit Tests

The regular unit tests do not require all this setup! Just run them directly:

<pre><code class="bash">build/env/bin/hue test specific beeswax.tests:test_split_statements &> a; vim a</code></pre>

**Note**

This requires to have done an <a href="https://github.com/cloudera/hue#getting-started" target="_blank" rel="noopener noreferrer">initial build</a> of Hue with:

<pre><code class="bash">make apps</code></pre>

# Integration Tests

### Live cluster

The tests will run against the cluster configured in your hue.ini one if you specify:

<pre><code class="bash">export LIVE_CLUSTER=true</code></pre>

### Mini cluster

The test will run in a mini cluster (mini Hadoop, Oozie, Sqoop2 and Hive) created and destroyed after each run.

Here is how to get started:

<pre><code class="bash">./tools/jenkins/jenkins.sh slow</code></pre>

**Note**

You might have lost all the changes in your local pseudo hue.ini because of the \`git clean\` done by the script.

In order to avoid this, add this into your \`~/.bashrc\`:

<pre><code class="bash">export SKIP_CLEAN=true</code></pre>

**Note**

To point to an Impalad and trigger the Impala tests:

<pre><code class="bash">export TEST_IMPALAD_HOST=impalad-01.gethue.com</code></pre>

or

<pre><code class="bash">./build/env/bin/hue test impalaimpalad-01.gethue.com</code></pre>

&nbsp;

It is then going to download the 4 latest Hadoop, Oozie, Sqoop2 and Hive and pre-install them for you.

You can CTRL+C and kill the script when you see:

<pre><code class="bash">INFO: Oozie webconsole disabled, ExtJS library not specified

New Oozie WAR file with added 'JARs' at /home/romain/projects/hue-master/ext/oozie/oozie-4.0.0-cdh5.1.0/oozie-server/webapps/oozie.war

INFO: Oozie is ready to be started

+ /home/romain/projects/hue-master/ext/oozie/oozie-4.0.0-cdh5.1.0/bin/ooziedb.sh create -sqlfile oozie.sql -run

setting CATALINA_OPTS="$CATALINA_OPTS -Xmx1024m"

Validate DB Connection

DONE

Check DB schema does not exist

DONE

Check OOZIE_SYS table does not exist

DONE

Create SQL schema

DONE

Create OOZIE_SYS table

DONE

Oozie DB has been created for Oozie version '4.0.0-cdh5.1.0'

The SQL commands have been written to: oozie.sql

+ build_sqoop

+ check_mtime /home/romain/.hue_cache/.sqoop_mtime http://archive.cloudera.com/cdh5/cdh/5/sqoop2-1.99.3-cdh5.1.0.tar.gz

+ MTIME_FILE=/home/romain/.hue_cache/.sqoop_mtime

++ curl -Is http://archive.cloudera.com/cdh5/cdh/5/sqoop2-1.99.3-cdh5.1.0.tar.gz

++ awk 'BEGIN {FS=":"} { if ($1 == "Last-Modified") { print substr($2,2) } }'

+ MTIME='Tue, 15 Jul 2014 20'

+ echo 'Tue, 15 Jul 2014 20'

+ diff /home/romain/.hue_cache/.sqoop_mtime -

+ return 0

+ '[' '!' -f /home/romain/.hue_cache/sqoop2-1.99.3-cdh5.1.0.tar.gz ']'

+ SQOOP_DIR=/home/romain/projects/hue-master/ext/sqoop

+ export SQOOP_HOME=/home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0

+ SQOOP_HOME=/home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0

+ mkdir -p /home/romain/projects/hue-master/ext/sqoop

+ rm -rf /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0

+ echo 'Unpacking /home/romain/.hue_cache/sqoop2-1.99.3-cdh5.1.0.tar.gz to /home/romain/projects/hue-master/ext/sqoop'

Unpacking /home/romain/.hue_cache/sqoop2-1.99.3-cdh5.1.0.tar.gz to /home/romain/projects/hue-master/ext/sqoop

+ tar -C /home/romain/projects/hue-master/ext/sqoop -xzf /home/romain/.hue_cache/sqoop2-1.99.3-cdh5.1.0.tar.gz

+ export SQOOP_CONF_DIR=/home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf

+ SQOOP_CONF_DIR=/home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf

+ rm -rf /home/romain/projects/hue-master/ext/sqoop/sqoop

+ ln -sf /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0 /home/romain/projects/hue-master/ext/sqoop/sqoop

+ sed -i.bk 's/12000/${test.port.http}/g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/server.xml

+ sed -i.bk 's/12001/${test.port.shutdown}/g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/server.xml

+ sed -i.bk 's/localhost/${test.host.local}/g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/server.xml

+ sed -i.bk 's|\(common.loader.\*$\)|\1,/home/romain/projects/hue-master/ext/hadoop/hadoop/share/hadoop/common/lib/\*.jar,/home/romain/projects/hue-master/ext/hadoop/hadoop/share/hadoop/mapreduce1/\*.jar,/home/romain/projects/hue-master/ext/hadoop/hadoop/share/hadoop/mapreduce1/lib/\*.jar|g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/catalina.properties

+ sed -i.bk 's|${catalina\.base}/logs|${test.log.dir}|g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/logging.properties

+ sed -i.bk 's|\@LOGDIR\@|${test.log.dir}|g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/sqoop.properties

+ sed -i.bk 's|\@BASEDIR\@|${test.base.dir}|g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/sqoop.properties

+ sed -i.bk 's|/etc/hadoop/conf|${test.hadoop.conf.dir}|g' /home/romain/projects/hue-master/ext/sqoop/sqoop2-1.99.3-cdh5.1.0/server/conf/sqoop.properties

+ make apps

cd /home/romain/projects/hue-master/maven && mvn install

[INFO] Scanning for projects...

[INFO]

[INFO] ------------------------

[INFO] Building Hue Maven Parent POM 3.6.0-SNAPSHOT

[INFO] ------------------------

[INFO]

[INFO] - maven-enforcer-plugin:1.0:enforce (default) @ hue-parent -

[INFO]

[INFO] - maven-install-plugin:2.3:install (default-install) @ hue-parent -

[INFO] Installing /home/romain/projects/hue-master/maven/pom.xml to /home/romain/.m2/repository/com/cloudera/hue/hue-parent/3.6.0-SNAPSHOT/hue-parent-3.6.0-SNAPSHOT.pom

[INFO] ------------------------

[INFO] BUILD SUCCESS

[INFO] ------------------------

[INFO] Total time: 1.488s

[INFO] Finished at: Thu Jul 24 10:46:56 PDT 2014

[INFO] Final Memory: 7M/150M

[INFO] ------------------------

</code></pre>

And that's it! You can run all the tests or some parts with this <a href="https://github.com/cloudera/hue#getting-started" target="_blank" rel="noopener noreferrer">syntax</a>:

<pre><code class="bash">build/env/bin/hue test specific filebrowser.views_test:test_listdir_sort_and_filter &> a; vim a</code></pre>

&nbsp;

**Note**:

In some cases you might need to clear up your your cache with something like:

<pre><code class="bash">rm /home/romain/.hue_cache/.*</code></pre>

then in

<pre><code class="bash">ext/</code></pre>

delete everything but

<pre><code class="bash">thirdparty/</code></pre>

&nbsp;

# Sum-up

We hope that is now easier to help you <a href="https://github.com/cloudera/hue/wiki/Contribute-to-HUE" target="_blank" rel="noopener noreferrer">contribute to Hue</a> 😉

As usual feel free to send feedback on the [hue-user][1] list or [@gethue][2]!

 [1]: http://groups.google.com/a/cloudera.org/group/hue-user
 [2]: https://twitter.com/gethue
