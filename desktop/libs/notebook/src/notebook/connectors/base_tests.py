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

import inspect
import os
import re
from builtins import object
from unittest.mock import Mock, patch

import pytest

from desktop.lib.django_test_util import make_logged_in_client
from notebook.connectors.base import ExecutionWrapper, get_api, Notebook
from useradmin.models import User


@pytest.mark.django_db
class TestNotebook(object):

  def setup_method(self):
    self.client = make_logged_in_client(username="test", groupname="empty", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_get_api(self):
    request = Mock()
    snippet = {
      'connector': {'optimizer': 'api'},
      'type': 'hive'  # Backward compatibility
    }

    get_api(request=request, snippet=snippet)

  def test_execute_and_wait(self):
    query = Notebook()

    query.execute = Mock(return_value={'history_uuid': 1, 'status': 0})
    query.check_status = Mock(
      side_effect=check_status_side_effect
    )
    query.fetch_result_data = Mock(
      return_value={'results': [[1], [2]]}
    )
    request = Mock()

    resp = query.execute_and_wait(request=request, include_results=True)

    assert 0 == resp.get('status'), resp
    assert 'available' == resp['query_status']['status'], resp
    assert [[1], [2]] == resp.get('results'), resp

    assert 2 == query.check_status.call_count

  def test_check_status(self):
    query = Notebook()

    request = Mock()
    operation_id = Mock()

    with patch('notebook.api.Document2.objects.get_by_uuid'):
      with patch('notebook.api.get_api') as get_api:
        with patch('notebook.api.Notebook'):
          get_api.return_value = Mock(
            check_status=Mock(return_value={'status': 0})
          )
          resp = query.check_status(request=request, operation_id=operation_id)

          assert 0 == resp['status']
          assert 0 == resp['query_status']['status']

  def test_statement_with_variables(self):
    snippet = {
      'statement_raw': "SELECT * FROM table WHERE city='${city}'",
      'type': 'hive',
      'variables': [
        {'name': 'city', 'value': 'San Francisco'},
      ]
    }

    assert (
      "SELECT * FROM table WHERE city='San Francisco'" ==
      Notebook.statement_with_variables(snippet))

    snippet['variables'][0]['value'] = 'Saint-Étienne'

    assert (
      "SELECT * FROM table WHERE city='Saint-Étienne'" ==
      Notebook.statement_with_variables(snippet))


@pytest.mark.django_db
class TestExecutionWrapperUntilAvailable(object):
  """
  Covers ExecutionWrapper._until_available()'s persistence of a connector's next_uri and any
  row data piggybacked on a status poll. This loop calls check_status() repeatedly against the
  same self.snippet -- if the advanced next_uri isn't written back after each poll, every
  iteration re-requests the same already-consumed Trino continuation URI, which is exactly what
  caused CSV/Excel downloads (which re-execute and poll to completion server-side, independent
  of the browser-facing check_status/fetch_result_data flow) to come back with no row data.
  """

  def _make_wrapper(self, next_uri='http://trino/1'):
    api = Mock()
    api.get_log_is_full_log.return_value = False
    snippet = {'result': {'handle': {'guid': 'test-guid', 'next_uri': next_uri}}}
    return ExecutionWrapper(api, notebook={}, snippet=snippet), api, snippet

  def test_persists_advancing_next_uri_and_polled_rows(self):
    wrapper, api, snippet = self._make_wrapper()
    api.check_status.side_effect = [
      {'status': 'running', 'next_uri': 'http://trino/2'},
      {
        'status': 'available',
        'next_uri': 'http://trino/3',
        'result': {'data': [['a'], ['b']], 'meta': [{'name': 'col', 'type': 'string', 'comment': ''}], 'type': 'table'}
      }
    ]

    wrapper._until_available()

    handle = snippet['result']['handle']
    assert handle['next_uri'] == 'http://trino/3'
    assert handle['result']['data'] == [['a'], ['b']]
    assert api.check_status.call_count == 2

  def test_accumulates_polled_rows_across_multiple_polls(self):
    wrapper, api, snippet = self._make_wrapper()
    api.check_status.side_effect = [
      {'status': 'running', 'next_uri': 'http://trino/2', 'result': {'data': [['a']], 'meta': [], 'type': 'table'}},
      {'status': 'available', 'next_uri': 'http://trino/3', 'result': {'data': [['b']], 'meta': [], 'type': 'table'}}
    ]

    wrapper._until_available()

    assert snippet['result']['handle']['result']['data'] == [['a'], ['b']]

  def test_does_not_touch_next_uri_for_connectors_that_dont_report_it(self):
    # Non-Trino connectors' check_status() responses have no 'next_uri' key at all -- the
    # handle's next_uri (if any) must be left untouched in that case.
    wrapper, api, snippet = self._make_wrapper(next_uri='http://trino/1')
    api.check_status.return_value = {'status': 'available'}

    wrapper._until_available()

    assert snippet['result']['handle']['next_uri'] == 'http://trino/1'


iteration = 0


def check_status_side_effect(request, operation_id):
  """First time query is still running, second time the execution is finished."""
  global iteration

  if iteration == 0:
    iteration += 1
    return {'status': 0, 'query_status': {'status': 'running'}}
  else:
    return {'status': 0, 'query_status': {'status': 'available'}}


@pytest.mark.django_db
class TestConnectorApiCompatibility(object):
  """
  Test API compatibility across all connectors to prevent signature mismatches.
  This ensures that when new parameters are added to the base API, all connectors
  remain compatible and don't break due to signature differences.
  """

  def setup_method(self):
    self.client = make_logged_in_client(username="test_connector_compatibility", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test_connector_compatibility")

  def teardown_method(self):
    User.objects.filter(username="test_connector_compatibility").delete()

  def test_base_api_method_signatures(self):
    """
    Test that the base Api class has the expected method signatures that all connectors should follow.
    """
    from notebook.connectors.base import Api

    # Check base get_sample_data signature
    base_method = getattr(Api, 'get_sample_data', None)
    assert base_method is not None, "Base Api class missing get_sample_data method"

    sig = inspect.signature(base_method)
    expected_params = {'self', 'snippet', 'database', 'table', 'column', 'nested', 'is_async', 'operation'}
    actual_params = set(sig.parameters.keys())

    assert expected_params == actual_params, f"Base Api method signature changed. Expected: {expected_params}, Got: {actual_params}"

    # Verify nested parameter has default None
    nested_param = sig.parameters.get('nested')
    assert nested_param is not None, "nested parameter missing from base Api"
    assert nested_param.default is None, f"nested parameter should default to None, got: {nested_param.default}"

  def test_source_code_signature_compatibility(self):
    """
    Test connector method signatures by parsing source code directly.
    This is the most reliable way to check signatures, avoiding decorator interference.
    """
    # Define connectors and their file paths
    connector_files = [
      ('SqlAlchemy', 'desktop/libs/notebook/src/notebook/connectors/sql_alchemy.py'),
      ('Spark', 'desktop/libs/notebook/src/notebook/connectors/spark_shell.py'),
      ('HiveServer2', 'desktop/libs/notebook/src/notebook/connectors/hiveserver2.py'),
      ('Flink', 'desktop/libs/notebook/src/notebook/connectors/flink_sql.py'),
      ('JDBC', 'desktop/libs/notebook/src/notebook/connectors/jdbc.py'),
      ('RDBMS', 'desktop/libs/notebook/src/notebook/connectors/rdbms.py'),
      ('Solr', 'desktop/libs/notebook/src/notebook/connectors/solr.py'),
      ('KSQL', 'desktop/libs/notebook/src/notebook/connectors/ksql.py'),
      ('SQLFlow', 'desktop/libs/notebook/src/notebook/connectors/sqlflow.py'),
      ('Trino', 'desktop/libs/notebook/src/notebook/connectors/trino.py'),
      ('HiveMetastore', 'desktop/libs/notebook/src/notebook/connectors/hive_metastore.py'),
    ]

    failed_connectors = []
    passed_connectors = []

    # Pattern to match get_sample_data method definition
    method_pattern = r'def get_sample_data\(([^)]+)\):'

    for name, file_path in connector_files:
      try:
        if not os.path.exists(file_path):
          continue

        # Read the source file
        with open(file_path, 'r') as f:
          content = f.read()

        # Find get_sample_data method signature
        match = re.search(method_pattern, content)

        if not match:
          continue

        signature_params = match.group(1)

        # Check for nested parameter
        has_nested = 'nested' in signature_params
        has_kwargs = '**kwargs' in signature_params

        if not has_nested and not has_kwargs:
          failed_connectors.append(f"{name}: Missing 'nested' parameter in source: {signature_params}")
        else:
          passed_connectors.append(name)

      except Exception as e:
        failed_connectors.append(f"{name}: Error reading source file: {e}")

    # Report results
    if failed_connectors:
      failure_details = '\n'.join([f"- {f}" for f in failed_connectors])
      assert False, f"Source Code Compatibility Test Failed!\n\nConnectors missing 'nested' parameter:\n{failure_details}"
