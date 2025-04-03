#!/usr/bin/env python
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
from unittest.mock import MagicMock, patch

from django.test import TestCase

from desktop.lib.django_test_util import make_logged_in_client
from notebook.connectors.flink_sql import FlinkSqlApi
from useradmin.models import User


class TestFlinkApi(TestCase):
  def setup_method(self, test_method):
    self.client = make_logged_in_client(username="hue_test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="hue_test")
    self.interpreter = {
      'options': {
        'url': 'https://example.com:8081',
      },
      'name': 'flink',
    }

  @patch('notebook.connectors.flink_sql.FlinkSqlClient')
  def test_create_session(self, client_mock):
    # given: mock interactions
    mock_client_instance = MagicMock()
    client_mock.return_value = mock_client_instance
    mock_client_instance.create_session.return_value = {'sessionHandle': '657c12d4-5509-477f-a460-ea6af927906d'}

    # and: FlinkSqlApi instance
    flink_api = FlinkSqlApi(self.user, interpreter=self.interpreter)

    # when
    created_session = flink_api.create_session(lang='flink', properties=None)

    # then
    assert created_session == {'id': '657c12d4-5509-477f-a460-ea6af927906d', 'type': 'flink'}
    assert mock_client_instance.session_heartbeat.call_count == 1

  @patch('notebook.connectors.flink_sql.FlinkSqlClient')
  def test_create_session_with_default_catalog_and_database(self, client_mock):
    # given: mock interactions
    mock_client_instance = MagicMock()
    client_mock.return_value = mock_client_instance
    mock_client_instance.create_session.return_value = {'sessionHandle': '657c12d4-5509-477f-a460-ea6af927906d'}

    # and: FlinkSqlApi instance with configuration
    self.interpreter['options']['default_catalog'] = 'default_catalog'
    self.interpreter['options']['default_database'] = 'default_database'
    flink_api = FlinkSqlApi(self.user, interpreter=self.interpreter)

    # when
    created_session = flink_api.create_session(lang='flink', properties=None)

    # then
    assert created_session == {'id': '657c12d4-5509-477f-a460-ea6af927906d', 'type': 'flink'}
    mock_client_instance.configure_session.assert_called_once_with(
      '657c12d4-5509-477f-a460-ea6af927906d', "USE `default_catalog`.`default_database`"
    )
    assert mock_client_instance.session_heartbeat.call_count == 1
