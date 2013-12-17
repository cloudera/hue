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

import re

from nose.tools import assert_true, assert_equal, assert_false
from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from beeswax.models import SavedQuery, QueryHistory
from beeswax.server import dbms
from beeswax.design import hql_query
from desktop.models import Document


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
      assert_equal(len(resp.context['h_page'].object_list), 1)
    finally:
      if beewax_query is not None:
        beewax_query.delete()
      if impala_query is not None:
        impala_query.delete()


# Could be refactored with SavedQuery.create_empty()
def create_saved_query(app_name, owner):
    query_type = SavedQuery.TYPES_MAPPING[app_name]
    design = SavedQuery(owner=owner, type=query_type)
    design.name = SavedQuery.DEFAULT_NEW_DESIGN_NAME
    design.desc = ''
    design.data = hql_query('show $tables', database='db1').dumps()
    design.is_auto = False
    design.save()

    Document.objects.link(design, owner=design.owner, extra=design.type, name=design.name, description=design.desc)

    return design
