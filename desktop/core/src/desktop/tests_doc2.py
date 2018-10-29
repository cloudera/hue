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

from datetime import datetime

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_false, assert_true, assert_not_equal, assert_raises
from django.contrib.auth.models import User
from django.core import management
from django.db.utils import OperationalError

from desktop.converters import DocumentConverter
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.fs import ProxyFS
from desktop.lib.test_utils import grant_access
from desktop.models import Directory, Document2, Document
from notebook.models import import_saved_beeswax_query

from beeswax.models import SavedQuery
from beeswax.design import hql_query
from useradmin.models import get_default_user_group
from oozie.models2 import Workflow


class MockFs():
  def __init__(self):
    pass

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

    # Document UUID and XML UUID missmatch
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    doc.uuid = '1234-5678-9'
    doc.save()
    assert_not_equal(doc.uuid, data['document']['uuid'])
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(doc.uuid, data['document']['uuid'])


  def test_directory_create_and_rename(self):
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(self.home_dir.uuid), 'name': json.dumps('test_mkdir')})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('directory' in data)
    assert_equal(data['directory']['name'], 'test_mkdir', data)
    assert_equal(data['directory']['type'], 'directory', data)

    response = self.client.post('/desktop/api2/doc/update', {'uuid': json.dumps(data['directory']['uuid']),
                                                             'name': 'updated'})

    data = json.loads(response.content)
    assert_equal(0, data['status'])
    assert_equal('updated', data['document']['name'], data)


  def test_file_move(self):
    source_dir = Directory.objects.create(name='test_mv_file_src', owner=self.user, parent_directory=self.home_dir)
    target_dir = Directory.objects.create(name='test_mv_file_dst', owner=self.user, parent_directory=self.home_dir)
    doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=source_dir)
    orig_last_modified = doc.last_modified

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

    # Verify that last_modified is intact
    doc = Document2.objects.get(id = doc.id)
    assert_equal(orig_last_modified.strftime('%Y-%m-%dT%H:%M:%S'), doc.last_modified.strftime('%Y-%m-%dT%H:%M:%S'))

  def test_file_copy(self):

    workflow_doc = Document2.objects.create(name='Copy Test', type='oozie-workflow2', owner=self.user, data={},
                                            parent_directory=self.home_dir)
    Document.objects.link(workflow_doc, owner=workflow_doc.owner, name=workflow_doc.name,
                          description=workflow_doc.description, extra='workflow2')

    workflow = Workflow(user=self.user)
    workflow.update_name('Copy Test')
    workflow.set_workspace(self.user)

    # Monkey patch check_workspace for both new wor
    if not hasattr(Workflow, 'real_check_workspace'):
      Workflow.real_check_workspace = Workflow.check_workspace

    try:
      Workflow.check_workspace = lambda a, b, c: None
      workflow.check_workspace(MockFs(), self.user)
      workflow_doc.update_data({'workflow': workflow.get_data()['workflow']})
      workflow_doc.save()

      def copy_remote_dir(self, src, dst, *args, **kwargs):
        pass

      # Monkey patch as we don't want to do real copy
      if not hasattr(ProxyFS, 'real_copy_remote_dir'):
        ProxyFS.real_copy_remote_dir = ProxyFS.copy_remote_dir

      ProxyFS.copy_remote_dir = copy_remote_dir
      response = self.client.post('/desktop/api2/doc/copy', {
        'uuid': json.dumps(workflow_doc.uuid)
      })
    finally:
      Workflow.check_workspace = Workflow.real_check_workspace
      ProxyFS.copy_remote_dir = ProxyFS.real_copy_remote_dir

    copy_doc_json = json.loads(response.content)
    copy_doc = Document2.objects.get(type='oozie-workflow2', uuid=copy_doc_json['document']['uuid'])
    copy_workflow = Workflow(document=copy_doc)

    # Check if document2 and data are in sync
    assert_equal(copy_doc.name, copy_workflow.get_data()['workflow']['name'])
    assert_equal(copy_doc.uuid, copy_workflow.get_data()['workflow']['uuid'])

    assert_equal(copy_workflow.name, workflow.name + "-copy")
    assert_not_equal(copy_workflow.deployment_dir, workflow.deployment_dir)
    assert_not_equal(copy_doc.uuid, workflow_doc.uuid)
    assert_not_equal(copy_workflow.get_data()['workflow']['uuid'], workflow.get_data()['workflow']['uuid'])



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
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, search='foobar')
    query2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, search='barfoo')
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
    response = self.client.get('/desktop/api2/doc', {'path': '/', 'text': 'foo'})
    data = json.loads(response.content)
    assert_equal('foo', data['text'])
    assert_equal(2, data['count'])

    response = self.client.get('/desktop/api2/doc', {'path': '/', 'text': 'foobar'})
    data = json.loads(response.content)
    assert_equal(1, data['count'])

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
    assert_false(Document2.objects.get(uuid=query.uuid).is_trashed)
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(query.uuid)})
    data = json.loads(response.content)
    assert_equal(0, data['status'])
    assert_true(Document2.objects.get(uuid=query.uuid).is_trashed)

    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash'})
    data = json.loads(response.content)
    assert_equal(1, data['count'])
    assert_equal(data['children'][0]['uuid'], query.uuid)

    # Delete test_dir directory w/ contents
    assert_false(Document2.objects.get(uuid=dir.uuid).is_trashed)
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(dir.uuid)})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_true(Document2.objects.get(uuid=dir.uuid).is_trashed)

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


  def test_validate_circular_directory(self):
    # Test that saving a document with cycle raises an error, i.e. - This should fail:
    # a.parent_directory = b
    # b.parent_directory = c
    # c.parent_directory = a
    c_dir = Directory.objects.create(name='c', owner=self.user)
    b_dir = Directory.objects.create(name='b', owner=self.user, parent_directory=c_dir)
    a_dir = Directory.objects.create(name='a', owner=self.user, parent_directory=b_dir)
    response = self.client.post('/desktop/api2/doc/move', {
        'source_doc_uuid': json.dumps(c_dir.uuid),
        'destination_doc_uuid': json.dumps(a_dir.uuid)
    })
    data = json.loads(response.content)
    assert_equal(-1, data['status'], data)
    assert_true('circular dependency' in data['message'], data)

    # Test simple case where directory is saved to self as parent
    dir = Directory.objects.create(name='dir', owner=self.user)
    response = self.client.post('/desktop/api2/doc/move', {
      'source_doc_uuid': json.dumps(dir.uuid),
      'destination_doc_uuid': json.dumps(dir.uuid)
    })
    data = json.loads(response.content)
    assert_equal(-1, data['status'], data)
    assert_true('circular dependency' in data['message'], data)


  def test_api_get_data(self):
    doc_data = {'info': 'hello', 'is_history': False}
    doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data=json.dumps(doc_data))
    doc_data.update({'id': doc.id, 'uuid': doc.uuid})

    response = self.client.get('/desktop/api2/doc/', {
        'uuid': doc.uuid,
    })
    data = json.loads(response.content)

    assert_true('document' in data, data)
    assert_false(data['data'], data)

    response = self.client.get('/desktop/api2/doc/', {
        'uuid': doc.uuid,
        'data': 'true'
    })
    data = json.loads(response.content)

    assert_true('data' in data, data)
    assert_equal(data['data'], doc_data)

  def test_is_trashed_migration(self):

    # Skipping to prevent failing tests in TestOozieSubmissions
    raise SkipTest

    start_migration = '0024_auto__add_field_document2_is_managed'
    mid_migration = '0025_auto__add_field_document2_is_trashed'
    end_migration = '0026_change_is_trashed_default_to_false'
    APP = 'desktop'

    # Making sure Migration is up-to-date with fake migrations
    management.call_command('migrate', 'desktop', fake=True, verbosity=0)

    dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    query = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=dir)
    trashed_query = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=dir)
    trashed_query.trash()

    try:
      assert_false(dir.is_trashed)
      assert_false(query.is_trashed)
      assert_true(trashed_query.is_trashed)

      # Reverse migrate to 0025
      management.call_command('migrate', APP, mid_migration, verbosity=0)

      dir = Document2.objects.get(uuid=dir.uuid)
      query = Document2.objects.get(uuid=query.uuid)
      trashed_query = Document2.objects.get(uuid=trashed_query.uuid)
      assert_false(dir.is_trashed)
      assert_false(query.is_trashed)
      assert_true(trashed_query.is_trashed)

      # Reverse migrate to 0024. Deletes 'is_trashed' field from desktop_documents2
      management.call_command('migrate', APP, start_migration, verbosity=0)

      assert_raises(OperationalError, Document2.objects.get, uuid=dir.uuid)
      assert_raises(OperationalError, Document2.objects.get, uuid=query.uuid)
      assert_raises(OperationalError, Document2.objects.get, uuid=trashed_query.uuid)

      # Forward migrate to 0025
      management.call_command('migrate', APP, mid_migration, verbosity=0)
      dir = Document2.objects.get(uuid=dir.uuid)
      query = Document2.objects.get(uuid=query.uuid)
      trashed_query = Document2.objects.get(uuid=trashed_query.uuid)
      assert_true(dir.is_trashed is None)
      assert_true(query.is_trashed is None)
      assert_true(trashed_query.is_trashed is None)

      # Forward migrate to 0026
      management.call_command('migrate', APP, end_migration, verbosity=0)
      dir = Document2.objects.get(uuid=dir.uuid)
      query = Document2.objects.get(uuid=query.uuid)
      trashed_query = Document2.objects.get(uuid=trashed_query.uuid)
      assert_true(dir.is_trashed is None)
      assert_true(query.is_trashed is None)
      assert_true(trashed_query.is_trashed is None)

      # New Documents should have is_trashed=False
      query1 = Document2.objects.create(name='new_query.sql', type='query-hive', owner=self.user, data={}, parent_directory=dir)
      assert_true(query1.is_trashed is False)

      # Create history doc
      query1.is_history = True
      query1.save()

      query1 = Document2.objects.get(uuid=query1.uuid)
      query1_last_modified = query1.last_modified
      dir_last_modified = dir.last_modified
      query_last_modified = query.last_modified
      trashed_query_last_modified = trashed_query.last_modified

      # Converter sets is_trashed=True for currently trashed docs
      converter = DocumentConverter(self.user)
      converter.convert()
      trashed_query = Document2.objects.get(uuid=trashed_query.uuid)
      dir = Document2.objects.get(uuid=dir.uuid)
      query = Document2.objects.get(uuid=query.uuid)
      assert_true(trashed_query.is_trashed)
      assert_true(dir.is_trashed is False)
      assert_true(query.is_trashed is False)

      # last_modified should be retained post conversion
      assert_equal(dir_last_modified, dir.last_modified)
      assert_equal(query_last_modified, query.last_modified)
      assert_equal(trashed_query_last_modified, trashed_query.last_modified)

      query1 = Document2.objects.get(uuid=query1.uuid)
      assert_equal(query1_last_modified, query1.last_modified)
    finally:
      # Delete docs
      dir.delete()
      query.delete()
      query1.delete()
      trashed_query.delete()


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

    # other user can share document with read permissions
    response = self.client_not_me.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(doc.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [],
          'group_ids': [
            self.default_group.id
          ],
        },
        'write': {
          'user_ids': [],
          'group_ids': [],
        }
      })
    })
    assert_equal(0, json.loads(response.content)['status'], response.content)

    # other user cannot share document with write permissions
    response = self.client_not_me.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(doc.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [],
          'group_ids': [],
        },
        'write': {
          'user_ids': [],
          'group_ids': [
            self.default_group.id
          ],
        }
      })
    })
    assert_equal(-1, json.loads(response.content)['status'], response.content)


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

    # they should also appear in user's home directory get_documents response
    response = self.client_not_me.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    doc_names = [doc['name'] for doc in data['children']]
    assert_true('query2.sql' in doc_names)
    assert_true('query3.sql' in doc_names)


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


  def test_inherit_parent_permissions(self):
    # Tests that when saving a document to a shared directory, the doc/dir inherits same permissions

    dir1 = Directory.objects.create(name='dir1', owner=self.user, parent_directory=self.home_dir)

    dir1.share(user=self.user, name='read', users=[], groups=[self.default_group])
    dir1.share(user=self.user, name='write', users=[self.user_not_me], groups=[])

    doc1 = Document2.objects.create(name='doc1', owner=self.user, parent_directory=dir1)

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc1.uuid})
    data = json.loads(response.content)
    assert_equal([{'id': self.default_group.id, 'name': self.default_group.name}],
                 data['document']['perms']['read']['groups'], data)
    assert_equal([{'id': self.user_not_me.id, 'username': self.user_not_me.username}],
                 data['document']['perms']['write']['users'], data)


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

  def test_x_share_directory_y_add_file_x_share(self):
    # Test that when another User, Y, adds a doc to dir shared by User X, User X doesn't fail to share the dir next time:
    # /
    #   test_dir/
    #     query1.sql


    # Dir owned by self.user
    parent_dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    child_doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=parent_dir)

    user_y = User.objects.create(username='user_y', password="user_y")

    # Share the dir with user_not_me
    response = self.client.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(parent_dir.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [],
          'group_ids': []
        },
        'write': {
          'user_ids': [user_y.id],
          'group_ids': []
        }
      })
    })

    user_y_child_doc = Document2.objects.create(name='other_query1.sql', type='query-hive', owner=user_y, data={},
                                          parent_directory=parent_dir)

    share_test_user = User.objects.create(username='share_test_user', password="share_test_user")

    # Share the dir with another user - share_test_user
    response = self.client.post("/desktop/api2/doc/share", {
      'uuid': json.dumps(parent_dir.uuid),
      'data': json.dumps({
        'read': {
          'user_ids': [],
          'group_ids': []
        },
        'write': {
          'user_ids': [share_test_user.id],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)
    for doc in [parent_dir, child_doc, user_y_child_doc]:
      assert_true(doc.can_read(self.user))
      assert_true(doc.can_write(self.user))
      assert_true(doc.can_read(share_test_user))
      assert_true(doc.can_write(share_test_user))


  def test_unicode_name(self):
    doc = Document2.objects.create(name='My Bundle a voté « non » à l’accord', type='oozie-workflow2', owner=self.user,
                                   data={}, parent_directory=self.home_dir)

    # Verify that home directory contents return correctly
    response = self.client.get('/desktop/api2/doc/', {'uuid': self.home_dir.uuid})
    data = json.loads(response.content)
    assert_equal(0, data['status'])

    # Verify that the doc's path is escaped
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(0, data['status'])
    path = data['document']['path']
    assert_equal('/My%20Bundle%20a%20vot%C3%A9%20%C2%AB%20non%20%C2%BB%20%C3%A0%20l%E2%80%99accord', path)


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

  def test_export_documents_with_dependencies(self):
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    query2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    query3 = Document2.objects.create(name='query3.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir, is_history=True)
    workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir)
    workflow.dependencies.add(query1)
    workflow.dependencies.add(query2)
    workflow.dependencies.add(query3)

    # Test that exporting workflow should export all dependencies except history
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id]), 'format': 'json'})
    documents = json.loads(response.content)
    documents = json.loads(documents)

    assert_equal(3, len(documents))
    assert_true('test.wf' in [doc['fields']['name'] for doc in documents])
    assert_true('query1.sql' in [doc['fields']['name'] for doc in documents])
    assert_true('query2.sql' in [doc['fields']['name'] for doc in documents])
    assert_false('query3.sql' in [doc['fields']['name'] for doc in documents])

    # Test that exporting multiple workflows with overlapping dependencies works
    workflow2 = Document2.objects.create(name='test2.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir)
    workflow2.dependencies.add(query1)

    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id, workflow2.id]), 'format': 'json'})
    documents = json.loads(response.content)
    documents = json.loads(documents)

    assert_equal(4, len(documents))
    assert_true('test.wf' in [doc['fields']['name'] for doc in documents])
    assert_true('test2.wf' in [doc['fields']['name'] for doc in documents])
    assert_true('query1.sql' in [doc['fields']['name'] for doc in documents])
    assert_true('query2.sql' in [doc['fields']['name'] for doc in documents])


  def test_export_documents_file_name(self):
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={},
                                      parent_directory=self.home_dir)
    query2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={},
                                      parent_directory=self.home_dir)
    query3 = Document2.objects.create(name='query3.sql', type='query-hive', owner=self.user, data={},
                                      parent_directory=self.home_dir, is_history=True)
    workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={},
                                        parent_directory=self.home_dir)
    workflow.dependencies.add(query1)
    workflow.dependencies.add(query2)
    workflow.dependencies.add(query3)

    # Test that exporting multiple workflows with overlapping dependencies works
    workflow2 = Document2.objects.create(name='test2.wf', type='oozie-workflow2', owner=self.user, data={},
                                         parent_directory=self.home_dir)
    workflow2.dependencies.add(query1)

    # Test that exporting to a file includes the date and number of documents in the filename
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id, workflow2.id])})
    assert_equal(response['Content-Disposition'], 'attachment; filename="hue-documents-%s-(4).json"' % datetime.today().strftime('%Y-%m-%d'))

    # Test that exporting single file gets the name of the document in the filename
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id])})
    assert_equal(response['Content-Disposition'], 'attachment; filename="' + workflow.name + '.json"')


  def test_export_directories_with_children(self):
    # Test that exporting a directory exports children docs
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

    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([dir1.id, dir2.id, doc3.id]), 'format': 'json'})
    documents = json.loads(response.content)
    documents = json.loads(documents)

    assert_equal(6, len(documents))
    assert_true('dir1' in [doc['fields']['name'] for doc in documents])
    assert_true('query1.sql' in [doc['fields']['name'] for doc in documents])
    assert_true('dir2' in [doc['fields']['name'] for doc in documents])
    assert_true('dir3' in [doc['fields']['name'] for doc in documents])
    assert_true('query2.sql' in [doc['fields']['name'] for doc in documents])
    assert_true('query3.sql' in [doc['fields']['name'] for doc in documents])


  def test_import_owned_document(self):
    owned_query = Document2.objects.create(
      name='query.sql',
      type='query-hive',
      owner=self.user,
      data=json.dumps({'description': 'original_query'}),
      parent_directory=self.home_dir
    )

    # Test that importing existing doc updates it and retains owner, UUID
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([owned_query.id]), 'format': 'json'})
    documents = response.content

    response = self.client.post('/desktop/api2/doc/import/', {'documents': documents})
    data = json.loads(response.content)

    assert_true('message' in data, data)
    assert_true('Installed 1 object' in data['message'], data)
    assert_true('count' in data)
    assert_equal(1, data['count'])
    assert_true('created_count' in data)
    assert_equal(0, data['created_count'])
    assert_true('updated_count' in data)
    assert_equal(1, data['updated_count'])
    assert_true('documents' in data)
    assert_true('name' in data['documents'][0])
    assert_equal('query.sql', data['documents'][0]['name'])
    assert_true('type' in data['documents'][0])
    assert_equal('query-hive', data['documents'][0]['type'])
    assert_true('owner' in data['documents'][0])
    assert_equal('perm_user', data['documents'][0]['owner'])

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
      data=json.dumps({'description': 'original_query'}),
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

    data = json.loads(response.content)
    assert_true('count' in data)
    assert_equal(1, data['count'])
    assert_true('created_count' in data)
    assert_equal(1, data['created_count'])
    assert_true('updated_count' in data)
    assert_equal(0, data['updated_count'])

  def test_import_with_history_dependencies(self):
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={},
                                      parent_directory=self.home_dir)
    query2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={},
                                      parent_directory=self.home_dir, is_history=True)
    workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={},
                                        parent_directory=self.home_dir)
    workflow.dependencies.add(query1)
    workflow.dependencies.add(query2)

    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id]), 'format': 'json'})
    documents = response.content

    # Delete previous entries from DB, so when you import it creates them
    query1.delete()
    query2.delete()
    workflow.delete()

    response = self.client_not_me.post('/desktop/api2/doc/import/', {'documents': documents})
    assert_true(Document2.objects.filter(name='query1.sql').exists())
    assert_false(Document2.objects.filter(name='query2.sql').exists())

    data = json.loads(response.content)
    assert_true('count' in data)
    assert_equal(2, data['count'])
    assert_true('created_count' in data)
    assert_equal(2, data['created_count'])
    assert_true('updated_count' in data)
    assert_equal(0, data['updated_count'])
