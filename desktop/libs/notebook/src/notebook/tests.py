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

from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import Directory, Document, Document2

from notebook.api import _historify
from notebook.connectors.base import QueryError
from notebook.decorators import api_error_handler


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
        "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"hive","status":"running","statement":"select * from web_logs","properties":{"settings":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
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
        "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"hive","status":"running","statement":"select * from web_logs","properties":{"settings":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
        "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a"
    }
    """

    response = self.client.post(reverse('notebook:save_notebook'), {'notebook': notebook_json})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    doc = Document2.objects.get(pk=data['id'])
    assert_equal(Document2.objects.get_home_directory(self.user).uuid, doc.parent_directory.uuid)

    # Test that saving a notebook will save the search field to the first statement text
    assert_equal(doc.search, "select * from web_logs")


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
