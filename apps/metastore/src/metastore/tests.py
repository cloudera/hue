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

import logging
import json

from nose.tools import assert_true, assert_equal, assert_false

from django.utils.encoding import smart_str
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

import hadoop
from desktop.lib.django_test_util import make_logged_in_client, assert_equal_mod_whitespace
from desktop.lib.test_utils import add_permission, grant_access
from useradmin.models import HuePermission, GroupPermission, group_has_permission

from beeswax.conf import BROWSE_PARTITIONED_TABLE_LIMIT
from beeswax.views import collapse_whitespace
from beeswax.test_base import make_query, wait_for_query_to_finish, verify_history, get_query_server_config, fetch_query_result_data
from beeswax.models import QueryHistory
from beeswax.server import dbms
from beeswax.test_base import BeeswaxSampleProvider


LOG = logging.getLogger(__name__)


def _make_query(client, query, submission_type="Execute",
                udfs=None, settings=None, resources=[],
                wait=False, name=None, desc=None, local=True,
                is_parameterized=True, max=30.0, database='default', email_notify=False, **kwargs):
  """Wrapper around the real make_query"""
  res = make_query(client, query, submission_type,
                   udfs, settings, resources,
                   wait, name, desc, local, is_parameterized, max, database, email_notify, **kwargs)

  # Should be in the history if it's submitted.
  if submission_type == 'Execute':
    fragment = collapse_whitespace(smart_str(query[:20]))
    verify_history(client, fragment=fragment)

  return res

class TestMetastoreWithHadoop(BeeswaxSampleProvider):
  requires_hadoop = True

  def setUp(self):
    user = User.objects.get(username='test')
    self.db = dbms.get(user, get_query_server_config())

  def test_basic_flow(self):
    # Default database should exist
    response = self.client.get("/metastore/databases")
    assert_true("default" in response.context["databases"])

    # Table should have been created
    response = self.client.get("/metastore/tables/")
    assert_true("test" in response.context["tables"])

    # Switch databases
    response = self.client.get("/metastore/tables/default")
    assert_true("test" in response.context["tables"])

    # Should default to "default" database
    response = self.client.get("/metastore/tables/not_there")
    assert_true("test" in response.context["tables"])

    # And have detail
    response = self.client.get("/metastore/table/default/test")
    assert_true("foo" in response.content)
    assert_true("serdeInfo:SerDeInfo" in response.content, response.content)

    # Remember the number of history items. Use a generic fragment 'test' to pass verification.
    history_cnt = verify_history(self.client, fragment='test')

    # Show table data.
    response = self.client.get("/metastore/table/default/test/read", follow=True)
    response = self.client.get(reverse("beeswax:api_watch_query_refresh_json", kwargs={'id': response.context['query'].id}), follow=True)
    response = wait_for_query_to_finish(self.client, response, max=30.0)
    # Note that it may not return all rows at once. But we expect at least 10.
    results = fetch_query_result_data(self.client, response)
    assert_true(len(results['results']) > 0)
    # This should NOT go into the query history.
    assert_equal(verify_history(self.client, fragment='test'), history_cnt, 'Implicit queries should not be saved in the history')

  def test_describe_view(self):
    resp = self.client.get('/metastore/table/default/myview')
    assert_equal(None, resp.context['sample'])
    assert_true(resp.context['table'].is_view)
    assert_true("View" in resp.content)
    assert_true("Drop View" in resp.content)
    # Breadcrumbs
    assert_true("default" in resp.content)
    assert_true("myview" in resp.content)

  def test_describe_partitions(self):
    response = self.client.get("/metastore/table/default/test_partitions")
    assert_true("Show Partitions (1)" in response.content, response.content)

    response = self.client.get("/metastore/table/default/test_partitions/partitions", follow=True)
    assert_true("baz_one" in response.content)
    assert_true("boom_two" in response.content)
    # Breadcrumbs
    assert_true("default" in response.content)
    assert_true("test_partitions" in response.content)
    assert_true("partitions" in response.content)

    # Not partitioned
    response = self.client.get("/metastore/table/default/test/partitions", follow=True)
    assert_true("is not partitioned." in response.content)

  def test_browse_partitioned_table_with_limit(self):
    # Limit to 90
    finish = BROWSE_PARTITIONED_TABLE_LIMIT.set_for_testing("90")
    try:
      response = self.client.get("/metastore/table/default/test_partitions")
      assert_true("0x%x" % 89 in response.content, response.content)
      assert_false("0x%x" % 90 in response.content, response.content)
    finally:
      finish()

  def test_browse_partitions(self):
    response = self.client.get("/metastore/table/default/test_partitions/partitions/0", follow=True)
    response = self.client.get(reverse("beeswax:api_watch_query_refresh_json", kwargs={'id': response.context['query'].id}), follow=True)
    response = wait_for_query_to_finish(self.client, response, max=30.0)
    results = fetch_query_result_data(self.client, response)
    assert_true(len(results['results']) > 0, results)

  def test_drop_multi_tables(self):
    hql = """
      CREATE TABLE test_drop_1 (a int);
      CREATE TABLE test_drop_2 (a int);
      CREATE TABLE test_drop_3 (a int);
    """
    resp = _make_query(self.client, hql)
    resp = wait_for_query_to_finish(self.client, resp, max=30.0)

    # Drop them
    resp = self.client.get('/metastore/tables/drop/default', follow=True)
    assert_true('want to delete' in resp.content, resp.content)
    resp = self.client.post('/metastore/tables/drop/default', {u'table_selection': [u'test_drop_1', u'test_drop_2', u'test_drop_3']})
    assert_equal(resp.status_code, 302)


  def test_drop_multi_databases(self):
    hql = """
      CREATE DATABASE test_drop_1;
      CREATE DATABASE test_drop_2;
      CREATE DATABASE test_drop_3;
    """
    resp = _make_query(self.client, hql)
    resp = wait_for_query_to_finish(self.client, resp, max=30.0)

    # Drop them
    resp = self.client.get('/metastore/databases/drop', follow=True)
    assert_true('want to delete' in resp.content, resp.content)
    resp = self.client.post('/metastore/databases/drop', {u'database_selection': [u'test_drop_1', u'test_drop_2', u'test_drop_3']})
    assert_equal(resp.status_code, 302)


  def test_load_data(self):
    """
    Test load data queries.
    These require Hadoop, because they ask the metastore
    about whether a table is partitioned.
    """
    # Check that view works
    resp = self.client.get("/metastore/table/default/test/load", follow=True)
    assert_true('Path' in resp.content)

    # Try the submission
    self.client.post("/metastore/table/default/test/load", dict(path="/tmp/foo", overwrite=True), follow=True)
    query = QueryHistory.objects.latest('id')

    assert_equal_mod_whitespace("LOAD DATA INPATH '/tmp/foo' OVERWRITE INTO TABLE `default.test`", query.query)

    resp = self.client.post("/metastore/table/default/test/load", dict(path="/tmp/foo", overwrite=False), follow=True)
    query = QueryHistory.objects.latest('id')
    assert_equal_mod_whitespace("LOAD DATA INPATH '/tmp/foo' INTO TABLE `default.test`", query.query)

    # Try it with partitions
    resp = self.client.post("/metastore/table/default/test_partitions/load", dict(path="/tmp/foo", partition_0="alpha", partition_1="beta"), follow=True)
    query = QueryHistory.objects.latest('id')
    assert_equal_mod_whitespace(query.query, "LOAD DATA INPATH '/tmp/foo' INTO TABLE `default.test_partitions` PARTITION (baz='alpha', boom='beta')")


  def test_has_write_access_frontend(self):
    client = make_logged_in_client(username='write_access_frontend', groupname='write_access_frontend', is_superuser=False)
    grant_access("write_access_frontend", "write_access_frontend", "metastore")
    user = User.objects.get(username='write_access_frontend')

    def check(client, assertz):
      response = client.get("/metastore/databases")
      assertz("Drop</button>" in response.content, response.content)
      assertz("Create a new database" in response.content, response.content)

      response = client.get("/metastore/tables/")
      assertz("Drop</button>" in response.content, response.content)
      assertz("Create a new table" in response.content, response.content)

    check(client, assert_false)

    # Add access
    group, created = Group.objects.get_or_create(name='write_access_frontend')
    perm, created = HuePermission.objects.get_or_create(app='metastore', action='write')
    GroupPermission.objects.get_or_create(group=group, hue_permission=perm)

    check(client, assert_true)


  def test_has_write_access_backend(self):
    client = make_logged_in_client(username='write_access_backend', groupname='write_access_backend', is_superuser=False)
    grant_access("write_access_backend", "write_access_backend", "metastore")
    grant_access("write_access_backend", "write_access_backend", "beeswax")
    user = User.objects.get(username='write_access_backend')

    resp = _make_query(client, 'CREATE TABLE test_perm_1 (a int);') # Only fails if we were using Sentry and won't allow SELECT to user
    resp = wait_for_query_to_finish(client, resp, max=30.0)

    def check(client, http_codes):
      resp = client.get('/metastore/tables/drop/default')
      assert_true(resp.status_code in http_codes, resp.content)

      resp = client.post('/metastore/tables/drop/default', {u'table_selection': [u'test_perm_1']})
      assert_true(resp.status_code in http_codes, resp.content)

    check(client, [301]) # Denied

    # Add access
    group, created = Group.objects.get_or_create(name='write_access_backend')
    perm, created = HuePermission.objects.get_or_create(app='metastore', action='write')
    GroupPermission.objects.get_or_create(group=group, hue_permission=perm)

    check(client, [200, 302]) # Ok
