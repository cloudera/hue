#!/usr/bin/env python
## -*- coding: utf-8 -*-
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

from collections import OrderedDict
from nose.plugins.attrib import attr
from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User
from django.urls import reverse
from azure.conf import is_adls_enabled

from desktop import appmanager
from desktop.conf import APP_BLACKLIST
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_permission
from desktop.models import Directory, Document, Document2
from hadoop import cluster as originalCluster

import notebook.connectors.hiveserver2

from notebook.api import _historify
from notebook.connectors.base import Notebook, QueryError, Api
from notebook.decorators import api_error_handler
from notebook.conf import get_ordered_interpreters, INTERPRETERS_SHOWN_ON_WHEEL, INTERPRETERS
from notebook.models import Analytics


class TestNotebookApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="test")
    self.user_not_me = User.objects.get(username="not_perm_user")

    grant_access("test", "default", "notebook")
    grant_access("not_perm_user", "default", "notebook")

    self.notebook_json = """
      {
        "selectedSnippet": "hive",
        "showHistory": false,
        "description": "Test Hive Query",
        "name": "Test Hive Query",
        "sessions": [
            {
                "type": "hive",
                "properties": [],
                "id": null
            }
        ],
        "type": "query-hive",
        "id": 50010,
        "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"hive","status":"running","statement_raw":"select * from default.web_logs where app = '${app_name}';","variables":[{"name":"app_name","value":"metastore"}],"statement":"select * from default.web_logs where app = 'metastore';","properties":{"settings":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from default.web_logs where app = 'metastore';","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
        "uuid": "5982a274-de78-083c-2efc-74f53dce744c",
        "isSaved": false,
        "parentUuid": null
    }
    """

    self.notebook = json.loads(self.notebook_json)
    self.doc2 = Document2.objects.create(id=50010, name=self.notebook['name'], type=self.notebook['type'], owner=self.user)
    self.doc1 = Document.objects.link(self.doc2, owner=self.user, name=self.doc2.name,
                                      description=self.doc2.description, extra=self.doc2.type)


  def test_save_notebook(self):
    # Test that saving a new document with a new parent will set the parent_directory
    home_dir = Document2.objects.get_home_directory(self.user)
    assert_equal(home_dir.uuid, self.doc2.parent_directory.uuid)

    new_dir = Directory.objects.create(name='new_dir', owner=self.user, parent_directory=home_dir)
    notebook_cp = self.notebook.copy()
    notebook_cp.pop('id')
    notebook_cp['directoryUuid'] = new_dir.uuid
    notebook_json = json.dumps(notebook_cp)

    response = self.client.post(reverse('notebook:save_notebook'), {'notebook': notebook_json})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    doc = Document2.objects.get(pk=data['id'])
    assert_equal(new_dir.uuid, doc.parent_directory.uuid)

    # Test that saving a new document with a no parent will map it to its home dir
    notebook_json = """
      {
        "selectedSnippet": "hive",
        "showHistory": false,
        "description": "Test Hive Query",
        "name": "Test Hive Query",
        "sessions": [
            {
                "type": "hive",
                "properties": [],
                "id": null
            }
        ],
        "type": "query-hive",
        "id": null,
        "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"hive","status":"running","statement_raw":"select * from default.web_logs where app = '${app_name}';","variables":[{"name":"app_name","value":"metastore"}],"statement":"select * from default.web_logs where app = 'metastore';","properties":{"settings":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from default.web_logs where app = 'metastore';","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
        "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a"
    }
    """

    response = self.client.post(reverse('notebook:save_notebook'), {'notebook': notebook_json})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    doc = Document2.objects.get(pk=data['id'])
    assert_equal(Document2.objects.get_home_directory(self.user).uuid, doc.parent_directory.uuid)

    # Test that saving a notebook will save the search field to the first statement text
    assert_equal(doc.search, "select * from default.web_logs where app = 'metastore';")


  def test_historify(self):
    # Starts with no history
    assert_equal(0, Document2.objects.filter(name__contains=self.notebook['name'], is_history=True).count())
    assert_equal(1, Document.objects.filter(name__contains=self.notebook['name']).count())

    history_doc = _historify(self.notebook, self.user)

    assert_true(history_doc.id > 0)

    # Test that historify creates new Doc2 and linked Doc1
    assert_equal(1, Document2.objects.filter(name__contains=self.notebook['name'], is_history=True).count())
    assert_equal(2, Document.objects.filter(name__contains=self.notebook['name']).count())

    # Historify again
    history_doc = _historify(self.notebook, self.user)

    assert_equal(2, Document2.objects.filter(name__contains=self.notebook['name'], is_history=True).count())
    assert_equal(3, Document.objects.filter(name__contains=self.notebook['name']).count())


  def test_get_history(self):
    assert_equal(0, Document2.objects.filter(name__contains=self.notebook['name'], is_history=True).count())
    _historify(self.notebook, self.user)
    _historify(self.notebook, self.user)
    _historify(self.notebook, self.user)
    assert_equal(3, Document2.objects.filter(name__contains=self.notebook['name'], is_history=True).count())

    # History should not return history objects that don't have the given doc type
    Document2.objects.create(name='Impala History', type='query-impala', data=self.notebook_json, owner=self.user, is_history=True)

    # Verify that get_history API returns history objects for given type and current user
    response = self.client.get(reverse('notebook:get_history'), {'doc_type': 'hive'})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_equal(3, len(data['history']), data)
    assert_true(all(doc['type'] == 'query-hive' for doc in data['history']), data)

    # TODO: test that query history for shared query only returns docs accessible by current user


  def test_clear_history(self):
    assert_equal(0, Document2.objects.filter(name__contains=self.notebook['name'], is_history=True).count())
    _historify(self.notebook, self.user)
    _historify(self.notebook, self.user)
    _historify(self.notebook, self.user)
    assert_equal(3, Document2.objects.filter(name__contains=self.notebook['name'], is_history=True).count())

    # Clear history should not clear history objects that don't have the given doc type
    Document2.objects.create(name='Impala History', type='query-impala', owner=self.user, is_history=True)

    # clear history should retain original document but wipe history
    response = self.client.post(reverse('notebook:clear_history'), {'notebook': self.notebook_json, 'doc_type': 'hive'})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_false(Document2.objects.filter(type='query-hive', is_history=True).exists())
    assert_true(Document2.objects.filter(type='query-hive', is_history=False).exists())
    assert_true(Document2.objects.filter(type='query-impala', is_history=True).exists())


  def test_delete_notebook(self):
    trash_notebook_json = """
        {
          "selectedSnippet": "hive",
          "showHistory": false,
          "description": "Test Hive Query",
          "name": "Test Hive Query",
          "sessions": [
              {
                  "type": "hive",
                  "properties": [],
                  "id": null
              }
          ],
          "type": "query-hive",
          "id": null,
          "snippets": [{"id": "e069ef32-5c95-4507-b961-e79c090b5abf","type":"hive","status":"ready","database":"default","statement":"select * from web_logs","statement_raw":"select * from web_logs","variables":[],"properties":{"settings":[],"files":[],"functions":[]},"result":{}}],
          "uuid": "8a20da5f-b69c-4843-b17d-dea5c74c41d1"
      }
      """

    # Assert that the notebook is first saved
    response = self.client.post(reverse('notebook:save_notebook'), {'notebook': trash_notebook_json})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    # Test that deleting it moves it to the user's Trash folder
    notebook_doc = Document2.objects.get(id=data['id'])
    trash_notebooks = [Notebook(notebook_doc).get_data()]
    response = self.client.post(reverse('notebook:delete'), {'notebooks': json.dumps(trash_notebooks)})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_equal('Trashed 1 notebook(s)', data['message'], data)

    response = self.client.get('/desktop/api2/doc', {'path': '/.Trash'})
    data = json.loads(response.content)
    trash_uuids = [doc['uuid'] for doc in data['children']]
    assert_true(notebook_doc.uuid in trash_uuids, data)

    # Test that any errors are reported in the response
    nonexistant_doc = {
      "id": 12345,
      "uuid": "ea22da5f-b69c-4843-b17d-dea5c74c41d1",
      "selectedSnippet": "hive",
      "showHistory": False,
      "description": "Test Hive Query",
      "name": "Test Hive Query",
      "sessions": [
        {
          "type": "hive",
          "properties": [],
          "id": None,
        }
      ],
      "type": "query-hive",
      "snippets": [{
        "id": "e069ef32-5c95-4507-b961-e79c090b5abf",
        "type": "hive",
        "status": "ready",
        "database": "default",
        "statement": "select * from web_logs",
        "statement_raw": "select * from web_logs",
        "variables": [],
         "properties": {"settings": [], "files": [], "functions": []},
        "result": {}
      }]
    }
    trash_notebooks = [nonexistant_doc]
    response = self.client.post(reverse('notebook:delete'), {'notebooks': json.dumps(trash_notebooks)})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_equal('Trashed 0 notebook(s) and failed to delete 1 notebook(s).', data['message'], data)
    assert_equal(['ea22da5f-b69c-4843-b17d-dea5c74c41d1'], data['errors'])


  def test_query_error_encoding(self):
    @api_error_handler
    def send_exception(message):
      raise QueryError(message=message)

    message = """SELECT
a.key,
a.*
FROM customers c, c.addresses a"""
    response =send_exception(message)
    data = json.loads(response.content)
    assert_equal(1, data['status'])

    message = """SELECT
\u2002\u2002a.key,
\u2002\u2002a.*
FROM customers c, c.addresses a"""
    response =send_exception(message)
    data = json.loads(response.content)
    assert_equal(1, data['status'])

    message = u"""SELECT
a.key,
a.*
FROM déclenché c, c.addresses a"""
    response =send_exception(message)
    data = json.loads(response.content)
    assert_equal(1, data['status'])


class MockedApi(Api):
  def execute(self, notebook, snippet):
    return {
      'sync': True,
      'has_result_set': True,
      'result': {
        'has_more': False,
        'data': [['test']],
        'meta': [{
          'name': 'test',
          'type': '',
          'comment': ''
        }],
        'type': 'table'
      }
    }

  def close_statement(self, notebook, snippet):
    pass

  def export_data_as_hdfs_file(self, snippet, target_file, overwrite):
    return {'destination': target_file}


class MockFs():
  def __init__(self, logical_name=None):

    self.fs_defaultfs = 'hdfs://curacao:8020'
    self.logical_name = logical_name if logical_name else ''
    self.DEFAULT_USER = 'test'
    self.user = 'test'
    self._filebrowser_action = ''

  def setuser(self, user):
    self.user = user

  @property
  def user(self):
    return self.user

  def do_as_user(self, username, fn, *args, **kwargs):
    return ''

  def exists(self, path):
    return True

  def isdir(self, path):
    return path == '/user/hue'

  def filebrowser_action(self):
    return self._filebrowser_action


class TestNotebookApiMocked(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="test")
    self.user_not_me = User.objects.get(username="not_perm_user")

    # Beware: Monkey patch HS2API Mock API
    if not hasattr(notebook.connectors.hiveserver2, 'original_HS2Api'): # Could not monkey patch base.get_api
      notebook.connectors.hiveserver2.original_HS2Api = notebook.connectors.hiveserver2.HS2Api
    notebook.connectors.hiveserver2.HS2Api = MockedApi

    originalCluster.get_hdfs()
    self.original_fs = originalCluster.FS_CACHE["default"]
    originalCluster.FS_CACHE["default"] = MockFs()

    grant_access("test", "default", "notebook")
    grant_access("test", "default", "beeswax")
    grant_access("test", "default", "hive")
    grant_access("not_perm_user", "default", "notebook")
    grant_access("not_perm_user", "default", "beeswax")
    grant_access("not_perm_user", "default", "hive")
    add_permission('test', 'has_adls', permname='adls_access', appname='filebrowser')

  def tearDown(self):
    notebook.connectors.hiveserver2.HS2Api = notebook.connectors.hiveserver2.original_HS2Api

    if originalCluster.FS_CACHE is None:
      originalCluster.FS_CACHE = {}
    originalCluster.FS_CACHE["default"] = self.original_fs


  @attr('integration')
  def test_export_result(self):
    notebook_json = """
      {
        "selectedSnippet": "hive",
        "showHistory": false,
        "description": "Test Hive Query",
        "name": "Test Hive Query",
        "sessions": [
            {
                "type": "hive",
                "properties": [],
                "id": null
            }
        ],
        "type": "query-hive",
        "id": null,
        "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"hive","status":"running","statement":"select * from web_logs","properties":{"settings":[],"variables":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
        "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a"
    }
    """

    response = self.client.post(reverse('notebook:export_result'), {
        'notebook': notebook_json,
        'snippet': json.dumps(json.loads(notebook_json)['snippets'][0]),
        'format': json.dumps('hdfs-file'),
        'destination': json.dumps('/user/hue'),
        'overwrite': json.dumps(False)
    })

    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_equal('/user/hue/Test Hive Query.csv', data['watch_url']['destination'], data)


    response = self.client.post(reverse('notebook:export_result'), {
        'notebook': notebook_json,
        'snippet': json.dumps(json.loads(notebook_json)['snippets'][0]),
        'format': json.dumps('hdfs-file'),
        'destination': json.dumps('/user/hue/path.csv'),
        'overwrite': json.dumps(False)
    })

    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_equal('/user/hue/path.csv', data['watch_url']['destination'], data)

    if is_adls_enabled():
      response = self.client.post(reverse('notebook:export_result'), {
          'notebook': notebook_json,
          'snippet': json.dumps(json.loads(notebook_json)['snippets'][0]),
          'format': json.dumps('hdfs-file'),
          'destination': json.dumps('adl:/user/hue/path.csv'),
          'overwrite': json.dumps(False)
      })

      data = json.loads(response.content)
      assert_equal(0, data['status'], data)
      assert_equal('adl:/user/hue/path.csv', data['watch_url']['destination'], data)

  def test_download_result(self):
    notebook_json = """
      {
        "selectedSnippet": "hive",
        "showHistory": false,
        "description": "Test Hive Query",
        "name": "Test Hive Query",
        "sessions": [
            {
                "type": "hive",
                "properties": [],
                "id": null
            }
        ],
        "type": "query-hive",
        "id": null,
        "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"hive","status":"running","statement":"select * from web_logs","properties":{"settings":[],"variables":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
        "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a"
    }
    """
    response = self.client.post(reverse('notebook:download'), {
        'notebook': notebook_json,
        'snippet': json.dumps(json.loads(notebook_json)['snippets'][0]),
        'format': 'csv'
    })
    content = "".join(response)
    assert_true(len(content) > 0)

def test_get_interpreters_to_show():
  default_interpreters = OrderedDict((
      ('hive', {
          'name': 'Hive', 'interface': 'hiveserver2', 'type': 'hive', 'is_sql': True, 'options': {}, 'is_catalog': False,
      }),
      ('spark', {
          'name': 'Scala', 'interface': 'livy', 'type': 'spark', 'is_sql': False, 'options': {}, 'is_catalog': False,
      }),
      ('pig', {
          'name': 'Pig', 'interface': 'pig', 'type': 'pig', 'is_sql': False, 'options': {}, 'is_catalog': False,
      }),
      ('java', {
          'name': 'Java', 'interface': 'oozie', 'type': 'java', 'is_sql': False, 'options': {}, 'is_catalog': False,
      })
    ))

  expected_interpreters = OrderedDict((
      ('java', {
        'name': 'Java', 'interface': 'oozie', 'type': 'java', 'is_sql': False, 'options': {}, 'is_catalog': False,
      }),
      ('pig', {
        'name': 'Pig', 'interface': 'pig', 'is_sql': False, 'type': 'pig', 'options': {}, 'is_catalog': False,
      }),
      ('hive', {
          'name': 'Hive', 'interface': 'hiveserver2', 'is_sql': True, 'type': 'hive', 'options': {}, 'is_catalog': False,
      }),
      ('spark', {
          'name': 'Scala', 'interface': 'livy', 'type': 'spark', 'is_sql': False, 'options': {}, 'is_catalog': False,
      })
    ))

  try:
    resets = [INTERPRETERS.set_for_testing(default_interpreters), APP_BLACKLIST.set_for_testing('')]
    appmanager.DESKTOP_MODULES = []
    appmanager.DESKTOP_APPS = None
    appmanager.load_apps(APP_BLACKLIST.get())

    interpreters_shown_on_wheel_unset = get_ordered_interpreters()
    assert_equal(default_interpreters.values(), interpreters_shown_on_wheel_unset,
                 'get_interpreters_to_show should return the same as get_interpreters when '
                 'interpreters_shown_on_wheel is unset. expected: %s, actual: %s'
                 % (default_interpreters.values(), interpreters_shown_on_wheel_unset))

    resets.append(INTERPRETERS_SHOWN_ON_WHEEL.set_for_testing('java,pig'))
    assert_equal(expected_interpreters.values(), get_ordered_interpreters(),
                 'get_interpreters_to_show did not return interpreters in the correct order expected: %s, actual: %s'
                 % (expected_interpreters.values(), get_ordered_interpreters()))
  finally:
    for reset in resets:
      reset()
    appmanager.DESKTOP_MODULES = []
    appmanager.DESKTOP_APPS = None
    appmanager.load_apps(APP_BLACKLIST.get())


class TestAnalytics():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_basic_stats(self):
    try:
      doc, created = Document2.objects.get_or_create(name='test_query_stats', type='query-hive', owner=self.user, data={})

      Analytics.admin_stats()
      Analytics.user_stats(user=self.user)
      Analytics.query_stats(query=doc)
    finally:
      doc.delete()
