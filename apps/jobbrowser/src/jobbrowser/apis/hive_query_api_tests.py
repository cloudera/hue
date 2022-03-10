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
