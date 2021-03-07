---
title: 'Hue API: Execute some builtin or shell commands'
author: admin
type: post
date: 2015-02-08T01:02:56+00:00
url: /hue-api-execute-some-builtin-commands/
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
Last update: March 3rd 2016

&nbsp;

Hue comes with a set of commands for simplifying the management of the service. Here is a quick guide about how to use them.

&nbsp;

## Get started

If using CM, export this variable in order to point to the correct Hue:

<pre><code class="bash">cd /opt/cloudera/parcels/CDH/lib/</code></pre>

<pre><code class="bash">HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id

echo $HUE_CONF_DIR

export HUE_CONF_DIR</code></pre>

Where <id> is the most recent ID in that process directory for hue-HUE_SERVER.

If not using CM, just append the root of Hue home, normally:

<pre><code class="bash">/usr/lib/hue</code></pre>

Note:

You might need to have access to a local directory for the logs of the command, e.g.:

<pre><code class="bash">cd /tmp</code></pre>

&nbsp;

<span style="font-weight: 400;">Starting in Cloudera Manager 5.5 passwords are not stored in configuration files in clear text anymore.  As a result on Cloudera Manager 5.5 and higher you will need to know the password for Hue's DB connection to be able to run the Hue command line.</span>

## Running Hue command line on Cloudera Manager 5.5 and above

<li style="font-weight: 400;">
  <span style="font-weight: 400;">Set </span><span style="font-weight: 400;">HUE_CONF_DIR</span><span style="font-weight: 400;"> to the current Hue configuration created by Cloudera Manager.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 `"</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">Run the Hue Command line by including the following environment variables:</span> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">HUE_DATABASE_PASSWORD=<dbpassword></span><span style="font-weight: 400;"> - This defines the password Hue should use to connect to the DB.</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1</span><span style="font-weight: 400;"> - This configures the Hue command line to run even if there are other unknown passwords defined in the Cloudera Manager created </span><span style="font-weight: 400;">hue.ini</span><span style="font-weight: 400;">.  Such as </span><span style="font-weight: 400;">bind_password</span><span style="font-weight: 400;"> or </span><span style="font-weight: 400;">ssl_password</span><span style="font-weight: 400;">.</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 400;">HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 HUE_DATABASE_PASSWORD=password /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue <command></span>
    </li>
    <li style="font-weight: 400;">
      <b>Note: </b><span style="font-weight: 400;">When you include environment variables on the command line without a ";" between them as the above command does, they will only apply to that command.  You won't have </span><span style="font-weight: 400;">HUE_DATABASE_PASSWORD</span><span style="font-weight: 400;"> in the environment after the command finishes.</span>
    </li>
  </ul>
</li>

<span style="font-weight: 400;">Example running </span><span style="font-weight: 400;">changepassword</span><span style="font-weight: 400;">:</span>

<pre><code class="bash">[root@nightly55-1 ~]# export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 \`"

[root@nightly55-1 ~]# HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 HUE_DATABASE_PASSWORD=password /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue changepassword admin

Changing password for user 'admin'

Password:

Password (again):

Password changed successfully for user 'admin'

</code></pre>

<span style="font-weight: 400;">If you are performing command line actions that require other password, such as </span><span style="font-weight: 400;">bind_password</span> <span style="font-weight: 400;">for syncing LDAP users and groups, you need to include environment variables to set those as well.  Here is a list:</span>

<pre><code class="bash">HUE_AUTH_PASSWORD = password used to authenticate to HS2/Impala.

HUE_LDAP_PASSWORD = password used to authenticate to HS2/Impala.

HUE_SSL_PASSWORD = password used for private key file.

HUE_SMTP_PASSWORD = password used for SMTP.

HUE_LDAP_BIND_PASSWORD = password used for Ldap Bind.</code></pre>

##

## Running Hue command line on Cloudera Manager 5.4 and below

<li style="font-weight: 400;">
  <span style="font-weight: 400;">Set HUE_CONF_DIR to the current Hue configuration created by Cloudera Manager.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 `"</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">Run the Hue command line.</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">/opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue <command></span>
</li>

<span style="font-weight: 400;">Example running </span><span style="font-weight: 400;">changepassword</span><span style="font-weight: 400;">.</span>

<pre><code class="bash">[root@cdhnok54-1 tmp]# export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 \`"

[root@cdhnok54-1 tmp]# /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue changepassword admin

Changing password for user 'admin'

Password:

Password (again):

Password changed successfully for user 'admin'</code></pre>

&nbsp;

## Commands

Executing the hue command with no argument will list them all:

<pre><code class="bash">./build/env/bin/hue

...

[auth]

changepassword

createsuperuser

[beeswax]

beeswax_install_examples

close_queries

close_sessions

[desktop]

config_dump

config_help

config_upgrade

create_desktop_app

create_proxy_app

create_test_fs

kt_renewer

runcherrypyserver

runcpserver

runpylint

sync_documents

test

version

[django]

cleanup

compilemessages

createcachetable

dbshell

diffsettings

dumpdata

flush

inspectdb

loaddata

makemessages

reset

runfcgi

runserver

shell

sql

sqlall

sqlclear

sqlcustom

sqlflush

sqlindexes

sqlinitialdata

sqlreset

sqlsequencereset

startapp

startproject

validate

[django_extensions]

clean_pyc

compile_pyc

create_app

create_command

create_jobs

describe_form

dumpscript

export_emails

generate_secret_key

graph_models

mail_debug

passwd

print_user_for_session

reset_db

runjob

runjobs

runprofileserver

runscript

runserver_plus

set_fake_emails

set_fake_passwords

shell_plus

show_templatetags

show_urls

sqldiff

sync_media_s3

syncdata

unreferenced_files

[django_openid_auth]

openid_cleanup

[hbase]

hbase_setup

[indexer]

indexer_setup

[oozie]

oozie_setup

[pig]

pig_setup

[search]

search_setup

[south]

convert_to_south

datamigration

graphmigrations

migrate

migrationcheck

schemamigration

startmigration

syncdb

testserver

[spark]

livy_server

[useradmin]

import_ldap_group

import_ldap_user

sync_ldap_users_and_groups

useradmin_sync_with_unix

</code></pre>

## Starting the server

For stating the test server, defaulting to port 8000:

<pre><code class="bash">./build/env/bin/hue runserver</code></pre>

For stating the production server, defaulting to port 8888:

<pre><code class="bash">./build/env/bin/hue runcpserver</code></pre>

These commands are more detailed on the [How to get started page][1].

## Installing the examples

All the commands finishing by '_setup' will install the example of the particular app.

<pre><code class="bash">./build/env/bin/hue search_setup</code></pre>

In the case of Hive, in order to install the sample_07 and sample_08 tables and SQL queries, type:

<pre><code class="bash">./build/env/bin/hue beeswax_install_examples</code></pre>

**Note**:

These commands are also accessible directly from the [Web UI][2].

[<img src="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080615.png" alt="Screenshot from 2014-04-09 08:06:15" width="757" height="634"  />][3]

## Changing a password

This command is explained in more detail in the [How to change or reset a forgotten password][4] post:

<pre><code class="bash">./build/env/bin/hue changepassword</code></pre>

## Closing Hive queries

This command is explained in more detail in the [Hive and Impala queries life cycle][5] post:

<pre><code class="bash">./build/env/bin/hue close_queries</code></pre>

<pre><code class="bash">./build/env/bin/hue close_sessions</code></pre>

## Running the tests

This command is explained in more detail in the [How to run the tests][6] post:

<pre><code class="bash">./build/env/bin/hue test</code></pre>

## Connect to the Database

This command is explained in more detail in the [How to manage the database with the shell][7] post:

<pre><code class="bash">./build/env/bin/hue dbshell</code></pre>

## Connect to the Python shell

In order to type any Django to Python:

<pre><code class="bash">./build/env/bin/hue shell</code></pre>

<pre><code class="bash">./build/env/bin/hue shell < script.py</code></pre>

&nbsp;

&nbsp;

Have any questions? Feel free to contact us on [hue-user][8] or [@gethue][9]!

 [1]: https://github.com/cloudera/hue#getting-started
 [2]: https://gethue.com/tutorial-live-demo-of-search-on-hadoop/
 [3]: https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080615.png
 [4]: https://gethue.com/password-management-in-hue/
 [5]: https://gethue.com/hadoop-tutorial-hive-and-impala-queries-life-cycle/
 [6]: https://gethue.com/tutorial-how-to-run-the-hue-integration-tests/
 [7]: https://gethue.com/how-to-manage-the-hue-database-with-the-shell/
 [8]: http://groups.google.com/a/cloudera.org/group/hue-user
 [9]: https://twitter.com/gethue
