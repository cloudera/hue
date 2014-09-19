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

from nose.tools import assert_true, assert_equal, assert_false, assert_not_equal, assert_raises

from libsentry import sentry_site
from libsentry.conf import SENTRY_CONF_DIR
from libsentry.sentry_site import get_sentry_server_principal,\
  get_sentry_server_admin_groups
from libsentry.client import SentryClient


def test_security_plain():
  tmpdir = tempfile.mkdtemp()
  finish = SENTRY_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = sentry_site_xml(provider='default')
    file(os.path.join(tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    assert_equal('test/test.com@TEST.COM', get_sentry_server_principal())
    assert_equal(['hive', 'impala', 'hue'], get_sentry_server_admin_groups())

    security = SentryClient('test.com', 11111, 'test')._get_security()

    assert_equal('test', security['kerberos_principal_short_name'])
    assert_equal(False, security['use_sasl'])
    assert_equal('NOSASL', security['mechanism'])
  finally:
    sentry_site.reset()
    finish()
    shutil.rmtree(tmpdir)


def test_security_kerberos():
  tmpdir = tempfile.mkdtemp()
  finish = SENTRY_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = sentry_site_xml(provider='default', authentication='kerberos')
    file(os.path.join(tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    security = SentryClient('test.com', 11111, 'test')._get_security()

    assert_equal(True, security['use_sasl'])
    assert_equal('GSSAPI', security['mechanism'])
  finally:
    sentry_site.reset()
    finish()
    shutil.rmtree(tmpdir)


def sentry_site_xml(
    provider='default',
    kerberos_principal='test/test.com@TEST.COM',
    authentication='NOSASL'):

  return """
    <configuration>

      <property>
        <name>hive.sentry.provider</name>
        <value>%(provider)s</value>
      </property>

      <property>
        <name>sentry.service.server.principal</name>
        <value>%(kerberos_principal)s</value>
      </property>

      <property>
        <name>sentry.service.security.mode</name>
        <value>%(authentication)s</value>
      </property>

      <property>
        <name>sentry.service.admin.group</name>
        <value>hive,impala,hue</value>
      </property>

    </configuration>
  """ % {
    'provider': provider,
    'kerberos_principal': kerberos_principal,
    'authentication': authentication,
  }
