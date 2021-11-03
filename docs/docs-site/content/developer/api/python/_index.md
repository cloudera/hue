---
title: "Python"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

Leverage the built-in Python shell to interact with the server and the API.

    build/env/bin/hue shell

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


## Query

Requires a user object:

    from notebook.models import make_notebook, MockRequest

    job = make_notebook(
        name='List tables in Salesforce database',
        editor_type='hive',
        statement='SHOW TABLES',
        status='ready',
        database='sfdc',
        on_success_url='assist.db.refresh'
    )

    request = MockRequest(user=user)
    job.execute_and_wait(request)

## Storage

### S3

Interact directly with S3 by first getting the client:

    from desktop.lib.fsmanager import get_client

    s3fs = get_client('default', 's3a', 'csso_hueuser')

Then grab the key:

    k = s3fs._get_key('s3a://gethue/')
    k.exists()
    s3fs.stats('s3a://gethue/user/gethue/footravel.csv').to_json_dict()

Or perform various FS operations:

    b = s3fs._get_bucket('gethue')
    list(b.list(prefix='user/gethue/'))

    new_k = b.new_key('user/gethue/data/3')
    new_k.set_contents_from_string('123')

    # new_k.delete()
    result = new_k.bucket.delete_keys(new_k)

    k = s3fs._get_key('s3a://gethue/user/gethue')

    s3fs.listdir_stats('s3a://gethue/user/gethue')
    s3fs.mkdir('s3a://gethue/user/gethue/demo')

### ADLS


Interact directly with ADLS by first getting the client:

    from desktop.lib.fsmanager import get_client

    fs = get_client('default', 'abfs', 'csso_hueuser')

Perform various FS operations:

    # Stats
    fs.stats('abfs://data/user/csso_hueuser/demo_dir')

    # List directory
    fs.listdir('abfs://data/user/csso_hueuser/demo_dir')

    # Create directory
    fs.mkdir('abfs://data/user/csso_hueuser/new_dir')

    # Create file
    fs.create('abfs://data/user/csso_hueuser/demo_dir/newfile.txt')

    # Create file with write data
    fs.create('abfs://data/user/csso_hueuser/demo_dir/demo_file.txt', data='Hello world!')

    # Read
    fs.read('abfs://data/user/csso_hueuser/demo_dir/demo_file.txt')

    # Delete path (can be file or empty directory)
    fs.remove('abfs://data/user/csso_hueuser/demo_dir/demo_file.txt')

    # Delete directory with recursive as true
    fs.rmtree('abfs://data/user/csso_hueuser/demo_dir')

    # Chmod (accepts both octal number and string)
    fs.chmod('abfs://data/user/csso_hueuser/demo_dir/demo_file.txt', permissionNumber='777')

    # Rename path
    fs.rename('abfs://data/user/csso_hueuser/old_name_dir', 'abfs://data/user/csso_hueuser/new_name_dir')

    # Copy (for both file and directory)
    fs.copy('abfs://data/user/csso_hueuser/source_path', 'abfs://data/user/csso_hueuser/destination_path')

## Users

### Create

    from desktop.auth.backend import create_user

    bob = create_user(username='bob', password='secret1', is_superuser=True)
    alice = create_user(username='alice', password='secret2', is_superuser=False)

### Find or Create

    from desktop.auth.backend import find_or_create_user

    bob = find_or_create_user(username='bob', password='secret1', is_superuser=True)
    alice = find_or_create_user(username='alice', password='secret2', is_superuser=False)

### Convert to admin

Then type something similar to:

    from django.contrib.auth.models import User

    a = User.objects.get(username='hdfs')
    a.is_staff = True
    a.is_superuser = True
    a.set_password('my_secret')
    a.save()

### Changing password

    from django.contrib.auth.models import User

    user = User.objects.get(username='example')
    user.set_password('some password')
    user.save()

### Counting documents

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
