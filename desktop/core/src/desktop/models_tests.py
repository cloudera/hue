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
from builtins import object
from datetime import datetime
from unittest.mock import patch

import pytest
from django.core import management
from django.db.utils import OperationalError

from beeswax.design import hql_query
from beeswax.models import SavedQuery
from desktop.conf import RAZ, has_connectors
from desktop.converters import DocumentConverter
from desktop.lib.connectors.models import Connector
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.fs import ProxyFS
from desktop.lib.test_utils import grant_access
from desktop.models import ClusterConfig, Directory, Document, Document2, Document2Permission, get_remote_home_storage
from filebrowser.conf import REMOTE_STORAGE_HOME
from notebook.models import import_saved_beeswax_query
from useradmin.models import User, get_default_user_group

try:
  from oozie.models2 import Workflow

  has_oozie = True
except RuntimeError:
  has_oozie = False


class MockFs(object):
  def __init__(self):
    pass


@pytest.mark.django_db
class TestClusterConfig(object):
  def setup_method(self):
    self.client = make_logged_in_client(username="test", groupname="test", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

    self.client_not_me = make_logged_in_client(username="test_not_me", groupname="test_not_me", recreate=True, is_superuser=False)
    self.user_not_me = User.objects.get(username="test_not_me")

  def test_get_fs(self):
    if not has_connectors():
      pytest.skip("Skipping Test")

    with patch('desktop.models.appmanager.get_apps_dict') as get_apps_dict:
      with patch('desktop.models.fsmanager.is_enabled_and_has_access') as is_enabled_and_has_access:
        # filebrowser

        ClusterConfig(user=self.user)

  def test_get_main_quick_action(self):
    with patch('desktop.models.get_user_preferences') as get_user_preferences:
      get_user_preferences.return_value = json.dumps({'app': 'editor', 'interpreter': 1})
      apps = {'editor': {'interpreters': [{'type': 1, 'name': 'SQL'}, {'type': 2, 'name': 'Stream SQL'}]}}

      main_app = ClusterConfig(user=self.user, apps=apps).get_main_quick_action(apps=apps)

      assert {'type': 1, 'name': 'SQL'}, main_app

  def test_get_remote_storage_home(self):
    # When REMOTE_STORAGE_HOME is set.
    resets = [REMOTE_STORAGE_HOME.set_for_testing('hdfs://gethue/dir')]

    try:
      remote_home_storage = get_remote_home_storage(self.user)
      assert remote_home_storage == 'hdfs://gethue/dir'

      remote_home_storage = get_remote_home_storage(self.user_not_me)
      assert remote_home_storage == 'hdfs://gethue/dir'
    finally:
      for reset in resets:
        reset()

    # When REMOTE_STORAGE_HOME is set and ends with /user in RAZ environment.
    resets = [RAZ.IS_ENABLED.set_for_testing(True), REMOTE_STORAGE_HOME.set_for_testing('abfs://gethue-container/user')]

    try:
      remote_home_storage = get_remote_home_storage(self.user)
      assert remote_home_storage == 'abfs://gethue-container/user/test'

      remote_home_storage = get_remote_home_storage(self.user_not_me)
      assert remote_home_storage == 'abfs://gethue-container/user/test_not_me'
    finally:
      for reset in resets:
        reset()

    # When REMOTE_STORAGE_HOME is not set.
    resets = [REMOTE_STORAGE_HOME.set_for_testing(None)]

    try:
      remote_home_storage = get_remote_home_storage(self.user)
      assert remote_home_storage is None

      remote_home_storage = get_remote_home_storage(self.user_not_me)
      assert remote_home_storage is None
    finally:
      for reset in resets:
        reset()


@pytest.mark.django_db
class TestDocument2(object):
  def setup_method(self):
    self.default_group = get_default_user_group()

    self.client = make_logged_in_client(username="doc2", groupname=self.default_group.name, recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_doc2", groupname=self.default_group.name, recreate=True, is_superuser=False)

    self.user = User.objects.get(username="doc2")
    self.user_not_me = User.objects.get(username="not_doc2")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

    # This creates the user directories for the new users
    response = self.client.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    assert '/' == data['document']['path'], data
    response = self.client_not_me.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    assert '/' == data['document']['path'], data

    self.home_dir = Document2.objects.get_home_directory(user=self.user)

  def test_trash_directory(self):
    assert Directory.objects.filter(owner=self.user, name=Document2.TRASH_DIR, type='directory').exists()

  def test_document_create(self):
    sql = 'SELECT * FROM sample_07'

    design = hql_query(sql)

    # is_auto
    # is_trashed
    # is_redacted
    old_query = SavedQuery.objects.create(
      type=SavedQuery.TYPES_MAPPING['hql'], owner=self.user, data=design.dumps(), name='See examples', desc='Example of old format'
    )

    try:
      new_query = import_saved_beeswax_query(old_query)
      new_query_data = new_query.get_data()

      assert 'query-hive' == new_query_data['type']
      assert 'See examples' == new_query_data['name']
      assert 'Example of old format' == new_query_data['description']

      assert 'ready' == new_query_data['snippets'][0]['status']
      assert 'See examples' == new_query_data['snippets'][0]['name']
      assert 'SELECT * FROM sample_07' == new_query_data['snippets'][0]['statement_raw']

      assert [] == new_query_data['snippets'][0]['properties']['settings']
      assert [] == new_query_data['snippets'][0]['properties']['files']
      assert [] == new_query_data['snippets'][0]['properties']['functions']
    finally:
      old_query.delete()

  def test_get_document(self):
    doc = Document2.objects.create(name='test_doc', type='query-hive', owner=self.user, data={})
    self.home_dir.children.add(doc)
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert 'document' in data
    assert doc.uuid == data['document']['uuid']

    # Invalid uuid returns error
    response = self.client.get('/desktop/api2/doc/', {'uuid': '1234-5678-9'})
    data = json.loads(response.content)
    assert -1 == data['status']
    assert 'not found' in data['message']

    # Document UUID and XML UUID missmatch
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    doc.uuid = '1234-5678-9'
    doc.save()
    assert doc.uuid != data['document']['uuid']
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert doc.uuid == data['document']['uuid']

  def test_directory_create_and_rename(self):
    response = self.client.post(
      '/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(self.home_dir.uuid), 'name': json.dumps('test_mkdir')}
    )
    data = json.loads(response.content)

    assert 0 == data['status'], data
    assert 'directory' in data
    assert data['directory']['name'] == 'test_mkdir', data
    assert data['directory']['type'] == 'directory', data

    response = self.client.post('/desktop/api2/doc/update', {'uuid': json.dumps(data['directory']['uuid']), 'name': 'updated'})

    data = json.loads(response.content)
    assert 0 == data['status']
    assert 'updated' == data['document']['name'], data

  def test_file_move(self):
    source_dir = Directory.objects.create(name='test_mv_file_src', owner=self.user, parent_directory=self.home_dir)
    target_dir = Directory.objects.create(name='test_mv_file_dst', owner=self.user, parent_directory=self.home_dir)
    doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=source_dir)
    orig_last_modified = doc.last_modified

    # Verify original paths before move operation
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert '/test_mv_file_src' == data['document']['path']

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert '/test_mv_file_src/query1.sql' == data['document']['path']

    response = self.client.post(
      '/desktop/api2/doc/move', {'source_doc_uuid': json.dumps(doc.uuid), 'destination_doc_uuid': json.dumps(target_dir.uuid)}
    )
    data = json.loads(response.content)
    assert 0 == data['status'], data

    # Verify that the paths are updated
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert not any(doc['uuid'] == doc.uuid for doc in data['children']), data['children']

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert '/test_mv_file_dst/query1.sql' == data['document']['path']

    # Verify that last_modified is intact
    doc = Document2.objects.get(id=doc.id)
    assert orig_last_modified.strftime('%Y-%m-%dT%H:%M:%S') == doc.last_modified.strftime('%Y-%m-%dT%H:%M:%S')

  def test_file_copy(self):
    if not has_oozie:
      pytest.skip("Skipping Test")

    workflow_doc = Document2.objects.create(
      name='Copy Test', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir
    )
    Document.objects.link(
      workflow_doc, owner=workflow_doc.owner, name=workflow_doc.name, description=workflow_doc.description, extra='workflow2'
    )

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
      response = self.client.post('/desktop/api2/doc/copy', {'uuid': json.dumps(workflow_doc.uuid)})
    finally:
      Workflow.check_workspace = Workflow.real_check_workspace
      ProxyFS.copy_remote_dir = ProxyFS.real_copy_remote_dir

    copy_doc_json = json.loads(response.content)
    copy_doc = Document2.objects.get(type='oozie-workflow2', uuid=copy_doc_json['document']['uuid'])
    copy_workflow = Workflow(document=copy_doc)

    # Check if document2 and data are in sync
    assert copy_doc.name == copy_workflow.get_data()['workflow']['name']
    assert copy_doc.uuid == copy_workflow.get_data()['workflow']['uuid']

    assert copy_workflow.name == workflow.name + "-copy"
    assert copy_workflow.deployment_dir != workflow.deployment_dir
    assert copy_doc.uuid != workflow_doc.uuid
    assert copy_workflow.get_data()['workflow']['uuid'] != workflow.get_data()['workflow']['uuid']

  def test_copy_of_shared_doc_in_home(self):
    user_not_me_home_dir = Document2.objects.get_home_directory(user=self.user_not_me)

    doc_to_copy = Document2.objects.create(
      name='new_doc', type='query-hive', owner=self.user_not_me, data={}, parent_directory=user_not_me_home_dir
    )
    # "user_not_me" can view document
    assert doc_to_copy.can_read(self.user_not_me)
    # "user" cannot view document
    assert not doc_to_copy.can_read(self.user)
    # "user_not_me" shares with user
    doc_to_copy.share(self.user_not_me, users=[self.user])
    # "user" can view document
    assert doc_to_copy.can_read(self.user)
    # The doc resides in the home directory of "user_not_me"
    assert doc_to_copy.parent_directory == user_not_me_home_dir

    # "user" makes a copy of the doc owned by "user_not_me" which resides in the home directory of "user_not_me"
    copied_doc = doc_to_copy.copy(name=doc_to_copy.name + '-copy', owner=self.user)

    # The copy should be located in the home folder of "user"
    user_home_dir = Document2.objects.get_home_directory(user=self.user)
    assert user_home_dir != user_not_me_home_dir
    assert copied_doc.parent_directory == user_home_dir

  def test_copy_of_doc_in_shared_folder(self):
    user_not_me_home_dir = Document2.objects.get_home_directory(user=self.user_not_me)
    user_not_me_shared_dir = Directory.objects.create(name='test_dir', owner=self.user_not_me, parent_directory=user_not_me_home_dir)

    doc_to_copy = Document2.objects.create(
        name='new_doc', type='query-hive', owner=self.user_not_me, data={}, parent_directory=user_not_me_shared_dir
    )
    # "user_not_me" can view document
    assert doc_to_copy.can_read(self.user_not_me)
    # "user" cannot view document
    assert not doc_to_copy.can_read(self.user)
    # "user_not_me" shares the parent directory with user
    user_not_me_shared_dir.share(self.user_not_me, users=[self.user])
    # "user" can view document
    assert doc_to_copy.can_read(self.user)
    # The doc resides in the shared directory of "user_not_me"
    assert doc_to_copy.parent_directory == user_not_me_shared_dir

    # "user" makes a copy of the doc owned by "user_not_me" which resides in the shared directory of "user_not_me"
    copied_doc = doc_to_copy.copy(name=doc_to_copy.name + '-copy', owner=self.user)

    # The copy should be located in the shared directory of "user_not_me"
    assert copied_doc.parent_directory == user_not_me_shared_dir

  def test_directory_move(self):
    source_dir = Directory.objects.create(name='test_mv', owner=self.user, parent_directory=self.home_dir)
    target_dir = Directory.objects.create(name='test_mv_dst', owner=self.user, parent_directory=self.home_dir)
    doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=source_dir)

    # Verify original paths before move operation
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert '/test_mv' == data['document']['path']

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert '/test_mv/query1.sql' == data['document']['path']

    response = self.client.post(
      '/desktop/api2/doc/move',
      {
        'source_doc_uuid': json.dumps(Directory.objects.get(owner=self.user, name='test_mv').uuid),
        'destination_doc_uuid': json.dumps(Directory.objects.get(owner=self.user, name='test_mv_dst').uuid),
      },
    )
    data = json.loads(response.content)
    assert 0 == data['status'], data

    # Verify that the paths are updated
    response = self.client.get('/desktop/api2/doc/', {'uuid': source_dir.uuid})
    data = json.loads(response.content)
    assert '/test_mv_dst/test_mv' == data['document']['path']

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert '/test_mv_dst/test_mv/query1.sql' == data['document']['path']

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
    assert 'children' in data
    assert 5 == data['count']  # This includes the 4 docs and .Trash and Gist

    # Test filter type
    response = self.client.get('/desktop/api2/doc', {'path': '/', 'type': ['directory']})
    data = json.loads(response.content)
    assert ['directory'] == data['types']
    assert 3 == data['count']
    assert all(doc['type'] == 'directory' for doc in data['children'])

    # Test search text
    response = self.client.get('/desktop/api2/doc', {'path': '/', 'text': 'foo'})
    data = json.loads(response.content)
    assert 'foo' == data['text']
    assert 2 == data['count']

    response = self.client.get('/desktop/api2/doc', {'path': '/', 'text': 'foobar'})
    data = json.loads(response.content)
    assert 1 == data['count']

    # Test pagination with limit
    response = self.client.get('/desktop/api2/doc', {'path': '/', 'page': 2, 'limit': 2})
    data = json.loads(response.content)
    assert 5 == data['count']
    assert 2 == len(data['children'])

  def test_update_document(self):
    doc = Document2.objects.create(
      name='initial', description='initial desc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir
    )

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert 'initial' == data['document']['name']
    assert 'initial desc' == data['document']['description']
    assert 'query-hive' == data['document']['type']

    # Update document's name and description
    response = self.client.post(
      '/desktop/api2/doc/update', {'uuid': json.dumps(doc.uuid), 'name': 'updated', 'description': 'updated desc', 'type': 'bogus-type'}
    )
    data = json.loads(response.content)
    assert 0 == data['status']
    assert 'document' in data, data
    assert 'updated' == data['document']['name'], data
    assert 'updated desc' == data['document']['description'], data
    # Non-whitelisted attributes should remain unchanged
    assert 'query-hive' == data['document']['type'], data

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
    assert 0 == data['count']

    # Delete query2.sql
    assert not Document2.objects.get(uuid=query.uuid).is_trashed
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(query.uuid)})
    data = json.loads(response.content)
    assert 0 == data['status']
    assert Document2.objects.get(uuid=query.uuid).is_trashed

    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash'})
    data = json.loads(response.content)
    assert 1 == data['count']
    assert data['children'][0]['uuid'] == query.uuid

    # Delete test_dir directory w/ contents
    assert not Document2.objects.get(uuid=dir.uuid).is_trashed
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(dir.uuid)})
    data = json.loads(response.content)
    assert 0 == data['status'], data
    assert Document2.objects.get(uuid=dir.uuid).is_trashed

    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash'})
    data = json.loads(response.content)
    assert 2 == data['count']

    # Child document should be in trash too
    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash/test_dir'})
    data = json.loads(response.content)
    assert nested_query.uuid == data['children'][0]['uuid']

    # Skip Trash (erase) on a directory with contents should erase all children recursively
    response = self.client.post('/desktop/api2/doc/delete', {'uuid': json.dumps(dir.uuid), 'skip_trash': json.dumps(True)})
    data = json.loads(response.content)
    assert 0 == data['status']
    assert not Document2.objects.filter(uuid=dir.uuid).exists()
    assert not Document2.objects.filter(uuid=nested_query.uuid).exists()

    # Verify that only doc in home is .Trash
    response = self.client.get('/desktop/api2/doc', {'path': '/'})
    data = json.loads(response.content)
    assert 'children' in data
    assert 1 == data['count']
    assert Document2.TRASH_DIR in [f['name'] for f in data['children']]

  def test_get_history(self):
    history = Document2.objects.get_history(user=self.user, doc_type='query-hive')
    assert not history.filter(name='test_get_history').exists()

    query = Document2.objects.create(name='test_get_history', type='query-hive', owner=self.user, is_history=True)

    try:
      history = Document2.objects.get_history(user=self.user, doc_type='query-hive')
      assert history.filter(name='test_get_history').exists()
    finally:
      query.delete()

  def test_get_history_with_connector(self):
    connector = Connector.objects.create(name='MySql', dialect='mysql')

    query = Document2.objects.create(name='test_get_history', type='query-hive', owner=self.user, is_history=False, connector=connector)

    try:
      history = Document2.objects.get_history(user=self.user, doc_type='query-hive', connector_id=connector.id)
      assert not history.filter(name='test_get_history').exists()

      query.is_history = True
      query.save()

      history = Document2.objects.get_history(user=self.user, doc_type='query-hive', connector_id=connector.id)
      assert history.filter(name='test_get_history').exists()
    finally:
      query.delete()
      connector.delete()

  def test_validate_immutable_user_directories(self):
    # Test that home and Trash directories cannot be recreated or modified
    test_dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    response = self.client.post(
      '/desktop/api2/doc/mkdir', {'parent_uuid': json.dumps(test_dir.uuid), 'name': json.dumps(Document2.TRASH_DIR)}
    )
    data = json.loads(response.content)
    assert -1 == data['status'], data
    assert 'Cannot create or modify directory with name: .Trash' == data['message']

    response = self.client.post(
      '/desktop/api2/doc/move', {'source_doc_uuid': json.dumps(self.home_dir.uuid), 'destination_doc_uuid': json.dumps(test_dir.uuid)}
    )
    data = json.loads(response.content)
    assert -1 == data['status'], data
    assert 'Cannot create or modify directory with name: ' == data['message']

    trash_dir = Directory.objects.get(name=Document2.TRASH_DIR, owner=self.user)
    response = self.client.post(
      '/desktop/api2/doc/move', {'source_doc_uuid': json.dumps(trash_dir.uuid), 'destination_doc_uuid': json.dumps(test_dir.uuid)}
    )
    data = json.loads(response.content)
    assert -1 == data['status'], data
    assert 'Cannot create or modify directory with name: .Trash' == data['message']

  def test_validate_circular_directory(self):
    # Test that saving a document with cycle raises an error, i.e. - This should fail:
    # a.parent_directory = b
    # b.parent_directory = c
    # c.parent_directory = a
    c_dir = Directory.objects.create(name='c', owner=self.user)
    b_dir = Directory.objects.create(name='b', owner=self.user, parent_directory=c_dir)
    a_dir = Directory.objects.create(name='a', owner=self.user, parent_directory=b_dir)
    response = self.client.post(
      '/desktop/api2/doc/move', {'source_doc_uuid': json.dumps(c_dir.uuid), 'destination_doc_uuid': json.dumps(a_dir.uuid)}
    )
    data = json.loads(response.content)
    assert -1 == data['status'], data
    assert 'circular dependency' in data['message'], data

    # Test simple case where directory is saved to self as parent
    dir = Directory.objects.create(name='dir', owner=self.user)
    response = self.client.post(
      '/desktop/api2/doc/move', {'source_doc_uuid': json.dumps(dir.uuid), 'destination_doc_uuid': json.dumps(dir.uuid)}
    )
    data = json.loads(response.content)
    assert -1 == data['status'], data
    assert 'circular dependency' in data['message'], data

  def test_api_get_data(self):
    doc_data = {'info': 'hello', 'is_history': False}
    doc = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data=json.dumps(doc_data))
    doc_data.update({'id': doc.id, 'uuid': doc.uuid})

    response = self.client.get(
      '/desktop/api2/doc/',
      {
        'uuid': doc.uuid,
      },
    )
    data = json.loads(response.content)

    assert 'document' in data, data
    assert not data['data'], data

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid, 'data': 'true'})
    data = json.loads(response.content)

    assert 'data' in data, data
    assert data['data'] == doc_data

  def test_is_trashed_migration(self):
    # Skipping to prevent failing tests in TestOozieSubmissions
    pytest.skip("Skipping Test")

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
      assert not dir.is_trashed
      assert not query.is_trashed
      assert trashed_query.is_trashed

      # Reverse migrate to 0025
      management.call_command('migrate', APP, mid_migration, verbosity=0)

      dir = Document2.objects.get(uuid=dir.uuid)
      query = Document2.objects.get(uuid=query.uuid)
      trashed_query = Document2.objects.get(uuid=trashed_query.uuid)
      assert not dir.is_trashed
      assert not query.is_trashed
      assert trashed_query.is_trashed

      # Reverse migrate to 0024. Deletes 'is_trashed' field from desktop_documents2
      management.call_command('migrate', APP, start_migration, verbosity=0)

      with pytest.raises(OperationalError):
        Document2.objects.get(uuid=dir.uuid)
      with pytest.raises(OperationalError):
        Document2.objects.get(uuid=query.uuid)
      with pytest.raises(OperationalError):
        Document2.objects.get(uuid=trashed_query.uuid)

      # Forward migrate to 0025
      management.call_command('migrate', APP, mid_migration, verbosity=0)
      dir = Document2.objects.get(uuid=dir.uuid)
      query = Document2.objects.get(uuid=query.uuid)
      trashed_query = Document2.objects.get(uuid=trashed_query.uuid)
      assert dir.is_trashed is None
      assert query.is_trashed is None
      assert trashed_query.is_trashed is None

      # Forward migrate to 0026
      management.call_command('migrate', APP, end_migration, verbosity=0)
      dir = Document2.objects.get(uuid=dir.uuid)
      query = Document2.objects.get(uuid=query.uuid)
      trashed_query = Document2.objects.get(uuid=trashed_query.uuid)
      assert dir.is_trashed is None
      assert query.is_trashed is None
      assert trashed_query.is_trashed is None

      # New Documents should have is_trashed=False
      query1 = Document2.objects.create(name='new_query.sql', type='query-hive', owner=self.user, data={}, parent_directory=dir)
      assert query1.is_trashed is False

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
      assert trashed_query.is_trashed
      assert dir.is_trashed is False
      assert query.is_trashed is False

      # last_modified should be retained post conversion
      assert dir_last_modified == dir.last_modified
      assert query_last_modified == query.last_modified
      assert trashed_query_last_modified == trashed_query.last_modified

      query1 = Document2.objects.get(uuid=query1.uuid)
      assert query1_last_modified == query1.last_modified
    finally:
      # Delete docs
      dir.delete()
      query.delete()
      query1.delete()
      trashed_query.delete()


@pytest.mark.django_db
class TestDocument2Permissions(object):
  def setup_method(self):
    self.default_group = get_default_user_group()

    self.client = make_logged_in_client(username="perm_user", groupname=self.default_group.name, recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(
      username="not_perm_user", groupname=self.default_group.name, recreate=True, is_superuser=False
    )

    self.user = User.objects.get(username="perm_user")
    self.user_not_me = User.objects.get(username="not_perm_user")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

    # This creates the user directories for the new user
    response = self.client.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    assert '/' == data['document']['path'], data

    self.home_dir = Document2.objects.get_home_directory(user=self.user)

  def test_default_permissions(self):
    # Tests that for a new doc by default, read/write perms are set to no users and no groups
    new_doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    response = self.client.get('/desktop/api2/doc/', {'uuid': new_doc.uuid})
    data = json.loads(response.content)
    assert new_doc.uuid == data['document']['uuid'], data
    assert 'perms' in data['document']
    assert {
      'read': {'users': [], 'groups': []},
      'write': {'users': [], 'groups': []},
      'link_read': False,
      'link_sharing_on': False,
      'link_write': False,
    } == data['document']['perms']

  def test_share_document_read_by_user(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # owner can view document
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert doc.uuid == data['document']['uuid'], data

    # other user cannot view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert -1 == data['status']

    # Share read perm by users
    response = self.client.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps(
          {
            'read': {
              'user_ids': [self.user.id, self.user_not_me.id],
              'group_ids': [],
            },
            'write': {
              'user_ids': [],
              'group_ids': [],
            },
          }
        ),
      },
    )

    assert 0 == json.loads(response.content)['status'], response.content
    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    # other user can view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert doc.uuid == data['document']['uuid'], data

    # other user can share document with read permissions
    response = self.client_not_me.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps(
          {
            'read': {
              'user_ids': [],
              'group_ids': [self.default_group.id],
            },
            'write': {
              'user_ids': [],
              'group_ids': [],
            },
          }
        ),
      },
    )
    assert 0 == json.loads(response.content)['status'], response.content

    # other user cannot share document with write permissions
    response = self.client_not_me.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps(
          {
            'read': {
              'user_ids': [],
              'group_ids': [],
            },
            'write': {
              'user_ids': [],
              'group_ids': [self.default_group.id],
            },
          }
        ),
      },
    )
    assert -1 == json.loads(response.content)['status'], response.content

  def test_share_document_read_by_group(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # owner can view document
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert doc.uuid == data['document']['uuid'], data

    # other user cannot view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert -1 == data['status']

    response = self.client.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps(
          {'read': {'user_ids': [self.user.id], 'group_ids': [self.default_group.id]}, 'write': {'user_ids': [], 'group_ids': []}}
        ),
      },
    )

    assert 0 == json.loads(response.content)['status'], response.content
    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    # other user can view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert doc.uuid == data['document']['uuid'], data

  def test_share_document_write_by_user(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # other user cannot modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert -1 == data['status']

    # Share write perm by user
    response = self.client.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps(
          {'read': {'user_ids': [self.user.id], 'group_ids': []}, 'write': {'user_ids': [self.user_not_me.id], 'group_ids': []}}
        ),
      },
    )

    assert 0 == json.loads(response.content)['status'], response.content
    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert doc.can_write(self.user_not_me)

    # other user can modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert 0 == data['status']

  def test_share_document_write_by_group(self):
    doc = Document2.objects.create(name='new_doc', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    # other user cannot modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert -1 == data['status']

    # Share write perm by group
    response = self.client.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps(
          {'read': {'user_ids': [self.user.id], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': [self.default_group.id]}}
        ),
      },
    )

    assert 0 == json.loads(response.content)['status'], response.content
    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert doc.can_write(self.user_not_me)

    # other user can modify document
    response = self.client_not_me.post('/desktop/api2/doc/delete', {'uuid': json.dumps(doc.uuid)})
    data = json.loads(response.content)
    assert 0 == data['status']

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
      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert not doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)

    # Update parent_dir permissions to grant write permissions to default group
    response = self.client.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(parent_dir.uuid),
        'data': json.dumps({'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': [self.default_group.id]}}),
      },
    )

    assert 0 == json.loads(response.content)['status'], response.content
    for doc in [parent_dir, child_doc, nested_dir, nested_doc]:
      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(self.user_not_me)
      assert doc.can_write(self.user_not_me)

  def test_get_shared_documents(self):
    not_shared = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    shared_1 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    shared_2 = Document2.objects.create(name='query3.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)

    shared_1.share(user=self.user, name='read', users=[self.user_not_me], groups=[])
    shared_2.share(user=self.user, name='read', users=[self.user_not_me], groups=[])

    # 2 shared docs should appear in the other user's shared documents response
    response = self.client_not_me.get('/desktop/api2/docs/', {'perms': 'shared'})
    data = json.loads(response.content)
    assert 'documents' in data
    assert 2 == data['count']
    doc_names = [doc['name'] for doc in data['documents']]
    assert 'query2.sql' in doc_names
    assert 'query3.sql' in doc_names
    assert 'query1.sql' not in doc_names

    # they should also appear in user's home directory get_documents response
    response = self.client_not_me.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    doc_names = [doc['name'] for doc in data['children']]
    assert 'query2.sql' in doc_names
    assert 'query3.sql' in doc_names

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
    assert 'documents' in data
    assert 3 == data['count'], data
    doc_names = [doc['name'] for doc in data['documents']]
    assert 'dir1' in doc_names
    assert 'dir3' in doc_names
    assert 'query3.sql' in doc_names
    assert 'dir2' not in doc_names

    # nested documents should not appear
    assert 'query1.sql' not in doc_names
    assert 'query2.sql' not in doc_names

    # but nested documents should still be shared/viewable by group
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc1.uuid})
    data = json.loads(response.content)
    assert doc1.uuid == data['document']['uuid'], data

    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc2.uuid})
    data = json.loads(response.content)
    assert doc2.uuid == data['document']['uuid'], data

  def test_inherit_parent_permissions(self):
    # Tests that when saving a document to a shared directory, the doc/dir inherits same permissions

    dir1 = Directory.objects.create(name='dir1', owner=self.user, parent_directory=self.home_dir)

    dir1.share(user=self.user, name='read', users=[], groups=[self.default_group])
    dir1.share(user=self.user, name='write', users=[self.user_not_me], groups=[])

    doc1 = Document2.objects.create(name='doc1', owner=self.user, parent_directory=dir1)

    response = self.client.get('/desktop/api2/doc/', {'uuid': doc1.uuid})
    data = json.loads(response.content)
    assert [{'id': self.default_group.id, 'name': self.default_group.name}] == data['document']['perms']['read']['groups'], data
    assert [{'id': self.user_not_me.id, 'username': self.user_not_me.username}] == data['document']['perms']['write']['users'], data

  def test_search_documents(self):
    owned_dir = Directory.objects.create(name='test_dir', owner=self.user, parent_directory=self.home_dir)
    owned_query = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=owned_dir)
    owned_history = Document2.objects.create(
      name='history.sql', type='query-hive', owner=self.user, data={}, is_history=True, parent_directory=owned_dir
    )
    owned_workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=owned_dir)

    other_home_dir = Document2.objects.get_home_directory(user=self.user_not_me)
    not_shared = Document2.objects.create(
      name='other_query1.sql', type='query-hive', owner=self.user_not_me, data={}, parent_directory=other_home_dir
    )
    shared_1 = Document2.objects.create(
      name='other_query2.sql', type='query-hive', owner=self.user_not_me, data={}, parent_directory=other_home_dir
    )
    shared_2 = Document2.objects.create(
      name='other_query3.sql', type='query-hive', owner=self.user_not_me, data={}, parent_directory=other_home_dir
    )

    shared_1.share(user=self.user_not_me, name='read', users=[self.user], groups=[])
    shared_2.share(user=self.user_not_me, name='read', users=[], groups=[self.default_group])

    # 3 total docs (1 owned, 2 shared)
    response = self.client.get('/desktop/api2/docs/', {'type': 'query-hive'})
    data = json.loads(response.content)
    assert 'documents' in data
    assert 3 == data['count']
    doc_names = [doc['name'] for doc in data['documents']]
    assert 'query1.sql' in doc_names
    assert 'other_query2.sql' in doc_names
    assert 'other_query3.sql' in doc_names

    # Return history docs
    response = self.client.get('/desktop/api2/docs/', {'type': 'query-hive', 'include_history': 'true'})
    data = json.loads(response.content)
    assert 'documents' in data
    assert 4 == data['count']
    doc_names = [doc['name'] for doc in data['documents']]
    assert 'history.sql' in doc_names

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
    response = self.client.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(parent_dir.uuid),
        'data': json.dumps({'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [user_y.id], 'group_ids': []}}),
      },
    )

    user_y_child_doc = Document2.objects.create(
      name='other_query1.sql', type='query-hive', owner=user_y, data={}, parent_directory=parent_dir
    )

    share_test_user = User.objects.create(username='share_test_user', password="share_test_user")

    # Share the dir with another user - share_test_user
    response = self.client.post(
      "/desktop/api2/doc/share",
      {
        'uuid': json.dumps(parent_dir.uuid),
        'data': json.dumps({'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [share_test_user.id], 'group_ids': []}}),
      },
    )

    assert 0 == json.loads(response.content)['status'], response.content
    for doc in [parent_dir, child_doc, user_y_child_doc]:
      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(share_test_user)
      assert doc.can_write(share_test_user)

  def test_unicode_name(self):
    doc = Document2.objects.create(
      name='My Bundle a voté « non » à l’accord', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir
    )

    # Verify that home directory contents return correctly
    response = self.client.get('/desktop/api2/doc/', {'uuid': self.home_dir.uuid})
    data = json.loads(response.content)
    assert 0 == data['status']

    # Verify that the doc's path is escaped
    response = self.client.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert 0 == data['status']
    path = data['document']['path']
    assert '/My%20Bundle%20a%20vot%C3%A9%20%C2%AB%20non%20%C2%BB%20%C3%A0%20l%E2%80%99accord' == path

  def test_link_permissions(self):
    doc = Document2.objects.create(
      name='test_link_permissions.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir
    )

    try:
      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert not doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)

      doc.share(self.user, name=Document2Permission.LINK_READ_PERM, is_link_on=True)

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)

      assert doc.get_permissions('read')
      assert not doc.get_permissions('write')
      assert not doc.get_permission('link_read').users.all()
      assert not doc.get_permission('link_read').groups.all()
      assert not doc.get_permission('read')  # There is no doc listing via links, only direct access
      assert not doc.get_permission('write')

      doc.share(self.user, name=Document2Permission.LINK_READ_PERM, is_link_on=False)

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert not doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)

      doc.share(self.user, name=Document2Permission.LINK_WRITE_PERM, is_link_on=True)

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(self.user_not_me)
      assert doc.can_write(self.user_not_me)

      doc.share(self.user, name=Document2Permission.LINK_WRITE_PERM, is_link_on=False)

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert not doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)
    finally:
      doc.delete()

  def test_combined_permissions(self):
    doc = Document2.objects.create(
      name='test_combined_permissions.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir
    )

    try:
      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert not doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)

      assert 0 == doc.get_permissions('read').count()
      assert 0 == doc.get_permissions('write').count()

      # READ and LINK_READ
      doc.share(self.user, name=Document2Permission.LINK_READ_PERM, is_link_on=True)
      doc.share(self.user, name=Document2Permission.READ_PERM, users=[self.user_not_me])

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)

      assert 2 == doc.get_permissions('read').count()
      assert 0 == doc.get_permissions('write').count()

      # READ, WRITE and LINK_READ
      doc.share(self.user, name=Document2Permission.WRITE_PERM, users=[self.user_not_me])

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(self.user_not_me)
      assert doc.can_write(self.user_not_me)

      assert 2 == doc.get_permissions('read').count()
      assert 1 == doc.get_permissions('write').count()

      # READ, WRITE, LINK_READ and LINK_WRITE
      doc.share(self.user, name=Document2Permission.LINK_WRITE_PERM, is_link_on=True)

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(self.user_not_me)
      assert doc.can_write(self.user_not_me)

      assert 2 == doc.get_permissions('read').count()
      assert 2 == doc.get_permissions('write').count()

      # WRITE and WRITE_READ
      doc.share(self.user, name=Document2Permission.LINK_READ_PERM, is_link_on=False)
      doc.share(self.user, name=Document2Permission.READ_PERM, users=[])

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert doc.can_read(self.user_not_me)
      assert doc.can_write(self.user_not_me)

      assert 1 == doc.get_permissions('read').count()
      assert 2 == doc.get_permissions('write').count()

      # Not shared
      doc.share(self.user, name=Document2Permission.LINK_WRITE_PERM, is_link_on=False)
      doc.share(self.user, name=Document2Permission.WRITE_PERM, users=[])

      assert doc.can_read(self.user)
      assert doc.can_write(self.user)
      assert not doc.can_read(self.user_not_me)
      assert not doc.can_write(self.user_not_me)

      assert 1 == doc.get_permissions('read').count()  # 1 READ but empty people
      assert not doc.get_permissions('read')[0].users.all()
      assert not doc.get_permissions('read')[0].groups.all()
      assert 1 == doc.get_permissions('write').count()  # 1 WRITE but empty people
      assert not doc.get_permissions('write')[0].users.all()
      assert not doc.get_permissions('write')[0].groups.all()
    finally:
      doc.delete()


@pytest.mark.django_db
class TestDocument2ImportExport(object):
  def setup_method(self):
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
    assert '/' == data['document']['path'], data

    self.home_dir = Document2.objects.get_home_directory(user=self.user)
    self.not_me_home_dir = Document2.objects.get_home_directory(user=self.user_not_me)

  def test_export_documents_with_dependencies(self):
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    query2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    query3 = Document2.objects.create(
      name='query3.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir, is_history=True
    )
    workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir)
    workflow.dependencies.add(query1)
    workflow.dependencies.add(query2)
    workflow.dependencies.add(query3)

    # Test that exporting workflow should export all dependencies except history
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id]), 'format': 'json'})
    documents = json.loads(response.content)
    documents = json.loads(documents)

    assert 3 == len(documents)
    assert 'test.wf' in [doc['fields']['name'] for doc in documents]
    assert 'query1.sql' in [doc['fields']['name'] for doc in documents]
    assert 'query2.sql' in [doc['fields']['name'] for doc in documents]
    assert 'query3.sql' not in [doc['fields']['name'] for doc in documents]

    # Test that exporting multiple workflows with overlapping dependencies works
    workflow2 = Document2.objects.create(name='test2.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir)
    workflow2.dependencies.add(query1)

    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id, workflow2.id]), 'format': 'json'})
    documents = json.loads(response.content)
    documents = json.loads(documents)

    assert 4 == len(documents)
    assert 'test.wf' in [doc['fields']['name'] for doc in documents]
    assert 'test2.wf' in [doc['fields']['name'] for doc in documents]
    assert 'query1.sql' in [doc['fields']['name'] for doc in documents]
    assert 'query2.sql' in [doc['fields']['name'] for doc in documents]

  def test_export_documents_file_name(self):
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    query2 = Document2.objects.create(name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    query3 = Document2.objects.create(
      name='query3.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir, is_history=True
    )
    workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir)
    workflow.dependencies.add(query1)
    workflow.dependencies.add(query2)
    workflow.dependencies.add(query3)

    # Test that exporting multiple workflows with overlapping dependencies works
    workflow2 = Document2.objects.create(name='test2.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir)
    workflow2.dependencies.add(query1)

    # Test that exporting to a file includes the date and number of documents in the filename
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id, workflow2.id])})
    assert response['Content-Disposition'] == 'attachment; filename="hue-documents-%s-(4).json"' % datetime.today().strftime('%Y-%m-%d')

    # Test that exporting single file gets the name of the document in the filename
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id])})
    assert response['Content-Disposition'] == 'attachment; filename="' + workflow.name + '.json"'

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

    assert 6 == len(documents)
    assert 'dir1' in [doc['fields']['name'] for doc in documents]
    assert 'query1.sql' in [doc['fields']['name'] for doc in documents]
    assert 'dir2' in [doc['fields']['name'] for doc in documents]
    assert 'dir3' in [doc['fields']['name'] for doc in documents]
    assert 'query2.sql' in [doc['fields']['name'] for doc in documents]
    assert 'query3.sql' in [doc['fields']['name'] for doc in documents]

  def test_import_owned_document(self):
    owned_query = Document2.objects.create(
      name='query.sql',
      type='query-hive',
      owner=self.user,
      data=json.dumps({'description': 'original_query'}),
      parent_directory=self.home_dir,
    )

    # Test that importing existing doc updates it and retains owner, UUID
    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([owned_query.id]), 'format': 'json'})
    documents = response.content

    if isinstance(documents, bytes):
      documents = documents.decode('utf-8')

    response = self.client.post('/desktop/api2/doc/import/', {'documents': documents})
    data = json.loads(response.content)

    assert 'message' in data, data
    assert 'Installed 1 object' in data['message'], data
    assert 'count' in data
    assert 1 == data['count']
    assert 'created_count' in data
    assert 0 == data['created_count']
    assert 'updated_count' in data
    assert 1 == data['updated_count']
    assert 'documents' in data
    assert 'name' in data['documents'][0]
    assert 'query.sql' == data['documents'][0]['name']
    assert 'type' in data['documents'][0]
    assert 'query-hive' == data['documents'][0]['type']
    assert 'owner' in data['documents'][0]
    assert 'perm_user' == data['documents'][0]['owner']

    assert 1 == Document2.objects.filter(name='query.sql').count()
    imported_doc = Document2.objects.get(name='query.sql')
    assert owned_query.uuid == imported_doc.uuid
    assert owned_query.owner == imported_doc.owner

    # Test that import non-existing doc creates it, sets parent to home
    Document2.objects.get(name='query.sql').delete()
    assert 0 == Document2.objects.filter(name='query.sql').count()

    response = self.client.post('/desktop/api2/doc/import/', {'documents': documents})

    assert 1 == Document2.objects.filter(name='query.sql').count()
    imported_doc = Document2.objects.get(name='query.sql')
    assert owned_query.uuid == imported_doc.uuid
    assert owned_query.owner == imported_doc.owner
    assert owned_query.parent_directory == imported_doc.parent_directory

  def test_import_nonowned_document(self):
    owned_query = Document2.objects.create(
      name='query.sql',
      type='query-hive',
      owner=self.user,
      data=json.dumps({'description': 'original_query'}),
      parent_directory=self.home_dir,
    )

    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([owned_query.id]), 'format': 'json'})
    documents = response.content

    if isinstance(documents, bytes):
      documents = documents.decode('utf-8')

    # Test that importing non-owned doc copies it, sets parent to home
    response = self.client_not_me.post('/desktop/api2/doc/import/', {'documents': documents})

    assert 2 == Document2.objects.filter(name='query.sql').count()
    imported_doc = Document2.objects.get(name='query.sql', owner=self.user_not_me)
    assert owned_query.uuid != imported_doc.uuid
    assert self.user_not_me == imported_doc.owner
    assert self.not_me_home_dir.uuid == imported_doc.parent_directory.uuid

    data = json.loads(response.content)
    assert 'count' in data
    assert 1 == data['count']
    assert 'created_count' in data
    assert 1 == data['created_count']
    assert 'updated_count' in data
    assert 0 == data['updated_count']

  def test_import_with_history_dependencies(self):
    query1 = Document2.objects.create(name='query1.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir)
    query2 = Document2.objects.create(
      name='query2.sql', type='query-hive', owner=self.user, data={}, parent_directory=self.home_dir, is_history=True
    )
    workflow = Document2.objects.create(name='test.wf', type='oozie-workflow2', owner=self.user, data={}, parent_directory=self.home_dir)
    workflow.dependencies.add(query1)
    workflow.dependencies.add(query2)

    response = self.client.get('/desktop/api2/doc/export/', {'documents': json.dumps([workflow.id]), 'format': 'json'})
    documents = response.content

    # Delete previous entries from DB, so when you import it creates them
    query1.delete()
    query2.delete()
    workflow.delete()

    if not isinstance(documents, str):
      documents = documents.decode('utf-8')

    response = self.client_not_me.post('/desktop/api2/doc/import/', {'documents': documents})
    assert Document2.objects.filter(name='query1.sql').exists()
    assert not Document2.objects.filter(name='query2.sql').exists()

    data = json.loads(response.content)
    assert 'count' in data
    assert 2 == data['count']
    assert 'created_count' in data
    assert 2 == data['created_count']
    assert 'updated_count' in data
    assert 0 == data['updated_count']
