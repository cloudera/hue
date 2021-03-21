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
import logging
import sys

from django.db import connection
from django.urls import reverse
from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_raises

from desktop.auth.backend import rewrite_user
from desktop.conf import QUERY_DATABASE
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

from jobbrowser.apis.hive_query_api import HiveQueryApi, HiveQueryClient
from jobbrowser.models import HiveQuery


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


LOG = logging.getLogger(__name__)



class TestHiveQueryApiNotebook():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))


  def test_kill_query(self):
    with patch('jobbrowser.apis.hive_query_api.make_notebook') as make_notebook:
      execute_and_wait = Mock()
      make_notebook.return_value = Mock(execute_and_wait=execute_and_wait)

      query_id = 'hive_20201124114044_bd1b8d39-f18f-4d89-ae1b-7a35e7950579'
      data = {
        'operation': json.dumps({'action': 'kill'}),
        'interface': json.dumps('queries-hive'),
        'app_ids': json.dumps([query_id])
      }
      response = self.client.post("/jobbrowser/api/job/action/queries-hive/kill", data)
      response_data = json.loads(response.content)

      make_notebook.assert_called_once_with(
        name='Kill query %s' % query_id,
        editor_type='hive',
        statement='KILL QUERY "%s";' % query_id,
        status='ready',
        on_success_url='assist.db.refresh',
        is_task=False,
      )

      assert_equal(0, response_data['status'])


class TestHiveQueryApi():

  def setUp(self):
    if not QUERY_DATABASE.HOST.get():
      raise SkipTest

    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))
    self.filters = {
      "endTime": 10,
      "facets": [{"field": "status", "values": ["SUCCESS"]}],
      "limit": 2,
      "offset": 0,
      "sortText": "",
      "startTime": 1,
      "text": "select"
    }

    with connection.schema_editor() as schema_editor:
      schema_editor.create_model(HiveQuery)

      if HiveQuery._meta.db_table not in connection.introspection.table_names():
        raise ValueError("Table `{table_name}` is missing in test database.".format(table_name=HiveQuery._meta.db_table))

  def tearDown(self):
    with connection.schema_editor() as schema_editor:
      schema_editor.delete_model(HiveQuery)


  def test_search_pagination(self):
    with patch('jobbrowser.apis.hive_query_api.HiveQueryClient._get_all_queries') as _get_all_queries:

      HiveQuery.objects.create(query_id='1', start_time=6, end_time=8, query="select * from employee1", status="SUCCESS")
      HiveQuery.objects.create(query_id='2', start_time=4, end_time=8, query="select * from employee2", status="ERROR")
      HiveQuery.objects.create(query_id='3', start_time=7, end_time=9, query="select * from employee3)", status="SUCCESS")
      HiveQuery.objects.create(query_id='4', start_time=2, end_time=9, query="select * from employee4", status="SUCCESS")
      HiveQuery.objects.create(query_id='5', start_time=8, end_time=9, query="create table xyz2()", status="SUCCESS")
      HiveQuery.objects.create(query_id='6', start_time=1, end_time=12, query="create table xyz3()", status="SUCCESS")

      _get_all_queries.return_value = HiveQuery.objects.order_by('-start_time')

      _data = json.dumps(self.filters)
      response = self.client.post("/jobbrowser/api/jobs/queries-hive", content_type='application/json', data=_data)
      data = json.loads(response.content)

      assert_equal(2, len(data['queries']))  # pagination
      assert_equal('3', data['queries'][0]['queryId'])  # query id (with order_by)
      assert_equal("SUCCESS", data['queries'][0]['status'])  # facet selection
      assert_true("select" in data['queries'][0]['query'])  # search text
      assert_equal(3, data['meta']['size'])  # total filtered queries count
      assert_equal(2, data['meta']['limit'])  # limit value of filter


  # TODO
  # def test_app(self):
  #   with patch('jobbrowser.apis.hive_query_api.HiveQueryClient.get_query') as get_query:
  #     query_id = 'd94d2fb4815a05c4:b1ccec1500000000'

  #     get_query.return_value = Mock(
  #       query_id=query_id,
  #       query='SELECT'
  #     )

  #     query = HiveQueryApi(self.user).app(query_id)

  #     assert_equal(query_id, query['id'])


class TestHiveQueryClient():

  def setUp(self):
    if not QUERY_DATABASE.HOST.get():
      raise SkipTest

    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))
    self.filters = {
      'endTime': 1602146114116,
      'facets': [],
      'limit': 2,
      'offset': 0,
      'sortText': "startTime:DESC",
      'startTime': 1601541314116,
      'text': "select"
    }
    self.query1 = HiveQuery()
    self.query2 = HiveQuery()
    self.query3 = HiveQuery()

    with connection.schema_editor() as schema_editor:
      schema_editor.create_model(HiveQuery)

      if HiveQuery._meta.db_table not in connection.introspection.table_names():
        raise ValueError("Table `{table_name}` is missing in test database.".format(table_name=HiveQuery._meta.db_table))

  def tearDown(self):
    with connection.schema_editor() as schema_editor:
      schema_editor.delete_model(HiveQuery)


  def test__get_all_queries(self):
    HiveQueryClient()._get_all_queries()


  def test_get_query_count(self):
    with patch('jobbrowser.apis.hive_query_api.HiveQueryClient._get_queries') as _get_queries:

      _get_queries.return_value = [self.query1, self.query2, self.query3]
      filtered_query_count = HiveQueryClient().get_query_count(self.filters)

      assert_equal(3, filtered_query_count)


  def test_get_queries(self):
    HiveQueryClient().get_queries(self.filters)


  def test_get_query(self):
    with patch('jobbrowser.apis.hive_query_api.HiveQueryClient.get_query') as get_query:
      query_id = 'd94d2fb4815a05c4:b1ccec1500000000'
      self.query1.query_id = query_id
      get_query.return_value = self.query1

      assert_equal(HiveQueryClient().get_query(query_id).query_id, query_id)
