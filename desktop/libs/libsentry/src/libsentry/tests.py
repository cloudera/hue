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

import lxml.etree
import os
import shutil
import tempfile

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false, assert_not_equal, assert_raises

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.test_utils import add_to_group, grant_access

from hadoop.pseudo_hdfs4 import is_live_cluster

from libsentry import sentry_site
from libsentry.api import get_api, API_CACHE
from libsentry.api2 import get_api as get_api2, API_CACHE as API2_CACHE
from libsentry.conf import is_enabled, HOSTNAME, PORT, SENTRY_CONF_DIR
from libsentry.client import SentryClient


class TestWithSentry(object):

  requires_hadoop = True

  @classmethod
  def setup_class(cls):
    if not is_live_cluster():
      raise SkipTest('Sentry tests require a live sentry server')

    if not os.path.exists(os.path.join(SENTRY_CONF_DIR.get(), 'sentry-site.xml')):
      raise SkipTest('Could not find sentry-site.xml, skipping sentry tests')

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "libsentry")

    cls.db = SentryClient(HOSTNAME.get(), PORT.get(), 'test')
    cls.config_path = os.path.join(SENTRY_CONF_DIR.get(), 'sentry-site.xml')


  def setUp(self):
    self.rpc_addresses = ''
    if sentry_site.get_sentry_server_rpc_addresses() is not None:
      self.rpc_addresses = ','.join(sentry_site.get_sentry_server_rpc_addresses())
    self.rpc_port = sentry_site.get_sentry_server_rpc_port() or '8038'

    self.tmpdir = tempfile.mkdtemp()
    self.resets = [
      SENTRY_CONF_DIR.set_for_testing(self.tmpdir),
    ]
    if API_CACHE is not None:
      self.resets.append(API_CACHE.set_for_testing(None))
    if API2_CACHE is not None:
      self.resets.append(API2_CACHE.set_for_testing(None))


  def tearDown(self):
    sentry_site.reset()
    for reset in self.resets:
      reset()
    shutil.rmtree(self.tmpdir)


  def test_get_collections(self):
    resp = self.db.list_sentry_roles_by_group() # Non Sentry Admin can do that
    assert_not_equal(0, resp.status.value, resp)
    assert_true('denied' in resp.status.message, resp)

    resp = self.db.list_sentry_roles_by_group(groupName='*')
    assert_equal(0, resp.status.value, resp)


  def test_ha_failover_good_bad_bad(self):
    # Test with good-host,bad-host-1,bad-host-2
    xml = self._sentry_site_xml(rpc_addresses='%s,bad-host-1:8039,bad-host-2' % self.rpc_addresses, rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    api = get_api(self.user)
    assert_equal('%s,bad-host-1:8039,bad-host-2' % self.rpc_addresses, ','.join(sentry_site.get_sentry_server_rpc_addresses()))
    resp = api.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))

    api2 = get_api2(self.user, 'solr')
    resp = api2.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))


  def test_ha_failover_bad_bad_good(self):
    # Test with bad-host-1,bad-host-2,good-host
    xml = self._sentry_site_xml(rpc_addresses='bad-host-1:8039,bad-host-2,%s' % self.rpc_addresses, rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    api = get_api(self.user)
    assert_equal('bad-host-1:8039,bad-host-2,%s' % self.rpc_addresses, ','.join(sentry_site.get_sentry_server_rpc_addresses()))
    resp = api.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))

    api2 = get_api2(self.user, 'solr')
    resp = api2.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))


  def test_ha_failover_bad_good_bad(self):
    # Test with bad-host-1,good-host,bad-host-2
    xml = self._sentry_site_xml(rpc_addresses='bad-host-1:8039,%s,bad-host-2' % self.rpc_addresses, rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    api = get_api(self.user)
    assert_equal('bad-host-1:8039,%s,bad-host-2' % self.rpc_addresses, ','.join(sentry_site.get_sentry_server_rpc_addresses()))
    resp = api.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))

    api2 = get_api2(self.user, 'solr')
    resp = api2.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))


  def test_ha_failover_all_bad(self):
    # Test with all bad hosts
    xml = self._sentry_site_xml(rpc_addresses='bad-host-1:8039,bad-host-2', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    api = get_api(self.user)
    assert_equal('bad-host-1:8039,bad-host-2', ','.join(sentry_site.get_sentry_server_rpc_addresses()))
    assert_raises(PopupException, api.list_sentry_roles_by_group, '*')

    api2 = get_api2(self.user, 'solr')
    assert_raises(PopupException, api2.list_sentry_roles_by_group, '*')


  def test_no_rpc_hosts(self):
    # Test with no rpc hosts and fallback to hostname and port
    xml = self._sentry_site_xml(rpc_addresses='')
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    api = get_api(self.user)
    assert_false(sentry_site.is_ha_enabled(), sentry_site.get_sentry_server_rpc_addresses())
    assert_true(is_enabled() and HOSTNAME.get() and HOSTNAME.get() != 'localhost')
    resp = api.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))

    api2 = get_api2(self.user, 'solr')
    resp = api2.list_sentry_roles_by_group(groupName='*')
    assert_true(isinstance(resp, list))


  def _sentry_site_xml(self, rpc_addresses, rpc_port='8038'):
    config = lxml.etree.parse(self.config_path)
    root = config.getroot()
    properties = config.findall('property')
    for prop in properties:
      name = prop.find('name')
      if name.text == 'sentry.service.client.server.rpc-address':
        value = prop.find('value')
        value.text = rpc_addresses
      elif name.text == 'sentry.service.client.server.rpc-port':
        value = prop.find('value')
        value.text = rpc_port
    return lxml.etree.tostring(root)