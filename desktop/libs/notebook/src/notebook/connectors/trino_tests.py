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

import pytest
from django.test import TestCase

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.rest.http_client import RestException
from notebook.connectors.base import QueryError
from notebook.connectors.trino import query_error_handler, TrinoApi
from useradmin.models import User


def query_result(rows):
  """A stand-in for the TrinoResult of the Trino client, which returns all of its rows (all pages) when iterated."""
  result = MagicMock()
  result.__iter__.return_value = iter(rows)
  return result


class TestTrinoApi(TestCase):

  @classmethod
  def setup_class(cls):
    # Mock user and interpreter
    cls.client = make_logged_in_client(username="hue_test", groupname="default", recreate=True, is_superuser=False)
    cls.user = User.objects.get(username="hue_test")
    cls.interpreter = {
      'options': {
        'url': 'https://example.com:8080'
      },
      'name': 'trino'
    }
    # Initialize TrinoApi with mock user and interpreter
    cls.trino_api = TrinoApi(cls.user, interpreter=cls.interpreter)

  def test_format_identifier(self):
    # db name test
    test_cases = [
      ("my_db", '"my_db"'),
      ("my_catalog.my_db", '"my_catalog"."my_db"'),
    ]

    for database, expected_output in test_cases:
      assert self.trino_api._format_identifier(database, is_db=True) == expected_output

    # table name test
    test_cases = [
      ("io.airlift.discovery.store:name=dynamic,type=distributedstore", '"io.airlift.discovery.store:name=dynamic,type=distributedstore"'),
      ("table", '"table"'),
    ]

    for table, expected_output in test_cases:
      assert self.trino_api._format_identifier(table) == expected_output

  def test_parse_api_url(self):
    # Test parse_api_url method
    api_url = 'http://example.com:8080'
    expected_result = ('example.com', 8080, 'http')
    result = self.trino_api.parse_api_url(api_url)

    assert result == expected_result

  def test_autocomplete_with_database(self):
    with patch('notebook.connectors.trino.TrinoApi._show_databases') as _show_databases:
      _show_databases.return_value = [
        {'name': 'test_catalog1.test_db1'}, {'name': 'test_catalog2.test_db1'}, {'name': 'test_catalog2.test_db2'}
      ]
      snippet = {}
      response = self.trino_api.autocomplete(snippet)

      assert 'databases' in response   # Check if 'databases' key exists in the response
      assert (response['databases'] ==
      [{'name': 'test_catalog1.test_db1'}, {'name': 'test_catalog2.test_db1'}, {'name': 'test_catalog2.test_db2'}])

  def test_autocomplete_with_database_and_table(self):
    with patch('notebook.connectors.trino.TrinoApi._show_tables') as _show_tables:
      _show_tables.return_value = [
        {'name': 'test_table1', 'type': 'table', 'comment': ''},
        {'name': 'test_table2', 'type': 'table', 'comment': ''},
        {'name': 'test_table3', 'type': 'table', 'comment': ''}
      ]
      snippet = {}
      database = 'test_db1'
      response = self.trino_api.autocomplete(snippet, database)

      assert 'tables_meta' in response   # Check if 'table_meta' key exists in the response
      assert (response['tables_meta'] ==
      [
      {'name': 'test_table1', 'type': 'table', 'comment': ''},
      {'name': 'test_table2', 'type': 'table', 'comment': ''},
      {'name': 'test_table3', 'type': 'table', 'comment': ''}
      ])

  def test_autocomplete_with_database_table_and_column(self):
    with patch('notebook.connectors.trino.TrinoApi._get_columns') as _get_columns:
      _get_columns.return_value = [
        {'name': 'test_column1', 'type': 'str', 'comment': ''},
        {'name': 'test_column2', 'type': 'int', 'comment': ''},
        {'name': 'test_column3', 'type': 'int', 'comment': ''}
      ]
      snippet = {}
      database = 'test_db1'
      table = 'test_table1'
      response = self.trino_api.autocomplete(snippet, database, table)

      assert 'extended_columns' in response   # Check if 'extended_columns' key exists in the response
      assert (response['extended_columns'] ==
      [
      {'comment': '', 'name': 'test_column1', 'type': 'str'},
      {'comment': '', 'name': 'test_column2', 'type': 'int'},
      {'comment': '', 'name': 'test_column3', 'type': 'int'}
      ])

      assert 'columns' in response   # Check if 'columns' key exists in the response
      assert response['columns'] == ['test_column1', 'test_column2', 'test_column3']

  def test_get_sample_data_success(self):
    with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
      # Mock TrinoQuery object and its execute method
      query_instance = TrinoQuery.return_value
      query_instance.execute.return_value = query_result([['value1', 'value2'], ['value3', 'value4']])
      query_instance.columns = [
        {'name': 'test_column1', 'type': 'string', 'comment': ''}, {'name': 'test_column2', 'type': 'string', 'comment': ''}
      ]

      # Call the get_sample_data method
      result = self.trino_api.get_sample_data(snippet={}, database='test_db', table='test_table')

      assert result['status'] == 0
      assert result['rows'] == [['value1', 'value2'], ['value3', 'value4']]
      assert (result['full_headers'] ==
      [{'name': 'test_column1', 'type': 'string', 'comment': ''}, {'name': 'test_column2', 'type': 'string', 'comment': ''}])

  def test_check_status_available(self):
    mock_trino_request = MagicMock()
    self.trino_api.trino_request = mock_trino_request

    # Configure the MagicMock object to return expected responses
    mock_trino_request.get.return_value = MagicMock()
    mock_trino_request.process.return_value = MagicMock(stats={'state': 'FINISHED'}, next_uri='http://url')

    # Call the check_status method
    result = self.trino_api.check_status(notebook={}, snippet={'result': {'handle': {'next_uri': 'http://url'}}})

    assert result['status'] == 'available'
    assert result['next_uri'] == 'http://url'

  def test_execute(self):
    with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
      # Mock TrinoQuery object and its methods
      mock_query_instance = TrinoQuery.return_value
      mock_query_instance.query = "SELECT * FROM test_table"
      mock_query_instance.execute.return_value = MagicMock(next_uri=None, id='123', rows=[], columns=[])

      mock_trino_request = MagicMock()
      self.trino_api.trino_request = mock_trino_request

      # Configure the MagicMock object to return expected responses
      mock_trino_request.get.return_value = MagicMock()
      mock_trino_request.process.return_value = MagicMock(stats={'state': 'FINISHED'}, next_uri='http://url', id=123, rows=[])

      # Call the execute method
      snippet = {
        'database': 'test_db',
        'statement': 'SELECT * FROM test_table;',
        'result': {'handle': {}}
      }
      result = self.trino_api.execute(notebook={}, snippet=snippet)

      expected_result = {
        'row_count': 0,
        'rows_remaining': 0,
        'next_uri': 'http://url',
        'sync': None,
        'has_result_set': True,
        'guid': 123,
        'result': {
          'has_more': True,
          'data': [],
          'meta': [],
          'type': 'table'
        },
        'statement_id': 0, 'has_more_statements': False, 'statements_count': 1,
        'previous_statement_hash': 'd1c7e7dd8869098919761253c921eea865d48ca79d4e43092c321cfd',
        'start': {'row': 0, 'column': 0}, 'end': {'row': 0, 'column': 23}, 'statement': 'SELECT * FROM test_table'
      }
      assert result == expected_result

      # Test multiple query execution
      snippet = {
        'database': 'test_db',
        'statement': 'use test_db;\nshow tables',
        'result': {'handle': {}}
      }
      result = self.trino_api.execute(notebook={}, snippet=snippet)

      expected_result = {
        'row_count': 0,
        'rows_remaining': 0,
        'next_uri': 'http://url',
        'sync': None,
        'has_result_set': True,
        'guid': 123,
        'result': {
          'has_more': True,
          'data': [],
          'meta': [],
          'type': 'table'
        },
        'statement_id': 0, 'has_more_statements': True, 'statements_count': 2,
        'previous_statement_hash': '793204944f1800a86d75684d4be11eccb03b35f68441febb1362fd35',
        'start': {'row': 0, 'column': 0}, 'end': {'row': 0, 'column': 12}, 'statement': 'use test_db'
      }
      assert result == expected_result

  def test_fetch_result_more_than_100(self):
    # Mock TrinoRequest object and its methods
    mock_trino_request = MagicMock()
    self.trino_api.trino_request = mock_trino_request

    # Configure the MagicMock object to return expected responses
    mock_trino_request.get.return_value = MagicMock()
    _columns = [{'comment': '', 'name': 'test_column1', 'type': 'str'}, {'comment': '', 'name': 'test_column2', 'type': 'str'}]

    # Generate more than 100 rows of mock data
    mock_data = [[f'value{i}', f'value{i + 1}'] for i in range(1, 201, 1)]

    mock_trino_request.process.side_effect = [
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri='http://url1', id=123,
        rows=mock_data[:57], columns=_columns
      ),
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri='http://url2', id=124,
        rows=mock_data[57:105], columns=_columns
      ),
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri=None, id=125,
        rows=mock_data[105:], columns=_columns
      )
    ]

    # Call the fetch_result method
    result = self.trino_api.fetch_result(
      notebook={}, snippet={'result': {'handle': {'next_uri': 'http://url', 'result': {'data': []}}}}, rows=0, start_over=False
    )

    expected_result = {
      'row_count': 100,
      'rows_remaining': 5,
      'next_uri': 'http://url1',
      'has_more': True,
      'data': mock_data[:100],
      'meta': [{
        'name': column['name'],
        'type': column['type'],
        'comment': ''
        } for column in _columns],
      'type': 'table'
    }

    assert result == expected_result
    assert len(result['data']) == 100
    assert len(result['meta']) == 2

  def test_fetch_result_less_than_100(self):
    # Mock TrinoRequest object and its methods
    mock_trino_request = MagicMock()
    self.trino_api.trino_request = mock_trino_request

    # Configure the MagicMock object to return expected responses
    mock_trino_request.get.return_value = MagicMock()
    _columns = [{'comment': '', 'name': 'test_column1', 'type': 'str'}, {'comment': '', 'name': 'test_column2', 'type': 'str'}]

    # Generate 100 rows of mock data
    mock_data = [[f'value{i}', f'value{i + 1}'] for i in range(1, 90, 1)]

    mock_trino_request.process.side_effect = [
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri='http://url1', id=123,
        rows=mock_data[:57], columns=_columns
      ),
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri=None, id=124,
        rows=mock_data[57:], columns=_columns
      )
    ]

    # Call the fetch_result method
    result = self.trino_api.fetch_result(
      notebook={}, snippet={'result': {'handle': {'next_uri': 'http://url', 'result': {'data': []}}}}, rows=0, start_over=False
    )

    expected_result = {
      'row_count': 89,
      'rows_remaining': 0,
      'next_uri': None,
      'has_more': False,
      'data': mock_data[:90],
      'meta': [{
        'name': column['name'],
        'type': column['type'],
        'comment': ''
        } for column in _columns],
      'type': 'table'
    }

    assert result == expected_result
    assert len(result['data']) == 89
    assert len(result['meta']) == 2

  def test_get_select_query(self):
    # Test with specified database, table, and column
    database = '`test_schema.test_db`'
    table = '`test_table`'
    column = 'test_column'
    expected_statement = (
        'SELECT "test_column"\n'
        'FROM "test_schema"."test_db"."test_table"\n'
        'LIMIT 100\n'
    )
    assert (
      self.trino_api._get_select_query(database, table, column) ==
      expected_statement)

    # Test with default parameters
    database = 'test_db'
    table = 'test_table'
    expected_statement = (
        'SELECT *\n'
        'FROM "test_db"."test_table"\n'
        'LIMIT 100\n'
    )
    assert (
      self.trino_api._get_select_query(database, table) ==
      expected_statement)

  def test_explain(self):
    with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
      snippet = {'statement': 'SELECT * FROM tpch.sf1.partsupp LIMIT 100;', 'database': 'tpch.sf1'}
      output = [['Trino version: 432\nFragment 0 [SINGLE]\n    Output layout: [partkey, suppkey, availqty, supplycost, comment]\n    '
      'Output partitioning: SINGLE []\n    Output[columnNames = [partkey, suppkey, availqty, supplycost, comment]]\n    │   '
      'Layout: [partkey:bigint, suppkey:bigint, availqty:integer, supplycost:double, comment:varchar(199)]\n    │   '
      'Estimates: {rows: 100 (15.67kB), cpu: 0, memory: 0B, network: 0B}\n    └─ Limit[count = 100]\n       │   '
      'Layout: [partkey:bigint, suppkey:bigint, availqty:integer, supplycost:double, comment:varchar(199)]\n       │   '
      'Estimates: {rows: 100 (15.67kB), cpu: 15.67k, memory: 0B, network: 0B}\n       └─ LocalExchange[partitioning = SINGLE]\n          '
      '│   Layout: [partkey:bigint, suppkey:bigint, availqty:integer, supplycost:double, comment:varchar(199)]\n          │   '
      'Estimates: {rows: 100 (15.67kB), cpu: 0, memory: 0B, network: 0B}\n          └─ RemoteSource[sourceFragmentIds = [1]]\n'
      '                 Layout: [partkey:bigint, suppkey:bigint, availqty:integer, supplycost:double, comment:varchar(199)]\n\n'
      'Fragment 1 [SOURCE]\n    Output layout: [partkey, suppkey, availqty, supplycost, comment]\n    Output partitioning: SINGLE []\n'
      '    LimitPartial[count = 100]\n    │   Layout: [partkey:bigint, suppkey:bigint, availqty:integer, supplycost:double, '
      'comment:varchar(199)]\n    │   Estimates: {rows: 100 (15.67kB), cpu: 15.67k, memory: 0B, network: 0B}\n    └─ '
      'TableScan[table = tpch:sf1:partsupp]\n           Layout: [partkey:bigint, suppkey:bigint, availqty:integer, supplycost:double, '
      'comment:varchar(199)]\n           Estimates: {rows: 800000 (122.44MB), cpu: 122.44M, memory: 0B, network: 0B}\n           '
      'partkey := tpch:partkey\n           availqty := tpch:availqty\n           supplycost := tpch:supplycost\n           '
      'comment := tpch:comment\n           suppkey := tpch:suppkey\n\n']]
      # Mock TrinoQuery object and its execute method
      query_instance = TrinoQuery.return_value
      query_instance.execute.return_value = query_result(output)

      # Call the explain method
      result = self.trino_api.explain(notebook=None, snippet=snippet)

      # Assert the result
      assert result['status'] == 0
      assert result['explanation'] == output
      assert result['statement'] == 'SELECT * FROM tpch.sf1.partsupp LIMIT 100'

      query_instance = TrinoQuery.return_value
      query_instance.execute.side_effect = Exception('Mocked exception')

      # Call the explain method
      result = self.trino_api.explain(notebook=None, snippet=snippet)

      # Assert the exception message
      assert result['explanation'] == 'Mocked exception'

  @patch('notebook.connectors.trino.DEFAULT_AUTH_USERNAME.get', return_value='mocked_username')
  @patch('notebook.connectors.trino.DEFAULT_AUTH_PASSWORD.get', return_value='mocked_password')
  def test_auth_username_and_auth_password_default(self, mock_default_username, mock_default_password):
    trino_api = TrinoApi(self.user, interpreter=self.interpreter)

    assert trino_api.auth_username == 'mocked_username'
    assert trino_api.auth_password == 'mocked_password'

  @patch('notebook.connectors.trino.DEFAULT_AUTH_USERNAME.get', return_value='mocked_username')
  @patch('notebook.connectors.trino.DEFAULT_AUTH_PASSWORD.get', return_value='mocked_password')
  def test_auth_username_custom(self, mock_default_username, mock_default_password):
    interpreter = {
      'options': dict(self.interpreter['options'], auth_username='custom_username', auth_password='custom_password'),
      'name': 'trino'
    }
    trino_api = TrinoApi(self.user, interpreter=interpreter)

    assert trino_api.auth_username == 'custom_username'
    assert trino_api.auth_password == 'custom_password'

  @patch('notebook.connectors.trino.DEFAULT_AUTH_PASSWORD.get', return_value='mocked_password')
  def test_auth_password_script(self, mock_default_password):
    interpreter = {
      'options': {
        'url': 'https://example.com:8080',
        'auth_password_script': 'custom_script'
      },
      'name': 'trino'
    }

    with patch('notebook.connectors.trino.coerce_password_from_script', return_value='custom_password_script'):
      trino_api = TrinoApi(self.user, interpreter=interpreter)
      assert trino_api.auth_password == 'custom_password_script'

  def test_get_log(self):
    notebook = {}
    snippet = {
      'result': {
        'handle': {
          'guid': '1234-abcd-5678-efgh'
        }
      }
    }

    # Expected result
    expected_log = "query_id: 1234-abcd-5678-efgh"
    result = self.trino_api.get_log(notebook, snippet)

    assert result == expected_log

  def test_show_databases(self):
    with patch('notebook.connectors.trino.LOG.error') as Log_error:
      with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
        with patch('notebook.connectors.trino.TrinoApi._show_catalogs') as _show_catalogs:
          _show_catalogs.return_value = [
            'catalog1', 'catalog2'
          ]
          query_instance = TrinoQuery.return_value
          query_instance.execute.side_effect = [
            query_result([["schema1"], ["schema2"]]),  # First catalog response
            Exception("Some error")  # Second catalog raises an exception
          ]
          result = self.trino_api._show_databases()

          # Assert the expected output
          expected_result = ['catalog1.schema1', 'catalog1.schema2']
          self.assertEqual(result, expected_result)

          # Assert error logging was called for the exception
          Log_error.assert_called_once_with(
            "Failed to fetch schemas from catalog catalog2: Some error"
          )

  def _create_api(self, **options):
    interpreter = {'options': dict({'url': 'https://example.com:8443'}, **options), 'name': 'trino'}
    return TrinoApi(self.user, interpreter=interpreter)

  def test_parse_api_url_defaults(self):
    assert self.trino_api.parse_api_url('http://example.com') == ('example.com', 8080, 'http')
    assert self.trino_api.parse_api_url('https://example.com') == ('example.com', 443, 'https')
    assert self.trino_api.parse_api_url('https://example.com:8443') == ('example.com', 8443, 'https')

  @patch('notebook.connectors.trino.DEFAULT_AUTH_USERNAME.get', return_value='global_username')
  @patch('notebook.connectors.trino.DEFAULT_AUTH_PASSWORD.get', return_value='global_password')
  def test_empty_interpreter_credentials_fall_back_to_the_global_ones(self, mock_default_password, mock_default_username):
    trino_api = self._create_api(auth_username='', auth_password='')

    assert trino_api.auth_username == 'global_username'
    assert trino_api.auth_password == 'global_password'

  @patch('notebook.connectors.trino.DEFAULT_AUTH_USERNAME.get', return_value=None)
  @patch('notebook.connectors.trino.DEFAULT_AUTH_PASSWORD.get', return_value=None)
  def test_no_credentials_means_no_authentication(self, mock_default_password, mock_default_username):
    assert self._create_api().auth is None

  def test_credentials_are_ignored_over_http(self):
    # The Trino client refuses to send credentials over plain HTTP
    with patch('notebook.connectors.trino.LOG.warning') as log_warning:
      trino_api = self._create_api(url='http://example.com:8080', auth_username='username', auth_password='password')

    assert trino_api.auth is None
    log_warning.assert_called_once()

  def test_credentials_are_used_over_https(self):
    with patch('notebook.connectors.trino.TrinoRequest') as trino_request:
      trino_api = self._create_api(auth_username='username', auth_password='password')

    assert trino_api.auth is not None
    assert trino_request.call_args.kwargs['auth'] is trino_api.auth

  @patch('notebook.connectors.trino.DEFAULT_AUTH_PASSWORD.get', return_value=None)
  def test_password_script_is_not_run_when_a_password_is_given(self, mock_default_password):
    with patch('notebook.connectors.trino.coerce_password_from_script') as coerce_password_from_script:
      trino_api = self._create_api(auth_username='username', auth_password='password', auth_password_script='script')

    coerce_password_from_script.assert_not_called()
    assert trino_api.auth_password == 'password'

  def test_ssl_verify(self):
    test_cases = [
      ({}, True),
      ({'ssl_verify': True}, True),
      ({'ssl_verify': False}, False),
      ({'ssl_verify': 'true'}, True),
      ({'ssl_verify': ' False '}, False),
      ({'ssl_verify': '/etc/ssl/ca.pem'}, '/etc/ssl/ca.pem'),
    ]

    for options, expected_verify in test_cases:
      with patch('notebook.connectors.trino.TrinoRequest') as trino_request:
        trino_api = self._create_api(**options)

      assert trino_api.ssl_verify == expected_verify, options
      assert trino_request.call_args.kwargs['verify'] == expected_verify, options

  def test_trino_user(self):
    assert self._create_api().trino_session.user == self.user.username
    assert self._create_api(trino_user='service_user').trino_session.user == 'service_user'

  def test_create_session_properties(self):
    with patch.object(self.trino_api, '_get_session_info_from_user', return_value=None):
      assert self.trino_api.create_session()['properties'] == {}
      assert self.trino_api.create_session(properties={'query_max_run_time': '1h'})['properties'] == {'query_max_run_time': '1h'}

  def test_fetch_result_has_more_when_the_last_page_has_rows_left(self):
    mock_trino_request = MagicMock()
    self.trino_api.trino_request = mock_trino_request
    mock_data = [[f'value{i}'] for i in range(150)]
    mock_trino_request.process.return_value = MagicMock(
      stats={'state': 'FINISHED'}, next_uri=None, id=123, rows=mock_data, columns=[{'name': 'col', 'type': 'str'}]
    )

    result = self.trino_api.fetch_result(
      notebook={}, snippet={'result': {'handle': {'next_uri': 'http://url', 'result': {'data': []}}}}, rows=0, start_over=False
    )

    assert len(result['data']) == 100
    assert result['rows_remaining'] == 50
    assert result['next_uri'] == 'http://url'
    assert result['has_more'] is True

  def test_cancel(self):
    mock_trino_request = MagicMock()
    self.trino_api.trino_request = mock_trino_request

    assert self.trino_api.cancel(notebook={}, snippet={'result': {'handle': {'next_uri': 'http://url'}}}) == {'status': 0}
    mock_trino_request.delete.assert_called_once_with('http://url')

    assert self.trino_api.cancel(notebook={}, snippet={'result': {'handle': {'next_uri': None}}}) == {'status': -1}

  def test_use_database(self):
    with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
      self.trino_api._use_database(None)
      TrinoQuery.assert_not_called()

      self.trino_api._use_database('my-catalog.my_schema')
      TrinoQuery.assert_called_once_with(self.trino_api.trino_request, 'USE "my-catalog"."my_schema"')

  def test_show_databases_quotes_the_catalog(self):
    with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
      with patch('notebook.connectors.trino.TrinoApi._show_catalogs', return_value=['my-catalog']):
        TrinoQuery.return_value.execute.return_value = query_result([['my_schema']])

        assert self.trino_api._show_databases() == ['my-catalog.my_schema']

    TrinoQuery.assert_called_once_with(self.trino_api.trino_request, 'SHOW SCHEMAS FROM "my-catalog"')

  def test_metadata_queries_read_all_the_pages(self):
    with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
      # Only the first page is available as the rows of the result, the iteration goes through all of them
      result = query_result([['table1'], ['table2'], ['table3']])
      result.rows = [['table1']]
      TrinoQuery.return_value.execute.return_value = result

      tables = self.trino_api._show_tables('my_catalog.my_schema')

    assert [table['name'] for table in tables] == ['table1', 'table2', 'table3']

  def test_query_error_handler(self):
    @query_error_handler
    def fail_with_rest_exception():
      raise RestException(Exception('the server failed'))

    @query_error_handler
    def fail_with_json_errors():
      raise RestException(Exception('{"errors": "bad query"}'))

    with pytest.raises(QueryError, match='the server failed'):
      fail_with_rest_exception()

    with pytest.raises(QueryError, match='bad query'):
      fail_with_json_errors()
