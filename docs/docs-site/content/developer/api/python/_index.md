---
title: "Python"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

Here is some overview about using the Python commands an shell and some examples below:

* [Hue API: Execute some builtin or shell commands](http://gethue.com/hue-api-execute-some-builtin-commands/).
* [How to manage the Hue database with the shell](http://gethue.com/how-to-manage-the-hue-database-with-the-shell/).

## Users

### Making a user admin

Via the Hue shell:

    build/env/bin/hue shell

Then type something similar to:

    from django.contrib.auth.models import User

    a = User.objects.get(username='hdfs')
    a.is_staff = True
    a.is_superuser = True
    a.set_password('my_secret')
    a.save()

### Changing user password

In the Hue shell:

    from django.contrib.auth.models import User

    user = User.objects.get(username='example')
    user.set_password('some password')
    user.save()


### Counting user documents

On the command line:

    ./build/env/bin/hue shell

If using Cloudera Manager, as a *root* user launch the shell.

Export the configuration directory:

    export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE_SERVER | tail -1 | awk '{print $9}'`"
    echo $HUE_CONF_DIR
    > /var/run/cloudera-scm-agent/process/2061-hue-HUE_SERVER

Get the process id:

    lsof -i :8888|grep -m1 hue|awk '{ print $2 }'
    > 14850

In order to export all Hue's env variables:

    for line in `strings /proc/$(lsof -i :8888|grep -m1 hue|awk '{ print $2 }')/environ|egrep -v "^HOME=|^TERM=|^PWD="`;do export $line;done

And finally launch the shell by:

    HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue shell
    > ALERT: This appears to be a CM Managed environment
    > ALERT: HUE_CONF_DIR must be set when running hue commands in CM Managed environment
    > ALERT: Please run 'hue <command> --cm-managed'

Then use the Python code to access a certain user information:

    Python 2.7.6 (default, Oct 26 2016, 20:30:19)
    Type "copyright", "credits" or "license" for more information.

    IPython 5.2.0 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    from django.contrib.auth.models import User
    from desktop.models import Document2

    user = User.objects.get(username='demo')
    Document2.objects.documents(user=user).count()

    In [8]: Document2.objects.documents(user=user).count()
    Out[8]: 1167

    In [10]: Document2.objects.documents(user=user, perms='own').count()
    Out[10]: 1166

    In [11]: Document2.objects.documents(user=user, perms='own', include_history=True).count()
    Out[11]: 7125

    In [12]: Document2.objects.documents(user=user, perms='own', include_history=True, include_trashed=True).count()
    Out[12]: 7638

    In [13]: Document2.objects.documents(user=user, perms='own', include_history=True, include_trashed=True, include_managed=True).count()
    Out[13]: 31408

    Out[14]:
    (85667L,
    {u'desktop.Document': 18524L,
      u'desktop.Document2': 31409L,
      u'desktop.Document2Permission': 556L,
      u'desktop.Document2Permission_groups': 277L,
      u'desktop.Document2Permission_users': 0L,
      u'desktop.Document2_dependencies': 15087L,
      u'desktop.DocumentPermission': 1290L,
      u'desktop.DocumentPermission_groups': 0L,
      u'desktop.DocumentPermission_users': 0L,
      u'desktop.Document_tags': 18524L})
