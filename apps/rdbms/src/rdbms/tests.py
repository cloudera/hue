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

import json
import os
import uuid

from django.urls import reverse
from nose.tools import assert_true, assert_equal

from desktop.lib.django_test_util import make_logged_in_client

from librdbms import conf as rdbms_conf
from librdbms.server import dbms


class MockRdbms:
  def get_databases(self):
    return ['db1', 'db2']

  def get_tables(self, database):
    return ['table1', 'table2']


class TestMockedRdbms:
  def setUp(self):
    self.client = make_logged_in_client()

    # Mock DB calls as we don't need the real ones
    self.prev_dbms = dbms.get
    dbms.get = lambda a, b: MockRdbms()

  def tearDown(self):
    # Remove monkey patching
    dbms.get = self.prev_dbms

  def test_basic_flow(self):
    response = self.client.get("/rdbms/")
    assert_true('DB Query' in response.content, response.content)

  def test_config_error(self):
    self.finish = rdbms_conf.DATABASES.set_for_testing({})

    response = self.client.get("/rdbms/")
    assert_true('There are currently no databases configured.' in response.content)

    response = self.client.get("/rdbms/execute/")
    assert_true('There are currently no databases configured.' in response.content)

    self.finish()


class TestSQLiteRdbmsBase(object):
  @classmethod
  def setup_class(cls):
    cls.database = '/tmp/%s.db' % uuid.uuid4()
    cls.prefillDatabase()

  @classmethod
  def teardown_class(cls):
    os.remove(cls.database)

  def setUp(self):
    self.client = make_logged_in_client()
    self.finish = rdbms_conf.DATABASES.set_for_testing({
      'sqlitee': {
        'name': self.database,
        'engine': 'sqlite'
      }
    })

  def tearDown(self):
    self.finish()

  @classmethod
  def prefillDatabase(cls):
    import sqlite3
    connection = sqlite3.connect(cls.database)
    connection.execute("CREATE TABLE test1 (date text, trans text, symbol text, qty real, price real)")
    connection.execute("INSERT INTO test1 VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
    connection.commit()
    connection.close()


class TestAPI(TestSQLiteRdbmsBase):
  def test_get_servers(self):
    response = self.client.get(reverse('rdbms:api_servers'))
    response_dict = json.loads(response.content)
    assert_true('sqlitee' in response_dict['servers'], response_dict)

  def test_get_databases(self):
    response = self.client.get(reverse('rdbms:api_databases', args=['sqlitee']))
    response_dict = json.loads(response.content)
    assert_true(self.database in response_dict['databases'], response_dict)

  def test_get_tables(self):
    response = self.client.get(reverse('rdbms:api_tables', args=['sqlitee', self.database]))
    response_dict = json.loads(response.content)
    assert_true('test1' in response_dict['tables'], response_dict)

  def test_get_columns(self):
    response = self.client.get(reverse('rdbms:api_columns', args=['sqlitee', self.database, 'test1']))
    response_dict = json.loads(response.content)
    assert_true('date' in response_dict['columns'], response_dict)
    assert_true('trans' in response_dict['columns'], response_dict)
    assert_true('symbol' in response_dict['columns'], response_dict)
    assert_true('qty' in response_dict['columns'], response_dict)
    assert_true('price' in response_dict['columns'], response_dict)

  def test_execute_query(self):
    data = {
      'server': 'sqlitee',
      'database': self.database,
      'query': 'SELECT * FROM test1'
    }
    response = self.client.post(reverse('rdbms:api_execute_query'), data, follow=True)
    response_dict = json.loads(response.content)
    assert_equal(1, len(response_dict['results']['rows']), response_dict)

  def test_explain_query(self):
    data = {
      'server': 'sqlitee',
      'database': self.database,
      'query': 'SELECT * FROM test1'
    }
    response = self.client.post(reverse('rdbms:api_explain_query'), data, follow=True)
    response_dict = json.loads(response.content)
    assert_true(len(response_dict['results']['rows']) > 0, response_dict)

  def test_options(self):
    finish = rdbms_conf.DATABASES['sqlitee'].OPTIONS.set_for_testing({'nonsensical': None})
    try:
      self.client.get(reverse('rdbms:api_tables', args=['sqlitee', self.database]))
    except TypeError, e:
      assert_true('nonsensical' in str(e), e)
    finish()
