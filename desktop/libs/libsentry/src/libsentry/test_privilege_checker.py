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
from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_false, assert_true

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access

from libsentry.api import get_api as get_api_v1
from libsentry.api2 import get_api as get_api_v2
from libsentry.privilege_checker import PrivilegeChecker


class TestDocumentConverter(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="test", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")
    grant_access("test", "test", "libsentry")

    self.api_v1 = get_api_v1(self.user)
    self.api_v2 = get_api_v2(self.user, component='solr')
    self.checker = PrivilegeChecker(user=self.user, api_v1=self.api_v1, api_v2=self.api_v2)


  def test_read_privilege(self):
    try:
      from mock import Mock
    except ImportError:
      raise SkipTest("Skips until HUE-2947 is resolved")

    action = 'READ'
    authorizableSet = [
      # V1 authorizables
      {u'column': None, u'table': u'customers', u'db': u'default', u'server': u'server1'},
      {u'column': None, u'table': u'sample_07', u'db': u'default', u'server': u'server1'},
      {u'column': None, u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': None, u'table': u'web_logs', u'db': u'default', u'server': u'server1'},
      {u'column': 'salary', u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': 'code', u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': 'total_emp', u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': 'total_emp', u'table': u'sample_07', u'db': u'default', u'server': u'server1'},
      # V2 authorizables
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'logs_demo'},
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'test_demo'},
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'twitter_demo'},
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'COLLECTION', u'name': u'yelp_demo'},
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'CONFIG', u'name': u'twitter_demo'},
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'CONFIG', u'name': u'managedTemplate'},
      {u'component': u'solr', u'serviceName': u'server1', u'type': u'CONFIG', u'name': u'yelp_demo'},
    ]

    self.api_v1.list_sentry_roles_by_group = Mock(return_value=[{'name': 'test', 'group': 'test'}])
    self.api_v1.list_sentry_privileges_by_role = Mock(return_value=[
      {'column': 'total_emp', 'grantOption': False, 'timestamp': 1478810635378, 'database': 'default', 'action': 'INSERT', 'scope': 'COLUMN', 'table': 'sample_08', 'URI': '', 'server': 'server1'},
      {'column': '', 'grantOption': False, 'timestamp': 1478810422058, 'database': 'default', 'action': 'SELECT', 'scope': 'TABLE', 'table': 'customers', 'URI': '', 'server': 'server1'},
      {'column': '', 'grantOption': False, 'timestamp': 1478810513849, 'database': 'default', 'action': 'SELECT', 'scope': 'TABLE', 'table': 'web_logs', 'URI': '', 'server': 'server1'},
      {'column': '', 'grantOption': False, 'timestamp': 1478810590335, 'database': 'default', 'action': 'SELECT', 'scope': 'TABLE', 'table': 'sample_08', 'URI': '', 'server': 'server1'},
      {'column': 'salary', 'grantOption': False, 'timestamp': 1478810635396, 'database': 'default', 'action': 'ALL', 'scope': 'COLUMN', 'table': 'sample_08', 'URI': '', 'server': 'server1'}
    ])

    self.api_v2.list_sentry_roles_by_group = Mock(return_value=[{'name': 'test', 'group': 'test'}])
    self.api_v2.list_sentry_privileges_by_role = Mock(return_value=[
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'ALL', 'authorizables': [{'type': 'CONFIG', 'name': 'managedTemplate'}]},
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'QUERY', 'authorizables': [{'type': 'COLLECTION', 'name': 'twitter_demo'}]},
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'UPDATE', 'authorizables': [{'type': 'COLLECTION', 'name': 'yelp_demo'}]},
      {'grantOption': False, 'timestamp': None, 'component': 'solr', 'serviceName': 'server1', 'grantorPrincipal': None, 'action': 'ALL', 'authorizables': [{'type': 'CONFIG', 'name': 'yelp_demo'}]}
    ])

    filtered_set = self.checker.filter_objects(authorizableSet=authorizableSet, action=action)
    expected_filtered_set = [
      # V2 authorizables
      {u'type': u'COLLECTION', u'serviceName': u'server1', u'component': u'solr', u'name': u'twitter_demo'},
      {u'type': u'COLLECTION', u'serviceName': u'server1', u'component': u'solr', u'name': u'yelp_demo'},
      {u'type': u'CONFIG', u'serviceName': u'server1', u'component': u'solr', u'name': u'managedTemplate'},
      {u'type': u'CONFIG', u'serviceName': u'server1', u'component': u'solr', u'name': u'yelp_demo'},
      # V1 authorizables
      {u'column': None, u'table': u'customers', u'db': u'default', u'server': u'server1'},
      {u'column': None, u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': 'code', u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': 'salary', u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': 'total_emp', u'table': u'sample_08', u'db': u'default', u'server': u'server1'},
      {u'column': None, u'table': u'web_logs', u'db': u'default', u'server': u'server1'},
    ]
    assert_equal(expected_filtered_set, sorted(filtered_set, key=lambda obj: (obj.get('table'), obj.get('column'), obj.get('component'), obj.get('type'), obj.get('name'))))
