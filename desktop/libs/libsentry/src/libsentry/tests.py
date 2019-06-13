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
from desktop.lib.exceptions import StructuredThriftTransportException
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.test_utils import add_to_group, grant_access

from hadoop.pseudo_hdfs4 import is_live_cluster

from libsentry import sentry_site
from libsentry.api import get_api, clear_api_cache
from libsentry.api2 import get_api as get_api2, clear_api_cache as clear_api2_cache
from libsentry.conf import is_enabled, HOSTNAME, PORT, SENTRY_CONF_DIR
from libsentry.client import SentryClient
from libsentry.sentry_ha import get_next_available_server
from libsentry.sentry_site import get_sentry_server


def create_mock_client_fn(client_class, username, server, component=None):
  class MockSentryClient(object):
    def __init__(self, host):
      self.host = host

    def list_sentry_roles_by_group(self, groupName='*'):
      if self.host.startswith('bad'):
        raise StructuredThriftTransportException(ex=None)
      else:
        return []

  if server is not None:
    return MockSentryClient(server['hostname'])
  else:
    raise PopupException(_('Cannot create a Sentry client without server hostname and port.'))


class TestWithSentry(object):

  @classmethod
  def setup_class(cls):
    if not os.path.exists(os.path.join(SENTRY_CONF_DIR.get(), 'sentry-site.xml')):
      raise SkipTest('Could not find sentry-site.xml, skipping sentry tests')

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "libsentry")

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

    clear_api_cache()
    clear_api2_cache()


  def tearDown(self):
    sentry_site.reset()
    for reset in self.resets:
      reset()
    shutil.rmtree(self.tmpdir)


  def test_get_random_sentry_server(self):
    # Test that with no current_host, a server for a random host is returned
    xml = self._sentry_site_xml(rpc_addresses='%s,host-1,host-2' % self.rpc_addresses, rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server = get_sentry_server()
    assert_true(server is not None)
    assert_true(server['hostname'] in '%s,host-1,host-2' % self.rpc_addresses)


  def test_get_single_sentry_server(self):
    # Test that with a current host and single server, the single server is returned
    xml = self._sentry_site_xml(rpc_addresses='host-1', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server = get_sentry_server(current_host='host-1')
    assert_true(server is not None)
    assert_equal(server['hostname'], 'host-1')


  def test_get_next_sentry_server(self):
    # Test that with a current host and multiple servers, the next server is returned
    xml = self._sentry_site_xml(rpc_addresses='%s,host-1,host-2' % self.rpc_addresses, rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server = get_sentry_server(current_host='host-1')
    assert_true(server is not None)
    assert_equal(server['hostname'], 'host-2')


  def test_get_first_sentry_server(self):
    # Test that if the current host is the last host of multiple servers, the first server is returned
    xml = self._sentry_site_xml(rpc_addresses='host-1,%s,host-2' % self.rpc_addresses, rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server = get_sentry_server(current_host='host-2')
    assert_true(server is not None)
    assert_equal(server['hostname'], 'host-1')


  def test_round_robin(self):
    # Test that get_next_available_client will check each server once and only once then exit
    xml = self._sentry_site_xml(rpc_addresses='host-1,host-2,host-3,host-4,host-5', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server, attempts = get_next_available_server(SentryClient, self.user.username, failed_host='host-1')
    assert_equal(None, server)
    assert_equal(['host-2','host-3','host-4','host-5'], attempts)


  def test_get_next_good_host(self):
    # Test that get_next_available_client will return the next good/successful server
    xml = self._sentry_site_xml(rpc_addresses='bad-host-1,good-host-1,bad-host-2,good-host-2,good-host-3', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server, attempts = get_next_available_server(SentryClient, self.user.username, failed_host='bad-host-2',
                                                 create_client_fn=create_mock_client_fn)
    assert_equal('good-host-2', server['hostname'])
    assert_equal([], attempts)


  def test_single_good_host(self):
    # Test that get_next_available_client will return the single good host on first try
    xml = self._sentry_site_xml(rpc_addresses='good-host-1', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server, attempts = get_next_available_server(SentryClient, self.user.username, failed_host=None,
                                                 create_client_fn=create_mock_client_fn)
    assert_equal('good-host-1', server['hostname'])
    assert_equal([], attempts)


  def test_single_bad_host(self):
    # Test that get_next_available_client will raise an exception on single bad host
    xml = self._sentry_site_xml(rpc_addresses='bad-host-1', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    assert_raises(PopupException, get_next_available_server, SentryClient, self.user.username, failed_host=None,
                  create_client_fn=create_mock_client_fn)


  def test_bad_good_host(self):
    # Test that get_next_available_client will return the good host
    xml = self._sentry_site_xml(rpc_addresses='bad-host-1,good-host-1', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server, attempts = get_next_available_server(SentryClient, self.user.username, failed_host='bad-host-1',
                                                 create_client_fn=create_mock_client_fn)
    assert_equal('good-host-1', server['hostname'])
    assert_equal([], attempts)


  def test_good_bad_host(self):
    # Test that get_next_available_client will return the good host
    xml = self._sentry_site_xml(rpc_addresses='good-host-1,bad-host-1', rpc_port=self.rpc_port)
    file(os.path.join(self.tmpdir, 'sentry-site.xml'), 'w').write(xml)
    sentry_site.reset()

    server, attempts = get_next_available_server(SentryClient, self.user.username, failed_host='bad-host-1',
                                                 create_client_fn=create_mock_client_fn)
    assert_equal('good-host-1', server['hostname'])
    assert_equal([], attempts)


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


class TestSentryWithHadoop(object):
  requires_hadoop = True
  integration = True

  @classmethod
  def setup_class(cls):
    if not is_live_cluster():
      raise SkipTest('TestSentryWithHadoop requires a live cluster.')

    if not os.path.exists(os.path.join(SENTRY_CONF_DIR.get(), 'sentry-site.xml')):
      raise SkipTest('Could not find sentry-site.xml, skipping sentry tests')

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "libsentry")

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

    clear_api_cache()
    clear_api2_cache()


  def tearDown(self):
    sentry_site.reset()
    for reset in self.resets:
      reset()
    shutil.rmtree(self.tmpdir)


  def test_get_collections(self):
    client = SentryClient(HOSTNAME.get(), PORT.get(), 'test')
    resp = client.list_sentry_roles_by_group() # Non Sentry Admin can do that
    assert_not_equal(0, resp.status.value, resp)
    assert_true('denied' in resp.status.message, resp)

    resp = client.list_sentry_roles_by_group(groupName='*')
    assert_equal(0, resp.status.value, resp)
