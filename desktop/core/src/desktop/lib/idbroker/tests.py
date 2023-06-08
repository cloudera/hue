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
import unittest
import sys

from nose.tools import assert_equal, assert_true

from desktop.lib.idbroker.client import IDBroker

if sys.version_info[0] > 2:
  from unittest.mock import patch
else:
  from mock import patch

LOG = logging.getLogger()

class TestIDBroker(unittest.TestCase):
  def test_username_authentication(self):
    with patch('desktop.lib.idbroker.conf.get_conf') as conf:
      with patch('desktop.lib.idbroker.client.resource.Resource.invoke') as invoke:
        with patch('desktop.lib.idbroker.client.http_client.HttpClient.set_basic_auth') as set_basic_auth:
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
          client = IDBroker.from_core_site('s3a', 'test')

          cab = client.get_cab()
          assert_equal(invoke.call_count, 2) # get_cab calls twice
          assert_equal(cab.get('Credentials'), 'Credentials')
          assert_equal(set_basic_auth.call_count, 1)

  def test_kerberos_authentication(self):
    with patch('desktop.lib.idbroker.conf.get_conf') as conf:
      with patch('desktop.lib.idbroker.client.is_kerberos_enabled') as is_kerberos_enabled:
        with patch('desktop.lib.idbroker.client.resource.Resource.invoke') as invoke:
          with patch('desktop.lib.idbroker.client.http_client.HttpClient.set_kerberos_auth') as set_kerberos_auth:
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
            client = IDBroker.from_core_site('s3a', 'test')

            cab = client.get_cab()
            assert_equal(invoke.call_count, 2) # get_cab calls twice
            assert_equal(cab.get('Credentials'), 'Credentials')
            assert_equal(set_kerberos_auth.call_count, 1)
