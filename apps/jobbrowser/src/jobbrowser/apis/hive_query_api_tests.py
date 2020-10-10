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


class TestHiveQueryApi():

  def setUp(self):
    if not QUERY_DATABASE.HOST.get():
      raise SkipTest

    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))

    with connection.schema_editor() as schema_editor:
      schema_editor.create_model(HiveQuery)

      if HiveQuery._meta.db_table not in connection.introspection.table_names():
        raise ValueError("Table `{table_name}` is missing in test database.".format(table_name=HiveQuery._meta.db_table))

  def tearDown(self):
    with connection.schema_editor() as schema_editor:
      schema_editor.delete_model(HiveQuery)


  def test_search_pagination(self):
    with patch('jobbrowser.apis.hive_query_api.HiveQueryClient._get_queries') as _get_queries:
      with patch('jobbrowser.apis.hive_query_api.HiveQueryClient.get_query_count') as get_query_count:
        query1 = HiveQuery()
        query1.query_id = 10
        query1.start_time = 5
        query1.query = "select * from employee"
        query1.end_time = 8
        query1.elapsed_time = 28
        query1.status = "SUCCESS"
        query1.user_id = "hive"
        query1.request_user = "hive"

        query2 = HiveQuery()
        query2.query_id = 12
        query2.start_time = 4
        query2.query = "select * from employee1"
        query2.end_time = 6
        query2.elapsed_time = 28
        query2.status = "SUCCESS"
        query2.user_id = "hive"
        query2.request_user = "hive"

        query3 = HiveQuery()
        query3.query_id = 14
        query3.start_time = 6
        query3.query = "select * from employee2"
        query3.end_time = 7
        query3.elapsed_time = 28
        query3.status = "FAIL"
        query3.user_id = "hive"
        query3.request_user = "hive"

        get_query_count.return_value = 3
        _get_queries.return_value = [query1, query2, query3]
        filters = {"endTime": 10, "facets": [], "limit": 2, "offset": 0, "sortText": "", "startTime": 1, "text": "", "type": "basic"}
        _data = json.dumps(filters)
        response = self.client.post("/jobbrowser/api/jobs/queries-hive", content_type='applecation/json', data=_data)
        data = json.loads(response.content)
        paginated_query_list = HiveQueryClient().get_queries(filters)

        assert_equal(2, len(paginated_query_list))
        assert_equal(10, data['queries'][0]['queryId'])
        assert_equal("SUCCESS", data['queries'][1]['status'])
        assert_equal(3, data['meta']['size'])
        assert_equal(2, data['meta']['limit'])


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
      'text': "select",
      'type': "basic",
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


  def test__get_queries(self):
    HiveQueryClient()._get_queries(self.filters)


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
