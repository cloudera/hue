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


  def test_apps_empty(self):
    with patch('jobbrowser.apis.hive_query_api.HiveQueryClient.get_queries') as get_queries:
      with patch('jobbrowser.apis.hive_query_api.HiveQueryClient.get_query_count') as get_query_count:
        get_queries.return_value = []
        get_query_count.return_value = 0

        app_filters = []

        queries = HiveQueryApi(self.user).apps(app_filters)

        assert_equal({'apps': [], 'total': 0}, queries)


  def test_app(self):
    with patch('jobbrowser.apis.hive_query_api.HiveQueryClient.get_query') as get_query:
      query_id = 'd94d2fb4815a05c4:b1ccec1500000000'

      get_query.return_value = Mock(
        query_id=query_id,
        query='SELECT'
      )

      query = HiveQueryApi(self.user).app(query_id)

      assert_equal(query_id, query['id'])


class TestHiveQueryClient():

  def setUp(self):
    if not QUERY_DATABASE.HOST.get() or True:  # Note: table migrations / non auto model to add before it can be enabled
      raise SkipTest

    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))


  def test_get_query_count(self):
    HiveQueryClient().get_query_count()


  def test_get_queries(self):
    HiveQueryClient().get_queries(limit=100)

    HiveQueryClient().get_queries(limit=10)


  def test_get_query(self):
    query_id = 'd94d2fb4815a05c4:b1ccec1500000000'

    assert_raises(HiveQuery.DoesNotExist, HiveQueryClient().get_query, query_id=query_id)
