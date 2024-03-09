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

import unittest
from nose.tools import assert_equal, assert_true, assert_raises, assert_false, assert_in, assert_is_none
from unittest.mock import MagicMock, patch, Mock

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from notebook.connectors.trino import TrinoApi
from useradmin.models import User


class TestTrinoApi(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    # Mock user and interpreter
    cls.client = make_logged_in_client(username="hue_test", groupname="default", recreate=True, is_superuser=False)
    cls.user = User.objects.get(username="hue_test")
    cls.interpreter = {
      'options': {
        'url': 'http://example.com:8080'
      }
    }
    # Initialize TrinoApi with mock user and interpreter
    cls.trino_api = TrinoApi(cls.user, interpreter=cls.interpreter)


  def test_parse_api_url(self):
    # Test parse_api_url method
    api_url = 'http://example.com:8080'
    expected_result = ('example.com', 8080, 'http')
    result = self.trino_api.parse_api_url(api_url)

    assert_equal(result, expected_result)


  def test_autocomplete_with_database(self):
    with patch('notebook.connectors.trino.TrinoApi._show_databases') as _show_databases:
      _show_databases.return_value = [
        {'name': 'test_catalog1.test_db1'}, {'name': 'test_catalog2.test_db1'}, {'name': 'test_catalog2.test_db2'}
      ]
      snippet = {}
      response = self.trino_api.autocomplete(snippet)

      assert_in('databases', response)   # Check if 'databases' key exists in the response
      assert_equal(response['databases'],
      [{'name': 'test_catalog1.test_db1'}, {'name': 'test_catalog2.test_db1'}, {'name': 'test_catalog2.test_db2'}]
      )


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
      
      assert_in('tables_meta', response)   # Check if 'table_meta' key exists in the response
      assert_equal(response['tables_meta'],
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

      assert_in('extended_columns', response)   # Check if 'extended_columns' key exists in the response
      assert_equal(response['extended_columns'],
      [
      {'comment': '', 'name': 'test_column1', 'type': 'str'},
      {'comment': '', 'name': 'test_column2', 'type': 'int'},
      {'comment': '', 'name': 'test_column3', 'type': 'int'}
      ])

      assert_in('columns', response)   # Check if 'columns' key exists in the response
      assert_equal(response['columns'], ['test_column1', 'test_column2', 'test_column3'])


  def test_get_sample_data_success(self):
    with patch('notebook.connectors.trino.TrinoQuery') as TrinoQuery:
      # Mock TrinoQuery object and its execute method
      query_instance = TrinoQuery.return_value
      query_instance.result.rows = [['value1', 'value2'], ['value3', 'value4']]
      query_instance.columns = [
        {'name': 'test_column1', 'type': 'string', 'comment': ''}, {'name': 'test_column2', 'type': 'string', 'comment': ''}
      ]

      # Call the get_sample_data method
      result = self.trino_api.get_sample_data(snippet={}, database='test_db', table='test_table')

      assert_equal(result['status'], 0)
      assert_equal(result['rows'], [['value1', 'value2'], ['value3', 'value4']])
      assert_equal(result['full_headers'],
      [{'name': 'test_column1', 'type': 'string', 'comment': ''}, {'name': 'test_column2', 'type': 'string', 'comment': ''}]
      )


  def test_check_status_available(self):
    mock_trino_request = MagicMock()
    self.trino_api.trino_request = mock_trino_request

    # Configure the MagicMock object to return expected responses
    mock_trino_request.get.return_value = MagicMock()
    mock_trino_request.process.return_value = MagicMock(stats={'state': 'FINISHED'}, next_uri='http://url')

    # Call the check_status method
    result = self.trino_api.check_status(notebook={}, snippet={'result': {'handle': {'next_uri': 'http://url'}}})

    assert_equal(result['status'], 'available')
    assert_equal(result['next_uri'], 'http://url')


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
      result = self.trino_api.execute(notebook={}, snippet={'database': 'test_db', 'statement': 'SELECT * FROM test_table;'})

      expected_result = {
        'row_count': 0,
        'next_uri': 'http://url',
        'sync': None,
        'has_result_set': True,
        'guid': 123,
        'result': {
          'has_more': True,
          'data': [],
          'meta': [],
          'type': 'table'
        }
      }
      assert_equal(result, expected_result)


  def test_fetch_result(self):
    # Mock TrinoRequest object and its methods
    mock_trino_request = MagicMock()
    self.trino_api.trino_request = mock_trino_request

    # Configure the MagicMock object to return expected responses
    mock_trino_request.get.return_value = MagicMock()
    _columns = [{'comment': '', 'name': 'test_column1', 'type': 'str'}, {'comment': '', 'name': 'test_column2', 'type': 'str'}]

    mock_trino_request.process.side_effect = [
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri='http://url', id=123,
        rows=[['value1', 'value2'], ['value3', 'value4']], columns=_columns
      ),
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri='http://url1', id=124,
        rows=[['value5', 'value6'], ['value7', 'value8']], columns=_columns
      ),
      MagicMock(
        stats={'state': 'FINISHED'}, next_uri=None, id=125,
        rows=[['value9', 'value10'], ['value11', 'value12']], columns=_columns
      )
    ]

    # Call the fetch_result method
    result = self.trino_api.fetch_result(
      notebook={}, snippet={'result': {'handle': {'next_uri': 'http://url', 'result': {'data': []}}}}, rows=0, start_over=False
    )

    expected_result = {
      'row_count': 94,
      'next_uri': None,
      'has_more': False,
      'data': [
        ['value1', 'value2'], ['value3', 'value4'], ['value5', 'value6'],
        ['value7', 'value8'], ['value9', 'value10'], ['value11', 'value12']
      ],
      'meta': [{
        'name': column['name'],
        'type': column['type'],
        'comment': ''
        } for column in _columns],
      'type': 'table'
    }
    
    assert_equal(result, expected_result)
    assert_equal(len(result['data']), 6)
    assert_equal(len(result['meta']), 2)


  def test_get_select_query(self):
    # Test with specified database, table, and column
    database = 'test_db'
    table = 'test_table'
    column = 'test_column'
    expected_statement = (
        "SELECT test_column\n"
        "FROM test_db.test_table\n"
        "LIMIT 100\n"
    )
    assert_equal(
      self.trino_api._get_select_query(database, table, column),
      expected_statement
    )

    # Test with default parameters
    database = 'test_db'
    table = 'test_table'
    expected_statement = (
        "SELECT *\n"
        "FROM test_db.test_table\n"
        "LIMIT 100\n"
    )
    assert_equal(
      self.trino_api._get_select_query(database, table),
      expected_statement
    )
