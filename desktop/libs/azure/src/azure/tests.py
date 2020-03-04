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
from __future__ import absolute_import

import logging
import sys
import unittest

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_not_equal

from azure import conf
from azure.client import get_credential_provider

from desktop.lib.fsmanager import get_client, clear_cache, is_enabled
from desktop.lib.python_util import current_ms_from_utc

if sys.version_info[0] > 2:
  from unittest.mock import patch
else:
  from mock import patch

LOG = logging.getLogger(__name__)


class TestAzureAdl(unittest.TestCase):

  def test_with_core_site(self):
    try:
      finish = (conf.AZURE_ACCOUNTS.set_for_testing({'default': {}}),
                conf.ADLS_CLUSTERS.set_for_testing({'default': {'fs_defaultfs': 'fs_defaultfs', 'webhdfs_url': 'webhdfs_url'}}))
      with patch('azure.client.conf_idbroker.get_conf') as get_conf:
        with patch('azure.client.WebHdfs.get_client'):
          with patch('azure.client.ActiveDirectory.get_token') as get_token:
            with patch('azure.conf.core_site.get_conf') as core_site_get_conf:
              get_token.return_value = {'access_token': 'access_token', 'token_type': '', 'expires_on': None}
              get_conf.return_value = {}
              core_site_get_conf.return_value = {'dfs.adls.oauth2.client.id': 'client_id', 'dfs.adls.oauth2.credential': 'client_secret', 'dfs.adls.oauth2.refresh.url': 'refresh_url'}
              client1 = get_client(name='default', fs='adl')
              client2 = get_client(name='default', fs='adl', user='test')

              provider = get_credential_provider('default', 'hue')
              assert_equal(provider.get_credentials().get('access_token'), 'access_token')
              assert_equal(client1, client2) # Should be the same as no support for user based client with credentials & no Expiration
    finally:
      for f in finish:
        f()
      clear_cache()

  def test_with_credentials(self):
    try:
      finish = (conf.AZURE_ACCOUNTS.set_for_testing({'default': {'client_id':'client_id', 'client_secret': 'client_secret', 'tenant_id': 'tenant_id'}}),
                conf.ADLS_CLUSTERS.set_for_testing({'default': {'fs_defaultfs': 'fs_defaultfs', 'webhdfs_url': 'webhdfs_url'}}))
      with patch('azure.client.conf_idbroker.get_conf') as get_conf:
        with patch('azure.client.WebHdfs.get_client'):
          with patch('azure.client.ActiveDirectory.get_token') as get_token:
            get_token.return_value = {'access_token': 'access_token', 'token_type': '', 'expires_on': None}
            get_conf.return_value = {}
            client1 = get_client(name='default', fs='adl')
            client2 = get_client(name='default', fs='adl', user='test')

            provider = get_credential_provider('default', 'hue')
            assert_equal(provider.get_credentials().get('access_token'), 'access_token')
            assert_equal(client1, client2) # Should be the same as no support for user based client with credentials & no Expiration
    finally:
      for f in finish:
        f()
      clear_cache()


  def test_with_idbroker(self):
    try:
      finish = (conf.AZURE_ACCOUNTS.set_for_testing({}),
                conf.ADLS_CLUSTERS.set_for_testing({'default': {'fs_defaultfs': 'fs_defaultfs', 'webhdfs_url': 'webhdfs_url'}}))
      with patch('azure.client.conf_idbroker.get_conf') as get_conf:
        with patch('azure.client.WebHdfs.get_client'):
          with patch('azure.client.IDBroker.get_cab') as get_cab:
            with patch('azure.client.conf.has_azure_metadata') as has_azure_metadata:
              get_conf.return_value = {
                'fs.azure.ext.cab.address': 'address'
              }
              has_azure_metadata.return_value = True
              get_cab.return_value = { 'access_token': 'access_token', 'token_type': 'token_type', 'expires_on': 0 }
              provider = get_credential_provider('default', 'hue')
              assert_equal(provider.get_credentials().get('access_token'), 'access_token')
              client1 = get_client(name='default', fs='adl', user='hue')
              client2 = get_client(name='default', fs='adl', user='hue')
              assert_not_equal(client1, client2) # Test that with Expiration 0 clients not equal

              get_cab.return_value = {
                'Credentials': {'access_token': 'access_token', 'token_type': 'token_type', 'expires_on': int(current_ms_from_utc()) + 10*1000}
              }
              client3 = get_client(name='default', fs='adl', user='hue')
              client4 = get_client(name='default', fs='adl', user='hue')
              client5 = get_client(name='default', fs='adl', user='test')
              assert_equal(client3, client4) # Test that with 10 sec expiration, clients equal
              assert_not_equal(client4, client5) # Test different user have different clients
    finally:
      for f in finish:
        f()
      clear_cache()


class TestAzureAbfs(unittest.TestCase):

  def test_with_core_site(self):
    try:
      finish = (conf.AZURE_ACCOUNTS.set_for_testing({'default': {}}),
                conf.ABFS_CLUSTERS.set_for_testing({'default': {'fs_defaultfs': 'fs_defaultfs', 'webhdfs_url': 'webhdfs_url'}}))
      with patch('azure.client.conf_idbroker.get_conf') as get_conf:
        with patch('azure.client.ABFS.get_client'):
          with patch('azure.client.ActiveDirectory.get_token') as get_token:
            with patch('azure.conf.core_site.get_conf') as core_site_get_conf:
              get_token.return_value = {'access_token': 'access_token', 'token_type': '', 'expires_on': None}
              get_conf.return_value = {}
              core_site_get_conf.return_value = {'fs.azure.account.oauth2.client.id': 'client_id', 'fs.azure.account.oauth2.client.secret': 'client_secret', 'fs.azure.account.oauth2.client.endpoint': 'refresh_url'}
              client1 = get_client(name='default', fs='abfs')
              client2 = get_client(name='default', fs='abfs', user='test')

              provider = get_credential_provider('default', 'hue')
              assert_equal(provider.get_credentials().get('access_token'), 'access_token')
              assert_equal(client1, client2) # Should be the same as no support for user based client with credentials & no Expiration
    finally:
      for f in finish:
        f()
      clear_cache()

  def test_with_credentials(self):
    try:
      finish = (conf.AZURE_ACCOUNTS.set_for_testing({'default': {'client_id':'client_id', 'client_secret': 'client_secret', 'tenant_id': 'tenant_id'}}),
                conf.ABFS_CLUSTERS.set_for_testing({'default': {'fs_defaultfs': 'fs_defaultfs', 'webhdfs_url': 'webhdfs_url'}}))
      with patch('azure.client.conf_idbroker.get_conf') as get_conf:
        with patch('azure.client.ABFS.get_client'):
          with patch('azure.client.ActiveDirectory.get_token') as get_token:
            get_token.return_value = {'access_token': 'access_token', 'token_type': '', 'expires_on': None}
            get_conf.return_value = {}
            client1 = get_client(name='default', fs='abfs')
            client2 = get_client(name='default', fs='abfs', user='test')

            provider = get_credential_provider('default', 'hue')
            assert_equal(provider.get_credentials().get('access_token'), 'access_token')
            assert_equal(client1, client2) # Should be the same as no support for user based client with credentials & no Expiration
    finally:
      for f in finish:
        f()
      clear_cache()


  def test_with_idbroker(self):
    try:
      finish = (conf.AZURE_ACCOUNTS.set_for_testing({}),
                conf.ABFS_CLUSTERS.set_for_testing({'default': {'fs_defaultfs': 'fs_defaultfs', 'webhdfs_url': 'webhdfs_url'}}))
      with patch('azure.client.conf_idbroker.get_conf') as get_conf:
        with patch('azure.client.ABFS.get_client'):
          with patch('azure.client.IDBroker.get_cab') as get_cab:
            with patch('azure.client.conf.has_azure_metadata') as has_azure_metadata:
              get_conf.return_value = {
                'fs.azure.ext.cab.address': 'address'
              }
              has_azure_metadata.return_value = True
              get_cab.return_value = { 'access_token': 'access_token', 'token_type': 'token_type', 'expires_on': 0 }
              provider = get_credential_provider('default', 'hue')
              assert_equal(provider.get_credentials().get('access_token'), 'access_token')
              client1 = get_client(name='default', fs='abfs', user='hue')
              client2 = get_client(name='default', fs='abfs', user='hue')
              assert_not_equal(client1, client2) # Test that with Expiration 0 clients not equal

              get_cab.return_value = {
                'Credentials': {'access_token': 'access_token', 'token_type': 'token_type', 'expires_on': int(current_ms_from_utc()) + 10*1000}
              }
              client3 = get_client(name='default', fs='abfs', user='hue')
              client4 = get_client(name='default', fs='abfs', user='hue')
              client5 = get_client(name='default', fs='abfs', user='test')
              assert_equal(client3, client4) # Test that with 10 sec expiration, clients equal
              assert_not_equal(client4, client5) # Test different user have different clients
    finally:
      for f in finish:
        f()
      clear_cache()