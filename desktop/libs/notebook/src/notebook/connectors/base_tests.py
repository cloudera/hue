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
from notebook.connectors.base import get_api, Notebook
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
