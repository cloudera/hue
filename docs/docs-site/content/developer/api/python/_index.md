---
title: "Python"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

Use the Hue Python shell to run code with the server settings and database. Use it for administration tasks such as managing users and documents.

Start the shell from your Hue installation:

```bash
build/env/bin/hue shell
```

In the examples below, `user` is a Django user object, for example `User.objects.get(username='demo')`.

## Query

Run a statement and wait for it to finish. The call needs a request object with a user:

```python
from django.contrib.auth.models import User
from notebook.models import make_notebook, MockRequest

user = User.objects.get(username='demo')

job = make_notebook(
    name='List tables in the sales database',
    editor_type='hive',
    statement='SHOW TABLES',
    status='ready',
    database='sales',
    on_success_url='assist.db.refresh'
)

request = MockRequest(user=user)
job.execute_and_wait(request)
```

## Storage

Get a client for a storage with `get_client(name, fs, user)`. The `fs` argument is the scheme of the storage, for example `s3a` or `abfs`.

### S3

Get the client:

```python
from desktop.lib.fsmanager import get_client

s3fs = get_client('default', 's3a', 'demo')
```

Then get a key:

```python
k = s3fs._get_key('s3a://gethue/')
k.exists()
s3fs.stats('s3a://gethue/user/gethue/footravel.csv').to_json_dict()
```

Or run file system operations:

```python
b = s3fs._get_bucket('gethue')
list(b.list(prefix='user/gethue/'))

new_k = b.new_key('user/gethue/data/3')
new_k.set_contents_from_string('123')

# Delete the key
result = new_k.bucket.delete_keys(new_k)

s3fs.listdir_stats('s3a://gethue/user/gethue')
s3fs.mkdir('s3a://gethue/user/gethue/demo')
```

### ADLS

Get the client:

```python
from desktop.lib.fsmanager import get_client

fs = get_client('default', 'abfs', 'demo')
```

Then run file system operations:

```python
# Stats
fs.stats('abfs://data/user/demo/demo_dir')

# List a directory
fs.listdir('abfs://data/user/demo/demo_dir')

# Create a directory
fs.mkdir('abfs://data/user/demo/new_dir')

# Create a file
fs.create('abfs://data/user/demo/demo_dir/newfile.txt')

# Create a file with content
fs.create('abfs://data/user/demo/demo_dir/demo_file.txt', data='Hello world!')

# Read a file
fs.read('abfs://data/user/demo/demo_dir/demo_file.txt')

# Delete a file or an empty directory
fs.remove('abfs://data/user/demo/demo_dir/demo_file.txt')

# Delete a directory and its content
fs.rmtree('abfs://data/user/demo/demo_dir')

# Change the permissions (octal number or string)
fs.chmod('abfs://data/user/demo/demo_dir/demo_file.txt', permissionNumber='777')

# Rename a path
fs.rename('abfs://data/user/demo/old_name_dir', 'abfs://data/user/demo/new_name_dir')

# Copy a file or a directory
fs.copy('abfs://data/user/demo/source_path', 'abfs://data/user/demo/destination_path')
```

## Users

### Create a user

```python
from desktop.auth.backend import create_user

bob = create_user(username='bob', password='secret1', is_superuser=True)
alice = create_user(username='alice', password='secret2', is_superuser=False)
```

### Find or create a user

```python
from desktop.auth.backend import find_or_create_user

bob = find_or_create_user(username='bob', password='secret1', is_superuser=True)
alice = find_or_create_user(username='alice', password='secret2', is_superuser=False)
```

### Make a user an admin

```python
from django.contrib.auth.models import User

a = User.objects.get(username='hdfs')
a.is_staff = True
a.is_superuser = True
a.set_password('my_secret')
a.save()
```

### Change a password

```python
from django.contrib.auth.models import User

user = User.objects.get(username='example')
user.set_password('some password')
user.save()
```

## Documents

### Count the documents of a user

The `perms` argument is `both` (default), `shared` or `owned`.

```python
from django.contrib.auth.models import User
from desktop.models import Document2

user = User.objects.get(username='demo')

# Owned and shared documents
Document2.objects.documents(user=user).count()

# Owned documents only
Document2.objects.documents(user=user, perms='owned').count()

# Include the query history
Document2.objects.documents(user=user, perms='owned', include_history=True).count()

# Include the trashed documents
Document2.objects.documents(user=user, perms='owned', include_history=True, include_trashed=True).count()

# Include the documents managed by Hue
Document2.objects.documents(user=user, perms='owned', include_history=True, include_trashed=True, include_managed=True).count()
```
