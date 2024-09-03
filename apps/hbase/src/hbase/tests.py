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
import sys
import json
import shutil
import tempfile
from builtins import object

import pytest
from django.test import TestCase
from django.urls import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster
from hbase.api import HbaseApi
from hbase.conf import HBASE_CONF_DIR
from hbase.hbase_site import (
  _CNF_HBASE_IMPERSONATION_ENABLED,
  get_conf,
  get_server_authentication,
  get_server_principal,
  is_impersonation_enabled,
  reset,
)
from useradmin.models import User


def test_security_plain():
  tmpdir = tempfile.mkdtemp()
  finish = HBASE_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = hbase_site_xml()
    open(os.path.join(tmpdir, 'hbase-site.xml'), 'w').write(xml)
    reset()

    assert 'NOSASL' == get_server_authentication()
    assert 'test' == get_server_principal()

    security = HbaseApi._get_security()

    assert 'test' == security['kerberos_principal_short_name']
    assert False is security['use_sasl']
  finally:
    reset()
    finish()
    shutil.rmtree(tmpdir)


def test_security_kerberos():
  tmpdir = tempfile.mkdtemp()
  finish = HBASE_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = hbase_site_xml(authentication='kerberos')
    open(os.path.join(tmpdir, 'hbase-site.xml'), 'w').write(xml)
    reset()

    assert 'KERBEROS' == get_server_authentication()
    assert 'test' == get_server_principal()

    security = HbaseApi._get_security()

    assert 'test' == security['kerberos_principal_short_name']
    assert True is security['use_sasl']
  finally:
    reset()
    finish()
    shutil.rmtree(tmpdir)


def hbase_site_xml(kerberos_principal='test/test.com@TEST.COM', authentication='NOSASL'):
  return """
    <configuration>

      <property>
        <name>hbase.thrift.kerberos.principal</name>
        <value>%(kerberos_principal)s</value>
      </property>

      <property>
        <name>hbase.security.authentication</name>
        <value>%(authentication)s</value>
      </property>

    </configuration>
  """ % {
    'kerberos_principal': kerberos_principal,
    'authentication': authentication,
  }


def test_impersonation_is_decorator_is_there():
  # Decorator is still there
  from hbased.Hbase import do_as


@pytest.mark.django_db
def test_impersonation():
  from hbased import Hbase as thrift_hbase

  c = make_logged_in_client(username='test_hbase', is_superuser=False)
  grant_access('test_hbase', 'test_hbase', 'hbase')
  user = User.objects.get(username='test_hbase')

  proto = MockProtocol()
  client = thrift_hbase.Client(proto)

  impersonation_enabled = is_impersonation_enabled()

  get_conf()[_CNF_HBASE_IMPERSONATION_ENABLED] = 'FALSE'
  try:
    client.getTableNames(doas=user.username)
  except AttributeError:
    pass  # We don't mock everything
  finally:
    get_conf()[_CNF_HBASE_IMPERSONATION_ENABLED] = impersonation_enabled

  assert {} == proto.get_headers()

  get_conf()[_CNF_HBASE_IMPERSONATION_ENABLED] = 'TRUE'

  try:
    client.getTableNames(doas=user.username)
  except AttributeError:
    pass  # We don't mock everything
  finally:
    get_conf()[_CNF_HBASE_IMPERSONATION_ENABLED] = impersonation_enabled

  assert {'doAs': 'test_hbase'} == proto.get_headers()


class MockHttpClient(object):
  def __init__(self):
    self.headers = {}

  def setCustomHeaders(self, headers):
    self.headers = headers


class MockTransport(object):
  def __init__(self):
    self._TBufferedTransport__trans = MockHttpClient()


class MockProtocol(object):
  def __init__(self):
    self.trans = MockTransport()

  def getTableNames(self):
    pass

  def get_headers(self):
    return self.trans._TBufferedTransport__trans.headers


@pytest.mark.integration
class TestIntegrationWithHBase(TestCase):
  @classmethod
  def setup_class(cls):
    if not is_live_cluster():
      pytest.skip('These tests can only run on a live cluster')

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "indexer")

  def test_list_tables(self):
    if not is_live_cluster():
      pytest.skip('HUE-2910: Skipping because test is not reentrant')

    for cluster in HbaseApi(self.user).getClusters():
      resp = self.client.post('/hbase/api/getTableList/' + cluster['name'])
      content = json.loads(resp.content)
      assert 'data' in content, content
