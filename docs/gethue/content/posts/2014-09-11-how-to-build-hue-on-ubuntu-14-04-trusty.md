---
title: How to build Hue on Ubuntu
author: admin
type: post
date: 2014-09-11T21:10:46+00:00
url: /how-to-build-hue-on-ubuntu-14-04-trusty/
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
ampforwp-amp-on-off:
  - default
categories:
  - Development

---
_Last Update: January 24th 2018_

&nbsp;

This guide takes 14.04 but it should be almost the same for 16 or 17.

Due to a [package bug,][1] we got quite a few questions about how to build Hue consistently. Here is a step by step guide about how to get up and running.

First, make sure that you are indeed on the 14.04:

<pre><code class="bash">> lsb_release -a

No LSB modules are available.

Distributor ID: Ubuntu

Description: Ubuntu 14.04 LTS

Release: 14.04

Codename: trusty

</code></pre>

Then install git and fetch Hue [source code][2] from github:

<pre><code class="bash">sudo apt-get install git

git clone https://github.com/cloudera/hue.git

cd hue

</code></pre>

Then some [development packages][3] need to be installed:

<pre><code class="bash">apt-get install python2.7-dev \

make \

libkrb5-dev \

libxml2-dev \

libffi-dev \

libxslt-dev \

libsqlite3-dev \

libssl-dev \

libldap2-dev \

python-pip

</code></pre>

You can also try this one line:

<pre><code class="bash">sudo apt-get install ant gcc g++ libkrb5-dev libffi-dev libmysqlclient-dev libssl-dev libsasl2-dev libsasl2-modules-gssapi-mit libsqlite3-dev libtidy-0.99-0 libxml2-dev libxslt-dev make libldap2-dev maven python-dev python-setuptools libgmp3-dev</code></pre>

You will also need the ‘maven’ package. You could install it with apt-get but it is also recommended to install from a [maven3 tarball][4] in order to avoid to pull a lot of dependencies.

Then it is time to build Hue. Just issue the ‘make apps’ command.

You will hit the Ubuntu package problem the first time if you are using a Hue version [smaller than 3.8][5]:

<pre><code class="bash">- Creating virtual environment at /root/hue/build/env

python2.7 /root/hue/tools/virtual-bootstrap/virtual-bootstrap.py \

-qq -no-site-packages /root/hue/build/env

Traceback (most recent call last):

File "/root/hue/tools/virtual-bootstrap/virtual-bootstrap.py", line 1504, in <module>

main()

File "/root/hue/tools/virtual-bootstrap/virtual-bootstrap.py", line 547, in main

use_distribute=options.use_distribute)

File "/root/hue/tools/virtual-bootstrap/virtual-bootstrap.py", line 637, in create_environment

install_setuptools(py_executable, unzip=unzip_setuptools)

File "/root/hue/tools/virtual-bootstrap/virtual-bootstrap.py", line 379, in install_setuptools

_install_req(py_executable, unzip)

File "/root/hue/tools/virtual-bootstrap/virtual-bootstrap.py", line 355, in _install_req

cwd=cwd)

File "/root/hue/tools/virtual-bootstrap/virtual-bootstrap.py", line 608, in call_subprocess

% (cmd_desc, proc.returncode))

OSError: Command /root/hue/build/env/bin/python2.7 -c "#!python

\"\"\"Bootstrap setuptoo...

</code></pre>

We use one of the workaround:

<pre><code class="bash">sudo ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

</code></pre>

Links on <https://issues.cloudera.org/browse/HUE-2246> detail its cause.

If you don’t have Oracle Java 7 installed the build will then stop with:

<pre><code class="bash">[INFO] ------------------------

[INFO] BUILD FAILURE

[INFO] ------------------------

[INFO] Total time: 1:20.498s

[INFO] Finished at: Wed Sep 10 18:53:55 PDT 2014

[INFO] Final Memory: 11M/116M

[INFO] ------------------------

[ERROR] Failed to execute goal on project hue-plugins: Could not resolve dependencies for project com.cloudera.hue:hue-plugins:jar:3.6.0-SNAPSHOT: Could not find artifact jdk.tools:jdk.tools:jar:1.7 at specified path /usr/lib/jvm/java-7-openjdk-amd64/jre/../lib/tools.jar -> [Help 1]

[ERROR]

[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.

[ERROR] Re-run Maven using the -X switch to enable full debug logging.

[ERROR]

[ERROR] For more information about the errors and possible solutions, please read the following articles:

[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/DependencyResolutionException

make[2]: \*** [/root/hue/desktop/libs/hadoop/java-lib/hue-plugins-3.6.0-SNAPSHOT.jar] Error 1

make[2]: Leaving directory \`/root/hue/desktop/libs/hadoop'

make[1]: \*** [.recursive-env-install/libs/hadoop] Error 2

make[1]: Leaving directory \`/root/hue/desktop'

make: \*** [desktop] Error 2

</code></pre>

To fix is install this packages:

<pre><code class="bash">sudo add-apt-repository ppa:webupd8team/java

sudo apt-get install oracle-java7-installer

sudo apt-get install oracle-java7-set-default

</code></pre>

**Note**

‘asciidoc‘ is also required if you want to build a tarball release at some point with ‘make prod’. If not you will get this error:

<pre><code class="bash">make[1]: Leaving directory \`/root/hue/apps'

make[1]: Entering directory \`/root/hue/docs'

- Generating sdk doc at /root/hue/build/docs/sdk/sdk.html

- Generated /root/hue/build/docs/sdk/sdk.html

- Generating release notes at /root/hue/build/docs/release-notes

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

/bin/bash: line 1: a2x: command not found

mv: cannot stat ‘release-notes/*.html’: No such file or directory

</code></pre>

And that’s it! At the end of the build:

<pre><code class="bash">=== Installing app at oozie

=== oozie v.3.6.0 is already installed

=== Installing app at proxy

=== proxy v.3.6.0 is already installed

=== Installing app at useradmin

=== useradmin v.3.6.0 is already installed

=== Installing app at impala

=== impala v.3.6.0 is already installed

=== Installing app at pig

=== pig v.3.6.0 is already installed

=== Installing app at search

=== search v.3.6.0 is already installed

=== Installing app at hbase

=== hbase v.3.6.0 is already installed

=== Installing app at sqoop

=== sqoop v.3.6.0 is already installed

=== Installing app at zookeeper

=== zookeeper v.3.6.0 is already installed

=== Installing app at rdbms

=== rdbms v.3.6.0 is already installed

=== Installing app at spark

=== spark v.3.6.0 is already installed

=== Installing app at security

=== security v.3.6.0 is already installed

=== Saved registry at /home/romain/projects/hue/app.reg

=== Saved /home/romain/projects/hue/build/env/lib/python2.7/site-packages/hue.pth

Running '/home/romain/projects/hue/build/env/bin/hue syncdb -noinput' with None

Syncing...

Creating tables ...

Installing custom SQL ...

Installing indexes ...

Installed 0 object(s) from 0 fixture(s)

Synced:

> django.contrib.auth

> django_openid_auth

> django.contrib.contenttypes

> django.contrib.sessions

> django.contrib.sites

> django.contrib.admin

> django_extensions

> south

> indexer

> about

> filebrowser

> help

> impala

> jobbrowser

> metastore

> proxy

> rdbms

> zookeeper

Not synced (use migrations):

- desktop

- beeswax

- hbase

- jobsub

- oozie

- pig

- search

- spark

- sqoop

- useradmin

- security

(use ./manage.py migrate to migrate these)

Running '/home/romain/projects/hue/build/env/bin/hue migrate -merge' with None

Running migrations for desktop:

- Nothing to migrate.

- Loading initial data for desktop.

Installed 0 object(s) from 0 fixture(s)

Running migrations for beeswax:

- Nothing to migrate.

- Loading initial data for beeswax.

Installed 0 object(s) from 0 fixture(s)

Running migrations for hbase:

- Nothing to migrate.

- Loading initial data for hbase.

Installed 0 object(s) from 0 fixture(s)

Running migrations for jobsub:

- Nothing to migrate.

- Loading initial data for jobsub.

Installed 0 object(s) from 0 fixture(s)

Running migrations for oozie:

- Nothing to migrate.

- Loading initial data for oozie.

Installed 0 object(s) from 0 fixture(s)

Running migrations for pig:

- Nothing to migrate.

- Loading initial data for pig.

Installed 0 object(s) from 0 fixture(s)

Running migrations for search:

- Nothing to migrate.

- Loading initial data for search.

Installed 0 object(s) from 0 fixture(s)

Running migrations for spark:

- Nothing to migrate.

- Loading initial data for spark.

Installed 0 object(s) from 0 fixture(s)

Running migrations for sqoop:

- Nothing to migrate.

- Loading initial data for sqoop.

Installed 0 object(s) from 0 fixture(s)

Running migrations for useradmin:

- Nothing to migrate.

- Loading initial data for useradmin.

Installed 0 object(s) from 0 fixture(s)

? You have no migrations for the 'security' app. You might want some.

make[1]: Leaving directory \`/home/romain/projects/hue/apps'

</code></pre>

Just start the development server:

<pre><code class="bash">./build/env/bin/hue runserver

</code></pre>

and visit <http://127.0.0.1:8000/> !

[<img src="https://cdn.gethue.com/uploads/2014/09/hue-login-1024x547.png" />][6]

After this, if the cluster is distributed, it is time to [configure Hue][7] to point to each [Hadoop service][8]!

<span style="color: #444444;">As usual feel free to send feedback on the </span><a style="color: #428bca !important;" href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a><span style="color: #444444;"> list or </span><a style="color: #428bca !important;" href="https://twitter.com/gethue">@gethue</a><span style="color: #444444;">!</span>

 [1]: https://bugs.launchpad.net/ubuntu/+source/python2.7/+bug/1115466
 [2]: https://github.com/cloudera/hue
 [3]: https://github.com/cloudera/hue#development-prerequisites
 [4]: http://maven.apache.org/download.cgi
 [5]: https://issues.cloudera.org/browse/HUE-2654
 [6]: https://cdn.gethue.com/uploads/2014/09/hue-login.png
 [7]: https://gethue.com/yahoo-hadoop-meetup-integrate-hue-with-your-hadoop-cluster/
 [8]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Installation-Guide/cdh5ig_cdh_hue_configure.html
