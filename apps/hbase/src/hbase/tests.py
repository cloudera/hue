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
import shutil
import tempfile

from nose.tools import assert_true, assert_equal

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group

from hbase.api import HbaseApi
from hbase.conf import HBASE_CONF_DIR
from hbase.hbase_site import get_server_authentication, get_server_principal, get_conf, reset, _CNF_HBASE_IMPERSONATION_ENABLED, is_impersonation_enabled
from hadoop.pseudo_hdfs4 import is_live_cluster
from nose.plugins.skip import SkipTest
from django.urls import reverse


def test_security_plain():
  tmpdir = tempfile.mkdtemp()
  finish = HBASE_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = hbase_site_xml()
    file(os.path.join(tmpdir, 'hbase-site.xml'), 'w').write(xml)
    reset()

    assert_equal('NOSASL', get_server_authentication())
    assert_equal('test', get_server_principal())

    security = HbaseApi._get_security()

    assert_equal('test', security['kerberos_principal_short_name'])
    assert_equal(False, security['use_sasl'])
  finally:
    reset()
    finish()
    shutil.rmtree(tmpdir)


def test_security_kerberos():
  tmpdir = tempfile.mkdtemp()
  finish = HBASE_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = hbase_site_xml(authentication='kerberos')
    file(os.path.join(tmpdir, 'hbase-site.xml'), 'w').write(xml)
    reset()

    assert_equal('KERBEROS', get_server_authentication())
    assert_equal('test', get_server_principal())

    security = HbaseApi._get_security()

    assert_equal('test', security['kerberos_principal_short_name'])
    assert_equal(True, security['use_sasl'])
  finally:
    reset()
    finish()
    shutil.rmtree(tmpdir)


def hbase_site_xml(
    kerberos_principal='test/test.com@TEST.COM',
    authentication='NOSASL'):

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
    pass # We don't mock everything
  finally:
    get_conf()[_CNF_HBASE_IMPERSONATION_ENABLED] = impersonation_enabled

  assert_equal({}, proto.get_headers())


  get_conf()[_CNF_HBASE_IMPERSONATION_ENABLED] = 'TRUE'

  try:
    client.getTableNames(doas=user.username)
  except AttributeError:
    pass # We don't mock everything
  finally:
    get_conf()[_CNF_HBASE_IMPERSONATION_ENABLED] = impersonation_enabled

  assert_equal({'doAs': u'test_hbase'}, proto.get_headers())



class MockHttpClient():
  def __init__(self):
    self.headers = {}

  def setCustomHeaders(self, headers):
    self.headers = headers

class MockTransport():
  def __init__(self):
    self._TBufferedTransport__trans = MockHttpClient()

class MockProtocol():
  def __init__(self):
    self.trans = MockTransport()

  def getTableNames(self):
    pass

  def get_headers(self):
    return self.trans._TBufferedTransport__trans.headers



class TestIntegrationWithHBase:
  integration = True

  @classmethod
  def setup_class(cls):

    if not is_live_cluster():
      raise SkipTest('These tests can only run on a live cluster')

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "indexer")


  def test_list_tables(self):
    if not is_live_cluster():
      raise SkipTest('HUE-2910: Skipping because test is not reentrant')

    for cluster in HbaseApi(self.user).getClusters():
      resp = self.client.post('/hbase/api/getTableList/' + cluster['name'])
      content = json.loads(resp.content)
      assert_true('data' in content, content)
