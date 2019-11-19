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

from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from useradmin.models import User

from notebook.connectors.sql_alchemy import SqlAlchemyApi

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock

LOG = logging.getLogger(__name__)


class TestApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)

    self.user = rewrite_user(User.objects.get(username="test"))
    grant_access("test", "default", "notebook")


  def test_column_backticks_escaping(self):
    interpreter = {
      'options': {
        'url': 'mysql://'
      }
    }
    assert_equal(SqlAlchemyApi(self.user, interpreter).backticks, '`')

    interpreter = {
      'options': {
        'url': 'postgresql://'
      }
    }
    assert_equal(SqlAlchemyApi(self.user, interpreter).backticks, '"')


  def test_create_athena_engine(self):
    interpreter = {
      'options': {
        'url': 'awsathena+rest://XXXXXXXXXXXXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX@athena.us-west-2.amazonaws.com:443/default?s3_staging_dir=s3://gethue-athena/scratch'
      }
    }

    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      SqlAlchemyApi(self.user, interpreter)._create_engine()


  def test_fetch_result_empty(self):
    interpreter = {
      'options': {
        'url': 'mysql://hue:localhost@hue:3306/hue'
      },
    }

    notebook = Mock()
    snippet = {'result': {'handle': {'guid': 'guid-1'}}}
    rows = 10
    start_over = True

    with patch('notebook.connectors.sql_alchemy.CONNECTION_CACHE') as CONNECTION_CACHE:
      CONNECTION_CACHE.get = Mock(
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

      data = SqlAlchemyApi(self.user, interpreter).fetch_result(notebook, snippet, rows, start_over)

      assert_false(data['has_more'])
      assert_not_equal(data['has_more'], [])
      assert_equal(data['has_more'], False)

      assert_equal(data['data'], [])
      assert_equal(data['meta'](), [{'type': 'BIGINT_TYPE'}])


  def test_fetch_result_rows(self):
    interpreter = {
      'options': {
        'url': 'mysql://hue:localhost@hue:3306/hue'
      }
    }

    notebook = Mock()
    snippet = {'result': {'handle': {'guid': 'guid-1'}}}
    rows = 10
    start_over = True

    with patch('notebook.connectors.sql_alchemy.CONNECTION_CACHE') as CONNECTION_CACHE:
      CONNECTION_CACHE.get = Mock(
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

      data = SqlAlchemyApi(self.user, interpreter).fetch_result(notebook, snippet, rows, start_over)

      assert_false(data['has_more'])
      assert_not_equal(data['has_more'], [])
      assert_equal(data['has_more'], False)

      assert_equal(data['data'], [['row1'], ['row2']])
      assert_equal(data['meta'](), [{'type': 'BIGINT_TYPE'}])


class TestAutocomplete(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)

    self.user = rewrite_user(User.objects.get(username="test"))
    grant_access("test", "default", "notebook")


  def test_empty_database_names(self):
    interpreter = {
      'options': {'url': 'phoenix://'}
    }

    snippet = Mock()
    with patch('notebook.connectors.sql_alchemy.create_engine') as create_engine:
      with patch('notebook.connectors.sql_alchemy.inspect') as inspect:
        with patch('notebook.connectors.sql_alchemy.Assist') as Assist:
          Assist.return_value=Mock(get_databases=Mock(return_value=['SYSTEM', None]))

          data = SqlAlchemyApi(self.user, interpreter).autocomplete(snippet)

          assert_equal(data['databases'], ['SYSTEM', 'NULL'])
