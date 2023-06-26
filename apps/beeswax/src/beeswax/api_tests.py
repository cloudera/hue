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

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_raises
from requests.exceptions import ReadTimeout

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from useradmin.models import User

from beeswax.api import _autocomplete, get_functions


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


LOG = logging.getLogger()


class TestApi():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")


  def test_autocomplete_time_out(self):
    get_tables_meta=Mock(
      side_effect=ReadTimeout("HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)")
    )
    db = Mock(
      get_tables_meta=get_tables_meta
    )

    resp = _autocomplete(db, database='database')

    assert_equal(
      resp,
      {
        'code': 500,
        'error': "HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)"
      }
    )


  def test_get_functions(self):
    db = Mock(
      get_functions=Mock(
        return_value=Mock(
          rows=Mock(
            return_value=[{'name': 'f1'}, {'name': 'f2'}]
          )
        )
      )
    )

    resp = get_functions(db)

    assert_equal(
      resp,
      [{'name': 'f1'}, {'name': 'f2'}]
    )


  def test_get_functions(self):
    with patch('beeswax.api._get_functions') as _get_functions:
      db = Mock()
      _get_functions.return_value = [
        {'name': 'f1'}, {'name': 'f2'}, {'name': 'f3'}
      ]

      resp = _autocomplete(db, database='default', operation='functions')

      assert_equal(
        resp['functions'],
        [{'name': 'f1'}, {'name': 'f2'}, {'name': 'f3'}]
      )


  def test_get_function(self):
    db = Mock()
    db.client = Mock(query_server = {'dialect': 'hive'})
    db.get_function = Mock(
      return_value = [
        ['floor_month(param) - Returns the timestamp at a month granularity'],
        ['param needs to be a timestamp value'],
        ['Example:'],
        ["> SELECT floor_month(CAST('yyyy-MM-dd HH:mm:ss' AS TIMESTAMP)) FROM src;"],
        ['yyyy-MM-01 00:00:00']
      ]
    )

    data = _autocomplete(db, database='floor_month', operation='function')

    assert_equal(
      data['function'],
      {
        'name': 'floor_month',
        'signature': 'floor_month(param)',
        'description':
            'Returns the timestamp at a month granularity\nparam needs to be a timestamp value\nExample:\n'
            '> SELECT floor_month(CAST(\'yyyy-MM-dd HH:mm:ss\' AS TIMESTAMP)) FROM src;\nyyyy-MM-01 00:00:00'
      }
    )


    db.client = Mock(query_server = {'dialect': 'impala'})
    data = _autocomplete(db, operation='function')

    assert_equal(data['function'], {})
