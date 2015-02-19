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

import os
import re
import sys

from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_equal, assert_false

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group
from desktop.models import Document

from beeswax.design import hql_query
from beeswax.models import SavedQuery, QueryHistory
from beeswax.server import dbms
from beeswax.test_base import get_query_server_config, wait_for_query_to_finish, fetch_query_result_data
from beeswax.tests import _make_query

from impala.conf import SERVER_HOST


class MockDbms:
  def get_databases(self):
    return ['db1', 'db2']

  def get_tables(self, database):
    return ['table1', 'table2']


class TestMockedImpala:
  def setUp(self):
    self.client = make_logged_in_client()

    # Mock DB calls as we don't need the real ones
    self.prev_dbms = dbms.get
    dbms.get = lambda a, b: MockDbms()

  def tearDown(self):
    # Remove monkey patching
    dbms.get = self.prev_dbms

  def test_basic_flow(self):
    response = self.client.get("/impala/")
    assert_true(re.search('Impala Editor', response.content), response.content)
    assert_true('Query Editor' in response.content)

    response = self.client.get("/impala/execute/")
    assert_true('Query Editor' in response.content)

  def test_saved_queries(self):
    user = User.objects.get(username='test')

    response = self.client.get("/impala/list_designs")
    assert_equal(len(response.context['page'].object_list), 0)

    try:
      beewax_query = create_saved_query('beeswax', user)
      response = self.client.get("/impala/list_designs")
      assert_equal(len(response.context['page'].object_list), 0)

      impala_query = create_saved_query('impala', user)
      response = self.client.get("/impala/list_designs")
      assert_equal(len(response.context['page'].object_list), 1)

      # Test my query page
      QueryHistory.objects.create(owner=user, design=impala_query, query='', last_state=QueryHistory.STATE.available.index)

      resp = self.client.get('/impala/my_queries')
      assert_equal(len(resp.context['q_page'].object_list), 1)
      assert_equal(resp.context['h_page'].object_list[0].design.name, 'create_saved_query')
    finally:
      if beewax_query is not None:
        beewax_query.delete()
      if impala_query is not None:
        impala_query.delete()


class TestImpalaIntegration:
  DATABASE = 'test_hue_impala'

  def setUp(self):
    self.finish = []

    # We need a real Impala cluster currently
    if not 'impala' in sys.argv and not os.environ.get('TEST_IMPALAD_HOST'):
      raise SkipTest

    if os.environ.get('TEST_IMPALAD_HOST'):
      self.finish.append(SERVER_HOST.set_for_testing(os.environ.get('TEST_IMPALAD_HOST')))

    self.client = make_logged_in_client()
    self.user = User.objects.get(username='test')
    add_to_group('test')
    self.db = dbms.get(self.user, get_query_server_config(name='impala'))

    hql = """
      USE default;
      DROP TABLE IF EXISTS %(db)s.tweets;
      DROP DATABASE IF EXISTS %(db)s;
      CREATE DATABASE %(db)s;

      USE %(db)s;
    """ % {'db': self.DATABASE}

    resp = _make_query(self.client, hql, database='default', local=False, server_name='impala')
    resp = wait_for_query_to_finish(self.client, resp, max=30.0)

    hql = """
      CREATE TABLE tweets (row_num INTEGER, id_str STRING, text STRING) STORED AS PARQUET;

      INSERT INTO TABLE tweets VALUES (1, "531091827395682000", "My dad looks younger than costa");
      INSERT INTO TABLE tweets VALUES (2, "531091827781550000", "There is a thin line between your partner being vengeful and you reaping the consequences of your bad actions towards your partner.");
      INSERT INTO TABLE tweets VALUES (3, "531091827768979000", "@Mustang_Sally83 and they need to get into you :))))");
      INSERT INTO TABLE tweets VALUES (4, "531091827114668000", "@RachelZJohnson thank you rach!xxx");
      INSERT INTO TABLE tweets VALUES (5, "531091827949309000", "i think @WWERollins was robbed of the IC title match this week on RAW also i wonder if he will get a rematch i hope so @WWE");
    """

    resp = _make_query(self.client, hql, database=self.DATABASE, local=False, server_name='impala')
    resp = wait_for_query_to_finish(self.client, resp, max=30.0)

    def tearDown(self):
      for f in self.finish:
        f()

  def test_basic_flow(self):
    dbs = self.db.get_databases()
    assert_true('_impala_builtins' in dbs, dbs)
    assert_true(self.DATABASE in dbs, dbs)

    tables = self.db.get_tables(database=self.DATABASE)
    assert_true('tweets' in tables, tables)

    QUERY = """
      SELECT * FROM tweets ORDER BY row_num;
    """
    response = _make_query(self.client, QUERY, database=self.DATABASE, local=False, server_name='impala')

    response = wait_for_query_to_finish(self.client, response, max=180.0)

    results = []

    # Check that we multiple fetches get all the result set
    while len(results) < 5:
      content = fetch_query_result_data(self.client, response, n=len(results)) # We get less than 5 results most of the time, so increase offset
      results += content['results']

    assert_equal([1, 2, 3, 4, 5], [col[0] for col in results])

    # Check start over
    results_start_over = []

    while len(results_start_over) < 5:
      content = fetch_query_result_data(self.client, response, n=len(results_start_over))
      results_start_over += content['results']

    assert_equal(results_start_over, results)


# Could be refactored with SavedQuery.create_empty()
def create_saved_query(app_name, owner):
    query_type = SavedQuery.TYPES_MAPPING[app_name]
    design = SavedQuery(owner=owner, type=query_type)
    design.name = 'create_saved_query'
    design.desc = ''
    design.data = hql_query('show $tables', database='db1').dumps()
    design.is_auto = False
    design.save()

    Document.objects.link(design, owner=design.owner, extra=design.type, name=design.name, description=design.desc)

    return design
