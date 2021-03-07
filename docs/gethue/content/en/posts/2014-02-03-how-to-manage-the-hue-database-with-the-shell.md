---
title: How to manage the Hue database with the shell
author: admin
type: post
date: 2014-02-03T17:59:00+00:00
url: /how-to-manage-the-hue-database-with-the-shell/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/75496233379/how-to-manage-the-hue-database-with-the-shell
tumblr_gethue_id:
  - 75496233379
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
  - Development

---
_Last update on March 9 2016_

&nbsp;

First, **<span style="color: #ff0000;">backup</span>** the database. By default this is this SqlLite file:

<pre><code class="bash">cp /var/lib/hue/desktop.db ~/</code></pre>

Then if using CM, export this variable in order to point to the correct database:

<pre><code class="bash">HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id

echo $HUE_CONF_DIR

export HUE_CONF_DIR</code></pre>

Where <id> is the most recent ID in that process directory for hue-HUE_SERVER.

A quick way to get the correct directory is to use this script:

<pre><code class="bash">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'\`"</code></pre>

Then go in the Database. From the Hue root (/use/lib/hue by default):

<pre><code class="bash">root@hue:hue# build/env/bin/hue dbshell</code></pre>

Note:

You might hit some permissions error about the logs:

<pre><code class="bash">build/env/bin/hue dbshell

Traceback (most recent call last):

File "/opt/cloudera/parcels/CDH-5.1.0-1.cdh5.1.0.p0.53/lib/hue/build/env/bin/hue", line 9, in <module>

load_entry_point('desktop==3.6.0', 'console_scripts', 'hue')()

File "/opt/cloudera/parcels/CDH-5.1.0-1.cdh5.1.0.p0.53/lib/hue/desktop/core/src/desktop/manage_entry.py", line 41, in entry

from desktop import settings, appmanager

File "/opt/cloudera/parcels/CDH-5.1.0-1.cdh5.1.0.p0.53/lib/hue/desktop/core/src/desktop/settings.py", line 55, in <module>

desktop.log.basic_logging(os.environ[ENV_HUE_PROCESS_NAME])

File "/opt/cloudera/parcels/CDH-5.1.0-1.cdh5.1.0.p0.53/lib/hue/desktop/core/src/desktop/log/__init__.py", line 146, in basic_logging

logging.config.fileConfig(log_conf)

File "/usr/lib/python2.7/logging/config.py", line 78, in fileConfig

handlers = _install_handlers(cp, formatters)

File "/usr/lib/python2.7/logging/config.py", line 156, in _install_handlers

h = klass(*args)

File "/usr/lib/python2.7/logging/handlers.py", line 118, in __init__

BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)

File "/usr/lib/python2.7/logging/handlers.py", line 65, in __init__

logging.FileHandler.__init__(self, filename, mode, encoding, delay)

File "/usr/lib/python2.7/logging/__init__.py", line 897, in __init__

StreamHandler.__init__(self, self._open())

File "/usr/lib/python2.7/logging/__init__.py", line 916, in _open

stream = open(self.baseFilename, self.mode)

IOError: [Errno 13] Permission denied: '/tmp/logs/dbshell.log'

</code></pre>

A "workaround" is to run the command as root:

<pre><code class="bash">sudo HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/9679-hue-HUE_SERVER /opt/cloudera/parcels/CDH-5.1.0-1.cdh5.1.0.p0.53/lib/hue/build/env/bin/hue dbshell</code></pre>

And you can start typing SQL queries:

<pre><code class="bash">sqlite> .tables

auth_group oozie_dataset

auth_group_permissions oozie_decision

auth_permission oozie_decisionend

auth_user oozie_distcp

auth_user_groups oozie_email

auth_user_user_permissions oozie_end

beeswax_metainstall oozie_fork

beeswax_queryhistory oozie_fs

beeswax_savedquery oozie_generic

beeswax_session oozie_history

desktop_document oozie_hive

desktop_document_tags oozie_java

desktop_documentpermission oozie_job

desktop_documentpermission_groups oozie_join

desktop_documentpermission_users oozie_kill

desktop_documenttag oozie_link

desktop_settings oozie_mapreduce

desktop_userpreferences oozie_node

django_admin_log oozie_pig

django_content_type oozie_shell

django_openid_auth_association oozie_sqoop

django_openid_auth_nonce oozie_ssh

django_openid_auth_useropenid oozie_start

django_session oozie_streaming

django_site oozie_subworkflow

jobsub_checkforsetup oozie_workflow

jobsub_jobdesign pig_document

jobsub_jobhistory pig_pigscript

jobsub_oozieaction search_collection

jobsub_ooziedesign search_facet

jobsub_ooziejavaaction search_result

jobsub_ooziemapreduceaction search_sorting

jobsub_ooziestreamingaction south_migrationhistory

oozie_bundle useradmin_grouppermission

oozie_bundledcoordinator useradmin_huepermission

oozie_coordinator useradmin_ldapgroup

oozie_datainput useradmin_userprofile

oozie_dataoutput</code></pre>

Or migrating the database manually:

<pre><code class="bash">build/env/bin/hue syncdb

build/env/bin/hue migrate</code></pre>

If you want to switch to another database (we recommend MySql), this [guide][1] details the migration process.

The database settings in Hue are located in the [hue.ini][2].

Note, you also query the database by pointing the <a href="http://gethue.tumblr.com/post/66661074125/dbquery-app-mysql-postgresql-oracle-and-sqlite-query" target="_blank" rel="noopener noreferrer">DB Query App</a> to the Hue database.

In developer mode (runserver command), you can also access the /admin page for using the <a href="https://docs.djangoproject.com/en/dev/ref/contrib/admin/" target="_blank" rel="noopener noreferrer">Django Admin</a>.

## Examples

Transfer Oozie workflows belonging to the user Bob to Joe.

**until** Hue 3.8

<pre><code class="bash"># First move the objects

from oozie.models import Job

from django.contrib.auth.models import User

u1 = User.objects.get(username='bob')

u2 = User.objects.get(username='joe')

Job.objects.filter(owner=u1)

> [<Job: MyWf - bob>]

Job.objects.filter(owner=u1).update(owner=u2)

> 1

Job.objects.filter(owner=u1)

> []

Job.objects.filter(owner=u2)

> [<Job: MyWf - joe>]

wfs = Job.objects.filter(owner=u2)

</code></pre>

**For** Hue 3.9+

<pre><code class="bash"># First move the objects

from desktop.models import Document2

from django.contrib.auth.models import User

u1 = User.objects.get(username='bob')

u2 = User.objects.get(username='joe')

Document2.objects.filter(owner=u1, type='oozie-workflow2')

> [<Document2: MyWf - bob>]

Document2.objects.filter(owner=u1, type='oozie-workflow2').update(owner=u2)

> 1

Document2.objects.filter(owner=u1, type='oozie-workflow2')

> []

Document2.objects.filter(owner=u2, type='oozie-workflow2')

> [<Document2: MyWf - joe>]

wfs = Document2.objects.filter(owner=u2, type='oozie-workflow2')

</code></pre>

**For** both

<pre><code class="bash"># The list of ALL the workflows (will also list the already known ones) of the second user

\# Then move the documents

from desktop.models import Document

Document.objects.filter(object_id__in=wfs)

> [<Document: workflow MyWf bob>]

Document.objects.filter(object_id__in=wfs)

> [<Document: workflow MyWf bob>]

Document.objects.filter(object_id__in=wfs).update(owner=u2)

> [<Document: workflow MyWf joe>]

</code></pre>

**Note**: it will change again in Hue 3.10 and be easier.

 [1]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Installation-Guide/cdh5ig_hue_database.html
 [2]: https://github.com/cloudera/hue/blob/branch-3.5/desktop/conf.dist/hue.ini#L185
