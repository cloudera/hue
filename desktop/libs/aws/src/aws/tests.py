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

from mock import patch, Mock
from nose.tools import assert_equal, assert_true, assert_not_equal

from aws import conf
from aws.client import clear_cache, get_client, get_credential_provider, current_ms_from_utc

LOG = logging.getLogger(__name__)

class TestAWS(unittest.TestCase):
  def test_with_credentials(self):
    try:
      finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'access_key_id':'access_key_id', 'secret_access_key': 'secret_access_key'}})
      with patch('aws.client.conf_idbroker.get_conf') as get_conf:
        with patch('aws.client.Client.get_s3_connection'):
          get_conf.return_value = {}
          client1 = get_client('default')
          client2 = get_client('default', 'test')

          provider = get_credential_provider()
          assert_equal(provider.get_credentials().get('AccessKeyId'), conf.AWS_ACCOUNTS['default'].ACCESS_KEY_ID.get())
          assert_equal(client1, client2) # Should be the same as no support for user based client with credentials & no Expiration
    finally:
      finish()
      clear_cache()

  def test_with_idbroker(self):
    try:
      finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {}})
      with patch('aws.client.conf_idbroker.get_conf') as get_conf:
        with patch('aws.client.Client.get_s3_connection'):
          with patch('aws.client.IDBroker.get_cab') as get_cab:
            get_conf.return_value = {
              'fs.s3a.ext.cab.address': 'address'
            }
            get_cab.return_value = {
              'Credentials': {'AccessKeyId': 'AccessKeyId', 'Expiration': 0}
            }
            provider = get_credential_provider()
            assert_equal(provider.get_credentials().get('AccessKeyId'), 'AccessKeyId')
            client1 = get_client('default', 'HUE')
            client2 = get_client('default', 'HUE')
            assert_not_equal(client1, client2) # Test that with Expiration 0 clients not equal

            get_cab.return_value = {
              'Credentials': {'AccessKeyId': 'AccessKeyId', 'Expiration': int(current_ms_from_utc()) + 10*1000}
            }
            client3 = get_client('default', 'HUE')
            client4 = get_client('default', 'HUE')
            client5 = get_client('default', 'test')
            assert_equal(client3, client4) # Test that with 10 sec expiration, clients equal
            assert_not_equal(client4, client5) # Test different user have different clients
    finally:
      finish()
      clear_cache()
