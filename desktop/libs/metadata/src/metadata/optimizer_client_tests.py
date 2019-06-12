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
import time

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access

from metadata.optimizer_client import OptimizerApi
from metadata.conf import OPTIMIZER, has_optimizer
from desktop.models import uuid_default


LOG = logging.getLogger(__name__)


class BaseTestOptimizerApi(object):
  integration = True
  UPLOADED = False
  DATABASE = 'db1'

  @classmethod
  def setup_class(cls):
    if not has_optimizer():
      raise SkipTest

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    cls.user = rewrite_user(cls.user)
    add_to_group('test')
    grant_access("test", "test", "metadata")
    grant_access("test", "test", "optimizer")

    cls.api = OptimizerApi(user=cls.user)

    if not BaseTestOptimizerApi.UPLOADED:
      cls.upload()
      BaseTestOptimizerApi.UPLOADED = True


  # Should run first
  @classmethod
  def upload(cls):
    queries = [
        (uuid_default(), 0, "select emps.id from emps where emps.name = 'Joe' group by emps.mgr, emps.id;", BaseTestOptimizerApi.DATABASE),
        (uuid_default(), 0, "select emps.name from emps where emps.num = 007 group by emps.state, emps.name;", BaseTestOptimizerApi.DATABASE),
        (uuid_default(), 0, "select Part.partkey, max(Part.salary), Part.name, Part.type from %s.Part where Part.yyprice > 2095" % BaseTestOptimizerApi.DATABASE, BaseTestOptimizerApi.DATABASE),
        (uuid_default(), 0, "select Part.partkey, Part.name, Part.mfgr FROM Part WHERE Part.name LIKE '%red';", BaseTestOptimizerApi.DATABASE),
        (uuid_default(), 0, "select count(*) as loans from account a where a.account_state_id in (5,9);", BaseTestOptimizerApi.DATABASE),
        (uuid_default(), 0, "select orders.key, orders.id from orders where orders.price < 9999", BaseTestOptimizerApi.DATABASE),

        (uuid_default(), 0, "select x from x join y where x.a = y.a;", BaseTestOptimizerApi.DATABASE),

        # DDL
        (uuid_default(), 0, ' '.join('''CREATE TABLE `web_logs`(
  `_version_` bigint,
  `app` string COMMENT 'app',
  `bytes` smallint COMMENT 'http://demo.gethue.com/ is',
  `city` string COMMENT 'city',
  `client_ip` string,
  `code` tinyint,
  `country_code` string,
  `country_code3` string,
  `country_name` string,
  `device_family` string,
  `extension` string,
  `latitude` float,
  `longitude` float,
  `method` string,
  `os_family` string,
  `os_major` string,
  `protocol` string,
  `record` string,
  `referer` string,
  `region_code` bigint,
  `request` string,
  `subapp` string,
  `time` string,
  `url` string,
  `user_agent` string,
  `user_agent_family` string,
  `user_agent_major` string,
  `id` string)
COMMENT 'http://demo.gethue.com/ rocks!'
PARTITIONED BY (
  `date` string)
'''.splitlines()), BaseTestOptimizerApi.DATABASE)
    ]

    resp = cls.api.upload(data=queries, data_type='queries', source_platform='hive')

    assert_true('status' in resp, resp)
    assert_true('count' in resp, resp)

    assert_true('state' in resp['status'], resp)
    assert_true('workloadId' in resp['status'], resp)
    assert_true('failedQueries' in resp['status'], resp)
    assert_true('successQueries' in resp['status'], resp)
    assert_true(resp['status']['state'] in ('WAITING', 'FINISHED', 'FAILED'), resp['status']['state'])

    resp = cls.api.upload_status(workload_id=resp['status']['workloadId'])
    assert_true('status' in resp, resp)
    assert_true('state' in resp['status'], resp)
    assert_true('workloadId' in resp['status'], resp)


    i = 0
    while i < 60 and resp['status']['state'] not in ('FINISHED', 'FAILED'):
      resp = cls.api.upload_status(workload_id=resp['status']['workloadId'])
      i += 1
      time.sleep(1)
      LOG.info('Upload state: %(state)s' % resp['status'])

    assert_true(i < 60 and resp['status']['state'] == 'FINISHED', resp)
    assert_equal(resp['status']['successQueries'], 8, resp)


  @classmethod
  def teardown_class(cls):
    cls.user.is_superuser = False
    cls.user.save()


class TestOptimizerApi(BaseTestOptimizerApi):

  def test_tenant(self):
    resp = self.api.get_tenant(cluster_id=OPTIMIZER.CLUSTER_ID.get())

    assert_true('tenant' in resp, resp)


  def test_top_tables(self):
    database_name = 'default'
    resp = self.api.top_tables(database_name=database_name)

    assert_true(isinstance(resp['results'], list), resp)

    assert_true('eid' in resp['results'][0], resp)
    assert_true('name' in resp['results'][0], resp)

    database_name = BaseTestOptimizerApi.DATABASE
    resp = self.api.top_tables(database_name=database_name)

    assert_true(isinstance(resp['results'], list), resp)


  def test_table_details(self):  # Requires test_upload to run before
    resp = self.api.table_details(database_name='default', table_name='emps')

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

    resp = self.api.table_details(database_name=BaseTestOptimizerApi.DATABASE, table_name='Part')

    assert_true('tid' in resp, resp)
    assert_true('columnCount' in resp, resp)


  def test_query_risk(self):
    query = 'Select * from items'

    resp = self.api.query_risk(query=query, source_platform='hive', db_name=BaseTestOptimizerApi.DATABASE)

    assert_true(len(resp) > 0, resp)
    assert_true('riskAnalysis' in resp['hints'][0], resp)
    assert_true('risk' in resp['hints'][0], resp)
    assert_true('riskRecommendation' in resp['hints'][0], resp)


  def test_query_compatibility(self):
    source_platform = 'hive'
    target_platform = 'impala'
    query = 'Select * from (Select item.id from item)'

    resp = self.api.query_compatibility(source_platform=source_platform, target_platform=target_platform, query=query)

    assert_true('clauseName' in resp, resp)
    assert_true('clauseError' in resp, resp)
    assert_true('queryError' in resp, resp)
    assert_true('clauseString' in resp, resp)


  def test_top_filters(self):
    resp = self.api.top_filters(db_tables=['%s.Part' % BaseTestOptimizerApi.DATABASE])

    assert_true(len(resp['results']) > 0, resp)


  def test_top_joins(self):
    resp = self.api.top_joins(db_tables=['%s.x' % BaseTestOptimizerApi.DATABASE])

    assert_true(len(resp['results']) > 0, resp)

    assert_true(resp['results'][0]['tables'], [u'%s.x', u'%s.y' % (BaseTestOptimizerApi.DATABASE, BaseTestOptimizerApi.DATABASE)])
    assert_true('queryIds' in resp['results'][0], resp)
    assert_true('totalTableCount' in resp['results'][0], resp)
    assert_true('totalQueryCount' in resp['results'][0], resp)
    assert_true('joinType' in resp['results'][0], resp)
    assert_equal(resp['results'][0]['joinCols'], [{u'columns': [u'%s.x.a' % BaseTestOptimizerApi.DATABASE, u'%s.y.a' % BaseTestOptimizerApi.DATABASE]}])


  def test_top_aggs(self):
    resp = self.api.top_aggs(db_tables=['%s.Part' % BaseTestOptimizerApi.DATABASE])

    assert_true(len(resp['results']) > 0, resp)

    assert_true('tables' in resp['results'][0], resp)
    assert_true('queryIds' in resp['results'][0], resp)
    assert_true('totalTableCount' in resp['results'][0], resp)
    assert_true('totalQueryCount' in resp['results'][0], resp)
    assert_true('type' in resp['results'][0], resp)
    assert_true('columns' in resp['results'][0], resp)


  def test_top_columns(self):
    resp = self.api.top_columns(db_tables=['%s.Part' % BaseTestOptimizerApi.DATABASE])

    assert_true('orderbyColumns' in resp, resp)
    assert_true('selectColumns' in resp, resp)
    assert_true('filterColumns' in resp, resp)
    assert_true('joinColumns' in resp, resp)
    assert_true('groupbyColumns' in resp, resp)

    assert_true(resp['orderbyColumns'], resp)
    assert_true('selectColumns' in resp, resp)
    assert_true('filterColumns' in resp, resp)
    assert_true('joinColumns' in resp, resp)
    assert_true('groupbyColumns' in resp, resp)


  def test_top_databases(self):
    resp = self.api.top_databases()

    assert_true(len(resp['results']) > 0, resp)

    assert_true('instanceCount' in resp['results'][0], resp)
    assert_true('totalTableCount' in resp['results'][0], resp)


  def test_similar_queries(self):
    raise SkipTest # Experimental only

    source_platform = 'hive'
    query = 'Select * from (Select item.id from item)'

    resp = self.api.similar_queries(source_platform=source_platform, query=query)

    assert_true('querySignature' in resp, resp)
    assert_true('query' in resp, resp)



class TestOptimizerRiskApi(BaseTestOptimizerApi):

  def test_risk_10_views(self):
    source_platform = 'hive'
    query = '''SELECT code
FROM
  (SELECT code
   FROM
     (SELECT code
      FROM
        (SELECT code
         FROM
           (SELECT code
            FROM
              (SELECT code
               FROM
                 (SELECT code
                  FROM
                    (SELECT code
                     FROM
                       (SELECT code
                        FROM
                          (SELECT code
                           FROM
                             (SELECT code
                              FROM
                                (SELECT code
                                 FROM
                                   (SELECT code
                                    FROM sample_01) t1) t2) t3) t4) t5) t6) t7) t8) t9) t10) t11) t12
'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=BaseTestOptimizerApi.DATABASE)
    _assert_risks(['>=10 Inline Views present in query.'], resp['hints'])


  def test_risk_cartesian_cross_join(self):
    source_platform = 'hive'
    query = '''SELECT ID, NAME, AMOUNT, DATE FROM CUSTOMERS, ORDERS
'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=BaseTestOptimizerApi.DATABASE)
    _assert_risks(['Cartesian or CROSS join found.'], resp['hints'])

    source_platform = 'hive'
    query = '''SELECT s07.description,
s07.total_emp,
s08.total_emp,
s07.salary
FROM sample_07 s07,
sample_08 s08
WHERE s07.salary > 88
ORDER BY s07.salary DESC
'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=BaseTestOptimizerApi.DATABASE)
    _assert_risks(['Cartesian or CROSS join found.'], resp['hints'])


  def test_risk_5_joins(self):
    source_platform = 'hive'
    query = '''SELECT s07.description, s07.total_emp, s08.total_emp, s07.salary
FROM
  sample_07 s07
JOIN
  sample_08 s08
ON ( s07.code = s08.code )
JOIN
  sample_06 s06
ON ( s07.code = s06.code )
JOIN
  sample_05 s05
ON ( s07.code = s05.code )
JOIN
  sample_04 s04
ON ( s07.code = s04.code )
JOIN
  sample_03 s03
ON ( s07.code = s03.code )
JOIN
  sample_02 s02
ON ( s07.code = s02.code )
JOIN
  sample_01 s01
ON ( s07.code = s01.code )

WHERE
( s07.total_emp > s08.total_emp
 AND s07.salary > 100000 )
ORDER BY s07.salary DESC
LIMIT 1000
'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=BaseTestOptimizerApi.DATABASE)
    _assert_risks(['>=5 table joins or >=10 join conditions found.'], resp['hints'])


  def test_risk_10_group_by_columns(self):

    source_platform = 'impala'
    query = '''SELECT *
FROM transactions
GROUP BY account_client,
         account_cty_code,
         account_num,
         allow_code,
         ally_811,
         anti_detect,
         anti_transcode,
         cc_fee,
         auth_code,
         cvv_eval,
         cred_extract, denied_code
         limit 5
'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=BaseTestOptimizerApi.DATABASE)
    _assert_risks(['>=10 columns present in GROUP BY list.'], resp['hints'])

    assert_equal(resp['noDDL'], ['%s.transactions' % BaseTestOptimizerApi.DATABASE])
    assert_equal(resp['noStats'], ['%s.transactions' % BaseTestOptimizerApi.DATABASE])


  def test_risk_cross_join_false_positive(self):
    source_platform = 'hive'
    query = '''SELECT s07.description, s07.total_emp, s08.total_emp, s07.salary
FROM
  sample_07 s07 JOIN
  sample_08 s08
ON ( s07.code = s08.code )
WHERE
( s07.total_emp > s08.total_emp
 AND s07.salary > 100000 )
ORDER BY s07.salary DESC
LIMIT 1000
'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=BaseTestOptimizerApi.DATABASE)
    _assert_risks(['Cartesian or CROSS join found.'], resp['hints'], present=False)


    source_platform = 'hive'
    query = '''select x from x join y where x.a = y.a'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=BaseTestOptimizerApi.DATABASE)
    _assert_risks(['Cartesian or CROSS join found.'], resp['hints'], present=False)


  def test_risk_no_filter_on_any_partitioned_column(self):
    source_platform = 'hive'
    query = '''SELECT * FROM web_logs'''
    db_name = BaseTestOptimizerApi.DATABASE

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=db_name)
    _assert_risks(['Query on partitioned table is missing filters on partioning columns.'], resp['hints'])

    assert_false(resp['noDDL'], resp) # DDL was uploaded already
    assert_equal(resp['noStats'], ['%s.web_logs' % BaseTestOptimizerApi.DATABASE])


    source_platform = 'hive'
    query = '''SELECT * FROM web_logs LIMIT 1'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=db_name)
    _assert_risks(['Query on partitioned table is missing filters on partioning columns.'], resp['hints'])


    source_platform = 'hive'
    query = '''SELECT * FROM web_logs WHERE app='oozie' LIMIT 1'''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=db_name)
    _assert_risks(['Query on partitioned table is missing filters on partioning columns.'], resp['hints'])


    source_platform = 'hive'
    query = '''SELECT * FROM web_logs WHERE date='20180101' '''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=db_name)
    _assert_risks(['Query on partitioned table is missing filters on partioning columns.'], resp['hints'], present=False)

    source_platform = 'hive'
    query = '''SELECT * FROM web_logs WHERE app='oozie' AND date='20180101' '''

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=db_name)
    _assert_risks(['Query on partitioned table is missing filters on partioning columns.'], resp['hints'], present=False)


  def test_risk_listing_all_risk_tables_all_the_time(self):
    source_platform = 'hive'
    query = '''SELECT * FROM web_logs JOIN a ON web_logs.id = a.id LIMIT 100'''
    db_name = BaseTestOptimizerApi.DATABASE

    resp = self.api.query_risk(query=query, source_platform=source_platform, db_name=db_name)
    _assert_risks(['Query on partitioned table is missing filters on partioning columns.'], resp['hints'])

    assert_equal([suggestion for suggestion in resp['hints'] if suggestion['riskId'] == 22][0]['riskTables'], ['%s.web_logs' % BaseTestOptimizerApi.DATABASE])
    assert_equal(resp['noDDL'], ['%s.a' % BaseTestOptimizerApi.DATABASE])
    assert_equal(resp['noStats'], ['%s.a' % BaseTestOptimizerApi.DATABASE, '%s.web_logs' % BaseTestOptimizerApi.DATABASE])


def _assert_risks(risks, suggestions, present=True):
  suggestion_names = [suggestion['riskAnalysis'] for suggestion in suggestions]

  for risk in risks:
    if present:
      assert_true(risk in suggestion_names, suggestions)
    else:
      assert_false(risk in suggestion_names, suggestions)
