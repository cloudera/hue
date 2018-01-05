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

from django.urls import reverse
from nose.plugins.skip import SkipTest
from nose.tools import assert_equal

from hadoop.conf import HDFS_CLUSTERS

from desktop.lib.test_utils import clear_sys_caches
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group

from libsentry import api
from security.api.hive import _massage_uri, _get_splitted_path


def mocked_get_api(user):
  return MockHiveApi(user)


class MockHiveApi(object):
  def __init__(self, user):
    self.user = user

  def list_sentry_roles_by_group(self, groupName): # return GroupName only
    return [{'name': groupName}]


class TestMockedApi(object):

  def setUp(self):
    if not hasattr(api, 'OriginalSentryApi'):
      api.OriginalSentryApi = api.get_api
    api.get_api = mocked_get_api

    self.client = make_logged_in_client(username='sentry_test', groupname='test', is_superuser=False)
    self.client_admin = make_logged_in_client(username='sentry_hue', groupname='hue', is_superuser=False)

    grant_access("sentry_test", "test", "security")
    grant_access("sentry_hue", "hue", "security")
    add_to_group("sentry_test")
    add_to_group("sentry_hue")

    raise SkipTest

  def tearDown(self):
    api.get_api = api.OriginalSentryApi


  def test_list_sentry_roles_by_group(self):
    response = self.client.post(reverse("security:list_sentry_roles_by_group"), {'groupName': ''})
    assert_equal('*', json.loads(response.content).get('roles', [{'name': ''}])[0]['name'], response.content)

    response = self.client.post(reverse("security:list_sentry_roles_by_group"), {'groupName': 'test'})
    assert_equal('test', json.loads(response.content).get('roles', [{'name': ''}])[0]['name'], response.content)


    response = self.client_admin.post(reverse("security:list_sentry_roles_by_group"), {'groupName': ''})
    assert_equal(None, json.loads(response.content).get('roles', [{'name': ''}])[0]['name'], response.content)

    response = self.client_admin.post(reverse("security:list_sentry_roles_by_group"), {'groupName': 'test'})
    assert_equal('test', json.loads(response.content).get('roles', [{'name': ''}])[0]['name'], response.content)


class TestUtils(object):

  def test_massage_uri(self):

    finish = HDFS_CLUSTERS['default'].LOGICAL_NAME.set_for_testing('namenode')
    clear_sys_caches()

    try:
      assert_equal('', _massage_uri(''))

      assert_equal('namenode/data', _massage_uri('hdfs:///data'))

      assert_equal('hdfs://nn:11/data', _massage_uri('hdfs://nn:11/data'))

      assert_equal('hdfs://logical/data', _massage_uri('hdfs://logical/data'))

      assert_equal('namenode/data', _massage_uri('/data'))

      assert_equal('file:///data', _massage_uri('file:///data'))
    finally:
      finish()

    finish = HDFS_CLUSTERS['default'].FS_DEFAULTFS.set_for_testing('hdfs://fs_defaultfs:8021')
    clear_sys_caches()

    try:
      assert_equal('', _massage_uri(''))

      assert_equal('hdfs://fs_defaultfs:8021/data', _massage_uri('hdfs:///data'))

      assert_equal('hdfs://nn:11/data', _massage_uri('hdfs://nn:11/data'))

      assert_equal('hdfs://logical/data', _massage_uri('hdfs://logical/data'))

      assert_equal('hdfs://fs_defaultfs:8021/data', _massage_uri('/data'))

      assert_equal('file:///data', _massage_uri('file:///data'))
    finally:
      finish()

  def test_get_splitted_path(self):
    assert_equal(('', '', ''), _get_splitted_path(''))
    assert_equal(('db', '', ''), _get_splitted_path('db'))
    assert_equal(('db', 'table', ''), _get_splitted_path('db.table'))
    assert_equal(('db', 'table', 'column'), _get_splitted_path('db.table.column'))
    assert_equal(('db', 'table', 'column'), _get_splitted_path('db.table.column.blah'))
