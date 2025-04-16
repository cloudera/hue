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
import logging
import pytest
import unittest

from django.test import TestCase
from unittest.mock import Mock, patch

from desktop.lib.idbroker.client import IDBroker
from desktop.lib.idbroker.conf import _handle_idbroker_ha
from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger()


class TestIDBrokerClient(TestCase):
  def test_username_authentication(self):
    with patch('desktop.lib.idbroker.conf.get_conf') as conf:
      with patch('desktop.lib.idbroker.client.resource.Resource.invoke') as invoke:
        with patch('desktop.lib.idbroker.client.http_client.HttpClient.set_basic_auth') as set_basic_auth:
          with patch('desktop.lib.idbroker.conf.get_cab_address') as get_cab_address:
            conf.return_value = {
              'fs.s3a.ext.cab.address': 'address',
              'fs.s3a.ext.cab.dt.path': 'dt_path',
              'fs.s3a.ext.cab.path': 'path',
              'fs.s3a.ext.cab.username': 'username',
              'fs.s3a.ext.cab.password': 'password'
            }
            invoke.return_value = {
              'Credentials': 'Credentials'
            }
            get_cab_address.return_value = 'address'

            client = IDBroker.from_core_site('s3a', 'test')
            cab = client.get_cab()

            assert invoke.call_count == 2 # get_cab calls twice
            assert cab.get('Credentials') == 'Credentials'
            assert set_basic_auth.call_count == 1


  def test_kerberos_authentication(self):
    with patch('desktop.lib.idbroker.conf.get_conf') as conf:
      with patch('desktop.lib.idbroker.client.is_kerberos_enabled') as is_kerberos_enabled:
        with patch('desktop.lib.idbroker.client.resource.Resource.invoke') as invoke:
          with patch('desktop.lib.idbroker.client.http_client.HttpClient.set_kerberos_auth') as set_kerberos_auth:
            with patch('desktop.lib.idbroker.conf.get_cab_address') as get_cab_address:
              is_kerberos_enabled.return_value = True
              conf.return_value = {
                'fs.s3a.ext.cab.address': 'address',
                'fs.s3a.ext.cab.dt.path': 'dt_path',
                'fs.s3a.ext.cab.path': 'path',
                'hadoop.security.authentication': 'kerberos',
              }
              invoke.return_value = {
                'Credentials': 'Credentials'
              }
              get_cab_address.return_value = 'address'

              client = IDBroker.from_core_site('s3a', 'test')
              cab = client.get_cab()

              assert invoke.call_count == 2 # get_cab calls twice
              assert cab.get('Credentials') == 'Credentials'
              assert set_kerberos_auth.call_count == 1


  def test_no_idbroker_address_found(self):
    with patch('desktop.lib.idbroker.conf.get_conf') as conf:
      with patch('desktop.lib.idbroker.conf.get_cab_address') as get_cab_address:
        conf.return_value = {
          'fs.s3a.ext.cab.address': 'address',
          'fs.s3a.ext.cab.dt.path': 'dt_path',
          'fs.s3a.ext.cab.path': 'path'
        }

        # No active IDBroker URL available
        get_cab_address.return_value = None
        with pytest.raises(PopupException):
          IDBroker.from_core_site('s3a', 'test')



class TestIDBrokerHA(TestCase):
  def test_idbroker_non_ha(self):
    with patch('desktop.lib.idbroker.conf.get_conf') as conf:
      with patch('desktop.lib.idbroker.conf.requests.get') as requests_get:
        conf.return_value = {'fs.s3a.ext.cab.address': 'https://idbroker0.gethue.com:8444/gateway'}
        requests_get.return_value = Mock(status_code=200)

        idbroker_url = _handle_idbroker_ha(fs='s3a')
        assert idbroker_url == 'https://idbroker0.gethue.com:8444/gateway'
        assert requests_get.call_count == 1


  def test_idbroker_ha(self):
    with patch('desktop.lib.idbroker.conf.get_conf') as conf:
      with patch('desktop.lib.idbroker.conf.requests.get') as requests_get:
        conf.return_value = {
          'fs.s3a.ext.cab.address': 'https://idbroker0.gethue.com:8444/gateway,https://idbroker1.gethue.com:8444/gateway'
        }

        # When IDBroker0 is healthy and IDBroker1 is unhealthy
        requests_get.side_effect = [Mock(status_code=200), Mock(status_code=404)]
        idbroker_url = _handle_idbroker_ha(fs='s3a')

        assert idbroker_url == 'https://idbroker0.gethue.com:8444/gateway'
        assert requests_get.call_count == 1
        requests_get.reset_mock()


        # When IDBroker0 is unhealthy and IDBroker1 is healthy
        requests_get.side_effect = [Mock(status_code=404), Mock(status_code=200)]
        idbroker_url = _handle_idbroker_ha(fs='s3a')

        assert idbroker_url == 'https://idbroker1.gethue.com:8444/gateway'
        assert requests_get.call_count == 2
        requests_get.reset_mock()


        # When both IDBroker0 and IDBroker1 are unhealthy
        requests_get.side_effect = [Mock(status_code=404), Mock(status_code=404)]
        idbroker_url = _handle_idbroker_ha(fs='s3a')

        assert idbroker_url == None
        assert requests_get.call_count == 2

