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

import logging

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster

from metadata.optimizer_client import OptimizerApi, is_optimizer_enabled


LOG = logging.getLogger(__name__)


class TestOptimizerApi(object):

  @classmethod
  def setup_class(cls):
    if not is_live_cluster() or not is_optimizer_enabled():
      raise SkipTest

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    cls.user = rewrite_user(cls.user)
    add_to_group('test')
    grant_access("test", "test", "metadata")
    grant_access("test", "test", "optimizer")

    cls.api = OptimizerApi()


  @classmethod
  def teardown_class(cls):
    cls.user.is_superuser = False
    cls.user.save()


  def test_tenant(self):
    resp = self.api.get_tenant(email='romain@cloudera.com')

    assert_equal('success', resp['status'], resp)


  def test_create_tenant(self):
    resp = self.api.create_tenant(group='hue')

    assert_equal('success', resp['status'], resp)
    assert_true('tenant' in resp, resp)


  def test_authenticate(self):
    resp = self.api.authenticate()

    assert_true(resp['token'], resp)
    assert_equal('success', resp['status'], resp)


  def test_get_status(self):
    resp = self.api.authenticate()
    token = resp['token']

    resp = self.api.get_status(token=token)

    assert_equal('success', resp['status'], resp)
    assert_true('filesFinished' in resp['details'], resp)
    assert_true('filesProcessing' in resp['details'], resp)
    assert_true('finished' in resp['details'], resp)


  def test_delete_workload(self):
    resp = self.api.authenticate()
    token = resp['token']

    resp = self.api.delete_workload(token=token)

    assert_equal('success', resp['status'], resp)


  def test_upload(self):
    queries = [
        "select emps.id from emps where emps.name = 'Joe' group by emps.mgr, emps.id;",
        "select emps.name from emps where emps.num = 007 group by emps.state, emps.name;",
        "select Part.partkey, Part.name, Part.type from db1.Part where Part.yyprice > 2095",
        "select Part.partkey, Part.name, Part.mfgr FROM Part WHERE Part.name LIKE '%red';",
        "select count(*) as loans from account a where a.account_state_id in (5,9);",
        "select orders.key, orders.id from orders where orders.price < 9999",
        "select mgr.name from mgr where mgr.reports > 10 group by mgr.state;"
    ]

    resp = self.api.upload(queries=queries)

    assert_equal('status' in resp, resp)
    assert_equal('state' in resp['status'], resp)
    assert_equal('workloadId' in resp['status'], resp)

    assert_true(resp['status']['state'] in ('WAITING', 'FINISHED', 'FAILED'), resp['status']['state'])

    resp = self.api.upload_status(workfload_id=resp['status']['workloadId'])
    assert_equal('status' in resp, resp)
    assert_equal('state' in resp['status'], resp)
    assert_equal('workloadId' in resp['status'], resp)


  def test_top_tables(self):
    database_name = 'default'
    resp = self.api.top_tables(database_name=database_name)

    assert_true(isinstance(resp['results'], list), resp)

    assert_true('eid' in resp['results'][0], resp)
    assert_true('name' in resp['results'][0], resp)


  def test_table_details(self):  # Requires test_upload to run before
    resp = self.api.table_details(database_name='default', table_name='emps')

    assert_equal('success', resp['status'], resp)
    assert_true('columnCount' in resp, resp)
    assert_true('createCount' in resp, resp)
    assert_true('table_ddl' in resp, resp)
    assert_true('deleteCount' in resp, resp)
    assert_true('iview_ddl' in resp, resp)
    assert_true('updateCount' in resp, resp)
    assert_true('colStats' in resp, resp)
    assert_true('joinCount' in resp, resp)
    assert_true('view_ddl' in resp, resp)
    assert_true('tableStats' in resp, resp)
    assert_true('queryCount' in resp, resp)
    assert_true('selectCount' in resp, resp)
    assert_true('insertCount' in resp, resp)
    assert_true('tid' in resp, resp)
    assert_true('type' in resp, resp)
    assert_true('name' in resp, resp)

    resp = self.api.table_details(database_name='db1', table_name='Part')

    assert_equal('success', resp['status'], resp)
    assert_true('tid' in resp, resp)
    assert_true('columnCount' in resp, resp)


  def test_query_risk(self):
    query = 'Select * from (Select item.id from item)'

    resp = self.api.query_risk(query=query)

    assert_equal('success', resp['status'], resp)

    assert_true('impalaRisk' in resp, resp)
    assert_true('riskAnalysis' in resp['impalaRisk'], resp)
    assert_true('risk' in resp['impalaRisk'], resp)
    assert_true('riskRecommendation' in resp['impalaRisk'], resp)

    assert_true('hiveRisk' in resp, resp)
    assert_true('riskAnalysis' in resp['hiveRisk'], resp)
    assert_true('risk' in resp['hiveRisk'], resp)
    assert_true('riskRecommendation' in resp['hiveRisk'], resp)


  def test_query_compatibility(self):
    source_platform = 'hive'
    target_platform = 'impala'
    query = 'Select * from (Select item.id from item)'

    resp = self.api.query_compatibility(source_platform=source_platform, target_platform=target_platform, query=query)

    assert_equal('success', resp['status'], resp)

    assert_true('clauseName' in resp, resp)
    assert_true('clauseError' in resp, resp)
    assert_true('queryError' in resp, resp)
    assert_true('clauseString' in resp, resp)


  def test_top_filters(self):  # Requires test_upload to run before
    resp = self.api.top_filters(db_tables='db1.Part')

    assert_equal('success', resp['status'], resp)
    assert_true('qids' in resp, resp)
    assert_true('popularValues' in resp, resp)


  def test_top_joins(self):
    resp = self.api.top_joins(db_tables='db1.Part')

    assert_equal('success', resp['status'], resp)
    assert_true('tables' in resp['results'][0], resp)
    assert_true('queryIds' in resp['results'][0], resp)
    assert_true('totalTableCount' in resp['results'][0], resp)
    assert_true('totalQueryCount' in resp['results'][0], resp)
    assert_true('type' in resp['results'][0], resp)
    assert_true('columns' in resp['results'][0], resp)


  def test_top_aggs(self):
    resp = self.api.top_aggs(db_tables='db1.Part')

    assert_equal('success', resp['status'], resp)
    assert_true('tables' in resp['results'][0], resp)
    assert_true('queryIds' in resp['results'][0], resp)
    assert_true('totalTableCount' in resp['results'][0], resp)
    assert_true('totalQueryCount' in resp['results'][0], resp)
    assert_true('type' in resp['results'][0], resp)
    assert_true('columns' in resp['results'][0], resp)


  def test_top_columns(self):
    resp = self.api.top_columns(db_tables='db1.Part')

    assert_equal('success', resp['status'], resp)
    assert_true('tables' in resp['results'][0], resp)


  def test_top_databases(self):
    resp = self.api.top_databases()

    assert_equal('success', resp['status'], resp)
    assert_true('instanceCount' in resp['results'], resp)
    assert_true('totalTableCount' in resp['results'], resp)


  def test_similar_queries(self):
    source_platform = 'hive'
    query = 'Select * from (Select item.id from item)'

    resp = self.api.similar_queries(source_platform=source_platform, query=query)

    assert_equal('successs', resp['status'], resp)

    assert_true('querySignature' in resp, resp)
    assert_true('query' in resp, resp)
