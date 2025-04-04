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
  TEST_SESSION_HANDLE = '657c12d4-5509-477f-a460-ea6af927906d'
  TEST_OPERATION_HANDLE = '1f6922e4-ec0c-4307-947b-7502757edf1a'

  def setup_method(self, test_method):
    self.client = make_logged_in_client(username='hue_test', groupname='default', recreate=True, is_superuser=False)
    self.user = User.objects.get(username='hue_test')
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
    mock_client_instance.create_session.return_value = {'sessionHandle': self.TEST_SESSION_HANDLE}
    mock_client_instance.info.return_value = {'version': '2.0.0'}

    # and: FlinkSqlApi instance
    flink_api = FlinkSqlApi(self.user, interpreter=self.interpreter)

    # when
    created_session = flink_api.create_session(lang='flink', properties=None)

    # then
    assert created_session == {'id': self.TEST_SESSION_HANDLE, 'type': 'flink'}
    assert mock_client_instance.session_heartbeat.call_count == 1

  @patch('notebook.connectors.flink_sql.FlinkSqlClient')
  def test_create_session_with_default_catalog_and_database(self, client_mock):
    # given: mock interactions
    mock_client_instance = MagicMock()
    client_mock.return_value = mock_client_instance
    mock_client_instance.create_session.return_value = {'sessionHandle': self.TEST_SESSION_HANDLE}
    mock_client_instance.info.return_value = {'version': '2.0.0'}

    # and: FlinkSqlApi instance with configuration
    self.interpreter['options']['default_catalog'] = 'default_catalog'
    self.interpreter['options']['default_database'] = 'default_database'
    flink_api = FlinkSqlApi(self.user, interpreter=self.interpreter)

    # when
    created_session = flink_api.create_session(lang='flink', properties=None)

    # then
    assert created_session == {'id': self.TEST_SESSION_HANDLE, 'type': 'flink'}
    mock_client_instance.configure_session.assert_called_once_with(
      self.TEST_SESSION_HANDLE, 'USE `default_catalog`.`default_database`'
    )
    assert mock_client_instance.session_heartbeat.call_count == 1

  @patch('notebook.connectors.flink_sql.FlinkSqlClient')
  def test_autocomplete_operation_functions(self, client_mock):
    # given: mock interactions
    mock_client_instance = MagicMock()
    client_mock.return_value = mock_client_instance
    mock_client_instance.create_session.return_value = {'sessionHandle': self.TEST_SESSION_HANDLE}
    mock_client_instance.info.return_value = {'version': '2.0.0'}
    mock_client_instance.execute_statement.return_value = {'operationHandle': self.TEST_OPERATION_HANDLE}
    mock_client_instance.fetch_results.return_value = {
      'resultType': 'PAYLOAD',
      'resultKind': 'SUCCESS_WITH_CONTENT',
      'results': {
        'columns': [{'name': 'function name', 'logicalType': {'type': 'VARCHAR', 'nullable': True, 'length': 1000}}],
        'rowFormat': 'JSON',
        'data': [
          {'kind': 'INSERT', 'fields': ['lower']},
          {'kind': 'INSERT', 'fields': ['upper']}
        ]},
      'nextResultUri': f'/v3/sessions/{self.TEST_SESSION_HANDLE}/operations/{self.TEST_OPERATION_HANDLE}/result/1?rowFormat=JSON'
    }

    # and: FlinkSqlApi instance with configuration
    flink_api = FlinkSqlApi(self.user, interpreter=self.interpreter)

    # and: session is created
    flink_api.create_session(lang='flink', properties=None)

    # when
    autocomplete_result = flink_api.autocomplete(snippet='dummy', database=None, table=None, column=None, nested=None,
                                                 operation='functions')

    # then
    mock_client_instance.execute_statement.assert_called_once_with(self.TEST_SESSION_HANDLE, 'SHOW FUNCTIONS')
    assert autocomplete_result == {'functions': [{'name': 'lower'}, {'name': 'upper'}]}

  @patch('notebook.connectors.flink_sql.FlinkSqlClient')
  def test_autocomplete_operation_function_flink_1_x(self, client_mock):
    # given: mock interactions
    mock_client_instance = MagicMock()
    client_mock.return_value = mock_client_instance
    mock_client_instance.create_session.return_value = {'sessionHandle': self.TEST_SESSION_HANDLE}
    mock_client_instance.info.return_value = {'version': '1.20.0'}

    # and: FlinkSqlApi instance with configuration
    flink_api = FlinkSqlApi(self.user, interpreter=self.interpreter)

    # and: session is created
    flink_api.create_session(lang='flink', properties=None)

    # when
    autocomplete_result = flink_api.autocomplete(snippet='dummy', database='test_function', table=None, column=None,
                                                 nested=None, operation='function')

    # then
    assert autocomplete_result == {'function': {'name': 'test_function'}}

  @patch('notebook.connectors.flink_sql.FlinkSqlClient')
  def test_autocomplete_operation_function_flink_2_x(self, client_mock):
    # given: mock interactions
    mock_client_instance = MagicMock()
    client_mock.return_value = mock_client_instance
    mock_client_instance.create_session.return_value = {'sessionHandle': self.TEST_SESSION_HANDLE}
    mock_client_instance.info.return_value = {'version': '2.0.0'}
    mock_client_instance.execute_statement.return_value = {'operationHandle': self.TEST_OPERATION_HANDLE}
    mock_client_instance.fetch_results.return_value = {
      'resultType': 'PAYLOAD',
      'resultKind': 'SUCCESS_WITH_CONTENT',
      'results': {
        'columns': [
          {'name': 'info name', 'logicalType': {'type': 'VARCHAR', 'nullable': True, 'length': 2147483647}},
          {'name': 'info value', 'logicalType': {'type': 'VARCHAR', 'nullable': True, 'length': 2147483647}}
        ],
        'rowFormat': 'JSON',
        'data': [
          {'kind': 'INSERT', 'fields': ['is system function', 'false']},
          {'kind': 'INSERT', 'fields': ['is temporary', 'false']},
          {'kind': 'INSERT', 'fields': ['class name', 'com.example.flink.udf.TestFunction']},
          {'kind': 'INSERT', 'fields': ['function language', 'JAVA']},
          {'kind': 'INSERT', 'fields': ['resource uris', '[]']},
          {'kind': 'INSERT', 'fields': ['kind', 'SCALAR']},
          {'kind': 'INSERT', 'fields': ['requirements', '[]']},
          {'kind': 'INSERT', 'fields': ['is deterministic', 'true']},
          {'kind': 'INSERT', 'fields': ['supports constant folding', 'true']},
          {'kind': 'INSERT', 'fields': ['signature', 'default_catalog.default_db.test_function(values <ANY>...)']},
        ]
      },
      'nextResultUri': f'/v3/sessions/{self.TEST_SESSION_HANDLE}/operations/{self.TEST_OPERATION_HANDLE}/result/1?rowFormat=JSON'
    }

    # and: FlinkSqlApi instance with configuration
    flink_api = FlinkSqlApi(self.user, interpreter=self.interpreter)

    # and: session is created
    flink_api.create_session(lang='flink', properties=None)

    # when
    autocomplete_result = flink_api.autocomplete(snippet='dummy', database='test_function', table=None, column=None,
                                                 nested=None, operation='function')

    # then
    mock_client_instance.execute_statement.assert_called_once_with(
      session_handle=self.TEST_SESSION_HANDLE,
      statement='DESCRIBE FUNCTION EXTENDED test_function'
    )
    assert autocomplete_result == {
      'function': {'name': 'test_function', 'signature': 'default_catalog.default_db.test_function(values <ANY>...)'}
    }
