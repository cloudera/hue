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
import shutil
import tempfile

from nose.tools import assert_true, assert_equal

from hbase.api import HbaseApi
from hbase.conf import HBASE_CONF_DIR
from hbase.hbase_site import get_server_authentication, get_server_principal, reset


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
