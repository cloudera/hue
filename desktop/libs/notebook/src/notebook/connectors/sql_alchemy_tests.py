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

from builtins import object
import logging
import sys

from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false, raises
from sqlalchemy.exc import UnsupportedCompilationError
from sqlalchemy.types import NullType, ARRAY, JSON, VARCHAR

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

from notebook.connectors.base import AuthenticationRequired
from notebook.connectors.sql_alchemy import SqlAlchemyApi, Assist


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


LOG = logging.getLogger(__name__)


class TestApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)

    self.user = rewrite_user(User.objects.get(username="test"))
    self.interpreter = {
      'name': 'hive',
      'options': {
        'url': 'mysql://hue:localhost@hue:3306/hue'
      },
    }


  def test_column_backticks_escaping(self):
    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'mysql://'
      }
    }
    assert_equal(SqlAlchemyApi(self.user, interpreter).backticks, '`')

    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'postgresql://'
      }
    }
    assert_equal(SqlAlchemyApi(self.user, interpreter).backticks, '"')


  def test_create_athena_engine(self):
    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'awsathena+rest://XXXXXXXXXXXXXXX:XXXXXXXXXXXXXXXXXXX@athena.us-west-2.amazonaws.com:443/default?'
            's3_staging_dir=s3://gethue-athena/scratch'
      }
    }

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      SqlAlchemyApi(self.user, interpreter)._create_engine()


  def test_fetch_result_empty(self):
    notebook = Mock()
    snippet = {'result': {'handle': {'guid': 'guid-1'}}}
    rows = 10
    start_over = True

    with patch('notebook.connectors.sql_alchemy.CONNECTIONS') as CONNECTIONS:
      CONNECTIONS.get = Mock(
        return_value={
          'result': Mock(
            fetchmany=Mock(return_value=[]) # We have 0 rows
          ),
          'meta': MagicMock(
            __getitem__=Mock(return_value={'type': 'BIGINT_TYPE'}),
            return_value=[{'type': 'BIGINT_TYPE'}]
          )
        }
      )

      data = SqlAlchemyApi(self.user, self.interpreter).fetch_result(notebook, snippet, rows, start_over)

      assert_false(data['has_more'])
      assert_not_equal(data['has_more'], [])
      assert_equal(data['has_more'], False)

      assert_equal(data['data'], [])
      assert_equal(data['meta'](), [{'type': 'BIGINT_TYPE'}])


  def test_fetch_result_rows(self):
    notebook = Mock()
    snippet = {'result': {'handle': {'guid': 'guid-1'}}}
    rows = 10
    start_over = True

    with patch('notebook.connectors.sql_alchemy.CONNECTIONS') as CONNECTIONS:
      CONNECTIONS.get = Mock(
        return_value={
          'result': Mock(
            fetchmany=Mock(return_value=[['row1'], ['row2']]) # We have 2 rows
          ),
          'meta': MagicMock(
            __getitem__=Mock(return_value={'type': 'BIGINT_TYPE'}),
            return_value=[{'type': 'BIGINT_TYPE'}]
          )
        }
      )

      data = SqlAlchemyApi(self.user, self.interpreter).fetch_result(notebook, snippet, rows, start_over)

      assert_false(data['has_more'])
      assert_not_equal(data['has_more'], [])
      assert_equal(data['has_more'], False)

      assert_equal(data['data'], [['row1'], ['row2']])
      assert_equal(data['meta'](), [{'type': 'BIGINT_TYPE'}])


  @raises(AuthenticationRequired)
  def test_create_engine_auth_error(self):
    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'mysql://${USER}:${PASSWORD}@hue:3306/hue'
      }
    }

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      SqlAlchemyApi(self.user, interpreter)._create_engine()


  def test_create_engine_auth(self):
    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'mysql://${USER}:${PASSWORD}@hue:3306/hue',
        'session': {
          'properties': [
            {
              'name': 'user',
              'value': 'test_user'
            },
            {
              'name': 'password',
              'value': 'test_pass'
            }
          ]
        }
      }
    }

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      SqlAlchemyApi(self.user, interpreter)._create_engine()


  @raises(AuthenticationRequired)
  def test_create_connection_error(self):
    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'mysql://${USER}:${PASSWORD}@hue:3306/hue'
      }
    }

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      engine = SqlAlchemyApi(self.user, interpreter)._create_engine()
      SqlAlchemyApi(self.user, interpreter)._create_connection(engine)

  def test_create_connection(self):
    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'mysql://${USER}:${PASSWORD}@hue:3306/hue',
        'session': {
          'properties': [
            {
              'name': 'user',
              'value': 'test_user'
            },
            {
              'name': 'password',
              'value': 'test_pass'
            }
          ]
        }
      }
    }

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      engine = SqlAlchemyApi(self.user, interpreter)._create_engine()
      SqlAlchemyApi(self.user, interpreter)._create_connection(engine)


  def test_create_engine_with_impersonation(self):
    interpreter = {
      'name': 'hive',
      'options': {
        'url': 'presto://hue:8080/hue',
        'session': {},
        'has_impersonation': False  # Off
      }
    }

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      engine = SqlAlchemyApi(self.user, interpreter)._create_engine()

      create_engine.assert_called_with('presto://hue:8080/hue', pool_pre_ping=True)


    interpreter['options']['has_impersonation'] = True  # On

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      engine = SqlAlchemyApi(self.user, interpreter)._create_engine()

      create_engine.assert_called_with('presto://test@hue:8080/hue', pool_pre_ping=True)


  def test_check_status(self):
    notebook = Mock()

    with patch('notebook.connectors.sql_alchemy.CONNECTIONS') as CONNECTIONS:

      snippet = {'result': {'handle': {'guid': 'guid-1', 'has_result_set': False}}}
      response = SqlAlchemyApi(self.user, self.interpreter).check_status(notebook, snippet)
      assert_equal(response['status'], 'success')

      snippet = {'result': {'handle': {'guid': 'guid-1', 'has_result_set': True}}}
      response = SqlAlchemyApi(self.user, self.interpreter).check_status(notebook, snippet)
      assert_equal(response['status'], 'available')


  def test_get_sample_data(self):
    snippet = Mock()

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      with patch('notebook.connectors.sql_alchemy.Assist.get_sample_data') as get_sample_data:
        with patch('notebook.connectors.sql_alchemy.inspect') as inspect:
          get_sample_data.return_value = (['col1'], [[1], [2]])

          response = SqlAlchemyApi(self.user, self.interpreter).get_sample_data(snippet)

          assert_equal(response['rows'], [[1], [2]])
          assert_equal(
            response['full_headers'],
            [{'name': 'col1', 'type': 'STRING_TYPE', 'comment': ''}]
          )


  def test_get_tables(self):
    snippet = MagicMock()

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      with patch('notebook.connectors.sql_alchemy.inspect') as inspect:
        with patch('notebook.connectors.sql_alchemy.Assist.get_table_names') as get_table_names:
          with patch('notebook.connectors.sql_alchemy.Assist.get_view_names') as get_view_names:
            get_table_names.return_value = ['table1']
            get_view_names.return_value = ['view1']

            response = SqlAlchemyApi(self.user, self.interpreter).autocomplete(snippet, database='database1')
            assert_equal(response['tables_meta'][0]['name'], 'table1')
            assert_equal(response['tables_meta'][1]['name'], 'view1')
            assert_equal(response['tables_meta'][0]['type'], 'Table')
            assert_equal(response['tables_meta'][1]['type'], 'View')


  def test_get_sample_data_table(self):
    snippet = Mock()

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      with patch('notebook.connectors.sql_alchemy.Assist.get_sample_data') as get_sample_data:
        with patch('notebook.connectors.sql_alchemy.inspect') as inspect:
          get_sample_data.return_value = (['col1'], [[1], [2]])

          response = SqlAlchemyApi(self.user, self.interpreter).get_sample_data(snippet, database='database1', table='table1')

          assert_equal(response['rows'], [[1], [2]])


  def test_dialect_trim_statement_semicolon(self):
    interpreter = {
      'name': 'presto',
      'options': {
        'url': 'presto://hue:8080/hue',
        'session': {},
      },
      'dialect_properties': {},
    }

    with patch('notebook.connectors.sql_alchemy.SqlAlchemyApi._create_connection') as _create_connection:
      with patch('notebook.connectors.sql_alchemy.SqlAlchemyApi._create_engine') as _create_engine:
        with patch('notebook.connectors.sql_alchemy.SqlAlchemyApi._get_session') as _get_session:
          execute = Mock(return_value=Mock(cursor=None))
          _create_connection.return_value = Mock(
            execute=execute
          )
          notebook = {}
          snippet = {'statement': 'SELECT 1;'}

          # Trim
          engine = SqlAlchemyApi(self.user, interpreter).execute(notebook, snippet)

          execute.assert_called_with('SELECT 1')

          # No Trim
          interpreter['options']['url'] = 'mysql://hue:3306/hue'
          interpreter['dialect_properties']['trim_statement_semicolon'] = False
          interpreter['dialect_properties']['sql_identifier_quote'] = '`'

          engine = SqlAlchemyApi(self.user, interpreter).execute(notebook, snippet)

          execute.assert_called_with('SELECT 1;')


class TestDialects(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))


  def test_backticks_with_connectors(self):
    interpreter = {'name': 'hive', 'options': {'url': 'dialect://'}, 'dialect_properties': {'sql_identifier_quote': '`'}}
    data = SqlAlchemyApi(self.user, interpreter).get_browse_query(snippet=Mock(), database='db1', table='table1')

    assert_equal(data, 'SELECT *\nFROM `db1`.`table1`\nLIMIT 1000\n')


    interpreter = {'options': {'url': 'dialect://'}, 'dialect_properties': {'sql_identifier_quote': '"'}}
    data = SqlAlchemyApi(self.user, interpreter).get_browse_query(snippet=Mock(), database='db1', table='table1')

    assert_equal(data, 'SELECT *\nFROM "db1"."table1"\nLIMIT 1000\n')


  def test_backticks_without_connectors(self):
    interpreter = {'name': 'hive', 'options': {'url': 'hive://'}}
    data = SqlAlchemyApi(self.user, interpreter).get_browse_query(snippet=Mock(), database='db1', table='table1')

    assert_equal(data, 'SELECT *\nFROM `db1`.`table1`\nLIMIT 1000\n')


    interpreter = {'name': 'postgresql', 'options': {'url': 'postgresql://'}}
    data = SqlAlchemyApi(self.user, interpreter).get_browse_query(snippet=Mock(), database='db1', table='table1')

    assert_equal(data, 'SELECT *\nFROM "db1"."table1"\nLIMIT 1000\n')


class TestAutocomplete(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))


  def test_empty_database_names(self):
    interpreter = {
      'name': 'hive',
      'options': {'url': 'phoenix://'}
    }

    snippet = MagicMock()
    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      with patch('notebook.connectors.sql_alchemy.inspect') as inspect:
        with patch('notebook.connectors.sql_alchemy.Assist') as Assist:
          Assist.return_value = Mock(get_databases=Mock(return_value=['SYSTEM', None]))

          data = SqlAlchemyApi(self.user, interpreter).autocomplete(snippet)

          assert_equal(data['databases'], ['SYSTEM', ''])

  def test_columns_with_null_type(self):
    interpreter = {
      'name': 'hive',
      'options': {'url': 'phoenix://'}
    }

    snippet = MagicMock()
    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      with patch('notebook.connectors.sql_alchemy.inspect') as inspect:
        with patch('notebook.connectors.sql_alchemy.Assist') as Assist:
          def col1_dict(key):
            return {
              'name': 'col1',
              'type': 'string'
            }.get(key, Mock())
          col1 = MagicMock()
          col1.__getitem__.side_effect = col1_dict
          col1.get = col1_dict
          def col2_dict(key):
            return {
              'name': 'col2',
              'type': NullType()
            }.get(key, Mock())
          col2 = MagicMock()
          col2.__getitem__.side_effect = col2_dict
          col2.get = col2_dict

          Assist.return_value = Mock(get_columns=Mock(return_value=[col1, col2]), get_keys=Mock(return_value={}))

          data = SqlAlchemyApi(self.user, interpreter).autocomplete(snippet, database='database', table='table')

          assert_equal(data['columns'], ['col1', 'col2'])
          assert_equal([col['type'] for col in data['extended_columns']], ['string', 'null'])

  def test_get_keys(self):

    with patch('notebook.connectors.sql_alchemy.Table') as Table:
      Table.return_value = Mock(
        foreign_keys=[
          Mock(
            parent=Mock(name='col1'),
            target_fullname='db2.table2.col2'
          )
        ],
        primary_key=Mock(columns=[Mock(name='col2')])
      )

      db, engine, backticks = Mock(), Mock(), Mock()
      database, table = Mock(), Mock()

      keys = Assist(db, engine, backticks).get_keys(database, table)

      assert_true(keys['primary_keys'])  # For some reason could not mock two level to get some colum names
      assert_equal(keys['foreign_keys'][0]['to'], 'db2.table2.col2')


class TestUtils():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)

    self.user = rewrite_user(User.objects.get(username="test"))
    self.interpreter = {
      'name': 'hive',
      'options': {
        'url': 'mysql://hue:localhost@hue:3306/hue'
      },
    }

  def test_get_column_type_name_complex(self):
    api = SqlAlchemyApi(self.user, self.interpreter)

    with patch('notebook.connectors.sql_alchemy.str') as str:
      str.side_effect = UnsupportedCompilationError(None, None)

      assert_equal(api._get_column_type_name({'type': VARCHAR}), 'varchar')  # Not complex but not testable otherwise
      assert_equal(api._get_column_type_name({'type': NullType}), 'null')
      assert_equal(api._get_column_type_name({'type': ARRAY}), 'array')
      assert_equal(api._get_column_type_name({'type': JSON}), 'json')


  def test_fix_bigquery_db_prefixes(self):
    interpreter = {
      'name': 'bigquery',
      'options': {
        'url': 'bigquery://'
      },
    }
    api = SqlAlchemyApi(self.user, interpreter)

    assert_equal(api._fix_bigquery_db_prefixes('table'), 'table')
    assert_equal(api._fix_bigquery_db_prefixes('db.table'), 'table')
