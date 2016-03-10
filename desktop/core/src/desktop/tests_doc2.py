#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import re

from nose.tools import assert_equal, assert_false, assert_true
from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import import_saved_beeswax_query, Directory, Document2

from beeswax.models import SavedQuery
from beeswax.design import hql_query
from useradmin.models import get_default_user_group


class TestDocument2(object):

  def setUp(self):
    self.client = make_logged_in_client(username="doc2", groupname="doc2", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="doc2")
    grant_access("doc2", "doc2", "beeswax")

    # This creates the user directories for the new user
    response = self.client.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    assert_equal('/', data['document']['path'], data)

    self.home_dir = Document2.objects.get_home_directory(user=self.user)


  def test_trash_directory(self):
    assert_true(Directory.objects.filter(owner=self.user, name=Document2.TRASH_DIR, type='directory').exists())


  def test_document_create(self):
    sql = 'SELECT * FROM sample_07'

    design = hql_query(sql)

    # is_auto
    # is_trashed
    # is_redacted
    old_query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['hql'],
        owner=self.user,
        data=design.dumps(),
        name='See examples',
        desc='Example of old format'
    )

    try:
      new_query = import_saved_beeswax_query(old_query)
      new_query_data = new_query.get_data()

      assert_equal('query-hive', new_query_data['type'])
      assert_equal('See examples', new_query_data['name'])
      assert_equal('Example of old format', new_query_data['description'])

      assert_equal('ready', new_query_data['snippets'][0]['status'])
      assert_equal('See examples', new_query_data['snippets'][0]['name'])
      assert_equal('SELECT * FROM sample_07', new_query_data['snippets'][0]['statement_raw'])

      assert_equal([], new_query_data['snippets'][0]['properties']['settings'])
      assert_equal([], new_query_data['snippets'][0]['properties']['files'])
      assert_equal([], new_query_data['snippets'][0]['properties']['functions'])
    finally:
      old_query.delete()


  def test_get_document(self):
    doc = Document2.objects.create(name='test_doc', type='query-hive', owner=self.user, data={})
    self.home_dir.children.add(doc)
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_true('document' in data)
    assert_equal(doc.uuid, data['document']['uuid'])

    # Invalid uuid returns error
    response = self.client.get('/desktop/api2/doc/', {'uuid': '1234-5678-9'})
    data = json.loads(response.content)
    assert_equal(-1, data['status'])
    assert_true('not found' in data['message'])


  def test_directory_create(self):
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(self.home_dir.uuid), 'name': json.dumps('test_mkdir')})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('directory' in data)
    assert_equal(data['directory']['name'], 'test_mkdir', data)
    assert_equal(data['directory']['type'], 'directory', data)


  def test_file_move(self):
    source_dir = Directory.objects.create(name='test_mv_file_src', owner=self.user, parent_directory=self.home_dir)
    target_dir = Directory.objects.create(name='test_mv_file_dst', owner=self.user, parent_directory=self.home_dir)
    doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=source_dir)

    # Verify original paths before move operation
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert_equal('/test_mv_file_src', data['document']['path'])

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal('/test_mv_file_src/query1.sql', data['document']['path'])

    response = self.client.post('/desktop/api2/doc/move', {
        'source_doc_uuid': json.dumps(doc.uuid),
        'destination_doc_uuid': json.dumps(target_dir.uuid)
    })
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    # Verify that the paths are updated
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert_false(any(doc['uuid'] == doc.uuid for doc in data['children']), data['children'])

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal('/test_mv_file_dst/query1.sql', data['document']['path'])


  def test_directory_move(self):
    source_dir = Directory.objects.create(name='test_mv', owner=self.user, parent_directory=self.home_dir)
    target_dir = Directory.objects.create(name='test_mv_dst', owner=self.user, parent_directory=self.home_dir)
    doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=source_dir)

    # Verify original paths before move operation
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert_equal('/test_mv', data['document']['path'])

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal('/test_mv/query1.sql', data['document']['path'])

    response = self.client.post('/desktop/api2/doc/move', {
        'source_doc_uuid': json.dumps(Directory.objects.get(owner=self.user, name='test_mv').uuid),
        'destination_doc_uuid': json.dumps(Directory.objects.get(owner=self.user, name='test_mv_dst').uuid)
    })
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    # Verify that the paths are updated
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert_equal('/test_mv_dst/test_mv', data['document']['path'])

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal('/test_mv_dst/test_mv/query1.sql', data['document']['path'])


  def test_directory_children(self):
    # Creates 2 directories and 2 queries and saves to home directory
    dir1 = Directory.objects.create(name='test_dir1', owner=self.user)
    dir2 = Directory.objects.create(name='test_dir2', owner=self.user)
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={})
    query2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={})
    children = [dir1, dir2, query1, query2]

    self.home_dir.children.add(*children)

    # Test that all children directories and documents are returned
    response = self.client.get('/desktop/api2/doc', {'path': '/'})
    data = json.loads(response.content)
    assert_true('children' in data)
    assert_equal(5, data['count'])  # This includes the 4 docs and .Trash

    # Test filter type
    response = self.client.get('/desktop/api2/doc', {'path': '/', 'type': ['directory']})
    data = json.loads(response.content)
    assert_equal(['directory'], data['types'])
    assert_equal(3, data['count'])
    assert_true(all(doc['type'] == 'directory' for doc in data['children']))

    # Test search text
    response = self.client.get('/desktop/api2/doc', {'path': '/', 'text': 'query'})
    data = json.loads(response.content)
    assert_equal('query', data['text'])
    assert_equal(2, data['count'])
    assert_true(all('query' in doc['name'] for doc in data['children']))

    # Test pagination with limit
    response = self.client.get('/desktop/api2/doc', {'path': '/', 'page': 2, 'limit': 2})
    data = json.loads(response.content)
    assert_equal(5, data['count'])
    assert_equal(2, len(data['children']))


  def test_update_document(self):
    doc = Document2.objects.create(
      name='initial',
      description='initial desc',
      type='query-hive',
      owner=self.user,
      data={},
      parent_directory=self.home_dir
    )

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal('initial', data['document']['name'])
    assert_equal('initial desc', data['document']['description'])
    assert_equal('query-hive', data['document']['type'])

    # Update document's name and description
    response = self.client.post('/desktop/api2/doc/update', {'uuid': json.dumps(doc.uuid),
                                                             'name': 'updated',
                                                             'description': 'updated desc',
                                                             'type': 'bogus-type'})
    data = json.loads(response.content)
    assert_equal(0, data['status'])
    assert_true('document' in data, data)
    assert_equal('updated', data['document']['name'], data)
    assert_equal('updated desc', data['document']['description'], data)
    # Non-whitelisted attributes should remain unchanged
    assert_equal('query-hive', data['document']['type'], data)


  def test_document_trash(self):
    # Create document under home and directory under home with child document
    # /
    #   test_dir/
    #     query1.sql
    #   query2.sql
    dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    nested_query = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=dir)
    query = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # Test that .Trash is currently empty
    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash'})
    data = json.loads(response.content)
    assert_equal(0, data['count'])

    # Delete query2.sql
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(query.uuid)})
    data = json.loads(response.content)
    assert_equal(0, data['status'])

    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash'})
    data = json.loads(response.content)
    assert_equal(1, data['count'])
    assert_equal(data['children'][0]['uuid'], query.uuid)

    # Delete test_dir directory w/ contents
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(dir.uuid)})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash'})
    data = json.loads(response.content)
    assert_equal(2, data['count'])

    # Child document should be in trash too
    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash/test_dir'})
    data = json.loads(response.content)
    assert_equal(nested_query.uuid, data['children'][0]['uuid'])

    # Skip Trash (erase) on a directory with contents should erase all children recursively
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(dir.uuid), 'skip_trash': json.dumps(True)})
    data = json.loads(response.content)
    assert_equal(0, data['status'])
    assert_false(Document2.objects.filter(uuid=dir.uuid).exists())
    assert_false(Document2.objects.filter(uuid=nested_query.uuid).exists())

    # Verify that only doc in home is .Trash
    response = self.client.get('/desktop/api2/doc', {'path': '/'})
    data = json.loads(response.content)
    assert_true('children' in data)
    assert_equal(1, data['count'])
    assert_equal(Document2.TRASH_DIR, data['children'][0]['name'])


  def test_validate_name(self):
    # Test invalid names
    invalid_name = '/invalid'
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(self.home_dir.uuid), 'name': json.dumps(invalid_name)})
    data = json.loads(response.content)
    assert_equal(-1, data['status'], data)
    assert_true('invalid character' in data['message'])


  def test_validate_same_name_and_path(self):
    # Test that creating a document with the same name at the same path will auto-rename the document
    test_dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(self.home_dir.uuid), 'name': json.dumps('test_dir')})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    pattern = re.compile("test_dir \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    assert_true(pattern.match(data['directory']['name']), data)

    # But can create same name in different location
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(test_dir.uuid), 'name': json.dumps('test_dir')})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_equal('test_dir', data['directory']['name'])


  def test_validate_immutable_user_directories(self):
    # Test that home and Trash directories cannot be recreated or modified
    test_dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(test_dir.uuid), 'name': json.dumps(Document2.TRASH_DIR)})
    data = json.loads(response.content)
    assert_equal(-1, data['status'], data)
    assert_equal('Cannot create or modify directory with name: .Trash', data['message'])

    response = self.client.post('/desktop/api2/doc/move', {
        'source_doc_uuid': json.dumps(self.home_dir.uuid),
        'destination_doc_uuid': json.dumps(test_dir.uuid)
    })
    data = json.loads(response.content)
    assert_equal(-1, data['status'], data)
    assert_equal('Cannot create or modify directory with name: ', data['message'])

    trash_dir = Directory.objects.get(name=Document2.TRASH_DIR, owner=self.user)
    response = self.client.post('/desktop/api2/doc/move', {
        'source_doc_uuid': json.dumps(trash_dir.uuid),
        'destination_doc_uuid': json.dumps(test_dir.uuid)
    })
    data = json.loads(response.content)
    assert_equal(-1, data['status'], data)
    assert_equal('Cannot create or modify directory with name: .Trash', data['message'])


class TestDocument2Permissions(object):

  def setUp(self):
    self.client = make_logged_in_client(username="perm_user", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="perm_user")
    self.user_not_me = User.objects.get(username="not_perm_user")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

    self.default_group = get_default_user_group()

    # This creates the user directories for the new user
    response = self.client.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    assert_equal('/', data['document']['path'], data)

    self.home_dir = Document2.objects.get_home_directory(user=self.user)


  def test_default_permissions(self):
    # Tests that for a new doc by default, read/write perms are set to no users and no groups
    new_doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    response = self.client.get('/desktop/api2/doc/', {'uuid': new_doc.uuid})
    data = json.loads(response.content)
    assert_equal(new_doc.uuid, data['document']['uuid'], data)
    assert_true('perms' in data['document'])
    assert_equal({'read': {'users': [], 'groups': []}, 'write': {'users': [], 'groups': []}},
                 data['document']['perms'])


  def test_share_document_read_by_user(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # owner can view document
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(doc.uuid, data['document']['uuid'], data)

    # other user cannot view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(-1, data['status'])

    # Share read perm by users
    response = self.client.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(doc.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id,
            self.user_not_me.id
          ],
          'group_ids': [],
        },
        'write': {
          'user_ids': [],
          'group_ids': [],
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)
    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # other user can view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(doc.uuid, data['document']['uuid'], data)


  def test_share_document_read_by_group(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # owner can view document
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(doc.uuid, data['document']['uuid'], data)

    # other user cannot view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(-1, data['status'])

    response = self.client.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(doc.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': [
            self.default_group.id
          ]
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)
    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # other user can view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(doc.uuid, data['document']['uuid'], data)


  def test_share_document_write_by_user(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # other user cannot modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert_equal(-1, data['status'])

    # Share write perm by user
    response = self.client.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(doc.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [
            self.user_not_me.id
          ],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)
    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    # other user can modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert_equal(0, data['status'])


  def test_share_document_write_by_group(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # other user cannot modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert_equal(-1, data['status'])

    # Share write perm by group
    response = self.client.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(doc.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': [
            self.default_group.id
          ]
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)
    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    # other user can modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert_equal(0, data['status'])


  def test_share_directory(self):
    # Test that updating the permissions for a directory updates all nested documents accordingly, with file structure:
    # /
    #   test_dir/
    #     query1.sql
    #     nested_dir/
    #       query2.sql

    # All initially owned by self.user
    parent_dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    child_doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=parent_dir)
    nested_dir = Directory.objects.create(name='nested_dir', owner=self.user, parent_directory=parent_dir)
    nested_doc = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=nested_dir)

    for doc in [parent_dir, child_doc, nested_dir, nested_doc]:
      assert_true(doc.can_read(self.user))
      assert_true(doc.can_write(self.user))
      assert_false(doc.can_read(self.user_not_me))
      assert_false(doc.can_write(self.user_not_me))

    # Update parent_dir permissions to grant write permissions to default group
    response = self.client.post("/desktop/api2/doc/share", {
        'uuid': json.dumps(parent_dir.uuid),
        'data': json.dumps({
          'read': {
            'user_ids': [],
            'group_ids': []
          },
          'write': {
            'user_ids': [],
            'group_ids': [
              self.default_group.id
            ]
          }
        })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)
    for doc in [parent_dir, child_doc, nested_dir, nested_doc]:
      assert_true(doc.can_read(self.user))
      assert_true(doc.can_write(self.user))
      assert_true(doc.can_read(self.user_not_me))
      assert_true(doc.can_write(self.user_not_me))


  def test_get_shared_documents(self):
    not_shared = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    shared_1 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    shared_2 = Document2.objects.create(name='query3.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    shared_1.share(user=self.user, name='read', users=[self.user_not_me], groups=[])
    shared_2.share(user=self.user, name='read', users=[self.user_not_me], groups=[])

    # 2 shared docs should appear in the other user's shared documents response
    response = self.client_not_me.get('/desktop/api2/docs/', {'perms': 'shared'})
    data = json.loads(response.content)
    assert_true('documents' in data)
    assert_equal(2, data['count'])
    doc_names = [doc['name'] for doc in data['documents']]
    assert_true('query2.sql' in doc_names)
    assert_true('query3.sql' in doc_names)
    assert_false('query1.sql' in doc_names)

<<<<<<< HEAD
    # they should not appear in the other user's regular get_documents response
    response = self.client_not_me.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    doc_names = [doc['name'] for doc in data['children']]
    assert_false('query2.sql' in doc_names)
    assert_false('query3.sql' in doc_names)
=======
    # they should also appear in user's home directory get_documents response
    response = self.client_not_me.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    doc_names = [doc['name'] for doc in data['children']]
    assert_true('query2.sql' in doc_names)
    assert_true('query3.sql' in doc_names)
>>>>>>> upstream/master


  def test_get_shared_directories(self):
    # Tests that when fetching the shared documents for a user, they are grouped by top-level directory when possible
    # /
    #   dir1/
    #     query1.sql
    #   dir2/
    #     dir3/
    #       query2.sql
    #   query3.sql

    dir1 = Directory.objects.create(name='dir1', owner=self.user, parent_directory=self.home_dir)
    doc1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=dir1)
    dir2 = Directory.objects.create(name='dir2', owner=self.user, parent_directory=self.home_dir)
    dir3 = Directory.objects.create(name='dir3', owner=self.user, parent_directory=dir2)
    doc2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=dir3)
    doc3 = Document2.objects.create(name='query3.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    dir1.share(user=self.user, name='read', users=[], groups=[self.default_group])
    dir3.share(user=self.user, name='read', users=[], groups=[self.default_group])
    doc3.share(user=self.user, name='read', users=[], groups=[self.default_group])

    # 3 shared docs should appear, due to directory rollup
    response = self.client_not_me.get('/desktop/api2/docs/', {'perms': 'shared', 'flatten': 'false'})
    data = json.loads(response.content)
    assert_true('documents' in data)
    assert_equal(3, data['count'], data)
    doc_names = [doc['name'] for doc in data['documents']]
    assert_true('dir1' in doc_names)
    assert_true('dir3' in doc_names)
    assert_true('query3.sql' in doc_names)
    assert_false('dir2' in doc_names)

    # nested documents should not appear
    assert_false('query1.sql' in doc_names)
    assert_false('query2.sql' in doc_names)

    # but nested documents should still be shared/viewable by group
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc1.uuid})
    data = json.loads(response.content)
    assert_equal(doc1.uuid, data['document']['uuid'], data)

    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc2.uuid})
    data = json.loads(response.content)
    assert_equal(doc2.uuid, data['document']['uuid'], data)


  def test_search_documents(self):
    owned_dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    owned_query = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=owned_dir)
    owned_history = Document2.objects.create(name='history.sql', type='query-hive', owner=self.user, data={}, is_history=True, parent_directory=owned_dir)
    owned_workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=owned_dir)

    other_home_dir = Document2.objects.get_home_directory(user=self.user_not_me)
    not_shared = Document2.objects.create(name='other_query1.sql', type='query-hive', owner=self.user_not_me, data={}, parent_directory=other_home_dir)
    shared_1 = Document2.objects.create(name='other_query2.sql', type='query-hive', owner=self.user_not_me, data={}, parent_directory=other_home_dir)
    shared_2 = Document2.objects.create(name='other_query3.sql', type='query-hive', owner=self.user_not_me, data={}, parent_directory=other_home_dir)

    shared_1.share(user=self.user_not_me, name='read', users=[self.user], groups=[])
    shared_2.share(user=self.user_not_me, name='read', users=[], groups=[self.default_group])

    # 3 total docs (1 owned, 2 shared)
    response = self.client.get('/desktop/api2/docs/', {'type': 'query-hive'})
    data = json.loads(response.content)
    assert_true('documents' in data)
    assert_equal(3, data['count'])
    doc_names = [doc['name'] for doc in data['documents']]
    assert_true('query1.sql' in doc_names)
    assert_true('other_query2.sql' in doc_names)
    assert_true('other_query3.sql' in doc_names)

    # Return history docs
    response = self.client.get('/desktop/api2/docs/', {'type': 'query-hive', 'include_history': 'true'})
    data = json.loads(response.content)
    assert_true('documents' in data)
    assert_equal(4, data['count'])
    doc_names = [doc['name'] for doc in data['documents']]
    assert_true('history.sql' in doc_names)
<<<<<<< HEAD
=======


class TestDocument2ImportExport(object):

  def setUp(self):
    self.client = make_logged_in_client(username="perm_user", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="perm_user")
    self.user_not_me = User.objects.get(username="not_perm_user")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

    self.default_group = get_default_user_group()

    # This creates the user directories for the new user
    response = self.client.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    assert_equal('/', data['document']['path'], data)

    self.home_dir = Document2.objects.get_home_directory(user=self.user)
    self.not_me_home_dir = Document2.objects.get_home_directory(user=self.user_not_me)

  def test_import_owned_document(self):
    owned_query = Document2.objects.create(
      name='query.sql',
      type='query-hive',
      owner=self.user,
      data={'description': 'original_query'},
      parent_directory=self.home_dir
    )

    # Test that importing existing doc updates it and retains owner, UUID
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([owned_query.id]), 'format': 'json'})
    documents = response.content

    response = self.client.post('/desktop/api2/doc/import/', {'documents': documents})
    data = json.loads(response.content)

    assert_true('message' in data, data)
    assert_true('Installed 1 object' in data['message'], data)

    assert_equal(1, Document2.objects.filter(name='query.sql').count())
    imported_doc = Document2.objects.get(name='query.sql')
    assert_equal(owned_query.uuid, imported_doc.uuid)
    assert_equal(owned_query.owner, imported_doc.owner)

    # Test that import non-existing doc creates it, sets parent to home
    Document2.objects.get(name='query.sql').delete()
    assert_equal(0, Document2.objects.filter(name='query.sql').count())

    response = self.client.post('/desktop/api2/doc/import/', {'documents': documents})

    assert_equal(1, Document2.objects.filter(name='query.sql').count())
    imported_doc = Document2.objects.get(name='query.sql')
    assert_equal(owned_query.uuid, imported_doc.uuid)
    assert_equal(owned_query.owner, imported_doc.owner)
    assert_equal(owned_query.parent_directory, imported_doc.parent_directory)

  def test_import_nonowned_document(self):
    owned_query = Document2.objects.create(
      name='query.sql',
      type='query-hive',
      owner=self.user,
      data={'description': 'original_query'},
      parent_directory=self.home_dir
    )

    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([owned_query.id]), 'format': 'json'})
    documents = response.content

    # Test that importing non-owned doc copies it, sets parent to home
    response = self.client_not_me.post('/desktop/api2/doc/import/', {'documents': documents})

    assert_equal(2, Document2.objects.filter(name='query.sql').count())
    imported_doc = Document2.objects.get(name='query.sql', owner=self.user_not_me)
    assert_true(owned_query.uuid != imported_doc.uuid)
    assert_equal(self.user_not_me, imported_doc.owner)
    assert_equal(self.not_me_home_dir.uuid, imported_doc.parent_directory.uuid)
>>>>>>> upstream/master
