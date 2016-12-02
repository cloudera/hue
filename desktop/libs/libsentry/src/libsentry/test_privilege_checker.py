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

from django.contrib.auth.models import User
from nose.tools import assert_equal, assert_false, assert_true

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access

from libsentry.privilege_checker import PrivilegeChecker


class MockSentryApiV1(object):


  def __init__(self, *args, **kwargs):
    pass


  def list_sentry_roles_by_group(self, *args, **kwargs):
    return [{'name': 'test', 'group': 'test'}]


  def list_sentry_privileges_by_role(self, *args, **kwargs):
    return [
      # Column ALL
      {'column': 'column_all', 'grantOption': False, 'timestamp': 1478810635396, 'database': 'default', 'action': 'ALL', 'scope': 'COLUMN', 'table': 'test_column', 'URI': '', 'server': 'server1'},
      # Column INSERT
      {'column': 'column_insert', 'grantOption': False, 'timestamp': 1478810635378, 'database': 'default', 'action': 'INSERT', 'scope': 'COLUMN', 'table': 'test_column', 'URI': '', 'server': 'server1'},
      # Column SELECT
      {'column': 'column_select', 'grantOption': False, 'timestamp': 1478810590335, 'database': 'default', 'action': 'SELECT', 'scope': 'TABLE', 'table': 'test_column', 'URI': '', 'server': 'server1'},
      # Table ALL
      {'column': '', 'grantOption': False, 'timestamp': 1478810513849, 'database': 'default', 'action': 'ALL', 'scope': 'TABLE', 'table': 'test_table_all', 'URI': '', 'server': 'server1'},
      # Table INSERT
      {'column': '', 'grantOption': False, 'timestamp': 1478810513849, 'database': 'default', 'action': 'INSERT', 'scope': 'TABLE', 'table': 'test_table_insert', 'URI': '', 'server': 'server1'},
      # Table SELECT
      {'column': '', 'grantOption': False, 'timestamp': 1478810422058, 'database': 'default', 'action': 'SELECT', 'scope': 'TABLE', 'table': 'test_table_select', 'URI': '', 'server': 'server1'},
      # DB ALL
      {'column': '', 'grantOption': False, 'timestamp': 1478810513849, 'database': 'test_db_all', 'action': 'ALL', 'scope': 'DATABASE', 'table': '', 'URI': '', 'server': 'server1'},
      # DB INSERT
      {'column': '', 'grantOption': False, 'timestamp': 1478810513849, 'database': 'test_db_insert', 'action': 'INSERT', 'scope': 'DATABASE', 'table': '', 'URI': '', 'server': 'server1'},
      # DB SELECT
      {'column': '', 'grantOption': False, 'timestamp': 1478810513849, 'database': 'test_db_select', 'action': 'SELECT', 'scope': 'DATABASE', 'table': '', 'URI': '', 'server': 'server1'},
      # URI ALL
      {'column': '', 'grantOption': False, 'timestamp': 1478810513849, 'database': '', 'action': 'ALL', 'scope': 'URI', 'table': '', 'URI': 'hdfs://ha-nn-uri/data/landing-skid', 'server': 'server1'},
    ]


class MockSentryApiV2(object):


  def __init__(self, *args, **kwargs):
    pass


  def list_sentry_roles_by_group(self, *args, **kwargs):
    return [{'name': 'test', 'group': 'test'}]


  def list_sentry_privileges_by_role(self, *args, **kwargs):
    return [
      # Collection ALL
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'ALL', 'authorizables': [{'type': 'COLLECTION', 'name': 'web_logs_demo'}]},
      # Collection UPDATE
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'UPDATE', 'authorizables': [{'type': 'COLLECTION', 'name': 'yelp_demo'}]},
      # Collection QUERY
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'QUERY', 'authorizables': [{'type': 'COLLECTION', 'name': 'twitter_demo'}]},
      # Config ALL
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'ALL', 'authorizables': [{'type': 'CONFIG', 'name': 'yelp_demo'}]},
      # URI ALL
      {'grantOption': False, 'timestamp': None, 'component': 'hdfs', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'ALL', 'authorizables': [{'type': 'URI', 'name': 'hdfs://ha-nn-uri/data/landing-skid'}]},
      # S3 URI ALL
      {'grantOption': False, 'timestamp': None, 'component': 's3', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'ALL', 'authorizables': [{'type': 'URI', 'name': 's3a://hue-datasets/test'}]},
    ]


class TestPrivilegeChecker(object):


  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="test", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")
    grant_access("test", "test", "libsentry")

    self.api_v1 = MockSentryApiV1()
    self.api_v2 = MockSentryApiV2()
    self.checker = PrivilegeChecker(user=self.user, api_v1=self.api_v1, api_v2=self.api_v2)


  def test_to_sentry_authorizables(self):
    objectSet = ['foo', 'bar', 'baz', 'boom']
    expectedSet = [
      {'db': 'foo', 'server': 'server1'},
      {'db': 'bar', 'server': 'server1'},
      {'db': 'baz', 'server': 'server1'},
    ]

    def test_key_fn(obj):
      if obj != 'boom':
        return {'db': obj}
      else:
        return None

    authorizableSet = self.checker._to_sentry_authorizables(objects=objectSet, key=test_key_fn)
    assert_equal(expectedSet, authorizableSet, authorizableSet)
    # Original list of objects should not be mutated
    assert_true(['bar', 'baz', 'foo'], sorted(objectSet, reverse=True))

    objectSet = [
      {
          u'identity': u'9282adb88478c2ce4beb13dbba997ef5',
          u'serDeLibName': u'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
          u'outputFormat': u'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
          u'sourceType': u'HIVE',
          u'inputFormat': u'org.apache.hadoop.mapred.TextInputFormat',
          u'created': u'2016-07-25T17: 22: 18.000Z',
          u'sourceId': u'4fbdadc6899638782fc8cb626176dc7b',
          u'tags': [
              u'asdf'
          ],
          u'deleted': False,
          u'_version_': 1549818955715051520,
          u'userEntity': False,
          u'properties': {
              u'1': u'2'
          },
          u'extractorRunId': u'4fbdadc6899638782fc8cb626176dc7b##1',
          u'compressed': False,
          u'parentPath': u'/default',
          u'owner': u'admin',
          u'originalName': u'sample_08',
          u'type': u'TABLE',
          u'lastAccessed': u'1970-01-01T00: 00: 00.000Z',
          u'fileSystemPath': u'hdfs: //hue-team-1.vpc.cloudera.com: 8020/user/hive/warehouse/sample_08',
          u'internalType': u'hv_table'
      },
      {
          u'serDeLibName': u'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
          u'owner': u'admin',
          u'fileSystemPath': u'hdfs: //hue-team-1.vpc.cloudera.com: 8020/user/hive/warehouse/sample_07',
          u'lastModifiedBy': u'admin',
          u'_version_': 1550478188023382016,
          u'type': u'TABLE',
          u'internalType': u'hv_table',
          u'sourceType': u'HIVE',
          u'inputFormat': u'org.apache.hadoop.mapred.TextInputFormat',
          u'tags': [
              u'hue-bugblitz',
              u'vvvvv',
              u'asdf',
              u'ffff'
          ],
          u'deleted': False,
          u'userEntity': False,
          u'originalDescription': u'HueisaWebinterfaceforanalyzingdatawithApacheHadoop.HueisaWebinterfaceforanalyzingdatawithApacheHadoop.HueisaWebinterfaceforanalyzingdatawithApacheHadoop.HueisaWebinterfaceforanalyzingdatawithApacheHadoop.\n\nHueisaWebinterfaceforanalyzingdatawithApacheHadoop.HueisaWebinterfaceforanalyzingdatawithApacheHadoop.',
          u'compressed': False,
          u'identity': u'ea27302e11370a3927ac11cbb920891d',
          u'outputFormat': u'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
          u'extractorRunId': u'4fbdadc6899638782fc8cb626176dc7b##8979',
          u'created': u'2016-07-25T17: 22: 15.000Z',
          u'sourceId': u'4fbdadc6899638782fc8cb626176dc7b',
          u'lastModified': u'2016-09-28T16: 25: 07.000Z',
          u'parentPath': u'/default',
          u'originalName': u'sample_07',
          u'lastAccessed': u'1970-01-01T00: 00: 00.000Z'
      }
    ]
    expectedSet = [
      {u'column': None, u'table': u'sample_08', u'db': u'default', 'server': 'server1'},
      {u'column': None, u'table': u'sample_07', u'db': u'default', 'server': 'server1'}
    ]

    def test_key_fn(obj):
      return {
        'column': None,
        'table': obj.get('originalName'),
        'db': obj.get('parentPath', '').strip('/')
      }

    authorizableSet = self.checker._to_sentry_authorizables(objects=objectSet, key=test_key_fn)
    assert_equal(expectedSet, authorizableSet, authorizableSet)
    # Original list of objects should not be mutated
    assert_true(all('server' not in obj for obj in objectSet))
    assert_true(all('db' not in obj for obj in objectSet))


  def test_columns_select(self):
    action = 'SELECT'
    authorizableSet = [
      # column-level SELECT privilege exists
      {u'column': 'column_select', u'table': u'test_column', u'db': u'default', u'server': u'server1'},
      # table-level SELECT privileges exists
      {u'column': 'id', u'table': u'test_table_select', u'db': u'default', u'server': u'server1'},
      # db-level SELECT privileges exist
      {u'column': 'id', u'table': u'test_db_select', u'db': u'test_db_select', u'server': u'server1'},
      # no privileges exist
      {u'column': 'id', u'table': u'test_none', u'db': u'default', u'server': u'server1'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'column': 'column_select', u'table': u'test_column', u'db': u'default', u'server': u'server1'},
     {u'column': 'id', u'table': u'test_table_select', u'db': u'default', u'server': u'server1'},
     {u'column': 'id', u'table': u'test_db_select', u'db': u'test_db_select', u'server': u'server1'}
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_columns_insert(self):
    action = 'INSERT'
    authorizableSet = [
      # column-level ALL privilege exists
      {u'column': 'column_all', u'table': u'test_column', u'db': u'default', u'server': u'server1'},
      # column-level INSERT privileges exist
      {u'column': 'column_insert', u'table': u'test_column', u'db': u'default', u'server': u'server1'},
      # SELECT, but not INSERT, privilege exists
      {u'column': 'column_select', u'table': u'test_column', u'db': u'default', u'server': u'server1'},
      # no privileges exist
      {u'column': 'salary', u'table': u'sample_07', u'db': u'default', u'server': u'server1'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'column': 'column_all', u'table': u'test_column', u'db': u'default', u'server': u'server1'},
      {u'column': 'column_insert', u'table': u'test_column', u'db': u'default', u'server': u'server1'},
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_tables_select(self):
    action = 'SELECT'
    authorizableSet = [
      # table-level SELECT privileges exists
      {u'column': '', u'table': u'test_table_select', u'db': u'default', u'server': u'server1'},
      # table-level INSERT privileges exists
      {u'column': '', u'table': u'test_table_insert', u'db': u'default', u'server': u'server1'},
      # db-level SELECT privileges exist
      {u'column': '', u'table': u'test_db_select', u'db': u'test_db_select', u'server': u'server1'},
      # no privileges exist
      {u'column': '', u'table': u'test_none', u'db': u'default', u'server': u'server1'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'column': '', u'table': u'test_table_insert', u'db': u'default', u'server': u'server1'},
      {u'column': '', u'table': u'test_table_select', u'db': u'default', u'server': u'server1'},
      {u'column': '', u'table': u'test_db_select', u'db': u'test_db_select', u'server': u'server1'}
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_tables_insert(self):
    action = 'INSERT'
    authorizableSet = [
      # table-level ALL privilege exists
      {u'column': '', u'table': u'test_table_all', u'db': u'default', u'server': u'server1'},
      # table-level INSERT privileges exist
      {u'column': '', u'table': u'test_table_insert', u'db': u'default', u'server': u'server1'},
      # SELECT, but not INSERT, privilege exists
      {u'column': '', u'table': u'test_table_select', u'db': u'default', u'server': u'server1'},
      # no privileges exist
      {u'column': '', u'table': u'sample_07', u'db': u'default', u'server': u'server1'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'column': '', u'table': u'test_table_all', u'db': u'default', u'server': u'server1'},
      {u'column': '', u'table': u'test_table_insert', u'db': u'default', u'server': u'server1'},
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_dbs_select(self):
    action = 'SELECT'
    authorizableSet = [
      # db-level SELECT privileges exists
      {u'column': '', u'table': u'', u'db': u'test_db_select', u'server': u'server1'},
      # db-level INSERT privileges exists
      {u'column': '', u'table': u'', u'db': u'test_db_insert', u'server': u'server1'},
      # no privileges exist
      {u'column': '', u'table': u'', u'db': u'test_db_none', u'server': u'server1'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'column': '', u'table': u'', u'db': u'test_db_insert', u'server': u'server1'},
      {u'column': '', u'table': u'', u'db': u'test_db_select', u'server': u'server1'},
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_dbs_insert(self):
    action = 'INSERT'
    authorizableSet = [
      # db-level ALL privilege exists
      {u'column': '', u'table': u'', u'db': u'test_db_all', u'server': u'server1'},
      # db-level INSERT privileges exist
      {u'column': '', u'table': u'', u'db': u'test_db_insert', u'server': u'server1'},
      # SELECT, but not INSERT, privilege exists
      {u'column': '', u'table': u'', u'db': u'test_db_select', u'server': u'server1'},
      # no privileges exist
      {u'column': '', u'table': u'', u'db': u'test_db_none', u'server': u'server1'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'column': '', u'table': u'', u'db': u'test_db_all', u'server': u'server1'},
      {u'column': '', u'table': u'', u'db': u'test_db_insert', u'server': u'server1'},
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_collections_query(self):
    action = 'QUERY'
    authorizableSet = [
      # ALL privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'web_logs_demo'},
      # UPDATE privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'yelp_demo'},
      # QUERY privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'twitter_demo'},
      # No privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'test_demo'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'type': u'COLLECTION', u'serviceName': u'server1', u'component': u'solr', u'name': u'twitter_demo'},
      {u'type': u'COLLECTION', u'serviceName': u'server1', u'component': u'solr', u'name': u'web_logs_demo'},
      {u'type': u'COLLECTION', u'serviceName': u'server1', u'component': u'solr', u'name': u'yelp_demo'}
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI', 'serviceName', 'component', 'type', 'name']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])), sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_collections_update(self):
    action = 'UPDATE'
    authorizableSet = [
      # ALL privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'web_logs_demo'},
      # UPDATE privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'yelp_demo'},
      # QUERY privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'twitter_demo'},
      # No privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'test_demo'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'type': u'COLLECTION', u'serviceName': u'server1', u'component': u'solr', u'name': u'web_logs_demo'},
      {u'type': u'COLLECTION', u'serviceName': u'server1', u'component': u'solr', u'name': u'yelp_demo'}
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI', 'serviceName', 'component', 'type', 'name']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])),
                 sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_config(self):
    action = 'UPDATE'
    authorizableSet = [
      # ALL privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'CONFIG', u'name': u'yelp_demo'},
      # No privilege
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'CONFIG', u'name': u'test_demo'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'type': u'CONFIG', u'serviceName': u'server1', u'component': u'solr', u'name': u'yelp_demo'}
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI', 'serviceName', 'component', 'type', 'name']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])),
                 sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))


  def test_uri(self):
    action = 'UPDATE'
    authorizableSet = [
      # HDFS privilege
      {u'component': u'hdfs', u'serviceName': u'server1', u'type': u'URI', u'name': u'hdfs://ha-nn-uri/data/landing-skid'},
      # S3 privilege
      {u'component': u's3', u'serviceName': u'server1', u'type': u'URI', u'name': u's3a://hue-datasets/test'},
      # No privilege
      {u'component': u's3', u'serviceName': u'server1', u'type': u'URI', u'name': u's3a://hue-datasets/none'},
    ]

    filtered_set = self.checker.filter_objects(objects=authorizableSet, action=action)
    expected_filtered_set = [
      {u'type': u'URI', u'serviceName': u'server1', u'component': u'hdfs', u'name': u'hdfs://ha-nn-uri/data/landing-skid'},
      {u'type': u'URI', u'serviceName': u'server1', u'component': u's3',  u'name': u's3a://hue-datasets/test'}
    ]

    sort_keys = ['server', 'db', 'table', 'column', 'URI', 'serviceName', 'component', 'type', 'name']
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])),
                 sorted(filtered_set, key=lambda obj: ([obj.get(key) for key in sort_keys])))
